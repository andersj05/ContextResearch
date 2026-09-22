"""Independent public reconstruction and disclosure checks for frozen fixtures."""
import json
from hashlib import sha256
from pathlib import Path
import unittest

from experiments.dependency_memory.schema_transfer.casebook import terminal
from . import casebook, memory


class CasebookTests(unittest.TestCase):
    def test_development_hashes_and_public_reconstruction(self):
        folder = Path(__file__).parent / "fixtures"
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(4, len(manifest["development"]))
        for item in manifest["development"]:
            path = folder / item["file"]
            self.assertEqual(item["sha256"], sha256(path.read_bytes()).hexdigest())
            case = json.loads(path.read_text(encoding="utf-8"))
            schema, rows = memory.join(case["tool_schemas"], case["tool_results"])
            self.assertEqual(7, len(rows))
            root = next(key for key in ("invoice_id", "package_id") if key in rows[0])
            reconstructed = {row[root]: row for row in rows}
            for future in case["futures"]:
                self.assertEqual(casebook.truth(case, future),
                                 terminal(case["family"], reconstructed[future["target"]], future["event"]))
            public = {key: case[key] for key in ("tool_schemas", "tool_results", "rule")}
            public_text = casebook.compact(public)
            self.assertNotIn("private_truth_rows", public_text)
            self.assertNotIn('"futures"', public_text)

    def test_seed_commit_conditioning(self):
        a = casebook.evaluation_seeds("a" * 40)
        b = casebook.evaluation_seeds("b" * 40)
        self.assertNotEqual(a, b)
        self.assertEqual(set(a), set(casebook.EVAL))
        self.assertTrue(all(len(a[family]) == 4 for family in a))


if __name__ == "__main__":
    unittest.main()
