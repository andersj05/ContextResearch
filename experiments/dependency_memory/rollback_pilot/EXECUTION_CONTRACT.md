# Rollback controller and data contract

October 8, 2026. Design v0.2, not an implemented or audited live adapter.
This contract makes the experiment reviewable at the request and record level.
It supports [E0 through E2](EXPERIMENT_SUITE.md); later policy differences are
declared in the suite rather than silently added to this controller.

## Components and access

| Component | May read | May write or return |
|---|---|---|
| Task builder | Pinned data, local seeds, evaluator references | Separate actor tasks and evaluator records |
| Controller | Explicit actor records, public feedback, schedule and usage ledger | Allowed context fields and dispatch reservations |
| Luna actor and writers | Only the serialized text for that call | Typed public artifacts |
| Public checker | Candidate plus public predicates/tests | Bounded public receipt |
| Terminal grader | Candidate plus original task and reserved evaluation material | Evaluator-only score after scheduled generation |
| Analysis | Frozen records, grades and costs | Tables and findings; no feedback into an active episode |

The controller is trusted code, not another model with unrestricted file access.
Use distinct actor/evaluator data types and an allowlist renderer, not a prompt
instruction asking the model to ignore hidden fields. The complete raw transcript
is retained for audit but is not reachable through an actor tool or session.

## Explicit record schema

All model outputs are one JSON object, with no Markdown fence or surrounding
text. Reject duplicate keys, unknown fields, nonfinite numbers and wrong types.
Do not repair malformed JSON with another model or extract an attractive candidate
from an otherwise invalid response. Structural validation never upgrades prose
claims into proven facts. Source/evidence IDs must refer to supplied records.

| Record | Required fields and types |
|---|---|
| Checkpoint | `facts`: list of `{statement: string, source_ids: list[string]}`; `open_requirements`: list[string]; `tentative_options`: list of up to three `{id: string, method: string, unverified_assumptions: list[string]}`; `possible_checks`: list[string] |
| Branch | `status`: `candidate` or `continue`; `chosen_option`: supplied ID or `new`; `assumptions`: list[string]; `observations`: list of `{statement: string, source_ids: list[string]}`; `artifact`: domain artifact or null |
| Lesson | `failure_kind`: string; `evidence_ids`: list[string]; `refuted_claims`: list[string]; `retained_observations`: list[string]; `uncertainties`: list[string] |
| Generic summary | `summary`: string |
| Math artifact | `values`: list of exactly the task's declared number of integers |
| Code artifact | `code`: complete standalone Python source string |
| Terminal output | The domain artifact alone |

`candidate` requires an artifact and `continue` requires null. An unsupported
new method is allowed; the experiment must not force the model down a known bad
route. A checkpoint may have zero useful facts; record this as a restatement
checkpoint rather than inventing reusable progress.

The host creates receipt IDs, candidate IDs, hashes and schedule labels. These
labels cannot be altered by model output. Never pass a held-out membership flag,
condition ID, desired outcome or evaluator note into the prompt. L and S each
have a 1,024 visible-token cap; their schemas count toward that cap. Oversize
writer outputs are preparation failures, not silently truncated summaries.

## Rendering the contexts

Use the identical common instruction and stage instruction from [PROMPTS.md](PROMPTS.md).
The original task persists independently of any model-generated checkpoint.
For each continuation serialize a single JSON data object with ordered logical
fields `task`, `checkpoint`, `trial`, `feedback`, `lesson`, `summary`. Unused fields
are null. Serialize UTF-8 JSON in that fixed top-level field order, with no
insignificant spaces and explicit JSON escaping. Preserve nested schema field
order deterministically. Do not alphabetically move the trial after the lesson:
failure evidence and the lesson must follow the trial in K. All continuation
requests have the same message roles.

| Arm | trial | feedback | lesson | summary |
|---|---|---|---|---|
| K | B | F | L | null |
| R | null | F | L | null |
| Z | null | F | null | null |
| G | null | F | null | S |

Task and checkpoint are identical in every arm. B contains chosen-route artifacts
and earlier observations, excluding final F. Preserve retained field bytes;
do not rewrite a weak checkpoint or strengthen a lesson for one condition.
In real episodes F/L may legitimately repeat information from B. The routing
fixture uses a B-only marker absent from fixed F/L to test raw-branch exclusion;
it does not assert that every semantic trace of B has been erased.

Before dispatching primary continuations, preflight both K and R. A K input
exceeding the whole-request cap makes that pair capacity-infeasible, not an R
victory. No truncation, provider auto-compaction or tool-output masking may change
the intended inputs without a new version. Record exact serialized request hashes
and hashes of the common C/F/L fields separately.

## E2 controller sequence

