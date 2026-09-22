"""Write development fixtures now; append commit-conditioned evaluation later."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from .casebook import DEV, DEV_SEEDS, EVAL, compact, evaluation_seeds, make_case

FOLDER = Path(__file__).parent / "fixtures"


def entry(case, path):
    raw = path.read_bytes()
    return {"file": path.name, "split": case["split"], "family": case["family"],
            "sha256": sha256(raw).hexdigest(), "bytes": len(raw)}


def write_case(case):
    path = FOLDER / f"{case['split']}-{case['id']}.json"
    if path.exists():
        raise ValueError("Never overwrite a frozen case")
    path.write_text(json.dumps(case, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    return entry(case, path)


def freeze_development():
    FOLDER.mkdir(exist_ok=True)
    manifest = FOLDER / "manifest.json"
    if manifest.exists():
        raise ValueError("Development manifest already frozen")
    rows = [write_case(make_case(family, seed, "development")) for family in DEV for seed in DEV_SEEDS]
    manifest.write_text(json.dumps({"version": "cross_record_v1", "development": rows,
                                    "evaluation": [], "implementation_commit": None}, indent=2) + "\n",
                        encoding="utf-8", newline="\n")


def freeze_evaluation(commit):
    manifest = FOLDER / "manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data["evaluation"] or data["implementation_commit"] is not None:
        raise ValueError("Evaluation already frozen")
    seeds = evaluation_seeds(commit)
    rows = [write_case(make_case(family, seed, "evaluation")) for family in EVAL for seed in seeds[family]]
    data.update(evaluation=rows, implementation_commit=commit, evaluation_seeds=seeds)
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--development", action="store_true")
    parser.add_argument("--evaluation-implementation-commit")
    args = parser.parse_args()
    if args.development == bool(args.evaluation_implementation_commit):
        parser.error("Choose exactly one freeze stage")
    if args.development:
        freeze_development()
    else:
        freeze_evaluation(args.evaluation_implementation_commit)


if __name__ == "__main__":
    main()
