# A finite lower bound for the construction's decoder family

October 1, 2026. **Elementary analytic restricted converse with independently
checked finite ingredients.** External correctness and literature priority review
remain open. No model calls are involved. The weighted-cover argument is not
claimed a novel general technique.

Let D^u_3(6) restrict the existing three-block model to final predictions
independent of the late coordinate J. Public R/O-dependent child relabellings
can be absorbed in the updater, so the canonical decoder predicts its received
bit. Constant endpoints are also included. The new local result is

\[
\boxed{\frac{40072}{147456}=\frac{5009}{18432}
\le D^u_3(6)\le\frac{40529}{147456}.}
\]

The interval is approximately **[27.1756%, 27.4855%]**, width 0.309923 percentage
points. The upper end is the [saved three-block construction](JOINT_THREE_BLOCK_WITNESS_2026-10-01.md).
The lower end is new local analysis of this restricted family. It is **not** a
lower bound of this size for all final decoders, nor an exact finite optimum. [C60]

## 1. Reduction and an elementary cover inequality

The information order is unchanged: three independent uniform four-bit source
blocks; at most 64 parent states before R,O; one child bit before J; final access
only to that bit and public R,O,J. No archive, source reread or source-dependent
public codebook is available. For each parent state, the updater's potential
outputs define a fixed triple of four-bit decision words. Hence every protocol
in this family has a public codebook C of at most 64 such triples. An arbitrary
encoder cannot do better than nearest-word assignment. Independent random tapes
can be fixed; the lower bound holds for each fixed tape and therefore their mean.

For one source block x, write u(x)=min_a L(x,a), with the prior
\(L(x,a)=\sum_o\sum_{j\ne o}\mathbf1\{x_j\ne a_o\}\).
By source weight 0,1,2,3,4, u(x) is respectively 0,3,4,3,0. Define t(x)=1 when
the source weight is two and zero otherwise. For three blocks, use sums U and T.
Let E(x,c)=L(x,c)-U(x) be a candidate's nonnegative excess, and
\(r(x,c)=(T(x)-E(x,c))_+\). Then

\[
\min_{c\in C}L(x,c)\ge U(x)+T(x)-\sum_{c\in C}r(x,c),
\]

because the maximum of the positive excess-saving terms is at most their sum.
Over all 4,096 source triples, sum U=36,864 and sum T=4,608.

## 2. Every column has reward at most 25

The one-block score is t(x)-(L(x,a)-u(x)). Its distribution over the sixteen
sources depends only on the weight class of decision word a. Exponents below
denote multiplicity, not powers:

| Decision class | Number of words | Score : multiplicity |
|---|---:|---|
| C: weight zero or four | 2 | 0:5, -1:6, -6:4, -12:1 |
| P: weight one or three | 8 | 0:3, -1:3, -2:3, -3:3, -5:3, -9:1 |
| B: weight two | 6 | 1:1, -1:4, -2:4, -3:1, -4:4, -6:2 |

Convolve three scores and sum the positive parts. Up to block order, the
complete ten possibilities are:

| Classes | Sum of positive parts over all sources |
|---|---:|
| CCC, CCP, CPP, PPP | 0 |
| BCC | 25 |
| BCP | 15 |
| BPP | 9 |
| BBC | 16 |
| BBP | 9 |
| BBB | 15 |

Thus \(\sum_x r(x,c)\le25\) for every one of the 4,096 decision triples, and
the eight all-constant triples have reward zero. The
[certificate](../experiments/dependency_memory/results/joint_three_block_cover_2026-10-01.json)
records every column reward and the complete one-block profiles. A separate
test enumerates all 16,777,216 source/column combinations without the generator's
histogram convolution; its reward counts are 0:1,000, 9:2,016, 15:792, 16:216
and 25:72.

## 3. Missing constant centers strengthen the bound

For each all-constant decision triple, exactly 5^3=125 source triples have
that unique ideal branch signature: each source block has weight zero/one or
three/four. These eight fibers are disjoint. On such a source, T=0 and every
positive reward term is zero. If its constant center is absent from C, a
different decision word changes at least one strict odd-majority decision,
giving integer excess at least one. This adds 125 for each missing center
without double-counting any reward.

If n_0 of the eight constant centers are in a codebook of size at most 64,
the summed loss is therefore at least

\[
36864+4608-25(64-n_0)+125(8-n_0)
=40872-100n_0\ge40072.
\]

The saved upper witness contains all eight constant centers. No enumeration of
all 64-element books is needed for this inequality. It leaves 457 outcomes of
uncertainty; it does not certify that either endpoint is attainable as an optimum.

## Scope and next question

Coordinate-dependent endpoints such as 010/101 are legal in the unrestricted
model and outside this proof's reduction. The bound API explicitly rejects
them. Keep the [decoder-complete all-k lower interval](DECODER_COMPLETE_FRONTIER_2026-09-21.md)
unchanged; this note sharpens a finite restricted problem only. Bits, fixed
public codebooks and average bit error do not imply token budgets, task success
or deployed-agent savings. The next mathematical question is whether a comparable
finite cover can include other decoder tables without losing this guarantee.
