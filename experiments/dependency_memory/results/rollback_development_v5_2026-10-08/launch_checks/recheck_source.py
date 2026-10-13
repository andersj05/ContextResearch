"""Recheck exact failed discovery identities using a writable workspace temp root."""
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest

root = Path.cwd().resolve()
checks = root / "experiments/dependency_memory/results/rollback_development_v5_2026-10-08/launch_checks"
original = checks / "repository_unit_tests.txt"
text = original.read_text(encoding="utf-8")
if not re.search(r"^Ran 744 tests in ", text, re.MULTILINE):
    raise SystemExit("Wait for the original discovery to finish before selecting rechecks.")
names = list(dict.fromkeys(re.findall(r"^\s*test_\S+ \(([\w.]+)\).*\.\.\. (?:ERROR|FAIL)\s*$", text, re.MULTILINE)))
if not names:
    raise SystemExit("No recorded failed test identities to recheck.")
temporary = (root / "tmp/v5-test-temp").resolve()
if not temporary.is_relative_to(root):
    raise SystemExit("Workspace temp root escaped the repository.")
temporary.mkdir(parents=True, exist_ok=True)
for key in ("TMPDIR", "TEMP", "TMP"):
    os.environ[key] = str(temporary)
tempfile.tempdir = str(temporary)
sys.path.insert(0, str(root / "experiments/dependency_memory"))
sys.path.insert(0, str(root))
selection = checks / "repository_rechecks_selection.json"
selected = {"test_ids": names, "unique_failed_test_ids": len(names),
            "temporary_directory": str(temporary),
            "scope": "Only identities with ERROR or FAIL in original discovery; no scientific code change, CLI process or model launch"}
if selection.exists():
    if json.loads(selection.read_text(encoding="utf-8")) != selected:
        raise SystemExit("Recorded recheck selection changed.")
else:
    with selection.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(selected, stream, indent=2)
        stream.write("\n")
suite = unittest.defaultTestLoader.loadTestsFromNames(names)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
