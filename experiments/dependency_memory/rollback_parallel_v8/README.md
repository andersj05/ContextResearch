# Parallel rollback runner v8

Engineering follow-up to [v7](../rollback_checkpoint_v7/README.md): default
sixteen workers, bounded support through thirty-two, dependent continuations
released after their own persisted prefix, and full client hashing with a
1 MiB buffer. All task evidence, paired inputs and per-call isolation remain.
Read the [frozen protocol](PROTOCOL.md) for budgets and interpretation limits.

```powershell
python -m unittest discover -s experiments/dependency_memory/rollback_parallel_v8 -v
python -m experiments.dependency_memory.rollback_parallel_v8.run prepare --output tmp/v8-prepared --workers 16
python -m experiments.dependency_memory.rollback_parallel_v8.run simulate --bundle tmp/v8-prepared --output tmp/v8-fixture --workers 16
python -m experiments.dependency_memory.rollback_parallel_v8.run audit --bundle tmp/v8-prepared --run tmp/v8-fixture --snapshot
```

Use fresh paths. `live_benchmark prepare` freezes a separate 64-call ABBA
throughput probe within the prepared bundle; `live_benchmark launch --live`
explicitly dispatches it. The 24-task pilot is separate, capped at 192 calls.
Run these live allocations serially. Never retry, replace, extend or relaunch
an admitted allocation. Use the archived source for historical audits.

`benchmark.py` imports sealed v7 timing evidence and compares identical fixed
job durations under old and new schedules. Its optional sleep workload is
synthetic and makes zero model calls. Neither result proves provider scaling.
Only saved live probes establish the observed local throughput at higher load.
