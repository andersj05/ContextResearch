# An implemented arithmetic parent with a hard value-bit cap

October 2, 2026. **Local construction, exact finite upper bounds and an
analytic code-family limit.** Claim C71. External correctness and publication
priority remain open. Zero new model calls or prospective natural episodes.
Entropy-constrained quantization, arithmetic intervals and time sharing are
established. This note instantiates them in the uniform delayed-query model
with a charged fallback and complete information timing.

The default implemented family has limiting error about **27.075301%**, below
the [C69 repeated six-block construction](CONDITIONAL_SIX_BLOCK_CODE_2026-10-02.md)'s
27.472579%. A separate simple public schedule at k=12,288 has error at most
**27.198892%** at the same 2k parent bits and one child bit. This finite number
is a conservative upper bound, not an exact large-population risk. Four
checked smaller lengths provably lose. The new family still stays above
[C67](UNRESTRICTED_RATE_CURVE_2026-10-02.md)'s optimal 26.189898% limit.

## 1. Model and public quantizers

X consists of k uniform iid four-bit blocks. R is an independent uniform block;
O is a uniform omission. Form M before R/O, with at most 2^(2k) states.
The updater sees only M,R,O and public k/a/tables, emits one bit Z and discards
M and its workspace. J then arrives, uniform among the remaining coordinates.
The final actor sees only Z,R,O,J and predicts Z. Source, parent, archives,
environment and provider sessions cannot be reread after their boundary.
Public descriptors and fixed tables are free in this value-bit model. Bits,
packed table bytes, program/runtime, framing and model costs are distinct.

Choose a public integer a before X. The first a blocks use majority response
signatures, while the other k-a use the two constant response words. A response
word's bit O is its one-bit updater answer; these four counterfactual answers
are not four retained child bits. Both quantizers see X before M and receive
no realized R/O/J. The two-word tie at source weight two chooses zero.

| Quantizer | Public response words | Uniform-source output counts, out of 16 | Queried-bit error |
|---|---|---|---:|
| Two constants | 0,15 | 11,5 | 5/16 |
| Majority signatures | 0,3,5,6,9,10,12,15 | 5,1,1,1,1,1,1,5 | 1/4 |

All 16 sources and 12 omission/query routes independently calibrate these
counts and errors. The response/probability tables have twenty four-bit entries,
**10 packed public data bytes**. Source-to-response rules and schedule code
are program data; k/a and framing descriptions are separate public metadata.
There is no learned per-instance histogram or uncharged allocation choice.

## 2. A fixed grid and a charged fallback

Map each source through its assigned quantizer. Arithmetic subdivision with
the fixed counts gives the resulting response sequence an interval [L,H) in
[0,1). Its length P is the product of its symbol probabilities. Exact integer
recurrences use denominator 16^k; no floating arithmetic participates.

Use the grid of odd numerators j over 2^(2k). Adjacent points are
2^(-(2k-1)) apart. The index m=(j-1)/2 takes **2k-1 bits**, because the final
odd bit is fixed publicly. If the interval contains a grid point, select its
least such j and store a leading regular flag plus m. This uses exactly 2k
bits. If none exists, store M=0 and use the all-zero response sequence.
Only zero is a valid fallback state; nonzero flag-zero states are rejected.
There are at most 2^(2k-1)+1 usable messages, inside the common cap.

The regular updater normalizes j/2^(2k) through the public arithmetic model
up to block R, recovers its response word and emits only bit O. The fallback
updater emits zero. Neither actor receives the interval, quantizer-output list,
source, source histogram or diagnostic record. The final function has only
Z,R,O,J arguments. Temporary exact-integer computation inside a stage is
permitted; its state does not cross the next boundary.

Every half-open interval of length at least one grid spacing contains a point.
Consequently failure is contained in

\[
\mathcal B=\{P<2^{-(2k-1)}\}.
\tag{1}
\]

Some shorter intervals also contain a point, so the length event is an upper
bound on failure, not equality. There is no variable-length parent exceeding
the cap, extra fallback bit, external codebook selector or overflow archive.
[codec.py](../experiments/dependency_memory/entropy_coding/codec.py) implements
the encoder and source-free updater.

