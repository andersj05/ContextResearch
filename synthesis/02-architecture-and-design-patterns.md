# LLM harness architecture and design patterns

**Research snapshot:** 2026-09-04  
**Unit of analysis:** a versioned runtime configuration, not a product name  
**Reading rule:** every performance number below is bounded to its cited task, model, budget, and evaluator. Recent 2026 harness papers are marked as descriptive or provisional where relevant.

## Architectural thesis

An LLM harness is best designed as a **closed-loop, stateful controller with explicit trust and resource boundaries**. The model proposes; the harness decides what the model may see, which proposal becomes an action, what executes, what evidence is authoritative, how state changes, and whether the run continues. A minimal control path is

\[
s_t
\xrightarrow{C_H} c_t
\xrightarrow{M} z_t
\xrightarrow{P_H,G_H} a_t
\xrightarrow{X_H,E_t} o_t
\xrightarrow{V_H,U_H} s_{t+1}
\xrightarrow{D_H} \{\text{continue, retry, branch, stop, escalate}\}.
\]

This view unifies tool calling, planning, reflection, retrieval, multi-agent coordination, and test-time scaling. They are not separate species of “agent”; they are policies for context \(C_H\), action construction \(P_H\), authorization \(G_H\), execution \(X_H\), verification \(V_H\), update \(U_H\), or scheduling \(D_H\).

The 2026 source-code study of eleven coding harnesses finds the same recurring implementation concerns: agent loop, model integration, tools/actions, memory/context, safety/permissions, orchestration, and extensibility ([barbaste-2026-harness-anatomy, Table 1, PDF p. 5](../papers/academic/barbaste-2026-harness-anatomy.pdf)). Its pattern catalog includes event sourcing, stuck detection, context forking, deferred tool loading, outer verification, session-tree versioning, syntax-aware permissions, and untrusted-content delimiting ([barbaste-2026-harness-anatomy, Tables 11–12, PDF pp. 52–53](../papers/academic/barbaste-2026-harness-anatomy.pdf)). Those observations show what production systems implement; they do not establish which mechanisms improve accuracy.

## 1. The state/action/context/execution/update contract

### State \(s_t\)

State should be serializable, inspectable, and divided by authority rather than stored as an undifferentiated chat transcript. A useful state tuple is

\[
s_t=(q_t,h_t,p_t,m_t,w_t,e_t,\ell_t,b_t),
\]

where \(q_t\) is the task specification, \(h_t\) event history, \(p_t\) current plan/hypotheses, \(m_t\) persistent memory, \(w_t\) working artifacts, \(e_t\) environment references or snapshots, \(\ell_t\) audit/lineage data, and \(b_t\) remaining budgets.

Required properties:

- **Single source of truth:** the plan, environment, and artifact states cannot silently disagree.
- **Monotone audit:** externally meaningful actions and observations are append-only even if a materialized view is compacted.
- **Typed provenance:** each record has origin, time, trust level, scope, and supersession status.
- **Fork semantics:** parallel branches receive explicit snapshots or immutable ancestry; they do not unknowingly share mutable scratch state.
- **Recovery semantics:** after a crash or tool timeout, the controller can determine whether an action did not start, completed, or has unknown outcome.

Event sourcing and session trees are observed production patterns rather than merely theoretical preferences ([barbaste-2026-harness-anatomy, Tables 11–12, PDF pp. 52–53](../papers/academic/barbaste-2026-harness-anatomy.pdf)). A 2026 runtime proposal independently treats context, project memory, task state, permissions, verification, and observability as named resources ([zhong-2026-harness-runtime, Tables 1–2, PDF pp. 6–7](../papers/academic/zhong-2026-harness-runtime.pdf)); it is a design proposal, not a completed causal evaluation.

### Context \(c_t=C_H(s_t,T,b_t)\)

Context is a projection, not state itself. The compiler should make four decisions explicitly:

1. **selection:** which instructions, evidence, tools, memories, and artifacts are included;
2. **ordering:** where each item appears and what recency or privilege it receives;
3. **representation:** raw text, schema, summary, diff, citation, or structured state;
4. **budgeting:** what is truncated, deferred, compressed, or retrieved later.

Every item should carry provenance and privilege. System policy, user intent, tool output, retrieved documents, peer-agent messages, and model-generated summaries are not equivalent evidence. Position alone changes model behavior: long-context experiments found a U-shaped accuracy pattern and cases where placing relevant evidence in the middle drove performance below the closed-book baseline ([liu-2024-lost-middle, §4 and position experiments](../papers/academic/liu-2024-lost-middle.pdf)).

### Action \(a_t=P_H(z_t,s_t)\)

The model emission \(z_t\) is a proposal. It becomes an action only after:

- parsing against a grammar or schema;
- type, range, path, and referential validation;
- resolution of tool/version and target principal;
- normalization of equivalent forms;
- deduplication or idempotency-key assignment;
- authorization by \(G_H\).

Invalid proposals should produce structured correction evidence, not be guessed into executable commands. Action schemas should distinguish reads, local writes, external writes, communication, financial/credential operations, and authority delegation.

### Execution \((o_t,E_{t+1})=X_H(a_t,E_t)\)

The executor owns containment, timeouts, cancellation, retries, concurrency, result size limits, secret handling, and transaction status. It must return a structured outcome such as

\[
o_t=(\text{status},\text{value},\text{error},\text{side effects},\text{provenance},\text{duration},\text{cost}).
\]

“Tool call failed” is insufficient. The update policy needs to know whether retry is safe, whether a side effect may already have happened, and which state was observed. For irreversible actions, use preview–approve–commit or compensating actions where possible.

