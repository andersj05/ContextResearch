"""Bounded-memory full client hashing with the unchanged v7 isolation boundary.

Every constructor and generation still hashes every executable byte. Only the
hash input buffer changes: a reusable 1 MiB block replaces a whole-executable
allocation. Fresh app-server processes/threads, all per-call channel checks,
the one-generation guard, diagnostics and no-retry behavior are inherited.
No hash, account result, process, provider thread or response is shared/cached.
"""
import hashlib
import os
from pathlib import Path

from ..rollback_checkpoint_v7 import client
from ..rollback_pilot.records import digest
from ..rollback_pilot.subscription import profile


HASH_CHUNK_BYTES = 1024 * 1024


def _file_identity(stat):
    # Windows stat() and fstat() expose different ctime semantics; use their
    # common file identity, length and modification timestamp fields here.
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)


def executable_sha256(path):
    """Hash the entire file, using one fixed buffer and rejecting observed drift.

    Metadata checks supplement the full content hash; they never substitute for
    reading the bytes. This detects observed modifications during verification,
    but cannot eliminate the existing check-to-process-launch race.
    """
    path = Path(path)
    digestor = hashlib.sha256()
    block = bytearray(HASH_CHUNK_BYTES)
    view = memoryview(block)
    with path.open("rb", buffering=0) as source:
        before = _file_identity(os.fstat(source.fileno()))
        while count := source.readinto(block):
            digestor.update(view[:count])
        after = _file_identity(os.fstat(source.fileno()))
    if before != after or after != _file_identity(path.stat()):
        raise ValueError("Codex executable changed during verification")
    return digestor.hexdigest()


class Transport(client.Transport):
    transport_id = "codex-chatgpt-subscription-rollback-parallel-v8"

    def check_hashes(self):
        # Keep every historical guard, including full hashes before each call.
        if executable_sha256(self.executable) != self.preflight["executable_sha256"]:
            raise ValueError("Codex executable changed")
        if digest(self.global_instructions.read_text(encoding="utf-8")) != self.preflight["global_instructions_sha256"]:
            raise ValueError("global instructions changed")
        if digest(str(profile.OVERRIDES + profile.PROVIDER_OVERRIDES)) != self.preflight["configuration_sha256"]:
            raise ValueError("isolation profile changed")
        if (self.preflight.get("registry_sha256") != client.REGISTRY_SHA256
                or self.preflight.get("namespace_metadata_sha256") != client.NAMESPACE_SHA256
                or self.preflight.get("mcp_inventory_checked_before_every_generation") is not True):
            raise ValueError("v7 exact-registry preflight required")


def live_factory(executable, global_instructions, checked, scratch_root):
    return lambda: Transport(executable, global_instructions, checked, scratch_root)
