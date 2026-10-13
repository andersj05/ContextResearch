"""Offline isolation regressions for the v7-only installed-client adapter."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import threading
import tomllib
import unittest
from unittest.mock import patch

from experiments.dependency_memory.rollback_checkpoint_v7 import client
from experiments.dependency_memory.rollback_checkpoint_v7.common import ROOT
from experiments.dependency_memory.rollback_checkpoint_v7.contexts import render
from experiments.dependency_memory.rollback_checkpoint_v7.engine import initial_state
from experiments.dependency_memory.rollback_checkpoint_v7.prepare import generate
from experiments.dependency_memory.rollback_pilot.records import digest, wire
from experiments.dependency_memory.rollback_pilot.subscription import profile
from experiments.dependency_memory.rollback_pilot.subscription.process import ProtocolError
from experiments.dependency_memory.rollback_pilot.subscription.transport import Response
from experiments.dependency_memory.rollback_pilot.subscription.accounting import Usage
from experiments.dependency_memory.rollback_pilot.transport import UnknownDispatch
from experiments.dependency_memory.rollback_math_followup_v4.observe import DiagnosedProtocolError


def config_fixture():
    return tomllib.loads("\n".join(profile.OVERRIDES + profile.PROVIDER_OVERRIDES))


def inventory_fixture():
    return {"data": [{"name": "node_repl", "runtimeStatus": "disabled", "tools": {},
                      "resources": [], "resourceTemplates": []}], "nextCursor": None}


def payload_fixture(request, global_text):
    # Synthetic public declarations keep tests independent of machine-local
    # captures. Only this test's fixture hashes are patched, never live pins.
    direct = ("exec", "request_user_input", "request_user_input_async", "wait")
    names = {"clock": {"functions": {"curr_time": {"name": "curr_time"}}},
             "functions": {"functions": {name: {"name": name}
                                            for name in (*direct, *client.RESOURCE_HELPERS)}}}
    embedded = [{"name": "functions", "tools": [
        {"name": name, "description": "Synthetic declaration " + name} for name in direct]}]
    texts = [("developer", profile.BASE), ("developer", profile.DEVELOPER),
             ("user", "# AGENTS.md instructions\n\n<INSTRUCTIONS>\n" + global_text.strip() + "\n</INSTRUCTIONS>"),
             ("user", request.json_text), ("developer", profile.GUARD)]
    body = {"model": profile.MODEL, "reasoning": {"effort": "medium", "context": "all_turns"},
            "store": False, "stream": True,
            "input": [{"type": "message", "role": role,
                       "content": [{"type": "input_text", "text": text}]} for role, text in texts],
            "client_metadata": {"x-codex-turn-metadata": wire({"model": profile.MODEL,
                                "reasoning_effort": "medium", "tool_namespaces_info": names})},
            "text": {"format": {"type": "json_schema", "schema": profile.output_schema(request)}}}
    body["input"].append({"type": "additional_tools", "role": "developer", "tools": embedded})
    return body, names, embedded


class ClientIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.task = generate(split="fixture", replicates=1)[0]
        cls.request = render(cls.task, initial_state(cls.task))

    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="rollback-v7-client-test-", dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.instructions = self.folder / "AGENTS.md"
        self.instructions.write_text("Synthetic global instructions.", encoding="utf-8")
        self.executable = self.folder / "fixture-client.exe"
        self.executable.write_bytes(b"Synthetic executable fixture; never run.")
        self.checked = {"serialization_and_retry_audit_passed": True,
                        "executable_sha256": digest(self.executable.read_bytes()),
                        "global_instructions_sha256": digest(self.instructions.read_text(encoding="utf-8")),
                        "configuration_sha256": digest(str(profile.OVERRIDES + profile.PROVIDER_OVERRIDES)),
                        "registry_sha256": client.REGISTRY_SHA256,
                        "namespace_metadata_sha256": client.NAMESPACE_SHA256,
                        "mcp_inventory_checked_before_every_generation": True}

    def transport(self, checked=None):
        return client.Transport(self.executable, self.instructions,
                                self.checked if checked is None else checked, self.folder / "scratch")

    def payload(self):
        global_text = self.instructions.read_text(encoding="utf-8")
        body, names, embedded = payload_fixture(self.request, global_text)
        stack = ExitStack()
        stack.enter_context(patch.object(client, "REGISTRY_SHA256", digest(wire(embedded))))
        stack.enter_context(patch.object(client, "NAMESPACE_SHA256", digest(wire(names))))
        self.addCleanup(stack.close)
        return body, global_text

    def test_exact_registry_adapter_preserves_sent_body_and_original_bytes(self):
        body, global_text = self.payload()
        original = deepcopy(body)
        result = client.audit_payload(body, self.request, global_text)
        self.assertEqual(body, original)
        self.assertEqual(result["actual_complete_body_bytes"], len(wire(original).encode("utf-8")))
        self.assertEqual(result["complete_body_bytes_observed"], result["actual_complete_body_bytes"])
        self.assertTrue(set(client.RESOURCE_HELPERS).issubset(result["registry_names"]["functions"]))
        # The original historical auditor must continue rejecting this metadata.
        with self.assertRaisesRegex(ValueError, "unexpected nested information tool"):
            profile.audit_payload(body, self.request, global_text)

    def test_even_same_name_declaration_changes_fail_exact_pin(self):
        body, global_text = self.payload()
        changed = deepcopy(body)
        changed["input"][-1]["tools"][0]["tools"][0]["description"] += " hidden access"
        with self.assertRaisesRegex(ValueError, "unrecognized v7 tool registry"):
            client.audit_payload(changed, self.request, global_text)
        for helper in client.RESOURCE_HELPERS:
            with self.subTest(helper=helper):
                changed = deepcopy(body)
                metadata = client.strict_loads(changed["client_metadata"]["x-codex-turn-metadata"])
                metadata["tool_namespaces_info"]["functions"]["functions"][helper]["extra"] = True
                changed["client_metadata"]["x-codex-turn-metadata"] = wire(metadata)
                with self.assertRaisesRegex(ValueError, "unrecognized v7 tool registry"):
                    client.audit_payload(changed, self.request, global_text)

    def test_legacy_history_tools_model_and_schema_rejections_still_apply(self):
        body, global_text = self.payload()
        mutations = []
        for key, value in (("tools", []), ("previous_response_id", "hidden"), ("model", "other")):
            row = deepcopy(body)
            row[key] = value
            mutations.append(row)
        row = deepcopy(body)
        row["input"].append({"type": "message", "role": "assistant", "content": []})
        mutations.append(row)
        row = deepcopy(body)
        row["input"][2]["content"][0]["text"] += "\nExtra environment state"
        mutations.append(row)
        row = deepcopy(body)
        row["text"]["format"]["schema"] = {}
        mutations.append(row)
        row = deepcopy(body)
        row["reasoning"]["effort"] = "high"
        mutations.append(row)
        for index, changed in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(ValueError):
                client.audit_payload(changed, self.request, global_text)

    def test_original_metadata_cannot_disappear_from_byte_limit(self):
        body, global_text = self.payload()
        full = len(wire(body).encode("utf-8"))
        variable = len(wire(self.request.json_text).encode("utf-8")) + len(wire(profile.output_schema(self.request)).encode("utf-8"))
        # The diagnostic normalization removes several metadata entries. A cap
        # just below the original size would pass if only normalized bytes count.
        with patch.object(profile, "FIXED_BYTES", full - variable - 1):
            with self.assertRaisesRegex(ValueError, "original byte bound"):
                client.audit_payload(body, self.request, global_text)

    def test_configuration_requires_inherited_contract_and_only_disabled_server(self):
        checked = client.check_config(config_fixture())
        self.assertTrue(checked["all_configured_mcp_servers_disabled"])
        for change in ("enable", "additional_disabled", "remove", "history", "routing"):
            config = config_fixture()
            if change == "enable":
                config["mcp_servers"]["node_repl"]["enabled"] = True
            elif change == "additional_disabled":
                config["mcp_servers"]["extra"] = {"enabled": False}
            elif change == "remove":
                config["mcp_servers"] = {}
            elif change == "history":
                config["history"]["persistence"] = "save-all"
            else:
                config["model_providers"][profile.PROVIDER]["base_url"] = "https://unapproved.invalid"
            with self.subTest(change=change), self.assertRaises((ValueError, ProtocolError)):
                client.check_config(config)

    def test_inventory_requires_complete_explicit_empty_disabled_result(self):
        result = client.check_mcp_inventory(inventory_fixture())
        self.assertEqual(result, {"server_count": 1, "disabled_server_count": 1,
                                  "tool_count": 0, "resource_count": 0,
                                  "resource_template_count": 0, "complete_inventory": True})
        values = [{"data": inventory_fixture()["data"]}, {"data": [], "nextCursor": None},
                  {"data": [None], "nextCursor": None}, {"data": ["node_repl"], "nextCursor": None}]
        for key, value in (("runtimeStatus", "connected"), ("tools", {"one": {}}),
                           ("resources", [{}]), ("resourceTemplates", [{}]), ("name", "extra")):
            row = inventory_fixture()
            row["data"][0][key] = value
            values.append(row)
        row = inventory_fixture()
        row["nextCursor"] = "more"
        values.append(row)
        row = inventory_fixture()
        row["data"].append(deepcopy(row["data"][0]))
        values.append(row)
        for index, value in enumerate(values):
            with self.subTest(index=index), self.assertRaises(ProtocolError):
                client.check_mcp_inventory(value)

    def test_resource_negative_probe_requires_specific_failure_and_observed_item(self):
        valid = {"item_counts": {"userMessage": 2, "mcpToolCall": 2}}
        client.check_tool_rejection("tool_or_external_information_attempt", valid)
        for reason, observation in (("single_answer_and_usage_required", valid),
                                     ("generation_timeout", valid),
                                     ("tool_or_external_information_attempt", {"item_counts": {"userMessage": 2}})):
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, "did not verify tool rejection"):
                client.check_tool_rejection(reason, observation)

    def test_transport_binds_client_config_instructions_and_registry_preflight(self):
        self.transport().check_hashes()
        for field in ("executable_sha256", "global_instructions_sha256", "configuration_sha256",
                      "registry_sha256", "namespace_metadata_sha256", "mcp_inventory_checked_before_every_generation"):
            checked = {**self.checked, field: "changed"}
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.transport(checked)

    def fake_server(self, instances, *, inventory=None, barrier=None):
        instructions = str(self.instructions)
        lock = threading.Lock()

        class Server:
            def __init__(inner, executable, cwd, overrides):
                with lock:
                    inner.index = len(instances)
                    instances.append(inner)
                inner.cwd, inner.overrides, inner.calls = cwd, overrides, []
                inner.closed = False

            def initialize(inner):
                inner.calls.append("initialize")

            def rpc(inner, method, params):
                inner.calls.append(method)
                if method == "account/read":
                    return {"account": {"type": "chatgpt"}}
                if method == "account/rateLimits/read":
                    return {"ordinaryUsageAllowed": True, "rateLimitsByLimitId": {"codex": {
                        "primary": {"usedPercent": 1}, "secondary": None,
                        "spendControlReached": False, "rateLimitReachedType": None}}}
                if method == "config/read":
                    return {"config": config_fixture()}
                if method == "model/list":
                    return {"data": [{"model": profile.MODEL,
                                      "supportedReasoningEfforts": [{"reasoningEffort": "medium"}]}]}
                if method == "thread/start":
                    inner.thread_params = deepcopy(params)
                    return {"model": profile.MODEL, "modelProvider": profile.PROVIDER,
                            "runtimeWorkspaceRoots": [], "instructionSources": [instructions],
                            "thread": {"id": "fresh-" + str(inner.index), "turns": [], "environments": []}}
                if method == "mcpServerStatus/list":
                    if barrier is not None:
                        barrier.wait(timeout=10)
                    return inventory_fixture() if inventory is None else inventory
                if method == "turn/start":
                    inner.turn_params = deepcopy(params)
                    return {"turn": {"id": "turn-" + str(inner.index)}}
                raise AssertionError("unexpected RPC: " + method)

            def close(inner):
                inner.closed = True

        return Server

    @staticmethod
    def fixture_collect(*args, **kwargs):
        return Response('{"fixture":true}', Usage(1, 0, 1, 0), {
            "model": profile.MODEL, "usage_events": 1, "tool_items": 0,
            "harness_termination": "sessionBudgetExceeded"})

    def test_live_transport_checks_inventory_before_turn_and_rejects_bad_inventory(self):
        instances = []
        transport = self.transport()
        with patch.object(client, "AppServer", self.fake_server(instances)), \
                patch.object(client, "collect", side_effect=self.fixture_collect):
            result = transport.generate(SimpleNamespace(key="first"), self.request)
            with self.assertRaises(UnknownDispatch):
                transport.generate(SimpleNamespace(key="first"), self.request)
        self.assertEqual(len(instances), 1)
        self.assertLess(instances[0].calls.index("mcpServerStatus/list"), instances[0].calls.index("turn/start"))
        self.assertTrue(instances[0].closed)
        self.assertEqual(result.metadata["mcp_resource_isolation"], client.check_mcp_inventory(inventory_fixture()))
        bad = inventory_fixture()
        bad["data"][0]["resources"] = [{"uri": "fixture://forbidden"}]
        with patch.object(client, "AppServer", self.fake_server(instances, inventory=bad)), \
                patch.object(client, "collect", side_effect=self.fixture_collect):
            with self.assertRaises(DiagnosedProtocolError) as caught:
                self.transport().generate(SimpleNamespace(key="second"), self.request)
        self.assertEqual(caught.exception.diagnostic["reason_code"], "unexpected_workspace_or_prior_state")
        self.assertNotIn("turn/start", instances[-1].calls)
        self.assertTrue(instances[-1].closed)

    def test_eight_transports_preserve_fresh_isolation_without_historical_global_mutation(self):
        instances, barrier = [], threading.Barrier(8)
        original = (profile.OVERRIDES, profile.PROVIDER_OVERRIDES, profile.audit_payload, profile.check_config)
        factory = client.live_factory(self.executable, self.instructions, self.checked, self.folder / "scratch")

        def execute(index):
            return factory().generate(SimpleNamespace(key="parallel-" + str(index)), self.request)

        with patch.object(client, "AppServer", self.fake_server(instances, barrier=barrier)), \
                patch.object(client, "collect", side_effect=self.fixture_collect):
            with ThreadPoolExecutor(max_workers=8) as pool:
                responses = list(pool.map(execute, range(8)))
        self.assertEqual(original, (profile.OVERRIDES, profile.PROVIDER_OVERRIDES, profile.audit_payload, profile.check_config))
        self.assertEqual(len({result.metadata["thread_id"] for result in responses}), 8)
        self.assertEqual(len({server.cwd for server in instances}), 8)
        self.assertTrue(all(server.closed and server.calls.count("turn/start") == 1 for server in instances))
        for server in instances:
            self.assertEqual(server.overrides, original[0] + original[1])
            self.assertEqual(server.thread_params["selectedCapabilityRoots"], [])
            self.assertEqual(server.thread_params["environments"], [])
            self.assertEqual(server.thread_params["runtimeWorkspaceRoots"], [])
            self.assertEqual(server.thread_params["dynamicTools"], [])
            self.assertTrue(server.thread_params["ephemeral"])
            self.assertEqual(server.turn_params["effort"], "medium")

    def test_preflight_requires_composite_diagnostic_separate_from_negative_successes(self):
        instances, observed = [], []

        def loopback(executable, text, request, case, scratch):
            observed.append(case)
            return {"case": case, "diagnostic_only": case in client.DIAGNOSTIC_CASES,
                    "accepted_transport": case in {"final_message", "clock_with_answer"},
                    "real_model_generations": 0}

        with patch.object(client, "AppServer", self.fake_server(instances)), \
                patch.object(client.subprocess, "run", return_value=SimpleNamespace(stdout="fixture-client\n")), \
                patch.object(client, "run_case", side_effect=loopback):
            result = client.preflight(self.executable, self.instructions, self.folder / "scratch")
        self.assertEqual(observed, [*client.CASES, "clock_with_answer"])
        self.assertNotIn("clock_with_answer", [row["case"] for row in result["cases"]])
        self.assertEqual(result["compatibility_diagnostics"], [{
            "case": "clock_with_answer", "diagnostic_only": True,
            "accepted_transport": True, "real_model_generations": 0}])


if __name__ == "__main__":
    unittest.main()
