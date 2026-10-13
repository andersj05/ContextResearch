"""Scientific controller invariants with scripted transport and receipt fixtures.

No source string is executed, no Docker process is started, and no model is
contacted. Runtime receipts below are fixtures, not evidence of patch quality.
"""
from copy import deepcopy
import json
import unittest

from experiments.dependency_memory.rollback_patch_v9 import engine
from experiments.dependency_memory.rollback_patch_v9.common import ARMS, ATTEMPTS, wire
from experiments.dependency_memory.rollback_patch_v9.contexts import parse_lesson, render
from experiments.dependency_memory.rollback_patch_v9.tasks import generate, public_task
from experiments.dependency_memory.rollback_pilot.transport import Response
from experiments.dependency_memory.rollback_development_v5_continuation.accounting import CallUnknown


LESSON = {"focus": "state_invariants", "location": "engine.py",
          "diagnosis": "wrong_state_update", "next_check": "trace_failed_example",
          "confidence": "low"}
PRIVATE_CANARY = "private-receipt-must-never-reach-an-actor"


class ScriptedInvoke:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, identity, request):
        self.calls.append((identity, request.data()))
        if not self.responses:
            raise AssertionError("unexpected model request")
        result = self.responses.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result if isinstance(result, Response) else Response(result, None)


class ReceiptRuntime:
    """Hand-authored grading outcomes; deliberately offers extra private detail."""
    def __init__(self, statuses, terminal_scores=None):
        self.statuses = list(statuses)
        self.terminal_scores = (list(terminal_scores) if terminal_scores is not None
                                else [int(s == "public_pass") for s in statuses])
        self.calls = []
        self.index = -1

    def check(self, candidate, tests, *, public):
        self.calls.append({"candidate": deepcopy(candidate), "tests": deepcopy(tests),
                           "public": public})
        if public:
            self.index += 1
            if self.index >= len(self.statuses):
                raise AssertionError("unexpected public grade")
            status = self.statuses[self.index]
            return {"status": status, "score": int(status == "public_pass"),
                    "disposition": "correct" if status == "public_pass" else "test_failure",
                    "check_id": tests[0]["id"], "input": deepcopy(tests[0]["input"]),
                    "expected": deepcopy(tests[0]["expected"]), "observed": None}
        score = self.terminal_scores[self.index]
        return {"score": score, "disposition": "correct" if score else "test_failure",
                "private_details": PRIVATE_CANARY}


class PatchEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_task = generate(per_family=1)[0]

    def setUp(self):
        self.task = deepcopy(self.source_task)
        self.task["evaluator"]["private_canary"] = PRIVATE_CANARY

    def action(self, marker="changed", *, lines=4, cosmetic=False):
        files = deepcopy(self.task["base_files"])
        additions = [f"# cosmetic fixture {i}" if cosmetic else
                     f"fixture_{i} = {marker!r}" for i in range(lines)]
        files[0]["text"] += "\n" + "\n".join(additions) + "\n"
        return wire({"files": files, "note": "Scripted patch fixture; never executed."})

    def prefix(self, writer=None, *, terminal_score=0):
        invoke = ScriptedInvoke(self.action(), wire(LESSON) if writer is None else writer)
        runtime = ReceiptRuntime(["public_mismatch"], [terminal_score])
        result = engine.run_prefix(self.task, invoke, runtime)
        self.assertTrue(result["eligible"])
        return result, invoke, runtime

    @staticmethod
    def supplied(call):
        return json.loads(call[1]["messages"][1]["content"])

    def test_first_four_requests_vary_only_deletion_and_lesson_and_keep_source_facts(self):
        prefix, _, _ = self.prefix()
        original = deepcopy(prefix)
        normalized = []
        for arm in ARMS:
            request = render(self.task, arm=arm, prefix=prefix).data()
            state = json.loads(request["messages"][1]["content"])
            self.assertEqual(state["task"], public_task(self.task))
            self.assertEqual(state["task"]["contract"], self.task["contract"])
            self.assertEqual(state["task"]["public_tests"], self.task["public_tests"])
            self.assertEqual(state["checkpoint_files"], self.task["base_files"])
            self.assertEqual(state["feedback"], prefix["failed_record"]["public"])
            self.assertEqual(state["remaining_attempts"], ATTEMPTS)
            self.assertEqual(state["continuation_records"], [])
            self.assertEqual(state["failed_work"], prefix["failed_record"]["visible_work"]
                             if arm.startswith("K") else None)
            self.assertEqual(state["lesson"], LESSON if arm.endswith("L") else None)
            self.assertNotIn(PRIVATE_CANARY, wire(request))
            state["failed_work"] = state["lesson"] = None
            request["messages"][1]["content"] = wire(state)
            normalized.append(wire(request))
        self.assertEqual(len(set(normalized)), 1)
        self.assertEqual(prefix, original)
        self.assertTrue(engine.factorial_contract(self.task, prefix)["passed"])

    def test_factorial_contract_checks_task_and_diff_against_authoritative_source(self):
        prefix, _, _ = self.prefix()
        altered_task = deepcopy(self.task)
        altered_task["contract"]["must_preserve"] = "a new requirement"
        with self.assertRaisesRegex(engine.ContractError, "eligible_task_identity"):
            engine.factorial_contract(altered_task, prefix)
        altered_prefix = deepcopy(prefix)
        altered_prefix["failed_record"]["visible_work"]["patch"] += " fabricated patch"
        with self.assertRaisesRegex(engine.ContractError, "diff_matches_submitted_files"):
            engine.factorial_contract(self.task, altered_prefix)

    def test_unterminated_diff_lines_remain_separate_and_mark_the_missing_newline(self):
        for before, after, markers in (("x = 1", "x = 2", 2),
                                       ("x = 1\n", "x = 2", 1),
                                       ("x = 1", "x = 2\n", 1)):
            with self.subTest(before=before, after=after):
                result = engine.patch([{"path": "engine.py", "text": before}],
                                      [{"path": "engine.py", "text": after}])
                lines = result["diff"].splitlines()
                self.assertIn("-x = 1", lines)
                self.assertIn("+x = 2", lines)
                self.assertEqual(lines.count("\\ No newline at end of file"), markers)
                self.assertEqual(result["changed_nonempty_lines"], 2)
                self.assertNotIn("-x = 1+x = 2", result["diff"])

    def test_initial_public_failure_feedback_survives_later_feedback_in_every_arm(self):
        prefix, _, _ = self.prefix()
        initial = deepcopy(prefix["failed_record"]["public"])
        later = {"status": "public_mismatch", "score": 0,
                 "check_id": "different_public_case", "observed": "later output"}
        records = [{"step": 1, "public": later,
                    "work": {"patch": "later visible patch", "note": "later repair"}}]
        for arm in ARMS:
            with self.subTest(arm=arm):
                request = render(self.task, arm=arm, prefix=prefix, records=records).data()
                state = json.loads(request["messages"][1]["content"])
                self.assertEqual(state["initial_feedback"], initial)
                self.assertEqual(state["feedback"], later)
                self.assertEqual(state["continuation_records"], records)
                self.assertEqual(state["task"], public_task(self.task))
                self.assertNotEqual(state["initial_feedback"], state["feedback"])
                self.assertNotIn(PRIVATE_CANARY, wire(request))
        self.assertEqual(prefix["failed_record"]["public"], initial)

    def test_natural_executable_mismatch_and_substantive_ast_change_are_required(self):
        for lines, cosmetic in ((1, False), (4, True)):
            with self.subTest(lines=lines, cosmetic=cosmetic):
                invoke = ScriptedInvoke(self.action(lines=lines, cosmetic=cosmetic))
                result = engine.run_prefix(self.task, invoke, ReceiptRuntime(["public_mismatch"]))
                self.assertFalse(result["eligible"])
                self.assertEqual(result["reason"], "insubstantial_patch")
                self.assertEqual(len(invoke.calls), 1)
        prefix, invoke, _ = self.prefix()
        self.assertEqual(prefix["failed_record"]["changed_nonempty_lines"], 4)
        self.assertEqual(prefix["reason"], "natural_substantive_patch_mismatch")
        self.assertEqual(len(invoke.calls), 2)

    def test_standalone_strings_and_comments_do_not_count_as_structural_work(self):
        files = deepcopy(self.task["base_files"])
        files[0]["text"] += '\n"one"\n"two"\n# three\n"four"\n'
        self.assertGreaterEqual(engine.patch(self.task["base_files"], files)["changed_nonempty_lines"], 4)
        self.assertFalse(engine.structure_changed(self.task["base_files"], files))
        files[0]["text"] += "\nthis is invalid Python !!!\n"
        self.assertFalse(engine.structure_changed(self.task["base_files"], files))

    def test_public_pass_or_execution_failure_does_not_create_a_fork(self):
        for status in ("public_pass", "syntax_error", "runtime_error", "timeout", "invalid_output"):
            with self.subTest(status=status):
                invoke = ScriptedInvoke(self.action())
                result = engine.run_prefix(self.task, invoke, ReceiptRuntime([status], [0]))
                self.assertFalse(result["eligible"])
                self.assertEqual(result["reason"], status)
                self.assertEqual(len(invoke.calls), 1)
                continuation = engine.run_continuation(self.task, "R0", result, ScriptedInvoke(), ReceiptRuntime([]))
                self.assertIsNone(continuation["score"])
                self.assertEqual(continuation["disposition"], "not_eligible:" + status)

    def test_hidden_outcome_does_not_change_prefix_eligibility_or_writer_input(self):
        zero, zero_invoke, _ = self.prefix(terminal_score=0)
        one, one_invoke, _ = self.prefix(terminal_score=1)
        self.assertEqual(zero["eligible"], one["eligible"])
        self.assertEqual(zero["reason"], one["reason"])
        self.assertEqual(zero_invoke.calls[1][1], one_invoke.calls[1][1])
        self.assertNotIn(PRIVATE_CANARY, wire(zero_invoke.calls[1][1]))
        self.assertEqual(set(zero["failed_record"]["terminal"]), {"score", "disposition"})

    def test_three_repair_attempts_permit_delayed_recovery_and_keep_each_public_fact(self):
        prefix, _, _ = self.prefix()
        invoke = ScriptedInvoke(self.action("first"), self.action("second"), self.action("third"))
        runtime = ReceiptRuntime(["public_mismatch", "public_mismatch", "public_pass"])
        result = engine.run_continuation(self.task, "R0", prefix, invoke, runtime)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["first_pass"], 3)
        self.assertEqual(len(result["attempts"]), 3)
        for index, call in enumerate(invoke.calls):
            state = self.supplied(call)
            self.assertEqual(state["task"], public_task(self.task))
            self.assertEqual(state["checkpoint_files"], self.task["base_files"])
            self.assertEqual(state["remaining_attempts"], 3 - index)
            self.assertEqual(len(state["continuation_records"]), index)
            self.assertIsNone(state["failed_work"])
            self.assertIsNone(state["lesson"])
            self.assertNotIn(PRIVATE_CANARY, wire(call[1]))
            for record in state["continuation_records"]:
                self.assertEqual(set(record), {"step", "public", "work"})
                self.assertNotIn("terminal", record)
        self.assertEqual(self.supplied(invoke.calls[2])["feedback"], result["attempts"][1]["public"])
        self.assertTrue(any("second" in row["work"]["patch"]
                            for row in self.supplied(invoke.calls[2])["continuation_records"]))

    def test_public_acceptance_stops_even_when_hidden_tests_fail(self):
        prefix, _, _ = self.prefix()
        invoke = ScriptedInvoke(self.action())
        runtime = ReceiptRuntime(["public_pass"], [0])
        result = engine.run_continuation(self.task, "KL", prefix, invoke, runtime)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["disposition"], "test_failure")
        self.assertEqual(result["first_pass"], 1)
        self.assertEqual(len(invoke.calls), 1)

    def test_three_public_failures_exhaust_the_budget_and_do_not_use_private_feedback(self):
        prefix, _, _ = self.prefix()
        invoke = ScriptedInvoke(*(self.action(str(index)) for index in range(3)))
        result = engine.run_continuation(self.task, "R0", prefix, invoke,
                                         ReceiptRuntime(["public_mismatch"] * 3, [1] * 3))
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["disposition"], "repair_budget_exhausted")
        self.assertIsNone(result["first_pass"])
        self.assertEqual(len(invoke.calls), ATTEMPTS)

    def test_malformed_and_capped_received_actions_each_consume_one_attempt(self):
        prefix, _, _ = self.prefix()
        invoke = ScriptedInvoke("not json", Response(self.action("capped"), None, capped=True),
                                self.action("repair"))
        runtime = ReceiptRuntime(["public_pass"])
        result = engine.run_continuation(self.task, "K0", prefix, invoke, runtime)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["first_pass"], 3)
        self.assertEqual([record["public"]["status"] for record in result["attempts"]],
                         ["invalid_candidate", "invalid_candidate", "public_pass"])
        self.assertEqual(len(runtime.calls), 2)
        self.assertEqual(self.supplied(invoke.calls[2])["remaining_attempts"], 1)

    def test_unknown_writer_leaves_only_lesson_arms_missing(self):
        prefix, _, _ = self.prefix(CallUnknown("writer unavailable"))
        self.assertIsNone(prefix["lesson"])
        self.assertEqual(prefix["lesson_disposition"], "unknown_dispatch")
        for arm in ARMS:
            with self.subTest(arm=arm):
                invoke = ScriptedInvoke() if arm.endswith("L") else ScriptedInvoke(self.action())
                result = engine.run_continuation(self.task, arm, prefix, invoke, ReceiptRuntime(["public_pass"]))
                if arm.endswith("L"):
                    self.assertIsNone(result["score"])
                    self.assertEqual(result["disposition"], "lesson_unavailable:unknown_dispatch")
                    self.assertEqual(invoke.calls, [])
                else:
                    self.assertEqual(result["score"], 1)
                    self.assertEqual(len(invoke.calls), 1)

    def test_invalid_lesson_cannot_reinsert_patch_content(self):
        for invalid in ({**LESSON, "patch": "full failed source"},
                        {**LESSON, "diagnosis": "arbitrary prose or source"}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    parse_lesson(wire(invalid))
                prefix, _, _ = self.prefix(wire(invalid))
                self.assertIsNone(prefix["lesson"])
                self.assertEqual(prefix["lesson_disposition"], "invalid_lesson")

    def test_unknown_prefix_has_unknown_outcome_and_no_known_eligibility(self):
        invoke = ScriptedInvoke(CallUnknown("unknown first attempt"))
        result = engine.run_prefix(self.task, invoke, ReceiptRuntime([]))
        self.assertFalse(result["eligible"])
        self.assertEqual(result["reason"], "unknown_dispatch")
        self.assertIsNone(result["outcome"]["score"])
        self.assertEqual(result["attempts"], [])

    def test_unknown_arm_remains_missing_instead_of_becoming_budget_failure(self):
        prefix, _, _ = self.prefix()
        invoke = ScriptedInvoke(self.action(), CallUnknown("unknown second repair"))
        result = engine.run_continuation(self.task, "R0", prefix, invoke, ReceiptRuntime(["public_mismatch"]))
        self.assertIsNone(result["score"])
        self.assertEqual(result["disposition"], "unknown_dispatch")
        self.assertEqual(len(result["attempts"]), 1)
        self.assertEqual(len(invoke.calls), 2)


if __name__ == "__main__":
    unittest.main()
