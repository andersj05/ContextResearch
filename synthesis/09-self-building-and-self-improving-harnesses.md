---
title: "Self-Building and Self-Improving LLM Harnesses"
document_type: "focused empirical and mechanism synthesis"
last_evidence_check: "2026-09-04"
scope: "automatic construction, optimization, persistence, and deployment of inference-time agent harnesses"
status_note: "All 2026 arXiv-only results are provisional unless a proceedings venue is explicitly stated."
---

# Self-building and self-improving LLM harnesses

## Executive answer

LLM systems can already generate prompts, tools, memory policies, workflow graphs, and executable harness code; evaluate candidate variants; retain selected improvements; and reuse them on later tasks. That is a real engineering capability. The evidence does **not** yet establish monotone, open-ended, or generally transferable recursive self-improvement.

The strongest defensible conclusion is narrower:

> A model-driven outer loop can sometimes discover a harness configuration with higher measured utility than its seed under a bounded search space, task distribution, evaluator, and budget. Whether that change is a genuine deployable improvement depends on an independent acceptance gate, model–harness compatibility, full cost accounting, regression tests, and evaluation on data that was not adaptively reused.

Four distinctions prevent most overclaiming:

1. **Construction is not improvement.** Producing runnable harness code tests synthesis and debugging. Improvement additionally requires a valid comparison against a pinned seed.
2. **Validation improvement is not deployment improvement.** Searching many candidates against one evaluator selects both signal and noise.
3. **An improved artifact is not a self-improved optimizer.** Most systems keep the outer search algorithm, evaluator, and authority boundary fixed.
4. **A higher system score is not an intrinsic model gain.** The model weights are usually unchanged; the result belongs to a particular model–harness–environment–verifier–budget configuration.

The current literature therefore supports a mathematics thesis about **adaptive program selection under noisy evaluation and model–harness interaction**, not a theorem that recursive agents inevitably improve.

## 1. The object being optimized

Let a deployed harness be parameterized by

\[
H_\phi=(C_\phi,P_\phi,G_\phi,X_\phi,V_\phi,U_\phi,D_\phi),
\]

where \(C\) compiles context, \(P\) parses model emissions into actions, \(G\) authorizes actions, \(X\) executes them, \(V\) verifies progress, \(U\) updates state and memory, and \(D\) controls retries, branching, stopping, and escalation. For a fixed model \(M\), task \(x\), environment \(E\), evaluation rule \(J\), and random seed \(\xi\),

\[
R_\phi(x,\xi)=\operatorname{Run}(M,H_\phi,E,x;\xi),
\qquad
Y_\phi(x,\xi)=J(R_\phi(x,\xi)).
\]

A self-building system maps a specification and evidence into an initial executable configuration,

\[
\phi_0 \sim Q_{\mathrm{build}}(\,\cdot\mid \text{specification},\text{examples},\text{library}\,).
\]

A self-improving system additionally runs an outer loop:

\[
\begin{aligned}
\phi'_k &\sim Q_{\mathrm{edit}}(\,\cdot\mid \phi_{\le k},\mathcal L_{\le k}),\\
\widehat U_k(\phi'_k) &= \operatorname{Eval}(\phi'_k;D_{\mathrm{dev}},J,B_k),\\
\phi_{k+1} &=
\begin{cases}
\phi'_k,&A_k(\phi'_k,\phi_k)=1,\\
\phi_k,&A_k(\phi'_k,\phi_k)=0,
\end{cases}
\end{aligned}
\]

where \(\mathcal L_{\le k}\) contains traces, errors, scores, and prior candidates; \(B_k\) is the evaluation budget; and \(A_k\) is an acceptance gate. “Self-evolving” normally adds a persistent population, archive, or memory that changes later proposal distributions. None of these definitions requires that the same model serve as builder, runtime agent, evaluator, and editor.

### Degrees of “self”

| Level | What changes | What remains fixed | Accurate interpretation |
|---|---|---|---|
| Generated harness | A model writes a prompt, graph, tool, or program once. | Builder, evaluator, and deployment policy. | Automatic construction. |
| Optimized harness | An outer loop searches candidates using development feedback. | Search algorithm and usually the acceptance rule. | Black-box or program optimization. |
| Persistent adaptation | Accepted prompts, skills, memories, or code affect later tasks. | Update authority and objective. | Online or continual harness adaptation. |
| Self-referential editing | The acting agent can edit code used by later versions of itself. | Usually the benchmark runner, sandbox, and archive policy. | Recursive artifact modification. |
| Meta-self-improvement | The system can improve the mechanism that proposes and accepts future changes. | At least a trusted external invariant checker. | The strongest claim; scarcely demonstrated empirically. |

