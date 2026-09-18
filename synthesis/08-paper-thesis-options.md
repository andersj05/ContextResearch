# Mathematics paper thesis options

## Recommendation in one sentence

Center the paper on a **self-improving context harness whose updates are constrained by
task-relevant rate--distortion and a statistically valid promotion gate**.

This keeps the conceptual ambition of Option C while adding the missing scientific
question: not only how an agent compresses task state, but when an adaptive outer loop
has enough evidence to believe that a new compiler is genuinely better. The focused
survey is in
[09-self-building-and-self-improving-harnesses.md](09-self-building-and-self-improving-harnesses.md),
the theorem map is in
[10-mathematics-of-harness-improvement.md](10-mathematics-of-harness-improvement.md),
and the experiment is specified in
[11-self-improving-experimental-blueprint.md](11-self-improving-experimental-blueprint.md).

## Option A — Correlated retries and imperfect verifiers

### Candidate thesis

> Standard agent-evaluation metrics systematically misstate deployment reliability because they treat repeated attempts as independent and verifier acceptance as correctness. A hierarchical latent-success model with audited verifier error yields identifiable bounds, calibrated uncertainty, and better cost-aware stopping policies.

### Possible contributions

1. A common probability model for pass@(k), pass(^{k}), task heterogeneity, within-task correlation, and adaptive retries.
2. Propositions showing when the independent approximation overstates opportunity and understates uncertainty.
3. Bounds or posterior estimates of latent correctness under imperfect tests or model judges.
4. A first-positive selection analysis showing how false positives accumulate with search.
5. A sequential retry/audit/escalation policy under cost and risk constraints.
6. A repeated-trial experiment with one or more open harnesses and a probability audit of outputs.

### Novelty and risk

- **Mathematical depth:** high.
- **Empirical feasibility:** high relative to the other options.
- **Dependence on proprietary access:** low.
- **Main risk:** a beta-binomial model alone is too familiar; novelty must come from identification, selection, adaptive dependence, useful bounds, or the empirical demonstration of rank reversal.

### Strong title candidates

- *Beyond Pass@k: Correlated Retries and Imperfect Verification in LLM Harness Evaluation*
- *What Does an Agent Pass Mean? Reliability, Selection, and Verifier Error in LLM Harnesses*
- *Estimating Reliable Success in Tool-Using Language Models*

## Option B — Causal model–harness–budget decomposition

### Candidate thesis

> “Agent performance” is a factorial interaction among model, harness, and resource budget; balanced paired designs and hierarchical estimators recover effects that one-factor leaderboards confound.

### Possible contributions

- formal estimands for model, harness, budget, environment, and interactions;
- optimal or near-optimal incomplete factorial designs under unequal run costs;
- hierarchical paired estimators and rank-reversal diagnostics;
- a cross-over study using minimal-loop and feature-rich open harnesses;
- a reproducibility schema for the full treatment tuple.

### Novelty and risk

- **Mathematical depth:** medium to high if experimental-design results are new.
- **Empirical feasibility:** medium; the cell count grows quickly.
- **Dependence on proprietary access:** optional.
- **Main risk:** without a novel allocation or identifiability result, this may read as excellent methodology rather than a mathematics paper.

### Best use

This is an excellent empirical backbone for Option A or a standalone paper if compute and task coverage are available.

## Option C — A self-improving context compiler with valid promotion

### Candidate thesis

> An agent context compiler is a lossy control channel from task state to
> model-visible state. A bounded outer loop may improve that compiler, but a change is
> deployable only when it clears an immutable promotion rule that controls adaptive
> selection error, cost, and regressions.

### Possible contributions

- define decision regret as a task-relevant distortion between full state and
  model-visible context;
- characterize sufficient summaries or belief states for a controlled task family;
- derive an operational rate--distortion frontier under a token constraint;
- formalize a typed, capacity-bounded family of self-editable context compilers;
- prove a finite-class or capacity-based promotion guarantee on an independent gate;
- quantify optimizer's-curse and adaptive-data-reuse effects as candidate budget grows;
- compare raw windows, retrieval, structured state, persistent memory, and learned
  compilers at matched model calls and tokens;
- test grounded feedback, intrinsic critique, random mutation, and careful manual
  context engineering as distinct proposal mechanisms.

### Novelty and risk

- **Mathematical depth:** very high: information theory, statistical learning,
  adaptive selection, and sequential testing meet in one explicit object.
- **Empirical feasibility:** medium to high if the primary theorem is tested in a
  generated finite environment and only one realistic task family is used for transfer.
- **Dependence on proprietary access:** low; frozen local/open models and a bounded DSL
  are sufficient.
- **Main risk:** a general LLM task has no observable optimal action or tractable state
  distribution. The theorem should therefore live in a deliberately controlled
  environment, while the realistic experiment is presented as an external-validity
  study rather than as proof of the theorem's assumptions.

### Strong title candidates

- *Context as a Control Channel: Rate-Distortion Models for Language-Agent Memory*
- *What Must an Agent Remember? Sufficient Context Under Token Constraints*
- *When Should an Agent Rewrite Its Harness? Rate-Distortion and Valid Promotion for
  Self-Improving Context Compilers*
- *Search Is Not Improvement: Statistical Gates for Self-Evolving Agent Harnesses*

## Option D — A verified event kernel for long-running harnesses

### Candidate thesis

> A small journaled control-plane kernel can guarantee replay, exactly-once logical commitment, budget monotonicity, and authority separation despite crashes and untrusted executors.

### Possible contributions

- define a labelled transition system for sessions, jobs, approvals, and tool effects;
- state safety and conditional liveness properties;
- prove them in TLA+/PlusCal, Alloy, Lean, or Coq;
- implement a reference kernel and test refinement with crash, duplicate, cancellation, and resize/race injection;
- delineate what cannot be guaranteed about nondeterministic models and external services.

