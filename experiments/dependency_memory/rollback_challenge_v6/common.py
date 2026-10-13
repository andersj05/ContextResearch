"""A new allocation, with no changes to the frozen v5 sources or evidence."""
from pathlib import Path
from ..rollback_development_v5.common import ROOT, now, wire, sha, read, save_new

PACKAGE = Path(__file__).resolve().parent
STUDY = "rollback-challenge-v6-2026-10-09"
MODEL = "gpt-6-luna"
EFFORT = "medium"
SEED = 2026100917
FAMILIES = ("constraint_grid", "bitvector_program", "revision_ledger")
LEVELS = (1, 2, 3)
EMPTY = {"values": [], "order": [], "files": []}
MAX_BODY_BYTES = 131072
WRITER_BYTES = 4096


def public_task(task):
    return {k: task[k] for k in ("task_id", "family", "domain", "contract", "initial_artifact")}


def stage_packet(task, stage):
    return {"stage": stage + 1, "stage_count": len(task["stages"]), **task["stages"][stage]}
