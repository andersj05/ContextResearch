"""Development-only dry runs of stage ordering and fail-closed fallback."""
from pathlib import Path
from decimal import Decimal
import tempfile
import unittest

from .casebook import DEV_SEEDS, make_case
from .memory import project
from .run import memory_request, prepare_memories
from luna6_revision.protocol import request_bytes


class FakeClient:
    def __init__(self, parent):
        self.parent = parent
        self.requests = []
        self.attempts = 0
        self.spent = Decimal(0)

    def complete(self, identity, request):
        self.attempts += 1
        self.requests.append((identity, request))
        return {"memory": self.parent if identity.endswith("parent") else "unstructured child"}


class RunnerDevelopmentTests(unittest.TestCase):
    def test_failure_replacement_uses_only_bounded_parent_at_child(self):
        case = make_case("escrow", DEV_SEEDS[0], "development")
        for proposed_parent, fallback in (("unstructured parent", True),
                                          (project(case["tool_schema"], case["tool_results"])[0], False)):
            client = FakeClient(proposed_parent)
            with tempfile.TemporaryDirectory() as folder:
                episode = prepare_memories(client, case, Path(folder))
            self.assertEqual(len(client.requests), 3)
            self.assertEqual([request["stage"] for _, request in client.requests], ["parent", "child", "child"])
            self.assertEqual(episode["checks"]["parent_fallback"], fallback)
            self.assertTrue(episode["checks"]["child_fallback"])
            self.assertEqual(episode["memories"]["checked"]["child"],
                             episode["memories"]["automatic"]["child"])
            self.assertNotIn("tool_results", client.requests[2][1]["observation"])
            self.assertLessEqual(len(episode["memories"]["checked"]["child"].encode()), 1050)

    def test_development_public_parent_request_fits_transport_cap(self):
        case = make_case("package", DEV_SEEDS[0], "development")
        request_bytes(memory_request(case, "parent", {"tool_schema": case["tool_schema"],
            "tool_results": case["tool_results"]}, 3000))


if __name__ == "__main__":
    unittest.main()
