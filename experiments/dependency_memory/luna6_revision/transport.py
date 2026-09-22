"""Separately pinned subscription adapter with durable pre-dispatch reservations."""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import tempfile
import time

from luna_appserver import AppServer, PROVIDER_OVERRIDES, check_quota, quota_snapshot, strict_json
from . import profile
from .preflight import config_check
from .protocol import request_bytes

RESERVATION = Decimal("7.65")
CREDIT_CAP = Decimal("20")
CALL_CAP = 144


def usage_cost(usage):
    fields = ("inputTokens", "cachedInputTokens", "outputTokens", "reasoningOutputTokens", "totalTokens")
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in fields):
        raise ValueError("Incomplete or invalid usage")
    i, c, o, r, total = (usage[k] for k in fields)
    if not 0 < i < 272000 or c > i or r > o or total != i + o or o > 128000:
        raise ValueError("Usage violates declared limits")
    return (Decimal(i-c)*Decimal("2.5") + Decimal(c)*Decimal(".25") + Decimal(o)*Decimal("12.5"))/1000000


def save(path, value):
    raw = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(raw, encoding="utf-8", newline="\n")
    temporary.replace(path)


class Client:
    def __init__(self, executable, global_instructions, directory, audit):
        self.executable, self.global_instructions, self.directory = Path(executable), Path(global_instructions), directory
        self.audit = audit
        self.spent, self.attempts, self.stopped = Decimal(0), 0, False
        self.calls = []
        if audit.get("isolation_passed") is not True or len(audit.get("cases", [])) != 4:
            raise ValueError("Missing isolation audit")
        self.check_hashes()

    def check_hashes(self):
        for key, raw in (("client_sha256", self.executable.read_bytes()),
                         ("global_instructions_sha256", self.global_instructions.read_text(encoding="utf-8").encode()),
                         ("profile_sha256", json.dumps(profile.ISOLATION_OVERRIDES).encode())):
            if hashlib.sha256(raw).hexdigest() != self.audit[key]:
                raise ValueError("Pinned input changed: " + key)

    def complete(self, identity, request):
        if self.stopped:
            raise RuntimeError("Launch stopped")
        if self.attempts >= CALL_CAP or self.spent + RESERVATION > CREDIT_CAP:
            raise RuntimeError("Allocation exhausted")
        self.check_hashes()
        raw = request_bytes(request)
        bound = profile.wire_body_byte_bound(request)
        if bound > profile.MAX_WIRE_BYTES:
            raise ValueError("Audited provider-body bound exceeded")
        path = self.directory / "calls" / (identity + ".json")
        if path.exists():
            raise RuntimeError("Never retry an existing identity")
        record = {"identity": identity, "request": request, "request_sha256": hashlib.sha256(raw).hexdigest(),
                  "model": profile.MODEL, "effort": "medium", "wire_body_byte_bound": bound,
                  "started_at": datetime.now(timezone.utc).isoformat(), "dispatched": False}
        start_time = time.perf_counter()
        self.last = record
        with tempfile.TemporaryDirectory(prefix="luna6-isolated-") as cwd:
            server = AppServer(self.executable, cwd, (*profile.ISOLATION_OVERRIDES, *PROVIDER_OVERRIDES))
            try:
                server.initialize()
                if (server.rpc("account/read", {"refreshToken": False}).get("account") or {}).get("type") != "chatgpt":
                    raise RuntimeError("Managed ChatGPT login required")
                record["quota_before"] = quota_snapshot(server.rpc("account/rateLimits/read", {}))
                record["quota_mode"] = check_quota(record["quota_before"], used_limit=100, credit_backed=True)
                record["effective_config"] = config_check(server.rpc("config/read", {"includeLayers": False})["config"])
                started = server.rpc("thread/start", profile.thread_parameters(cwd, "luna_research"))
                if started.get("model") != profile.MODEL or started.get("modelProvider") != "luna_research":
                    raise RuntimeError("Model or provider mismatch")
                if started.get("runtimeWorkspaceRoots") or started["thread"].get("turns") or started["thread"].get("environments"):
                    raise RuntimeError("Unexpected state channel")
                sources = {str(Path(x).resolve()).casefold() for x in started.get("instructionSources", [])}
                if sources != {str(self.global_instructions.resolve()).casefold()}:
                    raise RuntimeError("Unexpected instruction source")
                thread = started["thread"]["id"]
                # Durable reservation precedes the possibly-generating RPC.
                self.attempts += 1
                record.update(dispatched=True, status="reserved", reservation_credits=str(RESERVATION))
                save(path, record)
                turn = server.rpc("turn/start", profile.turn_parameters(thread, request))["turn"]["id"]
                pending, server.notifications = server.notifications, []
                usage, answers, usage_events, guard = None, [], 0, False
                deadline = time.monotonic() + 240
                while True:
                    if time.monotonic() >= deadline:
                        raise RuntimeError("Generation timeout")
                    message = pending.pop(0) if pending else server.receive(max(.01, deadline-time.monotonic()))
                    method, params = message.get("method"), message.get("params", {})
                    if params.get("threadId", thread) != thread or params.get("turnId", turn) != turn:
                        raise RuntimeError("Unexpected thread or turn event")
                    if method == "model/rerouted":
                        raise RuntimeError("Requested model was rerouted")
                    if method == "thread/tokenUsage/updated":
                        usage = params["tokenUsage"]["total"]
                        usage_events += 1
                    elif method in ("item/started", "item/completed"):
                        item = params.get("item", {})
                        if item.get("type") not in ("userMessage", "agentMessage", "reasoning"):
                            raise RuntimeError("Tool or unexpected item attempted")
                        if method == "item/completed" and item["type"] == "agentMessage":
                            answers.append(item.get("text"))
                    elif method == "error":
                        if (params.get("error") or {}).get("codexErrorInfo") != "sessionBudgetExceeded":
                            raise RuntimeError("Provider generation error")
                        guard = True
                    elif method == "turn/completed":
                        terminal = params["turn"]
                        guard |= (terminal.get("error") or {}).get("codexErrorInfo") == "sessionBudgetExceeded"
                        if terminal.get("id") != turn or (terminal.get("status") != "completed" and not guard):
                            raise RuntimeError("Incomplete turn")
                        break
                if usage_events != 1 or len(answers) != 1 or not isinstance(answers[0], str) or not guard:
                    raise RuntimeError("Single-generation contract violated")
                credit = usage_cost(usage)
                if credit > RESERVATION:
                    raise RuntimeError("Usage exceeded reservation")
                self.spent += credit
                record.update(status="completed", usage=usage, planning_credits=str(credit),
                              raw_answer=answers[0], wall_seconds=time.perf_counter()-start_time,
                              tool_items=0, usage_events=usage_events, harness_termination="sessionBudgetExceeded")
                try:
                    response = strict_json(answers[0])
                    record["response"] = response
                except ValueError:
                    response = None
                    record["response"] = None
                    record["policy_error"] = "invalid_json"
                # Persist a metered answer before any account-wide postcheck.
                # A later quota stop cannot erase or relaunch this generation.
                save(path, record)
                self.calls.append(record)
                print(json.dumps({"call": self.attempts, "id": identity, "credits": str(self.spent), "output_tokens": usage["outputTokens"]}), flush=True)
                return response
            except Exception as error:
                self.stopped = True
                record.update(status="transport_failure", error_type=type(error).__name__, error=str(error)[:160], wall_seconds=time.perf_counter()-start_time)
                save(path, record)
                raise
            finally:
                server.close()
