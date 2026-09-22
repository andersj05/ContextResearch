# Finite novelty audit

This package checks an elementary reformulation of the existing collision
auditor: budget-bounded recovery strategies induce accepted-output relations;
minimal unsafe groups induce a weak-coloring problem for additional memory.
It narrows the novelty claim and is not a new compression algorithm.

```powershell
python -m experiments.dependency_memory.novelty_audit.run
python -m unittest experiments.dependency_memory.novelty_audit.test_novelty_audit -v
```

The runner produces a deterministic [certificate](../results/feedback_novelty_certificate.json)
and [report](../results/feedback_novelty_report.md). It compares forward policy
enumeration with the existing recovery solver on 343 accepted-action tables at
three budgets, then compares independently enumerated colorings with repair
partitions. The 12 existing fixtures also receive coloring checks. This extends
the earlier three-world verification domain; it does not create independent
task samples or model observations.

Read the [derivation and novelty verdict](../../../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md)
for assumptions, prior art and remaining research questions. Original experiment
modules and saved model-study source fingerprints are unchanged.
