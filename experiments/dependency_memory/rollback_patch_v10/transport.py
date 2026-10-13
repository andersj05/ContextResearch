"""Explicit v10 body admission with the inherited subscription isolation.

The v7 generation sequence and localhost probe are copied into this new version
only to bind turn_parameters locally. No historical module/global is patched.
The v8 full streaming executable hash, exact empty MCP registry, quota gate,
one-response collector and zero-retry configuration remain unchanged.
"""
from copy import deepcopy
import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading

from .common import MAX_BODY_BYTES, MAX_INPUT_TEXT_BYTES
from ..rollback_parallel_v8.transport import Transport as StreamingTransport
from ..rollback_checkpoint_v7.client import (
    RESOURCE_HELPERS, REGISTRY_SHA256, NAMESPACE_SHA256, CASES, DIAGNOSTIC_CASES,
    check_config, inspect_thread, check_tool_rejection, audit_payload,
    preflight as baseline_preflight,
)
from ..rollback_pilot.records import InterfaceError, strict_loads, wire
from ..rollback_pilot.contexts import Request
from ..rollback_pilot.subscription import profile
from ..rollback_pilot.subscription.process import AppServer, ProtocolError
from ..rollback_pilot.subscription.transport import check_quota, quota_snapshot
from ..rollback_pilot.subscription.accounting import AccountingError
from ..rollback_pilot.transport import UnknownDispatch
from ..rollback_math_followup_v4.transport import effort, RESPONSE_OBSERVATION_SECONDS
from ..rollback_math_followup_v4.observe import collect, DiagnosedProtocolError, safe_reason


def fits_body(request):
    return profile.body_bound(request) <= MAX_BODY_BYTES


def fits(request):
    return fits_body(request) and len(request.json_text.encode("utf-8")) <= MAX_INPUT_TEXT_BYTES


def turn_parameters(thread, request):
    if not fits(request):
        raise InterfaceError("complete client body exceeds v10 admission")
    return {"threadId": thread,
            "input": [{"type": "text", "text": request.json_text, "text_elements": []}],
            "environments": [], "runtimeWorkspaceRoots": [], "model": profile.MODEL,
            "effort": effort(request.stage), "summary": "none", "serviceTierForTurn": "default",
            "outputSchema": profile.output_schema(request)}


class Transport(StreamingTransport):
    transport_id = "codex-chatgpt-subscription-rollback-patch-v10"

    def generate(self, identity, request):
        if identity.key in self.seen:
            raise UnknownDispatch("never retry a subscription identity")
        # Reject before creating a provider process; contexts.fits uses this cap.
        if not fits(request):
            raise InterfaceError("complete client body exceeds v10 admission")
        self.check_hashes()
        with tempfile.TemporaryDirectory(prefix="rollback-v10-actor-", dir=self.scratch_root) as cwd:
            server = AppServer(self.executable, cwd, profile.OVERRIDES + profile.PROVIDER_OVERRIDES)
            phase, observation = "initialize", {}
            try:
                server.initialize()
                phase = "account"
                if (server.rpc("account/read", {"refreshToken": False}).get("account") or {}).get("type") != "chatgpt":
                    raise ProtocolError("ChatGPT_subscription_signin_required")
                phase = "quota"
                quota = quota_snapshot(server.rpc("account/rateLimits/read", {}))
                check_quota(quota)
                phase = "configuration"
                check_config(server.rpc("config/read", {"includeLayers": False})["config"])
                phase = "thread"
                started = server.rpc("thread/start", profile.thread_parameters(cwd))
                inventory = inspect_thread(server, started, cwd, self.global_instructions)
                thread = started["thread"]["id"]
                params = turn_parameters(thread, request)
                self.seen.add(identity.key)
                phase = "generation"
                turn = server.rpc("turn/start", params)["turn"]["id"]
                phase = "collect"
                result = collect(server, thread, turn, timeout=RESPONSE_OBSERVATION_SECONDS, observation=observation)
                result.metadata.update(quota_before=quota, complete_body_byte_bound=profile.body_bound(request),
                                       complete_body_admission_bytes=MAX_BODY_BYTES,
                                       input_text_bytes=len(request.json_text.encode("utf-8")),
                                       input_text_byte_limit=MAX_INPUT_TEXT_BYTES,
                                       thread_id=thread, turn_id=turn, immutable_model_revision=None,
                                       reasoning_effort=effort(request.stage), mcp_resource_isolation=inventory,
                                       preflight_registry_sha256=REGISTRY_SHA256)
                return result
            except ProtocolError as error:
                raise DiagnosedProtocolError(error, phase, observation) from None
            except AccountingError:
                raise DiagnosedProtocolError(ProtocolError("invalid_subscription_usage"), phase, observation) from None
            finally:
                server.close()


