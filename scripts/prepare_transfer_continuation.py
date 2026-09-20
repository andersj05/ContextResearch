"""Prepare an OFFLINE certificate for remaining first model submissions.

This never creates a provider client or sends a request. Existing final evidence
must pass its saved-run auditor before a certificate can be prepared. It does
not authorize continuation or change the original frozen no-resumption rule;
any execution would require a separate documented operational amendment.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))
from audit_transfer_run import audit, digest, require
from luna_appserver import strict_json
from transfer_interface import request_bytes

VERSION = "transfer_first_submission_continuation_certificate_v1"
RESERVATION = Decimal("10.4025")
WORKER_CAP = Decimal(50)
TOTAL_CAP = Decimal(200)
FACTORS = ("jobs", "framing", "guarantee", "guidance", "refresh_rule")
FACTOR_VALUES = ((6, 12), ("compact", "workflow"), ("explicit_optimal", "unspecified"),
                 ("generic", "prospective"), ("first", "last", "none"))


def exact(value, label):
    require(type(value) is str, "Missing exact decimal: " + label)
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("Invalid exact decimal: " + label) from error
    require(result.is_finite() and result >= 0, "Negative or nonfinite amount: " + label)
    return result


def classify_attempt(attempt):
    """Classify only persisted dispatch/accounting evidence, never answer quality.

    A dispatch flag is set immediately before turn/start. A retained reservation
    counts conservatively as a dispatched attempt even if server acceptance is
    unknown. Missing metadata alone cannot establish that no request was sent.
    """
    status, meta = attempt.get("status"), attempt.get("provider_metadata")
    require(type(meta) is dict, "Ambiguous dispatch: missing provider metadata")
    require(status in ("completed", "policy_failure", "transport_failure"),
            "Ambiguous dispatch: unfinished or unknown attempt status")
    dispatched = meta.get("dispatched")
    if dispatched is True:
        require(type(meta.get("attempt_ticket")) is int and meta["attempt_ticket"] > 0,
                "Ambiguous dispatch: missing reservation ticket")
        account = meta.get("credit_accounting")
        require(type(account) is dict and account.get("ticket") == meta["attempt_ticket"],
                "Ambiguous dispatch: missing or inconsistent accounting")
        if account.get("status") == "settled":
            spent = exact(account.get("conservative_credit_equivalent_exact"), "settled attempt")
            require(spent <= RESERVATION, "Settled usage exceeds reserved envelope")
            return "dispatched", spent, Decimal(0)
        require(account.get("status") == "reservation_retained" and status == "transport_failure",
                "Ambiguous dispatch: missing settlement or retained reservation")
        return "dispatched_uncertain", Decimal(0), RESERVATION
    require(status == "transport_failure", "Non-dispatched attempt cannot contain a model outcome")
    if dispatched is False:
        require(not any(name in meta for name in ("attempt_ticket", "credit_accounting", "usage", "turn_id")),
                "Contradictory preflight dispatch or usage evidence")
        return "preflight_only", Decimal(0), Decimal(0)
    # The frozen worker sets last_metadata={} and checks the shared gate before
    # client.complete. This is the only missing-flag case with a proved origin.
    require(not meta and attempt.get("error_type") == "StudyStopped",
            "Ambiguous dispatch: absent flag is not proof of no generation")
    return "preflight_only", Decimal(0), Decimal(0)


def public_schedule(plan):
    require(type(plan) is dict and plan.get("version") == "transfer_study_v1", "Unexpected original study plan")
    cases = plan.get("cases")
    require(type(cases) is list and len(cases) == 1536 and len({c["case_id"] for c in cases}) == 1536,
            "Original plan must contain exactly 1536 unique cases")
    for field, expected in (("maximum_model_requests", 1536), ("workers", 4),
                           ("worker_request_cap", 384), ("credit_equivalent_cap", 200),
                           ("worker_credit_equivalent_cap", 50)):
        require(type(plan.get(field)) is int and plan[field] == expected, "Original allocation mismatch: " + field)
    result = []
    for index, case in enumerate(cases):
        require(type(case.get("block")) is int and 0 <= case["block"] < 32
                and type(case.get("worker")) is int and case["worker"] == case["block"] % 4,
                "Original worker assignment mismatch")
        raw = request_bytes(case["request"])
        require(case.get("request_sha256") == hashlib.sha256(raw).hexdigest()
                and case.get("request_bytes") == len(raw), "Original public request hash mismatch")
        result.append({"original_index": index, **{k:case[k] for k in
            ("case_id", "block", "worker", *FACTORS, "request_sha256", "request_bytes")}})
    for block in range(32):
        group = [c for c in result if c["block"] == block]
        require(Counter(tuple(c[k] for k in FACTORS) for c in group) == Counter(product(*FACTOR_VALUES)),
                "Original factorial block is incomplete or duplicated")
    for worker in range(4):
        blocks = [case["block"] for case in result if case["worker"] == worker]
        require(len(blocks) == 384 and blocks == sorted(blocks), "Original worker schedule order changed")
    return result


def certificate_from_evidence(phases):
    """Pure certificate construction from evidence already audited by load_phase.

    Kept separate for synthetic invariant tests. Call prepare_continuation for
    filesystem evidence; caller-supplied dictionaries are not authenticated.
    """
    require(type(phases) is list and phases, "At least one finalized prior phase is required")
    schedule = public_schedule(phases[0]["manifest"]["plan"])
    by_id = {case["case_id"]: case for case in schedule}
    dispatched, histories, threads = {}, {case["case_id"]: [] for case in schedule}, set()
    settled = [Decimal(0) for _ in range(4)]
    uncertain = [Decimal(0) for _ in range(4)]
    phase_records, seen_manifests = [], set()
    total_host_attempts = 0
    for phase_index, phase in enumerate(phases):
        manifest, prior_audit = phase["manifest"], phase["audit"]
        manifest_sha = digest(manifest)
        require(manifest_sha not in seen_manifests, "Duplicate prior phase manifest")
        seen_manifests.add(manifest_sha)
        require(prior_audit.get("passed") is True and prior_audit.get("manifest_sha256") == manifest_sha,
                "Prior phase lacks its matching fresh audit")
        require(manifest.get("fake") is False and prior_audit.get("fake") is False,
                "Fake model evidence cannot authorize remaining real submissions")
        require(manifest.get("source_commit") == prior_audit.get("source_commit")
                and prior_audit.get("source_blobs_checked", 0) > 0,
                "Prior phase lacks frozen Git source provenance")
        require(digest(manifest["plan"]) == manifest.get("plan_sha256"), "Prior plan hash mismatch")
        require(public_schedule(manifest["plan"]) == schedule, "Public schedule changed between prior phases")
        workers = phase.get("workers")
        require(type(workers) is list and len(workers) == 4, "Four finalized worker ledgers are required")
        phase_dispatched = 0
        phase_spent = phase_uncertain = Decimal(0)
        phase_case_ids = set()
        worker_records = []
        for worker, evidence in enumerate(workers):
            ledger, summary = evidence["ledger"], evidence["summary"]
            require(type(ledger) is list and summary.get("worker") == worker, "Worker evidence identity mismatch")
            require(digest(ledger) == summary.get("request_audit_sha256"), "Final worker ledger hash mismatch")
            require(summary.get("request_attempts") == len(ledger) and len(ledger) <= 384,
                    "Worker host-attempt count mismatch")
            spent_here = uncertain_here = Decimal(0)
            worker_dispatches = 0
            for index, attempt in enumerate(ledger):
                case_id = attempt.get("case_id")
                require(case_id in by_id and case_id not in phase_case_ids, "Unknown or duplicate case within prior phase")
                phase_case_ids.add(case_id)
                case = by_id[case_id]
                require(attempt.get("attempt") == index + 1 and attempt.get("worker") == worker == case["worker"]
                        and attempt.get("block") == case["block"], "Prior case identity mismatch")
                raw = attempt.get("request_utf8", "").encode("utf-8")
                require(hashlib.sha256(raw).hexdigest() == attempt.get("request_sha256") == case["request_sha256"]
                        and len(raw) == attempt.get("request_bytes") == case["request_bytes"], "Prior public request bytes changed")
                kind, amount, reserved = classify_attempt(attempt)
                require(case_id not in dispatched, "Previously dispatched case was attempted again: " + case_id)
                meta = attempt["provider_metadata"]
                thread = meta.get("thread_id")
                if thread is not None:
                    require(type(thread) is str and thread and thread not in threads, "Thread reused across prior phases")
                    threads.add(thread)
                history = {"phase_index":phase_index, "manifest_sha256":manifest_sha, "worker":worker,
                    "attempt":attempt["attempt"], "status":attempt["status"], "classification":kind,
                    "settled_credit_equivalent_exact":str(amount), "retained_reservation_exact":str(reserved)}
                histories[case_id].append(history)
                if kind != "preflight_only":
                    dispatched[case_id] = history
                    worker_dispatches += 1
                spent_here += amount
                uncertain_here += reserved
            budget = summary.get("credit_budget", {})
            require(budget.get("pending_ticket") is None, "Unfinished worker credit reservation")
            require(exact(budget.get("cap_credit_equivalent_exact"), "phase worker cap") <= WORKER_CAP,
                    "Prior worker cap exceeds original allocation")
            require(exact(budget.get("settled_credit_equivalent_exact"), "worker settled") == spent_here
                    and exact(budget.get("uncertain_credit_reservations_exact"), "worker uncertain") == uncertain_here
                    and exact(budget.get("committed_credit_equivalent_exact"), "worker committed") == spent_here + uncertain_here,
                    "Worker committed budget differs from attempt evidence")
            require(type(summary.get("model_requests")) is int and summary["model_requests"] == worker_dispatches,
                    "Worker model-attempt count mismatch")
            settled[worker] += spent_here
            uncertain[worker] += uncertain_here
            require(settled[worker] + uncertain[worker] <= WORKER_CAP, "Combined prior worker budget exceeds 50 equivalents")
            phase_dispatched += worker_dispatches
            phase_spent += spent_here
            phase_uncertain += uncertain_here
            total_host_attempts += len(ledger)
            worker_records.append({"worker":worker, "ledger_sha256":digest(ledger),
                "summary_sha256":digest(summary), "host_attempts":len(ledger), "model_attempts":worker_dispatches})
        require(prior_audit.get("model_requests") == phase_dispatched
                and exact(prior_audit.get("settled_credit_equivalent"), "audited settled") == phase_spent
                and exact(prior_audit.get("retained_credit_equivalent"), "audited retained") == phase_uncertain,
                "Fresh prior audit disagrees with classified attempts")
        phase_records.append({"phase_index":phase_index, "run_directory":phase["run_directory"],
            "manifest_sha256":manifest_sha, "plan_sha256":manifest["plan_sha256"],
            "source_commit":manifest["source_commit"], "audit_sha256":digest(prior_audit),
            "model_attempts":phase_dispatched, "worker_evidence":worker_records})
    require(len(dispatched) <= 1536 and sum(settled) + sum(uncertain) <= TOTAL_CAP, "Combined study allocation exceeded")
    dispositions = [{**case, "disposition":"already_dispatched" if case["case_id"] in dispatched else "eligible_first_submission",
        "prior_attempt_history":histories[case["case_id"]]} for case in schedule]
    worker_certificates = []
    for worker in range(4):
        eligible = [case for case in dispositions if case["worker"] == worker and case["disposition"] == "eligible_first_submission"]
        used = sum(case["worker"] == worker and case["case_id"] in dispatched for case in schedule)
        remaining = WORKER_CAP - settled[worker] - uncertain[worker]
        require(len(eligible) == 384 - used, "Residual worker cases do not reconcile")
        worker_certificates.append({"worker":worker, "prior_model_attempts":used,
            "remaining_model_attempt_cap":len(eligible), "eligible_case_ids":[case["case_id"] for case in eligible],
            "prior_settled_credit_equivalent_exact":str(settled[worker]),
            "prior_retained_reservations_exact":str(uncertain[worker]),
            "remaining_credit_equivalent_cap_exact":str(remaining),
            "first_reservation_fits":not eligible or remaining >= RESERVATION})
    certificate = {"version":VERSION, "status":"OFFLINE PROPOSAL; NO GENERATION AUTHORIZED OR PERFORMED",
        "original_public_schedule_sha256":digest(schedule), "original_planned_cases":1536,
        "prior_phases":phase_records, "prior_host_attempts":total_host_attempts,
        "prior_model_attempts":len(dispatched), "remaining_model_attempt_cap":1536-len(dispatched),
        "aggregate_credit_equivalent_cap_exact":"200",
        "prior_settled_credit_equivalent_exact":str(sum(settled)),
        "prior_retained_reservations_exact":str(sum(uncertain)),
        "remaining_credit_equivalent_cap_exact":str(TOTAL_CAP-sum(settled)-sum(uncertain)),
        "per_attempt_reservation_exact":str(RESERVATION), "workers":worker_certificates,
        "case_dispositions":dispositions, "new_model_requests":0, "changes_to_original_evidence":False,
        "response_quality_used_for_eligibility":False,
        "execution_conditions":["A separate versioned operational amendment and runner are required; the frozen run remains unchanged.",
            "Send only listed eligible cases in original worker order with byte-identical public requests.",
            "Never replace a prior dispatched success, policy failure, metered transport failure, or uncertain dispatch.",
            "Reverify every prior artifact hash before any later dispatch; reject changed evidence or unresolved ambiguity.",
            "Enforce residual per-worker credits and request caps, including outstanding reservations; no new 50-credit allocations.",
            "Preserve all prior host attempts and analyze one canonical outcome per original case, with phase and missingness visible."],
        "preparation_script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    certificate["certificate_sha256"] = digest(certificate)
    return certificate


def load_phase(run_dir):
    """Require finalized artifacts BEFORE reading any response ledger."""
    directory = Path(run_dir).resolve()
    required = [directory / name for name in ("manifest.json", "summary.json", "report.md")]
    required += [directory / f"worker-{worker}" / name for worker in range(4)
                 for name in ("manifest.json", "summary.json", "requests.json")]
    require(all(path.is_file() for path in required), "Prior run is not finalized; do not inspect active response ledgers")
    initial_hashes = {str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in required}
    prior_audit = audit(directory)
    manifest = strict_json((directory / "manifest.json").read_text(encoding="utf-8"))
    workers = [{"ledger":strict_json((directory / f"worker-{worker}" / "requests.json").read_text(encoding="utf-8")),
        "summary":strict_json((directory / f"worker-{worker}" / "summary.json").read_text(encoding="utf-8"))} for worker in range(4)]
    require(initial_hashes == {str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in required},
            "Prior evidence changed during verification; current run may still be active")
    try:
        recorded_directory = directory.relative_to(ROOT).as_posix()
    except ValueError:
        recorded_directory = directory.as_posix()
    return {"run_directory":recorded_directory, "manifest":manifest, "workers":workers, "audit":prior_audit}


def prepare_continuation(run_dirs):
    directories = [Path(path).resolve() for path in run_dirs]
    require(directories and len(set(directories)) == len(directories), "Distinct prior run directories are required")
    return certificate_from_evidence([load_phase(directory) for directory in directories])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prior-run-dir", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), "Continuation certificate must use a new output path")
    certificate = prepare_continuation(args.prior_run_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(certificate, output, indent=2, sort_keys=True, ensure_ascii=False)
        output.write("\n")
    print(json.dumps({"output":str(args.output), "prior_model_attempts":certificate["prior_model_attempts"],
        "remaining_model_attempt_cap":certificate["remaining_model_attempt_cap"],
        "remaining_credit_equivalent_cap_exact":certificate["remaining_credit_equivalent_cap_exact"],
        "new_model_requests":0}))


if __name__ == "__main__":
    main()
