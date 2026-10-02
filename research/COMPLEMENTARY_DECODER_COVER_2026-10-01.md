# A finite converse including coordinate-dependent complementary decoders

October 1, 2026. **Local analytic restricted converse with exact finite
witnesses.** Claim C62. External proof review and literature priority review
remain open. The cover argument is elementary; no new general coding technique,
finite optimum, model result or token-cost conclusion is claimed.

For three independent uniform four-bit blocks, six parent bits before R/O and
one child bit before J, let D^comp_3(6) permit complementary three-bit final
prediction endpoints at every R/O branch. The endpoints may depend on J.
The new local result extends the [coordinate-independent proof](JOINT_THREE_BLOCK_COVER_2026-10-01.md):

\[
\boxed{\frac{40072}{147456}=\frac{5009}{18432}
\le D^{\rm comp}_3(6)\le\frac{40529}{147456}.}
\]

The interval is **[27.1756%, 27.4855%]**, width 457/147,456, about 0.310
percentage points. The upper witness is unchanged. This includes endpoint pairs
such as 010/101 that were outside the earlier proof. Noncomplementary endpoint
pairs remain outside the new converse; the unrestricted finite optimum and
the previously certified all-decoder asymptotic frontier remain unchanged.

## 1. Decoder coverage and the information contract

The source disappears after parent encoding. The updater receives only the
parent M and public R/O, sends one bit Z, and loses access to M before J arrives.
The final prediction receives only Z,R,O,J. Public tables/codebooks are fixed
before the source; archives, rereads, session state and source-selected public
tables are excluded. Independent random tapes can be fixed, and the bound holds
for every fixed tape and hence the average. Parent/updater rules may be arbitrary
and jointly depend on all source blocks within this contract.

A three-bit word has four unordered complementary pairs, including 000/111,
001/110, 010/101 and 011/100. Sorting an endpoint pair merely relabels the
updater's child bit. Four omissions give 4^4=256 decoder tables per block.
Source bit flips and coordinate permutations partition these into six orbits;
independent transformations within each block preserve uniform source/query
laws and parent capacity. Permuting the three uniform blocks reduces the
6^3 ordered orbit choices to 56 unordered mixed cases. Thus the check covers
all 256^3=16,777,216 ordered three-block complementary-table choices, including
different tables for different blocks. These are covered mathematical cases,
not independent experiments or individually executed model calls.

| Orbit | Representative endpoint pairs, by omitted coordinate | Size | Ideal-word fiber sizes |
|---|---|---:|---|
| 0 | 000/111, 000/111, 000/111, 000/111 | 8 | two of size 5; six of size 1 |
| 1 | 000/111, 000/111, 000/111, 001/110 | 96 | two of size 3; two of size 2; six of size 1 |
| 2 | 000/111, 000/111, 001/110, 010/101 | 24 | eight of size 2 |
| 3 | 000/111, 000/111, 001/110, 011/100 | 96 | four of size 2; eight of size 1 |
| 4 | 000/111, 000/111, 011/100, 011/100 | 24 | four of size 3; four of size 1 |
| 5 | 000/111, 010/101, 011/100, 010/101 | 8 | sixteen of size 1 |

Binary strings in the table are ordinary three-bit word notation. The stored
integer endpoints use low-to-high bits in increasing order of nonomitted
coordinates; the exact [certificate](../experiments/dependency_memory/results/joint_three_block_complement_2026-10-01.json)
records all orbit members and all target arrays, so this notation adds no
unrecorded convention.

## 2. A cover inequality with the largest 64 columns

For a fixed table g, define its one-block error count
\(L_g(x,a)=\sum_o\sum_{j\ne o}{\bf1}\{x_j\ne v_{g,o}^{a_o}(j)\}\).
The analysis word a lists all four potential child outputs; those four bits
are not an extra information channel at final decoding. Each parent state
specifies one triple c of such words. Any protocol therefore has a fixed public
book C of at most 64 triples; arbitrary source encoding cannot beat nearest
assignment within that book.

