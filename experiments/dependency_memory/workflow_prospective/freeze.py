"""Method integrity only; append-only future task data are not this code freeze."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEPENDENCIES = (
    "evidence_use/guard.py", "workflow_intake/views.py", "workflow_eval/grader.py",
    "workflow_eval/packet.py", "workflow_eval/prompts.json", "workflow_eval_live/study.py", "workflow_eval_live/protocol.py",
)


def fingerprints():
    paths = [*HERE.glob("*.py"), HERE / "PROTOCOL.md"]
    paths += [HERE.parent / name for name in DEPENDENCIES]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def validate_lock():
    saved = json.loads((HERE / "method-lock.json").read_text(encoding="utf-8"))
    expected = {"version": "single_repository_method_lock_v1", "authorized_provider_dispatches": 0,
                "sha256": fingerprints()}
    if saved != expected:
        raise ValueError("Frozen method bytes changed; use a separate version")
    return len(saved["sha256"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-lock", action="store_true")
    args = parser.parse_args()
    if args.write_lock:
        target = HERE / "method-lock.json"
        if target.exists():
            raise FileExistsError("Do not overwrite a frozen method lock")
        target.write_bytes((json.dumps({"version": "single_repository_method_lock_v1", "authorized_provider_dispatches": 0,
                                      "sha256": fingerprints()}, sort_keys=True, indent=2) + "\n").encode())
    print(json.dumps({"method_integrity": "PASS", "locked_files": validate_lock(), "provider_dispatches": 0,
                      "live_launch_ready": False, "external_grader_review": "pending"}, indent=2))


if __name__ == "__main__":
    main()
