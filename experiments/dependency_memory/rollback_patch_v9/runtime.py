"""Batched two-module grading in a fresh, digest-pinned isolated container.

Candidate code is never imported, compiled or executed by the host. A fresh
container receives the two candidate files and all INPUTS in one public or
private suite; expected values stay in this trusted checker. Batch input
visibility and shared state within the batch are explicit experimental access.
The model receives public receipts only; private grading returns aggregates.
"""
from copy import deepcopy
import json
import threading

from ..rollback_pilot.code_runner import DockerRunner
from ..rollback_pilot.grading import InfrastructureError
from ..rollback_pilot.records import digest, strict_loads, wire


PINNED_IMAGE = "python:3.11-slim@sha256:0dd364ba7e10242f07755449e3a3d0e35f9efd987952737b90def6709ab0c5ce"
ALLOWED_FILES = ("engine.py", "rules.py")
MAX_SOURCE_BYTES = 32768
MAX_CASES = 128
MAX_SUITE_INPUT_BYTES = 131072
MAX_CONTAINERS = 4
FORMAT = "rollback-patch-v9-batch-result-v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(",", ":"))


PROGRAM = r'''
import json,pathlib,sys
files=json.loads(FILES_JSON)
cases=json.load(sys.stdin)['cases']
for item in files:
    pathlib.Path('/scratch',item['path']).write_text(item['text'],encoding='utf-8')
try:
    for item in files:
        compile(item['text'],'/scratch/'+item['path'],'exec')
except (SyntaxError,ValueError) as error:
    print(json.dumps({'format':'rollback-patch-v9-batch-result-v1','status':'syntax_error',
                      'outputs':[],'detail':str(error)[:512]},separators=(',',':')))
    sys.exit(0)
sys.path.insert(0,'/scratch')
import engine
outputs=[engine.solve(case) for case in cases]
print(json.dumps({'format':'rollback-patch-v9-batch-result-v1','status':'completed',
                  'outputs':outputs,'detail':''},separators=(',',':'),allow_nan=False))
'''


def candidate_program(candidate):
    """Validate paths/data only; turn files into a trusted container wrapper."""
    if type(candidate) is not dict or set(candidate) != {"files"}:
        raise ValueError("candidate must contain exactly files")
    rows = candidate["files"]
    if type(rows) is not list or len(rows) != len(ALLOWED_FILES):
        raise ValueError("exactly two replacement files required")
    files, size = {}, 0
    for row in rows:
        if type(row) is not dict or set(row) != {"path", "text"}:
            raise ValueError("replacement file must contain path and text")
        path, text = row["path"], row["text"]
        if type(path) is not str or path not in ALLOWED_FILES or path in files or type(text) is not str:
            raise ValueError("only unique engine.py and rules.py replacement files permitted")
        size += len(text.encode("utf-8"))
        files[path] = text
    if set(files) != set(ALLOWED_FILES) or size > MAX_SOURCE_BYTES:
        raise ValueError("candidate file inventory or total UTF-8 byte limit violated")
    canonical = [{"path": path, "text": files[path]} for path in ALLOWED_FILES]
    # repr encodes literal data in the wrapper; no host evaluation of source.
    return PROGRAM.replace("FILES_JSON", repr(wire(canonical)), 1)


def checked_tests(tests):
    if type(tests) is not list or not 1 <= len(tests) <= MAX_CASES:
        raise InfrastructureError("a nonempty bounded test suite is required")
    seen = set()
    for test in tests:
        if type(test) is not dict or set(test) != {"id", "input", "expected"}:
            raise InfrastructureError("invalid trusted test envelope")
        name = test["id"]
        if type(name) is not str or not name or len(name) > 128 or name in seen:
            raise InfrastructureError("unique bounded trusted test IDs required")
        seen.add(name)
        try:
            json.dumps([test["input"], test["expected"]], allow_nan=False)
        except (TypeError, ValueError):
            raise InfrastructureError("trusted tests must contain finite JSON values") from None
    payload = wire({"cases": [test["input"] for test in tests]})
    if len(payload.encode("utf-8")) > MAX_SUITE_INPUT_BYTES:
        raise InfrastructureError("suite input byte limit exceeded")
    return deepcopy(tests), payload


