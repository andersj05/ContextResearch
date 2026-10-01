"""Scientific checks of disclosure timing and UTF-8 memory boundaries."""
from copy import deepcopy
import unittest

from experiments.dependency_memory.workflow_intake.views import actor_view, PARENT_CAP, CHILD_CAP


class SerializedViewsTests(unittest.TestCase):
    def setUp(self):
        public = {k: "public" for k in ("check", "snapshot", "run_id", "returncode", "artifacts", "argv", "stdout", "stderr")}
        private = {**public, "expected": "SECRET_LABEL", "seed": "SECRET_SEED", "archive_path": "SECRET_ARCHIVE"}
        self.episode = {"initial": [private], "between": [{**private, "stdout": "later observation"}],
                        "scope": ["tests"], "task": {"snapshot": "final snapshot", "required_checks": ["tests"], "artifacts": {},
                                                         "expected": "SECRET_NESTED_LABEL"},
                        "expected": "SECRET_LABEL", "inspection": "evaluator private metadata"}

    def test_future_observations_and_labels_are_not_disclosed_early(self):
        parent = actor_view(self.episode, "parent")
        child = actor_view(self.episode, "child", "retained parent")
        final = actor_view(self.episode, "final", "retained child")
        self.assertNotIn("later observation", str(parent))
        self.assertNotIn("final snapshot", str(parent) + str(child))
        self.assertNotIn("later observation", str(final))
        for view in (parent, child, final):
            self.assertNotIn("SECRET", str(view))
            self.assertNotIn("evaluator private metadata", str(view))

    def test_memory_limits_count_utf8_bytes(self):
        for stage, cap in (("child", PARENT_CAP), ("final", CHILD_CAP)):
            self.assertIsInstance(actor_view(self.episode, stage, "a" * cap), dict)
            self.assertIsInstance(actor_view(self.episode, stage, "λ" * (cap // 2)), dict)
            with self.assertRaises(ValueError):
                actor_view(self.episode, stage, "λ" * (cap // 2 + 1))

    def test_views_do_not_mutate_source_or_share_state(self):
        original = deepcopy(self.episode)
        view = actor_view(self.episode, "parent")
        view["tool_observations"][0]["check"] = "changed"
        self.assertEqual(self.episode, original)
        self.assertNotEqual(view, actor_view(self.episode, "parent"))

    def test_unknown_stage_and_hidden_memory_are_rejected(self):
        with self.assertRaises(ValueError):
            actor_view(self.episode, "parent", "hidden previous state")
        with self.assertRaises(ValueError):
            actor_view(self.episode, "unknown", "memory")


if __name__ == "__main__":
    unittest.main()
