"""Independent review controls for the fixed live-probe controller and audit.

Every transport and client preflight in this file is explicitly substituted
with a local fixture. Real ledger admission, request saving, batching and audit
run normally; these tests make zero provider/model calls.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path
import io
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from experiments.dependency_memory.rollback_parallel_v8 import live_benchmark as probe
from experiments.dependency_memory.rollback_parallel_v8.audit import (
    EMPTY_MCP_INVENTORY, verify_live_preflight,
)
from experiments.dependency_memory.rollback_parallel_v8.client import (
    REGISTRY_SHA256, NAMESPACE_SHA256, RESOURCE_HELPERS,
)
from experiments.dependency_memory.rollback_parallel_v8.common import ROOT, read, sha, wire
from experiments.dependency_memory.rollback_parallel_v8.prepare import generate
from experiments.dependency_memory.rollback_math_followup_v4.observe import DiagnosedProtocolError
from experiments.dependency_memory.rollback_pilot.subscription.process import ProtocolError
from experiments.dependency_memory.rollback_pilot.subscription.accounting import Usage, RESERVATION
from experiments.dependency_memory.rollback_pilot.subscription.transport import Response


def fixture_preflight():
    positive = {"accepted_transport": True, "http_attempts": 1,
                "authorization_present": False, "real_model_generations": 0,
                "mcp_resource_isolation": deepcopy(EMPTY_MCP_INVENTORY)}
    return {
        "evidence_kind": "disclosed_offline_fixture",
        "serialization_and_retry_audit_passed": True,
        "v8_payload_schema_audit_passed": True, "v8_verified_workers": 16,
        "v8_parallel_payload_checks": [deepcopy(positive) for _ in range(16)],
        "real_model_generations": 0, "registry_sha256": REGISTRY_SHA256,
        "namespace_metadata_sha256": NAMESPACE_SHA256,
        "declared_inert_mcp_helpers": list(RESOURCE_HELPERS),
        "mcp_inventory_checked_before_every_generation": True,
        "cases": [{**deepcopy(positive), "case": helper, "accepted_transport": False,
                   "safe_failure_reason": {"reason_code": "tool_or_external_information_attempt"}}
                  for helper in RESOURCE_HELPERS],
        "compatibility_diagnostics": [{**deepcopy(positive), "case": "clock_with_answer",
            "diagnostic_only": True, "protocol_observation": {
                "server_error_codes": ["sessionBudgetExceeded"],
                "method_counts": {"thread/tokenUsage/updated": 1}}}],
    }


def reseal(folder):
    """Recompute a fixture seal so mutation tests exercise semantic audit."""
    value = {"files": [{"path": path.relative_to(folder).as_posix(), "sha256": sha(path.read_bytes())}
                       for path in sorted(folder.rglob("*.json"))
                       if path.name != "evidence_manifest.json" and "scratch" not in path.relative_to(folder).parts],
             "ledger_sha256": sha((folder / "ledger.sqlite").read_bytes())}
    (folder / "evidence_manifest.json").write_text(wire(value), encoding="utf-8")


class LiveProbeReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = generate(split="fixture", replicates=16)
        cls.manifest = probe.plan({"model": "gpt-6-luna", "effort": "medium", "source_bindings": []}, cls.tasks)

    def setUp(self):
        parent = ROOT / "tmp" / "rollback-v8-probe-review"
        parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name).resolve()
        self.bundle = self.folder / "bundle"
        self.bundle.mkdir()
        self.output = self.folder / "output"

    def run_fixture(self, *, local_unknown=False, global_failure=False, violate_eight_worker_cap=False):
        tasks, manifest = self.tasks, self.manifest
        touched, lock = Counter(), threading.Lock()
        actual_counts = (16, 16, 16, 16) if violate_eight_worker_cap else probe.COUNTS
        gates = [threading.Barrier(count) for count in actual_counts]

        class FixtureTransport:
            def generate(inner, identity, request):
                batch = int(identity.arm.split("-", 1)[0][len("batch"):])
                with lock:
                    touched[identity.key] += 1
                gates[batch].wait(timeout=20)
                time.sleep(0.002)
                if global_failure and batch == 0:
                    raise DiagnosedProtocolError(ProtocolError("fixture_configuration_failure"), "configuration", {})
                if identity.task_id == tasks[0]["task_id"]:
                    if local_unknown and batch == 1:
                        raise DiagnosedProtocolError(ProtocolError("generation_timeout"), "collect", {})
                metadata = {"thread_id": "offline-fixture-" + identity.key, "model": "gpt-6-luna",
                            "reasoning_effort": "medium", "harness_termination": "sessionBudgetExceeded",
                            "usage_events": 1, "tool_items": 0,
                            "mcp_resource_isolation": deepcopy(EMPTY_MCP_INVENTORY),
                            "preflight_registry_sha256": REGISTRY_SHA256}
                return Response('{"disclosed_offline_fixture":true}', Usage(20, 0, 5, 0), metadata, False)

        def executor(*, max_workers, **kwargs):
            return ThreadPoolExecutor(max_workers=16 if violate_eight_worker_cap else max_workers, **kwargs)

        with patch.object(probe, "checked_plan", return_value=(manifest, tasks)), \
             patch.object(probe, "client_preflight", return_value=fixture_preflight()), \
             patch.object(probe, "live_factory", return_value=FixtureTransport), \
             patch.object(probe, "ThreadPoolExecutor", side_effect=executor), \
             redirect_stdout(io.StringIO()):
            result = probe.run_probe(self.bundle, self.output, live=True,
                                     executable="never-executed-fixture", global_instructions=self.folder / "unused")
        return result, touched

    def audit_fixture(self):
        with patch.object(probe, "checked_plan", return_value=(self.manifest, self.tasks)):
            return probe.audit_probe(self.bundle, self.output)

    def test_all_64_fixture_admissions_are_unique_and_identically_prompted(self):
        result, touched = self.run_fixture()
        self.assertEqual(result["completed"], 64)
        self.assertEqual(result["unknown"], 0)
        self.assertEqual(set(touched.values()), {1})
        self.assertEqual(len(touched), 64)
        checked = self.audit_fixture()
        self.assertTrue(checked["all_passed"])
        self.assertTrue(checked["identical_prompts_verified"])
        self.assertTrue(checked["serial_batches_verified"])
        self.assertEqual(checked["peak_admitted_calls"], 16)
        analysis = read(self.output / "analysis.json")
        self.assertTrue(analysis["all_64_calls_known"])
        self.assertIsNotNone(analysis["descriptive_16_vs_8_speed_ratio"])
        self.assertEqual(sum(row["resources"]["recorded_calls"] for row in analysis["batches"]), 64)

    def test_one_unknown_preserves_reservation_and_removes_speed_ratio(self):
        result, touched = self.run_fixture(local_unknown=True)
        self.assertEqual(result["completed"], 63)
        self.assertEqual(result["unknown"], 1)
        self.assertIsNone(result["stop"])
        self.assertEqual(set(touched.values()), {1})
        self.assertTrue(self.audit_fixture()["all_passed"])
        accounting = read(self.output / "accounting.json")
        self.assertEqual(accounting["locked_planning_credits"], str(RESERVATION))
        analysis = read(self.output / "analysis.json")
        self.assertFalse(analysis["all_64_calls_known"])
        self.assertIsNone(analysis["descriptive_16_vs_8_speed_ratio"])
        self.assertIsNone(analysis["descriptive_elapsed_reduction_fraction"])
        self.assertEqual(sum(row["unknown_calls"] for row in analysis["batches"]), 1)
        self.assertEqual(sum(row["never_admitted_calls"] for row in analysis["batches"]), 0)
        self.assertEqual(sum(row["resources"]["recorded_calls"] for row in analysis["batches"]), 63)

    def test_global_failure_keeps_all_dispositions_without_replacements(self):
        result, touched = self.run_fixture(global_failure=True)
        self.assertIsNotNone(result["stop"])
        self.assertGreaterEqual(result["unknown"], 1)
        self.assertEqual(set(touched.values()), {1})
        self.assertTrue(self.audit_fixture()["all_passed"])
        analysis = read(self.output / "analysis.json")
        self.assertIsNone(analysis["descriptive_16_vs_8_speed_ratio"])
        self.assertEqual(sum(len(row["dispositions"]) for row in analysis["batches"]), 64)
        self.assertGreater(sum(row["never_admitted_calls"] for row in analysis["batches"]), 0)
        self.assertEqual(sum(row["admitted_calls"] + row["never_admitted_calls"]
                             for row in analysis["batches"]), 64)

    def test_eight_worker_batch_cannot_hide_sixteen_concurrent_admissions(self):
        self.run_fixture(violate_eight_worker_cap=True)
        with self.assertRaisesRegex(probe.ReplayMismatch, "concurrency invariant"):
            self.audit_fixture()

    def test_saved_request_mutation_is_rejected_even_after_resealing(self):
        self.run_fixture()
        path = next((self.output / "requests").glob("*.json"))
        value = read(path)
        value["messages"][1]["content"] += "\nUndeclared information."
        path.write_text(wire(value), encoding="utf-8")
        reseal(self.output)
        with self.assertRaisesRegex(probe.ReplayMismatch, "prompts differ"):
            self.audit_fixture()

    def test_wrong_elapsed_metric_is_rejected_after_analysis_and_seal_refresh(self):
        self.run_fixture()
        path = self.output / "batches" / "0.json"
        value = read(path)
        value["wall_seconds"] += 60.0
        path.write_text(wire(value), encoding="utf-8")
        batches = [read(self.output / "batches" / f"{index}.json") for index in range(4)]
        calls = read(self.output / "accounting.json")["calls"]
        (self.output / "analysis.json").write_text(wire(probe.analyze(calls, batches)), encoding="utf-8")
        reseal(self.output)
        with self.assertRaises(probe.ReplayMismatch):
            self.audit_fixture()

    def test_preflight_rejects_wrong_parallelism_authorization_and_channel_inventory(self):
        verify_live_preflight(fixture_preflight(), 16)
        for mutation in ("workers", "authorization", "resources", "missing_helper", "diagnostic"):
            with self.subTest(mutation=mutation):
                value = fixture_preflight()
                if mutation == "workers":
                    value["v8_parallel_payload_checks"] = value["v8_parallel_payload_checks"][:8]
                elif mutation == "authorization":
                    value["v8_parallel_payload_checks"][0]["authorization_present"] = True
                elif mutation == "resources":
                    value["v8_parallel_payload_checks"][0]["mcp_resource_isolation"]["resource_count"] = 1
                elif mutation == "missing_helper":
                    value["cases"].pop()
                else:
                    value["compatibility_diagnostics"] = []
                with self.assertRaises(probe.ReplayMismatch):
                    verify_live_preflight(value, 16)


if __name__ == "__main__":
    unittest.main()
