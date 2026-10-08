"""Append-only transactional call events and conservative synthetic-dollar accounting."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import sqlite3

from .records import InterfaceError, digest, strict_loads, wire


RATES = {"uncached_input": Decimal("0.10"), "cached_input": Decimal("0.01"),
         "cache_write": Decimal("0.125"), "output": Decimal("0.50")}
INPUT_CAP, OUTPUT_CAP = 32768, 16384
PER_CALL = (Decimal(INPUT_CAP) * max(RATES[k] for k in ("uncached_input", "cached_input", "cache_write"))
            + Decimal(OUTPUT_CAP) * RATES["output"]) / 1000000


class AccountingError(RuntimeError):
    pass


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    uncached_input: int
    cached_input: int
    cache_write: int
    output: int
    reasoning: int

    def validate(self):
        values = vars(self)
        if any(type(v) is not int or v < 0 for v in values.values()):
            raise AccountingError("usage must contain nonnegative integers")
        if self.input_tokens != self.uncached_input + self.cached_input + self.cache_write:
            raise AccountingError("input billing buckets are not exclusive/exhaustive")
        if self.reasoning > self.output:
            raise AccountingError("reasoning is a subset of output")
        if self.input_tokens > INPUT_CAP or self.output > OUTPUT_CAP:
            raise AccountingError("metered usage exceeded the declared caps")
        return self

    @property
    def cost(self):
        self.validate()
        return sum(Decimal(getattr(self, key)) * rate for key, rate in RATES.items()) / 1000000


@dataclass(frozen=True)
class Identity:
    launch_id: str
    task_id: str
    stage: str
    slot: int = 1
    arm: str | None = None
    draw: int | None = None

    @property
    def key(self):
        return digest(wire(vars(self)))


class Ledger:
    """SQLite transactions serialize admissions; history is never updated/deleted.

    A previously reserved/dispatched/unknown call blocks new admissions, including
    after reopening. Reconciliation is deliberately outside this offline controller.
    """
    def __init__(self, path, ceiling=Decimal("5.00"), max_calls=320):
        self.path, self.ceiling, self.max_calls = Path(path), Decimal(ceiling), max_calls
        self.connection = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        self.connection.execute("PRAGMA synchronous=FULL")
        self.connection.execute("CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, call_id TEXT NOT NULL, state TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(call_id,state))")
        self.connection.execute("CREATE TABLE IF NOT EXISTS configuration (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)")
        config = wire({"ceiling": str(self.ceiling), "max_calls": max_calls, "per_call": str(PER_CALL), "rates": {k: str(v) for k, v in RATES.items()}})
        self.connection.execute("INSERT OR IGNORE INTO configuration VALUES(1,?)", (config,))
        if self.connection.execute("SELECT payload FROM configuration WHERE id=1").fetchone()[0] != config:
            self.connection.close()
            raise AccountingError("existing ledger configuration cannot change")

    def close(self):
        self.connection.close()

    def events(self):
        return [{"seq": seq, "call_id": call_id, "state": state, **strict_loads(payload)}
                for seq, call_id, state, payload in self.connection.execute("SELECT seq,call_id,state,payload FROM events ORDER BY seq")]

    def rows(self):
        result = {}
        for event in self.events():
            result.setdefault(event["call_id"], {}).update(event)
        return result

    def summary(self):
        rows = list(self.rows().values())
        spent = sum((Decimal(row["cost_usd"]) for row in rows if row["state"] == "completed"), Decimal(0))
        unresolved = [row for row in rows if row["state"] in {"reserved", "dispatched", "unknown"}]
        locked = sum((Decimal(row["reserve_usd"]) for row in unresolved), Decimal(0))
        return {"completed_cost_usd": str(spent), "locked_reserve_usd": str(locked),
                "liability_usd": str(spent + locked), "admitted_calls": sum(row["state"] != "planned" for row in rows),
                "blocked": bool(unresolved), "unresolved_call_ids": [row["call_id"] for row in unresolved]}

    def _append(self, call_identity, state, **fields):
        fields["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        self.connection.execute("INSERT INTO events(call_id,state,payload) VALUES(?,?,?)", (call_identity.key, state, wire(fields)))

    def _transaction(self, action):
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            action()
            self.connection.execute("COMMIT")
        except BaseException:
            self.connection.execute("ROLLBACK")
            raise

    def plan(self, identity, request_hash):
        def action():
            if identity.key in self.rows():
                raise AccountingError("identity already exists; never repeat a planned dispatch")
            self._append(identity, "planned", identity=vars(identity), request_hash=request_hash, reserve_usd=str(PER_CALL))
        self._transaction(action)

    def reserve(self, identity):
        def action():
            row = self.rows().get(identity.key)
            if row is None or row["state"] != "planned":
                raise AccountingError("reservation requires a new planned row")
            summary = self.summary()
            if summary["blocked"]:
                raise AccountingError("unresolved call blocks the launch")
            if summary["admitted_calls"] >= self.max_calls or Decimal(summary["liability_usd"]) + PER_CALL > self.ceiling:
                raise AccountingError("call or liability ceiling reached")
            self._append(identity, "reserved")
        self._transaction(action)

    def dispatch(self, identity, request_hash):
        def action():
            row = self.rows().get(identity.key)
            if row is None or row["state"] != "reserved" or row["request_hash"] != request_hash:
                raise AccountingError("dispatch requires its matching reservation")
            self._append(identity, "dispatched")
        self._transaction(action)

    def complete(self, identity, usage: Usage, disposition, metadata=None):
        usage.validate()
        def action():
            row = self.rows().get(identity.key)
            if row is None or row["state"] != "dispatched":
                raise AccountingError("completion requires exactly one dispatch")
            if usage.cost > Decimal(row["reserve_usd"]):
                raise AccountingError("actual cost exceeds reservation")
            self._append(identity, "completed", usage=vars(usage), cost_usd=str(usage.cost), disposition=disposition, metadata=metadata or {})
        self._transaction(action)

    def unknown(self, identity, reason):
        def action():
            row = self.rows().get(identity.key)
            if row is None or row["state"] != "dispatched":
                raise AccountingError("unknown outcome requires a dispatch")
            self._append(identity, "unknown", disposition=reason)
        self._transaction(action)