### Verification \(v_t=V_H(\cdot)\)

Verification is evidence used by the controller, not a persuasive paragraph. Prefer, in order:

1. deterministic invariants and final-state checks;
2. environment feedback such as tests, compilers, database state, or simulator predicates;
3. independent reference data or cross-checks;
4. separately prompted/modelled critics with calibrated error estimates;
5. same-context self-critique.

The order is a design heuristic, not a universal theorem. It reflects a recurring empirical pattern: external evidence is more reliable than asking the same generator to reconsider without new information.

### Update and decision

The update function should preserve the raw event, update materialized state, invalidate superseded beliefs, debit budgets, and attach verification. The decision policy should be explicit:

\[
d_t=D_H(s_{t+1},v_t,b_t)\in
\{\text{continue},\text{retry},\text{branch},\text{rollback},\text{stop},\text{human}\}.
\]

Safety requires bounded liveness: every loop has a decreasing budget or a well-founded progress measure. A model’s assertion that it is done is a proposal to stop, not proof of completion.

## 2. Pattern: the transparent observe–act–update loop

The baseline harness asks for one action, executes it, appends the observation, and repeats. ReAct made this interleaving influential:

\[
a_t\sim\pi_M(\cdot\mid q,a_{<t},o_{<t}).
\]

On the original paper’s knowledge tasks, the effect was not uniformly positive. ReAct scored 27.4 on HotpotQA versus 29.4 for chain of thought, while hybrid ReAct/CoT variants reached roughly 34–35; on FEVER, ReAct scored 60.9 versus 56.3 for CoT and hybrids reached roughly 62–65 ([yao-2023-react, Table 1, PDF p. 4](../papers/academic/yao-2023-react.pdf)). In 200 manually labelled trajectories, ReAct reduced false-positive hallucination-like cases but introduced reasoning and search-result errors ([yao-2023-react, Table 2, PDF p. 5](../papers/academic/yao-2023-react.pdf)).

**Use when:** observations materially inform the next action; the action space is small enough to expose directly; transparent traces and low controller complexity matter.

**Implement with:**

- an explicit action grammar;
- structured error observations;
- maximum consecutive parse/tool failures;
- duplicate-action and no-progress detection;
- a verified stop condition;
- full trajectory and cost logging.

**Failure modes:** repetitive loops, hallucinated action names, stale observations, tool errors mistaken for task evidence, premature completion, and history growth. The production source study found multiple stuck-detection strategies, but their presence has not been causally compared ([barbaste-2026-harness-anatomy, Table 11, PDF p. 52](../papers/academic/barbaste-2026-harness-anatomy.pdf)).

> **Meme risk — ReAct as a universal improvement.** The landmark result established a useful interface between reasoning and action. Its own tables show task-dependent regressions and hybrid advantages. Treat interleaving as an architecture pattern, not a guarantee.

## 3. Pattern: typed tools, routing, and action interfaces

A tool harness has at least five separable mechanisms:

1. tool description and schema;
2. catalog selection or retrieval;
3. argument generation and validation;
4. authorization and execution;
5. result normalization and error recovery.

Benchmarking only final success collapses these stages. Log recall of the needed tool, selection precision, valid-call rate, execution success, recovery success, and downstream task success separately.

### Direct and deferred catalogs

Small catalogs can be included directly. Large catalogs require retrieval, hierarchical namespaces, or deferred loading. The source-code corpus found BM25-backed deferred tool/skill discovery in several production systems ([barbaste-2026-harness-anatomy, Table 11, PDF p. 52](../papers/academic/barbaste-2026-harness-anatomy.pdf)). This saves context but creates a new failure channel: a capable tool is unusable if the router never exposes it.

ToolLLM assembled 16,464 APIs, 126,486 instruction instances, and 469,585 calls and combined a retriever with depth-first decision-tree search ([qin-2023-toolllm, §3](../papers/academic/qin-2023-toolllm.pdf)). Results with oracle versus retrieved APIs make the retrieval bottleneck visible, but the paper bundles training data, retrieval, search, and model judging; it does not isolate a single harness effect.

HEART decomposes tool use into planner, router, and verifier primitives and permits up to three replans ([jin-2026-heart-tool-primitives, method and Table 1](../papers/academic/jin-2026-heart-tool-primitives.pdf)). Its ToolBench gains over the strongest commercial baselines in Table 1 are only about 1.7–1.9 points, although a small curated 50-task set shows a much larger gap. It was posted on 2026-09-01 and is not independently replicated; use it as a mechanism proposal, not settled evidence.

### Learned call insertion

Toolformer learns when to retain inserted tool calls. In simplified notation, it keeps a candidate call \(c_i\) when its reduction in future-token loss exceeds a threshold:

\[
L_i^- - L_i^+ \ge \tau_f.
\]

The full losses and filtering rule are defined in [schick-2023-toolformer, §2, PDF p. 2](../papers/academic/schick-2023-toolformer.pdf). This is mathematically useful for call value, but it is a training-time selection method over five fixed tools, not evidence that an arbitrary inference-time router will work.

### Interface design

SWE-agent’s agent–computer interface is evidence that tool/action representation can matter greatly for coding. The paper reports 12.5% on SWE-bench and 87.7% on HumanEvalFix and attributes substantial gains to a purpose-built interface ([yang-2024-swe-agent, abstract and §4](../papers/academic/yang-2024-swe-agent.pdf)). The interface was manually tuned, tasks were software-specific, and model, prompt, cost, and environment details still bound the result.

**Design rules:**

