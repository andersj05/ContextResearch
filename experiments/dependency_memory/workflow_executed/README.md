# Executed workflow follow-up

The [frozen contract](CONTRACT.md) specifies twelve deliberately controlled
scenarios, 48 actual subprocess observations, five methods and 108 Luna 6 medium
requests. This exercises narrow query scopes and executable failures/recoveries;
it is one authored fixture family, not twelve untouched real-world tasks.

The [capture](capture.json) retains source/runtime bytes and actual outputs.
`capture.py` refuses to overwrite it. Offline tests independently reexecute all
48 recorded source/runtime combinations and verify return codes and artifacts.
No model is called during those tests. The previous pilot and its frozen files
are imported or hashed, never changed. The subscription transport is versioned
separately only to allocate 108 requests; its profile remains the prior audited
September 29 profile. The shared request envelope does not change study identity.

```powershell
python -m unittest experiments.dependency_memory.workflow_executed.test_executed -v
python -m experiments.dependency_memory.workflow_executed.analyze experiments/dependency_memory/results/workflow_executed_2026-09-29
```

Use `preflight --executable ... --global-instructions ... --output ...` for a
fresh zero-generation audit, then `run --directory ... --prepare ...` to freeze
the manifest. Commit before `run --directory ... --launch --executable ...
--global-instructions ...`. Launch refuses existing call directories and never
retries an identity. A stopped launch remains stopped.

All costs include writers. Model credits, local resources and unknown account
debit remain distinct. No native-compaction or production-savings claim follows.
