#!/usr/bin/env python3
"""Re-capture the FULL raw compaction content for every datapoint via the remote
/responses/compact/ endpoint, resumable and pooled.

The big generation run retained only {id, enc_len, prefix} per compaction_summary
item. The raw compaction_content (full item incl. encrypted_content) is what the
dataset's contract wants: (entire input context window -> resulting raw compaction
content). We POST each datapoint's input window to the REMOTE /responses/compact/
and keep the complete compaction_summary item(s) + usage.

Compaction is STOCHASTIC: an identical input window recompacted produces a
different item id and envelope length, so re-captured envelopes are fresh valid
instances of the (window -> resulting compaction content) relation, not byte
restorations of the original. id_matches_stored is logged as an informational
stability signal only.

Output: raw/raw_big.jsonl keyed by (window_id, cutoff_budget_tokens).
Env: MODEL, WORKERS, CAP_ROWS, OUT.
First-party: synthetic content on the calling account.
"""
import sys, json, os, time, urllib.request, urllib.error, random, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

HOME = os.path.expanduser("~"); AUTH = os.path.join(HOME, ".codex", "auth.json")
COMPACT_URL = "https://chatgpt.com/backend-api/codex/responses/compact"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "raw", "datapoints-big.jsonl")
OUT = os.path.join(ROOT, "raw", "raw_big.jsonl")


def compact_standalone(model, input_msgs, retries=6, timeout=1800):
    body = json.dumps({"model": model, "input": input_msgs}).encode()
    req = urllib.request.Request(COMPACT_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + json.load(open(AUTH))["tokens"]["access_token"])
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(12 * (attempt + 1) + random.random() * 5)
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read()[:600].decode(errors='replace')}")


def capture_one(model, dp):
    c = dp["compaction"]
    prefix = dp["input_window"]
    try:
        j = compact_standalone(model, prefix)
    except Exception as e:
        return {"key": (dp.get("window_id"), c.get("cutoff_budget_tokens")),
                "error": str(e)[:200]}
    u = j.get("usage") or {}
    summ = [it for it in j.get("output", []) if it.get("type") == "compaction_summary"]
    stored = c["compaction_items"][0] if c["compaction_items"] else None
    cap = {
        "window_id": dp.get("window_id"),
        "cutoff_budget_tokens": c.get("cutoff_budget_tokens"),
        "input_window_sha": dp.get("input_window_sha"),
        "prefix_msgs": len(prefix),
        "api_in_tokens": u.get("input_tokens"),
        "output_tokens": u.get("output_tokens"),
        "n_compaction_items": len(summ),
        "compaction_items": [{"id": it.get("id"),
                              "enc_len": len(it.get("encrypted_content") or ""),
                              "encrypted_content": it.get("encrypted_content") or ""}
                             for it in summ],
    }
    if stored and summ:
        cap["id_matches_stored"] = (summ[0].get("id") == stored.get("id"))
    elif stored:
        cap["id_matches_stored"] = False
    cap["stored_enc_len"] = stored.get("enc_len") if stored else None
    return {"key": (dp.get("window_id"), c.get("cutoff_budget_tokens")), "cap": cap}


def main():
    model = os.environ.get("MODEL", "gpt-5.6-luna")
    workers = int(os.environ.get("WORKERS", "8"))
    cap_rows = int(os.environ.get("CAP_ROWS", "0"))
    out_path = os.environ.get("OUT", OUT)

    rows = [json.loads(l) for l in open(SRC) if l.strip()]
    existing = {}
    if os.path.exists(out_path):
        for l in open(out_path):
            try:
                r = json.loads(l)
                existing[(r["window_id"], r["cutoff_budget_tokens"])] = r
            except Exception:
                pass
    todo = [dp for dp in rows
            if (dp.get("window_id"), dp["compaction"].get("cutoff_budget_tokens")) not in existing]
    if cap_rows > 0:
        todo = todo[:cap_rows]
    print(f"[raw] total={len(rows)} done={len(existing)} todo={len(todo)} "
          f"model={model} workers={workers}", flush=True)

    lock = threading.Lock()
    n_done = [0]
    mism = [0]
    t0 = time.time()

    def work(dp):
        res = capture_one(model, dp)
        if res.get("error"):
            return res
        with lock:
            with open(out_path, "a") as f:
                f.write(json.dumps(res["cap"], ensure_ascii=False) + "\n")
            if res["cap"].get("id_matches_stored") is False:
                mism[0] += 1
            n_done[0] += 1
            if n_done[0] % 50 == 0:
                print(f"[raw] {n_done[0]}/{len(todo)} id_mismatch={mism[0]} "
                      f"elapsed={int(time.time()-t0)}s", flush=True)
        return res

    errs = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(work, dp): dp for dp in todo}
        for fut in as_completed(futs):
            try:
                fut.result()
            except Exception as e:
                errs.append((futs[fut].get("window_id"), str(e)[:120]))

    print(f"[raw] DONE new={n_done[0]} total={len(existing)+n_done[0]} "
          f"id_mismatches={mism[0]} errors={len(errs)} "
          f"elapsed={int(time.time()-t0)}s -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
