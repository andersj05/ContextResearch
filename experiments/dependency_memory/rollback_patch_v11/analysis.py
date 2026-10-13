"""Exploratory finite-cohort summaries preserve the v10 capacity invalidation."""
from ..rollback_patch_v10.analysis import analyze as inherited_analyze


def analyze(tasks, execution, accounting, manifest, *, simulated=False):
    result = inherited_analyze(tasks, execution, accounting, manifest, simulated=simulated)
    result["design_status"] = "unplanned exploratory study informed by control-only calibration; not the original gated v10 allocation"
    return result
