# Rollback pilot: draft protocol v0.2

Date: October 8, 2026. Status: **unperformed, not frozen for launch**.
Governing rules: [experiment protocol](../../../docs/EXPERIMENT_PROTOCOL.md).
Rationale and primary sources: [design review](../../../research/ROLLBACK_PILOT_DESIGN_2026-10-07.md).
Prompts: [draft interfaces](PROMPTS.md). No historical allocation is reopened.

Review entry point: [handoff](../../../docs/ROLLBACK_REVIEW_HANDOFF_2026-10-08.md).
Operational details: [tasks and grading](TASKS_AND_GRADING.md),
[execution contract](EXECUTION_CONTRACT.md), [analysis](ANALYSIS_PLAN.md) and
[complete suite](EXPERIMENT_SUITE.md). Version 0.2 adds these specifications to
the unfrozen October 7 draft; it does not amend a completed or frozen experiment.

## 1. Estimand and scope

Primary question: conditional on a predeclared public failure signal from an
initial branch, does retaining a common lesson while deleting that branch improve
terminal correctness under an equal continuation allowance?

Let `C` be the unchanged task/checkpoint record, `B` the model's subsequent visible
trial artifacts and earlier public observations, `F` the final public failure receipt,
`L` a lesson generated once from those materials, and `S` a separate generic
summary of the branch. C contains original instructions and the full task.
F is excluded from B so it appears exactly once in every continuation.

| ID used only by evaluator | Continuation input | Role |
|---|---|---|
| K | C + B + F + L | Keep history with the same lesson; primary control |
| R | C + F + L | Remove branch with retained lesson; primary treatment |
| Z | C + F | Remove branch without the generated lesson; diagnostic |
| G | C + F + S | Ordinary branch compaction; secondary practical control |

K and R have byte-identical C, F, L and continuation instructions. G receives the
same public evidence through a different representation; it is not a second
causal isolation of deletion. L and S have the same maximum token allowance,
not necessarily the same realized length. Never pad either to manufacture a
length match. Keep fixed message roles/section delimiters; no arm labels or
preferred-treatment language appears in the model input.

Every continuation is an independent reconstructed request with no carried opaque
reasoning. This tests editing visible context between calls. It does not isolate
physical KV cropping or measure uninterrupted private chain-of-thought revision.

## 2. Development tasks and freezing

Propose exactly 24 development tasks. Select before initial model answers; keep
all tasks in the cohort ledger regardless of success, difficulty or eligibility.

- Math: 12 generated finite constructive tasks, four each from bounded integer
  equations, modular constraints, and small graph/list-coloring constraints.
  Public predicates judge candidates with integer/rational arithmetic. An
  independent exhaustive formulation checks feasibility and grader agreement
  offline. Freeze generator, instance IDs, seeds and both checker hashes.
- Coding: 12 standard-library Python tasks from the proposed LiveCodeBench lite
  release_v6, with its retained reserved tests and a pinned dataset commit,
  four each of easy, medium and hard according to its existing labels. Freeze
  task IDs, license/provenance, release dates, public examples, reserved tests,
  reference checker, Python and container versions. Do not silently substitute
  another benchmark if the available release cannot satisfy these requirements.

Use schedule seed `20261007` and proposed generated-instance seed `20261008`.
These control local selection/order, not model sampling. No provider sampling
seed support has been verified. Two draws are repeated measurements on one task,
not two independent tasks. Dataset revisions and actual instances are still open.
A later confirmation set must be selected and sealed independently of this pilot.

MATH-500/EvalPlus are future transfer or runner-calibration options, outside the
24-task efficacy table. They do not establish uncontaminated generalization.
Constructed bad-branch fixtures are engineering tests only, never LLM observations.

## 3. Episode and eligibility

1. Generate C in one call: a concise public task state and tentative alternatives.
   Save the checkpoint before committing to a route; that choice belongs in B.
   Record whether it contains reusable pre-branch progress or merely restates
   the question. Content-quality flags do not exclude a task after its outcome.
2. Explore the proposed route for at most two calls. Host checks can evaluate a
   submitted artifact between calls. No web, retrieval, shell or provider tools
   are exposed to the model. No reference answers are supplied.
3. Stop at the first public falsification of the submitted candidate/claim.
   A wrong candidate does not imply the entire strategy is impossible.
