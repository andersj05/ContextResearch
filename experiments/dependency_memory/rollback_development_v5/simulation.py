"""Disclosed oracle fixtures for offline routing tests; never a model result."""
from copy import deepcopy
import json
import threading
import time

from .coding_tasks import batch_program, reference_ledger, reference_resolver
from .common import wire
from ..rollback_pilot.grading import ExecutionResult
from ..rollback_pilot.subscription.accounting import Usage
from ..rollback_pilot.subscription.transport import Response


class OracleRunner:
    """Recognizes exact authored sources; never executes source on the host."""
    def __init__(self, tasks):
        self.programs = {batch_program(t["evaluator"]["reference"]): t["family"] for t in tasks if t["domain"] == "coding"}

    def execute(self, code, stdin, wall_seconds=10):
        family = self.programs.get(code)
        data = json.loads(stdin)
        if family is None:
            actual = [{"scripted_wrong": True} for _ in data]
        else:
            oracle = reference_ledger if family == "ledger" else reference_resolver
            actual = [oracle(x) for x in data]
        return ExecutionResult("completed", wire(actual), "", 0.0)


def bad_candidate(task):
    c = deepcopy(task["evaluator"]["reference"])
    if task["family"] == "scheduling":
        c["values"][0] = task["contract"]["start_bounds"][1] + 1
    elif task["family"] == "routing":
        c["order"] = [0] * len(c["order"])
    else:
        c["files"] = [{"path": "engine.py", "text": "def solve(data): return {'scripted_wrong': True}\n"},
                      {"path": "rules.py", "text": "# offline negative fixture\n"}]
    return c


class ScriptedTransport:
    def __init__(self, tasks, *, fail_key=None, delay=0.0, inject_failures=True):
        self.tasks = {t["task_id"]: t for t in tasks}
        self.fail_key, self.delay, self.inject_failures = fail_key, delay, inject_failures

    def generate(self, identity, request):
        if self.delay:
            time.sleep(self.delay)
        if identity.key == self.fail_key:
            raise RuntimeError("scripted_unknown_dispatch")
        task = self.tasks[identity.task_id]
        if request.stage == "action":
            # Each first proposal is intentionally wrong ONLY in this offline fixture.
            wrong = self.inject_failures and identity.step == 1 and identity.arm not in {"KE", "RE"}
            value = {"status": "candidate", "candidate": bad_candidate(task) if wrong else task["evaluator"]["reference"],
                     "note": "Offline scripted fixture; not a model observation."}
        elif request.stage == "lesson":
            value = {"established": ["Public checker rejected the candidate."], "retained_observations": [], "uncertainties": ["No inference about all methods."]}
        else:
            value = {"summary": "Offline scripted summary, not inferred model memory."}
        return Response(wire(value), Usage(max(1, len(request.json_text.encode("utf-8")) // 4), 0, 64, 32),
                        {"thread_id": "scripted:" + identity.key, "model": "offline_fixture", "not_provider_telemetry": True})
