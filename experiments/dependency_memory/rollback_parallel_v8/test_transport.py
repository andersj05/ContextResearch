"""Independent buffer, drift and 32-way fresh-session transport checks."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import hashlib
import os
import tempfile
import threading
import tomllib
import unittest
from unittest.mock import patch

from experiments.dependency_memory.rollback_parallel_v8 import transport
from experiments.dependency_memory.rollback_checkpoint_v7 import client
from experiments.dependency_memory.rollback_checkpoint_v7.common import ROOT
from experiments.dependency_memory.rollback_checkpoint_v7.contexts import render
from experiments.dependency_memory.rollback_checkpoint_v7.engine import initial_state
from experiments.dependency_memory.rollback_checkpoint_v7.prepare import generate
from experiments.dependency_memory.rollback_pilot.records import digest
from experiments.dependency_memory.rollback_pilot.subscription import profile
from experiments.dependency_memory.rollback_pilot.subscription.accounting import Usage
from experiments.dependency_memory.rollback_pilot.subscription.transport import Response
from experiments.dependency_memory.rollback_pilot.transport import UnknownDispatch
from experiments.dependency_memory.rollback_math_followup_v4.observe import DiagnosedProtocolError


def empty_inventory():
    return {"data": [{"name": "node_repl", "runtimeStatus": "disabled",
                      "tools": {}, "resources": [], "resourceTemplates": []}],
            "nextCursor": None}


class StreamingTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        task = generate(split="fixture", replicates=1)[0]
        cls.request = render(task, initial_state(task))

    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="rollback-v8-transport-", dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.instructions = self.folder / "AGENTS.md"
        self.instructions.write_text("Synthetic global instructions.\n", encoding="utf-8")
        self.executable = self.folder / "fixture-client.exe"
        # Different values around block boundaries expose skipped/reused chunks.
        self.executable.write_bytes(b"a" * transport.HASH_CHUNK_BYTES +
                                    b"b" * transport.HASH_CHUNK_BYTES + b"last block")
        self.checked = {
            "serialization_and_retry_audit_passed": True,
            "executable_sha256": digest(self.executable.read_bytes()),
            "global_instructions_sha256": digest(self.instructions.read_text(encoding="utf-8")),
            "configuration_sha256": digest(str(profile.OVERRIDES + profile.PROVIDER_OVERRIDES)),
            "registry_sha256": client.REGISTRY_SHA256,
            "namespace_metadata_sha256": client.NAMESPACE_SHA256,
            "mcp_inventory_checked_before_every_generation": True,
        }

    def adapter(self, checked=None):
        return transport.Transport(self.executable, self.instructions,
                                   self.checked if checked is None else checked,
                                   self.folder / "scratch")

    def test_streamed_digest_matches_independent_sha_and_uses_one_bounded_buffer(self):
        expected = hashlib.sha256(self.executable.read_bytes()).hexdigest()
        opened, read_sizes, buffers = [], [], []
        original_open = Path.open

        class Reader:
            def __init__(inner, source):
                inner.source = source

            def __enter__(inner):
                return inner

            def __exit__(inner, *args):
                inner.source.close()

            def fileno(inner):
                return inner.source.fileno()

            def readinto(inner, block):
                read_sizes.append(len(block))
                buffers.append(id(block))
                return inner.source.readinto(block)

        def open_reader(path, *args, **kwargs):
            opened.append((path, args, kwargs))
            return Reader(original_open(path, *args, **kwargs))

        with patch.object(Path, "open", open_reader), \
                patch.object(Path, "read_bytes", side_effect=AssertionError("whole-file allocation")):
            observed = transport.executable_sha256(self.executable)
        self.assertEqual(observed, expected)
        self.assertEqual(len(opened), 1)
        self.assertEqual(opened[0][2]["buffering"], 0)
        self.assertGreaterEqual(len(read_sizes), 4)  # 3 chunks followed by EOF.
        self.assertEqual(set(read_sizes), {transport.HASH_CHUNK_BYTES})
        self.assertEqual(len(set(buffers)), 1)

    def test_empty_exact_multiple_and_tail_files_hash_every_byte(self):
        for size in (0, 1, transport.HASH_CHUNK_BYTES,
                     transport.HASH_CHUNK_BYTES + 1):
            with self.subTest(size=size):
                data = b"z" * size
                self.executable.write_bytes(data)
                self.assertEqual(transport.executable_sha256(self.executable),
                                 hashlib.sha256(data).hexdigest())

    def test_observed_file_change_during_hash_is_rejected(self):
        before = self.executable.stat()
        changed = SimpleNamespace(st_dev=before.st_dev, st_ino=before.st_ino,
                                  st_size=before.st_size, st_mtime_ns=before.st_mtime_ns + 1,
                                  st_ctime_ns=before.st_ctime_ns)
        with patch.object(transport.os, "fstat", side_effect=[before, changed]), \
                self.assertRaisesRegex(ValueError, "changed during verification"):
            transport.executable_sha256(self.executable)

    def test_same_size_change_with_restored_mtime_is_rehashed_and_rejected(self):
        adapter = self.adapter()
        stamp = self.executable.stat()
        with self.executable.open("r+b") as source:
            source.seek(transport.HASH_CHUNK_BYTES + 5)
            source.write(b"c")
        os.utime(self.executable, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        with self.assertRaisesRegex(ValueError, "Codex executable changed"):
            adapter.check_hashes()

    def test_all_client_instruction_configuration_and_registry_pins_remain(self):
        self.adapter().check_hashes()
        for field in ("executable_sha256", "global_instructions_sha256", "configuration_sha256",
                      "registry_sha256", "namespace_metadata_sha256",
                      "mcp_inventory_checked_before_every_generation"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.adapter({**self.checked, field: "changed"})

    def fake_server(self, instances, *, barrier=None, bad_inventory=False):
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
                        "primary": {"usedPercent": 1}, "secondary": None,
                        "spendControlReached": False, "rateLimitReachedType": None}}}
                if method == "config/read":
                    return {"config": tomllib.loads("\n".join(profile.OVERRIDES + profile.PROVIDER_OVERRIDES))}
                if method == "thread/start":
                    inner.thread_params = deepcopy(params)
                    return {"model": profile.MODEL, "modelProvider": profile.PROVIDER,
                            "runtimeWorkspaceRoots": [], "instructionSources": [instructions],
                            "thread": {"id": "v8-fresh-" + str(inner.index),
                                       "turns": [], "environments": []}}
                if method == "mcpServerStatus/list":
                    if barrier is not None:
                        barrier.wait(timeout=20)
                    inventory = empty_inventory()
                    if bad_inventory:
                        inventory["data"][0]["resources"] = [{"uri": "fixture://forbidden"}]
                    return inventory
                if method == "turn/start":
                    inner.turn_params = deepcopy(params)
                    return {"turn": {"id": "v8-turn-" + str(inner.index)}}
                raise AssertionError("unexpected RPC: " + method)

            def close(inner):
                inner.closed = True

        return Server

    @staticmethod
    def collect_fixture(*args, **kwargs):
        return Response('{"fixture":true}', Usage(1, 0, 1, 0), {
            "model": profile.MODEL, "usage_events": 1, "tool_items": 0,
            "harness_termination": "sessionBudgetExceeded"})

    def test_32_transports_keep_distinct_sessions_and_full_checks(self):
        instances, barrier = [], threading.Barrier(32)
        factory = transport.live_factory(self.executable, self.instructions,
                                         self.checked, self.folder / "scratch")
        original_hash = transport.executable_sha256

        def execute(index):
            return factory().generate(SimpleNamespace(key="parallel-" + str(index)), self.request)

        with patch.object(client, "AppServer", self.fake_server(instances, barrier=barrier)), \
                patch.object(client, "collect", side_effect=self.collect_fixture), \
                patch.object(transport, "executable_sha256", wraps=original_hash) as hasher:
            with ThreadPoolExecutor(max_workers=32) as pool:
                responses = list(pool.map(execute, range(32)))
        self.assertEqual(hasher.call_count, 64)  # Constructor and generation, no cache.
        self.assertEqual(len({response.metadata["thread_id"] for response in responses}), 32)
        self.assertEqual(len({server.cwd for server in instances}), 32)
        self.assertTrue(all(server.closed and server.calls.count("turn/start") == 1
                            for server in instances))
        for server in instances:
            self.assertLess(server.calls.index("mcpServerStatus/list"), server.calls.index("turn/start"))
            self.assertEqual(server.overrides, profile.OVERRIDES + profile.PROVIDER_OVERRIDES)
            for key in ("selectedCapabilityRoots", "environments", "runtimeWorkspaceRoots", "dynamicTools"):
                self.assertEqual(server.thread_params[key], [])
            self.assertTrue(server.thread_params["ephemeral"])
            self.assertEqual(server.turn_params["effort"], "medium")

    def test_unchanged_generation_checks_each_time_closes_and_never_retries(self):
        self.assertIs(transport.Transport.generate, client.Transport.generate)
        instances, adapter = [], self.adapter()
        original_hash = transport.executable_sha256
        with patch.object(client, "AppServer", self.fake_server(instances)), \
                patch.object(client, "collect", side_effect=self.collect_fixture), \
                patch.object(transport, "executable_sha256", wraps=original_hash) as hasher:
            for name in ("first", "second"):
                adapter.generate(SimpleNamespace(key=name), self.request)
            with self.assertRaises(UnknownDispatch):
                adapter.generate(SimpleNamespace(key="first"), self.request)
        self.assertEqual(hasher.call_count, 2)
        self.assertEqual(len(instances), 2)
        self.assertTrue(all(server.closed for server in instances))
        with patch.object(client, "AppServer", self.fake_server(instances, bad_inventory=True)), \
                patch.object(client, "collect", side_effect=self.collect_fixture):
            with self.assertRaises(DiagnosedProtocolError):
                adapter.generate(SimpleNamespace(key="third"), self.request)
        self.assertNotIn("turn/start", instances[-1].calls)
        self.assertTrue(instances[-1].closed)


if __name__ == "__main__":
    unittest.main()
