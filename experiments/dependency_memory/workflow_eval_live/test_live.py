"""Offline causal-channel, grading and launch-boundary checks; no model calls."""
from copy import deepcopy
import hashlib
import json
import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
from decimal import Decimal

from . import study, profile
from .run import execute
from .run import prepare
from .analyze import analyze
from .transport import save, usage_cost
from .protocol import request_bytes
from experiments.dependency_memory.workflow_eval.grader import expected_answer, wire
from experiments.dependency_memory.workflow_eval.packet import direct_records


class PerfectFake:
    def __init__(self):
        self.requests = []
    def complete(self, identity, request):
        self.requests.append((identity, request))
        observation = request["observation"]
        if request["stage"] == "parent":
            source = observation["tool_observations"]
        elif request["stage"] == "child":
            source = json.loads(observation["previous_memory"]) + observation["new_observations"]
        else:
            answer = expected_answer(json.loads(observation["memory"]), observation["final_public_state"])
            answer["evidence"] = {c: answer["evidence"].get(c) for c in study.CHECKS}
            return answer
        return {"memory": wire(direct_records(source)).decode()}


class LiveTests(unittest.TestCase):
    def test_saved_answer_replay_and_accounting_reject_tampering(self):
        with TemporaryDirectory() as temp:
            directory = Path(temp) / "fake-only"
            audit_path = Path(temp) / "fake-preflight.json"
            save(audit_path, {"isolation_passed": True, "real_model_generations": 0})
            prepare(directory, audit_path)
            (directory / "calls").mkdir()
            class RecordingFake(PerfectFake):
                def complete(self, identity, request):
                    response = super().complete(identity, request)
                    usage = {"inputTokens": 1, "cachedInputTokens": 0, "outputTokens": 1,
                             "reasoningOutputTokens": 0, "totalTokens": 2}
                    save(directory / "calls" / (identity + ".json"), {
                        "identity": identity, "status": "completed", "dispatched": True,
                        "model": "gpt-6-luna", "effort": "medium", "request": request,
                        "request_sha256": hashlib.sha256(request_bytes(request)).hexdigest(),
                        "usage_events": 1, "tool_items": 0, "harness_termination": "sessionBudgetExceeded",
                        "raw_answer": json.dumps(response), "response": response, "usage": usage,
                        "planning_credits": str(usage_cost(usage)), "wall_seconds": 0.0})
                    return response
            execute(RecordingFake(), directory)
            save(directory / "completion.json", {"status": "complete", "calls": 36,
                "planning_credits": str(36 * Decimal(".000015"))})
            result = analyze(directory)
            self.assertEqual(36, result["actual_model_calls"])
            self.assertTrue(all(row["successes"] == 4 for row in result["arms"].values()))
            final_path = directory / "calls/unchanged-direct-final.json"
            call = json.loads(final_path.read_text(encoding="utf-8"))
            call["response"]["ready"] = False
            save(final_path, call)
            with self.assertRaisesRegex(ValueError, "Answer or usage mismatch"):
                analyze(directory)

    def test_schedule_is_complete_unique_and_replayed_without_grader_feedback(self):
        client = PerfectFake()
        episodes = execute(client)
        self.assertEqual(study.schedule(), [identity for identity, _ in client.requests])
        self.assertEqual(36, len(set(study.schedule())))
        self.assertEqual(4, len(episodes))
        for identity, request in client.requests:
            if request["stage"] in {"parent", "child"}:
                self.assertNotIn("final_public_state", request["observation"])
                self.assertNotIn("task", request["observation"])
            if request["stage"] == "child":
                self.assertEqual({"previous_memory", "new_observations", "scope"}, set(request["observation"]))
        self.assertTrue(all(len(request_bytes(r)) <= 100000 for _, r in client.requests))

    def test_four_conditions_have_independently_expected_required_work(self):
        expected = {"unchanged": [], "new_snapshot": list(study.CHECKS),
                    "later_failure": ["tests"], "replaced_artifact": ["paper"]}
        for case in study.cases():
            answer = expected_answer(case["initial"] + case["between"], case["task"])
            self.assertEqual(expected[case["id"]], answer["needs_work"])
        self.assertEqual(["observed_local_capture"] + ["constructed_control"] * 3,
                         [case["origin"] for case in study.cases()])

    def test_checker_rejects_wrong_state_and_does_not_resurrect_deleted_source(self):
        case = study.cases()[2]
        source = case["initial"] + case["between"]
        wrong = direct_records(source)
        next(r for r in wrong if r["check"] == "tests")["returncode"] = 0
        memory, audit = study.checked_memory({"memory": wire(wrong).decode()}, source, study.CHILD_CAP)
        self.assertTrue(audit["fallback"])
        self.assertEqual(["tests"], expected_answer(json.loads(memory), case["task"])["needs_work"])
        # A child given only the later failed test cannot recover other receipts.
        memory, audit = study.checked_memory(None, case["between"], study.CHILD_CAP)
        self.assertEqual(["tests"], [r["check"] for r in json.loads(memory)])

    def test_oversize_or_malformed_prose_is_not_clipped_or_retried(self):
        self.assertEqual("", study.admit_prose({"memory": "x" * 1537}, 1536)[0])
        self.assertEqual("", study.admit_prose({"memory": 1}, 1536)[0])
        self.assertEqual("é", study.admit_prose({"memory": "é"}, 2)[0])
        self.assertEqual("", study.admit_prose({"memory": "é"}, 1)[0])

    def test_normalization_only_removes_nulls_from_exact_provider_keys(self):
        answer = {"ready": False, "needs_work": list(study.CHECKS), "evidence": {c: None for c in study.CHECKS}}
        self.assertEqual({}, study.normalize_response(answer)["evidence"])
        wrong = {**answer, "evidence": {**answer["evidence"], "invented": "x"}}
        self.assertEqual(wrong, study.normalize_response(wrong))

    def test_final_index_and_full_views_preserve_every_record_and_later_failure(self):
        fake = PerfectFake()
        execute(fake)
        requests = dict(fake.requests)
        for case in study.cases():
            indexed = json.loads(requests[case["id"] + "-indexed-final"]["observation"]["memory"])
            full = json.loads(requests[case["id"] + "-full-final"]["observation"]["memory"])
            self.assertEqual({r["run_id"]: r for r in full}, {r["run_id"]: r for r in indexed})
            self.assertEqual(expected_answer(full, case["task"]), expected_answer(indexed, case["task"]))

    def test_request_rejects_evaluator_metadata_and_large_body(self):
        request = study.audit_request()
        with self.assertRaises(ValueError):
            request_bytes({**request, "expected_answer": {}})
        oversized = deepcopy(request)
        oversized["observation"] = {"data": "x" * 100001}
        with self.assertRaises(ValueError):
            request_bytes(oversized)
        self.assertLess(profile.wire_body_byte_bound(request), profile.MAX_WIRE_BYTES)

    def test_isolation_audit_rejects_extra_message_and_external_registry(self):
        tools = [{"type": "namespace", "name": "functions", "tools": []}]
        registry = {ns: {"functions": {name: {"source": {"kind": "harness"}} for name in names}}
            for ns, names in {"functions": ("exec", "wait", "request_user_input", "request_user_input_async"),
                              "clock": ("curr_time", "sleep")}.items()}
        messages = [("developer", profile.BASE_INSTRUCTIONS), ("developer", profile.DEVELOPER_INSTRUCTIONS),
            ("user", "# AGENTS.md instructions\n\n<INSTRUCTIONS>\nfixed\n</INSTRUCTIONS>"),
            ("user", "public"), ("developer", profile.ROLLOUT_GUARD_TEXT)]
        body = {"model": profile.MODEL, "reasoning": {"effort": "medium"}, "store": False, "stream": True,
            "client_metadata": {"x-codex-turn-metadata": json.dumps({"model": profile.MODEL,
                "reasoning_effort": "medium", "tool_namespaces_info": registry})},
            "input": [{"type": "additional_tools", "id": "synthetic", "role": "developer", "tools": tools}]
                + [{"type": "message", "id": str(i), "role": role, "content": [{"type": "input_text", "text": text}]}
                   for i, (role, text) in enumerate(messages)]}
        digest = hashlib.sha256(json.dumps(tools, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        with patch.object(profile, "VISIBLE_TOOL_SPEC_SHA256", digest):
            profile.audit_payload(body, public_text="public", global_instructions_text="fixed")
            wrong = deepcopy(body)
            wrong["input"].append(wrong["input"][-1])
            with self.assertRaises(ValueError):
                profile.audit_payload(wrong, public_text="public", global_instructions_text="fixed")
            registry["shell"] = {"functions": {"exec_command": {"source": {"kind": "harness"}}}}
            wrong = deepcopy(body)
            wrong["client_metadata"]["x-codex-turn-metadata"] = json.dumps({"model": profile.MODEL,
                "reasoning_effort": "medium", "tool_namespaces_info": registry})
            with self.assertRaises(ValueError):
                profile.audit_payload(wrong, public_text="public", global_instructions_text="fixed")


if __name__ == "__main__":
    unittest.main()
