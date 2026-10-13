"""Fixed denominators, control-only difficulty gates, and charged paired resources."""
from collections import Counter
from fractions import Fraction
from statistics import median
from .common import sha
from .statistics import paired, wilson
from ..rollback_development_v5.analysis import metering


def analyze(tasks, execution, accounting, manifest, *, simulated):
    rows = [{**row["job"], **row["result"]} for row in execution["jobs"]]
    known_calls = [c for c in accounting["calls"] if c["state"] == "completed"]
    controls = []
    for family, level in manifest["cells"]:
        ids = {t["task_id"] for t in tasks if (t["family"],t["difficulty"]) == (family,level)}
        cell = {"family":family,"level":level}
        for arm in manifest["arms"]:
            subset = [r for r in rows if r["task_id"] in ids and r["arm"] == arm]
            known = [r for r in subset if r["score"] is not None]
            events = [e for r in subset for e in r.get("events",[])]
            passed = sum(r["score"] for r in known)
            cell[arm] = {"scheduled":len(subset),"known":len(known),"passed":passed,
                         "success_rate":passed/len(known) if known else None,"wilson_95":wilson(passed,len(known)),
                         "success_bounds":[passed/len(subset),(passed+len(subset)-len(known))/len(subset)] if subset else None,
                         "episodes_with_public_mismatch":sum(any(e["status"] == "public_mismatch" for e in r.get("events",[])) for r in subset),
                         "candidate_actions":sum(e["status"] != "no_candidate" for e in events),
                         "progress_only_actions":sum(e["status"] == "no_candidate" for e in events),
                         "median_actions":median(r["actions_used"] for r in subset if "actions_used" in r) if any("actions_used" in r for r in subset) else None,
                         "median_history_bytes":median(e["input_history_bytes"] for e in events) if events else None,
                         "max_history_bytes":max((e["input_history_bytes"] for e in events),default=0),
                         "dispositions":dict(Counter(r["disposition"] for r in subset))}
        controls.append(cell)
    totals = {arm:metering([c for c in known_calls if c["identity"]["arm"] == arm]) for arm in manifest["arms"]}
    complete_ids = {t["task_id"] for t in tasks if all(any(r["task_id"]==t["task_id"] and r["arm"]==a and r["score"] is not None for r in rows) for a in ("K","R"))}
    resources = {arm:metering([c for c in known_calls if c["identity"]["arm"] == arm and c["identity"]["task_id"] in complete_ids]) for arm in ("K","R")}
    confirmation = not simulated and manifest["split"] == "confirmation" and not execution["stopped"]
    return {"evidence_kind":"offline_scripted_fixture" if simulated else "observed_subscription_generations",
            "manifest_sha256":sha(manifest),"split":manifest["split"],"tasks":len(tasks),"control_cells":controls,
            "primary":paired(rows,tasks,confirmatory=confirmation) if {"K","R"} <= set(manifest["arms"]) else None,
            "family_diagnostics":{f:paired(rows,[t for t in tasks if t["family"]==f]) for f in {t["family"] for t in tasks}} if "R" in manifest["arms"] else {},
            "arm_resources":totals,"complete_pair_resources":resources,"accounting":accounting,
            "limitations":["Authored task distribution; task-level test does not establish new-family generalization.",
                           "Different provider draws; server revision and sampling seed unavailable.",
                           "A smaller p-value cannot establish practical value, population equivalence, or deployed-harness gains.",
                           "Planning credits use the inherited declared accounting conversion, not current API prices or actual subscription charges."]}


def bounded_control_rate(cell, lower, upper, minimum_scheduled):
    """Require the rate gate for every binary completion, with >=7/8 observed."""
    n, known, passed = (cell[k] for k in ("scheduled", "known", "passed"))
    if any(type(v) is not int for v in (n, known, passed)):
        return False
    if n < minimum_scheduled or not 0 <= passed <= known <= n or n-known > n//8:
        return False
    return (Fraction(passed, n) >= Fraction(str(lower)) and
            Fraction(passed+n-known, n) <= Fraction(str(upper)))


