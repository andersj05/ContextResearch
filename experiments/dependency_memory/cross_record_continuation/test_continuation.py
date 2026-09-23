"""Offline checks of the exact suffix, no-retry boundary and controller."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from experiments.dependency_memory.cross_record import memory
from . import plan, run


class ContinuationTests(unittest.TestCase):
    def test_frozen_prefix_suffix_and_permanent_failure(self):
        data = run.verify_plan()
        ordered = plan.schedule()
        self.assertEqual(348, len(ordered))
        self.assertEqual(ordered[198], data["original_failed_identity"])
        self.assertEqual(ordered[199:], data["ordered_pending"])
        self.assertEqual(149, len(data["ordered_pending"]))
        self.assertNotIn(data["original_failed_identity"], data["ordered_pending"])

    def test_controller_accepts_only_next_identity_and_never_retries(self):
        class Fake:
            def __init__(self, *_):
                self.attempts = 0
                self.spent = run.Decimal(0)
                self.stopped = False
            def complete(self, identity, request):
                self.attempts += 1
                self.spent += run.Decimal("0.01")
                return {"memory": identity}
        with TemporaryDirectory() as folder, patch.object(run, "Client", Fake):
            path = Path(folder)
            (path / "calls").mkdir()
            client = run.ContinuationClient(None, None, path, None, ["a", "b"])
            with self.assertRaises(ValueError):
                client.complete("b", {})
            client.complete("a", {})
            with self.assertRaises(ValueError):
                client.complete("a", {})
            client.complete("b", {})
            self.assertEqual(2, client.attempts)
            self.assertEqual(2, client.next_index)

    def test_full_suffix_dry_run_without_model_or_original_mutation(self):
        class Fake:
            def __init__(self, *_):
                self.attempts = 0
                self.spent = run.Decimal(0)
                self.stopped = False
            def complete(self, identity, request):
                self.attempts += 1
                self.spent += run.Decimal("0.001")
                stage = request["stage"]
                observation = request["observation"]
                if stage == "parent":
                    return {"memory": memory.project(observation["tool_schemas"], observation["tool_results"])[0]}
                if stage == "child":
                    return {"memory": memory.select(observation["previous_memory"], observation["candidates"])[0]}
                return {"action": "hold", "target_id": observation["target"], "work": []}
        with TemporaryDirectory() as folder, patch.object(run, "Client", Fake), patch.object(run, "run_case", return_value={"loopback": "ok"}):
            output = Path(folder) / "dry"
            instructions = Path(folder) / "instructions.txt"
            instructions.write_text("dry run", encoding="utf-8")
            run.launch(output, Path("fake"), instructions)
            completion = json.loads((output / "completion.json").read_text(encoding="utf-8"))
            self.assertEqual("complete_with_permanent_original_failure", completion["status"])
            self.assertEqual(149, completion["new_attempts"])

    def test_provider_error_is_permanent_and_advances_once(self):
        class Fake:
            instances = 0
            def __init__(self, *args):
                self.attempts = 0
                self.spent = run.Decimal(0)
                self.stopped = False
                self.directory = args[2]
                Fake.instances += 1
            def complete(self, identity, request):
                self.attempts += 1
                if identity == "a":
                    self.stopped = True
                    run.save(self.directory / "calls/a.json", {"identity": "a", "status": "transport_failure",
                                                               "dispatched": True, "error": "Provider generation error"})
                    raise RuntimeError("Provider generation error")
                self.spent += run.Decimal("0.01")
                return {"memory": "ok"}
        with TemporaryDirectory() as folder, patch.object(run, "Client", Fake):
            path = Path(folder)
            (path / "calls").mkdir()
            client = run.ContinuationClient(None, None, path, None, ["a", "b"])
            self.assertIsNone(client.complete("a", {}))
            self.assertTrue(client.last_failed)
            client.complete("b", {})
            self.assertEqual(["a"], client.provider_failures)
            self.assertEqual(run.RESERVATION, client.unknown_reservations)
            self.assertEqual(2, client.attempts)
            self.assertEqual(2, Fake.instances)


if __name__ == "__main__":
    unittest.main()
