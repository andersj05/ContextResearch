"""Generate constructed results, or audit a supplied explicit JSON specification.

python -m experiments.dependency_memory.collision_audit.run
python -m experiments.dependency_memory.collision_audit.run --input case.json --output audit.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .engine import Problem, audit, canonical
from .fixtures import diagnostic_specs


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"


def certificate():
    specs = diagnostic_specs()
    return {"schema": 1, "date": "2026-09-21", "evidence": "constructed finite diagnostics",
            "model_calls": 0, "specifications": specs,
            "specifications_sha256": hashlib.sha256(canonical(specs).encode()).hexdigest(),
            "source_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                              for name in ("engine.py", "fixtures.py", "run.py")},
            "audits": [audit(Problem(spec)) for spec in specs]}


def report(data):
    lines = ["# Compaction collision audit: constructed results", "",
             "September 21, 2026. No model calls. Costs are synthetic recovery units.", "",
             "The auditor searches entire groups of histories with identical retained and public",
             "channels. It returns an optimal adaptive recovery policy and a separately checked",
             "obstruction below that cost. A repair label is chosen before the future task is known.", "",
             "| Specification | Budget | Worst recovery cost | Extra retained states | Extra fixed bits |",
             "|---|---:|---:|---:|---:|"]
    for a in data["audits"]:
        costs = [c["minimum_worst_case_recovery_cost"] for t in a["tasks"] for c in t["cells"]]
        cost = "impossible" if None in costs else str(max(costs))
        lines.append(f"| {a['name']} | {a['budget']} | {cost} | {a['repair']['extra_messages']} | {a['repair']['extra_fixed_bits']} |")
    lines += ["", "## Checkable counterexample", "",
              "Three histories permit builds {A,B}, {B,C}, and {A,C}. All share the same retained",
              "summary and public state. Each of the three pairs admits a shared build, so every",
              "pair passes a zero-recovery feasibility check. The whole group has no shared build.",
              "One recovery unit resolves it; with zero units, two retained message states suffice",
              "and one does not. This is an elementary set-intersection example, not a new theorem.", "",
              "## Adaptive tools change the diagnosis", "",
              "The eight-world sharded archive takes two recovery units adaptively (directory, then",
              "the indicated shard). Any fixed batch of queries costs at least four. A one-bit",
              "pre-compaction codebook repair permits recovery within one unit. That bit describes",
              "a finite partition, not an LLM token or a measured natural-language summary improvement.", "",
              "## Revisions and negative controls", "",
              "Reading the latest workspace cannot recover an overwritten original receipt. A",
              "versioned archive rescues it at three units; without that archive, this fixture is",
              "unrecoverable. The late rollback trace is selected from the declared catalog, not",
              "synthesized from arbitrary program executions. Free public evidence, a common valid",
              "answer, and adequate recovery budgets each remove the need for extra retained states.", "",
              "## Scope", "",
              "All results are exact only for the supplied finite worlds, terminal accepted-action",
              "sets, deterministic read-only tools, and positive integer recovery prices. The full",
              "model is known; world identity is hidden from the controller. Tool outputs remain",
              "available during recovery. There is no second forced compaction, stochastic tool,",
              "side effect, semantic summary-equivalence inference, native-agent integration, or",
              "empirical performance claim. Worst-case zero-error guarantees are deliberately",
              "stronger than average task success. The codebook is not a practical compressor.", "",
              "Reproduce with python -m experiments.dependency_memory.collision_audit.run.", "",
              "[Research note](../../../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.input:
        result = audit(Problem(json.loads(args.input.read_text(encoding="utf-8"))))
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8", newline="\n")
        else:
            print(rendered, end="")
    else:
        if args.output:
            parser.error("--output requires --input")
        result = certificate()
        (RESULTS / "collision_audit_certificate.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        (RESULTS / "collision_audit_report.md").write_text(report(result), encoding="utf-8", newline="\n")
        (HERE / "example.json").write_text(json.dumps(diagnostic_specs()[0], indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"Audited {len(result['audits'])} constructed specifications; all policy and lower-proof checks passed.")


if __name__ == "__main__":
    main()
