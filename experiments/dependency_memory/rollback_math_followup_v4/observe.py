"""Observe enum counts without changing the sealed collector's acceptance rules."""
import re

from ..rollback_pilot.subscription.process import ProtocolError
from ..rollback_pilot.subscription.transport import collect as sealed_collect

METHODS={'thread/tokenUsage/updated','item/started','item/completed','turn/completed','error','model/rerouted','model/verification'}
ITEMS={'userMessage','agentMessage','reasoning','commandExecution','mcpToolCall','webSearch','imageView','codeMode','customToolCall','dynamicToolCall'}
ERROR_CODES={'unexpected_thread_or_turn','requested_model_unavailable','provider_or_generation_failure',
    'one_generation_guard_absent','generation_timeout','tool_or_external_information_attempt','single_answer_and_usage_required',
    'oversized_protocol_event','invalid_protocol_json','appserver_closed','appserver_write_failed','appserver_timeout',
    'unexpected_server_request','rpc_missing_result','unexpected_rpc_event_volume','rpc_timeout',
    'ChatGPT_subscription_signin_required','model_or_provider_mismatch','unexpected_workspace_or_prior_state',
    'unexpected_instruction_source','quota_missing','subscription_allowance_unavailable','individual_limit_unavailable',
    'quota_windows_missing','included_limit_reached_or_unknown','invalid_subscription_usage'}
RPCS={'initialize','account/read','account/rateLimits/read','config/read','thread/start','turn/start'}
SERVER_ERRORS={'sessionBudgetExceeded','usageLimitExceeded','authenticationError','internalServerError','modelUnavailable','other'}


def safe_reason(error):
    raw=str(error)
    if raw in ERROR_CODES:return {'reason_code':raw}
    match=re.fullmatch(r'rpc_error:([A-Za-z/]+):(-?\d{1,10})',raw)
    if match and match[1] in RPCS:return {'reason_code':'rpc_error','rpc_method':match[1],'rpc_numeric_code':int(match[2])}
    return {'reason_code':'unclassified_protocol_error'}


class DiagnosedProtocolError(ProtocolError):
    def __init__(self,error,phase,observation):
        phase=phase if phase in {'initialize','account','quota','configuration','thread','generation','collect'} else 'unknown'
        self.diagnostic={'version':1,'phase':phase,**safe_reason(error),'observation':observation}
        super().__init__(self.diagnostic['reason_code'])


class ObservingServer:
    def __init__(self,server,observation):
        self.server=server;self.pending=list(server.notifications);server.notifications=[];self.notifications=[]
        self.observation=observation;observation.update(method_counts={},item_counts={},server_error_codes=[],turn_statuses=[])

    def receive(self,timeout):
        message=self.pending.pop(0) if self.pending else self.server.receive(timeout)
        method=message.get('method');name=method if type(method) is str and method in METHODS else 'other'
        counts=self.observation['method_counts'];counts[name]=counts.get(name,0)+1
        params=message.get('params',{})
        if method in {'item/started','item/completed'}:
            kind=params.get('item',{}).get('type');kind=kind if type(kind) is str and kind in ITEMS else 'unrecognized_item'
            counts=self.observation['item_counts'];counts[kind]=counts.get(kind,0)+1
        if method=='error':
            code=params.get('error',{}).get('codexErrorInfo');code=code if type(code) is str and code in SERVER_ERRORS else 'other'
            if code not in self.observation['server_error_codes']:self.observation['server_error_codes'].append(code)
        if method=='turn/completed':
            status=params.get('turn',{}).get('status');status=status if type(status) is str and status in {'completed','failed','interrupted','inProgress'} else 'other'
            if status not in self.observation['turn_statuses']:self.observation['turn_statuses'].append(status)
        return message


def collect(server,thread,turn,*,timeout=900,observation=None):
    observation=observation if observation is not None else {}
    result=sealed_collect(ObservingServer(server,observation),thread,turn,timeout=timeout)
    result.metadata['protocol_observation']=observation
    return result
