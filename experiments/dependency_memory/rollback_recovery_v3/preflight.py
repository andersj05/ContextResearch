"""Fresh signed-in catalog and real-client low/medium/large-input mock checks."""
import argparse
from pathlib import Path

from ..rollback_pilot.controller import write_new
from ..rollback_pilot.fixtures import math_example, code_example
from ..rollback_pilot.records import wire
from ..rollback_pilot.subscription.preflight import run as baseline
from ..rollback_pilot.subscription.audit import CASES
from .client_audit import run_case
from .transport import Renderer


def run(executable,global_instructions,scratch_root):
    scratch_root=Path(scratch_root);scratch_root.mkdir(parents=True,exist_ok=True)
    result=baseline(executable,global_instructions,scratch_root)
    supported={x['reasoningEffort'] for x in result['model_catalog_entry']['supportedReasoningEfforts']}
    if not {'low','medium'}.issubset(supported):raise ValueError('requested low/medium efforts unavailable')
    renderer=Renderer();task,_,checkpoint,branch,feedback,lesson,summary=math_example()
    low=renderer.render('checkpoint',task);global_text=Path(global_instructions).read_text(encoding='utf-8')
    additional=[]
    for case in CASES:
        additional.append(run_case(executable,global_text,low,case,scratch_root))
        print(wire({'v3_low_mock_case':case,'passed':True}),flush=True)
    for kind in ('lesson','summary'):
        req=renderer.render(kind,task,checkpoint,[branch],feedback)
        additional.append(run_case(executable,global_text,req,'final_message',scratch_root))
        print(wire({'v3_writer_interface':kind,'passed':True}),flush=True)
    code=code_example()[0];public=code.data();public['statement']+='\nAdditional public formatting fixture: '+('x'*40000)
    from ..rollback_pilot.records import ActorTask
    large=renderer.render('checkpoint',ActorTask.from_dict('no-model-large-input-fixture','fixture',public))
    if large.input_units<=32768 or not renderer.fits(large):raise ValueError('expanded-admission fixture is not discriminating')
    additional.append(run_case(executable,global_text,large,'final_message',scratch_root))
    registry={x['payload_audit']['registry_sha256'] for x in result['cases']+additional}
    if registry!={result['registry_sha256']}:raise ValueError('registry changed across effort or body size')
    result.update(version='rollback-harder-v3-client-preflight',additional_cases=additional,
                  verified_stage_efforts={'checkpoint':'low','branch':'low','lesson':'medium','summary':'medium','terminal':'medium'},
                  expanded_complete_client_body_UTF8_bytes=131072,writer_visible_UTF8_bytes=4096)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable',type=Path,required=True);parser.add_argument('--global-instructions',type=Path,required=True)
    parser.add_argument('--scratch-root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=run(args.executable,args.global_instructions,args.scratch_root)
    write_new(args.output,wire(result)+'\n');print(wire({'passed':True,'mock_cases':len(result['cases'])+len(result['additional_cases']),'model_generations':0}))
