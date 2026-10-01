from copy import deepcopy
from itertools import combinations
import unittest

from experiments.dependency_memory import scope_codebook_control as control
from experiments.dependency_memory.workflow_replay import evidence
from experiments.dependency_memory.scope_inference import codec


class ExistingCodebookTests(unittest.TestCase):
    def test_packed_public_schema_survives_both_caps_and_all_late_queries(self):
        records, _ = evidence.load_snapshot()
        original = evidence.historical_classifier()
        parent, admitted = codec.admit(control.encode_rows(records), codec.PARENT_CAP)
        self.assertFalse(admitted["infeasible"])
        queries = 0
        for workers in combinations(range(4), 2):
            child, admission = codec.admit(control.child_rows(parent, workers), codec.CHILD_CAP)
            self.assertFalse(admission["infeasible"])
            for row in records:
                if row["worker"] in workers:
                    self.assertEqual(control.readout(child, row["case_id"], row["request_sha256"], original),
                                     evidence.original_decision(row, original))
                    queries += 1
        self.assertEqual(queries, 24)

    def test_no_parent_or_wrong_request_identity_cannot_recover(self):
        records, _ = evidence.load_snapshot()
        original = evidence.historical_classifier()
        self.assertEqual(control.child_rows("", (0, 1)), [])
        parent, _ = codec.admit(control.encode_rows(records), codec.PARENT_CAP)
        child, _ = codec.admit(control.child_rows(parent, (0, 1)), codec.CHILD_CAP)
        self.assertEqual(control.readout(child, records[0]["case_id"], "0" * 64, original), ["unknown", None, None])

    def test_codec_roundtrip_preserves_absence_and_nonempty_unknown_metadata(self):
        original = evidence.historical_classifier()
        base = {"status": "transport_failure", "error_type": "StudyStopped", "provider_metadata": {}}
        for metadata in ({}, {"unknown": 1}, {"dispatched": False}, {"dispatched": False, "usage": None}):
            row = {**base, "provider_metadata": deepcopy(metadata)}
            decoded = evidence.decode_fields(evidence.encode_fields(evidence.project(row)))
            self.assertEqual(evidence.original_decision(decoded, original), evidence.original_decision(row, original))


if __name__ == "__main__":
    unittest.main()