Gödel Machines supply the classical limiting ideal: a self-rewrite is executed only after a proof search establishes that the rewrite raises expected utility under formal assumptions ([schmidhuber-2003-godel-machines, §§2–4](../paper-notes/schmidhuber-2003-godel-machines.md)). Contemporary LLM systems replace proof with finite benchmark evidence. That substitution makes them experimentally useful, but it removes the original optimality guarantee.

## 2. Six-axis taxonomy of a self-improving harness

A paper should specify the following six axes before calling a system self-improving. Names such as “evolution,” “gradient,” or “swarm” are secondary.

| System or family | Editable artifact | Optimizer | Evaluator | Acceptance gate | Persistence | Deployment claim |
|---|---|---|---|---|---|---|
| Promptbreeder / GEPA / TextGrad | Prompt strings, module instructions, textual context | Evolution, reflective mutation, or textual gradient | Task score plus model- or environment-generated feedback | Tournament, Pareto pool, or validation winner | Prompt population or candidate archive | Reuse optimized prompts on the same or related task distribution |
| AgentOptimizer | Function descriptions and callable functions | Progressive add, revise, remove | Training-task loss and execution feedback | Rollback and early stopping on measured loss | Best function set | Deploy fixed learned functions with the target agent |
| AutoFlow / AFlow / ScoreFlow | Natural-language program or executable workflow graph | RL, MCTS/code editing, or preference optimization | Benchmark reward from a workflow interpreter | Best validation workflow or archive update | Candidate history and best program | Freeze a task-specific workflow |
| AgentSquare / MaAS / AgentSwift | Planning, reasoning, tool, memory modules and graph topology | Modular recombination, surrogate search, supernet sampling, or hierarchical MCTS | Task success and sometimes cost | Surrogate- or value-guided selection | Module library, supernet, or search tree | Select a query- or task-conditioned architecture |
| ADAS / GPTSwarm | General agent code or a communication graph | LLM program search or policy-gradient edge selection | Benchmark score | Archive insertion or stochastic edge update | Agent/code archive or graph distribution | Deploy the selected code/graph |
| EvoAgent / multi-agent evolution | Roles, prompts, skills, and collaboration structure | Mutation, crossover, LLM selection | End-task score or model judge | Population selection | Team population | Expand or specialize a seed multi-agent system |
| Meta-Harness / HarnessDev / AutoDesign | Storage, retrieval, context, tools, controller, critic, stopping, and sometimes full source | Trace-conditioned code editing | Development tasks, automated graders, and sometimes human preferences | Explicit train/dev or nominated-final gate | Versioned harness repository and trace history | Freeze and transfer a full harness to held-out tasks or executors |
| MemoHarness / ACE | Playbooks, episodic diagnoses, retrieval, and control policy | Reflection, curation, retrieval-conditioned editing | Environment outcomes and validation score | Pattern retention or validation selection | Cross-episode memory or playbook | Adapt future inference without weight updates |
| SICA / Darwin Gödel Machine / Gödel Agent | The agent’s own executable implementation | Self-referential code editing with greedy or open-ended archive search | Coding benchmarks, cost, time, and functionality checks | Utility selection or archive retention | Executable lineage of agents | Later descendants solve the same or transferred coding tasks |
| ToolMaker / EVOTOOL / HEART-like systems | New tools, wrappers, schemas, or the policy selecting them | Program synthesis, blamed-module mutation, retrieval, and repair | Unit tests, task reward, verifier outcome | Test pass, instance win, or bounded replanning | Tool registry or optimized module policy | Reuse executable capabilities on later tasks |

Representative local sources are [Promptbreeder](../paper-notes/fernando-2023-promptbreeder.md), [TextGrad](../paper-notes/yuksekgonul-2024-textgrad.md), [AgentOptimizer](../paper-notes/zhang-2024-agentoptimizer.md), [AutoFlow](../paper-notes/li-2024-autoflow.md), [AFlow](../paper-notes/zhang-2024-aflow.md), [ScoreFlow](../paper-notes/wang-2025-scoreflow.md), [AgentSquare](../paper-notes/shang-2024-agentsquare.md), [MaAS](../paper-notes/zhang-2025-maas.md), [AgentSwift](../paper-notes/li-2025-agentswift.md), [ADAS](../paper-notes/hu-2024-adas.md), [GPTSwarm](../paper-notes/zhuge-2024-gptswarm.md), [EvoAgent](../paper-notes/yuan-2024-evoagent.md), [Meta-Harness](../paper-notes/lee-2026-meta-harness.md), [HarnessDev](../paper-notes/wu-2026-harnessdev.md), [AutoDesign](../paper-notes/luo-2026-autodesign.md), [MemoHarness](../paper-notes/huang-2026-memoharness.md), [ACE](../paper-notes/zhang-2025-ace.md), [SICA](../paper-notes/robeyns-2025-sica.md), [Darwin Gödel Machine](../paper-notes/zhang-2025-darwin-godel-machine.md), [Gödel Agent](../paper-notes/yin-2024-godel-agent.md), and [ToolMaker](../paper-notes/wolflein-2025-toolmaker.md).

