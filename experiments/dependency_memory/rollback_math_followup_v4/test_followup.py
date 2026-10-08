"""Noninterference, error privacy and complete-cohort/stop invariants."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ..rollback_pilot.accounting import Identity
from ..rollback_pilot.fixtures import math_example
from ..rollback_pilot.records import wire
from ..rollback_pilot.subscription.process import ProtocolError
from ..rollback_pilot.subscription.transport import collect as sealed_collect
from ..rollback_recovery_v3.test_study import FakeChecker, FullFake
from ..rollback_recovery_v3.math_tasks import generate as old_tasks
from . import run
from .analysis import analyze
from .controller import Controller
from .observe import collect, DiagnosedProtocolError, safe_reason
from .verify import verify

RESULTS=run.ROOT/'experiments/dependency_memory/results/rollback_math_followup_v4_2026-10-08'
OLD_RESULTS=run.ROOT/'experiments/dependency_memory/results/rollback_recovery_v3_2026-10-08'
CANARY='PRIVATE_PROVIDER_TEXT_MUST_NEVER_BE_LOGGED'


class Server:
    def __init__(self,messages,queued=True):self.notifications=list(messages) if queued else [];self.messages=[] if queued else list(messages)
    def receive(self,timeout):
        if not self.messages:raise ProtocolError('appserver_timeout')
        return self.messages.pop(0)


def messages(kind='agentMessage',extra_usage=False):
    data=[{'method':'item/completed','params':{'threadId':'t','turnId':'u','item':{'type':kind,'text':CANARY,'arguments':CANARY}}},
          {'method':'thread/tokenUsage/updated','params':{'threadId':'t','tokenUsage':{'total':{'inputTokens':1000,'cachedInputTokens':100,
               'outputTokens':200,'reasoningOutputTokens':100,'totalTokens':1200}}}}]
    if extra_usage:data.append(data[-1])
    data.append({'method':'turn/completed','params':{'threadId':'t','turn':{'id':'u','status':'failed','error':{'codexErrorInfo':'sessionBudgetExceeded'}}}})
    return data


class MathFake(FullFake):
    def __init__(self,*args):self.pairs={t.task_id:(t,e) for t,e in run.cohort()};type(self).calls=[]
    def generate(self,identity,request):
        if self.fail_initial and not identity.task_id.startswith('authored-calibration'):
            type(self).calls.append(identity)
            raise DiagnosedProtocolError(ProtocolError('rpc_error:turn/start:-32000'),'generation',{'method_counts':{},'item_counts':{},'server_error_codes':[],'turn_statuses':[]})
        return super().generate(identity,request)


class FollowupTests(unittest.TestCase):
    def test_observation_preserves_complete_queued_reply_and_metering(self):
        original=sealed_collect(Server(messages()),'t','u');observation={}
        result=collect(Server(messages()),'t','u',observation=observation)
        self.assertEqual(result.text,original.text);self.assertEqual(result.usage,original.usage)
        self.assertEqual(result.capped,original.capped)
        self.assertEqual(observation['method_counts'],{'item/completed':1,'thread/tokenUsage/updated':1,'turn/completed':1})
        self.assertNotIn(CANARY,wire(observation))
        streamed=collect(Server(messages(),queued=False),'t','u')
        self.assertEqual(streamed.usage,result.usage)

    def test_duplicate_metering_remains_unknown_with_useful_counts(self):
        observation={}
        with self.assertRaises(ProtocolError) as caught:collect(Server(messages(extra_usage=True)),'t','u',observation=observation)
        error=DiagnosedProtocolError(caught.exception,'collect',observation)
        self.assertEqual(error.diagnostic['reason_code'],'single_answer_and_usage_required')
        self.assertEqual(error.diagnostic['observation']['method_counts']['thread/tokenUsage/updated'],2)
        self.assertNotIn(CANARY,wire(error.diagnostic))

    def test_tool_and_unrecognized_item_still_rejected_without_arguments(self):
        for kind in ('customToolCall',CANARY):
            with self.subTest(kind=kind):
                observation={}
                with self.assertRaises(ProtocolError) as caught:collect(Server(messages(kind)),'t','u',observation=observation)
                self.assertEqual(safe_reason(caught.exception)['reason_code'],'tool_or_external_information_attempt')
                self.assertNotIn(CANARY,wire(observation))

    def test_provider_error_messages_and_unknown_codes_are_never_retained(self):
        notification={'method':'error','params':{'error':{'message':CANARY,'codexErrorInfo':{'secret':CANARY}}}}
        observation={}
        with self.assertRaises(ProtocolError) as caught:collect(Server([notification]),'t','u',observation=observation)
        diagnostic=DiagnosedProtocolError(caught.exception,CANARY,observation).diagnostic
        self.assertEqual(diagnostic['phase'],'unknown');self.assertEqual(observation['server_error_codes'],['other'])
        self.assertNotIn(CANARY,wire(diagnostic));self.assertNotIn(CANARY,wire(safe_reason(ProtocolError(CANARY))))

    def test_only_fixed_rpc_methods_and_numeric_codes_are_retained(self):
        self.assertEqual(safe_reason(ProtocolError('rpc_error:turn/start:-32000')),{'reason_code':'rpc_error','rpc_method':'turn/start','rpc_numeric_code':-32000})
        self.assertEqual(safe_reason(ProtocolError('rpc_error:'+CANARY+':7')),{'reason_code':'unclassified_protocol_error'})
        observation={}
        with self.assertRaises(ProtocolError) as caught:collect(Server([]),'t','u',observation=observation)
        self.assertEqual(safe_reason(caught.exception),{'reason_code':'appserver_timeout'})

    def test_new_whole_cohort_disjoint_and_416_identities_fixed(self):
        pairs=run.cohort();self.assertEqual(len(pairs),32)
        self.assertTrue(all(t.domain=='math' for t,e in pairs))
        self.assertFalse({t.task_id for t,e in pairs}&{t.task_id for t,e in old_tasks()})
        self.assertFalse({t.hash for t,e in pairs}&{t.hash for t,e in old_tasks()})
        blocks=run.block_manifests(pairs,[]);slots=[Identity(**x).key for b in blocks for x in b['schedule']]
        self.assertEqual(len(blocks),2);self.assertEqual(len(set(slots)),416)
        for t,e in pairs:
            text=run.Renderer().render('checkpoint',t).json_text
            self.assertNotIn('witness',text);self.assertNotIn(str(e.data()['seed']),text)

    def test_complete_pair_screen_rejects_six_scheduled_but_only_five_complete(self):
        task=math_example()[0];rows=[]
        for i in range(6):
            row=Controller.empty_row(task);row.update(task_id=f'offline-{i}',primary_scheduled=True,scheduled_arms=['K','R'])
            if i<5:row['grades']['K']=[1,1];row['grades']['R']=[1,1]
            rows.append(row)
        result=analyze(rows,[])['domains']['math']
        self.assertTrue(result['feasibility_screen_at_least_six_primary_tasks'])
        self.assertFalse(result['complete_pair_screen_at_least_six'])
        rows[-1]['grades']['K']=[1,1];rows[-1]['grades']['R']=[1,1]
        self.assertTrue(analyze(rows,[])['domains']['math']['complete_pair_screen_at_least_six'])

    def fake_launch(self,fail):
        root=run.ROOT/'tmp/math_followup_v4_tests';root.mkdir(parents=True,exist_ok=True)
        temp=tempfile.TemporaryDirectory(dir=root);self.addCleanup(temp.cleanup);folder=Path(temp.name)/'launch'
        runtime=run.read(OLD_RESULTS/'reference_checks.json')['runtime']
        with patch.object(run.DockerRunner,'audit',return_value=runtime),patch.object(run,'CodeChecker',FakeChecker):
            run.freeze(folder,RESULTS/'preflight.json',RESULTS/'math_checks.json')
        MathFake.fail_initial=fail
        with patch.object(run,'Transport',MathFake),patch.object(run,'CodeChecker',FakeChecker),patch.object(run,'RecordingCodeChecker',FakeChecker),redirect_stdout(io.StringIO()):
            result=run.launch(folder,'unused','unused','unused')
        return folder,result,MathFake.calls

    def test_complete_synthetic_32_task_run_and_archive(self):
        folder,result,calls=self.fake_launch(False)
        self.assertEqual(len(calls),72);self.assertEqual(result['resources']['known_completed_calls'],64)
        self.assertEqual(len(run.lines(folder/'tasks.jsonl')),32);self.assertEqual(len(run.lines(folder/'slot_dispositions.jsonl')),416)
        self.assertTrue(all(x['initial_grade']['score']==1 for x in run.lines(folder/'tasks.jsonl')))
        checked=verify(folder);self.assertTrue(checked['synthetic_transport']);self.assertEqual(checked['verified_tasks'],32)

    def test_unknown_records_sanitized_reason_and_stops_second_block(self):
        folder,result,calls=self.fake_launch(True)
        self.assertEqual(len(calls),9);self.assertEqual(result['resources']['unknown_or_pending_calls'],1)
        self.assertFalse((folder/'blocks/02/ledger.sqlite').exists())
        failures=list((folder/'blocks/01/failures').glob('*.json'));self.assertEqual(len(failures),1)
        self.assertEqual(run.read(failures[0])['reason_code'],'rpc_error')
        self.assertEqual(verify(folder)['unknown_or_pending'],1)


if __name__=='__main__':unittest.main()