- Separate tool existence, discoverability, authorization, and successful use.
- Generate machine-readable schemas from a single source of truth.
- Reject extra fields and ambiguous identifiers.
- Make read operations easy and side-effecting operations explicit.
- Attach idempotency and transaction semantics to writes.
- Return actionable error types and bounded outputs.
- Do not put secrets in model-visible tool descriptions or observations.
- Treat every tool result as untrusted data until provenance and policy checks complete.

## 4. Pattern: planning and search

Planning harnesses externalize future actions in state. Search harnesses additionally keep multiple candidate states and a policy for expansion, scoring, pruning, and stopping.

| Method | Harness mechanism | Bounded result | Main confound or negative evidence |
|---|---|---|---|
| Tree of Thoughts | generate candidate thoughts, evaluate states, run BFS/DFS | Game of 24 success was 74% for ToT with breadth 5 versus 4% for CoT and 9% for CoT self-consistency in the paper’s Table 2 | custom decomposition/evaluator; many more calls; appendix cost about $0.74/case versus $0.13 for a simple input–output baseline ([yao-2023-tree-of-thoughts, Table 2 and Table 7](../papers/academic/yao-2023-tree-of-thoughts.pdf)) |
| RAP | use the LLM as both world model and agent inside Monte Carlo tree search | on Blocksworld, RAP with 20 simulations reported 1.00/0.88/0.42 at 2/4/6 steps versus GPT-4 CoT at 0.50/0.63/0.40 ([hao-2023-rap, Table 1](../papers/academic/hao-2023-rap.pdf)) | reward blends model likelihood, sampled confidence, and task heuristics; one cannot assign the gain to MCTS alone |
| LATS | tree search with environment feedback, reflection, and UCT selection | reported 92.7 on HumanEval and 75.9 on WebShop ([zhou-2024-lats, main results](../papers/academic/zhou-2024-lats.pdf)) | multiple mechanisms change together; public tests can be optimized; a later cost-controlled rerun found 88.0 at about $134.50 while simple warming retry reached 93.2 at about $2.45 ([kapoor-2024-agents-matter, Table A1](../papers/academic/kapoor-2024-agents-matter.pdf)) |

LATS uses an upper-confidence-tree term of the familiar form

\[
\operatorname{UCT}(s)
=
V(s)+w\sqrt{\frac{\log N(\operatorname{parent}(s))}{N(s)}}.
\]

The formula makes the exploration–exploitation tradeoff explicit, but its validity depends on the value estimates, feedback, and ability to revisit or roll back states. Real tool environments may have irreversible or non-stationary transitions, violating the convenient tree-search abstraction.

**Plan representation should include:** goal/subgoal, preconditions, expected evidence, dependencies, status, owner, and invalidation reason. A plan without an observation-linked update rule is merely text.

**Search records should include:** parent state, action, observation, value source, visit count, cost, environment snapshot, and whether branches are genuinely independent. Search over copied conversation text without environment snapshots can compare counterfactual branches that no longer correspond to executable world states.

**Minimum baselines:** one-shot; linear loop; independent retry at the same total call/token budget; best-of-\(k\) with the same verifier; and an oracle upper bound if available. Report the Pareto frontier of success versus dollars, tokens, wall time, and side effects.

> **Meme risk — search creates reasoning capability.** Search increases opportunities to sample, observe, and select. If a simpler retry or best-of-\(k\) baseline gets the same opportunities more cheaply, the elaborate controller has not demonstrated a planning-specific gain.

## 5. Pattern: feedback, critique, and verification

Feedback systems differ along two axes:

- **information:** did the revision receive new evidence?
- **selection:** is there a reliable mechanism for deciding that the revision is better?

A useful derived decomposition is

\[
\text{observed harness gain}
=
\text{information gain}
+\text{search gain}
+\text{selection gain}
+\text{interface gain}
-\text{coordination/retrieval error}.
\]

This is a synthesis heuristic, not an author’s theorem. It prevents every iterative improvement from being attributed to “reflection.”

### Intrinsic revision

Self-Refine recursively produces feedback and a new output:

\[
f_t=M(y_t,x),\qquad y_{t+1}=M(y_t,f_t,x).
\]

It reported large gains on some subjective generation tasks, but almost none on its math setting: GPT-3.5 remained 64.1, ChatGPT moved 74.8 to 75.0, and GPT-4 moved 92.9 to 93.1 ([madaan-2023-self-refine, Table 1](../papers/academic/madaan-2023-self-refine.pdf)). A later study found that a stronger initial prompt could outperform the self-correction procedure and that intrinsic correction often degraded GSM-style reasoning ([huang-2024-cannot-self-correct, Tables 2–3 and 8](../papers/academic/huang-2024-cannot-self-correct.pdf)).

A 2026 role-label experiment offers an additional warning: relabelling an identical wrong claim as coming from another role caused very large changes in strict “correction” behavior, yet paired final-answer tests were mostly statistically indistinguishable ([chen-2026-self-correction-illusion, Table 11](../papers/academic/chen-2026-self-correction-illusion.pdf)). The paper is a very recent preprint, but its separation of correction appearance from answer accuracy is methodologically important.

### External feedback

Reflexion stores verbal feedback across attempts. On HumanEval it reported 91% versus an 80% GPT-4 baseline ([shinn-2023-reflexion, Table 1](../papers/academic/shinn-2023-reflexion.pdf)). Its harder-program subset is more diagnostic: base and test-generation-only variants scored 60%, blind reflection scored 52%, and test generation plus verbal reflection scored 68% ([shinn-2023-reflexion, Table 3](../papers/academic/shinn-2023-reflexion.pdf)). The added tests supplied information; reflection alone was not sufficient.

