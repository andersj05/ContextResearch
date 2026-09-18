---
title: "Experimental Blueprint for a Self-Improving Context Harness"
document_type: "mathematics-paper design and reproducibility protocol"
last_evidence_check: "2026-09-04"
scope: "bounded context compilation, adaptive harness search, and statistically valid promotion"
---

# Experimental blueprint for a self-improving context harness

## Proposed paper in one sentence

Build a bounded agent harness that improves its own context compiler, then determine
when a measured improvement survives an untouched test set and when it is merely the
optimizer's curse caused by adaptive evaluator reuse.

This design preserves what is interesting about self-improving harnesses while keeping
the mathematical object identifiable. The model weights, task generator, evaluator,
promotion rule, and authority boundary remain fixed. The harness may change how it
selects, compresses, structures, retrieves, and persists model-visible information.

## 1. Research questions

The primary question is:

> Under a fixed context budget, what assumptions let an adaptive outer loop promote a
> context-harness update with a valid guarantee of lower task regret?

Four secondary questions make that claim falsifiable:

1. Does learned context compilation trace a better task-relevant rate--distortion
   frontier than raw truncation, retrieval, or a hand-written structured state?
2. How quickly does the development-to-test gap grow with the number and adaptivity of
   candidate evaluations?
3. Does grounded execution feedback improve the proposal distribution, or does a
   best-so-far curve rise even under random or self-generated mutations?
4. Are learned harness changes properties of the harness, or interactions with the
   executor model and task family?

## 2. Formal object

Let \(X\sim P\) be a task, \(S_t\) its latent environment state, and \(O_{0:t}\) the
observable history. A context compiler with parameters \(\phi\) emits

\[
C_{\phi,t}=c_\phi(O_{0:t},M_{\phi,t}),
\qquad |C_{\phi,t}|\le B,
\]

where \(M_{\phi,t}\) is persistent harness memory and \(B\) is a fixed token budget. A
frozen model \(L\) maps context to an action distribution, while a fixed parser, policy
gate, executor, and environment generate the next observation. The complete runtime is

\[
R_\phi(X,\xi)=
\operatorname{Run}(L,c_\phi,P,G,E,V,D;X,\xi),
\]

with random seed or API realization \(\xi\). The editable region is deliberately narrower
than the complete runtime:

\[
\phi=(q,r,z,m),
\]

where \(q\) selects evidence, \(r\) orders it, \(z\) compresses or structures it, and
\(m\) updates persistent memory. Tool permissions, evaluator code, hidden data, resource
ceilings, signing, and rollback are immutable.

For bounded task loss \(\ell\in[0,1]\), define deployment risk

\[
R_P(\phi)=\mathbb E_{X\sim P,\xi}\left[\ell(R_\phi(X,\xi))\right].
\]

Cost, latency, policy violations, and forgetting are separate outcomes, not terms hidden
inside an undocumented scalar score.

## 3. Task-relevant distortion

Ordinary text similarity is not the distortion relevant to an agent. A useful decision
distortion compares the value available from full state with the value induced by a
compiled context:

\[
d(s,c)=
\max_{a\in\mathcal A}Q^*(s,a)
-\mathbb E_{a\sim\pi_L(\cdot\mid c)}Q^*(s,a).
\]

For a controlled environment in which \(Q^*\) is known, the task rate--distortion
function is

\[
R_{\mathrm{task}}(D)=
\inf_{P(C\mid S):\,\mathbb E d(S,C)\le D} I(S;C).
\]

The experiment need not claim that tokens equal Shannon bits. It should instead report
both the operational token rate \(B\) and, where estimable, a mutual-information proxy.
Shannon's theorem supplies the lower-bound template only after the source, channel, and
distortion have been specified
([shannon-1959-rate-distortion](../paper-notes/shannon-1959-rate-distortion.md)).
The information-bottleneck relaxation supplies a relevance objective,

\[
\min I(S;C)-\beta I(C;Y),
\]

where \(Y\) may encode a sufficient action, verifier outcome, or future state
([tishby-2000-information-bottleneck](../paper-notes/tishby-2000-information-bottleneck.md)).

### Controlled theorem environment

