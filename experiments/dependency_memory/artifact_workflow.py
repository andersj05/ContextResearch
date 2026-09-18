"""Deterministic receipt/manifest environment with two forced memory boundaries.

Trusted, stateless scripted policies receive only PublicView. Evaluator fixtures,
snapshots, and logs are never arguments to a policy. This is an API information
contract, not a security sandbox for adversarial Python or an LLM experiment.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import json
import random


@dataclass(frozen=True)
class Config:
    jobs: int = 6
    candidate_count: int = 2
    first_capacity: int = 2
    second_capacity: int = 2
    probe_available: bool = True
    probe_cost: int = 1
    revise: bool = True
    delay: int = 3
    cost_budget: int = 100
    call_limit: int = 128
    recovery_available: bool = False
    recovery_cost: int = 1

    def __post_init__(self):
        numbers = (self.jobs, self.candidate_count, self.first_capacity,
                   self.second_capacity, self.probe_cost, self.delay,
                   self.cost_budget, self.call_limit, self.recovery_cost)
        if any(type(n) is not int for n in numbers):
            raise ValueError("Dimensions, capacities, and costs must be integers")
        if not (1 <= self.candidate_count <= self.jobs):
            raise ValueError("Candidate count must fit the positive job count")
        if min(self.first_capacity, self.second_capacity, self.delay, self.cost_budget) < 0:
            raise ValueError("Capacities, delay, and budget must be nonnegative")
        if self.probe_cost < 1 or self.call_limit < 1:
            raise ValueError("Probe cost and call limit must be positive")
        if self.recovery_cost < 0:
            raise ValueError("Recovery cost must be nonnegative")
        if any(type(v) is not bool for v in (self.probe_available, self.revise, self.recovery_available)):
            raise ValueError("Availability and revision flags must be booleans")


@dataclass(frozen=True)
class Receipt:
    key: str
    revision: int
    token: str


@dataclass(frozen=True)
class Fixture:
    """Evaluator-only values; no seed, manifest answer, or token goes to a policy here."""
    receipts: tuple[Receipt, ...]
    candidates: tuple[str, ...]
    target: str
    revision: Receipt | None


def make_fixture(seed: int, config: Config) -> Fixture:
    # Separate deterministic streams for routing and payloads. These are synthetic
    # fixtures, not information-theoretically random trials or secret RNG state.
    route = random.Random(seed)
    payload = random.Random(seed ^ 0x51A9E3)
    receipts = tuple(Receipt(f"job-{i}", 1, f"{payload.getrandbits(128):032x}")
                     for i in range(config.jobs))
    candidates = tuple(sorted(route.sample([r.key for r in receipts], config.candidate_count)))
    target = route.choice(candidates)
    revision = Receipt(candidates[0], 2, f"{payload.getrandbits(128):032x}") if config.revise else None
    return Fixture(receipts, candidates, target, revision)


@dataclass(frozen=True)
class Action:
    name: str
    receipt: Receipt | None = None


@dataclass(frozen=True)
class Observation:
    kind: str
    receipts: tuple[Receipt, ...] = ()
    candidates: tuple[str, ...] = ()
    required_key: str | None = None
    required_revision: int | None = None
    checkpoint: int | None = None
    completed_steps: int = 0
    success: bool | None = None
    error: str | None = None


class ArtifactEnvironment:
    """Tools mutate workflow state; only submit creates the terminal package."""
    def __init__(self, config: Config, fixture: Fixture):
        keys = [r.key for r in fixture.receipts]
        if len(keys) != config.jobs or len(set(keys)) != len(keys):
            raise ValueError("Fixture must have one receipt per distinct job")
        if (len(fixture.candidates) != config.candidate_count
                or len(set(fixture.candidates)) != len(fixture.candidates)
                or not set(fixture.candidates) <= set(keys)
                or fixture.target not in fixture.candidates):
            raise ValueError("Invalid fixture manifest")
        if any(r.revision != 1 or not r.token for r in fixture.receipts):
            raise ValueError("Initial receipts must have revision one and a nonempty token")
        if bool(fixture.revision) != config.revise:
            raise ValueError("Revision fixture and configuration disagree")
        if fixture.revision and (fixture.revision.key != fixture.candidates[0]
                                 or fixture.revision.revision != 2 or not fixture.revision.token):
            raise ValueError("The first candidate must carry revision two")
        self.config = config
        self._fixture = fixture
        self._current = {r.key: r for r in fixture.receipts}
        self.phase = "collect"
        self.probe_attempted = False
        self.recovery_attempted = False
        self.calls = 0
        self.cost_units = 0
        self.completed_steps = 0
        self.package = None
        self.verdict = None

    def _finish(self, error=None):
        self.phase = "terminal"
        self.verdict = {"success": error is None, "failure": error}
        return Observation("terminal", success=error is None, error=error)

    def step(self, action: Action) -> Observation:
        if self.phase == "terminal":
            raise ValueError("An episode has exactly one terminal result")
        self.calls += 1
        charge = self.config.probe_cost if action.name == "inspect_manifest" else 1
        if action.name == "recover_receipt":
            charge = self.config.recovery_cost
        if self.calls > self.config.call_limit:
            return self._finish("call_limit")
        if self.cost_units + charge > self.config.cost_budget:
            return self._finish("cost_budget")
        self.cost_units += charge
        if action.receipt is not None and action.name != "submit":
            return Observation("blocked", error="unexpected_payload")
        if self.phase == "collect" and action.name == "collect_receipts":
            self.phase = "before_first"
            return Observation("receipts", receipts=self._fixture.receipts)
        if self.phase == "before_first" and action.name == "inspect_manifest":
            if self.probe_attempted:
                return Observation("blocked", error="probe_already_attempted")
            self.probe_attempted = True
            if not self.config.probe_available:
                return Observation("blocked", error="probe_unavailable")
            return Observation("manifest", candidates=self._fixture.candidates)
        if self.phase == "before_first" and action.name == "seal_receipts":
            self.phase = "manifest"
            return Observation("checkpoint", checkpoint=1)
        if self.phase == "manifest" and action.name == "read_manifest":
            self.phase = "build"
            return Observation("manifest", candidates=self._fixture.candidates)
        if self.phase == "build" and action.name == "process_build":
            self.phase = "before_second"
            revision = self._fixture.revision
            if revision:
                self._current[revision.key] = revision
            return Observation("build", receipts=(revision,) if revision else ())
        if self.phase == "before_second" and action.name == "seal_build":
            self.phase = "work" if self.config.delay else "requirement"
            return Observation("checkpoint", checkpoint=2)
        if self.phase == "work" and action.name == "work":
            self.completed_steps += 1
            if self.completed_steps == self.config.delay:
                self.phase = "requirement"
            return Observation("progress", completed_steps=self.completed_steps)
        if self.phase == "requirement" and action.name == "get_requirement":
            self.phase = "submit"
            expected = self._current[self._fixture.target]
            return Observation("requirement", required_key=expected.key, required_revision=expected.revision)
        if self.phase == "submit" and action.name == "recover_receipt":
            if self.recovery_attempted:
                return Observation("blocked", error="recovery_already_attempted")
            self.recovery_attempted = True
            if not self.config.recovery_available:
                return Observation("blocked", error="recovery_unavailable")
            # Declared archive channel, restricted to the now-public requirement.
            return Observation("recovery", receipts=(self._current[self._fixture.target],))
        if self.phase == "submit" and action.name == "submit":
            self.package = action.receipt
            expected = self._current[self._fixture.target]
            if action.receipt is None:
                return self._finish("missing_receipt")
            if action.receipt.key != expected.key:
                return self._finish("wrong_artifact")
            if action.receipt.revision != expected.revision:
                return self._finish("stale_revision")
            if action.receipt.token != expected.token:
                return self._finish("wrong_receipt")
            return self._finish()
        return Observation("blocked", error="action_out_of_order")


@dataclass(frozen=True)
class PublicView:
    config: Config
    phase: str
    probe_attempted: bool
    memory: tuple[Receipt, ...]
    window: tuple[Observation, ...]


@dataclass(frozen=True)
class Policy:
    name: str
    probing: str = "never"
    retention: str = "manifest"
    probe_cost_ceiling: int = 2
    recovery: str = "never"
    first_keys: tuple[str, ...] = ()
    skip_refresh: bool = False

    def __post_init__(self):
        if self.probing not in ("never", "always", "budgeted"):
            raise ValueError("Unknown probe strategy")
        if self.retention not in ("recent", "manifest", "planned"):
            raise ValueError("Unknown retention strategy")
        if self.recovery not in ("never", "if_missing"):
            raise ValueError("Unknown recovery strategy")
        if len(set(self.first_keys)) != len(self.first_keys):
            raise ValueError("Planned keys must be distinct")


POLICIES = (
    Policy("recent_never", retention="recent"),
    Policy("structured_never"),
    Policy("structured_always", probing="always"),
    Policy("structured_budgeted", probing="budgeted"),
)


def visible_records(memory, window):
    """Revision-aware records reconstructed only from supplied observations."""
    records = {}
    for receipt in (*memory, *(r for event in window for r in event.receipts)):
        previous = records.get(receipt.key)
        if previous is None or receipt.revision >= previous.revision:
            records.pop(receipt.key, None)
            records[receipt.key] = receipt
    return tuple(records.values())


def compact(memory, window, capacity, policy):
    if capacity < 0:
        raise ValueError("Negative record capacity")
    records = visible_records(memory, window)
    manifests = [event.candidates for event in window if event.kind == "manifest"]
    if policy.retention in ("manifest", "planned") and manifests:
        records = tuple(r for r in records if r.key in manifests[-1])
    if policy.retention == "planned" and window and window[-1].checkpoint == 1:
        if manifests and policy.skip_refresh:
            records = tuple(r for r in records if r.key != manifests[-1][0])
        elif not manifests:
            records = tuple(r for r in records if r.key in policy.first_keys)
    return records[-capacity:] if capacity else ()


def choose_action(view: PublicView, policy: Policy) -> Action:
    if view.phase == "before_first":
        c = view.config
        probe = policy.probing == "always" or (policy.probing == "budgeted"
            and c.probe_available and c.candidate_count <= c.first_capacity < c.jobs
            and c.probe_cost <= policy.probe_cost_ceiling)
        return Action("inspect_manifest" if probe and not view.probe_attempted else "seal_receipts")
    if view.phase == "submit":
        requirement = next(event for event in reversed(view.window) if event.kind == "requirement")
        receipt = next((r for r in visible_records(view.memory, view.window)
                        if r.key == requirement.required_key
                        and r.revision == requirement.required_revision), None)
        attempted = any(event.kind == "recovery" or event.error in
                        ("recovery_unavailable", "recovery_already_attempted") for event in view.window)
        if (receipt is None and policy.recovery == "if_missing"
                and view.config.recovery_available and not attempted):
            return Action("recover_receipt")
        return Action("submit", receipt)
    return Action({"collect": "collect_receipts", "manifest": "read_manifest",
                   "build": "process_build", "before_second": "seal_build",
                   "work": "work", "requirement": "get_requirement"}[view.phase])


def memory_bytes(memory):
    return len(json.dumps([asdict(r) for r in memory], sort_keys=True,
                          separators=(",", ":")).encode("utf-8"))


@dataclass
class Checkpoint:
    """Evaluator-owned paired continuation, including environment AND context."""
    environment: ArtifactEnvironment
    memory: tuple[Receipt, ...]
    window: tuple[Observation, ...]
    trace: list[dict]
    compactions: list[dict]


@dataclass
class Episode:
    success: bool
    failure: str | None
    cost_units: int
    calls: int
    probe_attempted: bool
    recovery_attempted: bool
    compactions: list[dict]
    trace: list[dict]
    package: Receipt | None


def _apply_boundary(environment, memory, window, policy, compactions):
    if not window or window[-1].checkpoint not in (1, 2):
        raise ValueError("A continuation must start at a declared checkpoint")
    boundary = window[-1].checkpoint
    capacity = (environment.config.first_capacity if boundary == 1
                else environment.config.second_capacity)
    retained = compact(memory, window, capacity, policy)
    visible = visible_records(memory, window)
    if len(retained) > capacity or len({r.key for r in retained}) != len(retained):
        raise ValueError("Invalid retained record count")
    if any(r not in visible for r in retained):
        raise ValueError("Compactor invented a receipt or read an undeclared channel")
    # Round-trip precisely the state the next controller receives; no window/log.
    retained = tuple(Receipt(**row) for row in json.loads(json.dumps([asdict(r) for r in retained])))
    compactions.append({"boundary": boundary, "capacity_records": capacity,
                        "retained_records": len(retained), "serialized_bytes": memory_bytes(retained),
                        "retained_keys": [r.key for r in retained]})
    return retained, ()


def run_episode(config: Config, fixture: Fixture, policy: Policy, *,
                checkpoint: Checkpoint | None = None, stop_at_first_boundary=False):
    if checkpoint is None:
        environment = ArtifactEnvironment(config, fixture)
        memory, window, trace, compactions = (), (), [], []
    else:
        state = deepcopy(checkpoint)
        environment, memory, window = state.environment, state.memory, state.window
        if config != environment.config or fixture != environment._fixture:
            raise ValueError("Checkpoint and requested instance disagree")
        trace, compactions = state.trace, state.compactions
        memory, window = _apply_boundary(environment, memory, window, policy, compactions)
    while environment.phase != "terminal":
        view = PublicView(environment.config, environment.phase, environment.probe_attempted, memory, window)
        action = choose_action(view, policy)
        observation = environment.step(action)
        window += (observation,)
        trace.append({"action": asdict(action), "observation": asdict(observation),
                      "cumulative_cost_units": environment.cost_units})
        if observation.checkpoint:
            if stop_at_first_boundary:
                return Checkpoint(deepcopy(environment), memory, window, deepcopy(trace), deepcopy(compactions))
            memory, window = _apply_boundary(environment, memory, window, policy, compactions)
    return Episode(**environment.verdict, cost_units=environment.cost_units, calls=environment.calls,
                   probe_attempted=environment.probe_attempted, recovery_attempted=environment.recovery_attempted,
                   compactions=compactions,
                   trace=trace, package=environment.package)
