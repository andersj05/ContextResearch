"""Authored two-file repair tasks with separate public and private evidence.

Four families exercise real executable patches. Every public requirement, base
file and example is present before the first attempt and retained thereafter.
Host functions below are trusted independent oracles; candidate and reference
source strings are executed only by the separately audited Docker runtime.
"""

from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import itertools
import json
import random
from textwrap import dedent


FAMILIES = ("revision_ledger", "dependency_resolver", "quota_intervals", "temporal_routes")
FILES = ("engine.py", "rules.py")
DEFAULT_SEED = 2026101391
PUBLIC_CASES = 6
PRIVATE_CASES = 18
FOCUS_CATEGORIES = ("requirements", "boundary_cases", "state_invariants", "ordering",
                    "algorithm", "rounding", "tie_breaking", "dependencies", "unresolved")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def candidate(files):
    if type(files) is list:
        return {"files": deepcopy(files)}
    return {"files": [{"path": path, "text": files[path]} for path in FILES]}


def initial_candidate(task):
    return candidate(task["base_files"])


def reference_candidate(task):
    """Evaluator-only accessor. Never include this value in an actor request."""
    return candidate(task["evaluator"]["reference_files"])


def public_task(task):
    """An allowlist projection, not removal of a few currently known secrets."""
    return deepcopy({key: task[key] for key in
                     ("task_id", "family", "contract", "base_files", "public_tests")})


def public_check(task, proposed, runtime):
    return runtime.check(proposed, task["public_tests"], public=True)


def terminal_check(task, proposed, runtime):
    # Recheck public and reserved inputs together so a later patch cannot earn a
    # terminal pass by regressing an earlier public requirement. Private detail
    # is never returned by this task API, even if a runtime adds diagnostic keys.
    result = runtime.check(proposed, task["public_tests"] + task["evaluator"]["reserved_tests"], public=False)
    return {"score": result["score"], "disposition": result["disposition"]}


LEDGER_RULES = '''
POLICY = __POLICY__

def rounded(numerator, denominator, mode):
    if mode == "half_up":
        return (numerator + denominator // 2) // denominator
    return numerator // denominator

def winner_key(event, position):
    if POLICY["revision_priority"] == "sequence_first":
        return (event.get("sequence", 0), event.get("revision", 0), position)
    return (event.get("revision", 0), position)

def amount(event, mode):
    raw = event["price"] * event.get("quantity", 1)
    discount = min(10000, max(0, event.get("discount_bp", 0)))
    net = rounded(raw * (10000 - discount), 10000, mode)
    base = net if POLICY["tax_base"] == "discounted" else raw
    tax = rounded(base * event.get("tax_bp", 0), 10000, mode)
    gross = net + tax
    return -gross if event.get("kind") == "refund" else gross
'''

LEDGER_ENGINE = '''
from rules import amount, winner_key

def solve(data):
    chosen = {}
    cutoff = data.get("cutoff", 10**9)
    for position, event in enumerate(data["events"]):
        if event.get("sequence", 0) > cutoff:
            continue
        event_id = event.get("id", "anonymous:" + str(position))
        key = winner_key(event, position)
        if event_id not in chosen or key > chosen[event_id][0]:
            chosen[event_id] = (key, event)
    balances = dict(data.get("opening", {}))
    for _, event in chosen.values():
        if event.get("void", False):
            continue
        account = event.get("account", "default")
        currency = event.get("currency", "USD")
        key = account + "|" + currency
        balances[key] = balances.get(key, 0) + amount(event, data["rounding"])
    return {"balances": balances}
'''

RESOLVER_RULES = '''
POLICY = __POLICY__

def active_dependencies(row, features):
    return [dependency for dependency in row.get("deps", [])
            if not dependency.get("feature") or dependency["feature"] in features]

def acyclic(edges):
    finished, active = set(), set()
    def visit(name):
        if name in active:
            return False
        if name in finished:
            return True
        active.add(name)
        if any(not visit(other) for other in edges.get(name, [])):
            return False
        active.remove(name)
        finished.add(name)
        return True
    return all(visit(name) for name in edges)
'''

RESOLVER_ENGINE = '''
import itertools
from rules import POLICY, active_dependencies, acyclic

def solve(data):
    packages = data["packages"]
    names = sorted(packages, reverse=POLICY["name_order"] == "descending")
    options = [[None] + sorted(packages[name], key=lambda row: row["version"]) for name in names]
    best, best_vector = None, None
    for values in itertools.product(*options):
        chosen = {name: row for name, row in zip(names, values) if row is not None}
        constraints = dict(data["roots"])
        pending = list(constraints)
        seen, edges, valid = set(), {}, True
        while pending and valid:
            name = pending.pop()
            if name not in chosen:
                valid = False
                break
            low, high = constraints[name]
            if not low <= chosen[name]["version"] <= high:
                valid = False
                break
            if name in seen:
                continue
            seen.add(name)
            dependencies = active_dependencies(chosen[name], set(data.get("features", [])))
            edges[name] = [dependency["name"] for dependency in dependencies]
            for dependency in dependencies:
                other = dependency["name"]
                old = constraints.get(other, [-10**9, 10**9])
                constraints[other] = [max(old[0], dependency["min"]), min(old[1], dependency["max"])]
                pending.append(other)
        if not valid or set(chosen) != seen:
            continue
        if any(row["version"] in data.get("blocked", {}).get(name, []) for name, row in chosen.items()):
            continue
        if any(name in data.get("pins", {}) and row["version"] != data["pins"][name]
               for name, row in chosen.items()):
            continue
        if not acyclic(edges):
            continue
        vector = tuple(chosen[name]["version"] if name in chosen else -1 for name in names)
        better = (best_vector is None or
                  (vector > best_vector if POLICY["preference"] == "maximum" else vector < best_vector))
        if better:
            best_vector = vector
            best = {name: row["version"] for name, row in chosen.items()}
    return {"error": "unsatisfiable"} if best is None else {"versions": best}
'''

