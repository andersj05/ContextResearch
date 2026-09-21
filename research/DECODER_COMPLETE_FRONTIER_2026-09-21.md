# A certified rate-two frontier allowing every decoder

September 21, 2026. **Local analytic result with a complete finite,
exact-arithmetic certificate. External correctness and publication priority
remain unreviewed.** This phase makes no model requests. Claim C34 in the
[claim register](../paper/claims.csv) records the result and its limits.

## Result and why it changes the research question

In the existing delayed-query block model,

\[
\boxed{0.2618989799 < \lim_{k\to\infty}D_k(2k) < 0.2618989801.}
\]

The lower inequality also holds for **every finite k >= 1**, with arbitrary
joint encoding and arbitrary final decoder pairs. The upper inequality is
an asymptotic existence result. No finite code at that error is supplied.

This replaces the previously certified interval
[129/512, 101/384], approximately [0.251953125, 0.263020833]. Its width is
now 2e-10 in error probability, or 2e-8 percentage points. The irreducible
excess above the isolated child optimum is approximately **1.189898
percentage points**, over six times the previous uniform guarantee of
0.1953125 percentage points. Joint coding improves on the one-block
28.125% error, but cannot approach 25% at two parent bits per block.

This is a tightly certified value, **not an exact closed-form optimum**.
The separate 283/1024 two-block construction and the 2.548794941-bit
vanishing-excess threshold remain valid. The exact two-block optimum and
efficient finite-length encoders remain open. The claim concerns bits and
average bit error, not model tokens, task success, or dollars.

## 1. Information contract and complete decoder reduction

The source is k independent uniform four-bit blocks X^(r). A parent M
with at most 2^(2k) states is formed before independent uniform block R
and omission O are revealed. The updater then replaces M by one bit Z.
Only afterward is the uniform coordinate J != O revealed. The final
decoder has Z,R,O,J, with no parent, archive, source reread, or other
instance-dependent channel. Public codebooks are fixed before the source.

For a fixed block, each omission's final decoder is a pair of three-bit
prediction words (v_o^0,v_o^1). There are 64 ordered pairs. Exchanging the
two labels only relabels the updater's output for that omission, leaving
36 unordered pairs **including repeated endpoints**. Thus 36^4 = 1,679,616
tables cover all deterministic final decoders. Noncomplementary and
constant pairs remain included; they are not assumed inferior a priori.

Fix a table g. Define a decision word A in {0,1}^4 listing the updater's
four potential child bits, one per omission. For a source x and word a,

\[
L_g(x,a)=\sum_{o=0}^3\sum_{j\ne o}
  {\bf1}\{x_j\ne v_o^{a_o}(j)\},\qquad d_g=L_g/12.
\]

For any joint parent encoder, A_r is a deterministic function of M and
the fixed index r. It is an analysis variable, not four bits additionally
available at final decoding. Its marginal channel P(A_r|X^(r)) exists
even when M jointly depends on every source block. Data processing and
source independence give

\[
\sum_r I(X^{(r)};A_r)\le \sum_r I(X^{(r)};M)
\le H(M)\le 2k. \tag{1}
\]

Different blocks may use different fixed tables. The actual average loss
is (12k)^(-1) sum_r E L_{g_r}(X^(r),A_r). Consequently a common local
inequality I(X;A)+s E L_g >= C, valid for **every** table and channel,
implies

\[
D_k(2k)\ge \frac{C-2}{12s}. \tag{2}
\]

No independent encoding or equal information allocation is assumed.
Independent randomization cannot improve the bound: fix a complete random
tape with loss no greater than the average; the hard capacity remains valid.
A decoder table chosen using uncharged source information would violate
the contract and is not an allowed form of randomization.

## 2. A dual inequality that requires no trusted optimizer

Choose rational 0<t<1, write s=-log2(t), and let W_xa=t^(L_g(x,a)). For
any probability vector q over the 16 decision words, set

\[
z_x=\sum_a q_a W_{xa},\qquad
\gamma=\max_a\frac1{16}\sum_x\frac{W_{xa}}{z_x}.
\]

All z_x are positive even if some q_a are zero. Every channel P(A|X)
satisfies

\[
I(X;A)+s\,\mathbb E L_g(X,A)
\ge -\frac1{16}\sum_x\log_2 z_x-\log_2\gamma. \tag{3}
\]

