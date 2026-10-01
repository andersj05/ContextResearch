"""Independent public-rule execution and adversarial information-channel checks."""
from copy import deepcopy
import itertools
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from experiments.dependency_memory.evidence_use import guard
from experiments.dependency_memory.workflow_eval import grader
from experiments.dependency_memory.cross_record import run as cross_run
from experiments.dependency_memory.schema_transfer import casebook


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def receipt(check="tests", code=0, run="b", snapshot="a"):
    return {"check": check, "snapshot": snapshot * 64, "run_id": run * 64,
            "returncode": code, "artifacts": {p: "c" * 64 for p in guard.ARTIFACTS} if check == "paper" and code == 0 else {}}


def task(required=("tests",), snapshot="a"):
    return {"snapshot": snapshot * 64, "required_checks": sorted(required), "artifacts": {p: "c" * 64 for p in guard.ARTIFACTS}}


def request(records, public=None):
    return {"stage": "execute", "instruction": guard.RECEIPT_RULE + "\nFinal reporting instruction",
            "observation": {"memory": wire(records), "final_public_state": public or task()}}


def table(family, row):
    fields = list(guard.FIELDS[family])
    values = []
    for path in fields:
        cursor = row
        for name in path.split("."):
            cursor = cursor[name]
        values.append(cursor)
    return wire({"f": fields, "r": [values]})


class ReceiptExecutionTests(unittest.TestCase):
    def test_independent_grader_on_scope_revision_and_artifacts(self):
        base = [receipt("tests", run="1"), receipt("repository", run="2"), receipt("paper", run="3")]
        ledgers = [[], base, base + [receipt("tests", 1, "4")], base + [receipt("tests", 1, "4"), receipt("tests", 0, "5")],
                   base + [receipt("tests", 0, "6", "d")]]
        comparisons = 0
        for records in ledgers:
            for size in range(1, 4):
                for required in itertools.combinations(guard.CHECKS, size):
                    for snapshot, inventory in itertools.product(("a", "d"), ("original", "replaced", "missing")):
                        public = task(required, snapshot)
                        if inventory == "replaced":
                            public["artifacts"][guard.ARTIFACTS[1]] = "e" * 64
                        elif inventory == "missing":
                            public["artifacts"].pop(guard.ARTIFACTS[1])
                        self.assertEqual(guard.derive(request(records, public)), grader.expected_answer(records, public))
                        comparisons += 1
        self.assertEqual(comparisons, 210)

    def test_omission_is_indistinguishable_to_actor(self):
        success = receipt()
        failure = receipt(code=1, run="d")
        actor = request([success])
        proposal = grader.expected_answer([success], task())
        self.assertNotEqual(proposal, grader.expected_answer([success, failure], task()))
        verdict = guard.check(actor, proposal)
        self.assertEqual(verdict["status"], "consistent")
        self.assertFalse(verdict["source_complete_certified"])
        # The same actor input and output apply in both possible source histories.
        self.assertEqual(verdict, guard.check(deepcopy(actor), proposal))

    def test_correct_proposal_can_be_vetoed_by_lossy_memory(self):
        success, failure = receipt(), receipt(code=1, run="d")
        correct = grader.expected_answer([success, failure], task())
        self.assertEqual(guard.check(request([success]), correct)["status"], "contradicted")

    def test_prose_can_be_correct_but_uncheckable(self):
        actor = request([receipt()])
        actor["observation"]["memory"] = "The tests passed on snapshot " + "a" * 64 + "; run " + "b" * 64
        self.assertEqual(guard.check(actor, grader.expected_answer([receipt()], task()))["status"], "uncheckable")

    def test_forged_well_formed_receipt_is_not_authenticated(self):
        forged = receipt(run="f")
        verdict = guard.check(request([forged]), grader.expected_answer([forged], task()))
        self.assertEqual(verdict["status"], "consistent")
        self.assertFalse(verdict["source_complete_certified"])

    def test_duplicate_keys_nonfinite_and_bool_returncode(self):
        actor = request([receipt()])
        invalid_memories = ['[{"check":"tests","check":"paper"}]', '[NaN]', '[1e400]',
                            wire([{**receipt(), "returncode": False}]), wire([receipt(), receipt()])]
        for memory in invalid_memories:
            with self.subTest(memory=memory):
                actor["observation"]["memory"] = memory
                self.assertEqual(guard.check(actor, {})["status"], "uncheckable")

    def test_boolean_answer_cannot_be_integer(self):
        proposal = grader.expected_answer([receipt()], task())
        proposal["ready"] = 1
        result = guard.check(request([receipt()]), proposal)
        self.assertEqual(result["status"], "contradicted")
        self.assertIn("ready", result["changed_fields"])

    def test_extra_proposal_fields_and_malformed_proposal(self):
        actor = request([receipt()])
        correct = guard.derive(actor)
        self.assertEqual(guard.check(actor, {**correct, "extra": 1})["status"], "contradicted")
        self.assertEqual(guard.check(actor, '{"ready":true,"ready":false}')["status"], "contradicted")

    def test_no_filesystem_or_grader_access(self):
        actor = request([receipt()])
        correct = guard.derive(actor)
        with patch("builtins.open", side_effect=AssertionError("actor attempted file access")), patch.object(grader, "expected_answer", side_effect=AssertionError("actor used evaluator")):
            self.assertEqual(guard.check(actor, correct)["status"], "consistent")


