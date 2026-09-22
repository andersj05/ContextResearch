# Historical workflow handoff replay, v1

September 22, 2026. Offline, exploratory, zero new model calls. The selected
historical evidence has already been inspected. It is **not held-out evaluation**.
The historical failures were transport/accounting events, not demonstrated
compaction failures. The memory deletions and later queries below are new
counterfactual interventions on those real records.

## Task and selection

Use the last two attempt records in each of the four workers of the completed
`transfer_luna_2026-09-19_authorized` phase: eight records, selected by position,
not response quality. The final record in each worker is a transport failure;
three have dispatched and settled, one stopped before dispatch. Preserve source
file hashes, array positions, record hashes and the source commit. Do not copy
raw session logs into new tracked files. The runner reads existing evidence.

The later task is to produce an exact, local JSON handoff decision for an
attempt: its case ID, request hash, dispatch class, settled planning credit
equivalents, and retained reservation. `preflight_only` is eligible for its first
submission in the historical continuation; `dispatched` is not eligible for
replacement. Ambiguity must yield `unknown`, never permission to retry. This is
only one required component of a resumption plan. It does not authorize a launch
or substitute for the existing full phase, allocation and schedule audits.

The original `classify_attempt` function and its `exact` helper are extracted
with Python AST from the pinned local source, compiled without its imports or
top-level code, and used as the independent terminal reference. The new policy
adapter is checked against that source, including adversarial synthetic inputs.
No provider runner, client or historical collection script is executed.

## Information and timing

1. All methods read the same eight complete canonical attempt records.
2. First deletion: only the serialized, byte-capped memory remains.
3. Public reveal: two of four worker numbers. The pair is uniform over all six
   pairs and independent of response values.
4. Second deletion: filter to those workers and enforce the smaller byte cap.
5. Reveal one of the four records in that pair by case ID. Execute one handoff
   decision, with optional metered recovery from the declared archive.

There are 24 enumerated routes, not 24 independent task trials. Neither actual
pair nor target is supplied to the initial compactor. Identifiers, ordering,
tags, wrappers and exact amounts all count toward serialized UTF-8 memory.
Request hashes and case IDs are original opaque payloads, not a tiny catalog in
decoder code. No source records, evaluator objects, seed, record index, prior
proposals, feedback, file path or raw transcript enters the post-boundary policy.
Fixed source-independent schemas and the four worker numbers are public.

Interfaces are trusted Python functions, not security isolation. The environment
and grader retain truth to offer explicit costed tools and grade final actions.
The executor gets memory bytes, public reveals and that tool interface only.
No opaque model state or provider session exists in these offline replays.

## Methods

- `status`: retain request identity and outcome status; recover missing details.
- `fields`: retain an equally informed, lossless projection of all checker inputs.
- `compact_fields`: the same projection in a fixed ordered schema, removing the
  verbose-schema disadvantage. Presence/absence remains distinguishable.
- `repair`: start with status memory, check all eight declared obligations before
  deletion, emit a diagnosis packet, and replace insufficient entries with checked
  result receipts. This is one bounded repair pass, not learned feedback.
- `direct_receipts`: strong simple baseline that applies the same public rule
  directly and stores its result. It is expected to match or beat repair costs.

Use the same deterministic worker/chronological ordering in every packer. Greedy
whole-entry packing is a declared heuristic, not an optimal byte code. Recovery
may return a whole original record (`full`), an indexed critical-field projection
(`projected`), or be unavailable. The projected archive is an intentionally strong
cheap-recovery control available equally to every method. Its server computation
is charged; no retrieval of evaluator answers is offered.

## Costs and fixed grid

Memory caps in bytes: (512,256), (1024,512), (1536,768), (2048,1024),
(4096,2048). Additional total replay allowances after common initial observation:
1024, 4096, 16384, 65536 cost units. Checker prices: 0, 128, 1024 units;
tool call price: 128 units. One transmitted UTF-8 byte costs one unit.

Charge initial observations; every candidate/repair write and verification read;
diagnosis bytes; both boundary writes and subsequent reads; public reveals;
recovery request/response bytes and projection/check work; final output bytes;
and failed work already performed. Count every actual predicate evaluation,
including cache checks. A budget rejection stops dependent work without a free
answer. No padding of cheaper arms to fabricate equal realized expenditure.
Compare success at the same **maximum total allowance**, report actual spending
and separate byte/check/tool counts. These are explicit synthetic replay prices,
not tokens, dollars or measured total production cost. Python runtime and source
mining work are not priced by this model; the main claim must remain conditional.

The full workflow history's already-spent model tokens are historical sunk costs
outside this handoff replay. The fixed common initial observation is inside it.
Archive storage, index construction, tokenizer/cache billing and model execution
are unmeasured; do not infer savings over a deployed harness.

Also enumerate the complete descriptive allowance frontier: first run each
route with a nonbinding allowance, then evaluate every distinct successful
completion-cost threshold across all methods. This avoids choosing a favorable
single allowance between the coarse grid points. Policies do not adapt to the
allowance, so a route succeeds exactly when all its sequential charges fit.

## Scope and regression controls

Keep insufficient-memory, no-archive and cheap-archive outcomes. An oversized
candidate is never silently counted as retained. Check target invariance before
the first reveal, exact deletion at both boundaries, independent accounting,
unknown dispatch, retained reservations, contradictory preflight metadata and
unknown-versus-zero amounts.

Separately check receipt reuse under irrelevant metadata edits, relevant field
edits, absent-to-present fields, a changed checker version, changed task identity
and changed request payload. Hash the exact dependency projection, identity and
checker revision; a mismatch must invalidate the receipt. This cache check reads
the current evidence and reports that cost. It is not a free provenance oracle,
and is not silently added to the main unchanged-artifact replay.

No benefit over `direct_receipts`, inference on unseen workflow structures,
automatic natural-language rule extraction or new verification principle is
claimed. A later live experiment requires a new model/transport/budget contract
and an independently frozen task-structure split.
