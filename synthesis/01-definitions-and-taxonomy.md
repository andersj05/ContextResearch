# LLM harness engineering: definitions and taxonomy

**Research snapshot:** 2026-09-04  
**Scope:** inference-time systems that turn one or more language-model calls into stateful, tool-mediated work  
**Evidence convention:** citations use repository source IDs and PDF page, section, table, figure, or theorem locators where available  
**Status warning:** the papers that explicitly use the term *harness engineering* are mostly 2026 preprints. The operational definition below is therefore anchored in those papers but tested against older, peer-reviewed component research and negative results.

## Executive definition

**LLM harness engineering is the engineering and scientific study of the runtime controller that transforms model calls into bounded, stateful interactions with an external environment.** The harness selects and formats context, exposes and validates actions, executes or delegates them under permissions and budgets, records observations, updates persistent state, schedules retries or branches, invokes verification, and decides when to stop or ask for help.

This definition is intentionally behavioral. A component belongs to the harness when, at inference or execution time, it mediates the loop between model output and world state and can change the distribution of trajectories while the model endpoint, task, environment, evaluator, and resource budget are held fixed. A prompt template, tool registry, memory retriever, parser, sandbox policy, verifier, or scheduler can therefore be a harness component; a model checkpoint, a passive API, the repository being edited, and the benchmark scorer are different objects.

The short slogan “agent = model + harness” is a useful accounting identity, not a complete ontology. A 2026 source-code study defines the harness as the runtime coupling an LLM to the world and separates it from scaffolds, frameworks, evaluation harnesses, and meta-orchestrators; its seven observed subsystems are the loop, model integration, tools/actions, memory/context, safety/permissions, orchestration, and extensibility ([barbaste-2026-harness-anatomy, §2.1–2.3 and Table 1, PDF pp. 3–5](../papers/academic/barbaste-2026-harness-anatomy.pdf)). That study is descriptive—eleven coding systems, no controlled performance experiment—so it supports the anatomy, not a claim that any pattern causes higher accuracy.

## The formal object

Let \(M\) be a fixed model endpoint, \(T\) a task, \(E_t\) the external environment at step \(t\), \(J\) an evaluator, and \(H\) a harness. A run is a stochastic trajectory

\[
R = \operatorname{Run}(M,H,E_0,T;\xi),
\qquad
Y = \operatorname{Eval}(R;J),
\]

where \(\xi\) includes sampling, tool, environment, and service nondeterminism. This follows the model–harness–environment separation used by Harness-Bench ([yao-2026-harness-bench, §3 and equations on PDF pp. 4–5](../papers/academic/yao-2026-harness-bench.pdf)). Its reported configuration scores are diagnostics, not component-level causal estimates; the authors say this explicitly ([yao-2026-harness-bench, §2, PDF p. 2](../papers/academic/yao-2026-harness-bench.pdf)).

A useful decomposition of \(H\) is

\[
\begin{aligned}
c_t &= C_H(s_t,T,b_t), &&\text{context projection},\\
z_t &\sim M(\cdot\mid c_t), &&\text{model emission},\\
a_t &= P_H(z_t,s_t), &&\text{parse/construct an action},\\
g_t &= G_H(s_t,a_t), &&\text{authorize, deny, or request approval},\\
(o_t,E_{t+1}) &= X_H(a_t,E_t;g_t), &&\text{execute and observe},\\
v_t &= V_H(s_t,a_t,o_t,E_{t+1}), &&\text{verify or grade},\\
s_{t+1} &= U_H(s_t,a_t,o_t,v_t), &&\text{update state},\\
d_t &= D_H(s_{t+1},v_t,b_t), &&\text{continue, retry, branch, stop, or escalate}.
\end{aligned}
\]

Here \(s_t\) is harness state, \(c_t\) is the bounded view shown to the model, \(z_t\) is unconstrained model output, \(a_t\) is an admissible action, \(o_t\) is an observation, \(v_t\) is verification evidence, and \(b_t\) is the remaining resource/authority budget. The model never sees the full state unless \(C_H\) chooses to expose it. A related 2026 position paper writes \(a_t\sim\pi_\theta(\cdot\mid c(s_t))\) and treats the harness as the controller mapping \((s_t,a_t,o_t)\) to \(s_{t+1}\) ([zhang-2026-stop-comparing, §2.2, PDF p. 3](../papers/academic/zhang-2026-stop-comparing.pdf)). Its stability, context-drift, and control-lag formulas are proposed research instruments, not established laws.

