"""Staged fixture/replay runtime. No provider client, grader or label feedback."""
from copy import deepcopy
import hashlib
import random
from time import perf_counter_ns, process_time_ns

from experiments.dependency_memory.evidence_use.guard import check, receipt_answer, strict_json
from experiments.dependency_memory.workflow_intake.views import public_records
from . import actor


def order(episode_id):
    arms = list(actor.ARMS)
    random.Random(str(actor.SEED) + ":" + episode_id).shuffle(arms)
    return arms


def schedule(episode_id):
    return [episode_id + "-prose-parent", episode_id + "-prose-child"] + [episode_id + "-" + arm + "-final" for arm in order(episode_id)]


def public_case(case):
    result = {"id": case["id"], "initial": public_records(case["initial"]), "between": public_records(case["between"]),
              "scope": deepcopy(case["scope"]), "task": {k: deepcopy(case["task"][k])
                    for k in ("snapshot", "required_checks", "artifacts")}}
    if not isinstance(result["id"], str) or not result["id"] or result["scope"] != sorted(set(result["scope"])) or not result["scope"]:
        raise ValueError("Invalid task identity or scope")
    actor.validate_receipts(result["initial"] + result["between"])
    receipt_answer("[]", result["task"])
    if not set(result["task"]["required_checks"]) <= set(result["scope"]) <= set(actor.CHECKS):
        raise ValueError("Final required checks are outside the announced scope")
    return result


def execute(case, client):
    """Callbacks receive only public requests; the included modes make no generations."""
    if client.mode not in {"offline_fixture", "saved_response_replay"}:
        raise ValueError("This version has no live transport")
    case = public_case(case)
    slots = [{"identity": identity, "status": "not_dispatched", "dispatched": False} for identity in schedule(case["id"])]
    trace = {"version": actor.VERSION, "episode": case["id"], "mode": client.mode, "provider_generations": 0,
             "status": "running", "slots": slots, "memories": {}, "finals": {}, "local_events": [],
             "priced_total_cost": None}
    position = 0

    def measured(arm, name, inputs, operation):
        read_bytes = len(actor.wire(inputs))
        cpu, wall = process_time_ns(), perf_counter_ns()
        value = operation()
        trace["local_events"].append({"arm": arm, "name": name, "cpu_ns": process_time_ns() - cpu,
            "wall_ns": perf_counter_ns() - wall, "read_bytes": read_bytes, "write_bytes": len(actor.wire(value))})
        return value

    def call(request):
        nonlocal position
        slot = slots[position]
        raw = actor.request_bytes(request)
        slot.update(request=deepcopy(request), request_sha256=hashlib.sha256(raw).hexdigest(), request_bytes=len(raw))
        slot.update(dispatched=True, status="awaiting_response")
        position += 1
        text = client.complete(slot["identity"], deepcopy(request))
        if not isinstance(text, str):
            raise TypeError("Fixture/replay responses must retain their original JSON text")
        slot.update(status="completed", response_text=text)
        try:
            parsed = strict_json(text)
        except (ValueError, TypeError, RecursionError):
            parsed = None
        slot["response"] = parsed
        return parsed

    try:
        source = case["initial"]
        archive = measured("indexed", "build_declared_raw_archive", source,
                           lambda: {"records": deepcopy(source), "positions": {
                               c: [i for i, r in enumerate(source) if r["check"] == c] for c in actor.CHECKS}})
        storage_start = perf_counter_ns()
        initial_archive_bytes = len(actor.wire(archive))
        parent, parent_audit = measured("direct", "parent_projection", source,
                                     lambda: actor.direct_memory(source, actor.PARENT_CAP))
        trace["memories"]["direct_parent"] = {"memory": parent, "audit": parent_audit}
        response = call(actor.memory_request(case, "parent"))
        prose_parent, audit = measured("prose", "parent_admission", response,
                                       lambda: actor.admit_prose(response, actor.PARENT_CAP))
        trace["memories"]["prose_parent"] = {"memory": prose_parent, "audit": audit}
        update_time = perf_counter_ns()
        def update_archive():
            for row in case["between"]:
                archive["positions"][row["check"]].append(len(archive["records"]))
                archive["records"].append(deepcopy(row))
            return archive
        archive = measured("indexed", "append_new_observations", case["between"], update_archive)
        archive_bytes = len(actor.wire(archive))
        # Only the bounded direct parent and new observations feed its child.
        available = (strict_json(parent) if parent else []) + case["between"]
        direct, audit = measured("direct", "child_projection", available,
                                lambda: actor.direct_memory(available, actor.CHILD_CAP, case["scope"]))
        trace["memories"]["direct_child"] = {"memory": direct, "audit": audit}
        response = call(actor.memory_request(case, "child", prose_parent))
        prose, audit = measured("prose", "child_admission", response,
                               lambda: actor.admit_prose(response, actor.CHILD_CAP))
        trace["memories"]["prose_child"] = {"memory": prose, "audit": audit}
        for arm in order(case["id"]):
            if arm == "direct":
                memory = direct
            elif arm == "prose":
                memory = prose
            elif arm == "indexed":
                def retrieve():
                    positions = sorted(i for c in case["task"]["required_checks"] for i in archive["positions"][c])
                    return actor.wire([archive["records"][i] for i in positions]).decode()
                memory = measured(arm, "retrieve_requested_records", archive, retrieve)
            else:
                memory = measured(arm, "declared_full_history", source + case["between"],
                                  lambda: actor.wire(source + case["between"]).decode())
            request = actor.final_request(memory, case)
            response = call(request)
            normalized = actor.normalize(response)
            verdict = measured(arm, "common_final_consistency_check", [request, normalized], lambda: check(request, normalized))
            trace["finals"][arm] = {"identity": slots[position - 1]["identity"], "request": request,
                "response": normalized, "guard": verdict, "released": verdict["status"] == "consistent", "memory_bytes": len(memory.encode("utf-8"))}
        trace["archive_storage"] = {"serialized_bytes": archive_bytes,
            "byte_nanoseconds": initial_archive_bytes * (update_time - storage_start) + archive_bytes * (perf_counter_ns() - update_time),
            "scope": "declared archive residency across both fixture/replay boundaries and finals; Python heap overhead excluded"}
        trace["status"] = "complete"
    except Exception as error:
        # No exception message is persisted: arbitrary callbacks could include secrets.
        trace.update(status="stopped", error_type=type(error).__name__)
        if position and slots[position - 1]["status"] == "awaiting_response":
            slots[position - 1]["status"] = "missing_response"
        for slot in slots[position:]:
            slot["status"] = "not_dispatched_after_stop"
    trace["simulated_or_replayed_completions"] = sum(s["status"] == "completed" for s in slots)
    return trace
