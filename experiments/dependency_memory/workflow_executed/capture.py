"""Execute the prespecified local scenarios; never invoke a model or network."""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
from time import perf_counter_ns, process_time_ns

from experiments.dependency_memory.workflow_eval.grader import ARTIFACTS, CHECKS, wire, validate_records, validate_task

HERE = Path(__file__).parent
CAPTURE = HERE / "capture.json"
SCENARIOS = (
    ("unchanged", CHECKS, CHECKS),
    ("tests_later_failure", ("tests",), ("tests",)),
    ("tests_recovery", ("tests",), ("tests",)),
    ("repository_later_failure", ("repository",), ("repository",)),
    ("repository_recovery", ("repository",), ("repository",)),
    ("artifact_replaced", ("paper",), ("paper",)),
    ("artifact_missing", ("paper",), ("paper",)),
    ("new_source_unchecked", ("repository", "tests"), ("tests",)),
    ("partial_revision", ("repository", "tests"), ("repository", "tests")),
    ("older_source_selected", ("paper", "tests"), ("paper",)),
    ("irrelevant_failure", ("paper", "tests"), ("paper",)),
    ("fail_recover_fail", ("tests",), ("tests",)),
)

TEST_SOURCE = '''import json
from pathlib import Path
import unittest
from calc import add_offset

class ArithmeticTests(unittest.TestCase):
    def test_observed_contract(self):
        state = json.loads(Path("runtime.json").read_text())
        for value in (-11, 0, 7, 123):
            with self.subTest(value=value):
                self.assertEqual(value + state["expected_offset"], add_offset(value))

if __name__ == "__main__":
    unittest.main(verbosity=2)
'''

CHECK_SOURCE = '''import html
from pathlib import Path
import sys
from calc import add_offset

if sys.argv[1] == "repository":
    paths = ("calc.py", "test_calc.py", "README.md", "readiness.marker")
    missing = [p for p in paths if not Path(p).is_file()]
    print("Required files:", ", ".join(paths))
    if missing:
        print("Missing:", ", ".join(missing))
        raise SystemExit(1)
    assert "Arithmetic example" in Path("README.md").read_text()
    print("Repository check passed")
elif sys.argv[1] == "paper":
    source = Path("README.md").read_text() + "\\nObserved add_offset(7): " + str(add_offset(7)) + "\\n"
    folder = Path("build/paper")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "manuscript.md").write_text(source, encoding="utf-8")
    (folder / "preview.html").write_text("<!doctype html><html><body><pre>" + html.escape(source) + "</pre></body></html>", encoding="utf-8")
    print("Built Markdown and HTML from current source")
else:
    raise SystemExit(2)
'''


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def collect():
    cases, provenance = [], []
    rng = random.Random(2026092902)
    for cid, scope, required in SCENARIOS:
        offset = rng.randrange(100, 9000)
        with tempfile.TemporaryDirectory(prefix="executed-workflow-") as folder:
            root = Path(folder)
            source_names = ("calc.py", "test_calc.py", "README.md", "checks.py")
            (root / "test_calc.py").write_text(TEST_SOURCE, encoding="utf-8", newline="\n")
            (root / "checks.py").write_text(CHECK_SOURCE, encoding="utf-8", newline="\n")
            (root / "README.md").write_text(f"# Arithmetic example\n\nScenario {cid}.\n", encoding="utf-8", newline="\n")
            snapshots, states, runs, actions = {}, {}, [], []
            initial, between = [], []

            def source(value):
                (root / "calc.py").write_text(f"def add_offset(value):\n    return value + {value}\n", encoding="utf-8", newline="\n")

            def snapshot():
                files = {n: (root / n).read_bytes().decode() for n in source_names}
                sid = digest(wire(files))
                snapshots[sid] = files
                return sid

            def state(expected, marker=True):
                (root / "runtime.json").write_text(json.dumps({"expected_offset": expected}), encoding="utf-8")
                marker_path = root / "readiness.marker"
                if marker:
                    marker_path.write_text("ready\n", encoding="utf-8")
                elif marker_path.exists():
                    marker_path.unlink()
                raw = {"runtime.json": (root / "runtime.json").read_text(), "readiness.marker": marker}
                rid = digest(wire(raw))
                states[rid] = raw
                actions.append({"operation": "runtime_state", "state": rid})
                return rid

            def artifact_bytes():
                return {p: (root / p).read_bytes().decode() for p in ARTIFACTS if (root / p).is_file()}

            def run(check, destination):
                sid = snapshot()
                runtime = {"runtime.json": (root / "runtime.json").read_text(), "readiness.marker": (root / "readiness.marker").is_file()}
                state_id = digest(wire(runtime))
                states[state_id] = runtime
                args = ["-B", "test_calc.py"] if check == "tests" else ["-B", "checks.py", check]
                started = datetime.now(timezone.utc).isoformat()
                wall, cpu = perf_counter_ns(), process_time_ns()
                proc = subprocess.run([sys.executable, *args], cwd=root, capture_output=True, timeout=30)
                elapsed_wall, elapsed_cpu = perf_counter_ns()-wall, process_time_ns()-cpu
                built = artifact_bytes() if check == "paper" and proc.returncode == 0 else {}
                record = {"check": check, "snapshot": sid, "returncode": proc.returncode,
                          "artifacts": {p: digest(v.encode()) for p, v in built.items()},
                          "argv": ["python", *args], "stdout": proc.stdout.decode("utf-8"), "stderr": proc.stderr.decode("utf-8")}
                record["run_id"] = digest(wire({"case": cid, "sequence": len(runs), "started": started, "record": record}))
                destination.append(record)
                runs.append({"run_id": record["run_id"], "started": started, "source": sid,
                             "runtime_state": state_id, "artifacts": built,
                             "stdout_sha256": digest(proc.stdout), "stderr_sha256": digest(proc.stderr),
                             "wall_ns": elapsed_wall, "collector_cpu_ns": elapsed_cpu})

            source(offset)
            state(offset + (1 if cid == "tests_recovery" else 0), marker=cid != "repository_recovery")
            for check in CHECKS:
                run(check, initial)
            old_source, old_artifacts = snapshots[snapshot()], artifact_bytes()
            if cid == "older_source_selected":
                source(offset + 17)
                state(offset + 17)
                for check in CHECKS:
                    run(check, initial)
            if cid in {"tests_later_failure", "irrelevant_failure", "fail_recover_fail"}:
                state(offset + 1)
                run("tests", between)
                if cid == "fail_recover_fail":
                    state(offset)
                    run("tests", between)
                    state(offset + 2)
                    run("tests", between)
            if cid == "tests_recovery":
                state(offset)
                run("tests", between)
            if cid in {"repository_later_failure", "repository_recovery"}:
                state(offset, marker=cid == "repository_recovery")
                run("repository", between)
            if cid == "partial_revision":
                source(offset + 23)
                state(offset + 23)
                run("tests", between)
            # Post-boundary changes reveal no hidden new command outcome.
            if cid == "new_source_unchecked":
                source(offset + 31)
                actions.append({"operation": "post_boundary_source_change"})
            if cid == "artifact_replaced":
                with (root / ARTIFACTS[1]).open("a", encoding="utf-8") as stream:
                    stream.write("\n<!-- replaced after handoff -->\n")
                actions.append({"operation": "post_boundary_artifact_replacement", "path": ARTIFACTS[1]})
            if cid == "artifact_missing":
                (root / ARTIFACTS[1]).unlink()
                actions.append({"operation": "post_boundary_artifact_removal", "path": ARTIFACTS[1]})
            if cid == "older_source_selected":
                for name, content in old_source.items():
                    (root / name).write_bytes(content.encode())
                for name, content in old_artifacts.items():
                    (root / name).write_bytes(content.encode())
                actions.append({"operation": "post_boundary_restore_old_source_and_artifacts"})
            final_artifacts = artifact_bytes()
            task = {"snapshot": snapshot(), "required_checks": list(required),
                    "artifacts": {p: digest(v.encode()) for p, v in final_artifacts.items()}}
            validate_records(initial + between)
            validate_task(task)
            cases.append({"id": cid, "origin": "constructed_scenario_with_observed_subprocesses",
                          "initial": initial, "between": between, "scope": list(scope), "task": task})
            provenance.append({"id": cid, "source_files": snapshots, "runtime_states": states,
                               "runs": runs, "actions": actions, "final_artifacts": final_artifacts})
    return {"schema": "executed_workflow_capture_v1", "seed": 2026092902,
            "python_version": sys.version, "python_sha256": digest(Path(sys.executable).read_bytes()),
            "cases": cases, "provenance": provenance}


