"""Offline controls for permanent gaps, no-repeat dispatch and combined budgets."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .run import original, study, GAP, SuffixClient, prepare, verify, RESERVATION
from .analyze import analyze
from experiments.dependency_memory.workflow_executed.test_executed import Fake
from experiments.dependency_memory.workflow_executed.transport import save, usage_cost
from experiments.dependency_memory.workflow_eval_live.protocol import request_bytes


def record(identity, request, response):
    usage = {"inputTokens": 1, "cachedInputTokens": 0, "outputTokens": 1, "reasoningOutputTokens": 0, "totalTokens": 2}
    result = {"identity": identity, "status": "completed", "dispatched": True,
        "model": "gpt-6-luna", "effort": "medium", "request": request,
        "request_sha256": hashlib.sha256(request_bytes(request)).hexdigest(),
        "usage_events": 1, "tool_items": 0, "harness_termination": "sessionBudgetExceeded",
        "raw_answer": json.dumps(response), "response": response, "usage": usage,
        "planning_credits": str(usage_cost(usage)), "wall_seconds": 0.0}
    if identity == GAP:
        for key in ("usage", "raw_answer", "response", "planning_credits"):
            result.pop(key)
        result.update(status="transport_failure", error="appserver_timeout", reservation_credits=str(RESERVATION))
    return result


class ContinuationTests(unittest.TestCase):
    def fixture(self, root):
        old, new = root / "original", root / "continuation"
        preflight = root / "fake-preflight.json"
        save(preflight, {"isolation_passed": True, "real_model_generations": 0})
        original.prepare(old, preflight)
        (old / "calls").mkdir()
        fake = Fake()
        episodes = original.execute(fake)
        all_records = {identity: record(identity, request, fake_response(request)) for identity, request in fake.requests}
        for identity in study.schedule()[:17]:
            save(old / "calls" / (identity + ".json"), all_records[identity])
        save(old / "unchanged-episode.json", episodes[0])
        save(old / "completion.json", {"status": "stopped", "calls": 17, "planning_credits_settled": str(16 * Decimal(".000015"))})
        prepare(new, preflight, old)
        return old, new, all_records

    def test_suffix_never_dispatches_original_gap_and_analysis_keeps_missing_denominator(self):
        with TemporaryDirectory() as folder:
            old, new, records = self.fixture(Path(folder))
            plan, calls, known = verify(new, old)
            (new / "calls").mkdir()
            class Transport:
                spent = Decimal(0)
                identities = []
                def complete(self, identity, request):
                    self.identities.append(identity)
                    saved = records[identity]
                    self.spent += usage_cost(saved["usage"])
                    save(new / "calls" / (identity + ".json"), saved)
                    return saved["response"]
            transport = Transport()
            original.execute(SuffixClient(transport, calls, known, plan), new)
            save(new / "completion.json", {"status": "complete_suffix_with_original_gap", "new_calls": 91,
                "new_known_credits": str(transport.spent), "combined_known_credits": str(known + transport.spent)})
            result = analyze(new, old)
            self.assertEqual(study.schedule()[17:], transport.identities)
            self.assertNotIn(GAP, transport.identities)
            self.assertEqual(108, result["total_dispatches"])
            self.assertEqual(107, result["metered_answers"])
            self.assertEqual(11, len(result["complete_pair_cases"]))
            self.assertEqual(1, result["arms"]["prose"]["missing"])
            self.assertEqual(11, result["arms"]["prose"]["observed_successes"])
            self.assertEqual(12, result["arms"]["prose"]["success_count_upper"])
            self.assertTrue(all(a["complete_pair_successes"] == 11 for a in result["arms"].values()))
            self.assertEqual(Decimal(result["known_planning_credits"]) + RESERVATION, Decimal(result["reserved_upper_credits"]))
            changed = records[study.schedule()[17]]
            changed["response"]["ready"] = not changed["response"]["ready"]
            save(new / "calls" / (study.schedule()[17] + ".json"), changed)
            with self.assertRaisesRegex(ValueError, "Response or usage"):
                analyze(new, old)

    def test_unknown_reservation_prevents_dispatch_when_combined_ceiling_would_be_exceeded(self):
        with TemporaryDirectory() as folder:
            old, new, records = self.fixture(Path(folder))
            plan, calls, known = verify(new, old)
            class NeverCall:
                spent = Decimal("5")
                def complete(self, identity, request):
                    raise AssertionError("Must reject before transport")
            client = SuffixClient(NeverCall(), calls, known, plan)
            for identity in study.schedule()[:17]:
                client.complete(identity, records[identity]["request"])
            identity = study.schedule()[17]
            with self.assertRaisesRegex(RuntimeError, "Combined allocation"):
                client.complete(identity, records[identity]["request"])

    def test_original_evidence_changes_invalidate_continuation(self):
        with TemporaryDirectory() as folder:
            old, new, records = self.fixture(Path(folder))
            with (old / "unchanged-episode.json").open("a") as stream:
                stream.write("\n")
            with self.assertRaisesRegex(ValueError, "evidence changed"):
                verify(new, old)


def fake_response(request):
    return Fake().complete("offline-only", request)


if __name__ == "__main__":
    unittest.main()
