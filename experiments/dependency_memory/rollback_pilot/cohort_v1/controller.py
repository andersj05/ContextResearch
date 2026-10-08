"""Subscription E2 adapter over the independently tested E0 episode state machine."""
from pathlib import Path
import time

from ..accounting import Identity
from ..controller import Controller as E0Controller, write_new
from ..grading import CodeChecker
from ..records import InterfaceError, Record, digest, wire
from ..schedule import ordered_tasks
from ..subscription.accounting import Ledger
from ..subscription.calibration import check_bindings
from ..subscription.dispatcher import Dispatcher
from ..subscription.profile import Renderer, source_ids


class BoundDispatcher(Dispatcher):
    def __init__(self, folder, ledger, transport, manifest):
        super().__init__(folder, ledger, transport)
        self.manifest = manifest
        self.identities = {Identity(**x).key for x in manifest["schedule"]}

    def call(self, identity, request):
        if identity.key not in self.identities:
            raise InterfaceError("identity absent from frozen allocation")
        check_bindings(self.manifest["source_bindings"])
        return super().call(identity, request)


class RecordingCodeChecker(CodeChecker):
    def __init__(self, runner):
        super().__init__(runner)
        self.grades = []

    def grade(self, task, evaluator, candidate):
        result = super().grade(task, evaluator, candidate)
        self.grades.append({"task_id": task.task_id, "code_sha256": digest(candidate["code"]),
                            "actor_sha256": task.hash, "grade": result})
        return result


class Controller(E0Controller):
    """Reuse the sealed episode logic; substitute transport and resource units."""
    def __init__(self, folder, manifest, transport, code_checker):
        self.folder, self.manifest = Path(folder), manifest
        self.launch_id = manifest["launch_id"]
        self.renderer, self.code_checker = Renderer(), code_checker
        self.ledger = Ledger(self.folder / "ledger.sqlite", max_calls=312)
        self.dispatcher = BoundDispatcher(self.folder, self.ledger, transport, manifest)

    def _record(self, task, stage, checkpoint=None, branches=(), feedback=None,
                arm=None, draw=None, slot=1, lesson=None, summary=None):
        request = (self.renderer.continuation(arm, task, checkpoint, branches, feedback, lesson, summary)
                   if stage == "terminal" else self.renderer.render(stage, task, checkpoint, branches, feedback))
        if not self.renderer.fits(request):
            raise InterfaceError("complete client body exceeds byte admission")
        identity = Identity(self.launch_id, task.task_id, stage, slot=slot, arm=arm, draw=draw)
        response = self.dispatcher.call(identity, request)
        if response.capped:
            raise InterfaceError("capped_output")
        if stage in {"lesson", "summary"} and len(response.text.encode("utf-8")) > 1024:
            raise InterfaceError("writer_visible_byte_cap")
        supplied = source_ids(task)
        if checkpoint:
            supplied.update(f"C.fact{i+1}" for i in range(len(checkpoint.data()["facts"])))
        for index, branch in enumerate(branches):
            supplied.add(f"B{index+1}")
            supplied.update(f"B{index+1}.observation{i+1}" for i in range(len(branch.data()["observations"])))
        if feedback:
            supplied.add(feedback.data()["receipt_id"])
        options = [x["id"] for x in checkpoint.data()["tentative_options"]] if checkpoint else []
        return Record.parse(stage, response.text, task, supplied=supplied, option_ids=options), request

    def run(self, cohort):
        actors = ordered_tasks([x[0] for x in cohort])
        evaluators = {t.task_id: e for t,e in cohort}
        if [t.task_id for t in actors] != self.manifest["task_ids"]:
            raise InterfaceError("cohort differs from frozen allocation")
        rows, indices = [], {"math": 0, "coding": 0}
        started = time.monotonic()
        for task in actors:
            evaluators[task.task_id].check_binding(task)
            index = indices[task.domain]
            indices[task.domain] += 1
            if self.dispatcher.stopped or self.ledger.summary()["blocked"]:
                row = self.empty_row(task, "infrastructure_stop_before_task")
            else:
                row = self.episode(task, evaluators[task.task_id], index)
            rows.append(row)
            write_new(self.folder / "task_dispositions" / (digest(task.task_id)+".json"), wire(row)+"\n")
            print(wire({"task": task.task_id, "completed_tasks": len(rows), "flow": row["flow"],
                        "scheduled_arms": row["scheduled_arms"], "planning_credits": self.ledger.summary()["completed_credits"]}), flush=True)
        write_new(self.folder / "tasks.jsonl", "".join(wire(x)+"\n" for x in rows))
        write_new(self.folder / "usage_events.jsonl", "".join(wire(x)+"\n" for x in self.ledger.events()))
        write_new(self.folder / "accounting.json", wire(self.ledger.summary())+"\n")
        write_new(self.folder / "coding_grades.json", wire(self.code_checker.grades)+"\n")
        write_new(self.folder / "elapsed.json", wire({"episode_and_grading_wall_seconds": time.monotonic()-started})+"\n")
        return rows