### Novelty and risk

- **Mathematical depth:** high in formal methods.
- **Empirical feasibility:** medium.
- **Dependence on proprietary access:** none.
- **Main risk:** “exactly once” is impossible for arbitrary external side effects without idempotency or transactional assumptions. The theorem must concern logical commitment or explicitly state executor contracts.

### Best use

This is the best option if the paper venue values formal verification and systems semantics more than statistical evaluation.

## Option E — Cost/reliability Pareto frontiers and adaptive routing

### Candidate thesis

> No harness is uniformly best; optimal deployment is a policy over a Pareto frontier that routes tasks among retry, verification, delegation, model escalation, and human review.

### Possible contributions

- formalize multi-objective cost, latency, risk, and reliability;
- prove dominance and convexification results for randomized policies;
- learn calibrated task-conditional routing policies;
- derive regret or robustness bounds under nonstationary APIs;
- compare against fixed retry and strongest-model baselines.

### Novelty and risk

- **Mathematical depth:** medium to high.
- **Empirical feasibility:** medium to low because reliable cost and task-difficulty labels are needed.
- **Dependence on proprietary access:** moderate if frontier models are central.
- **Main risk:** routing improvements can collapse under distribution shift or be explained by a larger hidden compute budget.

## Option F — When multi-agent orchestration is more than sampling

### Candidate thesis

> Multi-agent orchestration has value beyond independent sampling only when task decomposition, branch information, and merger quality overcome correlated search and coordination loss.

### Possible contributions

- model parallel branch discoveries with dependence;
- characterize task-graph width and shared-state conditions for useful concurrency;
- bound information lost by compressed subagent reports;
- compare independent samples, tree search, identical agents, role agents, debate, and oracle merging at matched compute;
- identify regimes where communication is harmful.

### Novelty and risk

- **Mathematical depth:** high if the topology results are substantive.
- **Empirical feasibility:** low to medium because strict budget matching and merger evaluation are expensive.
- **Dependence on proprietary access:** optional.
- **Main risk:** the literature already contains many broad multi-agent claims; a small experiment will be absorbed into that noise unless the theory and controls are unusually sharp.

## Decision matrix

Scores are judgments based on this corpus, from 1 (weak) to 5 (strong).

| Option | Mathematical depth | Feasibility | Clear falsification | Durable beyond model releases | Overall |
|---|---:|---:|---:|---:|---:|
| A. correlated retries + verifier error | 5 | 5 | 5 | 5 | **20** |
| B. causal factorial decomposition | 4 | 3 | 5 | 5 | **17** |
| C. self-improving context compiler + valid promotion | 5 | 4 | 5 | 5 | **19** |
| D. verified event kernel | 5 | 3 | 5 | 5 | **18** |
| E. Pareto routing | 4 | 3 | 4 | 4 | **15** |
| F. multi-agent beyond sampling | 5 | 2 | 4 | 4 | **15** |

## Recommended paper structure for the chosen Option C

1. **Problem.** Current self-improving-harness work often confuses candidate search,
   validation selection, and transferable improvement.
2. **Context as a control channel.** Define state, compiled context, token rate,
   decision-regret distortion, and deployment risk.
3. **Controlled task model.** Specify a finite partially observable environment with a
   known belief state and optimal action values.
4. **Rate--distortion question.** Characterize sufficient context and the achievable
   distortion frontier for the controlled family.
5. **Editable compiler class.** Define a typed grammar for retrieval, ordering,
   compression, and persistent memory updates.
6. **Outer-loop selection.** Formalize the proposer, evaluator, candidate budget,
   adaptive transcript, and immutable acceptance gate.
7. **Guarantee and boundary.** Prove a finite-class or capacity-bounded promotion
   result; show why an expanding unrestricted class or repeatedly exposed test does not
   inherit it.
8. **Experiment.** Compare random and LLM-guided mutation, grounded and intrinsic
   feedback, manual context engineering, and unchanged baselines under matched budgets.
9. **Results.** Report rate--distortion curves, sealed-test change,
   development--test optimism, regressions, interaction effects, and total cost.
10. **Realistic transfer.** Repeat the bounded comparison on one pinned coding or tool
    environment without claiming that its unknown dynamics satisfy the theorem.
11. **Safety and artifacts.** Keep evaluator, permissions, hidden data, promotion keys,
    and rollback outside the editable region; release every candidate and trace.

## Claims to avoid in the paper

- “Harness X is best” without a task, model, budget, environment, and scorer.
- “Best-of-(k) proves self-correction” when candidates are merely resampled or selected by an external verifier.
- “Multi-agent collaboration caused the gain” without a matched-compute independent-sampling baseline.
- “Tests provide objective ground truth” without an audit of valid alternate solutions and incomplete patches.
- “The trials are independent” because temperature or seeds differ.
- “A significant aggregate difference generalizes” when repositories, days, or providers are the true independent clusters.
- “Production-scale” as a substitute for a sampling frame, control, or uncertainty interval.

## Immediate next decisions

Before beginning experiments, choose:

1. the controlled task family in which \(Q^*\), a belief state, and decision regret are
   exactly computable;
2. the typed operations the context compiler may edit;
3. a fixed candidate-capacity and gate-query budget;
4. one realistic transfer environment and the available number of independent
   outer-loop runs;
5. a private generator or sealed task cohort that the proposer never observes.

Option A remains the easiest independent paper. Option C is now the recommended thesis
because it is closer to actual harness design and supports a deeper question: how a
harness can improve its own information policy without turning its evaluator into a
training set.
