"""Save the separately scoped six archive verification probes."""
import argparse
from pathlib import Path
import os
import unittest

from ..checks import CheckResult
from ..controller import write_new
from ..prepare import ROOT
from ..records import digest, wire
from .verify import execution_module


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    os.environ["ROLLBACK_SUBSCRIPTION_EVIDENCE"]=str(args.folder.resolve())
    extra=[{"path":p.relative_to(ROOT).as_posix(),"sha256":digest(p.read_bytes())} for p in sorted(Path(__file__).resolve().parent.glob("*.py"))]
    selected=unittest.defaultTestLoader.loadTestsFromName("experiments.dependency_memory.rollback_pilot.verification_v1.test_evidence")
    with args.output.with_suffix(".progress.jsonl").open("x",encoding="utf-8",newline="\n") as progress:
        result=CheckResult(progress);selected.run(result)
    record={"scope":"positive archive verification and five independent semantic tamper probes","model_calls":0,"tests_run":result.testsRun,
            "successful":result.wasSuccessful() and not result.skipped,"records":result.records,
            "source_bindings":execution_module(args.folder).bindings()+extra}
    write_new(args.output,wire(record)+"\n")
    print(wire({k:v for k,v in record.items() if k not in {"records","source_bindings"}}))
    if not record["successful"]:raise SystemExit(1)
