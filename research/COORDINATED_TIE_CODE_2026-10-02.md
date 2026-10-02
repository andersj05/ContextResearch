# Coordinating tied answers improves hard-cap coding

October 2, 2026. **Local construction, restricted pair optimum, exact finite
upper bounds and an analytic polynomial code-family limit.** Claim C72.
External correctness and publication priority remain open. Zero new model
calls or prospective natural episodes. The underlying entropy quantization,
weighted greedy set cover, prefix/arithmetic coding and time sharing are known.

The [implemented code](../experiments/dependency_memory/tie_coding/README.md)
coordinates equally good constant responses. A fixed eight-block design has
actual limiting error in **[0.269293075342,0.269293075343]**, below
[C71](HARD_CAP_ENTROPY_CODE_2026-10-02.md)'s scalar 27.075301% limit. At k=12288,
the implemented code has error **at most 27.080384%**, below both named C71
codes' base-error lower bounds. A separate growing-group polynomial family
has actual limiting error **[0.267829178707,0.267829178708]**. It remains above
[C67](UNRESTRICTED_RATE_CURVE_2026-10-02.md)'s 26.189898% optimum.

These are uniform bit-model results. The fixed-eight public table is 1288
packed bytes versus C71's 10; instance bits, public data, program/runtime,
framing, tokens and cost are different quantities. Selected smaller finite
designs lose. No useful-agent or provider performance result follows.

## 1. Source timing and equally good responses

X has k=ng uniform iid four-bit blocks. R is a uniform independent block;
O is a uniform omission. Parent M is formed before R/O with at most 2^(2k)
states. The updater has only M,R,O and public n/g/a/tables and emits one bit
Z before J, which is uniform among the remaining three coordinates. Final
prediction is Z, with only Z/R/O/J access. Source, old parent, output lists,
archives, environment and provider session channels are excluded after their
boundary. Public programs, design/count parameters and tables precede X.
Temporary exact computation within a stage is allowed and discarded.

For constant response words 0/15, source weight below two forces zero and
weight above two forces one; weight two permits either at identical loss.
Their source-class sizes are 5,5,6 out of 16. Choosing any compatible constants
gives the same per-source average omission/query loss and overall error 5/16.
Coordinate those choices within each g-block group. Full majority response
signatures on other groups still give 1/4 error. The public oracle-group count
a is fixed before X; no per-instance allocation or histogram is free.

## 2. A weighted cover and an exact restricted pair optimum

Each group source has a ternary status pattern: forced zero, forced one or
tie. A pattern with f forced positions and e=g-f ties represents 5^f*6^e
uniform source words. A binary completion is compatible if it matches every
forced position. Greedy repeatedly selects the completion covering the largest
remaining source mass, ties by smallest binary word, and assigns all its
remaining compatible patterns. The implemented public builder uses 3^g
patterns and 4^g total incidences; it does not enumerate 16^g source words.
Every label retains at least 5^g mandatory fully forced sources.

For g=2, every completion has mandatory mass 25 and can cover at most 121
sources. Therefore every possible sorted output-mass vector is dominated
by [121,85,25,25]: its largest entry is at most 121, and the lower bounds 25
give top-two/three bounds 206/231. Greedy priority (0,3,1,2), using bit 0
as the first block, attains exactly this vector. Entropy is Schur concave,
so this is the minimum output entropy among all compatible constant-pair
choices, including assignments not expressible as a priority. It is a
restricted equal-loss quantizer optimum, not a global rate-distortion optimum.
All 24 priority orders separately calibrate the finite mechanism; they are
not enumeration of all arbitrary source assignments.

Independent weighted recounting verifies every greedy choice for
g=1,2,3,4,6,8. Literal source populations at g<=3 confirm the counts and 5/16
error. The pair entropy is

\[
H_2=8-\frac{121\log_2 121+85\log_2 85+50\log_2 25}{256},
\]

about 1.694635 bits per pair, below two scalar constant quantizers' 1.792076.
The fixed-eight group has entropy per block in
[0.770971385668,0.770971385669]. Larger greedy groups are not proved optimal.

## 3. Compatible completion entropy tends to 5/8 per block

Let E be the group erasure/tie mask and T its ternary status. Independently
per position, erasure probability is 3/8 and a nonerased sign is fair. Any
compatible completion Y determines T together with E. Thus

\[
H(Y)\ge I(T;Y)\ge H(T)-H(E)=5g/8.
\]

