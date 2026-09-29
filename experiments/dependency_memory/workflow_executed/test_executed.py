"""Independent execution/chronology, scope-channel and ledger invariants."""
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from . import study
from .capture import CAPTURE, validate_capture
from .run import execute, prepare
from .analyze import analyze
from .transport import save, usage_cost
from experiments.dependency_memory.workflow_eval.grader import expected_answer, wire
from experiments.dependency_memory.workflow_eval.packet import direct_records
from experiments.dependency_memory.workflow_eval_live.protocol import request_bytes

EXPECTED_WORK = {
    "unchanged": [], "tests_later_failure": ["tests"], "tests_recovery": [],
    "repository_later_failure": ["repository"], "repository_recovery": [],
    "artifact_replaced": ["paper"], "artifact_missing": ["paper"],
    "new_source_unchecked": ["tests"], "partial_revision": ["repository"],
    "older_source_selected": [], "irrelevant_failure": [], "fail_recover_fail": ["tests"],
}


class Fake:
    def __init__(self):
        self.requests = []

    def complete(self, identity, request):
        self.requests.append((identity, request))
        observation = request["observation"]
        if request["stage"] == "parent":
            source, scope = observation["tool_observations"], study.CHECKS
        elif request["stage"] == "child":
            source = json.loads(observation["previous_memory"] or "[]") + observation["new_observations"]
            scope = observation["scope"]
        else:
            answer = expected_answer(json.loads(observation["memory"] or "[]"), observation["final_public_state"])
            answer["evidence"] = {c: answer["evidence"].get(c) for c in study.CHECKS}
            return answer
        return {"memory": wire(direct_records(source, scope)).decode()}


