"""Canonical data and explicit study constants; no credentials or generation."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
STUDY = "rollback-development-v5-2026-10-08"
SEED = 2026100857
MODEL = "gpt-6-luna"
EFFORT = "medium"
HORIZONS = {"short": (2, 1), "medium": (10, 4), "long": (30, 8)}
FAMILIES = ("scheduling", "routing", "ledger", "resolver")
POLICIES = ("K", "R", "Z", "G", "F")
MECHANISM_ARMS = ("K", "R", "Z", "G", "F", "KE", "RE")
IMAGE = "python:3.11-slim@sha256:0dd364ba7e10242f07755449e3a3d0e35f9efd987952737b90def6709ab0c5ce"
MAX_WORKERS = 8
DEFAULT_WORKERS = 4
WRITER_BYTES = 4096
MAX_BODY_BYTES = 131072
MEMORY_BOUNDARIES = (2, 4)


def wire(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def sha(value):
    if not isinstance(value, bytes):
        value = (value if isinstance(value, str) else wire(value)).encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(wire(value) + "\n")


def now():
    return datetime.now(timezone.utc).isoformat()


def public_task(task):
    """Only the persistent contract. Future packets and evaluator fields excluded."""
    return {k: task[k] for k in ("task_id", "family", "domain", "contract", "initial_artifact")}


def stage_packet(task, stage):
    return {"stage": stage + 1, "stage_count": len(task["stages"]), **task["stages"][stage]}
