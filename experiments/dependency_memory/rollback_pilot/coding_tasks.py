"""Offline selection from an explicitly normalized, provenance-reviewed inventory.

This loader does not download a corpus, unpickle data, infer licenses, or invent
reference solutions. The complete retained test-set attestation is a preparation
input and remains a live-cohort gate until checked against pinned source bytes.
"""
import re

from .grading import InfrastructureError
from .records import ActorTask, EvaluatorTask, InterfaceError, digest, obj, validate_test, wire


EXPOSED = {("atcoder", x) for x in ("abc301_a", "abc301_b", "abc301_c", "abc301_d", "abc301_e", "abc301_f",
                                   "abc302_a", "abc302_d", "abc302_e", "abc302_f")}


def select_coding(inventory, code_checker, additional_exposed=()):
    required = ("dataset", "release", "dataset_commit", "loader_sha256", "source_files", "items")
    obj(inventory, required)
    if inventory["dataset"] != "livecodebench/code_generation_lite" or inventory["release"] != "release_v6":
        raise InterfaceError("only the proposed lite release_v6 is supported")
    if not re.fullmatch(r"[0-9a-f]{40}", inventory["dataset_commit"]) or not re.fullmatch(r"[0-9a-f]{64}", inventory["loader_sha256"]):
        raise InterfaceError("pin the actual dataset commit and loader SHA-256")
    if not inventory["source_files"]:
        raise InterfaceError("pinned source bytes/hashes are required")
    for row in inventory["source_files"]:
        obj(row, ("path", "sha256"))
        if not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
            raise InterfaceError("invalid source hash")
    exposed = EXPOSED | set(map(tuple, additional_exposed))
    exclusions, candidates, seen_ids, seen_content = [], [], set(), set()
    keys = ("platform", "question_id", "difficulty", "release_date", "statement", "input_format", "output_format",
            "public_tests", "private_tests", "interface", "comparison", "standard_library_python", "license_review",
            "reference_code", "reference_provenance", "retained_tests_complete")
    for raw in sorted(inventory["items"], key=lambda x: (x["platform"], x["question_id"], digest(wire(x)))):
        item = obj(raw, keys)
        identity = (item["platform"], item["question_id"])
        content_hash = digest(" ".join(item["statement"].split()))
        reason = None
        if identity in exposed:
            reason = "design_or_human_exposure"
        elif identity in seen_ids or content_hash in seen_content:
            reason = "duplicate_identity_or_statement"
        elif item["difficulty"] not in {"easy", "medium", "hard"}:
            reason = "unsupported_difficulty"
        elif item["interface"] != "stdin_stdout" or item["comparison"] != "exact_tokens" or item["standard_library_python"] is not True:
            reason = "unsupported_interface_or_judge"
        elif not item["public_tests"] or not item["private_tests"]:
            reason = "missing_public_or_reserved_tests"
        elif item["retained_tests_complete"] is not True:
            reason = "retained_test_inventory_unverified"
        elif (type(item["license_review"]) is not dict or item["license_review"].get("permitted") is not True
              or not item["license_review"].get("source") or not item["license_review"].get("reviewer")):
            reason = "source_license_unresolved"
        elif not item["reference_code"] or not item["reference_provenance"]:
            reason = "missing_reference_or_provenance"
        seen_ids.add(identity)
        seen_content.add(content_hash)
        if reason:
            exclusions.append({"platform": identity[0], "question_id": identity[1], "reason": reason})
            continue
        public = {"domain": "coding", "statement": item["statement"], "input_format": item["input_format"],
                  "output_format": item["output_format"], "public_examples": [validate_test(x) for x in item["public_tests"]]}
        task = ActorTask.from_dict("code-" + "-".join(identity), item["difficulty"], public)
        private = [validate_test(x) for x in item["private_tests"]]
        if len({x["id"] for x in public["public_examples"] + private}) != len(public["public_examples"] + private):
            raise InterfaceError("test IDs must be unique across the complete suite")
        evaluator = EvaluatorTask.bind(task, {"private_tests": private, "reference_code": item["reference_code"],
                                             "reference_provenance": item["reference_provenance"], "license_review": item["license_review"],
                                             "origin": {"dataset": inventory["dataset"], "release": inventory["release"],
                                                        "commit": inventory["dataset_commit"], "platform": identity[0],
                                                        "question_id": identity[1], "release_date": item["release_date"]},
                                             "loader_sha256": inventory["loader_sha256"], "source_files": inventory["source_files"],
                                             "reference_sha256": digest(item["reference_code"]), "private_tests_sha256": digest(wire(private))})
        try:
            grade = code_checker.grade(task, evaluator, {"code": item["reference_code"]})
        except InfrastructureError:
            # Engine loss is global; do not convert it into an outcome-driven cohort exclusion.
            raise
        if grade["score"] != 1:
            exclusions.append({"platform": identity[0], "question_id": identity[1], "reason": "reference_fails_fixed_suite_or_resources", "grade": grade})
            continue
        selection_hash = digest(f"rollback-v02|20261007|{identity[0]}|{identity[1]}")
        candidates.append((selection_hash, identity, task, evaluator))
    selected, ordering, shortfalls = [], [], {}
    for difficulty in ("easy", "medium", "hard"):
        ordered = sorted((x for x in candidates if x[2].stratum == difficulty), key=lambda x: (x[0], x[1]))
        ordering.extend({"platform": x[1][0], "question_id": x[1][1], "difficulty": difficulty,
                         "selection_hash": x[0], "selected": index < 4} for index, x in enumerate(ordered))
        selected.extend((x[2], x[3]) for x in ordered[:4])
        shortfalls[difficulty] = max(0, 4 - len(ordered))
    return selected, {"ordering": ordering, "exclusions": exclusions, "shortfalls": shortfalls,
                      "inventory_sha256": digest(wire(inventory)), "real_source_verification_required": True}
