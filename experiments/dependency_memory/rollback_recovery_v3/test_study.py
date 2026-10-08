"""Information-access, nonadaptive allocation and effort-policy invariants."""
from contextlib import closing, redirect_stdout
from decimal import Decimal
import io
from pathlib import Path
import shutil
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from ..rollback_pilot.fixtures import math_example, code_example
from ..rollback_pilot.records import digest, strict_loads, wire
from ..rollback_pilot.schedule import task_slots
from ..rollback_pilot.test_controller import fixture_script
from ..rollback_pilot.subscription.accounting import Usage
from ..rollback_pilot.subscription.transport import Response
from ..rollback_pilot.transport import UnknownDispatch
from . import run
from .analysis import family_view
from .coding_tasks import expected
from .controller import Controller
from .transport import Renderer, turn_parameters
from .verify import verify

RESULTS=run.ROOT/'experiments/dependency_memory/results/rollback_recovery_v3_2026-10-08'


def temporary():
    root=run.ROOT/'tmp/recovery_v3_tests';root.mkdir(parents=True,exist_ok=True)
    return tempfile.TemporaryDirectory(dir=root)


class FakeChecker:
    def __init__(self,*args):self.grades=[]
    def receipt(self,task,candidate,candidate_id,receipt_id):
        from ..rollback_pilot.grading import PublicReceipt
        return PublicReceipt.create(receipt_id,candidate_id,'public_pass',detail='All public examples pass.')
    def grade(self,task,evaluator,candidate):
        result={'score':1,'disposition':'correct','tests':[{'id':x['id'],'status':'public_pass','elapsed_seconds':0} for x in task.data()['public_examples']+evaluator.data()['private_tests']]}
        self.grades.append({'task_id':task.task_id,'code_sha256':digest(candidate['code']),'actor_sha256':task.hash,'grade':result});return result


class FullFake:
    calls=[]
    fail_initial=False
    def __init__(self,*args):self.pairs={t.task_id:(t,e) for t,e in run.cohort()};type(self).calls=[]
    def generate(self,identity,request):
        type(self).calls.append(identity)
        if identity.task_id.startswith('authored-calibration'):
            task,evaluator,c,b,f,l,s=math_example() if identity.task_id.endswith('math') else code_example()
            values={'checkpoint':c.data(),'branch':b.data(),'lesson':l.data(),'summary':s.data(),
                    'terminal':{'values':[6,4]} if task.domain=='math' else {'code':'print(6)'}}
            text=wire(values[identity.stage])
        else:
            if self.fail_initial:raise UnknownDispatch('synthetic unknown initial dispatch')
            t,e=self.pairs[identity.task_id]
            text=wire({'facts':[],'open_requirements':[],'tentative_options':[],'possible_checks':[]} if identity.stage=='checkpoint' else
                {'status':'candidate','chosen_option':'new','assumptions':[],'observations':[],
                 'artifact':e.data()['witness'] if t.domain=='math' else {'code':e.data()['reference_code']}})
        from .transport import effort
        return Response(text,Usage(1000,0,200,100),{'synthetic':True,'thread_id':identity.key,'model':'gpt-6-luna','tool_items':0,'reasoning_effort':effort(identity.stage)})


