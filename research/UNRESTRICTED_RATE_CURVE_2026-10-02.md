# The unrestricted asymptotic parent-rate curve

October 2, 2026. **Local analytic result with an exact continuum comparison
certificate.** Claim C67. External correctness and publication priority remain
open. Zero new model calls or natural workflow episodes. This characterizes a
specific bit model; it does not measure token, agent-success or production gains.

The [completion theorem](COMPLEMENTARY_COMPLETION_2026-10-02.md) reduces the
unrestricted problem to six complementary decoder families. The new result
proves that the unsigned family attains the minimum supporting objective at
**every positive slope**. Consequently the [C65 scalar formula](PARENT_RATE_SPECTRUM_2026-10-01.md)
now characterizes the entire unrestricted asymptotic curve, including rates
between its eight certified points. Historical C33/C34/C65/C66 artifacts stay
unchanged. No exact finite code or efficient encoder is supplied.

## 1. Model and theorem

There are k independent uniform four-bit blocks X_r. The parent M is formed
before independent uniform block R and omission O, with at most
2^floor(k*r) states. The updater sees only M,R,O, emits one bit Z and discards M.
The final decoder sees only Z,R,O,J, where J is uniform among the three retained
coordinates. Tables and codebooks are public and fixed before source. Source,
parent, archive, environment and provider-session rereads are excluded. Rates
are **bits per four-bit block**, not tokens or record slots.

Let D_k(B) be the minimum average queried-bit error under parent capacity B.
For an omission, a final decoder has two three-bit prediction words; repeats
are allowed. A table g has four such pairs. For a decision word a in {0,1}^4,
L_g(x,a) counts errors over all twelve omission/query routes. Decision words
describe possible updater responses; they are not four extra child bits.

**Theorem.** For every r>=0,

\[
D_\infty(r)=\lim_{k\to\infty}D_k(\lfloor kr\rfloor)
\]

exists and equals the ordinary rate-distortion curve for the unsigned table
g_u, whose omission endpoints are (000,111), with distortion L_u/12.
It has the following exact characterization:

- D_infinity(0)=1/2.
- For 0<r<h_star, choose the optimal unsigned Gibbs channel at a t in (0,1)
  with mutual information R(t)=r. Then D_infinity(r)=E_t[L_u]/12.
- D_infinity(r)=1/4 for r>=h_star, where h_star=4-(5/8)*log2(5).

The curve's positive-slope supporting optimum uses only constant decision
words below about 0.620690001029 information bits per block and adds the six
balanced words above that transition. This is a reproduction support change,
not the number of stored parent states. The five other complementary symmetry
families have strictly larger supporting minima for every positive slope.
We do not classify possible equality cases among noncomplementary tables.

## 2. A common supporting inequality

Put t=2^(-s), s>0. For a fixed table define

\[
C_g(s)=\min_{P(a|x)}[I(X;A)+s\,\mathbb E L_g(X,A)]
       =\min_q F_g(q,t),\qquad
F_g(q,t)=-\frac1{16}\sum_x\log_2 z_x,
\quad z_x=\sum_a q_a t^{L_g(x,a)}.
\]

The equality is the finite-alphabet Gibbs variational identity: minimize
D(P(a|x)||q | P_X)+s E L first over q to obtain I+s E L, or first over P to
obtain F. Supporting objectives and strategy alphabets are established tools.

For any witness q with all z_x>0, put
gamma_a=(1/16)*sum_x t^L(x,a)/z_x and gamma=max_a gamma_a. For any other q',
Jensen's inequality gives

