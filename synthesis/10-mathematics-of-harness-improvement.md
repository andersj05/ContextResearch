---
title: "Mathematics of Harness Improvement"
document_type: "theoretical synthesis and candidate theorem package"
last_evidence_check: "2026-09-04"
proof_status: "source theorems, transferred results, modeling choices, and new derivations are explicitly distinguished"
---

# Mathematics of Harness Improvement

## Abstract

A self-improving LLM harness is not one mathematical object. It combines at least
three: a lossy state encoder, an adaptive optimizer, and an evaluator that decides
which changes survive. Each component has useful theory, but the guarantees compose
only under explicit assumptions. Rate-distortion theory limits how well a bounded
context can preserve a specified task signal. Blackwell comparison and belief-state
sufficiency identify when a summary retains all information needed for a decision.
Adaptive-data-analysis results quantify the optimism created by repeatedly selecting
against one evaluator. Uniform convergence gives a clean monotone-promotion theorem
when every reachable harness lies in a fixed, capacity-bounded class. Safe-policy and
program-synthesis results provide narrower improvement gates. Rice's theorem and
Blum's speedup theorem rule out several universal claims, but do not rule out useful
verification or optimization inside a restricted design language.

The main constructive result of this chapter is a candidate theorem for a
self-improving context compiler. It is proved here, rather than attributed to the
literature: with an independent validation sample, a fixed finite compiler class,
bounded loss, and a promotion margin larger than twice the uniform estimation error,
every accepted update reduces the same population objective by a prespecified
amount. The theorem is intentionally modest. It does not establish open-ended
self-improvement, semantic correctness in an unrestricted programming language, or
optimality of the learned context.

## 1. Status labels and scope

Every formal statement below has one of the following labels.

| Label | Meaning |
|---|---|
| **Source theorem** | A theorem or proposition stated in the cited work. |
| **Transferred theorem** | A source theorem applied to a harness after an explicit mathematical identification. The source proves the theorem, not the identification. |
| **Derived proposition** | A short consequence proved in this chapter from stated assumptions. |
| **Candidate theorem** | A new theorem formulation for the proposed research program, with a proof supplied here. |
| **Modeling choice** | A useful definition or objective, not an empirical fact or theorem. |
| **Empirical precedent** | Evidence that a construction has been tried; it does not prove the general mathematical claim. |

The repository link convention also matters. A local link of the form
paper-notes/source-id.md is the predictable note path for a PDF already acquired by
the project; some such notes are reserved and may still be awaiting extraction.
Sources not acquired locally are linked only to their canonical publisher or author
page.

Unless a base is written explicitly, \(\log\) is the natural logarithm and mutual
information is measured in nats. Divide nats by \(\log 2\) to obtain bits. This
convention keeps the constants in the moment-generating-function and Hoeffding
bounds below unambiguous.

### 1.1 Core random variables

Let

\[
X_t \in \mathcal X
\]

be the decision-relevant state available to the harness at time \(t\). It may include
the conversation, repository state, tool observations, budget, and the harness's
private memory. A context compiler with parameter \(\phi\) is a possibly randomized
channel

\[
Q_\phi(c\mid x), \qquad C_t\sim Q_\phi(\,\cdot\mid X_t),
\]

subject to a visible-context budget. A downstream model or policy maps context to an
action,

\[
A_t\sim \pi_\phi(\,\cdot\mid C_t).
\]

Let \(Y_t\) denote the future quantity that the context should preserve: for example,
the correct edit, a verifier outcome, a latent task state, or future return. The
basic graphical assumption used by information-bottleneck arguments is

\[
Y_t - X_t - C_t,
\]

meaning \(C_t\) is generated from \(X_t\) and has no additional access to \(Y_t\).
This Markov condition must be checked, not inferred from the word context.

For evaluation, let \(Z\sim P\) be a complete independent evaluation unit. To absorb
stochastic models and tools, \(Z\) should contain both the task instance and an
independent rollout seed. A compiler induces a bounded loss function

\[
f_\phi(Z)\in[0,1],\qquad
R(\phi)=\mathbb E_P[f_\phi(Z)].
\]

If cost matters, let \(g_\phi(Z)\in[0,1]\) be normalized resource use and define,
for a fixed \(\lambda\geq 0\),

\[
J_\lambda(\phi)
  =\mathbb E[f_\phi(Z)+\lambda g_\phi(Z)].
\]

When \(f+\lambda g\) is not in \([0,1]\), it must be rescaled before a bound for
bounded losses is invoked.

## 2. Context as rate-distortion coding

### 2.1 Classical result

**Source theorem — Shannon's rate-distortion theorem.** For a discrete memoryless
source \(X_1,X_2,\ldots\), a reproduction alphabet \(\widetilde{\mathcal X}\), and a
nonnegative single-letter distortion \(d(x,\tilde x)\), define

\[
R(D)
  =
  \min_{P_{\widetilde X\mid X}:
        \mathbb E[d(X,\widetilde X)]\leq D}
  I(X;\widetilde X).
\]

In the asymptotic block-coding limit, rates above \(R(D)\) nats per source symbol
are achievable at expected distortion at most \(D\), while rates below \(R(D)\)
are not. Equivalently, the rate in bits is \(R(D)/\log 2\). This is the
central fidelity theorem in Shannon's
[shannon-1959-rate-distortion](../paper-notes/shannon-1959-rate-distortion.md),
Sections 3–5.

**Transferred interpretation.** Treat a compiled context as the reproduction
\(\widetilde X\), or more generally as a code from which a task-relevant
reproduction can be decoded. Then a desired average distortion \(D\) requires at
least \(R(D)\) information bits per source symbol under Shannon's assumptions.

This transfer does **not** imply that a prompt of \(W\) tokens has information rate
\(W\). Token count is a syntactic budget. A coding rate requires a code alphabet,
block length, distribution, and treatment of shared side information. Nor does the
asymptotic theorem supply a finite-window guarantee for one evolving agent
trajectory.

### 2.2 Distortion must encode the research question

The theory is empty until \(d\) is chosen. Three non-equivalent choices are useful.

**Modeling choice A — reconstruction distortion.**

\[
d_{\mathrm{rec}}(x,\tilde x)
\]

penalizes failure to reproduce the full state. This is usually too strong for a
harness because most repository or transcript details are irrelevant to the next
decision.

