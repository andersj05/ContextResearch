"""Pure interpretation of public rules using only an admitted final request.

No source ledger, grader, filesystem, archive, model client or semantic prose
parser is available here. A matching answer is consistent with this memory;
it is not a certificate that compression preserved the complete source.
"""
from __future__ import annotations

import json
import math
import re

CHECKS = ("paper", "repository", "tests")
ARTIFACTS = ("build/paper/manuscript.md", "build/paper/preview.html")
RECEIPT_RULE = (
    "Report whether the required checks have current successful evidence. For each required check use its latest observed run on the final source snapshot; a later failure supersedes an earlier success. A receipt is valid only if its bound artifact hashes match the final inventory. Return strict JSON with exactly ready (boolean), needs_work (sorted check names), and evidence (mapping each currently successful required check to its exact run_id). Include no extra fields. A missing, failed or stale check belongs in needs_work, not evidence. Do not invent evidence or shorten identifiers."
)
PUBLIC_RULES = {
    "retry_queue": "For the selected request: if dispatch.state is not_sent, action=submit and work=[]; otherwise require result.attempt_uuid and billing.for_attempt to match dispatch.attempt_uuid. If a scope mismatches, hold with result_scope or billing_scope. Otherwise close if result.state is passed and billing.state is settled; retry if result.state is failed and retry_policy.retry_allowed is true; otherwise hold with result, billing or retry_policy for the applicable failed conditions. Return target_id=request_token. Apply the late event first.",
    "ci_promotion": "Promote only if build.channel=stable, authorization.state=approved, authorization.approved_digest=build.digest, verification.subject=build.digest, verification.unit and integration both pass, and handoff.environment=prod. Otherwise hold with the exact sorted set of channel, approval, approval_scope, ci_scope, unit, integration, environment for each failed condition. Return target_id=build.digest. Apply the late event first.",
    "data_pipeline": "Publish only if extract, transform, load, quality states pass, transform.input_dataset=extract.output_dataset, load.input_dataset=transform.output_dataset, quality.subject_dataset=load.output_dataset, consent.state=approved, and consent.approved_output=load.output_dataset. Otherwise hold with the exact sorted set of extract, transform, load, quality, link_transform, link_load, quality_scope, approval, approval_scope for failed conditions. Return target_id=load.output_dataset. Apply the late event first.",
}
OWNERS = {"retry_queue": "request_token", "ci_promotion": "deployment_slot", "data_pipeline": "pipeline_run"}
FIELDS = {
    "retry_queue": ("request_token", "dispatch.attempt_uuid", "dispatch.state", "result.attempt_uuid", "result.state", "billing.for_attempt", "billing.state", "retry_policy.retry_allowed"),
    "ci_promotion": ("deployment_slot", "build.digest", "build.channel", "authorization.approved_digest", "authorization.state", "verification.subject", "verification.unit", "verification.integration", "handoff.environment"),
    "data_pipeline": ("pipeline_run", "extract.output_dataset", "extract.state", "transform.input_dataset", "transform.output_dataset", "transform.state", "load.input_dataset", "load.output_dataset", "load.state", "quality.subject_dataset", "quality.state", "consent.approved_output", "consent.state"),
}
PATH = re.compile(r"^[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*$")


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key")
            result[key] = value
        return result

    def nonfinite(_):
        raise ValueError("nonfinite_json")

    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError("nonfinite_json")
        return result

    return json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite, parse_float=finite_float)


def _hash(value, lengths=(64,)):
    return isinstance(value, str) and len(value) in lengths and re.fullmatch(r"[0-9a-f]+", value) is not None


def _artifacts(value):
    return isinstance(value, dict) and all(k in ARTIFACTS and _hash(v) for k, v in value.items())


