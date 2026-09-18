---
title: "Mathematical Foundations for LLM Harness Evaluation"
document_type: "definitions, derivations, estimators, and experimental design"
last_evidence_check: "2026-09-04"
proof_status: "source-reported results and original derivations are explicitly distinguished"
---

# Mathematical Foundations for LLM Harness Evaluation

## Abstract

LLM harness evaluation combines at least four mathematical problems:

1. estimating stochastic task success under repeated sampling;
2. separating true task completion from an imperfect verifier;
3. modeling a multi-stage, stateful reliability process; and
4. comparing model-harness configurations under clustered tasks, unequal cost, and
   changing budgets.

This document develops a coherent notation for those problems. It proves the standard
pass@\(k\) and pass\(^{k}\) estimators, extends them to correlated trials through a
beta-binomial model, derives verifier positive predictive value and label correction,
formalizes sequential stopping, gives reliability-chain bounds, specifies a factorial
mixed-effects design and clustered bootstrap, and develops cost-Pareto and time-horizon
models.

Every result is labeled either **source-reported**, **standard result derived here**, or
**proposed model**. The derivations do not convert empirical regularities into universal
laws. In particular, independence, exchangeability, verifier calibration, and task
representativeness must be tested rather than assumed.

## 1. Evaluation object and notation

An evaluated system is a configuration

\[
\mathcal C=(M,H,P,T,E,B,V,S),
\]

with:

| Symbol | Meaning |
|---|---|
| \(M\) | base model and exact version |
| \(H\) | harness implementation and version |
| \(P\) | system prompt, context construction, memory, and compression policy |
| \(T\) | tool roster, schemas, execution semantics, and tool versions |
| \(E\) | runtime environment, dependencies, hardware, network, and concurrency |
| \(B\) | token, dollar, wall-time, tool-call, CPU, RAM, and human-intervention budget |
| \(V\) | tests, judge, proof checker, or other verifier |
| \(S\) | sampling, branching, retry, selection, and stopping policy |

This systems-level object is a **proposed model** motivated by controlled ACI ablations
[yang-2024-swe-agent, PDF p. 6, Table 3], the full model-harness factorial design in
Harness-Bench [yao-2026-harness-bench, PDF p. 6, Table 1], and HAL's three-dimensional
model-scaffold-benchmark analysis [kapoor-2026-hal, PDF pp. 2-4].

Let:

- \(i=1,\ldots,N\) index tasks;
- \(g(i)\) identify a repository, task family, or other top-level cluster;
- \(j=1,\ldots,n_i\) index repeated rollouts on task \(i\);
- \(X_{ij}\in\{0,1\}\) denote **true** task success;
- \(Z_{ij}\in\{0,1\}\) denote a positive automated verifier result;
- \(p_i=P(X_{ij}=1\mid i,\mathcal C)\);
- \(C_{ij}\ge 0\) denote measured rollout cost; and
- \(R(\mathcal C)=E_{i\sim\mathcal P}[p_i]\) denote average one-run success on the
  target task population \(\mathcal P\).

The distinction \(X\ne Z\) is fundamental. SWE-bench audits found test-passing patches
that fail broader tests or semantic inspection
[wang-2026-swe-solved-correctly, PDF pp. 2 and 9-10]. The Agentic Benchmark Checklist
names this gap outcome validity
[zhu-2025-rigorous-agentic-benchmarks, PDF pp. 2-4, Figure 1].

## 2. Estimands before estimators

Several quantities called "accuracy" answer different questions:

\[
\begin{aligned}
R_1 &= E_i[p_i],
&&\text{one-run population success},\\
R_{\mathrm{any}}(k) &= E_i[1-(1-p_i)^k],
&&\text{at least one success in \(k\) independent runs},\\
R_{\mathrm{all}}(k) &= E_i[p_i^k],
&&\text{success in every one of \(k\) independent runs},\\
R_{\mathrm{verify}} &= E_i[P(Z_{ij}=1\mid i)],
&&\text{observed verifier pass rate},\\
R_{\mathrm{deploy}} &= P(\text{acceptable real outcome}),
&&\text{deployment utility under the actual workflow}.
\end{aligned}
\]

Only the first three coincide at \(k=1\) and only when the verifier is perfect. The
HumanEval paper introduced the second quantity as pass@\(k\)
[chen-2021-codex-passk, PDF p. 3, Equation 1]. Tau-bench introduced the third as
pass\(^{k}\) to measure consistency
[yao-2024-tau-bench, PDF pp. 2 and 7, Figure 4].

### 2.1 Basic one-run estimator

If the \(N\) tasks are sampled from \(\mathcal P\), each receives one independent
rollout, and \(X_i\) is observed without error, then

\[
\widehat R_1=\frac1N\sum_{i=1}^{N}X_i
\]

is unbiased for \(R_1\). Its elementary Bernoulli standard error
\(\sqrt{\widehat R_1(1-\widehat R_1)/N}\) is valid only when tasks are independent and
identically sampled. Repository tasks, variants from one task family, and multiple
rollouts violate that assumption; Section 11 gives clustered alternatives.

## 3. Pass@\(k\): opportunity under repeated sampling

### 3.1 Definition

For task \(i\), assume \(k\) exchangeable candidate generations with constant success
probability \(p_i\) and conditional independence. Then

\[
\operatorname{pass@}k_i
=P\left(\max_{1\le j\le k}X_{ij}=1\right)
=1-(1-p_i)^k.
\]

