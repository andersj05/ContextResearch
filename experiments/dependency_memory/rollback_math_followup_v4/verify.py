"""Independently reconcile the whole archive, then optionally re-execute graders."""
import argparse
from collections import Counter
from pathlib import Path

from ..rollback_pilot.accounting import Identity
from ..rollback_pilot.code_runner import DockerRunner
from ..rollback_pilot.contexts import ARMS, shared_hashes
from ..rollback_pilot.controller import write_new
from ..rollback_pilot.grading import CodeChecker, MathChecker, PublicReceipt, terminal_grade
from ..rollback_pilot.records import Record, InterfaceError, digest, wire
from ..rollback_pilot.subscription.accounting import Ledger, Usage
from ..rollback_pilot.subscription.profile import source_ids
from .run import check_frozen, read, lines, analyze, markdown, inspect_calibration, slot_dispositions
from .transport import Renderer, WRITER_BYTES, effort


def archive_files(folder):
    expected=set()
    for row in read(folder/'evidence_manifest.json')['files']:
        p=(folder/row['path']).resolve()
        if row['path'] in expected or not p.is_relative_to(folder) or p.is_symlink() or p.stat().st_size!=row['bytes'] or digest(p.read_bytes())!=row['sha256']:
            raise ValueError('archive evidence binding mismatch')
        expected.add(row['path'])
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p.name!='ledger.sqlite'}-{'evidence_manifest.json'}
    if actual!=expected:raise ValueError('unexpected or missing archive evidence')
    valid_ledgers={'calibration/ledger.sqlite'}|{f'blocks/{i:02d}/ledger.sqlite' for i in range(1,3)}
    if any(p.relative_to(folder).as_posix() not in valid_ledgers for p in folder.rglob('ledger.sqlite')):raise ValueError('undeclared ledger')
    return len(expected)


def ledger_snapshot(folder,maximum,schedule,threads):
    if not (folder/'ledger.sqlite').is_file():raise ValueError('missing durable ledger')
    ledger=Ledger(folder/'ledger.sqlite',max_calls=maximum)
    try:events,calls,summary=ledger.events(),ledger.rows(),ledger.summary()
    finally:ledger.close()
    if events!=lines(folder/'usage_events.jsonl'):raise ValueError('durable ledger/export mismatch')
    valid={Identity(**x).key:x for x in schedule};blocked=False
    for event in events:
        if blocked and event['state']=='dispatched':raise ValueError('dispatch after unresolved call')
        if event['state']=='unknown':blocked=True
    for key,call in calls.items():
        if key not in valid or call['identity']!=valid[key]:raise ValueError('unscheduled identity dispatched')
        states=[e['state'] for e in events if e['call_id']==key]
        if states not in (['planned'],['planned','reserved'],['planned','reserved','dispatched'],['planned','reserved','dispatched','completed'],['planned','reserved','dispatched','unknown']):
            raise ValueError('invalid dispatch lifecycle')
        if digest(wire(read(folder/'requests'/(key+'.json'))))!=call['request_hash']:raise ValueError('dispatched request hash mismatch')
        if call['state']=='completed':
            response=read(folder/'responses'/(key+'.json'));usage=Usage(**call['usage'])
            if str(usage.cost)!=call['planning_credits'] or response['usage']!=call['usage'] or response['metadata']!=call['metadata']:
                raise ValueError('saved response/usage/credit mismatch')
            metadata=call['metadata'];thread=metadata['thread_id']
            if thread in threads or metadata['tool_items']!=0 or metadata['model']!='gpt-6-luna' or metadata['reasoning_effort']!=effort(call['identity']['stage']):
                raise ValueError('shared continuity, tool access or model/effort mismatch')
            if not metadata.get('synthetic') and (metadata['usage_events']!=1 or metadata['harness_termination']!='sessionBudgetExceeded'):
                raise ValueError('single-generation guard absent')
            threads.add(thread)
    return events,calls,summary


