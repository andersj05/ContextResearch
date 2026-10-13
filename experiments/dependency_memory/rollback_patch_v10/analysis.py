"""Inherited factorial summaries with an explicit capacity-interpretation gate."""
from ..rollback_patch_v9.analysis import analyze as inherited_analyze


def analyze(tasks, execution, accounting, manifest, *, simulated=False):
    result = inherited_analyze(tasks, execution, accounting, manifest, simulated=simulated)
    stops = [{"task_id": row["job"]["task_id"], "arm": row["job"]["arm"]}
             for row in execution["jobs"]
             if row["result"].get("disposition") == "context_capacity"
             or row["result"].get("reason") == "context_capacity"]
    result["capacity_interpretation_gate"] = {
        "passed": not stops and not execution.get("stopped", False), "capacity_stops": stops,
        "global_stop": execution.get("stopped", False),
        "scope": "Any capacity stop prevents interpreting a factorial difference as an isolated content effect; all frozen outcomes still remain reported, with no sample replacement or truncation."}
    result["limitations"].append("Components recur within each allocation; task bootstrap intervals do not account for all dependence between composite tasks.")
    return result