def _failure(status, count, public, detail=""):
    if not public:
        return {"status": "private_fail", "score": 0, "disposition": status,
                "test_count": count, "passed_count": 0}
    return {"status": status, "score": 0, "disposition": status,
            "test_count": count, "passed_count": 0, "check_id": None,
            "input": None, "expected": None, "observed": None,
            "detail": detail.encode("utf-8")[:1024].decode("utf-8", errors="ignore"),
            "tests": []}


class PatchRuntime:
    def __init__(self, image=PINNED_IMAGE, *, max_containers=MAX_CONTAINERS,
                 runner=None):
        if type(max_containers) is not int or not 1 <= max_containers <= MAX_CONTAINERS:
            raise ValueError("one through four concurrent containers required")
        self.runner = DockerRunner(image) if runner is None else runner
        self.max_containers = max_containers
        self._slots = threading.BoundedSemaphore(max_containers)
        self._lock = threading.Lock()
        self._active = self._peak = self._executions = 0

    def configuration(self):
        return {"runtime": self.runner.configuration(), "allowed_files": list(ALLOWED_FILES),
                "source_bytes": MAX_SOURCE_BYTES, "maximum_suite_cases": MAX_CASES,
                "suite_input_bytes": MAX_SUITE_INPUT_BYTES,
                "maximum_concurrent_containers": self.max_containers,
                "wrapper_sha256": digest(PROGRAM),
                "access": "all inputs from one suite are available to the program in a fresh container; expected values never enter it; shared process/module state within that suite is permitted",
                "comparison": "exact typed canonical JSON values; no token or float tolerance",
                "model_private_feedback": "none; private grading returns aggregate score and disposition only"}

    def audit(self):
        return {"configuration": self.configuration(), "container_audit": self.runner.audit(),
                "model_calls": 0, "host_candidate_execution": False}

    def statistics(self):
        with self._lock:
            return {"executions": self._executions, "active_containers": self._active,
                    "peak_containers": self._peak, "maximum_containers": self.max_containers}

    def check(self, candidate, tests, *, public=True):
        if type(public) is not bool:
            raise ValueError("public must be boolean")
        tests, payload = checked_tests(tests)
        try:
            program = candidate_program(candidate)
        except (ValueError, UnicodeError):
            return _failure("invalid_candidate", len(tests), public,
                            "Two valid bounded replacement files are required.")
        with self._slots:
            with self._lock:
                self._active += 1
                self._peak = max(self._peak, self._active)
                self._executions += 1
            try:
                result = self.runner.execute(program, payload, wall_seconds=10)
            finally:
                with self._lock:
                    self._active -= 1
        if result.status not in {"completed", "syntax_error", "runtime_error", "timeout", "output_limit"}:
            raise InfrastructureError("unexpected isolated execution status")
        if result.status != "completed":
            return _failure(result.status, len(tests), public, result.stderr)
        try:
            value = strict_loads(result.stdout)
            if type(value) is not dict or set(value) != {"format", "status", "outputs", "detail"}:
                raise ValueError("batch output envelope")
            if value["format"] != FORMAT or type(value["detail"]) is not str:
                raise ValueError("batch output format")
            if value["status"] == "syntax_error" and value["outputs"] == []:
                return _failure("syntax_error", len(tests), public, value["detail"])
            outputs = value["outputs"]
            if value["status"] != "completed" or type(outputs) is not list or len(outputs) != len(tests):
                raise ValueError("batch output count/status")
        except (TypeError, ValueError, KeyError):
            return _failure("invalid_output", len(tests), public,
                            "Program did not return one valid JSON value per supplied case.")
        passed = [canonical(observed) == canonical(test["expected"]) for test, observed in zip(tests, outputs)]
        count, score = sum(passed), int(all(passed))
        disposition = "correct" if score else "test_failure"
        if not public:
            return {"status": "private_pass" if score else "private_fail", "score": score,
                    "disposition": disposition, "test_count": len(tests), "passed_count": count}
        bad = next((index for index, value in enumerate(passed) if not value), None)
        failed = tests[bad] if bad is not None else None
        return {"status": "public_pass" if score else "public_mismatch", "score": score,
                "disposition": disposition, "test_count": len(tests), "passed_count": count,
                "check_id": failed["id"] if failed else None,
                "input": failed["input"] if failed else None,
                "expected": failed["expected"] if failed else None,
                "observed": outputs[bad] if bad is not None else None,
                "detail": "All public cases pass." if score else "Public JSON output mismatch.",
                "tests": [{"id": test["id"], "status": "public_pass" if okay else "public_mismatch"}
                          for test, okay in zip(tests, passed)]}
