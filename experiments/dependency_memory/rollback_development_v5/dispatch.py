"""Durable call envelopes, source checks, fail-stop dispatch, no automatic retries."""
import threading
import time

from .accounting import Stopped
from .common import ROOT, read, sha, save_new
from ..rollback_math_followup_v4.transport import Transport


class Dispatcher:
    def __init__(self, folder, manifest, ledger, transport_factory):
        self.folder, self.manifest, self.ledger = folder, manifest, ledger
        self.transport_factory = transport_factory
        self.local = threading.local()

    def check_sources(self):
        for row in self.manifest["source_bindings"]:
            if sha((ROOT / row["path"]).read_bytes()) != row["sha256"]:
                self.ledger.stop("source_drift")
                raise Stopped("source_drift")

    def __call__(self, identity, request):
        if self.ledger.stopped():
            raise Stopped("global_stop")
        self.check_sources()
        if not hasattr(self.local, "transport"):
            try:
                self.local.transport = self.transport_factory()
            except Exception:
                self.ledger.stop("transport_preflight_failed")
                raise Stopped("transport_preflight_failed") from None
        try:
            self.ledger.admit(identity, sha(request.json_text))
        except Stopped:
            raise
        except Exception:
            self.ledger.stop("admission_invariant_failed")
            raise Stopped("admission_invariant_failed") from None
        started = time.monotonic()
        try:
            save_new(self.folder / "requests" / (identity.key + ".json"), request.data())
            response = self.local.transport.generate(identity, request)
            save_new(self.folder / "responses" / (identity.key + ".json"),
                     {"text": response.text, "usage": vars(response.usage), "metadata": response.metadata,
                      "capped": response.capped, "elapsed_seconds": time.monotonic() - started})
            self.ledger.complete(identity, response.usage, response.metadata, time.monotonic() - started)
            return response
        except Exception as error:
            self.ledger.unknown(identity, type(error).__name__)
            raise Stopped("unknown_dispatch") from None


def live_factory(executable, global_instructions, preflight, scratch_root):
    return lambda: Transport(executable, global_instructions, preflight, scratch_root)
