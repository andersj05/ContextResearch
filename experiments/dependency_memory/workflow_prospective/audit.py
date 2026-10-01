"""Evaluator-side finite comparisons and development screen; no model clients."""
from copy import deepcopy
import argparse
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

from experiments.dependency_memory.workflow_eval.grader import expected_answer
from experiments.dependency_memory.workflow_eval_live.study import checked_memory as old_checked
from experiments.dependency_memory.workflow_intake.packet import load_episode
from experiments.dependency_memory.evidence_use.guard import receipt_answer
from . import actor
from .freeze import fingerprints
from .oracle import ARTIFACTS, CHECKS, specification
from .runtime import execute, schedule

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results/workflow_method_2026-10-01"
SCOPES = [list(s) for n in range(1, 4) for s in combinations(CHECKS, n)]
TREES = ("a" * 40, "b" * 40, "c" * 40)
INVENTORIES = ({p: "a" * 64 for p in ARTIFACTS}, {p: "b" * 64 for p in ARTIFACTS}, {},
               {ARTIFACTS[0]: "a" * 64, ARTIFACTS[1]: "b" * 64})


def histories(max_length):
    alphabet = tuple(product(TREES[:2], CHECKS, (0, 1)))
    for length in range(max_length + 1):
        for events in product(alphabet, repeat=length):
            yield [{"check": check, "snapshot": tree, "run_id": hashlib.sha256(f"constructed-event:{i}:{tree}:{check}:{code}".encode()).hexdigest(),
                    "returncode": code, "artifacts": {p: tree[0] * 64 for p in ARTIFACTS} if check == "paper" and code == 0 else {}}
                   for i, (tree, check, code) in enumerate(events)]


def state(memory):
    records = actor.strict_json(memory) if memory else []
    return {(r["snapshot"], r["check"]): r for r in records}


def proposals(records):
    exact = actor.project(records)
    changed = deepcopy(exact)
    if changed:
        changed[0]["returncode"] = 1 - changed[0]["returncode"]
        changed[0]["artifacts"] = {}
    return [actor.wire(exact).decode(), actor.wire(list(reversed(exact))).decode(),
            " \n" + actor.wire(exact).decode() + " \n", actor.wire(exact[:-1]).decode(),
            actor.wire(changed).decode(), actor.wire(exact + exact[:1]).decode()]


def finite_audit():
    grader_checks = projection_checks = proposal_checks = chain_checks = 0
    for records in histories(3):
        projected = actor.project(records)
        for tree, scope, inventory in product(TREES, SCOPES, INVENTORIES):
            task = {"snapshot": tree, "required_checks": scope, "artifacts": inventory}
            answer = specification(records, task)
            if expected_answer(records, task) != answer:
                raise AssertionError("Primary grader/specification disagreement")
            grader_checks += 1
            if specification(projected, task) != answer:
                raise AssertionError("Projection lost required receipt state")
            projection_checks += 1
        split = len(records) // 2
        initial, between = records[:split], records[split:]
        for parent_cap, child_cap in ((4096, 1536), (202, 203), (0, 1536), (4096, 0)):
            direct_parent, _ = actor.direct_memory(initial, parent_cap)
            proposed = actor.wire(list(reversed(actor.project(initial)))).decode()
            checked_parent, _ = old_checked({"memory": proposed}, initial, parent_cap)
            if state(direct_parent) != state(checked_parent):
                raise AssertionError("Parent states differ")
            direct_available = (actor.strict_json(direct_parent) if direct_parent else []) + between
            checked_available = (actor.strict_json(checked_parent) if checked_parent else []) + between
            for scope in SCOPES:
                direct_child, _ = actor.direct_memory(direct_available, child_cap, scope)
                scoped = [r for r in checked_available if r["check"] in scope]
                # A deliberately omitted proposal exercises conditional fallback.
                proposed = actor.wire(actor.project(scoped)[:-1]).decode()
                checked_child, _ = old_checked({"memory": proposed}, scoped, child_cap)
                if state(direct_child) != state(checked_child):
                    raise AssertionError("Bounded child states differ")
                chain_checks += 1
    for records in histories(2):
        for cap, proposed in product((0, 1, 2, 203, 1536, 4096), proposals(records)):
            direct, _ = actor.direct_memory(records, cap)
            checked, _ = old_checked({"memory": proposed}, records, cap)
            canonical, _ = actor.checked_shadow({"memory": proposed}, records, cap)
            if state(direct) != state(checked) or canonical != direct:
                raise AssertionError("Writer proposal changed the declared receipt state")
            proposal_checks += 1
    return {"constructed_histories": 1885, "grader_query_comparisons": grader_checks,
            "projection_query_comparisons": projection_checks, "writer_proposal_comparisons": proposal_checks,
            "two_boundary_state_comparisons": chain_checks, "disagreements": 0,
            "evidence": "finite constructed checks, not independent tasks; local audit, external review pending"}


