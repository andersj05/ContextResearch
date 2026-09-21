# Experiment protocol draft

September 21 research pivot: the [finite collision auditor](../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md) adds 12 constructed offline specifications, exact adaptive recovery policies, independently checked obstructions and finite repair codebooks. It has no new model launch and no second forced memory boundary during recovery. Natural-task adapters and empirical gains remain unperformed; existing completed allocations are unchanged.

September 19 completed transfer milestone: all 1,536 scheduled requests have been dispatched, with 1,533 valid responses and three preserved transport losses. The [final findings](../research/TRANSFER_LUNA_FINDINGS_2026-09-19.md) and independent pooled audit report no established guidance benefit in the primary comparison. The original allocation is complete at 48.78528 conservative credit equivalents; the [continuation](TRANSFER_CONTINUATION.md) changed admission policy only and never repeated a dispatched case. The dated launch statements below describe history, not outstanding authorization or a request to extend this study.

September 19 continuation: the user subsequently authorized thousands of additional Luna requests. The [matched transfer contract](TRANSFER_STUDY.md) bounds this to 1,536 new calls and 200 conservative credit equivalents, with four workers and a fixed factorial analysis. It supersedes exhausted-allocation statements only for this new study; neither prior run is extended or overwritten. The design isolates early record retention under specified context, guarantee, and guidance changes. Native compaction and full-agent evaluation remain separate.

Current September 19 status: the [first 96-request Luna development tranche](../experiments/dependency_memory/results/luna_development_2026-09-19/report.md) is complete under its [amended controlled-transport contract](LUNA_DEVELOPMENT_RUN.md). The separate [24-request revision diagnostic](../research/REVISION_LUNA_FINDINGS_2026-09-19.md) is also complete under its [own contract](REVISION_DIAGNOSTIC.md) and explicit allocation. It returned 24 optimal selections in a simplified task; it is not a causal improvement comparison with the first run. The earlier launch-status paragraphs below are dated history; they do not override these later contracts or the [current status](STATUS.md). Native-harness and held-out evaluation remain unperformed.

Status: protocol draft, September 18, 2026. Finite coding diagnostics and a scripted artifact/manifest environment are implemented. LLM and provider-native experiments remain unperformed. This document incorporates the follow-up discussion about blind filtering, reasoning continuity, and prompt-cache economics.

September 19 update: the [pilot specification](LLM_PILOT_SPEC.md) separates inspection-decision calibration with scripted optimal retention from model retention with inferred dependencies. Its [offline schedule and calibration](../experiments/dependency_memory/results/pilot_calibration_report.md) reserve 12 decisions and 180 episodes, with a 432-request ceiling. These are planned counts, not completed trials. Renderers, isolation, model revision, token caps, and spending remain unresolved launch fields. The earlier 36-run sketch below is superseded for this pilot, while the eventual native-harness comparison remains a separate requirement.

The correctness audit refines the pilot to v0.2: with reliable scripted recovery/submission, successful completion alone cannot distinguish good retention from forgetting every receipt. Stage B therefore measures pre-recovery availability and completion cost, while terminal success checks interface/execution validity. Fixed-policy comparisons on the same reserved routes are mandatory; the tiny sample cannot separate template-family effects from route effects. This does not change the broader end-to-end protocol's task-success objective.

## Questions and stages

September 19 implementation update: the [development pilot](DEVELOPMENT_PILOT.md) now implements one template, allowlisted requests, fake-client controls, and the 96-request development ceiling. Existing Codex subscription sign-in is verified and GPT-5.6-Luna is selected provisionally. Provider context isolation, internal retries, and subscription charge bounds still prevent live dispatch. The reserved held-out families remain unfinished. This update supplies no model result and does not relax the launch contract.

1. **Finite representation:** characterize the extra loss or parent-memory cost imposed by successive irreversible bottlenecks with delayed side information.
2. **Natural-language updates:** compare prose, structured state, and explicit unresolved-dependency retention on matched event streams.
3. **Agent behavior:** measure delayed task completion and full cost in a state-changing tool environment, against the harness's supported native policy.

Do not present success in an earlier stage as a result in a later one. The currently implemented dictionary baseline receives explicit sound retirement events; inferred retirement is a different experimental condition.

## Information available to each method

Declare each input at every boundary: retained memory, new tool result, public task instructions, candidate subset, final query, environment files, provider session state, opaque reasoning items, and any archive. A no-archive condition must not retain access to evicted values through hidden API history or evaluator files. Fixed codebooks may encode a public rule, not an individual test instance.

Pair the same source values, final query, and task with the relevance clue arriving before versus after a binding compaction. Every method in a condition receives the same evidence. Report the altered information order as the treatment. Use held-out templates; development clues and evaluator answers must not enter test-time memory inputs.

## Provider-native state is part of the experiment

