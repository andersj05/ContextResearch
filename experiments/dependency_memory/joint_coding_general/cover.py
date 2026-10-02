"""All-decoder finite converse with ties and exact additive cover witnesses.

For zero-target sources, missing every ideal word costs at least one. A union
bound counts ideal incidence even when ideal words tie. Distinct columns with
the same entire source-loss vector can be identified for this average-error
objective. Neither reduction assumes a restricted parent encoder or updater.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
from itertools import combinations_with_replacement, product
import json
from pathlib import Path

from experiments.dependency_memory.joint_coding import decoder_frontier as frontier
from experiments.dependency_memory.joint_coding_complement import cover as complement
from experiments.dependency_memory.joint_coding_finite3 import witness

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DISCOVERY = HERE / "discovery.json"
OUTPUT = HERE.parent / "results/joint_three_block_general_2026-10-01.json"
SCALE = 4


def defect(table):
    return sum(3 if frontier.PAIRS[p][0] == frontier.PAIRS[p][1]
               else int((frontier.PAIRS[p][0] ^ frontier.PAIRS[p][1]) != 7) for p in table)


@lru_cache(None)
def census():
    counts, table_counts, groups = Counter(), Counter(), [[], [], [], []]
    digest = hashlib.sha256()
    for index, table, size in frontier.decoder_orbits():
        d = defect(table)
        counts[d] += 1
        table_counts[d] += size
        digest.update(f"{index}:{size}:{d}\n".encode("ascii"))
        if d <= 3:
            groups[d].append((index, table, size))
    if sum(counts.values()) != 4751 or sum(table_counts.values()) != 36**4:
        raise ValueError("All-decoder orbit coverage changed")
    return {"orbit_counts": dict(sorted(counts.items())), "table_counts": dict(sorted(table_counts.items())),
            "orbit_defect_digest_sha256": digest.hexdigest(), "groups": tuple(tuple(g) for g in groups)}


def near_cases(include_complementary=False):
    groups = census()["groups"]
    for types in combinations_with_replacement(range(4), 3):
        if sum(types) > 3 or (not include_complementary and sum(types) == 0):
            continue
        for a, b, c in product(*(groups[t] for t in types)):
            if (types[0] == types[1] and a[0] > b[0]) or (types[1] == types[2] and b[0] > c[0]):
                continue
            yield (a[0], b[0], c[0]), types


def unpack_target(code):
    if type(code) is not int or not 0 <= code < 2**20:
        raise ValueError("Expected a fixed twenty-bit mathematical target code")
    amplitude, mask = code & 15, code >> 4
    if amplitude > 8 or (amplitude == 0 and mask != 0):
        raise ValueError("Invalid quarter-unit target witness")
    return tuple(amplitude if (mask >> x) & 1 else 0 for x in range(16))


def pack_target(target):
    if len(target) != 16 or any(type(t) is not int or not 0 <= t <= 8 for t in target):
        raise ValueError("Expected sixteen bounded nonnegative quarter-unit targets")
    positive = set(target) - {0}
    if len(positive) > 1:
        raise ValueError("Saved witness format supports one positive amplitude")
    if not positive:
        return 0
    amplitude = positive.pop()
    return sum(2**x for x, t in enumerate(target) if t) * 16 + amplitude


@lru_cache(None)
def block(index, target_code):
    if type(index) is not int or not 0 <= index < 36**4:
        raise ValueError("Invalid decoder table index")
    table = frontier.decode_table(index)
    loss = frontier.loss_matrix(table)
    # Identify entire loss functions, not just equal histograms.
    columns = tuple(sorted({tuple(row[a] for row in loss) for a in range(16)}))
    oracle = tuple(min(row) for row in loss)
    target = unpack_target(target_code)
    if sum(oracle) != 48 + 4*defect(table):
        raise ValueError("Branch oracle-defect formula changed")
    profiles = Counter()
    for column in columns:
        scores = tuple(sorted(Counter(t - SCALE*(v-u) for t, v, u in zip(target, column, oracle)).items()))
        zero_ideal_incidence = sum(t == 0 and v == u for t, v, u in zip(target, column, oracle))
        profiles[scores, zero_ideal_incidence] += 1
    return {"index": index, "table": table, "target": target, "columns": columns, "oracle": oracle,
            "profiles": tuple(profiles.items()), "oracle_sum": sum(oracle), "target_sum_units": sum(target),
            "zero_sources": target.count(0), "binary": all(t in (0, SCALE) for t in target)}


@lru_cache(None)
def convolve(left, right):
    values = Counter()
    for a, n in left:
        for b, m in right:
            values[a+b] += n*m
    return tuple(sorted(values.items()))


@lru_cache(None)
def reward(sorted_profiles, binary):
    if binary:
        # A positive triple uses only scores 4, 0, -4; all <= -8 contribute zero.
        a, b, c = [dict(row) for row in sorted_profiles]
        ap, az, am = a.get(4, 0), a.get(0, 0), a.get(-4, 0)
        bp, bz, bm = b.get(4, 0), b.get(0, 0), b.get(-4, 0)
        cp, cz, cm = c.get(4, 0), c.get(0, 0), c.get(-4, 0)
        return SCALE * (3*ap*bp*cp + 2*(az*bp*cp + ap*bz*cp + ap*bp*cz)
                        + ap*bz*cz + az*bp*cz + az*bz*cp
                        + am*bp*cp + ap*bm*cp + ap*bp*cm)
    distribution = convolve(convolve(sorted_profiles[0], sorted_profiles[1]), sorted_profiles[2])
    return sum(max(score, 0)*n for score, n in distribution)


def bound(blocks):
    if len(blocks) != 3:
        raise ValueError("Expected three source blocks")
    histogram = Counter()
    binary = all(row["binary"] for row in blocks)
    for (a, na), (b, nb), (c, nc) in product(*(row["profiles"] for row in blocks)):
        saving = reward(tuple(sorted((a[0], b[0], c[0]))), binary)
        weight = saving + SCALE*a[1]*b[1]*c[1]
        histogram[weight] += na*nb*nc
    remaining, top = 64, 0
    for weight, count in sorted(histogram.items(), reverse=True):
        used = min(remaining, count)
        top += used*weight
        remaining -= used
        if remaining == 0:
            break
    zero_source_mass = 1
    columns = 1
    for row in blocks:
        zero_source_mass *= row["zero_sources"]
        columns *= len(row["columns"])
    if sum(histogram.values()) != columns:
        raise ValueError("Distinct source-loss column count changed")
    oracle = sum(row["oracle_sum"] for row in blocks)*256
    target = sum(row["target_sum_units"] for row in blocks)*256
    lower_units = SCALE*oracle + target + SCALE*zero_source_mass - top
    return {"oracle_errors": oracle, "target_sum_units": target, "zero_target_source_mass": zero_source_mass,
            "column_weight_histogram_units": dict(sorted(histogram.items())), "distinct_cost_columns": columns,
            "largest_64_column_sum_units": top, "lower_error_units": lower_units,
            "integer_lower_errors": -(-lower_units // SCALE)}


def certificate():
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    rows = discovery["selected_cases"]
    expected = list(near_cases())
    if len(rows) != 46436 or [tuple(row[:3]) for row in rows] != [key for key, _ in expected]:
        raise ValueError("Missing, duplicate or reordered noncomplementary mixed case")
    histogram, digest, total_columns, minima = Counter(), hashlib.sha256(), 0, []
    for row in rows:
        if len(row) != 7:
            raise ValueError("Malformed selected target witness row")
        blocks = [block(index, code) for index, code in zip(row[:3], row[3:6])]
        checked = bound(blocks)
        lower = checked["integer_lower_errors"]
        if lower != row[6] or lower < 40072:
            raise ValueError("Selected all-decoder cover does not certify its declared floor")
        histogram[lower] += 1
        total_columns += checked["distinct_cost_columns"]
        digest.update((json.dumps([*row[:6], checked["lower_error_units"], checked["largest_64_column_sum_units"],
                                   checked["zero_target_source_mass"], checked["distinct_cost_columns"]], separators=(",", ":")) + "\n").encode("ascii"))
        if lower == 40072:
            minima.append(row[:3])
    previous = complement.certificate()
    if previous["lower_errors"] != 40072 or previous["mixed_orbit_cases"] != 56:
        raise ValueError("Previously certified complementary cases changed")
    book = witness.selected_book()
    upper = witness.grade(witness.parent_table(book), book)["errors"]
    if upper != 40529:
        raise ValueError("Unchanged upper witness changed")
    c = census()
    files = (HERE / "cover.py", HERE / "discover.py", HERE / "discovery.json", HERE / "test_cover.py",
             HERE.parent / "joint_coding/decoder_frontier.py", HERE.parent / "joint_coding_complement/cover.py",
             HERE.parent / "results/joint_three_block_complement_2026-10-01.json",
             HERE.parent / "joint_coding_finite3/witness.py", HERE.parent / "joint_coding_finite3/discovery.json",
             HERE.parent / "results/joint_three_block_certificate_2026-10-01.json")
    return {"version": "finite3_all_decoder_cover_v1", "date": "2026-10-01", "new_model_calls": 0,
            "evidence_class": "local analytic all-decoder finite converse with exact rational witnesses",
            "covers_arbitrary_final_decoders": True, "parent_states_at_most": 64, "child_states_at_most": 2,
            "blocks": 3, "source_symbols": 4096, "target_unit_denominator": SCALE,
            "source_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            "decoder_tables_per_block": 36**4, "ordered_decoder_table_triples": 36**12,
            "per_block_orbits": 4751, "orbit_counts_by_defect": c["orbit_counts"],
            "table_counts_by_defect": c["table_counts"], "orbit_defect_digest_sha256": c["orbit_defect_digest_sha256"],
            "high_defect_gate": {"minimum_total_defect": 4, "oracle_lower_errors": 40960},
            "near_orbit_cases": 46492, "complementary_cases_reused": 56,
            "selected_noncomplementary_cases": len(rows), "distinct_cost_column_instances": total_columns,
            "case_lower_error_histogram": dict(sorted(histogram.items())), "selected_case_digest_sha256": digest.hexdigest(),
            "noncomplementary_cases_at_common_lower": minima,
            "lower_errors": 40072, "upper_errors": upper, "outcomes": 147456,
            "lower_fraction": str(Fraction(40072, 147456)), "upper_fraction": str(Fraction(upper, 147456)),
            "interval_width": str(Fraction(upper-40072, 147456)),
            "limits": "All final decoders in this fixed three-block model only. No exact finite optimum, exhaustive codebook or target optimization, asymptotic-frontier change, model gain, efficient practical encoder, token cost, generic-method novelty or priority claim. External proof review remains open."}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ("covers_arbitrary_final_decoders", "near_orbit_cases", "selected_noncomplementary_cases", "lower_errors", "upper_errors")}))


if __name__ == "__main__":
    main()