def calibration_check(folder,manifest,threads,regrade):
    requests=lines(folder/'calibration_requests.jsonl')
    schedule=[{'launch_id':manifest['study_id']+'_CAL','task_id':r['task_id'],'stage':r['stage'],
               'slot':r['calibration_call'],'arm':None,'draw':None} for r in requests]
    target=folder/'calibration';events,calls,accounting=ledger_snapshot(target,8,schedule,threads)
    summary=read(target/'summary.json')
    if summary['accounting']!=accounting or len(summary['results'])!=8:raise ValueError('calibration ledger mismatch')
    checker=CodeChecker(DockerRunner(manifest['runtime_image'])) if regrade else None
    stopped=False
    for allocation,request,result in zip(schedule,requests,summary['results'],strict=True):
        key=Identity(**allocation).key;call=calls.get(key)
        if result!=read(target/'dispositions'/f"{allocation['slot']:02d}.json") or not result['excluded_from_study']:
            raise ValueError('calibration disposition mismatch')
        if stopped and call:raise ValueError('calibration dispatched after stop')
        if call and read(target/'requests'/(key+'.json'))!=request['request']:raise ValueError('calibration context mismatch')
        if call and call['state']=='completed':
            class SavedGrade:
                def grade(self,*args):return result.get('grade')
            assessed=inspect_calibration(request,read(target/'responses'/(key+'.json'))['text'],checker or SavedGrade())
            if assessed['format_valid']!=result['format_valid'] or assessed['disposition']!=result['disposition']:
                raise ValueError('calibration format mismatch')
            if 'grade' in assessed and {k:assessed['grade'][k] for k in ('score','disposition')}!={k:result['grade'][k] for k in ('score','disposition')}:
                raise ValueError('calibration grade mismatch')
        stopped|=result['format_valid'] is not True
    if summary['stopped']!=stopped or summary['all_formats_valid']!=all(r['format_valid'] is True for r in summary['results']):raise ValueError('calibration stop mismatch')
    return summary,calls


def contexts(folder,pairs,rows,calls):
    """Reconstruct inputs only from public tasks and earlier typed model records."""
    renderer=Renderer();by_id={r['task_id']:r for r in rows};parsed_calls=[];coding_expected=[]
    for task,evaluator in pairs:
        row=by_id[task.task_id];checkpoint,branches,lesson,summary,feedback=None,[],None,None,None
        prep_path=folder/'preparations'/(digest(task.task_id)+'.json');prepared=read(prep_path) if prep_path.exists() else None
        if prepared:feedback=PublicReceipt(wire(prepared['feedback']))
        for call in calls.values():
            identity=Identity(**call['identity'])
            if identity.task_id!=task.task_id:continue
            request=(renderer.continuation(identity.arm,task,checkpoint,branches,feedback,lesson,summary) if identity.stage=='terminal'
                else renderer.render(identity.stage,task,checkpoint,branches if identity.stage!='checkpoint' else (),feedback if identity.stage in {'lesson','summary'} else None))
            if request.hash!=call['request_hash'] or request.data()!=read(folder/'requests'/(identity.key+'.json')):
                raise ValueError('canonical input includes unexpected information')
            if call['state']!='completed':continue
            response=read(folder/'responses'/(identity.key+'.json'));supplied=source_ids(task)
            if checkpoint:supplied.update(f'C.fact{i+1}' for i in range(len(checkpoint.data()['facts'])))
            for i,b in enumerate(branches):
                supplied.add(f'B{i+1}');supplied.update(f'B{i+1}.observation{j+1}' for j in range(len(b.data()['observations'])))
            if feedback and identity.stage in {'lesson','summary','terminal'}:supplied.add(feedback.data()['receipt_id'])
            try:
                if response['capped'] or (identity.stage in {'lesson','summary'} and len(response['text'].encode('utf-8'))>WRITER_BYTES):raise InterfaceError('capped writer/response')
                parsed=Record.parse(identity.stage,response['text'],task,supplied=supplied,option_ids=[x['id'] for x in checkpoint.data()['tentative_options']] if checkpoint else [])
            except InterfaceError:
                if identity.stage=='terminal' and (row['grades'][identity.arm][identity.draw-1]!=0 or not row['terminal_dispositions'][identity.arm][identity.draw-1].startswith('known_invalid:')):
                    raise ValueError('invalid terminal not counted as failure')
                continue
            parsed_calls.append((identity,task,evaluator,parsed,row))
            if identity.stage=='checkpoint':checkpoint=parsed
            elif identity.stage=='branch':branches.append(parsed)
            elif identity.stage=='lesson':lesson=parsed
            elif identity.stage=='summary':summary=parsed
            elif identity.stage=='terminal':
                if identity.arm not in row['scheduled_arms']:raise ValueError('unscheduled arm dispatched')
                scored=row['terminal_dispositions'][identity.arm][identity.draw-1] in {'correct','test_failure','constraint_failure'}
                if scored and task.domain=='math':
                    grade=terminal_grade(task,evaluator,parsed)
                    if grade['score']!=row['grades'][identity.arm][identity.draw-1] or grade['disposition']!=row['terminal_dispositions'][identity.arm][identity.draw-1]:raise ValueError('independent math grade mismatch')
                elif scored:coding_expected.append((task.task_id,digest(parsed.data()['code']),row['grades'][identity.arm][identity.draw-1]))
                if row['repeated_candidates'][identity.arm][identity.draw-1]!=(parsed.data()==branches[-1].data()['artifact']):raise ValueError('rejected-candidate repetition mismatch')
        if len(branches)!=row['branch_count']:raise ValueError('branch count mismatch')
        if 'initial_grade' in row:
            candidates=[b.data()['artifact'] for b in branches if b.data()['status']=='candidate']
            if len(candidates)!=1 or row['public_failure'] or row['scheduled_arms'] or 'public_pass' not in row['flow']:raise ValueError('public-pass stopping mismatch')
            if task.domain=='math' and terminal_grade(task,evaluator,Record.parse('terminal',wire(candidates[0]),task))!=row['initial_grade']:raise ValueError('independent initial math grade mismatch')
            if task.domain=='coding':coding_expected.append((task.task_id,digest(candidates[0]['code']),row['initial_grade']['score']))
        if prepared:
            if not row['public_failure'] or checkpoint.data()!=prepared['checkpoint'] or [b.data() for b in branches]!=prepared['branch'] or (lesson.data() if lesson else None)!=prepared['lesson'] or (summary.data() if summary else None)!=prepared['summary']:
                raise ValueError('preparation differs from model records')
            requests={a:renderer.continuation(a,task,checkpoint,branches,feedback,lesson,summary) for a in ARMS}
            routing={a:{'request_sha256':q.hash,'shared':shared_hashes(q),'input_units':q.input_units,'counter_id':q.counter_id} for a,q in requests.items()}
            primary=bool(lesson and all(renderer.fits(requests[a]) for a in ('K','R')))
            allowed={'K':primary,'R':primary,'Z':renderer.fits(requests['Z']),'G':bool(summary and renderer.fits(requests['G']))}
            if routing!=prepared['routing'] or routing!=row['context_hashes'] or row['primary_scheduled']!=primary or row['scheduled_arms']!=[a for a in ARMS if allowed[a]]:
                raise ValueError('matched-arm admission/routing mismatch')
    return parsed_calls,coding_expected


