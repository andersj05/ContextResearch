# Matched checkpoint rollback v7

This package tests deletion of one failed visible branch while preserving the
exact pre-failure checkpoint, all released task facts, public feedback and one
common lesson. Read the [protocol](PROTOCOL.md) before interpreting any result.
This is a new study; historical v4-v6 sources and evidence remain unchanged.

The first bounded development pilot has 24 authored ledger tasks, three stages,
four actions and eight parallel Luna-medium subscription workers. Its ceiling
is 192 admitted calls. Worker support is 1-16 and is frozen per allocation.
Only `launch --live` makes model calls; preparation, tests, fixtures and replay
are offline. No API key or purchased fallback is used.

The current client still advertises generic resource helpers. The v7 transport
pins their declarations, checks a disabled empty MCP inventory before every
generation and rejects any observed tool use. Read the protocol's compatibility
amendment; advertised helpers are not described as absent.
Its saved clock-plus-answer diagnostic also records a client event limitation:
an attempted clock helper can accompany an accepted answer without an exposed
tool event. One-generation isolation prevents a subsequent model request from
consuming any returned tool information; zero observed tools is not a proof of
zero attempted tools.

```powershell
python -m unittest discover -s experiments/dependency_memory/rollback_checkpoint_v7 -v
python -m experiments.dependency_memory.rollback_checkpoint_v7.run prepare --output tmp/rollback-v7-prepared --workers 8
python -m experiments.dependency_memory.rollback_checkpoint_v7.run simulate --bundle tmp/rollback-v7-prepared --output tmp/rollback-v7-fixture --workers 8
python -m experiments.dependency_memory.rollback_checkpoint_v7.run audit --bundle tmp/rollback-v7-prepared --run tmp/rollback-v7-fixture
```

Use fresh output paths for each allocation. Inspect an existing launch rather
than retrying any admitted identity. Account/source/isolation/accounting failures
stop all admissions; unknown responses stop their own trajectories. Completed
allocations cannot be extended. Prepared sources must stay unchanged during a
run. Use `audit --snapshot` for historical replay after source development.

K/R initial requests must differ only in the failed `trial` record. All released
packets and prior successful generated records survive in both conditions. The
shared preparation is charged once. A positive, negative, tied or infeasible
small pilot remains development evidence, not a general rollback claim.
