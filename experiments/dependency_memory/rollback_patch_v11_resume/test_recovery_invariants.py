"""Independent synthetic checks of the operational recovery policy.

No task result, receipt, or score from the live allocation is loaded here.
These checks test selection and preservation, not provider behavior.
"""

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.dependency_memory.rollback_patch_v11_resume.recovery import (
    copy_history, select_jobs,
)


ARMS = ("K0", "R0", "KL", "RL")
WORKSPACE = Path(__file__).resolve().parents[3]


def fixture():
    prefix = {"task_id": "synthetic-task", "arm": "prefix", "job_id": "prefix"}
    jobs = [prefix] + [dict(task_id="synthetic-task", arm=arm, job_id=arm,
                            depends_on="prefix") for arm in ARMS]
    prefix_result = {"eligible": True, "reason": "natural_substantive_patch_mismatch",
                     "lesson": {"synthetic": "valid"}, "lesson_disposition": "valid",
                     "outcome": {"score": 0}}
    rows = [{"job": deepcopy(prefix), "result": prefix_result}]
    rows.extend({"job": deepcopy(job), "result": {
        "score": None, "disposition": "infrastructure_stop", "attempts": [],
    }} for job in jobs[1:])
    return {"jobs": jobs}, {"jobs": rows, "stopped": True}


def admission(arm, state="completed", stage="action", step=1):
    return {"call_id": f"{arm}-{stage}-{step}", "state": state,
            "identity": {"study": "synthetic", "task_id": "synthetic-task",
                         "track": "patch_factorial", "arm": arm,
                         "step": step, "stage": stage}}


def results(execution):
    return {row["job"]["arm"]: row["result"] for row in execution["jobs"]}


def decisions(plan):
    return {row["arm"]: (row["decision"], row["reason"]) for row in plan["jobs"]}


