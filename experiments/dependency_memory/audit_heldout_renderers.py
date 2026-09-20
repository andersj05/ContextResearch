"""Freeze and exhaustively check offline held-out clue semantics; no model calls.

This is not a provider request format or a held-out launch manifest. Evaluator
keys and the full clue catalog in this artifact must not be sent to a model.
"""
from __future__ import annotations

import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path

from heldout_renderers import (
    FAMILY_NAMES, JOB_KEYS, RENDER_MODES, VERSION,
    infer_candidates, public_metadata, render_manifest,
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def build_audit():
    families = []
    for family in FAMILY_NAMES:
        metadata = public_metadata(family)
        metadata_bytes = canonical(metadata)
        clues = []
        for pair in combinations(JOB_KEYS, 2):
            forms = {}
            for mode in RENDER_MODES:
                clue = render_manifest(pair, metadata, mode)
                if infer_candidates(clue, metadata) != pair:
                    raise AssertionError("Clue changes the intended candidate set")
                # These two target continuations must share the same clue. The
                # renderer accepts no target, receipt, route, or fixture input.
                for _target in pair:
                    if canonical(render_manifest(pair, metadata, mode)) != canonical(clue):
                        raise AssertionError("Rendering is not deterministic")
                    if _target not in infer_candidates(clue, metadata):
                        raise AssertionError("A possible target was excluded by the clue")
                forms[mode] = clue
            clues.append({"candidate_keys": list(pair), "forms": forms,
                          "forms_sha256": digest(forms)})
        if canonical(metadata) != metadata_bytes:
            raise AssertionError("Rendering mutated persistent public metadata")
        for mode in RENDER_MODES:
            if len({canonical(row["forms"][mode]) for row in clues}) != 15:
                raise AssertionError("Distinct candidate pairs must have distinct clues")
        families.append({"family": family, "public_metadata": metadata,
                         "metadata_sha256": hashlib.sha256(metadata_bytes).hexdigest(),
                         "candidate_pairs": 15, "target_routes_per_mode": 30,
                         "clues": clues})
    here = Path(__file__).resolve().parent
    sources = ("heldout_renderers.py", "test_heldout_renderers.py",
               "audit_heldout_renderers.py")
    return {
        "version": "heldout_renderer_semantics_audit_v1", "renderer_version": VERSION,
        "date": "2026-09-19", "status": "offline semantic checkpoint; no live integration",
        "model_requests": 0, "provider_launch_ready": False,
        "evaluator_only": True,
        "counts": {"families": len(families), "candidate_pairs_per_family": 15,
                   "render_modes": len(RENDER_MODES), "family_mode_clue_entries": 120,
                   "unique_serialized_clues": len({canonical(clue)
                       for family in families for row in family["clues"]
                       for clue in row["forms"].values()}),
                   "target_route_checks": 240},
        "source_sha256": {name: hashlib.sha256((here / name).read_bytes()).hexdigest()
                          for name in sources},
        "families": families,
        "limitations": [
            "Exact synthetic relation lookup; no natural-task or model-generalization evidence.",
            "Route repetitions are semantic checks, not independent observations.",
            "Fixed authored names and mappings; no model-guided prompt or name search.",
            "Historical route, payload, and call-order reservations remain unchanged.",
            "Provider allowlist, boundary serialization, and full launch freeze remain future work.",
            "Static metadata grows with the catalog; byte/token cost is not held equal between families.",
            "One reserved route per family still confounds family and route effects.",
        ],
    }


def report(audit):
    lines = [
        "# Held-out renderer semantics: offline checkpoint", "", "September 19, 2026.", "",
        "Four synthetic dependency families now have deterministic explicit and inferred clues. "
        "This checkpoint freezes their static metadata and every two-job clue. It makes zero model "
        "calls and does not implement a provider request or authorize held-out evaluation.", "",
        "| Family | Candidate pairs | Clue forms | Target-route checks |",
        "|---|---|---|---|",
    ]
    for row in audit["families"]:
        lines.append(f"| {row['family']} | 15 | 30 | 60 |")
    lines += ["", "The 120 family/mode clue entries cover all 15 pairs in two modes across four families. "
              "There are 75 unique serialized clues because the 15 explicit forms are shared across families. "
              "Each pair has two possible final targets, giving 240 semantic checks; the target "
              "is not an argument to either renderer. Inferred forms resolve to exactly the same "
              "pair as explicit forms. Separate unit tests check the relation tables, malformed "
              "clues, and metadata channels. This is local software validation, not model evidence.", "",
              "Public metadata describes every job and every relation, independently of the selected "
              "pair. Only a manifest selects a dependency request. Metadata stays available at "
              "each decision; the selected clue must be removed at memory boundaries by the future "
              "request adapter. The existing development and revision interfaces are unchanged and "
              "do not dispatch these new formats.", "", "## Remaining limits", ""]
    lines += [f"- {item}" for item in audit["limitations"]]
    lines += ["", "The [machine-readable checkpoint](heldout_renderer_audit.json) is evaluator-only: "
              "it contains all pair answers and must never be included wholesale in a model request. "
              "See the [renderer contract](../../../docs/HELDOUT_RENDERERS.md).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    audit = build_audit()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "heldout_renderer_audit.json").write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n")
    (args.output / "heldout_renderer_report.md").write_text(report(audit), encoding="utf-8", newline="\n")
    print(json.dumps({"model_requests": 0, **audit["counts"]}))


if __name__ == "__main__":
    main()
