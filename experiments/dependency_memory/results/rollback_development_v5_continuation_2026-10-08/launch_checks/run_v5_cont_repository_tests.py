"""Run the requested full repository suite with workspace temp and pinned Docker."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

root = Path.cwd().resolve()
scratch = root / 'tmp' / 'v5-continuation-repository-test-temp'
scratch.mkdir(parents=True, exist_ok=True)
os.environ['TEMP'] = str(scratch)
os.environ['TMP'] = str(scratch)
tempfile.tempdir = str(scratch)
os.environ['ROLLBACK_E0_DOCKER_IMAGE'] = 'python:3.11-slim@sha256:0dd364ba7e10242f07755449e3a3d0e35f9efd987952737b90def6709ab0c5ce'
sys.path.insert(0, str(root))
sys.path.insert(1, str(root / 'experiments' / 'dependency_memory'))
suite = unittest.defaultTestLoader.discover(str(root / 'experiments' / 'dependency_memory'))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
