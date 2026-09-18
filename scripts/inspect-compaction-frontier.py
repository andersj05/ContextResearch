"""Offline audit of the supplied release; never calls its remote API clients.

Run with Python and pyarrow installed, or the temporary dependency directory
created during this inspection. Outputs go outside the original release.
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import statistics as st
import sys
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tmp" / "compaction-analysis-deps"))
import pyarrow.parquet as pq

RELEASE = ROOT / "compaction_frontier_v1"
OUT = ROOT / "research" / "compaction-frontier-inspection"


def load(name):
    return pq.read_table(RELEASE / "data" / f"{name}.parquet").to_pylist()


def median(values):
    values = [v for v in values if v is not None]
    return st.median(values) if values else None


def fidelity(rows, key):
    errors = [r[key] for r in rows if r.get(key) is not None]
    return {"n": len(errors), "median_error": median(errors),
            "within_5pct": sum(e <= .05 for e in errors)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    master = load("examples_master")
    selected = load("advanced_selected_examples")
    candidates = load("recovery_candidates")
    experiments = load("recovery_experiment_runs")
    sources = load("source_provenance")
    stats = load("statistical_evidence")
    report = {}
    manifest = json.loads((RELEASE / "manifest.json").read_text())
    mismatches = []
    for name, meta in manifest["files"].items():
        data = (RELEASE / name).read_bytes()
        if len(data) != meta["bytes"] or hashlib.sha256(data).hexdigest() != meta["sha256"]:
            mismatches.append(name)
    report["manifest_integrity"] = {"files_checked": len(manifest["files"]), "mismatches": mismatches}

    # The original validator assumes POSIX paths and the author's source tree.
    # Adapt only those two packaging assumptions in memory. Preserve all data,
    # statistics, trainer, checksum, and identity assertions and the source files.
    validator_path = RELEASE / "code" / "validate_frontier_release.py"
    validator = validator_path.read_text(encoding="utf-8")
    validator = validator.replace("str(path.relative_to(release))", "path.relative_to(release).as_posix()")
    validator = validator.replace('        assert source.is_file(), row["source_path"]',
                                  '        if not source.is_file():\n            continue')
    stdout = io.StringIO()
    old_argv = sys.argv
    try:
        sys.argv = [str(validator_path), "--release", str(RELEASE)]
        with contextlib.redirect_stdout(stdout):
            exec(compile(validator, str(validator_path), "exec"),
                 {"__file__": str(validator_path), "__name__": "__main__"})
        report["adapted_bundled_validator"] = {"status": "PASS", "output": json.loads(stdout.getvalue())}
    except Exception as error:
        report["adapted_bundled_validator"] = {"status": "FAIL", "error": repr(error), "output": stdout.getvalue()}
    finally:
        sys.argv = old_argv
    report["unavailable_original_sources"] = [r["source_path"] for r in sources if not (RELEASE / r["source_path"]).is_file()]
    report["coverage"] = {
        "master_rows": len(master), "parent_windows": len({r["parent_window_id"] for r in master}),
        "advanced_rows": len(selected), "advanced_parents": len({r["parent_window_id"] for r in selected}),
        "candidates": len(candidates), "experiment_records": len(experiments),
        "producer_models": dict(Counter(r["producer_model"] for r in master)),
        "selected_decoder_models": dict(Counter(r["advanced_decoder_model"] for r in selected)),
        "selected_variants": dict(Counter(r["advanced_variant"] for r in selected)),
        "selected_tiers": dict(Counter(r["confidence_tier"] for r in selected)),
        "input_tokens_min": min(r["actual_input_tokens"] for r in master),
        "input_tokens_max": max(r["actual_input_tokens"] for r in master),
    }
    report["fidelity"] = {"selected_all": fidelity(selected, "advanced_token_error")}
    for partition in ("holdout", "discovery"):
        rows = [r for r in selected if r["advanced_benchmark_partition"] == partition]
        report["fidelity"][partition] = {**fidelity(rows, "advanced_token_error"),
            "parents": len({r["parent_window_id"] for r in rows})}
    parents = {p: {r["parent_window_id"] for r in selected if r["advanced_benchmark_partition"] == p}
               for p in ("holdout", "discovery")}
    report["discovery_holdout_parent_overlap"] = sorted(parents["holdout"] & parents["discovery"])
    report["selected_signed_token_deltas"] = dict(Counter(
        r["advanced_adjusted_tokens"] - r["remote_compact_output_tokens"] for r in selected).most_common())
    recall_mismatches = []
    for row in selected:
        facts = row["ground_truth_facts_unique"]
        hits = sum(f in row["advanced_recovery_text"] for f in facts)
        if hits != row["advanced_unique_fact_hits"]:
            recall_mismatches.append(row["example_id"])
    report["independent_unique_fact_hit_mismatches"] = recall_mismatches
    primary = [r for r in experiments if r["experiment_stage"] == "preregistered_holdout_luna"]
    report["fidelity"]["all_primary_luna_candidates"] = fidelity(primary, "extraction_error")
    report["fidelity"]["primary_luna_replicate_zero"] = fidelity([r for r in primary if r["replicate"] == 0], "extraction_error")
    groups = defaultdict(list)
    for r in primary:
        if r.get("extraction_error") is not None and not r.get("refusal") and not r.get("error"):
            groups[r["prefix_sha256"]].append(r)
    primary_bests = [min(rows, key=lambda r: r["extraction_error"]) for rows in groups.values()]
    report["fidelity"]["primary_luna_best_of_10"] = fidelity(primary_bests, "extraction_error")
    report["scaling"] = []
    for lo, hi in ((0,5000),(5000,25000),(25000,100000),(100000,200000),(200000,300000),(300000,400000)):
        rows = [r for r in master if lo <= r["actual_input_tokens"] < hi]
        adv = [r for r in selected if lo <= r["actual_input_tokens"] < hi]
        report["scaling"].append({
            "input_range": [lo, hi], "n": len(rows), "advanced_n": len(adv),
            "median_input_tokens": median(r["actual_input_tokens"] for r in rows),
            "median_compact_tokens": median(r["remote_compact_output_tokens"] for r in rows),
            "median_output_input_ratio": median(r["remote_compact_output_tokens"] / r["actual_input_tokens"] for r in rows),
            "advanced_median_unique_fact_recall": median(r["advanced_unique_fact_recall"] for r in adv),
            "advanced_median_dynamic_fact_recall": median(r["advanced_dynamic_fact_recall"] for r in adv),
            "advanced_median_identifier_support": median(r["advanced_identifier_support"] for r in adv),
        })
    report["saved_controls"] = [r for r in stats if r["analysis_id"] == "controls_and_baselines"]
    report["experiment_stages"] = dict(Counter(r["experiment_stage"] for r in experiments))
    report["preference_splits"] = dict(Counter(r["split"] for r in pq.read_table(RELEASE / "trainer_views" / "compaction_preference_v2.parquet", columns=["split"]).to_pylist()))
    snippets = []
    for row in sorted(selected, key=lambda r: r["actual_input_tokens"])[::10]:
        target = row["advanced_recovery_text"]
        snippets.append({"example_id": row["example_id"], "input_tokens": row["actual_input_tokens"],
                         "target_chars": len(target), "head": target[:1100], "tail": target[-900:]})
    (OUT / "qualitative-samples.json").write_text(json.dumps(snippets, indent=2) + "\n", encoding="utf-8")
    report["examples"] = []
    ordered = sorted(selected, key=lambda r: r["actual_input_tokens"])
    examples = [ordered[0], min(ordered, key=lambda r: abs(r["actual_input_tokens"] - 100000)), ordered[-1]]
    for index, row in enumerate(examples, 1):
        summary = {k: row[k] for k in ("example_id", "parent_window_id", "actual_input_tokens", "input_message_count", "remote_compact_output_tokens", "advanced_adjusted_tokens", "advanced_token_error", "advanced_unique_fact_recall", "advanced_dynamic_fact_recall", "advanced_identifier_support")}
        missing = [f for f in row["ground_truth_facts_unique"] if f not in row["advanced_recovery_text"]]
        summary["missing_sentinel_examples"] = missing[:10]
        report["examples"].append(summary)
        text = f'# Saved example {index}\n\nRecovered text is a model rendering, not verified plaintext.\n\n```json\n{json.dumps(summary, indent=2)}\n```\n\n## Last four source messages\n\n'
        for message in row["input_messages"][-4:]:
            text += f'### {message["role"]}\n\n````text\n{message["content"]}\n````\n\n'
        text += f'## Complete recovered state\n\n````text\n{row["advanced_recovery_text"]}\n````\n'
        (OUT / f"example-{index}.md").write_text(text, encoding="utf-8")
    (OUT / "audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k,v in report.items() if k not in ("saved_controls", "unavailable_original_sources")}, indent=2))


if __name__ == "__main__":
    main()
