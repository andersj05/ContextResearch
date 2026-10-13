"""Explicit prepare/run/audit commands; importing the package makes no calls."""
import argparse
from .common import SEED, WORKERS, wire


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    freeze = sub.add_parser("prepare")
    freeze.add_argument("folder")
    freeze.add_argument("--split", choices=["study", "fixture"], default="study")
    freeze.add_argument("--seed", type=int, default=SEED)
    freeze.add_argument("--per-family", type=int, default=64)
    freeze.add_argument("--workers", type=int, default=WORKERS)
    freeze.add_argument("--gate-folder")
    launch = sub.add_parser("run")
    launch.add_argument("bundle")
    launch.add_argument("output")
    launch.add_argument("--live", action="store_true")
    audit = sub.add_parser("audit")
    audit.add_argument("bundle")
    audit.add_argument("output")
    audit.add_argument("destination")
    args = parser.parse_args()
    if args.command == "prepare":
        from .prepare import prepare
        from .runtime import PatchRuntime
        result = prepare(args.folder, runtime=PatchRuntime(), split=args.split, seed=args.seed,
                         per_family=args.per_family, workers=args.workers, gate_folder=args.gate_folder)
        print(wire({key: result[key] for key in ("study", "split", "generation_ceiling", "tasks_sha256", "snapshot_sha256")}))
    elif args.command == "run":
        from .runner import run
        print(wire(run(args.bundle, args.output, live=args.live)))
    else:
        from .audit import audit
        print(wire(audit(args.bundle, args.output, args.destination)))


if __name__ == "__main__":
    main()
