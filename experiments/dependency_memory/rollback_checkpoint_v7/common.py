"""New study constants; historical studies and allocations remain immutable."""
from pathlib import Path
from ..rollback_development_v5.common import ROOT, now, wire, sha, read, save_new
from ..rollback_challenge_v6.common import public_task, stage_packet

PACKAGE = Path(__file__).resolve().parent
STUDY = "rollback-checkpoint-v7-2026-10-12"
MODEL = "gpt-6-luna"
EFFORT = "medium"
SEED = 2026101267
MAX_WORKERS = 16
DEFAULT_WORKERS = 8
MAX_BODY_BYTES = 131072
WRITER_BYTES = 4096
EMPTY = {"values": [], "order": [], "files": []}
