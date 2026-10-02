# A three-block finite converse allowing every final decoder

October 1, 2026. **Local analytic converse with exact finite witnesses.**
Claim C63. External proof review and publication priority review remain open.
The cover and symmetry arguments are elementary; no new general coding method,
exact finite optimum, model gain or practical memory-cost result is claimed.

For three independent uniform four-bit blocks, six parent bits before R/O and
one child bit before J, let D_3(6) allow every final decoder in the existing
delayed-query model. The new result is

\[
\boxed{\frac{40072}{147456}=\frac{5009}{18432}
\le D_3(6)\le\frac{40529}{147456}.}
\]

This is **[27.1756%, 27.4855%]**, width 457/147,456, about 0.310 percentage
points. It extends the [complementary-decoder converse](COMPLEMENTARY_DECODER_COVER_2026-10-01.md)
to noncomplementary and repeated endpoints, including tied best predictions.
The upper witness is unchanged. The exact optimum inside this interval remains
open; this finite three-block result does not change the previously certified
[all-decoder asymptotic frontier](DECODER_COMPLETE_FRONTIER_2026-09-21.md).

## 1. All decoder tables and arbitrary joint encoding

The source X disappears after the parent encoder produces M with at most 64
states. Independent uniform block R and omission O arrive next. The updater
receives M,R,O, produces one bit Z, and loses M before the independent uniform
coordinate J != O arrives. The final prediction receives only Z,R,O,J.
Public programs, decoder tables and books are fixed before X. Source rereads,
archives, provider session state and source-selected public tables are excluded.
Independent random tapes can be fixed; a bound for every fixed tape also holds
after averaging. Encoders and updaters may jointly depend on all source blocks
within this information contract.

At each omission the final decoder supplies two three-bit prediction words.
Sorting the endpoints only relabels the updater's bit for that public branch.
There are 36 unordered pairs including repetition, hence 36^4 = 1,679,616
tables per block and 36^12 = 4,738,381,338,321,616,896 ordered table triples.
Source bit flips and coordinate permutations give the previously checked 4,751
orbits per block. Independent transformations inside each block and permutations
of the three uniform blocks preserve the source/query laws and capacity.
The unchanged [frontier implementation](../experiments/dependency_memory/joint_coding/decoder_frontier.py)
and its independent symmetry/Burnside tests supply this partition.

For table g, write

\[
L_g(x,a)=\sum_{o=0}^3\sum_{j\ne o}
 {\bf1}\{x_j\ne v_{g,o}^{a_o}(j)\},\qquad a\in\{0,1\}^4.
\]

The analysis word a lists four potential child bits; those four bits are not an
additional memory channel. A parent state specifies a triple c of such words,
one for each block. Every valid protocol therefore has a fixed book C of at most
64 triples. Its source-summed loss is at least
sum_x min_(c in C) L(x,c), where L is the sum of the three one-block losses.
Nearest assignment is also implementable for a fixed book under this contract.

For the average-error objective, actions with the same **entire loss vector on
all sixteen sources** may be identified. Replacing one by its representative
preserves the loss of every source and does not increase book size. Equal
histograms alone do not justify this reduction. Every one-block column sums to
96, so additive product columns can coincide only when each component loss
function coincides: any component difference would have to be a constant, and
equal means make that constant zero. Some repeated-endpoint tables therefore
have fewer than sixteen distinct cost columns. These identifications concern
average loss, not equivalence of individual query predictions.

## 2. An oracle gate eliminates distant decoder triples

Let u_g(x)=min_a L_g(x,a). For one omission, uniform projection onto three bits
gives the following exact sums over the sixteen source values:

| Endpoint type | Unordered pairs | Sum of nearest errors | Branch defect |
|---|---:|---:|---:|
| Complementary | 4 | 12 | 0 |
| Distinct, noncomplementary | 24 | 16 | 1 |
| Repeated | 8 | 24 | 3 |

Define d_g as the sum of four branch defects. Then sum_x u_g(x)=48+4d_g.
For three blocks, U(x)=sum_r u_(g_r)(x_r) is a relaxation in which the updater
can choose separately for every source, and

\[
\sum_x U(x)=(144+4(d_{g_1}+d_{g_2}+d_{g_3}))\,256.
\]

Total defect at least four thus implies at least **40,960 errors**, already
above the incumbent 40,529. No bound for those triples needs a target search.
The table census is independently checked against the polynomial
(4+24z+8z^3)^4; its coefficient at z^d counts the tables of defect d.
The near groups contain 6, 24, 170 and 642 orbits at defects 0, 1, 2 and 3,
respectively. They contain 284,928 per-block tables in 842 orbits.

| Sorted defect pattern | Mixed orbit cases |
|---|---:|
| 0,0,0 | 56 |
| 0,0,1 | 504 |
| 0,0,2 | 3,570 |
| 0,0,3 | 13,482 |
| 0,1,1 | 1,800 |
| 0,1,2 | 24,480 |
| 1,1,1 | 2,600 |
| Total | 46,492 |

The 56 all-complementary cases reuse C62. The remaining **46,436** have new
selected witnesses. The oracle gate, symmetries and these cases cover every
ordered table triple; the enormous table count is mathematical coverage, not
individually executed trials or model requests.

## 3. A union bound that permits tied ideal words

