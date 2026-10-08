# Rollback subscription implementation and calibration

October 8, 2026. E1 calibration complete; authored E2 engineering pilot in preparation.
The user selected their existing Codex
subscription for GPT-6 Luna and explicitly removed token/cost budget concerns
for completing these tests. This supersedes the direct-API preference and
credential question; no API key is needed for this route.

The [versioned adapter](../experiments/dependency_memory/rollback_pilot/subscription/README.md)
uses the installed official Codex app-server and ChatGPT sign-in. Its
[E1 contract](../experiments/dependency_memory/rollback_pilot/subscription/CONTRACT.md)
separately records the authored calibration schedule, information access,
accounting assumptions and unknown-outcome stops. The [original E0 evidence](ROLLBACK_E0_IMPLEMENTATION_2026-10-08.md)
remains frozen. Scientific checkpoint C75 and draft v0.42 are unchanged.

The installed CLI is `0.162.0-alpha.2`. Fresh no-auth localhost probes verify
one HTTP attempt for ordinary output, attempted tool use, HTTP 503, truncated
stream, missing usage and duplicate answers. Additional probes bind the coding,
writer and K/R interfaces. The actor has fixed global instruction text and
allowlisted harness wrappers; every tool attempt is rejected. This is a
client-side audit, not proof of an empty tool registry or server-side internals.

No configurable 16,384-token output ceiling is established for this client.
The subscription amendment uses provider-default output and records the broader
published model envelope as a conditional planning assumption. Byte admission,
token telemetry, calculated credits and actual account usage remain separate.
The original API USD estimate cannot price these subscription calls.

All **eight live E1 requests completed**, passed their strict format checks and
returned complete token telemetry. The two terminal candidates were correct;
the coding answer passed all three retained tests in isolated Docker. No tool
items, unknown usage or identity retry was observed. The archive verifies eight
identities, 45 source bindings and 32 evidence files. This is calibration success,
not evidence of a rollback benefit.

| E1 usage | Observed value |
|---|---:|
| Input tokens | 21,568 |
| Cached input tokens | 0 |
| Output tokens, including reasoning | 1,509 |
| Reasoning subset | 514 |
| Calculated subscription planning credits | 0.0727825 |
| API-key model calls / API-dollar spend | 0 / 0 |

Actual subscription account charges are unavailable. The calculation uses
dated published credit rates, not API token prices, and does not add reasoning
twice. There was no token or cost budget stopping gate; unknown transport or
metering would still have stopped the allocation for scientific validity.

The [result bundle](../experiments/dependency_memory/results/rollback_subscription_2026-10-08/README.md)
keeps raw structured requests, visible final answers, usage events, append-only
SQLite accounting and verification separate from this finding. No opaque
reasoning transcript or credentials are archived.

The proposed LiveCodeBench cohort remains unprepared: source permissions and
reference programs are unresolved. A separately disclosed [authored source amendment](../experiments/dependency_memory/rollback_pilot/cohort_v1/CONTRACT.md)
provides twelve original coding tasks alongside the specified twelve math tasks
for a complete engineering pilot. Every coding reference passed all 13 retained
tests in Docker (156 executions total); ten additional runner invariants pass.
Its structural difficulty labels are not benchmark ratings. E2 outcomes will be
reported separately after the exact cohort and new 312-call allocation are frozen.