class RecoverySelectionInvariants(unittest.TestCase):
    def test_terminal_success_failure_and_capacity_are_all_retained(self):
        manifest, execution = fixture()
        rows = results(execution)
        terminals = ((1, "correct"), (0, "wrong_answer"),
                     (0, "repair_budget_exhausted"), (0, "context_capacity"))
        for arm, (score, disposition) in zip(ARMS, terminals):
            rows[arm].update(score=score, disposition=disposition)
        plan = select_jobs(manifest, execution, [admission("prefix")])
        self.assertEqual(plan["counts"], {"retain": 5})
        self.assertTrue(all(decisions(plan)[arm][1] == "terminal_continuation" for arm in ARMS))

    def test_selection_is_invariant_to_scores_and_private_diagnostics(self):
        manifest, execution = fixture()
        results(execution)["K0"].update(score=0, disposition="wrong_answer")
        before = select_jobs(manifest, execution, [admission("prefix")])
        altered = deepcopy(execution)
        for index, row in enumerate(altered["jobs"]):
            row["result"]["score"] = index % 2
            row["result"]["outcome"] = {"score": 1, "private_case": "changed"}
            row["result"]["private_diagnostics"] = {"treatment_winner": "R0"}
        after = select_jobs(manifest, altered, [admission("prefix")])
        self.assertEqual(decisions(before), decisions(after))
        self.assertFalse(after["selection_uses_quality_scores"])
        # Provenance changes when source rows change, even though policy does not.
        self.assertNotEqual(before["jobs"][0]["prior_row_sha256"],
                            after["jobs"][0]["prior_row_sha256"])

    def test_unknown_initial_action_retains_prefix_and_blocks_all_children(self):
        manifest, execution = fixture()
        rows = results(execution)
        rows["prefix"].update(eligible=False, reason="unknown_dispatch", lesson=None,
                              lesson_disposition="not_needed")
        for arm in ARMS:
            rows[arm]["disposition"] = "not_eligible:unknown_dispatch"
        unknown = admission("prefix", state="unknown")
        plan = select_jobs(manifest, execution, [unknown])
        self.assertEqual(plan["counts"], {"retain": 5})
        self.assertEqual(plan["unknown_admissions_preserved"], 1)
        self.assertEqual(plan["jobs"][0]["unknown_call_ids"], [unknown["call_id"]])
        self.assertTrue(all(decisions(plan)[arm][1] == "blocked_by_retained_ineligible_prefix"
                            for arm in ARMS))

    def test_unknown_writer_preserved_but_no_lesson_arms_resume(self):
        manifest, execution = fixture()
        rows = results(execution)
        rows["prefix"].update(lesson=None, lesson_disposition="unknown_dispatch")
        for arm in ("KL", "RL"):
            rows[arm]["disposition"] = "lesson_unavailable:unknown_dispatch"
        history = [admission("prefix"), admission("prefix", "unknown", "lesson")]
        plan = select_jobs(manifest, execution, history)
        decision = decisions(plan)
        self.assertEqual(decision["prefix"][0], "retain")
        for arm in ("K0", "R0"):
            self.assertEqual(decision[arm], ("resume", "healthy_interrupted_continuation"))
        for arm in ("KL", "RL"):
            self.assertEqual(decision[arm], ("retain", "blocked_by_retained_unavailable_lesson"))

    def test_never_admitted_writer_resumes_prefix_and_recomputes_all_children(self):
        manifest, execution = fixture()
        rows = results(execution)
        rows["prefix"].update(lesson=None, lesson_disposition="infrastructure_stop")
        for arm in ("KL", "RL"):
            rows[arm]["disposition"] = "lesson_unavailable:infrastructure_stop"
        plan = select_jobs(manifest, execution, [admission("prefix")])
        self.assertEqual(plan["counts"], {"resume": 5})
        self.assertTrue(all(decisions(plan)[arm][1] == "recompute_after_resumed_prefix"
                            for arm in ARMS))

    def test_unstarted_initial_prefix_resumes_without_replacing_jobs(self):
        manifest, execution = fixture()
        rows = results(execution)
        rows["prefix"].update(eligible=False, reason="unstarted_global_stop", lesson=None,
                              lesson_disposition="not_needed")
        for arm in ARMS:
            rows[arm]["disposition"] = "not_eligible:unstarted_global_stop"
        plan = select_jobs(manifest, execution, [])
        self.assertEqual(plan["counts"], {"resume": 5})
        self.assertEqual([row["job_id"] for row in plan["jobs"]],
                         [row["job_id"] for row in manifest["jobs"]])
        self.assertTrue(all(not row["historical_call_ids"] for row in plan["jobs"]))

    def test_unknown_arm_retained_while_healthy_partial_arms_resume(self):
        manifest, execution = fixture()
        rows = results(execution)
        rows["K0"].update(disposition="unknown_dispatch", attempts=[{"step": 1}])
        rows["R0"]["attempts"] = [{"step": 1, "public": {"status": "invalid_candidate"}}]
        history = [admission("prefix"), admission("prefix", stage="lesson"),
                   admission("K0"), admission("K0", "unknown", step=2), admission("R0")]
        plan = select_jobs(manifest, execution, history)
        self.assertEqual(decisions(plan)["K0"], ("retain", "preserved_unknown_admission"))
        self.assertTrue(all(decisions(plan)[arm][0] == "resume" for arm in ("R0", "KL", "RL")))
        owner = {row["arm"]: row for row in plan["jobs"]}["R0"]
        self.assertEqual(owner["historical_call_ids"], ["R0-action-1"])
        self.assertEqual(plan["historical_admissions"], len(history))

    def test_unknown_owner_is_retained_even_when_parent_will_resume(self):
        manifest, execution = fixture()
        rows = results(execution)
        rows["prefix"].update(lesson=None, lesson_disposition="infrastructure_stop")
        rows["K0"]["disposition"] = "unknown_dispatch"
        plan = select_jobs(manifest, execution,
                           [admission("prefix"), admission("K0", "unknown")])
        self.assertEqual(decisions(plan)["prefix"][0], "resume")
        self.assertEqual(decisions(plan)["K0"], ("retain", "preserved_unknown_admission"))

    def test_parent_resolution_does_not_depend_on_manifest_position(self):
        manifest, execution = fixture()
        manifest["jobs"] = manifest["jobs"][1:] + manifest["jobs"][:1]
        execution["jobs"] = execution["jobs"][1:] + execution["jobs"][:1]
        plan = select_jobs(manifest, execution, [])
        self.assertEqual([row["job_id"] for row in plan["jobs"]], ["K0", "R0", "KL", "RL", "prefix"])
        self.assertEqual(plan["counts"], {"resume": 4, "retain": 1})

    def test_fail_closed_on_inconsistent_inventory_or_undrained_history(self):
        for mutation in ("job_order", "duplicate_call", "outside_owner", "inflight",
                         "unknown_without_admission", "unsafe_error", "cross_task_parent"):
            with self.subTest(mutation=mutation):
                manifest, execution = fixture()
                history = [admission("prefix")]
                if mutation == "job_order":
                    execution["jobs"].reverse()
                elif mutation == "duplicate_call":
                    history.append(deepcopy(history[0]))
                elif mutation == "outside_owner":
                    history[0]["identity"]["task_id"] = "replacement-task"
                elif mutation == "inflight":
                    history[0]["state"] = "dispatched"
                elif mutation == "unknown_without_admission":
                    results(execution)["K0"]["disposition"] = "unknown_dispatch"
                elif mutation == "unsafe_error":
                    results(execution)["K0"]["disposition"] = "controller_error"
                elif mutation == "cross_task_parent":
                    manifest["jobs"][1]["task_id"] = "other-task"
                    execution["jobs"][1]["job"] = deepcopy(manifest["jobs"][1])
                with self.assertRaises(ValueError):
                    select_jobs(manifest, execution, history)


