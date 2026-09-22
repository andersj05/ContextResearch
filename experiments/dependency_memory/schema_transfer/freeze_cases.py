"""One-time freeze; emit hashes and byte lengths without printing case values."""
from hashlib import sha256
import json
from pathlib import Path

from .casebook import DEV, EVAL, DEV_SEEDS, EVAL_SEEDS, make_case


def main():
    folder = Path(__file__).parent / "fixtures"
    if folder.exists():
        raise ValueError("Fixtures already frozen")
    folder.mkdir()
    manifest = {"version": "schema_transfer_v1", "cases": []}
    for split, families, seeds in (("development", DEV, DEV_SEEDS), ("evaluation", EVAL, EVAL_SEEDS)):
        for family in families:
            for seed in seeds:
                case = make_case(family, seed, split)
                raw = (json.dumps(case, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()
                name = f"{split}-{family}-{seed}.json"
                (folder / name).write_bytes(raw)
                manifest["cases"].append({"file": name, "split": split, "family": family,
                                          "sha256": sha256(raw).hexdigest(), "bytes": len(raw)})
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for row in manifest["cases"]:
        print(row["file"], row["sha256"], row["bytes"])


if __name__ == "__main__":
    main()
