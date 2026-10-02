"""Bounded post-hoc selection of exact finite cover witnesses; zero model calls.

This standard-library search first tries seven synchronized binary masks, then
mixed binary masks on failures, then quarter-unit masks on remaining failures.
The certificate checks the saved targets, not search or optimizer optimality.
"""
from collections import Counter
from functools import lru_cache
import hashlib
from itertools import product
import json

from experiments.dependency_memory.joint_coding_general import cover

INITIAL = ("oracle4", "1", "2", "3", "5", "zero", "one")
REFINEMENT = ("oracle4", "1", "2", "3", "4", "5", "6", "7", "8", "zero", "one",
              "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8")
FRACTIONAL = ("1", "2", "3", "4", "5", "6", "7", "8", "one",
              "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8")


@lru_cache(None)
def target(index, rule, amplitude=4):
    initial = cover.block(index, 0)
    columns, oracle = initial["columns"], initial["oracle"]
    counts = [sum(v == oracle[x] for x, v in enumerate(column)) for column in columns]
    largest_fiber = [max(n for column, n in zip(columns, counts) if column[x] == oracle[x]) for x in range(16)]
    if rule == "oracle4":
        mask = [u >= 4 for u in oracle]
    elif rule.startswith("u"):
        mask = [u >= int(rule[1:]) for u in oracle]
    elif rule == "one":
        mask = [True]*16
    elif rule == "zero":
        mask = [False]*16
    else:
        mask = [count <= int(rule) for count in largest_fiber]
    return cover.pack_target(tuple(amplitude*int(yes) for yes in mask))


def candidate(indices, codes):
    blocks = [cover.block(i, t) for i, t in zip(indices, codes)]
    checked = cover.bound(blocks)
    return [*indices, *codes, checked["integer_lower_errors"]], checked


def binary_key(row):
    # Equal relevant score/incidence profiles have equal weights for every
    # binary companion mask, even if lower negative scores differ.
    profiles = Counter()
    for (scores, q), n in row["profiles"]:
        values = dict(scores)
        profiles[values.get(4, 0), values.get(0, 0), values.get(-4, 0), q] += n
    return (tuple(sorted(profiles.items())), row["oracle_sum"], row["target_sum_units"], row["zero_sources"])


def binary_options(index):
    seen, choices = set(), []
    for rule in REFINEMENT:
        code = target(index, rule)
        key = binary_key(cover.block(index, code))
        if key not in seen:
            seen.add(key)
            choices.append((rule, code))
    return choices


def discover():
    selected, types_by_key, initial_trials = {}, {}, 0
    for indices, types in cover.near_cases():
        types_by_key[indices] = types
        best = None
        for rule in INITIAL:
            codes = tuple(target(index, rule) for index in indices)
            row, checked = candidate(indices, codes)
            initial_trials += 1
            if best is None or row[6] > best[6]:
                best = row
            if row[6] >= 40072:
                break
        selected[indices] = best
    initial_failures = [key for key, row in selected.items() if row[6] < 40072]
    refinement_trials, refinement_rows = 0, []
    for key in initial_failures:
        best = selected[key]
        for choice in product(*(binary_options(index) for index in key)):
            codes = tuple(row[1] for row in choice)
            row, _ = candidate(key, codes)
            refinement_trials += 1
            if row[6] > best[6]:
                best = row
            if row[6] >= 40072:
                break
        selected[key] = best
        refinement_rows.append(best)
    fractional_keys = [key for key, row in selected.items() if row[6] < 40072]
    fractional_trials, fractional_rows = 0, []
    for key in fractional_keys:
        if key[:2] != (335923, 335923):
            raise ValueError("Quarter-unit witness family does not cover a remaining case")
        best = selected[key]
        options = {}
        for rule, amplitude in product(FRACTIONAL, range(9)):
            code = target(key[2], rule, amplitude)
            options.setdefault(code, (rule, amplitude))
        for amplitude, third_code in product(range(9), options):
            unsigned_code = target(335923, "1", amplitude)
            row, _ = candidate(key, (unsigned_code, unsigned_code, third_code))
            fractional_trials += 1
            if row[6] > best[6]:
                best = row
            if row[6] >= 40072:
                break
        selected[key] = best
        fractional_rows.append(best)
        if best[6] < 40072:
            raise ValueError("Grid did not find a witness for every near case")
    rows = [selected[key] for key, _ in cover.near_cases()]
    files = (cover.HERE / "cover.py", cover.HERE / "discover.py",
             cover.HERE.parent / "joint_coding/decoder_frontier.py")
    return {"version": "finite3_general_cover_discovery_v1", "date": "2026-10-01", "new_model_calls": 0,
            "evidence_class": "post-hoc bounded mathematical witness selection, not a preregistered experiment",
            "target_encoding": "Low four bits give a nonnegative quarter-unit amplitude; high sixteen bits mark the source values receiving that amplitude. This is public proof metadata, not instance memory.",
            "case_columns": ["decoder_a", "decoder_b", "decoder_c", "target_a", "target_b", "target_c", "lower_errors"],
            "initial_rules": INITIAL, "initial_candidate_triples": initial_trials,
            "initial_cases_below_target": len(initial_failures), "binary_refinement_rules": REFINEMENT,
            "binary_refinement_candidate_triples": refinement_trials, "binary_refinement_rows": refinement_rows,
            "quarter_unit_rules": FRACTIONAL, "quarter_unit_amplitudes": list(range(9)),
            "quarter_unit_candidate_triples": fractional_trials, "quarter_unit_rows": fractional_rows,
            "selected_cases": rows, "source_sha256": {p.relative_to(cover.ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            "limits": "Selected witnesses prove inequalities only. No exhaustive target/codebook optimization or optimality, model gain, generic cover novelty or priority claim."}


def save(result):
    # One compact case per line keeps the large exact witness list reviewable.
    records = result["selected_cases"]
    header = {key: value for key, value in result.items() if key != "selected_cases"}
    text = json.dumps(header, sort_keys=True, indent=2)
    text = text[:-2] + ',\n  "selected_cases": [\n'
    text += ",\n".join("    " + json.dumps(row, separators=(",", ":")) for row in records)
    text += "\n  ]\n}\n"
    cover.DISCOVERY.write_text(text, encoding="utf-8", newline="\n")


def main():
    result = discover()
    save(result)
    print(json.dumps({"saved_cases": len(result["selected_cases"]),
                      "initial_failures": result["initial_cases_below_target"],
                      "mixed_binary_trials": result["binary_refinement_candidate_triples"],
                      "quarter_unit_cases": len(result["quarter_unit_rows"]),
                      "quarter_unit_trials": result["quarter_unit_candidate_triples"],
                      "minimum_lower_errors": min(row[6] for row in result["selected_cases"])}))


if __name__ == "__main__":
    main()