class RecoveryReceiptInvariants(unittest.TestCase):
    def test_preserves_known_unknown_responses_and_diagnostics_exactly(self):
        with TemporaryDirectory(dir=WORKSPACE, prefix=".recovery-invariant-") as temporary:
            prior, output = Path(temporary) / "prior", Path(temporary) / "new"
            known, unknown = admission("K0"), admission("R0", "unknown")
            payloads = {
                f"requests/{known['call_id']}.json": b'{ "sent" : true }\r\n',
                f"requests/{unknown['call_id']}.json": b'{"sent":null}\n',
                f"responses/{known['call_id']}.json": b'{"known":true}\r\n',
                f"responses/{unknown['call_id']}.json": b'{"partial":true}\n',
                f"diagnostics/{unknown['call_id']}.json": b'{"kind":"unknown"}\n',
                "execution.json": b'{"stopped":true}\n',
            }
            for name, content in payloads.items():
                path = prior / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            copied = copy_history(prior, output, [known, unknown])
            self.assertTrue(copied["receipt_bytes_preserved"])
            self.assertEqual(len(copied["files"]), len(payloads))
            for row in copied["files"]:
                self.assertEqual((output / row["path"]).read_bytes(), payloads[row["prior_path"]])
            with self.assertRaises(FileExistsError):
                copy_history(prior, output, [known, unknown])

    def test_no_missing_or_unadmitted_receipt_is_silently_accepted(self):
        for mutation in ("missing_request", "missing_known_response", "extra_request", "extra_diagnostic"):
            with self.subTest(mutation=mutation), TemporaryDirectory(
                    dir=WORKSPACE, prefix=".recovery-invariant-") as temporary:
                prior, output = Path(temporary) / "prior", Path(temporary) / "new"
                call = admission("K0")
                for directory in ("requests", "responses", "diagnostics"):
                    (prior / directory).mkdir(parents=True)
                if mutation != "missing_request":
                    (prior / "requests" / (call["call_id"] + ".json")).write_bytes(b'{}\n')
                if mutation != "missing_known_response":
                    (prior / "responses" / (call["call_id"] + ".json")).write_bytes(b'{}\n')
                if mutation in {"extra_request", "extra_diagnostic"}:
                    directory = "requests" if mutation == "extra_request" else "diagnostics"
                    (prior / directory / "unadmitted.json").write_bytes(b'{}\n')
                with self.assertRaises(ValueError):
                    copy_history(prior, output, [call])


if __name__ == "__main__":
    unittest.main()