4. Generate L once and S once using identical C,B,F access and the same model
   settings. Neither writer sees gold answers, private tests or other arms.
5. For an eligible, completely metered episode, run K,R,Z,G twice each with
   prespecified interleaved ordering. A draw has one terminal generation call.
   Draw two never sees draw one's answer. Grade only after all scheduled draws.

Public math feedback is one deterministic violated constraint with the supplied
candidate values and calculated residual, not a solution or a hint from hidden
search. Code feedback contains the first failing *public* example or a bounded
syntax/runtime error. A time limit states only that the attempt exceeded the
limit; it does not certify a mathematical dead end.

Primary eligibility requires a well-formed math artifact violating a public
predicate, or a completed code execution with a public output mismatch. Format
failures, syntax/runtime errors, timeouts, incomplete outputs and no-candidate
branches are separate feasibility categories. Passing
public tests but failing reserved tests is not used to issue an undisclosed
failure signal. Hidden grades cannot change eligibility retroactively.

Record immediate successes, no eligible failure, unsupported checkpoint,
unusable lesson/summary, oversize request, infrastructure stop and all other
dispositions. No replacement tasks or repeated initial draws to collect a desired
number of failures. Short branches are retained; no artificial filler is added.

If L includes a complete correct solution already, retain the case and flag
lesson sufficiency in evaluator-only analysis; do not quietly count it as evidence
of further problem solving. Do not use gold information to edit a writer's text.
Semantically poor but well-formed lessons remain part of the intervention.

If a writer fails its format/length contract, block only dependent conditions:
L failure blocks K/R, S failure blocks G, and neither blocks Z. Preserve the
full-cohort flow and secondary comparison denominators. A semantically poor but
valid writer output remains included. If either K or R exceeds the input cap,
mark the primary pair capacity-infeasible before dispatching either. Preparation
losses cannot disappear from a later deployment-cost analysis.

## 4. Information and environment contract

- Original task instructions persist identically. Model-authored records cannot
  override them. Trial assumptions remain visibly conditional.
- Save all raw records for evaluation, but the actor has no filesystem/archive
  access. Keep gold solutions and reserved tests outside its process and prompt.
- C must precede the assumptions being removed. A bad assumption already in C is
  a prefix-repair case; flag it rather than silently rewriting C in one arm.
- Do not forward response IDs, conversation handles, encrypted reasoning,
  compaction items or prior assistant output arrays. Build an explicit allowlist
  of text fields. `store:false` alone is insufficient to enforce this contract.
- No tools/plugins, personal memory, skills, research repository context or
  inherited transcripts may enter a request. Inspect the serialized input.
- Code is an output artifact, not an action on the research repository. Each
  execution gets a fresh isolated runtime without credentials, network, previous
  submissions or host-directory access. Bound time, memory, processes and output.
- The model receives only public feedback receipts. Candidate code cannot read
  reserved-test files; the external grader supplies bounded test inputs and
  compares outputs. All conditions start from the same declared environment.

This contract establishes intended accessible channels, not knowledge of private
provider internals. A native-harness continuity comparison belongs in a separate
study where opaque state is declared rather than silently dropped.

## 5. Model, budgets and missingness

Propose `gpt-6-luna`, medium effort, Standard speed. No fallback model, Fast mode,
or temperature/seed setting unsupported by the selected transport. Pin alias,
date, returned metadata, client/schema and exact prompts. The public alias is not
an immutable model revision. Current account access remains unverified.

| Component per eligible task | Maximum calls |
|---|---:|
| Checkpoint | 1 |
| Branch | 2 |
| Lesson and generic summary | 2 |
| Four arms times two independent continuations | 8 |
| Total | 13 |

24 * 13 = 312 task calls, plus eight calibration/transport calls = **320**.
All actual generations, including failed diagnostics, count against this bound.
Earlier termination leaves unused slots; slots are not transferred to new tasks.
No automatic retries. Persist identity/request hash/reservation before dispatch.
An unknown dispatch outcome remains charged/reserved and stops the launch.

Proposed direct-API request caps: 32,768 total rendered input tokens and 16,384
total generated tokens, including reasoning. Reserve actual tokenizer/schema
overhead; never equate UTF-8 bytes with tokens. Reject oversized input before
dispatch rather than silently truncating it. L and S each have a proposed 1,024
visible-token maximum; enforce after generation without a free repair call.

