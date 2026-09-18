#!/usr/bin/env python3
"""Drive the full-scale datapoint generation: size grid x seeds until >= TARGET_DPS
datapoints are written, resumable, bounded by CAP_TOKENS and MAX_WINDOWS.

Each window contributes DATAPOINTS per cutoff on its prefixes (one datapoint per
cutoff = its own (input prefix, resulting compaction) pair). Windows are built
deterministically; cutoffs at increasing fractions cover 10%..100% of the window.

Progress is printed per window; run supervised via hub. On interruption, re-running
continues (input_window_sha dedupe) and pads remaining size/seed cells.

First-party: synthetic content, calling account, codex/chatgpt plan auth via omp.
"""
import sys, os, json, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from big_scale import run_window

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "raw", "datapoints-big.jsonl")
SPEND_LOG = os.path.join(ROOT, "raw", "scale_progress.json")

# Size grid (real API tokens) -> seed count. First run: existing grid below produces
# ~1568; supplemental is launched with SUPPLEMENT=1 to add cheaper volume + extra tops.
BASE_GRID = [
    (5000,    60),
    (10000,   50),
    (25000,   40),
    (50000,   30),
    (100000,  22),
    (200000,  12),
    (300000,   6),
    (400000,   4),
]
SUPP_GRID = [
    (5000,    200),   # cheapest volume
    (10000,   120),
    (25000,    60),
    (100000,   16),
    (200000,   10),
    (400000,    6),
]
GRID = SUPP_GRID if os.environ.get("SUPPLEMENT") == "1" else BASE_GRID
CUTOFF_PCT = [10, 25, 40, 55, 70, 85, 100]
TARGET_DPS = int(os.environ.get("TARGET_DPS", "2000"))
CAP_TOKENS = int(os.environ.get("CAP_TOKENS", "600000000"))   # 600M input tokens ceiling
MAX_WINDOWS = int(os.environ.get("MAX_WINDOWS", "0"))


def seed_for(size, i):
    off = 0 if os.environ.get("SUPPLEMENT") != "1" else 1000
    return f"g{size}-s{i+off}"


def existing_hashes(out):
    seen = set()
    if os.path.exists(out):
        for l in open(out):
            l = l.strip()
            if l:
                try:
                    seen.add(json.loads(l)["input_window_sha"])
                except Exception:
                    pass
    return seen


import concurrent.futures
from threading import Lock

def main():
    model = os.environ.get("MODEL", "gpt-5.6-luna")
    tag = os.environ.get("TAG", "scale")
    workers = int(os.environ.get("WORKERS", "6"))
    seen = existing_hashes(OUT)
    total_dp = len(seen)
    total_spend = 0
    if os.path.exists(SPEND_LOG):
        try:
            total_spend = json.load(open(SPEND_LOG)).get("total_tokens", 0)
        except Exception:
            pass
    lock = Lock()
    started = time.time()

    print(f"[{tag}] model={model} TARGET_DPS={TARGET_DPS} CAP_TOKENS={CAP_TOKENS} "
          f"workers={workers} existing_dps={total_dp} existing_spend={total_spend}", flush=True)

    # Build the full task list up front (size, seed)
    tasks = []
    for size, n_seeds in GRID:
        for i in range(n_seeds):
            tasks.append((size, seed_for(size, i)))

    def work(t):
        size, seed = t
        cutoffs = sorted(set(max(500, size * p // 100) for p in CUTOFF_PCT))
        try:
            r = run_window(model, size, seed, cutoffs, tag, OUT, window_id=f"{size}-{seed}")
            return r
        except Exception as e:
            print(f"[{tag}] window {size}/{seed} ERR {str(e)[:160]}", flush=True)
            time.sleep(5)
            return {"window_id": f"{size}-{seed}", "datapoints": 0, "spend_tokens": 0}

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(work, t): t for t in tasks}
        for fut in concurrent.futures.as_completed(futs):
            r = fut.result()
            with lock:
                total_dp += r["datapoints"]
                total_spend += r["spend_tokens"]
                json.dump({"total_tokens": total_spend, "total_dps": total_dp,
                           "last_window": r["window_id"],
                           "elapsed_s": round(time.time() - started)},
                          open(SPEND_LOG, "w"))
                print(f"[{tag}] {r['window_id']} dps={r['datapoints']} spend={r['spend_tokens']} "
                      f"cum_dp={total_dp} cum_tok={total_spend} "
                      f"elapsed={round(time.time()-started)}s", flush=True)
                if total_dp >= TARGET_DPS:
                    print(f"[{tag}] TARGET_DPS reached ({total_dp})", flush=True)
                    for f in futs:
                        f.cancel()
                    break
                if CAP_TOKENS and total_spend >= CAP_TOKENS:
                    print(f"[{tag}] CAP_TOKENS reached ({total_spend})", flush=True)
                    for f in futs:
                        f.cancel()
                    break

    print(f"[{tag}] DONE total_dp={total_dp} total_tokens={total_spend} "
          f"elapsed={round(time.time()-started)}s", flush=True)


if __name__ == "__main__":
    main()
