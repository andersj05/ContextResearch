"""Exact audits of finite memory collisions with adaptive, read-only recovery.

Evaluator world IDs never select controller actions. A controller receives a
retained/public channel cell, the future task, then only tool observations.
The full finite model is public. Recovery observations remain available until
termination; this module does NOT solve another forced compaction during rescue.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import combinations
import json
from math import inf


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


@dataclass(frozen=True)
class Tool:
    name: str
    cost: int
    observations: tuple[str, ...]


@dataclass(frozen=True)
class Task:
    name: str
    trace: tuple[str, ...]
    accepted: tuple[frozenset[str], ...]


class Problem:
    def __init__(self, data):
        self.data = json.loads(canonical(data))
        data = self.data
        self.name = data["name"]
        self.worlds = data["worlds"]
        self.n = len(self.worlds)
        if not 1 <= self.n <= 12:
            raise ValueError("Explicit finite audit supports 1 to 12 worlds")
        self.ids = tuple(w["id"] for w in self.worlds)
        if any(not isinstance(x, str) or not x for x in self.ids) or len(set(self.ids)) != self.n:
            raise ValueError("World IDs must be distinct nonempty strings")
        # A repair encoder may use only the declared pre-compaction observation.
        # Duplicate prehistories require a more general encoder-access model.
        pre = [canonical([w["history"], w["public"]]) for w in self.worlds]
        if len(set(pre)) != self.n:
            raise ValueError("Worlds must have distinct declared visible prehistories")
        groups = {}
        for i, w in enumerate(self.worlds):
            groups.setdefault(canonical([w["retained"], w["public"]]), []).append(i)
        self.cells = tuple(tuple(v) for v in groups.values())
        self.tools = tuple(Tool(t["name"], t["cost"],
                                tuple(canonical(t["observations"][w]) for w in self.ids))
                           for t in data["tools"])
        if len({t.name for t in self.tools}) != len(self.tools):
            raise ValueError("Duplicate tool name")
        if any(type(t.cost) is not int or t.cost <= 0 for t in self.tools):
            raise ValueError("Recovery costs must be strictly positive integers")
        self.tasks = tuple(Task(t["name"], tuple(t["trace"]),
                                tuple(frozenset(t["accepted"][w]) for w in self.ids))
                           for t in data["tasks"])
        if not self.tasks or len({t.name for t in self.tasks}) != len(self.tasks):
            raise ValueError("Supply distinct future task names")
        for task in self.tasks:
            if any(not a or any(not isinstance(x, str) for x in a) for a in task.accepted):
                raise ValueError("Each world needs at least one accepted terminal action")
            if any(not isinstance(x, str) for x in task.trace):
                raise ValueError("Future trace entries must be public strings")
        self.budget = data["budget"]
        if type(self.budget) is not int or self.budget < 0:
            raise ValueError("Budget must be a nonnegative integer")


class Solver:
    def __init__(self, problem, task):
        self.problem = problem
        self.task = task
        self.answers = sorted(set().union(*task.accepted))

    def common(self, cell):
        return sorted(set.intersection(*(set(self.task.accepted[i]) for i in cell)))

    def split(self, cell, tool):
        groups = {}
        for i in cell:
            groups.setdefault(tool.observations[i], []).append(i)
        return {o: tuple(group) for o, group in sorted(groups.items())}

    @cache
    def optimum(self, cell):
        """Minimize worst-case additional recovery cost; terminal action costs 0."""
        answers = self.common(cell)
        if answers:
            return 0, {"answer": answers[0]}
        best, policy = inf, None
        for tool in self.problem.tools:
            groups = self.split(cell, tool)
            # A deterministic read-only query that does not refine knowledge
            # cannot help; deleting it strictly reduces cost with no effect.
            if len(groups) == 1:
                continue
            branches = {o: self.optimum(group) for o, group in groups.items()}
            cost = tool.cost + max(result[0] for result in branches.values())
            if cost < best:
                best = cost
                policy = {"tool": tool.name,
                          "branches": {o: result[1] for o, result in branches.items()}}
        return best, policy

    def obstruction(self, cell, budget):
        """Proof DAG: every answer fails somewhere; every tool has a bad branch."""
        if self.optimum(cell)[0] <= budget:
            raise ValueError("Cannot certify an obstruction for a feasible budget")
        nodes = {}

        def visit(group, remaining):
            key = canonical([group, remaining])
            if key in nodes:
                return key
            node = {"worlds": list(group), "budget": remaining,
                    "answers": {a: next(i for i in group if a not in self.task.accepted[i])
                                for a in self.answers}, "tools": {}}
            nodes[key] = node
            for tool in self.problem.tools:
                if tool.cost > remaining:
                    node["tools"][tool.name] = {"over_budget": True}
                elif len(self.split(group, tool)) == 1:
                    node["tools"][tool.name] = {"no_information": True}
                else:
                    obs, child = next((o, g) for o, g in self.split(group, tool).items()
                                      if self.optimum(g)[0] > remaining - tool.cost)
                    node["tools"][tool.name] = {
                        "observation": obs, "child": visit(child, remaining - tool.cost)}
            return key

        return {"root": visit(cell, budget), "nodes": nodes}

    def smallest_obstruction(self, cell, budget):
        for size in range(1, len(cell) + 1):
            for group in combinations(cell, size):
                if self.optimum(group)[0] > budget:
                    return group
        return None

    def impossibility_atom(self, cell):
        """Worlds that even ALL available tools cannot distinguish or solve."""
        groups = {}
        for i in cell:
            signature = tuple(t.observations[i] for t in self.problem.tools)
            groups.setdefault(signature, []).append(i)
        return next(tuple(g) for g in groups.values() if not self.common(tuple(g)))

    def nonadaptive_cost(self, cell):
        """Best fixed set of queries, all paid before choosing a terminal action."""
        best = inf
        for size in range(len(self.problem.tools) + 1):
            for tools in combinations(self.problem.tools, size):
                groups = {}
                for i in cell:
                    groups.setdefault(tuple(t.observations[i] for t in tools), []).append(i)
                if all(self.common(tuple(g)) for g in groups.values()):
                    best = min(best, sum(t.cost for t in tools))
        return best


def verify_obstruction(problem, task, cell, budget, proof):
    """Check a supplied lower proof without using the optimization recurrence.

    A rejecting world suffices to refute each answer. For each affordable
    splitting query, one realizable observation recursively refutes the smaller
    budget. Constant observations are checked as useless read-only queries;
    deleting them improves any policy. Recursive children are strict subsets.
    """
    answers = set().union(*task.accepted)
    tools = {t.name: t for t in problem.tools}
    checked = set()

    def check(key, group, remaining):
        node = proof["nodes"][key]
        if node["worlds"] != list(group) or node["budget"] != remaining:
            raise ValueError("Proof changed its information cell or budget")
        if key in checked:
            return
        if set(node["answers"]) != answers or set(node["tools"]) != set(tools):
            raise ValueError("Proof omitted a legal action")
        for answer, i in node["answers"].items():
            if type(i) is not int or i not in group or answer in task.accepted[i]:
                raise ValueError("Invalid rejecting world")
        for name, entry in node["tools"].items():
            tool = tools[name]
            if tool.cost > remaining:
                if entry != {"over_budget": True}:
                    raise ValueError("Invalid budget rejection")
            elif len({tool.observations[i] for i in group}) == 1:
                if entry != {"no_information": True}:
                    raise ValueError("Invalid nonrefining-query rejection")
            else:
                obs = entry["observation"]
                child = tuple(i for i in group if tool.observations[i] == obs)
                if not child:
                    raise ValueError("Unrealizable adversarial observation")
                check(entry["child"], child, remaining - tool.cost)
        checked.add(key)

    check(proof["root"], tuple(cell), budget)
    if checked != set(proof["nodes"]):
        raise ValueError("Unreachable extra proof nodes")
    return len(checked)


def verify_impossibility_atom(problem, task, cell, atom):
    """Budget-independent check that no allowed query can resolve this group."""
    if not atom or len(set(atom)) != len(atom) or not set(atom) <= set(cell):
        raise ValueError("Invalid impossible subcell")
    if set.intersection(*(set(task.accepted[i]) for i in atom)):
        raise ValueError("Impossible subcell has a universally accepted answer")
    if any(len({tool.observations[i] for i in atom}) != 1 for tool in problem.tools):
        raise ValueError("An allowed tool can distinguish the claimed atom")
    return True


def replay_policy(problem, task, cell, policy):
    """Independent forward execution; no evaluator ID is passed to a decision."""
    tools = {t.name: t for t in problem.tools}
    rows = []
    for world in cell:
        node, cost, trace = policy, 0, []
        # Generated finite trees refine at every query, hence at most n-1 queries.
        for _ in range(problem.n + 1):
            if "answer" in node:
                answer = node["answer"]
                if answer not in task.accepted[world]:
                    raise ValueError("Policy fails in a declared world")
                rows.append({"world": problem.ids[world], "cost": cost,
                             "answer": answer, "observations": trace})
                break
            tool = tools[node["tool"]]
            observation = tool.observations[world]
            cost += tool.cost
            trace.append({"tool": tool.name, "observation": observation})
            node = node["branches"][observation]
        else:
            raise ValueError("Nonterminating or unexpectedly long policy")
    return rows


def minimum_repair_partition(cell, solvers, budget):
    """Exact extra-message codebook; preserves the original retained/public cell.

    A new message is chosen from visible prehistory BEFORE the task is revealed.
    Its cell must support every declared future task. This optimizes states,
    not selected fields, serialized bytes, natural-language summaries or tokens.
    """
    @cache
    def safe(group):
        return all(s.optimum(group)[0] <= budget for s in solvers)

    @cache
    def partition(group):
        if not group:
            return ()
        if safe(group):
            return (group,)
        first, rest = group[0], group[1:]
        best = None
        for size in range(len(rest), -1, -1):
            for others in combinations(rest, size):
                candidate = (first,) + others
                if not safe(candidate):
                    continue
                remaining = tuple(i for i in rest if i not in others)
                choice = (candidate,) + partition(remaining)
                if best is None or len(choice) < len(best):
                    best = choice
        return best

    return partition(tuple(cell))


def audit(problem):
    solvers = [Solver(problem, task) for task in problem.tasks]
    task_rows, shortest = [], None
    for solver in solvers:
        rows = []
        for cell in problem.cells:
            cost, policy = solver.optimum(cell)
            row = {"worlds": list(cell), "minimum_worst_case_recovery_cost": None if cost == inf else cost,
                   "best_fixed_query_cost": None if (fixed := solver.nonadaptive_cost(cell)) == inf else fixed,
                   "within_budget": cost <= problem.budget, "policy": policy}
            if policy is not None:
                replay = replay_policy(problem, solver.task, cell, policy)
                if max(r["cost"] for r in replay) != cost:
                    raise AssertionError("Policy does not attain reported optimum")
                row["replays"] = replay
            else:
                atom = solver.impossibility_atom(cell)
                verify_impossibility_atom(problem, solver.task, cell, atom)
                row["unrecoverable_at_any_budget"] = list(atom)
            lower_budget = problem.budget if cost == inf else cost - 1
            if lower_budget >= 0:
                proof = solver.obstruction(cell, lower_budget)
                verify_obstruction(problem, solver.task, cell, lower_budget, proof)
                row["lower_bound_budget"] = lower_budget
                row["lower_bound_proof"] = proof
            witness = solver.smallest_obstruction(cell, problem.budget)
            row["smallest_failing_group"] = list(witness) if witness else None
            row["all_pairs_within_budget"] = all(solver.optimum(pair)[0] <= problem.budget
                                                 for pair in combinations(cell, 2))
            if witness:
                item = {"task": solver.task.name, "trace": list(solver.task.trace),
                        "worlds": list(witness)}
                if shortest is None or len(item["trace"]) < len(shortest["trace"]):
                    shortest = item
            rows.append(row)
        task_rows.append({"task": solver.task.name, "trace": list(solver.task.trace), "cells": rows})
    repairs = [minimum_repair_partition(c, solvers, problem.budget) for c in problem.cells]
    messages = max(len(p) for p in repairs)
    return {"schema": 1, "name": problem.name, "world_ids": list(problem.ids),
            "budget": problem.budget, "tasks": task_rows,
            "shortest_failing_declared_trace": shortest,
            "repair": {"partitions": [[list(g) for g in p] for p in repairs],
                       "extra_messages": messages, "extra_fixed_bits": (messages - 1).bit_length(),
                       "scope": "exact finite codebook refining existing cells across all listed tasks"},
            "channels": {"retained_utf8_bytes_by_world": [len(canonical(w["retained"]).encode("utf-8"))
                                                         for w in problem.worlds],
                         "public_utf8_bytes_by_world": [len(canonical(w["public"]).encode("utf-8"))
                                                       for w in problem.worlds],
                         "recovery_observations_retained_until_terminal": True,
                         "further_forced_compaction": False,
                         "cost_unit": "synthetic recovery units; terminal action excluded"}}
