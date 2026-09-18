**Context management in long-running agents: implementation survey and research opportunities**

Investigated September 16, 2026. This is a source-code and primary-literature investigation, not a benchmark run. The conclusions concern public implementations and documentation; they do not establish private lab budgets, proprietary compactor internals, or which experimental features a particular desktop deployment enables.

**There is substantial work on this already, and there is still a meaningful optimization problem.** The strongest opportunity is to manage the lifetime of information across a task: prevent unnecessary output from entering the prompt, retain the current work in detail, condense completed work into verifiable records, and make discarded detail recoverable. Better prose summaries are only one component. The relevant objective is the total cost and reliability of completing a task, including recovery after forgetting.

The public evidence does not support a universal “fill to 80%, summarize, repeat” description. Even the three requested harnesses use different thresholds and increasingly different alternatives to summarization. Public source also does not establish that their ordinary compaction requests run a recall-driven hill-climbing loop. Pi uses prompted summary generation; research systems such as ACON optimize compression guidelines separately; OpenAI's native compactor remains opaque. [Pi implementation](https://github.com/earendil-works/pi/blob/bdee230f1ea4beec1972c54716433ced691a92b5/packages/coding-agent/src/core/compaction/compaction.ts), [ACON](https://arxiv.org/html/2510.00615v1), [OpenAI compaction documentation](https://developers.openai.com/api/docs/guides/compaction).

The source revisions used for implementation claims are:

| Harness | Repository | Pinned commit |
|---|---|---|
| Codex | `openai/codex` | [`da18000cae9884ab45f83b2d07fbd5a220a1de39`](https://github.com/openai/codex/tree/da18000cae9884ab45f83b2d07fbd5a220a1de39) |
| Pi | `earendil-works/pi` | [`bdee230f1ea4beec1972c54716433ced691a92b5`](https://github.com/earendil-works/pi/tree/bdee230f1ea4beec1972c54716433ced691a92b5) |
| oh-my-pi / OMP | `can1357/oh-my-pi` | [`60c9a115b2e8decc0f75825459362d14188a8bc0`](https://github.com/can1357/oh-my-pi/tree/60c9a115b2e8decc0f75825459362d14188a8bc0) |

These are development snapshots retrieved on the investigation date, not claims about every installed release. Claude Code, Claude's API, OpenCode V2, and OpenHands SDK are compared using their official documentation. OpenCode V1 and V2 must be distinguished.

**Several operations commonly called “compression” solve different problems.**

| Operation | What changes | Typical benefit | Main limitation |
|---|---|---|---|
| Tool-output admission | Return bounded excerpts, selected fields, counts, or errors | Avoids admitting irrelevant tokens at all | Important details can be omitted before the agent sees them |
| Observation masking / pruning | Replace older tool results with placeholders or references | Cheap; no summarizer call required | The agent must retain the conclusion or recover the evidence |
| Semantic compaction | Replace a history span with a generated checkpoint | Preserves a useful account of earlier work in less space | Loss, fabrication, and accumulated summary drift |
| Subtask isolation / folding | Keep a subtask's detailed trajectory outside the parent context | Parent receives only relevant outcomes | Dependencies and unresolved issues must cross the boundary |
| External memory and retrieval | Keep material in files, logs, notes, or a search index | Context can remain bounded while storage grows | Retrieval takes time and can miss necessary material |
| Prompt/KV caching | Reuse computation for unchanged prefixes | Cheaper repeated input processing | Content still occupies the effective context; edits can invalidate reuse |
| Model/serving compression | Change attention, KV storage, or learned representations | Can reduce serving memory or compute | Usually requires model/server access and has separate quality tradeoffs |

A collapsed UI tool card is not evidence of model-context removal. A saved transcript is not proof that the model still receives it. Conversely, removing content from active context need not destroy it in the archive. Measure these separately.

**Codex bounds tool results before whole-history compaction.** Its unified execution tool has a default output allowance of 10,000 approximate tokens, and calls can request another allowance. The bundled model catalog also specifies a 10,000-token truncation policy for its listed models. Tool-output insertion into history applies a policy with a 20% serialization allowance unless tool-specific metadata overrides it. The shared text truncator removes the middle, retaining the beginning and end. These are distinct layers, so “every Codex tool result is exactly 10,000 tokens” would be incorrect. [Execution default](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/core/src/unified_exec/mod.rs#L79), [model catalog](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/models-manager/models.json), [history insertion](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/core/src/context_manager/history.rs#L425), [truncation utility](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/utils/output-truncation/src/lib.rs#L16).

In the ordinary total-context mode, the current public model helper defaults automatic compaction to 90% of the resolved context window and clamps a configured limit to that ceiling. The separate usable-context percentage defaults to 95%; these are not the same setting. For a resolved 272,000-token window, the corresponding numbers are 244,800 and 258,400. The configuration also has a `body_after_prefix` scope that changes what the threshold counts. Runtime catalogs and deployment configuration matter. [Threshold implementation](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/protocol/src/openai_models.rs#L511), [scope accounting](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/core/src/session/context_window.rs), [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

Codex dispatches compaction according to provider capability. Its local fallback asks the model to produce a continuation checkpoint. The remote V2 path receives a native compaction item and combines it with selected retained messages. It uses a 64,000-token retained-message budget; that is not a 64,000-token verbatim tail of all tool activity. The retained categories include real user messages and selected other messages, with filtering rules. The public API documents both standalone and in-stream compaction, carrying forward opaque encrypted state. Neither the ciphertext nor these client paths reveal the server's training algorithm or exact retained representation. [Dispatch](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/core/src/session/turn.rs#L1414), [local prompt](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/prompts/templates/compact/prompt.md), [remote retention](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/core/src/compact_remote_v2.rs#L504).

There is also a significant experimental alternative. The `token_budget` path starts a new context window without running a summarizer, and a history/notes extension exposes recovery and persistent note operations. The public feature registry marks `token_budget` and `context_management` as under development and disabled by default. This demonstrates active implementation work on explicit state and recovery; it does not establish general product availability. [Window-reset path](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/core/src/compact_token_budget.rs), [feature defaults](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/features/src/lib.rs#L1636), [history and notes operations](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/ext/history-notes/src/tools.rs).

**Pi has relatively simple defaults and explicit extension points.** Its shared tool truncator defaults to 2,000 lines or 50 KiB, whichever limit is reached first. Bash returns the tail and saves oversized output to a temporary file; file reads use head truncation and pagination. Grep has additional tool-specific limits, including a 500-character per-match line limit. These are output-shaping rules, not semantic summaries. [Shared limits](https://github.com/earendil-works/pi/blob/bdee230f1ea4beec1972c54716433ced691a92b5/packages/coding-agent/src/core/tools/truncate.ts), [bash behavior](https://github.com/earendil-works/pi/blob/bdee230f1ea4beec1972c54716433ced691a92b5/packages/coding-agent/src/core/tools/bash.ts#L234), [read tool](https://github.com/earendil-works/pi/blob/bdee230f1ea4beec1972c54716433ced691a92b5/packages/coding-agent/src/core/tools/read.ts).

Its default automatic threshold is `contextTokens > contextWindow - 16384`, and it retains approximately 20,000 recent tokens alongside the summary. On a 200,000-token model, that threshold is 183,616, or about 91.8%; on a 1,000,000-token model it is about 98.4%. Those are illustrations using the ordinary defaults, not recommendations. Pi checks inside a running tool loop as well as around user prompts. It preserves tool-call/result structure when selecting boundaries and handles a long split turn separately. [Compaction documentation](https://pi.dev/docs/latest/compaction).

The inspected summary generator serializes the selected history, includes the previous summary when present, and makes a summary-generation request. Its output allowance is capped at `floor(0.8 * reserveTokens)` and the model's maximum output; that allowance is not a promised summary length. Split turns can require a second summary of the turn prefix. File-operation metadata is tracked. Extensions can replace compaction and use a different summarizer model. I did not find a runtime recall-optimization loop in this inspected path. [Generation implementation](https://github.com/earendil-works/pi/blob/bdee230f1ea4beec1972c54716433ced691a92b5/packages/coding-agent/src/core/compaction/compaction.ts#L671), [custom-compaction example](https://github.com/earendil-works/pi/blob/bdee230f1ea4beec1972c54716433ced691a92b5/packages/coding-agent/examples/extensions/custom-compaction.ts).

**OMP already implements several of the fine-grained policies proposed in the question.** Its general artifact-spill defaults are a 50 KiB threshold and up to 20 KiB each of head and tail, with line caps. The wrapper saves the larger text as an artifact and returns an excerpt plus a recovery reference when saving succeeds. It handles tool-specific exceptions and capture failures, so this is not a universal per-tool formula. Streaming output and reads also have a configurable per-line byte cap, defaulting to 768. [Output settings](https://github.com/can1357/oh-my-pi/blob/60c9a115b2e8decc0f75825459362d14188a8bc0/packages/coding-agent/src/config/settings-schema.ts#L891), [spill implementation](https://github.com/can1357/oh-my-pi/blob/60c9a115b2e8decc0f75825459362d14188a8bc0/packages/coding-agent/src/tools/output-meta.ts#L772).

Its age-based pruning policy protects the newest 40,000 tool-output tokens and requires at least 20,000 estimated tokens of savings. It protects skills and active-plan reads, with a minimum size for ordinary pruning candidates. Separate passes recognize file reads superseded by newer reads and tool results explicitly marked uneventful. The corresponding superseded-read and uneventful-result settings default to enabled. The current orchestration additionally guards warm cached prefixes, so those numerical defaults do not mean an unconditional rolling 40,000-token window. Some pruning rewrites the persisted session, which means archival recoverability must not be assumed. [Pruning policy](https://github.com/can1357/oh-my-pi/blob/60c9a115b2e8decc0f75825459362d14188a8bc0/packages/agent/src/compaction/pruning.ts), [actual maintenance integration](https://github.com/can1357/oh-my-pi/blob/60c9a115b2e8decc0f75825459362d14188a8bc0/packages/coding-agent/src/session/session-maintenance.ts#L619).

OMP's reserve-based threshold leaves the larger of 15% of the context window or a 16,384-token default floor, with special handling for small windows. Thus the ordinary large-window threshold is around 85%. Explicit token or percentage thresholds can override it. Its current default method preference is remote compaction, snapcompact, handoff, shake, then local summary, subject to eligibility and fallback conditions. `shake` substitutes recoverable artifact references for heavy content. [Threshold code](https://github.com/can1357/oh-my-pi/blob/60c9a115b2e8decc0f75825459362d14188a8bc0/packages/agent/src/compaction/compaction.ts#L329), [method order](https://github.com/can1357/oh-my-pi/blob/60c9a115b2e8decc0f75825459362d14188a8bc0/packages/coding-agent/src/session/compaction-methods.ts), [shake implementation](https://github.com/can1357/oh-my-pi/blob/60c9a115b2e8decc0f75825459362d14188a8bc0/packages/agent/src/compaction/shake.ts).

Two newer mechanisms deserve attention. The opt-in notes mode carries a notebook and recent complete tool units into a fresh window, with searchable session history; its notebook replacement limit is 16,384 UTF-8 bytes. It does not automatically write missing notes. Separately, snapcompact serializes history into dense bitmap images that a vision model reads. Its rendering is local, but later image processing is still inference, and serialization caps, normalization, and visual reading can lose information. Project QA tests are not evidence of lossless recall or superior end-to-end coding outcomes. [Notes mode](https://github.com/can1357/oh-my-pi/blob/60c9a115b2e8decc0f75825459362d14188a8bc0/docs/compaction.md), [snapcompact implementation overview](https://github.com/can1357/oh-my-pi/blob/60c9a115b2e8decc0f75825459362d14188a8bc0/packages/snapcompact/README.md).

**Comparable systems confirm that context management is a first-class engineering concern.**

| System | Publicly documented behavior | Qualification |
|---|---|---|
| Claude Code | Clears older tool outputs before summarizing when necessary; subagents have separate contexts and return summaries; tool definitions can load on demand | The public product documentation does not expose a complete, fixed internal pruning algorithm. [Documentation](https://code.claude.com/docs/en/how-claude-code-works) |
| Claude API | Tool-result clearing supports a trigger, retained tool count, exclusions, and a minimum saving; defaults include a 100,000-input-token trigger and three recent tool uses | API configuration is not proof of Claude Code's internal defaults. [Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) |
| Claude API compaction | Server-side summary compaction has a configurable trigger; the documented default is 150,000 input tokens | Separate mechanism from clearing results; support depends on model and API route. [Compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) |
| OpenCode V2 | Default local checkpoints retain about 15,000 serialized recent tokens and use a 20,000-token buffer; provider-native policies are available | The retained serialization can shorten a tool result to 2,000 characters. V1 pruning settings do not describe V2. [V2 documentation](https://opencode.ai/v2/docs/compaction), [migration](https://opencode.ai/v2/docs/migrate-v1) |
| OpenHands SDK | Condensers transform the LLM's event view; the rolling pattern preserves a head and tail and summarizes the middle | Event-count thresholds are not equivalent to token budgets; this is a configurable SDK mechanism. [Architecture](https://docs.openhands.dev/sdk/arch/condenser) |
| Factory | Describes a persistent structured summary updated by merging summaries of newly removed spans | Its published comparison uses production sessions and model-judged probes, not an independent randomized task-completion trial. [Evaluation](https://factory.com/news/evaluating-compression) |

No credible public estimate of aggregate lab staffing or expenditure follows from these sources. What is observable is dedicated provider APIs, client implementations, extension hooks, recovery paths, source tests, and a growing research literature. The field is already active; optimality is not established.

**There is no defensible universal percentage of tool output that gets trimmed.** Limits act on different quantities: bytes, lines, approximate tokens, messages, or serialized records. A 100-token result may survive intact; a 1 MiB Pi bash output made of short lines retains at most 50 KiB before notices, removing at least roughly 95% of those bytes from the immediate result. A smaller output can lose more to the line limit. This says nothing by itself about aggregate session savings, recoverability, or success rate.

To answer the empirical question for a real workload, instrument four separate quantities: raw tool output, initially admitted output, output replayed on subsequent model calls, and archived/retrieved output. Also record the cache state and the number of future replays. A 5,000-token observation carried through 100 subsequent calls represents 500,000 repeated input-token appearances, even though it was produced only once. Those appearances may have discounted cache billing, so they must not all be priced as fresh input.

**The subtask-summary idea has direct precedents and remains useful.** HiAgent organizes working memory by subgoals: detailed action/observation history is associated with the active subgoal, while completed chunks become summaries with recovery when needed. Its ACL 2025 results cover five benchmark environments and report average success increasing from 21% to 42%. That is evidence for the mechanism in those settings, not a prediction that Codex's coding success will double. [HiAgent paper](https://aclanthology.org/2025.acl-long.1575.pdf).

Context-Folding makes branching and folding part of the agent's action space and trains the behavior using reinforcement learning. Its authors report comparable or better performance than their ReAct baselines with substantially smaller active context on deep-research and software tasks. This is especially close to “finish a subtask, keep its result, remove the intermediate process.” Training and harness changes are part of that treatment; it is not a free wrapper improvement demonstrated on every frozen frontier model. [Context-Folding](https://arxiv.org/abs/2510.11967).

The parent usually needs more than a completion bit. Consider this illustrative record:

```text
Subtask: replace the CSV parser
Status: completed and verified at revision abc123
Artifacts: src/parser.ts; tests/parser.test.ts
Result contract: UTF-8 input; original row order retained; malformed rows rejected
Verification: named parser suite passed, command exit 0, recorded against abc123
Open dependency: importer still calls the previous parser interface
Recovery: archive entry task-17 and verification log test-42
```

The record preserves what downstream work depends on, the scope of completion, and how to check it. “Parser done” omits the unresolved importer dependency. “Tests passed” without a revision can become stale after another edit. A useful parent record is therefore a compact contract with evidence, rather than a transcript or a vague status update. Its exact schema and size should be tested, not prescribed universally.

**The evidence supports substantial gains over naive histories, with important limits on extrapolation.**

| Study or report | Relevant result or mechanism | What it does not establish |
|---|---|---|
| [The Complexity Trap](https://arxiv.org/html/2508.21433v2) | In SWE-agent experiments across five model configurations, simple observation masking roughly halved cost against raw history and competed with LLM summaries on solve rate | A 50% saving over current Codex or OMP. Masking must be a strong baseline, not assumed inferior |
| [ACON](https://arxiv.org/html/2510.00615v1) | Optimizes observation/history compression guidelines using downstream failures; reports 26–54% lower peak tokens and explores smaller distilled compressors | Peak tokens are not total billed cost; reported results vary by benchmark and configuration |
| [AdaCoM](https://arxiv.org/html/2605.30785v1) | Trains an external context manager around frozen agents; finds different agents benefit from different retention styles | The paper explicitly does not optimize KV-cache preservation and acknowledges manager inference overhead |
| [TRACE / execution-instability study](https://arxiv.org/html/2608.06503v1) | Studies behavior after recurrent compression using controlled continuation comparisons; documents repeated exploration and execution instability | Its preliminary scope cannot certify all tasks or long-delayed dependencies |
| [Anthropic context-management report](https://claude.com/blog/context-management) | Reports 84% lower token consumption in a 100-turn search evaluation and performance gains on internal evaluations | Independent replication, general coding gains, or an 84% reduction in lab compute expenditure |

LLMLingua-style methods form another category: they select or delete prompt tokens using a learned compressor. They can be useful for retrieved text and other high-volume inputs, but their preservation properties must be checked for executable syntax, identifiers, numeric values, negation, and citation grounding. They are not interchangeable with task-state compaction. [LLMLingua-2](https://aclanthology.org/2024.findings-acl.57/).

There is also a cheaper upstream intervention: execute filtering or aggregation in code and return only the relevant results. Anthropic's MCP engineering example illustrates this approach by keeping bulk intermediate data out of model context. Its dramatic example reduction is illustrative rather than a general benchmark. [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp).

**Cache behavior changes which context policy is economical.** OpenAI documents that cache reuse needs a matching rendered prefix and eligible cache breakpoints; compaction can reset reuse from the first changed token. Anthropic likewise documents cache invalidation for tool-result clearing and exposes a minimum-savings parameter. OMP's protection of warm prefixes is a concrete implementation of this consideration. [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching), [Claude context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing).

A suitable accounting model is:

```text
total task cost = sum over every model call of
                 (uncached input cost + cache-read cost + cache-write cost
                  + output/reasoning cost)
                 + paid tools/storage/retrieval
```

Include summarizer and context-manager calls in the sum. Use mutually exclusive provider usage buckets to avoid double-counting cache writes as uncached input. Add latency and failure/rework to the optimization objective even when they are not directly billed.

For a simplified local pruning decision, let D be the net tokens removed, n the remaining calls expected to reuse that region, r the cache-read price per token, and K the one-time incremental cost of summarization plus rebuilding invalidated cache. Ignoring changes in model behavior, pruning breaks even when `n * D * r > K`. If the region would have been uncached, use the uncached rate. Include a separate expected cost for re-reading forgotten information. This is an illustrative marginal model; real sequences have changing suffixes, cache expiry, routing, and uncertain remaining work.

For example, removing 20,000 cached tokens before ten more calls avoids 200,000 cache-read tokens. At an illustrative cache-read rate of 0.1 times ordinary input pricing, that is only 20,000 ordinary-input-token equivalents. If the change incurs 70,000 equivalents of incremental cache rebuilding and summarization, it loses money over that horizon even though the prompt is smaller. This example is a calculation under stated assumptions, not a measured harness result or a provider price quote.

For a lab, shorter active sequences can also reduce attention work, KV storage, and memory traffic, and change feasible batching. Prefix caching saves repeated prefix computation but does not make conditioning on the retained sequence free. The exact benefit depends on attention architecture, serving implementation, sequence/output lengths, and hardware. API bills and internal inference costs are related but not interchangeable; neither token percentage nor a quadratic-attention slogan is a reliable GPU-cost estimate.

**A practical design should preserve information according to its future use and recovery cost.** The following is a proposed architecture, assembled from existing ideas, rather than a claim of novelty or demonstrated optimality.

| State category | Proposed treatment |
|---|---|
| User requirements, permissions, acceptance criteria | Preserve explicitly, with sources and supersession rules |
| Current subtask and unresolved dependencies | Keep detailed, recent evidence and pending obligations |
| Completed subtasks | Keep a compact outcome/contract/verification record |
| Large raw observations | Keep in an indexed archive, returning bounded views |
| Old file versions and revised facts | Mark as superseded; retain only when the difference matters |
| Failed approaches and negative results | Preserve the reason they failed when it could prevent repetition |
| Routine polling and redundant success output | Remove or aggregate when the information has no remaining use |

First, shape outputs at the source. Ask a test runner for failures and a summary, a database for the necessary columns, and a search tool for the relevant region. This can save the first admission as well as future replays. Keep access to the full result when exact detail may matter. A summarizer reading a huge log after the main model has already read it cannot reclaim that first expenditure.

Second, use selective deterministic reduction before paying for semantic summarization. Repeated boilerplate and identical observations are straightforward candidates. Supersession should account for resource identity, version, and read scope: a new read of lines 1–20 does not necessarily replace a prior observation of lines 500–600. An empty search can be valuable evidence of absence, so “empty” should not automatically mean irrelevant. These details are part of the correctness problem.

Third, create small updates when state changes. On subtask completion, store the outcome and remaining dependencies. After verification, record its scope and revision. After a failed approach, retain the failure condition. After a user correction, supersede the old requirement explicitly. A rolling state ledger can avoid repeatedly paraphrasing already settled facts, but it still needs a budget, an eviction rule, and verification against source events.

Fourth, decide when to install a compacted context using both semantic boundaries and cache economics. Write a completion record immediately if useful, but avoid repeatedly rewriting a deep cached prefix merely to install each small update. Append updates during an active window and consolidate at a milestone, cache-expiry opportunity, or meaningful token threshold. Summaries appended without actually removing or excluding history do not reduce active-context size.

Fifth, keep recovery cheap and specific. Store stable event IDs, paths, revisions, command exit status, timestamps, and bounded search/read operations. Keep the original evidence where feasible instead of recursively summarizing a summary as the only surviving source. Retrieval must be evaluated: the agent may not know what it forgot, and a current file read may not reconstruct an old transient error or a user's earlier requirement.

Sixth, treat delegation as a context boundary with overhead. A fresh worker can explore a noisy subproblem and return a narrow result. However, copying the whole parent history into every worker multiplies input processing, and dumping all worker logs back to the parent defeats the isolation. A minimal task brief and an evidence-bearing return contract are promising defaults. Parallel agents can improve latency while increasing total tokens; those outcomes should be reported separately.

The best threshold will depend on task structure, observation sizes, model robustness, expected remaining duration, cache state, summary quality, and the cost of retrieving evidence. A fixed fraction of the nominal context window captures few of these variables. There is no public basis for recommending one universally optimal percentage.

**The strongest research target is a controller evaluated on downstream behavior and real cost.** Recall probes are useful diagnostics, especially for exact identifiers and constraints, but they are not the ultimate objective. Perfect recollection of irrelevant logs wastes budget; losing one pending obligation can invalidate the task. The desired compact state should preserve the decisions that matter for successful continuation.

A credible experiment would hold model, tools, tasks, environment, and budget constant and compare:

1. The harness's native current policy.
2. Bounded tool outputs plus a strong recent-observation masking baseline.
3. Native or prompted whole-history summaries.
4. Subtask completion records plus the same recent window and archive access.
5. The same policy with cache-aware timing.
6. A learned manager only after the cheaper baselines are competitive and measurable.

Use both checkpoint interventions and complete runs. For a checkpoint intervention, restore the same environment state and history, change only the compiled context, and compare continuations. Complete runs expose feedback effects: different retained context changes future tool calls, retrieval, summary frequency, and failures. Neither experiment substitutes for the other.

Measure terminal success, total cost across all calls, elapsed time, repeated work, retrieval success, constraint loss, stale facts, invalid completion claims, and performance after repeated compactions. Record raw/admitted/replayed tool volume and cache hits separately. Include tasks with delayed dependencies, cross-subtask requirements, changing facts, failed tests, and transient observations. Freeze the policy before evaluating held-out task families; don't tune indefinitely against the test probes.

The hypothesis worth testing is: **a small explicit record of active obligations and verified subtask outcomes, paired with bounded observations, recoverable archives, and cache-aware consolidation, lowers completed-task cost at an acceptable success rate compared with strong native and masking baselines.** Most components already exist. A useful contribution would identify when and why their combination wins, implement a dependable policy, or establish a better cost-quality frontier under controlled evaluation.

Against an unbounded transcript, large gains are plausible and documented in particular settings. Against current Codex, OMP, and other capable harnesses, the remaining gain is an empirical question. I would prioritize selective tool output, reliable subtask records, and cache-aware timing before investing in a more elaborate generic summarizer. No production cost reduction or universal optimal policy was established by this investigation.

Method note: existing workspace notes were used as leads, not as proof of proprietary internals. In particular, reconstructed renderings of opaque compaction items and token-length matches cannot establish a hidden compactor's exact algorithm, training objective, or general retention guarantees. No paid agent evaluations, compactor calls, or model training were run for this survey.
