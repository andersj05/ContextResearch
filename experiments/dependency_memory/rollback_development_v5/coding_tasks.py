"""Two real Python-module repair families with staged public and reserved cases."""
from copy import deepcopy
import itertools
import random

from .common import wire

FILES = ("engine.py", "rules.py")

LEDGER_RULES = '''def rounded(n, d, mode):
    return (n + d // 2) // d if mode == "half_up" else n // d

def amount(e, mode):
    raw = e["price"] * e.get("quantity", 1)
    discount = min(10000, max(0, e.get("discount_bp", 0)))
    net = rounded(raw * (10000 - discount), 10000, mode)
    net += rounded(net * e.get("tax_bp", 0), 10000, mode)
    return -net if e.get("kind") == "refund" else net
'''
LEDGER_ENGINE = '''from rules import amount

def solve(data):
    chosen = {}
    for pos, e in enumerate(data["events"]):
        if e.get("sequence", 0) > data.get("cutoff", 10**9):
            continue
        key = e.get("id", "anonymous:" + str(pos))
        if key not in chosen or (e.get("revision", 0), pos) >= chosen[key][0]:
            chosen[key] = ((e.get("revision", 0), pos), e)
    result = {}
    for _, e in chosen.values():
        if e.get("void", False):
            continue
        key = e.get("account", "default") + "|" + e.get("currency", "USD")
        result[key] = result.get(key, 0) + amount(e, data["rounding"])
    for key, credit in data.get("opening", {}).items():
        result[key] = result.get(key, 0) + credit
    return {"balances": result}
'''

RESOLVER_RULES = '''def requirements(row, features):
    return [d for d in row.get("deps", []) if not d.get("feature") or d["feature"] in features]

def acyclic(edges):
    done, active = set(), set()
    def visit(n):
        if n in active: return False
        if n in done: return True
        active.add(n)
        if any(not visit(v) for v in edges.get(n, [])): return False
        active.remove(n); done.add(n)
        return True
    return all(visit(n) for n in edges)
'''
RESOLVER_ENGINE = '''import itertools
from rules import requirements, acyclic

def solve(data):
    packages = data["packages"]; names = sorted(packages)
    options = [[None] + sorted(rows, key=lambda r:r["version"]) for rows in (packages[n] for n in names)]
    best, best_key = None, None
    for choice in itertools.product(*options):
        chosen = {n:r for n,r in zip(names, choice) if r is not None}
        needed = dict(data["roots"]); pending = list(needed); seen = set(); edges = {}; ok = True
        while pending and ok:
            name = pending.pop()
            if name not in chosen: ok = False; break
            row = chosen[name]; low, high = needed[name]
            if not low <= row["version"] <= high: ok = False; break
            if name in seen: continue
            seen.add(name); deps = requirements(row, set(data.get("features", [])))
            edges[name] = [d["name"] for d in deps]
            for dep in deps:
                other = dep["name"]; old = needed.get(other, [-10**9, 10**9])
                needed[other] = [max(old[0], dep["min"]), min(old[1], dep["max"])]
                pending.append(other)
        if not ok or set(chosen) != seen: continue
        if any(r["version"] in data.get("blocked", {}).get(n, []) for n,r in chosen.items()): continue
        if any(n in data.get("pins", {}) and r["version"] != data["pins"][n] for n,r in chosen.items()): continue
        if not acyclic(edges): continue
        key = tuple(chosen[n]["version"] if n in chosen else -1 for n in names)
        if best_key is None or key > best_key:
            best_key = key; best = {n:r["version"] for n,r in chosen.items()}
    return {"error":"unsatisfiable"} if best is None else {"versions":best}
'''


