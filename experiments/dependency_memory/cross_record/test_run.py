"""Development-only request and budget-contract checks; never calls a model."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from . import memory, run
from luna6_revision.protocol import request_bytes


class RunTests(unittest.TestCase):
    def test_public_request_timing_and_bounds(self):
        folder = Path(__file__).parent / "fixtures"
        for path in sorted(folder.glob("development-*.json")):
            case = json.loads(path.read_text(encoding="utf-8"))
            parent = memory.project(case["tool_schemas"], case["tool_results"])[0]
            child = memory.select(parent, case["candidate_ids"])[0]
            for arm in ("prompt", "structured"):
                request = run.parent_request(case, arm)
                self.assertLess(len(request_bytes(request)), 16000)
                raw = json.dumps(request)
                self.assertNotIn("private_truth_rows", raw)
                self.assertNotIn("late_event", raw)
            for arm in ("prompt", "structured", "checked"):
                request = run.child_request(case, arm, parent)
                self.assertLess(len(request_bytes(request)), 16000)
                self.assertNotIn("late_event", json.dumps(request))
            for future in case["futures"]:
                self.assertLess(len(request_bytes(run.execution_request(case, child, future))), 16000)
                self.assertLess(len(request_bytes(run.execution_request(case, run.compact(case["tool_results"]), future))), 16000)

    def test_global_client_rotates_before_adapter_cap(self):
        class Fake:
            def __init__(self, *_):
                self.attempts = 0
                self.spent = run.Decimal(0)
            def complete(self, *_):
                self.attempts += 1
                self.spent += run.Decimal("0.001")
                return {"memory": "ok"}
        with patch.object(run, "Client", Fake):
            client = run.BudgetedClient(None, None, None, None)
            for index in range(121):
                client.complete(str(index), {})
            self.assertEqual(2, len(client.clients))
            self.assertEqual(120, client.clients[0].attempts)
            self.assertEqual(1, client.clients[1].attempts)
            self.assertEqual(121, client.attempts)

    def test_development_episode_and_full_group_recovery(self):
        from . import analyze
        path = Path(__file__).parent / "fixtures/development-package-61011.json"
        case = json.loads(path.read_text(encoding="utf-8"))

        class Fake:
            calls = []
            def complete(self, identity, request):
                self.calls.append(identity)
                if identity.endswith("-parent"):
                    if identity.endswith("structured-parent"):
                        return {"memory": "unverified summary"}
                    return {"memory": memory.project(case["tool_schemas"], case["tool_results"])[0]}
                parent = request["observation"]["previous_memory"]
                if identity.endswith("structured-child"):
                    return {"memory": "short summary"}
                return {"memory": memory.select(parent, case["candidate_ids"])[0]}

        with TemporaryDirectory() as folder:
            episode = run.prepare_memories(Fake(), case, Path(folder))
            self.assertEqual(5, len(Fake.calls))
            self.assertTrue(episode["checks"]["parent_fallback"])
            self.assertTrue(episode["checks"]["checked_child_proposal"]["passed"])
            for future in case["futures"]:
                for arm in ("checked", "automatic", "direct", "indexed_raw", "indexed_projected", "full"):
                    retained = run.retained_for(arm, case, episode, future)
                    self.assertEqual("sufficient", analyze.information_sufficiency(retained, case, future))
                recovered = json.loads(episode["index"][future["target"]])
                self.assertEqual(set(case["tool_schemas"]), {item["tool"] for item in recovered})


if __name__ == "__main__":
    unittest.main()
