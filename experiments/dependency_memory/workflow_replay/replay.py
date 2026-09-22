"""Two actual byte boundaries and a completely metered local handoff task."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import json

from .evidence import classify, decode_fields, encode_fields, project, wire

METHODS = ("status", "fields", "compact_fields", "repair", "direct_receipts")


class Exhausted(Exception):
    pass


@dataclass
class Meter:
    allowance: int
    check_price: int
    tool_price: int = 128
    byte_count: int = 0
    checks: int = 0
    tools: int = 0
    events: list = field(default_factory=list)
    rejected: str | None = None
    pre_recovery_available: bool = False

    @property
    def spent(self):
        return self.byte_count + self.check_price * self.checks + self.tool_price * self.tools

    def charge(self, label, *, byte_count=0, checks=0, tools=0):
        if min(byte_count, checks, tools) < 0:
            raise ValueError("Negative accounting")
        cost = byte_count + self.check_price * checks + self.tool_price * tools
        if self.spent + cost > self.allowance:
            self.rejected = label
            raise Exhausted(label)
        self.byte_count += byte_count
        self.checks += checks
        self.tools += tools
        self.events.append({"operation": label, "bytes": byte_count, "checks": checks,
                            "tools": tools, "cost": cost})

    def transmit(self, label, value):
        raw = wire(value)
        self.charge(label, byte_count=len(raw))
        return raw


def pack(entries, capacity):
    """Exact bytes, including all tags, IDs, order and the public schema version."""
    selected = []
    if len(wire([1, selected])) > capacity:
        raise ValueError("Capacity cannot hold the envelope")
    for entry in entries:
        if len(wire([1, selected + [entry]])) <= capacity:
            selected.append(entry)
    return wire([1, selected])


def unpack(memory):
    version, entries = json.loads(memory)
    if version != 1:
        raise ValueError("Unknown memory schema")
    return entries


def entry_for(record, method, meter):
    identity = [record["worker"], record["case_id"], record["request_sha256"]]
    if method == "status":
        return [*identity, "s", record["status"]]
    if method == "fields":
        return [*identity, "f", project(record)]
    if method == "compact_fields":
        return [*identity, "c", encode_fields(project(record))]
    if method in ("repair", "direct_receipts"):
        meter.charge("derive_receipt", checks=1)
        return [*identity, "r", classify(record)]
    raise ValueError("Unknown method")


def propose(records, method, capacity, meter, reference):
    # This is the sole function with pre-deletion source access. No realized
    # pair/target is accepted by its signature.
    meter.transmit("initial_observation", records)
    if method == "repair":
        initial = pack([entry_for(r, "status", meter) for r in records], capacity)
        meter.charge("initial_candidate_write", byte_count=len(initial))
        meter.charge("audit_candidate_read", byte_count=len(initial))
        missing = []
        known = {e[1]: e for e in unpack(initial)}
        for row in records:
            meter.charge("independent_obligation_audit", checks=1)
            # Derive the obligation from the original executable checker, not
            # from a hidden evaluation route. Status memory carries no amounts.
            expected = reference(row)
            entry = known.get(row["case_id"])
            proposed = decode_entry(entry, meter) if entry is not None else None
            if proposed != expected:
                missing.append(row["case_id"])
        meter.transmit("diagnosis_packet", {"missing": missing,
            "require": "exact dispatch class, settlement and reservation, bound to request identity"})
        # One repair, with all diagnosed obligations still available. No
        # candidate history or diagnosis packet survives the memory boundary.
    entries = [entry_for(r, method, meter) for r in records]
    memory = pack(entries, capacity)
    meter.charge("parent_memory_write", byte_count=len(memory))
    return memory


def narrow(memory, workers, capacity, meter):
    meter.charge("parent_memory_read", byte_count=len(memory))
    meter.transmit("pair_reveal", list(workers))
    child = pack([e for e in unpack(memory) if e[0] in workers], capacity)
    meter.charge("child_memory_write", byte_count=len(child))
    return child


def decode_entry(entry, meter):
    if entry is None:
        return None
    tag, payload = entry[3:]
    if tag == "r":
        return deepcopy(payload)
    if tag in ("c", "f"):
        meter.charge("check_retained_fields", checks=1)
        return classify(decode_fields(payload) if tag == "c" else payload)
    if tag == "s":
        return None  # Status alone cannot certify an exact accounting handoff.
    raise ValueError("Unknown entry tag")


class Archive:
    """The only source-record channel available after the first deletion."""

    def __init__(self, records, mode):
        if mode not in ("none", "full", "projected"):
            raise ValueError("Unknown archive mode")
        self._records = {r["case_id"]: deepcopy(r) for r in records}
        self.mode = mode

    def read(self, case_id, meter):
        if self.mode == "none":
            return None
        meter.transmit("archive_request", {"case_id": case_id})
        meter.charge("archive_call", tools=1)
        row = self._records[case_id]
        if self.mode == "projected":
            meter.charge("archive_projection", checks=1)
            row = {"case_id": row["case_id"], "request_sha256": row["request_sha256"],
                   **project(row)}
        meter.transmit("archive_response", row)
        return deepcopy(row)


def finish(memory, target, archive, meter):
    """Visible-only executor. No original records or grader objects are arguments."""
    meter.charge("child_memory_read", byte_count=len(memory))
    meter.transmit("target_reveal", {"case_id": target})
    entry = next((e for e in unpack(memory) if e[1] == target), None)
    result = decode_entry(entry, meter)
    available = result is not None and result[0] != "unknown"
    meter.pre_recovery_available = available
    request_hash = entry[2] if entry is not None else None
    if not available:
        row = archive.read(target, meter)
        if row is not None:
            meter.charge("check_recovered_fields", checks=1)
            result = classify(row)
            request_hash = row["request_sha256"]
    result = result or ["unknown", None, None]
    action = {"case_id": target, "request_sha256": request_hash,
              "classification": result[0], "settled": result[1], "reserved": result[2]}
    meter.transmit("terminal_action", action)
    return action, available


def prepare(records, method, parent_capacity, extra_allowance, check_price, reference):
    common = len(wire(records))
    meter = Meter(common + extra_allowance, check_price)
    try:
        memory = propose(records, method, parent_capacity, meter, reference)
    except Exhausted:
        memory = None
    return memory, meter


def continue_route(prepared, workers, target, child_capacity, archive, expected, *, detailed=False):
    parent, prefix = prepared
    meter = deepcopy(prefix)
    action = child = None
    available = False
    try:
        if parent is not None:
            child = narrow(parent, workers, child_capacity, meter)
            action, available = finish(child, target, archive, meter)
    except Exhausted:
        pass
    result = {"case_id": target, "workers": list(workers), "success": action == expected,
        "pre_recovery_available": meter.pre_recovery_available, "cost": meter.spent, "allowance": meter.allowance,
        "bytes": meter.byte_count, "checks": meter.checks, "tool_calls": meter.tools,
        "budget_rejected_at": meter.rejected,
        "parent_bytes": len(parent) if parent is not None else None,
        "child_bytes": len(child) if child is not None else None,
        "parent_entries": len(unpack(parent)) if parent is not None else 0,
        "child_entries": len(unpack(child)) if child is not None else 0}
    if detailed:
        result.update(action=action, expected=expected, events=meter.events,
                      parent_memory=parent.decode() if parent is not None else None,
                      child_memory=child.decode() if child is not None else None)
    return result