Use a finite partially observable task family with known transition law and optimal
policy. Examples include key--door navigation, dependency repair on generated graphs, or
resource-constrained scheduling with hidden state. Construct distractors, stale facts,
and delayed dependencies so the compiler must decide what to retain. This environment
supports exact \(Q^*\), a known belief state, counterfactual context ablations, and a
well-defined regret distortion.

### Realistic transfer environment

Add one version-pinned tool or coding task family in which semantic correctness is
determined by a hidden task generator or tests. This validates engineering relevance but
does not inherit the controlled environment's optimal-policy theorem. Claims from the two
environments must remain separate.

## 4. Bounded self-improvement loop

Represent candidate compilers in a typed grammar rather than unrestricted Python. A
candidate may:

- change retrieval keys, top-\(k\), decay, or diversity penalties;
- choose among lossless state fields and bounded summary schemas;
- add, revise, merge, supersede, or delete memory records;
- change evidence order and reserved token allocations;
- add a bounded verifier-triggered retrieval or repair branch.

It may not change the evaluator, data split, promotion threshold, grammar, tool authority,
or resource meter. Candidate generation can use an LLM, evolutionary mutation, Bayesian
optimization, or random mutation, but each optimizer receives the same target-evaluation
budget.

At outer round \(k\),

\[
\begin{aligned}
\phi'_k &\sim Q_k(\cdot\mid\phi_{0:k},\mathcal T_{0:k}),\\
\widehat R_S(\phi'_k)&=\operatorname{Eval}(\phi'_k;D_S),\\
\phi_{k+1}&=A(\phi_k,\phi'_k,D_G),
\end{aligned}
\]

where \(D_S\) is freely reusable search data, \(\mathcal T\) contains traces and grounded
feedback, and \(D_G\) is a metered promotion set. Every candidate, including failures and
rejections, is retained with its lineage and cost.

## 5. Data split and information policy

Use four non-overlapping samples at the level of the claimed generalization unit:

| Split | Permitted use | Information returned |
|---|---|---|
| \(D_S\): search | Candidate creation, debugging, and unrestricted analysis | Full traces and scores |
| \(D_G\): gate | A bounded number of promotion decisions | Pass/fail or a deliberately coarse improvement band |
| \(D_T\): sealed test | One nominated final candidate after all search choices freeze | Released once |
| \(D_F\): future/shift | Later task generator, repository cohort, or environment version | Released after the main analysis |

If tasks share templates, repositories, generators, or environments, split by that
cluster rather than by nominal instance. A “held-out” set consulted at every promotion
round is \(D_G\), not \(D_T\). This distinction is directly motivated by reusable-holdout
theory and the repeated promotion protocol in recent self-harness work
([dwork-2015-adaptive-holdout](../paper-notes/dwork-2015-adaptive-holdout.md);
[zhang-2026-self-harness](../paper-notes/zhang-2026-self-harness.md)).

## 6. A theorem target for promotion

Let \(\mathcal H_K\) be a fixed, ex-ante class of reachable compilers, with finite cardinality
\(N_K\). Let \(D_G=(X_i)_{i=1}^n\overset{\mathrm{iid}}\sim P^n\), independent of the
search process, and let losses lie in \([0,1]\). Hoeffding's inequality plus a union bound
gives, with probability at least \(1-\delta\),

\[
\sup_{\phi\in\mathcal H_K}
|\widehat R_G(\phi)-R_P(\phi)|
\le
\epsilon(n,N_K,\delta)
=
\sqrt{\frac{\log(2N_K/\delta)}{2n}}.
\]

Therefore, on that event, the immutable rule

\[
\widehat R_G(\phi')
\le
\widehat R_G(\phi)-(2\epsilon+\tau)
\]

implies

\[
R_P(\phi')\le R_P(\phi)-\tau.
\]

This is a proposed finite-class specialization of standard uniform convergence, not a
new unconditional self-improvement theorem. A paper can extend it in one of four useful
directions:

1. replace \(\log N_K\) with a capacity measure for a typed compiler class;
2. derive a paired bound that exploits common tasks and seeds;
3. add simultaneous cost and safety constraints;
4. quantify how expanding the editable grammar invalidates the original guarantee.

The related reachable-class result should be presented skeptically: finite capacity can
preserve PAC learnability under fixed i.i.d. assumptions, but estimating the capacity of
real executable harnesses remains open
([wang-2025-statistical-limits](../paper-notes/wang-2025-statistical-limits.md)).

### Sequential alternative

For paired losses \(Z_i=\ell(R_{\phi}(X_i))-\ell(R_{\phi'}(X_i))\), construct a
time-uniform lower confidence sequence \(L_t\) for \(\mathbb E Z_i\). Promote only when

\[
L_t\ge\tau,
\]

all hard invariants pass, and simultaneous upper bounds for cost and protected-slice
regressions remain below their limits. Confidence sequences allow optional stopping under
their stated stochastic assumptions; they do not make adaptive changes to the candidate
family or data distribution harmless
([howard-2021-confidence-sequences](../paper-notes/howard-2021-confidence-sequences.md)).

## 7. Optimizer's-curse prediction

If \(\widehat U_j=U_j+\varepsilon_j\) and the outer loop selects
\(j^*=\arg\max_{j\le m}\widehat U_j\), then even conditionally unbiased scores become
optimistic after selection
([smith-2006-optimizers-curse](../paper-notes/smith-2006-optimizers-curse.md)). For
sub-Gaussian empirical means, the information-theoretic adaptive-bias result suggests

\[
|\mathbb E(\widehat U_{j^*}-U_{j^*})|
\le
\sigma\sqrt{\frac{2I(j^*;\widehat{\mathbf U})}{n}}
\le
\sigma\sqrt{\frac{2\log m}{n}}.
\]

The experiment should test the scaling shape rather than claiming equality. Vary \(m\),
gate feedback precision, evaluator noise, and candidate dependence. Estimate the
development--test gap over complete independent outer-loop runs.

## 8. Experimental factors and controls

Use a balanced or deliberately optimized incomplete factorial design over:

- context budget \(B\);
- compiler family: truncation, retrieval, structured belief/state, learned compiler;
- proposal rule: random, LLM mutation, evolutionary archive, ablated grounded feedback;
- executor model: at least two frozen models of different capability;
- evaluator feedback: scalar only, grounded traces, self-generated critique;
- candidate budget \(m\);
- promotion policy: naive best validation, fixed-capacity margin, sequential gate;
- task family and distribution shift;
- independent outer-loop seed.

Mandatory controls are:

1. the unchanged seed harness;
2. careful hand-written context engineering;
3. independent retries or best-of-\(k\) at matched total model calls;
4. random edits with the same selection budget;
5. oracle context in the controlled environment;
6. a proposal-quality oracle that uses sealed outcomes only for retrospective analysis.

AgentOccam is the warning embodied by control 2: a simple observation/action redesign can
outperform much more elaborate agent systems
([yang-2024-agentoccam](../paper-notes/yang-2024-agentoccam.md)). AFlow's controlled ADAS
rerun and GPTSwarm's non-optimized GAIA setup similarly make matched implementation and
compute essential
([zhang-2024-aflow](../paper-notes/zhang-2024-aflow.md);
[zhuge-2024-gptswarm](../paper-notes/zhuge-2024-gptswarm.md)).

## 9. Outcomes and estimands

Report the complete outcome vector

\[
Y=(\text{task loss},\text{decision regret},\text{tokens},\text{calls},
\text{latency},\text{violations},\text{forgetting}).
\]

Primary estimands are:

\[
\Delta_T=R_T(\phi_{\mathrm{final}})-R_T(\phi_0),
\qquad
G_{S\to T}=
[R_S(\phi_{\mathrm{final}})-R_S(\phi_0)]-\Delta_T,
\]

the sealed-test improvement and adaptive generalization gap. Also estimate:

- distortion at each token budget and area under the rate--distortion frontier;
- probability that a promoted update regresses on \(D_T\);
- protected-slice worst-case or lower-quantile change;
- search efficiency per candidate evaluation and per unit cost;
- proposal improvement independent of best-so-far selection;
- model--harness interaction variance;
- forgetting on earlier task cohorts;
- total amortized cost
  \(C_{\mathrm{search}}+C_{\mathrm{gate}}+N_{\mathrm{deploy}}C_{\mathrm{run}}\).

The independent unit is an outer-loop run or task cluster, not an individual token,
candidate, or retry. Use paired task effects, hierarchical bootstrap intervals at the
cluster level, and simultaneous intervals for preregistered protected slices.

## 10. Preregistered hypotheses

The design is useful even if every hypothesis fails.

\[
\begin{aligned}
H_1:&\quad D_{\mathrm{learned}}(B)<D_{\mathrm{retrieval}}(B)
\text{ for some prespecified budget range};\\
H_2:&\quad G_{S\to T}\text{ increases with adaptive candidate budget and feedback bits};\\
H_3:&\quad \Delta_T^{\mathrm{grounded}}
<\Delta_T^{\mathrm{intrinsic}}
\text{ in loss units under matched cost};\\
H_4:&\quad \operatorname{Var}((\alpha\beta)_{\mathrm{model,harness}})>0;\\
H_5:&\quad \Pr(\text{test regression}\mid\text{promoted})
\text{ is lower under the valid gate than under naive selection}.
\end{aligned}
\]

Here lower loss is better. Report effect sizes and uncertainty, not only rejection
decisions. Treat an impressive development curve with no sealed-test gain as evidence
about selection dynamics, not a failed study.

## 11. Artifact and safety protocol

Each release must record

\[
\mathcal R_k=(\phi_k,L,\text{container},\text{tools},\text{data IDs},
\text{evaluator},\text{budget},\text{lineage},\text{hash},\text{signature}).
\]

The repository should preserve candidate source, diff, parent, proposer prompt, trace,
score, cost, failure class, gate decision, and rollback result. Generated candidates run
in clean capability-limited containers with no access to hidden tests, credentials,
promotion keys, or the host repository. Promotion is transactional: static check, unit
tests, sandbox run, statistical gate, signed release, canary, and automatic rollback.

Program-synthesis results explain why the restriction is scientifically useful. A typed
grammar plus a separate verifier can make correctness auditable relative to a formal
specification
([solar-lezama-2006-sketch](../paper-notes/solar-lezama-2006-sketch.md);
[alur-2013-sygus](../paper-notes/alur-2013-sygus.md)). It cannot decide arbitrary semantic
properties of unrestricted programs. Gödel-machine and fastest-provable-program results
are likewise conditional on encoded axioms and discoverable proofs, not guarantees for
unrestricted LLM-written code
([schmidhuber-2003-godel-machines](../paper-notes/schmidhuber-2003-godel-machines.md);
[hutter-2002-fastest-provable-program](../paper-notes/hutter-2002-fastest-provable-program.md)).

## 12. Claims this study could support

With successful experiments and the stated assumptions, the paper could support:

- an operational rate--distortion frontier for a specified agent task distribution;
- a sufficient or approximately sufficient context representation in a controlled model;
- a finite-class or capacity-bounded promotion guarantee;
- an empirical law relating adaptive search budget to validation optimism;
- a measured benefit of grounded feedback over intrinsic critique;
- a quantified model--harness interaction and transfer boundary;
- a safer, auditable engineering pattern for bounded self-improvement.

It could not support unconditional monotone recursive self-improvement, globally optimal
harness discovery, arbitrary semantic safety verification, transfer to every model or
task, or indefinite validity from a repeatedly exposed benchmark. Those exclusions are
not weaknesses of the paper. They are what make the theorem and experiment honest.

## 13. Minimal viable paper and extensions

The minimal publishable study combines:

1. one finite controlled task generator with exact regret distortion;
2. one typed context-compiler grammar;
3. naive and statistically valid promotion gates;
4. random and LLM-guided proposal mechanisms;
5. multiple complete outer-loop seeds and one sealed test;
6. a finite-class theorem plus an empirical adaptive-selection curve.

Extensions can add a real coding/tool environment, information-limited gate feedback,
continual task drift, safe-policy-improvement baselines, or cost-aware successive halving.
The central contribution should remain the same: separating the ability to **search for**
a better harness from the evidence required to **believe and deploy** the change.