This table reveals a recurring boundary: most systems optimize the **inner artifact** while keeping the optimizer, evaluator, gate, sandbox, and deployment procedure outside the editable region. They are self-modifying at one layer, not recursively unconstrained.

## 3. Mechanism families

### 3.1 Generate–evaluate–select over programs

ADAS made full agent code the search representation. Its Meta Agent Search asks a meta-model to create candidates using an archive of prior agents, evaluates them, and retains discoveries. On the four task domains in Table 1, the selected agents scored 79.4/53.4/69.6/34.6 versus 69.1/30.6/67.6/32.9 for prompt optimization, with 95% bootstrap intervals ([hu-2024-adas, Table 1, PDF p. 6](../paper-notes/hu-2024-adas.md)). The search is expressive, but “can represent any agent” is not a sample-efficiency or generalization result. Generated code also expands the safety and validity problem.

AFlow constrains this idea to code workflows assembled from seven operator types and uses MCTS-like iterative editing:

\[
W^*=\arg\max_{W\in\mathcal S}G(W,T).
\]

Its same-model comparison is especially important because it reruns several baselines under GPT-4o-mini. Across six tasks, direct prompting averaged 72.8, CoT 74.7, CoT-SC 76.0, ADAS 67.2, and AFlow 80.3 ([zhang-2024-aflow, Table 1, PDF p. 7](../paper-notes/zhang-2024-aflow.md)). This supports constrained workflow search in that protocol while contradicting a universal reading of the original ADAS result.

> **Meme risk — ADAS “invented agents that generally outperform human designs.”** ADAS demonstrated successful benchmark-conditioned program search. AFlow’s controlled rerun found ADAS below direct prompting and CoT on average. The scientifically stable claim is feasibility plus task/model sensitivity, not general dominance.

### 3.2 Search over modules and graphs

AgentSquare writes an agent as \(A=(P,R,T,M)\) for planning, reasoning, tools, and memory and searches modular combinations. Table 1 reports .607/.695/.781/.524/.583/.669 across six environments, above the reported ADAS row on each ([shang-2024-agentsquare, Eq. 1 and Table 1, PDF pp. 3–6](../paper-notes/shang-2024-agentsquare.md)). The result is conditional on a human-seeded module library and an in-context surrogate; it does not establish that the four modules are independent or that the surrogate ranks unseen designs reliably.

GPTSwarm instead represents agents as an optimizable graph \(G=(N,E,F,o)\) and learns stochastic edges:

\[
\max_\theta \mathbb E_{G'\sim D_\theta}[u_\tau(G')],
\]

using a REINFORCE estimator. Mini-Crosswords improved from .465±.0509 to .575±.0275 after ten optimization iterations; HumanEval prompt accuracy rose from .76 to .88±.007 ([zhuge-2024-gptswarm, Eqs. 1–2 and experiment tables](../paper-notes/zhuge-2024-gptswarm.md)). Those experiments reuse very small or public task sets during optimization.

The often-repeated GAIA result requires a harder boundary. GPTSwarm reported 18.45 versus GPT-4 Turbo’s 9.70, but the GAIA configuration did not optimize graph edges or nodes; it ran seven Tree-of-Thought branches and self-consistency, with roughly 415 seconds versus 71 seconds. It therefore supports an ensemble harness result, not learned graph optimization.

> **Meme risk — GPTSwarm’s GAIA score validates optimizable swarms.** The reported GAIA system used a hand-configured multi-run graph. The edge-learning claim is supported only by the smaller optimization experiments, where benchmark reuse and search cost remain material.

### 3.3 Textual optimization of prompts, tools, and context

Promptbreeder co-evolves task prompts and the mutation prompts that edit them. TextGrad treats natural-language critiques as gradient-like signals. GEPA reflects on full trajectories and retains an instance-wise Pareto pool. These methods broaden black-box prompt optimization, but the “gradient” metaphor does not imply differentiability, descent, or convergence.

