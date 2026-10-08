# Luna rollback experiment review and handoff

October 8, 2026. Prepared for your review. **Design complete for review; experiments
unrun.** The controller, task artifacts and isolated coding runner still need
implementation and verification before a launch.

The recommendation is to begin with one small, controlled comparison: give Luna
the same checkpoint, failure evidence and lesson, and change only whether the
failed branch remains in its visible context. If this comparison is informative,
test repetition on held-out tasks, full policy costs and autonomous rollback in
separate stages. The first model stage retains the proposed **USD 5 API ceiling**.

## What the first experiment measures

Your idea has two parts: learning something from a failed route, and removing
the detailed route while retaining that lesson. Both may help. Keeping the lesson
identical in the primary comparison lets us measure the second part specifically.

Let C be the original task plus a checkpoint saved before choosing a route, B the
explored branch, F a public failure receipt, L a short lesson and S a generic summary.

| Condition | Next input | Purpose |
|---|---|---|
| Keep history K | C + B + F + L | Main control |
| Rollback R | C + F + L | Test removal with the identical lesson |
| Removal alone Z | C + F | Check the value added by the lesson |
| Generic compaction G | C + F + S | Check whether ordinary summarization suffices |

All four receive the full original task. K/R use identical instructions and the
same C/F/L bytes. Each receives two independent terminal generations. The complete
transcript is kept for evaluation, but Luna has no route to read the deleted branch
through files, tools, session history or replayed opaque reasoning.

The implementation reconstructs requests between calls. It can test editable
visible working memory without changing model weights or directly manipulating
Luna's internal cache. Computation already spent on the failed route is still a
cost. A result here would not establish that all internal reasoning can be edited.

## Walk through one task

This is an authored illustration, not a model result:

1. The task is to find integer x and y with x+y=10 and x+2y=14.
2. Save a checkpoint containing the task and tentative approaches. No route has
   yet been adopted as true.
3. Explore an equal-value guess and propose x=5, y=5.
4. The public checker reports that the second equation evaluates to 15, not 14.
5. A lesson records the failed candidate and the constraint it violates. It does
   not give the solution.
6. K continues with the failed trial present. R continues with that trial removed.
   Both see the same checker receipt and lesson.
7. Grade their new candidates identically. The valid assignment x=6, y=4 belongs
   to the evaluator's illustration, not either continuation's input.

The [JSON fixture](../experiments/dependency_memory/rollback_pilot/review_example.json)
shows the actual proposed fields, including which values reach each condition.
A bad candidate refutes that candidate; it does not automatically disprove every
method related to it. This distinction is part of the lesson prompt.

## Tasks and measurement

Start with 12 generated math tasks and 12 coding tasks. Math has four each of
bounded integer equations, modular constraints and list coloring. Exact checks
can reject candidates without revealing a hidden solution. These are narrow
constructive diagnostics, not a claim about competition mathematics.

Coding has four tasks in each easy/medium/hard stratum. The proposed source is
LiveCodeBench's versioned lite dataset, release_v6, with public examples for
feedback and its retained reserved tests for grading. The variant prunes tests,
so a pass means success on that frozen suite. Exact task IDs and revisions still
need preparation. Public benchmark tasks may have appeared in model training.
See the [task selection and grading rules](../experiments/dependency_memory/rollback_pilot/TASKS_AND_GRADING.md).

Keep all 24 initial tasks in the report, including immediate successes and tasks
with no publicly detectable failure. Do not manufacture wrong branches, expose
private-test failures as feedback or replace easy tasks after seeing answers.
If few failures occur, the pilot has measured that feasibility limitation.

The primary measure is the task-level difference in recovery success between R
and K, separately for math and coding. Also report errors repeated, information
lost, tokens, actual costs and elapsed time. Two draws on one task are repeated
measurements, not two independent tasks. The pilot will not produce a defensible
general-superiority claim from a few successful examples.

## The complete experiment sequence

| Stage | Scope | Proposed resource limit | Review purpose |
|---|---|---|---|
| E0 offline checks | Renderers, graders, executor, accounting and analysis fixtures | No model calls | Verify the test does what we intend |
| E1 calibration | Eight disclosed interface requests | Included in the first USD 5 | Verify model formats, metering and isolation |
| E2 mechanism pilot | 24 initial tasks, four conditions, two terminal draws | At most 312 task calls; 320 including E1 | Learn whether deletion helps conditional recovery |
| E3 confirmation | New cohort, K/R only, one draw each | Size and allocation chosen before held-out outcomes | Check reproducibility with planned statistical sensitivity |
| E4 complete policies | 60 new tasks; repair, repair with lessons, rollback, compaction, retries | Proposed USD 31 including calibration | Compare success at USD 0.10 per task-policy episode |
| E5 autonomous rollback | 60 new tasks with three policies; 12 separate authored decision probes | Proposed USD 19 including calibration | Evaluate checkpoint choice and rejection of correct answers |

