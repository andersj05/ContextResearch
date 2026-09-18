#!/usr/bin/env python3
"""Scale compaction datapoints up to model context limits.

Design:
  * Diverse-content large windows: mix content_kind segments (code/math/json/logs/
    dialogue/search), each with sentinel facts, until a target character budget.
    Content is deterministic per (seed, segment) so regeneration is reproducible.
  * Cutoff engine: one big window yields MANY datapoints by compacting prefixes at
    increasing token cutoffs — each cutoff is its own (input prefix, compaction
    content) pair.
  * Worker pool (ThreadPool) with retry/backoff for 429/5xx.
  * Token-spend tracking: every call records usage.input_tokens so total cost is
    measured, not guessed.

First-party only: synthetic content on the calling account.
"""
import sys, json, os, time, hashlib, urllib.request, urllib.error, random
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_lib import GEN, _salt

HOME = os.path.expanduser("~"); AUTH = os.path.join(HOME, ".codex", "auth.json")
COMPACT_URL = "https://chatgpt.com/backend-api/codex/responses/compact"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Measured chars/token for this mixed content: ~2.23 (verified 160k chars -> 71,619 API tokens)
CHARS_PER_TOKEN = 2.23

def build_diverse_window(target_tokens, seed="seed42", kinds=("code","math","json","logs","dialogue","search"),
                         chunk_tokens=900):
    """Build a diverse conversation up to ~target_tokens REAL API tokens (ratio
    CHARS_PER_TOKEN). Common tokens include the roles/content markup; the ratio
    is calibrated empirically on this account. Returns (conv, facts, chunk_meta)."""
    conv = []
    facts = []
    chunk_meta = []
    acc_chars = 0
    target_chars = target_tokens * CHARS_PER_TOKEN
    seg = 0
    rnd = random.Random(seed + "-big")
    while acc_chars < target_chars:
        kind = kinds[seg % len(kinds)]
        blk_msgs, blk_facts, _ = GEN[kind](f"{seed}-big-{seg}", n_blocks=2, scale=rnd.randint(1, 3))
        new_chars = sum(len(m["content"]) for m in blk_msgs)
        acc_chars += new_chars
        start = len(conv)
        conv.extend(blk_msgs)
        facts.extend(blk_facts)
        chunk_meta.append({"start_msg": start, "kind": kind, "seg": seg,
                           "chars": new_chars, "facts": blk_facts})
        seg += 1
    return conv, facts, chunk_meta


def compact_standalone(model, input_msgs, retries=5):
    body = json.dumps({"model": model, "input": input_msgs}).encode()
    req = urllib.request.Request(COMPACT_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + json.load(open(AUTH))["tokens"]["access_token"])
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(12 * (attempt + 1) + random.random() * 5)
                continue
            raise


def prefix_up_to(conv, budget_tokens, char_per_tok=CHARS_PER_TOKEN):
    out = []
    acc = 0
    for m in conv:
        mc = len(m["content"])
        acc += mc / char_per_tok
        if acc > budget_tokens and out:
            break
        out.append(m)
    return out if out else conv[:1]


def make_datapoint(model, conv, prefix, facts_all, budget, window_id, tag):
    j = compact_standalone(model, prefix)
    summ = [it for it in j.get("output", []) if it.get("type") == "compaction_summary"]
    u = j.get("usage") or {}
    in_tok = u.get("input_tokens")
    rec = {
        "kind": "standalone_cutoff", "producer_model": model,
        "window_id": window_id, "cutoff_budget_tokens": budget,
        "prefix_msgs": len(prefix),
        "input_tokens_api": in_tok, "output_tokens": u.get("output_tokens"),
        "n_compaction_items": len(summ),
        "compaction_items": [{"id": it["id"], "enc_len": len(it.get("encrypted_content") or ""),
                              "prefix": (it.get("encrypted_content") or "")[:12]} for it in summ],
    }
    # facts that actually sit inside this prefix
    prefix_text = "\n".join(m["content"] for m in prefix)
    prefix_facts = [f for f in facts_all if f in prefix_text]
    dp = {"input_window": prefix, "window_id": window_id,
          "input_window_sha": hashlib.sha256(json.dumps(prefix, sort_keys=True).encode()).hexdigest()[:16],
          "ground_truth_facts": prefix_facts,
          "compaction": rec}
    return dp, in_tok


