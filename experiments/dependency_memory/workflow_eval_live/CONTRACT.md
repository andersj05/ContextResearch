# Luna 6 observed-handoff development launch v1

September 29, 2026. The user explicitly requested live tests with Luna 6 and a
comparison of results. This separately frozen development launch preserves the
[offline packet](../workflow_eval/PROTOCOL.md), its zero-call historical state,
and the still-unperformed twelve-episode held-out study.

## Scope and fixed schedule

Run **36 calls** on `gpt-6-luna`, medium reasoning, Standard/default speed:
four constructed development conditions times two checked writers, two prose
writers, and five terminal decisions. The five methods are checked proposals,
direct records, indexed raw recovery, strong prose, and full history. One real
local capture supplies all four conditions. They are correlated controls, not
four independent real tasks. Do not claim untouched workflows or native-agent
performance. No method/prompt/cap tuning after launch.

Conditions are: the observed unchanged successful workflow; a constructed new
source snapshot disclosed after the second handoff; a constructed later failed
test run disclosed between handoffs; and a constructed replacement of the HTML
artifact disclosed after the second handoff. The latter three are mutations,
not observed incidents. All final scopes request paper, repository and tests.
Thus the indexed control retrieves the entire requested workflow and may tie
full history; this easy control is intentional. The four writer/final schedules
are ordered deterministically with seed 20260929. No model sampling seed is
exposed. There is no separate paid smoke request.

At the first boundary all methods see the three original command receipts plus
the exact stdout/stderr text. Command names, source trees, return codes, run IDs
and artifact hashes are public tool metadata. At the second boundary reveal
the same intervening observations and requested scope to every arm. The source
revision and final artifact inventory arrive after the second memory reduction.
Keep the packet's 4096/1536 UTF-8 byte limits for memory-only methods. The later
failure is supplied after the first boundary, so it must survive the second.

## Implemented methods and terminal contract

Checked writers return a JSON receipt-list inside a `memory` string. Admission
verifies exact complete receipt tuples for the latest run per snapshot/check
available at that boundary. It rejects omissions, changes, duplicates and
oversize strings. On rejection it falls back to direct records made only from
still-available evidence. At the second boundary this means the bounded parent
and new public observations, never the original deleted history. Charge both
writers, every check and fallback. This domain-specific checker is not an
unknown-schema extractor or the earlier ID-only certificate.

Direct records use the frozen packet's explicit public-rule projection. Prose
writers get the same public rule, exact-identifier guidance and caps. Invalid
or oversized prose becomes an empty admitted memory with an explicit failure,
not truncation or a free retry. Indexed recovery builds an index over every raw
observation before the target is known and retrieves all records for the final
required checks, including the later failure. Full history reads every original
and intervening observation. Both archive arms have declared additional storage.

The existing independent terminal grader remains byte-for-byte frozen. The
provider uses a fixed object schema with nullable `paper`, `repository`, `tests`
evidence fields (null means absent); the host removes null fields before exact
grading. This serialization adapter avoids unsupported open-ended provider maps
and does not alter the grader's required evidence. Reject unknown fields and
types rather than coercing them. Scoring is deferred until all calls complete.
An action guard is not part of this development comparison.

## Transport, isolation and resource ceiling

Use the official installed Codex app-server through existing ChatGPT login;
no API key, credit purchase, reset or fallback model. The user's live-test
instruction supplies authorization for this new bounded run. The earlier
USD 20 proposal is not converted to credits: API-dollar spending is zero, and
this launch has a separate conservative **20 planning-credit** ceiling with
**7.65 credits reserved before every dispatch**, at most one call in flight.
Planning credits are token-derived, not measured account debit. A missing or
uncertain usage record retains its reservation and stops the run.

Before launch pin the installed executable, profile, global instruction and
source hashes and collect a fresh no-auth loopback audit. The installed client
now serializes base instructions as a developer message and wrapper tools in an
`additional_tools` item; the September 22 audit rejected that change before any
real model call. The new audit must allowlist every message and the exact
wrapper/clock registry, reject any other tools/state, prove one HTTP attempt
under normal output, tool-call, 503 and truncated-stream controls, and inspect
the maximum-sized actual public request. Accepted live turns contain no tool
items and one complete usage event. Every call gets a fresh process, empty
temporary working directory and ephemeral thread, no workspace roots, prior
conversation, evaluator files, skill catalog or environment context. The global
GitHub-auth instructions are declared fixed public background. No server-internal
erasure claim follows from this client audit.

Public requests are capped at 100,000 bytes and audited complete serialized
bodies at 131,072 bytes, including a 20,000-byte fixed-overhead allowance.
Reported model input must remain below 272,000 tokens and output at most
128,000 including reasoning. The app-server does not expose a verified hard
output-token limit here, so reservation uses the published model maximum and
conservative long-context multipliers. The rollout guard permits one generation;
it is not a 32,768 output-token cap. Freeze the mutable alias, medium effort,
CLI version and date; no immutable provider snapshot is exposed.

Write the exact public request and durable reservation before the generating
RPC. Never repeat an existing identity. A transport/model error, reroute, tool
attempt, unexpected context, source drift, usage uncertainty or allocation
failure stops the whole launch. Malformed but fully metered policy answers
remain failures in the fixed schedule. No resuming/retrying after dispatch.

## Accounting and interpretation

Use the September 29 official Standard Codex rates: 2.5 input, 0.25 cached input
and 12.5 output planning credits per million tokens. Reasoning is a subset of
output. Report cache-discounted and cache-neutral model credits separately,
plus measured local CPU/elapsed time, reads/writes, index bytes and retention
duration. Human implementation time and attributable account debit are unknown.
Do not convert resource vectors to total dollars or claim production savings.

Report exact decisions out of four, false-ready errors, byte failures, checker
fallbacks, retained-fact sufficiency, all 36 request dispositions, token usage
and model costs. A table tied at 4/4 demonstrates only feasibility. The packet's
held-out engineering go criterion remains unassessed. With any missing answer,
retain the full scheduled denominator and mark the comparison incomplete.

Provider sources reviewed September 29:
[app-server](https://learn.chatgpt.com/docs/app-server),
[Luna 6](https://developers.openai.com/api/docs/models/gpt-6-luna),
[Codex token rates](https://learn.chatgpt.com/docs/pricing).
Client serialization and account availability are checked locally, separately
from these public documents. Results: **unperformed until the saved ledger is analyzed**.