CRITIC couples critique to external search or code tools. On AmbigNQ, its ChatGPT configuration rose from 51.8/64.3 to 62.0/74.9 on the paper’s two metrics; on HotpotQA it rose from 32.7/42.8 to 40.3/52.9 ([gou-2024-critic, Table 1](../papers/academic/gou-2024-critic.pdf)). Tool-free ablations were smaller, and the experiment used cached Google results and 500-example subsets. Table 5’s critic AUROC values around 0.81–0.83 show useful but imperfect error discrimination ([gou-2024-critic, Table 5](../papers/academic/gou-2024-critic.pdf)).

### Process and outcome verifiers

Let \(q_j(\tau)\) be checks over a candidate trajectory or final state. A conservative acceptance gate is

\[
\operatorname{accept}(\tau)
=
\mathbf 1\!\left[
\bigwedge_{j\in \mathcal H}q_j(\tau)=1
\;\land\;
\sum_{j\in\mathcal S}w_jq_j(\tau)\ge \kappa
\right],
\]

where \(\mathcal H\) are hard deterministic constraints and \(\mathcal S\) are soft checks. This is a design pattern, not a claim that weighted scores are calibrated.

“Let’s Verify Step by Step” found that process reward models selected better MATH solutions than outcome reward models at very large best-of-\(N\) budgets; best-of-1,860 reached 78.2% for its process model versus 72.4% for the outcome model and 69.6% for majority vote ([lightman-2023-verify-step, Figure 3 and main result table](../papers/academic/lightman-2023-verify-step.pdf)). The result is often memed too broadly: the paper used enormous sampling, has length/step aggregation choices, and Appendix C says 4,500 original MATH test items entered training, leaving 500 held out; training sets are not directly comparable.

**Verification rules:**

- Verify effects, not prose: inspect final database/filesystem/browser state.
- Keep hidden evaluation tests separate from repair feedback.
- Require failure-localizing evidence before another attempt.
- Calibrate model judges on human-labelled errors and report false accepts/rejects.
- Use a different context or model for a critic when feasible; same-context agreement is not independence.
- Stop when evidence passes, not when criticism runs out.
- Record whether a successful final result emerged before or after seeing public tests.

> **Meme risk — “self-correction works.”** The bounded claim is conditional: iteration helps when it adds informative feedback, useful sample diversity, or a competent selector. Intrinsic reconsideration can be neutral or harmful.

## 6. Pattern: context engineering and memory

A memory subsystem is a six-stage controller:

\[
\text{write}\rightarrow\text{index}\rightarrow\text{retrieve}
\rightarrow\text{reconcile}\rightarrow\text{compress}\rightarrow\text{inject}.
\]

Most evaluations study only retrieve and answer. Harness engineering must also study who may write, what becomes stale, which record supersedes another, how summaries lose evidence, and how untrusted content crosses privilege boundaries.

### Retrieval-augmented context

RAG treats documents \(z\) as latent evidence with a learned retriever,

\[
p_\eta(z\mid x)\propto
\exp\!\big(d(z)^\top q(x)\big),
\]

and marginalizes generation over retrieved documents at sequence or token level ([lewis-2020-rag, §2](../papers/academic/lewis-2020-rag.pdf)). The paper also shows index-date dependence: matching 2016 versus 2018 corpora changed answers to time-sensitive questions. Retrieval provenance is therefore not truth, and swapping an index is a behavioral harness change.

### Virtual context and persistent memory

MemGPT frames the context window as fast memory with explicit movement to external storage. Its document-memory retrieval benchmark rose from 38.7 to 66.9 for GPT-3.5 and from 32.1 to 92.5 for GPT-4 under the reported setup ([packer-2023-memgpt, Table 2](../papers/academic/packer-2023-memgpt.pdf)). The baseline used lossy summaries while MemGPT retained searchable history; no complete component ablation justifies the meme “unbounded context.”

Generative Agents combines recency, importance, and relevance retrieval with reflection and planning. A 25-agent simulation ablation reported a TrueSkill mean of 29.89 for the full architecture, 26.88 without reflection, 25.64 without reflection/planning, and 21.21 without memory/reflection/planning ([park-2023-generative-agents, §6.5.1](../papers/academic/park-2023-generative-agents.pdf)). The outcome was human-rated believability, not factual or task correctness, and the components were not independently randomized.

### Context position and staleness

Lost-in-the-Middle shows that inclusion is not equivalent to use: relevant evidence near the beginning or end was often used more effectively than evidence in the middle ([liu-2024-lost-middle, §4](../papers/academic/liu-2024-lost-middle.pdf)). Context compilers should therefore test order, not only recall.

STALE creates conflicts between old and updated evidence. On 400 conflicts, 1,200 queries, and more than 100 topics, its Table 2 reports a best baseline around 55.2 while many named memory frameworks score below 10; the authors’ CUPMem reaches 68 ([chao-2026-stale, Table 2, PDF p. 6](../papers/academic/chao-2026-stale.pdf)). Table 3 is more important architecturally: some systems retrieve updated evidence but still answer from stale state ([chao-2026-stale, Table 3, PDF p. 6](../papers/academic/chao-2026-stale.pdf)). This 2026 result is provisional and author-proposed CUPMem lacks independent replication, but the retrieval-versus-adjudication distinction is robustly testable.

**Memory design rules:**

