"""Versioned request/access contract for the October 8 installed CLI."""
from pathlib import Path
import tomllib

from ..contexts import Renderer as OfflineRenderer, Request, schema
from ..records import ActorTask, InterfaceError, Record, digest, obj, strict_loads, wire

MODEL = "gpt-6-luna"
PROVIDER = "rollback_subscription"
BASE = "Return a JSON object according to the supplied response schema. Use only the supplied user input."
DEVELOPER = "This is a controlled test. Do not call tools."
GUARD = "<rollout_budget>\nYou have 32768 weighted tokens left in the shared session token budget.\n</rollout_budget>"
FIXED_BYTES, MAX_BODY_BYTES = 18000, 32768
OVERRIDES = (
    'forced_login_method="chatgpt"', 'model_reasoning_effort="medium"', 'model_reasoning_summary="none"',
    'approval_policy="never"', 'web_search="disabled"', 'project_doc_max_bytes=0', 'agents.enabled=false',
    'include_environment_context=false', 'include_permissions_instructions=false',
    'include_collaboration_mode_instructions=false', 'include_apps_instructions=false',
    'features.shell_tool=false', 'features.unified_exec=false', 'features.shell_snapshot=false',
    'features.apps=false', 'features.plugins=false', 'features.remote_plugin=false',
    'features.hooks=false', 'features.memories=false', 'features.multi_agent=false', 'features.multi_agent_v2=false',
    'features.goals=false', 'features.skill_mcp_dependency_install=false',
    'features.context_management.experimental_mode=false', 'features.skip_host_skill_discovery=true',
    'features.tool_registry.turn_metadata_includes_tool_info=true', 'features.unbounded_connection_retries=false',
    'features.artifact=false', 'features.browser_use=false', 'features.computer_use=false',
    'features.view_image=false', 'features.image_generation=false', 'features.tool_search=false',
    'features.code_mode_only=true',
    "features.code_mode={enabled=true,excluded_tool_namespaces=['skills'],direct_only_tool_namespaces=[]}",
    'features.sleep_tool=false', 'features.current_time_reminder=false',
    'memories.use_memories=false', 'memories.generate_memories=false', 'history.persistence="none"',
    'mcp_servers.node_repl.enabled=false', 'skills.include_instructions=false', 'skills.bundled.enabled=false',
    'features.rollout_budget={enabled=true,limit_tokens=32768,prefill_token_weight=1000000.0,sampling_token_weight=1.0,reminder_at_remaining_tokens=[]}',
    "skills.config=[{name='imagegen',enabled=false},{name='openai-docs',enabled=false},"
    "{name='plugin-creator',enabled=false},{name='skill-creator',enabled=false},"
    "{name='skill-installer',enabled=false},{name='artifact-template-anders-cover-letter',enabled=false}]",
)
PROVIDER_OVERRIDES = (
    f'model_provider="{PROVIDER}"', f'model_providers.{PROVIDER}.name="Rollback subscription"',
    f'model_providers.{PROVIDER}.requires_openai_auth=true',
    f'model_providers.{PROVIDER}.request_max_retries=0', f'model_providers.{PROVIDER}.stream_max_retries=0',
    f'model_providers.{PROVIDER}.supports_websockets=false', f'model_providers.{PROVIDER}.wire_api="responses"',
)


def source_ids(task):
    result = task.source_ids()
    if task.domain == "math" and task.data()["family"] != "coloring":
        result = {x for x in result if not x.startswith("list")}
    return result


def output_schema(request):
    # The schema is counted inside the instruction and also in the RPC schema.
    instruction = request.data()["messages"][0]["content"]
    raw = instruction.split("\nOutput schema: ", 1)[1].split("\nSupplied source IDs", 1)[0]
    return strict_loads(raw)


def body_bound(request):
    return FIXED_BYTES + len(wire(request.json_text).encode("utf-8")) + len(wire(output_schema(request)).encode("utf-8"))