def reference_ledger(data):
    """Independent evaluator formulation: filter, stable ordering, group reduction."""
    eligible = [(p, e) for p, e in enumerate(data["events"]) if e.get("sequence", 0) <= data.get("cutoff", 10**9)]
    groups = {}
    for p, e in eligible:
        groups.setdefault(e.get("id", f"anonymous:{p}"), []).append((p, e))
    result = dict(data.get("opening", {}))
    for events in groups.values():
        _, e = max(events, key=lambda pair: (pair[1].get("revision", 0), pair[0]))
        if e.get("void", False):
            continue
        divisor = 10000
        numerator = e["price"] * e.get("quantity", 1) * (10000 - max(0, min(10000, e.get("discount_bp", 0))))
        q, remainder = divmod(numerator, divisor)
        net = q + int(data["rounding"] == "half_up" and 2 * remainder >= divisor)
        q, remainder = divmod(net * e.get("tax_bp", 0), divisor)
        gross = net + q + int(data["rounding"] == "half_up" and 2 * remainder >= divisor)
        key = e.get("account", "default") + "|" + e.get("currency", "USD")
        result[key] = result.get(key, 0) + (-gross if e.get("kind") == "refund" else gross)
    return {"balances": result}


def reference_resolver(data):
    """Independent exhaustive constraint formulation (no reference-program import)."""
    names = sorted(data["packages"])
    rows = {n: {r["version"]: r for r in data["packages"][n]} for n in names}
    accepted = []
    for values in itertools.product(*[[-1] + sorted(rows[n]) for n in names]):
        chosen = {n: v for n, v in zip(names, values) if v != -1}
        if any(n not in chosen or not lo <= chosen[n] <= hi for n, (lo, hi) in data["roots"].items()):
            continue
        if any(v in data.get("blocked", {}).get(n, []) or (n in data.get("pins", {}) and data["pins"][n] != v) for n, v in chosen.items()):
            continue
        edges = {}
        ok = True
        for n, v in chosen.items():
            deps = [d for d in rows[n][v].get("deps", []) if not d.get("feature") or d["feature"] in data.get("features", [])]
            edges[n] = [d["name"] for d in deps]
            if any(d["name"] not in chosen or not d["min"] <= chosen[d["name"]] <= d["max"] for d in deps):
                ok = False; break
        if not ok:
            continue
        reached = set(data["roots"])
        for _ in names:
            reached |= {v for n in reached for v in edges.get(n, [])}
        if reached != set(chosen):
            continue
        remaining = set(chosen)
        while remaining:
            leaves = {n for n in remaining if not (set(edges[n]) & remaining)}
            if not leaves:
                break
            remaining -= leaves
        if not remaining:
            accepted.append((values, chosen))
    return {"versions": max(accepted)[1]} if accepted else {"error": "unsatisfiable"}


def ledger_case(rng, level, hard):
    events = [{"price": rng.randint(1, 999), "quantity": rng.randint(1, 5)} for _ in range(5 if hard else 2)]
    data = {"events": events, "rounding": "half_up" if hard else "floor"}
    if level >= 2: events[0]["kind"] = "refund"
    if level >= 3:
        for e in events: e["discount_bp"] = rng.choice([0, 1250, 3333, 5000, 12000])
    if level >= 4:
        for e in events: e["tax_bp"] = rng.choice([0, 825, 1750])
    if level >= 5:
        for i, e in enumerate(events): e.update(account=f"a{i % 2}", currency=["USD", "EUR"][i % 2])
    if level >= 6:
        events[0].update(id="repeat", revision=2)
        events.append({**events[0], "revision": 1, "price": 31})
        events.append({**events[0], "revision": 2, "price": 7})
    if level >= 7:
        data["cutoff"] = 4
        for i, e in enumerate(events): e["sequence"] = i
        # Excluded high revision must not suppress an earlier eligible revision.
        events.append({**events[0], "revision": 99, "sequence": 100})
    if level >= 8:
        events[1]["void"] = True
        data["opening"] = {"a0|USD": rng.randint(-50, 50), "reserve|JPY": 19}
    return data


