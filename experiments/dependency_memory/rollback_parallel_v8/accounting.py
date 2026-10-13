"""Bounded parallel admissions without retries or reopening an allocation.

The inherited ledger uses one locked SQLite admission transaction, unique call
identities and unique provider-thread identities. Its unknown reservations stay
locked; an ordinary missing response stops its trajectory, while systemic faults
stop global admission. Only the supported worker range changes here.
"""
from ..rollback_development_v5.accounting import Identity, Stopped
from ..rollback_development_v5_continuation.accounting import (
    CallUnknown,
    Ledger as LocalUnknownLedger,
)


MAX_WORKERS = 32
DEFAULT_WORKERS = 16


def check_workers(workers):
    if type(workers) is not int or not 1 <= workers <= MAX_WORKERS:
        raise ValueError("one through thirty-two workers required")
    return workers


class Ledger(LocalUnknownLedger):
    """A new, bounded v8 ledger; no prior-ledger import or replacement calls."""

    def __init__(self, path, identities, max_inflight, *, generation_ceiling):
        check_workers(max_inflight)
        if type(generation_ceiling) is not int or generation_ceiling <= 0:
            raise ValueError("positive generation ceiling required")
        super().__init__(path, identities, max_inflight,
                         generation_ceiling=generation_ceiling)
