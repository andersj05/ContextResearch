"""Planted scheduling and routing tasks; independent checker in verification.py."""
import random


def scheduling(rng, hard):
    n = 7 if hard else 4
    duration = [rng.randint(1, 4) for _ in range(n)]
    order = list(range(n)); rng.shuffle(order)
    witness = [0] * n
    clock = 0
    for i in order:
        witness[i] = clock + rng.randint(1, 3)
        clock = witness[i] + duration[i]
    machine = [rng.randrange(2 if hard else 3) for _ in range(n)]
    records = []
    for i in range(n):
        records.append({"id": f"window-{i}", "kind": "window", "job": i,
                        "release": max(0, witness[i] - rng.randint(1, 5)),
                        "deadline": witness[i] + duration[i] + rng.randint(1, 5)})
    records.append({"id": "machines", "kind": "machines", "assignment": machine})
    for a, b in zip(order, order[1:]):
        records.append({"id": f"precedence-{a}-{b}", "kind": "precedence", "a": a, "b": b,
                        "lag": rng.randint(0, witness[b] - witness[a] - duration[a])})
    for i in range(3 if hard else 2):
        coefficients = [rng.randint(-3, 3) for _ in range(n)]
        total = sum(a * b for a, b in zip(coefficients, witness))
        records.append({"id": f"coupling-{i}", "kind": "linear", "coefficients": coefficients,
                        "minimum": total - rng.randint(0, 3), "maximum": total + rng.randint(0, 3)})
    contract = {"instruction": "Find integer start times for ALL jobs. Satisfy every requirement revealed so far, including older stages. Later requirements can require changing earlier choices. A stage pass is provisional. No optimization objective.",
                "jobs": list(range(n)), "durations": duration, "start_bounds": [0, clock + 4],
                "candidate_format": "values = start time in job order; order and files must be empty",
                "semantics": "finish=start+duration; precedence requires start[b]>=finish[a]+lag; equal-machine intervals may touch but not overlap; linear bounds inclusive"}
    return contract, records, {"values": witness, "order": [], "files": []}


def routing(rng, hard):
    n = 8 if hard else 5
    tour = list(range(1, n)); rng.shuffle(tour)
    costs = [[0 if a == b else rng.randint(1, 9) for b in range(n)] for a in range(n)]
    t = 0; arrivals = {0: 0}; previous = 0
    for node in tour:
        t += costs[previous][node]; arrivals[node] = t; previous = node
    records = [{"id": f"travel-{i}", "kind": "travel", "from": i, "costs": row} for i, row in enumerate(costs)]
    for node in tour:
        records.append({"id": f"visit-{node}", "kind": "visit_window", "node": node,
                        "earliest": max(0, arrivals[node] - (0 if hard else 3)), "latest": arrivals[node] + rng.randint(0, 4)})
    for a, b in zip(tour[::2], tour[1::2]):
        records.append({"id": f"before-{a}-{b}", "kind": "before", "a": a, "b": b})
    records.append({"id": "return-budget", "kind": "route_budget", "maximum": t + costs[tour[-1]][0] + (0 if hard else 4)})
    contract = {"instruction": "Return a permutation of nodes 1..n-1. Start at depot 0 at time 0, visit each node once, return to 0. Satisfy all revealed requirements, including older stages. A stage pass is provisional. No optimization objective.",
                "node_count": n, "candidate_format": "order = route excluding depot; values and files must be empty",
                "semantics": "Travel times are directed. No waiting is allowed. Window bounds inclusive. A time/window/budget is checked only when all travel rows needed for it have been revealed."}
    return contract, records, {"values": [], "order": tour, "files": []}


def violation(task, candidate, requirements):
    """First public violation; reads no witness, seed, reserved suite or future packet."""
    contract = task["contract"]
    if task["family"] == "scheduling":
        values = candidate["values"]; duration = contract["durations"]
        if len(values) != len(duration) or candidate["order"] or candidate["files"]:
            return {"check": "shape", "detail": "One start per job required; other candidate fields empty."}
        lo, hi = contract["start_bounds"]
        if any(type(x) is not int or not lo <= x <= hi for x in values):
            return {"check": "bounds", "detail": [lo, hi]}
        for r in requirements:
            kind = r["kind"]; ok = True
            if kind == "window":
                j = r["job"]; ok = r["release"] <= values[j] and values[j] + duration[j] <= r["deadline"]
            elif kind == "precedence":
                ok = values[r["b"]] >= values[r["a"]] + duration[r["a"]] + r["lag"]
            elif kind == "linear":
                total = sum(c * x for c, x in zip(r["coefficients"], values))
                ok = r["minimum"] <= total <= r["maximum"]
            elif kind == "machines":
                ok = all(r["assignment"][a] != r["assignment"][b] or values[a] + duration[a] <= values[b] or values[b] + duration[b] <= values[a]
                         for a in range(len(values)) for b in range(a + 1, len(values)))
            else:
                raise ValueError("unknown scheduling requirement")
            if not ok:
                return {"check": r["id"], "detail": "Candidate violates this previously released requirement."}
    else:
        order = candidate["order"]; n = contract["node_count"]
        if candidate["values"] or candidate["files"] or len(order) != n - 1 or any(type(x) is not int for x in order) or set(order) != set(range(1, n)):
            return {"check": "route_shape", "detail": "Permutation of nondepot nodes required."}
        rows = {r["from"]: r["costs"] for r in requirements if r["kind"] == "travel"}
        path = [0] + order + [0]; elapsed = 0; arrivals = {}; known = True
        for a, b in zip(path, path[1:]):
            known = known and a in rows
            if known:
                elapsed += rows[a][b]; arrivals[b] = elapsed
        for r in requirements:
            kind = r["kind"]; ok = True
            if kind == "visit_window" and r["node"] in arrivals:
                ok = r["earliest"] <= arrivals[r["node"]] <= r["latest"]
            elif kind == "before":
                ok = order.index(r["a"]) < order.index(r["b"])
            elif kind == "route_budget" and known:
                ok = elapsed <= r["maximum"]
            if not ok:
                return {"check": r["id"], "detail": "Candidate violates this previously released requirement."}
    return None