- Separate working state, episodic traces, semantic facts, procedures, and artifacts.
- Preserve source, timestamp, scope, confidence, and supersession links.
- Do not let a model-generated summary delete the raw evidence it summarizes.
- Evaluate write precision, retrieval recall, evidence use, conflict resolution, and downstream accuracy separately.
- Revalidate memories whose external referents can change.
- Treat retrieved text as untrusted content, not instructions.
- Fork memory for speculative branches; merge only through an explicit reconciliation step.
- Allow users or deterministic sources to correct and tombstone records.

> **Meme risk — longer context or vector search solves memory.** More tokens can bury evidence; higher retrieval recall can surface contradictory or poisoned evidence. State maintenance requires provenance, temporal reasoning, and invalidation.

## 7. Pattern: inference-time scaling

Inference-time scaling spends additional calls/tokens on sampling, refinement, search, or verification. The harness must specify the generator, dependence among samples, selector, budget, and stopping rule.

### Voting

Self-consistency samples reasoning paths and returns the modal answer:

\[
\hat a_k=\arg\max_a \sum_{i=1}^{k}\mathbf 1[a_i=a].
\]

It reported substantial gains across arithmetic and commonsense benchmarks, generally using dozens of samples ([wang-2022-self-consistency, method and main results](../papers/academic/wang-2022-self-consistency.pdf)). Majority vote estimates the mode, not truth. Its gains depend on error diversity; correlated samples can confidently agree on the same error.

### Oracle coverage versus usable selection

With \(n\) generated candidates and \(c\) correct ones, the standard unbiased coverage estimator is

\[
\widehat{\operatorname{pass@}k}
=
1-\frac{\binom{n-c}{k}}{\binom{n}{k}}.
\]

For repeated reliability, the probability all \(k\) sampled runs pass is estimated by

\[
\widehat{\operatorname{pass}^{k}}
=
\frac{\binom{c}{k}}{\binom{n}{k}}.
\]

The distinction is operational: pass@\(k\) asks whether at least one success exists; pass\({}^{k}\) asks whether repeated runs are dependable. τ-bench uses both and reports that even when single-run scores were nontrivial, retail pass\({}^{8}\) was below 25% for the tested systems ([yao-2024-tau-bench, metric definitions and main reliability results](../papers/academic/yao-2024-tau-bench.pdf)).

“Large Language Monkeys” sampled up to 10,000 candidates and showed large oracle pass@\(k\) gains; on SWE-bench Lite one reported curve rose from 15.9 to 56 at \(k=250\), while practical selection lagged without a strong verifier ([brown-2024-language-monkeys, main scaling figures](../papers/academic/brown-2024-language-monkeys.pdf)). Oracle coverage is an upper bound, not deployed accuracy.

### Adaptive allocation

Test-time-compute work proposes allocating more compute to prompts where additional search or revision is useful. Snell et al. report that compute-optimal policies can use up to four times fewer generations than uniform allocation in their setting, but also find regimes—especially the hardest questions—where more compute gives little benefit ([snell-2024-test-time-compute, main results and compute formulation](../papers/academic/snell-2024-test-time-compute.pdf)). Difficulty estimates based on many oracle samples add cost and can leak hindsight.

If per-instance single-sample success is \(p_i\), independent oracle failure after \(k\) samples is

\[
(1-p_i)^k.
\]

When the distribution of \(p_i\) has substantial mass near zero, aggregate error can decay polynomially rather than exponentially. Under a density behaving like \(f(p)\propto p^{b-1}\) near zero,

\[
\mathbb E[(1-p)^k]\sim C\Gamma(b)k^{-b}.
\]

This is the central mathematical explanation in [schaeffer-2025-power-laws, theory sections](../papers/academic/schaeffer-2025-power-laws.pdf). It is counterevidence to universal “just sample more” narratives: hard-tail structure and correlated errors dominate asymptotics.

**Design rules:**

- Compare at equal total model calls, tokens, wall time, and dollars.
- Report oracle pass@\(k\), selected accuracy, selector recall/precision, and pass\({}^{k}\).
- Measure sample dependence and answer diversity.
- Allocate compute only when estimated marginal value exceeds marginal cost.
- Include a simple independent-retry baseline.
- Stop on verified success or exhausted budget, not a fixed ceremonial number of reflections.

## 8. Pattern: multi-agent control

A multi-agent harness adds worker identity, message routing, state partitioning, aggregation, and authority delegation. Its gain can come from parallel compute, sample diversity, specialization, or better selection; communication itself can also create conformity and error propagation.

### Common topologies

| Topology | Controller state | Appropriate use | Primary risk |
|---|---|---|---|
| Independent ensemble | isolated contexts; aggregate final answers | diversity and voting | correlated models/prompts; no task decomposition |
| Debate | shared rounds of proposals and critiques | surfacing conflicting rationales | conformity, anchoring, token amplification |
| Supervisor–workers | central plan routes bounded subtasks | decomposable work and authority control | supervisor bottleneck; lossy summaries |
| Blackboard | shared typed artifact/evidence store | asynchronous specialization | stale writes, provenance loss, races |
| Recursive delegation | workers may spawn scoped workers | dynamic decomposition | runaway branching and authority escalation |
| Market/bandit routing | controller allocates work by estimated value | heterogeneous models/tools | reward gaming and unstable allocation |

The early multi-agent debate paper used three agents and two rounds and reported 81.8 versus 69.0 for majority vote on arithmetic and 85 versus 81 on GSM-style questions ([du-2023-multiagent-debate, Table 1](../papers/academic/du-2023-multiagent-debate.pdf)). It used small samples, extra generations, and remained an arXiv preprint; it is feasibility evidence, not a general law.

