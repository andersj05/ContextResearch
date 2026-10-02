# Parent-memory spectrum and an unsigned-decoder support transition

October 1, 2026. **Local analytic result with exact finite supporting
certificates.** Claim C65. External correctness and publication priority review
remain open. This is mathematical research, with zero new model calls or natural
workflow episodes; it does not measure token, task-success or cost gains.

The [new package](../experiments/dependency_memory/rate_spectrum/README.md)
extends the rate-two result in two ways. First, the fixed unsigned decoder's
entire positive-slope supporting optimization reduces to one scalar, with a
unique transition between two and eight supported response words. Second,
eight additional rational parent rates have all-decoder asymptotic distortion
intervals narrower than 2e-11. Every point checks all 1,679,616 decoder tables,
including noncomplementary and repeated endpoints. The unrestricted curve at
untested rates remains unproved; these points are not finite codebooks.

## 1. Unchanged information contract

For k independent uniform four-bit blocks X, the parent has at most
2^floor(k*r) states and is formed before independent uniform block R and
omission O. The updater receives only parent,R,O and emits one bit Z, then
discards the parent. The final decoder receives Z,R,O,J for uniform J != O.
Source rereads, archives, session history and source-selected public tables are
absent. Public codebooks and decoder tables are fixed before X.

For each block, a final table g contains four unordered pairs of three-bit
prediction words, repeats allowed. There are 36^4 tables. Its decision word
A in {0,1}^4 lists the four possible updater responses. This is an analysis
variable/codeword symbol, not four additional bits supplied to the final decoder.
Let L_g(x,a) count disagreements on all twelve omission/query routes.