E3's worked power example can require roughly 1,000 initial tasks per domain
under its assumptions. It is not part of the USD 5 pilot or a chosen allocation.
The [suite specification](../experiments/dependency_memory/rollback_pilot/EXPERIMENT_SUITE.md)
shows the assumptions, call arithmetic and a separately scoped native-harness
comparison. Later stages are optional decisions after inspecting earlier evidence.

## How to interpret the outcomes

| Result | What it would mean |
|---|---|
| R reliably exceeds K | Support for removing failed-branch context in the tested setup |
| R and generic compaction perform similarly | A simpler summary may capture the benefit |
| R performs worse | The discarded branch may contain useful information or the lesson may be inadequate |
| R uses fewer tokens with similar observed scores | Potential savings; quality uncertainty and total costs still matter |
| Few failures or very short branches | Insufficient opportunity to test the mechanism, not a broad refutation |

Rollback with retained lessons has close prior art in Thought Rollback and
LongSeeker. The research opportunity is a clear explanation of when it helps and
a reproducible comparison, rather than a claim that backtracking itself is new.
See the [source review](../research/ROLLBACK_PILOT_DESIGN_2026-10-07.md).

## Defaults for your review

The proposed defaults are Luna at medium effort, explicit context reconstruction,
objective public checks for the first pilot, and separate math/coding reporting.
Direct API transport is the current design preference because an output-token
limit is documented. The existing subscription route remains an option after a
fresh cap and accounting audit. Dollar estimates here do not describe subscription
usage. Current documentation was rechecked on October 8; access remains untested.
[@openai-gpt6-luna2026; @openai-reasoning2026]

The model-token calculation reserves at most USD 0.012288 per request under the
proposed complete-input and generated-token caps. The 320-call ceiling gives
USD 3.93216, leaving headroom within USD 5. This assumes verified caps and no
automatic retries, paid tools or pricing premiums. Local runtime and development
effort are separate costs. Review of this packet does not itself dispatch a call.

The main choices to review are whether this narrow first hypothesis matches your
intent, whether these initial task families are useful, and whether to implement
E0 through E2 before committing to the larger policy stages. The recommended
sequence is E0, E1 and E2, then a decision based on their evidence and limitations.

## Handoff to the implementer

| Order | Deliverable | Acceptance before the next step |
|---|---|---|
| 1 | Typed records, canonical context renderer and fake transport | K/R differ only in B; private fields and routing marker stay out of R |
| 2 | Task manifests, exact math checks and isolated code grader | Independent checker agreement; reference programs pass; full provenance and hashes |
| 3 | Ledger, budget reservations and transport adapter | No automatic retries or hidden continuity; metered caps and stable request identities |
| 4 | Frozen calibration and pilot schedule | Exact task IDs, prompts, dataset revision, runtime digest and selected transport are bound |
| 5 | E1 then E2 under a separately recorded launch allocation | Preserve failures and all dispositions; stop on unknown dispatch/usage |
| 6 | Analysis and finding | Report every condition, costs and uncertainty before changing manuscript claims |

The existing Docker engine was not reachable in the October 7 inspection; its
present state has not been retested. The prior subscription wrapper also lacks a
verified cap for this design. Both are implementation prerequisites, not observed
experimental failures. Existing work and historical allocations remain intact.

## Detailed review files

- [Pilot protocol](../experiments/dependency_memory/rollback_pilot/DRAFT_PROTOCOL.md)
- [Experiment suite](../experiments/dependency_memory/rollback_pilot/EXPERIMENT_SUITE.md)
- [Tasks and grading](../experiments/dependency_memory/rollback_pilot/TASKS_AND_GRADING.md)
- [Controller and data contract](../experiments/dependency_memory/rollback_pilot/EXECUTION_CONTRACT.md)
- [Pilot prompts](../experiments/dependency_memory/rollback_pilot/PROMPTS.md) and [later policy prompts](../experiments/dependency_memory/rollback_pilot/POLICY_PROMPTS.md)
- [Analysis and interpretation](../experiments/dependency_memory/rollback_pilot/ANALYSIS_PLAN.md)
- [Machine-readable design](../experiments/dependency_memory/rollback_pilot/design_manifest.json)

The files are design artifacts. The manifest deliberately leaves real task hashes,
model revision, selected transport and runtime digest unset. No provider adapter,
cohort generation, coding execution or model experiment was run for this handoff.

## Suggested implementation handoff

> Implement the offline E0 controller, task preparation, graders and analysis
> fixtures described in this review package. Preserve the declared K/R contrast,
> public/private information split and all failure dispositions. Use a fake
> transport until the offline acceptance checks pass. Prepare a frozen E1/E2
> launch manifest with exact tasks, prompts, hashes, limits and accounting for
> review. Do not issue model requests or consume an old allocation during this
> implementation step. Keep the later E3/E4/E5 designs separate.

## Review validation

Catalog freshness, repository navigation/citations and paper assembly pass.
The bibliography has 63 entries; the manuscript still has 75 registered claims
and 48 cited sources. JSON parsing, all proposed call/budget calculations, the
authored example's arithmetic and its field-routing map were checked offline.
These checks validate the design documents, not a production renderer or an E0
implementation. The scientific test suite was not rerun for this design-only edit.
