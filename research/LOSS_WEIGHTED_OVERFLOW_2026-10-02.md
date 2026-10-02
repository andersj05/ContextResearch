# Loss-weighted overflow and finite public allocations

October 2, 2026. Local deduction, implemented finite codes, exact finite
checks and preserved unsuccessful offline search. Claim C74. External
correctness and priority review remain open.

The unchanged uniform iid four-bit source and independent uniform R/O/J law
admit a stronger finite certificate using the C72 actors. Weight the overflow
event by the loss it actually adds, then minimize this outward bound over
every integer public oracle allocation for five declared Chernoff exponents.
At k=768, the resulting code has error at most
8578395865937/31250000000000, or 27.450867% rounded upward. This is below
C69's exact repeated-six error 2304567/8388608, or 27.472579%.
At k=12288, the new upper bound is 270646703203513/10^15.

The three smaller checked lengths still provably lose to C69. At seven
checked lengths k>=192 the new code's upper bound is below the base-error
lower bound of C72's named previously selected code. This proves an actual
comparison with that code, beyond merely tightening its certificate.
It does not prove dominance over every C72 allocation or global finite
optimality. At k=96, the new and named old code have the same allocation.

No new quantizer is deployed. All 384 inspected group-quantizer starts fail
the stronger C72 entropy/distortion comparison. They remain preserved with
exact grading and original-byte provenance. Generic Chernoff bounds,
entropy-constrained quantization and public time sharing are established.
Zero new model calls and zero natural episodes.

## 1. Implementation, envelope and unchanged channels

[Bounds and allocation](../experiments/dependency_memory/weighted_overflow/bounds.py),
[actor wrapper](../experiments/dependency_memory/weighted_overflow/codec.py),
[independent certificate](../experiments/dependency_memory/weighted_overflow/certificate.py)
and [tests](../experiments/dependency_memory/weighted_overflow/test_weighted.py)
produce [the complete result](../experiments/dependency_memory/results/weighted_overflow_2026-10-02.json).
The old [C72 code and certificate](COORDINATED_TIE_CODE_2026-10-02.md),
[C71 scalar code](HARD_CAP_ENTROPY_CODE_2026-10-02.md),
[C69 six-block control](CONDITIONAL_SIX_BLOCK_CODE_2026-10-02.md) and
[C73 convergence family](DETERMINISTIC_NEAR_LIMIT_CODE_2026-10-02.md) remain
unchanged.

Let k=ng. The first ag blocks use the eight-response majority oracle; the
remaining n-a groups use the old compatible constant-completion quantizer.
For the finite comparison g=8, and a is chosen publicly before X. The exact
arithmetic interval and odd midpoint code are C72's original functions:
2k parent bits include one regular/fallback flag; the child is one bit
chosen after R/O and before J. The final actor receives only Z/R/O/J.
The fallback parent is zero and its public response is zero.

Public source-law/design/length/phase information precedes X. Source,
old parent after the child, output list, histogram, intervals, temporary
workspace, archive, environment and provider history do not cross the
declared boundary. Stage-local exact computation is allowed and discarded.
These are trusted pure-function actors, not an isolated execution of
untrusted agents.

The discovery protocol declares lengths 384/768/1536/3072/6144/12288 and a
262144-byte public-table envelope. The certificate also retains the existing
96/192 controls. Deployed fixed-eight response/count data stay at 1288 packed
bytes. Public n/g/a, program/runtime/framing and workspace are separate.
The large discovery maps are unused by the actors. Bits, table bytes, Python
RAM, tokens and provider cost are different resources.

## 2. Weight overflow by excess loss

For independent source segments i of size g_i, write p_i for their output
label probability and

\[
 I_i=-\log_2 p_i,\qquad
 \delta_i={L(X_i,F_i)-L(X_i,A_i)\over12g_i}\ge0.
\]

L counts routed errors across omissions and allowed queries, and F_i is a
fixed public fallback word. C72's nearest constants and the majority oracle
satisfy this nonnegative excess condition for every source. Their ideal
population error is D_0.

If the arithmetic interval has probability at least 2^{-(2k-1)}, its width
contains an allowed odd midpoint, including the half-open interval convention.
Thus actual fallback is contained in
B={sum_i I_i>2k-1}. The actual code error satisfies

\[
 D_0\le D_{\rm code}
 \le D_0+\mathbb E\left[
       \sum_i{g_i\over k}\delta_i\,1_B\right]\le {1\over2}.
\]

The final cap follows source by source from the fixed fallback; its
unconditional error is one half. Actual fallback can depend on label order
and interval position, so neither B's probability nor its weighted loss is
asserted equal to actual fallback behavior.

