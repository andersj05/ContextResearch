"""Freeze a bounded matched development pilot before any model observations."""
from dataclasses import asdict
from pathlib import Path
import zipfile

from .common import (ROOT, PACKAGE, STUDY, MODEL, EFFORT, SEED, MAX_WORKERS,
                     DEFAULT_WORKERS, sha, save_new, read, now)
from ..rollback_challenge_v6.tasks import generate as old_generate
from ..rollback_challenge_v6.verification import verify_tasks
from ..rollback_checkpoint_v7.prepare import bindings as old_bindings
from ..rollback_development_v5.accounting import Identity


def generate(*, split="pilot", seed=SEED, replicates=24, stages=3, actions=4):
    if split not in {"pilot", "fixture"}:
        raise ValueError("only development pilot or fixture allocations")
    tasks = old_generate(split="fixture" if split == "fixture" else "screen",
                         seed=seed, cells=[("revision_ledger", 2)], replicates=replicates,
                         stages=stages, actions=actions, require_candidates=True,
                         ledger_profile="intermediate")
    for task in tasks:
        task["task_id"] = f"v8-{split}-revision_ledger-{sha([STUDY, split, seed, task['replicate']])[:16]}"
        task["split"] = split
        task["sha256"] = sha({k: v for k, v in task.items() if k != "sha256"})
    return tasks


def identities(tasks):
    result = []
    for task in tasks:
        h = task["action_allowance"]
        result.extend(Identity(STUDY, task["task_id"], "mechanism", "prefix", step, "action")
                      for step in range(1, h + 1))
        result.extend(Identity(STUDY, task["task_id"], "mechanism", "prefix", step, "lesson")
                      for step in range(1, h))
        result.extend(Identity(STUDY, task["task_id"], "mechanism", arm, step, "action")
                      for arm in ("K", "R") for step in range(2, h + 1))
    return result


def jobs(tasks, seed):
    result = []
    for task in sorted(tasks, key=lambda t: sha([seed, "task-order", t["task_id"]])):
        prefix_id = sha([STUDY, task["task_id"], "prefix"])
        result.append({"task_id": task["task_id"], "arm": "prefix", "job_id": prefix_id})
        for arm in sorted(("K", "R"), key=lambda a: sha([seed, task["task_id"], a])):
            result.append({"task_id": task["task_id"], "arm": arm,
                           "job_id": sha([STUDY, task["task_id"], arm]), "depends_on": prefix_id})
    return result


def generation_bound(tasks):
    # Failure at action j: j prefix actions + one lesson + 2*(H-j) continuations.
    # j >= 1, hence <= 2H. No eligible failure: <= H, with no lesson.
    return sum(2 * task["action_allowance"] for task in tasks)


def bindings():
    paths = {row["path"] for row in old_bindings()}
    paths.add("scripts/run_offline_tests_parallel.py")
    paths.update(p.relative_to(ROOT).as_posix() for pattern in ("*.py", "*.md")
                 for p in PACKAGE.glob(pattern))
    return [{"path": path, "sha256": sha((ROOT / path).read_bytes())} for path in sorted(paths)]