\[
F_g(q',t)-F_g(q,t)
=-\mathbb E\log_2(z'_X/z_X)
\ge-\log_2\mathbb E(z'_X/z_X)
\ge-\log_2\gamma.
\]

Thus C_g(s)>=F_g(q,t)-log2(gamma), including channels using words outside q's
support. Set G_g=product_x(z_x)*gamma^16. If G_g is strictly below the unsigned
witness product H_u=product_x(z_{u,x}), then

\[
C_g(s)\ge-\log_2 G_g/16
>-\log_2 H_u/16=F_u(q_u,t)\ge C_u(s).
\tag{1}
\]

The unsigned witness need not be optimal or have a self-consistent Gibbs
marginal. It is only a comparison upper bound for the minimized free objective.

C66 preserves I(X;A) under a fixed public decision-word relabeling while choosing
a complementary table with no larger population-average loss. Hence the
minimum over all 36^4 tables equals the complementary minimum. By (1) and the
next section, it equals C_u(s) for every s>0.

For an arbitrary joint parent and heterogeneous block tables, each potential
response word A_r is a function of M. Source independence gives
sum_r I(X_r;A_r)<=H(M)<=floor(k*r). Applying the common bound block by block
yields, for every finite k and s>0,

\[
D_k(\lfloor kr\rfloor)\ge\frac{C_u(s)-r}{12s}.\tag{2}
\]

This permits unequal information allocation and different tables across blocks;
it does not assume separate parent encoders. Independent random tapes can be
fixed without increasing average loss or capacity.

## 3. An exact certificate on the whole parameter interval

The [generator](../experiments/dependency_memory/rate_curve/README.md) uses the
existing complete partition of 256 complementary tables into six symmetry
orbits, of sizes 8,96,24,96,24,8. The unsigned orbit is the first. Each other
family uses its explicit uniformly tie-broken nearest-word marginal as q;
this is a rational witness, not an assumed optimum.

Use three unsigned witnesses. Entries within each class are equal:

| t interval | Integer weight per constant word | Per balanced word | Per odd word | Total weight |
|---|---:|---:|---:|---:|
| [0,4/25] | 5 | 1 | 0 | 16 |
| [4/25,1/4] | 9 | 1 | 0 | 24 |
| [1/4,1] | 1 | 0 | 0 | 2 |

For a complementary table let m_x=min_a L_g(x,a); sum_x m_x=48. With integer
witness weights w_a and Q=sum_a w_a, subtract m_x from each kernel exponent.
Group identical relative partition polynomials
Z_j(t)=sum_a w_a*t^(L_g(x,a)-m_x), with source multiplicities c_j.
Define H_ja(t)=sum_(x in j) t^(L_g(x,a)-m_x) and

\[
N_a=\sum_j H_{ja}\prod_{l\ne j}Z_l,\qquad
G_{g,a}=\frac{t^{48}N_a^{16}}
 {16^{16}\prod_j Z_j^{16-c_j}},\qquad G_g=\max_a G_{g,a}.
\]

The factors Q cancel exactly. If U_x is the unsigned relative partition with
total weight Q_u, then H_u=t^48*product_x U_x/Q_u^16. All denominators are
positive for 0<t<1. Clearing them reduces G_(g,a)<H_u to the integer inequality

\[
K_{g,a}(t)=16^{16}\Big(\prod_j Z_j^{16-c_j}\Big)
                  \Big(\prod_x U_x\Big)-Q_u^{16}N_a^{16}>0.\tag{3}
\]

All sixteen columns are retained. Identical N_a polynomials group the
5*16*3=240 column/interval cases into **48 distinct comparisons**: 18,6,12,9,3
for the five other families. Every K factors exactly as
positive_content*(1-t)^h*P(t), with h=2 or 4 and primitive P of degree at most
606. No numerical optimizer or floating comparison certifies a sign.

For an interval [A/L,B/L] and n=degree(P), form the integer polynomial

\[
T(v)=L^n(1+v)^n P\left(\frac{A+Bv}{L(1+v)}\right).
\]

A Horner/Pascal recurrence computes its full coefficient vector exactly.
Across all 48 comparisons, **19,474 integer coefficients** are nonnegative,
and each vector's first and last coefficients are strictly positive. Therefore
P is positive throughout each closed interval, including the rational seams.
The stripped factors are positive on 0<t<1. The three intervals cover that
entire domain, proving (3) and hence (1) for every positive slope.

The regeneration, full column cover and analytic argument establish the result;
counts or digests alone do not. This is a standard polynomial-positivity test
applied to selected explicit witnesses, not a new general method or a grid
extrapolation. Strict separation concerns the five other complementary orbits.

## 4. The exact parametric curve

C65 independently proves that the unsigned minimizer has no odd-word mass and
reduces to q_0=q_15=(1-p)/2, q_a=p/6 for the six weight-two words. Its source
class weights are (1/8,1/2,3/8), and its class partitions are

\[
z_i=A_i+(B_i-A_i)p,\qquad
A=((1+t^{12})/2,(t^3+t^9)/2,t^6),\quad
B=(t^6,(t^5+t^7)/2,(t^4+4t^6+t^8)/6).
\]

Let b_i=B_i-A_i. For t<t_star the unique p in (0,1) satisfies the quadratic
sum_i w_i*b_i*product_(j!=i)(A_j+b_j*p)=0. For t>=t_star use p=0.
C65's exact transition polynomial in u=t^2 is

\[
1-11u-u^2-4u^3-2u^4-4u^5-u^6-11u^7+u^8.
\]

Its unique root gives 0.299826862327<t_star<0.299826862328. With this exact
p(t), let z_x=sum_a q_a*t^L_u(x,a) and define

\[
P_t(a|x)=q_a t^{L_u(x,a)}/z_x,\qquad
e(t)=\frac1{16}\sum_{x,a}P_t(a|x)L_u(x,a),
\]
\[
C_u(s)=-\frac1{16}\sum_x\log_2 z_x,\qquad
R(t)=C_u(s)+e(t)\log_2 t,\qquad D(t)=e(t)/12.\tag{4}
\]

At the scalar optimum the gradient is one on active constant/balanced words.
Symmetry and sum_a q_a*gamma_a=1 show that the Gibbs output marginal is q.
Thus R(t) is actual mutual information, not just its cross-information upper
bound. Equation (4) is an exact parametric characterization with an algebraic
root; a sampled floating curve is not part of the proof.

The optimizer/channel are continuous through the support transition. At t->1
the channel is source-independent: R->0 and D->1/2. At t->0 the nearest unsigned
signature is deterministic; its two constant fibers have size five and the six
balanced fibers size one. The limiting p is 3/8, R->h_star and D->1/4.
For example, after factoring the dominant kernel powers, the limiting scalar
log objective is (5/8)*log((1-p)/2)+(3/8)*log(p/6); its unique maximizer is 3/8.
Continuity and the endpoint limits ensure that every 0<r<h_star occurs as some
R(t). No strict-monotonicity assertion is needed for this coverage argument.

The formerly restricted transition enclosures now apply to the unrestricted
asymptotic curve: information [0.620690001029,0.620690001030] bits/block and
error [0.312681553947,0.312681553948]. The eight C65 intervals and C34's rate-two
interval remain valid consistency checks, rather than being rewritten as new
finite optima.

## 5. Achievability inside the exact fixed-length capacity

At r=R(t)>0, (2) gives D_k(floor(kr))>=D(t) for every k. To prove the matching
limsup, mix P_t with a source-independent channel P_0 with weight epsilon>0.
Mutual information is convex in the channel for a fixed source, so
I(P_epsilon)<r, while distortion tends to D(t) as epsilon->0. This is offline
test-channel design; it supplies no extra actor observations or runtime channel.

Choose I(P_epsilon)<rho<r. Standard finite-alphabet average-distortion coding
gives fixed codebooks at rate rho approaching that channel's distortion.
Rounding the codebook and including a fallback needs at most ceil(k*rho)+1
parent bits, which eventually fit floor(k*r). Each codeword lists k response
words; the legal updater emits only its selected block's omission bit, and the
unsigned final decoder predicts that one bit. Fix the public codebook before X.
Take k->infinity, then epsilon->0. No extra o(k) parent bits are assumed.

The same strict-slack mixing argument works at r=h_star with the deterministic
oracle-signature channel, recovering C33's exact-floor asymptotic threshold.
For r>=h_star, use that construction and the universal 1/4 oracle lower bound.
At r=0, the one-state parent cannot reveal source information and balanced
queried bits have error 1/2. These lower and upper limits prove existence and
the theorem for every r. Alternatively concatenation makes
k*D_k(floor(kr)) subadditive since floor(k1*r)+floor(k2*r)<=floor((k1+k2)*r).

Exact finite attainment of 1/4 still requires 3k parent bits. Asymptotic error
at rates h_star<=r<3 can converge to 1/4 without attaining it at any finite k.
The theorem supplies no finite blocklength, efficient code or practical savings.

## 6. Literature, discovery and limits

On October 2, the existing primary reference Polyanskiy and Wu was reread:
[MIT 6.441 Chapter 24](https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/aaa8d18ddecde45f97134d3f3dcee4a3_MIT6_441S16_chapter_24.pdf),
Theorems 24.1-24.3 and Sections 24.2/24.2.2, printed pp. 246-249; and
[Chapter 25](https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/5721b7df786b416dadad7c7bb3364d00_MIT6_441S16_chapter_25.pdf),
Section 25.2, Theorem 25.2 and support remarks, printed pp. 258-259. These supply
established finite-alphabet coding, supporting optimization and support care.
Chapter 24's finite-channel average-distortion construction with a fallback is
the relevant coding foundation. This bounded rereading is not a new whole-source
review or a publication-priority result. The existing strategy-alphabet
comparison remains in [C34's reading](DECODER_COMPLETE_FRONTIER_2026-09-21.md#5-literature-and-candidate-novelty).

[Preserved discovery](../experiments/dependency_memory/rate_curve/auxiliary/README.md)
includes a failed two-witness float screen, a successful three-witness screen,
and a factorial-convolution polynomial probe. The final checker uses a separate
Horner/Pascal interval transform. The selected distributions and seams are
post-hoc mathematical choices, not prespecified experiments or independent
trials. Neither convergence nor a float rank supports the theorem.

The candidate mathematical contribution is this specific unrestricted delayed-
query curve and its complete finite certificate, together with C66's model
reduction. Rate-distortion duality, strategy alphabets, averaging and polynomial
positivity are not claimed new. External proof/priority review, sharper finite
codes and natural-workflow applicability remain open. The balanced completion
counterexample shows why this result cannot be transferred to arbitrary biased
sources, and average loss is not individual semantic safety.