The benchmark estimand is the macro-average

\[
\operatorname{pass@}k
=\frac1N\sum_{i=1}^{N}\left[1-(1-p_i)^k\right].
\]

This is the probability of having at least one correct candidate available. It is not
the probability that an unaided harness identifies that candidate, and it is not
repeat-run reliability.

### 3.2 Unbiased finite-sample estimator

Suppose \(n_i\ge k\) i.i.d. candidates are generated for task \(i\), of which
\(c_i=\sum_{j=1}^{n_i}X_{ij}\) are truly correct.

**Theorem 1 (source-reported estimator; proof expanded here).**

\[
\widehat{\operatorname{pass@}k}
=\frac1N\sum_{i=1}^{N}
\left[
1-\frac{\binom{n_i-c_i}{k}}{\binom{n_i}{k}}
\right],
\]

with the numerator defined as zero when \(n_i-c_i<k\), is unbiased for the macro-average
pass@\(k\).

**Proof.** Conditional on the observed \(n_i\) candidates and \(c_i\) successes,
choose a \(k\)-subset uniformly without replacement. There are \(\binom{n_i}{k}\)
possible subsets. Exactly \(\binom{n_i-c_i}{k}\) contain only failed candidates.
Therefore the conditional probability that the selected subset contains at least one
success is

\[
1-\frac{\binom{n_i-c_i}{k}}{\binom{n_i}{k}}.
\]

Unconditionally, a uniformly selected \(k\)-subset of \(n_i\) i.i.d. candidates has
the same joint distribution as the first \(k\) candidates. Its probability of at least
one success is \(1-(1-p_i)^k\). The tower property gives unbiasedness task by task;
linearity of expectation gives unbiasedness of the macro-average. \(\square\)

The formula and the warning that \(1-(1-\widehat p)^k\) is biased are
**source-reported** [chen-2021-codex-passk, PDF p. 3, Equation 1 and Figure 3].

### 3.3 Numerically stable evaluation

For \(n-c\ge k\),

\[
\frac{\binom{n-c}{k}}{\binom nk}
=\prod_{\ell=0}^{k-1}\frac{n-c-\ell}{n-\ell}.
\]

For large \(n\) or \(k\), compute the log product:

\[
\log P(\text{all fail})
=\sum_{\ell=0}^{k-1}
\left[\log(n-c-\ell)-\log(n-\ell)\right],
\]

then use a stable negative-exponential transform for \(1-\exp(\cdot)\).

### 3.4 Assumption failures

The estimator does not identify deployment performance when:

- generations are adaptive rather than exchangeable;
- later prompts include earlier failures;
- candidates share a deterministic decoding path;
- the verifier is used in place of true \(X\);
- a selector cannot recognize the correct candidate; or
- repeated samples receive a larger budget than the comparator.

The inference-scaling critique is precisely that imperfect tests make generated
availability different from selected correctness
[stroebl-2026-inference-scaling-flaws, PDF pp. 4-7].

## 4. Pass\(^{k}\): consistency under repetition

### 4.1 Definition and estimator

Under the same conditional-i.i.d. model,

\[
\operatorname{pass}^{k}_i
=P(X_{i1}=\cdots=X_{ik}=1)=p_i^k,
\]

and the macro-average is \(N^{-1}\sum_i p_i^k\).

**Theorem 2 (standard result derived here).** With \(n_i\ge k\) observed candidates
and \(c_i\) true successes,

\[
\widehat{\operatorname{pass}^{k}}
=\frac1N\sum_{i=1}^{N}
\frac{\binom{c_i}{k}}{\binom{n_i}{k}}
\]

is unbiased for macro-average pass\(^{k}\).

**Proof.** Of the \(\binom{n_i}{k}\) uniformly selected \(k\)-subsets,
\(\binom{c_i}{k}\) contain only successes. A selected subset is distributionally
identical to \(k\) fresh i.i.d. trials, whose all-success probability is \(p_i^k\).
Apply the tower property and average over tasks. \(\square\)

Tau-bench reports GPT-4o function calling at 61.2% pass\(^{1}\) on retail but below
25% pass\(^{8}\) [yao-2024-tau-bench, PDF p. 7, Table 2 and Figure 4].

### 4.2 Pass@\(k\) and pass\(^{k}\) move in opposite directions

For \(0<p_i<1\):

\[
\frac{d}{dk}\left[1-(1-p_i)^k\right]>0,
\qquad
\frac{d}{dk}p_i^k<0,
\]

when \(k\) is viewed as continuous for monotonicity. Thus:

| Metric | Event | Operational meaning |
|---|---|---|
| pass@\(k\) | at least one of \(k\) works | opportunity with sampling and an oracle selector |
| pass\(^{k}\) | all \(k\) work | repeatability and consistency |

A complete agent report should normally include pass@1, an opportunity curve, and a
reliability curve rather than selecting whichever makes the system look strongest.

## 5. Correlated retries and the beta-binomial model

Independence is often implausible. Repeated runs share the task, repository, harness,
prompt prefix, provider, and infrastructure. In SWE-agent, recovery changes after an
edit failure [yang-2024-swe-agent, PDF pp. 31-32, Figures 19-20]. The following is a
**proposed statistical model**, not a model fitted in the cited papers.

### 5.1 Exchangeable latent-difficulty construction

For a task/configuration cluster, let

