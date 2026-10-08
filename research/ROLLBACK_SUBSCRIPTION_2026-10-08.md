# Rollback subscription implementation and calibration

October 8, 2026. Work in progress. The user selected their existing Codex
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

Saved artifacts and final outcomes will be recorded under
`experiments/dependency_memory/results/rollback_subscription_2026-10-08/`.
Calibration outcomes do not measure a rollback benefit. The real coding cohort,
source/reference/test verification and a frozen E2 amendment remain required
before the complete task comparison.
