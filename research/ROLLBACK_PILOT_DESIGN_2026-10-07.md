# Checkpoint, explore, retain a lesson, and roll back

October 7, 2026. Research and design review; **zero new model calls**.
The [draft pilot](../experiments/dependency_memory/rollback_pilot/DRAFT_PROTOCOL.md)
and [draft prompts](../experiments/dependency_memory/rollback_pilot/PROMPTS.md)
are unperformed plans, not a frozen launch or an empirical result. Earlier
allocations remain closed. The existing manuscript and claim C75 are unchanged.

For the expanded October 8 specifications and implementation handoff, start with
[the review packet](../docs/ROLLBACK_REVIEW_HANDOFF_2026-10-08.md). This note keeps
the October 7 source/transport observations separate from that later design work.

## Recommendation

Test one explicit context intervention on `gpt-6-luna`: after a naturally failed
branch, compare keeping that branch against replacing it with a failure lesson.
Both primary conditions must receive identical objective feedback and the exact
same lesson. Begin with visible task artifacts at model-call boundaries, rather
than claiming to inspect or remove proprietary hidden reasoning or KV state.

The initial implementation can be a small external controller: save the text
checkpoint, collect a branch and its check result, generate the lesson, then send
the chosen reconstructed context in a fresh request. Keep the complete transcript
in an evaluator-only archive. The actor sees only the active context permitted
by its condition. This requires no model-weight changes or direct cache access.
Discarding a branch cannot recover computation already spent exploring it; any
resource benefit must come from subsequent work.

Separate three questions:

1. Does branch removal help recovery when a public check identifies a failure?
2. Can the model choose useful checkpoints and rollback times itself?
3. Does a complete rollback policy improve success at a fixed total budget over
   ordinary repair, compaction, and independent retries?

The proposed 24-task development pilot addresses the first question and exposes
engineering failures. It is too small to establish a modest general improvement.
Do not use its conditional recovery result as an end-to-end policy result.

## Primary-source comparison

These are bounded primary readings, not independent replications. Prior readings
in the conversation are included only where the original text was inspected.
No inherited corpus review label is upgraded.

| Source and reading scope | What is already established as a proposed mechanism | Consequence for this pilot |
|---|---|---|
| Thought Rollback, v1, Sections 3.3 and 4.1-4.4 [@chen2024thoughtrollback] | Branch from before a diagnosed error and carry its analysis into subsequent attempts; the broader thought structure is retained | Rollback with lessons is prior art. Our comparison must distinguish context removal from feedback and additional attempts |
| LongSeeker, v1, Sections 3.1-3.4 and 4.1-4.2 [@lu2026longseeker] | Its Rollback removes the suffix and retains the reason and transferable information | Very close precedent. Its complete operation set and training/evaluation do not isolate our specific deletion contrast |
| ARC, v1, Sections 3.1-3.3 and 4.3 [@arc2026] | Revises interaction memory and checklist; includes ablations disabling memory revision | Active correction of working memory is also prior art; results concern the tested search setups |
| SCoRe, v2, Sections 3 and 6.1-6.2 [@kumar2024score] | Trains intrinsic self-correction and compares sequential correction with parallel sampling | Same number of attempts is an incomplete cost comparison; ordinary retry and repair must be strong controls |
| EvalPlus, v3 abstract and official repository's evaluation/container sections [@liu2023evalplus] | Stronger executable tests expose failures missed by weaker tests | Keep feedback tests and terminal grading separate; passing a few examples is not sufficient correctness evidence |
| LiveCodeBench, author project page's evaluation and date-filtering sections [@jain2024livecodebench] | Dated code tasks and a self-repair scenario | A candidate external coding cohort. Pin an actual release; the benchmark name does not certify absence from Luna's training |
| MATH-500, publisher dataset schema/viewer [@math500dataset] | A 500-row test collection with problem, solution, answer, subject, level and ID fields | Candidate later transfer benchmark. Gold-answer feedback is an oracle intervention, not natural error recognition |

The general idea is not new. A contribution would require a reproducible advantage
under declared evidence, compute, and context access, plus comparison against the
close methods above. This review does not certify novelty of any implementation.

## What should be measured

Use notation `C` for the checkpoint, `B` for the subsequently generated branch,
`F` for public failure feedback, and `L` for a lesson generated once from `C,B,F`.
The main contrast is `C+B+F+L` versus `C+F+L`. Same model, same instructions,
same terminal task, same feedback and lesson, same continuation allowance.
The extra raw information in the first arm is intentional: it is the treatment.

Both arms must start as reconstructed requests, without replayed hidden reasoning
items. Otherwise deleting the visible branch can also reset an opaque state in
only one arm. Such a comparison would not isolate visible-context removal.

A shorter prompt alone is not a reasoning improvement. Report correctness,
actual input/output/reasoning usage, cache categories, and elapsed time separately.
The initial exploration and lesson generation were real costs, even if replayed
across experimental arms. A later deployment comparison must charge each policy
its full standalone costs and permit a cheaper baseline to use its remaining
budget for additional attempts.

If `C` contains only the original question, rollback plus a lesson is a restart
with feedback. Record that fact; do not call it preservation of earlier work.
Report cases with substantive pre-branch progress separately. Checkpoints must
precede the trial-specific assumptions they are intended to undo.

## Tasks: start where failure is checkable

**Math:** start with bounded constructive problems with exact public constraints:
integer assignments, modular constraints, and small graph-coloring constructions.
A candidate can be rejected by a violated equation or constraint without exposing
a hidden solution. Independently check instance feasibility before freezing the
task set; do not select instances based on which treatment wins. These are narrow
search/math diagnostics, not competition-math or theorem-proving performance.

