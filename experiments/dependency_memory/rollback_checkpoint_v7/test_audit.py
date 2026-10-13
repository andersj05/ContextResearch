"""Adversarial checks of the live isolation evidence, without model calls."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import tempfile
import unittest

from experiments.dependency_memory.rollback_checkpoint_v7.accounting import Ledger
from experiments.dependency_memory.rollback_checkpoint_v7.audit import EMPTY_MCP_INVENTORY, ReplayMismatch, _metering, ledger_rows
from experiments.dependency_memory.rollback_checkpoint_v7.client import REGISTRY_SHA256
from experiments.dependency_memory.rollback_checkpoint_v7.common import ROOT, MODEL, EFFORT
from experiments.dependency_memory.rollback_checkpoint_v7.prepare import generate, identities
from experiments.dependency_memory.rollback_pilot.subscription.accounting import Usage


class LiveEvidenceTests(unittest.TestCase):
    def test_valid_metering_cannot_hide_missing_or_enabled_mcp_inventory(self):
        parent = ROOT / "tmp" / "rollback-v7-audit-tests"
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as directory:
            path = Path(directory) / "ledger.sqlite"
            identity = identities(generate(split="fixture", replicates=1))[0]
            ledger = Ledger(path, [identity], 1, generation_ceiling=1)
            metadata = {"thread_id": "disclosed-offline-fixture", "model": MODEL,
                        "reasoning_effort": EFFORT, "harness_termination": "sessionBudgetExceeded",
                        "usage_events": 1, "tool_items": 0,
                        "mcp_resource_isolation": deepcopy(EMPTY_MCP_INVENTORY),
                        "preflight_registry_sha256": REGISTRY_SHA256}
            ledger.admit(identity, "fixture-request")
            ledger.complete(identity, Usage(20, 0, 5, 0), metadata, 0.01)
            calls, events, stop = ledger_rows(path)
            manifest = {"generation_ceiling": 1, "schedule": [asdict(identity)],
                        "model": MODEL, "effort": EFFORT}
            settings = {"workers": 1, "live": True}
            self.assertEqual(_metering(calls, events, stop, manifest, settings)[1], 1)
            for mutation in ("missing", "enabled", "resource", "registry"):
                with self.subTest(mutation=mutation):
                    changed = deepcopy(calls)
                    record = changed[0]["metadata"]
                    if mutation == "missing":
                        record.pop("mcp_resource_isolation")
                    elif mutation == "enabled":
                        record["mcp_resource_isolation"]["disabled_server_count"] = 0
                    elif mutation == "resource":
                        record["mcp_resource_isolation"]["resource_count"] = 1
                    else:
                        record["preflight_registry_sha256"] = "unreviewed-registry"
                    with self.assertRaisesRegex(ReplayMismatch, "MCP inventory or pinned registry"):
                        _metering(changed, events, stop, manifest, settings)


if __name__ == "__main__":
    unittest.main()