def receipt_answer(memory, task):
    """Aggregate last retained receipts, independently of the ledger grader."""
    if not isinstance(task, dict) or set(task) != {"snapshot", "required_checks", "artifacts"}:
        raise ValueError("invalid_public_task")
    required = task["required_checks"]
    if (not _hash(task["snapshot"], (40, 64)) or not isinstance(required, list)
            or not required or any(c not in CHECKS for c in required)
            or required != sorted(set(required)) or not _artifacts(task["artifacts"])):
        raise ValueError("invalid_public_task")
    records = strict_json(memory)
    if not isinstance(records, list):
        raise ValueError("unsupported_receipt_representation")
    latest, identities = {}, set()
    for row in records:
        if (not isinstance(row, dict) or not {"check", "snapshot", "run_id", "returncode", "artifacts"} <= row.keys()
                or row["check"] not in CHECKS or not _hash(row["snapshot"], (40, 64))
                or not _hash(row["run_id"]) or type(row["returncode"]) is not int
                or not _artifacts(row["artifacts"]) or row["run_id"] in identities):
            raise ValueError("invalid_receipt")
        identities.add(row["run_id"])
        if row["check"] == "paper" and row["returncode"] == 0:
            if set(row["artifacts"]) != set(ARTIFACTS):
                raise ValueError("incomplete_artifact_bindings")
        elif row["artifacts"]:
            raise ValueError("unexpected_artifact_bindings")
        if row["snapshot"] == task["snapshot"] and row["check"] in required:
            latest[row["check"]] = row
    evidence = {}
    for name, row in latest.items():
        if row["returncode"] == 0 and row["artifacts"].items() <= task["artifacts"].items():
            evidence[name] = row["run_id"]
    missing = sorted(set(required) - evidence.keys())
    return {"ready": not missing, "needs_work": missing, "evidence": evidence}


def _flatten(data, prefix=""):
    if not isinstance(data, dict):
        raise ValueError("invalid_component")
    result = {}
    for name, value in data.items():
        if not isinstance(name, str) or not PATH.fullmatch(name) or "." in name:
            raise ValueError("invalid_field_path")
        path = prefix + name
        if isinstance(value, dict):
            result.update(_flatten(value, path + "."))
        elif type(value) in (str, bool, int, float) or value is None:
            result[path] = value
        else:
            raise ValueError("invalid_component_value")
    return result


def cross_rows(memory, family):
    """Decode the two public wire formats; never consult source schemas."""
    data = strict_json(memory)
    if isinstance(data, dict) and set(data) == {"f", "r"}:
        fields, values = data["f"], data["r"]
        if (not isinstance(fields, list) or not fields or any(not isinstance(f, str) or not PATH.fullmatch(f) for f in fields)
                or len(set(fields)) != len(fields) or not isinstance(values, list)
                or any(a.startswith(b + ".") for a in fields for b in fields)):
            raise ValueError("invalid_table_paths")
        rows = []
        for row in values:
            if not isinstance(row, list) or len(row) != len(fields) or any(isinstance(v, (dict, list)) for v in row):
                raise ValueError("invalid_table_rows")
            rows.append(dict(zip(fields, row)))
        return rows
    if not isinstance(data, list):
        raise ValueError("unsupported_cross_representation")
    groups = {}
    for item in data:
        if (not isinstance(item, dict) or set(item) != {"tool", "data"}
                or not isinstance(item["tool"], str) or not PATH.fullmatch(item["tool"]) or "." in item["tool"]
                or not isinstance(item["data"], dict)):
            raise ValueError("invalid_tool_result")
        key = item["data"].get("workflow_key")
        if not isinstance(key, str) or not key:
            raise ValueError("missing_join_key")
        group = groups.setdefault(key, {})
        if item["tool"] in group:
            raise ValueError("ambiguous_component")
        group[item["tool"]] = item["data"]
    components = {p.split(".")[0] for p in FIELDS[family] if "." in p}
    rows = []
    for group in groups.values():
        if not {"root", *components} <= group.keys():
            raise ValueError("incomplete_join")
        row = _flatten(group["root"])
        for component in components:
            row.update(_flatten({k: v for k, v in group[component].items() if k != "workflow_key"}, component + "."))
        rows.append(row)
    return rows


