# Exact-priced group coding: a small finite gain with larger public data

October 2, 2026. Claim C75. This is a checked finite construction and a
separate limiting-family deduction under the existing uniform bit model.
It is not a model experiment, a global quantizer optimum, a new generic
ECVQ algorithm or a practical-agent result.

The [certificate](../experiments/dependency_memory/results/priced_coding_2026-10-02.json)
gives error at most **54095129871619/200000000000000 = 0.270475649358095**
at k=12288, versus C74's upper bound 0.270646703203513. The new upper
bound is below the named C74 code's base-error lower bound 3325/12288.
That proves an actual improvement over that particular code, despite
neither large code's exact average error being enumerated.

The improvement in upper bounds is about 0.017105 percentage points.
The parent still has exactly 2k bits including its fallback flag, and the
child has one bit before J. Public data are larger: 66513 packed actor
bytes, or **94754 bytes including the finite planner's cell loss weights**,
versus C74's 1288 bytes. Both fit the previously declared 262144-byte
packed-payload envelope. Parameters, framing, program/runtime, JSON,
Python objects/caches, RAM and temporary workspace are separate.

## 1. Evidence and design scope

The [preserved discovery packet](../experiments/dependency_memory/priced_coding/discovery/README.md)
contains eight five-block full-population starts and two six-block starts.
The original conditional protocol and its post-hoc sampled-design amendment
remain distinct. Five-block starts inspect prices 2/5 and 1/2, with a
C69-product warm start and three fixed pseudorandom initializations.
Every five-block target certificate loses to C74 at k=12288.

Before either six-block launch, the amendment replaces expensive repeated
whole-population design updates with one fixed 131072-source pseudorandom
sample. It uses a C69 product and a 16384-word initialization, price 2/5,
and at most 60 updates. The protocol calls the sampling law uniform;
the executed sample is a fixed-seed xorshift construction, not independent
uniform or held-out trials. Sample trajectories and change counts have
sample scope. Each final six-block descriptor instead receives a complete
exact price pass over all 16777216 sources.

The selected six-block book has 7288 distinct response words. Its positive
proposal weights are sampled cell counts multiplied by 128. These weights
define its price rule; they are not its population probabilities. The
separately enumerated actual counts define its arithmetic CDF. This
distinction is material: six-block proposal and actual counts differ.
Book, price, true CDF, planning weights, allocation and public source length
are fixed before the evaluated source X.

Exact full-population quantizer error is 111976409/402653184, approximately
0.278096420070. Entropy per block is enclosed by
[1.737988868032,1.737988868033]. Neither quantity alone is a hard-cap
actor result. Arithmetic coding, fallback and public oracle mixing supply
the finite guarantee below.

## 2. Exact price rule and a safe fallback

For one source group x and response word w, let L(x,w) count errors over
the g blocks and all twelve scalar (O,J) routes. For scalar nibbles,

    L(x,w) = 3|x| + 3|w| - 2|x||w| + 2|x & w|.

This equals the literal omitted/query matrix on all 256 scalar pairs.
For public price a/b and positive proposal weight q_i, select the smallest
book index minimizing

    2^(b L(x,w_i)) / q_i^a.

The [implemented selector](../experiments/dependency_memory/priced_coding/design.py)
uses exact integer comparisons and group bit masks, with no floating price
decision and no full source-assignment table. CDF counts can be zero for
unused proposal words; such cells have zero width and are skipped.

Let F be the first largest-proposal word. If a chosen word had greater
group loss than F, its numerator would be strictly larger and its
denominator no larger. It could not minimize the price. Thus every source
has L(x,A(x))<=L(x,F). The fixed fallback expectation is 1/2 under the
uniform source, even for nonconstant F. Here F is packed word 3840.
This gives a nonnegative fallback excess for the loss-weighted proof.

## 3. Independent complete minimum check

The discovery program evaluates every retained candidate for every source.
Its 199310180352 recorded exact price comparisons are checked finite
operations, not independent observations or trials.

A [separate C checker](../experiments/dependency_memory/priced_coding/discovery/transform.c)
uses the literal twelve-query loss matrix and a tensor min-plus transform.
Initialize cost zero at each response word with its proposal weight and
book index, and infinity elsewhere. At each coordinate, minimize over its
sixteen possible response nibbles while adding the corresponding scalar
loss. Within a fixed nibble, the added cost is common to every candidate,
so it preserves price order and the index tie rule. Induction through g
coordinates gives the same full-group minimum by a different computation.

