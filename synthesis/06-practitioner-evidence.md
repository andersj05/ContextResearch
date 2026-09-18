# Practitioner evidence: operational lessons without turning them into folklore

- **Research cutoff:** 2026-09-04
- **Coverage:** 16 first-party engineering reports and benchmark audits
- **Evidence rule:** production experience can identify mechanisms and failure modes; it does not become a causal estimate merely because the system operated at scale

## Executive finding

The practitioner literature converges on a coherent systems view of an LLM harness:

1. maintain one recoverable source of truth for task and execution state;
2. compile a deliberately small, stable, well-described action interface;
3. treat context as a scarce, dynamically constructed control input;
4. put policy, credentials, budgets, and cancellation in a trusted control plane;
5. verify outcomes in the environment and keep full traces;
6. make model, harness, evaluator, infrastructure, and budget jointly versioned;
7. add search or multiple agents only when a budget-matched evaluation justifies them.

That convergence is stronger evidence that these are important **research variables** than that any particular implementation improves success. Most sources are selected case studies from organizations selling the system under discussion. Only a few disclose denominators or quantitative comparisons, and fewer still publish enough data for independent effect estimation.

## Evidence ladder used here

| Level | What it can support | Typical source in this corpus |
|---|---|---|
| P1 — versioned artifact | The interface or mechanism exists in a named snapshot | official repositories in [`05-open-source-harnesses.md`](05-open-source-harnesses.md) |
| P2 — operational case report | A failure mode occurred and a remedy was workable in one organization | Anthropic, OpenAI, Cursor, Manus, and Stencil engineering posts |
| P3 — disclosed internal comparison | A source-reported numerical association or before/after effect | multi-agent, infrastructure, managed-agent, and latency reports |
| P4 — reproducible controlled study | A treatment effect with public tasks, protocol, traces, and uncertainty | rare in this practitioner set; usually supplied by the academic corpus instead |

P1 and P2 are highly useful for architecture discovery. They should not be cited as P4. Internal numbers are retained because they constrain plausible magnitudes, but the notes preserve their sampling and confounding limits.

## Where the engineering reports agree

| Convergent proposition | Independent practitioner sources | Research interpretation |
|---|---|---|
| **State must outlive one model call or worker.** | [Stencil](../source-notes/stencil-2026-harness-playbook.md), [Anthropic managed agents](../source-notes/anthropic-2026-managed-agents.md), [Anthropic long-running agents](../source-notes/anthropic-2025-long-running-agents.md), [OpenAI harness engineering](../source-notes/openai-2026-harness-engineering.md) | Durable journals, feature ledgers, plans, commits, and progress files are alternative realizations of an external state variable. Their relative effects remain unmeasured. |
| **Context is a policy, not a transcript dump.** | [Manus](../source-notes/manus-2025-context-engineering.md), [Anthropic context engineering](../source-notes/anthropic-2025-context-engineering.md), [Cursor](../source-notes/cursor-2026-improving-harness.md), [Stencil](../source-notes/stencil-2026-harness-playbook.md) | Retrieval, summaries, filesystem offloading, cache layout, history preservation, and tool exposure should be explicit factors in an experiment. |
| **Tools define an action space and deserve product-level design.** | [Anthropic effective agents](../source-notes/anthropic-2024-building-effective-agents.md), [Stencil](../source-notes/stencil-2026-harness-playbook.md), [Cursor](../source-notes/cursor-2026-improving-harness.md) | Tool names, schemas, descriptions, result bounds, errors, and permanence can change both model behavior and runtime reliability. |
| **Execution and authority should be separated.** | [Stencil](../source-notes/stencil-2026-harness-playbook.md), [Anthropic managed agents](../source-notes/anthropic-2026-managed-agents.md) | Credentials, approvals, policy, and the journal should not share a failure domain with untrusted commands. This is a security and recoverability claim, not yet a benchmark-performance theorem. |
| **Verification must inspect outcomes, not only prose.** | [Anthropic harness design](../source-notes/anthropic-2026-harness-design.md), [Anthropic evals](../source-notes/anthropic-2026-agent-evals.md), [OpenAI harness engineering](../source-notes/openai-2026-harness-engineering.md), [SWE-bench audits](../source-notes/openai-2026-swebench-retirement.md) | Tests, browser state, artifacts, and policy compliance are distinct grader channels; each has false-positive and false-negative rates. |
| **Offline scores require production and infrastructure checks.** | [Cursor](../source-notes/cursor-2026-improving-harness.md), [Anthropic infrastructure](../source-notes/anthropic-2026-infrastructure-noise.md), [LangChain](../source-notes/langchain-2026-better-harness.md) | The target estimand must include runtime resources and deployment behavior. Small leaderboard movements can be noise or mismeasurement. |
| **Complexity must earn its cost.** | [Anthropic effective agents](../source-notes/anthropic-2024-building-effective-agents.md), [Anthropic multi-agent](../source-notes/anthropic-2025-multi-agent-research.md), [Anthropic harness design](../source-notes/anthropic-2026-harness-design.md) | Compare against simple retry and matched-token baselines; component removal is often more informative than one full-system comparison. |

