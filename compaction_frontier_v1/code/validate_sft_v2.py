#!/usr/bin/env python3
"""Validate compaction Parquet v2 package and smoke-load trainer rows."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "parquet_v2"


def read(name):
    return pq.read_table(DATA / name).to_pylist()


def ids(rows):
    return {row["example_id"] for row in rows}


def main():
    manifest = json.loads((DATA / "manifest.json").read_text())
    advanced = read("compaction_sft_v2_advanced_all.parquet")
    advanced_train = read("compaction_sft_v2_advanced_train.parquet")
    advanced_validation = read("compaction_sft_v2_advanced_validation.parquet")
    advanced_test = read("compaction_sft_v2_advanced_test.parquet")
    mixed = read("compaction_sft_v2_mixed.parquet")
    mixed_train = read("compaction_sft_v2_mixed_train.parquet")
    mixed_validation = read("compaction_sft_v2_mixed_validation.parquet")
    mixed_test = read("compaction_sft_v2_mixed_test.parquet")
    preferences = read("compaction_preference_v2.parquet")

    assert len(advanced) == 104
    assert len(advanced_train) == 86
    assert len(advanced_validation) == 10
    assert len(advanced_test) == 5
    assert len(preferences) == 86
    prompt = manifest["canonical_prompt"]["text"]
    assert manifest["canonical_prompt"]["lines"] == 8
    assert len(prompt.splitlines()) == 8 and len(prompt.splitlines()) <= 150

    # Every parent remains in one inherited fold across advanced, mixed, and preferences.
    parent_splits = {}
    for row in mixed:
        parent_splits.setdefault(row["parent_window_id"], set()).add(row["split"])
    for row in preferences:
        parent_splits.setdefault(row["parent_window_id"], set()).add(row["split"])
    assert all(len(value) == 1 for value in parent_splits.values())

    assert ids(advanced_train).isdisjoint(ids(advanced_validation))
    assert ids(advanced_train).isdisjoint(ids(advanced_test))
    assert ids(advanced_validation).isdisjoint(ids(advanced_test))
    assert all(row["token_count_error"] <= 0.05 for row in advanced_train)
    assert all(row["split"] == "train" for row in advanced_train)
    assert max(row["actual_input_tokens"] for row in advanced_train) >= 300_000
    assert min(row["actual_input_tokens"] for row in advanced_train) <= 2_000

    # One prefix must map to one target in every training view.
    assert len({row["prefix_sha256"] for row in mixed_train}) == len(mixed_train)
    assert len({row["assistant_target"] for row in advanced}) == len(advanced)
    assert all(not row["verified_plaintext"] for row in mixed)
    assert all(row["loss_scope"] == "final_assistant_message_only" for row in mixed)
    assert all(math.isfinite(row["sample_weight"]) and row["sample_weight"] > 0 for row in mixed)

    for row in mixed_train:
        assert row["messages"][-2] == {"role": "user", "content": prompt}
        assert row["messages"][-1] == {"role": "assistant", "content": row["assistant_target"]}
        assert row["recommended_for_training"]

    for row in preferences:
        assert row["prompt_messages"][-1] == {"role": "user", "content": prompt}
        assert row["chosen"] != row["rejected"]
        assert row["token_error_margin"] >= 0.20
        assert row["chosen_token_error"] < row["rejected_token_error"]
        assert row["chosen_variant"] == row["rejected_variant"]
        assert row["pair_status"].startswith("length_fidelity")

    assert not ({row["parent_window_id"] for row in mixed_train}
                & {row["parent_window_id"] for row in mixed_validation + mixed_test})

    # Manifest checksums verify package stability.
    for name, metadata in manifest["files"].items():
        path = DATA / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == metadata["sha256"]
        assert pq.read_metadata(path).num_rows == metadata["rows"]

    sample = advanced_train[0]
    print(json.dumps({
        "advanced": len(advanced),
        "advanced_train": len(advanced_train),
        "advanced_validation": len(advanced_validation),
        "advanced_test": len(advanced_test),
        "mixed": len(mixed),
        "mixed_train": len(mixed_train),
        "mixed_validation": len(mixed_validation),
        "mixed_test": len(mixed_test),
        "preferences": len(preferences),
        "parent_windows": len(parent_splits),
        "prompt_lines": len(prompt.splitlines()),
        "sample_messages": len(sample["messages"]),
        "sample_target_chars": len(sample["assistant_target"]),
        "advanced_input_range": [
            min(row["actual_input_tokens"] for row in advanced_train),
            max(row["actual_input_tokens"] for row in advanced_train),
        ],
        "status": "PASS",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