def run_window(model, target_tokens, seed, cutoffs, tag, out_path, window_id=None):
    conv, facts, meta = build_diverse_window(target_tokens, seed=seed)
    window_id = window_id or f"{tag}-{seed}-{target_tokens//1000}k"
    print(f"[{tag}] window {window_id} msgs={len(conv)} approx_tok={sum(len(m['content']) for m in conv)//4} "
          f"facts={len(facts)}", flush=True)
    spend = 0
    n = 0
    for budget in cutoffs:
        prefix = prefix_up_to(conv, budget)
        try:
            dp, in_tok = make_datapoint(model, conv, prefix, facts, budget, window_id, tag)
            with open(out_path, "a") as f:
                f.write(json.dumps(dp) + "\n")
            spend += (in_tok or 0)
            n += 1
            enc = dp["compaction"]["compaction_items"][0]["enc_len"] if dp["compaction"]["compaction_items"] else 0
            print(f"[{tag}]   cutoff {budget:>6} api_in={in_tok} env_len={enc} "
                  f"prefix_facts={len(dp['ground_truth_facts'])}", flush=True)
        except Exception as e:
            print(f"[{tag}]   cutoff {budget} ERR {str(e)[:200]}", flush=True)
            time.sleep(5)
    return {"window_id": window_id, "datapoints": n, "spend_tokens": spend}


import concurrent.futures

def _run_window_task(model, target, seed, cutoffs, tag, out_path):
    return run_window(model, target, seed, cutoffs, tag, out_path)

def main():
    model = os.environ.get("MODEL", "gpt-5.6-luna")
    tag = os.environ.get("TAG", "scale")
    out_path = os.environ.get("OUT", os.path.join(ROOT, "raw", "datapoints-big.jsonl"))
    targets = [int(t) for t in os.environ.get("TARGETS", "20000,100000,200000").split(",") if t.strip()]
    seeds = [s for s in os.environ.get("SEEDS", "seed42").split(",") if s.strip()]
    cutoff_pct = [int(p) for p in os.environ.get("CUTOFF_PCT", "10,25,50,75,100").split(",") if p.strip()]
    workers = int(os.environ.get("WORKERS", "4"))
    cap_tokens = int(os.environ.get("CAP_TOKENS", "0") or "0")  # 0 = unlimited
    cutoffs_override = [int(t) for t in os.environ.get("CUTOFFS", "").split(",") if t.strip()]

    # resume support: load existing dp hashes
    seen = set()
    if os.path.exists(out_path):
        for l in open(out_path):
            l=l.strip()
            if l:
                try: seen.add(json.loads(l)["input_window_sha"])
                except Exception: pass

    total_spend = 0
    total_dp = 0
    rows = []
    tasks = []
    for target in targets:
        for seed in seeds:
            if cutoffs_override:
                cutoffs = [max(500, c) for c in cutoffs_override]
            else:
                cutoffs = [max(500, target * p // 100) for p in cutoff_pct]
            cutoffs = sorted(set(cutoffs))
            tasks.append((model, target, seed, cutoffs, tag, out_path))

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_run_window_task, *t): t for t in tasks}
        for fut in concurrent.futures.as_completed(futs):
            try:
                r = fut.result()
                rows.append(r)
                total_spend += r["spend_tokens"]
                total_dp += r["datapoints"]
                print(f"[{tag}] {r['window_id']} dps={r['datapoints']} spend={r['spend_tokens']} "
                      f"cum_dp={total_dp} cum_tok={total_spend}", flush=True)
            except Exception as e:
                print(f"[{tag}] task ERR {e}", flush=True)
            if cap_tokens and total_spend >= cap_tokens:
                print(f"[{tag}] TOKEN CAP REACHED {total_spend}/{cap_tokens} — stopping", flush=True)
                for f in futs:
                    f.cancel()
                break
    print(f"[{tag}] SUMMARY datapoints={total_dp} total_input_tokens={total_spend}", flush=True)
    json.dump(rows, open(os.path.join(ROOT, "raw", f"spend_{tag}.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
