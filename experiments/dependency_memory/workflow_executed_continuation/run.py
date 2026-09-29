"""Freeze and dispatch only identities never attempted in the stopped launch."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from experiments.dependency_memory.workflow_executed import run as original
from experiments.dependency_memory.workflow_executed import study
from experiments.dependency_memory.workflow_executed.transport import Client, RESERVATION, save, usage_cost
from experiments.dependency_memory.workflow_eval.grader import strict_json, wire
from experiments.dependency_memory.workflow_eval_live.protocol import request_bytes

ROOT = original.ROOT
ORIGINAL = ROOT / "experiments/dependency_memory/results/workflow_executed_2026-09-29"
OUTPUT = ROOT / "experiments/dependency_memory/results/workflow_executed_continuation_2026-09-29"
GAP = "tests_later_failure-prose-final"


def read(path):
    return strict_json(path.read_text(encoding="utf-8"))


def original_files(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob("*")) if p.is_file()}


def code_fingerprints():
    folder = Path(__file__).parent
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted([*folder.glob("*.py"), folder / "CONTRACT.md"])}


def prefix(directory):
    manifest = read(directory / "manifest.json")
    completion = read(directory / "completion.json")
    calls = {p.stem: read(p) for p in (directory / "calls").glob("*.json")}
    ordered = study.schedule()
    if (manifest["fingerprints"] != original.fingerprints() or manifest["schedule"] != ordered
            or completion["status"] != "stopped" or completion["calls"] != 17
            or set(calls) != set(ordered[:17]) or ordered[16] != GAP):
        raise ValueError("Original stopped prefix differs")
    if any(calls[i]["status"] != "completed" for i in ordered[:16]):
        raise ValueError("Unexpected additional original gap")
    failed = calls[GAP]
    if (failed["status"] != "transport_failure" or failed["dispatched"] is not True
            or failed.get("error") != "appserver_timeout" or "usage" in failed or "response" in failed
            or Decimal(failed["reservation_credits"]) != RESERVATION):
        raise ValueError("Original gap disposition differs")
    known = sum((usage_cost(calls[i]["usage"]) for i in ordered[:16]), Decimal(0))
    if known != Decimal(completion["planning_credits_settled"]):
        raise ValueError("Original usage differs")
    return calls, known


def verify_record(record, identity, request, *, allow_gap=False):
    if (record["identity"] != identity or record["dispatched"] is not True
            or record["request"] != request or record["request_sha256"] != hashlib.sha256(request_bytes(request)).hexdigest()
            or record["model"] != "gpt-6-luna" or record["effort"] != "medium"):
        raise ValueError("Saved request differs: " + identity)
    if record["status"] != "completed":
        if allow_gap and identity == GAP and record["status"] == "transport_failure":
            return None
        raise ValueError("Unmetered response: " + identity)
    if (record["usage_events"] != 1 or record["tool_items"] != 0
            or record["harness_termination"] != "sessionBudgetExceeded"):
        raise ValueError("Response transport differs")
    try:
        response = strict_json(record["raw_answer"])
    except ValueError:
        response = None
    if response != record["response"] or usage_cost(record["usage"]) != Decimal(record["planning_credits"]):
        raise ValueError("Response or usage differs")
    return response


def prepare(directory, preflight, original_directory=ORIGINAL):
    calls, known = prefix(original_directory)
    audit = read(preflight)
    if audit.get("isolation_passed") is not True or audit.get("real_model_generations") != 0:
        raise ValueError("Fresh zero-generation preflight required")
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / "manifest.json").exists() or (directory / "calls").exists():
        raise ValueError("Continuation already exists")
    save(directory / "preflight.json", audit)
    save(directory / "manifest.json", {"version": "workflow_executed_continuation_v1",
        "code_fingerprints": code_fingerprints(), "original_source_fingerprints": original.fingerprints(),
        "original_files": original_files(original_directory), "permanent_gap": GAP,
        "schedule": study.schedule(), "pending": study.schedule()[17:], "new_call_cap": 91,
        "known_original_credits": str(known), "unknown_original_reservation": str(RESERVATION),
        "combined_credit_ceiling": "20", "preflight_sha256": hashlib.sha256((directory / "preflight.json").read_bytes()).hexdigest()})


def verify(directory, original_directory=ORIGINAL):
    plan = read(directory / "manifest.json")
    calls, known = prefix(original_directory)
    if (plan["code_fingerprints"] != code_fingerprints() or plan["original_source_fingerprints"] != original.fingerprints()
            or plan["original_files"] != original_files(original_directory) or plan["schedule"] != study.schedule()
            or plan["pending"] != study.schedule()[17:] or plan["new_call_cap"] != 91
            or plan["known_original_credits"] != str(known) or plan["unknown_original_reservation"] != str(RESERVATION)
            or plan["combined_credit_ceiling"] != "20" or plan["permanent_gap"] != GAP
            or plan["preflight_sha256"] != hashlib.sha256((directory / "preflight.json").read_bytes()).hexdigest()):
        raise ValueError("Continuation plan or evidence changed")
    return plan, calls, known


class SuffixClient:
    def __init__(self, transport, calls, known, plan):
        self.transport, self.calls, self.known, self.plan = transport, calls, known, plan
        self.position = 0
        self.new_position = 0

    def complete(self, identity, request):
        if self.position >= 108 or identity != self.plan["schedule"][self.position]:
            raise ValueError("Original request order changed")
        self.position += 1
        if identity in self.calls:
            return verify_record(self.calls[identity], identity, request, allow_gap=True)
        if self.new_position >= 91 or identity != self.plan["pending"][self.new_position]:
            raise ValueError("Not a never-dispatched identity")
        if self.known + RESERVATION + self.transport.spent + RESERVATION > Decimal("20"):
            raise RuntimeError("Combined allocation exhausted with unknown usage reserved")
        self.new_position += 1
        return self.transport.complete(identity, request)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", type=Path)
    mode.add_argument("--launch", action="store_true")
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--global-instructions", type=Path)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.prepare:
        prepare(directory, args.prepare)
        print("Frozen 91-identity suffix; original failed request excluded; zero new model calls.")
        return
    plan, calls, known = verify(directory)
    (directory / "calls").mkdir(exist_ok=False)
    transport = Client(args.executable, args.global_instructions, directory, read(directory / "preflight.json"))
    suffix = SuffixClient(transport, calls, known, plan)
    frozen = code_fingerprints()
    class Guarded:
        def complete(self, identity, request):
            if frozen != code_fingerprints() or plan["original_source_fingerprints"] != original.fingerprints():
                raise ValueError("Frozen code drift")
            return suffix.complete(identity, request)
    try:
        original.execute(Guarded(), directory)
        verify(directory)
        if transport.attempts != 91 or suffix.position != 108:
            raise ValueError("Incomplete suffix")
        save(directory / "completion.json", {"status": "complete_suffix_with_original_gap", "new_calls": transport.attempts,
            "new_known_credits": str(transport.spent), "combined_known_credits": str(known + transport.spent),
            "original_unknown_reservation": str(RESERVATION)})
    except Exception as error:
        save(directory / "completion.json", {"status": "stopped", "new_calls": transport.attempts,
            "new_known_credits": str(transport.spent), "original_unknown_reservation": str(RESERVATION),
            "error_type": type(error).__name__, "error": str(error)[:160]})
        raise


if __name__ == "__main__":
    main()
