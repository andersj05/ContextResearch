"""Immutable task and analysis freezes with separate calibration/test identities."""
from dataclasses import asdict
from pathlib import Path
import zipfile

from .common import ROOT, PACKAGE, STUDY, MODEL, EFFORT, SEED, sha, save_new, read, now
from .tasks import generate
from .verification import verify_tasks
from ..rollback_development_v5.accounting import Identity
from ..rollback_development_v5.prepare import bindings as old_bindings


def generation_bound(tasks, arms):
    return sum((2*t["action_allowance"]-1 if arm in {"K","R","G"} else t["action_allowance"]) for t in tasks for arm in arms)


def jobs(tasks, arms, seed):
    result = []
    # Neighboring pairs reduce time drift. Arm order is randomized within task,
    # independent of outcomes; workers advance independent complete episodes.
    for t in sorted(tasks, key=lambda t:sha([seed,"task-order",t["task_id"]])):
        for arm in sorted(arms,key=lambda a:sha([seed,t["task_id"],a])):
            result.append({"task_id":t["task_id"],"arm":arm,"job_id":sha([STUDY,t["task_id"],arm])})
    return result


def identities(tasks, arms):
    return [Identity(STUDY,t["task_id"],"policy",arm,step,kind)
            for t in tasks for arm in arms for step in range(1,t["action_allowance"]+1)
            for kind in (["action", "lesson" if arm in {"K","R"} else "summary"] if arm in {"K","R","G"} and step < t["action_allowance"] else ["action"])]


def bindings():
    paths = {r["path"] for r in old_bindings()}
    for package in (PACKAGE, PACKAGE.parent / "rollback_development_v5_continuation"):
        paths.update(p.relative_to(ROOT).as_posix() for p in package.glob("*.py"))
        paths.update(p.relative_to(ROOT).as_posix() for p in package.glob("*.md"))
    return [{"path":p,"sha256":sha((ROOT/p).read_bytes())} for p in sorted(paths)]


def verify_selection(selection, confirmation=False):
    from .audit import audit
    from .analysis import select_screen, validate_selection
    provenance = selection.get("provenance", {})
    def load_phase(label):
        bundle = (ROOT/provenance[label+"_bundle"]).resolve()
        run = (ROOT/provenance[label+"_run"]).resolve()
        if not bundle.is_relative_to(ROOT) or not run.is_relative_to(ROOT): raise ValueError("selection outside repository")
        audit(bundle,run)
        return read(bundle/"manifest.json"),read(run/"analysis.json")
    m,r=load_phase("screen"); expected=select_screen(r,m)
    if confirmation:
        m,r=load_phase("validation"); expected=validate_selection(expected,r,m)
    if {k:v for k,v in selection.items() if k!="provenance"} != expected:
        raise ValueError("selection disagrees with audited live controls")


