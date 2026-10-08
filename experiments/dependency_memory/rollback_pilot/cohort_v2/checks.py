"""Save two offline invariants for the cohort-wide language correction."""
import argparse
from pathlib import Path
import unittest

from ..checks import CheckResult
from ..controller import write_new
from ..records import wire
from .run import bindings


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    before=bindings()
    selected=unittest.defaultTestLoader.loadTestsFromName("experiments.dependency_memory.rollback_pilot.cohort_v2.test_language")
    with args.output.with_suffix(".progress.jsonl").open("x",encoding="utf-8",newline="\n") as progress:
        result=CheckResult(progress);selected.run(result)
    record={"scope":"cohort-wide Python-language amendment with unchanged task/test/reference contents","model_calls":0,"tests_run":result.testsRun,
            "successful":result.wasSuccessful() and before==bindings(),"records":result.records,"source_bindings":before}
    write_new(args.output,wire(record)+"\n")
    print(wire({k:v for k,v in record.items() if k not in {"records","source_bindings"}}))
    if not record["successful"]:raise SystemExit(1)
