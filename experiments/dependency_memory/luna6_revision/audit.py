# Derived from audit_luna_transport.py at 115496a; no production generation.
"""Audit installed Codex serialization against a local fake Responses server.

No real model or subscription-generation endpoint is contacted. This opt-in
integration check uses the real client binary, no-auth loopback HTTP, and one
synthetic public development request. Outputs contain allowlisted observations,
not uncontrolled provider transcripts or credential values.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
import threading

from artifact_workflow import Config
from codex_subscription import REVIEWED_CLI_SHA256
from luna_appserver import AppServer
from .profile import (ISOLATION_OVERRIDES, MAX_FIXED_WIRE_BYTES, MAX_WIRE_BYTES,
                            audit_payload, thread_parameters, turn_parameters,
                            schema_projection, wire_body_byte_bound)
from pilot_interface import inspection_request
from .protocol import request_bytes


def run_case(executable: str, global_instructions_text: str, case: str,
             public_request: dict | None = None) -> dict:
    if case not in {"final_message", "tool_call", "http_503", "truncated_sse"}:
        raise ValueError("Unknown synthetic case")
    observed = []
    if public_request is None:
        from .protocol import smoke_request
        public_request = smoke_request()
    public_text = request_bytes(public_request).decode()
    synthetic_final = synthetic_response(public_request)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            if self.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            observed.append({"path": self.path, "authorization_present": "Authorization" in self.headers,
                             "raw_wire_bytes": len(raw),
                             "body": json.loads(raw)})
            message = {"id": "synthetic_message", "type": "message", "role": "assistant",
                       "status": "completed", "content": [{"type": "output_text",
                       "text": synthetic_final, "annotations": []}]}
            if case == "tool_call":
                message = {"id": "synthetic_call", "type": "custom_tool_call", "name": "exec",
                           "call_id": "synthetic_call", "input": "text(ALL_TOOLS.map(x => x.name));"}
            events = [
                {"type": "response.created", "response": {"id": "synthetic_response", "status": "in_progress", "output": []}},
                {"type": "response.output_item.done", "output_index": 0, "item": message},
                {"type": "response.completed", "response": {"id": "synthetic_response", "status": "completed", "output": [message],
                 "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2,
                           "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 0}}}},
            ]
            status = 200
            content_type = "text/event-stream"
            if case == "http_503":
                status = 503
                content_type = "application/json"
                body = b'{"error":{"message":"synthetic error","type":"server_error"}}'
            else:
                if case == "truncated_sse":
                    events = events[:1]
                body = "".join("data: " + json.dumps(event) + "\n\n" for event in events).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    provider = (
        'model_provider="luna_mock"', 'model_providers.luna_mock.name="Local fake transport"',
        f'model_providers.luna_mock.base_url="http://127.0.0.1:{http.server_port}"',
        'model_providers.luna_mock.requires_openai_auth=false',
        'model_providers.luna_mock.request_max_retries=0', 'model_providers.luna_mock.stream_max_retries=0',
        'model_providers.luna_mock.supports_websockets=false', 'model_providers.luna_mock.wire_api="responses"',
    )
    try:
        with tempfile.TemporaryDirectory(prefix="luna-audit-empty-") as cwd:
            client = AppServer(executable, cwd, (*ISOLATION_OVERRIDES, *provider), timeout=30)
            try:
                client.initialize()
                started = client.rpc("thread/start", thread_parameters(cwd, "luna_mock"))
                if started["thread"].get("environments") != []:
                    raise ValueError("Environment access remained enabled")
                client.rpc("turn/start", turn_parameters(started["thread"]["id"], public_request))
                while not any(x.get("method") == "turn/completed" for x in client.notifications):
                    client.notifications.append(client.receive())
                notifications = client.notifications
            finally:
                client.close()
    finally:
        http.shutdown()
        http.server_close()
    if len(observed) != 1 or observed[0]["authorization_present"]:
        raise ValueError("Expected one unauthenticated local HTTP attempt")
    print(json.dumps({"synthetic_body_shape": {"keys": sorted(observed[0]["body"]),
          "model": observed[0]["body"].get("model"), "reasoning": observed[0]["body"].get("reasoning"),
          "tools": [{"type": x.get("type"), "name": x.get("name")} for x in observed[0]["body"].get("tools", [])],
          "input_types": [x.get("type") for x in observed[0]["body"].get("input", [])]}}), flush=True)
    payload_audit = audit_payload(observed[0]["body"], public_text=public_text,
                                  global_instructions_text=global_instructions_text)
    encoded_public_bytes = len(json.dumps(public_text, ensure_ascii=True).encode())
    encoded_schema_bytes = len(json.dumps(schema_projection(public_request["response_schema"]), ensure_ascii=True).encode())
    fixed_wire_bytes = observed[0]["raw_wire_bytes"] - encoded_public_bytes - encoded_schema_bytes
    if fixed_wire_bytes > MAX_FIXED_WIRE_BYTES or observed[0]["raw_wire_bytes"] > wire_body_byte_bound(public_request):
        raise ValueError("Fixed transport overhead exceeds the declared wire bound")
    finals = [x["params"]["item"]["text"] for x in notifications if x.get("method") == "item/completed"
              and x.get("params", {}).get("item", {}).get("type") == "agentMessage"]
    usage = [x["params"]["tokenUsage"] for x in notifications if x.get("method") == "thread/tokenUsage/updated"]
    terminals = [x["params"]["turn"] for x in notifications if x.get("method") == "turn/completed"]
    codes = [(x.get("error") or {}).get("codexErrorInfo") for x in terminals]
    if case in {"final_message", "tool_call"} and codes != ["sessionBudgetExceeded"]:
        raise ValueError("Rollout guard did not produce the expected controlled stop")
    if case == "final_message" and (finals != [synthetic_final] or len(usage) != 1):
        raise ValueError("Completed final response or complete usage absent")
    if case != "final_message" and finals:
        raise ValueError("Unexpected final response in negative control")
    return {"case": case, "http_attempts": len(observed), "authorization_present": False,
            "payload_audit": payload_audit, "final_response_count": len(finals),
            "observed_wire_bytes": observed[0]["raw_wire_bytes"],
            "fixed_wire_bytes_upper_observation": fixed_wire_bytes,
            "usage_records": len(usage), "terminal_statuses": [x.get("status") for x in terminals],
            "terminal_error_codes": codes, "real_model_generations": 0}


def synthetic_response(public_request: dict) -> str:
    request_bytes(public_request)
    return '{"memory":"synthetic"}'