def prepare(folder, *, split="screen", seed=SEED, cells=None, replicates=2, stages=4, actions=8,
            arms=None, max_calls=None, selection=None, power_plan=None, require_candidates=None,
            allow_fresh_ceiling=None, robust_control_missingness=None, ledger_profile=None):
    folder = Path(folder).resolve()
    if not folder.is_relative_to(ROOT) or folder.exists(): raise ValueError("new workspace bundle required")
    arms = list(arms or (["K","F"] if split in {"screen","validation"} else ["K","R","Z","G","F"]))
    if len(set(arms)) != len(arms) or any(a not in {"K","R","Z","G","F"} for a in arms): raise ValueError("invalid arms")
    if split in {"screen","validation"} and set(arms) != {"K","F"}: raise ValueError("difficulty selection must use K/F controls only")
    if split in {"validation","confirmation"}:
        if selection is None: raise ValueError("a selection from audited live controls is required")
        verify_selection(selection,confirmation=split=="confirmation")
        if not cells: cells=selection["selected_cells"]
        if sorted(map(tuple,cells))!=sorted(map(tuple,selection["selected_cells"])): raise ValueError("selected cells changed")
        if (stages,actions)!=(selection["stages"],selection["actions"]) or seed in selection["used_seeds"]: raise ValueError("independent seeds and same design required")
        expected_mode=selection.get("require_candidates",False)
        if require_candidates is None: require_candidates=expected_mode
        if require_candidates != expected_mode: raise ValueError("response contract differs from calibration")
        expected_gate=selection.get("allow_fresh_ceiling",False)
        if allow_fresh_ceiling is None: allow_fresh_ceiling=expected_gate
        if allow_fresh_ceiling != expected_gate: raise ValueError("calibration rule differs from selection")
        expected_missing=selection.get("robust_control_missingness",False)
        if robust_control_missingness is None: robust_control_missingness=expected_missing
        if robust_control_missingness != expected_missing: raise ValueError("missing-score rule differs from selection")
        expected_profile=selection.get("ledger_profile","standard")
        if ledger_profile is None: ledger_profile=expected_profile
        if ledger_profile != expected_profile: raise ValueError("ledger profile differs from selection")
    if require_candidates is None: require_candidates=False
    if type(require_candidates) is not bool: raise ValueError("require_candidates must be boolean")
    if allow_fresh_ceiling is None: allow_fresh_ceiling=False
    if type(allow_fresh_ceiling) is not bool: raise ValueError("allow_fresh_ceiling must be boolean")
    if robust_control_missingness is None: robust_control_missingness=False
    if type(robust_control_missingness) is not bool: raise ValueError("robust_control_missingness must be boolean")
    if ledger_profile is None: ledger_profile="standard"
    if type(ledger_profile) is not str or ledger_profile not in {"standard","intermediate"}: raise ValueError("unknown ledger profile")
    if robust_control_missingness and split in {"screen","validation"} and replicates < (8 if split=="screen" else 16):
        raise ValueError("robust control gate requires at least eight screen or sixteen validation tasks per cell")
    if split == "confirmation":
        if not {"K","R"} <= set(arms) or selection is None or power_plan is None:
            raise ValueError("confirmation requires selected validated cells, a frozen power plan, and K/R")
        if selection.get("ready_for_confirmation") is not True: raise ValueError("held-out calibration gate not passed")
        if sorted(map(tuple,cells or [])) != sorted(map(tuple,selection["selected_cells"])): raise ValueError("confirmation cells differ from blind calibration")
        if stages != selection["stages"] or actions != selection["actions"]: raise ValueError("difficulty access/action contract changed")
        if seed in selection["used_seeds"]: raise ValueError("confirmation needs a new seed")
        from .statistics import plan
        if power_plan != plan(power_plan["delta"],power_plan["discordance"],power_plan["target_power"],power_plan["alpha"],increment=power_plan["grid_increment"]):
            raise ValueError("power plan does not reproduce")
    tasks = generate(split=split,seed=seed,cells=cells,replicates=replicates,stages=stages,actions=actions,
                     require_candidates=require_candidates,ledger_profile=ledger_profile)
    bound = generation_bound(tasks,arms)
    if max_calls is not None and (type(max_calls) is not int or bound > max_calls):
        raise ValueError(f"complete frozen schedule needs at most {bound} calls, exceeding budget {max_calls}; reduce cohort before freezing")
    if split == "confirmation" and (power_plan.get("pairs") is None or len(tasks) < power_plan["pairs"]): raise ValueError("cohort smaller than power plan")
    verification = verify_tasks(tasks); sources = bindings()
    folder.mkdir(parents=True)
    save_new(folder/"tasks.json",tasks); save_new(folder/"verification.json",verification)
    with zipfile.ZipFile(folder/"source_snapshot.zip","x",compression=zipfile.ZIP_DEFLATED) as archive:
        for row in sources: archive.write(ROOT/row["path"],row["path"])
    manifest = {"study":STUDY,"prepared_utc":now(),"evidence_kind":"unperformed_allocation", "split":split,
                "model":MODEL,"effort":EFFORT,"immutable_model_revision":None,"provider_sampling_seed":None,
                "seed":seed,"arms":arms,"stages":stages,"actions":actions,"replicates":replicates,
                "require_candidates":require_candidates,
                "allow_fresh_ceiling":allow_fresh_ceiling,
                "robust_control_missingness":robust_control_missingness,"ledger_profile":ledger_profile,
                "cells":sorted({(t['family'],t['difficulty']) for t in tasks}),"tasks_sha256":sha(tasks),
                "jobs":jobs(tasks,arms,seed),"schedule":[asdict(i) for i in identities(tasks,arms)],
                "generation_ceiling":bound,"source_bindings":sources,"selection":selection,"power_plan":power_plan,
                "verification_sha256":sha(verification),"snapshot_sha256":sha((folder/"source_snapshot.zip").read_bytes()),
                "primary":"complete-episode R minus K terminal success; exact two-sided paired test at alpha=0.05",
                "secondary":"all other arms, resources, stages, failures and history length are descriptive",
                "access":"fresh isolated subscription thread per call; only allowlisted visible state; no tools/archive/opaque replay",
                "unknown_handling":"trajectory-local unknown, no retry; source/account/isolation/accounting failures stop all admission",
                "spending":"subscription only; no purchases or API fallback; every writer metered; actual charges unavailable"}
    save_new(folder/"manifest.json",manifest)
    save_new(folder/"bundle.json",{"manifest_sha256":sha(manifest)})
    return manifest


def check_bundle(folder, *, check_sources=True):
    folder = Path(folder); m=read(folder/"manifest.json"); tasks=read(folder/"tasks.json")
    if sha(m) != read(folder/"bundle.json")["manifest_sha256"] or sha(tasks) != m["tasks_sha256"]: raise ValueError("bundle changed")
    if type(m.get("require_candidates",False)) is not bool or any(t["contract"].get("require_candidates",False) != m.get("require_candidates",False) for t in tasks):
        raise ValueError("response contract differs from manifest")
    if type(m.get("allow_fresh_ceiling",False)) is not bool: raise ValueError("invalid calibration rule flag")
    if type(m.get("robust_control_missingness",False)) is not bool: raise ValueError("invalid missing-score rule flag")
    if m.get("ledger_profile","standard") not in {"standard","intermediate"}: raise ValueError("invalid ledger profile")
    if m["schedule"] != [asdict(i) for i in identities(tasks,m["arms"])] or m["jobs"] != jobs(tasks,m["arms"],m["seed"]): raise ValueError("schedule changed")
    if generation_bound(tasks,m["arms"]) != m["generation_ceiling"]: raise ValueError("allocation changed")
    if sha(read(folder/"verification.json")) != m["verification_sha256"]: raise ValueError("verification changed")
    if sha((folder/"source_snapshot.zip").read_bytes()) != m["snapshot_sha256"]: raise ValueError("snapshot changed")
    with zipfile.ZipFile(folder/"source_snapshot.zip") as archive:
        if set(archive.namelist()) != {r["path"] for r in m["source_bindings"]}: raise ValueError("snapshot inventory changed")
        for row in m["source_bindings"]:
            if sha(archive.read(row["path"])) != row["sha256"]: raise ValueError("snapshot source changed")
            if check_sources and sha((ROOT/row["path"]).read_bytes()) != row["sha256"]: raise ValueError("source drift: "+row["path"])
    return m,tasks
