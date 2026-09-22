"""Reconcile the fixed pilot and its separately frozen development follow-up."""
from decimal import Decimal
import json
from pathlib import Path

from analyze_luna6_revision import analyze
from luna6_data_first_followup import analyze as analyze_followup

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments/dependency_memory/results"


def summarize():
    original = analyze(RESULTS / "luna6_revision_2026-09-22")
    followup = analyze_followup()
    total = Decimal(original["actual_planning_credits"]) + Decimal(followup["planning_credits"])
    assert total == Decimal(followup["combined_credits"]) and total < 20
    assert original["actual_dispatches"] + followup["new_calls"] == 141 <= 144
    saved = json.loads((RESULTS / "luna6_data_first_2026-09-22/analysis.json").read_text())
    assert saved == followup
    methods = [{**row, "phase": "fixed pilot"} for row in original["methods"]]
    methods.insert(2, {"arm": "data_first", "phase": "post-pilot development", "cases": 16,
                      "success": followup["success"], "unsafe_release": followup["unsafe_release"],
                      "planning_credits": followup["planning_credits"], "cache_neutral_credits": followup["cache_neutral_credits"],
                      "model_calls_charged": 24, "clipped_memories": followup["clipped_memories"]})
    keys = ("inputTokens", "cachedInputTokens", "outputTokens", "reasoningOutputTokens")
    usage = {key: original["usage"][key]+followup["usage"][key] for key in keys}
    return {"audit_passed": True, "actual_model_calls": 141, "actual_planning_credits": str(total),
            "model": "gpt-6-luna", "reasoning_effort": "medium", "usage": usage, "methods": methods,
            "main_launch_commit": "136d589", "followup_launch_commit": "8d8a358",
            "followup_failed_ids": [r["id"] for r in followup["decisions"] if not r["success"]],
            "local_cost_calibration": original["local_cost_calibration"],
            "additional_extraction_headroom": original["additional_extraction_headroom"],
            "limitations": original["limitations"] + [followup["limitations"]]}


def render(report):
    costs = report["local_cost_calibration"]["methods"]
    direct_ms = costs["direct"]["median_cpu_ns_per_four_histories"]/1000000
    repair_ms = costs["repair"]["median_cpu_ns_per_four_histories"]/1000000
    lines = ["# Live GPT-6 Luna memory benchmark", "",
             "**141 fresh calls at medium reasoning; 1.3190825 planning credits; both evidence audits pass.**",
             "", "Four constructed release handoffs pass through 900-byte and 440-byte memory limits. Each method faces sixteen delayed decisions. These reuse four histories and are not independent production incidents.", "",
             "| Method | Exact decisions | Unsafe release | Model credits | Cache-neutral credits | Clipped memories | Phase |",
             "|---|---:|---:|---:|---:|---:|---|"]
    for row in report["methods"]:
        lines.append(f"| {row['arm']} | {row['success']}/16 | {row['unsafe_release']} | {row['planning_credits']} | {row['cache_neutral_credits']} | {row['clipped_memories']} | {row['phase']} |")
    lines += ["", "All memory-writing and execution calls count. The main pilot shares four parent calls, charging their full cost to each method that uses them. Cache-neutral figures remove discounts arithmetically. Actual subscription debit is not attributable, and infrastructure and adapter-development costs are unmeasured.", "",
              "## What failed", "",
              "- The original structured child cut off `REL-543e`, an open blocker for `delta-e58`, at its byte limit. The later model incorrectly chose release after an irrelevant note update.",
              "- A separately frozen data-first prompt announced that public rules would be repeated. It eliminated clipping but retained only 12/16 correct decisions.",
              "- In that unclipped follow-up, `atlas-99c` became `atlas-99`, and `ember-0c4` became `ember-0c`. Another child dropped the current artifact and treated the approval identifier as the reference for stale CI. Exact identifiers and semantic field roles were damaged even with unused memory capacity.", "",
              "## What repaired it, and at what cost", "",
              "A checked projection retains the executable gate's fields in 769 bytes at the first boundary and 311–321 bytes at the second. It gets 16/16 correct decisions and costs 8.9% less than the original structured pipeline, including proposal calls; the saving is 8.6% without cache discounts.", "",
              "The stronger data-first prompt is cheaper than that repair loop, but gets 12/16. Directly serializing the same checked fields gets 16/16 for much less than either. Indexed recovery and full-history access also get 16/16. Repair and direct terminal prompts are identical. This supports direct retention for this known gate; it does not establish a superior general feedback method.", "",
              f"Repeated local CPU measurements give {direct_ms:g} ms for direct serialization and {repair_ms:g} ms for checked replacement across all four histories. The live per-check timer resolved zero, so those zeros must not be interpreted as free computation. Indexed recovery transfers 12,404 bytes. The direct/indexed ranking changes when cache discounts are removed.", "",
              "An automatic projection extractor would have only 0.0428170 observed credits, or 0.0387850 cache-neutral credits, of extra budget across this four-history workload before direct retention loses its measured advantage over full-history access. No such extractor was run.", "",
              "## Interpretation and reproducibility", "",
              "The main schedule was frozen in `136d589`. The 24-call prompt follow-up was frozen in `8d8a358` after observing the first results; it is development evidence on reused fixtures. The prototype uses a manually specified gate adapter, not automatic semantic verification. Native compaction, production-total-cost savings, held-out transfer and publication novelty remain open.", "",
              "- [Detailed findings](../../../research/LUNA6_DELAYED_FAILURES_2026-09-22.md)",
              "- [Main contract](../luna6_revision/CONTRACT.md) and [main run](luna6_revision_2026-09-22/report.md)",
              "- [Follow-up contract](../../../docs/LUNA6_DATA_FIRST_FOLLOWUP.md) and [saved follow-up](luna6_data_first_2026-09-22/analysis.json)",
              "- [Prior-art comparison](../../../research/LUNA6_SCOPE_PRIOR_ART_2026-09-22.md)", "",
              "Offline reproduction: `python scripts/summarize_luna6_studies.py`, then `python scripts/validate_context_repo.py`. Never run a launch script as a repository check.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    report = summarize()
    (RESULTS / "luna6_memory_summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    (RESULTS / "luna6_memory_report.md").write_text(render(report), encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ("audit_passed", "actual_model_calls", "actual_planning_credits", "usage")}))