```text
read frozen task and create ledger row
generate checkpoint once
if checkpoint interface invalid: record preparation failure and end task
generate branch step, at most twice
  candidate -> public check -> stop on mismatch or public pass
  valid continue -> next planned branch slot, if available
  malformed, incomplete, runtime or timeout -> record disposition and stop
if no eligible public mismatch: keep initial disposition and end task
generate lesson and generic summary independently from the same C, B, F
validate each writer independently
preflight every condition and the common K/R pair
run permitted scheduled continuations with no cross-draw memory
grade terminal artifacts after the scheduled generation block
close ledger with actual costs, missingness and hashes
```

Generate L then S on even task indices and S then L on odd indices. Let the
domain-local frozen task index be t=0..11. Use a rotation of `[K,R,Z,G]` by
`t modulo 4` for draw one, then the reverse of that order for draw two. Missing
conditions leave empty scheduled slots; do not renumber later identities.
Interleave math and coding tasks by their precomputed hash order. Execute one
request at a time for this small pilot to simplify accounting and avoid separate
worker states. Provider randomness is not controlled by the local schedule seed.

The primary K/R pair needs valid L; G alone needs valid S; Z needs neither.
Known unusable writer artifacts block only their dependent conditions. Unknown
transport or usage state stops the whole launch because reservation reconciliation
and input provenance would be uncertain. Do not silently resume an ambiguous call.

## Model transport

Proposed settings remain `gpt-6-luna`, medium reasoning, Standard processing.
Use independently reconstructed requests, no previous-response/conversation ID,
no copied opaque reasoning/compaction items, and no model tools. Do not forward
entire provider output arrays. Allowlist the visible artifact text and required
usage metadata. Document the chosen endpoint and all actual serialized fields.

The official reasoning guide documents `max_output_tokens` as including reasoning,
visible text and non-visible formatting; it can terminate before a visible answer.
It also discusses encrypted reasoning in stateless workflows. A client-input audit
is therefore required even when storage is disabled. This does not expose or
certify private provider internals. [@openai-reasoning2026]

Proposed per-call caps: 32,768 complete input tokens and 16,384 generated tokens.
Pin token counting and include message/schema overhead in admission. Check actual
provider usage against the audited accounting. An unbounded or unverified wrapper
cannot support the numerical budget guarantee below. Retain requested/returned
model, timestamps, client and schema version, routing metadata when exposed, and
the precise caps. Do not invent a dated model snapshot or provider seed support.

The existing subscription transport can be evaluated as an alternative, but the
October 7 audit did not establish its output cap. Credentials, account access and
a new launch contract remain implementation work. Never reuse the old allocation
or infer API dollar spend from subscription planning credits.

## Reservations and costs

Published Standard API rates rechecked October 8, 2026 are 0.10/0.01/0.125/0.50
USD per million input/cached-input/cache-write/output tokens. Price every input
at the highest of these input categories for a conservative reservation:
[@openai-gpt6-luna2026]

```text
per_call_reserve = (32768 * 0.125 + 16384 * 0.50) / 1000000
                 = USD 0.012288
pilot_reserve    = 320 * per_call_reserve = USD 3.93216
```

The proposed USD 5 envelope is only model usage, with enforced caps and no paid
tools, automatic retries, regional or speed premiums. Recheck rates at launch.
Record exclusive billing buckets; do not charge cache-write tokens again as
uncached input or reasoning again on top of output. Missing usage leaves the
reservation locked and stops progression.

Persist `planned -> reserved -> dispatched -> completed/unknown` transitions
before proceeding. Each row binds launch/task/stage/arm/draw identity, request
hash, maximum liability, dispatch time, usage and disposition. Never overwrite
an existing dispatch row. A crash after possible dispatch is unknown and charged;
a response must be reconciled by its identity before any later launch. Disabling
application retries is insufficient if the client or SDK retries internally.

## Artifacts for implementation handoff

The proposed executable modules are task loading, context rendering, public
checking, isolated code execution, transport, reservations, orchestration and
analysis. Their interfaces are deliberately separate so a fake transport can
exercise the full sequence without credentials or model calls.

The eventual launch package must include `manifest.json`, `tasks_public.jsonl`,
separate evaluator task records, `schedule.jsonl`, immutable shared preparations,
sanitized exact requests, response artifacts, usage ledger, terminal grades and
report. Credentials and authorization headers are never saved. Private grading
material must not be nested in data structures supplied to an actor renderer.

Reserve result directory naming only after the actual launch ID exists, for
example `experiments/dependency_memory/results/rollback_pilot_<launch_id>/`.
Register existing stable result paths before committing evidence. Empty planned
paths and this design manifest are not saved experiment results.