This state machine is deliberately broader than a ReAct loop. It includes a single while-loop, a graph runtime, tree search, an event-sourced controller, a planner–executor pair, a human approval loop, and a multi-agent scheduler. It also exposes where failures originate: bad model proposal \(z_t\), lossy context \(C_H\), invalid parsing \(P_H\), excessive authority \(G_H\), execution error \(X_H\), weak oracle \(V_H\), corrupt state \(U_H\), or runaway scheduling \(D_H\).

### The harness effect

For research, “harness effect” should mean a controlled contrast, not the score of a named product:

\[
\Delta_H
=
\mathbb{E}[Y\mid \operatorname{do}(H=H_1),M,E,T,J,B]
-
\mathbb{E}[Y\mid \operatorname{do}(H=H_0),M,E,T,J,B],
\]

with the model endpoint, task instances, environment version, evaluator, and budget \(B\) fixed. This equation is a **derived experimental definition**, not a theorem from a source. If more than one harness component changes, the estimand is a configuration effect. If the model changes too, model–harness interaction must be estimated rather than attributed to either side.

An appropriate factorial model is, for example,

\[
Y_{m,h,t,r}=\mu+\alpha_m+\beta_h+(\alpha\beta)_{mh}+u_t+\varepsilon_{m,h,t,r},
\]

where \(m\) indexes models, \(h\) harness configurations, \(t\) tasks, and \(r\) repeated runs. The interaction term matters: a harness can improve one model and harm another. A proposed variance decomposition in the 2026 disclosure position paper makes the same point ([zhang-2026-stop-comparing, Eq. 1, PDF p. 4](../papers/academic/zhang-2026-stop-comparing.pdf)), but that paper is not empirical validation of the decomposition.

## Boundary dictionary

| Term | Operational definition | Relation to the harness | Experimental handling |
|---|---|---|---|
| **Model** | A fixed conditional generator or model endpoint \(M(z\mid c)\), including any inseparable provider-side behavior. | Proposes text, plans, or calls; it does not by itself execute external actions. | Pin model/version/endpoint and sampling parameters. If provider-side routing or hidden prompting cannot be separated, treat the whole endpoint as \(M^\ast\). |
| **Harness** | The runtime controller \(H=(C,P,G,X,V,U,D)\) mediating context, action, execution, state, verification, authority, and control flow. | Object of study. | Version code *and* prompts, tool schemas, permissions, budgets, memory, and stop rules. |
| **Agent** | The acting compound system instantiated from at least a model and harness, operating on a task in an environment. | \(A=(M,H)\) is a useful shorthand; deployed behavior also depends on \(E,T,\xi\). | Do not report an “agent” result without decomposing model, harness, environment, and budget. |
| **Scaffold** | Structural code or a procedural template for assembling a loop, planner, roles, or prompts. | A scaffold becomes part of a harness when instantiated as the running controller. It may omit product concerns such as persistence, permissions, recovery, and interfaces. | Report the instantiated configuration, not only the scaffold name. The scaffold/runtime distinction is discussed in [barbaste-2026-harness-anatomy, §2.2, PDF p. 4](../papers/academic/barbaste-2026-harness-anatomy.pdf). |
| **Framework / SDK** | A library used to build controllers, graphs, agents, or tool integrations. | Construction material, not necessarily the deployed harness. A framework instance may implement one. | Pin framework version and the application graph/configuration. The 2026 source study found no major “agentic framework” imports on production paths in its eleven-system corpus, but this is corpus-specific ([barbaste-2026-harness-anatomy, §13.2, PDF pp. 53–54](../papers/academic/barbaste-2026-harness-anatomy.pdf)). |
| **Tool** | A capability endpoint with an action schema and execution semantics: shell, browser, database, API, code runner, or human channel. | Passive affordance. Registry, selection, argument validation, authorization, dispatch, retry, and observation filtering are harness functions. | Pin tool version/schema and separate “tool available” from “tool selected and used correctly.” |
| **Environment** | External state and transition dynamics \(E_{t+1}=\Phi(E_t,a_t)\): files, services, websites, simulators, people, and clocks. | The world acted upon. A sandbox policy is harness control; the sandboxed filesystem/process state is environment. | Reset or snapshot initial state; record nondeterminism and side effects. |
| **Context** | The finite, ordered, privilege-labelled projection \(c_t=C_H(s_t,T,b_t)\) delivered to a model call. | A harness product, not a synonym for all history or memory. | Record included items, order, provenance, truncation, and token budget. |
| **Memory** | State persisted beyond the immediate model call: working, episodic, semantic, procedural, or artifact memory. | Storage alone is not enough; write, retrieve, reconcile, compress, and injection policies belong to the harness. | Evaluate retrieval and correct use separately. Stale-evidence experiments show that retrieval success can coexist with failure to update beliefs ([chao-2026-stale, Tables 2–3, PDF p. 6](../papers/academic/chao-2026-stale.pdf)). |
| **Orchestrator / meta-harness** | A controller that schedules or routes among complete agents/harness instances. | Outside an inner harness if it has no model-to-world loop of its own; a harness at a higher level if it maintains state, authority, execution, and updates for the ensemble. | State the level of analysis. Do not count workers and orchestration policy as one mechanism. |
| **Evaluator / judge** | A function \(J\) mapping completed trajectories or final state to measurements. | External to the agent harness when it only scores; internal \(V_H\) when its output controls the ongoing run. The same model can play either role, creating leakage risk. | Keep the final evaluator independent of the controller’s verifier where possible. |
| **Evaluation harness** | Infrastructure that resets tasks, launches the agent, enforces evaluation budgets, and collects/scores outputs. | Wraps the agent; the agent harness wraps the model. | Version separately. This “opposite direction of wrapping” is explicit in [barbaste-2026-harness-anatomy, §2.2, PDF p. 4](../papers/academic/barbaste-2026-harness-anatomy.pdf). |
| **Benchmark** | A task distribution plus initial environments, run protocol, budgets, ground truth, and evaluator. | Measurement setting, not part of the deployed agent. | Report task version, exclusions, contamination risks, pass criteria, number of trials, and cost. |