The recurrence of these propositions across organizations reduces the chance that each is an idiosyncratic vocabulary choice. It does **not** remove shared incentives, imitation, common model APIs, or correlated engineering culture.

## Quantitative claims and their proper bounds

| Source-reported result | Correctly bounded interpretation | Important missing information |
|---|---|---|
| Anthropic reports a multi-agent research configuration 90.2% above a single-agent configuration on an internal evaluation. Token use explains 80% of observed score variance; tokens, tool calls, and model choice explain 95%. Multi-agent runs use about 15× chat tokens. | Orchestration plus much greater inference budget can raise breadth-heavy internal research scores. This is not an isolated multi-agent effect. | public tasks, full factorial cells, regression specification, uncertainty, equal-token retry baseline |
| Anthropic reports a six-percentage-point Terminal-Bench spread between least- and most-resourced setups with (p<0.01), and up to 6% infrastructure errors during calibration. | Runtime resources can be as large as common leaderboard gaps. The source recommends caution for gaps below three points without matched infrastructure. | complete task-level data, multiplicity handling, cluster model, external replication |
| Anthropic reports about 60% lower p50 and more than 90% lower p95 time to first token after decoupling sandbox provisioning from session start. | The architecture plausibly improved latency in that production workload. | workload distribution, simultaneous changes, failure rates, confidence intervals |
| Cursor reports an order-of-magnitude reduction in unexpected tool errors and at least 99%, often 99.9%, tool-call reliability. | Error taxonomy and targeted repair can materially improve an internal operational metric. | exact numerator/denominator, observation window, severity weighting, independent reproduction |
| Manus reports roughly 100 input tokens per output token and about 50 tool calls for a typical task. | Input caching and context assembly can dominate cost for that product's task mix. | task distribution, quantiles, success-conditioned selection, controlled ablations |
| OpenAI reports roughly one million lines and 1,500 merged pull requests over five months, about 3.5 pull requests per engineer-day, and an estimated 10× development-time reduction. | The case demonstrates a high-throughput agent-first workflow in one undisclosed internal project. Lines and merges do not identify value, quality, or a counterfactual productivity effect. | code, tasks, costs, incidents, defect escape, maintenance horizon, comparable control project |
| Stencil reports a six-run median of 36.6 s with five permanent tools, versus 42.2 s for Codex and 37.0 s for Pi on its stated task. | A small tool grammar is a plausible latency hypothesis. | more tasks, randomization, variance, matched models/providers, independent reproduction |
| The original SWE-bench Verified screen retained 500 of 1,699 tasks; a later failure-enriched audit found material issues in 59.4% of 138 selected tasks. | Benchmark labels can fail even after expert screening; the 59.4% describes the selected frequently failed subset, not the whole 500-task set. | probability sample of all tasks and audits of successful patches |
| A SWE-Bench Pro audit labels 27.4% of all 731 tasks broken by an agent-assisted path and 34.1% by a human campaign after an initial filter. | The published benchmark has extensive scorer/task defects. Overall prevalence depends on the filter's recall because intensive review was focused on flagged tasks. | probability review of unflagged tasks, public per-task adjudications, independent audit |

These numbers are best used to design power analyses and stress tests. They should not be pooled into a meta-analysis: the outcomes, samples, units, models, budgets, and selection mechanisms are incommensurable.

## Close reading: the Stencil Harness Playbook

[The Harness Playbook](../source-notes/stencil-2026-harness-playbook.md) is unusually valuable because it states invariants, interfaces, failure cases, and a formal model, rather than only presenting a product narrative. It is also exceptionally recent, partly prospective, and not independently replicated.

### Five proposed design consequences

1. **One authoritative, journaled session.** Transcript, tool calls, jobs, settings, queues, and subagents are projections of a common history. Rewind, fork, resume, and replication become state transformations instead of unrelated features.
2. **A trusted host control plane.** Model calls, policy, approval, limits, routing, credentials, and the journal remain outside the untrusted executor. The sandbox receives only bounded execution requests and streams.
3. **Bounded and cancellable work.** Tool calls, subagents, daemons, and background tasks are represented as process-like jobs with explicit lifecycle and cancellation, rather than relying on a model or child process to cooperate.
4. **Compatibility with an explicit unknown state.** Provider behavior is compiled from capability data and precedence rules. Unknown is not silently treated as false.
5. **Views are projections.** Terminal, web, remote, and inspector clients render shared semantic state; none becomes the source of truth.

