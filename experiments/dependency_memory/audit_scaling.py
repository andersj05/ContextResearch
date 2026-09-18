"""Independent tuple/sign audit of the block proof's finite ingredients.

Does not import the original integer projection, codebook, or scaling code.
Checks include oriented decoders, repeated codewords, and abstract paired fibers.
"""

from collections import Counter
from fractions import Fraction
from itertools import product
import json
import math
from pathlib import Path


def compositions(total, parts):
    if parts == 1:
        yield (total,)
    else:
        for first in range(1, total - parts + 2):
            for rest in compositions(total - first, parts - 1):
                yield (first,) + rest


def certificate():
    triples = list(product((-1, 1), repeat=3))
    optimal = nonoptimal = None
    optimal_count = 0
    for a, b in product(triples, repeat=2):
        losses = [(sum(u != v for u, v in zip(x, a)),
                   sum(u != v for u, v in zip(x, b))) for x in triples]
        total = sum(min(pair) for pair in losses)
        if all(u == -v for u, v in zip(a, b)):
            optimal = total if optimal is None else min(optimal, total)
            optimal_count += 1
            assert total == 6 and all(abs(left - right) >= 1 for left, right in losses)
        else:
            nonoptimal = total if nonoptimal is None else min(nonoptimal, total)
            assert total >= 8

    sources = list(product((-1, 1), repeat=4))
    # For each omitted coordinate, construct all signed majorities directly.
    functions = []
    for omitted in range(4):
        branch = []
        for signs in triples:
            values = tuple(1 if sum(s * x[j] for s, j in zip(
                signs, (j for j in range(4) if j != omitted))) > 0 else -1
                for x in sources)
            # Unique cubic terms prove rank four for any branch assignment.
            for missing in range(4):
                coefficient = Fraction(sum(value * math.prod(
                    x[j] for j in range(4) if j != missing)
                    for x, value in zip(sources, values)), 16)
                assert abs(coefficient) == (Fraction(1, 2) if missing == omitted else 0)
            branch.append(values)
        functions.append(branch)

    histogram = Counter()
    maximum_product = 0
    for assignment in product(*functions):
        fibers = Counter(zip(*assignment))
        assert all(fibers[tuple(-v for v in y)] == size for y, size in fibers.items())
        histogram[len(fibers)] += 1
        maximum_product = max(maximum_product, math.prod(size**size for size in fibers.values()))
    assert min(histogram) == 8 and maximum_product == 5**10

    # A second optimization knows only antipodal pairing and at least 8 fibers.
    paired = [sizes for count in range(4, 9) for sizes in compositions(8, count)]
    abstract_maximum = max(math.prod(size ** (2 * size) for size in sizes) for sizes in paired)
    assert abstract_maximum == maximum_product
    assert maximum_product < 2**24
    assert 3**3 * 125**125 > 2**874
    return {
        "scope": "Local audit using independent formulations; not external peer review or a novelty certificate.",
        "ordered_child_decoders_including_repeated_words": 64,
        "optimal_ordered_child_decoders": optimal_count,
        "optimal_child_error": str(Fraction(optimal, 24)),
        "noncomplementary_child_error_lower_bound": str(Fraction(nonoptimal, 24)),
        "signed_majority_assignments": sum(histogram.values()),
        "signature_state_histogram": dict(sorted(histogram.items())),
        "maximum_signature_fiber_product": maximum_product,
        "abstract_paired_compositions_checked": len(paired),
        "abstract_paired_maximum_fiber_product": abstract_maximum,
        "entropy_lower_bound_exact": "4 - (5/8)*log2(5) > 5/2",
        "block_claims": "3*k parent bits necessary and sufficient at error 1/4; at 2*k bits error > 1/4 + 1/512.",
        "scope_correction": "The strict leave-one-out gap requires even n >= 4, not n = 2.",
        "unresolved": ["Novelty", "External proof review", "Exact two-bit chain optimum", "LLM relevance"],
    }


if __name__ == "__main__":
    result = certificate()
    (Path(__file__).parent / "results" / "scaling_audit_certificate.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
