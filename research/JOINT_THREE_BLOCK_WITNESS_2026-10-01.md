# A better explicit code for three delayed-query blocks

October 1, 2026. **Explicit finite construction with exact route grading.**
Heuristic discovery is not an optimality or publication-priority proof. No model
calls are involved. The original one-block optimum, two-block witness and
decoder-complete asymptotic frontier remain unchanged.

In the existing notation, the new local result is

\[
D_3(6) \le \frac{40529}{147456}
< \frac{427}{1536}.
\]

The right side is the prior explicit two-block code concatenated with the
one-block optimum. The new construction reduces error from approximately
27.7995% to 27.4855%, or 463 additional correct outcomes among 147,456. This is
0.3140 percentage points in average bit error, not agent task success. [C59]

| Six-bit parent control | Errors / outcomes | Average bit error |
|---|---:|---:|
| Three independent two-bit-per-block codes | 41,472 / 147,456 | 9/32 |
| Prior two-block witness plus one-block code | 40,992 / 147,456 | 427/1,536 |
| New fixed three-block code | 40,529 / 147,456 | 40,529/147,456 |

## Information order and actual encoder

The source consists of three independent uniform four-bit blocks. The encoder
retains a six-bit index before independent uniform block R and omission O are
known. The updater replaces this index with one bit before the uniform remaining
coordinate J is revealed. The final decoder sees that bit and R,O,J. It sees
no source, old parent, archive or instance-dependent public label. A fixed public
codebook is available to the updater before the source, under the unchanged
mathematical convention; it is not a token/byte implementation cost model.

Let bit positions be least-significant first. Encode a triple of branch-decision
words (a,b,c) by integer a+16b+256c. The complete fixed set of 64 integers is:

```text
0 3 5 6 9 10 12 15 48 63 80 95 96 111 133 137
144 159 160 175 192 207 230 240 243 245 246 248 255 256 271 307
348 496 1023 1535 1791 2559 2698 2815 3169 3327 3584 3599 3632 3824 3840 3843
3845 3846 3848 3850 3855 3871 3920 3984 4064 4079 4080 4082 4085 4089 4092 4095
```

For a source block x and decision word a, use the already established
\(L(x,a)=\sum_o\sum_{j\ne o}\mathbf1\{x_j\ne a_o\}\).
Choose the codeword minimizing the sum of these losses over all three source
blocks, breaking ties by the ascending integer order above. On public block R,
emit bit O of that codeword's corresponding decision word. The final decoder
predicts the emitted bit for every allowed J. The child never receives J early.
All 64 parent messages are used; every child has two possible states.

The [certificate](../experiments/dependency_memory/results/joint_three_block_certificate_2026-10-01.json)
contains the complete 4,096-row parent table, message occupancies, twelve
block/omission error counts and per-source loss histogram. Its Python grader
directly executes every source/R/O/J outcome. Separate tests construct one-block
costs by string-coordinate enumeration, check all nearest assignments, replay
the two baseline books and preserve error under relabelling, block permutation
and complement. Both formulations give exactly 40,529 errors.

## Search, comparisons and remaining questions

The [C heuristic](../experiments/dependency_memory/joint_coding_finite3/search.c)
greedily adds 64 decision triples from all 4,096 candidates, then accepts at most
eight best single replacements. The loss falls from 40,645 after addition to
40,529 after those swaps. It stops at the declared swap cap, so no single-swap
local-optimum claim applies to this book. A separate start at the old concatenated
book finds no improving single replacement and stays at 40,992. No random starts
are used. Discovery and a timing-label verification run are preserved together;
both reproduce the same books and losses. Neither enumerates all codebooks or
all final decoders. Compiler version/source/executable hashes and local clock
readings are recorded, without a portable performance claim.

This supplies a tighter finite upper bound at k=3. Concatenating this construction
on multiples of three also supplies the same upper bound there, but it remains
above the certified decoder-complete limiting interval
(0.2618989799, 0.2618989801). The exact finite optimum, better finite encoders,
external correctness review and literature priority remain open. Established
rate-distortion reductions and public-codebook coding are not claimed novel.
See the [prior joint-coding derivation](JOINT_BLOCK_CODING_2026-09-21.md) and
[decoder-complete converse](DECODER_COMPLETE_FRONTIER_2026-09-21.md).