To order candidates, the checker uses certified floors of
2^32 log2(q_i^a). The real scaled score lies in (G_i-1,G_i], where
G_i=2^32 b L-floor(2^32 log2(q_i^a)). Scores separated by more than
one unit have determined order. Near scores use exact integer crossproducts.
With g<=6 and a<=2, q_i^a<=2^48; a near-score shift is less than 49,
so the declared 128-bit products cannot overflow. Equal scores select the
smallest book index. The Python verifier independently encloses every
public log floor and binds the exact descriptor and complete compared labels.

All **41943040 source assignments across ten starts match**, with zero
minimum disagreements; the transform records 1132736192 comparisons.
Full independent literal-matrix grading also checks losses, CDF counts and
nonnegative fallback excesses. The original comparator calibration checks
1294947 price cases against unrestricted integer crossproducts, plus all
3072 scalar query terms. Four complete tiny tensor controls cover 8464
sources with literal losses and Fraction minima. Another 650 fixed source
probes compare the deployed Python selector with the checked large maps;
this is not a second complete Python argmin enumeration.

Original native programs, protocols, source IDs, terminal records,
descriptors, compressed JSON and original decompressed hashes survive.
Default validation grades the saved records; it does not silently rerun
the native 199-billion-comparison discovery or require a compiler.

## 4. Hard cap and loss-weighted allocation

The [actors](../experiments/dependency_memory/priced_coding/codec.py) use
k=ng+r, r<g. The first ag blocks use the scalar majority oracle; the
remaining n-a full groups use the price book. Arithmetic coding occupies
2ng bits including a charged fallback flag. The tail uses two bits per
block for nearest responses from (0,1,14,15), with exact error 9/32.
These fields always total 2k bits. A failed arithmetic interval emits the
fixed public F on full groups; the tail still decodes normally.

The parent precedes R/O; the child update sees the parent and R/O before J.
The final actor sees only Z/R/O/J. Source, old parent, arithmetic scratch,
output lists, instance histograms, archives, environment/provider history
and source-dependent caches cannot cross a boundary. Public compiled
book caches depend only on the fixed descriptor. Temporary stage computation
is permitted; these are trusted functions, not untrusted-process isolation.

For low cell i with actual count c_i and total nonnegative integer excess
Delta_i, at t=1/s define

    M_l = sum_i (c_i/N)^(1-t),
    W_l = sum_i Delta_i/(12gN) * (N/c_i)^t,
    N = 16^g.

Zero cells contribute zero. C74's checked scalar oracle identity gives M_h
and W_h independently of each coordinate of F. At a public oracle count a,
the full-group base is D_0+(a/n)(1/4-D_0). Loss-weighted overflow is at most

    2^(-(2ng-1)t) [
       (a/n) W_h M_h^(ga-1) M_l^(n-a)
       + ((n-a)/n) W_l M_h^(ga) M_l^(n-a-1) ].

Zero-coefficient terms are omitted. All remaining moment exponents are
nonnegative, so outward moment upper bounds remain valid despite the
factored implementation using ratios. Integer root enclosures and
per-cell upward fixed-point rounding at 64 bits supply those bounds.
The actual large risk lies between the base and this upper bound, clipped
at 1/2; a scalar tail is included with its exact weight.

The raw objective has form D_0+a(1/4-D_0)/n+A B^a(u+a v). Its second
forward difference, apart from a positive factor, is

    (B-1)^2 (u+a v) + 2B(B-1)v.

This is affine in a. Checking endpoints proves discrete convexity for all
eighty recorded plans: fifty target comparisons and thirty plans for the
selected fixed book at six lengths. Binary search uses exact unreduced
integer signs, avoiding rational reduction at each comparison. It minimizes
each raw outward expression over every integer a; five degrees
(8,16,32,64,128) are inspected. This is certificate optimization,
not optimization of actual risk, all exponents or global codebooks.

| k | Oracle groups a | Degree s | Error upper | Below named C74 base? |
|---:|---:|---:|---|---|
| 384 | 4 | 8 | 277407037393019/1000000000000000 | no |
| 768 | 19 | 8 | 274442885546539/1000000000000000 | no |
| 1536 | 51 | 8 | 68194874971801/250000000000000 | no |
| 3072 | 116 | 8 | 135927976823317/500000000000000 | no |
| 6144 | 264 | 16 | 270981980699193/1000000000000000 | yes |
| 12288 | 560 | 16 | 54095129871619/200000000000000 | yes |

All six selected bounds improve the corresponding C74 upper bounds.
At k=6144 and 12288 they also lie below the named C74 base-error lower
bounds, proving actual improvement over those particular codes. At the
other four lengths only tighter certificates are established. The
384-block code still provably loses to exact C69. None of these statements
compares against every old allocation or compensates for the larger tables.

