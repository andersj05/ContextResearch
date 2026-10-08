# Mathematical checks and coding constructions

[Catalog](../INDEX.md) · [Maintenance](../README.md)

Generated from [registry.csv](../registry.csv); original reports and frozen
contracts remain authoritative. Summaries describe the dated study scope.

These are local derivations and finite computational checks, not model trials.
External proof and priority review remain open. Later constructions can improve
earlier bounds without changing the earlier certificates.

## priced-code

**Exact-priced larger-group construction** — 2026-10-02 · completed

At k=12,288 error is at most 27.047565% with the same 2k-bit parent and one-bit child. All ten starts and 41,943,040 source assignments retain independent minimum checks.

**Limits:** The small gain costs 94,754 public bytes including planning weights and 11-19 second local encodes. A separate actual-limit family reaches about 26.901709%, worse than growing C72. No finite-selector limit, global optimum or agent gain is established.

Claims: [C75](../../paper/claims.csv).

Read first: [research/EXACT_PRICED_GROUP_CODE_2026-10-02.md](../../research/EXACT_PRICED_GROUP_CODE_2026-10-02.md).

Implementation: [experiments/dependency_memory/priced_coding](../dependency_memory/priced_coding).

Saved results: [experiments/dependency_memory/results/priced_coding_2026-10-02.json](../dependency_memory/results/priced_coding_2026-10-02.json).

## weighted-overflow

**Loss-weighted overflow and allocation bounds** — 2026-10-02 · completed

The unchanged C72 actors yield error at most 27.450867% at 768 blocks and 27.064671% at 12,288. Exact integer allocation minimizes five outward bounds; tables remain 1,288 bytes.

**Limits:** Certificate minimization is not actual-risk or global code optimality. Three smaller lengths lose; all 384 unsuccessful quantizer starts are retained.

Claims: [C74](../../paper/claims.csv).

Read first: [research/LOSS_WEIGHTED_OVERFLOW_2026-10-02.md](../../research/LOSS_WEIGHTED_OVERFLOW_2026-10-02.md).

Implementation: [experiments/dependency_memory/weighted_overflow](../dependency_memory/weighted_overflow).

Saved results: [experiments/dependency_memory/results/weighted_overflow_2026-10-02.json](../dependency_memory/results/weighted_overflow_2026-10-02.json).

## greedy-code

**Deterministic convergence construction** — 2026-10-02 · completed

An implemented polynomial family at exactly 2k parent bits and one child bit converges to the C67 rate-two optimum at every integer length.

**Limits:** Useful finite convergence is unresolved: small codes lose to stronger controls and conservative near-limit group sizes are enormous. Large books were not built.

Claims: [C73](../../paper/claims.csv).

Read first: [research/DETERMINISTIC_NEAR_LIMIT_CODE_2026-10-02.md](../../research/DETERMINISTIC_NEAR_LIMIT_CODE_2026-10-02.md).

Implementation: [experiments/dependency_memory/greedy_coding](../dependency_memory/greedy_coding).

Saved results: [experiments/dependency_memory/results/greedy_coding_2026-10-02.json](../dependency_memory/results/greedy_coding_2026-10-02.json).

## tie-code

**Coordinated equal-loss response construction** — 2026-10-02 · completed

The fixed-eight code has risk at most 27.080384% at k=12,288 with the same instance caps. Its limit is about 26.929308%; a separate growing-group family tends to 26.782918%.

**Limits:** Public fixed data increase to 1,288 packed bytes. Smaller losses remain; both limits exceed C67 and no practical-agent gain follows.

Claims: [C72](../../paper/claims.csv).

Read first: [research/COORDINATED_TIE_CODE_2026-10-02.md](../../research/COORDINATED_TIE_CODE_2026-10-02.md).

Implementation: [experiments/dependency_memory/tie_coding](../dependency_memory/tie_coding).

Saved results: [experiments/dependency_memory/results/tie_coding_2026-10-02.json](../dependency_memory/results/tie_coding_2026-10-02.json).

## entropy-code

**Hard-cap entropy construction** — 2026-10-02 · completed

A flagged 2k-bit parent and one-bit child have risk at most 27.198892% at k=12,288 under the retained rational schedule. The default family tends to about 27.075301%; public tables use 10 packed bytes.

**Limits:** Large-population values are conservative bounds, not enumerated exact averages. Four smaller lengths lose to stronger controls.

Claims: [C71](../../paper/claims.csv).

Read first: [research/HARD_CAP_ENTROPY_CODE_2026-10-02.md](../../research/HARD_CAP_ENTROPY_CODE_2026-10-02.md).

Implementation: [experiments/dependency_memory/entropy_coding](../dependency_memory/entropy_coding).