The proposed `Director` stack is a compositional controller over model yields. Instead of expressing every policy in a permanent system prompt, a director can accept a yield, reject it, continue inference, or temporarily impose a requirement. The tool-surface proposal similarly keeps the permanent grammar small and moves long-tail discovery into shell or code composition.

### Formal terminal-history invariant

With finalized logical blocks (F_1,ldots,F_c), current append-only block (W_j), and emitted prefix length (e_j), the playbook defines logical history as

\[
L=F_1\cdot F_2\cdots F_c\cdot W_j[1..e_j].
\]

This separates semantic block state, width-independent logical history, and physical screen scrollback. The intended safety properties are exactly-once ordered commitment, exclusion of mutable speculative snapshots, and independence of logical history from terminal resize. The appended TLA+ model is stronger than the usual informal blog argument, but this corpus has not model-checked the specification or shown that a production implementation refines it.

### Evidence judgment

The 78-example extension audit and six-run latency microbenchmark are diagnostics, not general estimates. The deeper contribution is a set of falsifiable invariants. Those invariants can be tested through crash injection, replay equivalence, cancellation races, privilege-boundary attacks, and history-refinement checks. That makes the post a strong **research-program source** and a medium-confidence implementation source, not proof that the proposed architecture is optimal.

## Context engineering: agreement and unresolved choices

Manus and Anthropic both treat the per-call context as the real operating state visible to the model. A general representation is

\[
C_t=P\;\Vert\;I\;\Vert\;R(q_t,M_t)\;\Vert\;\Sigma(H_{\le t-k})\;\Vert\;H_{t-k+1:t},
\qquad |C_t|\le W,
\]

where (P) is stable policy, (I) durable task instruction, (M_t) external memory, (R) retrieval, (Sigma) compression, (H) recent history, and (W) the context budget.

The practitioner sources agree that raw accumulation is inadequate, but not on one universally best policy:

- Manus emphasizes deterministic serialization for KV-cache reuse, masking rather than removing tools, filesystem offloading, goal recitation, retention of failed actions, and deliberate variation in repeated histories.
- Anthropic emphasizes selecting the smallest high-signal set, progressive disclosure, compaction, structured notes, and subagents that return compressed reports.
- Cursor says the best interface can be model-specific and validates changes against real usage.
- Stencil emphasizes a small stable permanent grammar with discovery through composition.

These can conflict. Keeping failed actions aids recovery but consumes tokens; a tiny fixed tool surface aids caching but can add discovery steps; summaries reduce length but introduce irreversible information loss; subagents isolate context but multiply inference cost and merge errors. The correct mathematical object is therefore a policy frontier over success, cost, latency, and information loss—not a universal recipe.

## Evaluation practice and the benchmark-correction cycle

The two OpenAI benchmark sequences are cautionary natural experiments:

1. professional review improves an automatically mined task set;
2. better models and repeated trials reveal ambiguities that reviewers missed;
3. failure-enriched audits discover material grader defects;
4. a recommended replacement is itself later found to have widespread flaws.

This is evidence against treating a benchmark as a static ground truth. An evaluation harness contains at least a task sampler, environment builder, resource allocator, agent runner, trace recorder, outcome scorer, error classifier, and aggregator. Each component can change the measured result.

The best practitioner evaluation guidance is consistent with the academic critique:

- retain trajectories and environment state, not only final scores;
- use complementary graders rather than one LLM judge or one test suite;
- audit false positives and false negatives on probability samples;
- distinguish exploration (at least one success) from reliability (repeated success);
- mine production failures but reserve a lockbox for the final claim;
- pair offline evaluation with deployment metrics and human review;
- record CPU, memory, time, network, image, and enforcement semantics.

## Multi-agent systems: useful topology, weak causal evidence

The production rationale for multiple agents is context isolation and parallel breadth. If (m) branches investigate separable subquestions with durations (T_i), ideal wall time approaches (max_i T_i) rather than (sum_iT_i). Real systems add coordination (T_c), synthesis (T_s), duplicated work, rate limits, and shared-resource contention:

\[
T_{\mathrm{multi}}\approx T_c+max_iT_i+T_s+T_{\mathrm{contention}}.
\]

Accuracy comparisons are more difficult because multi-agent systems usually spend more tokens and calls. The key missing cells are:

