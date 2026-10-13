"""Freeze, rehearse, launch, and independently audit the authorized v5 continuation."""
import argparse
from dataclasses import asdict
from pathlib import Path
import shutil

from .prepare import prepare, check_prepared
from .accounting import Ledger
from .dispatch import Dispatcher
from .schedule import execute
from .analysis import analyze
from ..rollback_development_v5.common import ROOT, IMAGE, now, read, save_new, sha, wire
from ..rollback_development_v5.run import fresh_output
from ..rollback_development_v5.schedule import identities
from ..rollback_development_v5.calibration import cases
from ..rollback_development_v5.preflight import preflight
from ..rollback_development_v5.dispatch import live_factory
from ..rollback_development_v5.simulation import ScriptedTransport, OracleRunner
from ..rollback_pilot.code_runner import DockerRunner


def run(prepared, output, *, workers=4, live=False, executable=None, global_instructions=None):
    if type(workers) is not int or not 1 <= workers <= 4:
        raise ValueError("one through four workers required by this amendment")
    manifest, tasks, historical, _ = check_prepared(prepared)
    prior = ROOT / manifest["continuation"]["prior_phase"]
    if live != manifest["continuation"]["prior"]["live"]:
        raise ValueError("offline fixtures and live evidence must not be mixed")
    output = fresh_output(output)
    save_new(Path(prepared) / ("launch_started.json" if live else "simulation_started.json"),
             {"started_utc": now(), "output": str(output), "manifest_sha256": sha(manifest)})
    if live:
        executable = executable or shutil.which("codex.exe") or shutil.which("codex")
        global_instructions = global_instructions or Path.home() / ".codex" / "AGENTS.md"
        checked = preflight(executable, global_instructions, output / "scratch")
        previous = read(prior / "preflight.json")
        # These pinned client properties define the declared information contract.
        fields = ("executable_sha256", "configuration_sha256", "global_instructions_sha256", "registry_sha256")
        if any(checked.get(k) != previous.get(k) for k in fields):
            raise ValueError("pinned client/global-instruction/registry binding changed")
        save_new(output / "preflight.json", checked)
        factory = live_factory(executable, global_instructions, checked, output / "scratch")
        runner = DockerRunner(IMAGE)
        runner.audit()
    else:
        factory = lambda: ScriptedTransport(tasks, delay=.002)
        runner = OracleRunner(tasks)
    for name in ("requests", "responses", "diagnostics"):
        if (prior / name).exists():
            shutil.copytree(prior / name, output / name)
    save_new(output / "calibration.json", read(prior / "calibration.json"))
    save_new(output / "prior_execution.json", read(prior / "execution.json"))
    save_new(output / "manifest.json", manifest)
    save_new(output / "run_settings.json", {"started_utc": now(), "workers": workers, "live": live,
             "prepared": str(Path(prepared).resolve()), "prior_phase": str(prior),
             "evidence_kind": "provider_continuation" if live else "offline_scripted_continuation"})
    allocation = identities(tasks, manifest["tracks"]) + [c["identity"] for c in cases()]
    ledger = Ledger(output / "ledger.sqlite", allocation, workers, prior=prior / "ledger.sqlite",
                    generation_ceiling=manifest["continuation"]["generation_ceiling"])
    dispatcher = Dispatcher(output, manifest, ledger, factory, historical=historical)
    execution = execute(tasks, manifest, dispatcher, runner, output, workers,
                        read(prior / "execution.json"), historical)
    accounting = ledger.snapshot()
    save_new(output / "execution.json", execution)
    save_new(output / "analysis.json", analyze(tasks, execution, accounting, manifest, simulated=not live))
    states = {c["call_id"]: c["state"] for c in accounting["calls"]}
    save_new(output / "slot_dispositions.json", [{"call_id": i.key, "identity": asdict(i),
             "disposition": states.get(i.key, "never_dispatched")} for i in allocation])
    save_new(output / "evidence_manifest.json", {"files": [
        {"path": p.relative_to(output).as_posix(), "sha256": sha(p.read_bytes())}
        for p in sorted(output.rglob("*.json"))], "ledger_sha256": sha((output / "ledger.sqlite").read_bytes())})
    return {"folder": str(output), "jobs": len(execution["jobs"]), "completed_calls": accounting["completed_calls"],
            "new_admissions": len(accounting["calls"]) - len(historical), "stopped": execution["stopped"],
            "model_calls": len(accounting["calls"]) - len(historical) if live else 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "simulate", "launch", "audit"))
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--prior", type=Path)
    parser.add_argument("--prepared", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--global-instructions", type=Path)
    args = parser.parse_args()
    if args.mode == "prepare":
        if args.bundle is None or args.prior is None:
            parser.error("prepare requires --bundle and --prior")
        m = prepare(args.bundle, args.prior, args.output)
        result = {"jobs": len(m["jobs"]), "generation_ceiling": m["continuation"]["generation_ceiling"], "model_calls": 0}
    elif args.prepared is None:
        parser.error("--prepared is required")
    elif args.mode == "audit":
        from .audit import audit
        result = audit(args.prepared, args.output)
    elif args.mode == "launch" and not args.live:
        parser.error("launch requires --live")
    else:
        result = run(args.prepared, args.output, workers=args.workers, live=args.mode == "launch",
                     executable=args.executable, global_instructions=args.global_instructions)
    print(wire(result), flush=True)


if __name__ == "__main__":
    main()