For a source x, let E(x,c)=L(x,c)-U(x), a nonnegative integer, and
A(x)={c:E(x,c)=0}. This set can contain several words. Choose any nonnegative
additive target T(x)=sum_r t_r(x_r). Source by source,

\[
\min_{c\in C}E(x,c)\ge T(x)-\sum_{c\in C}(T(x)-E(x,c))_+
 +{\bf1}\{T(x)=0\}\left(1-\sum_{c\in C}{\bf1}\{c\in A(x)\}\right). \tag{1}
\]

For positive T, the maximum positive saving is bounded by its sum. For zero T,
all saving terms vanish. If C contains no ideal word, the integer excess is at
least one; if C contains at least one, the correction is nonpositive. Thus (1)
holds even when several selected ideal words overlap on a source.

Let R_c=sum_x (T(x)-E(x,c))_+,
q_c=#{x:T(x)=0, c in A(x)}, and Q=#{x:T(x)=0}. In contrast to the
unique-ideal proof, **Q need not equal sum_c q_c**. Summation gives

\[
\sum_x\min_{c\in C}L(x,c)
\ge \sum_x U(x)+\sum_x T(x)+Q-\sum_{c\in C}(R_c+q_c)
\ge \sum_x U(x)+\sum_x T(x)+Q-\operatorname{Top}_{64}\{R_c+q_c\}. \tag{2}
\]

All weights are nonnegative. Top_64 means the sum of the largest min(64,N)
weights among the N distinct cost columns. It bounds every book of at most 64
words without enumerating all such books. Because targets are additive and
nonnegative, Q is the product of the three one-block zero-target counts, and
q_c is the product of their zero-target ideal incidences. Histograms of the
one-block scores t_r(x_r)-(L_(g_r)(x_r,c_r)-u_(g_r)(x_r)) compute R_c exactly.

## 4. Selected witnesses and independent checks

The [discovery file](../experiments/dependency_memory/joint_coding_general/discovery.json)
records one target triple per noncomplementary near case. Selection is bounded
post-hoc mathematics, not a preregistered experiment or an optimization claim:

1. Seven synchronized zero/one mask rules try 59,029 candidate triples; 78
   cases remain below the required 40,072 floor.
2. Mixed binary masks try 4,924 further candidate triples; 39 cases remain.
3. A quarter-unit grid tries 2,815 candidate triples on those 39 cases. Every
   selected witness reaches at least 40,072. The selected fractional targets
   actually take values zero, 1/4 or 1/2; the explored amplitudes were 0 through
   2 in quarter steps.

Each saved target code is public proof metadata: sixteen mask bits and four
bits for a quarter-unit amplitude. It is not source-instance storage, a model
token count or the six-bit parent budget. The certificate recomputes the selected
inequalities without trusting the discovery search or claiming target optimality.
The final checker uses standard-library integer arithmetic, no compiler,
numerical library, model call or floating-point bound.

Across the 46,436 selected cases it computes **178,240,944 distinct cost-column
instances** through exact histograms and declared profile multiplicities.
Thirty-one selected noncomplementary cases have the common 40,072 floor.
Another 42,656 have floors strictly above 40,529 and cannot improve the
incumbent. Together with C62, 3,790 near mixed cases remain possible; an interval
bound is not a proof that any one of them attains its lower endpoint.

Seven tests independently check the branch oracle sums and polynomial census,
all 842 near one-block tables on every source/action route, loss-function
identification, binary saving coefficients, fractional case histograms, the
pointwise tied-ideal inequality and source-bound certificates. The binary
formula is multilinear in multiplicities: a positive triple can use only scores
1, 0 and -1; scores at most -2 contribute zero. Checking all basis triples
independently verifies those coefficients. Fractional histograms use direct
source-triple sums for every distinct sorted score-multiset triple; explicit
caching reduces the 39 case checks to 432 direct sums. This is not a claim that
178 million times 4,096 source/column pairs were physically enumerated.
The zero-target fixtures include both missing ideals and overlapping selected
ideals. The unchanged upper witness retains its independent full route grading.

The controlled [auxiliary exploration](../experiments/dependency_memory/joint_coding_general/auxiliary/manifest.json)
preserves actual native search and numerical sources, raw outputs and hashes.
A separate [offline audit](../experiments/dependency_memory/results/joint_three_block_general_auxiliary_2026-10-01.json)
checks all 1,179,648 routes of eight candidate books; their best error count is
41,088, so none improves the incumbent. Native search was greedy plus two swaps,
not exhaustive or a certified local optimum. Twelve quantized rational dual
points are rechecked using outward rational logarithms; their earlier cover
counts include the oracle floor. Neither auxiliary computation is required by
(2) or the final witnesses. Preserved C clock readings are not a performance
comparison or a claim about CPU versus wall time.

## 5. What remains open

The result encloses the unrestricted **three-block** D_3(6); it does not
extrapolate the numerator or interval to other block lengths. The asymptotic
interval near 26.189898% and the child optimum 25% remain separate results.
An improved code must be saved and independently graded under the same timing;
a tighter converse must bound every allowed decoder and parent book. Exact
finite optimality, efficient encoders, external correctness and source priority
remain open. No natural workflow episode, LLM superiority, token saving or
production-cost advantage is added by this work.

Reproduction commands and the [source-bound certificate](../experiments/dependency_memory/results/joint_three_block_general_2026-10-01.json)
are in the [package guide](../experiments/dependency_memory/joint_coding_general/README.md).
