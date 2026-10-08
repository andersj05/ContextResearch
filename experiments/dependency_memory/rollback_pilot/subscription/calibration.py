"""Freeze, run and verify the separately allocated eight-call subscription E1."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from ..accounting import Identity
from ..contexts import Request
from ..controller import write_new
from ..code_runner import DockerRunner
from ..fixtures import math_example, code_example
from ..grading import CodeChecker, terminal_grade
from ..prepare import calibration_requests, source_bindings, ROOT
from ..records import Record, InterfaceError, digest, strict_loads, wire
from ..transport import UnknownDispatch
from .accounting import Ledger, Usage, RESERVATION
from .dispatcher import Dispatcher
from .profile import Renderer, source_ids, body_bound
from .transport import SubscriptionTransport

PACKAGE = Path(__file__).resolve().parent


def bindings():
    base = source_bindings()
    return base + [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p.read_bytes())}
                   for p in sorted(PACKAGE.iterdir()) if p.is_file() and p.suffix in {".py", ".md"}]


def check_bindings(rows):
    for row in rows:
        path = (ROOT / row["path"]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or path.is_symlink() or digest(path.read_bytes()) != row["sha256"]:
            raise ValueError("frozen source changed: " + row["path"])


def freeze(folder, preflight_path, *, image, schema_folder):
    folder, preflight_path = Path(folder), Path(preflight_path)
    preflight = strict_loads(preflight_path.read_text(encoding="utf-8"))
    if preflight.get("serialization_and_retry_audit_passed") is not True or preflight.get("real_model_generations") != 0:
        raise ValueError("successful no-generation preflight required")
    folder.mkdir(parents=True, exist_ok=False)
    runtime = DockerRunner(image).audit()
    requests = calibration_requests(Renderer())
    write_new(folder / "preflight.json", wire(preflight) + "\n")
    write_new(folder / "runtime_audit.json", wire(runtime) + "\n")
    write_new(folder / "calibration_requests.jsonl", "".join(wire(x) + "\n" for x in requests))
    schemas = [{"path": p.relative_to(schema_folder).as_posix(), "bytes": p.stat().st_size, "sha256": digest(p.read_bytes())}
               for p in sorted(Path(schema_folder).rglob("*.json"))]
    if not schemas:
        raise ValueError("installed-client generated schemas required")
    write_new(folder / "protocol_schema_bindings.json", wire(schemas) + "\n")
    manifest = {"version": "rollback-subscription-calibration-1", "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "launch_id": "ROLLBACK_E1_SUBSCRIPTION_2026-10-08_V1", "model": "gpt-6-luna", "reasoning_effort": "medium",
        "speed": "standard", "immutable_model_revision": None, "selected_transport": "official_codex_app_server_chatgpt_subscription",
        "authorization": "October 8 user instructions: Use the Codex Subscription I have to run GPT 6 Luna; Don't worry about the token budget or cost budget we need to do these tests.",
        "allocation": {"generation_attempt_ceiling": 8, "planning_credit_ceiling": None, "per_attempt_conditional_reservation_credits": str(RESERVATION),
                       "API_dollars_authorized": "0", "credit_fallback": False, "credit_purchase": False, "automatic_retries": False},
        "limits": {"complete_client_body_max_UTF8_bytes": 32768, "provider_configurable_output_cap": None,
                   "conditional_model_input_token_envelope": 1050000, "conditional_model_output_token_envelope": 128000,
                   "writer_visible_UTF8_byte_cap": 1024, "generation_wall_seconds": 240},
        "sampling_seed": None, "scope": "eight disclosed authored E1 fixtures; excludes all study cohorts",
        "request_count": len(requests), "request_hashes": [x["request_sha256"] for x in requests],
        "runtime_image": image, "source_bindings": bindings(),
        "frozen_artifacts": [{"path": p.name, "sha256": digest(p.read_bytes())} for p in sorted(folder.iterdir())],
        "E2_launch_authorized": False, "E2_open_gates": ["real_coding_cohort_12_verified_sources_references_tests", "v02_tokenizer_and_16384_output_cap_or_new_E2_amendment", "separate_frozen_E2_allocation"]}
    write_new(folder / "manifest.json", wire(manifest) + "\n")
    return manifest


def check_frozen(folder, *, check_sources=True):
    folder = Path(folder)
    manifest = strict_loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if check_sources:
        check_bindings(manifest["source_bindings"])
    for row in manifest["frozen_artifacts"]:
        path = (folder / row["path"]).resolve()
        if not path.is_relative_to(folder.resolve()) or path.is_symlink() or digest(path.read_bytes()) != row["sha256"]:
            raise ValueError("frozen artifact changed")
    rows = [strict_loads(x) for x in (folder / "calibration_requests.jsonl").read_text(encoding="utf-8").splitlines()]
    expected = calibration_requests(Renderer())
    if rows != expected or len(rows) != 8 or manifest["request_hashes"] != [x["request_sha256"] for x in rows] or manifest["request_count"] != 8:
        raise ValueError("frozen calibration request/schedule changed")
    if manifest["allocation"] != {"generation_attempt_ceiling": 8, "planning_credit_ceiling": None,
            "per_attempt_conditional_reservation_credits": str(RESERVATION), "API_dollars_authorized": "0",
            "credit_fallback": False, "credit_purchase": False, "automatic_retries": False} or manifest["E2_launch_authorized"]:
        raise ValueError("allocation changed")
    return manifest, rows


def inspect_answer(row, text, code_checker):
    fixture = math_example() if row["task_id"] == "authored-calibration-math" else code_example()
    task, evaluator, checkpoint, branch, feedback, lesson, summary = fixture
    supplied = source_ids(task) | {feedback.data()["receipt_id"], "B1"}
    supplied.update(f"C.fact{i+1}" for i in range(len(checkpoint.data()["facts"])))
    supplied.update(f"B1.observation{i+1}" for i in range(len(branch.data()["observations"])))
    try:
        if row["stage"] in {"lesson", "summary"} and len(text.encode("utf-8")) > 1024:
            raise InterfaceError("writer_visible_byte_cap")
        result = Record.parse(row["stage"], text, task, supplied=supplied,
                              option_ids=[x["id"] for x in checkpoint.data()["tentative_options"]])
    except InterfaceError as error:
        return {"format_valid": False, "disposition": str(error)}
    result_row = {"format_valid": True, "disposition": "valid_record"}
    if row["stage"] == "terminal":
        result_row["grade"] = terminal_grade(task, evaluator, result, code_checker)
    return result_row


def launch(folder, *, executable, global_instructions, scratch_root):
    folder = Path(folder)
    manifest, rows = check_frozen(folder)
    # An exclusive marker prevents any repeated launch, including after a crash.
    write_new(folder / "launch_started.json", wire({"started_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_sha256": digest((folder / "manifest.json").read_bytes()), "scope": "eight-call E1 only"}) + "\n")
    ledger = Ledger(folder / "ledger.sqlite", max_calls=8)
    preflight = strict_loads((folder / "preflight.json").read_text(encoding="utf-8"))
    transport = SubscriptionTransport(executable, global_instructions, preflight, scratch_root)
    dispatcher = Dispatcher(folder, ledger, transport)
    results, stopped = [], False
    checker = CodeChecker(DockerRunner(manifest["runtime_image"]))
    try:
        for row in rows:
            number = row["calibration_call"]
            result = {"calibration_call": number, "task_id": row["task_id"], "stage": row["stage"],
                      "request_sha256": row["request_sha256"], "excluded_from_all_model_study_cohorts": True}
            if stopped:
                result.update(disposition="not_dispatched_after_transport_stop", format_valid=None)
            else:
                check_bindings(manifest["source_bindings"])
                identity = Identity(manifest["launch_id"], row["task_id"], row["stage"], slot=number)
                request = Request(row["stage"], wire(row["request"]), row["complete_input_units"], row["counter_id"])
                result["call_id"] = identity.key
                try:
                    response = dispatcher.call(identity, request)
                    result.update(inspect_answer(row, response.text, checker))
                    result.update(usage=vars(response.usage), planning_credits=str(response.usage.cost))
                except Exception as error:
                    stopped = True
                    result.update(disposition="transport_or_grading_stop", format_valid=None,
                                  error_type=type(error).__name__, error_code=str(error)[:180])
            results.append(result)
            write_new(folder / "dispositions" / f"{number:02}.json", wire(result) + "\n")
            print(wire({"calibration_call": number, "disposition": result["disposition"],
                        "format_valid": result["format_valid"], "planning_credits": ledger.summary()["completed_credits"]}), flush=True)
        summary = {"version": "rollback-subscription-E1-result-1", "scope": "calibration, not a rollback comparison",
                   "all_scheduled_calls": 8, "known_format_valid": sum(x["format_valid"] is True for x in results),
                   "known_format_invalid": sum(x["format_valid"] is False for x in results),
                   "unknown_or_unperformed": sum(x["format_valid"] is None for x in results),
                   "transport_stopped": stopped, "accounting": ledger.summary(), "results": results,
                   "E2_v02_launch_ready": False, "E2_open_gates": manifest["E2_open_gates"],
                   "API_model_calls": 0, "API_spend_USD": "0", "immutable_model_revision": None}
        write_new(folder / "usage_events.jsonl", "".join(wire(x) + "\n" for x in ledger.events()))
        write_new(folder / "summary.json", wire(summary) + "\n")
        write_new(folder / "evidence_manifest.json", wire({"files": [{"path": p.relative_to(folder).as_posix(), "bytes": p.stat().st_size,
                   "sha256": digest(p.read_bytes())} for p in sorted(folder.rglob("*")) if p.is_file() and p.name != "ledger.sqlite"]}) + "\n")
        return summary
    finally:
        ledger.close()


def verify(folder, *, check_sources=True):
    folder = Path(folder).resolve()
    manifest, requests = check_frozen(folder, check_sources=check_sources)
    evidence = strict_loads((folder / "evidence_manifest.json").read_text(encoding="utf-8"))
    expected = set()
    for row in evidence["files"]:
        path = (folder / row["path"]).resolve()
        if not path.is_relative_to(folder) or path.is_symlink() or path.stat().st_size != row["bytes"] or digest(path.read_bytes()) != row["sha256"]:
            raise ValueError("evidence binding failed")
        if row["path"] in expected:
            raise ValueError("duplicate evidence path")
        expected.add(row["path"])
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()} - {"ledger.sqlite", "evidence_manifest.json"}
    if actual != expected:
        raise ValueError("unexpected or missing evidence file")
    summary = strict_loads((folder / "summary.json").read_text(encoding="utf-8"))
    ledger = Ledger(folder / "ledger.sqlite", max_calls=8)
    try:
        if summary["accounting"] != ledger.summary():
            raise ValueError("summary/ledger mismatch")
        if [strict_loads(x) for x in (folder / "usage_events.jsonl").read_text(encoding="utf-8").splitlines()] != ledger.events():
            raise ValueError("event export/ledger mismatch")
        rows = ledger.rows()
        if len(summary["results"]) != 8:
            raise ValueError("missing calibration identities")
        for request, result in zip(requests, summary["results"], strict=True):
            if result["request_sha256"] != request["request_sha256"] or result["calibration_call"] != request["calibration_call"]:
                raise ValueError("scheduled result mismatch")
            if result["format_valid"] is not None:
                row = rows[result["call_id"]]
                if row["state"] != "completed" or row["request_hash"] != result["request_sha256"]:
                    raise ValueError("known result lacks a completed matching dispatch")
                usage = Usage(**row["usage"])
                if str(usage.cost) != row["planning_credits"] or result["usage"] != row["usage"]:
                    raise ValueError("usage/cost mismatch")
                response = strict_loads((folder / "responses" / (result["call_id"] + ".json")).read_text(encoding="utf-8"))
                if response["usage"] != row["usage"]:
                    raise ValueError("saved response/usage mismatch")
        return {"verified_scheduled_calls": 8, "completed_generations": summary["accounting"]["admitted_calls"] - len(summary["accounting"]["unresolved_call_ids"]),
                "planning_credits": summary["accounting"]["completed_credits"], "source_bindings": len(manifest["source_bindings"]),
                "evidence_files": len(expected), "E2_launch_ready": False}
    finally:
        ledger.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("freeze", "launch", "verify"))
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--preflight", type=Path)
    parser.add_argument("--image")
    parser.add_argument("--schema-folder", type=Path)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--global-instructions", type=Path)
    parser.add_argument("--scratch-root", type=Path)
    args = parser.parse_args()
    if args.mode == "freeze":
        value = freeze(args.folder, args.preflight, image=args.image, schema_folder=args.schema_folder)
        value = {"frozen": True, "calibration_calls": value["request_count"], "E2_authorized": False}
    elif args.mode == "launch":
        value = launch(args.folder, executable=args.executable, global_instructions=args.global_instructions, scratch_root=args.scratch_root)
        value = {"completed": True, "accounting": value["accounting"], "format_valid": value["known_format_valid"]}
    else:
        value = verify(args.folder)
    print(wire(value))


if __name__ == "__main__":
    main()
