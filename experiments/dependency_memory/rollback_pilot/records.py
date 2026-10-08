"""Strict, immutable actor records, separate from evaluator material."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any


class InterfaceError(ValueError):
    """A model artifact does not meet the declared interface."""


def wire(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":"))


def digest(value: str | bytes) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def strict_loads(text: str) -> Any:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise InterfaceError(f"duplicate key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise InterfaceError(f"nonfinite number: {value}")

    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise InterfaceError("nonfinite number")
        return result

    try:
        return json.loads(text, object_pairs_hook=unique, parse_constant=constant,
                          parse_float=finite_float)
    except (ValueError, TypeError, RecursionError) as exc:
        raise InterfaceError(str(exc)) from exc


def obj(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise InterfaceError(f"object must have exactly these fields: {list(keys)}")
    return {key: value[key] for key in keys}


def string(value):
    if type(value) is not str:
        raise InterfaceError("expected string")
    # Invalid UTF-16 surrogate values cannot become a UTF-8 artifact.
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise InterfaceError("invalid Unicode string") from exc
    return value


def strings(value):
    if type(value) is not list:
        raise InterfaceError("expected list")
    return [string(x) for x in value]


def integer(value):
    if type(value) is not int:
        raise InterfaceError("expected integer (booleans and floats are invalid)")
    return value


def sources(value, supplied):
    result = strings(value)
    if any(x not in supplied for x in result):
        raise InterfaceError("citation refers to an unsupplied source ID")
    return result


@dataclass(frozen=True)
class ActorTask:
    task_id: str
    domain: str
    stratum: str
    public_json: str

    @classmethod
    def from_dict(cls, task_id, stratum, public):
        """Accept only the two explicit public task schemas; never an evaluator row."""
        domain = public.get("domain") if type(public) is dict else None
        if domain == "math":
            data = obj(public, ("domain", "statement", "family", "variables", "bounds",
                                "constraints", "allowed_colors", "edges"))
            if string(data["family"]) not in {"integer", "modular", "coloring"}:
                raise InterfaceError("unknown math family")
            data["variables"] = strings(data["variables"])
            n = len(data["variables"])
            if not n or len(set(data["variables"])) != n:
                raise InterfaceError("variables must be nonempty and unique")
            bounds = obj(data["bounds"], ("minimum", "maximum"))
            low, high = (integer(bounds[x]) for x in ("minimum", "maximum"))
            if low > high:
                raise InterfaceError("invalid bounds")
            data["bounds"] = bounds
            if type(data["constraints"]) is not list:
                raise InterfaceError("constraints must be a list")
            constraints = []
            for row in data["constraints"]:
                keys = ("id", "coefficients", "equals") if data["family"] == "integer" else (
                    "id", "coefficients", "modulus", "residue")
                row = obj(row, keys)
                string(row["id"])
                if type(row["coefficients"]) is not list or len(row["coefficients"]) != n:
                    raise InterfaceError("coefficient count")
                row["coefficients"] = [integer(x) for x in row["coefficients"]]
                if data["family"] == "integer":
                    integer(row["equals"])
                else:
                    if integer(row["modulus"]) <= 0:
                        raise InterfaceError("invalid modulus")
                    if not 0 <= integer(row["residue"]) < row["modulus"]:
                        raise InterfaceError("invalid residue")
                constraints.append(row)
            if len({r["id"] for r in constraints}) != len(constraints):
                raise InterfaceError("duplicate constraint ID")
            data["constraints"] = constraints
            if data["family"] == "coloring":
                if constraints or type(data["allowed_colors"]) is not list or len(data["allowed_colors"]) != n:
                    raise InterfaceError("coloring schema")
                data["allowed_colors"] = [list(map(integer, c)) for c in data["allowed_colors"]]
                if any(not c or len(set(c)) != len(c) or any(x < low or x > high for x in c)
                       for c in data["allowed_colors"]):
                    raise InterfaceError("invalid color list")
                if type(data["edges"]) is not list:
                    raise InterfaceError("edges must be a list")
                for edge in data["edges"]:
                    if type(edge) is not list or len(edge) != 2:
                        raise InterfaceError("invalid edge")
                    a, b = map(integer, edge)
                    if not 0 <= a < b < n:
                        raise InterfaceError("edge endpoints/order")
                if len(set(map(tuple, data["edges"]))) != len(data["edges"]):
                    raise InterfaceError("duplicate edge")
            elif not constraints or data["allowed_colors"] is not None or data["edges"] != []:
                raise InterfaceError("equation schema")
        elif domain == "coding":
            data = obj(public, ("domain", "statement", "input_format", "output_format", "public_examples"))
            string(data["input_format"])
            string(data["output_format"])
            if type(data["public_examples"]) is not list or not data["public_examples"]:
                raise InterfaceError("coding task needs public examples")
            data["public_examples"] = [validate_test(x) for x in data["public_examples"]]
            if len({t["id"] for t in data["public_examples"]}) != len(data["public_examples"]):
                raise InterfaceError("duplicate public test ID")
        else:
            raise InterfaceError("unknown domain")
        string(data["statement"])
        return cls(string(task_id), domain, string(stratum), wire(data))

    def data(self):
        return strict_loads(self.public_json)

    @property
    def hash(self):
        return digest(self.public_json)

    def source_ids(self):
        data = self.data()
        if self.domain == "coding":
            return {"task", *(r["id"] for r in data["public_examples"])}
        return {"task", "bounds", *(r["id"] for r in data["constraints"]),
                *(f"list{i + 1}" for i in range(len(data["variables"]))),
                *(f"edge{i + 1}" for i in range(len(data["edges"])))}


def validate_test(value):
    row = obj(value, ("id", "input", "output"))
    return {key: string(value) for key, value in row.items()}


@dataclass(frozen=True)
class EvaluatorTask:
    """No renderer accepts this type or its material."""
    task_id: str
    actor_hash: str
    material_json: str

    @classmethod
    def bind(cls, task: ActorTask, material):
        if type(task) is not ActorTask:
            raise InterfaceError("expected ActorTask")
        return cls(task.task_id, task.hash, wire(material))

    def data(self):
        return strict_loads(self.material_json)

    def check_binding(self, task):
        if type(task) is not ActorTask or self.task_id != task.task_id or self.actor_hash != task.hash:
            raise InterfaceError("evaluator/task binding mismatch")


def artifact(value, task):
    if task.domain == "math":
        data = obj(value, ("values",))
        if type(data["values"]) is not list or len(data["values"]) != len(task.data()["variables"]):
            raise InterfaceError("assignment length")
        data["values"] = [integer(x) for x in data["values"]]
    else:
        data = obj(value, ("code",))
        data["code"] = string(data["code"])
    return data


@dataclass(frozen=True)
class Record:
    kind: str
    json_text: str

    def data(self):
        return strict_loads(self.json_text)

    @classmethod
    def parse(cls, kind, text, task, supplied=None, option_ids=()):
        if type(task) is not ActorTask:
            raise InterfaceError("expected ActorTask")
        supplied = task.source_ids() if supplied is None else supplied
        value = strict_loads(text)
        if kind == "checkpoint":
            data = obj(value, ("facts", "open_requirements", "tentative_options", "possible_checks"))
            data["facts"] = observations(data["facts"], supplied)
            data["open_requirements"] = strings(data["open_requirements"])
            data["possible_checks"] = strings(data["possible_checks"])
            options = data["tentative_options"]
            if type(options) is not list or len(options) > 3:
                raise InterfaceError("up to three tentative options")
            data["tentative_options"] = []
            for opt in options:
                opt = obj(opt, ("id", "method", "unverified_assumptions"))
                string(opt["id"])
                string(opt["method"])
                opt["unverified_assumptions"] = strings(opt["unverified_assumptions"])
                if not opt["id"] or opt["id"] == "new":
                    raise InterfaceError("reserved/empty option ID")
                data["tentative_options"].append(opt)
            ids = [o["id"] for o in data["tentative_options"]]
            if len(set(ids)) != len(ids):
                raise InterfaceError("duplicate option ID")
        elif kind == "branch":
            data = obj(value, ("status", "chosen_option", "assumptions", "observations", "artifact"))
            string(data["status"])
            string(data["chosen_option"])
            if data["status"] not in {"candidate", "continue"}:
                raise InterfaceError("branch status")
            if data["chosen_option"] not in {*option_ids, "new"}:
                raise InterfaceError("unsupplied option ID")
            data["assumptions"] = strings(data["assumptions"])
            data["observations"] = observations(data["observations"], supplied)
            if data["status"] == "candidate":
                data["artifact"] = artifact(data["artifact"], task)
            elif data["artifact"] is not None:
                raise InterfaceError("continue requires null artifact")
        elif kind == "lesson":
            data = obj(value, ("failure_kind", "evidence_ids", "refuted_claims", "retained_observations", "uncertainties"))
            string(data["failure_kind"])
            data["evidence_ids"] = sources(data["evidence_ids"], supplied)
            for key in ("refuted_claims", "retained_observations", "uncertainties"):
                data[key] = strings(data[key])
        elif kind == "summary":
            data = obj(value, ("summary",))
            string(data["summary"])
        elif kind == "terminal":
            data = artifact(value, task)
        else:
            raise InterfaceError("unknown record kind")
        return cls(kind, wire(data))


def observations(value, supplied):
    if type(value) is not list:
        raise InterfaceError("observations must be a list")
    result = []
    for row in value:
        row = obj(row, ("statement", "source_ids"))
        result.append({"statement": string(row["statement"]), "source_ids": sources(row["source_ids"], supplied)})
    return result
