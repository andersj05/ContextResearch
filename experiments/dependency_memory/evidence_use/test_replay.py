"""Ledger conservation and counterfactual-readout limits on saved evidence."""
import json
import unittest

from experiments.dependency_memory.evidence_use import replay


class RetrospectiveReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = replay.analyze()

    def test_missing_outcomes_cannot_be_repaired_by_replay(self):
        rows = self.result["decisions"]
        self.assertEqual(len(rows), 8 * 36 + 5 * 4 + 5 * 12)
        self.assertEqual(len({(r["study"], r["identity"]) for r in rows}), len(rows))
        for row in rows:
            if row["status"] != "observed":
                self.assertIsNone(row["correct"])
                self.assertIsNone(row["guard"])
                self.assertIsNone(row["derived_exact"])
        self.assertEqual(sum(r["status"] == "missing_transport" for r in rows), 3)
        self.assertEqual(sum(r["status"] == "not_dispatched" for r in rows), 46)
        self.assertEqual(self.result["new_model_calls"], 0)
        self.assertIn("unassessable", self.result["historical_primary_status"]["workflow_executed"])

    def test_vetoes_and_readout_are_separate_from_task_success(self):
        rows = [r for r in self.result["decisions"] if r["status"] == "observed"]
        self.assertEqual(len(rows), 319)
        self.assertTrue(any(r["correct"] and r["guard"]["status"] == "uncheckable" for r in rows))
        self.assertTrue(any(not r["correct"] and r["guard"]["status"] == "contradicted" and r["derived_exact"] is False for r in rows))
        self.assertTrue(all(r["guard"]["source_complete_certified"] is False for r in rows))
        for row in rows:
            readout = row["guard"]["derived_answer"]
            if readout is not None:
                self.assertEqual(row["derived_exact"], readout == row["expected"])
        wrong = next(r for r in rows if r["identity"] == "retry_queue-215957210-0-structured")
        self.assertEqual(wrong["first_observed_readout_disagreement"], "by_first_boundary")

    def test_minimized_witnesses_preserve_original_diagnostic(self):
        inputs, _ = replay.observations()
        output = replay.witnesses(inputs)
        self.assertEqual(len(output["witnesses"]), 4)
        self.assertTrue(all(w["reduced_memory_bytes"] <= w["original_memory_bytes"] for w in output["witnesses"]))
        self.assertTrue(any(w["guard"]["derived_answer"] != w["evaluator_only_expected"] for w in output["witnesses"]))


if __name__ == "__main__":
    unittest.main()
