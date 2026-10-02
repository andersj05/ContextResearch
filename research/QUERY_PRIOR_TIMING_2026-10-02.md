# Query probabilities, robust memory and an early class cue

October 2, 2026. **Local deductions from C33/C67 and exact finite-code
sensitivity checks.** Claim C70. External correctness and publication priority
remain open. Zero new model calls or prospective natural episodes. This changes
the query-class law, keeping the uniform source and within-block law fixed.
It supplies no token, credit, production or natural-agent benefit measurement.

The [C69 six-block gain](CONDITIONAL_SIX_BLOCK_CODE_2026-10-02.md) depends on the
query distribution. Its original encoder is worse than the refined product
when the left class has probability below 59911/152862. An opposite-orientation
pair removes that sensitivity without extra instance state. When the prior is
known, ordinary unequal allocation can do much better. These are distinct
information conditions, rather than competing answers to one unspecified task.

## 1. Three information conditions

There are k=2n independent uniform four-bit blocks. The first n form public
class L and the last n class R. Independently of X, draw the class T with
Pr(T=L)=p, then draw block R uniformly inside that class. O is uniform among
four coordinates; after the child is formed, J is uniform among the remaining
three. The overloaded R denotes the queried block, not its class label.
Within-class queries remain uniform throughout this note.

The parent has at most 2^(4n) states: two bits per block. The updater sees
M,R,O and retains one bit Z; the final actor sees only Z,R,O,J and fixed public
tables. Source/parent rereads, archives, scratch values, environment and
provider sessions are excluded after their declared boundary. Fixed books and
public query descriptors are free in this value-bit model; implementation
bytes and instance bits are separately reported. Diagnostic losses do not
reach the actors.

| Condition | Available before parent design/formation | Actual class/block/O | Final J |
|---|---|---|---|
| Known prior | Fixed source-independent p and X | After M | After Z |
| Unknown prior | X and a design independent of p | After M; p may optionally be disclosed then | After Z |
| Early realized class | X and the actual sampled T | R/O remain after M | After Z |

Unknown-prior minimax means worst case over a single fixed p in [0,1], chosen
independently of the source. It excludes p chosen from X, M or each instance.
Knowing p is not knowing the realized class T. Moving T earlier changes the
information order even though I(X;T)=0.

## 2. Optimal asymptotic allocation when p is known

Let D(r) be the unrestricted asymptotic curve proved in
[C67](UNRESTRICTED_RATE_CURVE_2026-10-02.md). Let W_n(p) be the minimum error
with two n-block classes and exactly the 4n-bit parent cap. Then

\[
W(p)=\lim_{n\to\infty}W_n(p)
=\min_{r_L,r_R\ge0,\ r_L+r_R\le4}
  \{pD(r_L)+(1-p)D(r_R)\}.\tag{1}
\]

The converse includes arbitrary joint parent encoders and heterogeneous final
tables. For block i, let A_i list its four possible updater responses to O.
It is a function of M and public information. With uniform independent sources,

\[
\sum_i I(X_i;A_i)\le\sum_i I(X_i;M)
\le I(X^k;M)\le H(M)\le4n.
\]

C67's all-slope supporting inequalities give the block's mean error at least
D(I(X_i;A_i)), regardless of its table. Convexity of D and Jensen's inequality
within each class give (1)'s lower bound, with r_L and r_R their mean block
informations. This does not assume equal information allocation or a product
encoder. At p=0 or 1 the ignored class contributes zero weight; the same bound
applies.

For achievability, choose rates satisfying the variational constraint and
test channels approaching each D(r). Mix any positive-rate channel with a
source-independent channel to get strictly less information and arbitrarily
close distortion. Choose class coding rates rho_L and rho_R above those
informations but with rho_L+rho_R<4. Two fixed n-block codebooks, including
fallbacks, need at most ceil(n*rho_L)+ceil(n*rho_R)+2 bits, eventually within
4n. Fix both books before X. If a class rate is zero, use its one-state book;
if the optimum leaves unused capacity, strict slack is already available.
Taking n to infinity and then the mixing weight to zero proves (1). No extra
o(k) instance bits or per-source allocation marker are allowed. The coding
existence argument supplies no efficient finite encoder near this limit.

