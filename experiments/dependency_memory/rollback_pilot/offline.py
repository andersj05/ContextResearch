"""Save E0 evidence and E1/E2 preparation; no provider transport exists here."""
from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import analyze, report_markdown
from .code_runner import DockerRunner
from .controller import Controller, write_new
from .grading import MathChecker
from .independent_math import exhaustive_solutions
from .math_tasks import generate_math
from .prepare import PACKAGE, ROOT, prepare_bundle, source_bindings, verify_bundle
from .records import digest, strict_loads, wire
from .transport import FakeTransport


def scripted_math_transport(cohort):
    """Intentional bad branches and known answers are engineering fixtures only."""
    evaluators = {task.task_id: evaluator for task, evaluator in cohort}
    def script(identity, request):
        data = strict_loads(request.data()["messages"][1]["content"])
        stage = identity.stage
        if stage == "checkpoint":
            return wire({"facts": [], "open_requirements": ["Satisfy all declared public predicates."],
                         "tentative_options": [{"id": "O1", "method": "Authored engineering trial.", "unverified_assumptions": []}],
                         "possible_checks": ["Substitute every value."]})
        if stage == "branch":
            task = next(task for task, _ in cohort if task.task_id == identity.task_id)
            n = len(task.data()["variables"])
            bad = [0] * n
            # Never interpret this deliberate failure as a natural model branch.
            if MathChecker(task).violation(bad) is None:
                bad[0] = task.data()["bounds"]["maximum"] + 1
            return wire({"status": "candidate", "chosen_option": "O1", "assumptions": [],
                         "observations": [{"statement": "Authored E0 branch ROUTING_E0_ONLY_CANARY", "source_ids": ["task"]}],
                         "artifact": {"values": bad}})
        if stage == "lesson":
            return wire({"failure_kind": "public_constraint_violation", "evidence_ids": [data["feedback"]["receipt_id"]],
                         "refuted_claims": ["This candidate satisfies every public predicate."],
                         "retained_observations": [], "uncertainties": ["A valid assignment is still required."]})
        if stage == "summary":
            return wire({"summary": "The submitted candidate failed its public check. The original predicates still apply."})
        if stage == "terminal":
            return wire(evaluators[identity.task_id].data()["witness"])
        raise ValueError("unplanned fake stage")
    return FakeTransport(script)


def acceptance(checks):
    """Every package test must pass, including the actual Docker checks, at these sources."""
    if not checks or not checks["successful"] or not checks["docker_image"]:
        return False
    if checks["source_bindings"] != source_bindings():
        return False
    # unittest discovery prefixes differ between package and repository commands.
    present = {".".join(row["test_id"].split(".")[-4:]): row["status"] for row in checks["test_results"]}
    from unittest import TestLoader
    def flatten(suite):
        for item in suite:
            if hasattr(item, "id"):
                yield item
            else:
                yield from flatten(item)
    expected = TestLoader().loadTestsFromNames(["experiments.dependency_memory.rollback_pilot." + p.stem for p in sorted(PACKAGE.glob("test_*.py"))])
    ids = [".".join(test.id().split(".")[-4:]) for test in flatten(expected)]
    return bool(ids) and all(present.get(key) == "passed" for key in ids)