RESOLVER_BASE = '''
from rules import POLICY, active_dependencies

def solve(data):
    chosen = {}
    pending = [(name, bounds[0], bounds[1]) for name, bounds in data["roots"].items()]
    seen = set()
    while pending:
        name, low, high = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        rows = [row for row in data["packages"].get(name, []) if low <= row["version"] <= high]
        rows = [row for row in rows if row["version"] not in data.get("blocked", {}).get(name, [])]
        if name in data.get("pins", {}):
            rows = [row for row in rows if row["version"] == data["pins"][name]]
        if not rows:
            return {"error": "unsatisfiable"}
        row = __CHOOSE__(rows, key=lambda item: item["version"])
        chosen[name] = row["version"]
        for dependency in active_dependencies(row, set(data.get("features", []))):
            pending.append((dependency["name"], dependency["min"], dependency["max"]))
    return {"versions": chosen}
'''

INTERVAL_RULES = '''
import heapq
from collections import Counter
POLICY = __POLICY__

def allowed(selected, data):
    ids = {job["id"] for job in selected}
    if not set(data.get("mandatory", [])).issubset(ids):
        return False
    counts = Counter(job["group"] for job in selected)
    for group, (low, high) in data.get("quotas", {}).items():
        if not low <= counts[group] <= high:
            return False
    active_ends = []
    for job in sorted(selected, key=lambda row: (row["start"], row["end"], row["id"])):
        while active_ends and active_ends[0] <= job["start"]:
            heapq.heappop(active_ends)
        heapq.heappush(active_ends, job["end"])
        if len(active_ends) > POLICY["capacity"]:
            return False
    return True
'''

INTERVAL_ENGINE = '''
import itertools
from rules import POLICY, allowed

def solve(data):
    options = [job for job in data["jobs"] if job["id"] not in data.get("blocked", [])]
    best_value, best_ids = None, None
    for selected in itertools.combinations(options, data["k"]):
        if not allowed(selected, data):
            continue
        value = sum(job["value"] for job in selected)
        ids = sorted(job["id"] for job in selected)
        tie_better = (best_ids is None or
                      (ids < best_ids if POLICY["tie"] == "smallest" else ids > best_ids))
        if best_value is None or value > best_value or (value == best_value and tie_better):
            best_value, best_ids = value, ids
    if best_value is None:
        return {"error": "impossible"}
    return {"selected": best_ids, "value": best_value}
'''

INTERVAL_BASE = '''
from rules import POLICY, allowed

def solve(data):
    chosen = []
    options = [job for job in data["jobs"] if job["id"] not in data.get("blocked", [])]
    options.sort(key=lambda row: (-row["value"], row["id"]), reverse=__REVERSE__)
    for job in options:
        if len(chosen) == data["k"]:
            break
        if job["value"] < 0:
            continue
        trial = chosen + [job]
        # Build a locally compatible choice, then check the final quotas.
        stripped = {"mandatory": [], "quotas": {}}
        if allowed(trial, stripped):
            chosen = trial
    if len(chosen) != data["k"] or not allowed(chosen, data):
        return {"error": "impossible"}
    return {"selected": sorted(job["id"] for job in chosen),
            "value": sum(job["value"] for job in chosen)}
'''

ROUTE_RULES = '''
POLICY = __POLICY__

def departures(edge, arrival, coupons_left):
    depart = max(arrival, edge["open"])
    if depart >= edge["close"]:
        return []
    choices = [(depart + edge["duration"], coupons_left)]
    if coupons_left:
        duration = max(POLICY["minimum_duration"], edge["duration"] - edge.get("discount", 0))
        choices.append((depart + duration, coupons_left - 1))
    return choices

def visit_mask(node, required):
    mask = 0
    for index, name in enumerate(required):
        if node == name:
            mask |= 1 << index
    return mask
'''

