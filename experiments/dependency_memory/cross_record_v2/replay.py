"""Post-hoc decoder-compatibility replay of saved v1 parent proposals.

This reads existing evidence only. It does not dispatch model calls, replace a
saved child proposal, or rescore any terminal decision in the frozen study.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from experiments.dependency_memory.cross_record import memory as frozen
from experiments.dependency_memory.cross_record import run as frozen_run
from experiments.dependency_memory.schema_transfer import memory as table
from .compatibility import admit_or_project, certify_child, certify_parent, select_by_owner

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "experiments/dependency_memory/results/cross_record_2026-09-22"
CONTINUATION = ROOT / "experiments/dependency_memory/results/cross_record_continuation_2026-09-22"
OUTPUT = ROOT / "experiments/dependency_memory/results/cross_record_v2_parent_replay.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def replay(evidence=EVIDENCE, continuation=CONTINUATION):
    manifest = load(evidence / "manifest.json")
    paths, _ = frozen_run.fixture_paths()
    if manifest["fingerprints"] != frozen_run.fingerprints():
        raise ValueError("Frozen v1 implementation or fixtures changed")
    cases = []
    for path in paths:
        case = load(path)
        matches = [directory / (case["id"] + "-episode.json")
                   for directory in (evidence, continuation)
                   if (directory / (case["id"] + "-episode.json")).is_file()]
        if not matches:
            raise ValueError("Saved parent episode missing: " + case["id"])
        episode_path = matches[0]
        episode = load(episode_path)
        if any(load(other)["memories"]["structured"]["parent"] !=
               episode["memories"]["structured"]["parent"] for other in matches[1:]):
            raise ValueError("Original and continuation parents disagree: " + case["id"])
        if episode["case_id"] != case["id"]:
            raise ValueError("Saved case identity mismatch")
        proposal = episode["memories"]["structured"]["parent"]
        old_check = frozen.check(proposal, case["tool_schemas"], case["tool_results"])
        new_check = certify_parent(proposal, case["tool_schemas"], case["tool_results"])
        admitted, admitted_check, fallback = admit_or_project(
            proposal, case["tool_schemas"], case["tool_results"])
        if not admitted_check["passed"]:
            raise ValueError("Incompatible admitted parent")
        owner = admitted_check["owner_path"]
        owners = [row[owner] for row in table.decode(admitted)]
        pair_count = 0
        for pair in combinations(owners, 2):
            child = select_by_owner(admitted, owner, pair)
            if not certify_child(child, admitted, pair, owner, case["tool_schemas"])["passed"]:
                raise ValueError("Admitted parent fails a child handoff")
            pair_count += 1
        cases.append({"case_id": case["id"], "fixture_sha256": sha256(path.read_bytes()).hexdigest(),
                      "episode_sha256": [sha256(item.read_bytes()).hexdigest() for item in matches],
                      "v1_id_check_passed": old_check["passed"],
                      "v2_parent_passed": new_check["passed"],
                      "v2_reason": new_check["reason"], "fallback": fallback,
                      "proposal_bytes": len(proposal.encode("utf-8")),
                      "admitted_bytes": len(admitted.encode("utf-8")),
                      "max_child_bytes": admitted_check["max_child_bytes"],
                      "all_owner_pairs_checked": pair_count})
    reasons = Counter(row["v2_reason"] for row in cases)
    return {"version": "cross_record_v2_parent_replay_v1", "scope":
            "post_hoc_parent_and_deterministic_child_only_no_terminal_rescoring",
            "cases": cases, "counts": {"parents": len(cases),
                "v1_id_check_passes": sum(row["v1_id_check_passed"] for row in cases),
                "v2_parent_passes": sum(row["v2_parent_passed"] for row in cases),
                "v2_fallbacks": sum(row["fallback"] for row in cases),
                "decoder_compatible_admitted_parents": sum(row["all_owner_pairs_checked"] == 21 for row in cases),
                "all_owner_pairs_checked": sum(row["all_owner_pairs_checked"] for row in cases),
                "reasons": dict(sorted(reasons.items()))}}


def validate_saved(output=OUTPUT):
    """Recompute the committed diagnostic; missing or stale evidence must fail."""
    recorded = load(output)
    expected = replay()
    if recorded != expected:
        raise ValueError("Decoder-compatibility saved replay differs from source evidence")
    return expected


if __name__ == "__main__":
    result = replay()
    OUTPUT.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(result["counts"], indent=2))
