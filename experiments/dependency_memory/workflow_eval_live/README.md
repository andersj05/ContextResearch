# Luna 6 live development comparison

See the [separate launch contract](CONTRACT.md). This is a 36-call comparison on
one observed local workflow and three explicitly constructed controls. It does
not complete the offline packet's twelve-episode held-out study.

The user authorized live Luna 6 tests on September 29. Model: `gpt-6-luna`, medium
reasoning, Standard/default tier, existing Codex subscription. API spending is
zero; a separate 20-planning-credit reservation bound applies. No purchase,
reset, implicit retry or fallback model is used.

The profile/audit/transport were derived from the preserved `luna6_revision`
adapter at commit `1590deb`, with a newly inspected serialization allowlist for
CLI 0.158.0-alpha.2.1, a larger audited request bound and a 36-call cap. The prior
adapter rejected the changed client before any real generation. The new no-auth
loopback audit verifies normal output, tool call, HTTP 503 and truncated stream
at the largest public input; accepted live outputs have no tools or prior state.
Visible wrappers and clock tools remain declared, so this is not an empty-tool
registry claim. Exact client and global-instruction hashes are in the preflight.

Offline checks:

```powershell
python -m unittest experiments.dependency_memory.workflow_eval_live.test_live -v
```

Prepare with `python -m experiments.dependency_memory.workflow_eval_live.run`
and `--prepare PREFLIGHT --directory RESULT_DIRECTORY`. The separate `--launch`
mode requires the frozen manifest, exact executable and global-instructions
paths. It creates the calls directory exclusively and refuses reruns. The
preflight command only inspects managed login/configuration and runs local
unauthenticated fake-provider checks; it never generates a real model response.

Analyze saved evidence with:

```powershell
python -m experiments.dependency_memory.workflow_eval_live.analyze experiments/dependency_memory/results/workflow_live_2026-09-29
```

Analysis reconstructs every public request from frozen source plus saved model
responses, rechecks admission/deletion, reconciles all usage and grades terminal
decisions independently. The cost table reports model planning credits only;
CPU, byte traffic and index storage duration remain separate raw measurements.
The held-out primary criterion and any claim of total production savings remain
unassessed regardless of this development outcome.