W is symmetric about p=1/2 and concave in p, since (1) is the infimum of affine
functions of p. Its endpoints equal 1/4. At p=1/2, Jensen gives W=D(2).
For p other than 1/2, W(p)<D(2). For interior p, perturb (r_L,r_R)=(2,2)
in opposite directions: the directional derivative is
(2p-1)D'(2), which is nonzero, so one sign lowers the objective. The endpoint
values are also strictly smaller than D(2).

For completeness, the allocation has a unique interior optimum when 0<p<1.
Put h*=4-(5/8)log2(5). The sum constraint is active and both rates lie in
(4-h*,h*), wholly above C67's support transition. On this branch write
C(s)=min_mu F(s,mu), with s=-log2(t), using C65's interior balanced mass mu.
Strict scalar convexity gives F_mu_mu>0. At fixed mu,
F_ss=-(ln 2) E Var(L|X)<0: both constant response words have positive mass
and some losses differ. Differentiating the unique stationary mass gives
C''=F_ss-F_s_mu^2/F_mu_mu<0. Hence R(s)=C-sC' has R'=-sC''>0,
D'(r)=-1/(12s), and D is strictly convex there. A rate at h* has marginal
slope zero while the other class has a negative slope, so that boundary
cannot minimize an interior-p objective. The stationarity condition is

\[
pD'(r_L)=(1-p)D'(r_R),\qquad
\frac{s_L}{s_R}=\frac{p}{1-p}.\tag{2}
\]

For rational p=a/(a+b), a common q gives t_L=q^a and t_R=q^b. The exact
optimum obeys R(q^a)+R(q^b)=4. The numeric certificate uses nearby rational
q with strict rate slack, rather than treating a floating root as exact.

### Checked rational points

The [new checker](../experiments/dependency_memory/query_weighting/asymptotic.py)
uses C65's rational unsigned weights, a dual correction over all sixteen
response columns, and outward rational log bounds. C67 already proves unsigned
dominance for every positive slope; no new final-table enumeration occurs.
For s_0=-log2(q), let C_a^- and C_b^- be the certified supporting lower
bounds. Summing over the two classes gives the finite lower bound

\[
W_n(p)\ge\frac{C_a^-+C_b^--4}{12(a+b)s_0^+},\tag{3}
\]

where s_0^+ is an upper bound and the numerator is positive at these witnesses.
The two explicit rational Gibbs channels have combined information upper bound
strictly below 4. Their weighted distortion is therefore an asymptotic upper
bound using the strict-slack coding construction. The chosen witness
distribution need not equal its exact output marginal; the upper bound uses
cross-information, and the dual bound charges its residual.

| p | Exact outward enclosure of W(p) | Approximate error percentage |
|---|---|---:|
| 1/10 | [0.252875840765, 0.252875840766] | 25.287584% |
| 1/4 | [0.257186606420, 0.257186606421] | 25.718661% |
| 1/3 | [0.259483526591, 0.259483526593] | 25.948353% |
| 2/5 | [0.260962789402, 0.260962789404] | 26.096279% |
| 1/2 | [0.261898979908, 0.261898979909] | 26.189898% |

These are five exact interval computations and an analytic characterization
elsewhere; symmetry supplies the mirrored values. The uniform point is a
consistency check inside the unchanged historical C34/C67 enclosure
(0.2618989799,0.2618989801). No finite code at these error levels is supplied.

## 3. Unknown-prior minimax and the timing of a realized cue

Let U_n be the minimum, over parent designs independent of p, of worst-case
error over p in [0,1]. For every n,

\[
D_{2n}(4n)\le U_n\le D_n(2n).\tag{4}
\]

