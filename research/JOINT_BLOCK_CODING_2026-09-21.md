# Joint coding changes the delayed-query composition penalty

September 21, 2026. **Local mathematical results: explicit finite construction,
asymptotic achievability bound, and exact asymptotic threshold for vanishing
excess error.** Computations certify the finite ingredients. The asymptotic
conclusions require the analytic arguments below. External proof review and
priority assessment remain open. There are no new model trials.

## Results

Write D_k(B) for the minimum average bit error in the existing k-block model
with B parent bits and one child bit. The information contract is unchanged:
k independent uniform four-bit blocks; compress before the uniform block R
and omission O are revealed; replace the parent with one bit before the
uniform remaining coordinate J is revealed. The final decoder sees only
that bit and R,O,J. Public codebooks are fixed before the source; there is no
archive, old parent access, source-dependent public label, or source reread.

The new conclusions are:

1. **The one-block loss does not persist unchanged under joint encoding.**
   An explicit four-bit parent for two blocks has error 283/1024, below
   D_1(2) = 9/32 by 5/1024. This is an upper bound on D_2(4), not its optimum.
2. **The asymptotic error at two bits per block is at most 101/384.**
   A rational test channel has distortion 101/384 and mutual information
   strictly below two. Standard rate-distortion achievability, applied to
   branch-decision words, gives the operational bound with the same child
   restriction. No finite code attaining this asymptotic number is supplied.
3. **Approaching the child optimum requires and suffices at rate**
   h_* = 4 - (5/8)log_2(5), approximately 2.548794941 bits per block.
   Every fixed smaller rate has a positive excess-error gap. At rate h_*,
   floor(k h_*) parent bits suffice for error tending to 1/4. In contrast,
   exact error 1/4 at any finite k still requires 3k bits.

