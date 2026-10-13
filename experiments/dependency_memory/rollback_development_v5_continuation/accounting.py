"""Cumulative ledger import, no repeated identities, and local unknown failures."""
from dataclasses import asdict
from pathlib import Path
import json
import sqlite3

from ..rollback_development_v5.accounting import Ledger as OriginalLedger, Stopped
from ..rollback_development_v5.common import now, wire, sha
from ..rollback_pilot.subscription.accounting import RESERVATION


class CallUnknown(Stopped):
    """One admitted identity failed; unrelated jobs remain admissible."""


class Ledger(OriginalLedger):
    def __init__(self, path, identities, max_inflight, *, prior=None, generation_ceiling=13640):
        if Path(path).exists():
            raise ValueError("new cumulative ledger required")
        super().__init__(path, identities, max_inflight)
        if type(generation_ceiling) is not int or generation_ceiling <= 0:
            raise ValueError("positive total generation ceiling required")
        self.generation_ceiling = generation_ceiling
        with self.connect() as db:
            db.execute("CREATE TABLE continuation_config(id INTEGER PRIMARY KEY,payload TEXT)")
            db.execute("INSERT INTO continuation_config VALUES(1,?)", (wire({"generation_ceiling": generation_ceiling}),))
            db.execute("CREATE TABLE inherited_stops(reason TEXT)")
        if prior is not None:
            source = sqlite3.connect(Path(prior).resolve().as_uri() + "?mode=ro", uri=True)
            try:
                rows = source.execute("SELECT * FROM calls ORDER BY id").fetchall()
                events = source.execute("SELECT * FROM events ORDER BY seq").fetchall()
                threads = source.execute("SELECT * FROM threads ORDER BY thread_id").fetchall()
                stops = source.execute("SELECT reason FROM stops").fetchall()
                if any(r[3] not in {"completed", "unknown"} for r in rows):
                    raise ValueError("prior admitted calls must drain before continuation")
                if len(rows) > generation_ceiling:
                    raise ValueError("prior admissions exceed total allocation")
                if any(r[0] not in self.identities or json.loads(r[1]) != self.identities[r[0]] for r in rows):
                    raise ValueError("prior identity is outside the original allocation")
                with self.connect() as db:
                    db.executemany("INSERT INTO calls VALUES(?,?,?,?,?)", rows)
                    db.executemany("INSERT INTO events VALUES(?,?,?,?)", events)
                    db.executemany("INSERT INTO threads VALUES(?,?)", threads)
                    db.executemany("INSERT INTO inherited_stops VALUES(?)", stops)
            finally:
                source.close()

    def admit(self, identity, request_hash):
        with self.lock:
            with self.connect() as db:
                exhausted = db.execute("SELECT COUNT(*) FROM calls").fetchone()[0] >= self.generation_ceiling
                if exhausted:
                    db.execute("INSERT OR IGNORE INTO stops VALUES(1,?)", ("generation_ceiling_reached",))
            if exhausted:
                raise Stopped("generation_ceiling_reached")
            return super().admit(identity, request_hash)

    def unknown(self, identity, reason, *, diagnostic=None, fatal=False):
        payload = {"reason": reason, "reserve_credits": str(RESERVATION), "observed_utc": now(),
                   "diagnostic": diagnostic, "failure_scope": "global" if fatal else "trajectory"}
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT state FROM calls WHERE id=?", (identity.key,)).fetchone() != ("dispatched",):
                raise ValueError("unknown requires a newly admitted identity")
            db.execute("UPDATE calls SET state='unknown',payload=? WHERE id=?", (wire(payload), identity.key))
            db.execute("INSERT INTO events(call_id,state,payload) VALUES(?,?,?)", (identity.key, "unknown", wire(payload)))
            if fatal:
                db.execute("INSERT OR IGNORE INTO stops VALUES(1,?)", ("systemic_transport_failure",))