def code_evidence(folder,pairs,expected):
    tasks={t.task_id:(t,e) for t,e in pairs};actual=[];grades=read(folder/'coding_grades.json')
    for item in grades:
        task,evaluator=tasks[item['task_id']];tests=task.data()['public_examples']+evaluator.data()['private_tests'];grade=item['grade'];outcomes=grade['tests']
        if item['actor_sha256']!=task.hash or [x['id'] for x in outcomes]!=[x['id'] for x in tests[:len(outcomes)]] or len(outcomes)>len(tests):raise ValueError('coding suite coverage mismatch')
        passed=len(outcomes)==len(tests) and all(x['status']=='public_pass' for x in outcomes)
        if grade['score']!=int(passed) or grade['disposition']!=('correct' if passed else 'test_failure'):raise ValueError('coding score inconsistent with test outcomes')
        if any(type(x.get('elapsed_seconds')) not in (int,float) or x['elapsed_seconds']<0 for x in outcomes if 'elapsed_seconds' in x):raise ValueError('invalid grading elapsed time')
        actual.append((task.task_id,item['code_sha256'],grade['score']))
    if Counter(actual)!=Counter(expected):raise ValueError('missing, duplicate or unsupported coding grading evidence')
    return len(grades)


def recheck(folder,manifest,parsed_calls):
    checker=CodeChecker(DockerRunner(manifest['runtime_image']));results=[]
    for identity,task,evaluator,parsed,row in parsed_calls:
        if identity.stage not in {'branch','terminal'}:continue
        result={'task_id':task.task_id,'call_id':identity.key,'stage':identity.stage,'arm':identity.arm,'draw':identity.draw}
        if identity.stage=='branch':
            if parsed.data()['status']!='candidate':continue
            candidate=parsed.data()['artifact'];receipt=(MathChecker(task).receipt(candidate,f'B{identity.slot}',f'F{identity.slot}') if task.domain=='math' else checker.receipt(task,candidate,f'B{identity.slot}',f'F{identity.slot}'))
            if receipt.data()['status'] not in row['flow'] or receipt.eligible!=row['public_failure']:raise ValueError('public disposition differs from isolated recheck')
            result['public_receipt']=receipt.data()
            if receipt.eligible and receipt.data()!=read(folder/'preparations'/(digest(task.task_id)+'.json'))['feedback']:raise ValueError('public failure differs from isolated recheck')
            if 'initial_grade' in row:
                grade=terminal_grade(task,evaluator,Record.parse('terminal',wire(candidate),task),checker)
                if {k:grade[k] for k in ('score','disposition')}!={k:row['initial_grade'][k] for k in ('score','disposition')}:raise ValueError('initial retained suite differs from recheck')
                result['retained_grade']=grade
        else:
            if row['terminal_dispositions'][identity.arm][identity.draw-1] not in {'correct','test_failure','constraint_failure'}:continue
            grade=terminal_grade(task,evaluator,parsed,checker)
            if grade['score']!=row['grades'][identity.arm][identity.draw-1] or grade['disposition']!=row['terminal_dispositions'][identity.arm][identity.draw-1]:raise ValueError('terminal retained suite differs from recheck')
            result['retained_grade']=grade
        results.append(result);print(wire({'independent_recheck':task.task_id,'stage':identity.stage,'arm':identity.arm}),flush=True)
    return results


