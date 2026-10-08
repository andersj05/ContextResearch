"""Durable single-dispatch boundary for subscription generations."""
from pathlib import Path
import time

from ..controller import write_new
from ..records import wire
from ..transport import UnknownDispatch
from .accounting import AccountingError, Usage
from .profile import body_bound, MAX_BODY_BYTES
from .transport import Response


class Dispatcher:
    def __init__(self, folder, ledger, transport):
        self.folder, self.ledger, self.transport, self.stopped = Path(folder), ledger, transport, False

    def call(self, identity, request):
        if self.stopped:
            raise UnknownDispatch("allocation already stopped")
        if body_bound(request) > MAX_BODY_BYTES:
            raise ValueError("complete client body exceeds admission")
        self.ledger.plan(identity, request.hash)
        self.ledger.reserve(identity)
        write_new(self.folder / "requests" / (identity.key + ".json"), request.json_text + "\n")
        self.ledger.dispatch(identity, request.hash)
        start = time.monotonic()
        try:
            result = self.transport.generate(identity, request)
            if type(result) is not Response or type(result.text) is not str:
                raise AccountingError("invalid subscription response")
            write_new(self.folder / "responses" / (identity.key + ".json"), wire({"text": result.text,
                "usage": vars(result.usage) if type(result.usage) is Usage else None, "metadata": result.metadata,
                "capped": result.capped, "elapsed_seconds": time.monotonic() - start}) + "\n")
            self.ledger.complete(identity, result.usage, "capped" if result.capped else "received", result.metadata)
            return result
        except Exception as error:
            self.ledger.unknown(identity, type(error).__name__)
            self.stopped = True
            raise UnknownDispatch("subscription dispatch/metering unknown; allocation stopped") from error
