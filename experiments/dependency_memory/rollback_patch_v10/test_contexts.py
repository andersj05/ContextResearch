"""Compound-project information boundary tests; zero model or runtime calls.

The reference-file diffs here are constructed serialization fixtures. Their
invented mismatch receipts are not observations or patch-quality evidence.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
import unittest

from experiments.dependency_memory.rollback_patch_v10 import engine
from experiments.dependency_memory.rollback_patch_v10.common import (
    ARMS, ATTEMPTS, MAX_BODY_BYTES, MAX_INPUT_TEXT_BYTES, sha, wire,
)
from experiments.dependency_memory.rollback_patch_v10.contexts import Request, fits, parse_action, render
from experiments.dependency_memory.rollback_patch_v10.tasks import DEFAULT_SEED, generate


LESSON = {"focus": "state_invariants", "location": "both",
          "diagnosis": "wrong_state_update", "next_check": "check_all_constraints",
          "confidence": "low"}
PRIVATE_CANARY = "v10-evaluator-only-information-boundary-canary"


@lru_cache(maxsize=1)
def capacity_report():
    """Check both fixed cohorts using actual and conservative maximal records."""
    engine_text = "def solve(case):\n    return None\n"
    files = [{"path": "engine.py", "text": engine_text},
             {"path": "rules.py", "text": "#" + chr(1) * (32768 - len(engine_text) - 2) + "\n"}]
    action = parse_action(wire({"files": files, "note": "\\" * 240}))
    source_bytes = sum(len(row["text"].encode("utf-8")) for row in action["files"])
    # A parsed string of backslashes expands strongly in subsequent JSON
    # envelopes. Its original complete public-suite output remains <=64 KiB.
    envelope = {"format": "rollback-patch-v10-batch-result-v1", "status": "completed",
                "outputs": [None] * 6, "detail": ""}
    low, high = 0, 65536
    while low < high:
        middle = (low + high + 1) // 2
        envelope["outputs"][0] = "\\" * middle
        if len(wire(envelope).encode("utf-8")) <= 65536:
            low = middle
        else:
            high = middle - 1
    envelope["outputs"][0] = "\\" * low
    stdout_bytes = len(wire(envelope).encode("utf-8"))
    rows = []
    for split, seed, count in (("calibration", DEFAULT_SEED, 4), ("study", DEFAULT_SEED + 1, 64)):
        for task in generate(split=split, seed=seed, per_family=count):
            example = max(task["public_tests"], key=lambda row: len(wire(row)))
            ordinary = {"status": "public_mismatch", "score": 0, "disposition": "test_failure",
                        "test_count": 6, "passed_count": 0, "check_id": example["id"],
                        "input": deepcopy(example["input"]), "expected": deepcopy(example["expected"]),
                        "observed": None, "detail": "Public JSON output mismatch.",
                        "tests": [{"id": row["id"], "status": "public_mismatch"} for row in task["public_tests"]]}
            maximal = {**ordinary, "observed": envelope["outputs"][0]}
            values = {}
            for label, proposed, receipt, note in (
                    ("reference", task["evaluator"]["reference_files"], ordinary, "Serialization fixture."),
                    ("maximum", action["files"], maximal, action["note"])):
                delta = engine.patch(task["base_files"], proposed)
                work = {"patch": delta["diff"], "note": note}
                prefix = {"eligible": True, "task_sha256": sha(task),
                          "failed_record": {"public": receipt, "candidate": {"files": proposed},
                                            "visible_work": work,
                                            "changed_nonempty_lines": delta["changed_nonempty_lines"]},
                          "lesson": deepcopy(LESSON)}
                records = [{"step": step, "public": deepcopy(receipt), "work": deepcopy(work)} for step in (1, 2)]
                # KL is largest: its two optional fields are both present.
                third = render(task, arm="KL", prefix=prefix, records=records)
                writer = render(task, prefix=prefix, kind="lesson")
                values[label + "_third_repair_bytes"] = third.input_units
                values[label + "_writer_bytes"] = writer.input_units
                values[label + "_third_repair_text_bytes"] = len(third.json_text.encode("utf-8"))
                values[label + "_writer_text_bytes"] = len(writer.json_text.encode("utf-8"))
                values[label + "_third_repair_fits"] = fits(third)
                values[label + "_writer_fits"] = fits(writer)
                if label == "reference" and (not fits(third) or not fits(writer)):
                    raise AssertionError((task["task_id"], label, third.input_units, writer.input_units))
                if label == "maximum" and (fits(third) or not fits(writer)):
                    raise AssertionError((task["task_id"], label, "stress boundary not detected"))
            rows.append({"task_id": task["task_id"], "split": split, "family": task["family"], **values})
    fields = ("reference_third_repair_bytes", "reference_writer_bytes",
              "maximum_third_repair_bytes", "maximum_writer_bytes",
              "reference_third_repair_text_bytes", "reference_writer_text_bytes",
              "maximum_third_repair_text_bytes", "maximum_writer_text_bytes")
    return {"evidence_kind": "offline_serialization_capacity_check", "model_calls": 0,
            "candidate_code_executed_on_host": False, "declared_body_bound_bytes": MAX_BODY_BYTES,
            "declared_input_text_bound_utf8_bytes": MAX_INPUT_TEXT_BYTES,
            "tasks_checked": len(rows), "maximum_candidate_utf8_bytes": source_bytes,
            "maximum_fixture_original_stdout_bytes": stdout_bytes,
            "maxima": {key: max(row[key] for row in rows) for key in fields},
            "expected_stress_rejections": sum(not row["maximum_third_repair_fits"] for row in rows),
            "scope": "All 16 calibration and 256 study tasks; third-repair KL includes initial failed patch, two later patches, initial/latest feedback and complete public facts. Other arms omit optional fields. Reference-sized requests fit both bounds. A 32 KiB source with JSON-expanding valid-Python comment and a parsed receipt derived from <=64 KiB output are conservative serialization fixtures, not observed model work. Maximal third-repair fixtures exceed the input-text limit and are correctly rejected without trimming facts; passing this check does not establish that every permitted repair history can be admitted.",
            "passed": True, "tasks": rows}


class CompoundContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = generate(per_family=1)

    def fixture(self, source_task):
        task = deepcopy(source_task)
        task["evaluator"]["private_canary"] = PRIVATE_CANARY
        files = deepcopy(task["evaluator"]["reference_files"])
        delta = engine.patch(task["base_files"], files)
        example = task["public_tests"][0]
        public = {"status": "public_mismatch", "score": 0, "disposition": "test_failure",
                  "check_id": example["id"], "input": deepcopy(example["input"]),
                  "expected": deepcopy(example["expected"]), "observed": None,
                  "detail": "Invented serialization receipt; no source executed."}
        failed = {"step": 1, "public": public, "terminal": {"score": 0, "private": PRIVATE_CANARY},
                  "candidate": {"files": files},
                  "visible_work": {"patch": delta["diff"], "note": "Constructed context fixture."},
                  "changed_nonempty_lines": delta["changed_nonempty_lines"]}
        prefix = {"task_id": task["task_id"], "task_sha256": sha(task), "eligible": True,
                  "failed_record": failed, "lesson": deepcopy(LESSON), "lesson_disposition": "valid"}
        return task, prefix

    @staticmethod
    def state(request):
        return json.loads(request.data()["messages"][1]["content"])

    @staticmethod
    def authoritative_public(task):
        return {key: deepcopy(task[key]) for key in
                ("task_id", "family", "contract", "base_files", "public_tests")}

    def test_engine_implementation_is_exactly_the_verified_v9_dependency(self):
        here = Path(__file__).resolve().parent
        self.assertEqual((here / "engine.py").read_bytes(),
                         (here.parent / "rollback_patch_v9" / "engine.py").read_bytes())

    def test_all_compound_public_facts_and_original_files_are_in_every_request(self):
        for source in self.tasks:
            task, prefix = self.fixture(source)
            original = deepcopy(prefix)
            for arm in ARMS:
                with self.subTest(family=task["family"], arm=arm):
                    state = self.state(render(task, arm=arm, prefix=prefix))
                    self.assertEqual(state["task"], self.authoritative_public(task))
                    self.assertEqual(len(state["task"]["contract"]["component_contracts"]), 8)
                    self.assertEqual(state["task"]["contract"]["component_contracts"],
                                     task["contract"]["component_contracts"])
                    self.assertEqual(state["checkpoint_files"], task["base_files"])
                    self.assertEqual(state["initial_feedback"], prefix["failed_record"]["public"])
                    self.assertEqual(state["feedback"], prefix["failed_record"]["public"])
                    self.assertEqual(state["remaining_attempts"], ATTEMPTS)
                    self.assertEqual(state["continuation_records"], [])
            self.assertEqual(prefix, original)

    def test_only_failed_work_and_lesson_change_between_the_four_arm_payloads(self):
        for source in self.tasks:
            task, prefix = self.fixture(source)
            normalized = []
            for arm in ARMS:
                request = render(task, arm=arm, prefix=prefix).data()
                state = json.loads(request["messages"][1]["content"])
                self.assertEqual(state["failed_work"], prefix["failed_record"]["visible_work"]
                                 if arm.startswith("K") else None)
                self.assertEqual(state["lesson"], LESSON if arm.endswith("L") else None)
                state["failed_work"] = state["lesson"] = None
                request["messages"][1]["content"] = wire(state)
                normalized.append(wire(request))
            self.assertEqual(len(set(normalized)), 1)
            self.assertTrue(engine.factorial_contract(task, prefix)["passed"])

    def test_private_task_and_private_grade_details_never_enter_actor_or_writer_context(self):
        for source in self.tasks:
            task, prefix = self.fixture(source)
            requests = [render(task), render(task, prefix=prefix, kind="lesson")]
            requests.extend(render(task, arm=arm, prefix=prefix) for arm in ARMS)
            for request in requests:
                state = self.state(request)
                self.assertNotIn(PRIVATE_CANARY, request.json_text)
                self.assertNotIn("evaluator", state["task"])
                self.assertNotIn("terminal", state)
                self.assertEqual(state["task"], self.authoritative_public(task))

    def test_initial_feedback_and_all_compound_facts_survive_later_continuations(self):
        for source in self.tasks:
            task, prefix = self.fixture(source)
            latest = {"status": "public_mismatch", "score": 0, "check_id": "later-public-check"}
            records = [{"step": step, "public": deepcopy(latest),
                        "work": deepcopy(prefix["failed_record"]["visible_work"])} for step in (1, 2)]
            for arm in ARMS:
                request = render(task, arm=arm, prefix=prefix, records=records)
                state = self.state(request)
                self.assertEqual(state["task"], self.authoritative_public(task))
                self.assertEqual(state["checkpoint_files"], task["base_files"])
                self.assertEqual(state["initial_feedback"], prefix["failed_record"]["public"])
                self.assertEqual(state["feedback"], latest)
                self.assertEqual(state["remaining_attempts"], 1)
                self.assertEqual(state["continuation_records"], records)
                self.assertNotIn(PRIVATE_CANARY, request.json_text)

    def test_reference_sized_third_repair_contexts_fit_without_dropping_facts(self):
        for source in self.tasks:
            task, prefix = self.fixture(source)
            records = [{"step": step, "public": deepcopy(prefix["failed_record"]["public"]),
                        "work": deepcopy(prefix["failed_record"]["visible_work"])} for step in (1, 2)]
            for arm in ARMS:
                request = render(task, arm=arm, prefix=prefix, records=records)
                self.assertTrue(fits(request), (task["task_id"], arm, request.input_units))
                self.assertEqual(self.state(request)["task"], self.authoritative_public(task))

    def test_full_cohort_normal_requests_fit_and_maximal_histories_are_rejected(self):
        report = capacity_report()
        self.assertEqual(report["tasks_checked"], 272)
        self.assertEqual(report["maximum_candidate_utf8_bytes"], 32768)
        self.assertLessEqual(report["maximum_fixture_original_stdout_bytes"], 65536)
        self.assertGreater(report["maximum_fixture_original_stdout_bytes"], 65530)
        self.assertTrue(report["passed"])
        self.assertEqual(report["expected_stress_rejections"], 272)
        for key, value in report["maxima"].items():
            if "_text_bytes" not in key:
                self.assertLess(value, MAX_BODY_BYTES)
        self.assertLess(report["maxima"]["reference_third_repair_text_bytes"], MAX_INPUT_TEXT_BYTES)
        self.assertGreater(report["maxima"]["maximum_third_repair_text_bytes"], MAX_INPUT_TEXT_BYTES)

    def test_input_text_guard_enforces_exact_utf8_boundary_independent_of_body_limit(self):
        request = render(self.tasks[0])
        payload = request.data()
        payload["messages"][1]["content"] = ""
        fixed_bytes = len(wire(payload).encode("utf-8"))
        for excess, expected in ((0, True), (1, False)):
            payload["messages"][1]["content"] = "x" * (MAX_INPUT_TEXT_BYTES - fixed_bytes + excess)
            candidate = Request("action", wire(payload), 0, "offline-boundary-fixture")
            self.assertEqual(len(candidate.json_text.encode("utf-8")), MAX_INPUT_TEXT_BYTES + excess)
            self.assertEqual(fits(candidate), expected)
        payload["messages"][1]["content"] = "é" * ((MAX_INPUT_TEXT_BYTES - fixed_bytes) // 2 + 1)
        candidate = Request("action", wire(payload), 0, "offline-unicode-boundary-fixture")
        self.assertLess(len(candidate.json_text), MAX_INPUT_TEXT_BYTES)
        self.assertGreater(len(candidate.json_text.encode("utf-8")), MAX_INPUT_TEXT_BYTES)
        self.assertFalse(fits(candidate))


if __name__ == "__main__":
    unittest.main()
