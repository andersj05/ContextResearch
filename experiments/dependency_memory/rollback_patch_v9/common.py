"""New study identity; frozen earlier studies are imported without modification."""
from pathlib import Path
from ..rollback_development_v5.common import ROOT, now, wire, sha, read, save_new, IMAGE

PACKAGE = Path(__file__).resolve().parent
STUDY = "rollback-patch-factorial-v9-2026-10-13"
MODEL, EFFORT = "gpt-6-luna", "medium"
SEED = 2026101391
ARMS = ("K0", "R0", "KL", "RL")
ATTEMPTS = 3
WORKERS, RUNTIME_WORKERS = 32, 4
MAX_BODY_BYTES = 262144
MIN_CHANGED_LINES = 4
FOCUS = ("requirements", "boundary_cases", "state_invariants", "ordering", "algorithm",
         "rounding", "tie_breaking", "dependencies", "unresolved")