ROUTE_ENGINE = '''
import heapq
from rules import POLICY, departures, visit_mask

def solve(data):
    required = data.get("required", [])
    full = (1 << len(required)) - 1
    graph = [[] for _ in range(data["n"])]
    for edge in data["edges"]:
        graph[edge["u"]].append(edge)
    mask = visit_mask(data["source"], required)
    initial = (data["source"], mask, data["coupons"])
    distance = {initial: data["start"]}
    queue = [(data["start"],) + initial]
    while queue:
        arrival, node, mask, remaining = heapq.heappop(queue)
        if distance.get((node, mask, remaining)) != arrival:
            continue
        if node == data["target"] and mask == full:
            if POLICY["coupon_rule"] == "at_most" or remaining == 0:
                return {"arrival": arrival}
        for edge in graph[node]:
            for next_time, next_remaining in departures(edge, arrival, remaining):
                if next_time > data["deadline"]:
                    continue
                state = (edge["v"], mask | visit_mask(edge["v"], required), next_remaining)
                if next_time < distance.get(state, float("inf")):
                    distance[state] = next_time
                    heapq.heappush(queue, (next_time,) + state)
    return {"arrival": None}
'''

ROUTE_BASE = '''
import heapq
from rules import POLICY, departures, visit_mask

def solve(data):
    required = data.get("required", [])
    full = (1 << len(required)) - 1
    graph = [[] for _ in range(data["n"])]
    for edge in data["edges"]:
        graph[edge["u"]].append(edge)
    distance = {data["source"]: data["start"]}
    queue = [(data["start"], data["source"], 0, data["coupons"])]
    while queue:
        arrival, node, mask, remaining = heapq.heappop(queue)
        if distance.get(node) != arrival:
            continue
        if node == data["target"] and mask == full:
            return {"arrival": arrival}
        for edge in graph[node]:
            for next_time, next_remaining in departures(edge, arrival, remaining):
                if next_time __DEADLINE__ data["deadline"]:
                    continue
                if next_time < distance.get(edge["v"], float("inf")):
                    distance[edge["v"]] = next_time
                    heapq.heappush(queue, (next_time, edge["v"],
                                          mask | visit_mask(edge["v"], required), next_remaining))
    return {"arrival": None}
'''


def _source(text, policy):
    return dedent(text).strip().replace("__POLICY__", repr(policy)) + "\n"


