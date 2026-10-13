"""Prepare, verify, simulate, or explicitly launch the frozen parallel study."""
import argparse
from dataclasses import asdict
from pathlib import Path
import shutil

from .common import ROOT, IMAGE, DEFAULT_WORKERS, MAX_WORKERS, now, read, save_new, sha, wire
from .prepare import prepare, check_bundle, bindings
from .verification import verify_tasks
from .schedule import identities, execute, TRACKS
from .accounting import Ledger, Identity, Stopped
from .dispatch import Dispatcher, live_factory
from .analysis import analyze
from .simulation import ScriptedTransport, OracleRunner
from .calibration import cases, validate
from .preflight import preflight
from ..rollback_pilot.code_runner import DockerRunner


def fresh_output(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT) or path.exists():
        raise ValueError("new workspace output directory required")
    path.mkdir(parents=True)
    return path


def run(bundle, output, *, workers=DEFAULT_WORKERS, live=False, executable=None, global_instructions=None):
    if type(workers) is not int or not 1 <= workers <= MAX_WORKERS:
        raise ValueError("workers must be between 1 and 8")
    manifest, tasks = check_bundle(bundle)
    output = fresh_output(output)
    calibration = cases()
    allocation = identities(tasks, manifest["tracks"]) + [c["identity"] for c in calibration]
    if live:
        checks = read(Path(bundle) / "task_checks.json")
        if not checks.get("all_passed") or checks["tasks_sha256"] != sha(tasks) or checks.get("source_bindings") != bindings():
            raise ValueError("fresh complete task certification required")
        executable = executable or shutil.which("codex.exe") or shutil.which("codex")
        global_instructions = global_instructions or Path.home() / ".codex" / "AGENTS.md"
        if not executable or not Path(global_instructions).is_file():
            raise ValueError("installed Codex and declared global instruction file required")
        # Exclusive on the bundle, not just output, so a new output cannot bypass it.
        save_new(Path(bundle) / "launch_started.json", {"started_utc": now(), "output": str(output), "manifest_sha256": sha(manifest)})
        checked = preflight(executable, global_instructions, output / "scratch")
        save_new(output / "preflight.json", checked)
        factory = live_factory(executable, global_instructions, checked, output / "scratch")
        runner = DockerRunner(IMAGE); runner.audit()
    else:
        factory = lambda: ScriptedTransport(tasks + [c["task"] for c in calibration], delay=.002)
        runner = OracleRunner(tasks + [c["task"] for c in calibration])
    save_new(output / "manifest.json", manifest)
    save_new(output / "run_settings.json", {"started_utc": now(), "workers": workers, "live": live, "bundle": str(Path(bundle).resolve()),
                                           "evidence_kind": "provider_launch" if live else "offline_scripted_fixture"})
    ledger = Ledger(output / "ledger.sqlite", allocation, workers)
    dispatcher = Dispatcher(output, manifest, ledger, factory)
    calibration_rows = []
    if live:
        for case in calibration:
            try:
                response = dispatcher(case["identity"], case["request"])
                validate(case, response.text, runner)
                calibration_rows.append({"call_id": case["identity"].key, "disposition": "passed"})
            except Exception as error:
                ledger.stop("calibration_failed")
                calibration_rows.append({"call_id": case["identity"].key, "disposition": "failed", "error_type": type(error).__name__})
                break
    save_new(output / "calibration.json", {"live": live, "rows": calibration_rows, "excluded_from_study": True})
    execution = execute(tasks, manifest, dispatcher, runner, output, workers)
    accounting = ledger.snapshot()
    result = analyze(tasks, execution, accounting, simulated=not live)
    save_new(output / "execution.json", execution)
    save_new(output / "analysis.json", result)
    used = {r["call_id"]: r["state"] for r in accounting["calls"]}
    slots = [{"call_id": i.key, "identity": asdict(i), "disposition": used.get(i.key, "never_dispatched")} for i in allocation]
    save_new(output / "slot_dispositions.json", slots)
    save_new(output / "evidence_manifest.json", {"files": [{"path": p.relative_to(output).as_posix(), "sha256": sha(p.read_bytes())} for p in sorted(output.rglob("*.json"))],
                                                "ledger_sha256": sha((output / "ledger.sqlite").read_bytes())})
    return {"folder": str(output), "jobs": len(execution["jobs"]), "completed_calls": accounting["completed_calls"],
            "stopped": execution["stopped"], "real_model_generations": accounting["completed_calls"] if live else 0,
            "peak_parallel_jobs": execution["peak_active_jobs"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "verify", "preflight", "simulate", "audit", "launch"))
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--tracks", default=",".join(TRACKS))
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--global-instructions", type=Path)
    args = parser.parse_args()
    if args.mode == "prepare":
        m = prepare(args.bundle, tuple(args.tracks.split(",")))
        print(wire({"tasks": len(m["tasks"]), "jobs": len(m["jobs"]), "possible_call_identities": m["possible_total_call_identities"], "model_calls": 0}))
    elif args.mode == "verify":
        m, tasks = check_bundle(args.bundle)
        result = verify_tasks(tasks, workers=args.workers)
        check_bundle(args.bundle)
        result["source_bindings"] = bindings()
        save_new(args.output or args.bundle / "task_checks.json", result)
        print(wire({"all_passed": result["all_passed"], "math_tasks": len(result["mathematics"]), "coding_tasks": len(result["coding"]), "model_calls": 0}))
    elif args.mode == "preflight":
        check_bundle(args.bundle)
        output = fresh_output(args.output)
        result = preflight(args.executable or shutil.which("codex.exe") or shutil.which("codex"),
                           args.global_instructions or Path.home() / ".codex" / "AGENTS.md", output / "scratch")
        save_new(output / "preflight.json", result)
        print(wire({"passed": True, "real_model_generations": 0}))
    elif args.mode == "audit":
        from .audit import audit
        if args.output is None: parser.error("--output must name the existing run to audit")
        result = audit(args.bundle, args.output)
        print(wire(result))
    elif args.mode == "launch" and not args.live:
        parser.error("launch requires --live; preparation and simulation never call the model")
    else:
        if args.output is None: parser.error("--output is required")
        print(wire(run(args.bundle, args.output, workers=args.workers, live=args.mode == "launch",
                       executable=args.executable, global_instructions=args.global_instructions)))


if __name__ == "__main__":
    main()
