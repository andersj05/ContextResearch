# Conditional six-block construction and failure of product locality

October 2, 2026. **Local finite results, independently checked.** Claim C69.
The general methods are established. Exact finite optima, external correctness,
publication priority and practical-agent benefit remain open.

## 1. Result and information contract

The [previous three-block witness](JOINT_THREE_BLOCK_WITNESS_2026-10-01.md)
has 40,529 errors on 147,456 outcomes. Four further single-word changes give
**40,514 errors**, and an independent exhaustive replacement screen shows that
no one of its 64 response triples can be replaced by any of the 4,096 possible
triples to improve average loss within the fixed unsigned decoder family.
Nevertheless, the two-copy product admits an improving single six-block
response-word replacement. Eight such conditional changes yield:

| Construction | Six-block error count / 1,207,959,552 | Average error |
|---|---:|---:|
| Two old three-block components | 332,013,568 | 27.485487% |
| Two refined three-block components | 331,890,688 | 27.475315% |
| Refined product with one joint change | 331,886,587 | 27.474975% |
| Refined product with eight joint changes | **331,857,648** | **27.472579%** |

The last construction avoids 33,040 errors compared with the stronger refined
product: about **0.002735 percentage points**, not a large practical gain.
Its reduced distortion is 2,304,567 / 8,388,608. The
[all-decoder three-block lower bound](ALL_DECODER_THREE_BLOCK_COVER_2026-10-01.md)
is unchanged, so the current unrestricted bracket becomes

```text
40072 / 147456 <= D_3(6) <= 40514 / 147456.
```

Its 442-error width improves the old 457-error width by 15; neither the refined
component nor the six-block code is proved globally optimal. Old C59/C60/C62/C63
artifacts retain their original dated bounds.

The source is six independent uniform four-bit blocks. Independently, R is
uniform on six blocks, O is uniform on four omissions, and J is uniform on
the remaining three coordinates. The encoder reads X and stores M before R/O;
the updater reads M/R/O and stores one bit Z before J. The final actor reads
only Z/R/O/J. Source, old parent, scratch, session, archive and environment
rereads are absent after the corresponding boundary. Tables are public before
X and free under this bit-model convention. This is distinct from bytes,
Python object storage, tokens, provider credits and production costs.

## 2. Public conditional codebook and exact encoder

Let B contain the 64 refined response triples in their preserved slot order,
each represented by a twelve-bit integer. Parent M=a+64*b, a,b in 0..63, contains
exactly 12 bits. Its right response triple is B[b]. Its left response triple is
B[a], except for the following public overrides:

```text
M       left triple
3330    963
3343    3747
3354    362
3359    3637
3360    409
3366    3788
3368    3155
3714    1475
```

The first seven are in right group b=52; the last is in b=58. The updater
selects the response nibble for R and returns its O bit. The final actor
returns Z. Both triples can convey joint source information because the
encoder chooses a/b together before the selected block becomes known; there
is no extra conditional flag or retained source value.

For a source half x and response triple c, write L3(x,c) for its 36 individual
omission/query errors. The exact encoder first minimizes left loss among 64
entries separately for each modified b, sharing the base minimum for all
unmodified b. It then minimizes left minimum plus L3(y,B[b]) over 64 choices
of b. Tie order is smallest b, then smallest a, hence smallest integer M.
This equals exhaustive nearest selection among all 4,096 response words:
the two nested minima partition that book without deleting any candidate.
Optional encoder loss diagnostics are evaluator outputs; only M proceeds to
the updater.
Declared diagnostic sources also compare the encoder against the complete
book directly; this is not a claim of full six-source brute-force encoder
testing. All 4,096 parent messages are used in the certified population.

Packed public label payload consists of 96 base bytes and 24 override bytes.
Each base pair or (M,left triple) uses 24 bits. The override count eight is a
fixed public protocol constant. **120 bytes excludes count/framing, program,
runtime and JSON storage**, and is not charged to the instance's12 parent bits.
The refined product needs only the 96-byte base payload under the same convention;
this construction therefore has extra public design storage, not extra
instance memory. A self-describing serialization would separately carry count
and framing. Packing/unpacking is executable in the
[codec](../experiments/dependency_memory/conditional_coding/codec.py).

## 3. Independent component screen and product counterexample

For each of 4,096 three-block sources x, let d(x) be its nearest loss, a(x) its
least-index nearest word, and delta(x) the gap to the best other word. Ties
give delta=0. Adding c saves

```text
G(c) = sum_x max(0, d(x) - L3(x,c)).
```

Removing old slot a only costs on sources uniquely nearest to a. The exact
net improvement from replacing a by c is

```text
G(c) - sum_{x: a(x)=a} min(delta(x), max(0, L3(x,c)-d(x))).
```

To verify the identity, split into L3(x,c)<d(x), a distinct tied/strict old
winner surviving removal, and the uniquely removed winner. These exhaust all
cases and agree with the new nearest minimum. The Python checker accumulates
direct distances, rather than using the native margin histograms. It evaluates
all 64*4,096 candidate replacements, includes duplicate candidates, records a
digest of all signed gains, and finds **zero positive gains**. Direct complete
nearest recomputation on specified replacement books supplies additional checks.
All 147,456 component actor routes separately give 40,514 errors.