These boundaries are operational, not metaphysical. A built-in browser can be packaged with the harness but still acts as a tool. A verifier becomes harness logic when its output causes retry or acceptance. A provider endpoint may hide its own tool router; if it cannot be held fixed separately, it belongs in the experimentally fixed model endpoint rather than being guessed away.

## Taxonomy of harnesses

No single linear “autonomy level” captures harness structure. Classify a harness on the following independent axes.

### 1. Control topology

| Topology | State transition | Characteristic benefit | Characteristic risk |
|---|---|---|---|
| Linear action loop | one proposal, one execution, one update | transparent lower-bound controller | myopic repetition; no explicit alternatives |
| Planner–executor | plan state separated from action state | decomposition and progress tracking | stale plans; planner/executor mismatch |
| Search controller | maintains frontier/tree/graph of candidate states | explores alternatives and can backtrack | rapidly increasing tokens/cost; weak value model |
| Event-sourced graph | append-only events drive typed reducers/nodes | replay, recovery, concurrency, audit | complex ordering and state-reducer bugs |
| Outer verification loop | candidate loop nested inside independent acceptance/recovery loop | blocks false completion | verifier gaming, test leakage, endless repair |
| Multi-agent scheduler | messages, roles, or tasks coordinate several model contexts | diversity and parallel specialization | correlated errors, conformity, coordination cost |
| Human-in-the-loop | approval, clarification, or editing is an explicit transition | calibrated authority and ambiguity resolution | latency; hidden human labor confounds autonomy |

The production source study observes linear, event-sourced, recursive-composition, context-forking, outer-verification, and session-tree patterns ([barbaste-2026-harness-anatomy, Tables 11–12, PDF pp. 52–53](../papers/academic/barbaste-2026-harness-anatomy.pdf)). Presence is not evidence of superiority: the same study reports that loop sophistication did not predict self-reported benchmark performance across its heterogeneous systems ([barbaste-2026-harness-anatomy, Observation 1, PDF p. 12](../papers/academic/barbaste-2026-harness-anatomy.pdf)).

### 2. Context and state policy

- **Ephemeral:** only current prompt and observation.
- **Windowed:** recent turns under a fixed token/window policy.
- **Compacted:** summaries replace parts of history.
- **Retrieved:** external records are selected by lexical, embedding, graph, or learned retrieval.
- **Structured:** plans, hypotheses, task state, artifacts, and evidence live in typed stores.
- **Persistent:** state survives sessions and may be shared or forked.
- **Reconciled:** new evidence can invalidate or supersede old state instead of merely being appended.