Complementary endpoints on three coordinates have a unique better endpoint:
their errors sum to three, so they cannot tie. Every source has a unique ideal
word a_g(x). Write u_g(x)=min_a L_g(x,a). For each complementary table,
sum_x u_g(x)=48: each omission has two exact and six one-error nearest source
patterns, with uniform three-bit projection. Summing three blocks over 4,096
sources gives sum U=36,864. The excess E(x,c)=L(x,c)-U(x) is a nonnegative
integer and is at least one when c differs from the unique ideal triple.

Choose nonnegative additive target potentials T(x)=sum_r t_r(x_r), and let
r(x,c)=(T(x)-E(x,c))_+. Define q_c as the number of sources whose T is zero
and whose unique ideal triple is c; Q=sum_c q_c. Then, source by source,

\[
\min_{c\in C}E(x,c)\ge T(x)-\sum_{c\in C}r(x,c)
 +{\bf1}\{T(x)=0,\ a(x)\notin C\}. \tag{1}
\]

For positive T, the inequality uses maximum positive saving at most its sum.
For zero T all savings vanish, and missing the unique ideal word costs at
least one. The two terms do not double-count a source. Summing (1), with
R_c=sum_x r(x,c), gives

\[
\sum_x\min_{c\in C}L(x,c)
\ge36864+\sum_x T(x)+Q-\sum_{c\in C}(R_c+q_c)
\ge36864+\sum_x T(x)+Q-\operatorname{Top}_{64}\{R_c+q_c\}. \tag{2}
\]

All column weights are nonnegative. Their largest-64 sum bounds every book of
at most 64 words, including duplicate or unused parent states. This uses the
complete column-weight distribution, rather than replacing every column with
a single maximum. It does not enumerate all 64-element books.

## 3. Exact finite witnesses and independent checks

The final targets are all zero or one. An exploratory grid tries target one
on sources whose ideal-word fiber has size at most a cutoff in {0,1,2,3,5};
repeated target arrays are deduplicated. This checks 1,306 candidate orbit/target
triples. A separate 144-point quarter-unit refinement of case (0,0,4) gives no
better witness than the full-column binary calculation. These are post-hoc
mathematical choices, not a predeclared model experiment or target-optimality
claim. The checker needs only the 56 selected arrays and their exact inequalities.

The saved artifact computes all 4,096 decision columns for each selected case,
229,376 columns total, using exact integer histogram convolution. For (0,0,0),
sum T=4,608, Q=1,000 and Top_64=2,400; (2) gives 40,072. Every other selected
case gives at least 40,320. The initially problematic (0,0,4) uses target one
on each unsigned block's six singleton-fiber sources and on all sixteen sources
of orbit 4. Sum T=7,168, Q=0 and Top_64=3,504, giving **40,528**. No fractional
target is needed for the final certificate. Stored quarter units merely permit
exact comparison with the exploratory grid.

Five tests separately check the direct omission/coordinate routes, unique
one-block oracles, all orbit members using another symmetry implementation,
all 56 selected column histograms and the per-source inequality on three books.
The histogram cross-check explicitly enumerates source triples for every
distinct sorted score-multiset triple; caching equal multisets reduces this to
1,467 direct triple sums while checking all 229,376 column instances. It does
not reuse the generator's convolution or assert that 56 times 16,777,216 pairs
were individually executed. The API admits coordinate-dependent complementary
pairs and rejects noncomplementary inputs. The unchanged upper witness is
independently route-graded and source-bound.

Forty-six of the 56 orbit cases have lower bounds strictly above the 40,529-error
incumbent and cannot improve on that incumbent within the complementary family.
Ten cases remain possible; this prunes a finite search without proving that the
unsigned table is optimal. Extending to noncomplementary endpoints requires a
different treatment of tied ideal words and their fibers. It remains open.

## Reproduction

```powershell
python -m experiments.dependency_memory.joint_coding_complement.cover
python -m unittest experiments.dependency_memory.joint_coding_complement.test_cover -v
```

The [exploratory discovery](../experiments/dependency_memory/joint_coding_complement/discovery.json)
preserves grid counts, selected targets and source hashes. The separate
`discover` module regenerates that mathematical trace; it makes no model request.
Keep the previous [all-decoder frontier](DECODER_COMPLETE_FRONTIER_2026-09-21.md)
and earlier witness/proof artifacts unchanged. Bits and average bit error do
not imply tokens, task accuracy or subscription savings.
