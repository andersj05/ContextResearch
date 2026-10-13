"""New study constants; historical studies and allocations remain immutable."""
from pathlib import Path
from ..rollback_development_v5.common import ROOT, now, wire, sha, read, save_new
from ..rollback_challenge_v6.common import public_task, stage_packet

PACKAGE = Path(__file__).resolve().parent
STUDY = "rollback-parallel-v8-2026-10-13"
MODEL = "gpt-6-luna"
EFFORT = "medium"
SEED = 2026101368
MAX_WORKERS = 32
DEFAULT_WORKERS = 16
MAX_BODY_BYTES = 131072
WRITER_BYTES = 4096
EMPTY = {"values": [], "order": [], "files": []}
