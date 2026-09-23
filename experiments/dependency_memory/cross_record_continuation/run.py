"""Dispatch only the separately frozen 149-identity continuation suffix."""
from __future__ import annotations

import argparse
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import random
from time import perf_counter_ns

from experiments.dependency_memory.cross_record import run as original
from experiments.dependency_memory.cross_record.casebook import compact, truth
from luna6_revision.audit import run_case
from luna6_revision.transport import Client, RESERVATION, save
from .plan import ORIGINAL, PLAN_PATH, original_files, schedule

ROOT = original.ROOT
OUTPUT = ROOT / "experiments/dependency_memory/results/cross_record_continuation_2026-09-22"
CAP = Decimal("25")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def code_fingerprints():
    folder = Path(__file__).parent
    paths = list(folder.glob("*.py")) + [folder / "FROZEN_PROTOCOL.md", PLAN_PATH]
    return {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def verify_plan():
    plan = load(PLAN_PATH)
    if (plan.get("version") != "cross_record_continuation_v1" or
            plan.get("original_attempts") != 199 or plan.get("original_completed") != 198 or
            plan.get("new_dispatch_cap") != 149 or plan.get("planning_credit_cap") != "25" or
            plan.get("original_files") != original_files() or
            plan.get("original_source_fingerprints") != original.fingerprints()):
        raise ValueError("Frozen continuation plan/source drift")
    ordered = schedule()
    if ordered[198] != plan["original_failed_identity"] or ordered[199:] != plan["ordered_pending"]:
        raise ValueError("Frozen pending schedule drift")
    return plan


class ContinuationClient:
    """Global ordered budget; explicit provider generation failures stay missing."""
    def __init__(self, executable, global_instructions, directory, audit, ordered_pending):
        self.args = (executable, global_instructions, directory, audit)
        self.directory = directory
        self.pending = ordered_pending
        self.clients = [Client(*self.args)]
        self.next_index = 0
        self.unknown_reservations = Decimal(0)
        self.provider_failures = []
        self.last_failed = False

    @property
    def attempts(self):
        return sum(client.attempts for client in self.clients)

    @property
    def spent(self):
        return sum((client.spent for client in self.clients), Decimal(0))

    def complete(self, identity, request):
        if self.next_index >= len(self.pending) or identity != self.pending[self.next_index]:
            raise ValueError("Call not next in the frozen never-dispatched suffix")
        if self.spent + self.unknown_reservations + RESERVATION > CAP:
            raise RuntimeError("Continuation credit ceiling exhausted")
        current = self.clients[-1]
        if current.stopped or current.attempts >= 120 or current.spent + RESERVATION > Decimal("20"):
            current = Client(*self.args)
            self.clients.append(current)
        self.last_failed = False
        try:
            result = current.complete(identity, request)
        except RuntimeError as error:
            path = self.directory / "calls" / (identity + ".json")
            record = load(path) if path.exists() else {}
            if (str(error) != "Provider generation error" or
                    record.get("identity") != identity or record.get("status") != "transport_failure" or
                    record.get("dispatched") is not True or record.get("error") != str(error)):
                raise
            self.unknown_reservations += RESERVATION
            self.provider_failures.append(identity)
            self.last_failed = True
            result = None
        self.next_index += 1
        if self.attempts != self.next_index:
            raise ValueError("Provider attempts and plan cursor diverged")
        return result


def launch(directory, executable, global_instructions):
    if directory.exists():
        raise ValueError("Continuation output exists; never resume")
    plan = verify_plan()
    frozen_code = code_fingerprints()
    audit = load(ORIGINAL / "preflight.json")
    if audit.get("isolation_passed") is not True:
        raise ValueError("Original isolation audit absent")
    dev = load(Path(original.__file__).parent / "fixtures/development-escrow-61011.json")
    audit["continuation_loopback"] = run_case(str(executable), global_instructions.read_text(encoding="utf-8"),
                                               "final_message", original.parent_request(dev, "structured"))
    directory.mkdir(parents=True)
    (directory / "calls").mkdir()
    save(directory / "preflight.json", audit)
    save(directory / "manifest.json", {"version": "cross_record_continuation_v1",
        "status": "frozen-before-continuation-answers", "plan_sha256": sha256(PLAN_PATH.read_bytes()).hexdigest(),
        "code_fingerprints": frozen_code, "original_source_fingerprints": original.fingerprints(),
        "model": "gpt-6-luna", "effort": "medium", "scheduled_new_calls": len(plan["ordered_pending"]),
        "call_cap": 149, "planning_credit_cap": str(CAP),
        "original_failure": plan["original_failed_identity"]})
    client = ContinuationClient(executable, global_instructions, directory, audit, plan["ordered_pending"])
    original_ids = set(schedule()[:199])
    try:
        for path in original.fixture_paths()[0]:
            case = load(path)
            cid = case["id"]
            if cid + "-prompt-parent" in original_ids:
                episode = load(ORIGINAL / (cid + "-episode.json"))
                if episode.get("case_id") != cid:
                    raise ValueError("Original episode mismatch")
                # Prior fully completed cases have no pending identity.
                if not any(identity.startswith(cid + "-") for identity in plan["ordered_pending"]):
                    continue
                save(directory / (cid + "-episode.json"), episode)
            else:
                episode = original.prepare_memories(client, case, directory)
            episode.setdefault("decisions", [])
            for future in case["futures"]:
                arms = list(original.ARMS)
                random.Random(future["id"] + ":frozen-order").shuffle(arms)
                for arm in arms:
                    identity = future["id"] + "-" + arm
                    if identity in original_ids:
                        continue
                    retained = original.retained_for(arm, case, episode, future)
                    client.complete(identity, original.execution_request(case, retained, future))
                    episode["decisions"].append({"identity": identity, "arm": arm,
                        "future_id": future["id"], "memory_bytes": len(retained.encode()),
                        "truth": truth(case, future), "transport_failure": client.last_failed})
                    save(directory / (cid + "-episode.json"), episode)
        if (client.next_index != 149 or client.attempts != 149 or
                verify_plan() != plan or code_fingerprints() != frozen_code):
            raise ValueError("Continuation source drift or incomplete suffix")
        save(directory / "completion.json", {"status": "complete_with_permanent_original_failure",
            "new_attempts": client.attempts, "new_provider_failures": client.provider_failures,
            "settled_planning_credits": str(client.spent),
            "uncertain_reservation_credits": str(client.unknown_reservations)})
    except Exception as error:
        save(directory / "completion.json", {"status": "stopped", "new_attempts": client.attempts,
            "new_provider_failures": client.provider_failures,
            "settled_planning_credits": str(client.spent),
            "uncertain_reservation_credits": str(client.unknown_reservations),
            "error_type": type(error).__name__, "error": str(error)[:160]})
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--launch", action="store_true")
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    parser.add_argument("--executable", required=True, type=Path)
    parser.add_argument("--global-instructions", required=True, type=Path)
    args = parser.parse_args()
    if not args.launch:
        parser.error("Explicit --launch required")
    launch(args.directory.resolve(), args.executable.resolve(), args.global_instructions.resolve())


if __name__ == "__main__":
    main()
