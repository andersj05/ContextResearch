"""Record one explicitly selected command; no retries or automatic launches."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument("--record", type=Path, required=True)
parser.add_argument("command", nargs=argparse.REMAINDER)
args = parser.parse_args()
command = args.command[1:] if args.command[:1] == ["--"] else args.command
if not command:
    parser.error("explicit command required")
prefix = args.record
prefix.parent.mkdir(parents=True, exist_ok=True)
log = prefix.with_suffix(".txt")
record = prefix.with_suffix(".json")
if log.exists() or record.exists():
    parser.error("new evidence paths required")
start_utc = datetime.now(timezone.utc).isoformat()
started = time.monotonic()
with log.open("x", encoding="utf-8", newline="\n") as stream:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding="utf-8", errors="replace",
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    for line in process.stdout:
        stream.write(line)
        stream.flush()
        print(line, end="", flush=True)
    process.stdout.close()
    exit_code = process.wait()
summary = {"command": command, "cwd": str(Path.cwd()), "started_utc": start_utc,
           "finished_utc": datetime.now(timezone.utc).isoformat(),
           "elapsed_seconds": time.monotonic() - started, "exit_code": exit_code,
           "console_path": log.name, "console_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}
with record.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(summary, stream, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps(summary, sort_keys=True), flush=True)
sys.exit(exit_code)
