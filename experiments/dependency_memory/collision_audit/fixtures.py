"""Constructed audit specifications, not model responses or sampled trials."""
from copy import deepcopy


def worlds(histories, retained, public):
    return [{"id": f"w{i}", "history": history,
             "retained": deepcopy(retained), "public": deepcopy(public)}
            for i, history in enumerate(histories)]


def task(name, accepted, trace):
    return {"name": name, "trace": trace,
            "accepted": {f"w{i}": values for i, values in enumerate(accepted)}}


def tool(name, cost, observations):
    return {"name": name, "cost": cost,
            "observations": {f"w{i}": value for i, value in enumerate(observations)}}


def compatibility():
    return {"name": "three_way_compatibility", "budget": 0,
            "worlds": worlds(["Checked platform: supports A and B.",
                               "Checked platform: supports B and C.",
                               "Checked platform: supports A and C."],
                              {"summary": "Compatibility checked; choose a supported build."},
                              {"phase": "awaiting build request"}),
            "tasks": [task("choose_build", [["A", "B"], ["B", "C"], ["A", "C"]],
                           ["User requests one supported build."])],
            "tools": [tool("inspect_platform_family", 1, ["AB", "not-AB", "not-AB"])]}


def rollback(archive=True, budget=2):
    result = {"name": "rollback_with_archive" if archive else "rollback_archive_expired",
              "budget": budget,
              "worlds": worlds(["Release v1 receipt = cedar. Replaced by shared v2.",
                                 "Release v1 receipt = birch. Replaced by shared v2."],
                                {"release": "v2", "receipt": "shared"},
                                {"workspace": "v2", "old_transcript": "deleted"}),
              "tasks": [task("current_release", [["shared"], ["shared"]],
                             ["User requests current release receipt."]),
                        task("original_release", [["cedar"], ["birch"]],
                             ["Current release accepted.", "Unrelated work completed.",
                              "User requests original release receipt for rollback."])],
              "tools": [tool("read_current_workspace", 1, ["shared", "shared"])]}
    if archive:
        result["tools"].append(tool("read_versioned_archive", 3, ["cedar", "birch"]))
    return result


def shards(budget=1):
    histories = [f"Directory showed shard {i // 2}; record value receipt-{i}." for i in range(8)]
    tools = [tool("read_directory", 1, [f"shard-{i // 2}" for i in range(8)])]
    for shard in range(4):
        tools.append(tool(f"read_shard_{shard}", 1,
                          [f"receipt-{i}" if i // 2 == shard else "absent" for i in range(8)]))
    return {"name": "adaptive_sharded_recovery", "budget": budget,
            "worlds": worlds(histories, {"summary": "Receipt is archived."},
                              {"directory": "available", "shards": 4}),
            "tasks": [task("submit_receipt", [[f"receipt-{i}"] for i in range(8)],
                           ["User requests the archived receipt."])], "tools": tools}


def binary_receipts(budget):
    return {"name": f"binary_receipt_budget_{budget}", "budget": budget,
            "worlds": worlds([f"Observed three-bit receipt {i:03b}." for i in range(8)],
                              {"summary": "Receipt observed."}, {"bits": 3}),
            "tasks": [task("submit_receipt", [[f"{i:03b}"] for i in range(8)],
                           ["Submit the original receipt."])],
            "tools": [tool(f"read_bit_{bit}", 1, [str((i >> bit) & 1) for i in range(8)])
                      for bit in range(3)]}


def diagnostic_specs():
    shared = compatibility()
    shared["name"] = "harmless_lost_detail"
    shared["tools"] = []
    for answers in shared["tasks"][0]["accepted"].values():
        answers.append("portable")
    public = rollback(False)
    public["name"] = "public_evidence_control"
    for i, world in enumerate(public["worlds"]):
        world["public"]["original_receipt"] = ["cedar", "birch"][i]
    rich = rollback(True, 3)
    rich["name"] = "affordable_archive_control"
    adaptive = shards(2)
    adaptive["name"] = "adaptive_recovery_budget_two"
    return [compatibility(), rollback(), rollback(False), shards(), shared, public,
            rich, adaptive] + [binary_receipts(b) for b in range(4)]
