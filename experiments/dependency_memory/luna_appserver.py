"""Fresh-process Luna subscription client using the official app-server protocol.

Generation requires a recorded isolation audit. Credentials remain owned by the
official CLI. No direct HTTP endpoint, token extraction, or API-key fallback.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading
import time

from codex_subscription import MODEL, REVIEWED_CLI_SHA256
from luna_budget import CreditBudget
from request_contracts import request_bytes


PROVIDER = "luna_research"
PROVIDER_OVERRIDES = (
    'forced_login_method="chatgpt"',
    'model_provider="luna_research"',
    'model_providers.luna_research.name="Luna Research"',
    'model_providers.luna_research.requires_openai_auth=true',
    'model_providers.luna_research.request_max_retries=0',
    'model_providers.luna_research.stream_max_retries=0',
    'model_providers.luna_research.supports_websockets=false',
    'model_providers.luna_research.wire_api="responses"',
)


class TransportError(RuntimeError):
    pass


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate response key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON")))


class AppServer:
    """One local child; only explicitly sent RPCs are executed."""

    def __init__(self, executable, cwd, overrides, *, timeout=45):
        command = [str(executable), "app-server", "--stdio"]
        for value in overrides:
            command.extend(("-c", value))
        blocked_env = {"OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN", "OPENAI_BASE_URL"}
        environment = {key: value for key, value in os.environ.items() if key not in blocked_env}
        self.process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
            env=environment,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.timeout = timeout
        self.queue = queue.Queue()
        self.notifications = []
        self.next_id = 0
        self.closed = False
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        try:
            for line in self.process.stdout:
                try:
                    self.queue.put(strict_json(line))
                except ValueError:
                    self.queue.put({"fatal": "invalid_protocol_json"})
        finally:
            self.queue.put({"fatal": "appserver_closed"})

    def send(self, value):
        self.process.stdin.write(json.dumps(value, separators=(",", ":")) + "\n")
        self.process.stdin.flush()

    def receive(self, timeout=None):
        try:
            message = self.queue.get(timeout=self.timeout if timeout is None else timeout)
        except queue.Empty as error:
            raise TransportError("appserver_timeout") from error
        if "fatal" in message:
            raise TransportError(message["fatal"])
        if "method" in message and "id" in message:
            # No interactive approval, tool, credential, or data response supplied.
            raise TransportError("unexpected_server_request:" + message["method"])
        return message

    def rpc(self, method, params):
        self.next_id += 1
        number = self.next_id
        self.send({"id": number, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            if time.monotonic() >= deadline:
                raise TransportError("rpc_timeout")
            message = self.receive(max(.01, deadline - time.monotonic()))
            if message.get("id") == number:
                if "error" in message:
                    error = message["error"]
                    raise TransportError(f"rpc_error:{method}:{error.get('code')}")
                return message["result"]
            self.notifications.append(message)

    def initialize(self):
        self.rpc("initialize", {"clientInfo": {"name": "contextresearch_luna", "version": "0.1"},
                                "capabilities": {"experimentalApi": True}})
        self.send({"method": "initialized"})

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)


def quota_snapshot(value):
    if value.get("ordinaryUsageAllowed") is False:
        raise TransportError("ordinary_usage_not_allowed")
    snapshots = value.get("rateLimitsByLimitId") or {"codex": value.get("rateLimits")}
    result = {}
    for name, row in snapshots.items():
        if row:
            result[name] = {key: row.get(key) for key in ("primary", "secondary", "credits",
                "rateLimitReachedType", "individualLimit", "spendControlReached")}
    return result


def check_quota(snapshot):
    if not snapshot:
        raise TransportError("missing_quota_snapshot")
    observed = False
    for row in snapshot.values():
        if row.get("rateLimitReachedType") is not None:
            raise TransportError("account_rate_limit_reached")
        if row.get("spendControlReached") is True:
            raise TransportError("account_spend_control_reached")
        if row.get("individualLimit") and row["individualLimit"].get("remainingPercent", 0) <= 0:
            raise TransportError("individual_spend_limit_reached")
        for key in ("primary", "secondary"):
            window = row.get(key)
            if window is not None:
                used = window.get("usedPercent")
                if type(used) not in (int, float) or not 0 <= used < 80:
                    raise TransportError("quota_guard_80_percent")
                observed = True
    if not observed:
        raise TransportError("no_observed_allowance_window")


class LunaClient:
    def __init__(self, executable, audit, *, budget=None, timeout=120, progress=None):
        self.executable = str(Path(executable).resolve())
        self.audit = audit
        self.budget = budget or CreditBudget()
        self.timeout = timeout
        self.last_metadata = {}
        self.stopped = False
        self.progress = progress
        # Audited constants are supplied by the separate offline wire probe.
        from luna_isolation import ISOLATION_OVERRIDES, thread_parameters, turn_parameters
        self.isolation_overrides = ISOLATION_OVERRIDES
        self.thread_parameters = thread_parameters
        self.turn_parameters = turn_parameters
        if hashlib.sha256(Path(self.executable).read_bytes()).hexdigest() != REVIEWED_CLI_SHA256:
            raise TransportError("unreviewed_cli_binary")
        if audit.get("isolation_passed") is not True:
            raise TransportError("isolation_audit_not_ready")
        profile_hash = hashlib.sha256(json.dumps(ISOLATION_OVERRIDES).encode()).hexdigest()
        if audit.get("isolation_overrides_sha256") != profile_hash:
            raise TransportError("isolation_profile_changed_since_audit")
        self.global_instructions = Path.home() / ".codex" / "AGENTS.md"
        self.global_hash = hashlib.sha256(self.global_instructions.read_text(encoding="utf-8").encode()).hexdigest()
        if self.global_hash != audit.get("global_instructions_sha256"):
            raise TransportError("global_instructions_changed_since_audit")
        cases = {row["case"]: row for row in audit.get("cases", [])}
        if set(cases) != {"final_message", "tool_call", "http_503", "truncated_sse"} or any(
            row.get("http_attempts") != 1 or row.get("authorization_present") is not False
            for row in cases.values()):
            raise TransportError("incomplete_single_generation_audit")
        self.audit = {**audit, "launch_ready": True}
        self.metadata = {
            "version": "luna_subscription_development_v0.4", "model": MODEL,
            "model_revision": "mutable alias; no immutable revision exposed",
            "cli_version": "0.155.0-alpha.9.2", "cli_sha256": REVIEWED_CLI_SHA256,
            "isolation_profile_sha256": profile_hash, "reasoning_effort": "low",
            "service_tier": "default", "provider": PROVIDER,
            "authentication": "managed ChatGPT subscription; checked before every dispatch",
            "global_instructions_sha256": self.global_hash,
            "model_sampling_seed": None, "http_and_stream_retries": 0,
            "generation_guard": "one-generation weighted rollout budget; controlled sessionBudgetExceeded is retained",
            "public_background": "Fixed base/developer instructions, reviewed global GitHub guidance, pure wrapper registry, fixed rollout reminder",
            "state": "New app-server process and ephemeral thread per request; no environments, archive, prior outputs, or session links",
            "maximum_wire_body_bytes": 32768,
            "account_quota_stop_used_percent": 80,
            "budget": self.budget.snapshot(),
            "audit_scope": "Pinned client no-auth loopback serialization plus managed production-auth preflight; server internals unobserved",
            "provider_routing_source": "openai/codex@da18000cae9884ab45f83b2d07fbd5a220a1de39:codex-rs/model-provider-info/src/lib.rs",
        }

    def complete(self, request):
        if self.stopped:
            raise TransportError("client_stopped_after_failure")
        if hasattr(self, "global_instructions") and hashlib.sha256(
            self.global_instructions.read_text(encoding="utf-8").encode()).hexdigest() != self.global_hash:
            self.stopped = True
            raise TransportError("global_instructions_changed_during_run")
        payload = request_bytes(request)
        from luna_isolation import wire_body_byte_bound
        wire_bound = wire_body_byte_bound(request)
        if wire_bound > 32768:
            raise ValueError("complete_request_exceeds_wire_bound")
        self.last_metadata = {"dispatched": False, "model": MODEL, "provider": PROVIDER}
        self.last_metadata["wire_body_byte_bound"] = wire_bound
        ticket = None
        with tempfile.TemporaryDirectory(prefix="contextresearch-luna-") as cwd:
            server = AppServer(self.executable, cwd, (*self.isolation_overrides, *PROVIDER_OVERRIDES))
            try:
                server.initialize()
                account = server.rpc("account/read", {"refreshToken": False})
                if (account.get("account") or {}).get("type") != "chatgpt":
                    raise TransportError("chatgpt_subscription_required")
                before = quota_snapshot(server.rpc("account/rateLimits/read", {}))
                check_quota(before)
                self.last_metadata["quota_before"] = before
                config = server.rpc("config/read", {"includeLayers": False})["config"]
                from luna_isolation import validate_effective_config
                self.last_metadata["effective_isolation"] = validate_effective_config(config)
                provider = config.get("model_providers", {}).get(PROVIDER, {})
                if (config.get("model_provider") != PROVIDER
                    or provider.get("base_url") is not None
                    or provider.get("requires_openai_auth") is not True
                    or provider.get("request_max_retries") != 0
                    or provider.get("stream_max_retries") != 0
                    or provider.get("supports_websockets") is not False
                    or any(provider.get(key) for key in ("env_key", "experimental_bearer_token",
                        "http_headers", "env_http_headers", "query_params", "auth", "aws"))):
                    raise TransportError("provider_contract_mismatch")
                if any(row.get("enabled", True) for row in config.get("mcp_servers", {}).values()):
                    raise TransportError("unexpected_enabled_mcp_server")
                start = server.rpc("thread/start", self.thread_parameters(cwd, PROVIDER))
                if start.get("model") != MODEL or start.get("modelProvider") != PROVIDER:
                    raise TransportError("unexpected_model_or_provider")
                if start.get("runtimeWorkspaceRoots") or start["thread"].get("turns"):
                    raise TransportError("unexpected_prior_state_or_roots")
                if hasattr(self, "global_instructions"):
                    sources = {str(Path(path).resolve()).casefold() for path in start.get("instructionSources", [])}
                    if sources != {str(self.global_instructions.resolve()).casefold()}:
                        raise TransportError("unexpected_instruction_source")
                thread_id = start["thread"]["id"]
                self.last_metadata["thread_id"] = thread_id
                ticket = self.budget.reserve()
                self.last_metadata.update(dispatched=True, attempt_ticket=ticket)
                turn = server.rpc("turn/start", self.turn_parameters(thread_id, request))
                turn_id = turn["turn"]["id"]
                self.last_metadata["turn_id"] = turn_id
                deadline = time.monotonic() + self.timeout
                usage, answers, guard_stop = None, [], False
                pending = server.notifications
                server.notifications = []
                done = False
                while not done:
                    if time.monotonic() >= deadline:
                        raise TransportError("generation_timeout")
                    event = pending.pop(0) if pending else server.receive(max(.01, deadline-time.monotonic()))
                    method, params = event.get("method"), event.get("params", {})
                    if params.get("threadId", thread_id) != thread_id:
                        raise TransportError("unexpected_thread_event")
                    if params.get("turnId", turn_id) != turn_id:
                        raise TransportError("unexpected_turn_event")
                    if method == "model/rerouted":
                        raise TransportError("model_rerouted")
                    if method == "thread/tokenUsage/updated":
                        usage = params["tokenUsage"]["total"]
                    elif method in ("item/started", "item/completed"):
                        item = params.get("item", {})
                        if item.get("type") not in ("userMessage", "agentMessage", "reasoning"):
                            raise TransportError("tool_or_unknown_item:" + str(item.get("type")))
                        if method == "item/completed" and item["type"] == "agentMessage":
                            answers.append(item.get("text"))
                    elif method == "error":
                        if (params.get("error") or {}).get("codexErrorInfo") == "sessionBudgetExceeded":
                            guard_stop = True
                        else:
                            raise TransportError("provider_error")
                    elif method == "turn/completed":
                        if params["turn"].get("id") != turn_id:
                            raise TransportError("unexpected_completed_turn")
                        controlled_stop = (params["turn"].get("error") or {}).get("codexErrorInfo") == "sessionBudgetExceeded"
                        guard_stop = guard_stop or controlled_stop
                        if params["turn"].get("status") != "completed" and not controlled_stop:
                            raise TransportError("turn_not_completed:" + str(params["turn"].get("status")))
                        done = True
                if usage is None or len(answers) != 1 or not isinstance(answers[0], str):
                    raise TransportError("missing_usage_or_ambiguous_answer")
                if type(usage.get("inputTokens")) is not int or usage["inputTokens"] <= 0:
                    raise TransportError("nonpositive_input_usage_invalidates_generation_guard")
                if not guard_stop:
                    raise TransportError("missing_audited_generation_guard_termination")
                self.last_metadata["usage"] = {target: usage.get(source, 0) for source, target in (
                    ("inputTokens", "input_tokens"), ("cachedInputTokens", "cached_input_tokens"),
                    ("outputTokens", "output_tokens"), ("reasoningOutputTokens", "reasoning_output_tokens"))}
                self.last_metadata["usage"]["cache_write_input_tokens"] = usage.get("cacheWriteInputTokens")
                self.last_metadata["cache_write_tokens_reported"] = "cacheWriteInputTokens" in usage
                self.last_metadata["harness_termination"] = "session_budget_exceeded" if guard_stop else "completed"
                self.last_metadata["credit_accounting"] = self.budget.settle(ticket, usage)
                ticket = None
                # Quota changes are account-wide, not attributed to this request.
                after = quota_snapshot(server.rpc("account/rateLimits/read", {}))
                check_quota(after)
                self.last_metadata["quota_after"] = after
                self.last_metadata.update(status="completed", tool_events_observed=0,
                                          provider_generation_count_observed=1,
                                          provider_http_request_count=None)
                if getattr(self, "progress", None):
                    self.progress(self.budget.attempts, self.last_metadata)
                return strict_json(answers[0])
            except Exception as error:
                self.stopped = True
                self.last_metadata.update(status="failed", error_type=type(error).__name__,
                                          error_code=str(error)[:200])
                if ticket is not None:
                    self.last_metadata["credit_accounting"] = self.budget.fail(ticket, reason="generation_failure")
                raise
            finally:
                server.close()
