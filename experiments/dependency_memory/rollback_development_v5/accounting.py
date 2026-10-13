"""Atomic central admission for concurrent calls; unknown dispatch stops new work."""
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
import json
import sqlite3
import threading

from .common import now, sha, wire, save_new
from ..rollback_pilot.subscription.accounting import Usage, RESERVATION


class Stopped(RuntimeError):
    pass


@dataclass(frozen=True)
class Identity:
    study: str
    task_id: str
    track: str
    arm: str
    step: int
    stage: str

    @property
    def key(self):
        return sha(asdict(self))


class Ledger:
    def __init__(self, path, identities, max_inflight):
        self.path = Path(path)
        self.identities = {i.key: asdict(i) for i in identities}
        if len(self.identities) != len(identities):
            raise ValueError("duplicate frozen identity")
        self.max_inflight = max_inflight
        self.lock = threading.RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS calls(id TEXT PRIMARY KEY, identity TEXT, request_hash TEXT, state TEXT, payload TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, call_id TEXT, state TEXT, payload TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS config(id INTEGER PRIMARY KEY, payload TEXT)")
            config = wire({"identities": sha(self.identities), "max_inflight": max_inflight})
            db.execute("INSERT OR IGNORE INTO config VALUES(1,?)", (config,))
            if db.execute("SELECT payload FROM config WHERE id=1").fetchone()[0] != config:
                raise ValueError("ledger configuration changed")
            db.execute("CREATE TABLE IF NOT EXISTS stops(id INTEGER PRIMARY KEY, reason TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS threads(thread_id TEXT PRIMARY KEY, call_id TEXT UNIQUE)")
            if db.execute("SELECT 1 FROM calls LIMIT 1").fetchone():
                raise ValueError("an existing dispatched ledger cannot be reopened for execution")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.execute("PRAGMA synchronous=FULL")
        try:
            with db:
                yield db
        finally:
            db.close()

    def stopped(self):
        with self.connect() as db:
            return db.execute("SELECT reason FROM stops LIMIT 1").fetchone() is not None

    def stop(self, reason):
        with self.lock, self.connect() as db:
            db.execute("INSERT OR IGNORE INTO stops VALUES(1,?)", (reason,))

    def admit(self, identity, request_hash):
        key = identity.key
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if key not in self.identities or self.identities[key] != asdict(identity):
                raise ValueError("identity not frozen")
            if db.execute("SELECT 1 FROM stops LIMIT 1").fetchone():
                raise Stopped("global_stop")
            if db.execute("SELECT 1 FROM calls WHERE id=?", (key,)).fetchone():
                raise ValueError("never replay a call identity")
            if db.execute("SELECT COUNT(*) FROM calls WHERE state='dispatched'").fetchone()[0] >= self.max_inflight:
                raise ValueError("global concurrency bound exceeded")
            payload = wire({"admitted_utc": now(), "reserve_credits": str(RESERVATION)})
            db.execute("INSERT INTO calls VALUES(?,?,?,?,?)", (key, wire(asdict(identity)), request_hash, "dispatched", payload))
            db.execute("INSERT INTO events(call_id,state,payload) VALUES(?,?,?)", (key, "dispatched", payload))

    def complete(self, identity, usage, metadata, elapsed):
        if type(usage) is not Usage:
            raise ValueError("missing usage")
        usage.validate()
        if usage.cost > RESERVATION:
            raise ValueError("reservation exceeded")
        payload = {"usage": vars(usage), "planning_credits": str(usage.cost), "elapsed_seconds": elapsed,
                   "metadata": metadata, "completed_utc": now()}
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT state FROM calls WHERE id=?", (identity.key,)).fetchone()
            if row != ("dispatched",):
                raise ValueError("completion requires one admitted identity")
            # Real transports must not reuse provider threads between calls.
            thread = metadata.get("thread_id")
            if type(thread) is not str or not thread:
                raise ValueError("provider thread identity required")
            try:
                db.execute("INSERT INTO threads VALUES(?,?)", (thread, identity.key))
            except sqlite3.IntegrityError:
                raise ValueError("provider thread reused") from None
            db.execute("UPDATE calls SET state='completed',payload=? WHERE id=?", (wire(payload), identity.key))
            db.execute("INSERT INTO events(call_id,state,payload) VALUES(?,?,?)", (identity.key, "completed", wire(payload)))

    def unknown(self, identity, reason):
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            payload = wire({"reason": reason, "reserve_credits": str(RESERVATION), "observed_utc": now()})
            row = db.execute("SELECT state FROM calls WHERE id=?", (identity.key,)).fetchone()
            if row != ("dispatched",):
                raise ValueError("unknown requires an admitted identity")
            db.execute("UPDATE calls SET state='unknown',payload=? WHERE id=?", (payload, identity.key))
            db.execute("INSERT INTO events(call_id,state,payload) VALUES(?,?,?)", (identity.key, "unknown", payload))
            db.execute("INSERT OR IGNORE INTO stops VALUES(1,?)", ("unknown_dispatch",))

    def snapshot(self):
        with self.connect() as db:
            rows = [{"call_id": k, "identity": json.loads(i), "request_hash": h, "state": s, **json.loads(p)}
                    for k, i, h, s, p in db.execute("SELECT * FROM calls ORDER BY id")]
            stop = db.execute("SELECT reason FROM stops LIMIT 1").fetchone()
        completed = [r for r in rows if r["state"] == "completed"]
        pending = [r for r in rows if r["state"] in {"unknown", "dispatched"}]
        return {"calls": rows, "completed_calls": len(completed), "unknown_or_inflight_calls": len(pending),
                "planning_credits": str(sum((Decimal(r["planning_credits"]) for r in completed), Decimal(0))),
                "locked_planning_credits": str(len(pending) * RESERVATION), "stop": stop[0] if stop else None,
                "usage": {k: sum(r["usage"][k] for r in completed) for k in ("input_tokens", "cached_input", "output", "reasoning")},
                "actual_account_charge": None, "API_key_calls": 0}
