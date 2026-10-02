"""Weighted cover bound for late-coordinate-independent final predictions.

This does not cover arbitrary three-bit endpoint decoders. Codebooks, encoders
and updater tables are arbitrary within the stated restricted decoder family.
"""
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path

from experiments.dependency_memory.joint_coding.coding import branch_cost
from experiments.dependency_memory.joint_coding_finite3 import witness

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE.parent / "results/joint_three_block_cover_2026-10-01.json"


def oracle(source):
    return (0, 3, 4, 3, 0)[source.bit_count()]


def score(source, decision):
    return int(source.bit_count() == 2) - (branch_cost(source, decision) - oracle(source))


def convolve(left, right):
    result = Counter()
    for a, na in left.items():
        for b, nb in right.items():
            result[a + b] += na * nb
    return result


def require_coordinate_independent(decoder):
    if len(decoder) != 4 or any(len(pair) != 2 for pair in decoder):
        raise ValueError("Expected two three-bit endpoints for each omission")
    for pair in decoder:
        for endpoint in pair:
            if len(endpoint) != 3 or any(type(bit) is not int or bit not in (0, 1) for bit in endpoint):
                raise ValueError("Invalid endpoint")
            if len(set(endpoint)) != 1:
                raise ValueError("Late-coordinate-dependent decoder is outside the proved family")


def lower_bound(decoder):
    require_coordinate_independent(decoder)
    # Public child relabellings or constant endpoints can be absorbed by updater.
    return Fraction(40072, 147456)


def certificate():
    profiles = [Counter(score(x, a) for x in range(16)) for a in range(16)]
    rewards = []
    for c, b, a in product(range(16), repeat=3):
        profile = convolve(convolve(profiles[a], profiles[b]), profiles[c])
        rewards.append(sum(max(s, 0) * n for s, n in profile.items()))
    if max(rewards) != 25:
        raise ValueError("Cover-column bound changed")
    base = sum(oracle(x) for x in range(16)) * 256 * 3
    target = 6 * 256 * 3
    bounds = [{"constant_codewords": n, "lower_errors": base + target - 25 * (64 - n) + 125 * (8 - n)}
              for n in range(9)]
    incumbent = witness.selected_book()
    n_const = sum(all(a in (0, 15) for a in row) for row in incumbent)
    lower = min(row["lower_errors"] for row in bounds)
    if lower != 40072 or n_const != 8:
        raise ValueError("Center correction or witness changed")
    upper = witness.grade(witness.parent_table(incumbent), incumbent)["errors"]
    saved_upper = json.loads((HERE.parent / "results/joint_three_block_certificate_2026-10-01.json").read_text())
    if saved_upper["codebook"] != json.loads(json.dumps(incumbent)) or saved_upper["witness"]["errors"] != upper:
        raise ValueError("Upper witness and its saved certificate disagree")
    files = (HERE / "bounds.py", HERE / "test_bounds.py", HERE.parent / "joint_coding/coding.py",
             HERE.parent / "joint_coding_finite3/witness.py", HERE.parent / "joint_coding_finite3/discovery.json",
             HERE.parent / "results/joint_three_block_certificate_2026-10-01.json")
    classes = {"constant": profiles[0], "weight_one_or_three": profiles[1], "weight_two": profiles[3]}
    return {"version": "finite3_coordinate_independent_cover_v1", "date": "2026-10-01",
        "evidence_class": "elementary analytic restricted converse with exact finite ingredients",
        "new_model_requests": 0, "covers_arbitrary_final_decoders": False,
        "decoder_restriction": "Prediction independent of late coordinate J; public R/O-dependent child relabellings may be absorbed by updater.",
        "parent_states_at_most": 64, "child_states_at_most": 2, "blocks": 3,
        "source_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "one_block_score_profiles": classes, "all_4096_column_rewards": rewards,
        "column_reward_histogram": dict(sorted(Counter(rewards).items())), "maximum_column_reward": 25,
        "isolated_child_error_sum": base, "target_sum": target,
        "constant_centers": 8, "sources_per_constant_fiber": 125,
        "lower_bound_by_constant_count": bounds, "lower_errors": lower, "upper_errors": upper,
        "outcomes": 147456, "lower_fraction": str(Fraction(lower, 147456)),
        "upper_fraction": str(Fraction(upper, 147456)), "interval_width": str(Fraction(upper - lower, 147456)),
        "witness_constant_codewords": n_const,
        "limits": "Restricted decoder family only. Cover-column enumeration is not codebook optimization. No finite optimum, unrestricted improvement, novelty, practical memory units or model gain is claimed. External proof review remains open."}


def main():
    data = certificate()
    OUTPUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: data[k] for k in ("maximum_column_reward", "lower_errors", "upper_errors", "outcomes", "lower_fraction", "interval_width", "covers_arbitrary_final_decoders")}))


if __name__ == "__main__":
    main()
