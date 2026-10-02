# A deterministic polynomial code reaches the characterized limit

October 2, 2026. **Local constructive deduction, finite negative controls and
conservative analytic proximity bounds.** Claim C73. External correctness and
publication priority remain open. Zero new model calls or natural episodes.
Greedy coverage, source coding, logarithmic blocking and concentration are
established; this is an application to the delayed-query loss, not a new
general coding algorithm.

The [implemented public builder and actors](../experiments/dependency_memory/greedy_coding/README.md)
give a deterministic family at exactly two parent bits per four-bit block
and one child bit before the final query. Its actual error tends to
[C67](UNRESTRICTED_RATE_CURVE_2026-10-02.md)'s optimum, whose existing enclosure
is **(0.2618989799,0.2618989801)**. Public construction and actors have
polynomial bit complexity in the full input length.

This resolves formal constructive convergence at rate two. It does not give
useful finite convergence: the checked three-block code loses to C69, and
the default group size first reaches three at **536,870,912 blocks**.
One conservative certificate bounds error by 26.560821% at group size 10^10;
that group first occurs at k=2^(99,999,999,999). Those large codebooks were
not built. The stronger finite [C72](COORDINATED_TIE_CODE_2026-10-02.md)
construction remains useful evidence; this family does not replace it with
a measured improvement.

## 1. The unchanged information contract

X has k uniform iid four-bit blocks. Independent uniform R/O arrive after
the parent M; independent J is uniform among the three coordinates other
than O and arrives after the one-bit child Z. Public k/g/books/programs are
fixed before X. The updater sees only M,R,O and public data. The final actor
sees only Z,R,O,J and predicts Z.

Source, old parent, scratch, output lists, instance histograms, archives,
environment and provider-session rereads are excluded after their boundary.
Exact temporary computation inside a stage is allowed and discarded. The
actors are trusted pure functions, not isolated untrusted processes.
No per-instance schedule, selector, overflow flag or group header is free.

For a scalar source x and response word a, bit o of a is the child bit to
emit if o is omitted. All sixteen response words are allowed. Their loss is

\[
L(x,a)=\sum_{o=0}^3\sum_{j\ne o}
 {\bf1}\{x_j\ne a_o\}
=3|x|+3|a|-2|x||a|+2|x\mathbin{\&}a|.
\]

Each group word has g responses, and its loss is the sum of scalar losses.
There are 16^g sources and 16^g candidate responses. The denominator of the
group's queried-bit error is 12g*16^g. Response words are potential child
decisions; only one of their bits reaches the child.

## 2. A completely specified public finite design

For each integer threshold S=0,...,12g, form the source sets

\[
C_a(S)=\{x^g:\sum_r L(x_r,a_r)\le S\}.
\]

Begin with the all-zero response word, occupying one parent label. Remove
its covered sources. Repeatedly add the word covering the largest remaining
source count, breaking ties by the smallest packed integer word. Stop at
4^g total words or zero remaining gain. This is ordinary greedy coverage.

Then reassign **every** source to its nearest selected word, breaking ties
by the first word in book order, and compute its exact full-population loss.
Choose the threshold with the smallest loss, then smallest S. Also compare
the fixed product of the existing scalar book (0,1,14,15); choose that
product on a population-risk tie. All evaluation and selection precede X.
The retained memory never carries a source-dependent design choice.

The scalar control has loss 54/192=9/32. Independent enumeration of all
1,820 four-distinct-word books with this fixed unsigned final decoder finds
the same lexicographically first minimum. C19 already establishes the
stronger unrestricted one-block optimum; this is a control calibration.

The builder computes exact loss layers by tensoring scalar histograms into
source bit sets. Its integer threshold/coverage/risk selection uses neither
a floating optimizer nor a model. The supported implementation accepts any
positive public g; its growing schedule below supplies the polynomial bound.

## 3. The charged codec at every input length

Put n=floor(k/g) and r=k%g. Each complete group emits its nearest book index
in a fixed 2g-bit segment. Each of the r remaining blocks emits the nearest
scalar-control index in two bits. The parent is the concatenation of those
segments, requiring exactly 2ng+2r=2k bits and at most 2^(2k) states.
There is no separate fallback flag.

Given M,R,O, the updater extracts the appropriate segment, looks up the
selected group's response coordinate or the scalar tail response, and emits
that response's bit O. The final actor predicts its sole retained bit Z.
Source and nearest-search workspace do not survive alongside M.

Let E_g be the actual selected group's uniform error. Independence and
uniform block queries give the exact tiled risk

\[
D_{\rm code}(k,g)=\frac{(k-r)E_g+r(9/32)}{k}. \tag{1}
\]

This formula is a population deduction for arbitrary n, not enumeration of
all n-group inputs. Public response payload is 4g bits per book word.
The checked g=1/2/3 books use respectively 2/16/96 packed bytes. Public
k/g/counts, program/runtime/framing and temporary design workspace are
separate from both that payload and the charged instance memory.

