"""Frozen repeated-prompt identities and missingness in throughput diagnostics."""
import unittest

from experiments.dependency_memory.rollback_parallel_v8.live_benchmark import plan, analyze, COUNTS
from experiments.dependency_memory.rollback_parallel_v8.prepare import generate


class ProbeTests(unittest.TestCase):
    def test_four_batches_repeat_same_prompts_without_repeating_an_identity(self):
        tasks = generate(replicates=16)
        frozen = plan({"model": "gpt-6-luna", "effort": "medium", "source_bindings": []}, tasks)
        rows = frozen["schedule"]
        self.assertEqual(len(rows), 64)
        self.assertEqual(len({row["call_id"] for row in rows}), 64)
        for task in tasks:
            selected = [row for row in rows if row["identity"]["task_id"] == task["task_id"]]
            self.assertEqual(len({row["request_hash"] for row in selected}), 1)
            self.assertEqual([row["workers"] for row in selected], list(COUNTS))
        self.assertEqual(frozen["generation_ceiling"], 64)

    def test_incomplete_batches_cannot_claim_a_speed_ratio(self):
        batches = [{"batch": i, "workers": workers, "wall_seconds": 10.0,
                    "dispositions": []} for i, workers in enumerate(COUNTS)]
        result = analyze([], batches)
        self.assertFalse(result["all_64_calls_known"])
        self.assertIsNone(result["descriptive_16_vs_8_speed_ratio"])
        self.assertEqual(sum(row["never_admitted_calls"] for row in result["batches"]), 64)


if __name__ == "__main__":
    unittest.main()