The encoder and selected-prefix updater use O(k) arithmetic steps on O(k)-bit
integers. Schoolbook arithmetic gives polynomial bit complexity; the public
planner also uses polynomial-size integer powers and binary search. This is
an implemented algorithm, not an exponentially listed block codebook. It is
not a linear-time bit-complexity, portable runtime or practical-agent claim.

## 3. Exact finite overflow and excess-loss bounds

Let U count balanced signatures among the a majority blocks, and V count
upper outputs among the b=k-a two-word blocks. Independently,
U~Bin(a,3/8) and V~Bin(b,5/16). The interval's unnormalized width is

\[
W=5^{a-U+V}11^{b-V},\qquad P=W/16^k.
\]

Thus (1) is exactly W<2^(2k+1), an integer comparison. U and V increasing
only decrease W. For each V, an exact moving boundary finds the last good U;
binomial tail mass and its first moment then compute the bound in O(a+b)
frontier steps. This compresses a two-dimensional count calculation; it is
not physical enumeration of every source. Each boundary is independently
checked by direct integer powers. Small cases also use literal double sums.

Without overflow the quantizer risk is

\[
D_0=\frac5{16}-\frac{a}{16k}.
\]

For every source, replacing a chosen response by zero weakly increases its
average loss over O/J. Among majority blocks, the conditional excess branch
loss is 2 for a balanced signature and 18/5 for a common signature. For the
two-word quantizer it is zero for the lower output and 36/5 for the upper.
These values are directly calibrated from the sixteen source words.
Conditional on U=u,V=v, the all-zero replacement's expected excess queried-bit
loss is (18a-8u+36v)/(60k). Therefore the actual fixed code satisfies

\[
D_0\le D_{k,a}\le D_0+
\sum_{u,v:\,5^{a-u+v}11^{b-v}<2^{2k+1}}
\Pr(U=u)\Pr(V=v)\frac{18a-8u+36v}{60k}.
\tag{2}
\]

Actual failure may depend on the sequence order and specific constant outputs.
The inequality uses nonnegative per-source excess and the entire bad-length
event; it does not assume failure is independent of those values. All sums
are exact integers/rationals, and reported decimals round outward. Raw mass
and fraction digests supplement regeneration, rather than proving (2) alone.

## 4. A computable schedule and its limiting error

The two output entropies in bits per source block are

\[
h_2=4-\frac{11\log_2 11+5\log_2 5}{16},\qquad
h_8=4-\frac{10\log_2 5}{16}.
\]

Here h_2<1 follows from 5^5*11^11>2^48, and h_8>2 from 5^10<2^32.
Put lambda*=(2-h_2)/(h_8-h_2), approximately 0.667951769316.
For positive k let ell=ceil(log2(k+1)) and m=ceil(sqrt(k*ell)). These are
computed by bit length and integer square root. Choose the largest a satisfying

\[
5^{5(k+a)}11^{11(k-a)}\ge2^{32k+16m}.\tag{3}
\]

This is the mean self-information constraint
a*h_8+(k-a)*h_2<=2k-m with logarithms cleared. Its left side decreases
strictly with a, enabling exact public binary search. Zero is feasible since
m<=k and h_2<1. Maximality gives the reverse strict entropy inequality at a+1,
so a/k tends to lambda* as m/k tends to zero.

The response-sequence self-information is a sum of independent bounded
variables. Both quantizers have range less than three bits per block, so
variance is at most 9k/4. Chebyshev gives
Pr(B)<=9k/(4*(m-1)^2) for m>1. Since m^2/k grows like log k, that probability
tends to zero. No claim about this loose concentration bound's finite utility
is made; (2) supplies the much tighter checked finite bounds. The lower bound
D_0 and upper bound D_0+Pr(B) squeeze the **actual implemented code's** risk to

\[
D_{\rm scalar}=\frac5{16}
 -\frac{2-h_2}{16(h_8-h_2)}.
\tag{4}
\]

Outward rational log bounds give
[0.270753014417,0.270753014418]. This is the limit of the stated output-retention
schedule with vanishing overflow, not the unrestricted
rate-distortion optimum or an optimized entropy-constrained scalar/vector
quantizer. It stays strictly above the unchanged C67 rate-two enclosure.

The earlier public rational schedule a=max(0,floor(2k/3)-ceil(2sqrt(k))) remains
implemented as a control. Its limit is 13/48. The strict entropy margin for
fraction 2/3 follows exactly from 5^25*11^11>2^96. Its finite bounds beat the
new default at some lengths; the better asymptotic default does not dominate
every finite control.