class CrossRecordExecutionTests(unittest.TestCase):
    def test_public_rule_copy_matches_historical_instructions(self):
        for family in guard.PUBLIC_RULES:
            self.assertEqual(guard.PUBLIC_RULES[family], casebook.RULES[family])

    def test_every_fixture_row_and_late_event_against_independent_executor(self):
        count = 0
        for path in cross_run.fixture_paths()[0]:
            case = json.loads(path.read_text())
            for row in case["private_truth_rows"].values():
                for future in case["futures"]:
                    target = row[guard.OWNERS[case["family"]]]
                    answer = guard.cross_answer(table(case["family"], row), target, future["event"], case["family"])
                    self.assertEqual(answer, casebook.terminal(case["family"], row, future["event"]))
                    count += 1
        self.assertEqual(count, 252)

    def test_raw_tool_joins_match_independent_truth(self):
        for path in cross_run.fixture_paths()[0]:
            case = json.loads(path.read_text())
            for future in case["futures"]:
                actor = cross_run.execution_request(case, wire(case["tool_results"]), future)
                expected = casebook.terminal(case["family"], case["private_truth_rows"][future["target"]], future["event"])
                self.assertEqual(guard.derive(actor), expected)

    def test_predicate_sweeps_against_independent_executor(self):
        comparisons = 0
        for family, conditions in (
            ("ci_promotion", ("build.channel", "authorization.state", "authorization.approved_digest", "verification.subject", "verification.unit", "verification.integration", "handoff.environment")),
            ("data_pipeline", ("extract.state", "transform.state", "load.state", "quality.state", "transform.input_dataset", "load.input_dataset", "quality.subject_dataset", "consent.state", "consent.approved_output")),
        ):
            for bits in itertools.product((False, True), repeat=len(conditions)):
                row = casebook._row(family, 61011, 0)
                for failed, path in zip(bits, conditions):
                    if failed:
                        component, leaf = path.split(".")
                        row[component][leaf] = "mismatch"
                event = {"path": "note", "value": "irrelevant"}
                expected = casebook.terminal(family, row, event)
                self.assertEqual(guard.cross_answer(table(family, row), row[guard.OWNERS[family]], event, family), expected)
                comparisons += 1
        for dispatch, result, billing, allowed, rscope, bscope in itertools.product(("sent", "not_sent"), ("passed", "failed", "pending"), ("settled", "pending"), (False, True), (False, True), (False, True)):
            row = casebook._row("retry_queue", 61011, 0)
            row["dispatch"]["state"], row["result"]["state"], row["billing"]["state"] = dispatch, result, billing
            row["retry_policy"]["retry_allowed"] = allowed
            if rscope:
                row["result"]["attempt_uuid"] = "wrong"
            if bscope:
                row["billing"]["for_attempt"] = "wrong"
            event = {"path": "note", "value": "irrelevant"}
            self.assertEqual(guard.cross_answer(table("retry_queue", row), row["request_token"], event, "retry_queue"), casebook.terminal("retry_queue", row, event))
            comparisons += 1
        self.assertEqual(comparisons, 736)

    def test_duplicate_paths_overlapping_paths_and_owners_abstain(self):
        family = "ci_promotion"
        row = casebook._row(family, 61011, 0)
        memory = json.loads(table(family, row))
        variants = [deepcopy(memory), deepcopy(memory), deepcopy(memory)]
        variants[0]["f"].append(memory["f"][0]); variants[0]["r"][0].append(memory["r"][0][0])
        variants[1]["f"].append("build"); variants[1]["r"][0].append("scalar")
        variants[2]["r"].append(memory["r"][0])
        for variant in variants:
            with self.assertRaises(ValueError):
                guard.cross_answer(wire(variant), row["deployment_slot"], {"path": "note", "value": "x"}, family)

    def test_missing_state_and_wrong_boolean_type_abstain(self):
        row = casebook._row("retry_queue", 61011, 0)
        memory = json.loads(table("retry_queue", row))
        offset = memory["f"].index("retry_policy.retry_allowed")
        memory["r"][0][offset] = "true"
        with self.assertRaises(ValueError):
            guard.cross_answer(wire(memory), row["request_token"], {"path": "note", "value": "x"}, "retry_queue")
        memory["f"].pop(offset); memory["r"][0].pop(offset)
        with self.assertRaises(ValueError):
            guard.cross_answer(wire(memory), row["request_token"], {"path": "note", "value": "x"}, "retry_queue")

    def test_late_event_changes_scope_before_action(self):
        row = casebook._row("data_pipeline", 61011, 0)
        event = {"path": "load.output_dataset", "value": "new-exact-id"}
        answer = guard.cross_answer(table("data_pipeline", row), row["pipeline_run"], event, "data_pipeline")
        self.assertEqual(answer, {"action": "hold", "target_id": "new-exact-id", "work": ["approval_scope", "quality_scope"]})

    def test_unknown_rule_and_extra_actor_truth_abstain(self):
        actor = request([receipt()])
        actor["instruction"] = "Different reporting rule"
        self.assertEqual(guard.check(actor, {})["status"], "uncheckable")
        actor = request([receipt()])
        actor["observation"]["evaluator_truth"] = {"ready": True}
        self.assertEqual(guard.check(actor, {})["status"], "uncheckable")


if __name__ == "__main__":
    unittest.main()
