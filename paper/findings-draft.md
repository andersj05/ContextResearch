# Before an agent forgets: inspect, retain, or recover?

Living findings draft v0.1 — September 18, 2026. This is a short research summary, not a submission-ready paper. The [manuscript](manuscript.md) is the main paper entry point; the [claim register](claims.csv) links substantive statements to their evidence.

## The question

An agent can finish a piece of work before it knows which details will matter later. A summary may preserve “the build succeeded” while losing the exact receipt needed to release the result. Keeping more history is one option. Learning which receipt matters before deleting anything, or retrieving it afterward, are two others.

We study when those choices are useful. The working hypothesis is that context management should consider the timing of future obligations and the cost of recovering evidence, alongside the size and quality of the retained summary. This is a hypothesis about useful agent behavior; it is not yet a measured LLM improvement.

## What we have found

**1. Individually adequate memory budgets can become incompatible when used in sequence.** In our four-bit example, two initial bits achieve 3/16 error for the isolated first task, and one later bit suffices for 25% error when its encoder sees the original source. But a two-bit memory compressed again to one bit cannot attain that 25% target after relevance is disclosed. Three initial bits can. The exact optimum with two initial bits remains unknown. This is a checked finite result, not a new general claim about compression. [C03–C05; proof and audit](../research/PROOF_AUDIT_2026-09-18.md)

**2. The obstruction survives a particular scaling construction.** For k independent four-bit blocks with the specified late block/subset reveal, exactly 3k initial bits are needed to attain error 1/4. With 2k initial bits, error is strictly greater than 1/4 + 1/512, even with joint encoding across blocks. A local audit added an analytic entropy proof and independent finite checks. External review and novelty assessment remain open. These are information bits, not receipt slots or model tokens. [C11–C12; derivation](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md)

**3. Recovery can remove the economic case for early inspection.** We built a deterministic workflow with two memory boundaries, delayed receipt requirements, revisions, optional early inspection, and a charged late recovery tool. We then computed an exact reference for a restricted class of record-selection policies under a known uniform routing distribution. It chooses retained records before seeing the hidden final query.

For six jobs, two possible required jobs, two receipt slots at each boundary, and no revisions, the best success rate before recovery is 1/3 without inspection and one with inspection. At an inspection price of one synthetic unit:

| Recovery price per missing receipt | Cheapest route to perfect success | Expected extra cost |
|---|---|---|
| 1 unit | Retain, then recover a miss | 2/3 unit |
| 4 units | Inspect before the first boundary | 1 unit |

Both costs exclude the same mandatory ten-unit workflow. All episodes contribute to cost accounting, including failed retention followed by recovery. The exact break-even recovery price is 3/2. These are model expectations over all routes, not estimates from a sample. [C17–C18; results](../experiments/dependency_memory/results/recovery_frontier_report.md)

**4. Better retention need not produce a cheaper completed task.** With only one receipt slot at the second boundary, inspection raises pre-recovery success from 3/10 to 1/2. Nevertheless, when inspection costs one and recovery costs four, reaching perfect success costs 3 extra units with inspection versus 14/5 without it. A later memory limit can erase enough of the early clue's benefit that inspection is no longer worth its price. [C20; exact reference](../experiments/dependency_memory/RECOVERY_FRONTIER.md)

The revision rule matters too. Our public schedule refreshes the smallest candidate job. A reference policy can exploit that schedule, raising uninspected success to 4/5 and moving the inspection break-even recovery price to five. This is a property of that schedule; pooling revision conditions would conceal it. [C19]

## The resulting decision rule

Let p_0 and p_1 be the best probabilities of retaining the required receipt without and with inspection. With reliable recovery at price c_R, inspection at price c_I reduces the expected cost of perfect success exactly when

```text
c_I < (p_1 - p_0) * c_R.
```

This is elementary cost accounting within our declared model. Its value is as a reference against which to test an agent's decisions. We have not shown that a model can estimate these probabilities or use the rule effectively in ordinary work.

## What contribution is still plausible?

Successive refinement, functional compression, and costed side information already provide relevant theory. Recent compaction work also discusses query timing and recovery. The [literature comparison](../research/LITERATURE_POSITIONING_2026-09-18.md) therefore supports a narrow direction: a restricted compatibility result, plus a reproducible experiment that identifies when an action before compaction changes later task success and total cost. Broad novelty claims would be premature.

The current evidence comprises checked mathematics, 50 offline tests, 2,640 complete-route scripted episodes, and a 3,000-configuration exact reference grid. The earlier 320-case workflow and 810-case retention diagnostics remain separate constructed examples. None of these counts represents independent LLM trials. Archive storage, model tokens, provider state, latency, and API dollars have not been evaluated by the recovery model.

## Next update

The next empirical milestone is a frozen pilot specification: dependencies inferred from task evidence, a declared refresh process, isolated evaluator state, recovery access matched across methods, and complete cost accounting. Then test whether a model can choose inspection when it pays and decline it when recovery is cheaper. Model revision and spending must be specified before running that pilot. External review of the mathematical argument remains a separate task.

For each update, revise the result paragraphs and the claim register together, link the supporting artifact, and retain null or negative findings. Keep proposed work visibly separate from completed evidence.
