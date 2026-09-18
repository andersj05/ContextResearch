# Deep research report: LLM harness engineering

## Executive summary

LLM harness engineering is the design of the software, protocols, state, tools, execution boundaries, feedback, and evaluation that turn a language model call into an acting system. The term is newer than many of its mechanisms, so relevant evidence is distributed across tool learning, reasoning-and-acting, search, memory, multi-agent systems, coding agents, security, benchmarks, and recent industry engineering reports.

This review collected **171 academic PDFs spanning 5,390 pages, 16 practitioner sources, and 32 current implementation profiles: 219 unified sources in total**. The evidence supports a strong but bounded conclusion: **the harness is a first-class causal and experimental variable**. It does not support a universal ranking of named harnesses, nor an unconditional claim that a harness can improve itself.

The literature is vulnerable to “meme effects” when a memorable architecture label replaces a precise treatment, multiple components and compute change together, or a benchmark score is treated as ground truth. The most reliable results come from controlled interfaces, simple baselines, negative findings, repeated-trial analysis, task audits, and versioned implementations. The weakest are selected demos, author-judged case studies, and frontier claims on public benchmarks without cost or verifier controls.

For a mathematics paper, the recommended direction is now **Option C: a bounded self-improving context compiler**. It combines task-relevant rate--distortion under a fixed context budget with an independent, statistically valid promotion gate. The goal is not to prove open-ended self-improvement, but to characterize what information a compiler must preserve and when an adaptively proposed replacement can be promoted with a finite-sample guarantee. Correlated retries and imperfect verifiers remain a strong secondary Option A.

## 1. Scope and method

### 1.1 Research questions

The review asked:

1. What components distinguish an LLM harness from a model, application, or benchmark?
2. Which harness mechanisms have empirical support, null results, or counterevidence?
3. How do representative open and publicly documented harnesses implement control, state, context, tools, execution, concurrency, and evaluation?
4. Which practitioner claims expose useful operational knowledge, and which are not causally identified?
5. What mathematical estimands, estimators, theorems, models, and open problems follow?

### 1.2 Search strategy

The search began with agent surveys and foundational papers, then used backward and forward chaining across ten mechanism buckets: foundations, harness engineering, tool use, search and verification, mathematics and evaluation, memory and context, multi-agent systems, coding/evaluation, safety, and self-building/self-improving harnesses. It deliberately sought counterevidence on self-correction, debate, resampling, adaptive validation, recursive editing, benchmark validity, and infrastructure.

Academic acquisition stopped at mechanism saturation after **171 PDFs and 5,390 pages**: additional candidates largely repeated represented control topologies, optimization mechanisms, or theorem families, or lacked enough direct relevance to displace stronger primary sources. The fast-moving engineering layer was checked against official pages, repositories, releases, licenses, and documentation at the 2026-09-04 cutoff.

The resulting academic split is **100 venue-labelled publications and 71 preprints**. Recent 2026 “harness” papers are retained but explicitly treated as provisional. The other two evidence layers comprise **16 practitioner sources and 32 implementation profiles**, producing the 219-source unified corpus. Practitioner pages are represented by structured notes and canonical URLs rather than redistributed snapshots when rights were unclear.

### 1.3 Evidence discipline

Every major claim is used as one of four things:

- **mechanism evidence:** a component exists and behaves as described;
- **effect evidence:** a controlled comparison estimates an outcome difference;
- **contradiction or boundary:** a result limits a popular generalization;
- **hypothesis:** a plausible engineering proposition requiring a new experiment.

The [claim ledger](../catalog/claim-source-ledger.md) states the exact bounded claim, source IDs, evidence type, confidence, and caveat. Individual [paper notes](../paper-notes/INDEX.md) and [engineering notes](../source-notes/INDEX.md) preserve source-level findings.

## 2. The object: a harnessed stochastic system

Let a run be configured by

\[
\mathcal C=(M,H,P,T,E,V,B,D),
\]

where \(M\) is the model and decoding configuration, \(H\) the harness, \(P\)
the prompts and instructions, \(T\) the task population, \(E\) the execution
environment, \(V\) the verifier, \(B\) the budget, and \(D\) the deployment and
infrastructure conditions.

At step \(t\), a generic harness has state \(s_t\), constructs context
\(c_t=C_H(s_t,T,b_t)\), obtains a model proposal \(z_t\), maps it to an
admissible action \(a_t=P_H(z_t,s_t)\), executes that action, observes a result,
and updates state:

\[
z_t\sim M(\cdot\mid c_t),
\qquad
a_t=P_H(z_t,s_t),
\]

