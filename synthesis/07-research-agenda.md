---
title: "Research Agenda for Self-Building and Self-Improving LLM Harnesses"
document_type: "prioritized mathematics research agenda"
last_evidence_check: "2026-09-04"
primary_program: "bounded self-improving context compiler with independent promotion"
---

# Research agenda for self-building and self-improving LLM harnesses

## Executive priority

The primary research program is to build and analyze a **bounded self-improving
context compiler**. The runtime model remains frozen. A separate proposal loop may
search over ways to select, order, compress, retrieve, and persist model-visible
information, but it may not rewrite the evaluator, promotion rule, hidden data,
resource meter, or authority boundary. A statistically independent promotion gate
decides whether a proposed compiler replaces the incumbent.

This separation is the central scientific design:

\[
\boxed{
\text{proposal and search}
\quad\longrightarrow\quad
\text{independent promotion gate}
\quad\longrightarrow\quad
\text{versioned deployment or rollback}
}
\]

It preserves the interesting part of self-improvement—an agent can propose changes
to a component used by its later runs—without making the improvement claim
circular. It also produces a tractable mathematics paper: the editable class,
information budget, evaluation distribution, acceptance margin, and trust boundary
can all be stated explicitly.

Three companion syntheses supply the detailed foundation:

- [Self-building and self-improving harnesses](09-self-building-and-self-improving-harnesses.md)
  reviews the empirical mechanisms and separates construction, optimization,
  persistence, and recursive editing.
- [Mathematics of harness improvement](10-mathematics-of-harness-improvement.md)
  develops rate-distortion, sufficiency, adaptive-selection, promotion, program
  synthesis, impossibility, and cost results.
- [Experimental blueprint](11-self-improving-experimental-blueprint.md) specifies
  the data split, bounded edit language, estimands, controls, and reproducibility
  protocol for a feasible paper.

The defensible target is **bounded improvement under declared assumptions**, not
open-ended recursive self-improvement. The study succeeds scientifically if it
identifies when search produces transferable improvement and when it produces only
an impressive development curve.

## 1. Scientific object and trust boundary

Let one complete evaluation unit be \(Z\sim P\). It contains the task, environment,
all rollout randomness needed by the estimand, and the grading realization. For a
frozen model \(L\), a context compiler \(c_\phi\), and fixed runtime components,

\[
R_\phi(Z)
=
\operatorname{Run}
\bigl(
L,c_\phi,\text{parser},\text{policy gate},\text{executor},\text{verifier};Z
\bigr).
\]

The editable compiler parameter is deliberately narrow:

\[
\phi=(q,r,z,m),
\]

where \(q\) selects evidence, \(r\) orders it, \(z\) compresses or structures it,
and \(m\) updates persistent memory. Every compiled context satisfies a declared
token bound

\[
|C_{\phi,t}|\leq B.
\]

The outer loop has two different actors and two different evidence channels:

\[
\begin{aligned}
\phi'_k
&\sim
Q_k\!\left(
  \cdot\mid
  \phi_{0:k},
  \mathcal T_{0:k},
  D_S
\right),\\
\widehat R_S(\phi'_k)
&=
\operatorname{Eval}(\phi'_k;D_S),\\
\phi_{k+1}
&=
\mathsf P(\phi_k,\phi'_k;D_G).
\end{aligned}
\]

Here \(Q_k\) is the proposal/search rule, \(D_S\) is reusable search data with rich
traces, and \(\mathsf P\) is an immutable promotion rule evaluated on a separately
controlled gate \(D_G\). After all search choices freeze, exactly one nominated
artifact is evaluated on a sealed test \(D_T\). A later shift set \(D_F\) measures
temporal or distributional transport.

The proposal system may be an LLM, evolutionary search, Bayesian optimization, or
random mutation. Calling the system self-improving does not require the same model
to propose, execute, and judge changes. It does require that accepted changes alter
the compiler used by later runs and that improvement be defined against the same
population objective.

Self-building is a distinct preceding operation:

\[
\phi_0
\sim
Q_{\mathrm{build}}
\!\left(
  \cdot\mid
  \text{task specification},
  \text{compiler grammar},
  \text{component library}
\right).
\]

Its outcomes are executable-build rate, invariant-check rate, construction cost,
and the untuned risk of \(\phi_0\). Those measurements must be reported before any
outer-loop optimization. Producing a runnable compiler is construction; only a
valid comparison against the pinned \(\phi_0\) can establish improvement. For the
theorem-backed study, \(Q_{\mathrm{build}}\) must emit only members of the fixed
family and receive no information from \(D_G\) or \(D_T\).

### Immutable trusted envelope

The following remain outside the editable region:

- task generator, data assignments, and split identities;
- gate and sealed-test evaluator code;
- promotion threshold and confidence policy;
- model snapshot and runtime parser;
- tool permissions, credentials, and network policy;
- container image, resource meter, and timeout policy;
- artifact signing, release, canary, and rollback mechanisms; and
- the grammar that defines the reachable compiler class during a theorem-backed run.

This is a bounded self-modification experiment, not an attempt to let generated code
rewrite its own judge.

## 2. Primary falsifiable research questions

The questions below are ordered so that a null result remains informative.

| ID | Falsifiable question | Primary comparison or estimand | Evidence that would weaken the claim |
|---|---|---|---|
| RQ0 | Can a model build an executable, invariant-preserving compiler from a specification and fixed component grammar before outcome-guided search? | Build success, hard-check pass rate, construction cost, and untuned risk relative to a fixed human seed | Low build validity or performance no better than a trivial template after matched repair opportunities |
| RQ1 | At a fixed context budget, can adaptive search find a compiler with lower sealed-test task regret than truncation, retrieval, and a careful hand-written state? | \(R_T(\phi_{\mathrm{final}})-R_T(\phi_{\mathrm{baseline}})\) at prespecified \(B\) | No interval-supported benefit on \(D_T\), despite a rising search curve |
| RQ2 | Does a capacity-aware independent gate reduce false promotions relative to naive best-development selection? | Test-regression probability among promoted updates | Equal or higher regression under the valid gate after matched proposal streams and power |
| RQ3 | Does adaptive evaluator exposure create a development–test optimism gap that increases with candidate budget or feedback precision? | Slope of \(O_{S\to T}\) against candidate evaluations and gate transcript bits | A stable near-zero slope across preregistered stress levels with adequate precision |
| RQ4 | Does grounded execution feedback improve the proposal distribution, rather than merely increasing selection opportunity? | Probability a prespecified proposed candidate clears the gate, plus mean unselected candidate quality | Grounded and random or intrinsic-critique proposers have indistinguishable candidate distributions under matched calls |
| RQ5 | Are compiler gains properties of a model–compiler pair rather than executor-invariant harness quality? | Model-by-compiler interaction and cross-model rank reversals | Stable effects and ranks across the prespecified executor models |
| RQ6 | Does the learned compiler improve the operational task-relevant rate–distortion frontier? | Regret or sufficient-fact loss versus tokens, calls, and estimated information | The learned frontier is dominated by a simple baseline over the target budget range |
| RQ7 | Does promotion remain beneficial after search, gate, deployment, latency, and audit costs are included? | Amortized outcome-cost frontier at declared deployment volumes | Gains disappear before the preregistered break-even horizon |
| RQ8 | Can a restricted edit language preserve hard security invariants throughout search and deployment? | Violations, rejected unsafe proposals, escape attempts, and rollback failures | Any promoted artifact violates a hard invariant or cannot be rolled back atomically |

For lower-is-better loss, define

\[
\Delta_S
=
R_S(\phi_{\mathrm{final}})-R_S(\phi_0),
\qquad
\Delta_T
=
R_T(\phi_{\mathrm{final}})-R_T(\phi_0)
\]

and

\[
G_{S\to T}
=
\Delta_S-\Delta_T,
\qquad
O_{S\to T}
=
-G_{S\to T}
=
\Delta_T-\Delta_S.
\]

A negative \(\Delta_T\) is sealed-test improvement. The companion blueprint uses
the signed quantity \(G_{S\to T}\); this agenda also reports
\(O_{S\to T}\), whose positive direction is evaluator optimism. Thus a large
negative development change paired with \(\Delta_T\approx0\) produces
\(O_{S\to T}>0\): evidence of adaptive selection, not evidence that the experiment
“failed.”

## 3. Mathematical program

### 3.1 Task-relevant compression

Context is a lossy representation of an observed history or latent task state
\(X\). Token count and Shannon information are not interchangeable. The study
should report the syntactic budget \(B\) directly and use information-theoretic
quantities only after declaring a source model and relevance variable.

For a controlled environment with action-value function \(Q^\star\), one possible
decision distortion is

\[
d(x,c)
=
\max_a Q^\star(x,a)
-
\mathbb E_{a\sim\pi_L(\cdot\mid c)}Q^\star(x,a).
\]

The corresponding idealized rate-distortion object is

\[
R_{\mathrm{task}}(D)
=
\inf_{P(C\mid X):\,\mathbb E d(X,C)\leq D}
I(X;C).
\]

This is a model for the controlled task, not a claim that natural-language contexts
achieve Shannon's asymptotic optimum. A second useful target is predictive
sufficiency:

\[
I(X;Y\mid C)=0,
\]

where \(Y\) is a future state, sufficient action, or other preregistered relevance
variable. In the controlled environment, this condition can support a decision-risk
statement. In an open coding environment, it can only be approximated empirically.

### 3.2 A promotion guarantee worth testing

Let \(\Phi_0\) be a finite compiler family of size \(M\), fixed before the gate data
are drawn. Let

\[
h_\phi(Z)
=
\frac{
  \ell_\phi(Z)+\lambda\kappa_\phi(Z)
}{
  1+\lambda
}
\in[0,1],
\]

where \(\ell\) is task loss, \(\kappa\) is normalized resource cost, and
\(\lambda\geq0\) is fixed in advance. For
\(D_G=(Z_1,\ldots,Z_n)\overset{\mathrm{iid}}\sim P^n\), define

\[
\widehat J_G(\phi)
=
\frac1n\sum_{i=1}^{n}h_\phi(Z_i),
\qquad
J(\phi)=\mathbb E_P h_\phi(Z).
\]

Hoeffding's inequality and a union bound give, with probability at least
\(1-\delta\),

\[
\sup_{\phi\in\Phi_0}
\left|
\widehat J_G(\phi)-J(\phi)
\right|
\leq
\varepsilon,
\qquad
\varepsilon
=
\sqrt{
  \frac{\log(2M/\delta)}{2n}
}.
\]

Therefore the immutable rule

\[
\widehat J_G(\phi')
\leq
\widehat J_G(\phi)
-
(2\varepsilon+\tau)
\]

implies

\[
J(\phi')\leq J(\phi)-\tau
\]

simultaneously for every accepted proposal in the fixed family. This is the
candidate theorem proved in
[the mathematical synthesis](10-mathematics-of-harness-improvement.md), not an
unconditional theorem about arbitrary generated programs.

### 3.3 Assumptions that must appear beside the result

The guarantee requires:

1. **Fixed population:** gate units are i.i.d. from one declared \(P\), or a
   different valid concentration theorem is supplied.
2. **Complete unit:** all task, model, environment, and grading randomness is part
   of \(Z\), making \(h_\phi\) a fixed measurable function.
3. **Bounded, fixed objective:** loss, cost normalization, and \(\lambda\) are set
   before gate outcomes are inspected.
4. **Fixed reachable family:** every possible submitted compiler is in
   \(\Phi_0\), fixed independently of \(D_G\).
5. **Independent gate sample:** \(D_G\) is not used to construct the family,
   evaluator, threshold, or objective.
6. **Immutable gate:** score code, feedback policy, stopping policy, and protected
   slices do not change in response to gate results.
7. **Atomic rollback:** a rejection cannot partially modify later runtime state.

The theorem proves a population-risk statement only under these assumptions. It
does not prove:

- that the search procedure will find a promotable compiler;
- that the reachable class contains a useful compiler;
- global or open-ended convergence;
- transfer to a different model, task mixture, or future environment;
- semantic correctness of unrestricted generated code;
- protection against a misspecified objective or evaluator;
- task sufficiency of a context representation; or
- Pareto improvement when one scalar objective is used.

Because \(J\in[0,1]\) and every accepted update improves by at least
\(\tau>0\), the same theorem permits at most
\(\lfloor J(\phi_0)/\tau\rfloor\) accepted updates. Fixed-margin monotonicity is
therefore explicitly **not** a model of endless improvement.

### 3.4 Useful extensions

Mathematically substantive extensions include:

- replace \(\log M\) with a nonvacuous capacity measure for a typed compiler class;
- derive paired or variance-adaptive bounds using common tasks and seeds;
- use confidence sequences for a prespecified candidate under optional stopping;
- impose simultaneous upper bounds on cost and protected-slice regressions;
- characterize approximate sufficiency under decision regret;
- bound performance loss from repeated summary composition;
- quantify the price of coarse gate feedback; and
- formalize safe improvement under distribution drift or a finite-state MDP.

Each extension must state whether it changes the candidate family, stopping rule, or
data reuse assumptions. Optional stopping validity does not repair adaptive
candidate invention or distribution shift.

## 4. Controls for adaptive overfitting

### 4.1 Four-way data policy

| Split | Allowed use | Returned information |
|---|---|---|
| \(D_S\): search | Candidate creation, debugging, trace analysis, and search-model fitting | Full scores, traces, errors, and counterexamples |
| \(D_G\): promotion gate | A metered sequence of accept/reject decisions | One bit or a preregistered coarse band; never raw hidden cases |
| \(D_T\): sealed test | One final nominated compiler after all analysis choices freeze | Opened once for the primary result |
| \(D_F\): future or shift | Prespecified later generator, model, repository cohort, or environment version | Opened only after the main analysis |

Splits occur at the claimed unit of generalization. Tasks sharing a repository,
template, generator seed family, proof skeleton, or environment must remain in the
same cluster. A set consulted at every round is a gate, not a sealed test, even if
the tasks themselves remain invisible.

### 4.2 Gate-design controls

The primary study should combine several defenses rather than treating “hidden
tests” as sufficient:

- freeze the reachable class or preregister a capacity bound;
- limit both the number and precision of gate responses;
- retain the complete gate transcript, including rejected candidates;
- charge all candidates evaluated, not only accepted updates;
- use a fixed promotion margin and confidence allocation;
- nominate one final artifact before opening \(D_T\);
- repeat complete outer-loop searches with independent seeds;
- audit a probability sample of accepted and rejected outputs;
- report the search–gate–test gap as a primary outcome; and
- use fresh or rolling gates if the editable grammar must expand.

The study should experimentally vary candidate count and feedback precision. If
development improvement rises while sealed-test improvement saturates or reverses,
that curve is direct evidence about optimizer overfitting.

### 4.3 Evaluator validity

A promotion theorem about \(\widehat J_G\) does not establish that \(J\) measures
the intended construct. The protocol therefore needs:

- a written outcome rubric fixed before search;
- evaluator sensitivity and false-positive audits;
- independent human or formal review on sampled passes and failures;
- explicit scoring of timeouts, infrastructure faults, refusals, and policy
  violations;
- separate reporting for task success, verifier acceptance, and useful partial
  progress; and
- sensitivity analyses under plausible label-error rates.

This connects the lead program to the earlier work on imperfect verification rather
than treating verifier noise as a separate afterthought.

## 5. Feasible staged experiment

The implementation should proceed from a theorem-compatible controlled environment
to one realistic transfer test. The detailed reproducibility specification is in
the [experimental blueprint](11-self-improving-experimental-blueprint.md).

### Stage 0 — preregistration and executable specification

Before any outcome comparison:

1. define the target task distribution, clustering unit, loss, cost measures,
   protected slices, and smallest meaningful effect;
2. freeze the context-compiler grammar and enumerate no more than a tractable
   \(M\) configurations for the theorem-backed experiment;
3. fix model snapshots, prompts, containers, seeds, budgets, gate feedback, and
   rollback behavior;
4. generate and hash \(D_S,D_G,D_T,D_F\) by cluster; and
5. compute the gate sample size from \(M,\delta,\tau\), then separately power the
   sealed-test comparison.

### Stage 1 — controlled task family and oracle map

Build one finite partially observable task generator with delayed dependencies,
distractors, stale facts, and recoverable failures. Suitable examples are
key–door navigation, dependency repair on generated graphs, or bounded scheduling.
The transition law and optimal policy should be known so that the study can compute:

- an oracle belief state;
- exact or high-precision decision regret;
- facts sufficient for the next decision;
- counterfactual context ablations; and
- a meaningful task-relevant distortion curve.

This stage separates an information-loss mechanism from the uncontrolled semantics
of a public coding benchmark.

### Stage 2 — baseline frontier

At three or four prespecified token budgets, estimate outcome and cost for:

1. raw recent-history truncation;
2. retrieval with fixed keys and top-\(k\);
3. a careful hand-written structured state;
4. recursive summary without retrieval;
5. oracle sufficient state; and
6. the unchanged human seed compiler; and
7. a self-built initial compiler evaluated before outcome-guided improvement.

Use common tasks and seeds where valid. This establishes whether there is room for
learning and prevents a complex search system from claiming credit for an obvious
interface repair.

### Stage 3 — bounded outer-loop search

Run at least two proposal policies:

- **random mutation**, which measures gains from selection opportunity alone; and
- **LLM-guided grounded mutation**, which receives reusable search traces and must
  state a falsifiable reason for each proposed edit.

An optional third arm removes grounded traces and permits only intrinsic critique.
Match candidate-evaluation opportunities, executor calls, and maximum wall-clock
budget. Run multiple complete outer-loop seeds; repetitions of one candidate are
not substitutes for independent searches.

Every candidate remains in a lineage ledger containing its parent, exact diff,
proposal evidence, search score, gate decision, cost, error class, security checks,
and rollback result.

### Stage 4 — promotion and adaptive-stress experiment

Cross the proposal policies with:

1. naive best-on-search selection;
2. naive repeated use of exact gate scores;
3. the fixed-capacity margin gate; and
4. a sequential gate only if its assumptions and confidence allocation are
   specified in advance.

Vary the candidate budget and gate feedback precision across preregistered levels.
The principal adaptive-overfitting outcome is the difference between the apparent
gain on reused evidence and the gain on \(D_T\). Gate policies should be compared
using complete independent outer-loop runs, because acceptances change later
proposal histories.

### Stage 5 — sealed test

For each complete run, nominate exactly one final compiler before opening \(D_T\).
Estimate:

- sealed-test loss change relative to the seed and simple baselines;
- false-promotion or test-regression probability;
- the development–test gap;
- task-cluster heterogeneity;
- decision distortion at each token budget;
- cost and latency changes; and
- security, forgetting, and rollback outcomes.

Use paired task effects and cluster-respecting bootstrap or hierarchical intervals.
Report all preregistered arms, not only the strongest seed.

### Stage 6 — transfer without inherited theorem claims

Freeze the selected compiler and test one of:

- a second executor model;
- a shifted controlled-task generator; or
- one version-pinned coding or tool-use family with hidden generated tests.

This stage estimates transport. It does not inherit the controlled environment's
known-\(Q^\star\), sufficiency, or finite-class conclusions unless their assumptions
are re-established.

### Minimal viable paper

A feasible first paper needs only:

- one controlled task generator;
- one finite typed compiler family;
- one self-built initial compiler and one fixed human seed;
- three context budgets;
- random and grounded-LLM proposal arms;
- naive and capacity-aware gates;
- multiple independent outer-loop seeds;
- one sealed test; and
- the finite-class promotion proof plus an empirical adaptive-selection curve.

A realistic coding extension, continual drift, or unrestricted source editing
belongs after this result, not before it.

## 6. Required ablations

The following ablations distinguish proposal quality, context quality, and selection
effects:

| Component | Main condition | Ablation | What it identifies |
|---|---|---|---|
| Construction | Model-built initial compiler | Fixed human seed with the same grammar | Build validity and construction value before selection |
| Proposal | LLM with grounded traces | Random mutation at matched candidate count | Benefit beyond search opportunity |
| Feedback | Execution-grounded critique | Intrinsic/self-generated critique only | Value of external evidence |
| Selection | Capacity-aware gate | Naive best score | Protection from adaptive optimism |
| Gate transcript | Coarse accept/reject | Exact scores | Effect of feedback information |
| Context policy | Learned select/order/compress/memory | Freeze one operation at a time | Which compiler mechanism matters |
| Persistence | Versioned memory updates | Stateless compiler | Benefit and forgetting cost of memory |
| Retrieval | Learned retrieval policy | No retrieval or fixed top-\(k\) | Retrieval contribution |
| Compression | Typed summaries | Raw truncation at matched tokens | Compression benefit rather than extra context |
| Baseline design | Searched compiler | Careful hand-written compiler | Search value beyond interface engineering |
| Executor | Primary frozen model | Second frozen model | Model–harness interaction |
| Budget | Full search | Independent retries or best-of-\(k\) at matched calls | Value beyond inference scaling |
| Safety gate | Static and runtime invariants | Retrospective shadow evaluation only | Rejection rate and failure modes; unsafe deployment is not permitted |

The security “ablation” is observational: unsafe candidates may be evaluated in an
isolated shadow sandbox, but a hard protection is never disabled in deployment.

## 7. Outcomes, statistical analysis, and stopping

### Primary outcomes

Report an outcome vector rather than one opaque utility:

\[
Y
=
(
\text{task loss},
\text{decision regret},
\text{tokens},
\text{model calls},
\text{latency},
\text{dollars},
\text{violations},
\text{forgetting},
\text{human audit time}
).
\]

The primary confirmatory endpoint is sealed-test loss of the nominated compiler
relative to the seed at a prespecified context and search budget. Cost-adjusted
utility and protected-slice outcomes are key secondary endpoints.

### Unit of inference

The independent unit is a task cluster or a complete outer-loop run, depending on
the estimand. Tokens, candidate evaluations, and retries are not independent
replicates. Randomize treatment order within infrastructure blocks and model task,
repository or generator family, day, and search seed explicitly.

### Analysis

The analysis should include:

- paired task-level effects and cluster bootstrap intervals;
- a mixed-effects model for model, compiler, gate, budget, and their interactions;
- simultaneous intervals for preregistered protected slices;
- promotion precision and test-regression probability;
- a curve of adaptive gap against candidate count and feedback bits;
- the operational regret–token frontier;
- proposal-distribution quality before best-candidate selection;
- sensitivity to evaluator false positives and false negatives; and
- outcome-cost Pareto frontiers with amortization assumptions shown.

### Stopping

Search stops at the preregistered candidate budget, resource ceiling, or hard safety
event. It does not stop merely when the best-so-far curve looks impressive. Gate
testing stops only under a valid fixed-sample rule or a prespecified confidence
sequence. The sealed test is not reopened for model selection.

## 8. Cost and resource constraints

For each candidate, preserve:

\[
C
=
C_{\mathrm{proposal}}
+C_{\mathrm{search}}
+C_{\mathrm{gate}}
+C_{\mathrm{audit}}
+C_{\mathrm{deployment}}.
\]

Report tokens, model calls, tool calls, accelerator time, wall-clock latency, dollar
cost, and human review separately. Do not hide outer-loop search behind the cost of
the final harness.

For deployment volume \(N\), report total amortized cost

\[
C_{\mathrm{total}}(N)
=
C_{\mathrm{build}}
+C_{\mathrm{search}}
+C_{\mathrm{gate}}
+C_{\mathrm{audit}}
+N\,C_{\mathrm{run}}.
\]

The cost question is not “did the final compiler use fewer tokens?” but “at what
deployment volume, if any, does the full improved system dominate the seed?” Show
the Pareto frontier when conclusions depend on the scalarization parameter
\(\lambda\).

Candidate schedulers may use successive halving or another cost-aware rule only
after specifying why low-fidelity rankings are predictive. Shared ancestry and
correlated evaluations make classical independent-search guarantees inapplicable
unless separately proved.

## 9. Security and release constraints

Generated compilers execute in clean, capability-limited containers with no access
to hidden data, credentials, signing keys, or the host repository. The typed edit
language may modify context behavior but may not create arbitrary processes,
network endpoints, or filesystem authority.

Every proposed artifact passes:

1. grammar and type validation;
2. static policy and secret-access checks;
3. deterministic unit and metamorphic tests;
4. sandboxed adversarial execution;
5. the statistical promotion gate;
6. signed, versioned release;
7. canary deployment; and
8. automatic rollback on a hard invariant or monitored regression.

Required invariants include monotone resource counters, no access outside declared
storage, no gate-data exfiltration, no mutation of the evaluator or release policy,
complete action logging, idempotent rejection, and restoration of the prior
compiler after rollback.

Formal checks prove only the encoded properties in the modeled semantics. Tests
provide sampled evidence. Neither establishes that an unrestricted LLM-written
program is universally safe. This is why the primary experiment uses a typed
compiler grammar.

## 10. Secondary research directions

The earlier agenda remains useful, but these directions now support or extend the
lead self-improvement program.

### 10.1 Correlated retries and imperfect verification

Model repeated attempts with task-level dependence rather than
\(1-(1-p)^k\) alone, and estimate verifier sensitivity, specificity, and selected
answer precision. This is essential when proposal candidates share ancestry or the
gate accepts the first apparent success. It can become a dedicated paper if retry
dependence or label noise dominates the compiler effect.

### 10.2 Causal decomposition of model, harness, and budget

Cross model, compiler, gate, and resource budget in a factorial or deliberately
incomplete design. The key target is the model–compiler interaction: a selected
harness should not be described as generally better when its advantage belongs to
one executor and budget.

### 10.3 Harnesses as transition systems

Specify the trusted runtime kernel as a labeled transition system and prove
authorization, budget, replay, isolation, cancellation, and rollback properties.
Control-plane determinism must remain separate from stochastic model output and
external side effects.

### 10.4 Sequential stopping and cost-aware allocation

Study when to retry, verify more deeply, promote, escalate to a stronger model, ask
a human, or stop. Confidence sequences, bandit allocation, and value-of-information
rules are promising, but each needs explicit dependence, optional-stopping, and
distribution assumptions.

### 10.5 Multi-agent topology under matched compute

Compare a single proposer, independent proposer samples, adaptive search, specialist
agents, and debate or merger topologies while matching candidate count, tokens,
calls, and wall-clock opportunity. The estimands are proposal diversity, correlated
failure, merge loss, critical-path latency, and gate-clearing probability—not the
number of agents.

### 10.6 Benchmark lifecycle and temporal validity

Use rolling private task windows, canaries, probability audits, and explicit
repository and evaluator versioning. A repeatedly queried benchmark becomes part of
the optimizer state. Temporal decline in discrimination or rising grader disputes
should trigger revision or retirement.

### 10.7 Mathematics-research harnesses

For mathematical research, separate theorem-statement validity, proof validity,
novelty, citation accuracy, symbolic reproducibility, counterexample discovery,
assumption tracking, useful partial progress, and human verification time. Proof
assistants can give high-specificity checks for formalized statements, but
formalization itself is a selection process; novelty and informal insight cannot be
collapsed into one pass bit.

## 11. Decision rule for the broader agenda

The lead program should advance only if the bounded experiment survives the
following decision points:

1. **Mechanism:** the learned compiler beats simple context baselines on the sealed
   controlled-task test.
2. **Validity:** the independent gate has lower false-promotion risk than naive
   selection, or the study precisely shows why it does not.
3. **Attribution:** grounded proposal quality improves beyond matched random search
   and best-of-\(k\).
4. **Economics:** the improvement remains on the Pareto frontier after full search
   and audit costs.
5. **Safety:** no promoted artifact violates a hard invariant, and rollback works
   under injected faults.
6. **Transport:** at least one effect persists under a prespecified model or task
   shift, with interaction and failure cases reported.

Failure at a decision point narrows the claim; it does not justify relaxing the
gate after observing results. Only after these stages should the project expand the
editable language toward tools, routing, workflow graphs, or source code.

## 12. Evidence-update rule

This agenda deliberately avoids embedding a fixed corpus-size count because the PDF
inventory and source catalog are live research artifacts. Counts should be reported
from the current machine-readable catalogs at release time, not copied into this
document.

Future evidence should change the agenda only when it contributes at least one of:

- a controlled mechanism ablation;
- an independent replication or contradiction;
- public task-level traces and full cost data;
- a new theorem with assumptions that map to the harness;
- a probability-sampled verifier audit;
- an explicit adaptive-overfitting control;
- a materially new trust-boundary or formal-safety result; or
- evidence of transfer across executor models, task families, or time.

Product announcements, unversioned leaderboards, self-selected best runs, and
architecture diagrams without methods should not enlarge the evidentiary core merely
by repeating an existing claim.