## 4. Why the group error reaches C67

Fix any delta>0. C67's unsigned scalar rate-distortion curve and strict
channel mixing supply a channel with I(X;A)<rho<sigma<2 and mean queried-bit
loss below D_infinity(2)+delta/2. The ordinary finite-alphabet
excess-distortion coding argument gives a competitor book with

\[
\ell_g\le\lceil2^{g\sigma}\rceil,\qquad
\Pr\{\text{nearest loss}>S_g\}=\eta_g\longrightarrow0,
\]

where an integer threshold S_g has S_g/(12g)<=D_infinity(2)+delta for large
g. Its words belong to the builder's full candidate alphabet.
This is an established coding existence step, not the supplied algorithm.

The supplied greedy builder makes that existence constructive. If a
competitor's ell sets cover all but eta of source mass, and u_t is the
mass still uncovered by the greedy book after t additions, their union
covers at least u_t-eta of the remaining mass. One set therefore covers
at least (u_t-eta)/ell. The greedy maximum is at least this large, so

\[
u_{t+1}-\eta\le(1-1/\ell)(u_t-\eta),\qquad
u_m\le\eta+(1-1/\ell)^m
\le\eta+e^{-m/\ell}. \tag{2}
\]

The initial zero word can only help. If greedy stops early, no candidate
can cover anything left, so u<=eta and the conclusion persists. The
recurrence is the familiar coverage/submodular-greedy comparison; we give
its elementary proof rather than claim it as new.

Use m=4^g-1. Since sigma<2, m/ell_g tends to infinity. On covered sources,
nearest reassignment costs at most S_g; on other sources, normalized loss
is at most one. The best public threshold and scalar control can only
improve that average. Therefore limsup E_g<=D_infinity(2)+delta.
The C67 finite converse gives E_g>=D_infinity(2). Let delta decrease to zero:

\[
\lim_{g\to\infty} E_g=D_\infty(2). \tag{3}
\]

Neither greedy book optimality nor monotone finite improvement is needed.

## 5. Polynomial construction has a slow group schedule

Set

\[
g(k)=\max(1,\lfloor\operatorname{bit\_length}(k)/10\rfloor).
\]

Loss-layer masks have 16^g source bits and 16^g candidate rows, with O(g)
levels. Their space and tensor construction are bounded by
poly(g)*256^g. Each of O(g) threshold runs scans at most 16^g masks at
each of 4^g choices. Counting bit operations for those masks, public
construction is at most **poly(g)*1024^g**. Nearest grading and the scalar
product control fit within that bound.

For g>=2, 1024^g=2^(10g)<=2^bit_length(k)<=2k. Thus public construction
is O(k*poly(log k)), with polynomial workspace. Small g=1 is a fixed
constant-size exception. Nearest encoding, parent packing and updater
extraction also have polynomial bit complexity, including operations on
the 2k-bit parent; we do not assert linear-time actors or portable speed.

As k grows, g(k)->infinity and r<g(k)=o(k). Equations (1) and (3) prove
that the **implemented deterministic family**, at every positive integer
k, has actual limiting error D_infinity(2). No nonuniform infinite
codebook oracle or uncharged instance advice is assumed.

The first default group sizes expose the cost:

| g | First k using this group size |
|---|---:|
| 2 | 2^19 = 524,288 |
| 3 | 2^29 = 536,870,912 |
| 4 | 2^39 = 549,755,813,888 |
| 10 | 2^99 |

These are schedule thresholds, not executed populations or sufficient
near-optimal lengths. The construction is polynomial in k while exponential
in g; its asymptotic complexity alone does not establish useful convergence.

## 6. A finite conservative proximity certificate

Reuse the unchanged C34 rational Gibbs channel P_0 and reference weights q.
The checker reconfirms its cross-information upper bound J_0<2 and
distortion d_0<d_U=0.2618989801. Every active q_a>1/32. Mix the channel
with independent q using weight epsilon=1/h, for a power-of-two h>=2.
KL convexity gives cross-information J_epsilon<(1-epsilon)*2.
Its distortion is d_epsilon=(1-epsilon)d_0+epsilon/2.

The reference information density log2(P_epsilon(a|x)/q_a) lies in
[-log2 h,5], so its variance is at most (5+log2 h)^2/4. Normalized scalar
loss lies in [0,1], with variance at most 1/4. Chebyshev bounds the joint
probability of information above rho=2-1/h or average loss above
d_epsilon+1/h by

\[
\frac{((5+\log_2 h)^2+1)h^2}{4g}. \tag{4}
\]

For completeness, random coding can use reference q even if it is not the
mixed output marginal. Given source x, let G(x) be the conditional mass
of the good loss/information event. With gamma=2^(g*rho), reference
probability of the allowed distortion ball is at least G(x)/gamma.
M independently sampled words fail with probability at most
exp(-M*G(x)/gamma)<=exp(-M/gamma)+1-G(x), by convexity on G in [0,1].
Averaging proves the required competitor's uncovered-mass bound.