def run_offline(folder, checks=None, docker_image=None):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    before = source_bindings()
    accepted = acceptance(checks)
    if checks:
        write_new(folder / "package_checks.json", wire(checks) + "\n")
    audit = DockerRunner(docker_image).audit() if docker_image else None
    cohort = generate_math()
    math_certificates = []
    for task, evaluator in cohort:
        universe, solutions = exhaustive_solutions(task.data())
        checked = {values for values in universe if MathChecker(task).violation(values) is None}
        if checked != solutions or not solutions or tuple(evaluator.data()["witness"]["values"]) not in solutions:
            raise ValueError("independent math grader disagreement")
        math_certificates.append({"task_id": task.task_id, "public_sha256": task.hash, "enumerated_candidates": len(universe),
                                  "valid_assignments": len(solutions), "solution_set_sha256": digest(wire(sorted(solutions))),
                                  "independent_grader_agreement": True})
    write_new(folder / "math_certificates.json", wire(math_certificates) + "\n")
    controller = Controller(folder / "scripted_controller", "E0_AUTHORED_2026_10_08", scripted_math_transport(cohort))
    try:
        rows = controller.run(cohort)
        events = controller.ledger.events()
        result = analyze(rows, events)
        write_new(folder / "analysis.json", wire(result) + "\n")
        write_new(folder / "report.md", report_markdown(result))
    finally:
        controller.ledger.close()
    manifest = prepare_bundle(folder / "launch_review", runtime_audit=audit, e0_accepted=accepted)
    verified = verify_bundle(folder / "launch_review")
    if before != source_bindings():
        raise ValueError("sources changed while producing E0 evidence")
    summary = {"schema_version": "rollback-e0-1", "as_of": "2026-10-08", "evidence_kind": "offline_engineering_only",
               "model_calls": 0, "provider_spend_usd": "0", "E0_engineering_acceptance": accepted,
               "scripted_tasks": len(rows), "scripted_calls": len({x["call_id"] for x in events}),
               "independently_enumerated_math_candidates": sum(x["enumerated_candidates"] for x in math_certificates),
               "math_certificates": math_certificates, "runtime_image": docker_image,
               "prepared_bundle": verified, "open_live_gates": manifest["open_gates"],
               "limitations": ["Scripted candidate failures and successes are not model observations.",
                               "No LiveCodeBench source/license/reference package has been imported.",
                               "Byte admission units are synthetic; no provider tokenizer/endpoint audit is claimed.",
                               "Passing these container probes does not certify Docker or private provider internals."],
               "source_bindings": before}
    write_new(folder / "summary.json", wire(summary) + "\n")
    return summary


def verify_evidence(folder):
    folder = Path(folder)
    summary = strict_loads((folder / "summary.json").read_text(encoding="utf-8"))
    if summary["model_calls"] != 0 or summary["provider_spend_usd"] != "0" or summary["evidence_kind"] != "offline_engineering_only":
        raise ValueError("E0 cannot be represented as model observations")
    checked = verify_bundle(folder / "launch_review")
    certificates = strict_loads((folder / "math_certificates.json").read_text(encoding="utf-8"))
    if certificates != summary["math_certificates"]:
        raise ValueError("math summary/certificate mismatch")
    rows = [strict_loads(line) for line in (folder / "scripted_controller" / "tasks.jsonl").read_text(encoding="utf-8").splitlines()]
    events = [strict_loads(line) for line in (folder / "scripted_controller" / "usage_events.jsonl").read_text(encoding="utf-8").splitlines()]
    if strict_loads((folder / "analysis.json").read_text(encoding="utf-8")) != analyze(rows, events):
        raise ValueError("analysis differs from saved task/usage evidence")
    if (folder / "report.md").read_text(encoding="utf-8") != report_markdown(analyze(rows, events)):
        raise ValueError("report differs from saved analysis")
    for row in rows:
        if row["context_hashes"]["K"]["shared"] != row["context_hashes"]["R"]["shared"]:
            raise ValueError("primary shared fields differ")
    for event in events:
        if event["state"] != "planned":
            continue
        key = event["call_id"]
        request = strict_loads((folder / "scripted_controller" / "requests" / (key + ".json")).read_text(encoding="utf-8"))
        if digest(wire(request)) != event["request_hash"]:
            raise ValueError("saved request hash mismatch")
        if event["identity"]["stage"] == "terminal" and event["identity"]["arm"] in {"R", "Z", "G"} and "ROUTING_E0_ONLY_CANARY" in wire(request):
            raise ValueError("removed branch leaked into a scripted continuation")
    return {"scripted_tasks": len(rows), "scripted_calls": len({x["call_id"] for x in events}), **checked}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checks", type=Path)
    parser.add_argument("--docker-image")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        print(wire(verify_evidence(args.output)))
    else:
        checks = strict_loads(args.checks.read_text(encoding="utf-8")) if args.checks else None
        summary = run_offline(args.output, checks, args.docker_image)
        print(wire({k: summary[k] for k in ("E0_engineering_acceptance", "scripted_tasks", "scripted_calls", "model_calls", "open_live_gates")}))


if __name__ == "__main__":
    main()