## 5. A separate actual-limit family

The finite five-degree selector does not inherit an entropy-interpolation
limit. Instead [default_count](../experiments/dependency_memory/priced_coding/bounds.py)
implements a separate public schedule. At dynamic outward log precision,
choose the greatest clamped integer a with

    (n-a) H_l,upper + a*g H_h,upper <= 2gn - m_n,
    m_n = 4 ceil(sqrt(n bit_length(n))).

For sufficiently large n the constraint is feasible. The log enclosure
error tends to zero, m_n/n tends to zero, and
a/n tends to (2g-H_l)/(gH_h-H_l). Independent group information lies in
[0,4g]. Its variance is at most 4g^2 n, so Chebyshev bounds the length event
by 4g^2 n/(m_n-1)^2, tending to zero. The nonnegative bounded fallback
excess therefore vanishes in expectation. The r<g tail has vanishing
weight at every integer k. The actual limiting risk is enclosed by
**[0.269017091392,0.269017091393]**.

This improves C72's fixed-eight limit [0.269293075342,0.269293075343],
but loses to its separate growing-group limit
[0.267829178707,0.267829178708]. C67's unrestricted rate-two limit and
C73's formal convergence family remain unchanged. No near-C67 finite
convergence is supplied here.

## 6. Storage, runtime and remaining scope

The inclusive public pack uses 24 bits each for word and proposal-minus-one,
25 for actual count, and 31 for the cell loss weight: 104 bits per word,
7288 words, plus eight oracle and two tail bytes. Actor-only packing omits
the loss weights. Public parameters and code/runtime are separate.
Python JSON loading, object/cache RAM and grading maps are not claimed to
fit this packed-byte ceiling.

The original native workspace field omitted transient uniqueness storage.
Independent conservative array totals are 42041344 bytes for five and
221446144 for six, both below 268435456. Native tensor arrays and fixed
public buffers also fit that array envelope. Allocator/library/stack/RSS
overhead and Python grading/actor memory are unmeasured and separate.

Nineteen complete small actor populations execute 934848 final queries.
Nine large constructed inputs execute 540 final diagnostics. Whole large
actor source populations are not enumerated; the finite statements use
the proof and outward arithmetic.

[Local samples](../experiments/dependency_memory/priced_coding/local_timings_2026-10-02.json)
separate loaded-table cold planning, cached-public-book encoding, last-block
updating and prediction. At k=12288 planning took 11.897 seconds wall
(11.500 process CPU); three encodes took 10.609, 11.646 and 18.625 seconds
wall. Last-block updates took 0.078273, 0.149091 and 0.002744 seconds.
These are one sample per constructed input, with code/input hashes.
Certificate grading ran concurrently during part of measurement; hardware
and scheduling were not controlled. No speed comparison, population
latency, portable efficiency or model/token/provider-cost benefit follows.
The inexpensive C74 code remains an important engineering control.

The ECVQ precedent is unchanged [@chou1989entropy]. C74 already read
Section III, printed pp. 33–35, including the alternating minimizations.
C75 reuses that bounded reading without a new source or review-status
upgrade. Exact price rewriting, tensor minimization, public time sharing,
arithmetic coding and concentration are elementary or established methods;
no generic novelty is claimed. External correctness and priority review,
strong finite convergence toward C67, broader source/query laws and
natural-agent benefit remain open.

The next design experiment should use the verified tensor transform for
full-population design updates, with a separately frozen protocol. That
could remove sampled proposal/CDF mismatch and make larger searches cheaper;
an improved code from that extension has not been run or claimed.
Zero new model calls and zero prospective natural episodes occurred here.
Research commands do not fill the twelve untouched workflow slots.

Validation: all **597 offline tests pass**, including fourteen new
scientific checks. Repository validation reports PASS with 75 claims,
55 bibliography entries, 171 PDF hashes and 195 immutable import hashes.
Paper assembly checks all 48 cited sources. All 71 C75 bindings match.
The byte audit checks 2251 original tracked files: only the thirteen
intended documentation/validator/ignore files change; all other old
files, earlier claim/decision prefixes and bibliography retain their bytes.

Offline reproduction:

    python -m experiments.dependency_memory.priced_coding.certificate
    python -m unittest discover -s experiments/dependency_memory -v
    python scripts/validate_context_repo.py
    python scripts/build_paper.py

The benchmark is a separately saved measurement. Rerunning it produces a
new sample and requires preserving the old record and regenerating dependent
bindings; default validation does not rerun it.