def prepare(folder, *, split="pilot", seed=SEED, replicates=24, stages=3, actions=4,
            workers=DEFAULT_WORKERS, max_calls=192):
    folder = Path(folder).resolve()
    if not folder.is_relative_to(ROOT) or folder.exists():
        raise ValueError("new workspace bundle required")
    if type(workers) is not int or not 1 <= workers <= MAX_WORKERS:
        raise ValueError("worker count must be between one and thirty-two")
    tasks = generate(split=split, seed=seed, replicates=replicates, stages=stages, actions=actions)
    bound = generation_bound(tasks)
    if type(max_calls) is not int or max_calls < bound:
        raise ValueError(f"complete allocation requires at most {bound} admissions; budget is {max_calls}")
    verification = verify_tasks(tasks)
    sources = bindings()
    folder.mkdir(parents=True)
    save_new(folder / "tasks.json", tasks)
    save_new(folder / "verification.json", verification)
    with zipfile.ZipFile(folder / "source_snapshot.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for row in sources:
            info = zipfile.ZipInfo(row["path"], date_time=(2026, 10, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (ROOT / row["path"]).read_bytes())
    manifest = {
        "study": STUDY, "prepared_utc": now(), "split": split,
        "evidence_kind": "unperformed_development_allocation",
        "model": MODEL, "effort": EFFORT, "immutable_model_revision": None,
        "provider_sampling_seed": None, "seed": seed, "replicates": replicates,
        "stages": stages, "actions": actions, "arms": ["K", "R"],
        "workers": workers, "maximum_workers": MAX_WORKERS,
        "tasks_sha256": sha(tasks), "jobs": jobs(tasks, seed),
        "schedule": [asdict(i) for i in identities(tasks)],
        "generation_ceiling": bound, "possible_call_identities": len(identities(tasks)),
        "source_bindings": sources, "verification_sha256": sha(verification),
        "snapshot_sha256": sha((folder / "source_snapshot.zip").read_bytes()),
        "primary": "engineering efficiency and safe parallel execution; rollback outcomes are descriptive only",
        "scheduler": "dependency-ready continuations first, frozen manifest rank, bounded active futures",
        "live_comparison_scope": "new cohort operation check; no causal speedup estimate from comparison with v7",
        "pair_contract": "initial K/R requests byte-identical after removing only trial; full released dossier, pre-failure checkpoint, feedback and one common lesson identical",
        "eligibility": "first natural public mismatch, valid shared lesson, both requests fit, at least one action remains",
        "stopping": "complete fixed allocation regardless of observed direction; no extension for effect or minimum pair count",
        "minimum_complete_pairs_for_descriptive_interval": 6,
        "access": "fresh isolated subscription thread per call; full released public dossier; disabled and empty MCP inventory; every observed tool-use attempt rejected; no archives, future packets, evaluator or opaque reasoning replay",
        "unknown_handling": "unknowns stop affected trajectory and remain missing; no repeated identities; global source/account/isolation/accounting faults stop admission",
        "resources": "shared prefix and lesson counted once; continuation and projected standalone totals reported separately; no equal-token or equal-dollar claim",
        "authorization": "User requests more workers and efficient execution on 2026-10-13 UTC; standing Luna subscription authorization, no API key or purchase",
        "spending": "no API key, purchase, or provider fallback; every action, lesson and unknown counts; planning credits are not actual charges",
        "limitations": ["One authored family, new identities but control-informed development design.",
                        "Visible branch deletion, not private reasoning-state rollback.",
                        "The common lesson can retain branch-derived observations or failed values.",
                        "A small pilot cannot establish superiority, equivalence, or deployed-harness gains."]
    }
    save_new(folder / "manifest.json", manifest)
    save_new(folder / "bundle.json", {"manifest_sha256": sha(manifest), "model_calls": 0})
    return manifest


def check_bundle(folder, *, check_sources=True):
    folder = Path(folder)
    manifest, tasks = read(folder / "manifest.json"), read(folder / "tasks.json")
    if sha(manifest) != read(folder / "bundle.json")["manifest_sha256"] or sha(tasks) != manifest["tasks_sha256"]:
        raise ValueError("bundle changed")
    if manifest["study"] != STUDY or manifest["arms"] != ["K", "R"]:
        raise ValueError("study contract changed")
    if type(manifest["workers"]) is not int or not 1 <= manifest["workers"] <= MAX_WORKERS:
        raise ValueError("invalid frozen worker count")
    if tasks != generate(split=manifest["split"], seed=manifest["seed"], replicates=manifest["replicates"],
                         stages=manifest["stages"], actions=manifest["actions"]):
        raise ValueError("cohort does not reproduce")
    if manifest["schedule"] != [asdict(i) for i in identities(tasks)] or manifest["jobs"] != jobs(tasks, manifest["seed"]):
        raise ValueError("schedule changed")
    if manifest["generation_ceiling"] != generation_bound(tasks):
        raise ValueError("generation ceiling changed")
    if sha(read(folder / "verification.json")) != manifest["verification_sha256"]:
        raise ValueError("verification changed")
    if sha((folder / "source_snapshot.zip").read_bytes()) != manifest["snapshot_sha256"]:
        raise ValueError("snapshot changed")
    with zipfile.ZipFile(folder / "source_snapshot.zip") as archive:
        if set(archive.namelist()) != {r["path"] for r in manifest["source_bindings"]}:
            raise ValueError("snapshot inventory changed")
        for row in manifest["source_bindings"]:
            if sha(archive.read(row["path"])) != row["sha256"]:
                raise ValueError("snapshot source changed")
            if check_sources and sha((ROOT / row["path"]).read_bytes()) != row["sha256"]:
                raise ValueError("source drift: " + row["path"])
    return manifest, tasks