def live_factory(executable, global_instructions, checked, scratch_root):
    return lambda: Transport(executable, global_instructions, checked, scratch_root)


def preflight(executable, global_instructions, scratch_root):
    """Account/negative probes plus exact capacity; runner adds v10 shape probes."""
    from .contexts import render
    from .tasks import generate
    result = baseline_preflight(executable, global_instructions, scratch_root)
    result["v10_complete_body_admission_bytes"] = MAX_BODY_BYTES
    result["v10_input_text_byte_limit"] = MAX_INPUT_TEXT_BYTES
    request = render(generate(split="fixture", per_family=1)[0])
    result["v10_capacity_preflight"] = capacity_preflight(
        executable, Path(global_instructions).read_text(encoding="utf-8"), scratch_root, request)
    return result


def capacity_request(request, target_bytes):
    """Synthetic ASCII padding for localhost capacity tests, never a study input."""
    data = request.data()
    difference = target_bytes - profile.body_bound(request)
    if type(target_bytes) is not int or difference < 0:
        raise ValueError("capacity fixture must grow the original request")
    data["messages"][1]["content"] += "x" * difference
    value = Request(request.stage, wire(data), 0, "v10-localhost-capacity-fixture")
    observed = profile.body_bound(value)
    if observed != target_bytes:
        raise ValueError("capacity fixture bound is not exact")
    return Request(value.stage, value.json_text, observed, value.counter_id)


def capacity_preflight(executable, global_text, scratch_root, request):
    """Probe the binding input-text limit; body limit is also checked offline.

    The installed client says one million characters. A UTF-8 byte ceiling is
    deliberately conservative for non-ASCII input; the exact boundary fixture
    uses ASCII, for which bytes and characters agree. Nothing is truncated.
    """
    input_bytes = len(request.json_text.encode("utf-8"))
    boundary = capacity_request(request, profile.body_bound(request) + MAX_INPUT_TEXT_BYTES - input_bytes)
    accepted = run_case(executable, global_text, boundary, "final_message", scratch_root)
    overflow = capacity_request(boundary, profile.body_bound(boundary) + 1)
    try:
        turn_parameters("capacity-overflow-must-not-dispatch", overflow)
    except InterfaceError:
        rejected = True
    else:
        raise ValueError("one-byte body overflow was admitted")
    body_overflow = capacity_request(request, MAX_BODY_BYTES + 1)
    if fits_body(body_overflow):
        raise ValueError("one-byte complete-body overflow was admitted")
    return {"passed": True, "admission_bytes": MAX_BODY_BYTES,
            "input_text_byte_limit": MAX_INPUT_TEXT_BYTES,
            "accepted_input_text_bytes": len(boundary.json_text.encode("utf-8")),
            "accepted_body_bound_bytes": profile.body_bound(boundary),
            "body_overflow_rejected": True,
            "at_limit_accepted": accepted["accepted_transport"], "above_limit_rejected": rejected,
            "zero_model_calls": True, "model_calls": 0,
            "complete_body_admission_bytes": MAX_BODY_BYTES,
            "exact_bound_bytes": profile.body_bound(boundary), "exact_bound_localhost": accepted,
            "overflow_input_text_bytes": len(overflow.json_text.encode("utf-8")),
            "overflow_bound_bytes": profile.body_bound(overflow),
            "overflow_rejected_before_provider": rejected, "real_model_generations": 0,
            "scope": "binding one-MiB input-text boundary tested on unauthenticated localhost; four-MiB complete-body overflow checked independently offline; synthetic padding is not a semantic task or model result"}