This covers even an output chosen using extra source detail within each
status class. It does not optimize quantizers allowed to increase source-wise
constant loss or change the decoder family.

For an upper bound, randomly order the 2^g completions publicly before source,
and assign the first compatible one. If K positions are forced, there are
2^(g-K) compatible completions. The first compatible rank J has mean
(2^g+1)/(2^(g-K)+1)<=2^K over the random order. Jensen therefore gives
average E log2 J<=E K=5g/8. Some fixed order satisfies that inequality.
For that order, rank and completion are bijective labels.

An established prefix description of positive rank j writes its binary
length L with floor(log2 L) leading zeros followed by the bits of L; it then
appends j's L-1 trailing bits. Its length is
floor(log2 j)+2floor(log2(floor(log2 j)+1))+1, at most
log2 j+2log2(g+1)+1. The description is self delimiting, so its mean length
upper bounds output entropy. Consequently the optimal compatible cover
entropy H_opt obeys

\[
5g/8\le H_{\rm opt}\le5g/8+2\log_2(g+1)+1.
\]

Cardinal, Fiorini and Joret's published greedy guarantee applies to these
rational weighted covers: H_G<=H_opt+log2(e). We use that result as prior
work, not a new approximation theorem. Hence **H_G/g ->5/8**. This is an
analytic deduction for the specified compatible-completion source. Finite
rank means and prefix Kraft sums are checked independently; no random-order
or all-g source population is claimed physically enumerated.

## 4. Charged arithmetic parent and the two code limits

Use full majority signatures on the first a public groups, encoded as ag
scalar symbols with counts (5,1,1,1,1,1,1,5)/16. The other n-a groups use the
greedy completion symbols with counts c_y/16^g. Exact arithmetic subdivision
gives their complete response sequence an interval of product length P.
Select its least odd grid numerator over 2^(2k); its index needs 2k-1 bits.
Charge one regular flag inside the remaining bit. If no point fits, emit
M=0 and all-zero responses. No interval/output/source statistic survives
alongside M. The selected-prefix updater reconstructs a high response's O
bit or a low completion's R bit, emits only Z and discards its workspace.
Usable messages number at most 2^(2k-1)+1, within the common cap.

The quantizers minimize their permitted response loss source by source.
All-zero fallback therefore has nonnegative excess, and success retains
the exact selected response. Failure is contained in
B={P<2^(-(2k-1))}. With D_0=5/16-a/(16n),

\[
D_0\le D_{n,g,a}\le \min(1/2,D_0+\Pr(\mathcal B)).
\]

The 1/2 cap also follows source by source from comparison with the zero
response, followed by uniform-source averaging.

Let h_8=4-(10/16)log2 5 and H_G be the group's completion entropy.
The public planner uses outward rational entropies of increasing precision,
64+8(g+bit_length(n)) bits. At fixed g and positive margin multiplier c it
chooses the largest a satisfying the upper-entropy constraint
a*g*h_8+(n-a)*H_G<=2ng-c*ceil(sqrt(n*bit_length(n))), with the entropy
quantities replaced by their certified upper bounds. If even a=0 cannot
meet this slack, it uses a=0; the frame remains valid. At fixed g, rounding
vanishes and the margin is sublinear. Independent bounded information
summands and Chebyshev make Pr(B) vanish. The actual fixed-group code tends to

\[
D_g=\frac5{16}
 -\frac{2g-H_G}{16(gh_8-H_G)}.
\]

For fixed g=8, the exact outward enclosure is
[0.269293075342,0.269293075343], about 26.929308%.

For a separate growing family, choose
g(n)=max(1,floor(bit_length(n)/4)), k=n*g(n), and margin multiplier 4g(n).
For n>=8, 16^g<=2n, so the weighted builder, public tables and increasing
precision entropy planner all have polynomial size/bit complexity. The
encoder and updater have polynomially many steps on O(k)-bit integers;
arbitrary unbounded g without this schedule would be exponential in g.
This is not a portable speed or total-RAM measurement.

Low-group information ranges by less than 2g bits, and high scalar information
ranges by less than three. Thus variance is at most (13/4)ng^2. The growing
margin m=4g*ceil(sqrt(n*bit_length(n))) has m/(ng)->0 and makes
Var/(m-1)^2->0. The entropy constraint holds eventually and rounding vanishes.
Since H_G/g->5/8, actual risk tends to