def validate_capture(data):
    if [c["id"] for c in data["cases"]] != [c[0] for c in SCENARIOS]:
        raise ValueError("Scenario schedule differs")
    if len(data["provenance"]) != len(SCENARIOS):
        raise ValueError("Missing provenance")
    for case, evidence, specification in zip(data["cases"], data["provenance"], SCENARIOS):
        records = case["initial"] + case["between"]
        validate_records(records)
        validate_task(case["task"])
        if (case["id"] != evidence["id"] or case["scope"] != list(specification[1])
                or case["task"]["required_checks"] != list(specification[2])
                or len(records) != len(evidence["runs"])):
            raise ValueError("Capture specification mismatch")
        for sid, files in evidence["source_files"].items():
            if digest(wire(files)) != sid:
                raise ValueError("Source digest mismatch")
        for sid, state in evidence["runtime_states"].items():
            if digest(wire(state)) != sid:
                raise ValueError("Runtime digest mismatch")
        for index, (record, run) in enumerate(zip(records, evidence["runs"])):
            if record["snapshot"] not in evidence["source_files"] or run["runtime_state"] not in evidence["runtime_states"]:
                raise ValueError("Missing source or runtime")
            fields = {k: v for k, v in record.items() if k != "run_id"}
            identity = digest(wire({"case": case["id"], "sequence": index, "started": run["started"], "record": fields}))
            if run["run_id"] != record["run_id"] or identity != record["run_id"] or run["source"] != record["snapshot"]:
                raise ValueError("Run binding mismatch")
            if record["artifacts"] != {p: digest(v.encode()) for p, v in run["artifacts"].items()}:
                raise ValueError("Artifact binding mismatch")
            for stream in ("stdout", "stderr"):
                if digest(record[stream].encode()) != run[stream + "_sha256"]:
                    raise ValueError("Stream digest mismatch")
        if case["task"]["snapshot"] not in evidence["source_files"] or case["task"]["artifacts"] != {p: digest(v.encode()) for p, v in evidence["final_artifacts"].items()}:
            raise ValueError("Final state mismatch")
    return deepcopy(data["cases"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=CAPTURE)
    args = parser.parse_args()
    data = collect()
    validate_capture(data)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"cases": len(data["cases"]), "actual_commands": sum(len(p["runs"]) for p in data["provenance"]), "output": str(args.output)}))
