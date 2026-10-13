"""October 12 installed-client compatibility, scoped only to v7.

The observed alpha.17.2 client always declares three generic MCP resource
helpers. Their exact metadata and full visible registry are pinned here. Every
configured MCP server must be disabled and its runtime inventory empty before
each generation. The old collector rejects results with observed tool items.
This verifies absence of usable MCP providers, not impossibility of tool code
starting. No historical profile, transport, or Python module global is mutated.
"""
from copy import deepcopy
import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import tempfile
import threading

from .common import now
from ..rollback_pilot.records import digest, strict_loads, wire
from ..rollback_pilot.subscription import profile
from ..rollback_pilot.subscription.process import AppServer, ProtocolError
from ..rollback_pilot.subscription.transport import (
    SubscriptionTransport, check_quota, quota_snapshot,
)
from ..rollback_pilot.subscription.accounting import AccountingError
from ..rollback_pilot.transport import UnknownDispatch
from ..rollback_math_followup_v4.transport import (
    turn_parameters, effort, audit_payload as historical_audit_payload,
    RESPONSE_OBSERVATION_SECONDS,
)
from ..rollback_math_followup_v4.observe import collect, DiagnosedProtocolError, safe_reason


RESOURCE_HELPERS = ("list_mcp_resource_templates", "list_mcp_resources", "read_mcp_resource")
REGISTRY_SHA256 = "9500ae1e14fbdc4e98c806b8fcd89c568af5820929317d30b78a909d21cde744"
NAMESPACE_SHA256 = "fe615be5c698d60c6b19e66e412024f6761dca29c2952ef15aab136b714be449"
CASES = ("final_message", "tool_call", "http_503", "truncated_sse", "missing_usage",
         "duplicate_answer", *RESOURCE_HELPERS)
DIAGNOSTIC_CASES = ("clock_with_answer",)


def check_config(config, *, provider=True):
    result = profile.check_config(config, provider=provider)
    # Fail closed on a new configured provider, even one described as disabled.
    rows = config.get("mcp_servers")
    if type(rows) is not dict or set(rows) != {"node_repl"} or rows["node_repl"].get("enabled") is not False:
        raise ProtocolError("unexpected_workspace_or_prior_state")
    return {**result, "all_configured_mcp_servers_disabled": True,
            "configured_mcp_server_names": ["node_repl"]}


def check_mcp_inventory(value):
    """Retain counts only, never server credentials, resource names or content."""
    if type(value) is not dict or "nextCursor" not in value or value["nextCursor"] is not None:
        raise ProtocolError("unexpected_workspace_or_prior_state")
    rows = value.get("data")
    if (type(rows) is not list or len(rows) != 1 or type(rows[0]) is not dict
            or rows[0].get("name") != "node_repl"
            or rows[0].get("runtimeStatus") != "disabled"
            or rows[0].get("tools") != {} or rows[0].get("resources") != []
            or rows[0].get("resourceTemplates") != []):
        raise ProtocolError("unexpected_workspace_or_prior_state")
    return {"server_count": 1, "disabled_server_count": 1,
            "tool_count": 0, "resource_count": 0, "resource_template_count": 0,
            "complete_inventory": True}


def inspect_thread(server, started, cwd, global_instructions=None, provider=profile.PROVIDER):
    if started.get("model") != profile.MODEL or started.get("modelProvider") != provider:
        raise ProtocolError("model_or_provider_mismatch")
    if started.get("runtimeWorkspaceRoots") or started["thread"].get("turns") or started["thread"].get("environments"):
        raise ProtocolError("unexpected_workspace_or_prior_state")
    if global_instructions is not None:
        sources = {str(Path(path).resolve()).casefold() for path in started.get("instructionSources", [])}
        if sources != {str(Path(global_instructions).resolve()).casefold()}:
            raise ProtocolError("unexpected_instruction_source")
    return check_mcp_inventory(server.rpc("mcpServerStatus/list", {
        "threadId": started["thread"]["id"], "detail": "full", "limit": 100,
    }))


def audit_payload(body, request, global_text):
    """Verify the exact new declarations, then reuse all historical assertions.

    Only three already-verified metadata entries are removed from a diagnostic
    copy for the legacy name assertion. The sent payload and visible tool
    descriptions are never changed. Original bytes remain the capacity measure.
    """
    metadata = strict_loads(body.get("client_metadata", {}).get("x-codex-turn-metadata", "null"))
    if type(metadata) is not dict:
        raise ValueError("missing exact v7 client metadata")
    namespaces = metadata.get("tool_namespaces_info")
    embedded = [item for item in body.get("input", []) if item.get("type") == "additional_tools"]
    if (digest(wire(namespaces)) != NAMESPACE_SHA256 or len(embedded) != 1
            or digest(wire(embedded[0].get("tools"))) != REGISTRY_SHA256):
        raise ValueError("unrecognized v7 tool registry or metadata")
    raw_bytes = len(wire(body).encode("utf-8"))
    bound = profile.body_bound(request)
    fixed_bytes = raw_bytes - len(wire(request.json_text).encode("utf-8")) - len(wire(profile.output_schema(request)).encode("utf-8"))
    if fixed_bytes > profile.FIXED_BYTES or raw_bytes > bound:
        raise ValueError("actual v7 payload exceeds original byte bound")
    normalized = deepcopy(body)
    normalized_metadata = deepcopy(metadata)
    for name in RESOURCE_HELPERS:
        del normalized_metadata["tool_namespaces_info"]["functions"]["functions"][name]
    normalized["client_metadata"]["x-codex-turn-metadata"] = wire(normalized_metadata)
    result = historical_audit_payload(normalized, request, global_text)
    result.update(
        registry_sha256=REGISTRY_SHA256, namespace_metadata_sha256=NAMESPACE_SHA256,
        registry_names={name: sorted(row["functions"]) for name, row in namespaces.items()},
        declared_inert_mcp_helpers=list(RESOURCE_HELPERS),
        compatibility_normalization="diagnostic copy only: three pinned metadata entries removed for the legacy name assertion; sent bytes and tool definitions unchanged",
        actual_complete_body_bytes=raw_bytes, complete_body_bytes_observed=raw_bytes,
        fixed_body_bytes_observed=fixed_bytes, complete_body_bytes_bound=bound,
        scope="installed client loopback with empty disabled MCP inventory; unchanged collector rejects observed tool items; does not prove tool code cannot start",
    )
    return result