The lower bound takes p=1/2, where the block query is uniform over all 2n
blocks. The upper bound uses the same optimal n-block rate-two code on both
classes, with separate 2n-bit indices fitting 4n. Both class errors equal
D_n(2n), so every p has that error. C67 gives
lim U_n=D(2). This is an asymptotic squeeze, not equality of finite optima.
The result also holds if p is publicly disclosed after M: the upper code
ignores it, and the p=1/2 lower bound already allows arbitrary public tables.

If instead the actual T is public before M, store the three-bit majority
signature of each block in that selected class only. This uses 3n bits inside
the same 4n cap. After R/O the updater emits its selected omission bit; the
final decoder predicts that bit. Across uniform four-bit sources, its error
is exactly 1/4, the oracle lower bound even with complete source access before
the one-bit child. R determines T, so the parent need not store a class marker.
This executable construction is in
[codec.py](../experiments/dependency_memory/query_weighting/codec.py).

At late uniform T the limiting error exceeds the early-T error by
(0.0118989799,0.0118989801), about 1.189898 percentage points. For exact finite
1/4 attainment the late uniform law needs 6n parent bits by
[C33](JOINT_BLOCK_CODING_2026-09-21.md), whereas the
early cue construction uses 3n. The one-bit cue carries no source information;
it says which half may be queried. Its arrival time changes the permitted
parent dependence. These are elementary consequences of C33/C67, not a new
general side-information theorem or a measured agent result.

## 4. Frozen and reencoded finite books

C69's source-bound grouped actor counts split into left error 165,852,393
and right error 166,005,255. Each half has denominator
603,979,776=36*16^6. The refined three-block product has 165,945,344 errors
in each half. Thus the original uniform-trained encoder's error under p is

\[
\frac{p\,165852393+(1-p)\,166005255}{603979776},
\]

and it beats that product exactly when p>59911/152862. This is frozen-encoder
evaluation; it does not silently reassign messages after observing p.

For known-prior reencoding, keep the C69 book fixed but minimize weighted loss
over its 4096 response words. All unmodified right indices collapse to their
minimum right cost. There are two modified indices, 52 and 58. Group left
sources by their relative minimum changes delta_52,delta_58. The per-source
weighted loss becomes

\[
p d_L+\min\{(1-p)d_U,
p\delta_{52}+(1-p)d_{52},
p\delta_{58}+(1-p)d_{58}\}.\tag{5}
\]

Sixteen left groups and 108 right cost types give 1728 weighted terms covering
all 16,777,216 source pairs. For each term, enumerate every pairwise rational
line intersection in [0,1] and select the minimum at each rational midpoint.
Aggregate actual slope changes. The result has **52 exact affine segments**,
with continuity and concavity checked at every seam. This covers the entire
interval, not just a probability grid. The executable encoder chooses the
smallest integer M in ties; message ties do not affect (5)'s error.

The initial segment has intercept 40514/147456 and positive slope
875/75497472: even known-prior reencoding of this particular book is worse
than the refined product at small positive p. It beats all three allocation
controls below exactly on the open interval
(7485511/18906056,782337/1293050). This is a fixed-book result, not an optimal
weighted finite code or a complete search over allocations.

## 5. A deterministic pair robust to every p

Use two C69 six-block components, one with ordinary L/R orientation and one
with orientation reversed. Give each public class three blocks from each
orientation. Under uniform iid sources, swapping classes exchanges their
expected half losses. Each class's combined mean error is therefore

\[
\frac{165852393+166005255}{2\cdot603979776}
=\frac{2304567}{8388608}\approx0.274725794792.
\]

For any source-independent p the weighted mean has that same value. The
12-block parent uses exactly 24 bits and the child one bit. Group parity
determines orientation publicly; there is no stored orientation bit, random
tape, source-dependent selection or extra value channel. Independent pairs
extend this to k=12h with 2k parent bits. Public label payload remains 120
bytes: tables are shared across components. Framing, program/runtime and JSON
bytes are excluded from that payload figure and are not instance bits.

