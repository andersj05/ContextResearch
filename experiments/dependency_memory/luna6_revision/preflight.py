"""Read-only managed-account and no-auth serialization review; no model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from luna_appserver import AppServer, PROVIDER_OVERRIDES, quota_snapshot, check_quota
from . import profile
from .audit import run_case


def config_check(config):
    expected = profile.expected_isolation_config()
    checked = 0
    def walk(actual, wanted, path=""):
        nonlocal checked
        if isinstance(wanted, dict):
            if not isinstance(actual, dict):
                raise ValueError("Config shape: " + path)
            for key, value in wanted.items():
                walk(actual.get(key), value, path + "." + key)
        else:
            if type(actual) is not type(wanted) and not (type(actual) in (int, float) and type(wanted) in (int, float)) or actual != wanted:
                raise ValueError("Config drift: " + path)
            checked += 1
    walk(config, expected)
    for value in config.get("mcp_servers", {}).values():
        if value.get("enabled") is not False:
            raise ValueError("Enabled MCP server")
    provider = config.get("model_providers", {}).get("luna_research", {})
    if config.get("model_provider") != "luna_research" or provider.get("base_url") is not None:
        raise ValueError("Unexpected provider routing")
    for key, value in {"requires_openai_auth": True, "request_max_retries": 0, "stream_max_retries": 0, "supports_websockets": False, "wire_api": "responses"}.items():
        if provider.get(key) != value:
            raise ValueError("Provider configuration drift: " + key)
    if any(provider.get(key) for key in ("env_key", "experimental_bearer_token", "http_headers", "env_http_headers", "query_params", "auth", "aws")):
        raise ValueError("Unexpected provider credentials or headers")
    return {"verified_leaves": checked}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", required=True, type=Path)
    parser.add_argument("--global-instructions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    global_text = args.global_instructions.read_text(encoding="utf-8")
    version = subprocess.run([str(args.executable), "--version"], capture_output=True, text=True, check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="luna6-preflight-") as cwd:
        server = AppServer(args.executable, cwd, (*profile.ISOLATION_OVERRIDES, *PROVIDER_OVERRIDES))
        try:
            server.initialize()
            kind = (server.rpc("account/read", {"refreshToken": False}).get("account") or {}).get("type")
            if kind != "chatgpt":
                raise ValueError("Managed subscription required")
            quota = quota_snapshot(server.rpc("account/rateLimits/read", {}))
            mode = check_quota(quota, used_limit=100, credit_backed=True)
            config = config_check(server.rpc("config/read", {"includeLayers": False})["config"])
            catalog = server.rpc("model/list", {"includeHidden": True})
            selected = [row for row in catalog.get("data", []) if row.get("model") == profile.MODEL]
            if len(selected) != 1:
                raise ValueError("Requested exact model absent")
            model = selected[0]
            if not any(x.get("reasoningEffort") == "medium" for x in model.get("supportedReasoningEfforts", [])):
                raise ValueError("Medium effort unsupported")
        finally:
            server.close()
    cases = []
    for name in ("final_message", "tool_call", "http_503", "truncated_sse"):
        cases.append(run_case(str(args.executable), global_text, name))
        print(json.dumps({"mock": name, "passed": True}), flush=True)
    report = {"version": "luna6_preflight_v1", "client_version": version, "model_catalog_entry": model,
              "client_sha256": hashlib.sha256(args.executable.read_bytes()).hexdigest(),
              "global_instructions_sha256": hashlib.sha256(global_text.encode()).hexdigest(),
              "profile_sha256": hashlib.sha256(json.dumps(profile.ISOLATION_OVERRIDES).encode()).hexdigest(),
              "account_type": kind, "quota": quota, "quota_mode": mode, "config_check": config,
              "cases": cases, "real_model_generations": 0, "isolation_passed": True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"preflight": "passed", "version": version, "model": model["model"], "effort": "medium", "real_generations": 0, "output": str(args.output)}))


if __name__ == "__main__":
    main()
