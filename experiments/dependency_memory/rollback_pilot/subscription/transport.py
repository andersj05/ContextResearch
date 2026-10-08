"""Fresh-process subscription generations through the official app-server."""
from dataclasses import dataclass
from pathlib import Path
import tempfile
import time

from ..records import digest
from ..transport import UnknownDispatch
from .accounting import Usage
from . import profile
from .process import AppServer, ProtocolError


@dataclass(frozen=True)
class Response:
    text: str
    usage: Usage
    metadata: dict
    capped: bool = False


def quota_snapshot(value):
    rows = value.get("rateLimitsByLimitId") or {"codex": value.get("rateLimits")}
    return {name: {**{key: row.get(key) for key in ("primary", "secondary", "spendControlReached", "individualLimit", "rateLimitReachedType")},
                   "ordinaryUsageAllowed": value.get("ordinaryUsageAllowed")} for name, row in rows.items() if row}


def check_quota(snapshot):
    if type(snapshot) is not dict or not snapshot:
        raise ProtocolError("quota_missing")
    seen = False
    for row in snapshot.values():
        if row.get("ordinaryUsageAllowed") is not True or row.get("spendControlReached") is not False or row.get("rateLimitReachedType") is not None:
            raise ProtocolError("subscription_allowance_unavailable")
        individual = row.get("individualLimit")
        if individual is not None and (type(individual) is not dict or type(individual.get("remainingPercent")) not in (int, float) or not 0 < individual["remainingPercent"] <= 100):
            raise ProtocolError("individual_limit_unavailable")
        for key in ("primary", "secondary"):
            window = row.get(key)
            if window is not None:
                seen = True
                if type(window) is not dict or type(window.get("usedPercent")) not in (int, float) or not 0 <= window["usedPercent"] < 100:
                    raise ProtocolError("included_limit_reached_or_unknown")
    if not seen:
        raise ProtocolError("quota_windows_missing")


def collect(server, thread, turn, *, timeout=240):
    pending, server.notifications = server.notifications, []
    usage, answers, usage_count, guard = None, [], 0, False
    forbidden = []
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        message = pending.pop(0) if pending else server.receive(max(.01, deadline - time.monotonic()))
        method, params = message.get("method"), message.get("params", {})
        if params.get("threadId", thread) != thread or params.get("turnId", turn) != turn:
            raise ProtocolError("unexpected_thread_or_turn")
        if method in {"model/rerouted", "model/verification"}:
            raise ProtocolError("requested_model_unavailable")
        if method == "thread/tokenUsage/updated":
            usage = params.get("tokenUsage", {}).get("total")
            usage_count += 1
        elif method in {"item/started", "item/completed"}:
            item = params.get("item", {})
            if item.get("type") not in {"userMessage", "agentMessage", "reasoning"}:
                forbidden.append(item.get("type"))
            if method == "item/completed" and item.get("type") == "agentMessage":
                answers.append(item.get("text"))
        elif method == "error":
            if params.get("error", {}).get("codexErrorInfo") != "sessionBudgetExceeded":
                raise ProtocolError("provider_or_generation_failure")
            guard = True
        elif method == "turn/completed":
            terminal = params["turn"]
            guard |= (terminal.get("error") or {}).get("codexErrorInfo") == "sessionBudgetExceeded"
            if terminal.get("id") != turn or not guard or terminal.get("status") != "failed":
                raise ProtocolError("one_generation_guard_absent")
            break
    else:
        raise ProtocolError("generation_timeout")
    if forbidden:
        raise ProtocolError("tool_or_external_information_attempt")
    if usage_count != 1 or len(answers) != 1 or type(answers[0]) is not str:
        raise ProtocolError("single_answer_and_usage_required")
    metered = Usage.from_telemetry(usage)
    return Response(answers[0], metered, {"model": profile.MODEL, "usage_events": usage_count,
                    "tool_items": 0, "harness_termination": "sessionBudgetExceeded", "provider_request_count_scope": "one-response guard and zero-retry installed-client mock audit"})


class SubscriptionTransport:
    transport_id = "codex-chatgpt-subscription-rollback-v1"

    def __init__(self, executable, global_instructions, preflight, scratch_root):
        self.executable, self.global_instructions = Path(executable), Path(global_instructions)
        self.preflight, self.scratch_root = preflight, Path(scratch_root)
        self.scratch_root.mkdir(parents=True, exist_ok=True)
        if preflight.get("serialization_and_retry_audit_passed") is not True:
            raise ValueError("installed-client isolation audit required")
        self.seen = set()
        self.check_hashes()

    def check_hashes(self):
        if digest(self.executable.read_bytes()) != self.preflight["executable_sha256"]:
            raise ValueError("Codex executable changed")
        if digest(self.global_instructions.read_text(encoding="utf-8")) != self.preflight["global_instructions_sha256"]:
            raise ValueError("global instructions changed")
        if digest(str(profile.OVERRIDES + profile.PROVIDER_OVERRIDES)) != self.preflight["configuration_sha256"]:
            raise ValueError("isolation profile changed")

    def generate(self, identity, request):
        if identity.key in self.seen:
            raise UnknownDispatch("never retry a subscription identity")
        self.check_hashes()
        # Preflight happens before this identity's potentially-generating RPC.
        with tempfile.TemporaryDirectory(prefix="rollback-actor-", dir=self.scratch_root) as cwd:
            server = AppServer(self.executable, cwd, profile.OVERRIDES + profile.PROVIDER_OVERRIDES)
            try:
                server.initialize()
                account = server.rpc("account/read", {"refreshToken": False}).get("account") or {}
                if account.get("type") != "chatgpt":
                    raise ProtocolError("ChatGPT_subscription_signin_required")
                quota = quota_snapshot(server.rpc("account/rateLimits/read", {}))
                check_quota(quota)
                profile.check_config(server.rpc("config/read", {"includeLayers": False})["config"])
                started = server.rpc("thread/start", profile.thread_parameters(cwd))
                if started.get("model") != profile.MODEL or started.get("modelProvider") != profile.PROVIDER:
                    raise ProtocolError("model_or_provider_mismatch")
                if started.get("runtimeWorkspaceRoots") or started["thread"].get("turns") or started["thread"].get("environments"):
                    raise ProtocolError("unexpected_workspace_or_prior_state")
                sources = {str(Path(x).resolve()).casefold() for x in started.get("instructionSources", [])}
                if sources != {str(self.global_instructions.resolve()).casefold()}:
                    raise ProtocolError("unexpected_instruction_source")
                thread = started["thread"]["id"]
                params = profile.turn_parameters(thread, request)
                self.seen.add(identity.key)
                turn = server.rpc("turn/start", params)["turn"]["id"]
                result = collect(server, thread, turn)
                result.metadata.update(quota_before=quota, complete_body_byte_bound=profile.body_bound(request),
                                       thread_id=thread, turn_id=turn, immutable_model_revision=None)
                return result
            finally:
                server.close()
