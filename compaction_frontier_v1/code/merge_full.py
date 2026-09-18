#!/usr/bin/env python3
"""Merge raw envelopes + recovery into the canonical big dataset.

Joins:
  raw/datapoints-big.jsonl   (input window, gt facts, compaction metadata)
  raw/raw_big.jsonl          (fresh remote /responses/compact capture: FULL
                              compaction_summary item incl. encrypted_content)
  raw/recovery_big.jsonl     (decoder-swap reframe recovery + echo fidelity)

Emits dataset/datapoints_full.jsonl — one row per datapoint with
  .compaction.compaction_items[].encrypted_content  = RAW compaction content
  .recovery  = {best_text, facts_recalled, best_echo_tokens, candidates...}
  .fidelity  = {recovered_tokens(echo), input_tokens_api, ratio}
plus dataset/datapoints_full_summary.json and prints per-size-bin stats.

First-party: synthetic content on the calling account.
"""
import sys, json, os, statistics
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "raw", "datapoints-big.jsonl")
RAW = os.path.join(ROOT, "raw", "raw_big.jsonl")
REC = os.path.join(ROOT, "raw", "recovery_big.jsonl")
OUT = os.path.join(ROOT, "dataset", "datapoints_full.jsonl")
SUMM = os.path.join(ROOT, "dataset", "datapoints_full_summary.json")


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def main():
    dps = load(DP)
    raws = load(RAW)
    recs = load(REC)
    raw_by = {(r["window_id"], r["cutoff_budget_tokens"]): r for r in raws}
    rec_by = {(r["window_id"], r["cutoff_budget_tokens"]): r for r in recs}

    n_raw = n_rec = 0
    out_rows = []
    for dp in dps:
        k = (dp["window_id"], dp["compaction"].get("cutoff_budget_tokens"))
        raw = raw_by.get(k)
        rec = rec_by.get(k)
        if raw:
            n_raw += 1
            dp["compaction"]["raw_items"] = raw["compaction_items"]
            dp["compaction"]["raw_capture"] = {
                "api_in_tokens": raw.get("api_in_tokens"),
                "id_matches_stored": raw.get("id_matches_stored"),
                "stored_enc_len": raw.get("stored_enc_len"),
            }
        if rec:
            n_rec += 1
            dp["recovery"] = {
                "best_text": rec["best_text"],
                "best_len_chars": rec["best_len_chars"],
                "best_prompt_key": rec["best_prompt_key"],
                "best_echo_tokens": rec.get("best_echo_tokens"),
                "n_gt_facts": rec["n_gt_facts"],
                "facts_recalled": rec["facts_recalled"],
                "n_facts_recalled": rec["n_facts_recalled"],
                "candidates": rec["candidates"],
            }
            api_in = dp["compaction"].get("input_tokens_api")
            dp["fidelity"] = {
                "input_tokens_api": api_in,
                "recovered_tokens_echo": rec.get("best_echo_tokens"),
                "ratio_recovered_over_input": (round(rec["best_echo_tokens"] / api_in, 4)
                                               if rec.get("best_echo_tokens") and api_in else None),
                "raw_env_len": len(raw["compaction_items"][0].get("encrypted_content") or "")
                               if raw and raw.get("compaction_items") else None,
            }
        out_rows.append(dp)

    with open(OUT, "w") as f:
        for dp in out_rows:
            f.write(json.dumps(dp, ensure_ascii=False) + "\n")

    # ---- summary ----
    stats = defaultdict(list)
    for dp in out_rows:
        c = dp["compaction"]
        api = c.get("input_tokens_api") or 0
        b = api // 50000 * 50000
        env = (c.get("raw_items") or [{}])[0].get("enc_len")
        rec = dp.get("recovery") or {}
        gt = rec.get("n_gt_facts") or 0
        recalled = rec.get("n_facts_recalled") or 0
        stats[b].append({"api_in": api, "env_len": env,
                         "recall": recalled / gt if gt else None,
                         "echo": rec.get("best_echo_tokens"),
                         "raw_env": env is not None})

    bins = []
    for b in sorted(stats):
        v = stats[b]
        recalls = [x["recall"] for x in v if x["recall"] is not None]
        bins.append({
            "input_bin_tokens": f"{b}-{b+50000}",
            "n": len(v),
            "env_len_median": round(statistics.median([x["env_len"] for x in v if x["env_len"] is not None]), 1),
            "recall_mean": round(statistics.mean(recalls), 3) if recalls else None,
            "recall_median": round(statistics.median(recalls), 3) if recalls else None,
            "ratio_echo_over_input_median": round(statistics.median([x["echo"] / x["api_in"] for x in v if x["echo"] and x["api_in"]]), 4) if any(x["echo"] and x["api_in"] for x in v) else None,
            "with_raw_env": sum(1 for x in v if x["raw_env"]),
        })

    summary = {
        "total_datapoints": len(out_rows),
        "with_raw_envelope": n_raw,
        "with_recovery": n_rec,
        "overall_recall_mean": round(statistics.mean(
            [(dp.get("recovery") or {}).get("n_facts_recalled", 0) /
             max(1, (dp.get("recovery") or {}).get("n_gt_facts", 0))
             for dp in out_rows if dp.get("recovery") and (dp.get("recovery") or {}).get("n_gt_facts")]), 4),
        "size_bins": bins,
    }
    json.dump(summary, open(SUMM, "w"), indent=2)
    print(f"wrote {OUT}: rows={len(out_rows)} raw={n_raw} rec={n_rec}")
    print(f"summary -> {SUMM}")


if __name__ == "__main__":
    main()
