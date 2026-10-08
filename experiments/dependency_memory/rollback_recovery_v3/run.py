"""Freeze the whole new cohort, calibrate, then complete four nonadaptive blocks."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from ..rollback_pilot.accounting import Identity
from ..rollback_pilot.code_runner import DockerRunner
from ..rollback_pilot.controller import write_new
from ..rollback_pilot.contexts import Request
from ..rollback_pilot.fixtures import math_example, code_example
from ..rollback_pilot.grading import CodeChecker, terminal_grade
from ..rollback_pilot.prepare import ROOT, calibration_requests
from ..rollback_pilot.records import ActorTask, EvaluatorTask, Record, InterfaceError, digest, strict_loads, wire
from ..rollback_pilot.schedule import ordered_tasks, task_slots
from ..rollback_pilot.subscription.accounting import Ledger
from ..rollback_pilot.subscription.calibration import check_bindings
from ..rollback_pilot.cohort_v2.run import bindings as upstream_bindings
from ..rollback_pilot.cohort_v1.controller import RecordingCodeChecker
from .analysis import analyze, markdown
from .controller import Controller, Dispatcher
from .transport import Renderer, Transport, WRITER_BYTES, effort
from .math_tasks import generate as math
from .coding_tasks import generate as coding

PACKAGE=Path(__file__).resolve().parent
STUDY='ROLLBACK_HARDER_V3_2026-10-08'


def read(path):return strict_loads(Path(path).read_text(encoding='utf-8'))
def lines(path):return [strict_loads(x) for x in Path(path).read_text(encoding='utf-8').splitlines()]


def bindings():
    return upstream_bindings()+[{'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p.read_bytes())}
        for p in sorted(PACKAGE.iterdir()) if p.is_file() and p.suffix in {'.py','.md'}]


def cohort():
    pairs=math()+coding();by_id={t.task_id:(t,e) for t,e in pairs}
    return [by_id[t.task_id] for t in ordered_tasks([t for t,e in pairs])]


def block_manifests(pairs,sources):
    blocks=[]
    for block in range(4):
        selected=pairs[16*block:16*(block+1)];indices={'math':0,'coding':0};schedule=[]
        launch=f'{STUDY}_B{block+1:02d}'
        for t,e in selected:
            schedule.extend(vars(x) for x in task_slots(launch,t,indices[t.domain]));indices[t.domain]+=1
        blocks.append({'block':block+1,'launch_id':launch,'task_ids':[t.task_id for t,e in selected],
                       'schedule':schedule,'source_bindings':sources,'generation_attempt_ceiling':208})
    return blocks


def freeze(folder,preflight,reference_checks,math_checks):
    folder=Path(folder);preflight=read(preflight);refs=read(reference_checks);finite=read(math_checks);pairs=cohort()
    if not preflight['serialization_and_retry_audit_passed'] or len(preflight['additional_cases'])!=9:raise ValueError('v3 client audit required')
    if not refs['all_passed'] or refs['retained_test_executions']!=416 or not finite['all_passed']:raise ValueError('complete independent preparation checks required')
    by_id={t.task_id:(t,e) for t,e in pairs}
    if len(refs['tasks'])!=32 or len(finite['tasks'])!=32:raise ValueError('complete domain certification required')
    for row in refs['tasks']:
        t,e=by_id[row['task_id']]
        if t.hash!=row['actor_sha256'] or digest(e.material_json)!=row['evaluator_sha256'] or row['grade']['score']!=1:raise ValueError('coding binding mismatch')
    if {r['task_id']:r['actor_sha256'] for r in finite['tasks']}!={t.task_id:t.hash for t,e in pairs if t.domain=='math'}:raise ValueError('finite binding mismatch')
    image=refs['runtime']['configuration']['image'];runtime=DockerRunner(image).audit();renderer=Renderer()
    if any(not renderer.fits(renderer.render('checkpoint',t)) for t,e in pairs):raise ValueError('initial request cannot fit')
    folder.mkdir(parents=True,exist_ok=False)
    for name,value in (('preflight.json',preflight),('reference_checks.json',refs),('math_checks.json',finite),('runtime_audit.json',runtime)):
        write_new(folder/name,wire(value)+'\n')
    write_new(folder/'tasks_public.jsonl',''.join(wire({'task_id':t.task_id,'domain':t.domain,'stratum':t.stratum,'public':t.data(),'actor_sha256':t.hash})+'\n' for t,e in pairs))
    write_new(folder/'tasks_evaluator.jsonl',''.join(wire({'task_id':t.task_id,'actor_sha256':t.hash,'material':e.data()})+'\n' for t,e in pairs))
    calibration=calibration_requests(renderer);write_new(folder/'calibration_requests.jsonl',''.join(wire(x)+'\n' for x in calibration))
    sources=bindings();blocks=block_manifests(pairs,sources)
    for block in blocks:
        target=folder/'blocks'/f"{block['block']:02d}";target.mkdir(parents=True)
        write_new(target/'manifest.json',wire(block)+'\n')
    schedule=[x for block in blocks for x in block['schedule']]
    write_new(folder/'schedule.jsonl',''.join(wire(x)+'\n' for x in schedule))
    manifest={'version':'harder-rollback-development-v3','study_id':STUDY,'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
        'task_ids':[t.task_id for t,e in pairs],'task_counts':dict(Counter(t.domain for t,e in pairs)),
        'model':'gpt-6-luna','efforts':{'checkpoint':'low','branch':'low','lesson':'medium','summary':'medium','terminal':'medium'},
        'immutable_model_revision':None,'provider_sampling_seed':None,'source':'original constructed tasks; no benchmark source claim',
        'authorization':'User requests continued work to find useful results; existing Luna subscription and no token/cost ceiling remain selected.',
        'generation_attempt_ceiling':840,'task_call_ceiling':832,'calibration_call_ceiling':8,'planning_credit_ceiling':None,
        'API_dollars_authorized':'0','automatic_retries':False,'credit_purchase':False,'credit_fallback':False,
        'complete_client_body_UTF8_byte_bound':131072,'writer_visible_UTF8_byte_bound':WRITER_BYTES,
        'provider_configurable_output_token_cap':None,'response_observation_seconds':900,'conditional_input_envelope':1050000,'conditional_output_envelope':128000,
        'runtime_image':image,'source_bindings':sources,'coding_family_clusters':8,'coding_variants_per_family':4,
        'blocks':blocks,'calibration_requests_sha256':digest((folder/'calibration_requests.jsonl').read_bytes()),
        'frozen_artifacts':[{'path':p.relative_to(folder).as_posix(),'sha256':digest(p.read_bytes())} for p in sorted(folder.rglob('*')) if p.is_file()]}
    write_new(folder/'manifest.json',wire(manifest)+'\n');check_frozen(folder);return manifest


def check_frozen(folder):
    folder=Path(folder).resolve();manifest=read(folder/'manifest.json');check_bindings(manifest['source_bindings'])
    fixed={'version':'harder-rollback-development-v3','study_id':STUDY,'task_counts':{'math':32,'coding':32},
        'model':'gpt-6-luna','efforts':{s:effort(s) for s in ('checkpoint','branch','lesson','summary','terminal')},
        'immutable_model_revision':None,'provider_sampling_seed':None,'generation_attempt_ceiling':840,
        'task_call_ceiling':832,'calibration_call_ceiling':8,'planning_credit_ceiling':None,
        'API_dollars_authorized':'0','automatic_retries':False,'credit_purchase':False,'credit_fallback':False,
        'complete_client_body_UTF8_byte_bound':131072,'writer_visible_UTF8_byte_bound':4096,
        'provider_configurable_output_token_cap':None,'response_observation_seconds':900,'conditional_input_envelope':1050000,
        'conditional_output_envelope':128000,'coding_family_clusters':8,'coding_variants_per_family':4}
    if any(manifest.get(k)!=v for k,v in fixed.items()) or manifest['source_bindings']!=bindings():raise ValueError('allocation identity changed')
    paths=[x['path'] for x in manifest['frozen_artifacts']]
    expected={'preflight.json','reference_checks.json','math_checks.json','runtime_audit.json',
        'tasks_public.jsonl','tasks_evaluator.jsonl','calibration_requests.jsonl','schedule.jsonl'}|{f'blocks/{i:02d}/manifest.json' for i in range(1,5)}
    if len(paths)!=len(expected) or set(paths)!=expected:raise ValueError('frozen coverage changed')
    for item in manifest['frozen_artifacts']:
        p=(folder/item['path']).resolve()
        if not p.is_relative_to(folder) or p.is_symlink() or digest(p.read_bytes())!=item['sha256']:raise ValueError('frozen artifact changed')
    pairs=cohort()
    if manifest['task_ids']!=[t.task_id for t,e in pairs]:raise ValueError('selected tasks changed')
    public=lines(folder/'tasks_public.jsonl');private=lines(folder/'tasks_evaluator.jsonl')
    for a,e,(t,v) in zip(public,private,pairs,strict=True):
        if a!={'task_id':t.task_id,'domain':t.domain,'stratum':t.stratum,'public':t.data(),'actor_sha256':t.hash} or e!={'task_id':t.task_id,'actor_sha256':t.hash,'material':v.data()}:
            raise ValueError('cohort differs from independent reconstruction')
    blocks=block_manifests(pairs,manifest['source_bindings'])
    if manifest['blocks']!=blocks or lines(folder/'schedule.jsonl')!=[x for b in blocks for x in b['schedule']]:raise ValueError('schedule changed')
    if lines(folder/'calibration_requests.jsonl')!=calibration_requests(Renderer()):raise ValueError('calibration changed')
    if digest((folder/'calibration_requests.jsonl').read_bytes())!=manifest['calibration_requests_sha256']:raise ValueError('calibration binding changed')
    return manifest,pairs


def inspect_calibration(row,text,checker):
    task,evaluator,checkpoint,branch,feedback,lesson,summary=math_example() if row['task_id']=='authored-calibration-math' else code_example()
    from ..rollback_pilot.subscription.profile import source_ids
    supplied=source_ids(task)|{'B1',feedback.data()['receipt_id']}
    supplied.update(f'C.fact{i+1}' for i in range(len(checkpoint.data()['facts'])))
    supplied.update(f'B1.observation{i+1}' for i in range(len(branch.data()['observations'])))
    try:
        if row['stage'] in {'lesson','summary'} and len(text.encode('utf-8'))>WRITER_BYTES:raise InterfaceError('writer byte cap')
        record=Record.parse(row['stage'],text,task,supplied=supplied,option_ids=[x['id'] for x in checkpoint.data()['tentative_options']])
    except InterfaceError as error:return {'format_valid':False,'disposition':str(error)}
    result={'format_valid':True,'disposition':'valid_record'}
    if row['stage']=='terminal':result['grade']=terminal_grade(task,evaluator,record,checker)
    return result


def launch_calibration(folder,manifest,transport):
    target=Path(folder)/'calibration';target.mkdir()
    schedule=[{'launch_id':STUDY+'_CAL','task_id':r['task_id'],'stage':r['stage'],'slot':r['calibration_call'],'arm':None,'draw':None}
              for r in lines(Path(folder)/'calibration_requests.jsonl')]
    local={'schedule':schedule,'source_bindings':manifest['source_bindings']}
    ledger=Ledger(target/'ledger.sqlite',max_calls=8);dispatcher=Dispatcher(target,ledger,transport,local,Renderer())
    checker=CodeChecker(DockerRunner(manifest['runtime_image']));rows=[];stopped=False
    try:
        for allocation,row in zip(schedule,lines(Path(folder)/'calibration_requests.jsonl'),strict=True):
            result={'calibration_call':row['calibration_call'],'task_id':row['task_id'],'stage':row['stage'],'format_valid':None,'excluded_from_study':True}
            if stopped:result['disposition']='not_dispatched_after_calibration_stop'
            else:
                try:
                    request=Request(row['stage'],wire(row['request']),row['complete_input_units'],row['counter_id'])
                    answer=dispatcher.call(Identity(**allocation),request);result.update(inspect_calibration(row,answer.text,checker))
                    if not result['format_valid']:stopped=True
                except Exception as error:stopped=True;result.update(disposition='transport_or_grading_stop',error_type=type(error).__name__)
            rows.append(result);write_new(target/'dispositions'/f"{row['calibration_call']:02d}.json",wire(result)+'\n')
            print(wire({'calibration_call':row['calibration_call'],'format_valid':result['format_valid'],'disposition':result['disposition']}),flush=True)
        summary={'results':rows,'all_formats_valid':all(r['format_valid'] is True for r in rows),'stopped':stopped,'accounting':ledger.summary()}
        write_new(target/'summary.json',wire(summary)+'\n');write_new(target/'usage_events.jsonl',''.join(wire(x)+'\n' for x in ledger.events()))
        return summary
    finally:ledger.close()


def slot_dispositions(blocks,rows,latest):
    by_id={r['task_id']:r for r in rows};result=[]
    for block in blocks:
        for allocation in block['schedule']:
            identity=Identity(**allocation);event=latest.get(identity.key)
            row={'call_id':identity.key,'identity':allocation,'dispatch_state':event['state'] if event else 'not_dispatched'}
            if identity.stage=='terminal':
                task=by_id[identity.task_id];row.update(score=task['grades'][identity.arm][identity.draw-1],disposition=task['terminal_dispositions'][identity.arm][identity.draw-1])
            result.append(row)
    return result


def launch(folder,executable,global_instructions,scratch_root):
    folder=Path(folder);manifest,pairs=check_frozen(folder)
    write_new(folder/'launch_started.json',wire({'started_at_utc':datetime.now(timezone.utc).isoformat(),'manifest_sha256':digest((folder/'manifest.json').read_bytes())})+'\n')
    transport=Transport(executable,global_instructions,read(folder/'preflight.json'),scratch_root)
    calibration=launch_calibration(folder,manifest,transport);stop=calibration['stopped'];rows=[];events=[];latest={}
    for block in manifest['blocks']:
        selected=pairs[16*(block['block']-1):16*block['block']];target=folder/'blocks'/f"{block['block']:02d}"
        if stop:
            block_rows=[Controller.empty_row(t,'study_stop_before_block') for t,e in selected]
            write_new(target/'tasks.jsonl',''.join(wire(r)+'\n' for r in block_rows));rows.extend(block_rows);continue
        check_bindings(manifest['source_bindings'])
        controller=Controller(target,block,transport,RecordingCodeChecker(DockerRunner(manifest['runtime_image'])))
        try:
            block_rows=controller.run(selected);rows.extend(block_rows);events.extend(controller.ledger.events());latest.update(controller.ledger.rows())
            stop=controller.dispatcher.stopped or controller.ledger.summary()['blocked']
        finally:controller.ledger.close()
    result=analyze(rows,events)
    write_new(folder/'tasks.jsonl',''.join(wire(x)+'\n' for x in rows));write_new(folder/'usage_events.jsonl',''.join(wire(x)+'\n' for x in events))
    write_new(folder/'analysis.json',wire(result)+'\n');write_new(folder/'report.md',markdown(result))
    write_new(folder/'slot_dispositions.jsonl',''.join(wire(x)+'\n' for x in slot_dispositions(manifest['blocks'],rows,latest)))
    write_new(folder/'summary.json',wire({'completed':True,'study_stopped':stop,'calibration':calibration,'task_resources':result['resources'],
                                         'selected_tasks':64,'provider_model_revision':None})+'\n')
    write_new(folder/'evidence_manifest.json',wire({'files':[{'path':p.relative_to(folder).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())}
        for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='ledger.sqlite']})+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('freeze','launch'))
    parser.add_argument('--folder',type=Path,required=True);parser.add_argument('--preflight',type=Path)
    parser.add_argument('--reference-checks',type=Path);parser.add_argument('--math-checks',type=Path)
    parser.add_argument('--executable',type=Path);parser.add_argument('--global-instructions',type=Path);parser.add_argument('--scratch-root',type=Path)
    args=parser.parse_args()
    if args.mode=='freeze':
        r=freeze(args.folder,args.preflight,args.reference_checks,args.math_checks);print(wire({'frozen_tasks':len(r['task_ids']),'possible_task_calls':r['task_call_ceiling']}))
    else:print(wire(launch(args.folder,args.executable,args.global_instructions,args.scratch_root)['resources']))