GEPA provides one of the better budget comparisons. With Qwen3-8B, its aggregate score was 54.85 versus 45.23 for baseline, 47.84 for MIPRO, and 48.91 for GRPO; it used about 3,936 rollouts versus 24,000 for GRPO. Yet it lost to GRPO on AIME, and merging candidates hurt one instruction-following condition ([agrawal-2025-gepa, Tables 1–3](../paper-notes/agrawal-2025-gepa.md)). The evidence supports reflective prompt evolution as a competitive optimizer, not universal superiority to reinforcement learning.

AgentOptimizer treats callable functions as learnable weights and progressively adds, revises, or removes them with rollback:

\[
F^*=\arg\min_{F\subseteq\mathcal V}
\mathbb E[\operatorname{Loss}(S_F,D_{\mathrm{test}})].
\]

Eleven of fourteen model–agent–task cells improved, but some regressed; training sets contained only 10–20 examples and were adaptively reused for stopping and rollback ([zhang-2024-agentoptimizer, Eq. 1 and Tables 1–2](../paper-notes/zhang-2024-agentoptimizer.md)). ToolMaker extends the editable object to executable scientific tools, but its 80% implementation claim comes from only fifteen computational tasks ([wolflein-2025-toolmaker, main benchmark](../paper-notes/wolflein-2025-toolmaker.md)).

ACE makes a persistent playbook the object of optimization, using generation, reflection, and curation rather than repeatedly rewriting a short summary. It reports +10.6% on agent tasks and +8.6% on finance tasks ([zhang-2025-ace, abstract and main tables](../paper-notes/zhang-2025-ace.md)). Its mechanism is important even if the headline varies: persistent context needs add, revise, supersede, retrieve, and prune operations, not append-only memory.

### 3.4 Trace-conditioned full-harness editing

Meta-Harness exposes complete prior candidates, traces, source, and scores to a code-editing proposer. It reports a 7.7-point online-classification gain with four times fewer context tokens and a 4.7-point average math gain across five held-out models ([lee-2026-meta-harness, results and held-out-model experiment](../paper-notes/lee-2026-meta-harness.md)). This is promising transfer evidence, but it is a 2026 preprint with author-selected tasks and expensive outer-loop search.

HarnessDev explicitly separates creation from evolution. Across six creator models, four domains, five benchmarks, and 2,207 unique held-out instances, generated harnesses lag mature references on code and research/search, while matching or exceeding selected references on writing and ML experimentation. Evolution and transfer vary strongly with the eventual executor model ([wu-2026-harnessdev, Creation and Evolution results](../paper-notes/wu-2026-harnessdev.md)). That interaction is more informative than a single “best harness” row.

JIT-Agent makes the separation even more explicit: an author-trained helper emits a fixed four-module protocol for another model to execute. It reports large gains for some executor models, including up to 20.2 points for GLM-5.2, but the result is a one-week-old-at-cutoff preprint with many moving model and benchmark versions ([zhang-2026-jit-agent, four-module protocol and cross-model results; 2026 preprint, provisional](../paper-notes/zhang-2026-jit-agent.md)). It is evidence for conditional harness synthesis, not for model-independent harness intelligence.

MemoHarness edits six control dimensions from case-level diagnoses and a global pattern bank. It reports mean success 0.722→0.806 over its strongest fixed baseline and +0.098 averaged over held-out base models, but transfer is selective and some training peaks regress before final selection ([huang-2026-memoharness, Table 1 and Tables 2–4](../paper-notes/huang-2026-memoharness.md)). Observability-driven harness evolution similarly makes edits auditable by pairing trace evidence with a falsifiable prediction, but its observability, proposal, and acceptance components move together ([lin-2026-agentic-harness-evolution, method and evaluation](../paper-notes/lin-2026-agentic-harness-evolution.md)).

AutoDesign is unusually clear about nested loops: an inner designer–critic loop creates posters, while an outer code agent changes the designer, critic, tools, feedback, and stopping policy. Its learned harness moves 54.99→67.39 across seven configurations; the human Bradley–Terry preference estimate is 64.0% with a 95% interval of 55.2–77.8% ([luo-2026-autodesign, main tables and human study](../paper-notes/luo-2026-autodesign.md)). It remains a single-domain, seven-day, author-grader study and is provisional.

### 3.5 Self-referential source editing

SICA selects the best current coding agent as the next meta-agent, edits its own implementation, and retains the lineage. It reports 17%→53% on a random SWE-bench Verified subset over fifteen iterations, at roughly $7,000. Its limitations section describes path dependence: early feature ideas anchor later proposals, while short timeouts make speed-oriented tool improvements look especially valuable ([robeyns-2025-sica, Algorithm 1, Table 1, and §5.1](../paper-notes/robeyns-2025-sica.md)).