def resolver_case(rng, level, hard):
    count = 5 if hard else 3
    names = [chr(97 + i) for i in range(count)]
    packages = {n: [{"version": v, "deps": []} for v in range(1, 4 if hard else 3)] for n in names}
    data = {"packages": packages, "roots": {names[0]: [1, 9]}}
    if level >= 2: data["roots"][names[0]] = [1, rng.choice([1, 2])]
    if level >= 3:
        for i, n in enumerate(names[:-1]):
            for r in packages[n]:
                r["deps"] = [{"name": names[i + 1], "min": 1, "max": rng.choice([1, 2])}]
    if level >= 4: data["roots"][names[-1]] = [rng.choice([1, 2]), 9]
    if level >= 5: data["blocked"] = {names[1]: [rng.choice([1, 2])]}
    if level >= 6: data["pins"] = {names[0]: rng.choice([1, 2])}
    if level >= 7:
        for r in packages[names[0]]: r["deps"][0]["feature"] = "extra"
        data["features"] = ["extra"] if rng.randrange(2) else []
    if level >= 8:
        packages[names[-1]][0]["deps"] = [{"name": names[0], "min": 1, "max": 9}]
    return data


LEDGER_SPEC = [
    "Input has events and rounding. Each nonnegative integer price is multiplied by quantity (default 1). Return balances keyed account|currency; defaults default|USD. Include a key even if its total is zero.",
    "kind=refund negates the final amount; all other kinds are positive charges.",
    "Apply discount_bp clamped to [0,10000] to price*quantity; divide by 10000 and round using rounding: floor or half_up. All intermediate magnitudes are nonnegative.",
    "After discount rounding, tax_bp (default 0) is applied to that rounded net, independently rounded, and added before refund negation.",
    "Aggregate separately by account and currency. Never convert currencies.",
    "Events with the same id: greatest revision wins, last input position breaks revision ties. Missing ids are unique anonymous:<original_position>. Never assume chronological revision order.",
    "Filter sequence>cutoff BEFORE duplicate resolution. Missing sequence is 0; missing cutoff is 10**9.",
    "After duplicate resolution ignore void=true. Add opening balances (possibly negative), keeping opening-only and zero keys. Do not discard an earlier revision merely because a later out-of-cutoff revision exists.",
]
RESOLVER_SPEC = [
    "Input packages maps names to rows {version:int,deps:list}. roots maps names to inclusive [min,max]. Return {versions:{name:version}}. Select exactly the dependency closure of roots. Among feasible installations maximize the version vector in sorted ALL package-name order, using -1 for absent packages.",
    "Respect each root's inclusive version interval; versions need not be consecutive. If impossible return {error:unsatisfiable}.",
    "Every active dependency {name,min,max} of every selected version must also be installed within its inclusive range. Version choice may require backtracking.",
    "All roots and all constraints on a shared dependency must hold simultaneously. Do not greedily satisfy one root and overwrite another.",
    "blocked maps package names to forbidden versions. Absent entries forbid nothing.",
    "pins maps names to exact versions, binding only if that package is installed. A pin does not add a root.",
    "A dependency with a nonempty feature is active only if that feature is in features (default []). A dependency without a feature is always active.",
    "The selected active dependency graph must be acyclic, including no self cycle. Backtrack to an acyclic version choice when possible before reporting unsatisfiable.",
]