class Renderer(OfflineRenderer):
    """Same contexts/prompts with an explicitly different transport envelope."""
    def render(self, stage, task, checkpoint=None, branches=(), feedback=None, lesson=None, summary=None):
        if type(task) is not ActorTask:
            raise InterfaceError("renderer accepts ActorTask only")
        task = ActorTask.from_dict(task.task_id, task.stratum, task.data())
        supplied = source_ids(task)
        for value, kind in ((checkpoint, "checkpoint"), *((b, "branch") for b in branches), (lesson, "lesson"), (summary, "summary")):
            if value is None:
                continue
            if type(value) is not Record or value.kind != kind:
                raise InterfaceError("record kind mismatch")
            options = [x["id"] for x in checkpoint.data()["tentative_options"]] if checkpoint else []
            # Removed-branch citations in the retained lesson are intentionally
            # provenance labels. Strict schema still rejects any extra payload.
            check_sources = supplied | set(value.data().get("evidence_ids", [])) if kind == "lesson" else supplied
            Record.parse(kind, value.json_text, task, supplied=check_sources, option_ids=options)
            if kind == "checkpoint":
                supplied.update(f"C.fact{i+1}" for i in range(len(value.data()["facts"])))
            elif kind == "branch":
                index = len([x for x in supplied if x.startswith("B") and "." not in x]) + 1
                supplied.add(f"B{index}")
                supplied.update(f"B{index}.observation{i+1}" for i in range(len(value.data()["observations"])))
        result = super().render(stage, task, checkpoint, branches, feedback, lesson, summary)
        payload = result.data()
        payload["settings"] = {"model": MODEL, "reasoning_effort": "medium", "processing": "standard",
                               "transport": "codex_subscription", "output_limit": "provider_default_unverified_configurable_cap"}
        if stage != "terminal":
            if feedback:
                supplied.add(feedback.data()["receipt_id"])
            instruction = payload["messages"][0]["content"].split("\nSupplied source IDs", 1)[0]
            payload["messages"][0]["content"] = instruction + "\nSupplied source IDs (C.fact and B.observation numbers refer to list order): " + wire(sorted(supplied))
        raw = wire(payload)
        candidate = Request(stage, raw, 0, "subscription-complete-client-body-byte-bound-v1")
        return Request(stage, raw, body_bound(candidate), candidate.counter_id)

    def fits(self, request):
        return body_bound(request) <= MAX_BODY_BYTES


def thread_parameters(cwd, provider=PROVIDER):
    folder = Path(cwd)
    if not folder.is_absolute() or not folder.is_dir() or any(folder.iterdir()):
        raise ValueError("empty absolute scratch directory required")
    return {"model": MODEL, "modelProvider": provider, "ephemeral": True,
            "environments": [], "selectedCapabilityRoots": [], "dynamicTools": [],
            "cwd": str(folder), "runtimeWorkspaceRoots": [], "approvalPolicy": "never", "sandbox": "read-only",
            "baseInstructions": BASE, "developerInstructions": DEVELOPER, "allowProviderModelFallback": False}


def turn_parameters(thread, request):
    if body_bound(request) > MAX_BODY_BYTES:
        raise InterfaceError("complete client body exceeds declared byte admission")
    return {"threadId": thread, "input": [{"type": "text", "text": request.json_text, "text_elements": []}],
            "environments": [], "runtimeWorkspaceRoots": [], "model": MODEL, "effort": "medium",
            "summary": "none", "serviceTierForTurn": "default", "outputSchema": output_schema(request)}


def check_config(config, provider=True):
    expected = tomllib.loads("\n".join(OVERRIDES + (PROVIDER_OVERRIDES if provider else ())))
    count = 0
    def walk(actual, desired, path=""):
        nonlocal count
        if type(desired) is dict:
            if type(actual) is not dict:
                raise ValueError("config shape: " + path)
            for key, value in desired.items():
                walk(actual.get(key), value, path + "." + key)
        else:
            if type(actual) is not type(desired) or actual != desired:
                raise ValueError("config drift: " + path)
            count += 1
    walk(config, expected)
    for row in config.get("mcp_servers", {}).values():
        if type(row) is not dict or row.get("enabled") is not False:
            raise ValueError("enabled MCP server")
    if provider:
        row = config["model_providers"][PROVIDER]
        if any(row.get(x) for x in ("base_url", "env_key", "experimental_bearer_token", "http_headers", "env_http_headers", "query_params", "auth", "aws")):
            raise ValueError("unexpected provider routing/credentials")
    return {"verified_configuration_leaves": count}


