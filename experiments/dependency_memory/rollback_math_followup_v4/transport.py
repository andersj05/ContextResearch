"""Versioned per-stage effort and expanded-body adapter over the audited CLI."""
from copy import deepcopy
from pathlib import Path
import tempfile

from ..rollback_pilot.contexts import Request
from ..rollback_pilot.records import InterfaceError, wire
from ..rollback_pilot.subscription import profile
from ..rollback_pilot.subscription.process import AppServer, ProtocolError
from ..rollback_pilot.subscription.transport import SubscriptionTransport, check_quota, quota_snapshot
from ..rollback_pilot.transport import UnknownDispatch
from ..rollback_pilot.subscription.accounting import AccountingError
from .observe import collect, DiagnosedProtocolError

MAX_BODY_BYTES=131072
WRITER_BYTES=4096
RESPONSE_OBSERVATION_SECONDS=900


def effort(stage):
    return 'low' if stage in {'checkpoint','branch'} else 'medium'


class Renderer(profile.Renderer):
    def render(self,stage,task,checkpoint=None,branches=(),feedback=None,lesson=None,summary=None):
        result=super().render(stage,task,checkpoint,branches,feedback,lesson,summary)
        payload=result.data();payload['settings']['reasoning_effort']=effort(stage)
        if stage in {'lesson','summary'}:
            payload['messages'][0]['content']+='\nKeep the entire returned JSON object within 4096 visible UTF-8 bytes, including JSON punctuation. This same acceptance limit applies to both writers.'
        raw=wire(payload);candidate=Request(stage,raw,0,'v4-complete-client-body-byte-bound')
        return Request(stage,raw,profile.body_bound(candidate),candidate.counter_id)

    def fits(self,request):
        return profile.body_bound(request)<=MAX_BODY_BYTES


def turn_parameters(thread,request):
    if profile.body_bound(request)>MAX_BODY_BYTES:raise InterfaceError('complete client body exceeds v4 admission')
    return {'threadId':thread,'input':[{'type':'text','text':request.json_text,'text_elements':[]}],
            'environments':[],'runtimeWorkspaceRoots':[],'model':profile.MODEL,'effort':effort(request.stage),
            'summary':'none','serviceTierForTurn':'default','outputSchema':profile.output_schema(request)}


def audit_payload(body,request,global_text):
    expected=effort(request.stage)
    if body.get('reasoning')!={'effort':expected,'context':'all_turns'}:raise ValueError('per-stage reasoning effort mismatch')
    metadata=profile.strict_loads(body.get('client_metadata',{}).get('x-codex-turn-metadata','null'))
    if type(metadata) is not dict or metadata.get('reasoning_effort')!=expected:raise ValueError('per-stage metadata effort mismatch')
    # Preserve the original checker and every information-channel invariant.
    # Normalize only the two asserted effort fields for its fixed-medium contract.
    normalized=deepcopy(body);normalized['reasoning']['effort']='medium';metadata['reasoning_effort']='medium'
    normalized['client_metadata']['x-codex-turn-metadata']=wire(metadata)
    result=profile.audit_payload(normalized,request,global_text)
    if len(wire(body).encode('utf-8'))>profile.body_bound(request):raise ValueError('actual complete body exceeds bound')
    result.update(actual_reasoning_effort=expected,actual_complete_body_bytes=len(wire(body).encode('utf-8')),
                  effort_normalization_scope='two separately asserted effort fields only; all other original structural checks unchanged')
    return result


class Transport(SubscriptionTransport):
    transport_id='codex-chatgpt-subscription-rollback-math-v4'

    def generate(self,identity,request):
        if identity.key in self.seen:raise UnknownDispatch('never retry a subscription identity')
        self.check_hashes()
        with tempfile.TemporaryDirectory(prefix='rollback-v4-actor-',dir=self.scratch_root) as cwd:
            server=AppServer(self.executable,cwd,profile.OVERRIDES+profile.PROVIDER_OVERRIDES)
            phase='initialize';observation={}
            try:
                server.initialize()
                phase='account'
                if (server.rpc('account/read',{'refreshToken':False}).get('account') or {}).get('type')!='chatgpt':
                    raise ProtocolError('ChatGPT_subscription_signin_required')
                phase='quota'
                quota=quota_snapshot(server.rpc('account/rateLimits/read',{}));check_quota(quota)
                phase='configuration'
                profile.check_config(server.rpc('config/read',{'includeLayers':False})['config'])
                phase='thread'
                started=server.rpc('thread/start',profile.thread_parameters(cwd))
                if started.get('model')!=profile.MODEL or started.get('modelProvider')!=profile.PROVIDER:
                    raise ProtocolError('model_or_provider_mismatch')
                if started.get('runtimeWorkspaceRoots') or started['thread'].get('turns') or started['thread'].get('environments'):
                    raise ProtocolError('unexpected_workspace_or_prior_state')
                sources={str(Path(x).resolve()).casefold() for x in started.get('instructionSources',[])}
                if sources!={str(self.global_instructions.resolve()).casefold()}:raise ProtocolError('unexpected_instruction_source')
                thread=started['thread']['id'];params=turn_parameters(thread,request);self.seen.add(identity.key)
                phase='generation'
                turn=server.rpc('turn/start',params)['turn']['id']
                phase='collect';result=collect(server,thread,turn,timeout=RESPONSE_OBSERVATION_SECONDS,observation=observation)
                result.metadata.update(quota_before=quota,complete_body_byte_bound=profile.body_bound(request),
                    thread_id=thread,turn_id=turn,immutable_model_revision=None,reasoning_effort=effort(request.stage))
                return result
            except ProtocolError as error:raise DiagnosedProtocolError(error,phase,observation) from None
            except AccountingError:raise DiagnosedProtocolError(ProtocolError('invalid_subscription_usage'),phase,observation) from None
            finally:server.close()