The last distinction is essential. “Memory” systems often optimize recall, while stateful work requires temporal adjudication. In STALE, some systems retrieved updated evidence frequently yet still failed to resolve the conflict; the paper’s Table 3 separates retrieval from failure despite evidence ([chao-2026-stale, Table 3, PDF p. 6](../papers/academic/chao-2026-stale.pdf)).

### 3. Action and execution policy

- **Free-form text** interpreted by a parser.
- **Constrained structured calls** validated against schemas.
- **Code actions** executed in an interpreter or shell.
- **Retrieved/deferred tools** selected from a larger catalog.
- **Transactional actions** with preview, commit, compensation, or rollback.
- **Delegated actions** sent to another agent, service, or human.

Action representation is a genuine treatment variable. SWE-agent showed large differences from changing the agent–computer interface while holding the underlying model family central to the comparison, but the result is tied to coding tasks and a manually designed interface ([yang-2024-swe-agent, §4 and interface ablations](../papers/academic/yang-2024-swe-agent.pdf)). ToolLLM combines retrieval, tool-use training, and depth-first search, so its gains cannot be assigned to a single harness component ([qin-2023-toolllm, §3–4](../papers/academic/qin-2023-toolllm.pdf)).

### 4. Feedback and verification policy

- **Intrinsic:** the same model critiques or revises its own output without new evidence.
- **Environmental:** compiler, tests, browser state, API response, simulator, or user supplies new evidence.
- **Model-graded:** another call scores, ranks, or critiques candidates.
- **Deterministic:** a checker validates an invariant or final state.
- **Hybrid:** deterministic checks gate model judgment or vice versa.

This taxonomy prevents “reflection” from swallowing several distinct mechanisms. Reflexion’s programming ablation found that blind reflection did not improve a hard subset, while test generation plus verbal reflection did ([shinn-2023-reflexion, Table 3](../papers/academic/shinn-2023-reflexion.pdf)). Conversely, intrinsic self-correction without external feedback often degraded reasoning accuracy ([huang-2024-cannot-self-correct, Tables 2–3 and 8](../papers/academic/huang-2024-cannot-self-correct.pdf)). The scientifically relevant variable is therefore the information and selection channel, not the word *reflection*.

### 5. Authority and containment policy

Classify each action by its maximum effect:

1. read-only and reversible;
2. local write with rollback;
3. external write or communication;
4. financial, credential, privacy, deployment, or physical effect;
5. delegation of authority to another principal.

For each class, record allow/deny rules, sandbox boundary, approval point, credential scope, rate/budget limits, idempotency, rollback, and audit trail. ToolEmu demonstrates why capability scores alone are inadequate: on 144 high-stakes test cases, its safest tested prompted agent still had 23.9% evaluator-identified failures, while “NoAct” achieved perfect safety but near-zero helpfulness ([ruan-2023-toolemu, Table 5, PDF p. 11](../papers/academic/ruan-2023-toolemu.pdf)). The estimate depends on an LM emulator and LM evaluator; end-to-end identified-failure precision was 68.8%–72.5% in human validation ([ruan-2023-toolemu, Tables 3–4, PDF p. 10](../papers/academic/ruan-2023-toolemu.pdf)).

### 6. Resource and stopping policy

Report token, call, wall-clock, dollar, tool, branch, and human-intervention budgets. Distinguish:

- fixed steps or fixed samples;
- confidence/evidence thresholds;
- adaptive compute allocation;
- failure/stuck detection;
- success verified by an external condition;
- model-declared completion;
- human escalation.

This axis is routinely hidden. A rerun of several agent methods found that a simple retry baseline could outperform elaborate search at far lower cost on HumanEval: warming retry reached 93.2% at about $2.45 versus LATS at 88.0% and about $134.50 in that study ([kapoor-2024-agents-matter, Table A1](../papers/academic/kapoor-2024-agents-matter.pdf)). That does not prove search is useless; it proves that compute, selection, and retry baselines must be disclosed.

## What counts as evidence about a harness?

Use the strongest label justified by the design:

| Evidence level | Minimum condition | What it supports |
|---|---|---|
| **Controlled harness effect** | Same \(M,T,E,J,B\); one randomized harness difference; repeated paired runs | Causal effect for that component and setting |
| **Factorial interaction** | Multiple models and harness variants with task blocking and repeated runs | Main and model–harness interaction effects |
| **Component ablation** | One subsystem removed or replaced within a system | Local necessity/sensitivity, subject to compensation effects |
| **Configuration comparison** | Complete systems/configurations differ in several ways | End-to-end ranking only |
| **Source-code observation** | Versioned implementation inspected | Mechanism exists and is implemented as described |
| **Demonstration/case study** | Selected trajectories or qualitative examples | Feasibility and failure hypotheses |
| **Position/proposal** | Conceptual framework or unexecuted protocol | Vocabulary and testable hypotheses |

Harness-Bench’s 106 tasks and 5,194 trajectories are valuable configuration-level evidence; its Table 2 reports a 23.8-point gap between two configurable harnesses, but multiple configuration dimensions vary and an LLM contributes to process scoring ([yao-2026-harness-bench, Tables 1–2, PDF p. 6](../papers/academic/yao-2026-harness-bench.pdf)). Treat the number as evidence that harness configuration can be behaviorally material, not as the causal effect of a named subsystem.

## Meme-risk boxes

> **Meme risk: “Agent = model + harness” means a clean physical split.** It is an experimental convention. Hosted endpoints can hide routing, safety, memory, or tool behavior. Define the fixed endpoint and observable controller boundary; do not invent an internal separation.

> **Meme risk: a better agent score proves a better harness.** End-to-end systems often change model, prompt, tools, retrieval, compute, and evaluator together. Without a controlled contrast, the result is a configuration score. The cost-controlled reruns in [kapoor-2024-agents-matter, Table A1](../papers/academic/kapoor-2024-agents-matter.pdf) are a direct warning.

> **Meme risk: visible reasoning is a planner.** A chain-of-thought string may be transient model output. Planning becomes a harness mechanism when plans are represented in state, checked against observations, revised by an update rule, and coupled to scheduling or acceptance.

> **Meme risk: memory is retrieval or a longer prompt.** Retrieval answers “what record is similar?” Stateful control must also answer “which record is current, authoritative, and safe to expose?” Lost-in-the-middle position effects and stale-evidence failures make those separate questions ([liu-2024-lost-middle, §4 and position experiments](../papers/academic/liu-2024-lost-middle.pdf); [chao-2026-stale, Tables 2–3](../papers/academic/chao-2026-stale.pdf)).

> **Meme risk: self-reflection creates information.** Revision can help when it exposes a better sample or uses new evidence; it can also amplify the original error. On several reasoning tasks, intrinsic self-correction failed while oracle feedback helped ([huang-2024-cannot-self-correct, Tables 2–3](../papers/academic/huang-2024-cannot-self-correct.pdf)). A 2026 role-label experiment further shows that the appearance of “correction” can change sharply while final accuracy does not ([chen-2026-self-correction-illusion, Table 11](../papers/academic/chen-2026-self-correction-illusion.pdf)).

> **Meme risk: more agents imply more independent intelligence.** Many “multi-agent” gains are ordinary sampling and aggregation with extra tokens. Majority vote frequently matches or beats debate, and correlated agents can converge on shared errors ([choi-2025-debate-or-vote, Table 1 and Theorems 1–2](../papers/academic/choi-2025-debate-or-vote.pdf); [yang-2025-revisiting-mad, Table 1](../papers/academic/yang-2025-revisiting-mad.pdf)).

## A concise inclusion test

When deciding whether a mechanism belongs in a harness study, ask:

1. Does it run at inference/execution time rather than changing model weights?
2. Does it control context, admissible action, execution, state update, verification, authority, scheduling, or stopping?
3. Could changing it alter the trajectory distribution with the model endpoint fixed?
4. Can its inputs, outputs, version, and budget be logged?
5. Is it inside the acting system rather than solely wrapping and scoring the completed run?

“Yes” to 1–3 usually makes it a harness component. Question 4 determines scientific tractability. Question 5 distinguishes the agent harness from the evaluation harness. Border cases should be declared, versioned, and tested rather than settled by branding.

## Working research principle

The most useful unit for mathematics is not a product called an agent and not a transcript called reasoning. It is a controlled stochastic controller:

\[
(M,H,E,T,J,B)\longmapsto \mathcal{D}(R,Y,\text{cost},\text{risk}).
\]

Harness engineering studies how \(C,P,G,X,V,U,D\) change that joint distribution, under what assumptions, and at what resource and safety cost. This definition makes positive results, negative results, and implementation evidence commensurable without pretending that they are the same kind of evidence.
