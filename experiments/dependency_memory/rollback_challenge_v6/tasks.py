"""Three seeded challenge families with public, deterministic correctness checks.

These are authored tasks, not claimed benchmark samples. Levels are hypotheses
until measured. The actor receives neither construction seeds nor witnesses.
"""
from copy import deepcopy
import random

from .common import EMPTY, FAMILIES, LEVELS, SEED, sha


def candidate(values):
    return {"values": list(values), "order": [], "files": []}


def grid(rng, level):
    # Generalized Sudoku with extra cages and inequalities. Any satisfying grid
    # is accepted; the planted witness is not an exact-match answer requirement.
    box_rows, box_cols = ((2, 2), (2, 3), (3, 3))[level - 1]
    n = box_rows * box_cols
    def shuffled(xs):
        xs = list(xs); rng.shuffle(xs); return xs
    rows = [b * box_rows + r for b in shuffled(range(box_cols)) for r in shuffled(range(box_rows))]
    cols = [b * box_cols + c for b in shuffled(range(box_rows)) for c in shuffled(range(box_cols))]
    digits = shuffled(range(1, n + 1))
    solution = [digits[(box_cols * (r % box_rows) + r // box_rows + c) % n] for r in rows for c in cols]
    contract = {"instruction": "Fill every cell of the grid. Return values in row-major order; order and files empty. Satisfy every released clue. Any valid solution is accepted.",
                "size": n, "box_rows": box_rows, "box_cols": box_cols,
                "rules": "Integers 1..size. Every row, column and box contains each integer exactly once. Cell indices are zero-based row-major. Cages constrain a sum only; they do not impose distinctness."}
    cells = shuffled(range(n * n))
    given_count = round(n * n * (0.38, 0.28, 0.22)[level - 1])
    records = [{"kind": "given", "cell": i, "value": solution[i]} for i in cells[:given_count]]
    for i in range(0, n * n - 2, 3):
        group = cells[i:i + 3]
        records.append({"kind": "sum", "cells": group, "total": sum(solution[j] for j in group)})
    for _ in range(n):
        a, b = rng.sample(range(n * n), 2)
        if solution[a] != solution[b]:
            records.append({"kind": "less", "a": a if solution[a] < solution[b] else b,
                            "b": b if solution[a] < solution[b] else a})
    rng.shuffle(records)
    return contract, records, candidate(solution)


def run_program(program, x, width):
    """Finite DSL only. No eval, shell, file access, or submitted Python."""
    mask = (1 << width) - 1
    for opcode, constant in zip(program[::2], program[1::2]):
        if opcode == 0: x = (x + constant) & mask
        elif opcode == 1: x ^= constant
        elif opcode == 2: x = (x * constant) & mask
        elif opcode == 3:
            r = constant % width
            x = ((x << r) | (x >> ((width - r) % width))) & mask
        else: raise ValueError("unknown opcode")
    return x


def bitvector(rng, level):
    width, length = ((4, 3), (5, 5), (6, 7))[level - 1]
    mask = (1 << width) - 1
    program = []
    # Alternate operations so the planted map is a composition, not a single
    # multiply/add or identity. Alternative shorter programs remain accepted.
    previous = None
    for _ in range(length):
        opcode = rng.choice([i for i in range(4) if i != previous])
        constant = rng.randrange(1, width) if opcode == 3 else rng.randrange(1, mask + 1)
        if opcode == 2: constant |= 1
        program += [opcode, constant]; previous = opcode
    contract = {"instruction": "Synthesize a straight-line bitvector program matching all released input/output examples. Return values=[opcode,constant,...]. order and files empty. Any matching program within max_instructions is accepted.",
                "width": width, "max_instructions": length,
                "operations": {"0": "x=(x+c) modulo 2**width", "1": "x=x XOR c", "2": "x=(x*c) modulo 2**width", "3": "rotate x left by c modulo width bits"},
                "constants": f"0..{mask}", "execution": "Start with the supplied x; execute pairs from left to right. All words are unsigned width-bit integers."}
    inputs = list(range(mask + 1)); rng.shuffle(inputs)
    records = [{"kind": "example", "x": x, "y": run_program(program, x, width)} for x in inputs]
    return contract, records, candidate(program)


def ledger_answer(records, accounts):
    """Last revision per transaction wins; void revisions suppress the transfer."""
    latest = {}
    for r in records:
        if r["kind"] != "transaction": continue
        if r["tx"] not in latest or (r["revision"], r["sequence"]) > (latest[r["tx"]]["revision"], latest[r["tx"]]["sequence"]):
            latest[r["tx"]] = r
    balances = [0] * accounts
    for r in latest.values():
        if r["void"]: continue
        balances[r["source"]] -= r["amount"]
        balances[r["destination"]] += r["amount"]
    return balances


def ledger(rng, level, profile="standard"):
    sizes = {"standard": ((5, 18), (8, 40), (12, 80)),
             "intermediate": ((5, 22), (6, 28), (7, 34))}
    if profile not in sizes: raise ValueError("unknown ledger profile")
    accounts, transaction_count = sizes[profile][level - 1]
    records = []
    for tx in range(transaction_count):
        revisions = rng.randint(1, 2 + level)
        for revision in range(revisions):
            source, destination = rng.sample(range(accounts), 2)
            records.append({"kind": "transaction", "tx": f"T{tx:03d}", "revision": revision,
                            "source": source, "destination": destination,
                            "amount": rng.randint(1, 50 + level * 50), "void": rng.random() < .15})
    rng.shuffle(records)
    for sequence, r in enumerate(records): r["sequence"] = sequence
    contract = {"instruction": "Reconcile the transaction ledger released so far. Return values=balances for accounts 0..account_count-1; order and files empty. Earlier packets remain relevant. Revisions replace a whole transaction; they are not additional transfers.",
                "account_count": accounts, "opening_balances": [0] * accounts,
                "rules": "For each tx choose the largest revision, breaking a revision tie by largest sequence. Ignore it if void=true. Otherwise subtract amount from source and add amount to destination. A late packet can revise an old transaction. Recompute all balances at every stage."}
    return contract, records, candidate(ledger_answer(records, accounts))


BUILDERS = {"constraint_grid": grid, "bitvector_program": bitvector, "revision_ledger": ledger}


def generate(*, split="screen", seed=SEED, cells=None, replicates=2, stages=1, actions=4, require_candidates=False,
             ledger_profile="standard"):
    if split not in {"screen", "validation", "confirmation", "fixture"}:
        raise ValueError("unknown split")
    if type(replicates) is not int or replicates < 1 or not 1 <= stages <= actions <= 30:
        raise ValueError("positive replicate count and 1 <= stages <= actions <= 30 required")
    if type(require_candidates) is not bool: raise ValueError("require_candidates must be boolean")
    cells = list(cells) if cells is not None else [(f, l) for f in FAMILIES for l in LEVELS]
    if not cells or len(set(map(tuple, cells))) != len(cells) or any(f not in FAMILIES or l not in LEVELS for f, l in cells):
        raise ValueError("distinct valid family/level cells required")
    if ledger_profile not in {"standard", "intermediate"}:
        raise ValueError("unknown ledger profile")
    if ledger_profile != "standard" and any(f != "revision_ledger" for f, _ in cells):
        raise ValueError("intermediate profile is restricted to ledger tasks")
    tasks = []
    for family, level in cells:
        for replicate in range(replicates):
            identity = [seed, split, family, level, replicate] + (["required-candidates"] if require_candidates else [])
            if ledger_profile != "standard": identity += ["ledger-profile", ledger_profile]
            task_seed = int(sha(identity)[:16], 16)
            if family == "revision_ledger":
                contract, records, reference = ledger(random.Random(task_seed), level, ledger_profile)
            else:
                contract, records, reference = BUILDERS[family](random.Random(task_seed), level)
            if require_candidates: contract["require_candidates"] = True
            for i, r in enumerate(records): r["id"] = f"record-{i:04d}"
            packets = [{"requirements": records[len(records)*i//stages:len(records)*(i+1)//stages]} for i in range(stages)]
            if any(not p["requirements"] for p in packets): raise ValueError("empty stage")
            references = [deepcopy(reference) for _ in packets]
            if family == "revision_ledger":
                references = [candidate(ledger_answer([r for p in packets[:i+1] for r in p["requirements"]], contract["account_count"])) for i in range(stages)]
            task = {"task_id": f"v6-{split}-{family}-{sha(identity)[:16]}",
                    "family": family, "domain": "finite", "horizon": f"stages-{stages}", "difficulty": level,
                    "split": split, "replicate": replicate, "action_allowance": actions,
                    "contract": contract, "initial_artifact": deepcopy(EMPTY), "stages": packets,
                    "evaluator": {"seed": task_seed, "reference": reference, "stage_references": references,
                                  "provenance": "repository-authored finite tasks; no measured difficulty at construction"}}
            task["sha256"] = sha(task); tasks.append(task)
    return sorted(tasks, key=lambda t: sha([seed, t["task_id"]]))


def requirements(task, stage):
    return [r for p in task["stages"][:stage + 1] for r in p["requirements"]]


def public_check(task, stage, c, runner=None):
    def mismatch(check):
        return {"status": "public_mismatch", "check": check, "detail": "Candidate violates this released requirement; no replacement answer supplied."}
    if type(c) is not dict or set(c) != {"values", "order", "files"} or c["order"] or c["files"] or type(c["values"]) is not list or any(type(v) is not int for v in c["values"]):
        return {"status": "invalid_candidate"}
    v = c["values"]; contract = task["contract"]; rs = requirements(task, stage)
    if task["family"] == "constraint_grid":
        n = contract["size"]; br, bc = contract["box_rows"], contract["box_cols"]
        if len(v) != n*n or any(x < 1 or x > n for x in v): return mismatch("grid-shape-or-range")
        for i in range(n):
            if len(set(v[i*n:(i+1)*n])) != n: return mismatch(f"row-{i}")
            if len(set(v[i::n])) != n: return mismatch(f"column-{i}")
        for r in range(0, n, br):
            for col in range(0, n, bc):
                if len({v[(r+a)*n+col+b] for a in range(br) for b in range(bc)}) != n: return mismatch(f"box-{r}-{col}")
        for r in rs:
            if r["kind"] == "given" and v[r["cell"]] != r["value"]: return mismatch(r["id"])
            if r["kind"] == "sum" and sum(v[i] for i in r["cells"]) != r["total"]: return mismatch(r["id"])
            if r["kind"] == "less" and v[r["a"]] >= v[r["b"]]: return mismatch(r["id"])
    elif task["family"] == "bitvector_program":
        width = contract["width"]
        if len(v) % 2 or len(v) > 2*contract["max_instructions"] or any(x not in range(4) for x in v[::2]) or any(x not in range(1 << width) for x in v[1::2]): return mismatch("program-format")
        for r in rs:
            if run_program(v, r["x"], width) != r["y"]: return mismatch(r["id"])
    elif task["family"] == "revision_ledger":
        if len(v) != contract["account_count"]: return mismatch("balance-vector-length")
        expected = ledger_answer(rs, len(v))
        for i, (got, want) in enumerate(zip(v, expected)):
            if got != want: return mismatch(f"balance-{i}")
    else: raise ValueError("unknown task family")
    return {"status": "public_pass", "checks": len(rs)}


def terminal_check(task, c, runner=None):
    good = public_check(task, len(task["stages"]) - 1, c)["status"] == "public_pass"
    return {"score": int(good), "disposition": "correct" if good else "public_failure"}
