"""Run every discovered unittest ID once in bounded isolated module processes.

This accelerates the repository's offline suite without changing any test or
retrying a failure. Each module gets a fresh interpreter, unique temporary root,
exact test-ID allocation, stdout/stderr logs, and a machine-readable outcome.
Discovery, loaded IDs and terminal coverage are reconciled before success.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
MAX_WORKERS = 16


def flattened(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flattened(item)
        else:
            yield item


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as target:
        json.dump(value, target, indent=2, sort_keys=True)
        target.write("\n")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def collect(start_directory, top_level_directory, pattern):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    loader = unittest.TestLoader()
    suite = loader.discover(str(start_directory), pattern=pattern,
                            top_level_dir=str(top_level_directory))
    if loader.errors:
        raise ValueError("unittest discovery failed:\n" + "\n".join(loader.errors))
    groups, ids = {}, []
    for test in flattened(suite):
        identifier = test.id()
        if identifier in ids:
            raise ValueError("duplicate discovered test ID: " + identifier)
        ids.append(identifier)
        groups.setdefault(test.__class__.__module__, []).append(identifier)
    if not ids:
        raise ValueError("no tests discovered")
    return ids, groups


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started_ids, self.completed_ids = [], []
        self.outcomes, self.fixture_events = {}, []

    def startTest(self, test):
        self.started_ids.append(test.id())
        super().startTest(test)

    def stopTest(self, test):
        self.completed_ids.append(test.id())
        super().stopTest(test)

    def record(self, test, disposition, detail=None):
        identifier = test.id()
        if identifier in self.started_ids:
            self.outcomes[identifier] = disposition
        else:
            self.fixture_events.append({"id": identifier, "disposition": disposition,
                                        "detail": detail})

    def addSuccess(self, test):
        self.record(test, "passed")
        super().addSuccess(test)

    def addError(self, test, err):
        self.record(test, "error")
        super().addError(test, err)

    def addFailure(self, test, err):
        self.record(test, "failed")
        super().addFailure(test, err)

    def addSkip(self, test, reason):
        self.record(test, "skipped", reason)
        super().addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self.record(test, "expected_failure")
        super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self.record(test, "unexpected_success")
        super().addUnexpectedSuccess(test)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self.record(test, "failed" if issubclass(err[0], test.failureException) else "error")
        super().addSubTest(test, subtest, err)


def fixture_coverage(planned, completed, events):
    covered = {}
    for event in events:
        match = re.fullmatch(r"setUp(?:Class|Module) \((.+)\)", event["id"])
        if not match:
            continue
        prefix = match.group(1) + "."
        for identifier in planned:
            if identifier not in completed and identifier.startswith(prefix):
                covered[identifier] = ("skipped_fixture" if event["disposition"] == "skipped"
                                       else "blocked_fixture_error")
    return covered


def run_child(job_path):
    job = read_json(job_path)
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, job["top_level_directory"])
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(job["test_ids"])
    loaded = [test.id() for test in flattened(suite)]
    if loader.errors or loaded != job["test_ids"]:
        write_json(job["result_path"], {
            "loaded_test_ids": loaded, "planned_test_ids": job["test_ids"],
            "collection_errors": loader.errors, "coverage_passed": False,
            "successful": False, "reason": "child test allocation differs",
        })
        return 1
    runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=2,
                                     resultclass=RecordedResult)
    start = time.monotonic()
    result = runner.run(suite)
    fixture = fixture_coverage(loaded, result.completed_ids, result.fixture_events)
    covered = {**result.outcomes, **fixture}
    coverage = (len(result.started_ids) == len(set(result.started_ids))
                and result.started_ids == result.completed_ids
                and set(covered) == set(loaded)
                and set(result.completed_ids) <= set(loaded))
    value = {
        "loaded_test_ids": loaded, "planned_test_ids": job["test_ids"],
        "started_test_ids": result.started_ids, "completed_test_ids": result.completed_ids,
        "covered_test_outcomes": covered, "fixture_events": result.fixture_events,
        "coverage_passed": coverage, "successful": coverage and result.wasSuccessful(),
        "tests_run": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "skips": len(result.skipped),
        "expected_failures": len(result.expectedFailures),
        "unexpected_successes": len(result.unexpectedSuccesses),
        "elapsed_seconds": time.monotonic() - start,
        "temporary_directory": os.environ.get("TMPDIR"), "process_id": os.getpid(),
    }
    write_json(job["result_path"], value)
    return 0 if value["successful"] else 1


def run_suite(output, *, workers=8, start_directory=None,
              top_level_directory=None, pattern="test*.py"):
    if type(workers) is not int or not 1 <= workers <= MAX_WORKERS:
        raise ValueError("one through sixteen workers required")
    output = Path(output).resolve()
    start_directory = Path(start_directory or ROOT / "experiments/dependency_memory").resolve()
    # Match `unittest discover -s experiments/dependency_memory`: this start
    # directory is not itself an importable package with an __init__.py.
    top_level_directory = Path(top_level_directory or start_directory).resolve()
    if output.exists():
        raise ValueError("new output directory required; never overwrite or retry a validation run")
    output.mkdir(parents=True)
    # Imports can print; preserve this separately from structured progress.
    with (output / "discovery.log").open("x", encoding="utf-8") as stream:
        with redirect_stdout(stream), redirect_stderr(stream):
            ids, groups = collect(start_directory, top_level_directory, pattern)
    jobs = []
    # Begin larger modules first; every module's collected test order is intact.
    for module, identifiers in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
        slug = hashlib.sha256(module.encode()).hexdigest()[:16]
        folder = output / "modules" / slug
        temporary = folder / "tmp"
        temporary.mkdir(parents=True)
        job = {"module": module, "test_ids": identifiers,
               "top_level_directory": str(top_level_directory),
               "temporary_directory": str(temporary),
               "result_path": str(folder / "result.json"),
               "stdout_path": str(folder / "stdout.log"),
               "stderr_path": str(folder / "stderr.log"),
               "job_path": str(folder / "job.json")}
        write_json(job["job_path"], job)
        jobs.append(job)
    manifest = {"version": 1, "workers": workers, "pattern": pattern,
                "start_directory": str(start_directory),
                "top_level_directory": str(top_level_directory),
                "test_ids": ids, "jobs": jobs, "retries": 0,
                "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    write_json(output / "manifest.json", manifest)

    def execute(job):
        environment = os.environ.copy()
        environment.update({key: job["temporary_directory"] for key in ("TMP", "TEMP", "TMPDIR")})
        start = time.monotonic()
        with Path(job["stdout_path"]).open("x", encoding="utf-8") as stdout, \
                Path(job["stderr_path"]).open("x", encoding="utf-8") as stderr:
            process = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                      "--child", job["job_path"]], cwd=ROOT,
                                     env=environment, stdout=stdout, stderr=stderr,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        path = Path(job["result_path"])
        value = read_json(path) if path.is_file() else {}
        terminal_ids = list(value.get("covered_test_outcomes", {}))
        valid = (value.get("planned_test_ids") == job["test_ids"]
                 and value.get("loaded_test_ids") == job["test_ids"]
                 and set(terminal_ids) == set(job["test_ids"])
                 and value.get("coverage_passed") is True
                 and value.get("temporary_directory") == job["temporary_directory"])
        return {"module": job["module"], "returncode": process.returncode,
                "coverage_passed": valid, "successful": valid and process.returncode == 0
                and value.get("successful") is True,
                "terminal_test_ids": terminal_ids, "process_id": value.get("process_id"),
                "tests_run": value.get("tests_run", 0), "failures": value.get("failures", 0),
                "errors": value.get("errors", 0), "skips": value.get("skips", 0),
                "expected_failures": value.get("expected_failures", 0),
                "unexpected_successes": value.get("unexpected_successes", 0),
                "covered_test_outcomes": value.get("covered_test_outcomes", {}),
                "elapsed_seconds": time.monotonic() - start,
                "result_path": str(path), "stderr_path": job["stderr_path"]}

    start, results = time.monotonic(), []
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="offline-module") as pool:
        futures = {pool.submit(execute, job): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            try:
                row = future.result()
            except Exception as error:
                row = {"module": job["module"], "successful": False, "coverage_passed": False,
                       "terminal_test_ids": [], "error_type": type(error).__name__}
            results.append(row)
            print(json.dumps({"completed_modules": len(results), "total_modules": len(jobs),
                              "module": row["module"], "successful": row["successful"],
                              "coverage_passed": row["coverage_passed"]}), flush=True)
    covered = [identifier for row in results for identifier in row["terminal_test_ids"]]
    coverage = (len(covered) == len(ids) and set(covered) == set(ids)
                and all(row["coverage_passed"] for row in results))
    outcomes = {}
    for row in results:
        for disposition in row.get("covered_test_outcomes", {}).values():
            outcomes[disposition] = outcomes.get(disposition, 0) + 1
    summary = {"version": 1, "all_passed": coverage and all(row["successful"] for row in results),
               "coverage_passed": coverage, "discovered_test_count": len(ids),
               "terminal_test_count": len(covered), "module_count": len(jobs),
               "workers": workers, "retries": 0, "wall_seconds": time.monotonic() - start,
               "outcomes": outcomes, "modules": sorted(results, key=lambda row: row["module"]),
               **{key: sum(row.get(key, 0) for row in results) for key in
                  ("tests_run", "failures", "errors", "skips", "expected_failures", "unexpected_successes")}}
    write_json(output / "summary.json", summary)
    print(json.dumps({key: value for key, value in summary.items() if key != "modules"}), flush=True)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--start-directory", type=Path)
    parser.add_argument("--top-level-directory", type=Path)
    parser.add_argument("--pattern", default="test*.py")
    parser.add_argument("--child", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.child is not None:
        return run_child(args.child)
    if args.output is None:
        parser.error("--output must name a new directory")
    report = run_suite(args.output, workers=args.workers, start_directory=args.start_directory,
                       top_level_directory=args.top_level_directory, pattern=args.pattern)
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
