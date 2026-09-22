"""Cost sensitivity and corrected provenance for the frozen schema-check run."""
from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "experiments/dependency_memory/results/schema_checks_2026-09-22"
CPU = Decimal("0.0001")
BYTE = Decimal("0.00000001")


def load(name):
    return json.loads((DIR / name).read_text(encoding="utf-8"))


def main():
    analysis = load("analysis.json")
    calibration = load("local_calibration.json")
    if (analysis["model_calls"] != 72 or analysis["paired_terminal_decisions"] != 12 or
            calibration["version"] != "schema_checks_local_calibration_v1"):
        raise ValueError("Wrong saved study")
    rows = {}
    for arm in analysis["arm_totals"]:
        label = {"automatic": "automatic", "direct": "direct", "indexed": "indexed_two_reads",
                 "full": "full_two_reads"}.get(arm)
        cpu_ns = 0 if label is None else sum(
            max(row[label]["max_batch_ns_per_operation"] for row in calibration["rows"] if row["family"] == family) * 2
            for family in ("retry", "ci_handoff", "data_job"))
        source = analysis["arm_totals"][arm]
        model = Decimal(source["model_credits"])
        bytes_cost = Decimal(source["local_bytes_read"]) * BYTE
        cpu_cost = Decimal(cpu_ns) / Decimal(10**9) * CPU
        rows[arm] = {"failures": source["failures"], "model_calls": source["model_calls"],
                     "model_credits": str(model), "local_bytes_read": source["local_bytes_read"],
                     "calibrated_cpu_ns_upper_batch": cpu_ns,
                     "byte_credits": str(bytes_cost), "cpu_credits": str(cpu_cost),
                     "sensitivity_total_credits": str(model + bytes_cost + cpu_cost)}
    prompt = Decimal(rows["prompt"]["sensitivity_total_credits"])
    auto = Decimal(rows["automatic"]["sensitivity_total_credits"])
    seconds = Decimal(rows["automatic"]["calibrated_cpu_ns_upper_batch"]) / Decimal(10**9)
    break_even = (prompt - Decimal(rows["automatic"]["model_credits"]) -
                  Decimal(rows["automatic"]["byte_credits"])) / seconds
    result = {"version": "schema_checks_reconciled_v1", "protocol_commit": "284405d",
              "frozen_implementation_commit": "75ab94f",
              "analysis_sha256": sha256((DIR / "analysis.json").read_bytes()).hexdigest(),
              "calibration_sha256": sha256((DIR / "local_calibration.json").read_bytes()).hexdigest(),
              "arms": rows, "matched_allowance_credits": str(prompt),
              "eligible_at_matched_allowance": [arm for arm, row in rows.items()
                   if Decimal(row["sensitivity_total_credits"]) <= prompt],
              "prespecified_primary_success": analysis["criteria"]["primary_success"],
              "parity_with_direct": analysis["criteria"]["no_more_failures_than_direct"],
              "cpu_price_break_even_credits_per_second": str(break_even),
              "limitation": "The live Windows process_time_ns timer quantized short local operations to zero; "
                  "CPU is repriced from a post-run high-resolution development-trace calibration. "
                  "This is a sensitivity estimate, not a per-run CPU measurement or provider debit."}
    (DIR / "reconciled_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Frozen schema-check comparison: reconciled cost sensitivity", "",
        "The frozen 72-call run covers six constructed evaluation traces and 12 paired terminal decisions. "
        "Every arm succeeds on 12/12. The automatic method therefore **fails the preregistered primary criterion** "
        "of fewer failures than stronger prompting at no higher total cost. It matches the hand-written direct record outcomes.",
        "", "| Arm | Failures | Calls | Model credits | Local read bytes | Estimated total credits |",
        "|---|---:|---:|---:|---:|---:|"]
    for arm, row in rows.items():
        lines.append(f"| {arm} | {row['failures']}/12 | {row['model_calls']} | {row['model_credits']} | "
                     f"{row['local_bytes_read']} | {row['sensitivity_total_credits']} |")
    lines += ["", "The matched allowance is the stronger prompt arm's observed total, " + str(prompt) +
              " experimental credits; all controls fit. The direct and indexed controls are cheaper than the automatic method. "
              "The automatic method removes memory-writing model calls and is cheaper than prompting, but terminal outcomes are tied.",
              "", "**CPU correction.** The live Windows `process_time_ns` reported zero for short local operations. "
              "The separate development-trace benchmark uses `perf_counter_ns` in seven 1,000-repeat batches. "
              "This table prices the largest measured batch for each family, twice for its two evaluation traces, "
              "at the preregistered 0.0001 credit/second plus exact locally read bytes at 0.00000001 credit/byte. "
              "Those prices are synthetic and the CPU calibration is post-run; only model tokens and local bytes were "
              "measured in the live comparison. No actual subscription debit is attributable.",
              "", "The raw analysis field `source_commit` names the protocol-price commit (`284405d`); "
              "the implementation frozen before model answers is `75ab94f`, as recorded in this reconciliation.",
              "", "The extractor uses schema-provided opaque-ID, reference and ephemeral annotations. "
              "It checks exact IDs and owner/path/reference triples but does not certify unannotated state. "
              "The evaluation cases have new identities and tool results within the three development schema families. "
              "They are constructed traces, not previously observed incidents or unseen schema structures. "
              "The direct records omit human schema-authoring cost. No native compaction or production gain is shown.",
              "", "The raw [saved-evidence analysis](analysis.json), [local calibration](local_calibration.json), "
              "and [frozen protocol](../../schema_checks/FROZEN_PROTOCOL.md) give the inputs for this sensitivity report."]
    (DIR / "reconciled_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"primary_success": result["prespecified_primary_success"],
                      "parity_with_direct": result["parity_with_direct"],
                      "automatic_total": rows["automatic"]["sensitivity_total_credits"],
                      "prompt_total": rows["prompt"]["sensitivity_total_credits"]}))


if __name__ == "__main__":
    main()