def run_case(executable, global_text, request, case, scratch_root):
    """One unauthenticated localhost response; never a live model generation."""
    if case not in CASES + DIAGNOSTIC_CASES:
        raise ValueError("unknown mock case")
    observed, attempts = [], 0
    answer = '{"synthetic":"fixture"}'

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            nonlocal attempts
            attempts += 1
            raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            if self.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            if "Authorization" in self.headers:
                observed.append({"authorization_present": True})
            else:
                observed.append({"authorization_present": False,
                                 "body": strict_loads(raw.decode()), "bytes": len(raw)})
            item = {"id": "fixture_message", "type": "message", "role": "assistant", "status": "completed",
                    "content": [{"type": "output_text", "text": answer, "annotations": []}]}
            assistant_item = item
            if case in {"tool_call", "clock_with_answer"} or case in RESOURCE_HELPERS:
                arguments = '{server:"node_repl",uri:"fixture://unavailable"}' if case == "read_mcp_resource" else '{}'
                code = ("text(await tools.clock__curr_time({}));" if case in {"tool_call", "clock_with_answer"}
                        else f"text(await tools.{case}({arguments}));")
                item = {"id": "fixture_tool", "type": "custom_tool_call", "name": "exec",
                        "call_id": "fixture_tool", "input": code}
            items = [item, {**item, "id": "fixture_message2"}] if case == "duplicate_answer" else [item]
            if case == "clock_with_answer":
                items = [assistant_item, item]
            completed = {"id": "fixture_response", "status": "completed", "output": items,
                         "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2,
                                   "input_tokens_details": {"cached_tokens": 0},
                                   "output_tokens_details": {"reasoning_tokens": 0}}}
            if case == "missing_usage":
                completed.pop("usage")
            events = [{"type": "response.created", "response": {"id": "fixture_response", "status": "in_progress", "output": []}}]
            events.extend({"type": "response.output_item.done", "output_index": index, "item": item}
                          for index, item in enumerate(items))
            events.append({"type": "response.completed", "response": completed})
            if case == "truncated_sse":
                events = events[:1]
            if case == "http_503":
                status, content_type, content = 503, "application/json", b'{"error":{"message":"fixture","type":"server_error"}}'
            else:
                status, content_type = 200, "text/event-stream"
                content = "".join("data: " + wire(event) + "\n\n" for event in events).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

    http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    provider = ('model_provider="rollback_mock"', 'model_providers.rollback_mock.name="Unauthenticated loopback"',
                f'model_providers.rollback_mock.base_url="http://127.0.0.1:{http.server_port}"',
                'model_providers.rollback_mock.requires_openai_auth=false', 'model_providers.rollback_mock.request_max_retries=0',
                'model_providers.rollback_mock.stream_max_retries=0', 'model_providers.rollback_mock.supports_websockets=false',
                'model_providers.rollback_mock.wire_api="responses"')
    accepted, failure, response, observation, inventory = False, None, None, {}, None
    try:
        with tempfile.TemporaryDirectory(prefix="rollback-v10-mock-", dir=scratch_root) as cwd:
            server = AppServer(executable, cwd, profile.OVERRIDES + provider, timeout=30)
            try:
                server.initialize()
                check_config(server.rpc("config/read", {"includeLayers": False})["config"], provider=False)
                started = server.rpc("thread/start", profile.thread_parameters(cwd, "rollback_mock"))
                inventory = inspect_thread(server, started, cwd, provider="rollback_mock")
                thread = started["thread"]["id"]
                turn = server.rpc("turn/start", turn_parameters(thread, request))["turn"]["id"]
                try:
                    response = collect(server, thread, turn, timeout=30, observation=observation)
                    accepted = True
                except (ProtocolError, ValueError) as error:
                    failure = str(error)
            finally:
                server.close()
    finally:
        http.shutdown()
        http.server_close()
    if attempts != 1 or len(observed) != 1 or observed[0]["authorization_present"]:
        raise ValueError("mock retry/authentication invariant failed")
    payload = audit_payload(observed[0]["body"], request, global_text)
    if observed[0]["bytes"] > profile.body_bound(request):
        raise ValueError("actual wire body exceeds bound")
    if ((case not in DIAGNOSTIC_CASES and accepted != (case == "final_message"))
            or (accepted and response.text != answer)):
        raise ValueError("mock acceptance expectation failed: " + case)
    if case in RESOURCE_HELPERS:
        check_tool_rejection(failure, observation)
    if case == "tool_call" and failure != "single_answer_and_usage_required":
        raise ValueError("clock probe rejection changed from pinned client observation")
    if case == "clock_with_answer" and accepted is not True:
        raise ValueError("composite clock visibility changed from pinned client observation")
    return {"case": case, "http_attempts": attempts, "authorization_present": False,
            "v10_complete_body_admission_bytes": MAX_BODY_BYTES,
            "accepted_transport": accepted, "rejection": failure, "payload_audit": payload,
            "actual_wire_bytes": observed[0]["bytes"], "real_model_generations": 0,
            "protocol_observation": observation, "mcp_resource_isolation": inventory,
            "diagnostic_only": case in DIAGNOSTIC_CASES,
            "safe_failure_reason": safe_reason(ProtocolError(failure)) if failure else None,
            "negative_probe_scope": ("observed MCP tool item rejected by collector" if case in RESOURCE_HELPERS
                                     else "clock fixture rejected for absence of an accepted answer; no tool event exposed"
                                     if case == "tool_call" else None),
            "diagnostic_scope": ("composite clock and answer accepted without an exposed tool item; one request and guard prevent tool-result feedback to another generation"
                                 if case == "clock_with_answer" else None)}