An opaque reasoning or compaction item is a memory channel. Removing it may change reasoning continuity independently of the visible text summary. Keeping it may preserve information supposedly removed by an irreversible bottleneck.

- OpenAI documents opaque compaction state and says to pass the returned compacted window forward unchanged. [Compaction guide](https://developers.openai.com/api/docs/guides/compaction).
- Anthropic documents model-dependent preservation and prefix-binding rules. Some client-side edits can invalidate later thinking blocks; supported server-side compaction/context editing has different semantics. [Preserved thinking](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking), [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing).
- Record the provider, model revision, API, thinking settings, continuity rules, and dropped-block/error metadata where available. Recheck these living documents when implementing the experiment; the review above was September 18, 2026.

For the controlled representation study, ensure the actual accessible channels match the model's declared assumptions. For the production comparison, prefer supported provider mechanisms and evaluate the complete intervention. If an intervention necessarily discards reasoning state, report that treatment explicitly; it does not isolate visible-summary quality.

## Baselines and failure signals

Use an intact native harness policy; a strong structured summary; a prose-summary baseline; and a recent-observation masking baseline when the API permits it without an undeclared continuity change. Hold task, environment, model, available evidence, and declared budget constant within each comparison. Add dependency records only after these controls are working.

Retain exact unresolved identifiers and constraints, relevant negative results, the scope/revision of verification, and residual obligations from completed subtasks. Test the tempting error of replacing a subtask by a bare `done` marker. Include transient observations that cannot be recreated by reading a current file. Recovery is a separately evaluated mechanism, not an assumption.

## Cost and timing

Count every manager, summarizer, main-model, and retrieval call. Use mutually exclusive provider billing buckets for uncached input, cache reads, cache writes, and output/reasoning; do not charge a cache-write token again as uncached input. Track raw tool bytes, admitted tokens, repeated tokens, and retained memory separately. API dollars and internal serving cost are distinct outcomes.

A simplified break-even calculation is `N * D * r > K`: expected future reuses times net tokens removed times the read price must exceed incremental compactor/cache-rebuild cost. This omits behavioral changes; add rework, retrieval, and failure when evaluating runs. A smaller prompt alone is not evidence of lower total cost. [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching), [Anthropic context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing).

Append small state updates during a stable cached window and evaluate consolidation at meaningful boundaries. Compare timing policies rather than assuming a universal percentage threshold.

## Outcomes and study discipline

Primary behavioral outcome: deterministic terminal task success, including delayed obligations. Report total cost and latency alongside success; retain unsuccessful runs in accounting. Diagnostics include stale facts, repeated failed actions, invalid completion claims, exact retention, retrieval success, and cumulative compaction count.

Restore both environment and context in paired checkpoint continuations. Complete runs are also needed because actions and future observations change after a memory intervention. Immediate next-action agreement cannot establish preservation of a late obligation.

The proposed 36-run pilot (six paired templates, two disclosure timings, three methods, one budget) is a debugging exercise. Choose final sample size from a prespecified effect size and pilot variability; do not claim significance from constructed configurations or tune against held-out tasks. Save model/configuration versions, seeds, immutable task definitions, usage records, and analysis code with each result.

## Implemented deterministic environment

The [artifact/manifest contract](../experiments/dependency_memory/ARTIFACT_WORKFLOW.md) specifies the state machine, exact policy inputs, two forced record-capacity boundaries, observation-window deletion, receipt revisions, optional manifest inspection, and terminal verifier. The runner passes neither source seeds nor evaluator truth, snapshots, or full logs to scripted policies. This is an interface contract for trusted functions; it is not yet an isolation boundary for an untrusted model tool process.

The [development results](../experiments/dependency_memory/results/artifact_workflow_report.md) cover 320 constructed configurations and one explicit paired retention witness. Costs are synthetic action units, memory limits are receipt records, and serialized bytes are separate diagnostics. Fixtures and environment code are hashed in the outputs. All seeds are development seeds; there is no held-out empirical claim. These runs neither validate the bit-optimal theorem on natural language nor compare a new method with native compaction.

The [metered recovery reference](../experiments/dependency_memory/RECOVERY_FRONTIER.md) now adds a separately declared late archive read and a complete uniform-route enumeration. It reports an exact expected incremental-cost frontier for atomic-record selectors under reliable recovery and nonbinding episode limits. The 2,640 scripted episodes verify executable reference policies and fixed heuristics; the 3,000-configuration grid is a deterministic calculation, not additional independent trials. Archive storage and API costs remain unmeasured. A model pilot should retain cheap-recovery and later-bottleneck controls where inspection does not pay, rather than evaluating only the favorable regime.

## Claim boundary

The Theo/Jev criticism was supplied by the user; the specific Jev implementation and original post were not independently audited. It motivates failure cases but is not a citable measurement. No universal claim that filtering always harms performance, that native compaction is optimal, or that cache writes occupy a fixed share of spending follows from that discussion.
