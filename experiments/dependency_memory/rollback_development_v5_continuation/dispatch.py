"""Receipt-only reconstruction and safe diagnostics; no repeated provider calls."""
from dataclasses import asdict
from pathlib import Path
import threading
import time

from .accounting import CallUnknown
from ..rollback_development_v5.accounting import Stopped
from ..rollback_development_v5.common import read, save_new, sha
from ..rollback_development_v5.dispatch import Dispatcher as OriginalDispatcher
from ..rollback_development_v5.audit import ReplayMismatch
from ..rollback_math_followup_v4.observe import METHODS, ITEMS, ERROR_CODES, RPCS, SERVER_ERRORS
from ..rollback_pilot.subscription.accounting import Usage
from ..rollback_pilot.subscription.transport import Response

PHASES = {"initialize", "account", "quota", "configuration", "thread", "generation", "collect", "unknown"}
GLOBAL_REASONS = {"ChatGPT_subscription_signin_required", "model_or_provider_mismatch", "unexpected_workspace_or_prior_state",
                  "unexpected_instruction_source", "quota_missing", "subscription_allowance_unavailable",
                  "individual_limit_unavailable", "quota_windows_missing", "included_limit_reached_or_unknown",
                  "requested_model_unavailable", "tool_or_external_information_attempt", "unexpected_thread_or_turn"}


def safe_diagnostic(error):
    value = getattr(error, "diagnostic", None)
    if type(value) is not dict:
        return {"version": 1, "phase": "unknown", "reason_code": "unclassified_controller_error", "observation": {}}
    reason = value.get("reason_code")
    result = {"version": 1, "phase": value.get("phase") if value.get("phase") in PHASES else "unknown",
              "reason_code": reason if reason in ERROR_CODES | {"rpc_error", "unclassified_protocol_error"} else "unclassified_protocol_error"}
    if result["reason_code"] == "rpc_error":
        if value.get("rpc_method") in RPCS and type(value.get("rpc_numeric_code")) is int:
            result.update(rpc_method=value["rpc_method"], rpc_numeric_code=value["rpc_numeric_code"])
    observation = value.get("observation")
    observation = observation if type(observation) is dict else {}
    retained = {}
    for field, allowed in (("method_counts", METHODS | {"other"}), ("item_counts", ITEMS | {"unrecognized_item"})):
        raw = observation.get(field)
        if type(raw) is dict:
            retained[field] = {k: v for k, v in raw.items() if k in allowed and type(v) is int and v >= 0}
    for field, allowed in (("server_error_codes", SERVER_ERRORS), ("turn_statuses", {"completed", "failed", "interrupted", "inProgress", "other"})):
        raw = observation.get(field)
        if type(raw) is list:
            retained[field] = [v for v in raw if type(v) is str and v in allowed]
    result["observation"] = retained
    return result


def systemic(diagnostic):
    return (diagnostic["phase"] in {"initialize", "account", "quota", "configuration", "thread", "unknown"}
            or diagnostic["reason_code"] in GLOBAL_REASONS
            or bool(set(diagnostic["observation"].get("server_error_codes", [])) & {"authenticationError", "usageLimitExceeded", "modelUnavailable"}))


class Dispatcher(OriginalDispatcher):
    def __init__(self, folder, manifest, ledger, transport_factory, *, historical=()):
        super().__init__(Path(folder), manifest, ledger, transport_factory)
        self.historical = {r["call_id"]: r for r in historical}
        self.replay_used = set()
        self.replay_lock = threading.Lock()

    def __call__(self, identity, request):
        self.check_sources()
        if identity.key in self.historical:
            old = self.historical[identity.key]
            with self.replay_lock:
                if identity.key in self.replay_used:
                    raise ReplayMismatch("historical identity reconstructed twice")
                self.replay_used.add(identity.key)
            if old["identity"] != asdict(identity) or old["request_hash"] != sha(request.json_text):
                self.ledger.stop("historical_request_mismatch")
                raise ReplayMismatch("historical request differs from restored public state")
            path = self.folder / "requests" / (identity.key + ".json")
            if not path.is_file() or read(path) != request.data():
                self.ledger.stop("historical_request_mismatch")
                raise ReplayMismatch("historical request evidence changed")
            if old["state"] != "completed":
                raise CallUnknown("preserved_unknown_identity")
            value = read(self.folder / "responses" / (identity.key + ".json"))
            if value["usage"] != old["usage"] or value["metadata"] != old["metadata"]:
                self.ledger.stop("historical_response_mismatch")
                raise ReplayMismatch("historical response and ledger disagree")
            return Response(value["text"], Usage(**value["usage"]), value["metadata"], value["capped"])
        if self.ledger.stopped():
            raise Stopped("global_stop")
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
        except Exception as error:
            self.ledger.unknown(identity, type(error).__name__, diagnostic=safe_diagnostic(error), fatal=True)
            raise Stopped("evidence_write_failed") from None
        try:
            response = self.local.transport.generate(identity, request)
        except Exception as error:
            diagnostic = safe_diagnostic(error)
            fatal = systemic(diagnostic)
            try:
                save_new(self.folder / "diagnostics" / (identity.key + ".json"), diagnostic)
            except Exception:
                self.ledger.unknown(identity, "diagnostic_write_failed", diagnostic=diagnostic, fatal=True)
                raise Stopped("evidence_write_failed") from None
            self.ledger.unknown(identity, type(error).__name__, diagnostic=diagnostic, fatal=fatal)
            if fatal:
                raise Stopped("systemic_transport_failure") from None
            raise CallUnknown("unknown_dispatch") from None
        try:
            save_new(self.folder / "responses" / (identity.key + ".json"),
                     {"text": response.text, "usage": vars(response.usage), "metadata": response.metadata,
                      "capped": response.capped, "elapsed_seconds": time.monotonic() - started})
            self.ledger.complete(identity, response.usage, response.metadata, time.monotonic() - started)
            return response
        except Exception as error:
            diagnostic = safe_diagnostic(error)
            self.ledger.unknown(identity, type(error).__name__, diagnostic=diagnostic, fatal=True)
            raise Stopped("response_evidence_or_accounting_failed") from None