Scaling the number of independent agents can help through ordinary ensemble effects. Forty Llama-13B agents increased GSM performance from about 0.35 to 0.59 in one study, while HumanEval moved only from about 0.14 to 0.18 and token use scaled roughly linearly ([li-2024-more-agents, main scaling results](../papers/academic/li-2024-more-agents.pdf)). Calling this “collaboration” would obscure the mechanism: independent sampling plus aggregation.

Stronger counterevidence comes from controlled debate comparisons. On MATH500, self-consistency matched or beat multi-agent debate for Qwen models from 1.5B through 32B in the cited Table 1; heterogeneous groups could converge toward a weak member ([yang-2025-revisiting-mad, Table 1 and analysis](../papers/academic/yang-2025-revisiting-mad.pdf)). A NeurIPS 2025 study reports majority vote above its tested debate protocols on average—for example 0.7691 versus at most 0.7377 for one Qwen setting and 0.7242 versus 0.6990 for one Llama setting ([choi-2025-debate-or-vote, Table 1](../papers/academic/choi-2025-debate-or-vote.pdf)). Its Theorem 1 gives a majority-vote lower bound under its probabilistic assumptions; Theorem 2 shows a martingale condition for debate beliefs when a neighbor’s mean message equals the receiver’s current belief. These are assumption-bound results, not impossibility theorems for all protocols.

AceMAD uses peer scores and multiplicative weights and proves improvement under strong conditions, including a truth-holder that predicts the crowd correctly and a uniform advantage ([liu-2026-acemad, theory and main tables](../papers/academic/liu-2026-acemad.pdf)). Its large reported gains are on selected challenging subsets and the paper is a very recent preprint; some cells regress.

**Multi-agent design rules:**

- State the compute-matched single-agent and independent-ensemble baselines.
- Preserve private first-pass answers before communication to measure conformity.
- Route typed claims and evidence, not only persuasive prose.
- Attach source and confidence to shared-memory writes.
- Scope each worker’s tools, credentials, budget, and delegation rights.
- Make the supervisor verify artifacts directly rather than trust worker summaries.
- Detect duplicated work, cyclic delegation, and consensus without evidence.
- Measure diversity before and after communication, not only final accuracy.

> **Meme risk — role labels create expertise.** Naming identical model calls “researcher,” “critic,” and “judge” does not create independent information. Benefits must survive equal-compute ensembles and blinded role-label controls.

## 9. Pattern: safety as a reference monitor

Safety cannot be delegated to a natural-language reminder alone. The harness guard should behave like a reference monitor:

\[
G_H(s_t,a_t,p)=
\begin{cases}
\text{allow}, & \text{if principal }p\text{ has scoped authority and invariants hold},\\
\text{approve}, & \text{if informed human authorization is required},\\
\text{deny}, & \text{otherwise}.
\end{cases}
\]

The guard must be invoked on every action and must not be bypassable by tool output or peer-agent text.

### Threat model: instructions arrive through data

Indirect prompt injection occurs when retrieved or tool-returned content is interpreted as authority. Greshake et al. demonstrated qualitative proof-of-concept attacks including exfiltration, remote control, persistence through memory, manipulated summaries, and denial of service ([greshake-2023-indirect-injection, threat model and demonstrations, PDF pp. 3–10](../papers/academic/greshake-2023-indirect-injection.pdf)). The paper explicitly notes that it did not systematically quantify attack success and relied partly on synthetic applications ([greshake-2023-indirect-injection, §5.2, PDF p. 11](../papers/academic/greshake-2023-indirect-injection.pdf)).

InjecAgent provides broader but still stylized evidence: 1,054 cases cross 17 user tools with 62 attacker cases ([zhan-2024-injecagent, Table 2, PDF p. 4](../papers/academic/zhan-2024-injecagent.pdf)). Its prompted GPT-4 configuration had a 24% base-setting attack success rate; fine-tuned models were more resistant in the tested setup ([zhan-2024-injecagent, §3–4, PDF pp. 2 and 6](../papers/academic/zhan-2024-injecagent.pdf)). Cases were generated with GPT-4 and manually repaired, and the setup begins after the benign tool result has already been obtained, limiting end-to-end realism.

AgentDojo makes environment state and utility/security checks explicit. Its NeurIPS 2024 benchmark contains 97 user tasks and 629 security cases ([debenedetti-2024-agentdojo, abstract and Table 1, PDF pp. 1 and 6](../papers/academic/debenedetti-2024-agentdojo.pdf)). On GPT-4o, Table 5 reports 57.69% targeted attack success with no defense; a prompt-injection detector reduced this to 7.95% but benign utility fell to 41.49%, while tool filtering achieved 6.84% with 73.13% benign utility ([debenedetti-2024-agentdojo, Table 5, PDF p. 20](../papers/academic/debenedetti-2024-agentdojo.pdf)). Tool filtering works only when needed capabilities can be known in advance, and the authors stress adaptive attacks and dynamic evaluation ([debenedetti-2024-agentdojo, §4.3, PDF p. 9](../papers/academic/debenedetti-2024-agentdojo.pdf)).

### Defense layers