At October 8 documented Standard rates and pricing all input at the cache-write
rate, the upper model-token estimate is **USD 3.93216** for 320 capped calls.
Propose a separate **USD 5** ceiling only for a direct-API launch with these
verified conditions. Exclude paid model tools; include writer and failed-call
costs. No conversion to Codex credits or assumption of an existing allocation.

The subscription alternative must establish its own enforceable cap and planning
credit ceiling. Historical wrappers do not verify the proposed output limit.
No live adapter is implemented or configured by this document.

Use the first eight calls only for format, cap and isolation calibration, on
separate disclosed tasks. A transport/isolation failure or incomplete capped
generation prevents automatic progression into the task pilot. Any adjustment
requires a new recorded version before comparing outcomes; do not silently
increase the budget on selected difficult cases.

Known metered terminal outputs that are wrong, malformed or capped count as failures.
Infrastructure-unknown outcomes remain missing, never selectively retried. For
the paired analysis show known complete pairs and worst/best bounds over missing
scheduled outcomes. A transport stop makes the scheduled comparison incomplete.

## 6. Outcomes and interpretation

Primary: for each eligible task, average the two binary terminal correctness
scores within K and R, then take the paired difference R-K. Report math and
coding separately, the full task flow, paired outcomes, and descriptive
task-level uncertainty. Repeated draws share the task and branch; do not count
them as independent sample size. The development cohort supports no confirmatory
p-value or universal superiority claim.

Secondary: Z and G contrasts; exact candidate/check failures; branch length;
overlap of F/L with B; retained-fact loss; and repeat of a *specific refuted assumption*. Reusing the
same broad strategy is not automatically an error. Preserve ambiguous cases;
blind human coding of behavioral labels is optional and must be costed/declared.
If F/L reproduce most of a short B, the effective removal contrast is small;
report that limitation rather than treating a null result as a broad refutation.

Report total input, cached input, cache-write and output usage when exposed;
reasoning is a subset of output, not an additional charge. Unknown billing
fields remain unknown. Also report writer/initial exploration costs, failures,
wall time and local executor work. Experimental shared computation is charged
once in the experiment ledger; reconstructed standalone policy costs must charge
each policy for the preparation it would actually need.

Equal continuation token ceilings do not mean equal total compute, latency or
dollars. Plot success against measured resources; do not claim efficiency from
prompt length alone. API billed cost and underlying hardware work are different.

Before broader claims, run a separately powered held-out study plus end-to-end
policies from the original task. Include ordinary repair, independent retries
with a declared deployable selector, generic compaction and supported native
behavior. Report oracle best-of-N only as a labeled upper bound, never as an
available solution selector. Add autonomous rollback triggering only after the
controlled intervention is understood. Measure false abandonment on successful
paths in that later study.

## 7. Required offline checks before a launch

1. K/R identity tests for C,F,L, roles, instructions and common task data.
2. With fixed synthetic C/F/L fixtures, a unique B-only canary reaches K and is
   absent from R/Z serialized bodies. In real episodes, F/L may legitimately
   preserve information from B. No opaque-state replay or hidden tool/archive
   channel is allowed. This is a routing check, not proof of semantic forgetting.
3. Independent exact math checker agreement on all bounded development instances;
   invalid-but-well-formed candidates and boundary cases must be included.
4. Coding runner isolation/resource tests, reference solutions and deliberately
   incorrect fixtures; no live model-generated code on the host.
5. Reproducible task IDs/order/hashes, common preparation reuse, immutable request
   identities, cost reservations and non-retry handling of ambiguous dispatch.
6. Public/private feedback separation, all-cohort dispositions, exact terminal
   grading, and a synthetic analysis fixture with known paired outcomes.

## 8. Fields still needed for a frozen launch

Dataset and generated-task manifest; all checker/test hashes; prompt/rendering
implementation; isolated runner image/resources; transport and credentials route;
verified complete-request limits and cache accounting; eight-call calibration
schedule; a separate accepted resource allocation; model/client/request audit;
and stable result paths registered before evidence is committed.

These open fields are implementation work. This draft is not permission to launch
from a historical script, spend a closed budget, or describe planned outcomes as
observations.