def cross_answer(memory, target, event, family):
    rows = cross_rows(memory, family)
    if not isinstance(target, str) or not target:
        raise ValueError("invalid_target")
    matched = [r for r in rows if r.get(OWNERS[family]) == target]
    if len(matched) != 1:
        raise ValueError("target_not_unique")
    row = dict(matched[0])
    if not isinstance(event, dict) or set(event) != {"path", "value"}:
        raise ValueError("invalid_late_event")
    if event["path"] != "note":
        if event["path"] not in FIELDS[family]:
            raise ValueError("unsupported_late_event")
        row[event["path"]] = event["value"]
    for path in FIELDS[family]:
        value = row.get(path)
        expected_type = bool if path == "retry_policy.retry_allowed" else str
        if type(value) is not expected_type or (expected_type is str and not value):
            raise ValueError("missing_or_wrong_type:" + path)
    if family == "retry_queue":
        attempt = row["dispatch.attempt_uuid"]
        target_id = row["request_token"]
        scope = {name for name, path in (("result_scope", "result.attempt_uuid"), ("billing_scope", "billing.for_attempt")) if row[path] != attempt}
        result, billing, retry = row["result.state"], row["billing.state"], row["retry_policy.retry_allowed"]
        if row["dispatch.state"] == "not_sent":
            action, work = "submit", []
        elif scope:
            action, work = "hold", sorted(scope)
        elif (result, billing) == ("passed", "settled"):
            action, work = "close", []
        elif result == "failed" and retry:
            action, work = "retry", []
        else:
            action = "hold"
            work = sorted(name for name, failed in (("result", result != "passed"), ("billing", billing != "settled"), ("retry_policy", result == "failed" and not retry)) if failed)
    else:
        if family == "ci_promotion":
            target_id = row["build.digest"]
            equalities = {
                "channel": (row["build.channel"], "stable"),
                "approval": (row["authorization.state"], "approved"),
                "approval_scope": (row["authorization.approved_digest"], target_id),
                "ci_scope": (row["verification.subject"], target_id),
                "unit": (row["verification.unit"], "pass"),
                "integration": (row["verification.integration"], "pass"),
                "environment": (row["handoff.environment"], "prod"),
            }
            successful_action = "promote"
        else:
            target_id = row["load.output_dataset"]
            equalities = {name: (row[name + ".state"], "pass") for name in ("extract", "transform", "load", "quality")}
            equalities.update({
                "link_transform": (row["transform.input_dataset"], row["extract.output_dataset"]),
                "link_load": (row["load.input_dataset"], row["transform.output_dataset"]),
                "quality_scope": (row["quality.subject_dataset"], target_id),
                "approval": (row["consent.state"], "approved"),
                "approval_scope": (row["consent.approved_output"], target_id),
            })
            successful_action = "publish"
        work = sorted(name for name, (left, right) in equalities.items() if left != right)
        action = "hold" if work else successful_action
    return {"action": action, "target_id": target_id, "work": work}


def derive(request):
    if not isinstance(request, dict) or request.get("stage") != "execute":
        raise ValueError("not_a_final_request")
    observation, instruction = request.get("observation"), request.get("instruction")
    if not isinstance(observation, dict) or not isinstance(instruction, str) or not isinstance(observation.get("memory"), str):
        raise ValueError("invalid_request")
    if set(observation) == {"memory", "final_public_state"} and instruction.startswith(RECEIPT_RULE + "\n"):
        return receipt_answer(observation["memory"], observation["final_public_state"])
    if set(observation) == {"memory", "target", "late_event"}:
        families = [f for f, rule in PUBLIC_RULES.items() if instruction.endswith(rule)]
        if len(families) == 1:
            return cross_answer(observation["memory"], observation["target"], observation["late_event"], families[0])
    raise ValueError("unsupported_public_rule")


def check(request, proposal):
    """A veto/abstention diagnostic, with an explicitly conditional readout."""
    try:
        answer = derive(request)
    except (ValueError, TypeError, KeyError, RecursionError) as error:
        return {"status": "uncheckable", "reason": str(error), "derived_answer": None,
                "changed_fields": [], "source_complete_certified": False}
    try:
        observed = strict_json(proposal) if isinstance(proposal, str) else proposal
        # Compare serialized JSON so bool/int equality cannot accept invalid types.
        exact = (isinstance(observed, dict) and json.dumps(observed, sort_keys=True, allow_nan=False)
                 == json.dumps(answer, sort_keys=True, allow_nan=False))
    except (ValueError, TypeError, RecursionError):
        observed, exact = None, False
    changed = sorted(k for k in answer if not isinstance(observed, dict)
                     or json.dumps(observed.get(k), sort_keys=True, allow_nan=False)
                     != json.dumps(answer[k], sort_keys=True, allow_nan=False))
    if isinstance(observed, dict) and set(observed) != set(answer):
        changed.append("answer_schema")
    return {"status": "consistent" if exact else "contradicted", "reason": "matches_retained_evidence" if exact else "contradicts_retained_evidence",
            "derived_answer": answer, "changed_fields": changed, "source_complete_certified": False}
