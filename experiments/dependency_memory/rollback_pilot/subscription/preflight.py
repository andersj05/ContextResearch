"""Freeze a read-only account and installed-client mock audit; no live generations."""
import argparse
from pathlib import Path
import subprocess

from ..controller import write_new
from ..prepare import calibration_requests
from ..records import digest, wire
from . import profile
from .audit import CASES, run_case
from .process import AppServer
from .transport import check_quota, quota_snapshot


def run(executable, global_instructions, scratch_root):
    executable, global_instructions, scratch_root = Path(executable), Path(global_instructions), Path(scratch_root)
    scratch_root.mkdir(parents=True, exist_ok=True)
    global_text = global_instructions.read_text(encoding="utf-8")
    version = subprocess.run([str(executable), "--version"], capture_output=True, text=True, check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.strip()
    # Safe account/model checks never return tokens, email addresses or IDs.
    server = AppServer(executable, scratch_root, profile.OVERRIDES + profile.PROVIDER_OVERRIDES)
    try:
        server.initialize()
        account_type = (server.rpc("account/read", {"refreshToken": False}).get("account") or {}).get("type")
        if account_type != "chatgpt":
            raise ValueError("subscription sign-in required")
        quota = quota_snapshot(server.rpc("account/rateLimits/read", {}))
        check_quota(quota)
        config = profile.check_config(server.rpc("config/read", {"includeLayers": False})["config"])
        catalog = server.rpc("model/list", {"includeHidden": True})
        models = [x for x in catalog.get("data", []) if x.get("model") == profile.MODEL]
        if len(models) != 1 or not any(x.get("reasoningEffort") == "medium" for x in models[0].get("supportedReasoningEfforts", [])):
            raise ValueError("GPT-6 Luna medium absent from signed-in catalog")
    finally:
        server.close()
    renderer = profile.Renderer()
    from ..contexts import Request
    requests = [Request(row["stage"], wire(row["request"]), row["complete_input_units"], row["counter_id"])
                for row in calibration_requests(renderer)]
    if any(not renderer.fits(x) for x in requests):
        raise ValueError("calibration request exceeds byte admission")
    cases = []
    for case in CASES:
        cases.append(run_case(executable, global_text, requests[0], case, scratch_root))
        print(wire({"mock_case": case, "pass": True}), flush=True)
    # Different artifact interfaces and K/R deletion take the same provider path.
    for index in (1, 4, 6, 7):
        result = run_case(executable, global_text, requests[index], "final_message", scratch_root)
        result["calibration_call"] = index + 1
        cases.append(result)
        print(wire({"serialization_call": index + 1, "pass": True}), flush=True)
    registry_hashes = {x["payload_audit"]["registry_sha256"] for x in cases}
    if len(registry_hashes) != 1:
        raise ValueError("tool registry changed across request interfaces")
    return {"version": "rollback-subscription-preflight-1", "as_of": "2026-10-08", "client_version": version,
            "executable_sha256": digest(executable.read_bytes()), "global_instructions_sha256": digest(global_text),
            "configuration_sha256": digest(str(profile.OVERRIDES + profile.PROVIDER_OVERRIDES)),
            "model_catalog_entry": models[0], "account_type": account_type, "quota": quota,
            "configuration_check": config, "cases": cases, "registry_sha256": registry_hashes.pop(),
            "serialization_and_retry_audit_passed": True, "real_model_generations": 0,
            "configured_16384_output_cap_verified": False, "provider_tokenizer_verified": False,
            "immutable_model_revision": None, "E2_v02_launch_ready": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--global-instructions", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.executable, args.global_instructions, args.scratch_root)
    write_new(args.output, wire(result) + "\n")
    print(wire({"preflight": "passed", "mock_cases": len(result["cases"]), "real_model_generations": 0,
                "configured_16384_output_cap_verified": False}))


if __name__ == "__main__":
    main()
