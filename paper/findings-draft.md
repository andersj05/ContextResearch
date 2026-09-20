# Before an agent forgets: inspect, retain, or recover?

Living findings draft v0.8 — September 19, 2026. This is a short research summary, not a submission-ready paper. The [manuscript](manuscript.md) is the main paper entry point; the [claim register](claims.csv) links substantive statements to their evidence.

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

## First Luna development results

The [pilot design](../docs/LLM_PILOT_SPEC.md) separates inspection choice with ideal scripted retention from inspection with model-selected records. Its historical full schedule reserves 432 requests; only the 96-request development tranche has run. The four held-out families now have offline clue renderers, while request integration and model evaluation remain unfinished. [C22, C28]

The development renderer and strict request interface are now implemented. In fake-client checks, both optimal and forget-all controls completed 36 episodes with 96 requests; their pre-recovery availability differed, 26/36 versus 0/36. These are software controls on one route, not model trials. [C24; implementation and audit](../docs/DEVELOPMENT_PILOT.md)

The [first live run](../experiments/dependency_memory/results/luna_development_2026-09-19/report.md) completed all **96 Luna requests** through the existing Codex subscription, with no schema or transport failures. Ten of the 12 calibration decisions selected the exact lower-cost action. The two disagreements involved revisions, and identical repeated prompts produced different choices in those cells. This is a debugging observation, not an estimated general accuracy rate. [C25]

All 36 workflow episodes finished, but the required receipt survived before recovery in only **21/36**; the other 15 needed recovery. Never, always, and model-selected inspection had availability 3/12, 10/12, and 8/12, and synthetic action costs 154, 140, and 137. These totals describe one paired route. They do not establish population superiority, and a different valid tie-break can change the result on that route. Reliable recovery explains why completion alone would hide the retention differences. [C25; detailed findings](../research/LUNA_DEVELOPMENT_FINDINGS_2026-09-19.md)

The run used 276,048 input and 27,140 output tokens, including reasoning within output. Its conservative accounting equivalent was **2.5395 credits** under a 20-equivalent cap; the experiment's actual subscription debit is unknown. There was no API billing, credit purchase, reset redemption, or held-out call. The [transport contract](../docs/LUNA_DEVELOPMENT_RUN.md) declares fixed background instructions and restricted wrappers, fresh processes and threads, zero configured retries, and a one-generation guard. It does not expose remote internals or make the mutable model alias an immutable revision.

The [completed offline analysis](../experiments/dependency_memory/results/revision_analysis_report.md) now isolates three strictly worse first-boundary choices, all in uninspected revision cases. The other 33 parent choices attain the reference for their public view. All 36 observed later choices are optimal given the surviving records. This matters because a miss on one realized target can also be an equally good tie choice; the analysis distinguishes those cases from avoidable parent loss. It reuses existing responses and makes no new model calls. [C26]

The mechanism is concrete. If the smaller member of the future pair will be refreshed, retaining the two largest keys gives ideal later availability 4/5. The observed low-key pairs instead give 3/5 or 8/15. With no refresh, all two-key parents tie at 1/3. This is an exact calculation for the declared uniform-pair model, not a claim about Luna's hidden reasoning.

The separately authorized [24-request diagnostic](../research/REVISION_LUNA_FINDINGS_2026-09-19.md) is now complete. Every response selected an optimal full pair: `job-4/job-5` in all eight refresh-first cells, `job-0/job-1` in all eight refresh-last cells, and that same low pair in all eight no-refresh cells, where all full pairs tie. All eight matched direction shifts equal eight, unlike the prespecified static controls. Exact regret is zero throughout; its paired form is algebraically equivalent to the direction shift for full outputs, not independent confirmation. The result shows rule-sensitive choices in these simplified prompts, but the changed framing and explicitly optimal later selector prevent calling it a fix for the first workflow's errors. The 30 evaluated routes per answer are exact scoring continuations, not extra model trials. [C27, C29]

The new run had no policy/transport failures, retries, or held-out calls. Reported usage was 66,200 input and 5,651 output tokens, or **0.58328 conservative credit equivalents** under its separately authorized 12-equivalent cap. Attributable subscription debit is unknown. Both request allocations are exhausted, at 120 model requests total; no API billing, purchases, or resets occurred. The next useful behavioral comparison should vary framing and the downstream guarantee separately on matched inputs, under a new protocol and allocation. [C29]

The [held-out semantic checkpoint](../docs/HELDOUT_RENDERERS.md) covers alias chains, package prerequisites, validation scopes, and deployment handoffs. All 15 candidate pairs in both explicit and inferred formats resolve to the same intended pair, giving 120 clue forms and 240 pair/target checks across the four families. The renderer has no final-target or receipt-value input. This is offline software evidence only, with no change to the reserved routes or previous model results. Final request integration, boundary deletion checks, and a complete launch freeze remain necessary. Catalog sizes differ, and the tiny one-route-per-family sample cannot establish generalization or isolate family effects. [C28]

An [external review packet](../research/EXTERNAL_REVIEW_PACKET_2026-09-19.md) is ready, but no reviewer has been contacted. External mathematical review and novelty remain open, and the single-block exact gap does not strengthen the all-k bound automatically.

For each update, revise the result paragraphs and the claim register together, link the supporting artifact, and retain null or negative findings. Keep proposed work visibly separate from completed evidence.
