"""Optional local C heuristic; keep discovery separate from witness validation."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / "search.c"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default="clang")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new output path; saved discovery evidence is immutable")
    resolved = shutil.which(args.compiler)
    if not resolved:
        parser.error("C compiler not found")
    compiler = Path(resolved).resolve()
    binary = ROOT / "build/finite3-search.exe"
    binary.parent.mkdir(parents=True, exist_ok=True)
    flags = ["-O3", "-std=c11", "-Wall", "-Wextra", "-Werror"]
    subprocess.run([str(compiler), *flags, str(SOURCE), "-o", str(binary)], check=True)
    version = subprocess.run([str(compiler), "--version"], check=True, stdout=subprocess.PIPE).stdout.decode().strip()
    runs = {}
    for mode in ("greedy", "concatenation"):
        start = perf_counter()
        raw = subprocess.run([str(binary), mode], check=True, stdout=subprocess.PIPE).stdout
        result = json.loads(raw.decode())
        result["process_wall_seconds"] = perf_counter() - start
        result["raw_stdout_sha256"] = hashlib.sha256(raw).hexdigest()
        runs[mode] = result
    record = {"version": "finite3_discovery_record_v1", "date": "2026-10-01", "runs": runs,
        "compiler_version": version, "compiler_sha256": digest(compiler), "compiler_flags": flags,
        "search_executable_sha256": digest(binary), "search_source_sha256": digest(SOURCE),
        "discovery_script_sha256": digest(Path(__file__)), "new_model_requests": 0,
        "search_scope": "Two starts, greedy and historical concatenation; 64 of 4096 unsigned decision triples, up to eight best single swaps. Not a complete codebook or decoder search.",
        "measurement_note": "C clock() reading plus separately measured process wall time. No process-CPU or portable efficiency claim."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({mode: row["errors"] for mode, row in runs.items()}))


if __name__ == "__main__":
    main()
