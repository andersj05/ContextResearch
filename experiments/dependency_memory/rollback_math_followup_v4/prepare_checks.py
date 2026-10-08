"""No-model, independently formulated finite and isolated reference validation."""
import argparse
from pathlib import Path
import time

from ..rollback_pilot.code_runner import DockerRunner
from ..rollback_pilot.controller import write_new
from ..rollback_pilot.grading import CodeChecker, MathChecker
from ..rollback_pilot.independent_math import exhaustive_solutions
from ..rollback_pilot.records import digest, wire
from .math_tasks import generate as math


def finite_math(output):
    rows=[]
    for task,evaluator in math():
        started=time.monotonic();universe,accepted=exhaustive_solutions(task.data());checker=MathChecker(task)
        actual={tuple(values) for values in universe if checker.violation(values) is None}
        if actual!=accepted or tuple(evaluator.data()['witness']['values']) not in accepted:
            raise ValueError('independent finite agreement failed')
        row={'task_id':task.task_id,'actor_sha256':task.hash,'candidates':len(universe),'solutions':len(accepted),
             'solution_set_sha256':digest(wire(sorted(accepted))),'independent_agreement':True,'elapsed_seconds':time.monotonic()-started}
        rows.append(row);print(wire({k:row[k] for k in ('task_id','candidates','solutions')}),flush=True)
    record={'scope':'independent exhaustive finite solution sets and production grader agreement','model_calls':0,'tasks':rows,
            'total_candidates':sum(r['candidates'] for r in rows),'all_passed':True}
    write_new(output,wire(record)+'\n');return record


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('math',))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--image')
    args=parser.parse_args()
    result=finite_math(args.output)
    print(wire({k:v for k,v in result.items() if k not in {'tasks','runtime'}}))
