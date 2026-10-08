"""Save structured offline checks for the authored subscription cohort adapter."""
import argparse
from pathlib import Path
import unittest

from ..checks import CheckResult
from ..controller import write_new
from ..records import wire
from .run import bindings


def run(output):
    output=Path(output)
    before=bindings()
    suite=unittest.defaultTestLoader.loadTestsFromName("experiments.dependency_memory.rollback_pilot.cohort_v1.test_cohort")
    with output.with_suffix(".progress.jsonl").open("x",encoding="utf-8",newline="\n") as progress:
        result=CheckResult(progress)
        suite.run(result)
    success=result.wasSuccessful() and before==bindings()
    record={"scope":"authored subscription cohort adapter offline invariants","model_calls":0,
            "tests_run":result.testsRun,"successful":success,"records":result.records,"source_bindings":before}
    write_new(output,wire(record)+"\n")
    if not success:
        raise ValueError("offline cohort checks failed")
    return record


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    print(wire({k:v for k,v in run(parser.parse_args().output).items() if k not in {"records","source_bindings"}}))
