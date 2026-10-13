"""Repeat exactly the two Windows replacement failures, without changing tests."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

root = Path.cwd().resolve()
scratch = root / 'tmp' / 'v5-continuation-exact-recheck-temp'
scratch.mkdir(parents=True, exist_ok=True)
os.environ['TEMP'] = str(scratch)
os.environ['TMP'] = str(scratch)
tempfile.tempdir = str(scratch)
sys.path.insert(0, str(root))
sys.path.insert(1, str(root / 'experiments' / 'dependency_memory'))
names = [
    'experiments.dependency_memory.cross_record_continuation.test_continuation.ContinuationTests.test_full_suffix_dry_run_without_model_or_original_mutation',
    'test_development_pilot.DevelopmentPilotTests.test_budget_reservation_and_failed_attempts_do_not_retry',
]
suite = unittest.defaultTestLoader.loadTestsFromNames(names)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