- one agent, one trajectory;
- one agent, (m) independent or adaptively selected trajectories;
- (m) agents with the same aggregate token/tool budget;
- (m) agents with unconstrained production budget.

Without the middle two, an improvement is compatible with a pure test-time-compute explanation. The practitioner evidence therefore supports multi-agent systems for operationally separable workloads, while the causal claim “roles or debate improve reasoning” remains unsettled by this set.

## Security and reliability as control-plane properties

The Stencil and managed-agent reports imply a reference-monitor architecture:

\[
\text{model proposal}\rightarrow
\text{policy/approval}\rightarrow
\text{bounded executor}\rightarrow
\text{journaled observation}.
\]

Isolation and approval are orthogonal. A container may limit host damage while still authorizing a destructive repository action; a confirmation prompt may preserve human authority while a local process retains excessive OS access. Credentials should remain outside the executor, with scoped capabilities mediated by the host.

Operational reliability is likewise a chain. If required stages have reliabilities (r_1,ldots,r_m), an independence approximation gives (prod_j r_j), but correlated provider, network, or infrastructure failures invalidate that product. At minimum, report failures by stage and preserve an end-to-end trace. Tool-call “nines” are not the same as task-success nines.

## Counterexamples to practitioner memes

| Meme | Counterevidence in this corpus |
|---|---|
| “More autonomous is better.” | Aider's human-led loop is a mature alternative; Anthropic recommends the simplest sufficient workflow. |
| “More tools give the model more capability.” | Tool retrieval and schema confusion can reduce usable action selection; Stencil's small-surface result is a hypothesis in the opposite direction. |
| “Summarization is harmless compression.” | Summaries are lossy and model/task dependent; Manus sometimes preserves failures precisely because deleting them removes recovery information. |
| “An agent improvement is a model improvement.” | Cursor tunes each model-harness pair; SWE-agent interface and infrastructure studies show large harness/runtime effects. |
| “Passing tests means the issue is solved.” | Verified and Pro audits find narrow, wide, low-coverage, misleading, and underspecified tasks. |
| “Multi-agent gains show collaboration.” | Anthropic's own analysis says token usage explains most observed variance and reports a large compute multiplier. |
| “A persistent session requires a persistent worker.” | Managed Agents separates durable logs from stateless harness workers and ephemeral sandboxes. |
| “A public repository is open source.” | Claude Code is public but proprietary; Codex's open client does not make its hosted service or models open. |

## Converting the reports into experiments

The practitioner corpus yields hypotheses with testable interventions:

| Hypothesis | Minimal controlled intervention | Primary outcomes |
|---|---|---|
| journaled state improves recovery | append-only event log versus mutable transcript under injected worker crashes | recovery success, duplicate side effects, lost work, recovery time |
| small tool grammar improves selection | full direct roster versus stable core plus retrieval, with identical underlying capabilities | task success, wrong-tool rate, discovery steps, latency, cache hit rate |
| failure retention improves adaptation | preserve versus summarize versus remove failed actions | repeated-error rate, token cost, eventual success |
| goal recitation mitigates drift | fixed periodic goal insertion versus none at matched total tokens | constraint violations, completion, useful work per token |
| external feature ledger improves long runs | immutable acceptance ledger versus free-form handoff note | premature completion, requirement coverage, cross-session regression |
| control-plane separation improves safety | host-mediated capabilities versus executor-held credentials | unauthorized actions, credential exposure, task completion, human burden |
| multiple agents improve breadth beyond compute | parallel specialists versus independent single-agent samples at matched cost | coverage, correctness, redundancy, synthesis errors, critical-path latency |
| infrastructure affects measured capability | randomized resource cells with identical agent configuration | success, infra-failure rate, timeout rate, interaction with task duration |

Every experiment should publish the configuration tuple, task sampling frame, allocation rule, traces, scorer version, exclusions, failures, and cost ledger. The proposed statistical analysis is in [`04-mathematical-foundations.md`](04-mathematical-foundations.md).

## Bottom line

Practitioner reports are most credible when they expose a concrete failure, mechanism, invariant, denominator, or removable component. They are least credible when a product-scale throughput number is presented without a comparison population or when a full-system change is narrated as one mechanism's effect.

The defensible synthesis is not “industry has solved harness engineering.” It is:

> Industry reports have identified a stable set of control, state, context, execution, and evaluation variables. Academic work increasingly confirms that these variables alter measured performance, while the comparative, long-horizon, and causal evidence needed to rank complete harnesses remains sparse.

That gap is precisely where a mathematics-oriented paper can contribute.
