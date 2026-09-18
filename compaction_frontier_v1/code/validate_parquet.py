#!/usr/bin/env python3
"""Validate the generated compaction Parquet package and smoke-load SFT rows."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "parquet"


def rows(name: str) -> list[dict]:
    return pq.read_table(DATA / name).to_pylist()


def keys(items: list[dict]) -> set[str]:
    return {item["example_id"] for item in items}


def main() -> None:
    manifest = json.loads((DATA / "manifest.json").read_text())
    artifacts = rows("compaction_artifacts.parquet")
    strict = rows("compaction_sft_strict.parquet")
    broad = rows("compaction_sft_broad.parquet")
    train = rows("compaction_sft_train.parquet")
    validation = rows("compaction_sft_validation.parquet")
    test = rows("compaction_sft_test.parquet")
    experimental = rows("compaction_sft_experimental_balanced.parquet")

    assert len(artifacts) == 2061
    assert len({row["prefix_sha256"] for row in artifacts}) == len(artifacts)
    assert all(row["raw_compaction_encrypted_content"] for row in artifacts)
    assert all(row["raw_compaction_encrypted_content"].startswith("gAAAAA") for row in artifacts)
    assert all(not row["label_is_gold"] and not row["verified_plaintext"] for row in artifacts)
    assert all(row["target_status"] == "weak_pseudo_label" for row in artifacts)
    assert all(row["selection_metric"].startswith("oracle_") for row in artifacts)

    # Nested prefix cutoffs from a parent window must remain in one fold.
    parent_splits: dict[str, set[str]] = {}
    for row in artifacts:
        parent_splits.setdefault(row["parent_window_id"], set()).add(row["split"])
    assert all(len(splits) == 1 for splits in parent_splits.values())

    assert keys(strict) <= keys(broad)
    assert keys(train).isdisjoint(keys(validation))
    assert keys(train).isdisjoint(keys(test))
    assert keys(validation).isdisjoint(keys(test))
    assert keys(train) | keys(validation) | keys(test) == keys(broad)
    assert len({row["assistant_target"] for row in broad}) == len(broad)

    for row in broad + experimental:
        messages = row["messages"]
        assert len(messages) >= 3
        assert messages[-2]["role"] == "user"
        assert messages[-2]["content"] == row["compaction_instruction"]
        assert messages[-1] == {"role": "assistant", "content": row["assistant_target"]}
        assert row["loss_scope"] == "final_assistant_message_only"
        assert row["label_status"] == "weak_pseudo_label_oracle_selected"
        assert not row["verified_plaintext"]
        assert row["assistant_target"].strip()
        assert math.isfinite(row["sample_weight"]) and row["sample_weight"] > 0

    # Strict/broad are honest small-context pseudo-label tiers; only experimental spans the ceiling.
    assert max(row["actual_input_tokens"] for row in broad) < 10_000
    assert max(row["actual_input_tokens"] for row in experimental) >= 350_000
    assert manifest["data_contract_verdict"]["verified_plaintext_compaction_summary"] is False
    assert manifest["data_contract_verdict"]["gold_label"] is False
    assert manifest["recommended_training"]["loss_scope"] == "final assistant message only"

    print(json.dumps({
        "artifacts": len(artifacts),
        "strict": len(strict),
        "broad": len(broad),
        "train": len(train),
        "validation": len(validation),
        "test": len(test),
        "experimental": len(experimental),
        "parent_windows": len(parent_splits),
        "broad_max_input_tokens": max(row["actual_input_tokens"] for row in broad),
        "experimental_max_input_tokens": max(
            row["actual_input_tokens"] for row in experimental
        ),
        "sample_training_message_count": len(train[0]["messages"]),
        "sample_target_chars": len(train[0]["assistant_target"]),
        "status": "PASS",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