def audit_payload(body, request, global_text):
    allowed = {"client_metadata", "include", "input", "model", "parallel_tool_calls", "prompt_cache_key",
               "reasoning", "store", "stream", "text", "tool_choice"}
    if type(body) is not dict or set(body) - allowed or body.get("model") != MODEL:
        raise ValueError("unexpected provider-body field/model/state channel")
    if body.get("reasoning") != {"effort": "medium", "context": "all_turns"} or body.get("store") is not False or body.get("stream") is not True:
        raise ValueError("unexpected reasoning/storage/stream settings")
    texts, embedded = [], []
    for item in body.get("input", []):
        if item.get("type") == "additional_tools":
            embedded.append(item)
            continue
        if item.get("type") != "message" or item.get("role") not in {"developer", "user"}:
            raise ValueError("history or unexpected input type")
        content = item.get("content")
        if type(content) is not list or any(x.get("type") != "input_text" for x in content):
            raise ValueError("unexpected content channel")
        texts.extend((item["role"], x["text"]) for x in content)
    expected = [("developer", BASE), ("developer", DEVELOPER),
                ("user", "# AGENTS.md instructions\n\n<INSTRUCTIONS>\n" + global_text.strip() + "\n</INSTRUCTIONS>"),
                ("user", request.json_text), ("developer", GUARD)]
    if texts != expected:
        raise ValueError("unexpected visible instructions, environment or history")
    metadata = strict_loads(body.get("client_metadata", {}).get("x-codex-turn-metadata", "null"))
    if type(metadata) is not dict or metadata.get("model") != MODEL or metadata.get("reasoning_effort") != "medium":
        raise ValueError("missing model/registry metadata")
    namespaces = metadata.get("tool_namespaces_info")
    if type(namespaces) is not dict or set(namespaces) != {"functions", "clock"}:
        raise ValueError("unexpected tool namespace")
    names = {ns: sorted(row.get("functions", {})) for ns, row in namespaces.items()}
    if names != {"functions": ["exec", "request_user_input", "request_user_input_async", "wait"], "clock": ["curr_time"]}:
        raise ValueError("unexpected nested information tool")
    if len(embedded) != 1 or embedded[0].get("role") != "developer":
        raise ValueError("unexpected embedded registry")
    exposed = embedded[0].get("tools")
    if type(exposed) is not list or len(exposed) != 1 or exposed[0].get("name") != "functions":
        raise ValueError("unexpected exposed namespace")
    if sorted(x.get("name") for x in exposed[0].get("tools", [])) != names["functions"]:
        raise ValueError("exposed tool mismatch")
    # Pin complete visible tool definitions, not just their names.
    registry_hash = digest(wire(exposed))
    fmt = body.get("text", {}).get("format", {})
    if fmt.get("type") != "json_schema" or fmt.get("schema") != output_schema(request):
        raise ValueError("schema mismatch")
    raw_bytes = len(wire(body).encode("utf-8"))
    fixed = raw_bytes - len(wire(request.json_text).encode("utf-8")) - len(wire(output_schema(request)).encode("utf-8"))
    if fixed > FIXED_BYTES or raw_bytes > body_bound(request):
        raise ValueError("client serialization overhead exceeded admission bound")
    return {"model": MODEL, "visible_message_count": len(texts), "registry_sha256": registry_hash,
            "registry_names": names, "fixed_body_bytes_observed": fixed, "complete_body_bytes_observed": raw_bytes,
            "complete_body_bytes_bound": body_bound(request), "global_instructions_sha256": digest(global_text),
            "prior_state_items": 0, "configured_output_cap_verified": False,
            "scope": "current installed client serialization to unauthenticated loopback; server internals unobserved"}