The [existing reduction](DECODER_COMPLETE_FRONTIER_2026-09-21.md#1-information-contract-and-complete-decoder-reduction)
allows arbitrary joint parent encoders and heterogeneous tables across blocks:
sum_r I(X_r;A_r) <= H(M) <= floor(k*r). A common supporting inequality
I(X;A)+s E L_g >= C therefore gives D_k(floor(k*r)) >= (C-r)/(12*s)
for every k. Independent random tapes can be fixed; they are not extra memory.

## 2. The unsigned family's scalar optimization

Fix each omission's endpoints to (000,111). Put t=2^(-s), 0<t<1.
The supporting objective equals

\[
C_u(s)=\min_q -\frac1{16}\sum_x\log_2\sum_a q_a t^{L_u(x,a)}.
\]

This is the established finite-alphabet rate-distortion formulation. Source
permutations and complementation preserve this decoder's loss. Convexity lets us
average q over those symmetries without increasing the objective. Its masses
are consequently uniform within three classes: two constant words, six balanced
weight-two words, and eight odd-weight words.

Source weights 0/4, 1/3 and 2 have masses w=(1/8,1/2,3/8). Average kernels for
the three reproduction classes are respectively

\[
\begin{aligned}
A&=((1+t^{12})/2,\ (t^3+t^9)/2,\ t^6),\\
B&=(t^6,\ (t^5+t^7)/2,\ (t^4+4t^6+t^8)/6),\\
E&=((t^3+t^9)/2,\ (3t^4+2t^6+3t^8)/8,\ (t^5+t^7)/2).
\end{aligned}
\]

These formulas are independently checked by executing all twelve routes for
each of the sixteen sources and sixteen decision words.

### Removing odd-weight words for every positive slope

Set alpha=(1-t+t^2)/(1+t)^2. It lies in (0,1), and the classwise difference
alpha*A+(1-alpha)*B-E is

\[
\left(
\frac{(1-t^3)^2(1-t)^2(1+t+2t^2+4t^3+2t^4+t^5+t^6)}{2(1+t)^2},
\frac{t^3(1-t)^4(4+t+4t^2)}8,
0\right).
\]

The first two entries are strictly positive. Replacing any positive odd mass
by this mixture increases the corresponding partition values and strictly
decreases the objective. Thus no symmetric optimum has odd mass. This is a
domination argument specific to the unsigned loss, not an all-decoder theorem.

Let p be the total balanced mass. Then q_0=q_15=(1-p)/2 and each balanced word
has mass p/6. With z_i=A_i+(B_i-A_i)*p, maximize H(p)=sum_i w_i log2(z_i).
It is strictly concave for 0<t<1. Writing b_i=B_i-A_i, its derivative has the
sign of sum_i w_i b_i/z_i; the interior solution satisfies

\[
\sum_{i=0}^2 w_i b_i\prod_{j\ne i}(A_j+b_jp)=0.
\]

This is a quadratic equation. Its unique root in (0,1), when present, gives the
optimal p. The supporting objective and Gibbs channel then characterize this
fixed decoder's nontrivial rate-distortion branch parametrically.

### A unique support transition

For u=t^2, define

\[
P(u)=1-11u-u^2-4u^3-2u^4-4u^5-u^6-11u^7+u^8.
\]

Up to the positive factor 1/ln(2), the derivative H'(0) is

\[
\frac{(1-u)^2(1+u)P(u)}{16u(1+u^3)(1+u^6)}.
\]

The derivative at p=1 is strictly negative: its negative has numerator
(1-u)^2*(1+6u+20u^2+42u^3+20u^4+6u^5+u^6), with positive denominator
16u^3*(1+4u+u^2). These identities are checked by exact polynomial coefficients.

To prove P has precisely one root in (0,1), put u=v/(1+v). Then

\[
(1+v)^8P(v/(1+v))=
1-3v-50v^2-185v^3-352v^4-401v^5-283v^6-128v^7-32v^8.
\]

This polynomial decreases strictly from one to minus infinity on v>0.
Consequently there is a unique t_*; p=0 for t>=t_*, and 0<p<1 for t<t_*.
Rational bisection certifies

\[
0.299826862327<t_*<0.299826862328.
\]

For the two-word Gibbs channel, complement symmetry makes its output marginal
exactly (1/2,1/2). Its distortion increases with t, since the derivative of
conditional expected loss is conditional variance divided by t. Its information
decreases with t: I'(t)=log2(t)*(E L)'(t). Evaluating both rational endpoints with
outward logarithms therefore encloses the **restricted** transition in

- parent information: [0.620690001029, 0.620690001030] bits per block;
- average bit error: [0.312681553947, 0.312681553948].

Below this information rate, the unsigned optimum uses only two constant words;
above it, it also uses six balanced words. Support size is not the parent's
finite alphabet size or an extra channel to the final decoder. This does not
alter the existing finite exact 3k-bit requirement for error 1/4.

## 3. Eight all-decoder supporting certificates

The [saved result](../experiments/dependency_memory/results/rate_spectrum_2026-10-01.json)
uses t in {1/100,1/20,3/20,1/4,2/5,3/5,4/5,19/20}. The unsigned q is a nearby
rational version of the scalar optimum; every other orbit uses the existing
explicit nearest-word output marginal. That marginal need not be optimal.

The unchanged exact dual computes an upper bound G on product_x(z_x)*gamma^16,
where gamma=max_a E_x[t^L(x,a)/z_x]. Thus every channel has objective at least
-log2(G)/16. Integer products compare all 4,751 orbit representatives, covering
all 1,679,616 tables at each point. The unsigned orbit has the largest dual
product at every point, and every other orbit's objective lower bound strictly
exceeds the unsigned witness's free-objective upper bound. This certifies the
unsigned decoder's optimal supporting family at these eight slopes, including
channels assigning mass outside the witness's support.

There are 38,008 orbit/point checks. Counts and digests are diagnostics; the
regenerated integer inequalities, complete orbit cover and analytic reduction
establish the result. The old C34 two-bit certificate is unchanged.

At each point, choose the rational rate r strictly above the Gibbs channel's
certified information upper bound, by rounding to the next 1e-10 grid point.
Standard fixed-length rate-distortion achievability at an intermediate rate
gives codebooks fitting floor(k*r) bits for sufficiently large k. Concatenation
makes k*D_k(floor(k*r)) subadditive, so the limit exists. The universal supporting
bound supplies the lower endpoint for every k; the explicit rational channel
supplies the asymptotic upper endpoint.

| Parent rate, bits/block | Certified limiting average bit error | Unsigned support |
|---:|---|---:|
| 0.0165926507 | [0.4622655556512390, 0.4622655556637469] | 2 |
| 0.2134351417 | [0.3724619398456761, 0.3724619398593340] | 2 |
| 0.4907596121 | [0.3239155693912685, 0.3239155693954863] | 2 |
| 0.6058375138 | [0.3135219199215007, 0.3135219199226038] | 2 |
| 0.9726441913 | [0.2969469397286971, 0.2969469397292819] | 8 |
| 1.7464668030 | [0.2691674660155883, 0.2691674660163260] | 8 |
| 2.4100909748 | [0.2522903157473951, 0.2522903157487049] | 8 |
| 2.5406225816 | [0.2500924641065645, 0.2500924641067975] | 8 |

These are rational rates with strict coding slack, not rounded versions of a
claim at rates 0.5,1,1.5,2.5. All interval widths are below 2e-11. They are
mathematical enclosures, not confidence intervals or empirical precision.

## 4. Discovery, prior work and validation scope

Six bounded floating probes preceded the derivation; the two smaller-t points
were added afterward. The [raw summaries and original script](../experiments/dependency_memory/rate_spectrum/auxiliary/README.md)
preserve that post-hoc mathematical discovery. Neither convergence nor a float
rank is trusted. The final certificate uses only standard-library exact integer
and rational arithmetic; numerical weights and NumPy are not inputs.

On October 1, the existing primary citation Polyanskiy and Wu, MIT 6.441 Chapter
25, Section 25.2, Theorem 25.2 and support-condition remarks, pp. 258–259, was
reread from [the original course notes](https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/5721b7df786b416dadad7c7bb3364d00_MIT6_441S16_chapter_25.pdf).
Supporting objectives, iterative evaluation and careful treatment of support
are established rate-distortion tools. The specific class domination,
transition polynomial and eight complete-table bounds are local calculations;
the methods are not claimed as new. This bounded rereading is not a new full
source review, replication or publication-priority conclusion.

Six independent tests check direct source/query routes, exact positive-factor
identities, transformed coefficients, root/optimizer brackets, constant Gibbs
marginals and the dual inequality on separately constructed channels using
Decimal logarithms. They also regenerate all eight source-bound certificates.

The remaining mathematical step is a proof or counterexample for all-decoder
optimality between the checked slopes, or efficient finite codes approaching
these limits. The empirical next step remains a separately frozen new cohort
with strong source-analysis/direct/cached controls and actual variable-command
intake. More calls on the inspected dispatch classifier are not needed to
establish these mathematical statements.
