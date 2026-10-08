"""Structured offline checks binding both the frozen base and subscription code."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import time
import unittest

from ..checks import CheckResult
from ..controller import write_new
from ..prepare import ROOT
from ..records import wire
from .calibration import bindings


def run(output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    before, start = bindings(), time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    name = __package__ + ".test_subscription"
    suite = unittest.defaultTestLoader.loadTestsFromName(name)
    with output.with_suffix(".progress.jsonl").open("x", encoding="utf-8", newline="\n") as progress:
        result = CheckResult(progress)
        suite.run(result)
    value = {"suite": name, "started_utc": started, "elapsed_seconds": time.monotonic() - start,
             "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
             "skipped": len(result.skipped), "passed": sum(x["status"] == "passed" for x in result.records),
             "successful": result.wasSuccessful() and before == bindings(), "source_bindings": before,
             "sources_unchanged_during_tests": before == bindings(), "test_results": result.records,
             "model_calls": 0, "API_spend_USD": "0"}
    write_new(output, wire(value) + "\n")
    print(wire({k: value[k] for k in ("tests_run", "passed", "failures", "errors", "skipped", "successful")}))
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output)["successful"] else 1)