Saved results: [experiments/dependency_memory/results/entropy_coding_2026-10-02.json](../dependency_memory/results/entropy_coding_2026-10-02.json).

## query-priors

**Query-prior allocation and timing** — 2026-10-02 · completed

Known 25%/75% class priors have limiting error near 25.718661%; unknown-prior minimax retains the uniform limit. An early actual class cue reaches 25% using 3n bits within the same 4n cap.

**Limits:** Source-independent class priors only. Early realized side information changes the timing contract; it is not merely a prior.

Claims: [C70](../../paper/claims.csv).

Read first: [research/QUERY_PRIOR_TIMING_2026-10-02.md](../../research/QUERY_PRIOR_TIMING_2026-10-02.md).

Implementation: [experiments/dependency_memory/query_weighting](../dependency_memory/query_weighting).

Saved results: [experiments/dependency_memory/results/query_weighting_2026-10-02.json](../dependency_memory/results/query_weighting_2026-10-02.json).

## conditional-code

**Conditional six-block construction** — 2026-10-02 · completed

331,857,648 errors on 1,207,959,552 outcomes at 12 parent bits and one child bit, improving a refined product. The three-block bracket tightens to [40,072,40,514]/147,456.

**Limits:** Small finite gain; no final six-block optimum or locality certificate. Public payload is 120 bytes.

Claims: [C69](../../paper/claims.csv).

Read first: [research/CONDITIONAL_SIX_BLOCK_CODE_2026-10-02.md](../../research/CONDITIONAL_SIX_BLOCK_CODE_2026-10-02.md).

Implementation: [experiments/dependency_memory/conditional_coding](../dependency_memory/conditional_coding).

Saved results: [experiments/dependency_memory/results/conditional_six_block_2026-10-02.json](../dependency_memory/results/conditional_six_block_2026-10-02.json).

## trellis-code

**Finite trellis construction** — 2026-10-02 · completed

An exact 16-state encoder has 867,837 errors on 3,145,728 four-block outcomes, versus pair-product 869,376, with eight parent bits and one child bit. Public labels occupy 96 packed bytes.

**Limits:** Smaller cycles lose; the existing three-block product wins at common lengths 12n. Longer-cycle optimality is open.

Claims: [C68](../../paper/claims.csv).

Read first: [research/FINITE_TRELLIS_CODE_2026-10-02.md](../../research/FINITE_TRELLIS_CODE_2026-10-02.md).

Implementation: [experiments/dependency_memory/trellis_coding](../dependency_memory/trellis_coding).

Saved results: [experiments/dependency_memory/results/trellis_coding_2026-10-02.json](../dependency_memory/results/trellis_coding_2026-10-02.json).

## full-rate-curve

**Full unrestricted asymptotic rate curve** — 2026-10-02 · completed

Forty-eight exact polynomial comparisons certify the unrestricted curve at every parent rate; error reaches the 1/4 floor near 2.548795 bits per block.

**Limits:** Uniform source and stated delayed-query law; no efficient finite near-curve code or natural-workflow result follows.

Claims: [C67](../../paper/claims.csv).

Read first: [research/UNRESTRICTED_RATE_CURVE_2026-10-02.md](../../research/UNRESTRICTED_RATE_CURVE_2026-10-02.md).

Implementation: [experiments/dependency_memory/rate_curve](../dependency_memory/rate_curve).

Saved results: [experiments/dependency_memory/results/rate_curve_2026-10-02.json](../dependency_memory/results/rate_curve_2026-10-02.json).

## decoder-completion

**Balanced-source complementary completion** — 2026-10-02 · completed

Complementary final endpoints suffice at every block count and parent capacity under the balanced-source average-error contract. Checks cover 9,216 branch cases and 3,686,400 whole-code routes.

**Limits:** A biased-source counterexample and individual harms delimit the result; the numerical frontier is unchanged.

Claims: [C66](../../paper/claims.csv).

Read first: [research/COMPLEMENTARY_COMPLETION_2026-10-02.md](../../research/COMPLEMENTARY_COMPLETION_2026-10-02.md).

Implementation: [experiments/dependency_memory/decoder_completion](../dependency_memory/decoder_completion).

Saved results: [experiments/dependency_memory/results/decoder_completion_2026-10-02.json](../dependency_memory/results/decoder_completion_2026-10-02.json).

## parent-rate-spectrum

**Parent-rate support spectrum** — 2026-10-01 · completed

Eight rational-rate intervals and an analytic unsigned support transition near 0.620690001029 bits per block are checked.

**Limits:** The unrestricted curve between these checks was open at this milestone; C67 later resolves it.

Claims: [C65](../../paper/claims.csv).

Read first: [research/PARENT_RATE_SPECTRUM_2026-10-01.md](../../research/PARENT_RATE_SPECTRUM_2026-10-01.md).

