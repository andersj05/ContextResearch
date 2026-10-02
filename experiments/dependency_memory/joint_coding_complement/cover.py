"""A three-block converse for complementary, possibly coordinate-dependent endpoints.

The per-source inequality and top-64 column sum are described in the research
note. Targets are fixed exact rational witnesses chosen by an exploratory grid;
neither an optimizer nor an exhaustive codebook search is trusted by the proof.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
from itertools import combinations_with_replacement, product
import json
from pathlib import Path

from experiments.dependency_memory.joint_coding import decoder_frontier as frontier
from experiments.dependency_memory.joint_coding_finite3 import witness

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE.parent / "results/joint_three_block_complement_2026-10-01.json"
SCALE = 4


@lru_cache(None)
def orbits():
    indices = tuple(frontier.PAIR_INDEX[(a, 7-a)] for a in range(4))
    maps = frontier.symmetry_maps()
    all_tables = set(product(indices, repeat=4))
    seen, result = set(), []
    for table in product(indices, repeat=4):
        if table in seen:
            continue
        orbit = set()
        for mapping in maps:
            transformed = [None] * 4
            for o, (target, pairs) in enumerate(mapping):
                transformed[target] = pairs[table[o]]
            orbit.add(tuple(transformed))
        if not orbit.issubset(all_tables) or seen.intersection(orbit):
            raise ValueError("Complementary decoder orbit partition failed")
        seen.update(orbit)
        result.append((table, tuple(sorted(orbit))))
    if len(seen) != 256 or len(result) != 6:
        raise ValueError("Complementary decoder coverage changed")
    return tuple(result)


def block(table, targets):
    if len(table) != 4 or any(type(i) is not int or not 0 <= i < 36 for i in table):
        raise ValueError("Expected four unordered decoder-pair indices")
    if any((frontier.PAIRS[i][0] ^ frontier.PAIRS[i][1]) != 7 for i in table):
        raise ValueError("Noncomplementary endpoints are outside the proved family")
    if len(targets) != 16 or any(type(t) is not int or t < 0 for t in targets):
        raise ValueError("Expected sixteen nonnegative quarter-unit targets")
    loss = frontier.loss_matrix(tuple(table))
    ideal = tuple(min(range(16), key=lambda a: row[a]) for row in loss)
    if any(row.count(min(row)) != 1 for row in loss):
        raise ValueError("Complementary odd-length endpoints must have a unique ideal word")
    zero_fibers = Counter(ideal[x] for x, t in enumerate(targets) if t == 0)
    profiles = tuple(tuple(sorted(Counter(targets[x] - SCALE * (loss[x][a] - min(loss[x]))
                                          for x in range(16)).items())) for a in range(16))
    return {"table": tuple(table), "targets": tuple(targets), "loss": loss, "ideal": ideal,
            "profiles": profiles, "zero_fibers": tuple(zero_fibers[a] for a in range(16)),
            "oracle_sum": sum(map(min, loss)), "target_sum_units": sum(targets)}


@lru_cache(None)
def convolve(left, right):
    result = Counter()
    for a, n in left:
        for b, m in right:
            result[a+b] += n*m
    return tuple(sorted(result.items()))


@lru_cache(None)
def reward(left, middle, right):
    return sum(max(value, 0) * count for value, count in convolve(convolve(left, middle), right))


def bound(blocks):
    if len(blocks) != 3 or any(row["oracle_sum"] != 48 for row in blocks):
        raise ValueError("Expected three complementary four-bit blocks")
    histogram = Counter()
    for a, b, c in product(range(16), repeat=3):
        saving = reward(blocks[0]["profiles"][a], blocks[1]["profiles"][b], blocks[2]["profiles"][c])
        zero_mass = blocks[0]["zero_fibers"][a] * blocks[1]["zero_fibers"][b] * blocks[2]["zero_fibers"][c]
        histogram[saving + SCALE * zero_mass] += 1
    remaining, top_sum = 64, 0
    for value, count in sorted(histogram.items(), reverse=True):
        used = min(count, remaining)
        top_sum += used * value
        remaining -= used
        if remaining == 0:
            break
    if remaining or sum(histogram.values()) != 4096:
        raise ValueError("Decision-column cardinality changed")
    oracle = sum(row["oracle_sum"] for row in blocks) * 256
    target_units = sum(row["target_sum_units"] for row in blocks) * 256
    zero_mass = 1
    for row in blocks:
        zero_mass *= sum(row["zero_fibers"])
    lower_units = SCALE * oracle + target_units + SCALE * zero_mass - top_sum
    return {"oracle_errors": oracle, "target_sum_units": target_units, "zero_target_source_mass": zero_mass,
            "column_weight_histogram_units": dict(sorted(histogram.items())), "largest_64_column_sum_units": top_sum,
            "lower_error_units": lower_units, "integer_lower_errors": -(-lower_units // SCALE)}


def lower_bound(tables):
    """Return the proved common bound, rejecting decoders outside its scope."""
    if len(tables) != 3:
        raise ValueError("Expected three block decoder tables")
    for table in tables:
        block(tuple(table), (0,) * 16)
    return Fraction(40072, 147456)


def certificate():
    discovery = json.loads((HERE / "discovery.json").read_text(encoding="utf-8"))
    representatives = orbits()
    choices = discovery["selected_targets"]
    expected_types = list(combinations_with_replacement(range(6), 3))
    if [tuple(row["types"]) for row in choices] != expected_types:
        raise ValueError("Missing or reordered mixed orbit case")
    rows = []
    for choice in choices:
        if len(choice["targets"]) != 3:
            raise ValueError("Expected three target arrays per orbit case")
        blocks = [block(representatives[i][0], target) for i, target in zip(choice["types"], choice["targets"])]
        checked = bound(blocks)
        if checked["lower_error_units"] != choice["lower_error_units"]:
            raise ValueError("Exploratory selected witness does not reproduce")
        rows.append({"types": choice["types"], "targets_units": choice["targets"], **checked})
    lower = min(row["integer_lower_errors"] for row in rows)
    book = witness.selected_book()
    upper = witness.grade(witness.parent_table(book), book)["errors"]
    saved_upper = json.loads((HERE.parent / "results/joint_three_block_certificate_2026-10-01.json").read_text())
    if (lower != 40072 or upper != saved_upper["witness"]["errors"] or upper != 40529
            or saved_upper["codebook"] != json.loads(json.dumps(book))):
        raise ValueError("Saved finite interval changed")
    files = (HERE / "cover.py", HERE / "discover.py", HERE / "discovery.json", HERE / "test_cover.py",
             HERE.parent / "joint_coding/decoder_frontier.py", HERE.parent / "joint_coding_finite3/witness.py",
             HERE.parent / "joint_coding/coding.py", HERE.parent / "joint_coding_finite3/discovery.json",
             HERE.parent / "results/joint_three_block_certificate_2026-10-01.json")
    return {"version": "finite3_complementary_cover_v1", "date": "2026-10-01", "new_model_calls": 0,
            "evidence_class": "local analytic restricted converse with exact rational finite witnesses",
            "decoder_restriction": "The two three-bit prediction endpoints for every R/O branch are complementary; prediction may depend on late J.",
            "covers_arbitrary_final_decoders": False, "parent_states_at_most": 64, "child_states_at_most": 2,
            "blocks": 3, "target_unit_denominator": SCALE,
            "source_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            "decoder_tables_per_block": 256, "ordered_three_block_table_choices": 256**3,
            "decoder_orbits_per_block": 6, "mixed_orbit_cases": 56,
            "orbits": [{"representative": table, "pairs": [frontier.PAIRS[i] for i in table], "members": members,
                        "size": len(members)} for table, members in representatives],
            "cases": rows, "decision_columns_checked": 56 * 4096,
            "lower_errors": lower, "upper_errors": upper, "outcomes": 147456,
            "lower_fraction": str(Fraction(lower, 147456)), "upper_fraction": str(Fraction(upper, 147456)),
            "interval_width": str(Fraction(upper-lower, 147456)),
            "limits": "Complementary endpoints only; noncomplementary decoders remain open. Exact cover ingredients and selected rational witnesses are not exhaustive codebook optimization or target optimality. No finite optimum, unrestricted-frontier change, efficient encoder, model gain, novelty or priority claim. External proof review remains open."}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ("decoder_tables_per_block", "mixed_orbit_cases", "decision_columns_checked", "lower_errors", "upper_errors", "covers_arbitrary_final_decoders")}))


if __name__ == "__main__":
    main()
