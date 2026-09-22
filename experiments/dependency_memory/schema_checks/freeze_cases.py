"""One-time fixture freeze; reports hashes and byte sizes, never case contents."""
from hashlib import sha256
import json
from pathlib import Path

from .cases import DEV_SEEDS, EVAL_SEEDS, FAMILIES, make_case


def main():
    directory = Path(__file__).parent / "fixtures"
    if directory.exists():
        raise ValueError("Frozen fixtures already exist")
    directory.mkdir()
    manifest = {"version": "tool_trace_v1", "cases": []}
    for split, seeds in (("development", DEV_SEEDS), ("evaluation", EVAL_SEEDS)):
        for family in FAMILIES:
            for seed in seeds:
                case = make_case(family, seed, split)
                raw = (json.dumps(case, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()
                path = directory / f"{split}-{family}-{seed}.json"
                path.write_bytes(raw)
                manifest["cases"].append({"file": path.name, "split": split,
                                          "sha256": sha256(raw).hexdigest(), "bytes": len(raw)})
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for item in manifest["cases"]:
        print(item["file"], item["sha256"], item["bytes"])


if __name__ == "__main__":
    main()
