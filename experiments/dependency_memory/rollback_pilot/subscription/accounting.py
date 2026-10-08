"""Durable subscription planning-credit reservations; never API dollar billing."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sqlite3

from ..accounting import AccountingError, Identity
from ..records import strict_loads, wire

INPUT_ENVELOPE, OUTPUT_ENVELOPE = 1050000, 128000
RATES = {"uncached_input": Decimal("2.5"), "cached_input": Decimal(".25"),
         "output": Decimal("12.5")}
RESERVATION = (INPUT_ENVELOPE * RATES["uncached_input"] + OUTPUT_ENVELOPE * RATES["output"]) / 1000000


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    cached_input: int
    output: int
    reasoning: int

    @classmethod
    def from_telemetry(cls, value):
        required = ("inputTokens", "cachedInputTokens", "outputTokens", "reasoningOutputTokens", "totalTokens")
        if type(value) is not dict or any(type(value.get(x)) is not int or value[x] < 0 for x in required):
            raise AccountingError("missing or invalid subscription usage")
        if value["totalTokens"] != value["inputTokens"] + value["outputTokens"]:
            raise AccountingError("inconsistent subscription total")
        return cls(value["inputTokens"], value["cachedInputTokens"], value["outputTokens"], value["reasoningOutputTokens"]).validate()

    def validate(self):
        if any(type(x) is not int or x < 0 for x in vars(self).values()):
            raise AccountingError("usage must contain nonnegative integers")
        if self.cached_input > self.input_tokens or self.reasoning > self.output:
            raise AccountingError("cached/reasoning counts are subsets")
        if self.input_tokens == 0:
            raise AccountingError("a nonempty request needs positive input metering")
        if self.input_tokens > INPUT_ENVELOPE or self.output > OUTPUT_ENVELOPE:
            raise AccountingError("usage exceeded conditional model envelope")
        return self

    @property
    def cost(self):
        self.validate()
        return ((self.input_tokens - self.cached_input) * RATES["uncached_input"]
                + self.cached_input * RATES["cached_input"] + self.output * RATES["output"]) / 1000000


class Ledger:
    def __init__(self, path, *, ceiling=None, max_calls=8):
        try:
            self.ceiling = None if ceiling is None else Decimal(ceiling)
        except InvalidOperation as error:
            raise AccountingError("invalid credit ceiling") from error
        if (self.ceiling is not None and (not self.ceiling.is_finite() or self.ceiling <= 0)) or type(max_calls) is not int or not 0 < max_calls <= 320:
            raise AccountingError("invalid allocation")
        self.max_calls, self.path = max_calls, Path(path)
        self.connection = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        self.connection.execute("PRAGMA synchronous=FULL")
        self.connection.execute("CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, call_id TEXT NOT NULL, state TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(call_id,state))")
        self.connection.execute("CREATE TABLE IF NOT EXISTS configuration(id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)")
        config = wire({"unit": "subscription_planning_credits", "ceiling": None if self.ceiling is None else str(self.ceiling),
                       "max_calls": max_calls, "reservation": str(RESERVATION),
                       "rates": {k: str(v) for k, v in RATES.items()},
                       "conditional_input_envelope": INPUT_ENVELOPE, "conditional_output_envelope": OUTPUT_ENVELOPE})
        self.connection.execute("INSERT OR IGNORE INTO configuration VALUES(1,?)", (config,))
        if self.connection.execute("SELECT payload FROM configuration WHERE id=1").fetchone()[0] != config:
            self.close()
            raise AccountingError("existing credit ledger configuration cannot change")

    def close(self):
        self.connection.close()

    def events(self):
        return [{"seq": seq, "call_id": key, "state": state, **strict_loads(payload)}
                for seq, key, state, payload in self.connection.execute("SELECT seq,call_id,state,payload FROM events ORDER BY seq")]

    def rows(self):
        result = {}
        for event in self.events():
            result.setdefault(event["call_id"], {}).update(event)
        return result

    def summary(self):
        rows = list(self.rows().values())
        spent = sum((Decimal(x["planning_credits"]) for x in rows if x["state"] == "completed"), Decimal(0))
        unresolved = [x for x in rows if x["state"] in {"reserved", "dispatched", "unknown"}]
        locked = sum((Decimal(x["reserve_credits"]) for x in unresolved), Decimal(0))
        return {"unit": "subscription_planning_credits_not_actual_account_charge", "completed_credits": str(spent),
                "locked_reserve_credits": str(locked), "liability_credits": str(spent + locked),
                "admitted_calls": sum(x["state"] != "planned" for x in rows), "blocked": bool(unresolved),
                "unresolved_call_ids": [x["call_id"] for x in unresolved]}

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
                raise AccountingError("identity exists; never replay")
            self._append(identity, "planned", identity=vars(identity), request_hash=request_hash, reserve_credits=str(RESERVATION))
        self._transaction(action)

    def reserve(self, identity):
        def action():
            row, summary = self.rows().get(identity.key), self.summary()
            if row is None or row["state"] != "planned" or summary["blocked"]:
                raise AccountingError("new, unresolved-free plan required")
            if summary["admitted_calls"] >= self.max_calls or (self.ceiling is not None and Decimal(summary["liability_credits"]) + RESERVATION > self.ceiling):
                raise AccountingError("call or planning-credit ceiling reached")
            self._append(identity, "reserved")
        self._transaction(action)

    def dispatch(self, identity, request_hash):
        def action():
            row = self.rows().get(identity.key)
            if row is None or row["state"] != "reserved" or row["request_hash"] != request_hash:
                raise AccountingError("matching reservation required")
            self._append(identity, "dispatched")
        self._transaction(action)

    def complete(self, identity, usage, disposition, metadata=None):
        if type(usage) is not Usage:
            raise AccountingError("subscription usage required")
        usage.validate()
        def action():
            row = self.rows().get(identity.key)
            if row is None or row["state"] != "dispatched" or usage.cost > Decimal(row["reserve_credits"]):
                raise AccountingError("one reserved dispatch and bounded usage required")
            self._append(identity, "completed", usage=vars(usage), planning_credits=str(usage.cost),
                         disposition=disposition, metadata=metadata or {})
        self._transaction(action)

    def unknown(self, identity, reason):
        def action():
            row = self.rows().get(identity.key)
            if row is None or row["state"] != "dispatched":
                raise AccountingError("unknown requires a dispatch")
            self._append(identity, "unknown", disposition=reason)
        self._transaction(action)
