"""Prepare, rehearse, run a bounded pilot, or replay saved receipts."""
import argparse
from pathlib import Path

from .common import DEFAULT_WORKERS, SEED, wire
from .prepare import prepare, check_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "simulate", "launch", "audit", "preview"])
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--split", choices=["pilot", "fixture"], default="pilot")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--replicates", type=int, default=24)
    parser.add_argument("--stages", type=int, default=3)
    parser.add_argument("--actions", type=int, default=4)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--max-calls", type=int, default=192)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--snapshot", action="store_true")
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--global-instructions", type=Path)
    parser.add_argument("--task-index", type=int, default=0)
    args = parser.parse_args()
    if args.snapshot and args.mode != "audit":
        parser.error("--snapshot is for offline audit only")
    if args.live and args.mode != "launch":
        parser.error("--live is only valid with launch")
    if args.mode == "prepare":
        if not args.output:
            parser.error("prepare requires --output")
        result = prepare(args.output, split=args.split, seed=args.seed, replicates=args.replicates,
                         stages=args.stages, actions=args.actions,
                         workers=args.workers if args.workers is not None else DEFAULT_WORKERS,
                         max_calls=args.max_calls)
        result = {"tasks": args.replicates, "jobs": len(result["jobs"]),
                  "generation_ceiling": result["generation_ceiling"],
                  "possible_identities": result["possible_call_identities"],
                  "workers": result["workers"], "model_calls": 0}
    else:
        if not args.bundle:
            parser.error("--bundle required")
        if args.mode in {"simulate", "launch"}:
            if not args.output:
                parser.error("--output required")
            if args.mode == "launch" and not args.live:
                parser.error("launch requires explicit --live")
            from .runner import run
            result = run(args.bundle, args.output, live=args.mode == "launch", workers=args.workers,
                         executable=args.executable, global_instructions=args.global_instructions)
        elif args.mode == "audit":
            if not args.run:
                parser.error("--run required")
            if args.snapshot:
                from .snapshot import audit_snapshot
                result = audit_snapshot(args.bundle, args.run)
            else:
                from .audit import audit
                result = audit(args.bundle, args.run)
        else:
            from .engine import initial_state
            from .contexts import actor_state
            _, tasks = check_bundle(args.bundle)
            task = tasks[args.task_index]
            result = actor_state(task, initial_state(task))
    print(wire(result), flush=True)


if __name__ == "__main__":
    main()
