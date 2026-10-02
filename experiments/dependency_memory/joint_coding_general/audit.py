"""Offline checks of preserved auxiliary exploration; not needed by the proof."""
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from experiments.dependency_memory.joint_coding_general import cover, discover

HERE = Path(__file__).resolve().parent
AUX = HERE / "auxiliary"
OUTPUT = HERE.parent / "results/joint_three_block_general_auxiliary_2026-10-01.json"


@lru_cache(None)
def direct_routes(index):
    """Prediction errors by binary strings, separately from the loss matrix."""
    table = cover.frontier.decode_table(index)
    routes = []
    for x in range(16):
        source = list(reversed(f"{x:04b}"))
        actions = []
        for a in range(16):
            action = list(reversed(f"{a:04b}"))
            errors = []
            for o, p in enumerate(table):
                endpoint = cover.frontier.PAIRS[p][int(action[o])]
                predictions = list(reversed(f"{endpoint:03b}"))
                for j, prediction in zip((j for j in range(4) if j != o), predictions):
                    errors.append(int(prediction != source[j]))
            actions.append(tuple(errors))
        routes.append(tuple(actions))
    return tuple(routes)


def grade_native(record):
    ids = record["codeword_ids"]
    if len(ids) != 64 or len(set(ids)) != 64 or any(type(i) is not int or not 0 <= i < 4096 for i in ids):
        raise ValueError("Invalid preserved native codebook")
    words = tuple((i % 16, (i // 16) % 16, i // 256) for i in ids)
    matrices = [cover.frontier.loss_matrix(cover.frontier.decode_table(i)) for i in record["decoder_indices"]]
    routes = [direct_routes(i) for i in record["decoder_indices"]]
    errors, parent = 0, []
    for i in range(4096):
        source = (i % 16, (i // 16) % 16, i // 256)
        m = min(range(64), key=lambda m: sum(loss[x][a] for loss, x, a in zip(matrices, source, words[m])))
        parent.append(m)
        # Every one of the 3*4*3 actual final query routes, including ties in
        # nearest assignment. The source is used only by this offline grader.
        errors += sum(sum(row[x][a]) for row, x, a in zip(routes, source, words[m]))
    if errors != record["errors"] or record["outcomes"] != 147456:
        raise ValueError("Preserved native book does not reproduce its error count")
    if len(record["greedy_steps"]) != 64 or record["greedy_steps"][-1][1] != record["initial_errors"]:
        raise ValueError("Native discovery trace has inconsistent greedy counts")
    progression = [r[1] for r in record["greedy_steps"]] + [r[2] for r in record["accepted_swaps"]]
    if any(b >= a for a, b in zip(progression, progression[1:])) or progression[-1] != errors:
        raise ValueError("Native discovery trace is not strictly improving")
    return {"decoder_indices": record["decoder_indices"], "errors": errors, "outcomes": 147456,
            "parent_assignment_sha256": hashlib.sha256(bytes(parent)).hexdigest(),
            "parent_states": 64, "strict_improvement_over_incumbent": errors < 40529}


@lru_cache(None)
def dual_constant(index, weights, t):
    loss = cover.frontier.loss_matrix(cover.frontier.decode_table(index))
    n, d = cover.frontier.dual_product(loss, weights, t)
    _, upper = cover.frontier.log2_bounds(n, d)
    return -upper / 16


def certificate():
    manifest = json.loads((AUX / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["source_sha256"].items():
        if hashlib.sha256((AUX / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Preserved auxiliary bytes changed: {name}")
    native = [grade_native(json.loads(p.read_text(encoding="utf-8"))) for p in sorted(AUX.glob("search_*.json"))]
    if len(native) != 8 or min(r["errors"] for r in native) != 41088:
        raise ValueError("Native auxiliary case count or minimum changed")
    inputs = json.loads((AUX / "dual_input.json").read_text(encoding="utf-8"))["cases"]
    by_key = {tuple(r["indices"]): r for r in inputs}
    records = json.loads((AUX / "dual_search.json").read_text(encoding="utf-8"))["records"]
    dual = []
    for row in records:
        t = Fraction(*row["t"])
        s_upper = -cover.frontier.log2_bounds(t.numerator, t.denominator)[0]
        constants = [dual_constant(i, tuple(w), t) for i, w in zip(row["indices"], row["weights"])]
        lower = 4096 * (sum(constants) - 6) / s_upper
        lower_integer = -(-lower.numerator // lower.denominator)
        previous = by_key[tuple(row["indices"])]
        rules = previous.get("rules", [previous["rule"]]*3)
        codes = [discover.target(i, r) for i, r in zip(row["indices"], rules)]
        checked_cover = cover.bound([cover.block(i, c) for i, c in zip(row["indices"], codes)])
        # The exploratory input keeps the oracle floor if its selected cover
        # is weaker. Preserve that original convention rather than relabel it.
        earlier_lower = max(checked_cover["integer_lower_errors"], checked_cover["oracle_errors"])
        if (lower_integer != row["dual_lower_errors"] or earlier_lower != row["cover_lower_errors"]
                or max(lower_integer, row["cover_lower_errors"]) != row["combined_lower"]):
            raise ValueError("Auxiliary rational dual or its earlier cover witness changed")
        dual.append({"decoder_indices": row["indices"], "dual_lower_errors": lower_integer,
                     "cover_lower_errors": row["cover_lower_errors"], "combined_lower_errors": row["combined_lower"]})
    if len(dual) != 12:
        raise ValueError("Auxiliary rational dual record count changed")
    files = [HERE / "audit.py", HERE / "test_cover.py", AUX / "manifest.json"]
    files += [AUX / name for name in manifest["source_sha256"]]
    files += [cover.HERE / "cover.py", cover.HERE / "discover.py",
              cover.HERE.parent / "joint_coding/decoder_frontier.py"]
    return {"version": "general_decoder_auxiliary_audit_v1", "date": "2026-10-01", "new_model_calls": 0,
            "native_books": native, "native_outcomes_checked": len(native)*147456,
            "minimum_native_errors": min(r["errors"] for r in native), "rational_dual_records": dual,
            "source_sha256": {p.relative_to(cover.ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            "limits": "Auxiliary post-hoc discovery only. Final cover proof uses no numerical optimizer or native code. Exact grading of these eight books does not certify a heuristic optimum or model gain."}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({"native_books": len(result["native_books"]), "native_outcomes_checked": result["native_outcomes_checked"],
                      "minimum_native_errors": result["minimum_native_errors"], "rational_duals": len(result["rational_dual_records"])}))


if __name__ == "__main__":
    main()
