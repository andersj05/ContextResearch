"""Development-only pilot orchestration; defaults to an offline fake client.

Fixtures, reference answers, and accounting stay in this evaluator. Clients see
only canonical allowlisted requests. No held-out renderer or route is executed.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import time

from artifact_workflow import (Action, ArtifactEnvironment, Fixture, Policy, PublicView,
                               Receipt, choose_action, memory_bytes, run_episode,
                               visible_records)
from pilot_interface import (FakeClient, inspection_request, public_metadata,
                             request_bytes, retention_request,
                             validate_inspection_response, validate_retention_response)
from pilot_plan import SEEDS, build_plan
from recovery_frontier import executable_policy
from run_recovery_frontier import route_fixtures, scenarios


VERSION = "development_pilot_v0.3"
MAX_REQUESTS = 96


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def development_fixture(config, assignment):
    """Domain-separated opaque payloads, shared across arms/modes/revision cells."""
    if assignment["split"] != "development" or assignment["family"] != "direct_artifact_tags":
        raise ValueError("This version executes only the development family")
    base = tuple(route_fixtures(config))[assignment["route_index"]]
    domain = (SEEDS["payload_root"], assignment["split"], assignment["family"], assignment["route_index"])
    def receipt(key, revision):
        return Receipt(key, revision, digest([*domain, key, revision])[:32])
    return Fixture(tuple(receipt(r.key, 1) for r in base.receipts), base.candidates, base.target,
                   receipt(base.candidates[0], 2) if config.revise else None)


class RequestStop(RuntimeError):
    pass


class RequestFailure(RuntimeError):
    pass


class RequestLedger:
    """Reserve each attempt before dispatch. Failures are never retried here."""

    def __init__(self, client, *, cap=MAX_REQUESTS, fake=True, path=None):
        if type(cap) is not int or not 0 <= cap <= MAX_REQUESTS:
            raise ValueError("Development request cap must be an integer from zero to 96")
        self.client, self.cap, self.fake = client, cap, fake
        self.path = path
        self.rows = []
        self.stopped = False

    def _persist(self):
        if self.path is not None:
            # Evaluator-only structured audit, never a provider conversation log.
            temporary = self.path.with_suffix(".part")
            with temporary.open("w", encoding="utf-8", newline="\n") as stream:
                stream.write("".join(canonical(row).decode() + "\n" for row in self.rows))
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(self.path)

    def complete(self, request, evaluator_id, validator):
        if self.stopped or len(self.rows) >= self.cap:
            raise RequestStop("request_cap_or_prior_transport_stop")
        payload = request_bytes(request)
        row = {"attempt": len(self.rows) + 1, "evaluator_id": evaluator_id,
               "request_utf8": payload.decode("utf-8"),
               "request_sha256": hashlib.sha256(payload).hexdigest(),
               "request_bytes": len(payload), "status": "reserved",
               "response": None, "provider_metadata": {}, "latency_seconds": None}
        self.rows.append(row)
        self._persist()  # A process interruption leaves a counted reserved attempt.
        start = time.monotonic()
        try:
            if hasattr(self.client, "last_metadata"):
                self.client.last_metadata = {}
            # Round-trip prevents mutation/identity links to evaluator request objects.
            response = self.client.complete(json.loads(payload))
        except Exception as error:
            row.update(status="transport_failure", error_type=type(error).__name__)
            self.stopped = True
            raise RequestStop("transport_failure; no automatic retry") from error
        else:
            row["response"] = response
            try:
                result = validator(response)
            except (ValueError, TypeError, KeyError) as error:
                row.update(status="policy_failure", error_type=type(error).__name__)
                raise RequestFailure("invalid_response") from error
            row["status"] = "completed"
            return result
        finally:
            row["latency_seconds"] = None if self.fake else round(time.monotonic() - start, 6)
            row["provider_metadata"] = dict(getattr(self.client, "last_metadata", {}) or {})
            self._persist()


def run_model_episode(config, fixture, arm, render_mode, ledger, evaluator_id):
    if arm not in ("never_inspect", "always_inspect", "model_selective"):
        raise ValueError("Unknown arm")
    env = ArtifactEnvironment(config, fixture)
    metadata = public_metadata(config)
    memory, window, compactions = (), (), []
    inspect = arm == "always_inspect"
    inspection_chosen = arm != "model_selective"
    pre_recovery_available = None
    request_start = len(ledger.rows)
    try:
        while env.phase != "terminal":
            if env.phase == "before_first" and not inspection_chosen:
                request = inspection_request(config, metadata, memory, window, render_mode=render_mode)
                inspect = ledger.complete(request, evaluator_id + "/inspect", validate_inspection_response)
                inspection_chosen = True
            view = PublicView(config, env.phase, env.probe_attempted, memory, window)
            if env.phase == "submit" and pre_recovery_available is None:
                requirement = next(o for o in reversed(window) if o.kind == "requirement")
                pre_recovery_available = any(r.key == requirement.required_key and
                    r.revision == requirement.required_revision for r in visible_records(memory, window))
            policy = Policy("scripted_controller", probing="always" if inspect else "never",
                            recovery="if_missing")
            observation = env.step(choose_action(view, policy))
            window += (observation,)
            if observation.checkpoint:
                boundary = observation.checkpoint
                request = retention_request(config, metadata, memory, window, boundary, render_mode)
                retained = ledger.complete(request, evaluator_id + f"/retain-{boundary}",
                    lambda response: validate_retention_response(response, request))
                # Canonical state is the only survivor; discard the old window.
                memory = tuple(Receipt(**r) for r in json.loads(canonical([asdict(r) for r in retained])))
                window = ()
                compactions.append({"boundary": boundary, "retained_keys": [r.key for r in memory],
                                    "retained_records": len(memory), "serialized_bytes": memory_bytes(memory)})
        status, failure = "completed", env.verdict["failure"]
        success = env.verdict["success"]
    except RequestFailure:
        status, failure, success = "policy_failure", "invalid_response", False
    except RequestStop as error:
        status, failure, success = "incomplete", str(error), False
    return {"status": status, "success": success, "failure": failure,
            "request_attempts": len(ledger.rows) - request_start,
            "inspection": inspect if inspection_chosen else None,
            "pre_recovery_available": pre_recovery_available,
            "recovery_attempted": env.recovery_attempted, "tool_attempts": env.calls,
            "synthetic_cost_units": env.cost_units, "compactions": compactions}


def make_manifest(cap=MAX_REQUESTS, client="fake-optimal"):
    plan = build_plan()
    assignment = next(a for a in plan["fixture_assignments"] if a["split"] == "development")
    episodes = {e["episode_id"]: e for e in plan["stage_b_episodes"] if e["split"] == "development"}
    schedule = [episodes[key] for key in plan["stage_b_execution_order"] if key in episodes]
    configs = scenarios()
    source_names = ("run_development_pilot.py", "pilot_interface.py", "artifact_workflow.py",
                    "pilot_plan.py", "recovery_frontier.py", "run_recovery_frontier.py")
    return {"version": VERSION, "client": client, "request_cap": cap,
            "maximum_scheduled_requests": MAX_REQUESTS, "automatic_runner_retries": 0,
            "split": "development", "heldout_requests": 0,
            "stage_a": plan["stage_a_decisions"], "stage_b": schedule,
            "fixtures": {name: asdict(development_fixture(configs[name], assignment))
                         for name in {e["scenario"] for e in schedule}},
            "source_sha256": {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                              for name in source_names},
            "information_contract": "Only pilot_interface.request_bytes payloads enter client.complete.",
            "interpretation": "Exploratory development/debugging; no general superiority inference."}


def execute(client, *, cap=MAX_REQUESTS, fake=True, output=None, client_name="fake-optimal"):
    if not fake:
        from luna_appserver import LunaClient
        if not isinstance(client, LunaClient) or not client.audit.get("launch_ready"):
            raise ValueError("Live execution is not enabled until the provider launch contract passes")
        if output is None:
            raise ValueError("Live execution requires a persisted output directory")
    if type(cap) is not int or not 0 <= cap <= MAX_REQUESTS:
        raise ValueError("Development request cap must be an integer from zero to 96")
    manifest = make_manifest(cap, client_name)
    if not fake:
        manifest["transport"] = client.metadata
    if output is not None:
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        if any(output.iterdir()):
            raise ValueError("Use an empty output directory; never overwrite a previous run")
        (output / "manifest.json").write_bytes(canonical(manifest) + b"\n")
    ledger = RequestLedger(client, cap=cap, fake=fake,
                           path=output / "requests.jsonl" if output else None)
    configs = scenarios()
    calibration = {c["scenario"]: c for c in build_plan()["calibration"]}
    decisions, episodes = [], []
    for item in manifest["stage_a"]:
        config = configs[item["scenario"]]
        result = {**item, "status": "incomplete", "inspection": None}
        try:
            decision = ledger.complete(inspection_request(config, calibration=True),
                                       item["decision_id"], validate_inspection_response)
            cell = calibration[item["scenario"]]
            cost = Fraction(cell["inspection_extra_cost" if decision else "no_inspection_extra_cost"])
            result.update(status="completed", inspection=decision, expected_extra_cost=str(cost),
                          excess_cost=str(cost - Fraction(cell["optimal_extra_cost"])))
        except RequestFailure:
            result["status"] = "policy_failure"
        except RequestStop:
            pass
        decisions.append(result)
    for item in manifest["stage_b"]:
        config = configs[item["scenario"]]
        fixture = Fixture(tuple(Receipt(**r) for r in manifest["fixtures"][item["scenario"]]["receipts"]),
                          tuple(manifest["fixtures"][item["scenario"]]["candidates"]),
                          manifest["fixtures"][item["scenario"]]["target"],
                          Receipt(**manifest["fixtures"][item["scenario"]]["revision"])
                          if manifest["fixtures"][item["scenario"]]["revision"] else None)
        if ledger.stopped or len(ledger.rows) >= cap:
            result = {"status": "incomplete", "success": False, "failure": "request_stop",
                      "request_attempts": 0, "synthetic_cost_units": 0, "tool_attempts": 0,
                      "pre_recovery_available": None, "recovery_attempted": False, "compactions": []}
        else:
            result = run_model_episode(config, fixture, item["arm"], item["render_mode"], ledger, item["episode_id"])
        # Fixed population policy on this exact fixture, never fitted to its target.
        references = {}
        for inspect, name in ((False, "skip"), (True, "inspect")):
            ref = run_episode(config, fixture, executable_policy(config, inspect=inspect, recover=True))
            references[name] = {"synthetic_cost_units": ref.cost_units,
                                "pre_recovery_available": not ref.recovery_attempted}
        episodes.append({**item, **result, "fixed_policy_reference": references})
    summary = {"version": VERSION, "client": client_name, "fake": fake,
               "manifest_sha256": digest(manifest), "request_attempts": len(ledger.rows),
               "model_requests": 0 if fake else sum(r["provider_metadata"].get("dispatched", False) for r in ledger.rows), "heldout_requests": 0,
               "request_cap": cap, "attempt_status_counts": {status: sum(r["status"] == status for r in ledger.rows)
                   for status in ("completed", "policy_failure", "transport_failure", "reserved")},
               "request_audit_sha256": digest(ledger.rows), "stage_a": decisions, "stage_b": episodes,
               "cost_accounting": {"api_dollars": 0,
                                   "subscription_usage": "none" if fake else "see provider ledger; not API dollars"},
               "limitations": ["One development route; repeated paired measurements.",
                   "Reliable recovery permits success even after empty retention.",
                   "Fake-client results validate plumbing, not model performance."]}
    if not fake:
        summary["limitations"][-1] = "Controlled single-response Luna diagnostic with declared fixed harness instructions."
        summary["transport_manifest"] = client.metadata
        summary["cost_accounting"]["credit_budget"] = client.budget.snapshot()
        summary["request_metrics"] = [{key: row[key] for key in (
            "evaluator_id", "status", "latency_seconds", "provider_metadata")} for row in ledger.rows]
    if output is not None:
        (output / "summary.json").write_bytes(canonical(summary) + b"\n")
    return summary, ledger


def offline_audit():
    """Small reproducible certificate; complete request bytes can be regenerated."""
    controls = []
    for mode in ("optimal", "forget_all", "invalid"):
        summary, ledger = execute(FakeClient(mode), client_name="fake-" + mode)
        rows = summary["stage_b"]
        controls.append({"mode": mode, "fake_request_attempts": len(ledger.rows),
                         "manifest_sha256": summary["manifest_sha256"],
                         "request_audit_sha256": summary["request_audit_sha256"],
                         "stage_a_completed": sum(r["status"] == "completed" for r in summary["stage_a"]),
                         "stage_b_completed": sum(r["status"] == "completed" for r in rows),
                         "stage_b_successes": sum(r["success"] for r in rows),
                         "stage_b_pre_recovery_available": sum(r["pre_recovery_available"] is True for r in rows),
                         "stage_b_recoveries": sum(r["recovery_attempted"] for r in rows),
                         "policy_failures": summary["attempt_status_counts"]["policy_failure"]})
    return {"version": VERSION, "model_requests": 0, "api_dollars": 0,
            "heldout_requests": 0, "development_route_index": next(
                a["route_index"] for a in build_plan()["fixture_assignments"] if a["split"] == "development"),
            "controls": controls, "source_sha256": make_manifest()["source_sha256"],
            "scope": "Trusted evaluator/serializer checks with fake clients; not provider isolation or LLM performance."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fake-mode", choices=("optimal", "forget_all", "invalid"), default="optimal")
    parser.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-audit", action="store_true", help="Write the reproducible three-control certificate")
    args = parser.parse_args()
    if args.offline_audit:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        audit = offline_audit()
        args.output.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(audit))
        return
    summary, _ = execute(FakeClient(args.fake_mode), cap=args.max_requests, output=args.output,
                         client_name="fake-" + args.fake_mode)
    print(json.dumps({"output": str(args.output), "fake": True, "model_requests": 0,
                      "fake_requests": summary["request_attempts"],
                      "stage_b_completed": sum(r["status"] == "completed" for r in summary["stage_b"])}))


if __name__ == "__main__":
    main()
