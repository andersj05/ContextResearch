#!/usr/bin/env python3
"""Assemble the large-scale datapoint JSONL into a clean dataset + summary.

Reads raw/datapoints-big.jsonl (produced by scale_run.py) and emits:
  - dataset/datapoints_big.jsonl  (canonical, without duplicate window text)
  - dataset/datapoints_big_summary.json  (table of api_in / env_len / cutoff / facts)
  - analysis tables: envelope-length vs input-size scaling, per-window coverage
"""
import json, os, sys, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "raw", "datapoints-big.jsonl")
OUT = os.path.join(ROOT, "dataset", "datapoints_big.jsonl")
SUMM = os.path.join(ROOT, "dataset", "datapoints_big_summary.json")


def main():
    rows = []
    if not os.path.exists(SRC):
        print("no source yet:", SRC); return
    for l in open(SRC):
        l = l.strip()
        if not l:
            continue
        try:
            dp = json.loads(l)
        except Exception:
            continue
        c = dp["compaction"]
        items = c.get("compaction_items", [])
        rows.append({
            "window_id": dp.get("window_id"),
            "input_window_sha": dp.get("input_window_sha"),
            "cutoff_budget": c.get("cutoff_budget_tokens"),
            "api_in_tokens": c.get("input_tokens_api"),
            "api_out_tokens": c.get("output_tokens"),
            "prefix_msgs": c.get("prefix_msgs"),
            "envelope_len": items[0]["enc_len"] if items else None,
            "envelope_prefix": items[0]["prefix"] if items else None,
            "n_facts_in_prefix": len(dp.get("ground_truth_facts", [])),
            "full": dp,
        })

    if not rows:
        print("no rows"); return

    with open(OUT, "w") as f:
        for r in rows:
            f.write(json.dumps(r["full"], ensure_ascii=False) + "\n")

    # summary table
    table = []
    for r in rows:
        table.append({
            "window_id": r["window_id"],
            "cutoff_budget": r["cutoff_budget"],
            "api_in_tokens": r["api_in_tokens"],
            "envelope_len": r["envelope_len"],
            "prefix_msgs": r["prefix_msgs"],
            "n_facts_in_prefix": r["n_facts_in_prefix"],
            "ratio_env_over_input": round(r["envelope_len"] / r["api_in_tokens"], 4) if r["api_in_tokens"] else None,
        })

    # scaling analysis: bucket by api_in
    buckets = {}
    for r in rows:
        ai = r["api_in_tokens"] or 0
        b = int(ai) // 25000 * 25000
        buckets.setdefault(b, []).append(r["envelope_len"] or 0)
    scaling = []
    for b in sorted(buckets):
        envs = buckets[b]
        scaling.append({
            "input_bucket": f"{b}-{b+25000}",
            "n": len(envs),
            "env_len_min": min(envs), "env_len_max": max(envs),
            "env_len_median": round(statistics.median(envs), 1),
        })

    summary = {
        "total_datapoints": len(rows),
        "n_windows": len({r["window_id"] for r in rows}),
        "api_in_total_tokens": sum(r["api_in_tokens"] or 0 for r in rows),
        "envelope_len_sum": sum(r["envelope_len"] or 0 for r in rows),
        "input_size_bins": scaling,
        "table": table,
    }
    json.dump(summary, open(SUMM, "w"), indent=2)
    print(f"rows={len(rows)} windows={summary['n_windows']} "
          f"api_in_total={summary['api_in_total_tokens']} -> {OUT}")


if __name__ == "__main__":
    main()