**Modeling choice B — predictive distortion.** If \(Y\) is the relevant future
variable, define

\[
d_{\mathrm{pred}}(x,c)
  =
  D_{\mathrm{KL}}\!\left(
    P(Y\mid X=x)
    \,\Vert\,
    P(Y\mid C=c)
  \right).
\]

This matches the distortion that appears in the information-bottleneck stationary
equations. It requires a well-defined joint distribution \(P(X,Y)\). Because
\(P(Y\mid C=c)\) itself depends on the encoder, this is not a fixed distortion
matrix that can be inserted into Shannon's classical \(R(D)\) unchanged; it belongs
to the joint information-bottleneck variational problem.

**Modeling choice C — decision regret.** For action loss
\(\ell(a,x)\), let \(a_C(c)\) be the action selected from compiled context and set

\[
d_{\mathrm{dec}}(x,c)
  =
  \mathbb E[\ell(a_C(c),x)\mid x,c]
  -
  \inf_{a\in\mathcal A}\ell(a,x).
\]

This directly measures harm caused by context loss, but it is relative to an action
class and decoder. It is not an intrinsic property of the text.

The acquired prompt-compression studies
[nagle-2024-prompt-compression-rate-distortion](../paper-notes/nagle-2024-prompt-compression-rate-distortion.md)
and
[wang-2024-quito-x](../paper-notes/wang-2024-quito-x.md)
are useful empirical precedents for importing rate-distortion or
information-bottleneck language into prompt compression. They do not remove the
need to identify the source distribution, distortion, or operational code in an
agent harness.

### 2.3 A finite-window lower bound that is safe to claim

**Derived proposition.** For any joint law \(P_{X,C}\) generated by a compiler and
any distortion constraint \(\mathbb E d(X,C)\leq D\),

\[
I(X;C)\geq R(D)
\]

by the definition of \(R(D)\), provided \(C\) is in the reproduction alphabet used
to define that function.

This inequality is finite-sample as a property of one joint distribution. The
stronger claim that \(R(D)\) tokens are necessary or sufficient is not justified
without an operational token code.

**Derived proposition — an explicit token upper bound.** Suppose context is a
string of at most \(W\) symbols from a fixed vocabulary of size \(q\), the length is
observable, and there is no additional out-of-band context. Then

\[
I(X;C)
\leq H(C)
\leq
\log\!\left(
  \sum_{w=0}^{W}q^w
\right).
\]

If every context has exactly \(W\) symbols, this simplifies to

\[
I(X;C)\leq W\log q.
\]

**Proof.** Mutual information never exceeds the entropy of either variable, and
the entropy of a random variable supported on \(N\) values is at most \(\log N\).
There are at most \(\sum_{w=0}^{W}q^w\) permitted strings. \(\square\)

This is only an upper bound. It can be very loose, and shared model weights,
retrieved files, tool state, or hidden memory are side information that must be
included in the channel model.

## 3. The information bottleneck

### 3.1 Variational objective and stationary encoder

**Source theorem — information-bottleneck stationary conditions.** Under the
Markov relation \(C-X-Y\), Tishby, Pereira, and Bialek define

\[
\mathcal L_\beta(Q)
  =
  I(X;C)-\beta I(C;Y),
  \qquad \beta\geq 0.
\]

The stationary encoder obeys

\[
Q_\beta(c\mid x)
  =
  \frac{P_\beta(c)}
       {Z_\beta(x)}
  \exp\!\left[
    -\beta
    D_{\mathrm{KL}}\!\left(
      P(Y\mid x)\Vert P_\beta(Y\mid c)
    \right)
  \right].
\]

The associated marginals \(P_\beta(c)\) and \(P_\beta(Y\mid c)\) satisfy
self-consistency equations. See
[tishby-2000-information-bottleneck](../paper-notes/tishby-2000-information-bottleneck.md),
Equations 15 and 28 and Theorems 4–5.

The alternating procedure has the stated stationary/minimum structure under the
paper's assumptions. The joint optimization is not generally convex in all
conditional distributions simultaneously, so the theorem is not a guarantee that
an arbitrary neural compiler training run finds a unique global optimum.

### 3.2 Sufficient context

**Definition — predictive sufficiency.** A context \(C\) is sufficient for \(Y\)
relative to \(X\) when

\[
Y\perp X\mid C,
\]

or equivalently, under ordinary regularity conditions,

\[
I(X;Y\mid C)=0.
\]

Because \(C-X-Y\), the chain rule gives

\[
I(X;Y)
  =
  I(C;Y)+I(X;Y\mid C).
\]

Thus sufficiency is equivalent to

\[
I(C;Y)=I(X;Y).
\]

**Derived proposition.** If \(C\) is predictively sufficient for \(Y\), then every
Bayes decision problem whose loss depends on \(X\) only through \(Y\) has the same
optimal Bayes risk when conditioned on \(C\) as when conditioned on \(X\).

**Proof.** Sufficiency gives \(P(Y\mid X)=P(Y\mid C)\) almost surely. Expected loss
for any action is therefore computed from the same posterior distribution of \(Y\)
under either observation. Taking the infimum over actions preserves equality.
\(\square\)

The conclusion is task-relative. Choosing \(Y\) to be one benchmark label does not
make the context sufficient for debugging, safety, or a later task distribution.

## 4. Blackwell order and belief-state sufficiency

### 4.1 A compiler is a garbling of its input

