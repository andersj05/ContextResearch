"""Regenerate execution-graded, offline feedback-loop diagnostics."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from .feedback import Verifier, certificate_replays, learn, successful_candidate
from .workflow import Candidate, Contract, KEYS, Workflow
from ..collision_audit.engine import canonical


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
MODES = ("one_pass", "enumerate", "last_only", "accumulated", "critical_fields")


def summarize(rows):
    return {"episodes": len(rows), "successful": sum(r["success"] for r in rows),
            "retained_available": sum(r["retained_available"] for r in rows),
            "recovery_units": sum(r["recovery_units"] for r in rows),
            "environment_units": sum(r["environment_units"] for r in rows),
            "max_parent_records": max(r["parent_records"] for r in rows),
            "max_child_records": max(r["child_records"] for r in rows),
            "max_parent_utf8_bytes": max(r["parent_utf8_bytes"] for r in rows),
            "max_child_utf8_bytes": max(r["child_utf8_bytes"] for r in rows)}


def evaluate(workflow, mode, detail=False):
    result = learn(workflow, mode)
    learned = successful_candidate(workflow, result)
    # Baseline proposals are still executable after the verifier rejects them.
    candidate = learned or (workflow.critical_fields if mode == "critical_fields" else
                            workflow.initial if mode == "one_pass" else None)
    if candidate is not None:
        result["execution"] = summarize(workflow.execution(candidate))
    if learned is not None:
        replays = certificate_replays(workflow, learned)
        result["certified_replay_successes"] = sum(r["success"] for r in replays)
    if not detail:
        result.pop("history")
    return result


def feedback_channel_check():
    # Same parent memory (job-0/job-1), missing job-2. No new world-dependent
    # observation means any deterministic decoder chooses one of its two tokens.
    workflow = Workflow()
    p = workflow.problem(workflow.initial, 3)  # pair (0,2), target 2
    best = sum(max(Counter(next(iter(p.tasks[0].accepted[i])) for i in cell).values())
               for cell in p.cells)
    return {"worlds": p.n, "maximum_correct_without_new_channel": best,
            "correct_with_true_missing_value_feedback": p.n,
            "conditional_feedback_alphabet": 2,
            "conditional_feedback_bits": 1,
            "warning": "The actual missing value is a new information channel; global offline constraints are not that channel."}


def certificate():
    main = Workflow()
    primary = {m: evaluate(main, m, detail=True) for m in MODES}
    matrix = []
    for parent in range(4):
        for child in range(3):
            for recovery, budget in ((False, 0), (True, 0), (True, 2), (True, 3)):
                contract = Contract(parent_capacity=parent, child_capacity=child,
                                    recovery=recovery, recovery_budget=budget)
                w = Workflow(contract)
                matrix.append({"contract": asdict(contract),
                               "arms": {mode: evaluate(w, mode) for mode in MODES}})
    narrow = learn(main, routes=(0, 1))
    narrow_candidate = successful_candidate(main, narrow)
    unseen_failure = Verifier(main, routes=(2, 3, 4, 5)).first_failure(narrow_candidate)
    timing = {}
    for early in (False, True):
        w = Workflow(Contract(child_capacity=1, early_target=early))
        timing["early_target" if early else "late_target"] = evaluate(w, "accumulated", detail=True)
    code_workflow = Workflow(Contract(child_capacity=1))
    coded = Candidate(KEYS[1:], "coded")
    if Verifier(code_workflow).first_failure(coded) is not None:
        raise AssertionError("Identifier-channel code should be feasible")
    code_replay = certificate_replays(code_workflow, coded)
    support = [len(code_workflow.problem(coded, r).cells) for r in range(6)]
    source_paths = [HERE / name for name in ("workflow.py", "feedback.py", "run.py")]
    source_paths += [HERE.parent / "artifact_workflow.py", HERE.parent / "collision_audit/engine.py"]
    counts = {m: dict(Counter(row["arms"][m]["status"] for row in matrix)) for m in MODES}
    return {"schema": 1, "date": "2026-09-22", "model_calls": 0,
            "evidence": "constructed execution-graded finite diagnostics, not sampled LLM trials",
            "information_contract": {
                "worlds": 8, "manifest_target_routes": 6,
                "public_catalog": "two tokens per job/revision, fixed before the realized world",
                "revision_correlation": "revision two uses the same binary coordinate as revision one",
                "parent_before_manifest": True, "target_after_child_unless_explicit_treatment": True,
                "feedback": "global offline unsafe groups; no realized-instance label at execution",
                "memory_unit": "atomic tagged receipt records; JSON bytes separately measured",
                "rescue_memory": "no further forced memory boundary during final recovery",
                "source_access": "only selected parent records and the new build receipt reach child selector",
                "recovery_price": 3, "mandatory_environment_units_per_episode": 9,
                "audit_compute": "audit calls, cell checks, constraint checks, constructed candidate/routes; no wall-time or dollar equivalence",
                "isolation": "trusted scripted API; evaluator fixtures are not policy inputs, not process sandboxing"},
            "source_sha256": {str(p.relative_to(HERE.parent)).replace("\\", "/"):
                              hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
            "primary": primary, "matrix": matrix, "matrix_status_counts": counts,
            "timing": timing,
            "limited_probe_control": {"training_routes": [0, 1], "training": narrow,
                                      "unprobed_routes": [2, 3, 4, 5],
                                      "unprobed_failure": asdict(unseen_failure),
                                      "all_route_execution": summarize(main.execution(narrow_candidate))},
            "identifier_channel": {"candidate": coded.name,
                                   "child_records": 1, "states_per_public_route": support,
                                   "state_bits_per_public_route": 2,
                                   "retained_only": summarize(code_workflow.execution(coded)),
                                   "catalog_decoder": summarize(code_workflow.execution(coded, coded_decode=True)),
                                   "certificate_replay_successes": len(code_replay),
                                   "scope": "finite public two-value catalog and value-dependent record choice; no arbitrary-token compression claim"},
            "late_feedback_channel": feedback_channel_check(),
            "rare_obligation": {"failure_probability": "1/100", "independent_probes": 20,
                                "miss_probability": str(Fraction(99, 100) ** 20),
                                "miss_probability_decimal": float(Fraction(99, 100) ** 20),
                                "scope": "elementary hypothetical iid probe calculation, not measured prevalence"}}


def report(data):
    lines = ["# Feedback before forgetting: executable diagnostic results", "",
             "September 22, 2026. Zero model calls. All worlds and routes are constructed.", "",
             "The adapter executes the existing artifact/manifest environment, grades submitted",
             "receipts through its terminal verifier, and passes exact retained/public channels",
             "to the collision auditor. There are two enforced record-memory boundaries.", "",
             "## Main case: two parent records, two child records, no recovery", "",
             "| Method | Audit outcome | Full audits | Cell checks | Constraint checks | Executed success |",
             "|---|---|---:|---:|---:|---:|"]
    for name, row in data["primary"].items():
        execution = row.get("execution")
        success = f"{execution['successful']}/{execution['episodes']}" if execution else "no accepted candidate"
        lines.append(f"| {name} | {row['status']} | {row['audit_calls']} | {row['cell_checks']} | {row['constraint_checks']} | {success} |")
    lines += ["", "The accumulated loop retains both unsafe-group constraints and selects job-1/job-2.",
              "The last-only loop cycles between single-field repairs. Enumeration reaches the same",
              "solution with more full audits, but the accumulated loop also pays constraint checks",
              "and constructs counterfactual candidate states. These counts do not establish a CPU",
              "speedup. The workflow-aware critical-fields baseline already chooses the solution:",
              "**no advantage over that strong baseline is established.**", "",
              "The successful memories use two records at each boundary. JSON byte lengths are in",
              "the certificate. Each executed episode has nine mandatory environment units;",
              "an allowed recovery adds three. Offline synthesis work is reported separately and",
              "is never represented as free deployment work or mixed with record/bit counts.", "",
              "## Binding second boundary and feedback timing", "",
              f"With one child record and a late target, the declared priority-selector family is {data['timing']['late_target']['status']}.",
              f"Moving the target before that boundary gives {data['timing']['early_target']['status']}.",
              "This changes the information order. It does not show that feedback can reconstruct",
              "an already lost value. Candidate-family exhaustion is not impossibility for arbitrary",
              "encoders, as the identifier-channel control below demonstrates.", "",
              "## A record identifier can carry hidden coding information", "",
              "For two independent binary receipt values, choose the lower-key receipt when their",
              "bits agree and the upper-key receipt otherwise. A public finite-catalog decoder can",
              "then recover both values from one tagged record: the selected key carries equality",
              "information. All 48 executable outcomes and certificate replays pass. There are FOUR",
              "possible retained states per public route, hence two bits, despite one record slot.",
              "Ordinary retained-receipt submission succeeds only 24/48 for this same representation.",
              "This is a deliberate information-channel control, not practical arbitrary-token compression.", "",
              "## Partial probes and late oracle feedback", "",
              "Certifying only the two routes for manifest job-0/job-1 leaves a reproducible failure",
              "on an unprobed manifest. A hypothetical 1% failure family escapes 20 independent probes",
              f"with probability (99/100)^20 = {data['rare_obligation']['miss_probability_decimal']:.6f}.",
              "That arithmetic is not a measurement of rare-task prevalence or a claim about adaptive probes.", "",
              "After job-2's value is deleted, the best decoder using unchanged accessible channels",
              "gets 4/8 worlds correct on the selected route. An oracle disclosing the missing value",
              "gets 8/8 by adding one conditional bit under the two-value catalog. Such feedback is",
              "a recovery channel; it cannot be excluded from the information budget.", "",
              "## Capacity and recovery sweep", "",
              "48 contracts cross four parent capacities, three child capacities and four archive/budget",
              "settings. Each of five methods is run on every contract; these are deterministic",
              "diagnostics, not 240 independent trials. Counts below summarize audit outcomes.", "",
              "| Method | Certified | Rejected | Cycles | Exhausted candidate family |", "|---|---:|---:|---:|---:|"]
    for m, counts in data["matrix_status_counts"].items():
        lines.append(f"| {m} | {counts.get('certified', 0)} | {counts.get('rejected', 0)} | {counts.get('cycle', 0)} | {counts.get('exhausted_family', 0)} |")
    lines += ["", "## Boundaries", "",
              "A finite public token catalog, deliberate revision correlation, trusted Python",
              "interfaces and hand-written selectors make this a calibration artifact. No semantic",
              "prose compiler, natural-task distribution, LLM performance gain, complete end-to-end",
              "cost advantage or publication novelty has been established. Final recovery has no",
              "additional forced compaction. The earlier collision solver and historical model data",
              "are unchanged. The synthesis algorithm is standard finite candidate elimination.", "",
              "Reproduce: `python -m experiments.dependency_memory.feedback_compaction.run`.", "",
              "[Research note](../../../research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md).", ""]
    return "\n".join(lines)


def main():
    data = certificate()
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "feedback_compaction_certificate.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (RESULTS / "feedback_compaction_report.md").write_text(report(data), encoding="utf-8", newline="\n")
    print(json.dumps({"contracts": len(data["matrix"]), "model_calls": 0,
                      "status_counts": data["matrix_status_counts"]}, indent=2))


if __name__ == "__main__":
    main()