Implementation: [experiments/dependency_memory/rate_spectrum](../dependency_memory/rate_spectrum).

Saved results: [experiments/dependency_memory/results/rate_spectrum_2026-10-01.json](../dependency_memory/results/rate_spectrum_2026-10-01.json).

## all-decoder-cover

**Unrestricted three-block converse** — 2026-10-01 · completed

An oracle gate and 46,492 near mixed cases cover all final decoders, establishing lower bound 40,072/147,456.

**Limits:** The historical upper witness is 40,529; C69 tightens it to 40,514. Exact finite optimality remains open.

Claims: [C63](../../paper/claims.csv).

Read first: [research/ALL_DECODER_THREE_BLOCK_COVER_2026-10-01.md](../../research/ALL_DECODER_THREE_BLOCK_COVER_2026-10-01.md).

Implementation: [experiments/dependency_memory/joint_coding_general](../dependency_memory/joint_coding_general).

Saved results: [experiments/dependency_memory/results/joint_three_block_general_2026-10-01.json](../dependency_memory/results/joint_three_block_general_2026-10-01.json); [experiments/dependency_memory/results/joint_three_block_general_auxiliary_2026-10-01.json](../dependency_memory/results/joint_three_block_general_auxiliary_2026-10-01.json); [experiments/dependency_memory/results/joint_three_block_certificate_2026-10-01.json](../dependency_memory/results/joint_three_block_certificate_2026-10-01.json).

## complementary-cover

**Complementary three-block converse** — 2026-10-01 · completed

All 256 complementary tables per block are covered, including J-dependent predictions; the lower bound remains 40,072/147,456.

**Limits:** Noncomplementary endpoints are outside this certificate; C63 covers them.

Claims: [C62](../../paper/claims.csv).

Read first: [research/COMPLEMENTARY_DECODER_COVER_2026-10-01.md](../../research/COMPLEMENTARY_DECODER_COVER_2026-10-01.md).

Implementation: [experiments/dependency_memory/joint_coding_complement](../dependency_memory/joint_coding_complement).

Saved results: [experiments/dependency_memory/results/joint_three_block_complement_2026-10-01.json](../dependency_memory/results/joint_three_block_complement_2026-10-01.json); [experiments/dependency_memory/results/joint_three_block_certificate_2026-10-01.json](../dependency_memory/results/joint_three_block_certificate_2026-10-01.json).

## three-block-cover

**Restricted three-block converse** — 2026-10-01 · completed

The restricted final-decoder family has lower bound 40,072/147,456 and the historical 40,529 upper witness.

**Limits:** This converse alone assumes final predictions independent of late coordinate J; later converse packages extend coverage.

Claims: [C60](../../paper/claims.csv).

Read first: [research/JOINT_THREE_BLOCK_COVER_2026-10-01.md](../../research/JOINT_THREE_BLOCK_COVER_2026-10-01.md).

Implementation: [experiments/dependency_memory/joint_coding_cover](../dependency_memory/joint_coding_cover).

Saved results: [experiments/dependency_memory/results/joint_three_block_cover_2026-10-01.json](../dependency_memory/results/joint_three_block_cover_2026-10-01.json); [experiments/dependency_memory/results/joint_three_block_certificate_2026-10-01.json](../dependency_memory/results/joint_three_block_certificate_2026-10-01.json).

## three-block-witness

**Explicit three-block witness** — 2026-10-01 · completed

40,529 errors on all 147,456 outcomes, versus 40,992 for the earlier concatenation, at six parent bits and one child bit.

**Limits:** Achievable construction, not a finite optimum. C69 later improves the witness to 40,514 without rewriting this certificate.

Claims: [C59](../../paper/claims.csv).

Read first: [research/JOINT_THREE_BLOCK_WITNESS_2026-10-01.md](../../research/JOINT_THREE_BLOCK_WITNESS_2026-10-01.md).

Implementation: [experiments/dependency_memory/joint_coding_finite3](../dependency_memory/joint_coding_finite3).

Saved results: [experiments/dependency_memory/results/joint_three_block_certificate_2026-10-01.json](../dependency_memory/results/joint_three_block_certificate_2026-10-01.json).

## decoder-frontier

**Decoder-complete rate-two frontier** — 2026-09-21 · completed

All 1,679,616 legal final tables are covered. The limiting error at two parent bits per block is strictly between 0.2618989799 and 0.2618989801; the lower bound holds at every finite block count.

**Limits:** Uniform finite bit model; no model trials or practical-agent result. External correctness and priority review remain open.

Claims: [C34](../../paper/claims.csv).

Read first: [research/DECODER_COMPLETE_FRONTIER_2026-09-21.md](../../research/DECODER_COMPLETE_FRONTIER_2026-09-21.md).

