#!/usr/bin/env python3
"""Thin client for the ChatGPT-backed codex /responses surface.

Uses the user's own ChatGPT OAuth access token from ~/.codex/auth.json.
Streams SSE events, records items (incl. compaction items) and usage.
First-party: only the calling account's own conversations.
"""
import json, os, sys, time, urllib.request, urllib.error, argparse, gzip, re

HOME = os.path.expanduser('~')
AUTH = os.path.join(HOME, '.codex', 'auth.json')
URL = "https://chatgpt.com/backend-api/codex/responses"


def load_token():
    d = json.load(open(AUTH))
    return d['tokens']['access_token']


def post_stream(body: dict, timeout=600):
    token = load_token()
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "text/event-stream")
    req.add_header("Accept-Encoding", "gzip")
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:1000].decode(errors='replace')}")


def event_iter(resp):
    """Yield parsed SSE events; each is a dict {event, data}."""
    buf = b""
    for chunk in iter(lambda: resp.read(65536), b""):
        buf += chunk
        while b"\n\n" in buf:
            raw, buf = buf.split(b"\n\n", 1)
            event = "{type:json}"
            data_lines = []
            for line in raw.split(b"\n"):
                if line.startswith(b"event: "):
                    event = line[7:].decode(errors="replace")
                elif line.startswith(b"data:"):
                    data_lines.append(line[5:].strip())
            if data_lines:
                yield {"event": event, "data": "\n".join(x.decode(errors="replace") for x in data_lines)}


def collect_response(body, save_raw=None, verbose=False, timeout=600):
    """Run a full streaming response, aggregate output items + usage.

    Merges output_text.delta / reasoning summary deltas into items so message
    content is complete (the response.output_item.added skeleton excludes text).
    """
    items = []          # all output items in order
    usage = None
    status = None
    errors = []
    events = []
    by_id = {}
    for ev in event_iter(post_stream(body, timeout=timeout)):
        events.append(ev)
        try:
            data = json.loads(ev["data"])
        except Exception:
            continue
        et = data.get("type")
        if et == "response.output_item.added":
            it = data.get("item", {})
            items.append(it)
            by_id[it.get("id")] = it
        elif et == "response.output_item.done":
            pass
        elif et == "response.output_text.delta":
            it = by_id.get(data.get("item_id"))
            if it is not None:
                delta = data.get("delta") or ""
                # find/create output_text part
                parts = [p for p in it.setdefault("content", []) if p.get("type") == "output_text"]
                if parts:
                    parts[0]["text"] = (parts[0].get("text") or "") + delta
                else:
                    it["content"].append({"type": "output_text", "text": delta})
        elif et == "response.reasoning_summary_text.delta":
            it = by_id.get(data.get("item_id"))
            if it is not None:
                delta = data.get("delta") or ""
                parts = [p for p in it.setdefault("content", []) if p.get("type") == "summary_text"]
                if parts:
                    parts[0]["text"] = (parts[0].get("text") or "") + delta
                else:
                    it["content"].append({"type": "summary_text", "text": delta})
        elif et == "response.completed":
            usage = data.get("response", {}).get("usage", usage) or data.get("usage")
        elif et == "error":
            errors.append(data.get("error", data))
        elif et == "response.failed":
            status = "failed"
        elif et == "response.in_progress":
            status = "in_progress"
    if save_raw:
        with open(save_raw, "w") as f:
            for ev in events:
                f.write(ev["event"] + "\n" + ev["data"] + "\n\n")
    return {"items": items, "usage": usage, "status": status, "errors": errors, "events": events}


def summarize_items(items):
    out = []
    for it in items:
        t = it.get("type")
        row = {"type": t, "id": it.get("id")}
        if t == "compaction":
            row["token_count"] = it.get("token_count")
            row["keys"] = list(it.keys())
            row["has_encrypted_content"] = bool(it.get("encrypted_content"))
            row["encrypted_content_len"] = len(it.get("encrypted_content") or "")
            row["encrypted_content_head"] = (it.get("encrypted_content") or "")[:80]
        elif t == "message":
            content = it.get("content", [])
            texts = [c.get("text", "") for c in content if c.get("type") == "output_text"]
            row["text_head"] = (texts[0][:160] if texts else None)
            row["text_len"] = sum(len(t) for t in texts)
            row["role"] = it.get("role")
        elif t == "reasoning":
            row["summary_len"] = len(it.get("summary", []))
            row["has_encrypted_summary"] = bool(it.get("encrypted_content") or it.get("summary_mask")) \
                if isinstance(it.get("encrypted_content"), str) else False
            keys = set(it.keys())
            row["keys"] = sorted(keys)
        else:
            row["keys"] = sorted(it.keys())
        out.append(row)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--reasoning", default="low")
    ap.add_argument("--max-output-tokens", type=int, default=256)
    ap.add_argument("--compact-threshold", type=int, default=None,
                    help="if set, add context_management compaction with this threshold")
    ap.add_argument("--save-raw", default=None)
    ap.add_argument("--input-json", default=None, help="file containing input items JSON array")
    ap.add_argument("--prompt", default=None)
    args = ap.parse_args()

    if args.input_json:
        input_items = json.load(open(args.input_json))
    else:
        input_items = [{"role": "user", "content": args.prompt or "Say OK"}]

    body = {
        "model": args.model,
        "input": input_items,
        "store": False,
        "stream": True,
        "reasoning": {"effort": args.reasoning},
    }
    if args.compact_threshold is not None:
        body["context_management"] = [{"type": "compaction", "compact_threshold": args.compact_threshold}]

    res = collect_response(body, save_raw=args.save_raw)
    print("STATUS:", res["status"], "errors:", res["errors"][:3])
    print("USAGE:", json.dumps(res["usage"], indent=1) if res["usage"] else None)
    print("ITEMS:")
    for row in summarize_items(res["items"]):
        print(" -", json.dumps(row)[:400])
