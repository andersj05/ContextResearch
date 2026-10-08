"""Preserve the tested episode state machine with new explicitly frozen limits."""
from pathlib import Path
import time

from ..rollback_pilot.accounting import Identity
from ..rollback_pilot.controller import write_new
from ..rollback_pilot.records import InterfaceError, Record, wire
from ..rollback_pilot.subscription.accounting import Ledger, Usage, AccountingError
from ..rollback_pilot.subscription.calibration import check_bindings
from ..rollback_pilot.subscription.profile import source_ids
from ..rollback_pilot.subscription.transport import Response
from ..rollback_pilot.transport import UnknownDispatch
from ..rollback_pilot.cohort_v1.controller import Controller as PriorController
from .transport import Renderer, WRITER_BYTES


class Dispatcher:
    def __init__(self,folder,ledger,transport,manifest,renderer):
        self.folder=Path(folder);self.ledger=ledger;self.transport=transport;self.renderer=renderer
        self.manifest=manifest;self.identities={Identity(**x).key for x in manifest['schedule']};self.stopped=False

    def call(self,identity,request):
        if self.stopped:raise UnknownDispatch('study allocation stopped')
        if identity.key not in self.identities:raise InterfaceError('undeclared frozen identity')
        if not self.renderer.fits(request):raise InterfaceError('complete client body exceeds v4 bound')
        check_bindings(self.manifest['source_bindings'])
        self.ledger.plan(identity,request.hash);self.ledger.reserve(identity)
        write_new(self.folder/'requests'/(identity.key+'.json'),request.json_text+'\n')
        self.ledger.dispatch(identity,request.hash);started=time.monotonic()
        try:
            result=self.transport.generate(identity,request)
            if type(result) is not Response or type(result.text) is not str:raise AccountingError('invalid subscription response')
            write_new(self.folder/'responses'/(identity.key+'.json'),wire({'text':result.text,'usage':vars(result.usage) if type(result.usage) is Usage else None,
                'metadata':result.metadata,'capped':result.capped,'elapsed_seconds':time.monotonic()-started})+'\n')
            self.ledger.complete(identity,result.usage,'capped' if result.capped else 'received',result.metadata)
            return result
        except Exception as error:
            diagnostic=getattr(error,'diagnostic',None)
            if type(diagnostic) is not dict:diagnostic={'version':1,'reason_code':'unclassified_non_protocol_error'}
            write_new(self.folder/'failures'/(identity.key+'.json'),wire(diagnostic)+'\n')
            self.ledger.unknown(identity,type(error).__name__);self.stopped=True
            raise UnknownDispatch('dispatch/metering unknown; stop entire study') from error


class Controller(PriorController):
    def __init__(self,folder,manifest,transport,code_checker):
        self.folder=Path(folder);self.manifest=manifest;self.launch_id=manifest['launch_id'];self.code_checker=code_checker
        self.renderer=Renderer();self.ledger=Ledger(self.folder/'ledger.sqlite',max_calls=208)
        self.dispatcher=Dispatcher(self.folder,self.ledger,transport,manifest,self.renderer)

    def _record(self,task,stage,checkpoint=None,branches=(),feedback=None,arm=None,draw=None,slot=1,lesson=None,summary=None):
        request=(self.renderer.continuation(arm,task,checkpoint,branches,feedback,lesson,summary) if stage=='terminal'
                 else self.renderer.render(stage,task,checkpoint,branches,feedback))
        identity=Identity(self.launch_id,task.task_id,stage,slot=slot,arm=arm,draw=draw)
        response=self.dispatcher.call(identity,request)
        if response.capped:raise InterfaceError('capped_output')
        if stage in {'lesson','summary'} and len(response.text.encode('utf-8'))>WRITER_BYTES:raise InterfaceError('writer_visible_byte_cap')
        supplied=source_ids(task)
        if checkpoint:supplied.update(f'C.fact{i+1}' for i in range(len(checkpoint.data()['facts'])))
        for index,branch in enumerate(branches):
            supplied.add(f'B{index+1}');supplied.update(f'B{index+1}.observation{i+1}' for i in range(len(branch.data()['observations'])))
        if feedback:supplied.add(feedback.data()['receipt_id'])
        options=[x['id'] for x in checkpoint.data()['tentative_options']] if checkpoint else []
        return Record.parse(stage,response.text,task,supplied=supplied,option_ids=options),request