def verify(folder,*,regrade=False):
    folder=Path(folder).resolve();manifest,pairs=check_frozen(folder);files=archive_files(folder)
    if read(folder/'launch_started.json')['manifest_sha256']!=digest((folder/'manifest.json').read_bytes()):raise ValueError('launch marker mismatch')
    threads=set();calibration,cal_calls=calibration_check(folder,manifest,threads,regrade)
    stop=calibration['stopped'];events=[];calls={};rows=[];parsed=[];grade_count=0
    for block in manifest['blocks']:
        target=folder/'blocks'/f"{block['block']:02d}";selected=pairs[16*(block['block']-1):16*block['block']];block_rows=lines(target/'tasks.jsonl')
        if [r['task_id'] for r in block_rows]!=block['task_ids']:raise ValueError('block task omission/reorder')
        if stop:
            if (target/'ledger.sqlite').exists() or any(r['flow']!=['study_stop_before_block'] for r in block_rows):raise ValueError('later block evades unresolved study stop')
        else:
            ev,cs,accounting=ledger_snapshot(target,208,block['schedule'],threads)
            if accounting!=read(target/'accounting.json'):raise ValueError('block accounting mismatch')
            if any(read(target/'task_dispositions'/(digest(r['task_id'])+'.json'))!=r for r in block_rows):raise ValueError('task disposition mismatch')
            pc,expected=contexts(target,selected,block_rows,cs);grade_count+=code_evidence(target,selected,expected)
            parsed.extend((target,x) for x in pc);events.extend(ev);calls.update(cs)
            stop=accounting['blocked'] or any(any(x.startswith('infrastructure_stop') for x in r['flow']) for r in block_rows)
        rows.extend(block_rows)
    if rows!=lines(folder/'tasks.jsonl') or events!=lines(folder/'usage_events.jsonl'):raise ValueError('whole-study aggregation mismatch')
    slots=slot_dispositions(manifest['blocks'],rows,calls)
    if slots!=lines(folder/'slot_dispositions.jsonl'):raise ValueError('slot disposition mismatch')
    result=analyze(rows,events)
    if result!=read(folder/'analysis.json') or markdown(result)!=(folder/'report.md').read_text(encoding='utf-8'):raise ValueError('analysis differs from recomputation')
    if read(folder/'summary.json')!={'completed':True,'study_stopped':bool(stop),'calibration':calibration,'task_resources':result['resources'],'selected_tasks':32,'provider_model_revision':None}:raise ValueError('whole-study summary mismatch')
    synthetic=any(c.get('metadata',{}).get('synthetic') for c in list(calls.values())+list(cal_calls.values()))
    value={'verified_tasks':len(rows),'verified_possible_slots':len(slots),'task_generations':result['resources']['known_completed_calls'],
        'calibration_generations':sum(x['state']=='completed' for x in cal_calls.values()),'unknown_or_pending':result['resources']['unknown_or_pending_calls'],
        'source_bindings':len(manifest['source_bindings']),'evidence_files':files,'coding_grade_records':grade_count,'unique_provider_threads':len(threads),
        'synthetic_transport':synthetic,'regraded_in_Docker':regrade,'archive_identity_authentication':'local source/evidence bindings; not authenticated provider internals'}
    if regrade:
        value['independent_rechecks']=[]
        for block in manifest['blocks']:
            target=folder/'blocks'/f"{block['block']:02d}"
            value['independent_rechecks'].extend(recheck(target,manifest,[x for p,x in parsed if p==target]))
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--folder',type=Path,required=True)
    parser.add_argument('--output',type=Path);parser.add_argument('--regrade',action='store_true');args=parser.parse_args()
    value=verify(args.folder,regrade=args.regrade)
    if args.output:write_new(args.output,wire(value)+'\n')
    print(wire({k:v for k,v in value.items() if k!='independent_rechecks'}))