\[
(o_t,E_{t+1})=X_H(a_t,E_t),
\qquad
s_{t+1}=U_H(s_t,a_t,o_t).
\]

A controller chooses whether to continue, retry, branch, verify, escalate, ask a human, or stop. A policy layer decides which proposed actions are authorized. An evaluator maps traces and final environment state into observed outcomes.

This decomposition prevents three category errors:

1. attributing a harness change to the model;
2. treating a model-generated plan as an independently validated planner;
3. treating verifier acceptance as latent task correctness.

The detailed boundary and taxonomy are in [`01-definitions-and-taxonomy.md`](01-definitions-and-taxonomy.md).

## 3. Architecture families

The current implementations are hybrids, but four top-level control families are useful.

### 3.1 Model-directed loops

SWE-agent, mini-SWE-agent, OpenHands, Codex CLI, Claude Code, goose, smolagents, Haystack Agent, Letta Code, and much of Pydantic AI repeatedly expose context, receive an action, execute it, append feedback, and test a terminal condition. Important differences lie in the action grammar, context processor, event model, executor, approvals, recovery, and budget—not in the fact that a `while` loop exists.

### 3.2 Explicit graphs and dataflow

LangGraph, LlamaAgents Workflows, CrewAI Flows, Semantic Kernel orchestrations, and PocketFlow make nodes, transitions, reducers, branches, and checkpoints explicit. A graph improves inspectability and composition but does not automatically provide a good model policy, safe executor, memory semantics, or evaluator.

### 3.3 Actor and multi-agent runtimes

AutoGen and AG2 represent agents as stateful message participants; other frameworks layer delegation on a loop or graph. The scientific treatment includes topology, local contexts, message protocol, concurrency, merger, and aggregate budget. A role name is not an independent causal mechanism.

### 3.4 Human-led edit loops

Aider is an important counterexample to autonomy-as-progress. Repository retrieval, constrained patch formats, validation, Git checkpoints, and human acceptance form a mixed human–machine controller. Human attention and authority belong in the cost and outcome model.

The version-pinned 32-system comparison is [`05-open-source-harnesses.md`](05-open-source-harnesses.md). It also records discontinuities such as OpenHands V0 versus V1, AutoGen generations, AG2 classic versus v1, current Letta Code versus older Letta/MemGPT repositories, and package-specific LangGraph releases.

## 4. What the academic evidence says

### 4.1 Action and tool interfaces

ReAct demonstrates that interleaving reasoning and environment action can outperform isolated reasoning or action on some tasks, but not uniformly. Toolformer, ToolLLM, ART, and related work show that tool selection, call formatting, retrieval, and execution feedback can be learned or prompted. The durable conclusion is that a tool interface changes the model's effective action space.

Coding-agent studies sharpen this point. SWE-agent attributes substantial effects to the agent-computer interface; Agentless shows that a simpler localization/repair pipeline can compete with more elaborate agents. “Agent architecture” is therefore too coarse a variable. File navigation, search output, patch format, shell persistence, error messages, and stopping limits must be controlled separately.

### 4.2 Planning and search

Tree of Thoughts, RAP, LATS, and test-time-compute work demonstrate that sampling and search can raise the probability that a useful candidate appears. They do not establish that every named search controller adds value beyond more samples, a stronger selector, or more tokens.

The core decomposition is:

\[
P(\text{return correct})=
P(\text{candidate set contains a correct answer})
\times
P(\text{selector returns one}\mid\text{coverage}),
\]

with qualifications when stopping and selection interact. More search raises cost and can expose the selector to more false positives. Cost-matched warm-up and resampling controls are therefore necessary.

### 4.3 Feedback and self-correction

Reflexion, CRITIC, and execution-guided approaches show gains when a later attempt obtains new information. Self-Refine demonstrates task-specific benefits from iterative self-feedback. Negative work shows that an LLM often cannot correct reasoning merely by being asked again, and that apparent correction may depend on role relabeling or explicit error cues.

The defensible principle is not “reflection works.” It is:

> Revision is most credible when the feedback channel carries information not already latent in the failed trajectory and when the extra budget is matched against resampling or direct execution baselines.

### 4.4 Context and memory

RAG, Generative Agents, MemGPT, MemoryBank, HiAgent, and related work expose distinct storage and retrieval strategies. Lost-in-the-Middle and long-memory benchmarks show that available tokens are not the same as usable information. STALE adds the recent warning that remembered information may cease to be valid.

No universal memory architecture follows. The relevant intervention is a context compiler:

\[
C_t=P\Vert I\Vert R(q_t,M_t)\Vert\Sigma(H_{\le t-k})\Vert H_{t-k+1:t},
\qquad |C_t|\le W.
\]

Retrieval can omit necessary evidence; summaries can delete constraints; full histories add distraction and cost; files restore information only if the agent can discover them. These are measurable tradeoffs.

### 4.5 Multi-agent control

Debate, voting, collaboration, and role specialization sometimes improve outcomes. Later comparisons show that debate is conditional, independent voting can dominate interaction, agents may fail to explore one another's reasoning, and many failures occur in specification, coordination, and verification.

Any multi-agent claim requires a matched aggregate budget and an independent-sampling control. Otherwise the gain may be ordinary test-time scaling. Task decomposability, dependency-graph width, state coupling, merger error, and critical-path latency are better explanatory variables than the number of agent personas.

### 4.6 Safety

Indirect prompt injection is a system threat: retrieved or tool-returned data can influence a later privileged action. AgentDojo, InjecAgent, and real-world demonstrations show why prompt-only separation is inadequate.

A useful control path is

\[
\text{proposal}\rightarrow\text{policy/approval}\rightarrow
\text{bounded executor}\rightarrow\text{journaled observation}.
\]

The sandbox limits consequences; an approval or capability policy limits authority. They are orthogonal and both can fail. Credentials should remain outside untrusted execution, but architectural separation is not proof of correct authorization.

The mechanism-by-mechanism analysis, including null results and meme-risk boxes, is [`02-architecture-and-design-patterns.md`](02-architecture-and-design-patterns.md).

## 5. Self-building and self-improving harnesses

### 5.1 The outer loop is the object

A self-building system constructs a harness from a task or environment description. A self-optimizing system searches candidate harnesses against development feedback. A self-improving system goes one step further: it **persists an accepted replacement that is used by later runs**. A self-referential system may also edit the proposal procedure itself. These are different claims. None requires a model-weight update, and none by itself implies that measured improvement generalizes.

Let \(h_t\in\mathcal H\) be the deployed harness at outer-loop round \(t\). An inner run of the fixed model \(M\) under \(h_t\) produces a trace and bounded loss:

\[
(\tau,\ell)=\operatorname{Run}(M,h_t,x,\xi),
\qquad 0\leq \ell\leq 1,
\]

where \(x\) is the task and \(\xi\) includes model, environment, tool, and grading randomness. A generic outer loop is

