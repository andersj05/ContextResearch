"""Shared, locally audited Codex app-server isolation controls.

The registry retains three harness wrappers. Its audit checks that they expose
no nested tools or other information channels; it does not call this an empty
tool registry. A live adapter must reject every tool attempt and freshen the
thread for every decision. Authenticated provider behavior is a separate gate.
The subscription transport uses Python 3.11+ for standard-library TOML parsing;
the original offline mathematical diagnostics remain independent of that API.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

MODEL = "gpt-5.6-luna"
BASE_INSTRUCTIONS = (
    "Return a JSON object according to the supplied response schema. "
    "Use only the supplied user input."
)
DEVELOPER_INSTRUCTIONS = "This is a controlled test. Do not call tools."
ALLOWED_WRAPPERS = {"exec", "wait", "request_user_input"}
ROLLOUT_GUARD_TEXT = "<rollout_budget>\nYou have 32768 weighted tokens left in the shared session token budget.\n</rollout_budget>"
ROLLOUT_GUARD_OVERRIDE = (
    "features.rollout_budget={enabled=true,limit_tokens=32768,"
    "prefill_token_weight=1000000.0,sampling_token_weight=1.0,reminder_at_remaining_tokens=[]}"
)
MAX_FIXED_WIRE_BYTES = 16000
MAX_WIRE_BYTES = 32768
ALLOWED_BODY_KEYS = {
    "client_metadata", "include", "input", "model", "parallel_tool_calls",
    "prompt_cache_key", "reasoning", "store", "stream", "text", "tool_choice",
    "tools", "instructions",
}

# A parent-map {} did not remove inherited MCP settings in the observed client.
# Live preflight must additionally reject any unexpected enabled MCP server.
ISOLATION_OVERRIDES = (
    'model_reasoning_effort="low"', 'model_reasoning_summary="none"',
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
    'features.tool_search=false', 'features.code_mode_only=false',
    "features.code_mode={enabled=false,excluded_tool_namespaces=['skills']}",
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

    The 16 KB fixed allowance must be checked by the installed-client mock
    audit, and the binary/profile/global-instruction hashes must stay fixed.
    This is not a claim about undocumented server-side context.
    """
    from pilot_interface import request_bytes
    public_text = request_bytes(request).decode("utf-8")
    encoded_public = json.dumps(public_text, ensure_ascii=True).encode("utf-8")
    encoded_schema = json.dumps(schema_projection(request["response_schema"]), ensure_ascii=True).encode("utf-8")
    return MAX_FIXED_WIRE_BYTES + len(encoded_public) + len(encoded_schema)


def turn_parameters(thread_id: str, request: dict[str, Any], *,
                    max_public_bytes: int = 32768) -> dict[str, Any]:
    from pilot_interface import request_bytes
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
        "effort": "low", "summary": "none", "serviceTierForTurn": "default",
        "outputSchema": schema_projection(request["response_schema"]),
    }


def audit_payload(body: dict[str, Any], *, public_text: str,
                  global_instructions_text: str) -> dict[str, Any]:
    """Allowlist a captured *synthetic* serialized request without saving IDs.

    Both ordinary tools and newer input-embedded additional_tools must be read.
    Registry metadata is required: omitted visible tools alone prove nothing.
    The global instructions are approved public background, supplied by caller.
    """
    if set(body) - ALLOWED_BODY_KEYS:
        raise ValueError("Unexpected provider-body field or prior-state channel")
    if body.get("store") is not False or body.get("stream") is not True:
        raise ValueError("Expected nonpersistent streaming request")
    if body.get("model") != MODEL or body.get("tools") not in (None, []):
        raise ValueError("Unexpected model or top-level tools")
    if body.get("instructions") not in (None, ""):
        raise ValueError("Unexpected separate instructions")
    raw_metadata = body.get("client_metadata", {}).get("x-codex-turn-metadata")
    if not isinstance(raw_metadata, str):
        raise ValueError("Tool-registry metadata absent")
    metadata = json.loads(raw_metadata)
    registry = metadata.get("tool_namespaces_info")
    if not isinstance(registry, dict) or set(registry) != {"functions"}:
        raise ValueError("Unexpected tool namespace")
    functions = registry["functions"].get("functions", {})
    if set(functions) != ALLOWED_WRAPPERS:
        raise ValueError("Unexpected direct or nested tool")
    for name, spec in functions.items():
        if spec != {"name": name, "direct": True, "code_mode_name": None,
                    "deferred": False, "source": {"kind": "harness"}}:
            raise ValueError("Unexpected wrapper exposure")
    texts = []
    tool_items = []
    for item in body.get("input", []):
        if item.get("type") == "additional_tools":
            tool_items.append(item)
        elif item.get("type") == "message":
            if item.get("role") not in {"developer", "user"}:
                raise ValueError("Unexpected message role/history")
            content = item.get("content")
            if not isinstance(content, list) or any(c.get("type") != "input_text" for c in content):
                raise ValueError("Unexpected content channel")
            texts.extend((item["role"], c["text"]) for c in content)
        else:
            raise ValueError("Unexpected history or model input item")
    if len(tool_items) != 1:
        raise ValueError("Expected exactly one declared tool item")
    namespaces = tool_items[0].get("tools", [])
    if len(namespaces) != 1 or namespaces[0].get("name") != "functions":
        raise ValueError("Unexpected visible namespace")
    wrappers = namespaces[0].get("tools", [])
    if {x.get("name") for x in wrappers} != ALLOWED_WRAPPERS or len(wrappers) != 3:
        raise ValueError("Unexpected visible tools")
    expected = [
        ("developer", BASE_INSTRUCTIONS), ("developer", DEVELOPER_INSTRUCTIONS),
        ("user", "# AGENTS.md instructions\n\n<INSTRUCTIONS>\n" + global_instructions_text.strip() + "\n</INSTRUCTIONS>"),
        ("user", public_text),
        ("developer", ROLLOUT_GUARD_TEXT),
    ]
    if texts != expected:
        raise ValueError("Unexpected model-visible background or public input")
    return {
        "model": MODEL, "input_message_count": len(texts),
        "global_instructions_sha256": hashlib.sha256(global_instructions_text.encode()).hexdigest(),
        "public_text_sha256": hashlib.sha256(public_text.encode()).hexdigest(),
        "allowed_wrapper_tools": sorted(ALLOWED_WRAPPERS),
        "nested_tools": [], "external_information_tools": [],
        "skill_catalog_present": False, "environment_context_present": False,
        "audit_scope": "synthetic no-auth loopback client serialization",
    }