These extend [C21's exact one-block result](EXACT_CHAIN_OPTIMUM_2026-09-19.md)
and the [C11-C12 scaling proof](PROOF_AUDIT_2026-09-18.md). They do not overturn
either. In particular, the previous warning against multiplying the
one-block excess is now supported by a strict counterexample. Claims C31-C33
are registered in [the manuscript evidence ledger](../paper/claims.csv).

## 1. A representation that respects the one-bit child

Fix the final decoder to predict its received bit, regardless of J. A
four-bit word a encodes four *potential* child decisions: on omission o,
the updater emits bit a_o. Only one of these decisions is emitted, after
o is known. A parent message indexes a fixed sequence of k such words.

For source word x and decision word a define the integer loss

\[
L(x,a)=\sum_{o=0}^3\sum_{j\ne o}{\bf1}\{x_j\ne a_o\},
\qquad d(x,a)=L(x,a)/12.
\]

An encoder choosing a sequence a^k has average chain loss
k^{-1} sum_r d(x^(r),a^(r)). This identity uses the uniform independent
block/omission/query distribution. Thus an ordinary fixed-length code for
this distortion supplies a valid chain code. This is an achievability
reduction, not a claim that these unsigned decoders exhaust all protocols.
The exponential public codebook is not charged as instance memory, exactly
as in the original mathematical model; no runtime efficiency is asserted.

## 2. Explicit two-block construction

Coordinates and omission bits use least-significant-bit-first integer
notation. Let T = {3,5,6,9,10,12}, the six four-bit words of weight two.
Use the following 16 codewords, each a pair of decision words:

\[
\mathcal C=
\bigl(\{0,15\}\times\{0,1,14,15\}\bigr)
\;\cup\;\{(1,15),(14,15)\}
\;\cup\;\bigl(T\times\{0\}\bigr).
\]

For source blocks (x,y), retain the index of a pair (a,b) minimizing
L(x,a)+L(y,b), breaking ties by lexicographic pair order. On R=0 emit a_O;
on R=1 emit b_O. The last decoder predicts the emitted bit. This uses 16
parent states and two child states on every execution.

For comparison, the product code {0,1,14,15}^2 has error 9/32. It is a
coordinate permutation of two copies of the known one-block optimal code.
The following integer table grades the joint construction, summing over
all 16 choices of the first source and all 24 block/omission/query routes
for each fixed second source:

| Weight of y | Number of such y | Errors for each fixed y |
|---|---:|---:|
| 0 | 1 | 48 |
| 1 | 4 | 96 |
| 2 | 6 | 134 |
| 3 | 4 | 102 |
| 4 | 1 | 54 |

Consequently the total is
48 + 4(96) + 6(134) + 4(102) + 54 = 1698 errors out of 6144, or 283/1024.
The product code has 1728 errors on the same outcomes. The 30-error
improvement is exact and independent of floating-point optimization.

The [certificate](../experiments/dependency_memory/results/joint_block_certificate.json)
includes all 256 parent assignments, all message occupancies, and eight
block/omission counts. A separate formulation in the tests computes each
coordinate disagreement without the generator's popcount loss formula.
The code was discovered by deterministic greedy codeword addition over
256 candidate decision-word pairs, followed by a swap check. Twelve seeded
local-search starts did not improve this witness. That exploratory search
is not a completeness or optimality argument; the explicit construction
and exact grader are sufficient to establish the stated upper bound.

Concatenating the two-block code gives, for even k, D_k(2k) <= 283/1024.
For odd k, use the one-block code on the leftover block, giving

\[
D_k(2k)\le\frac{283}{1024}+\frac{5}{1024k}.
\]

Therefore every k >= 2 admits an error strictly below 9/32. This comparison
is with independent two-bit-per-block coding; it is not a lower bound for
all separately encoded systems with unequal memory allocations.

## 3. A rational asymptotic upper bound at rate two

The unsigned optimal branch signature is
Y(x)_o = majority(x_j : j != o). It has values 0,15, and T. Values 0 and 15
each have five source preimages; each t in T has one. This distribution
was already established in the scaling audit.

Define a conditional distribution for a reproduction word A given X:

- If the weight of X is not two, set A=Y(X).
- Otherwise, set A=Y(X) with probability 19/24, and set A=0 or A=15
  with probability 5/48 each.

This is a *test channel* for constructing a block code, not a suggestion
to keep independently sampled four-bit words in two bits each. Its output
probabilities are 45/128 for each constant word and 19/384 for each of the
six weight-two words.

On a weight-two source, using a constant decision word increases L from
4 to 6. The source has weight two with probability 3/8. Hence

\[
\mathbb E d(X,A)=\frac14+\frac38\frac5{24}\frac2{12}
=\frac{101}{384}.
\]

Computing H(A)-H(A|X) and cancelling logarithms gives

\[
I(X;A)=\frac{371-40\log_2 5-95\log_2 3}{64}<2.
\]

The strict inequality is equivalent to 2^243 < 5^40 3^95. It is checked
with integers; the approximate value 1.992991229 is for readability only.
Tests independently reconstruct the coefficients of log_2 of every prime
from the rational joint distribution and directly count its expected loss.

Apply the standard finite-alphabet rate-distortion coding theorem to the
uniform 16-symbol source, reproduction alphabet {0,15} union T, and bounded
separable distortion d [@polyanskiywu2016coding]. Choose a fixed rate rho
strictly between I(X;A) and 2. There exist deterministic fixed codebooks
with at most 2^(ceil(k rho)) indices and distortion at most 101/384 + o(1).
For large k, ceil(k rho) <= 2k. Section 1 turns these into valid delayed-query
chains: the updater uses the chosen codeword's bit for R,O, then discards M.
The final decoder never sees the parent index or the other codeword bits.
Thus

\[
\limsup_{k\to\infty}D_k(2k)\le\frac{101}{384}\approx0.263020833.
\]

The optimum sequence actually converges: concatenation makes k D_k(2k)
subadditive, so the elementary subadditive-sequence lemma gives a limit
equal to inf_k D_k(2k). Combined with the existing uniform lower bound,

\[
\frac{129}{512}\le\lim_{k\to\infty}D_k(2k)\le\frac{101}{384}.
\]

The left endpoint is non-strict here: strict finite-k bounds alone do not
justify a strict limit bound. The exact asymptotic distortion at rate two,
and the exact two-block optimum, remain unknown.

## 4. Exact threshold for vanishing excess error

Let h_* = 4 - (5/8)log_2 5. This section characterizes the asymptotic rate
needed for D_k(B_k) to tend to 1/4, without assuming unsigned decoders in
the converse.

### Converse

Fix any deterministic chain with excess error delta. Use the definitions
from the [scaling audit](PROOF_AUDIT_2026-09-18.md). A block is good when
all four decoder pairs are complementary. Every other block has excess
error at least 1/48, so the fraction of bad blocks is at most 48 delta.

In a good block r, the required signature Y_r has entropy at least h_*,
by the existing analytic antipodal-fiber lemma. Its prediction from M has
error probability p_r <= 12 delta_r. Assign auxiliary p_r=0 on bad blocks.
Conditional error entropy gives H(Y_r|M) <= h_2(p_r)+p_r log_2 15.
For 0 <= delta <= 1/48, concavity and monotonicity of h_2 below 1/2 imply

\[
\frac{B_k}{k}\ge\frac1k\sum_r I(X^{(r)};M)
\ge h_*(1-48\delta)-h_2(12\delta)-12\delta\log_2 15. \tag{1}
\]

The first inequality uses source independence and H(M) <= B_k; it does
not assume separate encoding. The right side tends to h_* as delta tends
to zero. Therefore D_k(B_k) -> 1/4 requires liminf B_k/k >= h_*.
For any fixed rho < h_*, continuity in (1) gives a positive gap uniformly
in k whenever B_k/k <= rho. Independent randomization cannot avoid the
bound: fix a full random tape with loss no greater than its average and
the same hard state capacity.

### Achievability above the threshold

For unsigned signatures, H(Y)=h_* and the signatures are independent
across blocks. For eta>0 the set

\[
\mathcal T_m=\{y^m:-\log_2 P(y^m)\le m(h_*+\eta)\}
\]

has at most 2^(m(h_*+eta)) elements. Store its index when present; otherwise
use one additional overflow state and a fixed all-zero reconstruction.
This is a hard state-count code even on overflow. The variance of the
single-signature information is V=(15/64)(log_2 5)^2. Chebyshev's inequality
gives P(Y^m outside T_m) <= V/(m eta^2). The increase in normalized loss
is at most this probability, since the per-block loss is bounded by one.
For every rho>h_*, taking m=k and eta<rho-h_* proves achievability at rate
rho. This is the standard almost-lossless typical-set construction,
applied to the already derived signature distribution.

### Achievability at the exact asymptotic rate

To avoid silently allowing extra o(k) bits, set B_k=floor(k h_*),
eta_k=k^(-1/4), and, for sufficiently large k,

\[
m_k=\left\lfloor\frac{B_k-1}{h_*+\eta_k}\right\rfloor.
\]

Encode only the first m_k signatures by the construction above. Its
at most 2^(m_k(h_*+eta_k)) + 1 states fit within 2^B_k, because the exponent
is at most B_k-1. On any unencoded block emit zero. The set of unencoded
blocks is fixed publicly, independent of the instance. The chain error is
bounded by

\[
\frac14+\frac{m_k}{k}\frac{V}{m_k\eta_k^2}
         +\frac{k-m_k}{4k},
\]

which tends to 1/4: m_k/k -> 1 and k eta_k^2 -> infinity. Small k can use
any admissible code. Hence floor(k h_*) bits suffice asymptotically.
This does not contradict the finite exact 3k requirement: a vanishing
fraction of overflow/unencoded cases is allowed, and exact target error
is never asserted at a finite k with fewer than 3k bits.

## 5. Literature comparison and novelty boundary

The [previous focused comparison](SCALING_LITERATURE_CHECK_2026-09-19.md)
already attributes signature compression and information direct-sum
arguments to established work. This extension adds two primary readings,
checked September 21, 2026:

- Polyanskiy and Wu's [MIT 6.441 notes](https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/pages/lecture-notes/):
  Chapter 7.1's fixed-length almost-lossless setup; Chapter 24, Theorems
  24.1-24.2 and the Section 24.2.1 codebook construction. These supply the
  standard entropy and rate-distortion foundations. Neither joint-coding
  gains nor the distinction between support size and entropy is new.
- Basu, Seo, and Varshney, [arXiv:2204.02586v2](https://arxiv.org/html/2204.02586v2):
  Sections II-A4 and V-B, Theorems 9-10. Their cascade codec also re-encodes
  a received message without rereading the source. They study asymptotic
  descriptions of function sequences with distortion constraints. The
  checked formulation has no intervening random block/omission followed
  by a single-bit replacement before the final coordinate reveal. A
  direct reduction preserving that timing and hard child capacity remains
  to be established. The entire paper's proofs were not audited here.

**Candidate contribution:** the explicit non-product finite witness, a
certified rational upper bound for this delayed-query family, and its
particular exact-versus-asymptotic threshold, together with the earlier
local lower bounds. These are new additions to this repository. This
targeted reading does not certify publication novelty or exclude an
equivalent construction under different terminology. The distinction of
models above is our comparison, not a theorem asserted by those sources.

## 6. Verification, handoff, and next research decision

The [generator](../experiments/dependency_memory/joint_coding/coding.py)
uses only standard-library integer/rational arithmetic for every certified
comparison. Floating-point logarithms appear only in display text. The
[tests](../experiments/dependency_memory/joint_coding/test_joint_block_coding.py) check
all 6144 finite outcomes, the five-row aggregate, the product control,
message/block/complement symmetries, invalid capacities, signature fibers,
and the rational channel's prime-log coefficients. Routine repository
validation regenerates both the certificate and report in memory.

The new code lives in a separate `joint_coding` package. The historical
revision/transfer plans fingerprint all top-level Python files in the
parent directory; keeping the unrelated mathematics in its own package
preserves those plans and completed-run records byte for byte. No historical
plan was regenerated and no source-fingerprint comparison was relaxed.

```powershell
python experiments/dependency_memory/joint_coding/coding.py
python -m unittest discover -s experiments/dependency_memory -v
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

Completed September 21: all 260 tests pass; the repository validator passes,
including the unchanged historical study fingerprints and saved-run audits;
the manuscript builds with 22 cited sources. The unchanged 171,798,901-case
native one-block search was not rerun in this phase; its existing certificate
and witness checks remain part of normal validation.

The finite witness is fully executable. The long-block bounds are analytic
existence results, with no practical encoder complexity guarantee, no model
experiment, and no token or dollar equivalence. The new proofs are a local
review by the same assistant, not independent external review.

Next, seek a matching converse or a tighter certified interval for rate
two, first comparing cascade/functional-compression formulations. A full
rate-distortion optimization must allow arbitrary branch decoder pairs;
optimizing unsigned signatures alone cannot certify the unrestricted
optimum. For empirical work, retain the separately required binding child
boundary and executed downstream policy. Nothing here justifies extending
the completed reminder-only model study or treating an upper bound as a
measured agent improvement.
