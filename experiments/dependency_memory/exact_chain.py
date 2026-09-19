"""Exact finite parent/child coding optimum by enumerating parent partitions.

The reference backend uses only Python's standard library.  The native backend
compiles the embedded, auditable C99 search with an explicitly selected compiler;
it makes the 171,798,901-partition four-bit search practical.  No model calls,
external optimization packages, floating-point objective, or heuristic pruning.

Run the full certificate with:
    python experiments/dependency_memory/exact_chain.py --compiler clang
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import shutil
import subprocess
import tempfile
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path


# The scalar native search deliberately does not use SIMD or platform intrinsics.
# Its score table is derived from signed coordinate sums.  The Python witness
# grader below instead reconstructs decoder bits and checks individual outcomes.
NATIVE_SOURCE = r"""
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

static unsigned n, states, universe_size;
static unsigned cells[4], witness[4], best;
static unsigned char gains[65536][4];
static uint64_t histogram[129], partitions;

static void grade(void) {
    unsigned cuts[8], count = 0, score = 0;
    /* Every binary split exactly once, modulo exchanging child labels.
       Include the constant split; its gain is zero. */
    for (unsigned labels = 0; labels < (1u << (states - 1)); ++labels) {
        unsigned mask = cells[0];
        for (unsigned c = 1; c < states; ++c)
            if (labels & (1u << (c - 1))) mask |= cells[c];
        cuts[count++] = mask;
    }
    for (unsigned omitted = 0; omitted < n; ++omitted) {
        unsigned maximum = 0;
        for (unsigned c = 0; c < count; ++c)
            if (gains[cuts[c]][omitted] > maximum)
                maximum = gains[cuts[c]][omitted];
        score += maximum;
    }
    ++partitions;
    ++histogram[score];
    if (partitions == 1 || score > best) {
        best = score;
        for (unsigned c = 0; c < states; ++c) witness[c] = cells[c];
    }
}

static void visit(unsigned x, unsigned used) {
    if (x == universe_size) {
        if (used == states) grade();
        return;
    }
    if (used + universe_size - x < states) return;
    unsigned bit = 1u << x;
    for (unsigned c = 0; c < used; ++c) {
        cells[c] |= bit;
        visit(x + 1, used);
        cells[c] ^= bit;
    }
    if (used < states) {
        cells[used] = bit;
        visit(x + 1, used + 1);
        cells[used] = 0;
    }
}