class FixtureClient:
    """Scripted interface control, including JSON memory for the prose slot."""
    mode = "offline_fixture"

    def complete(self, identity, request):
        view = request["observation"]
        if request["stage"] == "execute":
            answer = receipt_answer(view["memory"], view["final_public_state"])
            answer["evidence"] = {c: answer["evidence"].get(c) for c in CHECKS}
            return actor.wire(answer).decode()
        available = view["tool_observations"] if request["stage"] == "parent" else actor.strict_json(view["previous_memory"]) + view["new_observations"]
        return actor.wire({"memory": actor.wire(actor.project(available, view.get("scope", CHECKS))).decode()}).decode()


def screen(episode):
    full = specification(episode["initial"] + episode["between"], episode["task"])
    refreshed = specification(episode["between"], episode["task"])
    parent, p = actor.direct_memory(episode["initial"], actor.PARENT_CAP)
    child, c = actor.direct_memory((actor.strict_json(parent) if parent else []) + episode["between"], actor.CHILD_CAP, episode["scope"])
    full_request = actor.final_request(actor.wire(episode["initial"] + episode["between"]).decode(), episode)
    trace = execute(episode, FixtureClient())
    if trace["status"] != "complete" or [s["identity"] for s in trace["slots"]] != schedule(episode["id"]):
        raise AssertionError("Fixture runtime did not complete its fixed schedule")
    if any(specification(episode["initial"] + episode["between"], episode["task"]) != r["response"] for r in trace["finals"].values()):
        raise AssertionError("Scripted interface control differs from separate specification")
    return {"episode": episode["id"], "evidence_class": "inspected_development", "source_commits": episode["source_commits"],
        "actual_primary_answer": full, "between_only_answer": refreshed, "parent_needed_for_actual_query": full != refreshed,
        "direct_parent_bytes": p["proposal_bytes"], "direct_child_bytes": c["proposal_bytes"],
        "direct_parent_fits": not p["infeasible"], "direct_child_fits": not c["infeasible"],
        "direct_retained_readout": receipt_answer(child, episode["task"]),
        "logical_full_request_bytes": len(actor.request_bytes(full_request)),
        "previous_100000_byte_envelope_would_fit": len(actor.request_bytes(full_request)) <= 100000,
        "fixture_completions": trace["simulated_or_replayed_completions"], "provider_generations": 0,
        "fixture_guard_verdicts": {arm: r["guard"]["status"] for arm, r in trace["finals"].items()},
        "limits": ["One inspected actual task; no prospective or model outcome.",
                   "Full B refresh removes parent dependence for the actual query, not every possible constructed query.",
                   "The fixture prose slot returns a JSON table; this validates interfaces, not prose-model performance."]}


def analyze():
    episode = load_episode(HERE.parent / "workflow_intake/development/E0001")
    return {"version": "workflow_method_audit_v1", "date": "2026-10-01", "source_sha256": fingerprints(),
            "finite": finite_audit(), "development_screen": screen(episode), "prospective_evaluation_episodes": 0,
            "provider_generations": 0, "external_grader_review": "pending", "live_launch_ready": False}


def report(result):
    f, s = result["finite"], result["development_screen"]
    return ("# Local workflow method audit\n\nOctober 1, 2026. Offline finite checks and one inspected development screen; zero provider generations.\n\n"
            f"- Independent grader query comparisons: {f['grader_query_comparisons']}.\n"
            f"- Direct projection query comparisons: {f['projection_query_comparisons']}.\n"
            f"- Old checked-writer proposal comparisons: {f['writer_proposal_comparisons']}.\n"
            f"- Two-boundary checked/direct state comparisons: {f['two_boundary_state_comparisons']}.\n"
            f"- Disagreements: {f['disagreements']}. These are constructed checks, not task trials.\n\n"
            "The exact-table checker with fallback preserves the same receipt map as direct retention in this declared family. "
            "Old accepted JSON may differ in presentation; semantic equality does not prove equality of stochastic model answers. "
            "The new shadow canonicalizes both states and is excluded as a paid arm.\n\n"
            f"Development episode {s['episode']}: parent needed for actual final query = {s['parent_needed_for_actual_query']}; "
            f"direct memory = {s['direct_parent_bytes']}/{s['direct_child_bytes']} bytes. "
            f"The full logical request is {s['logical_full_request_bytes']} bytes; the old 100,000-byte envelope fits = {s['previous_100000_byte_envelope_would_fit']}.\n\n"
            "A scripted client completes six interface slots and all four final checks are consistent. This is not model or prose performance. "
            "No executed repair or total priced cost is measured. Prospective intake, external grader review and live transport remain unfinished.\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write:
        RESULTS.mkdir(exist_ok=True)
        (RESULTS / "analysis.json").write_bytes((json.dumps(result, indent=2, sort_keys=True) + "\n").encode())
        (RESULTS / "report.md").write_bytes(report(result).encode())
    print(json.dumps({"finite": result["finite"], "development_screen": result["development_screen"]}, indent=2))


if __name__ == "__main__":
    main()
