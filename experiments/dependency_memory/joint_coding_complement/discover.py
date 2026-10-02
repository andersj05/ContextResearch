"""Exploratory finite grids selecting exact cover witnesses, not optimality claims.

The checker consumes the saved target arrays; it never needs this search to
establish the inequality. Selection is post-hoc mathematical discovery, with
zero model calls and no inference about general codebook or target optimality.
"""
from collections import Counter
import hashlib
from itertools import combinations_with_replacement, product
import json

from experiments.dependency_memory.joint_coding_complement import cover


def options(table):
    initial = cover.block(table, (0,) * 16)
    counts = Counter(initial["ideal"])
    seen, rows = set(), []
    for cutoff in (0, 1, 2, 3, 5):
        target = tuple(4 * int(counts[a] <= cutoff) for a in initial["ideal"])
        if target not in seen:
            seen.add(target)
            rows.append((cutoff, cover.block(table, target)))
    return rows


def discover():
    representatives = cover.orbits()
    variants = [options(table) for table, _ in representatives]
    selected, evaluations = [], 0
    binary_best = []
    for types in combinations_with_replacement(range(6), 3):
        best = None
        for candidate in product(*(variants[i] for i in types)):
            blocks = [row[1] for row in candidate]
            checked = cover.bound(blocks)
            evaluations += 1
            row = {"types": types, "targets": [b["targets"] for b in blocks],
                   "discovery": "binary fiber-count cutoffs", "cutoffs": [c[0] for c in candidate],
                   "lower_error_units": checked["lower_error_units"]}
            if best is None or row["lower_error_units"] > best["lower_error_units"]:
                best = row
        selected.append(best)
        binary_best.append({"types": types, "cutoffs": best["cutoffs"], "lower_error_units": best["lower_error_units"]})
    critical = (0, 0, 4)
    target_position = [tuple(row["types"]) for row in selected].index(critical)
    refinement = []
    for unsigned_target, other_target in product(range(1, 13), repeat=2):
        blocks = []
        for i, value in zip(critical, (unsigned_target, unsigned_target, other_target)):
            table = representatives[i][0]
            loss = cover.frontier.loss_matrix(table)
            target = tuple(value if min(row) == 4 else 0 for row in loss)
            blocks.append(cover.block(table, target))
        checked = cover.bound(blocks)
        row = {"unsigned_target_units": unsigned_target, "other_target_units": other_target,
               "lower_error_units": checked["lower_error_units"]}
        refinement.append(row)
        if row["lower_error_units"] > selected[target_position]["lower_error_units"]:
            selected[target_position] = {"types": critical, "targets": [b["targets"] for b in blocks],
                "discovery": "quarter-unit oracle-loss-four refinement", **row}
    files = (cover.HERE / "discover.py", cover.HERE / "cover.py",
             cover.HERE.parent / "joint_coding/decoder_frontier.py")
    return {"version": "complementary_cover_witness_discovery_v1", "date": "2026-10-01", "new_model_calls": 0,
            "evidence_class": "exploratory mathematical witness selection, not preregistered experiment",
            "binary_cutoffs": [0, 1, 2, 3, 5], "binary_candidate_triples": evaluations,
            "binary_grid_best": binary_best, "critical_orbit_types": critical,
            "quarter_unit_grid_range_inclusive": [1, 12], "refinement_candidates": refinement,
            "selected_targets": selected,
            "source_sha256": {p.relative_to(cover.ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            "limits": "Only the saved selected rational arrays are certified by cover.py. No exhaustive target optimization, codebook optimization, priority or model gain is claimed."}


def main():
    result = discover()
    path = cover.HERE / "discovery.json"
    path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"saved": str(path), "binary_candidates": result["binary_candidate_triples"],
                     "refinement_candidates": len(result["refinement_candidates"]),
                     "minimum_lower_error_units": min(row["lower_error_units"] for row in result["selected_targets"]),
                     "target_unit_denominator": 4}))


if __name__ == "__main__":
    main()