**Coding:** use a pinned, standard-library Python subset of LiveCodeBench, with
public examples as feedback and all reserved tests for terminal scoring. Begin
with a fixed easy/medium/hard stratification to expose feasibility across difficulty.
Public-test passes with private-test
failures remain in the cohort but do not receive a hidden-test-derived rollback
signal. EvalPlus is useful for runner validation or later transfer; it is not
automatically an uncontaminated or sufficiently difficult Luna cohort.

No inflated 100k-token failure stories, manually planted bad reasoning, or forced
wrong branches in the primary cohort. Natural branches may be short. Record
failure frequency and branch lengths before deciding whether a later long-context
study is justified. Constructed fixtures belong only to engineering checks.

MATH-500 is deferred: either supply only problem-derived checks, or explicitly
label a separate correctness-oracle condition. Never provide a reference solution
to a lesson writer or use it to silently repair the lesson. Answer-only grading
also does not certify a proof.

## Luna and transport review

Official documentation was checked October 7, 2026. The proposed model is
`gpt-6-luna`, medium reasoning, Standard processing. Its public page exposes that
alias rather than an immutable dated snapshot. Record requested/returned model,
effort, provider metadata, time and client version; do not invent reproducibility
from a seed or snapshot the service does not expose. "Small" here refers to the
intended efficient model tier; no parameter count is established. [@openai-gpt6-luna2026]

The Responses API is the cleaner proposed transport for this diagnostic because
it documents a total generated-token cap. Explicitly construct every input,
omit previous-response/conversation handles and replayed opaque items, and disable
model tools. `store:false` alone does not prevent reasoning continuity: encrypted
reasoning can be returned in stateless mode and carried forward by a client.
Audit actual request bodies, not only wrapper arguments. This is a client input
contract, not proof of the provider's private internals. [@openai-reasoning2026]

The existing subscription path remains a possible alternative. Its official
app-server exposes thread and usage controls, but current schema inspection did
not establish a per-generation output cap. It needs a fresh serialization and
budget audit before reusing any historical adapter. [@openai-codex-appserver2026]

Local read-only observations on October 7:

| Check | Observed result and limit |
|---|---|
| `codex --version` | `codex-cli 0.162.0-alpha.2`; CLI emitted sandbox temp/PATH-alias warnings but returned the version |
| Executable SHA-256 | `3553cd6e7df5a093d8cb8301cd8088a57e0971aba71ddbe0e67f7f44a15cdf68` |
| Experimental app-server JSON schema generation | Completed offline under ignored `tmp/rollback_schema_2026-10-07/`; searches of turn/start, thread/start, config and capability schemas found no named maximum-output-token field. This does not prove no configuration mechanism exists |
| Existing adapter | [Historical profile](../experiments/dependency_memory/workflow_eval_live/profile.py) excludes `max_output_tokens` from its request allowlist; its [contract](../experiments/dependency_memory/workflow_eval_live/CONTRACT.md) explicitly reserves against the model maximum. Do not alter or import its historical allocation |
| Code executor | Docker executable exists; querying the engine failed because its named pipe was absent. Availability of a functioning isolated runner is unverified |

No authentication values were read, no key was provisioned, and no model access
or current account entitlement was tested. No model-generated code was executed.

## Proposed size and resource envelope

The draft schedules 12 math and 12 coding tasks, at most 13 calls per task, plus
eight separate calibration/transport calls: **320 calls maximum**. This is a
ceiling, not a promise to fill unsuccessful task slots or an active allocation.
Inputs are proposed to stay within 32,768 actual tokens and total generated
tokens within 16,384 per call. The latter includes hidden reasoning and can
terminate generation before an answer. Calibration must check its adequacy.

For the direct API option, the documented Standard short-context rates are
$0.10 input, $0.01 cached input, $0.125 cache write and $0.50 output per million
tokens. Conservatively pricing every input token at the highest input category:

```text
320 * (32,768 * 0.125 + 16,384 * 0.50) / 1,000,000 = USD 3.93216
```

This arithmetic assumes enforced whole-request caps, no automatic retries, no
paid tools, and no regional/speed premiums. A proposed USD 5 model-usage ceiling
would provide headroom; this is not a prediction of actual spend or a total project
cost. Unexpected billing categories require a revised contract. [@openai-gpt6-luna2026]

At published Codex Standard token-credit rates, the same *hypothetically enforced*
caps would correspond to 91.7504 planning credits. This is not attributable account
debit or a conversion from the dollar budget. The subscription output cap is not
yet verified, so that number cannot serve as its launch guarantee. [@openai-codex-pricing2026]

## Implementation order and decision gates

1. Implement the offline task schema, exact math checker and four context renderers.
   Use fabricated fixtures to prove the intended inputs differ only as specified.
2. Validate an isolated coding executor and pin data/test artifacts. Keep host
   credentials, repository files, archives and hidden evaluator state inaccessible.
3. Select transport and billing route; pin prompts and actual input controls,
   hard limits, request accounting and a separate bounded launch manifest.
4. Run the eight calibration calls first. Halt on transport ambiguity, truncation
   or unusable formatting; amend a new version before proceeding if needed.
5. Run the fixed 24-task pilot without tuning or replacing easy/failed cases.
   If few eligible failures occur, report that feasibility limitation.
6. Only after this, design a powered held-out comparison and an autonomous,
   repeated-rollback policy with retry/repair and native-compaction controls.

Neither novelty nor a deployed-harness improvement follows from feasibility.
The immediate deliverable is a measurement that can distinguish benefit, harm,
and insufficient evidence without changing the question after seeing results.