| Boundary | Harness control | Failure prevented or contained |
|---|---|---|
| Instruction/data | privilege labels; parse data as data; untrusted-content markers; delimiter defanging | tool/web text overriding policy |
| Context | provenance, taint propagation, secret redaction, least disclosure | injection persistence and data leakage |
| Tool catalog | task-scoped allowlist; deferred exposure | unnecessary dangerous capability |
| Arguments | schema and semantic validation; path/host/account constraints | malformed or overbroad calls |
| Authorization | policy-as-code; capability tokens; human approval for high-impact actions | confused-deputy and privilege escalation |
| Execution | OS/container sandbox; network egress controls; time/output limits | host compromise, runaway code, exfiltration |
| Transactions | preview, idempotency, two-phase commit, rollback/compensation | duplicate or irreversible side effects |
| Memory | write authorization, provenance, expiry, quarantine, supersession | persistent prompt injection and stale state |
| Delegation | child authority no greater than parent; bounded depth/budget | recursive escalation and resource explosion |
| Observability | complete action/effect/approval trace; anomaly alarms | silent policy bypass and weak incident response |

Instruction-hierarchy training is useful model-level defense, not a substitute for these harness controls. The trained GPT-3.5 variant improved robustness across direct, browsing, tool, extraction, and jailbreak evaluations ([wallace-2024-instruction-hierarchy, Figures 2–3, PDF p. 7](../papers/academic/wallace-2024-instruction-hierarchy.pdf)). The authors also report over-refusal tests, explicitly recommend system-level guardrails, and warn that their models remain vulnerable to stronger attacks ([wallace-2024-instruction-hierarchy, Figure 4 and discussion, PDF p. 9](../papers/academic/wallace-2024-instruction-hierarchy.pdf)). Merely adding an instruction-hierarchy system prompt was weaker than training on hierarchy data ([wallace-2024-instruction-hierarchy, Figure 5 and Table 3, PDF p. 12](../papers/academic/wallace-2024-instruction-hierarchy.pdf)).

ToolEmu addresses a different risk: unsafe behavior under underspecified benign requests. Across 36 high-stakes toolkits and 144 cases, it found evaluator-identified failures even in its safest prompted configuration ([ruan-2023-toolemu, Table 5, PDF p. 11](../papers/academic/ruan-2023-toolemu.pdf)). Its LM-emulated sandbox and judge were imperfect: human validation put identified-failure precision at 68.8%–72.5%, and safety-judge agreement was Cohen’s \(\kappa\approx0.478\) ([ruan-2023-toolemu, Tables 3–4, PDF p. 10](../papers/academic/ruan-2023-toolemu.pdf)). Use emulation for scalable discovery, then reproduce serious findings in real sandboxes.

> **Meme risk — delimiting untrusted text “solves” prompt injection.** Delimiters are a useful signal, not a security boundary. If the same model both reads hostile content and holds broad credentials, an adversarial string can still influence action selection. Enforce authority outside the model.

> **Meme risk — refusal rate equals safety.** No-action policies can look perfectly safe while being useless. Report utility under benign conditions, utility under attack, attack success, false approvals, false denials, and severity-weighted effects.

## 10. Pattern: observability, evaluation, and recovery

A production trace should be sufficient to reconstruct what the controller knew and why an effect occurred. At minimum, record:

- task and environment version/snapshot;
- model endpoint, sampling settings, and provider request ID;
- exact context manifest, order, token counts, and provenance;
- raw model emission and parsed action;
- authorization decision and approving principal;
- tool version, arguments, exit status, duration, output digest, and side effects;
- state delta and invalidated records;
- verifier inputs, outputs, calibration version, and acceptance decision;
- budgets before/after, retries, branches, human interventions, and final stop reason.

The 2026 runtime proposal calls for action, tool, context, verification, failure-attribution, intervention, entropy, and residue traces ([zhong-2026-harness-runtime, Table 4, PDF p. 9](../papers/academic/zhong-2026-harness-runtime.pdf)). This is a useful schema proposal; its H0–H3 ladder is not yet a broad empirical benchmark.

Harness-Bench introduces “execution alignment”—correspondence among reasoning, observed workspace state, actions, and evaluator conditions—and scores final configuration performance across 106 offline tasks and 5,194 trajectories ([yao-2026-harness-bench, abstract and §3–4, PDF pp. 1 and 5–9](../papers/academic/yao-2026-harness-bench.pdf)). Its reported harness gaps show that runtime configuration is material, but its own caveat is decisive: configuration diagnostics are not causal decomposition ([yao-2026-harness-bench, §2, PDF p. 2](../papers/academic/yao-2026-harness-bench.pdf)).

For interactive tasks, score final environment state rather than only the final message. τ-bench formalizes user/tool interaction as a partially observed process and multiplies action and output rewards; it also reports both pass@\(k\) and pass\({}^{k}\) to distinguish opportunity from reliability ([yao-2024-tau-bench, formulation and reliability metrics](../papers/academic/yao-2024-tau-bench.pdf)). Its authors note that final database state can still miss policy violations, so trajectory constraints remain necessary.

For recovery, distinguish:

- **parse recovery:** malformed proposal corrected without action;
- **tool recovery:** transient execution failure retried safely;
- **semantic recovery:** observation disproves a hypothesis and plan changes;
- **state recovery:** crash resumes without duplicating side effects;
- **safety recovery:** risky proposal is denied or escalated before effect;
- **verification recovery:** failed check localizes the fault and produces a bounded repair.

## 11. Failure-mode matrix