For t>0 define M_i=E[p_i^{-t}] and W_i=E[delta_i p_i^{-t}]. Independence and
1_B <= 2^{t(sum_i I_i-(2k-1))} give

\[
 \mathbb E[\delta_{\rm total}1_B]
 \le 2^{-t(2k-1)}
    \sum_i {g_i\over k}W_i\prod_{j\ne i}M_j.                 \tag{1}
\]

This is the established exponential-moment argument with a loss weight.
C71 already used conditional excess with exact scalar binomial statistics;
(1) extends the weighted calculation to coordinated group cells without
claiming a new generic concentration inequality.

## 3. Exact cell weights and outward arithmetic

For low groups, independently enumerate forced-zero, forced-one and tied
statuses. A status with f forced coordinates has mass 5^f 6^{g-f}. The old
public priority assigns its first compatible binary word. For each
forced-one coordinate, four weight-three sources save six errors relative
to zero and one weight-four source saves twelve. Hence conditional excess
is 36/5 per forced-one coordinate. Tied coordinates save zero. Accumulate
integer loss sums Delta_y in each cell; the factor five divides every
relevant category mass.

For N=16^g, counts c_y and t=1/s,

\[
 M_L=\sum_y(c_y/N)^{1-1/s},\qquad
 W_L=\sum_y{\Delta_y\over12gN}(N/c_y)^{1/s}.
\]

Literal routed populations at g=1/2/3 independently verify both counts and
Delta_y. Their sum is 12gN(3/16), the difference between fallback error 1/2
and nearest-constant error 5/16.

For the scalar oracle, two fibers have size five and six have size one.
Across all 16 sources their excess sums are respectively 36 and 12:

\[
 M_H=2(5/16)^{1-1/s}+6(1/16)^{1-1/s},\quad
 W_H={3\over16}(16/5)^{1/s}+{1\over16}16^{1/s}.
\]

The 256 source/fixed-fallback combinations independently check that these
sums hold for every unsigned fallback word, although deployment uses zero.
All root enclosures use the unchanged C72 integer root helper at 64 bits.
Moments round upward and the threshold rounds downward. No floating-point
admission or probability estimates enter the proof.

For n groups and a oracle groups, (1) becomes

\[
 U_a={1\over T}\left[
 {a\over n}W_H M_H^{ag-1}M_L^{n-a}
 +{n-a\over n}W_L M_L^{n-a-1}M_H^{ag}\right],\quad
 T=2^{(2ng-1)/s}.
\]

Terms with zero coefficient are omitted, so no negative moment powers are
used in the outward product argument. The numeric bound is
min(1/2,5/16-a/(16n)+U_a).

## 4. Minimize the outward bound over all public allocations

For each of s=8/16/32/64/128, factor the *outward* moments:

\[
 A={M_L^n\over T},\quad B={M_H^g\over M_L},\quad
 u={W_L\over M_L},\quad v={W_H/M_H-u\over n},
\quad
 F_a={5\over16}-{a\over16n}+AB^a(u+av).
\]

These ratios algebraically factor the product of already rounded moments;
they are not independently asserted upper bounds on ratios of exact moments.
The certificate checks B>1, u>=0 and v>=0 for all six supported g values
1/2/3/4/6/8 and all five s values. Then

\[
 F_{a+1}-F_a=-{1\over16n}
  +AB^a[(B-1)(u+av)+Bv]
\]

is increasing in a. Binary search finds the smallest unrounded F_a minimum
over every a=0,...,n, checking both neighbor signs. The selected code
minimizes the clipped bound among these five plans. This is a complete
allocation search for the five stated outward bounds, not a search over
every exponent, every codebook or actual risk.

Independent complete allocation lists for six small n/g settings validate
the convex search. Forty minima retain every exponent at eight lengths.
Another forty calculations grade C72's old multiplier grid using the new
weight, ensuring a fair unchanged-code comparison.

| k | New a | Selected s | Error upper, percent rounded upward | Compared with C69 |
|---:|---:|---:|---:|---|
| 96 | 5 | 8 | 29.175773 | provably loses |
| 192 | 12 | 8 | 28.277062 | provably loses |
| 384 | 28 | 8 | 27.756417 | provably loses |
| 768 | 59 | 8 | 27.450867 | provably improves |
| 1536 | 123 | 8 | 27.285448 | provably improves |
| 3072 | 250 | 8 | 27.190703 | provably improves |
| 6144 | 510 | 16 | 27.116024 | provably improves |
| 12288 | 1030 | 16 | 27.064671 | provably improves |