def _policy(family, replicate):
    # Project semantics vary independently of the random example values and
    # bug variants. Every policy field is in the complete public contract.
    index = replicate - 1
    if family == "revision_ledger":
        return {"revision_priority": ("revision_first", "sequence_first")[index % 2],
                "tax_base": ("discounted", "original")[(index // 2) % 2]}
    if family == "dependency_resolver":
        return {"preference": ("maximum", "minimum")[index % 2],
                "name_order": ("ascending", "descending")[(index // 2) % 2]}
    if family == "quota_intervals":
        return {"capacity": 1 + index % 2, "tie": ("smallest", "largest")[(index // 2) % 2]}
    return {"coupon_rule": ("at_most", "exact")[index % 2],
            "minimum_duration": 1 + (index // 2) % 2}


def _programs(family, policy, variant):
    if family == "revision_ledger":
        reference = {"engine.py": _source(LEDGER_ENGINE, policy), "rules.py": _source(LEDGER_RULES, policy)}
        base = deepcopy(reference)
        base["engine.py"] = base["engine.py"].replace('if event.get("sequence", 0) > cutoff:',
                                                      'if event.get("sequence", 0) < 0:')
        base["engine.py"] = base["engine.py"].replace('balances = dict(data.get("opening", {}))', 'balances = {}')
        base["rules.py"] = base["rules.py"].replace('min(10000, max(0, event.get("discount_bp", 0)))',
                                                    'max(0, event.get("discount_bp", 0))')
        if variant % 2:
            base["rules.py"] = base["rules.py"].replace('return -gross if event.get("kind") == "refund" else gross',
                                                       'return gross')
        else:
            base["rules.py"] = base["rules.py"].replace('(numerator + denominator // 2) // denominator',
                                                       'numerator // denominator')
        if variant % 3:
            base["engine.py"] = base["engine.py"].replace('key > chosen[event_id][0]', 'key < chosen[event_id][0]')
        return reference, base
    if family == "dependency_resolver":
        reference = {"engine.py": _source(RESOLVER_ENGINE, policy), "rules.py": _source(RESOLVER_RULES, policy)}
        base = {"engine.py": _source(RESOLVER_BASE, policy).replace("__CHOOSE__", "max" if variant % 2 else "min"),
                "rules.py": reference["rules.py"]}
        if variant % 3:
            base["rules.py"] = base["rules.py"].replace('if not dependency.get("feature") or dependency["feature"] in features',
                                                       'if not dependency.get("feature")')
        return reference, base
    if family == "quota_intervals":
        reference = {"engine.py": _source(INTERVAL_ENGINE, policy), "rules.py": _source(INTERVAL_RULES, policy)}
        base = {"engine.py": _source(INTERVAL_BASE, policy).replace("__REVERSE__", repr(bool(variant % 2))),
                "rules.py": reference["rules.py"].replace('active_ends[0] <= job["start"]', 'active_ends[0] < job["start"]')}
        if variant % 3:
            base["rules.py"] = base["rules.py"].replace('counts[group]', 'counts.get(group, low)')
        return reference, base
    reference = {"engine.py": _source(ROUTE_ENGINE, policy), "rules.py": _source(ROUTE_RULES, policy)}
    base = {"engine.py": _source(ROUTE_BASE, policy).replace("__DEADLINE__", ">=" if variant % 2 else ">"),
            "rules.py": reference["rules.py"].replace('depart >= edge["close"]', 'depart > edge["close"]')}
    if variant % 3:
        base["rules.py"] = base["rules.py"].replace('max(POLICY["minimum_duration"], edge["duration"] - edge.get("discount", 0))',
                                                   'edge["duration"]')
    return reference, base


def _requirements(family, policy):
    if family == "revision_ledger":
        priority = ("greatest (revision, original input position)" if policy["revision_priority"] == "revision_first"
                    else "greatest (sequence, revision, original input position)")
        tax = "rounded discounted net" if policy["tax_base"] == "discounted" else "original price times quantity"
        return [
            "Input events is a list of records. Return {balances:{account|currency:integer}}. JSON object key order is irrelevant. Keep zero balances and opening-only keys.",
            "Filter events whose sequence exceeds cutoff BEFORE choosing revisions. Defaults: sequence=0, revision=0, cutoff=10**9. For each ID choose " + priority + ".",
            "Explicit IDs are strings starting tx-. A missing ID is unique anonymous:<original input position>. After revision selection, void=true removes the winning event; never restore an older revision.",
            "Compute raw=price*quantity, quantity default1. Clamp discount_bp to [0,10000] and round raw*(10000-discount_bp)/10000 to get net. rounding is floor or half_up (ties upward), independently at every rounding operation.",
            "Compute tax on the " + tax + ": round(base*tax_bp/10000), tax_bp default0. Add tax to net, then negate the total only for kind=refund. Other/missing kinds are charges.",
            "Aggregate by account (default default) and currency (default USD). Add opening balances, which may be negative. Do not convert currencies or drop zero keys.",
            "Bounds: at most24 events; nonnegative integer prices<=9999, quantity<=5, tax_bp<=2500, revision/sequence<=100; discount_bp may be negative or exceed10000. Names contain no |. All inputs are valid JSON within these bounds.",
        ]
    if family == "dependency_resolver":
        return [
            "packages maps names to distinct positive integer version rows {version,deps}; roots maps names to inclusive [min,max]. Return {versions:{name:version}}, or {error:unsatisfiable}.",
            "Select exactly the active dependency closure of the roots, without unused packages. Every active dependency {name,min,max} must be installed and satisfy its inclusive version interval, simultaneously with all roots and other dependencies.",
            "A dependency with no feature or empty feature is always active. A nonempty feature activates it only when present in input features (default []).",
            "blocked maps package names to forbidden versions, default{}. pins maps names to exact versions, default{}. A pin constrains an installed package but does NOT install it by itself.",
            "The selected active dependency graph must have no directed cycle, including self-loops. Search alternatives before declaring unsatisfiable; greedy highest/lowest choices can be infeasible.",
            "Among feasible installations, choose the lexicographically " + policy["preference"] + " version vector in " + policy["name_order"] + " sorted ALL-package-name order. Use -1 for an absent package, even if it is not a root. Return only installed packages.",
            "Bounds: 1..6 packages, 1..3 versions per package, at most3 dependencies per version. All referenced packages exist, names are ASCII strings, all versions/range endpoints are integers1..9. Roots may be empty. JSON object key order is irrelevant.",
        ]
    if family == "quota_intervals":
        return [
            "Input jobs have distinct string IDs and integer start,end,value plus string group. Choose exactly input k jobs. Maximize their total value; values may be negative. Return {selected:[IDs sorted ascending],value:integer} or {error:impossible}.",
            "Intervals are half-open [start,end), so touching endpoints do not overlap. At every time at most " + str(policy["capacity"]) + " chosen intervals may overlap. Duplicated intervals with different IDs are separate choices.",
            "blocked (default[]) prohibits IDs. Every mandatory ID (default[]) must be selected; a mandatory blocked ID therefore makes the request impossible.",
            "quotas (default{}) maps groups to inclusive [minimum,maximum] counts among chosen jobs. Groups absent from quotas have bounds[0,k]. A mentioned group with no jobs still has count0.",
            "If multiple feasible subsets have the same maximum value, choose the lexicographically " + policy["tie"] + " ascending-sorted list of selected IDs. Output IDs remain ascending even when choosing the largest tie.",
            "k=0 is allowed and obeys mandatory/quota constraints. Bounds: 0..14 jobs, 0<=k<=14, 0<=start<end<=30, |value|<=100, group names ASCII. Quota bounds are integers0..14 with min<=max. All mentioned blocked/mandatory IDs exist.",
        ]
    return [
        "Find the earliest arrival at target from source in a directed graph. Input gives n, edges, source,target,start,deadline,coupons,required. Return {arrival:integer} or {arrival:null} if impossible by the inclusive deadline.",
        "Every edge has u,v,duration,open,close and optional discount(default0). A traversal may depart at any INTEGER time t with open<=t<close. Waiting at any node is allowed; traversals and visits may repeat. Edge closure limits departure, not arrival.",
        "Traversing without a coupon takes duration. At most one coupon may be spent per traversal; then duration is max(" + str(policy["minimum_duration"]) + ", duration-discount). A coupon may be spent even when it gives no improvement.",
        "The route must use " + ("exactly" if policy["coupon_rule"] == "exact" else "at most") + " the input coupons number. Remaining coupon budget and visited requirements are parts of the search state, not properties of the node alone.",
        "Visit every node in required (default[]) at least once in any order. The initial source visit counts. Reaching target before meeting these conditions does not end the search; a valid route may leave and return to target.",
        "Bounds: 1..8 nodes numbered0..n-1, <=24 directed edges, positive duration2..9, discount0..9, 0<=start<=deadline<=70, 0<=open<close<=70, coupons0..2, required has at most3 distinct nodes. Paths must arrive no later than deadline. Inputs are valid.",
    ]


def oracle_ledger(data, policy):
    """Group-and-reduce evaluator; reference program uses streaming selection."""
    groups = defaultdict(list)
    for position, event in enumerate(data["events"]):
        if event.get("sequence", 0) <= data.get("cutoff", 10**9):
            groups[event.get("id", "anonymous:" + str(position))].append((position, event))
    result = deepcopy(data.get("opening", {}))
    def round_ratio(numerator):
        quotient, remainder = divmod(numerator, 10000)
        return quotient + int(data["rounding"] == "half_up" and remainder >= 5000)
    for members in groups.values():
        if policy["revision_priority"] == "sequence_first":
            key = lambda item: (item[1].get("sequence", 0), item[1].get("revision", 0), item[0])
        else:
            key = lambda item: (item[1].get("revision", 0), item[0])
        _, event = max(members, key=key)
        if event.get("void", False):
            continue
        raw = event["price"] * event.get("quantity", 1)
        discount = sorted((0, event.get("discount_bp", 0), 10000))[1]
        net = round_ratio(raw * (10000 - discount))
        tax_base = {"discounted": net, "original": raw}[policy["tax_base"]]
        amount = net + round_ratio(tax_base * event.get("tax_bp", 0))
        if event.get("kind") == "refund":
            amount = -amount
        account = event.get("account", "default") + "|" + event.get("currency", "USD")
        result[account] = result.get(account, 0) + amount
    return {"balances": result}


def oracle_resolver(data, policy):
    """Simultaneous assignments plus closure/elimination, not greedy traversal."""
    names = sorted(data["packages"], reverse=policy["name_order"] == "descending")
    lookup = {name: {row["version"]: row for row in data["packages"][name]} for name in names}
    accepted = []
    for vector in itertools.product(*[[-1] + sorted(lookup[name]) for name in names]):
        chosen = {name: version for name, version in zip(names, vector) if version != -1}
        if any(name not in chosen or not low <= chosen[name] <= high
               for name, (low, high) in data["roots"].items()):
            continue
        if any(version in data.get("blocked", {}).get(name, []) or
               (name in data.get("pins", {}) and data["pins"][name] != version)
               for name, version in chosen.items()):
            continue
        edges, valid = {}, True
        for name, version in chosen.items():
            dependencies = [dep for dep in lookup[name][version].get("deps", [])
                            if not dep.get("feature") or dep["feature"] in data.get("features", [])]
            if any(dep["name"] not in chosen or not dep["min"] <= chosen[dep["name"]] <= dep["max"]
                   for dep in dependencies):
                valid = False
                break
            edges[name] = {dep["name"] for dep in dependencies}
        if not valid:
            continue
        reached = set(data["roots"])
        while True:
            new = reached | {other for name in reached for other in edges[name]}
            if new == reached:
                break
            reached = new
        if reached != set(chosen):
            continue
        remaining = set(chosen)
        while remaining:
            leaves = {name for name in remaining if not (edges[name] & remaining)}
            if not leaves:
                break
            remaining -= leaves
        if not remaining:
            accepted.append((vector, chosen))
    if not accepted:
        return {"error": "unsatisfiable"}
    selection = (max if policy["preference"] == "maximum" else min)(accepted, key=lambda pair: pair[0])
    return {"versions": selection[1]}


def oracle_intervals(data, policy):
    """Enumerate bitsets and sweep signed endpoints; no greedy heap checker."""
    jobs, accepted = data["jobs"], []
    for mask in range(1 << len(jobs)):
        if mask.bit_count() != data["k"]:
            continue
        selected = [job for index, job in enumerate(jobs) if mask >> index & 1]
        ids = {job["id"] for job in selected}
        if ids & set(data.get("blocked", [])) or not set(data.get("mandatory", [])).issubset(ids):
            continue
        counts = Counter(job["group"] for job in selected)
        if any(not low <= counts[group] <= high for group, (low, high) in data.get("quotas", {}).items()):
            continue
        deltas = sorted([(job["start"], 1) for job in selected] + [(job["end"], -1) for job in selected])
        active, valid = 0, True
        for _, delta in deltas:
            active += delta
            if active > policy["capacity"]:
                valid = False
                break
        if valid:
            accepted.append((sum(job["value"] for job in selected), sorted(ids)))
    if not accepted:
        return {"error": "impossible"}
    highest = max(value for value, _ in accepted)
    tied = [ids for value, ids in accepted if value == highest]
    return {"selected": (min if policy["tie"] == "smallest" else max)(tied), "value": highest}


def oracle_routes(data, policy):
    """Exhaustive integer-time reachability, independent of earliest-state Dijkstra."""
    layers = [set() for _ in range(data["deadline"] + 1)]
    required = set(data.get("required", []))
    layers[data["start"]].add((data["source"], frozenset({data["source"]} & required), 0))
    for moment in range(data["start"], data["deadline"] + 1):
        for node, seen, used in layers[moment]:
            if node == data["target"] and set(seen) == required:
                if policy["coupon_rule"] == "at_most" or used == data["coupons"]:
                    return {"arrival": moment}
            if moment < data["deadline"]:
                layers[moment + 1].add((node, seen, used))
            for edge in data["edges"]:
                if edge["u"] != node or not edge["open"] <= moment < edge["close"]:
                    continue
                for spend in (0, 1):
                    if used + spend > data["coupons"]:
                        continue
                    duration = edge["duration"] if spend == 0 else max(policy["minimum_duration"], edge["duration"] - edge.get("discount", 0))
                    arrival = moment + duration
                    if arrival <= data["deadline"]:
                        layers[arrival].add((edge["v"], seen | ({edge["v"]} & required), used + spend))
    return {"arrival": None}


ORACLES = {"revision_ledger": oracle_ledger, "dependency_resolver": oracle_resolver,
           "quota_intervals": oracle_intervals, "temporal_routes": oracle_routes}


def _ledger_case(rng, index, private):
    data = {"rounding": rng.choice(("floor", "half_up")), "events": [], "cutoff": rng.randint(3, 8),
            "opening": {"reserve|JPY": rng.randint(-30, 30), "acct-0|USD": 0}}
    count = 10 if private else 6
    for position in range(count):
        event = {"price": rng.randint(1, 999), "quantity": rng.randint(1, 5),
                 "discount_bp": rng.choice((-200, 0, 1250, 3333, 5000, 10000, 12000)),
                 "tax_bp": rng.choice((0, 825, 1000, 1750)), "account": "acct-" + str(position % 2),
                 "currency": rng.choice(("USD", "EUR")), "revision": rng.randint(0, 4),
                 "sequence": rng.randint(0, 10)}
        if position % 4 != 0:
            event["id"] = "tx-" + str(position % 3)
        if position % 3 == 0:
            event["kind"] = "refund"
        if position % 7 == 6:
            event["void"] = True
        data["events"].append(event)
    # Every example remains a complete nontrivial input; fixed patterns cover
    # filter-before-revision, final tie position, tombstones and rounding ties.
    if index % 6 == 0:
        data["events"] += [{"id": "tx-special", "price": 3, "revision": 5, "sequence": 1},
                           {"id": "tx-special", "price": 99, "revision": 99, "sequence": 100}]
    elif index % 6 == 1:
        data["events"] += [{"id": "tx-special", "price": 11, "revision": 3, "sequence": 1},
                           {"id": "tx-special", "price": 13, "revision": 1, "sequence": 2}]
    elif index % 6 == 2:
        data["events"] += [{"id": "tx-special", "price": 17, "revision": 2, "sequence": 1},
                           {"id": "tx-special", "price": 19, "revision": 2, "sequence": 1, "void": True}]
    elif index % 6 == 3:
        data["rounding"] = "half_up"
        data["events"] += [{"price": 1, "discount_bp": 5000, "tax_bp": 500, "kind": "refund"},
                           {"price": 3, "discount_bp": 12000, "tax_bp": 1000}]
    elif index % 6 == 4:
        data["events"] += [{"id": "tx-special", "price": 7, "revision": 2},
                           {"id": "tx-special", "price": 9, "revision": 2}]
    return data


def _resolver_case(rng, index, private):
    count = (6 if index % 7 == 0 else 5) if private else 4
    names = ["pkg-" + letter for letter in rng.sample("abcdefghjkmnpqrstuvwxyz", count)]
    packages = {name: [{"version": version, "deps": []} for version in (1, 2, 3)] for name in names}
    data = {"packages": packages, "roots": {names[0]: [1, 3]}, "features": ["extra"] if index % 2 else []}
    # Acyclic alternatives plus occasional cycles/shared conflicting constraints.
    for i, name in enumerate(names[:-1]):
        for row in packages[name]:
            low = rng.randint(1, 2)
            dependency = {"name": names[i + 1], "min": low, "max": rng.randint(low, 3)}
            if rng.randrange(3) == 0:
                dependency["feature"] = "extra"
            row["deps"].append(dependency)
    if index % 6 == 0:
        packages[names[-1]][2]["deps"] = [{"name": names[0], "min": 1, "max": 3}]
        data["roots"][names[-1]] = [2, 3]
    elif index % 6 == 1:
        data["blocked"] = {names[1]: [3]}
        packages[names[0]][2]["deps"] = [{"name": names[1], "min": 3, "max": 3}]
    elif index % 6 == 2:
        data["roots"][names[-1]] = [rng.randint(1, 2), 2]
        data["pins"] = {names[1]: rng.randint(1, 3)}
    elif index % 6 == 3:
        for row in packages[names[0]]:
            row["deps"] = [{"name": names[1], "min": 1, "max": 3, "feature": "extra"}]
        data["features"] = []
        data["pins"] = {names[-1]: 3}
    elif index % 6 == 4:
        data["roots"] = {}
        data["pins"] = {names[-1]: 3}
    else:
        packages[names[0]][0]["deps"] = [{"name": names[0], "min": 1, "max": 1}]
        data["roots"][names[-1]] = [1, 3]
    return data


def _interval_case(rng, index, private):
    count = (14 if index % 8 == 0 else rng.randint(7, 10)) if private else 7
    jobs = []
    for i in range(count):
        start = rng.randint(0, 11)
        jobs.append({"id": "job-" + str(i).zfill(2), "start": start, "end": start + rng.randint(1, 6),
                     "value": rng.randint(-8, 15), "group": "g" + str(i % 3)})
    data = {"jobs": jobs, "k": rng.randint(2, min(5, count)),
            "quotas": {"g0": [1, 3], "g1": [0, 2]}}
    if index % 6 == 0:
        jobs[0].update(start=0, end=2, value=5)
        jobs[1].update(start=2, end=4, value=5)
        data["mandatory"] = [jobs[0]["id"], jobs[1]["id"]]
    elif index % 6 == 1:
        for i, job in enumerate(jobs):
            job.update(start=i, end=i + 1, value=-1 - i % 3)
        data["k"] = 3
    elif index % 6 == 2:
        jobs[0].update(start=0, end=1, value=20)
        jobs[3].update(start=0, end=1, value=20)
        data.update(k=1, quotas={"g0": [1, 1]})
    elif index % 6 == 3:
        data["blocked"] = [jobs[-1]["id"]]
        data["mandatory"] = [jobs[-1]["id"]]
    elif index % 6 == 4:
        data.update(k=0, quotas={"missing": [0, 0]})
    else:
        jobs[0].update(start=0, end=6, value=12)
        jobs[1].update(start=0, end=3, value=7)
        jobs[2].update(start=3, end=6, value=7)
        data["mandatory"] = [jobs[rng.randint(0, count - 1)]["id"]]
    rng.shuffle(data["jobs"])
    return data


def _edge(u, v, duration, opening=0, close=30, discount=0):
    return {"u": u, "v": v, "duration": duration, "open": opening, "close": close, "discount": discount}


def _route_case(rng, index, private):
    if not private:
        templates = [
            {"n": 4, "source": 0, "target": 3, "start": 0, "deadline": 12, "coupons": 1, "required": [2],
             "edges": [_edge(0, 3, 2), _edge(0, 1, 2), _edge(1, 2, 3, 5, 6, 2), _edge(2, 3, 3)]},
            {"n": 3, "source": 0, "target": 2, "start": 0, "deadline": 10, "coupons": 1, "required": [0],
             "edges": [_edge(0, 1, 4, 0, 1, 3), _edge(1, 2, 4, 0, 10, 2)]},
            {"n": 3, "source": 0, "target": 2, "start": 0, "deadline": 8, "coupons": 0, "required": [],
             "edges": [_edge(0, 1, 2), _edge(1, 2, 2, 0, 2)]},
            {"n": 3, "source": 0, "target": 2, "start": 0, "deadline": 4, "coupons": 1, "required": [1],
             "edges": [_edge(0, 1, 2, 0, 5, 0), _edge(1, 2, 2, 0, 5, 0)]},
            {"n": 4, "source": 0, "target": 3, "start": 0, "deadline": 14, "coupons": 2, "required": [2],
             "edges": [_edge(0, 1, 2, 0, 30, 2), _edge(1, 3, 2, 0, 30, 9), _edge(1, 2, 3), _edge(2, 1, 3)]},
            {"n": 3, "source": 0, "target": 0, "start": 0, "deadline": 9, "coupons": 1, "required": [1],
             "edges": [_edge(0, 1, 3, 0, 30, 1), _edge(1, 0, 3), _edge(0, 2, 2), _edge(2, 0, 2)]},
        ]
        data = deepcopy(templates[index % len(templates)])
        permutation = rng.sample(range(data["n"]), data["n"])
        offset = rng.randrange(4)
        for field in ("source", "target"):
            data[field] = permutation[data[field]]
        data["required"] = [permutation[node] for node in data["required"]]
        for field in ("start", "deadline"):
            data[field] += offset
        for edge in data["edges"]:
            edge["u"], edge["v"] = permutation[edge["u"]], permutation[edge["v"]]
            edge["open"] += offset
            edge["close"] += offset
        return data
    count = rng.randint(3, 6)
    data = {"n": count, "source": 0, "target": count - 1, "start": rng.randrange(3),
            "deadline": rng.randint(10, 28), "coupons": index % 3,
            "required": rng.sample(range(count), min(index % 4, count)), "edges": []}
    for node in range(count - 1):
        data["edges"].append(_edge(node, node + 1, rng.randint(2, 6), 0, 30, rng.randint(0, 6)))
    for _ in range(count + 2):
        opening = rng.randint(0, 15)
        data["edges"].append(_edge(rng.randrange(count), rng.randrange(count), rng.randint(2, 9),
                                   opening, opening + rng.randint(1, 10), rng.randint(0, 9)))
    if index % 7 == 0:
        data["target"] = 0
    return data


MAKERS = {"revision_ledger": _ledger_case, "dependency_resolver": _resolver_case,
          "quota_intervals": _interval_case, "temporal_routes": _route_case}


def _tests(family, policy, rng, private, forbidden=()):
    result, seen = [], set(forbidden)
    count = PRIVATE_CASES if private else PUBLIC_CASES
    for index in range(count):
        for attempt in range(1000):
            value = MAKERS[family](rng, index, private)
            fingerprint = sha(value)
            if fingerprint not in seen:
                break
        else:
            raise ValueError("case generator exhausted distinct inputs")
        seen.add(fingerprint)
        result.append({"id": ("private-" if private else "public-") + str(index + 1).zfill(2),
                       "input": value, "expected": ORACLES[family](value, policy)})
    return result


def generate(*, split="calibration", seed=DEFAULT_SEED, per_family=4):
    if split not in {"calibration", "study", "fixture"}:
        raise ValueError("calibration, study or fixture split required")
    if type(seed) is not int or type(per_family) is not int or not 1 <= per_family <= 64:
        raise ValueError("integer seed and one through64 instances per family required")
    if split == "calibration" and per_family > 4:
        raise ValueError("calibration is capped at sixteen tasks")
    result = []
    for family in FAMILIES:
        for replicate in range(1, per_family + 1):
            task_seed = int(sha(["rollback-patch-v9", split, seed, family, replicate])[:16], 16)
            rng = random.Random(task_seed)
            policy = _policy(family, replicate)
            variant = rng.randrange(12)
            references, base = _programs(family, policy, variant)
            public = _tests(family, policy, rng, False)
            reserved = _tests(family, policy, rng, True, {sha(test["input"]) for test in public})
            task_id = "v9-" + split + "-" + family + "-" + sha([seed, family, replicate, split])[:16]
            task = {
                "task_id": task_id, "family": family, "domain": "coding", "split": split,
                "replicate": replicate,
                "contract": {
                    "instruction": "Repair the supplied two-module Python3.11 project to implement every requirement. Return complete replacement contents for both files. The whole specification, original base files and every public example remain available on every attempt.",
                    "entrypoint": "engine.solve(case) -> JSON value", "files": list(FILES),
                    "candidate_format": {"files": [{"path": "engine.py", "text": "complete source"},
                                                     {"path": "rules.py", "text": "complete source"}]},
                    "source_limit_utf8_bytes": 32768,
                    "execution": "Python3.11 standard library only; no network, subprocess requirements, workspace access or third-party packages. Tests call solve repeatedly in one fresh isolated process per suite. Results must not depend on prior cases. Public and private suites use separate containers; all inputs in a suite are visible to candidate code, but expected outputs are never provided to it.",
                    "policy": policy, "requirements": _requirements(family, policy),
                    "lesson_focus_categories": list(FOCUS_CATEGORIES),
                    "public_feedback": "Public receipts refer only to listed public examples. Private terminal results are never fed back into an actor or lesson request.",
                },
                "base_files": candidate(base)["files"], "public_tests": public,
                "evaluator": {"reference_files": candidate(references)["files"], "reserved_tests": reserved,
                              "seed": task_seed, "bug_variant": variant,
                              "provenance": "Repository-authored v9 project-repair tasks. Fixed family semantics with seeded public/private inputs and explicit project policies; not an external benchmark or natural production repository. Study instances are disjoint by construction from calibration, within the same four authored families."},
            }
            task["sha256"] = sha(task)
            result.append(task)
    return sorted(result, key=lambda task: sha([seed, split, "order", task["task_id"]]))


def verify_tasks(tasks):
    """Offline structure and independent expected-value checks; no source execution."""
    identities = set()
    public_count = private_count = 0
    for task in tasks:
        if task["task_id"] in identities or task["family"] not in FAMILIES:
            raise ValueError("duplicate or unknown task")
        identities.add(task["task_id"])
        if task["sha256"] != sha({key: value for key, value in task.items() if key != "sha256"}):
            raise ValueError("task binding changed")
        if (len(task["base_files"]) != 2 or len(task["evaluator"]["reference_files"]) != 2
                or {row["path"] for row in task["base_files"]} != set(FILES)
                or {row["path"] for row in task["evaluator"]["reference_files"]} != set(FILES)):
            raise ValueError("two-file project required")
        if len(task["public_tests"]) != PUBLIC_CASES or len(task["evaluator"]["reserved_tests"]) != PRIVATE_CASES:
            raise ValueError("fixed test denominator changed")
        seen = set()
        for test in task["public_tests"] + task["evaluator"]["reserved_tests"]:
            fingerprint = sha(test["input"])
            if fingerprint in seen:
                raise ValueError("public/private cases overlap")
            seen.add(fingerprint)
            expected = ORACLES[task["family"]](test["input"], task["contract"]["policy"])
            if canonical(test["expected"]) != canonical(expected):
                raise ValueError("independent expected output differs")
        public_count += len(task["public_tests"])
        private_count += len(task["evaluator"]["reserved_tests"])
    return {"passed": True, "scope": "offline task structure and independent oracle values; Docker reference execution is a separate required gate",
            "tasks": len(tasks), "public_cases": public_count, "private_cases": private_count,
            "model_calls": 0, "candidate_code_executed_on_host": False}
