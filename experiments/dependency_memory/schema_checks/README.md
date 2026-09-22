# Schema-derived checks on frozen tool-result traces

The [protocol](FROZEN_PROTOCOL.md) and [finding](../../../research/SCHEMA_CHECKS_UNSEEN_TRACES_2026-09-22.md)
cover the completed 72-call comparison. The constructed trace generator,
terminal grader, and evaluation values were committed before `memory.py`.
Evaluation values are distinct from development values but reuse the same three
annotated schema families. No model call is made by the offline checks below.

```powershell
python -m unittest experiments.dependency_memory.schema_checks.test_schema_checks -v
python -m experiments.dependency_memory.schema_checks.analyze
python scripts/benchmark_schema_checks.py
python scripts/reconcile_schema_checks.py
python scripts/validate_context_repo.py
```

`run.py --launch` is a live one-shot launcher, already completed. It refuses an
existing output directory and never retries a dispatched request. Its previous
80-call/10-credit ceiling was only for this fixed 72-call schedule and is not
permission for another run. The [saved results](../results/schema_checks_2026-09-22/reconciled_report.md)
preserve all terminal failures and costs; every arm happened to have zero
failures, so the primary improvement criterion failed. The original raw report
records zero CPU nanoseconds because Windows `process_time_ns` could not resolve
the brief operations. The separate high-resolution calibration is a post-run
local-cost sensitivity, not a replacement for per-run CPU measurement.
