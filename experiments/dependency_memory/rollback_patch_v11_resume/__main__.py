"""Explicit frozen recovery preparation, launch and independent audit."""

import argparse
from experiments.dependency_memory.rollback_patch_v11.common import wire


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("folder")
    prepare_parser.add_argument("--original-bundle", required=True)
    prepare_parser.add_argument("--prior-output", required=True)
    prepare_parser.add_argument("--prior-audit", required=True)
    launch = sub.add_parser("run")
    launch.add_argument("bundle")
    launch.add_argument("output")
    launch.add_argument("--live", action="store_true")
    launch.add_argument("--executable")
    launch.add_argument("--global-instructions")
    audit_parser = sub.add_parser("audit")
    audit_parser.add_argument("bundle")
    audit_parser.add_argument("output")
    audit_parser.add_argument("destination")
    args = parser.parse_args()
    if args.command == "prepare":
        from experiments.dependency_memory.rollback_patch_v11_resume.prepare import prepare
        result = prepare(args.folder, original_bundle=args.original_bundle,
                         prior_output=args.prior_output, prior_audit=args.prior_audit)
        print(wire({key: result[key] for key in ("study", "generation_ceiling", "tasks_sha256")}))
    elif args.command == "run":
        from experiments.dependency_memory.rollback_patch_v11_resume.runner import run
        print(wire(run(args.bundle, args.output, live=args.live,
                       executable=args.executable, global_instructions=args.global_instructions)))
    else:
        from experiments.dependency_memory.rollback_patch_v11_resume.audit import audit
        print(wire(audit(args.bundle, args.output, args.destination)))


if __name__ == "__main__":
    main()