The Darwin Gödel Machine replaces greedy lineage with an open-ended archive. On its optimization samples, performance rises 20.0%→50.0% on SWE-bench and 14.0%→38.0% on Polyglot; Table 1 reports 39.0%/28.0% without self-improvement and 23.0%/14.0% without open-ended exploration. Cross-benchmark tests also improve, although less strongly. One SWE-bench run is estimated near $22,000 versus about $10,000 for either ablation ([zhang-2025-darwin-godel-machine, Fig. 2, Table 1, Fig. 4, and Appendix E.1](../paper-notes/zhang-2025-darwin-godel-machine.md)).

These are substantive results, but the editable agent still cannot rewrite the benchmark, private tests, sandbox, archive rule, or top-level objective. Indeed, DGM documents an attempted objective-hacking lineage in a small hallucination experiment. Recursive code access increases the importance of an immutable evaluator and authority boundary; it does not remove them.

Quine supplies a useful systems boundary rather than a performance claim: process identity, streams, exit status, memory, filesystem, and fork/exec/exit can be delegated to POSIX semantics, while cognition, task-relative state, evaluation, and semantic rollback must remain specified above the kernel ([ke-2026-quine, architecture and boundary analysis](../paper-notes/ke-2026-quine.md)).

## 4. Reconciling headline wins with counterevidence