\[
\Theta\sim\operatorname{Beta}(\alpha,\beta),
\qquad
X_j\mid\Theta\overset{\mathrm{iid}}{\sim}\operatorname{Bernoulli}(\Theta).
\]

Marginalizing the shared latent success propensity makes the \(X_j\) exchangeable and
positively correlated. If \(C_k=\sum_{j=1}^{k}X_j\), then:

\[
P(C_k=c)
=\binom{k}{c}
\frac{B(\alpha+c,\beta+k-c)}{B(\alpha,\beta)},
\qquad c=0,\ldots,k.
\]

**Derivation.**

\[
\begin{aligned}
P(C_k=c)
&=\int_0^1
\binom{k}{c}\theta^c(1-\theta)^{k-c}
\frac{\theta^{\alpha-1}(1-\theta)^{\beta-1}}
     {B(\alpha,\beta)}
\,d\theta\\
&=\binom{k}{c}
\frac{B(\alpha+c,\beta+k-c)}{B(\alpha,\beta)}.
\end{aligned}
\]

This is the beta-binomial distribution.

### 5.2 Mean, variance, and intraclass correlation

Let \(p=\alpha/(\alpha+\beta)\). Then:

\[
E[X_j]=p,
\qquad
\operatorname{Corr}(X_j,X_\ell)
=\rho=\frac{1}{\alpha+\beta+1}
\quad(j\ne\ell).
\]

**Proof.** Conditional independence gives

\[
\operatorname{Cov}(X_j,X_\ell)
=\operatorname{Var}(E[X_j\mid\Theta])
=\operatorname{Var}(\Theta)
=\frac{p(1-p)}{\alpha+\beta+1}.
\]

Since a marginal Bernoulli variable has variance \(p(1-p)\), division yields \(\rho\).
\(\square\)

Consequently,

\[
\operatorname{Var}(C_k)
=kp(1-p)\left[1+(k-1)\rho\right].
\]

The design effect is \(1+(k-1)\rho\), and the corresponding heuristic effective
sample size is

\[
k_{\mathrm{eff}}=\frac{k}{1+(k-1)\rho}.
\]

Treating correlated retries as \(k\) independent observations understates uncertainty.

### 5.3 Correlated opportunity and reliability

Using the rising factorial \((x)_k=x(x+1)\cdots(x+k-1)\):

\[
\begin{aligned}
P(C_k\ge1)
&=1-E[(1-\Theta)^k]
=1-\frac{B(\alpha,\beta+k)}{B(\alpha,\beta)}
=1-\frac{(\beta)_k}{(\alpha+\beta)_k},\\
P(C_k=k)
&=E[\Theta^k]
=\frac{B(\alpha+k,\beta)}{B(\alpha,\beta)}
=\frac{(\alpha)_k}{(\alpha+\beta)_k}.
\end{aligned}
\]

For \(k\ge2\), Jensen's inequality gives:

\[
E[(1-\Theta)^k]\ge(1-p)^k,
\qquad
E[\Theta^k]\ge p^k.
\]

Therefore positive latent heterogeneity produces more all-failure and all-success
clusters than an independent Bernoulli model:

\[
P(C_k\ge1)\le1-(1-p)^k,
\qquad
P(C_k=k)\ge p^k.
\]

Correlation lowers the opportunity gain from retries while increasing the mass at
both extremes. This is why an aggregate one-run rate is insufficient to reconstruct
either tail.

### 5.4 Parameterization and limitations

Given an estimated mean \(p\) and positive intraclass correlation \(\rho\):

\[
\kappa=\rho^{-1}-1,\qquad
\alpha=p\kappa,\qquad
\beta=(1-p)\kappa.
\]

The beta-binomial cannot represent negative correlation, ordered adaptation, changing
prompts, or a model that learns from tool feedback. Use a logistic mixed model for
multiple clustering factors or a Markov/state-space model for history-dependent
retries. In particular, the beta-binomial describes exchangeable overdispersion; it
does not prove that repeated attempts are causally correlated.

## 6. Imperfect verifiers, false positives, and PPV

### 6.1 Confusion model

For one candidate, define:

\[
\pi=P(X=1),\quad
s=P(Z=1\mid X=1),\quad
f=P(Z=1\mid X=0).
\]

Here \(s\) is verifier sensitivity and \(f\) is its false-positive rate. The observed
pass probability is:

\[
q=P(Z=1)=s\pi+f(1-\pi).
\]

The positive predictive value is:

\[
\operatorname{PPV}
=P(X=1\mid Z=1)
=\frac{s\pi}{s\pi+f(1-\pi)}.
\]

These are **standard probability identities derived here**. Their relevance is
empirical: broader tests found that some SWE-bench positive labels were false
[wang-2026-swe-solved-correctly, PDF p. 2], and resampling experiments show false
positives become operationally important when the verifier selects candidates
[stroebl-2026-inference-scaling-flaws, PDF pp. 4-7].

Even a small \(f\) can yield poor PPV when correct candidates are rare. For example,
if \(\pi=0.01\), \(s=0.9\), and \(f=0.01\), then:

\[
\operatorname{PPV}
=\frac{0.009}{0.009+0.0099}
\approx0.476.
\]

More than half of verifier-positive candidates are then wrong despite 99% specificity.

### 6.2 First-positive selection over at most \(K\) attempts

Assume independent, identically distributed candidates and stop at the first
verifier-positive candidate, or abstain after \(K\) verifier negatives. Let:

\[
a=s\pi,\qquad b=f(1-\pi),\qquad q=a+b.
\]

