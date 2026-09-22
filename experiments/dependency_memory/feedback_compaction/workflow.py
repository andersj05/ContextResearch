"""Adapt the existing receipt environment to finite compaction audits.

Eight explicitly constructed worlds, three two-job manifests and two possible
late targets per manifest. Parent schemas are fixed before manifest reveal.
All receipt values are in a PUBLIC two-value-per-key catalog. That catalog is
an information channel, not a claim about arbitrary secret receipt strings.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from functools import cached_property
from hashlib import sha256
from itertools import combinations, product

from ..artifact_workflow import Action, ArtifactEnvironment, Config, Fixture, Receipt
from ..collision_audit.engine import Problem, canonical


KEYS = ("job-0", "job-1", "job-2")


def token(key, revision, bit, salt):
    return sha256(f"{salt}/{key}/{revision}/{bit}".encode()).hexdigest()[:32]


def receipt(key, revision, bit, salt):
    return Receipt(key, revision, token(key, revision, bit, salt))


def receipt_json(value):
    return asdict(value)


@dataclass(frozen=True)
class Candidate:
    fields: tuple[str, ...]
    child: str = "priority"

    @property
    def name(self):
        return "+".join(self.fields) + "/" + self.child


@dataclass(frozen=True)
class Contract:
    parent_capacity: int = 2
    child_capacity: int = 2
    recovery: bool = False
    recovery_budget: int = 0
    recovery_price: int = 3
    early_target: bool = False
    salt: str = "feedback-development-v1"

    def __post_init__(self):
        for n in (self.parent_capacity, self.child_capacity, self.recovery_budget):
            if type(n) is not int or n < 0:
                raise ValueError("Capacities and recovery budget must be nonnegative integers")
        if self.parent_capacity > 3 or self.child_capacity > 2:
            raise ValueError("This diagnostic has three source records and at most two child records")
        if type(self.recovery_price) is not int or self.recovery_price <= 0:
            raise ValueError("Recovery price must be positive")


class Workflow:
    def __init__(self, contract=Contract()):
        self.contract = contract
        self.config = Config(jobs=3, candidate_count=2,
                             first_capacity=contract.parent_capacity,
                             second_capacity=contract.child_capacity,
                             probe_available=False, revise=True, delay=2,
                             recovery_available=contract.recovery,
                             recovery_cost=contract.recovery_price)

    @cached_property
    def routes(self):
        return tuple((pair, target) for pair in combinations(KEYS, 2) for target in pair)

    @cached_property
    def bits(self):
        return tuple(product((0, 1), repeat=3))

    @cached_property
    def candidates(self):
        return tuple(Candidate(fields) for size in range(self.contract.parent_capacity + 1)
                     for fields in combinations(KEYS, size))

    @property
    def initial(self):
        return Candidate(KEYS[:self.contract.parent_capacity])

    @property
    def critical_fields(self):
        # The lower manifest key is refreshed; only job-1 and job-2 can be the
        # unrefreshed higher key. This baseline knows the public workflow rule.
        return Candidate(KEYS[1:1 + self.contract.parent_capacity])

    def fixture(self, bits, pair, target):
        old = tuple(receipt(key, 1, bits[i], self.contract.salt) for i, key in enumerate(KEYS))
        # Deliberate finite correlation: new and old tokens share a binary world
        # coordinate, but have distinct values. This is NOT a random revision model.
        revised = receipt(pair[0], 2, bits[KEYS.index(pair[0])], self.contract.salt)
        return Fixture(old, pair, target, revised)

    def parent(self, observed_receipts, candidate):
        if candidate not in self.candidates and not (
                candidate.child == "coded" and len(candidate.fields) <= self.contract.parent_capacity
                and len(set(candidate.fields)) == len(candidate.fields)
                and set(candidate.fields) <= set(KEYS)):
            raise ValueError("Candidate is outside the declared representation family")
        selected = tuple(r for r in observed_receipts if r.key in candidate.fields)
        if len(selected) > self.contract.parent_capacity:
            raise AssertionError("Parent capacity exceeded")
        return selected

    def child(self, parent_memory, build_receipts, pair, candidate, visible_target=None):
        available = {r.key: r for r in parent_memory}
        available.update({r.key: r for r in build_receipts})
        if not self.contract.child_capacity:
            return ()
        if visible_target is not None:
            chosen = [available[visible_target]] if visible_target in available else []
        elif candidate.child == "coded" and all(k in available for k in pair):
            # Diagnostic of the identifier channel. Equal bits -> lower record;
            # unequal bits -> upper record. Its identity transmits an extra bit.
            values = [next(b for b in (0, 1) if receipt(k, available[k].revision, b,
                       self.contract.salt) == available[k]) for k in pair]
            chosen = [available[pair[0] if values[0] == values[1] else pair[1]]]
        else:
            # Prefer the unrefreshed higher receipt, then the refreshed lower.
            # This decision never sees the late target or evaluator world ID.
            chosen = [available[k] for k in reversed(pair) if k in available]
        return tuple(chosen[:self.contract.child_capacity])

    def checkpoint(self, candidate, bits, route):
        pair, target = route
        env = ArtifactEnvironment(self.config, self.fixture(bits, pair, target))
        collection = env.step(Action("collect_receipts"))
        parent_memory = self.parent(collection.receipts, candidate)
        env.step(Action("seal_receipts"))
        manifest = env.step(Action("read_manifest"))
        build = env.step(Action("process_build"))
        # early_target is an explicit treatment that moves the SAME public task
        # identity before boundary two. It is not part of the base environment.
        early = target if self.contract.early_target else None
        memory = self.child(parent_memory, build.receipts, manifest.candidates, candidate, early)
        env.step(Action("seal_build"))
        for _ in range(self.config.delay):
            env.step(Action("work"))
        requirement = env.step(Action("get_requirement"))
        public = {"candidates": list(manifest.candidates), "target": requirement.required_key,
                  "required_revision": requirement.required_revision, "phase": env.phase}
        history = {"collected": [receipt_json(r) for r in collection.receipts]}
        return env, history, parent_memory, memory, public

    def problem(self, candidate, route_index):
        route = self.routes[route_index]
        snapshots = [self.checkpoint(candidate, b, route) for b in self.bits]
        # Enumerate every possible valid receipt in this finite public catalog.
        # The environment's submit function requires exact Receipt equality, so
        # no other action payload can succeed. We grade every catalog entry by
        # executing submit on a restored copy; a failed attempt ends that copy.
        actions = tuple(receipt(k, v, b, self.contract.salt)
                        for k in KEYS for v in (1, 2) for b in (0, 1))
        accepted, observations, worlds = {}, {}, []
        for i, (env, history, _, memory, public) in enumerate(snapshots):
            wid = f"w{i}"
            accepted[wid] = [canonical(receipt_json(r)) for r in actions
                             if deepcopy(env).step(Action("submit", r)).success]
            worlds.append({"id": wid, "history": history,
                           "retained": [receipt_json(r) for r in memory], "public": public})
            if self.contract.recovery:
                recovered = deepcopy(env).step(Action("recover_receipt"))
                observations[wid] = [receipt_json(r) for r in recovered.receipts]
        tools = [{"name": "recover_receipt", "cost": self.contract.recovery_price,
                  "observations": observations}] if self.contract.recovery else []
        pair, target = route
        trace = ["seal receipts", f"manifest {pair}", "refresh lower key"]
        if self.contract.early_target:
            trace.append(f"auxiliary public announcement of target {target}")
        trace += ["seal build", "two work steps", f"require {target}"]
        return Problem({"name": f"{'-'.join(pair)}->{target}", "worlds": worlds,
                        "budget": self.contract.recovery_budget, "tools": tools,
                        "tasks": [{"name": "submit_required_receipt", "accepted": accepted,
                                   "trace": trace}]})

    def execution(self, candidate, coded_decode=False):
        rows = []
        for route_index, route in enumerate(self.routes):
            for world, bits in enumerate(self.bits):
                env, _, parent, memory, public = self.checkpoint(candidate, bits, route)
                matching = [r for r in memory if r.key == public["target"]
                            and r.revision == public["required_revision"]]
                retained_available = bool(matching)
                answer = matching[0] if matching else None
                used_recovery = 0
                if coded_decode and candidate.child == "coded" and memory:
                    r = memory[0]
                    bit = next(b for b in (0, 1) if receipt(r.key, r.revision, b,
                               self.contract.salt) == r)
                    low, high = route[0]
                    values = {low: bit, high: bit} if r.key == low else {low: 1 - bit, high: bit}
                    answer = receipt(public["target"], public["required_revision"],
                                     values[public["target"]], self.contract.salt)
                if answer is None and self.contract.recovery and (
                        self.contract.recovery_budget >= self.contract.recovery_price):
                    answer = env.step(Action("recover_receipt")).receipts[0]
                    used_recovery = self.contract.recovery_price
                outcome = env.step(Action("submit", answer))
                rows.append({"route": route_index, "world": world, "success": outcome.success,
                             "failure": outcome.error, "retained_available": retained_available,
                             "recovery_units": used_recovery, "environment_units": env.cost_units,
                             "parent_records": len(parent), "child_records": len(memory),
                             "parent_utf8_bytes": len(canonical([receipt_json(r) for r in parent]).encode()),
                             "child_utf8_bytes": len(canonical([receipt_json(r) for r in memory]).encode())})
        return rows