def check_tool_rejection(failure, observation):
    """A negative probe must reach the unchanged collector's tool rejection."""
    items = observation.get("item_counts", {})
    forbidden = any(count > 0 for kind, count in items.items()
                    if kind not in {"userMessage", "agentMessage", "reasoning"})
    if failure != "tool_or_external_information_attempt" or not forbidden:
        raise ValueError("mock tool probe did not verify tool rejection")


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
        with tempfile.TemporaryDirectory(prefix="rollback-v7-mock-", dir=scratch_root) as cwd:
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


def preflight(executable, global_instructions, scratch_root):
    """Read-only account gate plus all negative cases on actual v7 payloads."""
    from .prepare import generate
    from .contexts import render
    from .engine import initial_state
    executable, global_instructions, scratch_root = Path(executable), Path(global_instructions), Path(scratch_root)
    scratch_root.mkdir(parents=True, exist_ok=True)
    global_text = global_instructions.read_text(encoding="utf-8")
    version = subprocess.run([str(executable), "--version"], capture_output=True, text=True, check=True,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.strip()
    server = AppServer(executable, scratch_root, profile.OVERRIDES + profile.PROVIDER_OVERRIDES)
    try:
        server.initialize()
        account_type = (server.rpc("account/read", {"refreshToken": False}).get("account") or {}).get("type")
        if account_type != "chatgpt":
            raise ValueError("subscription sign-in required")
        quota = quota_snapshot(server.rpc("account/rateLimits/read", {}))
        check_quota(quota)
        config = check_config(server.rpc("config/read", {"includeLayers": False})["config"])
        models = [row for row in server.rpc("model/list", {"includeHidden": True}).get("data", [])
                  if row.get("model") == profile.MODEL]
        if len(models) != 1 or not any(row.get("reasoningEffort") == "medium" for row in models[0].get("supportedReasoningEfforts", [])):
            raise ValueError("GPT-6 Luna medium absent from signed-in catalog")
    finally:
        server.close()
    task = generate(split="fixture", replicates=1)[0]
    request = render(task, initial_state(task))
    cases = []
    for case in CASES:
        cases.append(run_case(executable, global_text, request, case, scratch_root))
        print(wire({"v7_client_mock_case": case, "pass": True}), flush=True)
    diagnostics = [run_case(executable, global_text, request, case, scratch_root)
                   for case in DIAGNOSTIC_CASES]
    return {"version": "rollback-checkpoint-v7-client-2026-10-12", "checked_utc": now(),
            "client_version": version, "executable_sha256": digest(executable.read_bytes()),
            "global_instructions_sha256": digest(global_text),
            "configuration_sha256": digest(str(profile.OVERRIDES + profile.PROVIDER_OVERRIDES)),
            "model_catalog_entry": models[0], "account_type": account_type, "quota": quota,
            "configuration_check": config, "cases": cases, "registry_sha256": REGISTRY_SHA256,
            "compatibility_diagnostics": diagnostics,
            "namespace_metadata_sha256": NAMESPACE_SHA256,
            "declared_inert_mcp_helpers": list(RESOURCE_HELPERS),
            "mcp_inventory_checked_before_every_generation": True,
            "serialization_and_retry_audit_passed": True, "real_model_generations": 0,
            "configured_output_cap_verified": False, "provider_tokenizer_verified": False,
            "immutable_model_revision": None,
            "compatibility_scope": "exact new declarations accepted only with disabled empty MCP inventory; original body bytes counted; unchanged collector rejects observed tool items; clock fixture lacks an accepted answer"}


class Transport(SubscriptionTransport):
    transport_id = "codex-chatgpt-subscription-rollback-checkpoint-v7"

    def check_hashes(self):
        super().check_hashes()
        if (self.preflight.get("registry_sha256") != REGISTRY_SHA256
                or self.preflight.get("namespace_metadata_sha256") != NAMESPACE_SHA256
                or self.preflight.get("mcp_inventory_checked_before_every_generation") is not True):
            raise ValueError("v7 exact-registry preflight required")

    def generate(self, identity, request):
        if identity.key in self.seen:
            raise UnknownDispatch("never retry a subscription identity")
        self.check_hashes()
        with tempfile.TemporaryDirectory(prefix="rollback-v7-actor-", dir=self.scratch_root) as cwd:
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