**Proof.** Let pi be the channel's output marginal. Nonnegativity of
KL divergence to the normalized vector pi_a W_xa gives
I+s E L >= -(1/16) sum_x log2(sum_a pi_a W_xa). Write that last inner sum
as z_x times its ratio to z_x. Jensen's inequality bounds the average
logarithm of the ratio by
log2(sum_a pi_a [(1/16)sum_x W_xa/z_x]) <= log2(gamma). This proves (3),
including channels with zeros in their support.

The inequality is standard rate-distortion dual reasoning, derived here
to make the computational certificate self-contained. q need not be
optimal, and convergence of a numerical iteration is not an assumption.

For achievability, the rational Gibbs channel

\[
P_q(a|x)=\frac{q_a t^{L_g(x,a)}}{z_x} \tag{4}
\]

has exact rational distortion. Its information obeys

\[
I(X;A)\le -\frac1{16}\sum_x\log_2z_x
                  +12\,\mathbb E d_g(X,A)\log_2t. \tag{5}
\]

The difference between the right side and I is KL(P_A || q), so (5)
does not silently assume q equals the resulting marginal.

## 3. Exhaustive coverage and exact integer witnesses

Use

```text
t = 116328784 / 1000000000 = 7270549 / 62500000.
```

Source-coordinate permutations and independent coordinate bit flips
preserve the uniform source and the uniform omission/query loss. Acting
simultaneously on all four decoder pairs gives a group of size 24*16=384.
Child-label swaps introduced by sorting pairs only permute A's columns.

The enumerator visits each still-unseen table in lexicographic integer
order, explicitly generates its orbit, checks that the orbit is disjoint
from all earlier orbits, and marks every member. The resulting **4,751
orbits cover all 1,679,616 tables**. A separate Burnside fixed-point count
in the tests obtains 384*4751 without enumerating these orbits. Other tests
verify the group action using coordinate dictionaries and actual query
predictions, independently of the generator's packed-bit loss formula.

For the all-unsigned table, whose four pairs are (000,111), use weights
w_a with total Q=3*10^15:

| Decision word a | Integer weight w_a |
|---|---:|
| 0000 or 1111 | 1009489803807342 each |
| Any of the six weight-two words | 163503398730886 each |
| Weight one or three | 0 |

For every other orbit, a simpler witness suffices: on each x choose
uniformly among words minimizing L_g(x,a), and take its output marginal
as q. Branch decisions minimize separately, so a tie set has 1,2,4,8,or
16 elements. All these q values have denominator 256. This rule is an
explicit witness construction, not an optimality assumption.

To eliminate numerical error, let t=u/v in reduced form and define

\[
K_{xa}=u^{L_g(x,a)}v^{12-L_g(x,a)},\quad
Z_x=\sum_a w_a K_{xa},\quad C_0=2^{160},
\]

\[
S=\max_a\sum_x\left\lceil\frac{C_0 K_{xa}}{Z_x}\right\rceil.
\]

Then gamma <= Q S/(16 C_0) and

\[
\left(\prod_x z_x\right)\gamma^{16}
\le G_g:=\frac{(\prod_x Z_x)S^{16}}{(16C_0v^{12})^{16}}. \tag{6}
\]

The denominator of G_g is common to every orbit, regardless of Q.
Comparing its integer numerators therefore identifies the largest upper
bound without logarithms or floating-point arithmetic. The unsigned
orbit is largest. Every other orbit satisfies G_g < 2^(-190), checked
by integer multiplication, so its supporting objective exceeds 95/8.
This separation is for the chosen supporting objective; we do not assert
that unsigned decoders are optimal at every rate.

The [certificate](../experiments/dependency_memory/results/decoder_frontier_certificate.json)
records orbit sizes, the extremal representatives, exact witness
parameters, and a digest of every orbit's integer comparison numerator.
Routine validation regenerates the entire enumeration and certificate;
matching the counts or digest alone is not the proof.

## 4. Certified arithmetic and the resulting bounds

For the largest G, (3) gives C >= -log2(G)/16. Logarithms are bounded
with integer interval arithmetic, not ordinary machine logarithms.
Normalize a positive rational as 2^e*y with 1<=y<2, set z=(y-1)/(y+1),
and expand ln y = 2 sum_{j>=0} z^(2j+1)/(2j+1). At z<=1/3 the remainder
after N terms is at most 3^(-2N). The code uses 100 terms, rounds each
operation outward on a 2^192 grid, and divides by independently bounded
ln 2 with the correct endpoint order. Tests also compare against Python's
separate high-precision Decimal logarithm implementation.

Outward rounded certified enclosures are:

| Quantity | Lower endpoint | Upper endpoint |
|---|---:|---:|
| Universal supporting-objective lower bound C | 11.7543331549651500 | 11.7543331549651501 |
| Conservative all-k lower bound from (2) | 0.2618989799084461 | 0.2618989799084462 |
| Distortion of the rational Gibbs channel | 0.2618989800764624 | 0.2618989800764625 |
| Upper bound on that channel's information | 1.9999999937422941 | 1.9999999937422942 |

The first two rows enclose the **computed lower bounds**, not the optimum
itself. The fourth row encloses an upper bound on information, not a
claim that the exact mutual information equals that expression.

Equation (2) proves D_k(2k)>0.2618989799 at every k. The explicit channel's
information is strictly below two, with about 6.26e-9 bits of certified
slack. Standard finite-alphabet fixed-length rate-distortion achievability
at any intermediate rate supplies deterministic codebooks fitting 2k
parent bits for sufficiently large k. A codeword specifies k decision
words; the updater emits only its selected block's omission bit. Thus
limsup D_k(2k)<=0.2618989800764625<0.2618989801. The already established
concatenation/subadditivity argument supplies existence of the limit.

The tiny rate slack may require very long codes. No finite blocklength,
efficient encoder, or engineering advantage is inferred from it. The
width of the certified interval should not be mistaken for empirical
measurement precision or a confidence interval.

## 5. Literature and candidate novelty

Primary sources checked September 21, 2026:

- Polyanskiy and Wu, [MIT 6.441 Chapter 25](https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/5721b7df786b416dadad7c7bb3364d00_MIT6_441S16_chapter_25.pdf),
  Section 25.2, Theorem 25.2 and its support-condition remarks, pages
  258-259. This supplies established supporting-objective and optimality
  reasoning. The earlier Chapter 24 reading supplies coding achievability.
  We do not claim a new rate-distortion duality theorem. [@polyanskiywu2016coding]
- Dupuis, Yu, and Willems, [ISIT 2004 presentation](https://www.comm.toronto.edu/~weiyu/ab_isit04.pdf),
  title page and slides 11-16. Their strategy alphabet represents a whole
  response function to side information; slides 12-13 optimize a supporting
  rate-distortion objective. This predates our branch-decision-word
  representation. These are primary presentation slides, not a reviewed
  journal proof. [@dupuis2004strategies]
- Basu, Seo, and Varshney, [arXiv:2204.02586v2](https://arxiv.org/html/2204.02586v2),
  Sections II-A4 and V-B, Theorems 9-10, revisited for the cascade access
  contract. A codec re-encoding only its received message is established.
  Their checked setup uses long-block descriptions of two function
  sequences, not the present single child bit formed after R,O and before
  J. This is our model comparison, not a claim made by the source. [@basu2022hypergraph]

**Candidate contribution:** a completely enumerated, quantitatively sharp
composition penalty for this specified delayed-query family, with a
converse allowing every decoder and arbitrary joint encoding. The
contribution is the particular result and its checkable certificate, not
Shannon strategies, rate-distortion coding, convex duality, symmetry
reduction, or information direct sums. This phase resolves the previous
wide-interval uncertainty to a certified numerical interval and materially
strengthens the all-k gap.

Targeted searches for delayed-query one-bit compression, strategy-based
rate-distortion formulations, and this numerical value did not identify
the same example in the material reviewed. Search absence is not evidence
of priority, and no external expert has reviewed this result. A publication
novelty claim still requires comparison with equivalent formulations, not
merely a different problem name or an extra digit of precision.

## 6. Reproduce and review

```powershell
python experiments/dependency_memory/joint_coding/decoder_frontier.py
python -m unittest discover -s experiments/dependency_memory -v
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

The [implementation](../experiments/dependency_memory/joint_coding/decoder_frontier.py)
and [independent-formulation tests](../experiments/dependency_memory/joint_coding/test_decoder_frontier.py)
use the standard library. Exploratory floating-point calculations selected
the rational t and weights, but are not needed to generate or verify the
certificate. All older study plans and completed model evidence remain
unchanged. The full historical one-block partition search need not be rerun
to check this new proof, which uses a different reduction.

Completed verification: all **270 tests pass**; the repository validator
reports no errors, including all unchanged historical source fingerprints
and saved-model audits; the manuscript builds with **23 cited sources**.
The older full one-block partition search was not rerun in this phase.

Review priorities are the timing-preserving reduction (1), the dual
inequality (3), symmetry completeness including repeated pairs, the
outward logarithm bounds, and the use of strict information slack in
achievability. The next substantive mathematical questions concern useful
finite-length constructions and structural results across a range of
rates; adding more decimal places here has little research value.
