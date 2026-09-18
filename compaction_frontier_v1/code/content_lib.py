#!/usr/bin/env python3
"""Content-type library: deterministic synthetic content blocks, each tagged
with a type and carrying sentinel facts (identifiers, hex, endpoints, flags)
so recovery fidelity is measurable. NO real secrets/PII anywhere.

Each generator returns (conversation_msgs, facts, meta) where
conversation_msgs is a list of {role, content} building the input window.
"""
import json, hashlib, random
from dataclasses import dataclass, field

FACT_POOL = {
    "code": ["0x3f8e91ab7c42d605", "MERGE-MANIFEST-88", "gen_stamp_0xA1B2C3", "cold.tier.backend:8443"],
    "math": ["phi=1.618033", "m+n+p=193", "L=7*sqrt(3)", "det=4.2e-7"],
    "json": ["QLARK-SEG-001", "0x9f33c12b8a4de071", "ring:3", "ttl=window=morn"],
    "logs": ["TRACE-7f9a2bc4", "0xdeadbeef", "drainer.wave=512", "mirror:ACK:8"],
    "dialogue": ["AURORA-SEGMENT-001", "skyhook.mirror.gateway:9229", "VLFN-CLOCK-88423", "CIPHER-ROT13-BLOOM-77"],
    "search": ["rosebud.saltness.cairn:4410", "KX-ACCOUNT-HASH=0x7f9a", "nearest.neighbor=42", "query:alpha.09"],
}

def _salt(seed, block):
    h = hashlib.sha256(f"{seed}:{block}".encode()).hexdigest()
    return ("SALT-" + h[:8] + "-" + h[24:32]).upper()


def gen_code(seed, n_blocks=3, scale=1):
    msgs, facts, meta = [], [], []
    for i in range(n_blocks):
        f1 = FACT_POOL["code"][i % 4]
        f2 = _salt(seed, f"code-{i}")
        code = "\n".join([
            f"def reconcile_{i}(rows, wave={512 * scale}):",
            f"    # {f1}: chained SHA-256 over prior digest",
            f'    salt = "{f2}"',
            "    ledger = [{'r': r, 'h': __import__('hashlib').sha256(str(r).encode()).hexdigest()[:16]} for r in range(min(len(rows) if rows else 0, 4))]",
            "    for row in (rows or []):",
            "        if getattr(row, 'tombstoned', False):",
            f'            row.backfill(sentinel=True, flag="{f1}")',
            "    return ledger",
        ])
        msgs.append({"role": "user", "content": f"Code block {i} (tooling):\n{code}"})
        msgs.append({"role": "assistant", "content": f"Compiled block {i}; flag {f1} noted."})
        facts += [f1, f2]
        meta.append({"type": "code", "block": i})
    return msgs, facts, meta


def gen_math(seed, n_blocks=2, scale=1):
    msgs, facts, meta = [], [], []
    for i in range(n_blocks):
        f1 = FACT_POOL["math"][i % 4]
        f2 = _salt(seed, f"math-{i}")
        msgs.append({"role": "user", "content": (
            f"Math block {i}: show that for the integral I = int_0^1 x e^(-x^2) dx, "
            f"I = (1 - e^{-1})/2 exactly, and derive the constant {f1} in the expansion. "
            f"Tag your derivation with {f2}.")})
        msgs.append({"role": "assistant", "content": f"Derivation {i} complete. Constant {f1}; tag {f2}."})
        facts += [f1, f2]
        meta.append({"type": "math", "block": i})
    return msgs, facts, meta


def gen_json(seed, n_blocks=2, scale=1):
    msgs, facts, meta = [], [], []
    for i in range(n_blocks):
        f1 = FACT_POOL["json"][i % 4]
        f2 = _salt(seed, f"json-{i}")
        doc = {
            "config": f1,
            "ring": 3, "flag": f2,
            "leases": [{"k": k, "salt": _salt(seed, f"json-{i}-k{k}")} for k in range(6)],
        }
        msgs.append({"role": "user", "content": f"Config document {i}:\n{json.dumps(doc, indent=2)}"})
        msgs.append({"role": "assistant", "content": f"Config {i} validated; key {f1}."})
        facts += [f1, f2]
        meta.append({"type": "json", "block": i})
    return msgs, facts, meta


def gen_logs(seed, n_blocks=2, scale=1):
    msgs, facts, meta = [], [], []
    for i in range(n_blocks):
        f1 = FACT_POOL["logs"][i % 4]
        f2 = _salt(seed, f"logs-{i}")
        lines = [f"t={j*10}ms trace={f1} wave={512*scale} {f2} status=ok" for j in range(8)]
        msgs.append({"role": "user", "content": f"Log block {i}:\n" + "\n".join(lines)})
        msgs.append({"role": "assistant", "content": f"Logs {i} parsed; trace {f1} flagged {f2}."})
        facts += [f1, f2]
        meta.append({"type": "logs", "block": i})
    return msgs, facts, meta


def gen_dialogue(seed, n_blocks=2, scale=1):
    msgs, facts, meta = [], [], []
    for i in range(n_blocks):
        f1 = FACT_POOL["dialogue"][i % 4]
        f2 = _salt(seed, f"dlg-{i}")
        msgs.append({"role": "user", "content": f"Dialogue user {i}: note the fact {f1} and the reserved flag {f2}."})
        msgs.append({"role": "assistant", "content": f"Noted {f1} and {f2}."})
        facts += [f1, f2]
        meta.append({"type": "dialogue", "block": i})
    return msgs, facts, meta


def gen_search(seed, n_blocks=2, scale=1):
    msgs, facts, meta = [], [], []
    for i in range(n_blocks):
        f1 = FACT_POOL["search"][i % 4]
        f2 = _salt(seed, f"sea-{i}")
        msgs.append({"role": "user", "content": f"Search task {i}: retrieve records matching {f1}; bind {f2} as the result key."})
        msgs.append({"role": "assistant", "content": f"Result {i}: {f1} -> {f2}"})
        facts += [f1, f2]
        meta.append({"type": "search", "block": i})
    return msgs, facts, meta


GEN = {
    "code": gen_code, "math": gen_math, "json": gen_json,
    "logs": gen_logs, "dialogue": gen_dialogue, "search": gen_search,
}


def build_window(kinds, seed="seed42", blocks_each=2, scale=1, order_locked=True):
    """Compose a conversation from a list of content kinds. Returns
    (msgs, all_facts, block_meta) where block_meta has a tokens_approx per block."""
    msgs, all_facts, meta = [], [], []
    rnd = random.Random(seed)
    order = kinds if order_locked else rnd.sample(kinds, len(kinds))
    block_idx = 0
    for kind in order:
        blk_msgs, blk_facts, blk_meta = GEN[kind](seed, n_blocks=blocks_each, scale=scale)
        for bm, b_cont in zip(blk_meta, blk_msgs):
            bm["msg_index"] = len(msgs)
            bm["end_msg_index"] = len(msgs) + (len(blk_msgs) - 1)
            bm["tokens_approx"] = len(b_cont["content"]) // 4
        msgs.extend(blk_msgs)
        all_facts.extend(blk_facts)
        # mark block boundaries by kind
        for bm in blk_meta:
            bm["kind"] = kind
            bm["block_id"] = block_idx
            meta.append(bm)
        block_idx += 1
    return msgs, list(dict.fromkeys(all_facts)), meta


def window_tokens_accounting(msgs, kind="chars4"):
    if kind == "chars4":
        return sum(len(m["content"]) for m in msgs) // 4
    return len(msgs)