class ExecutedTests(unittest.TestCase):
    def test_reexecute_captured_sources_and_runtime_to_verify_actual_outcomes(self):
        data = json.loads(CAPTURE.read_text(encoding="utf-8"))
        cases = validate_capture(data)
        observed = 0
        for case, provenance in zip(cases, data["provenance"]):
            for record, run in zip(case["initial"] + case["between"], provenance["runs"]):
                with TemporaryDirectory(prefix="workflow-reproduction-") as folder:
                    root = Path(folder)
                    for name, contents in provenance["source_files"][run["source"]].items():
                        (root / name).write_bytes(contents.encode())
                    state = provenance["runtime_states"][run["runtime_state"]]
                    (root / "runtime.json").write_bytes(state["runtime.json"].encode())
                    if state["readiness.marker"]:
                        (root / "readiness.marker").write_bytes(b"ready\n")
                    args = ["-B", "test_calc.py"] if record["check"] == "tests" else ["-B", "checks.py", record["check"]]
                    self.assertEqual(["python", *args], record["argv"])
                    result = subprocess.run([sys.executable, *args], cwd=root, capture_output=True, timeout=30)
                    self.assertEqual(record["returncode"], result.returncode, (case["id"], record["check"]))
                    for name, contents in run["artifacts"].items():
                        self.assertEqual(contents.encode(), (root / name).read_bytes())
                    observed += 1
        self.assertEqual(48, observed)

    def test_expected_work_and_last_failure_are_independently_specified(self):
        for case in study.cases():
            answer = expected_answer(case["initial"] + case["between"], case["task"])
            self.assertEqual(EXPECTED_WORK[case["id"]], answer["needs_work"])
        case = next(c for c in study.cases() if c["id"] == "fail_recover_fail")
        self.assertEqual([1, 0, 1], [r["returncode"] for r in case["between"]])
        self.assertEqual(1, len({r["snapshot"] for r in case["initial"] + case["between"]}))

    def test_source_and_artifact_evidence_tampering_is_rejected(self):
        original = json.loads(CAPTURE.read_text(encoding="utf-8"))
        wrong = deepcopy(original)
        wrong["cases"][0]["initial"][0]["returncode"] = 1
        wrong["cases"][0]["initial"][0]["artifacts"] = {}
        with self.assertRaises(ValueError):
            validate_capture(wrong)
        wrong = deepcopy(original)
        next(iter(wrong["provenance"][0]["source_files"].values()))["calc.py"] += "# change\n"
        with self.assertRaisesRegex(ValueError, "Source digest"):
            validate_capture(wrong)

    def test_schedule_and_scope_revelation_do_not_leak_final_state(self):
        fake = Fake()
        episodes = execute(fake)
        self.assertEqual(108, len(fake.requests))
        self.assertEqual(study.schedule(), [i for i, _ in fake.requests])
        self.assertEqual(108, len(set(study.schedule())))
        for identity, request in fake.requests:
            observation = request["observation"]
            if request["stage"] == "parent":
                self.assertEqual({"tool_observations"}, set(observation))
            elif request["stage"] == "child":
                self.assertEqual({"previous_memory", "new_observations", "scope"}, set(observation))
            self.assertLessEqual(len(request_bytes(request)), 100000)
        self.assertTrue(all(not r["memories"]["direct_child"]["audit"]["infeasible"] for r in episodes))

    def test_index_preserves_chronology_and_excludes_unrequested_checks(self):
        fake = Fake()
        execute(fake)
        requests = dict(fake.requests)
        for case in study.cases():
            indexed = json.loads(requests[case["id"] + "-indexed-final"]["observation"]["memory"])
            full = json.loads(requests[case["id"] + "-full-final"]["observation"]["memory"])
            self.assertEqual(expected_answer(full, case["task"]), expected_answer(indexed, case["task"]))
            for check in study.CHECKS:
                observed = [r for r in indexed if r["check"] == check]
                wanted = [r for r in full if r["check"] == check] if check in case["task"]["required_checks"] else []
                self.assertEqual(wanted, observed)

    def test_checked_child_uses_only_scoped_bounded_parent_and_new_records(self):
        fake = Fake()
        episodes = execute(fake)
        for case, episode in zip(study.cases(), episodes):
            parent = json.loads(episode["memories"]["checked_parent"]["memory"])
            available = [r for r in parent + case["between"] if r["check"] in case["scope"]]
            memory, audit = study.checked_memory(None, available, study.CHILD_CAP)
            self.assertTrue(audit["fallback"])
            self.assertEqual(direct_records(available), json.loads(memory))
            self.assertEqual(expected_answer(case["initial"] + case["between"], case["task"]), expected_answer(json.loads(memory), case["task"]))
        memory, audit = study.checked_memory(None, [], study.CHILD_CAP)
        self.assertEqual("[]", memory)

    def test_full_saved_ledger_replay_reconciles_usage_and_rejects_answer_tampering(self):
        with TemporaryDirectory() as folder:
            directory = Path(folder) / "fake-only"
            preflight = Path(folder) / "preflight.json"
            save(preflight, {"isolation_passed": True, "real_model_generations": 0})
            prepare(directory, preflight)
            (directory / "calls").mkdir()
            class RecordingFake(Fake):
                def complete(self, identity, request):
                    response = super().complete(identity, request)
                    usage = {"inputTokens": 1, "cachedInputTokens": 0, "outputTokens": 1, "reasoningOutputTokens": 0, "totalTokens": 2}
                    save(directory / "calls" / (identity + ".json"), {
                        "identity": identity, "status": "completed", "dispatched": True, "model": "gpt-6-luna", "effort": "medium",
                        "request": request, "request_sha256": hashlib.sha256(request_bytes(request)).hexdigest(),
                        "usage_events": 1, "tool_items": 0, "harness_termination": "sessionBudgetExceeded",
                        "raw_answer": json.dumps(response), "response": response, "usage": usage,
                        "planning_credits": str(usage_cost(usage)), "wall_seconds": 0.0})
                    return response
            execute(RecordingFake(), directory)
            save(directory / "completion.json", {"status": "complete", "calls": 108, "planning_credits": str(108 * Decimal(".000015"))})
            result = analyze(directory)
            self.assertTrue(all(r["successes"] == 12 for r in result["arms"].values()))
            self.assertEqual(11, result["selective_retrieval"]["cases"])
            path = directory / "calls/unchanged-direct-final.json"
            changed = json.loads(path.read_text())
            changed["response"]["ready"] = False
            save(path, changed)
            with self.assertRaisesRegex(ValueError, "Answer or usage mismatch"):
                analyze(directory)


if __name__ == "__main__":
    unittest.main()
