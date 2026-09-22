"""Finite counterexample-guided candidate elimination (established machinery).

A witness is an unsafe WHOLE collision group, not a single bad agent rollout.
Keep its proof and reject candidates that merge that same group after the same
public continuation. No realized-instance feedback reaches the execution policy.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import inf

from ..collision_audit.engine import Solver, canonical, replay_policy, verify_obstruction


@dataclass(frozen=True)
class Witness:
    route: int
    worlds: tuple[int, ...]
    budget: int
    proof: dict


class Verifier:
    def __init__(self, workflow, routes=None):
        self.workflow = workflow
        self.routes = tuple(range(len(workflow.routes))) if routes is None else tuple(routes)
        if not self.routes or len(set(self.routes)) != len(self.routes) or any(
                type(r) is not int or not 0 <= r < len(workflow.routes) for r in self.routes):
            raise ValueError("Supply nonempty distinct valid route indices")
        self.cache = {}
        self.audit_calls = 0
        self.cell_checks = 0
        self.constraint_checks = 0

    def problem(self, candidate, route):
        key = (candidate, route)
        if key not in self.cache:
            self.cache[key] = self.workflow.problem(candidate, route)
        return self.cache[key]

    def first_failure(self, candidate):
        self.audit_calls += 1
        for route in self.routes:
            p = self.problem(candidate, route)
            solver = Solver(p, p.tasks[0])
            for cell in p.cells:
                self.cell_checks += 1
                if solver.optimum(cell)[0] > p.budget:
                    worlds = solver.smallest_obstruction(cell, p.budget)
                    proof = solver.obstruction(worlds, p.budget)
                    verify_obstruction(p, p.tasks[0], worlds, p.budget, proof)
                    return Witness(route, worlds, p.budget, proof)
        return None

    def merges(self, candidate, witness):
        self.constraint_checks += 1
        p = self.problem(candidate, witness.route)
        if p.budget != witness.budget:
            raise ValueError("Cannot reuse feedback at a different recovery budget")
        # Revalidate against the CURRENT task/tool table. This is necessary if
        # feedback is ever moved across contracts, revisions, or access changes.
        verify_obstruction(p, p.tasks[0], witness.worlds, witness.budget, witness.proof)
        values = {canonical([p.worlds[i]["retained"], p.worlds[i]["public"]])
                  for i in witness.worlds}
        return len(values) == 1

    def stats(self):
        return {"audit_calls": self.audit_calls, "cell_checks": self.cell_checks,
                "constraint_checks": self.constraint_checks,
                "constructed_candidate_routes": len(self.cache),
                "adapter_terminal_checks": len(self.cache) * 8 * 12,
                "adapter_prefix_tool_calls": len(self.cache) * 8 * 8,
                "adapter_recovery_observations": len(self.cache) * 8 if self.workflow.contract.recovery else 0}


def learn(workflow, mode="accumulated", routes=None, limit=32):
    if mode not in {"accumulated", "last_only", "enumerate", "one_pass", "critical_fields"}:
        raise ValueError("Unknown feedback control")
    if type(limit) is not int or limit < 1:
        raise ValueError("limit must be a positive integer")
    verifier = Verifier(workflow, routes)
    current = workflow.critical_fields if mode == "critical_fields" else workflow.initial
    constraints, history, seen, tested = [], [], set(), set()
    max_constraint_bytes = 2
    result = {"mode": mode}
    for _ in range(limit):
        state = (current, tuple((w.route, w.worlds) for w in constraints))
        if state in seen:
            result.update(status="cycle", candidate=None)
            break
        seen.add(state)
        witness = verifier.first_failure(current)
        history.append({"candidate": current.name, "fields": list(current.fields),
                        "witness": asdict(witness) if witness else None})
        tested.add(current)
        if witness is None:
            result.update(status="certified", candidate=current.name)
            break
        if mode in {"one_pass", "critical_fields"}:
            result.update(status="rejected", candidate=None)
            break
        constraints = constraints + [witness] if mode == "accumulated" else [witness]
        max_constraint_bytes = max(max_constraint_bytes,
                                   len(canonical([asdict(w) for w in constraints]).encode()))
        if mode == "enumerate":
            # Feedback says only that the previous proposal failed. Try each
            # other proposal once in the same fixed size/lexicographic order.
            choices = (c for c in workflow.candidates if c not in tested)
        else:
            choices = (c for c in workflow.candidates
                       if all(not verifier.merges(c, w) for w in constraints))
        current = next(choices, None)
        if current is None:
            result.update(status="exhausted_family", candidate=None)
            break
    else:
        result.update(status="round_limit", candidate=None)
    result.update(history=history, audit_log_utf8_bytes=len(canonical(history).encode()),
                  max_constraint_utf8_bytes=max_constraint_bytes, **verifier.stats())
    return result


def successful_candidate(workflow, result):
    return next((c for c in workflow.candidates if c.name == result["candidate"]), None)


def certificate_replays(workflow, candidate):
    """Replay all certified final controllers, then execute each terminal submit."""
    import json
    from ..artifact_workflow import Action, Receipt

    rows = []
    for route in range(len(workflow.routes)):
        p = workflow.problem(candidate, route)
        solver = Solver(p, p.tasks[0])
        for cell in p.cells:
            cost, policy = solver.optimum(cell)
            if cost == inf or cost > p.budget:
                raise ValueError("Candidate is not certified for this contract")
            for row in replay_policy(p, p.tasks[0], cell, policy):
                world = p.ids.index(row["world"])
                env = workflow.checkpoint(candidate, workflow.bits[world], workflow.routes[route])[0]
                for observation in row["observations"]:
                    obs = env.step(Action("recover_receipt"))
                    actual = canonical([asdict(r) for r in obs.receipts])
                    if actual != observation["observation"]:
                        raise AssertionError("Modeled tool response disagrees with execution")
                outcome = env.step(Action("submit", Receipt(**json.loads(row["answer"]))))
                if not outcome.success:
                    raise AssertionError("Certified terminal action failed executable verifier")
                rows.append({"route": route, "world": world, "recovery_units": row["cost"],
                             "environment_units": env.cost_units, "success": outcome.success})
    return rows
