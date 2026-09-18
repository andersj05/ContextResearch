"""Regenerate development diagnostics and a paired delayed-obligation witness."""

import argparse
import csv
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from artifact_workflow import Config, Fixture, POLICIES, Policy, Receipt, make_fixture, run_episode


def scenarios():
    base = Config()
    return {
        "tight_cheap": base,
        "ample_cheap": replace(base, first_capacity=base.jobs),
        "tight_expensive": replace(base, probe_cost=8),
        "tight_unavailable": replace(base, probe_available=False),
        "child_too_small": replace(base, second_capacity=1),
    }


def paired_witness():
    config = Config(jobs=4, delay=2)
    fixture = Fixture(tuple(Receipt(f"job-{i}", 1, f"{i+1:032x}") for i in range(4)),
                      ("job-0", "job-1"), "job-1", Receipt("job-0", 2, f"{11:032x}"))
    prefix_policy = POLICIES[2]
    checkpoint = run_episode(config, fixture, prefix_policy, stop_at_first_boundary=True)
    structured = run_episode(config, fixture, prefix_policy, checkpoint=checkpoint)
    recent = run_episode(config, fixture, Policy("recent_same_prefix", probing="always", retention="recent"),
                         checkpoint=checkpoint)
    assert structured.success and recent.failure == "missing_receipt"
    assert structured.cost_units == recent.cost_units
    return {
        "scope": "Hand-constructed development regression case; no automatic minimization or model trials.",
        "config": asdict(config), "fixture": asdict(fixture),
        "common_prefix_actions": len(checkpoint.trace),
        "restore": "Environment, pending context, retained memory, cost, and trace restored together.",
        "lost_obligation": {"key": "job-1", "revision": 1,
                            "lost_at_boundary": 1, "detected_at": "terminal submit"},
        "structured": asdict(structured), "recent": asdict(recent),
    }


def diagnostics():
    rows = []
    for scenario, base in scenarios().items():
        for seed in range(8):
            for revise in (False, True):
                config = replace(base, revise=revise)
                fixture = make_fixture(seed, config)
                for policy in POLICIES:
                    result = run_episode(config, fixture, policy)
                    rows.append({
                        "scenario": scenario, "seed": seed, **asdict(config),
                        "fixture_sha256": hashlib.sha256(json.dumps(asdict(fixture), sort_keys=True).encode("utf-8")).hexdigest(),
                        "policy": policy.name, "success": result.success,
                        "failure": result.failure or "", "cost_units": result.cost_units,
                        "calls": result.calls, "probe_attempted": result.probe_attempted,
                        "compactions": len(result.compactions),
                        "peak_retained_records": max((c["retained_records"] for c in result.compactions), default=0),
                        "peak_retained_serialized_bytes": max((c["serialized_bytes"] for c in result.compactions), default=0),
                    })
    aggregates = []
    for scenario in scenarios():
        for policy in POLICIES:
            group = [r for r in rows if r["scenario"] == scenario and r["policy"] == policy.name]
            aggregates.append({
                "scenario": scenario, "policy": policy.name, "configurations": len(group),
                "successes": sum(r["success"] for r in group),
                "total_cost_units": sum(r["cost_units"] for r in group),
                "mean_cost_units": str(Fraction(sum(r["cost_units"] for r in group), len(group))),
            })
    summary = {
        "environment_version": "artifact_manifest_v2",
        "source_sha256": {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                          for name in ("artifact_workflow.py", "run_artifact_workflow.py")},
        "scope": "Constructed development diagnostics using stateless scripted policies; no LLM trials or significance claim.",
        "seeds": list(range(8)), "revision_conditions": [False, True],
        "policies": [asdict(p) for p in POLICIES],
        "configurations": len(rows), "cost_unit": "synthetic action unit, not API dollars",
        "memory_unit": "receipt record slots at boundaries; serialized bytes reported separately",
        "aggregates": aggregates,
    }
    return rows, summary, paired_witness()


def report(summary):
    lines = ["# Artifact workflow: deterministic development results", "",
             "September 18, 2026. Generated from 320 constructed configurations (8 seeds, 2 revision conditions, 5 settings, 4 scripted policies). These are not independent LLM trials or a powered benchmark.", "",
             "Each table cell shows terminal successes out of 16 and mean synthetic action units. Failed episodes remain in cost accounting. Memory is capped in receipt records at two boundaries; bytes are recorded separately. The [CSV](artifact_workflow.csv) includes the recent-record baseline and every configuration.", "",
             "| Setting | Structured, never inspect | Structured, always inspect | Structured, budgeted inspection |",
             "|---|---|---|---|"]
    for scenario in scenarios():
        cells = [scenario]
        for name in ("structured_never", "structured_always", "structured_budgeted"):
            row = next(r for r in summary["aggregates"] if r["scenario"] == scenario and r["policy"] == name)
            cells.append(f"{row['successes']}/{row['configurations']}; {row['mean_cost_units']} units")
        lines.append("| " + " | ".join(cells) + " |")
    lines += ["", "The tight/cheap case demonstrates the intended information-timing mechanism. With ample first-stage memory, structured retention succeeds without inspection. Expensive inspection exposes a cost/success tradeoff: the budgeted heuristic declines it and loses some successes. An unavailable clue cannot help, and an insufficient second-stage record capacity still loses obligations after early inspection.", "",
              "The [paired witness](artifact_workflow_witness.json) is a separate hand-constructed regression fixture. Both continuations receive the same early clue and start from the same saved environment and context. Recent retention loses job-1 at boundary 1 and fails only when the delayed receipt is submitted; structured retention succeeds at the same action cost. This witness was not automatically minimized.", "",
              "These outcomes establish expected behavior of this environment and these fixed policies. They do not establish a new policy's general superiority, theorem-optimal bit compression, API cost savings, or performance against native compaction. See the [information contract](../ARTIFACT_WORKFLOW.md).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows, summary, witness = diagnostics()
    with (args.output / "artifact_workflow.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    for name, value in (("artifact_workflow_summary.json", summary),
                        ("artifact_workflow_witness.json", witness)):
        (args.output / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    (args.output / "artifact_workflow_report.md").write_text(report(summary), encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
