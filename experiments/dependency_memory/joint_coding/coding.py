"""Exact witnesses for joint coding in the existing delayed-query block family.

No provider calls or third-party packages. The finite code is an achievable
construction, NOT an exhaustive search or a two-block optimality certificate.
The rational test channel certifies ingredients of an asymptotic achievability
proof; it is NOT an implemented finite-length encoder at that distortion.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import product
import json
from math import log2
from pathlib import Path


# Bit o of a word is the child bit returned on omission o. Coordinate zero is
# the least significant bit of both a source word and a branch-decision word.
CODEBOOK = tuple(sorted(
    [(a, b) for a in (0, 15) for b in (0, 1, 14, 15)]
    + [(1, 15), (14, 15)]
    + [(a, 0) for a in (3, 5, 6, 9, 10, 12)]
))
SIGNATURES = (0, 3, 5, 6, 9, 10, 12, 15)


def fraction_record(value: Fraction) -> dict:
    return {"numerator": value.numerator, "denominator": value.denominator}


def branch_cost(source: int, word: int) -> int:
    """Number of errors on all 12 omission/query routes in one block."""
    total = 0
    for omitted in range(4):
        ones = source.bit_count() - ((source >> omitted) & 1)
        total += 3 - ones if (word >> omitted) & 1 else ones
    return total


def majority_signature(source: int) -> int:
    return sum((source.bit_count() - ((source >> o) & 1) >= 2) << o
               for o in range(4))


def validate_codebook(codebook: tuple) -> None:
    if not 1 <= len(codebook) <= 16 or len(set(codebook)) != len(codebook):
        raise ValueError("A four-bit parent needs 1..16 distinct codewords")
    if any(len(pair) != 2 or any(type(a) is not int or not 0 <= a < 16
                                 for a in pair) for pair in codebook):
        raise ValueError("Each codeword must contain two four-bit branch words")


def parent_table(codebook: tuple = CODEBOOK) -> list[int]:
    validate_codebook(codebook)
    # Row x + 16*y is the parent message for source blocks (x,y).
    return [min(range(len(codebook)), key=lambda m:
                branch_cost(x, codebook[m][0]) + branch_cost(y, codebook[m][1]))
            for y in range(16) for x in range(16)]


def grade_table(table: list[int], codebook: tuple = CODEBOOK) -> dict:
    """Directly execute every source/block/omission/query outcome."""
    validate_codebook(codebook)
    if len(table) != 256 or any(type(m) is not int or not 0 <= m < len(codebook)
                               for m in table):
        raise ValueError("Expected 256 admissible parent messages")
    branch_errors = [[0] * 4 for _ in range(2)]
    column_errors = [0] * 16
    for y in range(16):
        for x in range(16):
            message = table[x + 16 * y]
            for block, source in enumerate((x, y)):
                for omitted in range(4):
                    child = (codebook[message][block] >> omitted) & 1
                    for query in range(4):
                        if query != omitted:
                            error = child != ((source >> query) & 1)
                            branch_errors[block][omitted] += error
                            column_errors[y] += error
    errors = sum(column_errors)
    return {"errors": errors, "outcomes": 6144,
            "distortion": fraction_record(Fraction(errors, 6144)),
            "branch_errors": branch_errors,
            "errors_by_second_source": column_errors,
            "message_occupancies": [table.count(m) for m in range(len(codebook))]}


def test_channel() -> list[list[Fraction]]:
    """A rational single-letter distribution, not an operational memory code.

    Preserve signatures for source weights other than two. On weight two,
    return its exact signature with probability 19/24, otherwise return either
    constant branch word with probability 5/48 each.
    """
    channel = []
    for x in range(16):
        row = [Fraction(0)] * len(SIGNATURES)
        signature = majority_signature(x)
        if x.bit_count() == 2:
            row[SIGNATURES.index(signature)] = Fraction(19, 24)
            row[0] = row[-1] = Fraction(5, 48)
        else:
            row[SIGNATURES.index(signature)] = Fraction(1)
        channel.append(row)
    return channel


def channel_certificate() -> dict:
    channel = test_channel()
    marginal = [sum(row[a] for row in channel) / 16 for a in range(8)]
    distortion = sum(channel[x][a] * branch_cost(x, word)
                     for x in range(16) for a, word in enumerate(SIGNATURES)) / 192
    # All logarithms reduce to I=(371-40*log2(5)-95*log2(3))/64.
    # Thus I<2 iff the following EXACT integer inequality holds.
    lhs, rhs = 2**243, 5**40 * 3**95
    assert lhs < rhs
    return {
        "reproduction_words": list(SIGNATURES),
        "conditional_probability_denominator": 48,
        "conditional_probability_numerators":
            [[int(48 * p) for p in row] for row in channel],
        "output_probabilities": [fraction_record(p) for p in marginal],
        "distortion": fraction_record(distortion),
        "mutual_information_bits": "(371 - 40*log2(5) - 95*log2(3))/64",
        "mutual_information_less_than_two": {
            "equivalent_inequality": "2^243 < 5^40 * 3^95",
            "left_integer": lhs, "right_integer": rhs, "holds": lhs < rhs},
        "operational_status": "asymptotic existence via standard rate-distortion theorem",
        "finite_length_encoder_at_this_distortion_implemented": False,
    }


def certificate() -> dict:
    table = parent_table()
    finite = grade_table(table)
    product_codebook = tuple(product((0, 1, 14, 15), repeat=2))
    product_grade = grade_table(parent_table(product_codebook), product_codebook)
    fibers = Counter(majority_signature(x) for x in range(16))
    return {
        "schema": "joint-block-coding-v1",
        "model": "independent uniform four-bit blocks; late uniform block/omission/query",
        "evidence_status": "exact achievable witnesses; no joint-optimum claim",
        "finite_witness": {"blocks": 2, "parent_bits": 4, "child_bits": 1,
                           "codebook": [list(word) for word in CODEBOOK],
                           "parent_table_x_plus_16y": table, **finite},
        "product_reference": {"codebook": [list(word) for word in product_codebook],
                              "errors": product_grade["errors"],
                              "distortion": product_grade["distortion"]},
        "finite_improvement": fraction_record(Fraction(product_grade["errors"] - finite["errors"], 6144)),
        "asymptotic_rate_two_witness": channel_certificate(),
        "optimal_unsigned_signature_fibers":
            [{"signature": a, "sources": fibers[a]} for a in sorted(fibers)],
        "vanishing_excess_rate_threshold": {
            "bits_per_block": "4 - (5/8)*log2(5)",
            "exact_attainment_bits_per_block": 3,
            "evidence": "analytic argument in research/JOINT_BLOCK_CODING_2026-09-21.md",
            "proof_not_established_by_finite_enumeration_alone": True},
    }


def report(result: dict) -> str:
    witness = result["finite_witness"]
    rate = (371 - 40 * log2(5) - 95 * log2(3)) / 64
    return f"""# Joint block coding: exact witnesses

