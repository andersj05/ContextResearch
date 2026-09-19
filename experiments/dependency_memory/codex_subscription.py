"""Supported Codex subscription integration and a fail-closed research gate.

This module can inspect the installed official CLI and prepare a candidate
invocation. It intentionally cannot launch the irreversible-memory experiment:
the reviewed CLI does not yet satisfy the information and accounting contract.
No credential file is read, no API-key fallback is used, and no model is called
by this module. See research/CODEX_SUBSCRIPTION_TRANSPORT_2026-09-19.md.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any, Callable


MODEL = "gpt-5.6-luna"
REVIEWED_CLI_VERSION = "codex-cli 0.155.0-alpha.9.2"
REVIEWED_CLI_SHA256 = "bc45017e8239dc150258f69309ced9df6bbcdf5b8e4f346decf780ac0999e226"
CONTRACT_VERSION = "codex_subscription_research_gate_v0.1"
REVIEW_DATE = "2026-09-19"
MAX_DEVELOPMENT_REQUESTS = 96

# These are unresolved scientific launch conditions, not sign-in requirements.
# Removing one requires implementation evidence, tests, and a new contract.
LAUNCH_BLOCKERS = (
    "Exact outbound model payload and empty tool registry have not been verified; "
    "local prompt inspection still included global instructions and host skills.",
    "A zero-retry bound for the built-in subscription provider has not been verified; "
    "one CLI invocation cannot yet be counted as one provider request.",
    "A hard output/reasoning-token cap and conservative subscription-credit "
    "reservation bound have not been verified.",
)

# Documented switches improve isolation, but are NOT an isolation certificate.
CONFIG_OVERRIDES = (
    'forced_login_method="chatgpt"',
    'model_provider="openai"',
    'model_reasoning_effort="low"',
    'model_reasoning_summary="none"',
    'approval_policy="never"',
    'web_search="disabled"',
    "project_doc_max_bytes=0",
    "agents.enabled=false",
    "features.shell_tool=false",
    "features.unified_exec=false",
    "features.shell_snapshot=false",
    "features.apps=false",
    "features.plugins=false",
    "features.remote_plugin=false",
    "features.hooks=false",
    "features.memories=false",
    "features.multi_agent=false",
    "features.goals=false",
    "features.skill_mcp_dependency_install=false",
    "features.context_management.experimental_mode=false",
    "memories.use_memories=false",
    "memories.generate_memories=false",
    'history.persistence="none"',
    "tools.view_image=false",
)


class SubscriptionNotReady(RuntimeError):
    """The reviewed subscription transport cannot satisfy the frozen protocol."""


class InvalidCodexOutput(ValueError):
    """Unexpected CLI events, usage, tool activity, or response structure."""


@dataclass(frozen=True)
class PreparedRequest:
    """Review artifact only; no executable method is provided."""

    command: tuple[str, ...]
    stdin: bytes
    request_sha256: str
    max_input_bytes: int
    launch_ready: bool = False


def contract() -> dict[str, Any]:
    """Serializable declared limits; unknown accounting fields stay null."""
    return {
        "version": CONTRACT_VERSION,
        "provider": "OpenAI Codex CLI / ChatGPT subscription",
        "model": MODEL,
        "model_revision": None,
        "model_revision_limitation": "Mutable alias; no immutable Luna snapshot verified.",
        "reviewed_cli_version": REVIEWED_CLI_VERSION,
        "reviewed_cli_sha256": REVIEWED_CLI_SHA256,
        "official_documentation_review_date": REVIEW_DATE,
        "reasoning_effort": "low",
        "sampling_seed": None,
        "api_key_fallback": False,
        "application_retries": 0,
        "provider_retries": None,
        "development_request_ceiling": MAX_DEVELOPMENT_REQUESTS,
        "hard_output_token_cap": None,
        "subscription_charge_bound": None,
        "api_dollar_spend_authorized": 0,
        "subscription_credits_are_free": False,
        "cross_request_state": "Proposed fresh ephemeral CLI process; not yet certified.",
        "launch_ready": False,
        "launch_blockers": list(LAUNCH_BLOCKERS),
        "sources": [
            "https://learn.chatgpt.com/docs/auth",
            "https://learn.chatgpt.com/docs/non-interactive-mode",
            "https://learn.chatgpt.com/docs/config-file/config-reference",
            "https://developers.openai.com/api/docs/models/gpt-5.6-luna",
        ],
    }


def prepare_request(
    request: dict[str, Any],
    *,
    executable: str,
    empty_cwd: str,
    output_schema: str,
    max_input_bytes: int = 32768,
) -> PreparedRequest:
    """Return an explicit candidate command without creating files or dispatching.

    The caller must supply an empty absolute scratch directory and schema path.
    Use stdin for the public request, never shell interpolation. The complete
    provider payload also includes CLI instructions; stdin is not that payload.
    """
    from pilot_interface import request_bytes

    if type(max_input_bytes) is not int or max_input_bytes <= 0:
        raise ValueError("max_input_bytes must be a positive integer")
    cwd = Path(empty_cwd)
    if not cwd.is_absolute() or not cwd.is_dir() or any(cwd.iterdir()):
        raise ValueError("Candidate cwd must be an existing empty absolute directory")
    schema = Path(output_schema)
    if not schema.is_absolute() or not schema.is_file():
        raise ValueError("Output schema must be an existing absolute file")
    raw = request_bytes(request)
    try:
        supplied_schema = json.loads(schema.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)
    except (OSError, ValueError) as error:
        raise ValueError("Cannot read a strict output schema") from error
    if supplied_schema != request["response_schema"]:
        raise ValueError("Output schema must match the validated public request")
    if len(raw) > max_input_bytes:
        raise ValueError("Public request exceeds the declared byte cap")
    args = [
        executable, "exec", "--ignore-user-config", "--ignore-rules",
        "--strict-config", "--ephemeral", "--skip-git-repo-check",
        "--sandbox", "read-only", "--model", MODEL, "--cd", str(cwd),
        "--output-schema", str(schema), "--json", "--color", "never",
    ]
    for override in CONFIG_OVERRIDES:
        args.extend(("--config", override))
    args.append("-")
    return PreparedRequest(tuple(args), raw, hashlib.sha256(raw).hexdigest(), max_input_bytes)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidCodexOutput("Duplicate JSON object key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise InvalidCodexOutput("Non-standard JSON numeric constant")


def parse_events(raw: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Parse a completed CLI response conservatively; never preserve raw logs.

    This is a secondary detector, not a substitute for preventing tool access.
    JSONL turn usage is aggregated CLI telemetry, not an HTTP-request ledger.
    Cached input is a subset of input; reasoning may overlap output and is not
    added to it. No token-to-dollar conversion is applied to subscription use.
    """
    allowed_events = {"thread.started", "turn.started", "turn.completed", "item.started", "item.updated", "item.completed"}
    messages: list[str] = []
    completed_usage: list[dict[str, int]] = []
    threads: list[str] = []
    turns = 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line, object_pairs_hook=_strict_object, parse_constant=_reject_constant)
        except (ValueError, TypeError) as exc:
            raise InvalidCodexOutput("Invalid JSONL event") from exc
        if not isinstance(event, dict) or event.get("type") not in allowed_events:
            raise InvalidCodexOutput("Unexpected event or provider/transport failure")
        kind = event["type"]
        if kind == "thread.started":
            value = event.get("thread_id")
            if not isinstance(value, str) or not value:
                raise InvalidCodexOutput("Missing thread identifier")
            threads.append(value)
        elif kind == "turn.started":
            turns += 1
        elif kind.startswith("item."):
            item = event.get("item")
            if not isinstance(item, dict) or item.get("type") not in {"agent_message", "reasoning"}:
                raise InvalidCodexOutput("Tool activity or unknown item: quarantine this response")
            if kind == "item.completed" and item["type"] == "agent_message":
                if not isinstance(item.get("text"), str):
                    raise InvalidCodexOutput("Missing response text")
                messages.append(item["text"])
        elif kind == "turn.completed":
            usage = event.get("usage")
            if not isinstance(usage, dict):
                raise InvalidCodexOutput("Missing usage accounting")
            required = ("input_tokens", "cached_input_tokens", "output_tokens")
            if any(type(usage.get(k)) is not int or usage[k] < 0 for k in required):
                raise InvalidCodexOutput("Invalid usage accounting")
            if usage["cached_input_tokens"] > usage["input_tokens"]:
                raise InvalidCodexOutput("Cached input cannot exceed total input")
            cleaned = {key: usage[key] for key in required}
            reasoning = usage.get("reasoning_output_tokens")
            if reasoning is not None:
                if type(reasoning) is not int or reasoning < 0:
                    raise InvalidCodexOutput("Invalid reasoning usage")
                cleaned["reasoning_output_tokens"] = reasoning
            completed_usage.append(cleaned)
    if len(threads) != 1 or turns != 1 or len(completed_usage) != 1 or len(messages) != 1:
        raise InvalidCodexOutput("Expected exactly one fresh thread, turn, usage record, and final response")
    try:
        response = json.loads(messages[0], object_pairs_hook=_strict_object, parse_constant=_reject_constant)
    except (ValueError, TypeError) as exc:
        raise InvalidCodexOutput("Response is not strict JSON") from exc
    if not isinstance(response, dict):
        raise InvalidCodexOutput("Response must be a JSON object")
    return response, {
        "usage": completed_usage[0],
        "thread_id": threads[0],
        "provider_request_id": None,
        "provider_request_count": None,
        "charged_dollars": None,
        "subscription_credits": None,
        "tool_events_observed": 0,
        "accounting_scope": "CLI turn telemetry; not verified provider request accounting",
    }