\[
D_{\rm grow}=\frac5{16}
 -\frac{2-5/8}{16(h_8-5/8)}
\in[0.267829178707,0.267829178708].
\]

This is a deterministic, implemented polynomial family and a proved limit
along k(n), not an exact finite optimum, a guarantee of efficient approach
to C67 or physical execution of the asymptotic sequence. Its growing public
table/framing descriptions are separate from instance value bits.

## 5. Exact finite upper bounds and controls

For t=1/s and source self-information S, Markov gives
Pr(B)<=2^(-t(2k-1)) M_H(t)^(ag) M_G(t)^(n-a), where
M_H=sum p_H^(1-t) and M_G=sum p_G^(1-t). Outward integer s-th-root
enclosures compute every moment and threshold as rationals. No float enters
admission or proof. Checked exponents are s=8,16,32,64,128. The minimum
certified tail plus D_0 gives a conservative risk upper, not exact failure
probability or exact large-code risk.

Forty inspected margin designs use multipliers 2,3,4,5,6 at eight lengths.
The best *bound* at each length is below; it does not minimize actual risk.

| k | Public margin multiplier | Oracle groups a | Conservative risk upper |
|---:|---:|---:|---:|
| 96 | 5 | 5 | 0.311200937890 |
| 192 | 6 | 11 | 0.285831292575 |
| 384 | 6 | 26 | 0.279197312230 |
| 768 | 5 | 57 | 0.275541733985 |
| 1536 | 4 | 121 | 0.273252699729 |
| 3072 | 4 | 248 | 0.272170067994 |
| 6144 | 4 | 506 | 0.271381270318 |
| 12288 | 4 | 1025 | 0.270803837006 |

At the four larger lengths these upper bounds lie below **both C71 codes'
base-error lower bounds**, proving actual improvement over those codes,
as well as C69's repeated six-block code. At the four smaller lengths, the
selected designs' lower bounds already exceed C69 and the better named C71
code's upper bound: those selected actual codes provably lose. Not all forty
designs have that negative certificate. Their conservative selection does not
rank actual risk among overlapping intervals. All lengths are multiples of
six, permitting the same C69 cap/timing comparison.

Fixed-eight public data are 256 g-bit priority labels plus 256 counts of 4g bits each,
1280 packed bytes, and eight oracle word/count bytes: **1288 bytes** total.
This increase over C71's 10 bytes must stay visible. Program/runtime, public
n/g/a, framing and the variable-g family's growing tables are separate.

## 6. What was executed, prior work and remaining scope

All g<=3 literal quantizers execute 153792 final queries. Thirteen complete
small arithmetic populations (25888 source assignments) execute 915840 queries.
The g=1 arithmetic code agrees exactly with C71 for every small source/public
a. Independent fraction intervals verify first legal midpoints and framing.
Fifteen constructed fixed/growing inputs execute 1008 additional diagnostic
queries. Those spots do not grade large uniform-source averages. Weighted
source types, integer root enclosures and the whole-population proof justify
the large bounds. Seventeen bindings preserve original C71/C67/C69 evidence.

The [discovery record](../experiments/dependency_memory/tie_coding/discovery/README.md)
retains the failed first search, 486 revised float maps, six group probes
and forty finite margin designs. All saved pair maps' counts/loss independently
rescore; larger-group optimality and every float trajectory are not certified.
Compressed pair JSON preserves its original bytes on decompression. A
scratch bound script imports evolving code rather than a frozen runtime.

On October 2, Cardinal/Fiorini/Joret's
[author manuscript](https://gjoret.be/papers/entropy-setcover.pdf), Introduction,
Section 2/Theorem 1 and weighted extension, plus Lemma 2's statement, printed
pp. 1–5, were read. Joret's [publication list](https://gjoret.be/publications.html)
corroborates Algorithmica 51(1):49–60, 2008. Bounded reading only, not full review,
replication or priority certification; key cardinal2008entropy.
[C71](HARD_CAP_ENTROPY_CODE_2026-10-02.md)'s Chou reading remains bounded prior
work. Greedy minimum-entropy cover, quantization, tie selection, prefix coding,
arithmetic intervals and time sharing are established.

The local addition is the compatible-answer reduction, scoped pair optimum,
implemented cap/complexity result and concrete fixed/growing-family bounds.
Other source/query laws, general quantizer/finite optimality, efficient codes
reaching C67, external correctness/priority and natural-agent/model/token/
credit/production benefit remain open. Provider allocations and the untouched
natural-task denominator remain unchanged.
