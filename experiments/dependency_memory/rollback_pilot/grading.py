"""Public receipts contain public evidence only; terminal grading is separate."""
from __future__ import annotations

from dataclasses import dataclass
import time

from .records import ActorTask, EvaluatorTask, InterfaceError, Record, artifact, strict_loads, wire


class InfrastructureError(RuntimeError):
    """An unavailable/unsafe runner is not a candidate's wrong answer."""


def prefix(text, byte_limit):
    return text.encode("utf-8")[:max(0, byte_limit)].decode("utf-8", errors="ignore")


@dataclass(frozen=True)
class PublicReceipt:
    json_text: str

    def data(self):
        return strict_loads(self.json_text)

    @classmethod
    def create(cls, receipt_id, candidate_id, status, check_id=None, observed=None, expected=None, detail="", cap=2048):
        if cap < 512 or any(type(x) is not str or len(x) > 128 for x in (receipt_id, candidate_id, status)):
            raise InterfaceError("invalid receipt identity/cap")
        data = {"receipt_id": receipt_id, "candidate_id": candidate_id, "status": status,
                "check_id": check_id, "observed": observed, "expected": expected, "detail": detail, "truncated": False}
        if len(wire(data).encode("utf-8")) > cap:
            data["truncated"] = True
            # Preserve typed small values; display larger values as bounded text.
            for field in ("observed", "expected", "detail"):
                value = data[field]
                encoded = value if type(value) is str else wire(value)
                if len(encoded.encode("utf-8")) > 256:
                    data[field] = prefix(encoded, 256)
            while len(wire(data).encode("utf-8")) > cap:
                field = max(("observed", "expected", "detail"), key=lambda k: len(wire(data[k])))
                value = data[field] if type(data[field]) is str else wire(data[field])
                data[field] = prefix(value, len(value.encode("utf-8")) // 2)
                if not any(data[k] for k in ("observed", "expected", "detail")):
                    raise InterfaceError("receipt identities exceed cap")
        return cls(wire(data))

    @property
    def eligible(self):
        return self.data()["status"] == "public_mismatch"


class MathChecker:
    def __init__(self, task: ActorTask):
        if type(task) is not ActorTask or task.domain != "math":
            raise InterfaceError("expected public math task")
        self.task = task
        self.data = task.data()

    def violation(self, values):
        """First failure in declared order; no feasibility search or hidden witness."""
        low, high = self.data["bounds"].values()
        for i, value in enumerate(values):
            if value < low or value > high:
                return f"bound{i + 1}", value, [low, high], "Candidate is outside the declared integer bounds."
        if self.data["family"] == "coloring":
            for i, allowed in enumerate(self.data["allowed_colors"]):
                if values[i] not in allowed:
                    return f"list{i + 1}", values[i], allowed, "Candidate color is absent from the public list."
            for i, (a, b) in enumerate(self.data["edges"]):
                if values[a] == values[b]:
                    return f"edge{i + 1}", [values[a], values[b]], "different colors", "The public edge has equal endpoint colors."
        else:
            for row in self.data["constraints"]:
                total = sum(c * x for c, x in zip(row["coefficients"], values))
                if self.data["family"] == "integer":
                    observed, expected = total, row["equals"]
                else:
                    observed, expected = total % row["modulus"], row["residue"]
                if observed != expected:
                    return row["id"], observed, expected, f"Candidate {values} violates this public constraint; residual is {observed - expected}."
        return None

    def receipt(self, candidate, candidate_id="B1", receipt_id="F1"):
        parsed = artifact(candidate, self.task)
        failure = self.violation(parsed["values"])
        if failure:
            return PublicReceipt.create(receipt_id, candidate_id, "public_mismatch", *failure)
        return PublicReceipt.create(receipt_id, candidate_id, "public_pass", detail="All public constraints pass.")


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    stdout: str = ""
    stderr: str = ""
    elapsed_seconds: float = 0.0


def compare_tokens(actual, expected):
    return actual.split() == expected.split()


class CodeChecker:
    def __init__(self, runner, suite_wall_seconds=120):
        self.runner, self.suite_wall_seconds = runner, suite_wall_seconds

    def check(self, code, tests, candidate_id="B1", receipt_id="F1", public=True):
        start = time.monotonic()
        outcomes = []
        for test in tests:
            remaining = self.suite_wall_seconds - (time.monotonic() - start)
            if remaining <= 0:
                outcomes.append({"id": test["id"], "status": "suite_timeout"})
                break
            result = self.runner.execute(code, test["input"], wall_seconds=min(10, remaining))
            if result.status not in {"completed", "syntax_error", "runtime_error", "timeout", "output_limit"}:
                raise InfrastructureError(f"unexpected runner state: {result.status}")
            status = ("public_pass" if compare_tokens(result.stdout, test["output"]) else "public_mismatch") if result.status == "completed" else result.status
            outcomes.append({"id": test["id"], "status": status, "elapsed_seconds": result.elapsed_seconds})
            if status != "public_pass":
                receipt = PublicReceipt.create(receipt_id, candidate_id, status, test["id"],
                                               result.stdout if status == "public_mismatch" else None,
                                               test["output"] if status == "public_mismatch" else None,
                                               "Public output mismatch." if status == "public_mismatch" else result.stderr)
                return (receipt if public else None), outcomes
        passed = len(outcomes) == len(tests) and all(x["status"] == "public_pass" for x in outcomes)
        receipt = PublicReceipt.create(receipt_id, candidate_id, "public_pass" if passed else "suite_timeout",
                                       detail="All public examples pass." if passed else "Suite wall limit exceeded.")
        return (receipt if public else None), outcomes

    def receipt(self, task, candidate, candidate_id="B1", receipt_id="F1"):
        code = artifact(candidate, task)["code"]
        return self.check(code, task.data()["public_examples"], candidate_id, receipt_id)[0]

    def grade(self, task: ActorTask, evaluator: EvaluatorTask, candidate):
        evaluator.check_binding(task)
        code = artifact(candidate, task)["code"]
        tests = task.data()["public_examples"] + evaluator.data()["private_tests"]
        _, outcomes = self.check(code, tests, public=False)
        passed = len(outcomes) == len(tests) and all(x["status"] == "public_pass" for x in outcomes)
        return {"score": int(passed), "disposition": "correct" if passed else "test_failure", "tests": outcomes}


def terminal_grade(task, evaluator, output, code_checker=None):
    evaluator.check_binding(task)
    if output is None:
        return {"score": None, "disposition": "unknown"}
    try:
        if type(output) is not Record or output.kind != "terminal":
            raise InterfaceError("terminal record required")
        candidate = artifact(output.data(), task)
    except InterfaceError:
        return {"score": 0, "disposition": "malformed"}
    if task.domain == "math":
        correct = MathChecker(task).violation(candidate["values"]) is None
        return {"score": int(correct), "disposition": "correct" if correct else "constraint_failure"}
    if code_checker is None:
        raise InfrastructureError("isolated code grader is unavailable")
    return code_checker.grade(task, evaluator, candidate)
