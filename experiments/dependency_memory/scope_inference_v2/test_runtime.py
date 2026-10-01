"""Cold-directory persistence and pre-generation invariants; no model requests."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.dependency_memory.scope_inference import profile, protocol, transport
from experiments.dependency_memory.scope_inference_v2 import run


class FakeServer:
    generation_starts = 0
    identity = "scope-v2-cold-control"
    directory = None
    instructions = None

    def __init__(self, *args):
        self.notifications = []

    def initialize(self):
        pass

    def rpc(self, method, params):
        if method == "account/read":
            return {"account": {"type": "chatgpt"}}
        if method == "account/rateLimits/read":
            return {}
        if method == "config/read":
            return {"config": {}}
        if method == "thread/start":
            return {"model": profile.MODEL, "modelProvider": "luna_research", "runtimeWorkspaceRoots": [],
                    "thread": {"id": "cold-thread", "turns": [], "environments": []},
                    "instructionSources": [str(self.instructions)]}
        if method == "turn/start":
            path = self.directory / "calls" / (self.identity + ".json")
            saved = json.loads(path.read_text())
            if saved["status"] != "reserved" or saved["dispatched"] is not True or saved["reservation_credits"] != "7.65":
                raise AssertionError("Generation before durable reservation")
            FakeServer.generation_starts += 1
            usage = {"inputTokens": 128, "cachedInputTokens": 0, "outputTokens": 40,
                     "reasoningOutputTokens": 10, "totalTokens": 168}
            self.notifications = [
                {"method": "thread/tokenUsage/updated", "params": {"tokenUsage": {"total": usage}}},
                {"method": "item/completed", "params": {"item": {"type": "agentMessage", "text":
                    json.dumps({"value_paths": ["status"], "presence_paths": [], "nonempty_paths": []})}}},
                {"method": "turn/completed", "params": {"turn": {"id": "cold-turn", "status": "failed",
                    "error": {"codexErrorInfo": "sessionBudgetExceeded"}}}}]
            return {"turn": {"id": "cold-turn"}}
        raise AssertionError("Unexpected RPC " + method)

    def receive(self, *args):
        raise AssertionError("No additional generation or event is allowed")

    def close(self):
        pass


class CorrectedLaunchTests(unittest.TestCase):
    def client(self, root):
        executable, instructions = root / "dummy-executable", root / "AGENTS.md"
        executable.write_bytes(b"local mock; not invoked")
        instructions.write_bytes(b"local public mock instructions")
        FakeServer.directory, FakeServer.instructions = root, instructions.resolve()
        FakeServer.generation_starts = 0
        audit = {"version": "scope_luna6_preflight_v1", "isolation_passed": True, "real_model_generations": 0,
            "cases": [{"payload_audit": {"visible_tool_spec_sha256": profile.VISIBLE_TOOL_SPEC_SHA256,
                       "bootstrap_tool_specification": None}} for _ in range(4)],
            "client_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
            "global_instructions_sha256": hashlib.sha256(instructions.read_bytes()).hexdigest(),
            "profile_sha256": hashlib.sha256(json.dumps(profile.ISOLATION_OVERRIDES).encode()).hexdigest()}
        return transport.Client(executable, instructions, root, audit)

    def transport_mocks(self):
        return (patch.object(transport, "AppServer", FakeServer),
                patch.object(transport, "config_check", lambda config: {"mock_only": True}),
                patch.object(transport, "quota_snapshot", lambda payload: {}),
                patch.object(transport, "check_quota", lambda *args, **kwargs: "included"))

    def test_original_missing_directory_fails_before_generation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            client = self.client(root)
            a, b, c, d = self.transport_mocks()
            with a, b, c, d, self.assertRaises(FileNotFoundError):
                client.complete(FakeServer.identity, protocol.request("concise"))
            self.assertEqual(FakeServer.generation_starts, 0)
            self.assertFalse((root / "calls").exists())

    def test_corrected_cold_directory_saves_reservation_before_generation_and_metering(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            client = self.client(root)
            (root / "calls").mkdir(exist_ok=False)
            a, b, c, d = self.transport_mocks()
            with a, b, c, d:
                answer = client.complete(FakeServer.identity, protocol.request("concise"))
            saved = json.loads((root / "calls" / (FakeServer.identity + ".json")).read_text())
            self.assertEqual(FakeServer.generation_starts, 1)
            self.assertEqual(saved["status"], "completed")
            self.assertEqual(saved["usage_events"], 1)
            self.assertEqual(saved["response"], answer)
            self.assertEqual(saved["planning_credits"], "0.00082")
            self.assertEqual(saved["tool_items"], 0)

    def test_new_local_identities_preserve_every_public_request_byte(self):
        old = run.study.schedule()
        new = run.schedule()
        self.assertEqual({r["identity"] for r in old} & {r["identity"] for r in new}, set())
        self.assertEqual([(r["replicate"], r["variant"]) for r in old], [(r["replicate"], r["variant"]) for r in new])
        for a, b in zip(old, new):
            self.assertEqual(protocol.request_bytes(protocol.request(a["variant"])),
                             protocol.request_bytes(protocol.request(b["variant"])))


if __name__ == "__main__":
    unittest.main()
