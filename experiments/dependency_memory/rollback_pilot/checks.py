"""Run offline unittest suites and save structured, source-bound verification."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from .controller import write_new
from .prepare import PACKAGE, ROOT, source_bindings
from .records import digest, wire


class CheckResult(unittest.TestResult):
    def __init__(self, progress):
        super().__init__()
        self.records, self.progress, self.start_times = [], progress, {}

    def startTest(self, test):
        super().startTest(test)
        self.start_times[test.id()] = time.monotonic()

    def record(self, test, status, detail=None):
        row = {"test_id": test.id(), "status": status,
               "elapsed_seconds": time.monotonic() - self.start_times.get(test.id(), time.monotonic())}
        if detail:
            row["detail"] = detail[:3000]
        self.records.append(row)
        self.progress.write(wire(row) + "\n")
        self.progress.flush()

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, "passed")

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, "error", self._exc_info_to_string(err, test))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, "failed", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "skipped", reason)

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err:
            self.record(subtest, "failed_subtest", self._exc_info_to_string(err, test))

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.record(test, "expected_failure")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.record(test, "unexpected_success")


def run_checks(output, suite="package", docker_image=None):
    output = Path(output)
    if output.exists() or output.with_suffix(".progress.jsonl").exists():
        raise FileExistsError("verification output/progress identity already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    scratch = ROOT / "tmp" / "repository_test_scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(scratch)
    os.environ["TEMP"] = os.environ["TMP"] = str(scratch)
    if docker_image:
        os.environ["ROLLBACK_E0_DOCKER_IMAGE"] = docker_image
    else:
        os.environ.pop("ROLLBACK_E0_DOCKER_IMAGE", None)
    start, started = time.monotonic(), datetime.now(timezone.utc).isoformat()
    loader = unittest.TestLoader()
    if suite == "repository":
        selected = loader.discover(str(ROOT / "experiments" / "dependency_memory"))
    elif suite == "package":
        selected = loader.loadTestsFromNames(["experiments.dependency_memory.rollback_pilot." + p.stem for p in sorted(PACKAGE.glob("test_*.py"))])
    else:
        raise ValueError("unknown test suite")
    before = source_bindings()
    with output.with_suffix(".progress.jsonl").open("x", encoding="utf-8", newline="\n") as progress:
        result = CheckResult(progress)
        selected.run(result)
    imported = []
    for module in list(sys.modules.values()):
        name = getattr(module, "__file__", None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT) and path.is_file() and path.suffix == ".py":
                imported.append((path.relative_to(ROOT).as_posix(), digest(path.read_bytes())))
    success = result.wasSuccessful() and before == source_bindings()
    record = {"schema_version": "rollback-checks-1", "suite": suite, "started_utc": started,
              "finished_utc": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": time.monotonic() - start,
              "python_version": sys.version, "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "tests_run": result.testsRun, "passed": sum(r["status"] == "passed" for r in result.records),
              "skipped": len(result.skipped), "failures": len(result.failures), "errors": len(result.errors),
              "successful": success, "source_bindings_unchanged_during_checks": before == source_bindings(),
              "docker_image": docker_image, "model_calls": 0, "provider_spend_usd": "0",
              "test_results": result.records, "source_bindings": before,
              "imported_python_source_bindings": [{"path": p, "sha256": h} for p, h in sorted(set(imported))]}
    write_new(output, wire(record) + "\n")
    print(wire({key: record[key] for key in ("suite", "tests_run", "passed", "skipped", "failures", "errors", "successful", "elapsed_seconds")}))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--suite", choices=("package", "repository"), default="package")
    parser.add_argument("--docker-image")
    args = parser.parse_args()
    record = run_checks(args.output, args.suite, args.docker_image)
    raise SystemExit(0 if record["successful"] else 1)


if __name__ == "__main__":
    main()
