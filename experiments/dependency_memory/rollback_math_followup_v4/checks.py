"""Save offline invariant results separately from live model observations."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import time
import unittest

from ..rollback_pilot.checks import CheckResult
from ..rollback_pilot.controller import write_new
from ..rollback_pilot.records import wire
from .run import bindings


def run(output,test_name=None):
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);before=bindings();start=time.monotonic()
    name=test_name or __package__+'.test_followup'
    started=datetime.now(timezone.utc).isoformat();suite=unittest.defaultTestLoader.loadTestsFromName(name)
    with output.with_suffix('.progress.jsonl').open('x',encoding='utf-8',newline='\n') as progress:
        result=CheckResult(progress);suite.run(result)
    value={'suite':name,'started_utc':started,'elapsed_seconds':time.monotonic()-start,
        'tests_run':result.testsRun,'passed':sum(r['status']=='passed' for r in result.records),'failures':len(result.failures),
        'errors':len(result.errors),'skipped':len(result.skipped),'successful':result.wasSuccessful() and before==bindings(),
        'source_bindings':before,'sources_unchanged_during_tests':before==bindings(),'test_results':result.records,
        'model_calls':0,'API_spend_USD':'0','synthetic_outcomes_are_model_trials':False}
    write_new(output,wire(value)+'\n');print(wire({k:value[k] for k in ('tests_run','passed','failures','errors','skipped','successful')}));return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--test-name');args=parser.parse_args()
    raise SystemExit(0 if run(args.output,args.test_name)['successful'] else 1)
