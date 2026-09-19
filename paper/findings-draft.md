# Before an agent forgets: inspect, retain, or recover?

Living findings draft v0.4 — September 19, 2026. This is a short research summary, not a submission-ready paper. The [manuscript](manuscript.md) is the main paper entry point; the [claim register](claims.csv) links substantive statements to their evidence.

## The question

An agent can finish a piece of work before it knows which details will matter later. A summary may preserve “the build succeeded” while losing the exact receipt needed to release the result. Keeping more history is one option. Learning which receipt matters before deleting anything, or retrieving it afterward, are two others.

We study when those choices are useful. The working hypothesis is that context management should consider the timing of future obligations and the cost of recovering evidence, alongside the size and quality of the retained summary. This is a hypothesis about useful agent behavior; it is not yet a measured LLM improvement.

## What we have found

**1. Individually adequate memory budgets can become incompatible when used in sequence—and we now know the exact penalty in the small example.** Two initial bits achieve 3/16 error for the isolated first task, and one later bit suffices for 25% error when its encoder sees the original source. With delayed relevance and a two-bit memory compressed again to one bit, the best error is **9/32 = 28.125%**. That is a 3.125 percentage-point penalty relative to the later task's isolated optimum. Three initial bits recover the 25% target. [C03–C05, C21; exact result](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md)

The September 19 computation examines all 171,798,901 partitions of the 16 possible source strings into four nonempty parent states. An independent decoder check grades a winning representation on all 192 outcomes. This closes the exact-optimum question for this finite example; it does not establish a new general compression theorem or an LLM effect.

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

The current evidence comprises checked mathematics, offline invariant tests, the exhaustive finite-chain computation, 2,640 complete-route scripted episodes, and a 3,000-configuration exact reference grid. The earlier 320-case workflow and 810-case retention diagnostics remain separate constructed examples. None of these counts represents independent LLM trials. Archive storage, model tokens, provider state, latency, and API dollars have not been evaluated by the recovery model.

The [correctness audit](../research/CORRECTNESS_AUDIT_2026-09-19.md) reproduced the complete finite search and fixed two validation gaps without changing those numerical results. It also exposed an evaluation limit: reliable recovery lets an agent forget everything and still finish. The pilot must measure what survives before recovery and the cost of completing the task; completion alone cannot demonstrate good memory. [C23]

## Next update

The [pilot design and offline schedule](../docs/LLM_PILOT_SPEC.md) are now specified. Stage A asks whether a model chooses inspection when it pays, with optimal retention supplied by code. Stage B adds model retention and dependencies inferred from task evidence. Separating these questions matters: a model that retains poorly may have different inspection costs than the ideal reference. The design reserves six favorable, null, and adverse regimes, with 12 decision requests and 180 paired episodes; these are planned counts, with no model runs completed. [C22]

The development renderer and strict request interface are now implemented. In fake-client checks, both optimal and forget-all controls completed 36 episodes with 96 requests; their pre-recovery availability differed, 26/36 versus 0/36. These are software controls on one route, not model trials. [C24; implementation and audit](../docs/DEVELOPMENT_PILOT.md)

The existing Codex subscription sign-in is verified, with GPT-5.6-Luna selected for the proposed run. The [provider review](../research/CODEX_SUBSCRIPTION_TRANSPORT_2026-09-19.md) found unresolved context/tool isolation, underlying retry counts, and generation/credit bounds. Live execution stays disabled; no model request or API charge has occurred. The next step is to close those gates, then complete the held-out renderers before held-out evaluation. The tiny held-out sample cannot separate template effects from route effects; two strict population cost preferences become ties on its actual routes, which we retain and report. A [focused evaluation review](../research/PILOT_EVALUATION_REVIEW_2026-09-19.md) adds whole-episode and information-sufficient controls. An [external review packet](../research/EXTERNAL_REVIEW_PACKET_2026-09-19.md) now states concrete correctness and theorem-transfer questions; no reviewer has yet been contacted. External mathematical review and novelty assessment remain separate work. The single-block exact gap does not strengthen the proved all-k bound automatically.

For each update, revise the result paragraphs and the claim register together, link the supporting artifact, and retain null or negative findings. Keep proposed work visibly separate from completed evidence.