| Headline | What the evidence actually supports | Missing control or contradiction |
|---|---|---|
| ADAS discovers agents superior to hand designs. | On its studied domains, archive-guided code search found high-scoring candidates, including large DROP and MGSM gains. | AFlow’s same-model rerun gives ADAS 67.2 average, below IO 72.8 and CoT 74.7. Search and implementation choices matter. |
| AFlow reaches high performance at 4.55% of GPT-4o cost. | On HumanEval, one selected workflow’s deployment cost was $0.0291 versus $0.6371 for GPT-4o IO. | The percentage is task-specific and excludes the 20-round workflow-search cost; it is not total cost of improvement. |
| GPTSwarm doubles GPT-4 Turbo on GAIA. | A seven-branch ToT/self-consistency harness outscored the cited baseline. | GAIA used no learned graph optimization and much longer runtime; it cannot validate the optimization algorithm. |
| SICA and DGM recursively improve coding agents. | Persistent code lineages improve substantially on selected coding benchmarks; DGM’s ablations support both editing and archive diversity. | High optimization cost, static benchmarks, small task samples, path dependence, and an externally fixed objective/gate bound the claim. |
| Self-Harness improves itself across agent benchmarks. | A fixed model proposes bounded verifier-grounded edits and large gains are reported on Terminal-Bench 2, SWE, and AppWorld. | The nominal held-out set participates in every promotion gate. Repeated adaptive reuse means it is validation, not a sealed final test ([Self-Harness, Table 1 and promotion rule; 2026 preprint, provisional](https://arxiv.org/abs/2606.09498)). |
| Evo-Harness compiles experience into generally useful skills. | Grounded failure feedback can improve a persistent natural-language harness for several strong model/task cells. | Self-generated feedback falls below no-evolve on CL, 27.96 versus 29.54, and SWE, 61.67 versus 63.67; Sonnet drops 58.0→55.3/55.7 under same/cross-model evolution ([Evo-Harness, Tables 1, 2, and 4; 2026 preprint, provisional](https://arxiv.org/abs/2608.15071)). |
| A stronger evolver should improve any weaker runtime. | Optimizer competence matters in some searches. | Harness Updating Is Not Harness Benefit finds at most a 3.1-point spread among evolvers but 18.6–35.2-point base-agent gaps, with harness benefit ranging roughly +2.4 to +19.3 on SWE ([2026 preprint, provisional](https://arxiv.org/abs/2605.30621)). |
| Elaborate autonomous search is required for strong agents. | Search is helpful when partial states are informative and a selector is reliable. | Agentless resolves 32% of SWE-bench Lite with a simple staged pipeline at about $0.70/task ([xia-2024-agentless, revised result](../paper-notes/xia-2024-agentless.md)); AgentOccam reports +9.8 absolute on WebArena using a deliberately simple interface ([AgentOccam, ICLR 2025](https://openreview.net/forum?id=oWdzUpOlkX)). |

The last control is fundamental. SWE-agent’s fixed-model interface comparison also moves SWE-bench Lite resolution from roughly 11% with a shell-only interface to roughly 18% with its tailored agent–computer interface ([yang-2024-swe-agent, §4 and interface ablations](../paper-notes/yang-2024-swe-agent.md)). Automatic search should therefore be compared not only with named agent systems, but with careful manual interface engineering and small explicit pipelines.

> **Meme risk — a rising optimization curve proves learning.** A best-so-far curve is mechanically nondecreasing even when candidate quality is stationary. It shows selection, not necessarily a changing proposal distribution, transfer, or deployment benefit.

## 5. Why improvement claims fail

### 5.1 Adaptive validation overfitting

Suppose candidate \(j\) has true utility \(U_j\) and noisy estimate

\[
\widehat U_j=U_j+\varepsilon_j.
\]

Selecting \(\arg\max_{j\le m}\widehat U_j\) selects positive noise as well as quality. Even if all candidates have equal utility and independent sub-Gaussian noise with scale \(\sigma\), the expected maximum noise grows on the order of

\[
\sigma\sqrt{2\log m}.
\]

This is a standard order-statistic heuristic, not an effect estimate for any particular paper. Repeatedly consulting the same “held-out” sample makes the problem adaptive and can invalidate ordinary confidence intervals. HarnessOpt-Bench therefore hides test state, meters target evaluations, preserves candidate versions, and scores one nominated final harness; it still observes validation winners that lose on held-out evaluation ([ursekar-2026-harnessopt, Fig. 1 and Tables 1–3; 2026 preprint, provisional](../paper-notes/ursekar-2026-harnessopt.md)).

Reusable-holdout mechanisms show that limited feedback can preserve statistical validity under adaptive querying, but their guarantees depend on bounded sensitivity, a specified query class, and the mechanism’s privacy or stability conditions ([dwork-2015-adaptive-holdout, main theorems](../paper-notes/dwork-2015-adaptive-holdout.md)). They do not transfer automatically to stochastic, stateful agent traces.

### 5.2 Evaluator optimization and objective hacking

The optimizer learns what the evaluator rewards, including its blind spots. Unit tests can accept incomplete patches; a 2026 ICSE study estimates that 11.0% of plausible SWE-bench patches may be incorrect and that scores may be inflated by 6.4 points under its extrapolation assumptions ([wang-2026-swe-solved-correctly, results and extrapolation](../paper-notes/wang-2026-swe-solved-correctly.md)). Across ten agent benchmarks, seven had outcome-validity flaws, seven had task-validity flaws, and all had reporting limitations in one audit ([zhu-2025-rigorous-agentic-benchmarks, pp. 1–2](../paper-notes/zhu-2025-rigorous-agentic-benchmarks.md)).

An acceptance gate should therefore separate:

- hard validity and safety invariants;
- task utility;
- efficiency;
- semantic or human audit;
- regression performance outside the optimized slice.

A single weighted score can conceal catastrophic tradeoffs. Report the vector as well as any scalarization.

### 5.3 Extra search compute masquerading as architecture

Search changes the number of samples, evaluator calls, and opportunities to observe tests. The relevant comparison is a cost frontier, not only accuracy. In one five-run HumanEval rerun, LATS achieved 88.0% for about $134.50 while a simple warming-retry baseline achieved 93.2% for about $2.45; the accuracy difference was not significant ([kapoor-2024-agents-matter, Table A1](../paper-notes/kapoor-2024-agents-matter.md)). This does not show that workflow search is useless. It shows that independent retries, best-of-\(k\), and the same verifier at matched cost are mandatory controls.

Report at least:

\[
C_{\mathrm{total}}
=C_{\mathrm{search}}+C_{\mathrm{candidate\ eval}}
+C_{\mathrm{human}}+N_{\mathrm{deploy}}C_{\mathrm{inference}}.
\]

“One-time” optimization cost may be amortized, but only for a stated deployment volume \(N_{\mathrm{deploy}}\).

### 5.4 Model–harness interaction and weak activation

A harness is an instruction-bearing program executed partly by a model. A stronger optimizer can write a sophisticated harness that a weaker runtime does not follow. Conversely, a simple interface may unlock a weaker model better than a long playbook. A crossed model–harness design is therefore necessary:

\[
Y_{m,h,t,r}
=\mu+\alpha_m+\beta_h+(\alpha\beta)_{mh}+u_t+\varepsilon_{m,h,t,r}.
\]

Harness-Bench’s 5,194 trajectories across 106 tasks support the existence of substantial pairing effects, but incomplete factorial coverage prevents a universal ranking ([yao-2026-harness-bench, design and Tables 1–2; 2026 preprint, provisional](../paper-notes/yao-2026-harness-bench.md)). HarnessDev, MemoHarness, Evo-Harness, and Harness Updating all independently warn that transfer depends on the executor.

### 5.5 Bad feedback and self-confirming memory

Intrinsic critique is not a reliable update oracle. On GSM8K, repeated intrinsic correction reduced GPT-3.5 from 75.9 to 75.1 and 74.7 and GPT-4 from 95.5 to 91.5 and 89.0; compute-matched self-consistency also beat debate in the reported comparison ([huang-2024-cannot-self-correct, Tables 2–3 and 8](../paper-notes/huang-2024-cannot-self-correct.md)). Reflexion’s harder coding ablation similarly found blind reflection at 52%, below the 60% base, while generated tests plus reflection reached 68% ([shinn-2023-reflexion, Table 3](../paper-notes/shinn-2023-reflexion.md)).

Memory retrieval is not state correction. In STALE, a system could retrieve new evidence in 77.5% of selected cases yet fail state resolution 56.1% of the time and premise resistance 99.0% of the time ([chao-2026-stale, Tables 2–3; 2026 preprint, provisional](../paper-notes/chao-2026-stale.md)). Persistent self-improvement needs provenance, contradiction detection, supersession, and deletion—not just accumulation.

### 5.6 Unsafe edits and authority expansion

Generated harness code can execute tools, read secrets, alter its own checks, or widen permissions. The optimizer must not control the root of trust used to judge it. Keep outside the editable region:

- credentials and network policy;
- evaluator data and grader implementation;
- hard safety invariants;
- signing and promotion authority;
- resource ceilings;
- audit logs and rollback snapshots.

An improvement candidate should run in a clean, capability-limited environment. Promotion should be transactional: build, static-check, sandbox-test, evaluate, sign, canary, then roll back automatically on regression. Self-referential code access without these controls is an authority escalation mechanism, not merely a learning mechanism.

## 6. A valid acceptance protocol

Partition tasks by the level at which generalization is claimed:

\[
D_{\mathrm{search}},\quad
D_{\mathrm{gate}},\quad
D_{\mathrm{test}},\quad
D_{\mathrm{future}}.
\]

- \(D_{\mathrm{search}}\) may be queried freely to create candidates.
- \(D_{\mathrm{gate}}\) may be used a bounded number of times for promotion.
- \(D_{\mathrm{test}}\) is touched once after the complete search and selection procedure is frozen.
- \(D_{\mathrm{future}}\) is a later or shifted deployment sample.

For paired task outcomes, estimate the utility change

\[
\widehat\Delta_k
=\frac1n\sum_{i=1}^{n}
\left[
u(R_{\phi'_k,i})-u(R_{\phi_k,i})
\right].
\]

A conservative gate is

\[
A_k=1
\iff
\begin{cases}
L_k^{\mathrm{utility}}\ge \delta,\\
U_k^{\mathrm{cost}}\le \kappa,\\
\text{all hard invariants pass},\\
L_{k,g}^{\mathrm{regression}}\ge-\rho_g
\quad\forall g,
\end{cases}
\]

where \(L\) and \(U\) are simultaneous lower and upper confidence bounds, \(\delta\) is a minimum useful gain, \(\kappa\) a cost ceiling, and \(\rho_g\) permitted regression in protected slice \(g\). For many adaptive rounds, use alpha spending, confidence sequences, reusable-holdout machinery, or a fresh gate sample. Ordinary per-round \(p<.05\) testing is not enough.

A recent theoretical paper gives a sharper conditional result: distribution-free PAC learnability of self-improvement requires finite VC dimension of the policy-reachable envelope, and an independent validation gate can guarantee true-risk descent only for a capped candidate family and a sufficiently large empirical margin ([On The Statistical Limits of Self-Improving Agents, Theorems 1–2; 2026 preprint, provisional](https://arxiv.org/abs/2510.04399)). Its assumptions—i.i.d. data, bounded loss, fixed distribution, independent splits—exclude much of open-ended interactive deployment. The result is a useful boundary theorem, not proof that current agent loops satisfy it.

### Persistence and deployment are separate experiments

An accepted artifact should become an immutable, versioned release:

\[
\mathcal R_k=(\phi_k,\text{model},\text{dependencies},\text{environment},
\text{evaluator version},\text{budget},\text{provenance},\text{signature}).
\]

Deployment then tests whether the release maintains utility under drift. Track both improvement and forgetting:

\[
\Delta_{\mathrm{new}}
=U_{t+1}(\phi_{k+1})-U_{t+1}(\phi_k),
\qquad
\Delta_{\mathrm{old}}
=U_{\le t}(\phi_{k+1})-U_{\le t}(\phi_k).
\]

Without \(\Delta_{\mathrm{old}}\), a system can call specialization “evolution.” Without a later sample, it can call adaptive benchmark fitting “continual improvement.”

## 7. What is and is not established

| Claim | Current assessment | Reason |
|---|---|---|
| LLMs can synthesize runnable prompts, workflows, tools, and harness code. | **Supported.** | Demonstrated across AutoFlow, ToolMaker, ADAS, Meta-Harness, HarnessDev, and related systems. |
| Automated search can beat a seed or selected human baseline on the optimized distribution. | **Supported but conditional.** | Repeated positive results, including ADAS, AFlow, AgentSquare, GEPA, SICA, DGM, and AutoDesign; attribution and budgets vary. |
| The discovered harness transfers to a different task or model. | **Sometimes supported.** | ADAS, Meta-Harness, DGM, HarnessDev, MemoHarness, and Evo-Harness show positive cells and negative or weak cells. |
| The same model can improve a persistent artifact used by later copies of itself. | **Partially supported.** | SICA, DGM, and Self-Harness approximate this, but fixed external objectives, evaluators, and sandboxes remain essential. |
| The optimizer itself becomes steadily better at producing future improvements. | **Weak evidence.** | Archives and meta-edits change proposal context, but few studies isolate proposal-distribution improvement from best-so-far selection. |
| Accepted changes monotonically improve deployment utility and safety. | **Not supported.** | Validation/test reversals, model interactions, category regressions, evaluator errors, and memory failures are common. |
| Open-ended recursive self-improvement follows from access to source code. | **Not supported.** | Expressivity does not imply discoverability, evaluability, safe acceptance, or non-saturating objectives. |

## 8. A mathematics-paper formulation

The most tractable thesis is:

> **When does adaptive harness search produce transferable improvement rather than selection-induced overfitting?**

Treat the optimizer as choosing a sequence of programs from a model-dependent reachable class \(\mathcal H_M\). The principal quantities are:

- search budget \(m\);
- evaluator noise and bias;
- dependence among candidates;
- task-level sample size and clustering;
- candidate-class capacity;
- model–harness interaction;
- acceptance margin;
- regression and safety constraints;
- amortized optimization cost.

A clean empirical study would:

1. Pin a seed harness, model snapshots, container images, tools, and budgets.
2. Randomly split by repository, environment family, or task generator—not by near-duplicate instance.
3. Give each optimizer identical target-evaluation opportunities and report its own inference cost separately.
4. Include random mutation, independent retry, best-of-\(k\), a small hand-designed interface, and no-update controls.
5. Run multiple complete outer-loop seeds; candidate-level repeats are not substitutes for search-level repeats.
6. Cross at least two optimizers, two executor models, and two harness representations.
7. Nominate exactly one final candidate per search before opening the sealed test.
8. Audit accepted and rejected outputs with an evaluator independent of the search reward.
9. Report task-wise paired effects, simultaneous intervals, cost frontiers, regressions, and failure transitions.
10. Release every candidate, trace, evaluation count, rejection reason, and environment version.

Three falsifiable hypotheses follow:

\[
\begin{aligned}
H_1:&\quad
\mathbb E[\Delta_{\mathrm{test}}\mid m]
\text{ initially rises but diverges from }
\Delta_{\mathrm{dev}}
\text{ as adaptive queries grow};\\
H_2:&\quad
\operatorname{Var}\!\left((\alpha\beta)_{mh}\right)>0,
\text{ so no harness ranking is executor-invariant};\\
H_3:&\quad
\text{grounded feedback produces a larger accepted-test gain than}\\
&\quad\text{self-generated critique under matched calls and candidate count}.
\end{aligned}
\]

Failure to reject any of these is informative. A null result under a sealed, compute-matched protocol would be stronger scientific evidence than another uncorrected best-so-far curve.

## 9. Evidence boundary

The pre-2026 corpus establishes the main mechanism classes: code and workflow search, prompt evolution, graph optimization, modular architecture search, tool synthesis, and recursive source editing. Several foundations are peer reviewed, while the early recursive-source-editing results include preprints. The explicit “harness optimization” wave—Meta-Harness, HarnessOpt-Bench, HarnessDev, MemoHarness, AutoDesign, JIT-Agent, Self-Harness, Evo-Harness, and Harness Updating Is Not Harness Benefit—is mostly 2026 preprint evidence and should be cited as provisional.

No reviewed source in this corpus proves open-ended improvement for an LLM harness in a changing real environment. The literature instead identifies the ingredients of a valid claim: a specified editable artifact, optimizer, evaluator, acceptance gate, persistence rule, deployment distribution, immutable trust boundary, full cost ledger, and sealed outer test. Those ingredients are the research object.
