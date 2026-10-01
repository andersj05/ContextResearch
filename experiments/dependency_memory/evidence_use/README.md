# Evidence-use investigation

October 1, 2026. An offline retrospective audit plus an actor-side final-decision
check, with actual-workflow collection preparation. Read the
[retrospective protocol](PROTOCOL.md) and [prospective intake contract](INTAKE.md).

```powershell
python -m experiments.dependency_memory.evidence_use.replay
python -m unittest experiments.dependency_memory.evidence_use.test_guard experiments.dependency_memory.evidence_use.test_replay -v
```

The [report](../results/evidence_use_2026-10-01/report.md),
[complete diagnostics](../results/evidence_use_2026-10-01/analysis.json),
[four reduced witnesses](../results/evidence_use_2026-10-01/witnesses.json) and
[local measurements](../results/evidence_use_2026-10-01/measurement.json) are new
artifacts. Historical calls, sources, protocols and grades are unchanged.

`guard.py` is pure: it reads only admitted final-request fields and the proposed
answer, with hand-written compilers of already public rules. `replay.py` has
evaluator access for independent grading. `observe.py` separately captures real
offline commands at clean source commits; it is not accessible to the actor.

The audit includes 368 scheduled finals in three selected studies: 319 answers,
three transport gaps and 46 never dispatched. It does not treat these correlated
development observations as independent samples or repair old primary tests.
An unparsed format is unknown. A matching retained readout is an instance-level
calculation, not a proof that the full history was preserved. No overall gain,
native-compaction result, unseen-schema extraction or total-cost claim is made.