The two-copy product has total six-block loss 8192*40,514=331,890,688. Change
only parent 3330's left triple from B[2] to 963, preserving right triple B[52].
An independent full-population grouped nearest calculation gives 331,886,587,
a strict gain 4,101. Exactly one of the 4,096 six-block response words changes.
This proves a scoped counterexample: **a component locally optimal under all
single response-triple replacements need not have a product locally optimal
under single six-block response-word replacements**, for this uniform source
and loss. It does not establish any general new quantization theorem or the
failure of products of globally optimal components.

## 4. Exact weighted six-block grading

For each left source x, compute minimum d_b(x) within right group b and the
least low digit a_b(x). Let d(x) be its base-component minimum. All unchanged
groups have d_b(x)=d(x). Partition left sources by the pair

```text
(d_52(x)-d(x), d_58(x)-d(x)).
```

There are 16 groups in the selected construction. For each right source y,
the high digit b minimizes L3(y,B[b]) plus that group's relative left minimum.
The subtracted d(x) is common to every b. Thus b and its tie decision are
identical for every x in the group. Right responses depend only on b; left
responses use the separately computed least a_b(x).

For each group/y, the checker executes the right actor's36 routes with weight
equal to group size. For each x/b, it executes the left actor's36 routes with
weight equal to the number of right sources selecting b. Zero-weight pairs
are skipped. Those weights cover every one of the 16,777,216 six-block sources
and every R/O/J outcome exactly once, as the Cartesian group partition and
the selected-b counts show. Bit-string truth labels are used only after the
source-inaccessible actor returns its prediction.

The check physically executes **11,783,592 actor queries** representing
**1,207,959,552 equally weighted outcomes**. Their errors sum to 331,857,648,
agreeing with a separate sum of grouped nearest distances and the native
full-source-pair calculation. Do not describe this as individually executing
1.2 billion actor queries. All source-pair weights and parent occupancies sum
to 16,777,216. All accepted search steps independently rescore too; rejected
native conditional candidate scores are preserved only as per-slot maxima and
are not all independently recomputed.

## 5. Product extension, search failures and established precedents

Repeat independent six-block segments at any k=6*n. Encode each using 12 bits,
concatenate their parents, and use public R to select the segment before
producing Z. There is no extra segment identity or child bit. Source/query
independence and ordinary additive expectation preserve the same distortion
for every such k, with 2*k parent bits. At common k=12*n, this beats both the
old and refined three-block products. It improves these explicit repeated-code
upper bounds, while the [C67 optimal asymptotic curve](UNRESTRICTED_RATE_CURVE_2026-10-02.md)
and its approximately 26.189898% rate-two value remain unchanged. Larger complete
populations are not executed, and this is not an encoder approaching that curve.

The search was adaptive after inspecting the finite population. Original modal
product initialization and three perturbed starts failed. A first joint change
beat the old product but lost to the newly refined component product; modal
continuation did not help. Keep those failures in
[the preserved discovery](../experiments/dependency_memory/conditional_coding/discovery/README.md).
Component refinement accepted gains 8,2,2,3, then reached a zero single-word
screen. Conditional refinement accepted eight changes and stopped at its cap
with a positive last gain. **Final six-block single-word locality is unproved.**
Compiler flags, source/header/raw-output hashes and Windows C-clock observations
are retained, without treating those clocks as portable latency measurements.

Jégou, Douze and Schmid's author manuscript, Section II-A/B, describes nearest
assignment, local Lloyd conditions, Cartesian product codebooks, additive
distortion and separate codebook storage [@jegou2011product]. These are prior
methods; its Euclidean nearest-neighbor setting differs from our delayed-query
loss. This bounded reading supplies no performance transfer or priority verdict.
The particular integer upper bounds and scoped counterexample are local
additions, with external correctness and publication priority open. The earlier
trellis sources remain relevant to C68; no generic codeword-replacement,
coordinate-search, product-code or conditional-codebook novelty is claimed.

## 6. Reproduction and evidence boundary

Use the [package](../experiments/dependency_memory/conditional_coding/README.md)
to regenerate the
[certificate](../experiments/dependency_memory/results/conditional_six_block_2026-10-02.json)
and its 24 bindings. The independent checker uses only the Python standard
library and does not execute native discovery or contact a provider. Eight
scientific tests check routes, full-book diagnostic encoders, all component
replacements, product locality, grouping/ties, weighted outcomes, packing,
timing and segment memory. The repository validator regenerates the artifact.
All 541 offline tests pass. Repository validation reports PASS with 69 claims,
51 bibliography entries and 171 PDF hashes; paper assembly checks 44 cited
sources. All 24 witness/provenance bindings regenerate.

This milestone has zero new model calls, zero prospective natural workflows
and no measured token, credit, runtime or production improvement. Earlier
provider launches, permanent gaps and the zero untouched-episode count remain
unchanged. Work stays in separate folders of this one repository.