These larger-product error counts follow from the bound C69 component
population and independence. They are not enumeration of all 16^12 sources.
The new routing checker executes 196,608 response checks and 589,824 final
query checks: every 4096 local parent message, both orientations, both public
classes, all ranks/O/J. Other-group extraction is proved by disjoint 12-bit
masks and checked with distinct padding parents. Complete-source diagnostics
separately compare the packed product and actual actor losses. Per-instance
class errors need not be equal; equality is over the specified source law.

Stronger named controls use the same average two parent bits per block. These
finite comparisons use complete three-block classes or their products, so n
is a multiple of three; all controls fit the balanced pair's k=12h lengths:

| Public allocation | Class L error | Class R error | Weighted error |
|---|---:|---:|---|
| Refined three-block products, 6 bits per triple in each class | 40514/147456 | 40514/147456 | 40514/147456 |
| One bit per L block, three per R block | 5/16 | 1/4 | 1/4+p/16 |
| Three bits per L block, one per R block | 1/4 | 5/16 | 5/16-p/16 |

The single-block books {0,15} and the eight majority signatures have errors
60/192 and 48/192, independently graded over all sources/O/J. Equal class
sizes make the 1/3 allocations total 4n bits. The allocation is public and
fixed before X; no uncharged per-source choice is allowed. We do not claim
the one-bit control is the unrestricted optimum.

The balanced pair beats all three named known-prior controls exactly when
207415/524288<p<316873/524288, approximately 0.395613<p<0.604387. At p=1/4,
the 1/3 allocation instead achieves 17/64=26.5625%, substantially below
27.472579%. For unknown-prior minimax the unequal controls have worst-case
5/16, while the balanced pair preserves the small uniform gain over the
refined product. Neither finite code approaches the proven minimax limit.

## 6. Discovery, prior work and validation

The changed-law inspection and witnesses are post-hoc development mathematics,
not independent model trials. The first floating probe bounded the common q
by 0.299 and failed at p=2/5: combined information was 4.687711329867541>4.
The common q can exceed a single-class transition even when q^m and q^n do not.
Changing only that bracket to 0.9 corrected the candidate. Initial JSON had
been overwritten; the explicitly named initial_recomputed_probe.json is an
offline rerun of the original deterministic script, not a recovered original
raw log or timing record. Both scripts, corrected output, recomputed failure,
admission script and this distinction remain in
[discovery](../experiments/dependency_memory/query_weighting/discovery/README.md).

The admission rule rounds each float-selected q upward at denominator 10^12
and permits at most ten increasing numerators. All five first candidates pass
exact strict information<4 and interval-width<2e-11 checks. Only exact
rationals, dual residuals and outward logs support the numeric bounds. The
checker validates 16 source/provenance bindings, including original C67/C69
results and their source bindings. Historical source/results are unchanged.

On October 2, the existing Polyanskiy/Wu primary
[MIT Chapter 25](https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/5721b7df786b416dadad7c7bb3364d00_MIT6_441S16_chapter_25.pdf),
Section 25.2, Theorem 25.2 and support remarks, printed pp. 258–259, was reread.
It supplies established supporting optimization and support conditions. The
coding foundation remains C67's bounded Chapter 24 reading. Existing key
`polyanskiywu2016coding`; no new bibliography metadata, full-review status or
replication is asserted. Generic allocation, symmetrization, product coding
and early side information are established; the addition is the explicitly
scoped application and its checked finite controls. Publication priority and
external proof review remain open.

Eight new scientific tests check independent query losses, complete-message
weighted minima and ties, all envelope seams, rational supporting/slack bounds
and independent channel entropy, product capacity/routing, early-cue access,
negative controls and failure provenance. Full repository verification is
recorded in the [current status](../docs/STATUS.md). Biased sources, nonuniform
within-class queries, correlated/adaptive queries, efficient near-curve codes,
new natural episodes and production costs remain outside these results.
