# Executed workflow follow-up v1

September 29, 2026. The user authorized further experiments after the 36-call
Luna 6 pilot. This is a new **108-call** allocation, not a continuation or retry
of any prior launch. Freeze all code, captured inputs and schedule before live
dispatch. No model-answer-dependent case selection, prompt or cap changes.

## Question and evidence status

Does the five-method comparison remain accurate when queries select fewer checks
and receipts come from actual failed, repaired and superseded command runs?
The previous pilot's indexed arm retrieved every check. This follow-up retains
the existing caps and methods but varies query scope and executes the controlled
changes instead of changing return codes or artifact hashes in JSON.

Use twelve deliberately scripted episodes of one small standard-library Python
project. Its tests exercise an arithmetic function, its repository check verifies
source/documentation and an external readiness marker, and its paper build
produces Markdown and HTML from source. These are constructed workload scenarios
with real subprocess outputs, not naturally occurring incidents, twelve separate
workflow families, native-agent runs or the original packet's held-out episodes.
The implementer sees every scenario. Do not make a held-out claim.

The fixed scenarios are: unchanged success; later test failure; recovered tests;
later repository-check failure; recovered repository check; replaced HTML;
missing HTML; untested new source; partially checked revision; late selection of
an older source; irrelevant failed check; and fail/recover/fail on one snapshot.
Each gets a distinct fixture value from seed 2026092902. This is a data/schedule
seed; no provider sampling seed is exposed. There is no output padding. Capture
the exact source bytes, declared runtime-state changes, argv, stdout/stderr,
return code, artifact bytes and hashes, timings, and interpreter identity.
Snapshot identities hash the declared source files; runtime state is explicitly
excluded, allowing a test or check to fail on unchanged source. The harness
executes only its own fixed commands, never commands from model output or traces.

## Timing, methods and grading

Use the previous public rule and five methods: checked JSON proposals, direct
records, raw indexed recovery, strong prose and full history. Charge two writers
and a final call for checked/prose, and one final call for each other arm:
nine calls per episode, 108 total. Every method sees the same evidence.
At A retain at most **4096 UTF-8 bytes**. Then reveal intervening observations
and a possible-check scope. At B retain at most **1536 UTF-8 bytes**. Only then
reveal final source, artifact inventory and a nonempty subset of that scope.
The scope tells which check names can matter; it does not reveal the final source.

At A checked/direct preserve the latest receipt per source/check. At B they
filter by announced scope using bounded parent plus new observations only.
Checked proposals must equal those complete receipt objects; reject malformed,
altered, missing or extra tuples, then use deterministic direct fallback if it
fits. If a representation cannot fit, retain empty memory and record infeasibility;
do not change caps or recover evicted source. Prose gets the same scope explanation
and byte caps, with oversize output rejected rather than truncated.
The archive arms explicitly retain every raw observation; indexed recovery
retrieves every run of requested checks, including failures and older snapshots.
Full history reads every run. Archive storage and retrieval are separate resources.

The unchanged packet grader scans the complete chronological ledger independently
of memory and scores exact ready/needs_work/evidence. Host normalization only
removes null evidence fields from the fixed provider schema. The final question
is a reporting contract, not a proof of arbitrary program correctness. Post-run
diagnostics compare admitted tables with raw-ledger truth; prose sufficiency can
remain unknown. No grader feedback reaches the actors, and there is no action
guard. Offline controls independently check expected work for all twelve cases.

## Transport, budget and stop rules

Use `gpt-6-luna`, medium effort, default Standard tier and existing ChatGPT
subscription. Reuse the September 29 audited client profile and request envelope,
with a fresh four-case no-auth preflight on this study's largest public input.
Pin the exact executable, profile, instruction and implementation hashes. The
model alias is mutable; an immutable revision and sampling seed are unavailable.
There is no API-key setup, API-dollar spending, purchase or quota reset.

Authorize at most **108 single-in-flight dispatches** within a separate
**20 token-derived planning-credit** ceiling, with **7.65 credits reserved**
before each dispatch. These are planning units, not measured account debit.
Reuse the prior verified request/body limits (100000/131072 bytes), conservative
input/output bounds and fixed tool/instruction registry. Use a fresh empty
temporary cwd, process and ephemeral thread per request; no previous session,
repository files, evaluator files, archive tools or opaque reasoning carryover.
The declared wrapper/clock registry remains visible; accepted turns contain no
tool attempt. Client checks do not prove server-internal erasure.

Write each unique request and reservation before generation. A transport failure,
tool attempt, source/config drift, model reroute, uncertain usage or allocation
exhaustion stops the run. Never redispatch an attempted identity. Metered malformed
answers count as policy failures. Missing outcomes retain their denominator and
make the complete comparison unavailable. Do not silently launch a continuation.

Use the already reviewed September 29 Standard rates: input 2.5, cached input
0.25, output 12.5 credits per million. Reasoning is included in output. Record all
writer/final costs, cache-neutral costs, local CPU/elapsed/byte measures, archive
storage duration and capture costs separately. Human time and attributable account
debit are unknown; do not make a fully priced production-cost claim.

## Analysis fixed before launch

Report exact success /12, false-ready decisions, malformed answers, memory
infeasibility, fallbacks, per-case answers, retained-table sufficiency and costs.
Compare indexed versus full input tokens on the cases with narrower final scopes,
including any accuracy difference. Report all cases even when they are easy.
Use paired descriptive outcomes only: these related scenarios do not support
population significance. Retain direct records as the central baseline; no
further candidate-mechanism complexity is justified by a tie at higher cost.
The original packet's untouched real-workflow criterion remains unassessed.

Sources and previous client audit:
[previous contract](../workflow_eval_live/CONTRACT.md),
[model](https://developers.openai.com/api/docs/models/gpt-6-luna),
[app-server](https://learn.chatgpt.com/docs/app-server),
[pricing](https://learn.chatgpt.com/docs/pricing).