int main(int argc, char **argv) {
    if (argc != 3) return 2;
    n = (unsigned)atoi(argv[1]);
    states = (unsigned)atoi(argv[2]);
    if (n < 2 || n > 4 || states < 1 || states > 4) return 2;
    universe_size = 1u << n;
    for (unsigned mask = 0; mask < (1u << universe_size); ++mask) {
        int signed_counts[4] = {0, 0, 0, 0};
        for (unsigned x = 0; x < universe_size; ++x)
            if (mask & (1u << x))
                for (unsigned j = 0; j < n; ++j)
                    signed_counts[j] += (x & (1u << j)) ? 1 : -1;
        for (unsigned omitted = 0; omitted < n; ++omitted) {
            unsigned gain = 0;
            for (unsigned j = 0; j < n; ++j)
                if (j != omitted) gain += (unsigned)abs(signed_counts[j]);
            gains[mask][omitted] = (unsigned char)gain;
        }
    }
    cells[0] = 1;
    visit(1, 1);
    printf("%llu %u\n", (unsigned long long)partitions, best);
    for (unsigned c = 0; c < states; ++c) printf("%u ", witness[c]);
    printf("\n");
    for (unsigned score = 0; score < 129; ++score)
        if (histogram[score])
            printf("%u %llu\n", score, (unsigned long long)histogram[score]);
    return 0;
}
"""


def validate_parameters(source_bits: int, parent_states: int) -> None:
    if not 2 <= source_bits <= 4 or not 1 <= parent_states <= 4:
        raise ValueError("supported domain: 2..4 source bits, 1..4 parent states")


def stirling_second_kind(n: int, k: int) -> int:
    """Independent expected partition count, using the Stirling recurrence."""
    row = [1] + [0] * k
    for _ in range(n):
        row = [0] + [row[j - 1] + j * row[j] for j in range(1, k + 1)]
    return row[k]


def parent_partitions(source_count: int, states: int):
    """Unlabeled nonempty cells in increasing order of their least source."""
    cells = [1] + [0] * (states - 1)

    def visit(x: int, used: int):
        if x == source_count:
            if used == states:
                yield tuple(cells)
            return
        if used + source_count - x < states:
            return
        for c in range(used):
            cells[c] |= 1 << x
            yield from visit(x + 1, used)
            cells[c] ^= 1 << x
        if used < states:
            cells[used] = 1 << x
            yield from visit(x + 1, used + 1)
            cells[used] = 0

    yield from visit(1, 1)


def child_cuts(cells: tuple[int, ...]):
    """Represent each child split by the union containing the first cell."""
    for labels in itertools.product((False, True), repeat=len(cells) - 1):
        yield cells[0] | sum(cell for cell, selected in zip(cells[1:], labels)
                             if selected)


def coordinate_imbalance(mask: int, source_bits: int) -> tuple[int, ...]:
    return tuple(abs(sum(1 if x & (1 << j) else -1
                         for x in range(1 << source_bits) if mask & (1 << x)))
                 for j in range(source_bits))


def cut_gains(mask: int, source_bits: int) -> tuple[int, ...]:
    imbalance = coordinate_imbalance(mask, source_bits)
    return tuple(sum(imbalance) - imbalance[omitted]
                 for omitted in range(source_bits))


def score_partition(cells: tuple[int, ...], source_bits: int) -> int:
    gain_vectors = [cut_gains(mask, source_bits) for mask in child_cuts(cells)]
    return sum(max(g[omitted] for g in gain_vectors)
               for omitted in range(source_bits))


def search_python(source_bits: int = 4, parent_states: int = 4) -> dict:
    """Transparent reference; the full n=4,k=4 run is intentionally slow."""
    validate_parameters(source_bits, parent_states)
    histogram = Counter()
    best, witness = -1, None
    for cells in parent_partitions(1 << source_bits, parent_states):
        gain = score_partition(cells, source_bits)
        histogram[gain] += 1
        if gain > best:
            best, witness = gain, cells
    return {"partitions": sum(histogram.values()), "best_gain": best,
            "witness_masks": witness, "gain_histogram": dict(sorted(histogram.items()))}


def search_native(compiler: str, source_bits: int = 4, parent_states: int = 4) -> dict:
    """Build and execute the embedded scalar C99 search in a temporary folder."""
    validate_parameters(source_bits, parent_states)
    executable = shutil.which(compiler)
    if not executable:
        raise ValueError(f"compiler not found: {compiler}")
    version = subprocess.run([executable, "--version"], check=True, text=True,
                             capture_output=True).stdout.splitlines()[0]
    with tempfile.TemporaryDirectory(prefix="context-exact-chain-") as temporary:
        source = Path(temporary) / "search.c"
        binary = Path(temporary) / "search.exe"
        source.write_text(NATIVE_SOURCE, encoding="utf-8", newline="\n")
        subprocess.run([executable, "-O3", "-std=c99", str(source), "-o", str(binary)],
                       check=True, capture_output=True, text=True)
        start = time.perf_counter()
        output = subprocess.run([str(binary), str(source_bits), str(parent_states)],
                                check=True, capture_output=True, text=True).stdout
        duration = time.perf_counter() - start
    lines = output.splitlines()
    count, gain = map(int, lines[0].split())
    return {
        "partitions": count,
        "best_gain": gain,
        "witness_masks": tuple(map(int, lines[1].split())),
        "gain_histogram": dict(tuple(map(int, line.split())) for line in lines[2:]),
        "compiler": version,
        "native_source_sha256": hashlib.sha256(NATIVE_SOURCE.encode()).hexdigest(),
        "native_search_seconds": round(duration, 6),
    }


def grade_witness(cells: tuple[int, ...], source_bits: int = 4) -> dict:
    """Independent decoder construction and outcome-by-outcome grading.

    Exhaust all ordered child assignments, including constant assignments.  For
    each assignment, construct coordinate-majority decoders directly from the
    assigned source strings, without using the signed-count gain identity.
    """
    full_mask = (1 << (1 << source_bits)) - 1
    if not cells or any(not cell for cell in cells):
        raise ValueError("parent cells must be nonempty")
    if sum(cell.bit_count() for cell in cells) != (1 << source_bits):
        raise ValueError("parent cells must cover each source exactly once")
    union = 0
    for cell in cells:
        if cell & union or cell & ~full_mask:
            raise ValueError("parent cells must be disjoint source subsets")
        union |= cell
    if union != full_mask:
        raise ValueError("parent cells must cover every source")
    source_to_parent = [next(c for c, mask in enumerate(cells) if mask & (1 << x))
                        for x in range(1 << source_bits)]
    branches = []
    for omitted in range(source_bits):
        coordinates = [j for j in range(source_bits) if j != omitted]
        optimum = None
        for labels in itertools.product((0, 1), repeat=len(cells)):
            words = []
            for label in (0, 1):
                sources = [x for x, parent in enumerate(source_to_parent)
                           if labels[parent] == label]
                words.append([int(sum((x >> j) & 1 for x in sources) * 2 > len(sources))
                              for j in coordinates])
            errors = sum(((x >> j) & 1) != words[labels[parent]][index]
                         for x, parent in enumerate(source_to_parent)
                         for index, j in enumerate(coordinates))
            candidate = {"omitted_coordinate": omitted, "coordinates": coordinates,
                         "child_labels_by_parent": list(labels), "decoder_bits": words,
                         "errors": errors}
            if optimum is None or errors < optimum["errors"]:
                optimum = candidate
        branches.append(optimum)
    return {"parent_masks": list(cells), "source_to_parent": source_to_parent,
            "branches": branches, "errors": sum(b["errors"] for b in branches),
            "outcomes": (1 << source_bits) * source_bits * (source_bits - 1)}


def certificate(result: dict, source_bits: int = 4, parent_states: int = 4) -> dict:
    validate_parameters(source_bits, parent_states)
    baseline = (1 << (source_bits - 1)) * source_bits * (source_bits - 1)
    histogram = result["gain_histogram"]

    def integer_in_range(value, lower, upper):
        return type(value) is int and lower <= value <= upper

    expected = stirling_second_kind(1 << source_bits, parent_states)
    if not integer_in_range(result["partitions"], 1, expected):
        raise ValueError("partition count must be a positive integer within the search domain")
    if (not isinstance(histogram, dict) or not histogram
            or any(not integer_in_range(gain, 0, baseline)
                   or not integer_in_range(count, 1, expected)
                   for gain, count in histogram.items())):
        raise ValueError("gain histogram must have integer scores and positive integer counts")
    if not integer_in_range(result["best_gain"], 0, baseline):
        raise ValueError("best score must be an integer within the gain domain")
    if result["partitions"] != expected or sum(histogram.values()) != expected:
        raise ValueError("incomplete partition enumeration")
    if result["best_gain"] != max(histogram):
        raise ValueError("best score disagrees with histogram")
    # Both backends enumerate exactly this many nonempty cells, including when
    # a smaller partition could attain the same loss after refinement.
    if len(result["witness_masks"]) != parent_states:
        raise ValueError("witness must match the declared parent-state capacity")
    witness = grade_witness(result["witness_masks"], source_bits)
    if witness["errors"] != baseline - result["best_gain"]:
        raise ValueError("independent witness grading disagrees with search objective")
    return {
        "scope": "Checked exhaustive finite optimum; no novelty or LLM performance claim.",
        "source_bits": source_bits, "parent_state_capacity": parent_states,
        "child_state_capacity": 2, "subset_size": source_bits - 1,
        "distribution": "uniform independent source and omission, then uniform query in subset",
        "decoder_access": "child bit, omission, query; no parent state or source archive",
        "exact_error": str(Fraction(witness["errors"], witness["outcomes"])),
        "minimum_errors": witness["errors"], "outcomes": witness["outcomes"],
        "optimal_parent_partitions": result["gain_histogram"][result["best_gain"]],
        **{key: value for key, value in result.items() if key != "witness_masks"},
        "witness": witness,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    backend = parser.add_mutually_exclusive_group(required=True)
    backend.add_argument("--compiler", help="C99 compiler, e.g. clang or gcc")
    backend.add_argument("--python", action="store_true", help="slow reference backend")
    parser.add_argument("--source-bits", type=int, default=4)
    parser.add_argument("--parent-states", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = (search_native(args.compiler, args.source_bits, args.parent_states)
           if args.compiler else search_python(args.source_bits, args.parent_states))
    result = certificate(raw, args.source_bits, args.parent_states)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")


if __name__ == "__main__":
    main()