def build(family, rng, hard):
    if family == "ledger":
        specs, maker, oracle = LEDGER_SPEC, ledger_case, reference_ledger
        source = {"engine.py": LEDGER_ENGINE, "rules.py": LEDGER_RULES}
        buggy = {"engine.py": "from rules import amount\ndef solve(data):\n    return {'balances': {'default|USD': sum(amount(e, data['rounding']) for e in data['events'])}}\n",
                 "rules.py": "def amount(e, mode):\n    return e['price']\n"}
    else:
        specs, maker, oracle = RESOLVER_SPEC, resolver_case, reference_resolver
        source = {"engine.py": RESOLVER_ENGINE, "rules.py": RESOLVER_RULES}
        buggy = {"engine.py": "from rules import choose\ndef solve(data):\n    return {'versions': {n: choose(data['packages'][n]) for n in data['roots']}}\n",
                 "rules.py": "def choose(rows):\n    return min(r['version'] for r in rows)\n"}
    records = []
    for level, spec in enumerate(specs, 1):
        tests = []
        for j in range(2):
            data = maker(rng, level, hard)
            tests.append({"id": f"public-{level}-{j}", "input": data, "expected": oracle(data)})
        records.append({"id": f"requirement-{level}", "spec": spec, "tests": tests})
    reserved = []
    for i in range(24):
        data = maker(rng, 1 + i % 8, hard)
        reserved.append({"id": f"reserved-{i}", "input": data, "expected": oracle(data)})
    contract = {"instruction": "Repair this two-module Python 3.11 project. engine.solve(data) must implement ALL requirements revealed so far, including earlier stages. Return complete replacement contents for both allowlisted files. No third-party libraries, tools, network, or workspace access. A stage pass is provisional.",
                "files": list(FILES), "entrypoint": "engine.solve(data)",
                "candidate_format": "files=[{path:engine.py,text:...},{path:rules.py,text:...}]; values and order empty"}
    candidate = lambda files: {"values": [], "order": [], "files": [{"path": k, "text": v} for k, v in files.items()]}
    return contract, records, candidate(source), candidate(buggy), reserved


def batch_program(candidate):
    """Model source runs only inside the pinned DockerRunner, never on the host."""
    files = candidate["files"]
    if candidate["values"] or candidate["order"] or len(files) != 2 or {f["path"] for f in files} != set(FILES):
        raise ValueError("both allowlisted Python files required")
    if any(type(f["text"]) is not str for f in files) or sum(len(f["text"].encode("utf-8")) for f in files) > 32768:
        raise ValueError("invalid or oversized source")
    encoded = wire({f["path"]: f["text"] for f in files})
    return ("import json,pathlib,sys\n"
            f"files=json.loads({encoded!r})\n"
            "for name,source in files.items(): pathlib.Path('/scratch',name).write_text(source,encoding='utf-8')\n"
            "sys.path.insert(0,'/scratch')\nfrom engine import solve\n"
            "data=json.load(sys.stdin)\nprint(json.dumps([solve(x) for x in data],sort_keys=True))\n")


def run_tests(candidate, tests, runner):
    from ..rollback_pilot.grading import InfrastructureError
    try:
        program = batch_program(candidate)
    except (ValueError, KeyError, TypeError):
        return {"status": "invalid_candidate", "check": "files", "detail": "Both allowlisted files, at most 32768 UTF-8 source bytes, required."}
    outcome = runner.execute(program, wire([t["input"] for t in tests]), wall_seconds=10)
    if outcome.status not in {"completed", "syntax_error", "runtime_error", "timeout", "output_limit"}:
        raise InfrastructureError("coding runner unavailable")
    if outcome.status != "completed":
        return {"status": outcome.status, "check": "execution", "detail": outcome.stderr[:1024]}
    try:
        import json
        actual = json.loads(outcome.stdout)
    except (ValueError, TypeError):
        return {"status": "invalid_output", "check": "json", "detail": "JSON batch output required."}
    if not isinstance(actual, list) or len(actual) != len(tests):
        return {"status": "invalid_output", "check": "batch", "detail": "One output per input required."}
    for t, value in zip(tests, actual):
        # Compare canonical JSON, so bool does not silently equal the integer 1.
        if wire(value) != wire(t["expected"]):
            return {"status": "public_mismatch", "check": t["id"], "observed": value, "expected": t["expected"]}
    return {"status": "public_pass", "checks": len(tests)}
