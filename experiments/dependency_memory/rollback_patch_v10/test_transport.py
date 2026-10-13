"""Expanded admission with unchanged isolated subscription channels."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import threading
import tomllib
import unittest
from unittest.mock import patch

from experiments.dependency_memory.rollback_patch_v10 import transport
from experiments.dependency_memory.rollback_patch_v10.common import ROOT, MAX_BODY_BYTES, MAX_INPUT_TEXT_BYTES
from experiments.dependency_memory.rollback_patch_v10.contexts import render, fits, LESSON
from experiments.dependency_memory.rollback_patch_v10.engine import patch as source_patch
from experiments.dependency_memory.rollback_patch_v10.tasks import generate
from experiments.dependency_memory.rollback_pilot.records import digest, InterfaceError
from experiments.dependency_memory.rollback_pilot.subscription import profile
from experiments.dependency_memory.rollback_pilot.subscription.accounting import Usage
from experiments.dependency_memory.rollback_pilot.subscription.transport import Response
from experiments.dependency_memory.rollback_pilot.transport import UnknownDispatch
from experiments.dependency_memory.rollback_math_followup_v4.observe import DiagnosedProtocolError


def empty_inventory():
    return {"data": [{"name": "node_repl", "runtimeStatus": "disabled", "tools": {},
                      "resources": [], "resourceTemplates": []}], "nextCursor": None}


def continuation_request(task):
    # A serialization fixture using authored source, never an observed failure.
    files = task["evaluator"]["reference_files"]
    delta = source_patch(task["base_files"], files)
    public = {"status": "public_mismatch", "input": task["public_tests"][0]["input"],
              "expected": task["public_tests"][0]["expected"], "observed": None,
              "detail": "Synthetic serialization fixture, not execution evidence."}
    prefix = {"failed_record": {"public": public,
                               "visible_work": {"patch": delta["diff"], "note": "Fixture patch"}},
              "lesson": {key: value["enum"][-1] for key, value in LESSON["properties"].items()}}
    records = [{"step": step, "public": public, "work": prefix["failed_record"]["visible_work"]}
               for step in (1, 2)]
    return render(task, arm="KL", prefix=prefix, records=records)


class ExpandedTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = generate(split="fixture", per_family=1)
        cls.request = max((continuation_request(task) for task in cls.tasks), key=profile.body_bound)

    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="rollback-v10-transport-", dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.instructions = self.folder / "AGENTS.md"
        self.instructions.write_text("Synthetic global instructions.\n", encoding="utf-8")
        self.executable = self.folder / "fixture-client.exe"
        self.executable.write_bytes(b"synthetic executable bytes, never launched")
        self.checked = {"serialization_and_retry_audit_passed": True,
                        "executable_sha256": digest(self.executable.read_bytes()),
                        "global_instructions_sha256": digest(self.instructions.read_text(encoding="utf-8")),
                        "configuration_sha256": digest(str(profile.OVERRIDES + profile.PROVIDER_OVERRIDES)),
                        "registry_sha256": transport.REGISTRY_SHA256,
                        "namespace_metadata_sha256": transport.NAMESPACE_SHA256,
                        "mcp_inventory_checked_before_every_generation": True}

    def adapter(self, checked=None):
        return transport.Transport(self.executable, self.instructions,
                                   self.checked if checked is None else checked, self.folder / "scratch")

    def fake_server(self, instances, *, barrier=None, bad_inventory=False, exhausted=False):
        lock, instructions = threading.Lock(), str(self.instructions)

        class Server:
            def __init__(inner, executable, cwd, overrides):
                with lock:
                    inner.index = len(instances)
                    instances.append(inner)
                inner.cwd, inner.overrides = cwd, overrides
                inner.calls, inner.closed = [], False

            def initialize(inner):
                inner.calls.append("initialize")

            def rpc(inner, method, params):
                inner.calls.append(method)
                if method == "account/read":
                    return {"account": {"type": "chatgpt"}}
                if method == "account/rateLimits/read":
                    return {"ordinaryUsageAllowed": True, "rateLimitsByLimitId": {"codex": {
                        "primary": {"usedPercent": 100 if exhausted else 1}, "secondary": None,
                        "spendControlReached": False, "rateLimitReachedType": None}}}
                if method == "config/read":
                    return {"config": tomllib.loads("\n".join(profile.OVERRIDES + profile.PROVIDER_OVERRIDES))}
                if method == "thread/start":
                    inner.thread_params = deepcopy(params)
                    return {"model": profile.MODEL, "modelProvider": profile.PROVIDER,
                            "runtimeWorkspaceRoots": [], "instructionSources": [instructions],
                            "thread": {"id": "v10-fresh-" + str(inner.index), "turns": [], "environments": []}}
                if method == "mcpServerStatus/list":
                    if barrier is not None:
                        barrier.wait(timeout=20)
                    inventory = empty_inventory()
                    if bad_inventory:
                        inventory["data"][0]["resources"] = [{"uri": "fixture://forbidden"}]
                    return inventory
                if method == "turn/start":
                    inner.turn_params = deepcopy(params)
                    return {"turn": {"id": "v10-turn-" + str(inner.index)}}
                raise AssertionError("unexpected RPC: " + method)

            def close(inner):
                inner.closed = True

        return Server

    @staticmethod
    def collect_fixture(*args, **kwargs):
        return Response('{"fixture":true}', Usage(1, 0, 1, 0), {
            "model": profile.MODEL, "usage_events": 1, "tool_items": 0,
            "harness_termination": "sessionBudgetExceeded"})

    def test_context_and_rpc_share_input_boundary_and_independent_body_guard(self):
        self.assertEqual(MAX_BODY_BYTES, 4 * 1024 * 1024)
        self.assertEqual(MAX_INPUT_TEXT_BYTES, 1024 * 1024)
        for bound, accepted in ((MAX_BODY_BYTES, True), (MAX_BODY_BYTES + 1, False)):
            request = transport.capacity_request(self.request, bound)
            self.assertEqual(profile.body_bound(request), bound)
            self.assertEqual(transport.fits_body(request), accepted)
        for input_bytes, accepted in ((MAX_INPUT_TEXT_BYTES, True), (MAX_INPUT_TEXT_BYTES + 1, False)):
            bound = profile.body_bound(self.request) + input_bytes - len(self.request.json_text.encode("utf-8"))
            request = transport.capacity_request(self.request, bound)
            self.assertEqual(len(request.json_text.encode("utf-8")), input_bytes)
            self.assertEqual(fits(request), accepted)
            self.assertEqual(transport.fits(request), accepted)
            if accepted:
                self.assertEqual(transport.turn_parameters("fixture", request)["input"][0]["text"], request.json_text)
            else:
                with self.assertRaises(InterfaceError):
                    transport.turn_parameters("fixture", request)

    def test_realistic_third_attempt_exceeds_historical_cap_but_is_admissible(self):
        self.assertGreater(profile.body_bound(self.request), 131072)
        self.assertTrue(fits(self.request))
        params = transport.turn_parameters("fixture", self.request)
        self.assertEqual(params["environments"], [])
        self.assertEqual(params["runtimeWorkspaceRoots"], [])
        self.assertEqual(params["summary"], "none")

    def test_body_overflow_is_rejected_before_any_provider_process(self):
        oversized = transport.capacity_request(self.request, MAX_BODY_BYTES + 1)
        adapter = self.adapter()
        with patch.object(transport, "AppServer", side_effect=AssertionError("must not launch provider")):
            with self.assertRaises(InterfaceError):
                adapter.generate(SimpleNamespace(key="oversized"), oversized)
        self.assertNotIn("oversized", adapter.seen)

    def test_32_parallel_realistic_requests_keep_fresh_sessions_and_channel_checks(self):
        instances, barrier = [], threading.Barrier(32)
        factory = transport.live_factory(self.executable, self.instructions, self.checked, self.folder / "scratch")
        requests = [continuation_request(task) for task in self.tasks]

        def run(index):
            return factory().generate(SimpleNamespace(key="parallel-" + str(index)), requests[index % len(requests)])

        with patch.object(transport, "AppServer", self.fake_server(instances, barrier=barrier)), \
                patch.object(transport, "collect", side_effect=self.collect_fixture):
            with ThreadPoolExecutor(max_workers=32) as pool:
                responses = list(pool.map(run, range(32)))
        self.assertEqual(len({response.metadata["thread_id"] for response in responses}), 32)
        self.assertEqual(len({server.cwd for server in instances}), 32)
        for server in instances:
            self.assertTrue(server.closed)
            self.assertEqual(server.calls.count("turn/start"), 1)
            self.assertLess(server.calls.index("mcpServerStatus/list"), server.calls.index("turn/start"))
            self.assertEqual(server.overrides, profile.OVERRIDES + profile.PROVIDER_OVERRIDES)
            for key in ("selectedCapabilityRoots", "environments", "runtimeWorkspaceRoots", "dynamicTools"):
                self.assertEqual(server.thread_params[key], [])
            self.assertTrue(server.thread_params["ephemeral"])
            self.assertEqual(server.turn_params["effort"], "medium")
        self.assertTrue(all(response.metadata["complete_body_admission_bytes"] == MAX_BODY_BYTES for response in responses))

    def test_exhausted_included_quota_and_nonempty_inventory_stop_before_generation(self):
        for settings in ({"exhausted": True}, {"bad_inventory": True}):
            instances = []
            adapter = self.adapter()
            with patch.object(transport, "AppServer", self.fake_server(instances, **settings)), \
                    self.assertRaises(DiagnosedProtocolError):
                adapter.generate(SimpleNamespace(key="rejected"), self.request)
            self.assertNotIn("turn/start", instances[0].calls)
            self.assertTrue(instances[0].closed)

    def test_duplicate_identity_never_retries_and_each_call_rechecks_pins(self):
        instances, adapter = [], self.adapter()
        with patch.object(transport, "AppServer", self.fake_server(instances)), \
                patch.object(transport, "collect", side_effect=self.collect_fixture):
            adapter.generate(SimpleNamespace(key="once"), self.request)
            with self.assertRaises(UnknownDispatch):
                adapter.generate(SimpleNamespace(key="once"), self.request)
            self.instructions.write_text("Changed global instructions", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "global instructions changed"):
                adapter.generate(SimpleNamespace(key="changed"), self.request)
        self.assertEqual(len(instances), 1)


if __name__ == "__main__":
    unittest.main()