Every displayed improvement uses an upper bound below the control's exact
error, or below a named old code's base-error lower bound. The new bounds
at k>=768 also lie below both named C71 codes' base errors. Uncertainty
between the new base and upper bounds remains; no exact large-code average
or fallback probability is measured. The new public finite selector's actual
asymptotic limit is not established. C72/C73's earlier family limits retain
their own original schedules.

## 5. Preserved failed quantizer search and prior work

[Original protocols, C programs and compressed records](../experiments/dependency_memory/weighted_overflow/discovery/README.md)
retain 192 fixed-response starts: g=3 with the eight and all-sixteen response
alphabets and g=4 with eight responses. Eight slopes and eight initializations
were inspected. A stated conditional extension then inspected 192
centroid-updating starts at g=3/4, twelve slopes and eight initializations.
All complete population maps, integer loss sums, trajectories and original
JSON hashes survive; decompression restores the actual original bytes.
This is post-hoc mathematical discovery, not independent empirical trials.

The centroid rule is elementary for this loss: within each cell and block,
bit O is one iff twice the cell's number of source ones outside O exceeds
three times cell mass. Ties choose zero. This instantiates established ECVQ.
On October 2 the original Chou/Lookabaugh/Gray Section III, printed pp. 33–35,
including the three alternating minimizations and Figure 3, was read
[@chou1989entropy]. The prior source note already covered Introduction/
Section II. This remains bounded primary reading, not a whole-paper review.
Primary: [Stanford-hosted original paper](https://web.stanford.edu/class/ee398a/handouts/papers/Chou%20-%20EC%20VQ.pdf).

For a safe fallback, choose the original largest-occupancy output word,
ties by smallest packed integer. Redirect any source whose assigned group
loss exceeds this word's loss into that cell. This cannot increase loss;
moving mass into a largest cell majorizes the old count vector and cannot
increase entropy. The corrected fixed map is public before X, not an
instance-selected fallback.

The independent checker grades 11403264 group-source assignments with the
literal omission/query scalar matrix. Root-free outward log bounds enclose
every corrected map's entropy. Each non-oracle point provably lies above
the old C72 fixed-eight/oracle chord. All low/high rate-two interpolations
between discovered points and an explicit oracle are lower bounded as well;
the best remains above 0.269293075343. Thus these maps do not improve that
ideal entropy/distortion comparison. Their scores are not executed hard-cap
codes, global quantizer optima or evidence that larger groups cannot help.
No positive result is inferred from exploratory floating displays.

## 6. Execution, local runtime and limits

Thirteen complete small actor populations execute 915840 final queries,
checking actual fallback, the length-event upper bound and weighted excess.
Nine constructed larger inputs execute 540 final diagnostics; they do not
stand in for whole-source populations. The finite guarantees instead use
the derivation and outward arithmetic.

[Saved local timing samples](../experiments/dependency_memory/weighted_overflow/local_timings_2026-10-02.json)
separate cold public planning from warm actors. One Python 3.14.2 Windows
sample per input records wall and process CPU time, with code and input
hashes. At k=12288 public planning took 31.651 seconds wall, 30.984 seconds
process CPU. Three constructed encodes took 0.022–0.044 seconds wall;
last-block updates took 0.000013–0.320 seconds. The fast fallback case is
included. These are single local samples, not population latency, portable
speed, an optimized arithmetic implementation or a model/cost result.

The result preserves all upstream code/result bindings and closes no
external review or novelty question. Useful coding near C67's unchanged
26.189898% limit remains open, as do other source/query laws and natural
agent/model/token/provider-cost benefits. Research commands add no
prospective untouched workflow episodes.

Validation: all 583 offline tests pass, including eight new scientific checks.
Repository validation reports PASS with 74 claims, 55 bibliography entries,
171 PDF hashes and 195 immutable import hashes. The paper builds with 48
cited sources. All 29 new code/provenance bindings match. Earlier claim and
decision prefixes and all 76 original coding-package/result files retain
their actual bytes.

Offline reproduction:

    python -m experiments.dependency_memory.weighted_overflow.certificate
    python -m unittest experiments.dependency_memory.weighted_overflow.test_weighted -v
    python -m unittest discover -s experiments/dependency_memory -v
    python scripts/validate_context_repo.py
    python scripts/build_paper.py

The benchmark is a separately saved measurement, not rerun by the deterministic
certificate. Running benchmark.py again would create a new measurement and
require regenerating its dependent certificate; original scientific records
should be preserved before any such extension.