def inspect_installation(
    executable: str | None = None,
    *,
    check_auth: bool = False,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    """Read-only diagnostics. Never echo auth output (API status may contain keys).

    A sandbox/configuration failure is 'unverified', not authentication failure.
    The optional status probe uses the official CLI's existing credential store.
    """
    resolved = executable or shutil.which("codex")
    report: dict[str, Any] = contract()
    report.update({"installed": bool(resolved), "installed_cli_version": None,
                   "executable_sha256": None, "authentication": "not_checked"})
    if not resolved:
        return report
    path = Path(resolved)
    if path.is_file():
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        report["executable_sha256"] = digest.hexdigest()
        report["reviewed_binary_matches"] = digest.hexdigest() == REVIEWED_CLI_SHA256
    try:
        result = runner([resolved, "--version"], capture_output=True, text=True, timeout=15, check=False)
        version = next((line.strip() for line in result.stdout.splitlines() if line.startswith("codex-cli ")), None)
        report["installed_cli_version"] = version
        report["reviewed_version_matches"] = version == REVIEWED_CLI_VERSION
        if check_auth:
            result = runner([resolved, "login", "status"], capture_output=True, text=True, timeout=15, check=False)
            status = (result.stdout + "\n" + result.stderr).lower()
            if result.returncode == 0 and "logged in using chatgpt" in status:
                report["authentication"] = "chatgpt"
            elif result.returncode == 0 and "api key" in status:
                report["authentication"] = "api_key_not_authorized_for_this_adapter"
            else:
                report["authentication"] = "unverified"
    except (OSError, subprocess.TimeoutExpired):
        report["authentication"] = "unverified" if check_auth else "not_checked"
    return report


class CodexSubscriptionClient:
    """Fail-closed placeholder at the official CLI boundary, never a secret shim.

    There is deliberately no force/bypass switch. Closing the documented gates
    requires a versioned implementation change before complete() may dispatch.
    """

    def __init__(self, executable: str | None = None) -> None:
        self.executable = executable or shutil.which("codex")
        self.metadata = contract()
        self.last_metadata: dict[str, Any] = {}

    def complete(self, request: dict[str, Any]) -> dict[str, Any]:
        self.last_metadata = {
            "status": "launch_gate_blocked",
            "dispatched": False,
            "provider_request_count": 0,
            "launch_blockers": list(LAUNCH_BLOCKERS),
        }
        raise SubscriptionNotReady("; ".join(LAUNCH_BLOCKERS))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Inspect CLI version without calling a model")
    parser.add_argument("--check-auth", action="store_true", help="Also inspect official CLI sign-in status; no secrets are printed")
    parser.add_argument("--executable", help="Path to the installed official codex executable")
    args = parser.parse_args()
    result = inspect_installation(args.executable, check_auth=args.check_auth) if args.check or args.check_auth else contract()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