| Layer | Observable symptom | Likely mechanism | Detection and containment |
|---|---|---|---|
| Context selection | needed evidence never appears | retrieval miss, wrong scope, deferred tool not found | oracle-recall audit; log candidates and ranks |
| Context order | evidence present but ignored | position sensitivity, distraction | randomized-order ablation; citation/use tracing |
| Context trust | tool text overrides user/system intent | indirect prompt injection | privilege labels, taint, external authorization |
| Compaction | constraints disappear after summary | lossy model summary | preserve raw lineage; regression checks over constraints |
| Memory | old fact wins over update | no temporal reconciliation | supersession graph; stale-conflict tests |
| Tool routing | nonexistent or wrong tool chosen | schema ambiguity, catalog retrieval error | tool-recall/selection metrics; constrained namespace |
| Arguments | valid JSON causes wrong effect | semantic validation absent | domain constraints, preview, typed identifiers |
| Execution | duplicate write after timeout | ambiguous completion and unsafe retry | idempotency key; transaction log; effect query |
| Planning | repeated or stale subgoals | plan not linked to evidence | progress invariant; explicit invalidation |
| Search | cost explodes without quality gain | weak value model, redundant branches | marginal-value stopping; equal-budget retry baseline |
| Self-correction | answer changes but accuracy falls | no new evidence; biased critic | hidden oracle; paired correctness, not change rate |
| Verification | public tests pass but hidden tests fail | verifier overfit or leakage | independent holdout; mutation/adversarial tests |
| Model judge | fluent failure accepted | correlated generator/judge errors | calibration set; deterministic hard gates |
| Multi-agent | consensus forms around error | correlated priors and conformity | private first pass; diversity metrics; evidence voting |
| Delegation | recursive agents exhaust budget | unbounded spawn depth/authority | child budgets, depth cap, cancellation tree |
| Safety | policy prompt ignored | model is both planner and reference monitor | non-model guard; least privilege; sandbox |
| Stopping | model declares success early | completion is self-reported | final-state invariant and verification gate |
| Evaluation | “better harness” result disappears | model/budget/evaluator changed too | paired factorial experiment and full manifest |

## 12. A minimal robust architecture

The following is a defensible baseline for research and deployment:

1. **Immutable task contract.** Store user objective, constraints, acceptance tests, environment version, and allowed authority separately from conversation text.
2. **Typed event log.** Append model calls, proposed actions, guard decisions, executions, observations, state deltas, verifier results, and budget changes.
3. **Context compiler.** Build each model view from explicit sources with ordering, provenance, privilege, and token-budget logs.
4. **Small typed action surface.** Expose read-first tools; retrieve additional tools on demand; validate syntax and semantics.
5. **External reference monitor.** Enforce permissions, credentials, egress, paths, rates, spend, and approvals outside the model.
6. **Transactional executor.** Use sandboxes, timeouts, cancellation, idempotency, preview/commit, and side-effect reports.
7. **Structured state update.** Maintain plan, hypotheses, artifacts, and memory with invalidation and supersession.
8. **Evidence ladder.** Run deterministic and environmental checks before model critique; keep final evaluation independent.
9. **Bounded scheduler.** Track calls, tokens, dollars, time, branches, tool effects, and delegation; detect no progress.
10. **Verified termination.** Stop only when hard constraints pass, budget ends safely, or a human accepts/escalates.

This baseline does not require an elaborate framework. In the source-code study, a roughly 100-line minimal harness implements a loop, template, tool, message list, and limits, while larger systems devote much of their code to safety, recovery, UX, and extensibility ([barbaste-2026-harness-anatomy, §2.4 and Observation 1, PDF pp. 5 and 12](../papers/academic/barbaste-2026-harness-anatomy.pdf)). Minimality is a useful experimental control; production readiness depends on the surrounding invariants.

## 13. Experiment-ready harness manifest

Every reported run should disclose:

| Dimension | Required fields |
|---|---|
| Model | provider, exact model/version, endpoint behavior, temperature/top-p, seed if honored |
| Prompt/context | system/user templates, context compiler version, included sources/order, token budget, compaction/retrieval |
| Tools | names, schemas, versions, selection policy, permissions, executor/sandbox |
| State/memory | store format, write/retrieve/reconcile policies, initial contents, persistence and fork rules |
| Control | loop/graph/search topology, planner, verifier, retry/branch/stop policy |
| Multi-agent | worker models/prompts, topology, communication rounds, state sharing, aggregator |
| Resources | calls, tokens, dollars, wall time, parallelism, tool budget, human interventions |
| Environment | task version, initial snapshot, service/data versions, network state, reset policy |
| Evaluation | final-state checks, trajectory checks, judge identity/prompt, hidden/public split, repeated trials |
| Safety | trust labels, allow/deny rules, credentials, approvals, egress, irreversible-action handling |
| Provenance | code commit, configuration digest, raw traces, exclusions, failures, confidence intervals |

The core scientific comparison is a paired change to one row while the others remain fixed. When that is impossible, call the result a configuration comparison and report interactions and cost rather than assigning causality by narrative.

## 14. What the current evidence supports

The literature supports five bounded conclusions:

1. **Harness mechanisms are behaviorally material.** Action interfaces, retrieval, execution feedback, verification, sampling, and runtime configuration can change outcomes substantially.
2. **Effects are conditional.** ReAct, reflection, planning, memory, and debate all have tasks or settings where they are neutral or harmful.
3. **New information and competent selection explain much of the gain.** External feedback, tests, retrieval, independent samples, and strong verifiers are more defensible mechanisms than vague appeals to “reasoning.”
4. **Compute and authority are hidden treatment variables.** More branches, agents, or retries consume resources and increase both opportunity and risk.
5. **The field lacks enough controlled harness experiments.** The newest harness-specific studies provide useful vocabulary, source maps, and configuration evidence, but component-level causal, cross-model, cost-matched, and independently replicated results remain the central research gap.

The practical design implication is conservative: build a transparent controller with typed state, constrained action, external verification, least privilege, and complete traces; add search, persistent memory, or multiple agents only when an equal-budget ablation demonstrates that the mechanism—not merely more samples or more authority—earns its complexity.
