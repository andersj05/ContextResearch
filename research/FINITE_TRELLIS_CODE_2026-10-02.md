# A compact finite code for delayed queries

October 2, 2026. **Local finite construction, an elementary encoder derivation,
and exhaustive mathematical checks.** Claim C68. This implements an achievable
code under the existing bit-model contract, after C67's asymptotic existence
result. It does not prove finite optimality or a new general coding method.

A fixed 16-state tail-biting trellis with three public response tables achieves
**867,837 errors on 3,145,728 four-block outcomes**, at an eight-bit parent and
one-bit child. The pair-product control has 869,376 errors: a reduction of
1,539 errors, or about **0.0489235 percentage points**. The exact distortion is
289279/1048576, about **27.5877953%**. Independent four-block concatenation
attains this same error at every k=4*n with exactly 2*k parent bits.

The [standard-library implementation](../experiments/dependency_memory/trellis_coding/README.md)
includes an exact dynamic-programming encoder, local updater, fixed final
decoder, [public labels](../experiments/dependency_memory/trellis_coding/tables.json),
[frozen discovery](../experiments/dependency_memory/trellis_coding/discovery/metadata.json),
and [independent finite certificate](../experiments/dependency_memory/results/trellis_coding_2026-10-02.json).
No model request, prospective natural workflow, historical outcome rewrite or
change to the [unrestricted asymptotic curve](UNRESTRICTED_RATE_CURVE_2026-10-02.md)
is added.

## 1. Information order and representation

There are k independent uniform four-bit source blocks X_r. The parent is
formed before the independent uniform block R and omission O arrive. The
updater forms one child bit Z before the final coordinate J, uniform among the
three coordinates other than O. The final actor sees only Z/R/O/J. The source,
parent, encoder scratch, search record, archive, environment files and provider
session state are unavailable at that final boundary. This is a trusted offline
mathematical codec, not an isolation claim about an untrusted Python process.

The parent consists of k quaternary symbols u_r, packed as

```text
M = sum_r u_r * 2^(2*r),     0 <= M < 2^(2*k).
```

There are three fixed public tables T_0,T_1,T_2, each with 64 four-bit response
words. They are selected before any instance X. For b=u_(r-2), p=u_(r-1), c=u_r,
with symbol indices interpreted cyclically modulo k, define

```text
A_r = T_0[c + 4*b + 16*p]     when r mod 3 = 0,
      T_1[p + 4*c + 16*b]     when r mod 3 = 1,
      T_2[b + 4*p + 16*c]     when r mod 3 = 2.
```

The updater extracts A_R from M and returns Z=(A_R >> O)&1. The final decoder
returns Z on every allowed J. Thus the child is fixed before J and every actor
respects the same timing as the old unsigned codes. The final decoder cannot
reread M. Public k, tables and segmentation rules are design information, not
instance memory.

The labels contain 3*64*4=768 bits, or **96 packed label bytes**. That figure
excludes program, runtime, JSON, indices and provenance metadata. Public design
is free in this bit model; 96 bytes is not a measured production footprint or
a change in the parent bit budget. Duplicate emitted response sequences are
legal. At k=4, the 256 messages emit 254 distinct sequences, all 254 used by
the smallest-message nearest assignment.

## 2. Exact encoder within the fixed construction

Let L(x,a) count errors over the 12 ordered omission/query routes of one block.
It has the directly checked form

```text
w = popcount(x), x_o = bit_o(x), a_o = bit_o(a),
L(x,a) = sum_o [a_o*(3-w+x_o) + (1-a_o)*(w-x_o)].
```

The encoder minimizes sum_r L(X_r,A_r) over all 4^k parent messages. A forward
trellis state consists of two adjacent symbols; an edge appends one of four
symbols. There are 16 states. To avoid retaining a separate initial state,
enforce cyclic closure. The initial pair is already the last two symbols of M.
Every message gives one such closed labelled path. Conversely every closed
path determines consistent cyclic symbols and hence one message. This remains
true when output labels coincide; it is a statement about paths and messages.

The implemented reverse recurrence also gives a transparent tie rule. In
reverse order let q=p+4*c and h(q,b)=b+4*p. For each candidate cyclic boundary
s in 0..15, use

```text
F_(-1)^s(q) = 0 if q=s, infinity otherwise,
B_r(q,b) = L(X_r, response(b, q mod 4, floor(q/4), r mod 3)),
F_r^s(q) = min_(b=0..3) [B_r(q,b) + F_(r-1)^s(h(q,b))].
best cost = min_s F_(k-1)^s(s).
```

Induction on r proves that F is the minimum cost of a reverse path through
blocks r,...,0 ending at the prescribed boundary. Taking the minimum over s
therefore minimizes exactly over the closed paths, hence all messages in this
fixed construction. It does not optimize other public tables or final decoders.

For k>=2, s=u_(k-2)+4*u_(k-1) specifies the most significant four bits of M.
Choose the smallest tied s. Trace backwards, choosing the smallest tied next
symbol; the newly chosen positions are k-3,...,0 before the two wrapped symbols
repeat. This yields the smallest integer M among minimum-cost messages. The
k=1 implementation directly checks four messages; only equal-symbol boundary
pairs close in that case.

At k>=2 the recurrence evaluates **16*16*4*k = 1024*k branch relaxations**.
It stores cost rows for one candidate boundary and the current best boundary,
at most two k-by-16 tables of bounded integer entries, plus source costs and
symbol scratch. Path integers do not grow inside the recurrence. These are
operation/storage counts, not a portable wall-time, CPU or bit-operation
complexity measurement. The source and scratch are discarded once M is formed;
none becomes a retained side channel.

## 3. Finite results, product extension and failed transfer

