"""Never-dispatched selection and combined unknown-usage budget invariants."""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.dependency_memory.scope_inference import profile, protocol, transport
from experiments.dependency_memory.scope_inference_suffix import run


class SuffixControls(unittest.TestCase):
    def test_only_never_dispatched_identities_and_original_order(self):
        before = run.preceding()
        pending = [r["identity"] for r in before["calls"] if r["status"] == "not_dispatched"]
        selected = [r["identity"] for r in run.schedule()]
        self.assertEqual(selected, pending)
        self.assertEqual(len(selected), 5)
        self.assertNotIn("scope-v2-r2-concise", selected)
        self.assertEqual(set(selected) & {r["identity"] for r in before["calls"] if r.get("dispatched")}, set())
        seed = run.budget_seed()
        self.assertEqual(seed["provider_dispatches"], 3)
        self.assertEqual(Decimal(seed["committed_planning_credits"]), Decimal("7.712325"))

    def test_another_unknown_reservation_stops_before_any_server_or_hash_read(self):
        client = transport.Client.__new__(transport.Client)
        client.attempts, client.spent, client.stopped = 4, Decimal("15.362325"), False
        with patch.object(transport, "AppServer") as server, patch.object(client, "check_hashes") as hashes:
            with self.assertRaisesRegex(RuntimeError, "Allocation exhausted"):
                client.complete("never-dispatched-control", protocol.request("closure"))
            server.assert_not_called()
            hashes.assert_not_called()

    def test_frozen_manifest_rejects_erased_unknown_usage_and_failed_identity(self):
        audit = {"version": "scope_luna6_preflight_v1", "isolation_passed": True, "real_model_generations": 0,
                 "cases": [{"payload_audit": {"visible_tool_spec_sha256": profile.VISIBLE_TOOL_SPEC_SHA256}} for _ in range(4)]}
        with tempfile.TemporaryDirectory() as folder:
            import json
            root = Path(folder)
            audit_path = root / "preflight.json"
            audit_path.write_text(json.dumps(audit))
            manifest = run.prepare(audit_path, root / "prepared")
            run.verify(manifest)
            bad = deepcopy(manifest)
            bad["budget_seed"]["unknown_reservations"] = "0"
            with self.assertRaises(ValueError):
                run.verify(bad)
            bad = deepcopy(manifest)
            bad["requests"][0]["identity"] = "scope-v2-r2-concise"
            with self.assertRaises(ValueError):
                run.verify(bad)


if __name__ == "__main__":
    unittest.main()