Generated by `joint_coding/coding.py`. These are mathematical constructions,
not model trials or a search certificate for the two-block optimum.

| Construction | Parent capacity | Error | Evidence |
|---|---|---|---|
| Product of two optimal single-block codes | 4 bits | 9/32 | 1728/6144 direct outcomes |
| Joint two-block witness | 4 bits | 283/1024 | {witness['errors']}/6144 direct outcomes |
| Rational test channel and block coding | 2 bits/block | limsup at most 101/384 | Exact channel and integer rate inequality; asymptotic coding theorem |

The finite improvement is 5/1024. Repeating the joint code gives error
283/1024 for even block counts; an odd leftover gives 283/1024 + 5/(1024k).
This proves that the one-block 9/32 optimum does not extend unchanged.

The test channel has I(X;A) = (371 - 40 log2(5) - 95 log2(3))/64,
approximately {rate:.9f} bits. Its strict rate slack is certified by
2^243 < 5^40 * 3^95, not floating-point tolerance. No finite-length code
attaining 101/384 is supplied.

The analytic vanishing-excess threshold is 4 - (5/8)log2(5), approximately
{4 - 5 * log2(5) / 8:.9f} bits/block. Exact error 1/4 at finite k still
requires 3k bits. See the [proof and literature boundary](../../../research/JOINT_BLOCK_CODING_2026-09-21.md).

Per-block/omission error counts: {witness['branch_errors']}.
Errors summed over the first source for each second source 0..15:
{witness['errors_by_second_source']}.

Novelty and external proof review remain open. No provider calls were made.
"""


def main() -> None:
    result = certificate()
    output = Path(__file__).parent.parent / "results"
    (output / "joint_block_certificate.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    (output / "joint_block_report.md").write_text(
        report(result), encoding="utf-8", newline="\n")
    print("Joint witness: 1698/6144 = 283/1024; asymptotic upper bound: 101/384")


if __name__ == "__main__":
    main()