**Proposition 3 (standard result derived here, for \(q>0\)).**

\[
\begin{aligned}
P(\text{return correct by }K)
&=\frac{a}{q}\left[1-(1-q)^K\right],\\
P(\text{return incorrect by }K)
&=\frac{b}{q}\left[1-(1-q)^K\right],\\
P(\text{abstain})
&=(1-q)^K,\\
E[N_K]
&=\frac{1-(1-q)^K}{q},
\end{aligned}
\]

where \(N_K\) is the number of attempted candidates.

**Proof.** To return a true positive at attempt \(j\), the first \(j-1\) candidates
must be verifier-negative and the \(j\)th a true positive. Summing the geometric series:

\[
\sum_{j=1}^{K}(1-q)^{j-1}a
=\frac{a}{q}[1-(1-q)^K].
\]

Replace \(a\) with \(b\) for an incorrect return. Abstention requires \(K\) negatives.
Finally,

\[
E[N_K]=\sum_{j=1}^{K}P(N_K\ge j)
=\sum_{j=1}^{K}(1-q)^{j-1}.
\quad\square
\]

Conditional correctness of a returned candidate remains \(a/q=\operatorname{PPV}\);
increasing \(K\) reduces abstention but does not improve PPV in this homogeneous
model. The unconditional probability of returning a false positive increases toward
\(1-\operatorname{PPV}\).

When \(q=0\), no candidate can be verifier-positive: the policy always abstains and
\(E[N_K]=K\). These values are also the continuous limits of the formulas above.

### 6.3 Why finite optimal \(K\) requires more structure

Suppose a correct return yields benefit \(G>0\), an incorrect return incurs loss
\(L>0\), and each attempt costs \(c>0\). Under the stationary model:

\[
U(K)
=\frac{1-(1-q)^K}{q}
\left(Ga-Lb-c\right).
\]

Because the multiplier rises monotonically with \(K\), the optimum is a boundary:
use the maximum permitted \(K\) when \(Ga-Lb>c\), and do not sample when
\(Ga-Lb<c\). When \(Ga-Lb=c\), every \(K\) has the same zero utility. Thus there is
no strict interior optimum.

The finite, often small optimum observed in the inference-scaling study
[stroebl-2026-inference-scaling-flaws, PDF pp. 6-7, Figures 4-6] therefore implies
departures from the homogeneous model: heterogeneous task difficulty, a changing
conditional distribution after repeated failures, nonconstant verifier quality,
nonlinear costs, or a different selector. This is a useful diagnostic, not a defect in
the empirical finding.

## 7. Sequential stopping

### 7.1 History-dependent marginal rule

Let \(h_{j-1}\) be the complete history before attempt \(j\). Define:

\[
\begin{aligned}
a_j(h)&=P(X_j=1,Z_j=1\mid h),\\
b_j(h)&=P(X_j=0,Z_j=1\mid h),\\
c_j(h)&=\text{cost of the next attempt}.
\end{aligned}
\]

The one-step expected net value of continuing is:

\[
\Delta_j(h)=G\,a_j(h)-L\,b_j(h)-c_j(h).
\]

If future attempts cannot improve this value, a sufficient stopping rule is:

\[
\text{continue only while }\Delta_j(h)>0.
\]

In a task mixture, repeated verifier negatives update \(h\) toward tasks or trajectories
that are harder and may have greater false-positive risk. This formalizes the empirical
"easy tasks finish first" explanation
[stroebl-2026-inference-scaling-flaws, PDF p. 7, Section 4].

### 7.2 Bellman formulation

For general adaptive search, let \(A(h)\) be available actions: stop and return a
candidate, abstain, run a test, sample, revise, or escalate. A finite-horizon value
function is:

\[
V_t(h)=
\max_{a\in A(h)}
\left\{
r(h,a)-c(h,a)
+E[V_{t+1}(H')\mid h,a]
\right\},
\]

with terminal value determined by true deployment utility. This is a **proposed
decision model**. A harness implements an approximation to this policy whenever it
chooses whether to retry, branch, ask for approval, or stop.

The state must contain enough information to make continuation values meaningful.
Lost failure history, nonreplayable tool state, and stale workspace state violate the
Markov approximation; this connects sequential decision quality to authoritative
harness state.

### 7.3 Sequential probability ratio test for one candidate

Repeated candidates and repeated tests of one candidate are different. If a harness can
run independent diagnostic tests \(E_1,E_2,\ldots\) on a fixed candidate, define:

\[
\Lambda_m
=\sum_{\ell=1}^{m}
\log\frac{P(E_\ell\mid X=1)}{P(E_\ell\mid X=0)}.
\]

For desired type-I error \(\alpha_0\) and type-II error \(\beta_0\), Wald's approximate
boundaries are:

\[
A=\log\frac{1-\beta_0}{\alpha_0},
\qquad
B=\log\frac{\beta_0}{1-\alpha_0}.
\]

Accept when \(\Lambda_m\ge A\), reject when \(\Lambda_m\le B\), and acquire another
test otherwise. This is a **standard sequential-testing result**. Its guarantees depend
on correctly specified and sufficiently independent evidence distributions. Generated
tests that share blind spots do not provide the nominal evidence accumulation.

## 8. Reliability chains and recovery processes

### 8.1 Required-stage chain

Suppose success requires \(m\) stages:

\[
A_1\cap A_2\cap\cdots\cap A_m,
\]

such as context acquisition, localization, valid tool call, correct edit, execution,
verification, and artifact submission. Let \(r_\ell=P(A_\ell)\).

Under independence:

\[
R_{\mathrm{chain}}=\prod_{\ell=1}^{m}r_\ell.
\]

Without independence, two universal bounds are:

\[
\max\left(0,1-\sum_{\ell=1}^{m}(1-r_\ell)\right)
\le
P\left(\bigcap_{\ell=1}^{m}A_\ell\right)
\le
\min_\ell r_\ell.
\]

**Proof of the lower bound.** Let \(F_\ell=A_\ell^c\). By the union bound,

\[
P\left(\bigcup_\ell F_\ell\right)
\le\sum_\ell P(F_\ell)
=\sum_\ell(1-r_\ell).
\]

Taking complements gives the result; probabilities cannot be negative. The upper bound
follows because the intersection is contained in every \(A_\ell\). \(\square\)

If stages are independent with equal reliability \(r\), then \(R=r^m\). To attain a
target \(R_\star\), every equal-reliability stage must satisfy:

\[
r\ge R_\star^{1/m}.
\]

For \(R_\star=0.90\) over 20 stages, this requires \(r\ge0.99475\). Long workflows can
therefore be unreliable even when each primitive looks highly reliable.

### 8.2 Retryable stages

If a stage has independent per-attempt success probability \(r\) and at most \(k\)
attempts, its reliability is \(1-(1-r)^k\). This expression is inappropriate when a
failure changes the state. SWE-agent's reported recovery drop from 90.5% before an
edit failure to 57.2% after one failure directly demonstrates state dependence
[yang-2024-swe-agent, PDF pp. 31-32].

### 8.3 Absorbing Markov model

Let transient states encode progress and failure history, \(Q\) be the transient-state
transition matrix, \(\boldsymbol s\) the one-step transition probabilities to success,
and \(\boldsymbol\mu\) the initial row distribution. Then the probability of success by
step \(K\) is:

\[
P(\text{success by }K)
=\boldsymbol\mu
\left(\sum_{j=0}^{K-1}Q^j\right)
\boldsymbol s.
\]

When \(I-Q\) is invertible:

\[
P(\text{success by }K)
=\boldsymbol\mu
(I-Q^K)(I-Q)^{-1}
\boldsymbol s.
\]

This **proposed reliability model** can distinguish productive recovery, repeated
failure loops, premature submission, timeout, and abandonment. It is preferable to an
i.i.d. retry curve when traces reveal history-dependent transitions.

## 9. Correcting benchmark labels

### 9.1 Confusion-matrix inversion

Recall:

\[
q=s\pi+f(1-\pi)=f+(s-f)\pi.
\]

If \(s\) and \(f\) are known and \(s\ne f\), then:

\[
\pi=\frac{q-f}{s-f}.
\]

This is a **standard identification result derived here**. It is not usable from the
benchmark pass rate alone: \(q\) supplies one equation for three unknowns
\((\pi,s,f)\). An independent audit with a stronger reference procedure is required.

An audit only of verifier-positive outputs estimates PPV, not sensitivity. It can
estimate the proportion \(q\operatorname{PPV}\) of all evaluated cases that are both
declared and truly successful, but cannot identify false negatives. Many patch audits
therefore estimate score inflation more directly than complete latent accuracy.

### 9.2 Delta-method uncertainty

Let \(\widehat q\) be based on \(N\) benchmark tasks,
\(\widehat s\) on \(n_1\) known-success audit cases, and \(\widehat f\) on \(n_0\)
known-failure cases, with independent samples. Since:

\[
\frac{\partial\pi}{\partial q}=\frac1{s-f},
\quad
\frac{\partial\pi}{\partial s}=-\frac{\pi}{s-f},
\quad
\frac{\partial\pi}{\partial f}=-\frac{1-\pi}{s-f},
\]

the first-order variance is:

\[
\operatorname{Var}(\widehat\pi)
\approx
\frac{
q(1-q)/N
+\pi^2s(1-s)/n_1
+(1-\pi)^2f(1-f)/n_0
}{(s-f)^2}.
\]

Use the full covariance matrix when audit estimates share cases. The denominator shows
an identifiability problem: correction becomes unstable as \(s\) approaches \(f\).
Bootstrap intervals are often safer near boundaries; report unclipped and
probability-clipped estimates.

### 9.3 Correcting a selected audit

The OpenAI Verified audit selected tasks that a model failed inconsistently; its 59.4%
flaw rate is therefore conditional on selection, not a population estimate
[openai-2026-swebench-retirement, section "Background"]. If tasks are divided into
sampling strata \(h\), with known population weights \(W_h\), estimate:

\[
\widehat F=\sum_h W_h\widehat F_h.
\]

If item \(i\) has known audit inclusion probability \(\lambda_i\), a Hajek
inverse-probability estimator is:

\[
\widehat F_{\mathrm{IPW}}
=
\frac{\sum_{i\in\mathcal A}D_i/\lambda_i}
     {\sum_{i\in\mathcal A}1/\lambda_i},
\]

where \(D_i=1\) marks a flawed item and \(\mathcal A\) is the audited set. Without
stratum weights or inclusion probabilities, population correction is not identified.

## 10. Factorial mixed-effects design for harness effects

### 10.1 Experimental design

For model \(m\), harness \(h\), budget \(b\), environment \(e\), task \(i\) in
repository \(g\), and replicate \(r\), observe:

\[
Y_{g,i,m,h,b,e,r}\in\{0,1\}.
\]

A defensible design:

1. samples target repositories first and tasks within repositories;
2. evaluates every selected task under every randomized model-harness-budget cell;
3. repeats cells across seeds, API days, and infrastructure blocks;
4. holds verifier and task image fixed within a comparison;
5. records failures and abstentions rather than silently dropping them; and
6. reserves an untouched outer holdout for final claims.

Harness-Bench implements a useful \(6\times8\) configuration matrix while explicitly
warning that native harness components move together
[yao-2026-harness-bench, PDF pp. 6 and 9]. Thus its effects are configuration effects,
not effects of a single tool or prompt component.

### 10.2 Binary-outcome generalized linear mixed model

A starting model is:

\[
\begin{aligned}
\operatorname{logit}P(Y_{g,i,m,h,b,e,r}=1)
=\;&\mu+\alpha_m+\beta_h+\delta_b+\xi_e\\
&+(\alpha\beta)_{mh}
+(\alpha\delta)_{mb}
+(\beta\delta)_{hb}\\
&+u_g+v_{i(g)}+w_{ih},
\end{aligned}
\]

where:

- \(\alpha_m,\beta_h,\delta_b,\xi_e\) are fixed treatment effects;
- \((\alpha\beta)_{mh}\) is the model-harness interaction;
- \(u_g\sim N(0,\sigma_g^2)\) is a repository/task-family random intercept;
- \(v_{i(g)}\sim N(0,\sigma_i^2)\) is a task intercept nested in repository; and
- \(w_{ih}\) is an optional task-specific random harness slope.

This is a **proposed analysis model**. The interaction is substantively central: a
harness optimized for one model's edit dialect or context behavior may hurt another.
Cursor's report of patch versus string-replacement tools is direct practitioner
motivation [cursor-2026-improving-harness, section "Customizing the harness for
different models"].

### 10.3 Estimands and interpretation

Log-odds coefficients are not probability differences. For harnesses \(h\) and \(h'\),
report an average marginal contrast on the same task sample:

\[
\widehat{\operatorname{AME}}_{h,h'}
=\frac1N\sum_{i=1}^{N}
\left[
\widehat P(Y_i=1\mid h)
-\widehat P(Y_i=1\mid h')
\right].
\]

Also report cell-level predicted probabilities and model-harness interactions. A
single "average harness rank" can hide crossovers.

To isolate one component, randomize that component within a compatible harness while
holding all other fields fixed. Comparing complete native harnesses estimates a bundle
effect. It cannot support a causal statement such as "memory caused the gain."

### 10.4 Other outcomes

- Fit log cost or token count with a log-normal or gamma mixed model.
- Fit time-to-success with survival analysis, treating budget exhaustion as censoring
  only when censoring is plausibly noninformative.
- Fit failure categories with a multinomial mixed model.
- Model true success as latent when verifier sensitivity and specificity are
  separately estimated.

Multiplicity matters when many cells and mechanisms are compared. Predeclare primary
contrasts or control false discovery, and report all attempted configurations to avoid
winner's-curse selection.

## 11. Clustered and hierarchical bootstrap

### 11.1 Why rollout-level resampling is wrong

Rollouts on the same task share code, tests, prompt, and latent difficulty. Tasks from
the same repository share dependencies and conventions. Treating every rollout as an
independent row creates artificially narrow intervals.

The METR time-horizon study uses 10,000 hierarchical bootstrap samples over task
families, then tasks, then runs [kwa-2025-long-software-tasks, PDF p. 6, Section 3.2].
That hierarchy is directly transferable.

### 11.2 Paired hierarchical bootstrap algorithm

For each bootstrap replicate:

1. Sample top-level repositories or task families with replacement.
2. Within each selected top-level cluster, sample tasks with replacement.
3. For each sampled task, retain every compared treatment cell so contrasts remain
   paired.
4. If trial stochasticity is part of the estimand, resample rollouts within each
   retained task-treatment cell.
5. Recompute the complete statistic: pass rate, marginal contrast, Pareto point, or
   time-horizon fit.
6. Repeat \(B\) times and use percentile or bias-corrected intervals.

For a paired accuracy contrast:

\[
\widehat\Delta
=\frac1N\sum_i
\left(\overline Y_{i,A}-\overline Y_{i,B}\right).
\]

Resample the task-level pairs, not the \(A\) and \(B\) outcomes independently.

### 11.3 What the bootstrap cannot repair

Bootstrap intervals quantify variation under the observed sampling design. They do not
correct:

- a nonrepresentative benchmark;
- contaminated tasks;
- broken graders;
- selective reporting of configurations;
- unobserved infrastructure differences; or
- a shifted deployment distribution.

With very few top-level clusters, ordinary cluster bootstrap can itself be unstable.
Report the number of independent clusters and supplement it with cluster-robust or
small-sample sensitivity analysis.

## 12. Cost and Pareto analysis

### 12.1 Repriceable cost accounting

For rollout \(r\), record:

\[
C_r
=\lambda_{\mathrm{in}}T_{\mathrm{in},r}
+\lambda_{\mathrm{out}}T_{\mathrm{out},r}
+C_{\mathrm{tool},r}
+C_{\mathrm{compute},r}
+C_{\mathrm{human},r}.
\]

Report token and resource quantities separately from prices because prices change.
This recommendation is **source-reported**
[kapoor-2024-agents-matter, PDF pp. 6-7, Section 4].

Useful cost estimands include:

\[
\overline C=\frac1N\sum_i C_i,
\qquad
C_{\mathrm{per\ true\ success}}
=\frac{\sum_i C_i}{\sum_i X_i}.
\]

If \(X\) is not directly observed, use audited true-positive counts or explicitly label
the denominator "verifier-positive," not "successful."

### 12.2 Pareto dominance

For configuration \(\theta\), let \(A(\theta)\) be true accuracy and \(C(\theta)\)
expected cost. Configuration \(\theta_1\) dominates \(\theta_2\) when:

\[
A(\theta_1)\ge A(\theta_2),
\qquad
C(\theta_1)\le C(\theta_2),
\]

with at least one strict inequality. Only nondominated configurations belong to the
Pareto frontier.

AI Agents That Matter reports simple baselines on the frontier relative to several
named HumanEval agents and large cost differences at similar accuracy
[kapoor-2024-agents-matter, PDF pp. 3-4, Figure 1].

### 12.3 Convexification by randomized policies

**Proposition 4 (source argument formalized here).** If a harness may choose
configuration 1 with probability \(\lambda\) and configuration 2 otherwise before a
task, then the expected operating point is:

\[
\left(
\lambda C_1+(1-\lambda)C_2,\;
\lambda A_1+(1-\lambda)A_2
\right).
\]

**Proof.** Both cost and binary success expectation are linear under the mixture law.
\(\square\)

Thus randomized routing makes convex combinations feasible. The efficient set is the
nondominated boundary of the feasible convex hull: equivalently, the lower boundary
when cost is plotted as a function of required accuracy, or the upper-left boundary
when cost is horizontal and accuracy is vertical. This argument appears in AI Agents
That Matter
[kapoor-2024-agents-matter, PDF p. 3, footnote 2].

### 12.4 Fixed cost, variable cost, and break-even

Let configuration \(\theta\) require one-time optimization cost \(F_\theta\) and
per-task variable cost \(v_\theta\):

\[
C_\theta(n)=F_\theta+n v_\theta.
\]

If \(F_A>F_B\) but \(v_A<v_B\), configuration \(A\) becomes cheaper after:

\[
n^\star=\frac{F_A-F_B}{v_B-v_A}.
\]

The joint-optimization experiment reports a break-even near 1,350 HotPotQA tasks
[kapoor-2024-agents-matter, PDF pp. 5-6]. That number is experiment-specific; the
equation is general.

### 12.5 Optimization formulations

Equivalent formulations include:

\[
\max_{\theta} A(\theta)
\quad\text{subject to}\quad C(\theta)\le C_{\max},
\]

or:

\[
\max_{\theta}\left[A(\theta)-\lambda C(\theta)\right].
\]

For safety-critical work, replace raw accuracy with expected utility that assigns
larger loss to false-positive success:

\[
\max_\theta
\left[
G\,P(\mathrm{TP}\mid\theta)
-L\,P(\mathrm{FP}\mid\theta)
-\lambda C(\theta)
\right].
\]

Optimization and final evaluation must use different task sets. Otherwise harness
search converts the benchmark into training data, as both the academic holdout critique
and practitioner hill-climbing report warn
[kapoor-2024-agents-matter, PDF pp. 7-9;
langchain-2026-better-harness, section "Building learning systems that generalize"].

## 13. Time-horizon logistic models

### 13.1 Source-reported model

The METR study assigns task \(i\) a human completion time \(t_i\) and fits, for agent
\(a\):

\[
P(Y_{ia}=1)
=\sigma\left(\beta_a[\log h_a-\log t_i]\right),
\]

where \(\sigma(x)=1/(1+e^{-x})\), \(h_a\) is the 50% completion-time horizon, and
\(\beta_a\) controls slope [kwa-2025-long-software-tasks, PDF pp. 5-6, Section 3.1].
The horizon interpretation and the comparisons below assume \(\beta_a>0\).

Because \(\sigma(0)=1/2\), \(P(Y=1)=1/2\) exactly when \(t_i=h_a\). The following
quantile transformation is **derived here** from the source-reported model. The task
duration associated with target success probability \(q\) is:

\[
t_{a,q}
=h_a\exp\left[-\frac{\operatorname{logit}(q)}{\beta_a}\right].
\]

For \(q>1/2\), this reliable horizon is shorter than \(h_a\). Empirically, the paper's
80% horizons are four to six times shorter than its 50% horizons
[kwa-2025-long-software-tasks, PDF p. 7, Section 3.2.1].

### 13.2 Trend and doubling time

The paper fits a log-linear release-date trend. Writing that **source-reported model**
as:

\[
\log h_a=\gamma_0+\gamma_1d_a+\varepsilon_a,
\]

where \(d_a\) is measured in days, solving for a factor-of-two increase gives the
following **derived result** when \(\gamma_1>0\):

\[
D=\frac{\log2}{\gamma_1}.
\]

The paper reports \(D=207\) days with hierarchical-bootstrap 95% interval 166-240
days, and an o3 50% horizon around 110 minutes
[kwa-2025-long-software-tasks, PDF p. 6, Section 3.2].

### 13.3 Identification and extrapolation limits

This model assumes that human duration is a meaningful one-dimensional difficulty
coordinate. Threats include:

- errors and group dependence in human time measurement;
- task-family selection;
- binarization of continuous task scores;
- a discontinuity between very short atomic tasks and longer tasks;
- simultaneous evolution of models and harnesses;
- contamination and benchmark-specific adaptation;
- different notions of "human": maintainers and contractors can differ sharply; and
- extrapolation beyond observed task lengths and dates.

The paper reports contractors taking 5-18 times as long as maintainers on five internal
pull requests and worse model performance on "messier" tasks
[kwa-2025-long-software-tasks, PDF p. 7, Section 4]. Therefore \(h_a\) is relative to
a reference population and task distribution, not a universal amount of autonomous
work. Forecasts to month-long work are conditional extrapolations, not theorem
consequences.

### 13.4 Recommended extension

A harness-aware hierarchical model would be:

\[
\operatorname{logit}P(Y_{iamh}=1)
=\beta\left[
\eta_m+\zeta_h+(\eta\zeta)_{mh}
-\log t_i
\right]
+u_{g(i)}+v_i,
\]

where model, harness, and their interaction receive separate terms. Repeated
measurements across calendar time should keep a stable reference harness or explicitly
model harness changes. Otherwise a trend in \(h\) measures the frontier system, not the
base model.

## 14. Minimum mathematical reporting protocol

For each claimed harness improvement:

1. Define the target task population and independent sampling unit.
2. Publish the full configuration tuple \(\mathcal C\).
3. Report pass@1, pass@\(k\), and pass\(^{k}\) with their exact sampling and selection
   policies.
4. Estimate verifier sensitivity, false-positive rate, and PPV on a probability audit
   sample; distinguish test pass from true success.
5. Use balanced, paired model-harness-budget cells and test the model-harness
   interaction.
6. Resample repositories/task families before tasks and rollouts when computing
   uncertainty.
7. Report token, tool, compute, latency, human, and dollar costs separately.
8. Show the accuracy-cost or utility-cost Pareto frontier and simple retry/escalation
   baselines.
9. Preserve all attempted configurations, traces, exclusions, timeouts, and
   infrastructure failures.
10. Optimize on one split and make final claims on a private or rotating outer holdout.
11. Repeat on multiple API days or infrastructure blocks.
12. State which assumptions are empirical checks, modeling conveniences, or untested
    extrapolations.

## 15. Proof and provenance ledger

| Result | Status | Primary empirical motivation |
|---|---|---|
| unbiased pass@\(k\) estimator | source-reported; proof expanded here | [chen-2021-codex-passk, PDF p. 3] |
| unbiased pass\(^{k}\) estimator | standard result derived here | [yao-2024-tau-bench, PDF pp. 2 and 7] |
| beta-binomial retry model and Jensen comparisons | proposed model; derivations here | clustered reliability in tau-bench and history dependence in SWE-agent |
| verifier PPV and label inversion | standard Bayes/confusion-matrix result derived here | SWE-bench patch audits |
| first-positive stopping formulas | standard geometric result derived here | verifier-selected resampling |
| finite-\(K\) diagnostic | derived here; empirical finite optima are source-reported | [stroebl-2026-inference-scaling-flaws, PDF pp. 6-7] |
| Bellman and SPRT stopping formulations | standard/proposed application | adaptive harness control |
| reliability product and union bounds | standard results proved here | long multi-stage traces |
| absorbing Markov recovery model | proposed model | SWE-agent edit recovery |
| stratified/IPW benchmark-audit correction | standard survey-sampling application | selected Verified audit |
| factorial logistic mixed model | proposed analysis design | Harness-Bench and HAL |
| hierarchical paired bootstrap | standard resampling design | METR's three-level bootstrap |
| Pareto dominance and randomized convexification | source argument formalized here | [kapoor-2024-agents-matter, PDF pp. 3-6] |
| fixed/variable break-even equation | standard result derived here | joint optimization in AI Agents That Matter |
| time-horizon logistic model | source-reported; quantile and doubling derivations here | [kwa-2025-long-software-tasks, PDF pp. 5-7] |

## 16. Source key

| Source ID | Local or canonical source |
|---|---|
| chen-2021-codex-passk | [local PDF](../papers/academic/chen-2021-codex-passk.pdf) |
| yang-2024-swe-agent | [local PDF](../papers/academic/yang-2024-swe-agent.pdf) |
| kapoor-2024-agents-matter | [local PDF](../papers/academic/kapoor-2024-agents-matter.pdf) |
| wang-2026-swe-solved-correctly | [local PDF](../papers/academic/wang-2026-swe-solved-correctly.pdf) |
| zhu-2025-rigorous-agentic-benchmarks | [local PDF](../papers/academic/zhu-2025-rigorous-agentic-benchmarks.pdf) |
| yao-2024-tau-bench | [local PDF](../papers/academic/yao-2024-tau-bench.pdf) |
| stroebl-2026-inference-scaling-flaws | [local PDF](../papers/academic/stroebl-2026-inference-scaling-flaws.pdf) |
| kwa-2025-long-software-tasks | [local PDF](../papers/academic/kwa-2025-long-software-tasks.pdf) |
| kapoor-2026-hal | [local PDF](../papers/academic/kapoor-2026-hal.pdf) |
| yao-2026-harness-bench | [local PDF](../papers/academic/yao-2026-harness-bench.pdf) |
| openai-2026-swebench-retirement | <https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/> |
| cursor-2026-improving-harness | <https://cursor.com/blog/continually-improving-agent-harness> |
| langchain-2026-better-harness | <https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals> |
