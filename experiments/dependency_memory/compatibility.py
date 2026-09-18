"""Finite compatibility certificate for two successive memory bottlenecks.

X is four independent fair bits. First retain B1 bits. Then observe a uniform
three-element subset S of the four indices. Retain B2=1 bit. Finally a uniform
J in S is queried. No archive or other observations reveal X.

We exhaustively establish the least first-stage state count that permits the
optimal 1-bit, 3-coordinate error (1/4) for EVERY S. We do not solve the exact
minimum error for B1=2; we establish it is strictly greater than 1/4.
"""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path


def project(value: int, subset: tuple[int, ...]) -> int:
    return sum(((value >> position) & 1) << i for i, position in enumerate(subset))


def best_child_codes() -> tuple[int, list[tuple[int, int]]]:
    """All optimal 2-codeword decoders for three fair bits, exactly enumerated."""
    scores = {}
    for code in itertools.combinations(range(8), 2):
        scores[code] = sum(min((x ^ c).bit_count() for c in code) for x in range(8))
    minimum = min(scores.values())
    return minimum, [c for c, score in scores.items() if score == minimum]


def certificate() -> dict:
    subsets = list(itertools.combinations(range(4), 3))
    minimum_child_errors, codes = best_child_codes()
    assert minimum_child_errors == 6  # 6 / (8 input strings * 3 coordinates)
    assert len(codes) == 4 and all(a ^ b == 7 for a, b in codes)
    histogram = Counter()
    best_states, best_assignment, best_signatures = 17, None, None

    for assignment in itertools.product(codes, repeat=len(subsets)):
        signatures = []
        for x in range(16):
            signature = []
            for subset, code in zip(subsets, assignment):
                observed = project(x, subset)
                losses = [(observed ^ c).bit_count() for c in code]
                # Complementary length-three words imply no nearest-code tie.
                assert losses[0] != losses[1]
                signature.append(int(losses[1] < losses[0]))
            signatures.append(tuple(signature))
        needed = len(set(signatures))
        histogram[needed] += 1
        if needed < best_states:
            best_states = needed
            best_assignment = assignment
            best_signatures = signatures

    # Build and directly grade the 3-bit first-stage witness.
    labels = {signature: i for i, signature in enumerate(sorted(set(best_signatures)))}
    decoded_labels = {i: signature for signature, i in labels.items()}
    errors = trials = 0
    table = []
    for x, signature in enumerate(best_signatures):
        parent = labels[signature]
        table.append({"source": format(x, "04b"), "parent_state": parent,
                      "branch_labels": list(signature)})
        for branch, (subset, code) in enumerate(zip(subsets, best_assignment)):
            child = decoded_labels[parent][branch]
            reconstruction = code[child]
            for i, position in enumerate(subset):
                errors += ((x >> position) & 1) != ((reconstruction >> i) & 1)
                trials += 1

    return {
        "scope": "Finite exhaustive compatibility certificate; not a novelty claim.",
        "source_bits": 4,
        "possible_subsets": [list(s) for s in subsets],
        "child_memory_bits": 1,
        "child_codebooks_examined": math.comb(8, 2),
        "optimal_child_codebooks": [list(c) for c in codes],
        "branch_code_assignments_examined": sum(histogram.values()),
        "necessary_parent_states_histogram": dict(sorted(histogram.items())),
        "minimum_parent_states_to_attain_child_optimum": best_states,
        "minimum_parent_bits_to_attain_child_optimum": math.ceil(math.log2(best_states)),
        "child_optimal_error": str(Fraction(1, 4)),
        "first_cut_alone_2_bit_optimal_error": str(Fraction(3, 16)),
        "max_of_independent_cut_optima": str(Fraction(1, 4)),
        "two_stage_2_bit_then_1_bit_error_lower_bound": str(Fraction(49, 192)),
        "two_stage_2_bit_then_1_bit_exact_optimum": "not computed",
        "three_bit_parent_witness_error": str(Fraction(errors, trials)),
        "uniform_source_subset_query_outcomes": trials,
        "witness_branch_codebooks": [list(c) for c in best_assignment],
        "witness_encoder_table": table,
    }


def main() -> None:
    result = certificate()
    destination = Path(__file__).parent / "results" / "compatibility_certificate.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "witness_encoder_table"}, indent=2))


if __name__ == "__main__":
    main()
