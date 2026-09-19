"""Offline diagnostics for the dependency-memory research proposal.

Standard library only. No model calls, network, training, or token estimates.
Exact bit-channel enumeration and a separate record-retention event test.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
from collections import OrderedDict
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path


def binary_entropy(p: float) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("Probability must be in [0, 1].")
    if p in (0.0, 1.0):
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def entropy_error_lower_bound(n_bits: int, memory_bits: int) -> float:
    """Necessary average error, not generally an attainable finite-block rate."""
    if n_bits < 1 or memory_bits < 0:
        raise ValueError("Invalid bit budget.")
    if memory_bits == 0:
        return 0.5
    if memory_bits >= n_bits:
        return 0.0
    target = 1.0 - memory_bits / n_bits
    low, high = 0.0, 0.5
    for _ in range(70):
        mid = (low + high) / 2
        if binary_entropy(mid) < target:
            low = mid
        else:
            high = mid
    return (low + high) / 2


@lru_cache(maxsize=None)
def exact_codebook(n_bits: int, memory_bits: int) -> tuple[float, tuple[int, ...], int]:
    """Minimum average bit-query error for independent fair bits, n <= 4.

    Each memory label decodes to one predicted n-bit vector. Enumerating sets
    of <= 2**B vectors and nearest-vector encoding exhausts deterministic
    encoders/decoders for uniform source strings and uniform query indices.
    Private/shared randomness cannot improve the minimum average linear loss.
    The public codebook is fixed before seeing the source, not extra storage.
    """
    if not 1 <= n_bits <= 4 or memory_bits < 0:
        raise ValueError("Enumeration is limited to 1 <= n_bits <= 4.")
    size = 1 << n_bits
    if memory_bits >= n_bits:
        return 0.0, tuple(range(size)), 1
    labels = 1 << memory_bits
    distances = [[(x ^ y).bit_count() for y in range(size)] for x in range(size)]
    best_sum, best_code, evaluated = math.inf, (), 0
    for code in itertools.combinations(range(size), labels):
        error_sum = sum(min(row[y] for y in code) for row in distances)
        evaluated += 1
        if error_sum < best_sum:
            best_sum, best_code = error_sum, code
    return best_sum / (size * n_bits), best_code, evaluated


def one_bit_partition_optimum(n_bits: int) -> float:
    """Independent exhaustive encoder check, used only for n <= 3 in tests."""
    if not 1 <= n_bits <= 3:
        raise ValueError("Partition enumeration limited to n <= 3.")
    size = 1 << n_bits
    best = math.inf
    for assignments in itertools.product((0, 1), repeat=size):
        errors = 0
        for label in (0, 1):
            members = [x for x, m in enumerate(assignments) if m == label]
            for bit in range(n_bits):
                ones = sum((x >> bit) & 1 for x in members)
                errors += min(ones, len(members) - ones)
        best = min(best, errors)
    return best / (size * n_bits)


@dataclass(frozen=True)
class Event:
    kind: str
    key: str = ""
    value: int | None = None


class RecordMemory:
    """A record baseline. The budget is records, NOT total information bits.

    Policy sees only the current event and its own retained dictionary. Keys,
    ordering, and values all occupy serialization space, reported separately.
    No evicted payload, replay log, or generator state is accessible here.
    """

    def __init__(self, capacity: int, release_on_retire: bool):
        if capacity < 1:
            raise ValueError("Capacity must be positive.")
        self.capacity = capacity
        self.release_on_retire = release_on_retire
        self.records: OrderedDict[str, int] = OrderedDict()
        self.peak_records = 0
        self.peak_payload_bytes = 0
        self.checkpoints = 0

    def serialized(self) -> str:
        return json.dumps(list(self.records.items()), separators=(",", ":"))

    def update(self, event: Event) -> int | None:
        answer = None
        if event.kind == "value":
            if event.value is None:
                raise ValueError("A value event must contain its payload.")
            self.records.pop(event.key, None)
            self.records[event.key] = event.value
            while len(self.records) > self.capacity:
                self.records.popitem(last=False)
        elif event.kind == "retire":
            if self.release_on_retire:
                self.records.pop(event.key, None)
        elif event.kind == "query":
            answer = self.records.get(event.key)
            if event.key in self.records:
                self.records.move_to_end(event.key)
        elif event.kind == "checkpoint":
            # Exact round trip. This is deliberately NOT an LLM compactor.
            self.records = OrderedDict(json.loads(self.serialized()))
            self.checkpoints += 1
        elif event.kind != "noise":
            raise ValueError(f"Unknown event type: {event.kind}")
        self.peak_records = max(self.peak_records, len(self.records))
        self.peak_payload_bytes = max(
            self.peak_payload_bytes, len(self.serialized().encode("utf-8"))
        )
        return answer


def make_workflow(seed: int, width: int, batches: int, noise: int = 2,
                  checkpoints_per_batch: int = 1) -> list[Event]:
    """One long-lived anchor plus batches of short-lived independent jobs.

    Retire is an observable, sound expiry signal: the key cannot be queried
    again. A value update revises an existing key or introduces a fresh key.
    This is an event-stream diagnostic, not an autonomous agent environment.
    """
    if width < 2 or batches < 1 or noise < 0 or checkpoints_per_batch < 0:
        raise ValueError("Invalid workflow dimensions.")
    rng = random.Random(seed)
    events = [Event("value", "anchor", rng.getrandbits(64))]
    for batch in range(batches):
        keys = [f"job_{batch}_{i}" for i in range(width - 1)]
        for key in keys:
            events.append(Event("value", key, rng.getrandbits(64)))
        # Revision after the first batch, followed by enough later jobs to
        # expose eviction. No source values are recoverable from identifiers.
        if batch == 0:
            events.append(Event("value", "anchor", rng.getrandbits(64)))
        events.extend(Event("noise") for _ in range(noise))
        events.extend(Event("checkpoint") for _ in range(checkpoints_per_batch))
        for key in keys:
            events.append(Event("query", key))
            events.append(Event("retire", key))
    events.extend((Event("query", "anchor"), Event("retire", "anchor")))
    return events


def run_workflow(events: list[Event], capacity: int, release: bool) -> dict:
    memory = RecordMemory(capacity, release)
    # Truth is evaluator-only; update() is never passed this dictionary.
    truth: dict[str, int] = {}
    correct = queries = max_live = 0
    anchor_correct = False
    for event in events:
        if event.kind == "value":
            truth[event.key] = event.value
        max_live = max(max_live, len(truth))
        result = memory.update(event)
        if event.kind == "query":
            queries += 1
            hit = result == truth[event.key]
            correct += hit
            if event.key == "anchor":
                anchor_correct = hit
        elif event.kind == "retire":
            del truth[event.key]
    return {
        "policy": "release_on_retire" if release else "lru_value_records",
        "capacity_records": capacity,
        "events": len(events),
        "max_live_records": max_live,
        "queries": queries,
        "correct": correct,
        "all_correct": correct == queries,
        "anchor_correct": anchor_correct,
        "peak_records": memory.peak_records,
        "peak_serialized_payload_bytes": memory.peak_payload_bytes,
        "checkpoints": memory.checkpoints,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def diagnostics() -> tuple[list[dict], list[dict], list[dict], list[dict], dict]:
    """Recompute every result in memory for read-only artifact validation."""
    frontier = []
    for n in range(1, 5):
        for budget in range(n + 1):
            error, code, evaluated = exact_codebook(n, budget)
            frontier.append({
                "candidate_bits": n,
                "memory_bits": budget,
                "exact_min_average_error": error,
                "entropy_lower_bound": entropy_error_lower_bound(n, budget),
                "fixed_coordinate_retention_error": 0.5 * (1 - min(n, budget) / n),
                "codebook": " ".join(format(x, f"0{n}b") for x in code),
                "codebooks_evaluated": evaluated,
            })
    # Four original bits. Public clue selects one equal-size block independent
    # of the values. The final query is uniform in that block. Moving only the
    # clue across the first bottleneck changes what the encoder can exploit.
    disclosure = []
    for candidates in (1, 2, 4):
        for budget in (1, 2):
            early = exact_codebook(candidates, budget)[0]
            late = exact_codebook(4, budget)[0]
            disclosure.append({
                "original_bits": 4,
                "candidate_bits_after_clue": candidates,
                "memory_bits": budget,
                "clue_before_bottleneck_error": early,
                "clue_after_bottleneck_error": late,
                "timing_gap": late - early,
            })
    workflows = []
    for seed, width, batches, checkpoints in itertools.product(
        range(5), (2, 4, 8), (4, 16, 64), (0, 1, 5)
    ):
        events = make_workflow(seed, width, batches, checkpoints_per_batch=checkpoints)
        for capacity in sorted({width - 1, width, 2 * width}):
            for release in (False, True):
                row = run_workflow(events, capacity, release)
                workflows.append({"seed": seed, "width": width, "batches": batches, **row})
    example_events = [asdict(x) for x in make_workflow(0, 2, 3)]
    fit = [r for r in workflows if r["capacity_records"] >= r["width"]]
    summary = {
        "scope": "Exact toy channels and deterministic record policies; no LLM results.",
        "exact_frontier_rows": len(frontier),
        "workflow_runs": len(workflows),
        "adequate_capacity_runs_per_policy": len(fit) // 2,
        "release_all_correct_at_adequate_capacity": sum(
            r["all_correct"] for r in fit if r["policy"] == "release_on_retire"
        ),
        "lru_all_correct_at_adequate_capacity": sum(
            r["all_correct"] for r in fit if r["policy"] == "lru_value_records"
        ),
        "exact_unknown_query_4_bits_1_bit_memory_error": exact_codebook(4, 1)[0],
        "exact_known_query_1_bit_memory_error": 0.0,
    }
    return frontier, disclosure, workflows, example_events, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    frontier, disclosure, workflows, example_events, summary = diagnostics()
    for name, result in (("exact_frontier.csv", frontier), ("disclosure_timing.csv", disclosure),
                         ("workflow_retention.csv", workflows)):
        write_csv(args.output / name, result)
    # Preserve the established CRLF serialization of these original artifacts.
    (args.output / "example_events.json").write_text(json.dumps(example_events, indent=2), encoding="utf-8", newline="\r\n")
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\r\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