Implementation: [experiments/dependency_memory/joint_coding](../dependency_memory/joint_coding).

Saved results: [experiments/dependency_memory/results/decoder_frontier_certificate.json](../dependency_memory/results/decoder_frontier_certificate.json); [experiments/dependency_memory/results/decoder_frontier_report.md](../dependency_memory/results/decoder_frontier_report.md).

## joint-block

**Two-block witness and asymptotic threshold** — 2026-09-21 · completed

The two-block witness attains 283/1024 error on all 6,144 outcomes. A rational channel gives the earlier asymptotic upper bound 101/384; the threshold for approaching 1/4 is about 2.5488 parent bits per block.

**Limits:** The two-block optimum is not claimed. Later decoder-complete and all-rate results strengthen the earlier asymptotic bound.

Claims: [C31, C32, C33](../../paper/claims.csv).

Read first: [research/JOINT_BLOCK_CODING_2026-09-21.md](../../research/JOINT_BLOCK_CODING_2026-09-21.md).

Implementation: [experiments/dependency_memory/joint_coding](../dependency_memory/joint_coding).

Saved results: [experiments/dependency_memory/results/joint_block_certificate.json](../dependency_memory/results/joint_block_certificate.json); [experiments/dependency_memory/results/joint_block_report.md](../dependency_memory/results/joint_block_report.md).

## exact-chain

**Exact four-bit chain optimum** — 2026-09-19 · completed

Complete enumeration of 171,798,901 four-cell partitions establishes exact error 9/32; 128 partitions attain it. The saved witness is independently graded.

**Limits:** Routine checks verify the search source, count and witness; they do not repeat the full exhaustive search.

Claims: [C21](../../paper/claims.csv).

Read first: [research/EXACT_CHAIN_OPTIMUM_2026-09-19.md](../../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md).

Implementation: [experiments/dependency_memory/exact_chain.py](../dependency_memory/exact_chain.py).

Saved results: [experiments/dependency_memory/results/exact_chain_certificate.json](../dependency_memory/results/exact_chain_certificate.json).

## scaling-audit

**Scaling, leave-one-out and independent proof checks** — 2026-09-19 · completed

Local information arguments allow joint encoding across blocks: exact child-optimal error needs 3k parent bits; 2k parent bits force error above 1/4 + 1/512. Independent finite checks audit the proof ingredients.

**Limits:** Local derivation with external review open; do not multiply the one-block 1/32 excess across arbitrary joint encodings.

Claims: [C11, C12, C13](../../paper/claims.csv).

Read first: [research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md](../../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md).

Implementation: [experiments/dependency_memory/compatibility_scaling.py](../dependency_memory/compatibility_scaling.py); [experiments/dependency_memory/audit_scaling.py](../dependency_memory/audit_scaling.py).

Saved results: [experiments/dependency_memory/results/compatibility_scaling_certificate.json](../dependency_memory/results/compatibility_scaling_certificate.json); [experiments/dependency_memory/results/scaling_audit_certificate.json](../dependency_memory/results/scaling_audit_certificate.json).

## parent-compatibility

**Four-bit parent/child compatibility** — 2026-09-16 · completed

Three parent bits suffice and are necessary to attain the isolated child optimum of 25%. The earlier two-bit certificate supplies only a conservative 49/192 lower bound.

**Limits:** The separate exact-chain computation sharpens this bound to 9/32; do not treat the conservative certificate as the optimum.

Claims: [C04, C05](../../paper/claims.csv).

Read first: [research/LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md](../../research/LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md).

Implementation: [experiments/dependency_memory/compatibility.py](../dependency_memory/compatibility.py).

Saved results: [experiments/dependency_memory/results/compatibility_certificate.json](../dependency_memory/results/compatibility_certificate.json).

## single-cut

**Single-cut coding and reveal timing** — 2026-09-16 · completed

Exact small-source codebook enumeration separates a late queried coordinate from an early relevance cue. The isolated four-bit first cut has error 3/16; the isolated one-bit three-coordinate child has error 1/4.

**Limits:** One memory boundary in the timing comparison; it does not establish the two-stage chain optimum.

Claims: [C03](../../paper/claims.csv).

Read first: [experiments/dependency_memory/README.md](../dependency_memory/README.md).

Implementation: [experiments/dependency_memory/experiment.py](../dependency_memory/experiment.py).

Saved results: [experiments/dependency_memory/results/exact_frontier.csv](../dependency_memory/results/exact_frontier.csv); [experiments/dependency_memory/results/compatibility_certificate.json](../dependency_memory/results/compatibility_certificate.json); [experiments/dependency_memory/results/disclosure_timing.csv](../dependency_memory/results/disclosure_timing.csv).