Choose ell=M=ceil(2^(g*(2-1/(2h)))). Then M/gamma>=2^(g/(2h)) and
(4^g-1)/ell>=2^(g/(2h))/4. Combining that coding bound, (2), threshold
rounding and e^(-x)<=1/x gives the supplied conservative bound

\[
E_g\le\min\left\{\frac12,\,
(1-1/h)d_U+\frac1{2h}+\frac1h+\frac1{12g}
+\frac{((5+\log_2 h)^2+1)h^2}{4g}
+5\,2^{-\lfloor g/(2h)\rfloor}\right\}. \tag{5}
\]

The 1/2 cap follows from nearest reassignment with the zero word always
present. The implementation truncates the positive exponent to 80, which
only enlarges (5). All computations and rounded displays are rational.
Fifty-four inspected g/h bounds retain weak values, rather than report
only favorable points. The best of nine h values at each g is:

| g | h | Error upper bound, rounded upward |
|---|---:|---:|
| 10^4 | 16 | 0.500000000000 |
| 10^6 | 32 | 0.326445720306 |
| 10^8 | 128 | 0.277510845152 |
| 10^10 | 512 | 0.265608205363 |
| 10^12 | 2048 | 0.262773005646 |
| 10^14 | 4096 | 0.262213414339 |

These are bounds on the algorithm's group risk, followed by (1) for tail
blocks. They are not actual large-code errors, measured runtimes, built
codebooks or sharp necessary blocklengths. The enormous schedule onset
is encoded as an exponent, not a fabricated giant physical execution.

## 7. What was executed and what stays open

All 75 thresholds at g=1/2/3 are built over the full response alphabet.
An independent direct-query distance matrix checks **16,843,008**
source/candidate distances and all **768** final-builder greedy choices.
The distance rows add literal scalar-route losses; those matrix entries
are not additional executed actor queries.
The resulting codes have:

| g | Best threshold-only error | Selected code error | Selected public bytes |
|---|---:|---:|---:|
| 1 | 7/24 | 9/32, scalar product | 2 |
| 2 | 9/32 | 9/32, scalar product on tie | 16 |
| 3 | 2543/9216 | 2543/9216 | 96 |

The three-block value is about 27.593316%, above the refined three-block
40514/147456 and C69's six-block 2304567/8388608. Those stronger controls
stay retained. The initial eight-response and subsequent sixteen-response
probes each inspected 75 thresholds; both give the same threshold-only
best errors. All 150 original design records and 1,616 greedy choices
are independently checked. These are post-hoc mathematical designs,
not independent statistical trials. Original probe bytes and output-path
assumptions are preserved; console timing was not saved.

Six complete small actor populations contain 12,816 sources and execute
454,848 final queries, including tail blocks. They explicitly fix public g;
these are generic-codec checks, rather than the default schedule at small k. Forty constructed product/
tail inputs execute 3,552 additional diagnostic queries. The general
partial-cover recurrence is separately calibrated on all 4,096 set systems
of four subsets of three elements, with 307,200 competitor/step comparisons.
Every small valid parent state is decoded in tests. Sixteen source/provenance
bindings preserve C72/C67/C34 and their source chains. Large groups in (5)
are not executed or physically enumerated.

The focused primary readings on October 2 were:

- Nemhauser, Wolsey and Fisher, [original paper](https://thibaut.horel.org/submodularity/papers/nemhauser1978.pdf),
  selected Section 4 passages: greedy definition, Proposition 4.1 and proof,
  Theorem 4.2 statement, printed pp. 276–281. The
  [publisher record](https://link.springer.com/article/10.1007/BF01588971)
  verifies Mathematical Programming 14:265–294 (1978), DOI 10.1007/BF01588971.
  Greedy coverage is established. This is bounded reading, not full review.
- Polyanskiy and Wu, existing [MIT Chapter 24](https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/aaa8d18ddecde45f97134d3f3dcee4a3_MIT6_441S16_chapter_24.pdf),
  Theorem 24.4 and its short excess-distortion proof, printed p. 251,
  and selected following memoryless argument on pp. 251–252.
  The reference-q adaptation above is derived explicitly; generic random
  coding is established. No full-chapter review upgrade is made.
- Śmieja and Tabor, [publisher-indexed original text](https://www.mdpi.com/1099-4300/17/5/3400),
  Introduction and Section 3.1, Entropy 17(5):3400–3418 (2015),
  DOI 10.3390/e17053400. Error-control families and greedy lossy coding are
  direct precedents. Direct HTML/PDF opens failed; the returned indexed
  primary text was read. Section 3.2's full proof was not reviewed.

The contribution remains the specific C67 delayed-query curve and scoped
constructive consequences, with external correctness/priority unresolved.
Formal polynomial convergence is now supplied. A useful finite code near
the curve, sharper convergence bounds, general source/query laws and
natural-agent/model/token/cost benefits remain open. Repeating inspected
classifier trials or counting research commands as natural episodes would
not settle those questions.