class StudyTests(unittest.TestCase):
    def test_whole_cohort_and_all_832_identities_fixed_with_shared_families(self):
        pairs=run.cohort();self.assertEqual(len(pairs),64)
        self.assertEqual([t.domain for t,e in pairs],['math','coding']*32)
        blocks=run.block_manifests(pairs,[]);self.assertEqual(len(blocks),4)
        from ..rollback_pilot.accounting import Identity
        slots=[Identity(**x).key for b in blocks for x in b['schedule']]
        self.assertEqual(len(slots),832);self.assertEqual(len(set(slots)),832)
        self.assertTrue(all(len(b['schedule'])==208 for b in blocks))
        self.assertEqual(len({t.stratum for t,e in pairs if t.domain=='coding'}),8)

    def test_renderer_preserves_primary_contrast_and_explicit_effort_and_writer_units(self):
        t,e,c,b,f,l,s=math_example();r=Renderer()
        keep=r.continuation('K',t,c,[b],f,l,s);rollback=r.continuation('R',t,c,[b],f,l,s)
        a=strict_loads(keep.data()['messages'][1]['content']);z=strict_loads(rollback.data()['messages'][1]['content']);a['trial']=None
        self.assertEqual(a,z)
        self.assertEqual(turn_parameters('thread',r.render('checkpoint',t))['effort'],'low')
        self.assertEqual(turn_parameters('thread',keep)['effort'],'medium')
        for kind in ('lesson','summary'):self.assertIn('4096 visible UTF-8 bytes',r.render(kind,t,c,[b],f).json_text)

    def test_private_material_never_serialized_for_new_tasks(self):
        for t,e in run.cohort():
            raw=Renderer().render('checkpoint',t).json_text
            if t.domain=='coding':
                self.assertIn('Python 3.11',raw)
                self.assertNotIn(e.data()['reference_code'],raw);self.assertNotIn(e.data()['private_tests_sha256'],raw)
            self.assertNotIn('reserved-stress',raw);self.assertNotIn('witness',raw)

    def test_independent_oracles_expose_required_nonstandard_edge_cases(self):
        self.assertEqual(expected('interval_k',([(0,1,-4)],1)),'-4')
        self.assertEqual(expected('tree_k',([20,1,1],[(0,1),(0,2)],1)),'20')
        self.assertEqual(expected('tree_k',([20,1,1],[(0,1),(0,2)],2)),'2')
        self.assertEqual(expected('digit_range',(0,0,1,0)),'1')
        self.assertEqual(expected('gf2_lex',(4,[('1100',1),('0011',1)])),'0101')
        self.assertEqual(expected('two_machines',([(0,2,4),(2,3,5),(0,3,20)],0)),'29')

    def test_family_interval_requires_families_rather_than_many_variants(self):
        t=math_example()[0];rows=[]
        for i in range(20):
            row=Controller.empty_row(t);row.update(task_id=f'fake-{i}',domain='coding',stratum='one-template',primary_scheduled=True,scheduled_arms=['K','R'])
            row['grades']['K']=[0,0];row['grades']['R']=[1,1];rows.append(row)
        result=family_view(rows,'coding');self.assertEqual(result['represented_families'],1);self.assertIsNone(result['family_resampling'])

    def test_new_writer_cap_accepts_1500_byte_summary_and_retains_all_arms(self):
        with temporary() as directory:
            task,evaluator,*_=math_example();script=fixture_script({'summary':wire({'summary':'x'*1500})})
            class FixtureTransport:
                def generate(self,identity,request):return Response(script(identity,request),Usage(1000,0,200,100),{'synthetic':True})
            manifest={'launch_id':'synthetic','task_ids':[task.task_id],'schedule':[vars(x) for x in task_slots('synthetic',task,0)],'source_bindings':[]}
            controller=Controller(directory,manifest,FixtureTransport(),SimpleNamespace(grades=[]))
            try:
                with redirect_stdout(io.StringIO()):rows=controller.run([(task,evaluator)])
                self.assertEqual(rows[0]['scheduled_arms'],['K','R','Z','G'])
                self.assertEqual(controller.ledger.summary()['completed_credits'],'0.060')
            finally:controller.ledger.close()

    def fake_launch(self,fail):
        temp=temporary();self.addCleanup(temp.cleanup);folder=Path(temp.name)/'launch'
        runtime=run.read(RESULTS/'reference_checks.json')['runtime']
        with patch.object(run.DockerRunner,'audit',return_value=runtime):
            run.freeze(folder,RESULTS/'preflight.json',RESULTS/'reference_checks.json',RESULTS/'math_checks.json')
        FullFake.fail_initial=fail
        with patch.object(run,'Transport',FullFake),patch.object(run,'CodeChecker',FakeChecker),patch.object(run,'RecordingCodeChecker',FakeChecker),redirect_stdout(io.StringIO()):
            result=run.launch(folder,'unused','unused','unused')
        return folder,result,FullFake.calls

    def test_complete_synthetic_study_keeps_64_tasks_and_every_unsent_slot(self):
        folder,result,calls=self.fake_launch(False)
        self.assertEqual(len(calls),136)
        self.assertEqual(len(run.lines(folder/'tasks.jsonl')),64)
        self.assertEqual(len(run.lines(folder/'slot_dispositions.jsonl')),832)
        self.assertEqual(result['resources']['known_completed_calls'],128)
        self.assertTrue(all(r['initial_grade']['score']==1 for r in run.lines(folder/'tasks.jsonl')))
        checked=verify(folder)
        self.assertEqual(checked['verified_possible_slots'],832);self.assertTrue(checked['synthetic_transport'])

    def test_unknown_in_first_block_stops_all_later_blocks_without_new_dispatch(self):
        folder,result,calls=self.fake_launch(True)
        self.assertEqual(len(calls),9) # eight separate synthetic calibration calls and one unknown task call
        self.assertEqual(result['resources']['unknown_or_pending_calls'],1)
        self.assertEqual(Decimal(result['resources']['locked_reserve_credits']),Decimal('4.225'))
        self.assertEqual(len(run.lines(folder/'tasks.jsonl')),64)
        self.assertTrue(all(x['dispatch_state']=='not_dispatched' for x in run.lines(folder/'slot_dispositions.jsonl')[13:]))
        for block in ('02','03','04'):self.assertFalse((folder/'blocks'/block/'ledger.sqlite').exists())
        self.assertEqual(verify(folder)['unknown_or_pending'],1)

    def test_archive_rejects_six_independent_mutations_even_when_resigned(self):
        original,_,_=self.fake_launch(False)
        def save(path,value):path.write_text(wire(value)+'\n',encoding='utf-8')
        def reseal(folder):
            save(folder/'evidence_manifest.json',{'files':[{'path':p.relative_to(folder).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())}
                for p in sorted(folder.rglob('*')) if p.is_file() and p.name not in {'ledger.sqlite','evidence_manifest.json'}]})
        for probe in ('extra_file','task_omission','grade_omission','effort_allocation','hidden_input','dispatch_after_stop'):
            with self.subTest(probe=probe),temporary() as directory:
                folder=Path(directory)/'copy';shutil.copytree(original,folder)
                if probe=='extra_file':(folder/'unlisted.txt').write_text('unexpected',encoding='utf-8')
                elif probe=='task_omission':
                    rows=run.lines(folder/'tasks.jsonl');(folder/'tasks.jsonl').write_text(''.join(wire(r)+'\n' for r in rows[:-1]),encoding='utf-8');reseal(folder)
                elif probe=='grade_omission':
                    grades=run.read(folder/'blocks/01/coding_grades.json');save(folder/'blocks/01/coding_grades.json',grades[:-1]);reseal(folder)
                elif probe=='effort_allocation':
                    manifest=run.read(folder/'manifest.json');manifest['efforts']['terminal']='low';save(folder/'manifest.json',manifest)
                    marker=run.read(folder/'launch_started.json');marker['manifest_sha256']=digest((folder/'manifest.json').read_bytes());save(folder/'launch_started.json',marker);reseal(folder)
                elif probe=='hidden_input':
                    target=folder/'blocks/01';path=next((target/'requests').glob('*.json'));request=run.read(path)
                    request['messages'].append({'role':'user','content':'reserved evaluator answer'});save(path,request)
                    key=path.stem
                    with closing(sqlite3.connect(target/'ledger.sqlite')) as db,db:
                        seq,payload=db.execute("SELECT seq,payload FROM events WHERE call_id=? AND state='planned'",(key,)).fetchone()
                        event=strict_loads(payload);event['request_hash']=digest(wire(request));db.execute('UPDATE events SET payload=? WHERE seq=?',(wire(event),seq))
                    from ..rollback_pilot.subscription.accounting import Ledger
                    ledger=Ledger(target/'ledger.sqlite',max_calls=208);events=ledger.events();ledger.close()
                    (target/'usage_events.jsonl').write_text(''.join(wire(r)+'\n' for r in events),encoding='utf-8');reseal(folder)
                else:
                    target=folder/'blocks/01';events=run.lines(target/'usage_events.jsonl');event=events[3]
                    with closing(sqlite3.connect(target/'ledger.sqlite')) as db,db:db.execute("UPDATE events SET state='unknown' WHERE seq=?",(event['seq'],))
                    events[3]['state']='unknown';(target/'usage_events.jsonl').write_text(''.join(wire(r)+'\n' for r in events),encoding='utf-8');reseal(folder)
                with self.assertRaises((ValueError,KeyError)):verify(folder)


if __name__=='__main__':unittest.main()