## 5. Checked finite comparisons and execution scope

Both schedules use the same hard-cap encoder/updater and a public pre-source
count. All lengths below are multiples of six, so the C69 repeated code fits
at exactly the same capacity and timing. Its error is 2304567/8388608,
approximately 0.274725794792.

| k | Default a | Default conservative error upper | Rational a | Rational conservative error upper |
|---:|---:|---:|---:|---:|
| 96 | 48 | 0.281603348573 | 44 | 0.283870713233 |
| 192 | 104 | 0.278867101169 | 100 | 0.279976782631 |
| 384 | 220 | 0.276821214734 | 216 | 0.277375032262 |
| 768 | 459 | 0.275226935919 | 456 | 0.275429556595 |
| 1536 | 947 | 0.274021698983 | 945 | 0.274087068355 |
| 3072 | 1935 | 0.273163543701 | 1937 | 0.273131523313 |
| 6144 | 3932 | 0.272520029390 | 3939 | 0.272464393688 |
| 12288 | 7956 | 0.272044632203 | 7970 | 0.271988910419 |

The first four lengths' base-error lower bounds already exceed C69, proving
those actual codes lose. At the other four lengths, both upper bounds are
strictly below C69, proving improvement. The best displayed finite bound
uses the retained rational control. These are sixteen inspected exact bounds,
not independent trials, an optimal schedule search or exact large-code risks.

All sources at k=1,2,3 and every a=0..k are physically checked: **17,184 source
assignments and 608,640 final actor queries**. Each decoded regular sequence
agrees with the independently reconstructed intended interval; observed
fallback probability is bounded by the exact length event. All small valid
parent states and midpoint ties are checked independently of encoder coverage.

Twelve constructed large inputs at k=1536/12288, both schedules and three
source patterns execute another **864 final actor queries** at six declared
positions. They include regular and fallback cases. These are route diagnostics,
not large uniform-population averages. At k=12288 the count-statistic calculation
represents over 34 million U/V cells while each boundary is independently
checked; the full source population has 2^49152 points and is not enumerated.
The complete whole-population upper bound comes from (1)-(2), not from spots.

Eight scientific tests check literal query losses/conditional means, independent
fraction intervals, complete small populations, direct two-dimensional binomial
sums, all finite boundary inequalities, maximal public entropy counts, memory
framing, source-free actors and preserved controls. The
[JSON certificate](../experiments/dependency_memory/results/entropy_coding_2026-10-02.json)
binds fifteen code/provenance files and checks original C67/C69 source bindings.
Full repository verification is recorded in [status](../docs/STATUS.md).

## 6. Discovery, primary-source comparison and limits

The inspected [discovery record](../experiments/dependency_memory/entropy_coding/discovery/README.md)
retains actual prototype codec/checker bytes and all eight initial/revised
probe outputs. The revised scratch script imports evolving production code;
it is not a frozen historical runtime. Joint three-/six-block output-entropy
alternatives have weaker scalar time-share limits in the saved comparison.
The prototype remains a stronger finite control at several lengths. Float
displays selected the direction only; inequalities, bounds and admission use
exact integer/rational calculations. Search is post-hoc development mathematics.

On October 2, Chou, Lookabaugh and Gray's original
[Entropy-Constrained Vector Quantization](https://web.stanford.edu/class/ee398a/handouts/papers/Chou%20-%20EC%20VQ.pdf),
Introduction and Section II, printed pp. 31–33, were read. They distinguish
index entropy from fixed index length and describe time sharing for variable
rate coders. Their average-rate setting does not supply our hard-cap guarantee;
that is derived above. Author/venue/pages are checked against Gray's
[author publication list](https://www-ee.stanford.edu/~gray/publications.html),
entry 68. This is a bounded reading, not full review, replication or a priority
verdict; citation key `chou1989entropy`. Generic entropy coding and time sharing
are direct precedents, and arithmetic coding is established.

The contribution here is a specific implementable model construction and its
checked cap/overflow/error bounds. Other sources/query laws, global optimality,
efficient codes reaching C67, adaptive allocation/inferred dependencies and
natural-agent/model/token/cost benefit remain open. C70's changed-prior and
early-realized-class results remain separate conditions; this phase uses the
original uniform query law. Provider allocations and natural-task counts do
not change.