def select_screen(report, manifest):
    if manifest["split"] != "screen" or report["evidence_kind"] != "observed_subscription_generations":
        raise ValueError("only live control screening can nominate cells")
    if set(manifest["arms"]) != {"K","F"}: raise ValueError("treatment-blind calibration required")
    selected = []
    robust = manifest.get("robust_control_missingness", False)
    capacity_limited = []
    for cell in report["control_cells"]:
        counts = {a:cell[a].get("dispositions",{}).get("context_capacity",0) for a in ("K","F")}
        if any(counts.values()):
            capacity_limited.append({"family":cell["family"],"level":cell["level"],"capacity_failures":counts})
    for family in sorted({c["family"] for c in report["control_cells"]}):
        candidates = []
        for cell in report["control_cells"]:
            if cell["family"] != family: continue
            k,f = cell["K"],cell["F"]
            # Capacity is an observed end-to-end failure, but cannot establish
            # that a question is difficult for the model under this design.
            if any(c.get("dispositions",{}).get("context_capacity",0) for c in (k,f)): continue
            fresh_upper = 1.0 if manifest.get("allow_fresh_ceiling",False) else .90
            if robust:
                if report.get("accounting", {}).get("stop", "absent") is not None: continue
                if not bounded_control_rate(k, .25, .85, 8) or not bounded_control_rate(f, .25, fresh_upper, 8): continue
            else:
                if k["known"] < 2 or f["known"] < 2 or k["known"] != k["scheduled"] or f["known"] != f["scheduled"]: continue
                if not .25 <= k["success_rate"] <= .85 or not .25 <= f["success_rate"] <= fresh_upper: continue
            if k["episodes_with_public_mismatch"] < 1: continue
            candidates.append(cell)
        if candidates:
            best = min(candidates,key=lambda c:(abs(c["K"]["success_rate"]-.575),c["level"]))
            selected.append([family,best["level"]])
    return {"selected_cells":selected,"ready_for_confirmation":False,"capacity_limited_cells":capacity_limited,
            "next":"independent validation" if selected else "no suitable cell; report ceiling/floor and freeze a new design",
            "stages":manifest["stages"],"actions":manifest["actions"],"used_seeds":[manifest["seed"]],
            "require_candidates":manifest.get("require_candidates",False),
            "allow_fresh_ceiling":manifest.get("allow_fresh_ceiling",False),
            "robust_control_missingness":robust,
            "ledger_profile":manifest.get("ledger_profile", "standard"),
            "screen_manifest_sha256":sha(manifest),"screen_analysis_sha256":sha(report),
            "rule":("one tier per family nearest known K rate 0.575; >=8 scheduled and >=7/8 observed per arm; every missing-score completion must satisfy K [0.25,0.85] and the frozen F bounds; K public mismatch, no capacity failures or global stop; ties choose lower tier"
                    if robust else
                    "one tier per family, nearest K rate 0.575; complete K in [0.25,0.85], F in [0.25,1], K public mismatch and no capacity failures; ties choose lower tier"
                    if manifest.get("allow_fresh_ceiling",False) else
                    "one tier per family, nearest K rate 0.575 among complete non-floor/non-ceiling K/F cells with no context-capacity failures; ties choose lower tier")}


def validate_selection(screen, report, manifest):
    if manifest["split"] != "validation" or report["evidence_kind"] != "observed_subscription_generations" or set(manifest["arms"]) != {"K","F"}:
        raise ValueError("live independent K/F validation required")
    if sorted(manifest["cells"]) != sorted(screen["selected_cells"]) or manifest["seed"] in screen["used_seeds"]:
        raise ValueError("validation must use exactly the nominated cells and a new seed")
    if (manifest["stages"],manifest["actions"]) != (screen["stages"],screen["actions"]): raise ValueError("validation design differs")
    if manifest.get("require_candidates",False) != screen.get("require_candidates",False): raise ValueError("validation response contract differs")
    if manifest.get("allow_fresh_ceiling",False) != screen.get("allow_fresh_ceiling",False): raise ValueError("validation calibration rule differs")
    if manifest.get("robust_control_missingness",False) != screen.get("robust_control_missingness",False): raise ValueError("validation missing-score rule differs")
    if manifest.get("ledger_profile","standard") != screen.get("ledger_profile","standard"): raise ValueError("validation ledger profile differs")
    robust = manifest.get("robust_control_missingness",False)
    checks = []
    for cell in report["control_cells"]:
        capacity = {a:cell[a].get("dispositions",{}).get("context_capacity",0) for a in ("K","F")}
        if robust:
            rate_gate = (report.get("accounting", {}).get("stop", "absent") is None and
                         all(bounded_control_rate(cell[a], .4,
                             1.0 if a=="F" and manifest.get("allow_fresh_ceiling",False) else .75, 16)
                             for a in ("K","F")))
        else:
            rate_gate = all(cell[a]["known"]==cell[a]["scheduled"] and cell[a]["known"]>=8
                           and .4 <= cell[a]["success_rate"] <= (1.0 if a=="F" and manifest.get("allow_fresh_ceiling",False) else .75)
                           for a in ("K","F"))
        checks.append({"family":cell["family"],"level":cell["level"],"capacity_failures":capacity,"passed":
                       rate_gate
                       and not any(capacity.values())
                       and cell["K"]["episodes_with_public_mismatch"] >= .25*cell["K"]["scheduled" if robust else "known"]})
    # No dropping inconvenient validation cells. The nominated fixed mixture must
    # pass as a whole, or this design does not progress to confirmation.
    return {**screen,"ready_for_confirmation":bool(checks) and all(c["passed"] for c in checks),
            "validation_checks":checks,"used_seeds":screen["used_seeds"]+[manifest["seed"]],
            "validation_manifest_sha256":sha(manifest),"validation_analysis_sha256":sha(report),
            "next":"freeze fixed-size confirmation" if checks and all(c["passed"] for c in checks) else "calibration gate failed; no confirmation claim",
            "validation_uncertainty":"eight per cell is a minimum design gate, not proof that future success rates stay in range"}
