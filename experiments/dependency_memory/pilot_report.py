"""Render development-pilot summaries without omitting failed or unstarted work.

Optional ``request_metrics`` contains ledger rows (only evaluator_id, status,
latency_seconds and provider_metadata are read). Optional ``transport_manifest``
records the client contract. Missing measurements are unknown, never zero.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path


UNKNOWN = "unknown"


def _text(value):
    if value is None:
        return UNKNOWN
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headings, rows):
    return ["| " + " | ".join(headings) + " |",
            "| " + " | ".join("---" for _ in headings) + " |",
            *("| " + " | ".join(_text(v) for v in row) + " |" for row in rows), ""]


def _number(value):
    return type(value) in (int, float) and value >= 0


def _measurement(metrics, expected, name, *, usage=False):
    values = []
    for metric in metrics:
        data = metric.get("provider_metadata", {}).get("usage", {}) if usage else metric
        value = data.get(name)
        if _number(value):
            values.append(value)
    if not values:
        return UNKNOWN
    total = sum(values)
    if type(total) is float:
        total = round(total, 6)
    return f"{total} reported ({len(values)}/{expected} attempts measured)"


def _statuses(rows):
    counts = Counter(row.get("status", UNKNOWN) for row in rows)
    order = ("completed", "policy_failure", "transport_failure", "incomplete", "reserved")
    return "; ".join(f"{status}={counts.get(status, 0)}" for status in
                     (*order, *sorted(set(counts) - set(order))))


def _episode_metrics(summary, row):
    prefix = row["episode_id"] + "/"
    return [m for m in summary.get("request_metrics", [])
            if m.get("evaluator_id", "").startswith(prefix)]


def _completed_delta(row):
    """Do not compare a truncated episode's partial cost with a full reference."""
    if row.get("status") != "completed" or type(row.get("inspection")) is not bool:
        return None
    reference = row.get("fixed_policy_reference", {}).get("inspect" if row["inspection"] else "skip", {})
    if row.get("synthetic_cost_units") is None or reference.get("synthetic_cost_units") is None:
        return None
    return str(Fraction(str(row["synthetic_cost_units"])) - Fraction(str(reference["synthetic_cost_units"])))