The population certificate independently enumerates all source/message costs
and chooses the smallest tied parent. It then directly invokes the updater and
final predictor on every delayed query, grading against evaluator truth after
prediction. It does not call the Viterbi encoder to generate those population
assignments. The recurrence proof and separate enumeration tests connect the
two encoders.

| Four-block code, eight parent bits and one child bit | Exact error count / 3,145,728 |
|---|---:|
| Tuned trellis | **867,837** |
| Pair-product control | 869,376 |
| Existing three-block witness plus one block | 869,648 |
| Four independent two-bit blocks | 884,736 |

The controls are independently recomputed by product additivity from small
component loss sums 1,698 over 256 two-block sources, 40,529 over 4,096
three-block sources, and 54 over 16 one-block sources. For example, two pairs
give 2*1698*256=869376. These are exact derived counts, not additional executed
four-block actor queries. The comparisons concern these named controls, not
every possible product allocation or the unknown four-block optimum.

For k=4*n, concatenate n independently closed four-block groups. Their parent
messages are one byte each, giving exactly 2*k bits. The public R selects the
group and local coordinate; no group identifier or cyclic boundary is retained
separately. Additivity and identical uniform group marginals give exactly the
same average distortion 289279/1048576 for every n. The code has 1024*k branch
relaxations. This is an elementary product construction, not a full enumeration
of 16^(4*n) inputs or an approach to the optimal asymptotic curve.

At common lengths k=12*n, repeating the preserved three-block witness instead
gives lower distortion 40529/147456, about 27.4854872%. Both products store
exactly 2*k parent bits and use one child bit. Their error difference is
9655/9437184, about 0.1023081 percentage points. At k=12 the certificate derives
the two full error counts by product additivity rather than executing the
enormous population. Thus the four-block improvement does not improve the
best known repeated-short-code asymptotic upper bound. Its value here is the
particular finite four-block construction and checked local-table encoder.

One long cycle with the selected tables has different edges from those
independently reset groups. Its smaller-block results are explicitly worse:

| k | Selected long-cycle errors / outcomes | Existing control errors / same outcomes |
|---|---:|---:|
| 1 | 58 / 192 | 54 / 192 |
| 2 | 1,802 / 6,144 | 1,698 / 6,144 |
| 3 | 41,649 / 147,456 | 40,529 / 147,456 |

Together with k=4, these checks execute **3,299,520 actor query routes**.
General k validity follows from the codec derivation; quality of one longer
cycle and proximity to C67's rate-two limit near 26.189898% remain open. The
older three-block witness and its all-decoder converse are unchanged.

## 4. Bounded discovery and independent checks

Start from the preserved C59 64-word three-block book B. For a permutation P
of 0..63, set T_phase[index]=bit-nibble_phase(B[P[index]]). At k=3 the three
index formulas all equal the global message integer, so the emitted book is
exactly B under a parent relabelling. That identity does not guarantee a good
overlap extension to k=4.

The native search evaluated identity and xorshift32/Fisher-Yates seeds 1..32.
Identity has 884,313 errors; the selected seed 11 has 879,487. All 33 fail to
beat the pair-product control. Both results are independently recomputed in
Python tests. The native record retains every permutation and score.

Starting from seed 11, four fixed sweeps visit phases 0..2 and entries 0..63.
At each visit all 15 alternative four-bit labels are scored on the full
four-block population. Accept strict improvements, breaking improving ties by
the smallest label. The 768 visits and 11,520 alternatives yield 93 accepted
changes. Sweep totals are 870,625, 869,300, 868,254 and 867,837; accepted changes
are 54,15,15,9. Every candidate score is preserved. The final sweep still
changes nine entries, so the search neither certifies a local optimum nor
exhausts the 16^192 tables. Rejected alternative scores remain native
observations; the final population result is independently regenerated.

Compiler/source/upstream hashes and the Windows Clang 19.1.0 flags are retained.
C `clock()` reports 13.251 seconds for the optimization; process wall/CPU time
was not independently recorded, and no portable-speed claim follows. Discovery
is adaptive post-hoc mathematics on an inspected population, not held-out
generalization, independent trials or a model study.

Eight scientific tests independently check route loss, public lookup, every
k<=3 source against every parent, declared k=4/6 examples, a 32-block closed
path, four-block product grouping, timing/capacity, failed initial searches and
immutable discovery choices. The standard-library generator binds 15 source
files and regenerates the selected counts without compiling or rerunning the
native search.

## 5. Primary-source comparison and remaining work

[Marcellin and Fischer (1990)](https://experts.arizona.edu/en/publications/trellis-coded-quantization-of-memoryless-and-gauss-markov-sources-2/)
already develops trellis-coded quantization and source-tailored branch labels.
Only the author university record's abstract/metadata was read; its full
12-page paper remains unreviewed. Bibliographic key `marcellinfischer1990tcq`.

[QTIP, pinned v4](https://arxiv.org/html/2406.11235v4), Sections 2.3, 3.1 and 3.2,
establishes additive-cost Viterbi coding, bit-window decoding and tail-biting
as precedents. Its boundary discussion distinguishes extra initial-state
storage from cyclic coding and gives an approximate two-pass method for large
state spaces. Our 16-state recurrence is exact. Gaussian weight-quantization
results and hardware performance are not transferred. Bibliographic key
`qtip2024`; this is a bounded primary reading, not replication or full review.

The local addition is a fixed finite witness and checked implementation for
the delayed-query loss, with a hard one-bit child formed before J. General
TCQ/Viterbi, bit shifts, table tuning, product coding and tail-biting are not
novelty claims. Exact finite optimality, publication priority, codes approaching
the full curve, changed source/query laws and useful natural-language retention
remain open. A next construction should compare equally charged public data
and parent capacity, retaining negative transfer cases and all search attempts.
