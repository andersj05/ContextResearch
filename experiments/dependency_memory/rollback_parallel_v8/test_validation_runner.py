"""Small synthetic suites verify complete parallel unittest accounting."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/run_offline_tests_parallel.py"


class ParallelValidationTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="validation-runner-test-", dir=ROOT / "tmp")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.suite = self.folder / "synthetic_suite"
        self.suite.mkdir()
        (self.suite / "__init__.py").write_text("", encoding="utf-8")

    def module(self, name, content):
        (self.suite / (name + ".py")).write_text(content, encoding="utf-8")

    def run_suite(self, *, workers=2):
        output = self.folder / "report"
        process = subprocess.run([sys.executable, str(SCRIPT), "--output", str(output),
                                  "--workers", str(workers), "--start-directory", str(self.suite),
                                  "--top-level-directory", str(self.folder)],
                                 capture_output=True, text=True,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        return process, summary, manifest

    def test_all_ids_run_once_with_independent_process_temp_roots_and_skips(self):
        content = '''import os,tempfile,unittest
class Example(unittest.TestCase):
    def test_temp(self):
        self.assertEqual(os.path.realpath(tempfile.gettempdir()), os.path.realpath(os.environ['TMPDIR']))
        with open(os.path.join(tempfile.gettempdir(),'fixed-name.txt'),'x') as output:
            output.write('module-local')
    @unittest.skip('fixture optional capability')
    def test_skip(self): pass
'''
        self.module("test_one", content)
        self.module("test_two", content)
        process, summary, manifest = self.run_suite()
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertTrue(summary["all_passed"])
        self.assertTrue(summary["coverage_passed"])
        self.assertEqual(summary["discovered_test_count"], 4)
        self.assertEqual(summary["terminal_test_count"], 4)
        self.assertEqual(summary["outcomes"], {"passed": 2, "skipped": 2})
        self.assertEqual(len({row["process_id"] for row in summary["modules"]}), 2)
        self.assertEqual(len({job["temporary_directory"] for job in manifest["jobs"]}), 2)
        self.assertEqual(summary["retries"], 0)

    def test_failure_error_and_fixture_skip_are_complete_but_not_green(self):
        self.module("test_cases", '''import unittest
class Cases(unittest.TestCase):
    def test_fail(self): self.assertEqual(1,2)
    def test_error(self): raise ValueError('fixture error')
    def test_subtest(self):
        with self.subTest(value=1): self.assertFalse(True)
class Skipped(unittest.TestCase):
    @classmethod
    def setUpClass(cls): raise unittest.SkipTest('fixture class unavailable')
    def test_one(self): pass
    def test_two(self): pass
''')
        self.module("test_pass", '''import unittest
class Pass(unittest.TestCase):
    def test_independent(self): self.assertTrue(True)
''')
        process, summary, _ = self.run_suite()
        self.assertEqual(process.returncode, 1)
        self.assertFalse(summary["all_passed"])
        self.assertTrue(summary["coverage_passed"])
        self.assertEqual(summary["terminal_test_count"], 6)
        self.assertEqual(summary["outcomes"], {"failed": 2, "error": 1,
                                               "passed": 1, "skipped_fixture": 2})
        self.assertEqual(summary["failures"], 2)
        self.assertEqual(summary["errors"], 1)

    def test_fixture_error_covers_blocked_tests_without_pretending_they_ran(self):
        self.module("test_broken", '''import unittest
def setUpModule(): raise RuntimeError('fixture setup failed')
class Blocked(unittest.TestCase):
    def test_one(self): pass
    def test_two(self): pass
''')
        process, summary, _ = self.run_suite()
        self.assertEqual(process.returncode, 1)
        self.assertTrue(summary["coverage_passed"])
        self.assertEqual(summary["tests_run"], 0)
        self.assertEqual(summary["outcomes"], {"blocked_fixture_error": 2})
        self.assertEqual(summary["errors"], 1)

    def test_discovery_failure_stops_before_any_child(self):
        self.module("test_broken", "raise RuntimeError('synthetic import error')\n")
        output = self.folder / "discovery_failure"
        result = subprocess.run([sys.executable, str(SCRIPT), "--output", str(output),
                                 "--start-directory", str(self.suite),
                                 "--top-level-directory", str(self.folder)], capture_output=True, text=True,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((output / "manifest.json").exists())
        self.assertFalse((output / "modules").exists())
        self.assertIn("unittest discovery failed", result.stderr)

    def test_child_allocation_mismatch_cannot_be_green(self):
        self.module("test_one", "import unittest\nclass One(unittest.TestCase):\n    def test_present(self): pass\n")
        job = {"top_level_directory": str(self.folder),
               "test_ids": ["synthetic_suite.test_one.One.test_absent"],
               "result_path": str(self.folder / "child_result.json")}
        path = self.folder / "child_job.json"
        path.write_text(json.dumps(job), encoding="utf-8")
        process = subprocess.run([sys.executable, str(SCRIPT), "--child", str(path)],
                                 capture_output=True, text=True,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        report = json.loads(Path(job["result_path"]).read_text(encoding="utf-8"))
        self.assertEqual(process.returncode, 1)
        self.assertFalse(report["successful"])
        self.assertFalse(report["coverage_passed"])


if __name__ == "__main__":
    unittest.main()
