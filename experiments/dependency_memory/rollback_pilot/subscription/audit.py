"""Installed-client serialization/negative probes against unauthenticated localhost."""
import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading

from ..records import digest, strict_loads, wire
from . import profile
from .process import AppServer, ProtocolError
from .transport import collect

CASES = ("final_message", "tool_call", "http_503", "truncated_sse", "missing_usage", "duplicate_answer")


def run_case(executable, global_text, request, case, scratch_root):
    if case not in CASES:
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
                # This provider is strictly unauthenticated; never log the header.
                observed.append({"authorization_present": True})
            else:
                observed.append({"authorization_present": False, "body": strict_loads(raw.decode()), "bytes": len(raw)})
            item = {"id": "fixture_message", "type": "message", "role": "assistant", "status": "completed",
                    "content": [{"type": "output_text", "text": answer, "annotations": []}]}
            if case == "tool_call":
                item = {"id": "fixture_tool", "type": "custom_tool_call", "name": "exec", "call_id": "fixture_tool",
                        "input": "text(await tools.clock__curr_time({}));"}
            items = [item, {**item, "id": "fixture_message2"}] if case == "duplicate_answer" else [item]
            completed = {"id": "fixture_response", "status": "completed", "output": items,
                         "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2,
                                   "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 0}}}
            if case == "missing_usage":
                completed.pop("usage")
            events = [{"type": "response.created", "response": {"id": "fixture_response", "status": "in_progress", "output": []}}]
            events.extend({"type": "response.output_item.done", "output_index": i, "item": x} for i, x in enumerate(items))
            events.append({"type": "response.completed", "response": completed})
            if case == "truncated_sse":
                events = events[:1]
            if case == "http_503":
                status, content_type, content = 503, "application/json", b'{"error":{"message":"fixture","type":"server_error"}}'
            else:
                status, content_type = 200, "text/event-stream"
                content = "".join("data: " + wire(x) + "\n\n" for x in events).encode()
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
    accepted, failure, response = False, None, None
    try:
        with tempfile.TemporaryDirectory(prefix="rollback-mock-", dir=scratch_root) as cwd:
            server = AppServer(executable, cwd, profile.OVERRIDES + provider, timeout=30)
            try:
                server.initialize()
                profile.check_config(server.rpc("config/read", {"includeLayers": False})["config"], provider=False)
                started = server.rpc("thread/start", profile.thread_parameters(cwd, "rollback_mock"))
                if started["thread"].get("environments") != []:
                    raise ValueError("mock has environment access")
                thread = started["thread"]["id"]
                turn = server.rpc("turn/start", profile.turn_parameters(thread, request))["turn"]["id"]
                try:
                    response = collect(server, thread, turn, timeout=30)
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
    body = observed[0]["body"]
    payload = profile.audit_payload(body, request, global_text)
    if observed[0]["bytes"] > profile.body_bound(request):
        raise ValueError("actual wire body exceeds bound")
    if accepted != (case == "final_message"):
        raise ValueError("mock acceptance expectation failed: " + case)
    if accepted and response.text != answer:
        raise ValueError("mock answer changed")
    # A schema-independent synthetic answer is intentional: this audits transport,
    # while the calibration host separately parses task-specific schemas.
    return {"case": case, "http_attempts": attempts, "authorization_present": False,
            "accepted_transport": accepted, "rejection": failure, "payload_audit": payload,
            "actual_wire_bytes": observed[0]["bytes"], "real_model_generations": 0}