def report(summary):
    """Return deterministic Markdown for the full scheduled development tranche.

    No cell is dropped for failure, truncation, or missing measurements. Reference
    values are those saved by the evaluator, not recomputed or fitted to outcomes.
    """
    stage_a, stage_b = summary["stage_a"], summary["stage_b"]
    if any(row.get("split", "development") != "development" for row in stage_b):
        raise ValueError("This report is restricted to the development split")
    if summary.get("heldout_requests", 0) != 0:
        raise ValueError("This report cannot combine held-out requests with the development split")
    attempts = summary["request_attempts"]
    if type(attempts) is not int or attempts < 0:
        raise ValueError("Request attempts must be a nonnegative integer")
    if any(type(row.get("request_attempts", 0)) is not int or row.get("request_attempts", 0) < 0 for row in stage_b):
        raise ValueError("Episode request attempts must be nonnegative integers")
    b_attempts = sum(row.get("request_attempts", 0) for row in stage_b)
    a_attempts = attempts - b_attempts
    if a_attempts < 0 or a_attempts > len(stage_a):
        raise ValueError("Request counts do not reconcile with one-request Stage A")
    metrics = summary.get("request_metrics", [])
    if len(metrics) > attempts:
        raise ValueError("Metric coverage exceeds the recorded attempt count")
    if sum(summary.get("attempt_status_counts", {}).values()) != attempts:
        raise ValueError("Attempt status counts do not reconcile with request attempts")
    contract = summary.get("transport_manifest", {})
    accounting = summary.get("cost_accounting", {})
    planned = sum(row.get("maximum_model_requests", 1) for row in stage_a)
    planned += sum(row["maximum_model_requests"] for row in stage_b)
    completed_b = [row for row in stage_b if row.get("status") == "completed"]
    lines = ["# Development pilot report", "",
             "Exploratory development/debugging only. These paired measurements share one development route; "
             "they are not independent trials, held-out evidence, or evidence of general superiority.", "",
             f"Client: **{_text(summary.get('client'))}**. "
             f"Fake client: **{_text(summary.get('fake'))}**. "
             f"Version: `{_text(summary.get('version'))}`.", "",
             f"Manifest SHA-256: `{_text(summary.get('manifest_sha256'))}`. "
             f"Request-audit SHA-256: `{_text(summary.get('request_audit_sha256'))}`.", "",
             "## Completion and accounting", ""]
    lines += _table(["Quantity", "Recorded value"], [
        ("Maximum scheduled requests", planned),
        ("Run request cap", summary.get("request_cap")),
        ("Request attempts (including failures)", attempts),
        ("Recorded model requests", summary.get("model_requests")),
        ("Held-out requests", summary.get("heldout_requests")),
        ("Stage A decisions: planned / attempted", f"{len(stage_a)} / {a_attempts}"),
        ("Stage A statuses", _statuses(stage_a)),
        ("Stage B episodes: planned / attempted", f"{len(stage_b)} / {sum(r.get('request_attempts', 0) > 0 for r in stage_b)}"),
        ("Stage B statuses", _statuses(stage_b)),
        ("Stage B request attempts", b_attempts),
        ("Stage B terminal successes / planned", f"{sum(r.get('success') is True for r in stage_b)} / {len(stage_b)}"),
        ("Pre-recovery available / reached measurement", f"{sum(r.get('pre_recovery_available') is True for r in stage_b)} / {sum(type(r.get('pre_recovery_available')) is bool for r in stage_b)}"),
        ("Pre-recovery measurement not reached", sum(r.get("pre_recovery_available") is None for r in stage_b)),
        ("Recovery attempts", sum(r.get("recovery_attempted") is True for r in stage_b)),
        ("Synthetic action cost, all episodes including partial/failed", sum(r.get("synthetic_cost_units", 0) for r in stage_b)),
        ("Synthetic action cost, completed episodes only", sum(r.get("synthetic_cost_units", 0) for r in completed_b)),
        ("API dollars", accounting.get("api_dollars")),
        ("Subscription usage", accounting.get("subscription_usage")),
        ("Subscription credits consumed", accounting.get("subscription_credits")),
        ("Total measured request latency (seconds)", _measurement(metrics, attempts, "latency_seconds")),
        *((name.replace("_", " ").capitalize(), _measurement(metrics, attempts, name, usage=True))
          for name in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")),
    ])
    counts = summary.get("attempt_status_counts", {})
    lines += ["Request statuses: " + "; ".join(f"{_text(k)}={v}" for k, v in sorted(counts.items())) + ".", "",
              "Input includes cached input; reasoning may overlap output. These buckets are not added together. "
              "Reported subtotals with incomplete coverage are not full-run totals. Synthetic action units, "
              "tokens, subscription credits, and API dollars are distinct quantities.", ""]
    lines += _table(["Transport field", "Recorded value"], [
        ("Model alias", contract.get("model")),
        ("Immutable model revision", contract.get("model_revision")),
        ("CLI/client version", contract.get("installed_cli_version", contract.get("reviewed_cli_version"))),
        ("Reasoning effort", contract.get("reasoning_effort")),
        ("Underlying provider retries", contract.get("provider_retries")),
        ("Hard output token cap", contract.get("hard_output_token_cap")),
        ("Subscription charge bound", contract.get("subscription_charge_bound")),
        ("Cross-request state contract", contract.get("cross_request_state")),
    ])
    lines += ["Missing transport/accounting fields mean unknown, not zero. A model alias is not an immutable revision.", "",
              "## Stage A: inspection decisions", "",
              "Expected extra costs and regret use the exact uniform-route population calibration, in synthetic action units. "
              "Replicates are listed separately; no significance calculation is made.", ""]
    lines += _table(["Cell", "Replicate", "Status", "Inspect", "Expected extra cost", "Exact regret"], [
        (row["scenario"], row.get("replicate"), row.get("status"), row.get("inspection"),
         row.get("expected_extra_cost"), row.get("excess_cost"))
        for row in sorted(stage_a, key=lambda r: (r["scenario"], r.get("replicate", 0)))])
    lines += ["## Stage B: retention and recovery", "",
              "Reliable scripted recovery can make even empty retention succeed. Terminal success primarily checks execution; "
              "pre-recovery availability and synthetic completion cost carry the retention signal. "
              "Each row remains present after failure or a budget stop.", "",
              "Cost delta compares a completed episode with the fixed population policy using the same inspection choice on "
              "the exact same fixture. Partial episode costs receive no completed-reference delta.", ""]
    rows = []
    for row in sorted(stage_b, key=lambda r: (r["scenario"], r["render_mode"], r["arm"])):
        rows.append((row["scenario"], row["render_mode"], row["arm"], row.get("status"),
                     row.get("request_attempts"), row.get("inspection"), row.get("pre_recovery_available"),
                     row.get("recovery_attempted"), row.get("success"), row.get("synthetic_cost_units"),
                     _completed_delta(row)))
    lines += _table(["Cell", "Mode", "Arm", "Status", "Requests", "Inspect", "Pre-recovery", "Recovered", "Success", "Cost", "Cost delta"], rows)
    references = {}
    for row in stage_b:
        key = (row["scenario"], row.get("route_index"))
        reference = row.get("fixed_policy_reference", {})
        if key in references and reference != references[key]:
            raise ValueError("Fixed references disagree across the same scenario and route")
        references[key] = reference
    lines += ["### Fixed-policy comparison on the exact fixture", "",
              "Both policies were fixed from the public population before evaluation. These realized costs are not "
              "population expectations and must not be used to refit the policy to this one target.", ""]
    lines += _table(["Cell", "Route", "Skip cost", "Skip pre-recovery", "Inspect cost", "Inspect pre-recovery"], [
        (cell, route, ref.get("skip", {}).get("synthetic_cost_units"), ref.get("skip", {}).get("pre_recovery_available"),
         ref.get("inspect", {}).get("synthetic_cost_units"), ref.get("inspect", {}).get("pre_recovery_available"))
        for (cell, route), ref in sorted(references.items(), key=lambda item: (item[0][0], str(item[0][1])))])
    if metrics:
        lines += ["### Stage B reported token usage", "",
                  "Coverage counts include unsuccessful request attempts. Unknown or missing usage is not replaced by zero.", ""]
        lines += _table(["Cell", "Mode", "Arm", "Input tokens", "Output tokens"], [
            (row["scenario"], row["render_mode"], row["arm"],
             _measurement(_episode_metrics(summary, row), row.get("request_attempts", 0), "input_tokens", usage=True),
             _measurement(_episode_metrics(summary, row), row.get("request_attempts", 0), "output_tokens", usage=True))
            for row in sorted(stage_b, key=lambda r: (r["scenario"], r["render_mode"], r["arm"]))])
    lines += ["## Interpretation limits", "",
              "One development template and one route were used. Repeated modes and arms reuse paired fixtures; "
              "they do not increase the number of independent routes. The reserved held-out sample remains unrun by this runner "
              "and, when run, is a debugging exercise. This report establishes no native-harness comparison, statistical "
              "significance, generalization, or general superiority.", ""]
    if summary.get("fake"):
        lines += ["These are fake-client software checks, not model-performance results.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--requests", type=Path, help="Optional structured request ledger, used only for accounting")
    parser.add_argument("--transport-manifest", type=Path, help="Optional transport contract JSON")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    if args.requests:
        summary["request_metrics"] = [json.loads(line) for line in args.requests.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.transport_manifest:
        summary["transport_manifest"] = json.loads(args.transport_manifest.read_text(encoding="utf-8"))
    args.output.write_text(report(summary), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
