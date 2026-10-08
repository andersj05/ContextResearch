"""E2 state machine exercised only with FakeTransport in this implementation."""
from __future__ import annotations

import os
from pathlib import Path
import time

from .accounting import AccountingError, Identity, Ledger
from .contexts import ARMS, Renderer, shared_hashes
from .grading import CodeChecker, InfrastructureError, MathChecker, terminal_grade
from .records import ActorTask, EvaluatorTask, InterfaceError, Record, digest, wire
from .schedule import ordered_tasks, task_slots, terminal_order, writer_order
from .transport import FakeTransport, Response, UnknownDispatch


def write_new(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


class Dispatcher:
    def __init__(self, folder, ledger, transport, renderer):
        if type(transport) is not FakeTransport:
            raise ValueError("only the offline fake transport is implemented")
        self.folder, self.ledger, self.transport, self.renderer = Path(folder), ledger, transport, renderer
        self.stopped = False

    def call(self, identity, request):
        if self.stopped:
            raise UnknownDispatch("launch already stopped")
        if not self.renderer.fits(request):
            raise InterfaceError("complete request exceeds its admission cap")
        self.ledger.plan(identity, request.hash)
        self.ledger.reserve(identity)
        write_new(self.folder / "requests" / (identity.key + ".json"), request.json_text + "\n")
        self.ledger.dispatch(identity, request.hash)
        start = time.monotonic()
        try:
            response = self.transport.generate(identity, request)
            if type(response) is not Response:
                raise AccountingError("missing response")
            write_new(self.folder / "responses" / (identity.key + ".json"), wire({"text": response.text,
                      "capped": response.capped, "usage": vars(response.usage) if response.usage else None, "elapsed_seconds": time.monotonic() - start,
                      "metadata": list(response.metadata)}) + "\n")
            if response.usage is None:
                raise AccountingError("missing usage")
            response.usage.validate()
            self.ledger.complete(identity, response.usage, "capped" if response.capped else "response_received",
                                 {"request_hash": request.hash, "transport": self.transport.transport_id,
                                  "elapsed_seconds": time.monotonic() - start, "returned_metadata": list(response.metadata)})
            return response
        except Exception as exc:
            self.ledger.unknown(identity, type(exc).__name__)
            self.stopped = True
            raise UnknownDispatch("unknown dispatch or metering; launch stopped") from exc


class Controller:
    def __init__(self, folder, launch_id, transport, renderer=None, code_checker=None, ceiling="5.00", max_calls=320):
        if type(transport) is not FakeTransport:
            raise ValueError("only the offline fake transport is implemented")
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=False)
        self.launch_id, self.renderer, self.code_checker = launch_id, renderer or Renderer(), code_checker
        self.ledger = Ledger(self.folder / "ledger.sqlite", ceiling=ceiling, max_calls=max_calls)
        self.dispatcher = Dispatcher(self.folder, self.ledger, transport, self.renderer)

    def _record(self, task, stage, checkpoint=None, branches=(), feedback=None, arm=None, draw=None, slot=1, lesson=None, summary=None):
        request = (self.renderer.continuation(arm, task, checkpoint, branches, feedback, lesson, summary)
                   if stage == "terminal" else self.renderer.render(stage, task, checkpoint, branches, feedback))
        identity = Identity(self.launch_id, task.task_id, stage, slot=slot, arm=arm, draw=draw)
        response = self.dispatcher.call(identity, request)
        if response.capped:
            raise InterfaceError("capped_output")
        if stage in {"lesson", "summary"} and self.renderer.counter.visible(response.text) > 1024:
            raise InterfaceError("writer_visible_cap")
        supplied = task.source_ids()
        if checkpoint:
            supplied.update(f"C.fact{i + 1}" for i in range(len(checkpoint.data()["facts"])))
        for index, branch in enumerate(branches):
            supplied.add(f"B{index + 1}")
            supplied.update(f"B{index + 1}.observation{i + 1}" for i in range(len(branch.data()["observations"])))
        if feedback:
            supplied.add(feedback.data()["receipt_id"])
        options = [x["id"] for x in checkpoint.data()["tentative_options"]] if checkpoint else []
        return Record.parse(stage, response.text, task, supplied=supplied, option_ids=options), request

    def run(self, cohort):
        actors = [x[0] for x in cohort]
        if len({t.task_id for t in actors}) != len(actors):
            raise InterfaceError("duplicate task identity")
        evaluators = {t.task_id: e for t, e in cohort}
        for task in actors:
            if type(task) is not ActorTask or type(evaluators[task.task_id]) is not EvaluatorTask:
                raise InterfaceError("separate typed actor/evaluator records required")
            evaluators[task.task_id].check_binding(task)
        order = ordered_tasks(actors)
        write_new(self.folder / "cohort_public.jsonl", "".join(wire({"task_id": t.task_id, "domain": t.domain, "stratum": t.stratum,
                                                                  "public": t.data(), "sha256": t.hash}) + "\n" for t in order))
        write_new(self.folder / "cohort_evaluator.jsonl", "".join(wire({"task_id": t.task_id, "actor_hash": t.hash,
                                                                     "material": evaluators[t.task_id].data()}) + "\n" for t in order))
        domain_indices = {"math": 0, "coding": 0}
        schedule = []
        for task in order:
            schedule.extend(vars(x) for x in task_slots(self.launch_id, task, domain_indices[task.domain]))
            domain_indices[task.domain] += 1
        write_new(self.folder / "schedule.jsonl", "".join(wire(x) + "\n" for x in schedule))
        rows, domain_indices = [], {"math": 0, "coding": 0}
        for task in order:
            index = domain_indices[task.domain]
            domain_indices[task.domain] += 1
            if self.dispatcher.stopped or self.ledger.summary()["blocked"]:
                rows.append(self.empty_row(task, "infrastructure_stop_before_task"))
                continue
            rows.append(self.episode(task, evaluators[task.task_id], index))
        write_new(self.folder / "tasks.jsonl", "".join(wire(x) + "\n" for x in rows))
        write_new(self.folder / "usage_events.jsonl", "".join(wire(x) + "\n" for x in self.ledger.events()))
        write_new(self.folder / "accounting.json", wire({"unit": "synthetic_API_USD_not_actual_spend", **self.ledger.summary()}) + "\n")
        return rows

    @staticmethod
    def empty_row(task, disposition=None):
        return {"task_id": task.task_id, "domain": task.domain, "stratum": task.stratum,
                "flow": [disposition] if disposition else [], "public_failure": False,
                "lesson_usable": False, "summary_usable": False, "primary_scheduled": False,
                "capacity_infeasible": False, "scheduled_arms": [], "grades": {arm: [None, None] for arm in ARMS},
                "terminal_dispositions": {arm: ["not_scheduled", "not_scheduled"] for arm in ARMS},
                "context_hashes": {}, "checkpoint_content": None, "branch_count": 0, "repeated_candidates": {arm: [None, None] for arm in ARMS}}

    def episode(self, task, evaluator, index):
        row = self.empty_row(task)
        # Persist a start before the first dispatch; interrupted tasks remain visible.
        write_new(self.folder / "task_starts" / (digest(task.task_id) + ".json"), wire(row) + "\n")
        branches, feedback, lesson, summary, checkpoint, rejected = [], None, None, None, None, None
        try:
            checkpoint, _ = self._record(task, "checkpoint")
        except InterfaceError as exc:
            row["flow"].append("invalid_checkpoint:" + str(exc))
            return row
        except (UnknownDispatch, AccountingError):
            row["flow"].append("infrastructure_stop_checkpoint")
            self.dispatcher.stopped = True
            return row
        row["checkpoint_content"] = "has_authored_facts_unverified" if checkpoint.data()["facts"] else "restatement_checkpoint"
        for slot in (1, 2):
            try:
                branch, _ = self._record(task, "branch", checkpoint, branches, slot=slot)
                branches.append(branch)
                row["branch_count"] += 1
                if branch.data()["status"] == "continue":
                    row["flow"].append("no_candidate")
                    continue
                candidate = branch.data()["artifact"]
                checker = MathChecker(task) if task.domain == "math" else self.code_checker
                if checker is None:
                    raise InfrastructureError("isolated coding runner unavailable")
                feedback = (checker.receipt(candidate, f"B{slot}", f"F{slot}") if task.domain == "math"
                            else checker.receipt(task, candidate, f"B{slot}", f"F{slot}"))
                row["flow"].append(feedback.data()["status"])
                if feedback.eligible:
                    row["public_failure"] = True
                    rejected = candidate
                elif feedback.data()["status"] == "public_pass":
                    terminal = Record.parse("terminal", wire(candidate), task)
                    row["initial_grade"] = terminal_grade(task, evaluator, terminal, self.code_checker)
                break
            except InterfaceError as exc:
                row["flow"].append("malformed_branch:" + str(exc))
                break
            except (UnknownDispatch, AccountingError, InfrastructureError):
                row["flow"].append("infrastructure_stop_branch")
                self.dispatcher.stopped = True
                break
        if not row["public_failure"]:
            return row
        for kind in writer_order(index):
            if self.dispatcher.stopped:
                break
            try:
                writer, _ = self._record(task, kind, checkpoint, branches, feedback)
                if kind == "lesson":
                    lesson, row["lesson_usable"] = writer, True
                else:
                    summary, row["summary_usable"] = writer, True
            except InterfaceError as exc:
                row["flow"].append(kind + "_unusable:" + str(exc))
            except (UnknownDispatch, AccountingError):
                row["flow"].append("infrastructure_stop_" + kind)
                self.dispatcher.stopped = True
        prepared = {arm: self.renderer.continuation(arm, task, checkpoint, branches, feedback, lesson, summary) for arm in ARMS}
        primary_fit = all(self.renderer.fits(prepared[arm]) for arm in ("K", "R"))
        row["capacity_infeasible"] = bool(lesson and not primary_fit)
        row["primary_scheduled"] = bool(lesson and primary_fit)
        allowed = {"K": row["primary_scheduled"], "R": row["primary_scheduled"],
                   "Z": self.renderer.fits(prepared["Z"]), "G": bool(summary and self.renderer.fits(prepared["G"]))}
        row["scheduled_arms"] = [arm for arm in ARMS if allowed[arm]]
        row["context_hashes"] = {arm: {"request_sha256": req.hash, "shared": shared_hashes(req),
                                              "input_units": req.input_units, "counter_id": req.counter_id} for arm, req in prepared.items()}
        write_new(self.folder / "preparations" / (digest(task.task_id) + ".json"), wire({"checkpoint": checkpoint.data(),
                   "branch": [b.data() for b in branches], "feedback": feedback.data(), "lesson": lesson.data() if lesson else None,
                   "summary": summary.data() if summary else None, "routing": row["context_hashes"]}) + "\n")
        outputs = {}
        for arm, draw in terminal_order(index):
            if not allowed[arm]:
                continue
            row["terminal_dispositions"][arm][draw - 1] = "unknown_not_dispatched"
            if self.dispatcher.stopped:
                continue
            try:
                output, request = self._record(task, "terminal", checkpoint, branches, feedback, arm, draw, slot=draw,
                                               lesson=lesson, summary=summary)
                if request.hash != prepared[arm].hash:
                    raise InfrastructureError("continuation changed after preflight")
                outputs[(arm, draw)] = output
                row["terminal_dispositions"][arm][draw - 1] = "received_pending_grade"
                row["repeated_candidates"][arm][draw - 1] = output.data() == rejected
            except InterfaceError as exc:
                row["grades"][arm][draw - 1] = 0
                row["terminal_dispositions"][arm][draw - 1] = "known_invalid:" + str(exc)
            except (UnknownDispatch, AccountingError, InfrastructureError):
                row["flow"].append("infrastructure_stop_terminal")
                self.dispatcher.stopped = True
        # No terminal grade or earlier draw enters any scheduled request.
        for (arm, draw), output in outputs.items():
            try:
                grade = terminal_grade(task, evaluator, output, self.code_checker)
                row["grades"][arm][draw - 1] = grade["score"]
                row["terminal_dispositions"][arm][draw - 1] = grade["disposition"]
            except InfrastructureError:
                row["terminal_dispositions"][arm][draw - 1] = "grading_infrastructure_unknown"
                row["flow"].append("infrastructure_stop_grading")
                self.dispatcher.stopped = True
        return row
