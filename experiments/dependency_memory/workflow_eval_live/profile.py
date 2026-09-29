# Derived from luna6_revision/profile.py at 1590deb; separately audited September 29.
"""Shared, locally audited Codex app-server isolation controls.

The current registry retains four functions wrappers plus clock access. Its
complete visible tool specification is pinned, and registry metadata rejects
every other namespace. All tool attempts are forbidden in accepted live turns.
Fresh threads and a local serialization audit do not establish server internals.
The subscription transport uses Python 3.11+ for standard-library TOML parsing;
the original offline mathematical diagnostics remain independent of that API.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

MODEL = "gpt-6-luna"
BASE_INSTRUCTIONS = (
    "Return a JSON object according to the supplied response schema. "
    "Use only the supplied user input."
)
DEVELOPER_INSTRUCTIONS = "This is a controlled test. Do not call tools."
ROLLOUT_GUARD_TEXT = "<rollout_budget>\nYou have 32768 weighted tokens left in the shared session token budget.\n</rollout_budget>"
ROLLOUT_GUARD_OVERRIDE = (
    "features.rollout_budget={enabled=true,limit_tokens=32768,"
    "prefill_token_weight=1000000.0,sampling_token_weight=1.0,reminder_at_remaining_tokens=[]}"
)
MAX_FIXED_WIRE_BYTES = 20000
MAX_WIRE_BYTES = 131072
ALLOWED_BODY_KEYS = {
    "client_metadata", "include", "input", "model", "parallel_tool_calls",
    "prompt_cache_key", "reasoning", "store", "stream", "text", "tool_choice",
    "tools", "instructions",
}

# A parent-map {} did not remove inherited MCP settings in the observed client.
# Live preflight must additionally reject any unexpected enabled MCP server.
ISOLATION_OVERRIDES = (
    'model_reasoning_effort="medium"', 'model_reasoning_summary="none"',
    'approval_policy="never"', 'web_search="disabled"',
    'project_doc_max_bytes=0', 'agents.enabled=false',
    'include_environment_context=false', 'include_permissions_instructions=false',
    'include_collaboration_mode_instructions=false', 'include_apps_instructions=false',
    'features.shell_tool=false', 'features.unified_exec=false',
    'features.shell_snapshot=false', 'features.apps=false',
    'features.plugins=false', 'features.remote_plugin=false',
    'features.hooks=false', 'features.memories=false',
    'features.multi_agent=false', 'features.goals=false',
    'features.skill_mcp_dependency_install=false',
    'features.context_management.experimental_mode=false',
    'features.skip_host_skill_discovery=true',
    'features.tool_registry.turn_metadata_includes_tool_info=true',
    'features.unbounded_connection_retries=false',
    'features.artifact=false', 'features.browser_use=false',
    'features.computer_use=false', 'features.view_image=false',
    'features.tool_search=false', 'features.code_mode_only=true',
    "features.code_mode={enabled=true,excluded_tool_namespaces=['skills'],direct_only_tool_namespaces=[]}",
    'memories.use_memories=false', 'memories.generate_memories=false',
    'history.persistence="none"', 'mcp_servers.node_repl.enabled=false',
    'skills.include_instructions=false', 'skills.bundled.enabled=false',
    ROLLOUT_GUARD_OVERRIDE,
    "skills.config=[{name='imagegen',enabled=false},{name='openai-docs',enabled=false},"
    "{name='plugin-creator',enabled=false},{name='skill-creator',enabled=false},"
    "{name='skill-installer',enabled=false},{name='artifact-template-anders-cover-letter',enabled=false}]",
)


def thread_parameters(cwd: str, provider: str) -> dict[str, Any]:
    directory = Path(cwd)
    if not directory.is_absolute() or not directory.is_dir() or any(directory.iterdir()):
        raise ValueError("An existing empty absolute scratch directory is required")
    return {
        "model": MODEL, "modelProvider": provider, "ephemeral": True,
        "environments": [], "selectedCapabilityRoots": [], "dynamicTools": [],
        "cwd": str(directory), "runtimeWorkspaceRoots": [],
        "approvalPolicy": "never", "sandbox": "read-only",
        "baseInstructions": BASE_INSTRUCTIONS,
        "developerInstructions": DEVELOPER_INSTRUCTIONS,
        "allowProviderModelFallback": False,
    }


def expected_isolation_config() -> dict[str, Any]:
    """Parse the exact shared overrides; no user configuration is read."""
    import tomllib
    return tomllib.loads("\n".join(ISOLATION_OVERRIDES))


def validate_effective_config(config: dict[str, Any]) -> dict[str, int]:
    """Verify config/read's resolved isolation fields before starting a thread.

    Extra unrelated preferences are allowed, but every declared leaf must be
    present and equal. Arrays are exact, so added skill entries are rejected.
    All configured MCP servers must be explicitly disabled. Error messages name
    only the setting; no possibly sensitive configuration values are echoed.
    """
    if not isinstance(config, dict):
        raise ValueError("Effective configuration must be an object")
    checked = 0

    def compare(actual: Any, expected: Any, path: str) -> None:
        nonlocal checked
        if isinstance(expected, dict):
            if not isinstance(actual, dict):
                raise ValueError("Isolation configuration shape mismatch: " + path)
            for key, value in expected.items():
                child = path + "." + key if path else key
                if key not in actual:
                    raise ValueError("Isolation configuration missing: " + child)
                compare(actual[key], value, child)
            return
        if type(expected) in (int, float):
            matches = type(actual) in (int, float) and actual == expected
        else:
            matches = type(actual) is type(expected) and actual == expected
        if not matches:
            raise ValueError("Isolation configuration drift: " + path)
        checked += 1

    compare(config, expected_isolation_config(), "")
    for server in config.get("mcp_servers", {}).values():
        if not isinstance(server, dict) or server.get("enabled") is not False:
            raise ValueError("Unexpected enabled MCP server")
    return {"verified_isolation_leaves": checked}


def schema_projection(schema: Any) -> Any:
    """Remove unsupported provider uniqueness keyword; host still enforces it."""
    if isinstance(schema, dict):
        return {key: schema_projection(value) for key, value in schema.items() if key != "uniqueItems"}
    if isinstance(schema, list):
        return [schema_projection(value) for value in schema]
    return schema


def wire_body_byte_bound(request: dict[str, Any]) -> int:
    """Conservative bound conditional on the audited fixed client context.

    The 20 KB fixed allowance must be checked by the installed-client mock
    audit, and the binary/profile/global-instruction hashes must stay fixed.
    This is not a claim about undocumented server-side context.
    """
    from .protocol import request_bytes
    public_text = request_bytes(request).decode("utf-8")
    encoded_public = json.dumps(public_text, ensure_ascii=True).encode("utf-8")
    encoded_schema = json.dumps(schema_projection(request["response_schema"]), ensure_ascii=True).encode("utf-8")
    return MAX_FIXED_WIRE_BYTES + len(encoded_public) + len(encoded_schema)


def turn_parameters(thread_id: str, request: dict[str, Any], *,
                    max_public_bytes: int = 100000) -> dict[str, Any]:
    from .protocol import request_bytes
    if type(max_public_bytes) is not int or max_public_bytes <= 0:
        raise ValueError("max_public_bytes must be a positive integer")
    raw = request_bytes(request)
    if len(raw) > max_public_bytes:
        raise ValueError("Public request exceeds byte cap")
    if wire_body_byte_bound(request) > MAX_WIRE_BYTES:
        raise ValueError("Declared complete provider-body bound exceeds byte cap")
    return {
        "threadId": thread_id, "input": [{"type": "text", "text": raw.decode("utf-8"), "text_elements": []}],
        "environments": [], "runtimeWorkspaceRoots": [], "model": MODEL,
        "effort": "medium", "summary": "none", "serviceTierForTurn": "default",
        "outputSchema": schema_projection(request["response_schema"]),
    }


VISIBLE_TOOL_SPEC_SHA256 = '3b6005047e9aebf2d4dd955caf1839501f044ce8382c1403bb6615f918461b93'

def audit_payload(body, *, public_text, global_instructions_text):
    """Verify the installed September 29 client's exact local mock context."""
    if set(body) - ALLOWED_BODY_KEYS or body.get("instructions") is not None:
        raise ValueError("Unexpected provider-body field or separate instructions")
    if (body.get("model") != MODEL or body.get("reasoning", {}).get("effort") != "medium"
            or body.get("store") is not False or body.get("stream") is not True):
        raise ValueError("Model, effort or persistence mismatch")
    metadata = json.loads(body.get("client_metadata", {}).get("x-codex-turn-metadata", "{}"))
    registry = metadata.get("tool_namespaces_info", {})
    expected_names = {"functions": {"exec", "wait", "request_user_input", "request_user_input_async"},
                      "clock": {"curr_time", "sleep"}}
    if (metadata.get("model") != MODEL or metadata.get("reasoning_effort") != "medium"
            or set(registry) != set(expected_names)):
        raise ValueError("Unexpected model or registry metadata")
    for namespace, names in expected_names.items():
        functions = registry[namespace].get("functions", {})
        if set(functions) != names or any(x.get("source") != {"kind": "harness"} for x in functions.values()):
            raise ValueError("External or unknown nested tools")
    items = body.get("input", [])
    if not items or items[0].get("type") != "additional_tools" or body.get("tools"):
        raise ValueError("Unexpected tool serialization")
    tool_item = items[0]
    if set(tool_item) != {"type", "id", "role", "tools"} or tool_item["role"] != "developer":
        raise ValueError("Unexpected tool item metadata")
    digest = hashlib.sha256(json.dumps(tool_item["tools"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if digest != VISIBLE_TOOL_SPEC_SHA256:
        raise ValueError("Visible tool descriptions or schema changed")
    messages = []
    for item in items[1:]:
        if set(item) != {"type", "id", "role", "content"} or item["type"] != "message":
            raise ValueError("Unexpected history item")
        for part in item["content"]:
            if set(part) != {"type", "text"} or part["type"] != "input_text":
                raise ValueError("Unexpected content channel")
            messages.append((item["role"], part["text"]))
    expected = [("developer", BASE_INSTRUCTIONS), ("developer", DEVELOPER_INSTRUCTIONS),
        ("user", "# AGENTS.md instructions\n\n<INSTRUCTIONS>\n" + global_instructions_text.strip() + "\n</INSTRUCTIONS>"),
        ("user", public_text), ("developer", ROLLOUT_GUARD_TEXT)]
    if messages != expected:
        raise ValueError("Unexpected model-visible instructions/history")
    return {"model": MODEL, "input_message_count": len(messages),
        "visible_tool_spec_sha256": digest, "declared_registry": {k: sorted(v) for k, v in expected_names.items()},
        "all_tool_attempts_forbidden": True, "workspace_roots": [], "prior_history": False,
        "global_instructions_sha256": hashlib.sha256(global_instructions_text.encode()).hexdigest(),
        "public_text_sha256": hashlib.sha256(public_text.encode()).hexdigest(),
        "audit_scope": "synthetic unauthenticated loopback; server internals unverified"}
