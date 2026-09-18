"""Checks for exploratory compatibility scaling derivations, September 18, 2026.

Independent finite checks of an analytic bound, not an exact chain optimizer,
novelty certificate, or LLM experiment. Run this file to regenerate its JSON.
"""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path

from compatibility import best_child_codes, project


def child_error(m: int) -> Fraction:
    if m < 1 or m % 2 != 1:
        raise ValueError("Child length must be positive and odd")
    return Fraction(1, 2) - Fraction(math.comb(m - 1, (m - 1) // 2), 2**m)


def check_child_codebooks(m: int) -> dict:
    """Enumerate all pairs, independently of the analytic distance formula."""
    words = range(2**m)
    scores = {
        pair: sum(min((x ^ pair[0]).bit_count(), (x ^ pair[1]).bit_count())
                  for x in words)
        for pair in itertools.combinations(words, 2)
    }
    best = min(scores.values())
    optimal = [pair for pair, loss in scores.items() if loss == best]
    assert Fraction(best, m * 2**m) == child_error(m)
    assert len(optimal) == 2 ** (m - 1)
    assert all(a ^ b == 2**m - 1 for a, b in optimal)
    if m == 3:
        assert min(loss for (a, b), loss in scores.items() if a ^ b != 7) == 8
    return {"child_bits": m, "codebooks_checked": len(scores),
            "optimal_codebooks": len(optimal), "error": str(child_error(m))}


def check_family(n: int) -> dict:
    """Grade three witnesses directly over all source/subset/query outcomes."""
    if n < 4 or n % 2:
        raise ValueError("Source length must be even and at least four")
    signatures = set()
    child_errors = global_errors = first_cut_errors = 0
    fourier_diagonal = [0] * n
    for x in itertools.product((-1, 1), repeat=n):
        total = sum(x)
        signature = tuple(1 if total - x[i] > 0 else -1 for i in range(n))
        signatures.add(signature)
        global_prediction = 1 if total >= 0 else -1
        first_prediction = 1 if sum(x[:-1]) > 0 else -1
        for i in range(n):
            fourier_diagonal[i] += signature[i] * math.prod(x[:i] + x[i + 1:])
            for j in range(n):
                if j != i:
                    child_errors += signature[i] != x[j]
                    global_errors += global_prediction != x[j]
                    first_cut_errors += (x[-1] if j == n - 1 else first_prediction) != x[j]
    outcomes = 2**n * n * (n - 1)
    target = child_error(n - 1)
    child_actual = Fraction(child_errors, outcomes)
    global_actual = Fraction(global_errors, outcomes)
    first_actual = Fraction(first_cut_errors, outcomes)
    gap_upper = Fraction(math.comb(n - 2, (n - 2) // 2), n * 2 ** (n - 1))
    coefficient = Fraction((-1) ** ((n - 2) // 2) * math.comb(n - 2, (n - 2) // 2), 2 ** (n - 2))
    assert child_actual == target
    assert first_actual == Fraction(n - 1, n) * target < target
    assert global_actual - target == gap_upper
    assert len(signatures) == math.comb(n, n // 2) + 2
    assert all(Fraction(value, 2**n) == coefficient for value in fourier_diagonal)
    assert all(tuple(-v for v in signature) in signatures for signature in signatures)
    return {
        "source_bits": n,
        "directly_graded_outcomes": outcomes,
        "child_optimal_error": str(target),
        "isolated_first_cut_two_bit_witness_error": str(first_actual),
        "analytic_parent_states_lower_bound_at_exact_target": 2 * n,
        "analytic_parent_bits_lower_bound_at_exact_target": (2 * n - 1).bit_length(),
        "unsigned_majority_witness_parent_states": len(signatures),
        "unsigned_majority_witness_parent_bits": (len(signatures) - 1).bit_length(),
        "unsigned_majority_witness_chain_error": str(child_actual),
        "global_majority_one_bit_chain_error": str(global_actual),
        "two_bit_chain_excess_error_upper_bound": str(gap_upper),
        "top_fourier_coefficient_unsigned_branch": str(coefficient),
        "exact_minimum_parent_states": "not computed here",
        "exact_two_bit_chain_error": "not computed",
    }


def check_block_entropy() -> dict:
    """Exact integer certificate for every possible optimal branch-code choice.

    H(Y) = 4 - log2(product(fiber_size**fiber_size)) / 16. Thus a
    product at most 2**24 certifies H(Y) >= 5/2 without floating point.
    """
    subsets = list(itertools.combinations(range(4), 3))
    _, codes = best_child_codes()
    maximum_product = 0
    minimum_states = 16
    worst_fibers = None
    assignments = 0
    for assignment in itertools.product(codes, repeat=4):
        fibers = Counter(
            tuple(int((project(x, subset) ^ code[1]).bit_count()
                      < (project(x, subset) ^ code[0]).bit_count())
                  for subset, code in zip(subsets, assignment))
            for x in range(16)
        )
        product = math.prod(size**size for size in fibers.values())
        minimum_states = min(minimum_states, len(fibers))
        if product > maximum_product:
            maximum_product = product
            worst_fibers = sorted(fibers.values())
        assignments += 1
    assert assignments == 256 and minimum_states == 8
    assert maximum_product == 5**10 < 2**24
    # h2(3/128) < 11/64 iff this integer inequality holds.
    assert 3**3 * 125**125 > 2**874
    # At delta = 1/512, the information lower bound is strictly over 2.
    assert Fraction(5, 2) - 168 * Fraction(1, 512) - Fraction(11, 64) == 2
    return {
        "optimal_branch_assignments_checked": assignments,
        "minimum_signature_states": minimum_states,
        "maximum_fiber_product": maximum_product,
        "entropy_minimizing_fiber_sizes": worst_fibers,
        "certified_signature_entropy_lower_bound_bits": "5/2",
        "entropy_certificate_integer_bound": "5**10 < 2**24",
        "binary_entropy_certificate": "3**3 * 125**125 > 2**874 implies h2(3/128) < 11/64",
        "block_family_exact_target_parent_bits": "3*k",
        "block_family_two_bit_per_block_excess_error_strict_lower_bound": "1/512",
        "scope": "The certificates support the general information argument in the note; they do not enumerate joint encoders across k blocks.",
    }


def certificate() -> dict:
    return {
        "scope": "Independent finite checks of an exploratory analytic derivation; novelty unresolved.",
        "child_codebook_checks": [check_child_codebooks(m) for m in (1, 3, 5, 7)],
        "leave_one_out_checks": [check_family(n) for n in (4, 6, 8, 10)],
        "block_entropy_check": check_block_entropy(),
        "limitation": "General bounds use proofs in the note. The leave-one-out family has vanishing excess error; the separate block family has a uniform positive lower bound. Neither exact two-bit chain optimum nor LLM outcomes are computed.",
    }


if __name__ == "__main__":
    result = certificate()
    output = Path(__file__).parent / "results" / "compatibility_scaling_certificate.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