**Source theorem — Blackwell comparison.** For finite statistical experiments,
experiment \(E\) is at least as informative as experiment \(F\) for every prior,
action set, and bounded payoff function if and only if \(F\) can be obtained by a
stochastic garbling of \(E\). See Blackwell,
[Equivalent Comparisons of Experiments](https://doi.org/10.1214/aoms/1177729032).

Since \(C\sim Q_\phi(\cdot\mid X)\), observing \(C\) is a garbling of observing
\(X\). Therefore:

\[
V^\star(X;u)\geq V^\star(C;u)
\]

for every ideal Bayesian decision problem \(u\).

**Transferred theorem.** No lossy context compiler can improve the value of
information for an ideal, unconstrained Bayesian decision maker in every task.

This does not contradict practical improvements from summarization. A fixed LLM has
bounded attention, imperfect inference, a context-window constraint, and
nonzero processing cost. Compression may improve the performance of that bounded
decoder even though it cannot improve the Blackwell information order.

### 4.2 Belief as a sufficient control state

For a partially observed Markov process with hidden state \(S_t\), history \(H_t\),
known transition model, and known observation model, define the posterior belief

\[
b_t(s)=P(S_t=s\mid H_t).
\]

**Source theorem — finite-horizon POMDP reduction.** In the finite-state,
finite-action, finite-horizon setting, \(b_t\) is a sufficient state for optimal
control, and the finite-horizon value function is piecewise linear and convex in
the belief. See Smallwood and Sondik,
[The Optimal Control of Partially Observable Markov Processes over a Finite Horizon](https://doi.org/10.1287/opre.21.5.1071).

**Transferred design target.** A harness memory need not reproduce the transcript
if it preserves a sufficient belief about the task state. The practical obstacle is
that software tasks do not arrive with a known finite transition or observation
model. An LLM-generated summary is an estimated belief representation, not the
belief-state theorem's exact statistic.

### 4.3 What can be proved and what must be modeled

| Claim | Status |
|---|---|
| Garbling cannot improve every ideal decision problem | Source theorem transferred directly |
| Exact posterior belief is sufficient in the specified finite POMDP | Source theorem |
| A particular text summary approximates that posterior | Empirical/modeling claim |
| A lower information-bottleneck objective improves a coding agent | Empirical claim |
| Token length is an information-theoretic rate | Generally false without an explicit code model |

## 5. Selection bias and the optimizer's curse

Let candidate \(i\) have unknown population value \(\mu_i\) and noisy estimate
\(V_i\). The optimizer selects

\[
i^\star\in\arg\max_i V_i.
\]

**Source theorem — optimizer's curse.** If the estimates are conditionally
unbiased for their candidate values, then

\[
\mathbb E[\mu_{i^\star}-V_{i^\star}]\leq 0,
\]

with strict inequality under conditions that permit erroneous selection. The sign
result does not require independent or Gaussian errors. See Smith and Winkler,
[smith-2006-optimizers-curse](../paper-notes/smith-2006-optimizers-curse.md),
Proposition 1.

A transparent special-case derivation is:

\[
\mathbb E[V_{i^\star}]
  =
  \mathbb E[\max_i V_i]
  \geq
  \max_i \mathbb E[V_i]
  =
  \max_i\mu_i,
\]

while \(\mu_{i^\star}\leq\max_i\mu_i\) pointwise. Hence
\(\mathbb E[V_{i^\star}-\mu_{i^\star}]\geq0\).
This derivation illustrates the source proposition; it is not an independent
literature claim.

The magnitude is model-dependent. Under independent
\(\sigma/\sqrt n\)-sub-Gaussian evaluation errors for \(m\) candidates, the
information bound in the next section yields the familiar upper scale

\[
\sigma\sqrt{\frac{2\log m}{n}}.
\]

It is an upper bound under assumptions, not a universal law of benchmark hacking.

The acquired study
[cawley-2010-model-selection-overfitting](../paper-notes/cawley-2010-model-selection-overfitting.md)
provides empirical and methodological evidence that optimizing a noisy
cross-validation criterion can improve the criterion while worsening true error.
Its remedy is nested evaluation around the full selection procedure. It does not
establish a universal numerical correction for harness search.

## 6. Mutual information bounds for adaptive evaluation

Suppose \(\phi_1,\ldots,\phi_m\) are estimates of means
\(\mu_1,\ldots,\mu_m\), and each centered variable
\(\phi_i-\mu_i\) is \(\sigma\)-sub-Gaussian:

\[
\log\mathbb E
  \exp\{\lambda(\phi_i-\mu_i)\}
  \leq\frac{\lambda^2\sigma^2}{2}
  \quad\text{for all }\lambda\in\mathbb R.
\]

An adaptive procedure observes information about
\(\boldsymbol\phi=(\phi_1,\ldots,\phi_m)\) and outputs index \(T\).

**Source theorem — information-theoretic adaptive bias.**

\[
\left|
  \mathbb E[\phi_T-\mu_T]
\right|
\leq
\sigma\sqrt{2I(T;\boldsymbol\phi)}.
\]

See Russo and Zou,
[russo-2016-adaptive-bias](../paper-notes/russo-2016-adaptive-bias.md),
Proposition 1 and its corollaries.

For an average of \(n\) independent \(\sigma\)-sub-Gaussian observations per
candidate, the scale becomes

\[
\left|
  \mathbb E[\widehat\mu_T-\mu_T]
\right|
\leq
\sigma\sqrt{\frac{2I(T;\boldsymbol{\widehat\mu})}{n}}.
\]

Since \(I(T;\boldsymbol{\widehat\mu})\leq H(T)\leq\log m\),

\[
\left|
  \mathbb E[\widehat\mu_T-\mu_T]
\right|
\leq
\sigma\sqrt{\frac{2\log m}{n}}.
\]

### 6.1 Proof mechanism

For each fixed \(i\), the sub-Gaussian moment-generating-function bound and a
change-of-measure inequality imply

\[
\lambda\,
\mathbb E[\phi_T-\mu_T]
\leq
I(T;\boldsymbol\phi)
+\frac{\lambda^2\sigma^2}{2}.
\]

Dividing by \(\lambda>0\) and minimizing at
\(\lambda=\sqrt{2I}/\sigma\) gives the positive-direction bound. Applying the same
argument to \(-(\phi_i-\mu_i)\) gives the absolute-value result.

### 6.2 Transfer limits

The theorem bounds **expected bias**, not a high-probability deviation for one
experiment. \(I(T;\boldsymbol\phi)\) describes the information revealed about
scores by the entire adaptive procedure; counting the final prompt edits is not a
substitute. The finite-\(m\) corollary also fails to describe an unrestricted
program generator unless its output is discretized into a fixed candidate family.

For harness engineering, the theorem supports three design principles:

1. reveal less exact evaluator information to the generator;
2. keep the number or capacity of selectable variants controlled; and
3. use an independent final gate after adaptive development.

It does not prove that hiding scores is always operationally optimal, because
feedback also carries useful optimization signal.

## 7. Reusable holdouts and leaderboard feedback

### 7.1 Transcript capacity

Suppose a fixed, nonadaptive analysis would fail with probability at most
\(\beta\), but an adaptive interaction with the holdout produces at most \(B\)
bits of transcript. There are at most \(2^B\) possible transcripts and therefore
at most \(2^B\) induced fixed analyses.

**Derived union-bound proposition.**

\[
P(\text{some transcript-selected analysis fails})
\leq 2^B\beta.
\]

This elementary argument is one motivation for bounded-description or
differentially private feedback. It becomes vacuous once \(B\) is large.

**Source results — reusable holdout.** Dwork et al. show that stability, formalized
through differential privacy and approximate max-information, permits repeated
adaptive use of a holdout. In particular, their Theorem 20 bounds approximate
max-information for an \(\varepsilon\)-differentially private algorithm on an
i.i.d. sample:

\[
I_{\infty}^{\beta}(S;A(S))
\leq
\log(e)
\left[
  \frac{\varepsilon^2 n}{2}
  +
  \varepsilon
  \sqrt{\frac{n\log(2/\beta)}{2}}
\right].
\]

See
[dwork-2015-adaptive-holdout](../paper-notes/dwork-2015-adaptive-holdout.md),
especially Theorem 20 and the Thresholdout analysis. These are theorems for
bounded statistical queries, i.i.d. sampling, specified sensitivity, and the
paper's privacy mechanism. They are not a license to reuse an arbitrary coding
benchmark indefinitely.

### 7.2 The Ladder

The Ladder mechanism reports a new leaderboard value only when a submission
meaningfully improves the running best, with rounding.

**Source theorem — Ladder leaderboard error.** For \(t\) adaptively selected
classifiers, sample size \(n\), bounded loss, and Ladder step size \(\eta\), Blum
and Hardt establish a bound of the form

\[
P\!\left(
  \left|
    \min_{i\leq t}R_D(f_i)-R_t
  \right|
  >
  \varepsilon+\eta
\right)
\leq
\exp\!\left[
  -2\varepsilon^2n
  +
  \left(\frac{1}{\eta}+2\right)
  \log\!\left(\frac{4t}{\eta}\right)
  +1
\right].
\]

Choosing \(\eta\) appropriately yields leaderboard error on the order of

\[
O\!\left(
  \left(\frac{\log(tn)}{n}\right)^{1/3}
\right).
\]

See
[blum-2015-ladder](../paper-notes/blum-2015-ladder.md),
Theorem 3.1. The guarantee concerns the reported running best, not valid estimates
for every submission and not arbitrary rich diagnostic feedback.

### 7.3 A computational barrier

Hardt and Ullman give a conditional hardness result: under standard
cryptographic assumptions, no efficient oracle with \(n\) samples can validly
answer roughly \(n^{3+o(1)}\) adversarially adaptive statistical queries in their
model. See
[hardt-2014-adaptive-hardness](../paper-notes/hardt-2014-adaptive-hardness.md).
This is a worst-case computational result for a formal query model. It is evidence
against unlimited evaluator reuse, not a measured limit for current LLM agents.

## 8. Fixed-capacity promotion guarantees

The cleanest improvement theorem avoids trying to characterize the optimizer. It
instead constrains every result the optimizer is allowed to submit.

### 8.1 Finite-class uniform validation

Let \(\mathcal F=\{f_1,\ldots,f_M\}\) be fixed before validation data
\(V=(Z_1,\ldots,Z_n)\) are drawn, with each \(f\in\mathcal F\) mapping evaluation
units to \([0,1]\). Define

\[
\widehat R_V(f)=\frac1n\sum_{j=1}^{n}f(Z_j),
\qquad
R(f)=\mathbb E f(Z).
\]

By Hoeffding's inequality and a union bound, with probability at least
\(1-\delta\),

\[
\sup_{f\in\mathcal F}
\left|
  \widehat R_V(f)-R(f)
\right|
\leq
\varepsilon_{n,M,\delta},
\]

where

\[
\varepsilon_{n,M,\delta}
=
\sqrt{
  \frac{\log(2M/\delta)}{2n}
}.
\]

This event is simultaneous over the entire class. Consequently, candidates may be
chosen adaptively using validation feedback **without invalidating this particular
bound**, as long as every possible candidate was already in the fixed class and the
loss mapping itself was fixed.

### 8.2 Monotone promotion

**Derived proposition — fixed-class promotion.** On the simultaneous event above,
accept a proposed \(f_{\mathrm{new}}\) over incumbent \(f_{\mathrm{old}}\) only if

\[
\widehat R_V(f_{\mathrm{new}})
\leq
\widehat R_V(f_{\mathrm{old}})
-
\left(2\varepsilon_{n,M,\delta}+\tau\right)
\]

for a chosen \(\tau>0\). Then every accepted promotion satisfies

\[
R(f_{\mathrm{new}})
\leq
R(f_{\mathrm{old}})-\tau.
\]

**Proof.**

\[
\begin{aligned}
R(f_{\mathrm{new}})
&\leq
\widehat R_V(f_{\mathrm{new}})+\varepsilon\\
&\leq
\widehat R_V(f_{\mathrm{old}})-\varepsilon-\tau\\
&\leq
R(f_{\mathrm{old}})-\tau.
\end{aligned}
\]

All inequalities hold simultaneously on the stated event. \(\square\)

**Corollary — finite accepted sequence.** Because \(R\geq0\), a sequence beginning
at risk \(R_0\) can contain at most

\[
\left\lfloor\frac{R_0}{\tau}\right\rfloor
\]

accepted \(\tau\)-improvements on the same target distribution and objective.

This is a strength and a warning. Fixed-margin monotonicity cannot by itself produce
infinitely many strict improvements in a bounded objective.

### 8.3 Capacity-bounded extension

For an infinite class with VC-subgraph dimension or pseudodimension \(d<\infty\),
standard uniform-convergence results replace the finite-class radius by a bound of
the schematic form

\[
\varepsilon_{n,d,\delta}
=
O\!\left(
  \sqrt{
    \frac{
      d\log(en/d)+\log(1/\delta)
    }{n}
  }
\right).
\]

The same three-line promotion proof then applies. Constants and logarithmic terms
depend on the precise loss class and theorem selected; they should be fixed before
power calculations.

A directly related 2025 preprint, revised in 2026, by Wang, Dorchen, and Jin,
[wang-2025-statistical-limits](../paper-notes/wang-2025-statistical-limits.md),
formalizes a fixed reachable envelope and a two-gate rule. Its central
distribution-free condition is finite capacity of the reachable union, and its
promotion margin likewise exceeds twice the validation deviation plus a target
improvement. The current archival status should be checked before publication:
the arXiv record and the search-visible review record have not always displayed the
same status. Much of the mathematical engine is standard VC uniform convergence;
the hard research question is whether the reachable class of a real harness can be
specified and bounded non-vacuously.

### 8.4 Failure modes

The guarantee fails or changes when:

- the generator expands \(\mathcal F\) after seeing validation results;
- the evaluator, rubric, normalization, or stopping rule is tuned on \(V\);
- task instances are dependent in a way not covered by the concentration theorem;
- hidden stochasticity is not included in the evaluation unit;
- the population distribution drifts between promotions;
- the objective changes, so risks from different rounds are not comparable; or
- only the accepted candidates, rather than all reachable candidates, are counted
  when setting \(M\).

An independent locked audit remains useful even when the theorem applies. It tests
whether the formal class, sampling assumptions, and loss implementation matched
reality.

## 9. Safe policy improvement

When a harness change is naturally a policy update in a Markov decision process,
safe-policy-improvement theory offers a different kind of gate.

**Source theorem — SPIBB.** In a finite discounted MDP, SPIBB constrains the new
policy to follow a baseline policy \(\pi_b\) on state-action pairs whose dataset
count is below a threshold \(N_\Lambda\). Under the paper's model-estimation and
coverage assumptions, Theorem 2 gives, with probability at least \(1-\delta\),

\[
\rho(\pi_{\mathrm{SPIBB}},M^\star)
\geq
\rho(\pi_b,M^\star)-\zeta,
\]

where \(\zeta\) is an explicit function of \(N_\Lambda\), discount factor, state
and action counts, value range, confidence level, and empirical-model returns. See
[laroche-2019-spibb](../paper-notes/laroche-2019-spibb.md),
Theorem 2.

**Transferred design pattern.** Preserve the incumbent behavior in regions with
insufficient evidence, and allow changes only where coverage supports them.

The transfer is structural, not automatic. A coding agent does not become a finite
MDP merely because its run is sequential. State aliasing, model drift, enormous
action spaces, and tool side effects can violate the assumptions. Also,
\(\zeta\)-approximate safety permits degradation by as much as \(\zeta\); it is not
a theorem of strict improvement.

The fixed-class promotion theorem and SPIBB answer different questions:

- promotion controls selection error on an evaluation distribution;
- SPIBB controls policy degradation relative to a baseline under offline-MDP
  coverage assumptions.

Using both requires satisfying both sets of assumptions.

## 10. Restricted synthesis and proof gates

### 10.1 Syntax-guided synthesis

Let \(T\) be a decidable background theory, \(\varphi(f)\) a formal specification,
and \(L(G)\) the expressions generated by grammar \(G\). Syntax-guided synthesis
asks for

\[
e\in L(G)
\quad\text{such that}\quad
T\models\varphi[e/f].
\]

**Source framework.** Alur et al.,
[alur-2013-sygus](../paper-notes/alur-2013-sygus.md),
formalize this restricted search problem. Counterexample-guided inductive synthesis
iterates:

\[
\text{candidate}
\longrightarrow
\text{verifier}
\longrightarrow
\text{counterexample}
\longrightarrow
\text{refined candidate}.
\]

Solar-Lezama et al.,
[solar-lezama-2006-sketch](../paper-notes/solar-lezama-2006-sketch.md),
show how holes in a finite program sketch can be solved against assertions using
Boolean synthesis.

**Transferred theorem.** If the verifier is sound for \(T\), the specification is
correctly encoded, and a returned candidate satisfies the verification condition,
then the candidate satisfies that encoded condition in \(T\).

The conclusion is deliberately intensional. It proves neither that the
specification captures the user's intent nor that an external tool, operating
system, or model conforms to the formal semantics. Termination and completeness
also depend on the grammar, theory, and solver.

### 10.2 Proof-carrying self-modification

Schmidhuber's Gödel machine executes a self-rewrite only when its proof searcher
finds a proof, in the machine's axiom system, that switching now has greater
expected encoded utility than continuing the current search:

\[
\mathbb E[U\mid\text{execute switch now}]
>
\mathbb E[U\mid\text{continue proof search}].
\]

**Source theorem.** The global-optimality theorem is relative to the encoded
utility, axioms, hardware and resource model, and proof-search procedure. See
[schmidhuber-2003-godel-machines](../paper-notes/schmidhuber-2003-godel-machines.md),
Theorem 4.1. It does not guarantee that a useful proof exists, that it is found
within budget, or that the axioms correctly describe the world.

Hutter gives a related restricted result. For programs whose equivalence to a
reference program and runtime bounds are provable in a fixed formal system, a
universal construction has runtime

\[
\operatorname{time}_{M_{p^\star}}(x)
\leq
5t_p(x)
+d_p\,\operatorname{time}_{t_p}(x)
+c_p.
\]

See
[hutter-2002-fastest-provable-program](../paper-notes/hutter-2002-fastest-provable-program.md).
The constants can be enormous, and only provably equivalent competitors enter the
comparison.

### 10.3 Practical proof gate

A defensible harness proof gate therefore has four explicit layers:

1. **restricted edit language:** only a bounded grammar of context policies,
   routing rules, or tool wrappers may change;
2. **formal invariants:** type, access-control, budget, and state-transition
   properties checked by a sound verifier;
3. **empirical promotion:** outcome and cost tested on an independent statistical
   gate; and
4. **rollback:** the incumbent remains available when deployment evidence violates
   assumptions.

Formal verification covers layer 2. It does not replace layer 3 for properties such
as model helpfulness or distributional performance.

## 11. Limits from computability and complexity

### 11.1 Rice's theorem

Let \(\varphi_e\) be the partial computable function implemented by program index
\(e\). For any nontrivial extensional property \(P\) of partial computable
functions, the index set

\[
\{e:P(\varphi_e)\}
\]

is undecidable.

**Source theorem.** This is Rice's theorem; see
[Classes of Recursively Enumerable Sets and Their Decision Problems](https://doi.org/10.1090/S0002-9947-1953-0053041-6).

**Transfer.** There is no total algorithm that takes an arbitrary harness program
and decides every nontrivial semantic property such as always solves the task or
never causes harm.

**Limit of the limit.** Rice's theorem does not prohibit:

- verification in a finite or otherwise decidable DSL;
- proving a sufficient but incomplete set of invariants;
- bounded model checking;
- testing on a distribution;
- proof-carrying edits; or
- rejecting candidates when the verifier returns unknown.

Thus Rice motivates restricted synthesis; it does not make verification futile.

### 11.2 Blum speedup

Under a Blum complexity measure, the speedup theorem constructs total computable
functions for which no program is asymptotically fastest: for a prescribed
computable speedup relation, every program computing the function has another
program computing the same function that is eventually faster by that relation.
See Blum,
[A Machine-Independent Theory of the Complexity of Recursive Functions](https://doi.org/10.1145/321386.321395).

**Transferred implication.** A universal claim that open-ended search must
eventually find the final fastest equivalent harness is false in the unrestricted
setting.

**Transfer limit.** This is an existential asymptotic result. It does not say that
every task admits endless practical speedups, nor that a finite harness family lacks
an optimum. Hutter's proof-restricted comparison does not contradict Blum: it
changes the comparator class and pays program-dependent constants.

### 11.3 Self-modification policy invariance

Everitt et al. analyze agents that can modify their own policy or utility function.
Under modification-independent beliefs and an initial utility function used to
evaluate future modifications, their realistic-value construction makes future
policies on-policy optimal for the initial objective. See
[everitt-2016-self-modification](../paper-notes/everitt-2016-self-modification.md),
especially Theorem 16.

The result is a coherence theorem inside an idealized model. It does not protect a
harness from a misspecified objective, corrupted observations or rewards,
off-policy distribution shift, failed exploration, or an unsound evaluator.

## 12. Cost-aware candidate search

Outcome-only optimization encourages expensive retry loops. Two classical search
models provide useful baselines, but neither exactly models evolving LLM-generated
candidates.

### 12.1 Objective and Pareto order

**Modeling choice.** For risk \(R(\phi)\) and expected cost \(C(\phi)\), define

\[
J_\lambda(\phi)=R(\phi)+\lambda C(\phi).
\]

For a fixed \(\lambda\), promotion may use \(J_\lambda\) in place of \(R\), provided
the per-evaluation scalar loss is bounded or has an appropriate concentration
bound. Because conclusions depend on \(\lambda\), a stronger report presents the
estimated Pareto set:

\[
\mathcal P
=
\left\{
  \phi:
  \nexists\phi'
  \text{ with }
  R(\phi')\leq R(\phi),
  C(\phi')\leq C(\phi),
  \text{ and one strict}
\right\}.
\]

Scalarization can miss non-convex parts of a Pareto frontier.

### 12.2 Pandora's rule

In Weitzman's search model, box \(i\) has independent reward \(X_i\) from a known
distribution and inspection cost \(c_i\). Its reservation value \(z_i\) solves

\[
c_i=\mathbb E[(X_i-z_i)^+].
\]

**Source theorem.** Inspect the unopened box with greatest reservation value and
stop when the best observed reward is at least every remaining reservation value.
This policy is optimal under the model's assumptions. See
[weitzman-1979-optimal-search](../paper-notes/weitzman-1979-optimal-search.md).

For a harness, this supplies an interpretable value-of-information policy only when
candidate value distributions and evaluation costs are known and candidates are
independent. Generated patches usually share ancestry, evaluations reveal
correlated information, and the distribution changes as the optimizer learns.
Without a new dependent-search proof, Pandora's rule is a heuristic.

### 12.3 Successive Halving

For \(n\) fixed candidate arms with limiting losses
\(\nu_1<\nu_2\leq\cdots\leq\nu_n\), suppose each finite-budget loss approaches its
limit within a known envelope \(\gamma_i(t)\), and let
\(\bar\gamma(t)=\max_i\gamma_i(t)\). Write the generalized inverse as

\[
\bar\gamma^{-1}(a)
=
\min\{t:\bar\gamma(t)\leq a\}.
\]

**Source theorem.** Jamieson and Talwalkar show that Successive Halving identifies
the best arm when total budget \(B\) exceeds a threshold of the form

\[
B
>
2\lceil\log_2 n\rceil
\max_{2\leq i\leq n}
i
\left[
  1+
  \bar\gamma^{-1}
  \left(
    \frac{\nu_i-\nu_1}{2}
  \right)
\right].
\]

See
[jamieson-2016-successive-halving](../paper-notes/jamieson-2016-successive-halving.md),
Theorem 1 and the doubling discussion.

This justifies eliminating clearly weak fixed candidates at low fidelity when
their evaluation trajectories converge predictably. It does not cover candidates
created adaptively after observing prior eliminations, nonconvergent model behavior,
or early evaluations that reverse rankings without a valid envelope.

### 12.4 Cost-aware promotion

**Derived proposition.** Let

\[
h_\phi(Z)
=
\frac{
  f_\phi(Z)+\lambda g_\phi(Z)
}{
  1+\lambda
}
\in[0,1].
\]

If the fixed-class promotion rule of Section 8 is applied to \(h_\phi\), then with
the same probability it decreases normalized population objective
\(\mathbb E h_\phi\) by at least \(\tau\) per accepted update. Equivalently,

\[
J_\lambda(\phi_{\mathrm{new}})
\leq
J_\lambda(\phi_{\mathrm{old}})
-
(1+\lambda)\tau.
\]

This proves monotonicity for one declared scalarization. It does not prove Pareto
dominance or optimal candidate-allocation policy.

## 13. Candidate definition and theorem package

This section isolates a research target that is both mathematically precise and
plausibly testable.

### 13.1 Definition: self-improving context compiler

**Candidate definition.** A self-improving context compiler is a tuple

\[
\mathfrak C
=
(
  P,\mathcal X,\mathcal C,\mathcal Y,
  \Phi,Q,\Pi,\ell,\kappa,
  \mathcal D,\mathcal V,\mathcal T,
  \mathsf G,\mathsf P
),
\]

with:

1. a fixed target distribution \(P\) over complete evaluation units \(Z\), latent
   states \(X\), and relevance variables \(Y\);
2. a compiler family
   \(Q_\phi(C\mid X)\), \(\phi\in\Phi\), with visible-context alphabet
   \(\mathcal C\);
3. a downstream policy family \(\Pi\) that acts only through compiled context;
4. bounded task loss \(\ell_\phi(Z)\in[0,1]\) and normalized resource cost
   \(\kappa_\phi(Z)\in[0,1]\);
5. disjoint development, promotion, and audit samples
   \(\mathcal D,\mathcal V,\mathcal T\);
6. a generator \(\mathsf G\) that proposes new \(\phi\) using development
   information and only the feedback channel declared for \(\mathcal V\); and
7. a promotion gate \(\mathsf P\) that either retains the incumbent or atomically
   replaces it.

The compiler is **rate constrained** at budget \(r\) when

\[
I_P(X;C)\leq r.
\]

It is **syntactically constrained** at token budget \(W\) when

\[
|C|\leq W
\quad\text{almost surely}.
\]

These constraints are different. One does not imply the other without a coding
model.

It is **\(Y\)-sufficient** when

\[
I_P(X;Y\mid C)=0.
\]

It is **\(\varepsilon\)-decision-sufficient** for action class
\(\mathcal A\) when

\[
\inf_{\delta:\mathcal C\to\mathcal A}
\mathbb E[\ell(\delta(C),Y)]
-
\inf_{\alpha:\mathcal X\to\mathcal A}
\mathbb E[\ell(\alpha(X),Y)]
\leq\varepsilon.
\]

It is **self-improving at margin \(\tau\)** over a run when every promoted compiler
reduces the same declared population objective by at least \(\tau\).

### 13.2 Admissibility assumptions

For a theorem, impose:

**A1 — fixed population.** All promotion units are i.i.d. from one distribution
\(P\), and \(P\) does not change across the theorem's run.

**A2 — complete evaluation unit.** \(Z\) includes all randomized rollout,
environment, and grading seeds required to make \(h_\phi(Z)\) a fixed measurable
function.

**A3 — bounded fixed objective.**

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

with \(\lambda\) fixed before viewing promotion data.

**A4 — fixed reachable family.** The initial incumbent and every compiler the
generator could submit belong to a finite family \(\Phi_0\) of size \(M\), fixed
independently of \(\mathcal V\). Equivalently, the induced loss family
\(\mathcal H_0=\{h_\phi:\phi\in\Phi_0\}\) is fixed.

**A5 — independent promotion sample.**
\(\mathcal V=(Z_1,\ldots,Z_n)\) is independent of all data used to design
\(\Phi_0\), though the generator may adapt to the allowed feedback from
\(\mathcal V\).

**A6 — immutable gate.** The promotion threshold, objective, evaluator code, and
class \(\Phi_0\) are not altered using \(\mathcal V\).

**A7 — atomic rollback.** Rejecting a candidate leaves the incumbent and its
external state unchanged. This is an engineering assumption, not a statistical
consequence.

### 13.3 Candidate theorem: monotone promotion of a fixed compiler family

Define

\[
\widehat J_V(\phi)
=
\frac1n\sum_{j=1}^{n}h_\phi(Z_j),
\qquad
J(\phi)=\mathbb E_P[h_\phi(Z)],
\]

and

\[
\varepsilon
=
\sqrt{\frac{\log(2M/\delta)}{2n}}.
\]

Promote \(\phi'\) over incumbent \(\phi\) only if

\[
\widehat J_V(\phi')
\leq
\widehat J_V(\phi)
-
(2\varepsilon+\tau).
\tag{P}
\]

**Candidate theorem — proved here.** Under A1–A6, with probability at least
\(1-\delta\) over \(\mathcal V\), every promotion made by rule (P), including an
adaptively chosen sequence of promotions, satisfies

\[
J(\phi')\leq J(\phi)-\tau.
\]

Consequently, if the run begins at \(\phi_0\), the number \(N\) of accepted
promotions satisfies

\[
N\leq
\left\lfloor
  \frac{J(\phi_0)}{\tau}
\right\rfloor
\leq
\left\lfloor
  \frac1{\tau}
\right\rfloor.
\]

**Proof.** For fixed \(\phi\), Hoeffding gives

\[
P\!\left(
  |\widehat J_V(\phi)-J(\phi)|>\varepsilon
\right)
\leq
2e^{-2n\varepsilon^2}.
\]

A union bound over the \(M\) fixed compilers makes the probability that any
deviation exceeds \(\varepsilon\) at most

\[
2M e^{-2n\varepsilon^2}=\delta.
\]

On the complementary simultaneous event, for every possible incumbent and
candidate,

\[
\begin{aligned}
J(\phi')
&\leq \widehat J_V(\phi')+\varepsilon\\
&\leq \widehat J_V(\phi)-\varepsilon-\tau\\
&\leq J(\phi)-\tau.
\end{aligned}
\]

Because this event holds for all \(\Phi_0\) at once, adaptive selection inside that
fixed family does not require a second union bound over rounds. Iterating gives
\(J(\phi_N)\leq J(\phi_0)-N\tau\). Since \(J\geq0\), the claimed bound on \(N\)
follows. \(\square\)

### 13.4 Corollaries and non-corollaries

**Corollary — sample-size requirement.** To make the statistical component of the
promotion margin at most \(\gamma>0\), it suffices that

\[
2\varepsilon\leq\gamma,
\]

or

\[
n
\geq
\frac{2\log(2M/\delta)}{\gamma^2}.
\]

**Corollary — rate-distortion compatibility.** If, separately, the source is
discrete memoryless, the operational asymptotic coding assumptions hold, and every
admissible compiler achieves expected distortion at most \(D\), then its
information rate must be at least \(R(D)\). This constrains the feasible class but
does not prove that promotion finds a rate-distortion-optimal member.

**Corollary — formal safety.** If every \(\phi\in\Phi_0\) is produced by a sound
restricted synthesizer and verified against invariant \(\mathcal I\), then every
promoted compiler satisfies \(\mathcal I\) in the verifier's semantics. This
conclusion comes from the proof gate, not from statistical validation.

The theorem does **not** imply:

- convergence to the globally optimal compiler;
- sufficiency of the learned context;
- improvement after the fixed class is expanded;
- protection against a wrong objective or wrong population;
- improvement on a future distribution;
- safety of side effects excluded from \(Z\) and \(\ell\); or
- an efficient method for finding candidates that pass the margin.

### 13.5 A publishable experimental test

The theorem suggests a factorial experiment rather than a single benchmark score.
Predeclare:

- context budget \(W\) and, where estimable, information proxy \(r\);
- compiler class or capacity envelope;
- feedback regime: exact, rounded Ladder-style, or fresh-split;
- promotion margin and confidence level;
- outcome-cost scalarization or full Pareto reporting;
- locked final audit; and
- ablations for compiler, evaluator, proof gate, and candidate scheduler.

The mathematical claim is then about promotion validity. The empirical claim is
whether the proposed compiler family contains useful improvements at tolerable
cost.

## 14. Claims that are not defensible

The following statements should not appear as conclusions of the paper without
substantially stronger assumptions or new proofs.

1. **A shorter context contains more information than the full state.** A compiler
   is a Blackwell garbling. It may help a bounded decoder, not dominate full
   information for every ideal decision maker.

2. **A \(W\)-token context has rate \(W\).** Tokens and Shannon bits are not
   interchangeable without an operational code and source model.

3. **Information-bottleneck training finds the globally optimal context.** The
   classical stationary equations do not guarantee unique global neural
   optimization, and relevance variable \(Y\) may be misspecified.

4. **A benchmark improvement selected from many variants is unbiased.** The
   optimizer's curse and adaptive-data-analysis bounds predict optimism unless
   selection is covered by uniform convergence, stability, or fresh data.

5. **A holdout can be reused indefinitely because it was initially hidden.**
   Exact or rich feedback leaks information. Reuse guarantees require a specified
   mechanism and assumptions.

6. **Counting accepted edits controls evaluator overfitting.** The relevant
   complexity is the set of all reachable or distinguishable candidates and the
   feedback transcript, including rejected proposals.

7. **A two-gate margin guarantees improvement for an open-ended generator.** The
   fixed-class proof fails when the generator or evaluator expands using the
   promotion set.

8. **Approximate safe policy improvement means no degradation.** SPIBB's theorem
   permits loss up to its stated \(\zeta\) and requires a finite discounted-MDP
   model with coverage.

9. **Passing tests proves semantic correctness.** Tests establish only sampled
   behavior. Formal synthesis proves only the encoded specification in the stated
   semantics.

10. **A Gödel-style proof gate guarantees that a beneficial self-rewrite will be
    found.** Its theorem is conditional on finding a proof in the encoded system
    and on the correctness of that system.

11. **Rice's theorem makes harness verification impossible.** It blocks complete
    decision procedures for nontrivial extensional properties of arbitrary
    programs, not restricted DSLs or sound incomplete checks.

12. **Blum speedup means practical harness optimization never terminates.** It is
    an existential asymptotic theorem, not a statement about every finite task or
    compiler family.

13. **Pandora's rule is optimal for LLM-generated candidates.** Its optimality
    assumes known independent box-value distributions and fixed inspection costs.

14. **Successive Halving is valid for continually invented candidates.** The cited
    result assumes a fixed arm set and valid convergence envelopes.

15. **Monotone validation risk is open-ended self-improvement.** Under a positive
    fixed margin and bounded objective, the candidate theorem allows only finitely
    many accepted updates.

16. **An evaluator score is the construct of harness intelligence.** It is a
    measurement under a task distribution, rubric, resource budget, and time
    horizon. Construct validity remains empirical.

## 15. Source map and acquisition status

### 15.1 Acquired PDFs with predictable local note paths

The project has acquired PDFs for the following sources. Their links reserve the
consistent note paths used by this repository:

- [nagle-2024-prompt-compression-rate-distortion](../paper-notes/nagle-2024-prompt-compression-rate-distortion.md)
- [wang-2024-quito-x](../paper-notes/wang-2024-quito-x.md)
- [cawley-2010-model-selection-overfitting](../paper-notes/cawley-2010-model-selection-overfitting.md)
- [dwork-2015-adaptive-holdout](../paper-notes/dwork-2015-adaptive-holdout.md)
- [blum-2015-ladder](../paper-notes/blum-2015-ladder.md)
- [laroche-2019-spibb](../paper-notes/laroche-2019-spibb.md)
- [schmidhuber-2003-godel-machines](../paper-notes/schmidhuber-2003-godel-machines.md)
- [shannon-1959-rate-distortion](../paper-notes/shannon-1959-rate-distortion.md)
- [tishby-2000-information-bottleneck](../paper-notes/tishby-2000-information-bottleneck.md)
- [smith-2006-optimizers-curse](../paper-notes/smith-2006-optimizers-curse.md)
- [russo-2016-adaptive-bias](../paper-notes/russo-2016-adaptive-bias.md)
- [hardt-2014-adaptive-hardness](../paper-notes/hardt-2014-adaptive-hardness.md)
- [wang-2025-statistical-limits](../paper-notes/wang-2025-statistical-limits.md)
- [solar-lezama-2006-sketch](../paper-notes/solar-lezama-2006-sketch.md)
- [alur-2013-sygus](../paper-notes/alur-2013-sygus.md)
- [hutter-2002-fastest-provable-program](../paper-notes/hutter-2002-fastest-provable-program.md)
- [everitt-2016-self-modification](../paper-notes/everitt-2016-self-modification.md)
- [weitzman-1979-optimal-search](../paper-notes/weitzman-1979-optimal-search.md)
- [jamieson-2016-successive-halving](../paper-notes/jamieson-2016-successive-halving.md)

### 15.2 Canonical links for sources not yet acquired

- Blackwell, [Equivalent Comparisons of Experiments](https://doi.org/10.1214/aoms/1177729032)
- Smallwood and Sondik, [The Optimal Control of Partially Observable Markov Processes over a Finite Horizon](https://doi.org/10.1287/opre.21.5.1071)
- Rice, [Classes of Recursively Enumerable Sets and Their Decision Problems](https://doi.org/10.1090/S0002-9947-1953-0053041-6)
- Blum, [A Machine-Independent Theory of the Complexity of Recursive Functions](https://doi.org/10.1145/321386.321395)

## Conclusion

The strongest defensible mathematical program is not universal self-improvement.
It is constrained improvement with separately auditable claims:

\[
\text{task-relevant compression}
+
\text{capacity-controlled search}
+
\text{independent promotion}
+
\text{restricted verification}
+
\text{cost accounting}.
\]

Rate-distortion and sufficiency theory define what the context should preserve.
Adaptive-analysis theory defines how evaluator reuse can fail. Uniform convergence
provides a provable promotion rule for a fixed reachable class. Proof gates protect
formally stated invariants inside restricted languages. Cost-aware search allocates
resources under additional assumptions. The negative results mark the boundary:
none of these components, alone or together, proves that an unrestricted harness
can verify, optimize, and improve itself forever.