\[
h'_{t,1:m}
\sim
Q_\psi(\cdot\mid h_t,\mathcal T_t,D_{\mathrm{dev}}),
\qquad
\bar h_t
=
\arg\min_{h\in\{h_t,h'_{t,1:m}\}}
\widehat J_{\mathrm{dev}}(h),
\]

\[
h_{t+1}
=
\begin{cases}
\bar h_t,&\mathsf P(h_t,\bar h_t;D_{\mathrm{gate}})=1,\\
h_t,&\text{otherwise.}
\end{cases}
\]

Here \(Q_\psi\) is a proposer or optimizer, \(\mathcal T_t\) contains traces and feedback, and \(\mathsf P\) is a promotion rule. The deployed artifact is the result of **two different statistical operations**:

1. **Search** uses development information to find a promising candidate. It may be evolutionary search, MCTS, Bayesian optimization, policy gradients, textual critique, program synthesis, or a hand-written edit.
2. **Acceptance** asks whether that adaptively selected candidate has enough independent evidence to replace the incumbent. It must also enforce validity, safety, compatibility, and rollback conditions.

Optimizing a validation score is not an acceptance theorem. Conversely, a conservative gate cannot rescue an optimizer whose candidate space, objective, or evaluator was changed after seeing the gate data.

### 5.2 Six axes and five mechanism families

Every self-improvement claim should identify six axes before reporting a score:

| Axis | Required specification | Typical failure |
|---|---|---|
| Editable artifact | Prompt, context compiler, memory, tool, graph, code, model assignment, or optimizer | Calling a prompt rewrite whole-agent improvement |
| Proposer/optimizer | Mutation kernel, search tree, surrogate, gradient estimator, critic, or human edit | Crediting the accepted artifact while hiding search compute |
| Evaluator | Task distribution, loss, verifier, judge, resource penalty, and randomness | Optimizing a proxy or a shared-model judge |
| Acceptance gate | Validation split, threshold, multiplicity control, regression and safety predicates | Reusing a nominal held-out set at every round |
| Persistence | What is versioned, signed, inherited, merged, or rolled back | Demonstrating a better attempt without later reuse |
| Deployment | Target model, environment, permissions, context budget, canary, and retirement rule | Assuming transfer across executors or distributions |

The empirical methods then fall into five overlapping families:

| Family | Representative mechanisms | What is actually learned | Evidence boundary |
|---|---|---|---|
| Whole-program generation | ADAS, AgentOptimizer, STOP, SICA, Darwin Gödel Machine | Executable agent or improver source | Expressive but unsafe, expensive, and especially exposed to adaptive benchmark selection |
| Modular and graph search | AFlow, AgentSquare, GPTSwarm, MaAS, AgentSwift, Archon, EvoMAS | Operators, nodes, edges, routing, roles, model and tool assignments | More executable and ablatable, but bounded by human-designed modules and unequal search budgets |
| Prompt, context, and memory evolution | PromptBreeder, TextGrad, GEPA, ACE, Self-Harness, Evo-Harness | Instructions, playbooks, summaries, retrieval and reusable skills | Cheap to persist and inspect; vulnerable to context collapse, evaluator imitation, and model-specific activation |
| Tool and asset construction | LATM, CRAFT, ToolMaker, AWO, EVOTOOL, Mem2Evolve | Code tools, wrappers, composite calls, expert agents, or asset memories | Can amortize repeated work; correctness is limited by tests, API stability, retrieval, and executable-code safety |
| Recursive and meta-level editing | STOP, Gödel Agent, DGM, HSI | The deployed policy and sometimes the update routine | Self-reference is operationally possible; it does not inherit Gödel-machine optimality or prove open-ended progress |

This taxonomy also clarifies what does **not** count as persistent harness improvement: best-of-\(k\) sampling with no retained artifact, a one-off task plan, a stronger replacement model, a workflow generated separately for every query, or an evaluation prompt rewritten by the same optimizer it is meant to judge.

### 5.3 What the results support—and what they do not

The positive evidence is real but conditional. Constrained workflow search can find useful designs: under a common GPT-4o-mini executor, AFlow reports an 80.3 average against 67.2 for ADAS in its main table. GEPA reports Qwen3-8B improvement from 45.23 to 54.85 with about 3,936 rollouts on average, compared with GRPO at 48.91 using 24,000. AgentSquare, EvoMAS, EVOTOOL, ACE, and Mem2Evolve provide component or ablation evidence that topology, localized editing, structured incremental context, and persistent assets can matter. SICA reports 17% to 53% on a selected SWE subset, and Darwin Gödel Machine reports 20% to 50% in one SWE setting, showing that executable source can accumulate domain-specific engineering improvements.

Those results do not add up to a law of recursive improvement:

- **Constrained search can beat open-ended search.** AFlow's same-executor comparison is counterevidence to the idea that a larger code space is automatically better. AgentOccam shows that a simple, static observation/action interface can beat elaborate agents without an optimizer.
- **Search compute and model mixtures are treatments.** SICA's search costs about $7,000; DGM reports roughly $22,000 for its full search versus about $10,000 for an ablation. Multi-agent and multi-model systems often change both architecture and aggregate sampling.
- **Public-benchmark reuse can erase the test.** GPTSwarm repeatedly optimizes on all of HumanEval and uses the same 20 Mini Crosswords for optimization and evaluation. Its GAIA headline does not use its graph optimizer; it uses a much slower seven-sample self-consistency system.
- **A nominal holdout may be adaptive validation.** Self-Harness reports large gains across Terminal-Bench 2, SWE, and AppWorld, but consults its held-out split at every promotion. That split is not an untouched estimate of final deployment benefit.
- **Feedback quality is load-bearing.** Evo-Harness reports that self-generated feedback falls below no evolution on CL, 27.96 versus 29.54, and SWE, 61.67 versus 63.67. It also reports negative task and cross-model cells, including Sonnet 58.0 falling to 55.3/55.7.
- **The executor may dominate the evolver.** Harness Updating Is Not Harness Benefit finds at most a 3.1-point spread among tested evolvers but 18.6–35.2-point gaps among base agents; weaker agents activate learned skills about 25% of the time versus roughly 96% for stronger agents.
- **Selection can expose objective hacking.** DGM documents an objective-hacking example; generated tools and code can pass incomplete tests; LM judges can reward the vocabulary or style of the optimizer that produced the candidate.
- **Negative cells matter.** GEPA loses AIME to its GRPO comparator, 32 versus 38; evolving-orchestration experiments include task regressions; richer adaptive or meta-level variants in recent 2026 work sometimes lose to simpler variants.

The strongest bounded conclusion is therefore:

> A model-driven outer loop can sometimes discover a harness with higher measured utility than its seed under a specified model, search space, task distribution, evaluator, and budget. A deployable improvement additionally requires independent promotion evidence, compatibility with the target executor, complete cost accounting, regression and safety checks, and later-task reuse.

Most explicit self-harness papers from 2026 remain provisional preprints. Their role in this report is to define testable mechanisms and failure modes, not to establish a settled autonomous-improvement capability.

### 5.4 Theorem boundaries: useful guarantees are deliberately narrow

Three mathematical layers must not be conflated.

First, **rate--distortion theory** can describe the minimum information rate needed to preserve a declared task-relevant distortion under its source and coding assumptions. If latent task state is \(X\), compiled context is \(C\), and distortion is \(d(X,C)\), then

\[
R(D)=\inf_{Q(C\mid X):\,\mathbb E d(X,C)\leq D} I(X;C).
\]

Shannon's theorem is asymptotic for a specified source and distortion; it is not a finite-prompt guarantee, it does not identify the right semantic distortion, and a token limit \(|C|\leq W\) is not equivalent to \(I(X;C)\leq r\) without a coding model. Blackwell comparison also gives an important boundary: a lossy compiler is a garbling of its input and cannot improve every ideal decision problem. A bounded LLM may still improve when the compiler removes distraction or expresses information in a more usable form; that is a model--harness interaction, not information creation.

Second, **adaptive search is optimistically biased**. Selecting the maximum of noisy development estimates creates the optimizer's curse, and repeated leaderboard or holdout feedback can leak information about the evaluation sample. More proposals generally make the selected development score look better even when true utility does not improve.

Third, an **independent fixed-capacity promotion gate** can give a modest finite-sample result. Let a compiler class \(\Phi_0\) of size \(M\) be fixed before drawing an i.i.d. gate sample \(V\) of size \(n\). Let each compiler have a fixed bounded loss \(h_\phi(Z)\in[0,1]\), empirical risk \(\widehat J_V(\phi)\), and population risk \(J(\phi)\). Define

\[
\varepsilon_{n,M,\delta}
=
\sqrt{\frac{\log(2M/\delta)}{2n}}.
\]

If a candidate \(\phi'\) is promoted over incumbent \(\phi\) only when

\[
\widehat J_V(\phi')
\leq
\widehat J_V(\phi)-(2\varepsilon_{n,M,\delta}+\tau),
\]

then a Hoeffding union bound implies that, with probability at least \(1-\delta\), every accepted promotion within that predeclared class reduces the same population risk by at least \(\tau\). The result allows adaptive selection **inside the fixed class** because the deviation event holds simultaneously over all \(M\) candidates.

It does not imply global optimality, useful compression, safe side effects, improvement after expanding the class, validity under dependent tasks or distribution drift, correctness of the loss, or transfer to another model. If the optimizer can change the evaluator, promotion threshold, permissions, hidden data, or class after seeing gate feedback, the premise fails. A sound syntax or proof gate can establish properties of generated code only relative to its formal specification; it is separate from statistical evidence of utility.

Operationally, the trusted host should keep the evaluator, data partitions, promotion policy, credentials, signing keys, and rollback mechanism outside editable state. Candidate code executes as untrusted input. Promotion should be transactional: build, static-check, sandbox-test, evaluate, sign, canary, and roll back on regression. The final locked audit remains untouched until the study or release decision.

The full empirical synthesis is [09-self-building-and-self-improving-harnesses.md](09-self-building-and-self-improving-harnesses.md). Source theorems, transferred results, proposed derivations, and non-corollaries are separated in [10-mathematics-of-harness-improvement.md](10-mathematics-of-harness-improvement.md). A preregistration-ready design with disjoint search, gate, and audit data is in [11-self-improving-experimental-blueprint.md](11-self-improving-experimental-blueprint.md).

## 6. Benchmark validity and evaluation

### 6.1 The scorer is part of the harness

An agent evaluation includes task sampling, environment construction, resource allocation, execution, retry rules, trace capture, scoring, error classification, and aggregation. A benchmark number changes if any of these changes.

SWE-bench illustrates the problem. Verified used professional review to select 500 tasks from 1,699. Later analysis found that tests could reject functionally valid patches or accept incomplete ones. OpenAI's later audit found material issues in 59.4% of a deliberately selected 138-task subset that o3 failed inconsistently over 64 runs. That percentage estimates the failure-enriched subset, not all 500 tasks.

A subsequent SWE-Bench Pro audit reported 200/731 tasks broken in an agent-assisted path and 249/731 in a human campaign after an initial flagging stage. Those counts are alarming, but prevalence still depends on how many broken tasks the initial filter missed.

These sequences demonstrate a lifecycle: screening improves a dataset; stronger systems reveal new ambiguity; failure analysis discovers grader defects; the replacement benchmark itself later needs audit. “Ground truth” must be maintained, sampled, versioned, and retired.

### 6.2 Infrastructure and deployment

Anthropic reports a six-percentage-point difference between least- and most-resourced Terminal-Bench configurations and infrastructure-error rates up to 6% during calibration. Even if that exact magnitude does not generalize, it establishes infrastructure as a plausible treatment variable rather than administrative noise.

CPU, memory, network, disk, timeout, image, dependency mirror, and enforcement semantics should be randomized or matched. Infrastructure failure should be reported separately from agent failure. Repeating a failed run silently changes the retry policy.

### 6.3 Recommended outcome vector

Do not collapse evaluation immediately to one success rate. Record at least:

\[
(\text{latent correctness estimate},\ 
\text{verifier acceptance},\
\text{cost},\
\text{latency},\
\text{human effort},\
\text{policy violations},\
\text{infra failures}).
\]

Report task-level paired outcomes, repository clusters, traces, exclusions, and the full configuration tuple. The empirical evidence and audit analysis are in [`03-empirical-evidence-and-benchmark-validity.md`](03-empirical-evidence-and-benchmark-validity.md).

## 7. What practitioner reports add

Across Stencil, Anthropic, OpenAI, Manus, Cursor, and LangChain, five operational themes recur.

### 7.1 Durable state and recoverable sessions

Journals, progress files, feature ledgers, plans, commits, and event logs all externalize task state beyond one context window or worker. They support recovery, audit, and handoff. Their recurrence is strong evidence that state policy matters; it is not evidence that one representation is optimal.

### 7.2 Context engineering

Manus emphasizes KV-cache stability, tool masking, filesystem offloading, goal recitation, retention of failures, and avoiding repetitive action patterns. Anthropic emphasizes high-signal context, compaction, structured notes, and isolated subagents. Cursor reports model-specific harness tuning.

These recommendations conflict in predictable ways. Keeping failures aids recovery but costs context; summaries save tokens but lose details; stable tool grammars aid caching but require discovery; subagents compress information but multiply cost and merge risk. This is a multi-objective optimization problem, not a checklist with one global optimum.

### 7.3 Trusted host and bounded executor

Stencil and Anthropic's managed-agent architecture separate durable session state and policy from ephemeral workers and sandboxes. The design improves recoverability and limits credential exposure. It requires explicit contracts for side effects, cancellation, idempotency, and failure.

### 7.4 Verification loops

Anthropic's long-running and application-building reports use ledgers, smoke tests, browser checks, evaluator passes, small commits, and explicit handoffs. OpenAI describes repository legibility, executable rules, CI repair, and durable plans. These are plausible error-feedback mechanisms, but most reports lack controlled task distributions, costs, and quality-adjusted counterfactuals.

### 7.5 Online learning signals

Cursor and LangChain connect offline traces with production failures, behavioral tags, A/B tests, holdouts, operational errors, and human review. This is stronger methodology than optimizing one public benchmark. Repeated holdout reuse and private metrics remain threats.

The full numerical and bias-aware treatment is [`06-practitioner-evidence.md`](06-practitioner-evidence.md).

## 8. Stencil's Harness Playbook as a research source

The Stencil post is the most explicit practitioner systems document in the set. It proposes:

- one authoritative journal-derived session;
- a trusted host control plane and small sandbox stub;
- a common cancellable process-like job abstraction;
- a compositional director over model yields;
- declarative provider capabilities with an explicit unknown state;
- a small permanent tool grammar with long-tail discovery;
- interfaces as projections of semantic state.

Its terminal model distinguishes semantic blocks, logical history, and physical
screen state. If \(F_i\) are finalized blocks, \(W_j\) is the current append-only
block, and \(e_j\) is its emitted prefix, logical history is

\[
L=F_1\cdots F_c\cdot W_j[1..e_j].
\]

The intended invariants include ordered exactly-once logical commitment and resize-independent history. A TLA+ appendix makes the claims inspectable, but this review did not independently model-check it or verify an implementation refinement.

The post's 78-example extension audit and six-run latency comparison are too small and author-controlled for broad causal claims. Its main value is converting engineering intuitions into falsifiable properties: replay equivalence, bounded streams, cancellation, privilege separation, compatibility precedence, and view purity.

## 9. Mathematical foundation

### 9.1 Estimands

For task population \(\mathcal P\), distinguish:

- one-run reliability \(R_1=P(Y=1)\);
- opportunity \(R_{@k}=P(\max_{r\le k}Y_r=1)\);
- repeated consistency \(R_{^k}=P(\min_{r\le k}Y_r=1)\);
- selected-answer correctness \(P(Y_{\tau}=1)\) under stopping/selection rule
  \(\tau\);
- observed verifier acceptance \(P(Z_\tau=1)\);
- cost- or risk-adjusted utility.

These answer different questions. An agent can have high opportunity but low reliability.

### 9.2 Finite-sample pass@k

If \(n\) sampled candidates contain \(c\) successes, the unbiased subset estimator is

\[
\widehat{\operatorname{pass@}k}
=1-\frac{\binom{n-c}{k}}{\binom nk},
\]

with the all-success analogue

\[
\widehat{\operatorname{pass}^{k}}
=\frac{\binom ck}{\binom nk}.
\]

The formulas describe uniform subsets of observed candidates. They do not make adaptive or correlated generation independent.

### 9.3 Correlated retries

A tractable task-heterogeneity model is

\[
\Theta\sim\operatorname{Beta}(\alpha,\beta),
\qquad Y_r\mid\Theta\sim\operatorname{Bernoulli}(\Theta).
\]

Then \(p=\alpha/(\alpha+\beta)\), and the intraclass correlation is

\[
\rho=\frac{1}{\alpha+\beta+1},
\]

and

\[
P(\text{all fail})=\frac{B(\alpha,\beta+k)}{B(\alpha,\beta)},
\qquad
P(\text{all succeed})=\frac{B(\alpha+k,\beta)}{B(\alpha,\beta)}.
\]

Positive task heterogeneity clusters successes and failures. Treating all retries as independent typically overstates effective diversity and produces intervals that are too narrow. The beta-binomial is an interpretable starting model, not a description of adaptive histories or provider drift.

### 9.4 Imperfect verifiers

For latent correctness prevalence \(p\), sensitivity \(s\), and false-positive rate
\(f\),

\[
q=P(Z=1)=sp+(1-p)f,
\]

\[
\operatorname{PPV}=P(Y=1\mid Z=1)=\frac{sp}{sp+(1-p)f}.
\]

With independent candidates, the probability of at least one false positive among
\(k\) evaluated attempts is

\[
1-[1-(1-p)f]^k.
\]

A first-positive policy can therefore stop faster while returning the wrong answer more often. A finite optimal search depth requires a cost, risk, declining-quality, dependence, or stopping model; it does not follow from the geometric curve alone.

### 9.5 Reliability chains

For required independent stages with reliabilities \(r_j\), end-to-end reliability
is \(\prod_j r_j\). Without independence, the universal union lower bound is

\[
P(\text{all stages succeed})\ge 1-\sum_j(1-r_j),
\]

clipped at zero. Shared provider or infrastructure failures make stage dependence important. An absorbing Markov model can represent recovery, retries, terminal success, and terminal failure.

### 9.6 Correcting observed benchmark labels

If observed positive rate is \(q_{\mathrm{obs}}\), sensitivity is \(Se\), and
specificity is \(Sp\), then

\[
q_{obs}=Se\,\pi +(1-Sp)(1-\pi),
\]

so, when \(Se+Sp>1\),

\[
\pi=\frac{q_{obs}+Sp-1}{Se+Sp-1}.
\]

This correction is identified only if the audit estimates the relevant error rates. A failure-enriched sample requires stratified weighting or known inclusion probabilities.

### 9.7 Factorial effects and clustered uncertainty

A starting binary-outcome model includes model, harness, budget, environment, and their interactions, with task and repository random effects. The model–harness interaction tests whether interface changes transfer across models.

Uncertainty must be resampled at the level of independent variation: repository or task family, then task, while preserving paired treatment outcomes. Rollout-level bootstrap alone falsely treats multiple trials of the same task as independent evidence.

### 9.8 Cost and stopping

A harness policy is Pareto-dominated if another policy is no worse in success, latency, human effort, or risk and strictly better in at least one. Report the frontier rather than one accuracy rank.

At history \(h_r\), a conceptual adaptive rule continues when expected marginal
benefit exceeds incremental cost and risk:

\[
\Delta_r(h_r)>c_r(h_r)+\lambda q_r(h_r).
\]

Making this optimal requires a calibrated value model and explicit assumptions. Fixed retry, first-pass, strongest-model, and human-escalation rules remain necessary baselines.

The complete proof and provenance ledger is [`04-mathematical-foundations.md`](04-mathematical-foundations.md). It distinguishes source-reported results, standard derivations for this application, and proposed research models.

## 10. The research opportunity

### Recommended thesis

> **Option C — bounded self-improving context compiler.** Under a fixed context budget, define task-relevant distortion between latent task state and model-visible compiled context. Allow an adaptive outer loop to search a predeclared compiler family, but deploy a replacement only when it clears an independent, immutable promotion rule with a finite-sample improvement margin.

This thesis joins two questions that are usually separated. Rate--distortion asks what task information a bounded context must preserve; statistical validation asks when noisy adaptive evidence is strong enough to replace the incumbent. The proposed theorem is intentionally local: monotone promotion within a fixed finite or capacity-bounded family, on a fixed population and objective, with an independent gate. The realistic agent experiment tests how quickly those assumptions fail under context-window constraints, model--harness interaction, evaluator error, and distribution shift.

### Candidate contributions

1. Define a context compiler, token constraint, information-rate constraint, task-relevant distortion, downstream decision loss, and resource cost without treating tokens as bits.
2. Construct a finite controlled task family in which regret distortion and the rate--distortion frontier can be estimated or solved.
3. Prove a finite-class or capacity-bounded promotion result using an independent gate and an ex-ante fixed objective, compiler class, and margin.
4. Quantify the optimizer's curse as candidate count, search adaptivity, evaluator noise, and gate reuse increase.
5. Compare retrieval, truncation, summarization, a fixed learned compiler, naive adaptive promotion, and valid adaptive promotion at matched context and total-search budgets.
6. Estimate model--compiler interactions, negative transfer, context sufficiency, cost, latency, and safety violations rather than reporting one accuracy average.
7. Keep utility validation distinct from syntax/proof gates, permissions, sandboxing, signed promotion, canary deployment, and rollback.

### Minimal study design

- one finite controlled partially observable task generator with known latent state and exact or computable regret distortion;
- one realistic secondary environment using private, rotating, or time-split tasks, explicitly not covered by the controlled theorem;
- at least two fixed executor models and three compiler families with the same visible-context budget;
- disjoint search, metered promotion, and final locked-audit data, with information access logged by process and artifact;
- an ex-ante reachable class or defensible capacity bound, immutable loss and threshold, and complete evaluation units including model/environment seeds;
- baselines for full history, truncation, retrieval, summarization, static optimization, naive best-validation selection, and no harness evolution;
- repeated independent outer-loop runs, matched search and inference cost, full trajectories, no silent reruns, and paired task-cluster uncertainty;
- atomic versioning and rollback, untrusted candidate execution, fixed permissions, and audit of accepted as well as rejected outputs.

### Secondary alternative: Option A

If the bounded compiler class or task-relevant distortion cannot be specified non-vacuously, **Option A—correlated retries and imperfect verifiers—remains the lower-risk independent paper**. It has cleaner observable estimands and a more direct empirical path, but it is now secondary because it says less about the distinctive self-building harness question. It can also serve as a supporting evaluation chapter for Option C, especially when the promotion gate itself uses stochastic retries or a fallible verifier.

The broader agenda covers context rate-distortion, verified event kernels, factorial model–harness effects, multi-agent information value, adaptive routing, and benchmark retirement. See [`07-research-agenda.md`](07-research-agenda.md) and [`08-paper-thesis-options.md`](08-paper-thesis-options.md).

## 11. Conclusions

LLM harness engineering is not merely prompt engineering, a tool wrapper, or an agent-framework brand. It is a systems discipline spanning stochastic control, partial observability, information selection, distributed execution, security policy, verification, experimental design, and human authority.

The current academic literature supplies mechanisms and important negative results but often changes multiple factors, underreports cost, or relies on fallible public benchmarks. The practitioner literature supplies rich operational failure modes and architecture hypotheses but usually lacks public controls and uncertainty. Open implementations reveal the true configuration surface and show why project names are poor experimental units.

The research program should therefore proceed from precise configurations, simple controls, matched budgets, retained traces, independent clusters, and audited outcomes. The recommended paper makes that program concrete through **Option C**: a rate-constrained context compiler with task-relevant distortion, a bounded adaptive search space, and an independent statistically valid promotion gate. The theorem should govern only the declared compiler class, objective, distribution, and acceptance rule; the experiment should measure where real agents violate those assumptions.

Option A on correlated retries and imperfect verifiers remains a valuable secondary alternative and a natural support module for the promotion study. The 219-source corpus does not establish open-ended self-improvement. It does make a bounded question precise enough to prove, falsify, and engineer responsibly.
