# Paper workspace

Working title: **Repeated Context Compression with Delayed Task Dependencies**. The title, venue, and authorship are provisional.

## Documents to edit

- [Manuscript](manuscript.md): the main paper entry point, including the finite example, locally audited scaling result, scripted recovery comparison, completed Luna studies, and limitations.
- [Living findings draft](findings-draft.md): a short account of what we know, what the new results change, and the next milestone. Update it together with the claim register as evidence changes.
- [Outline](outline.md): section-by-section argument and remaining work.
- [Related-work map](related-work.md): nearby results and the distinctions a novelty argument must address.
- [Claim register](claims.csv): what may currently be stated, with evidence and limitations.
- [Bibliography](references.bib): stable citation keys and known metadata. Entries with incomplete metadata say so.

Use `[@citation-key]` citations in Markdown. The builder checks keys and appends readable references to the assembled Markdown. Its HTML preview is a self-contained reading copy with headings and linked citations; it does not typeset LaTeX mathematics. The editable document is always `paper/manuscript.md`, not a generated preview.

```powershell
python scripts/build_paper.py
python scripts/validate_context_repo.py
```

Generated files are under ignored `build/paper/`. No external typesetting software is required to begin drafting.

## Current draft and update discipline

Living draft v0.41 adds [loss-weighted overflow and public allocations](../research/LOSS_WEIGHTED_OVERFLOW_2026-10-02.md),
claim C74. The same actors/tables have error <=27.450867% at k=768 and
<=27.064671% at k=12288, below repeated C69. Seven checked codes improve
the named prior C72 codes using upper/lower comparisons; three smaller
codes still lose to C69. Exact convex search minimizes five outward
bounds over all integer allocations, not actual code risk. All 384
unsuccessful quantizer starts and 29 bindings remain preserved. Public
table bytes stay 1288; local timing and analytic population guarantees
have distinct scopes. All 583 tests pass, repository validation reports PASS with 74 claims/
55 bibliography entries/171 PDF hashes/195 immutable imports, and paper
assembly checks all 48 cited sources. New selector
limit, external correctness/priority, near-C67 codes and agent benefit
remain open; zero new model calls or natural episodes.

Earlier living draft v0.40 adds the [deterministic distortion-cover family](../research/DETERMINISTIC_NEAR_LIMIT_CODE_2026-10-02.md),
claim C73. A public polynomial builder and actors attain C67's actual limiting
error at every integer input length, with exactly 2k parent bits/one child bit.
This is an application of established greedy coverage and source coding.
Formal convergence is supplied; useful finite convergence stays open:
the small three-block code loses and checked conservative bounds use enormous
groups. Fifty-four analytic bounds, 454848 full small actor queries, 3552
constructed diagnostics and 16 bindings keep their scopes explicit.
All 575 tests, repository validation and 48-source paper assembly pass.
External correctness/priority and natural-agent/model/cost benefit remain
open; zero new model calls or natural episodes.

Earlier living draft v0.39 adds [coordinated tied-answer coding](../research/COORDINATED_TIE_CODE_2026-10-02.md),
claim C72. Joint equal-loss constant choices reduce entropy; the compatible
pair minimum has counts [121,85,25,25]/256. A fixed-eight code has error at
most 27.080384% at k=12,288, below both C71 codes' lower bounds at the same
2k/one-bit cap. Its actual limit is 26.929308%; a separate implemented
polynomial growing family tends to 26.782918%, still above C67. Public data
increase to 1,288 packed bytes versus C71's 10. Published minimum-entropy
greedy cover underpins the local entropy-limit deduction. Forty finite bounds,
small physical populations and large diagnostics have separate scopes.
Selected smaller designs lose. External correctness/priority, efficient
near-C67 codes and practical-agent benefit remain open; zero new model calls.

Earlier living draft v0.38 adds the [implemented hard-cap entropy code](../research/HARD_CAP_ENTROPY_CODE_2026-10-02.md),
claim C71. A polynomial arithmetic-grid family charges its fallback flag
inside 2k parent bits and retains one child bit before J. Its default risk
tends to 27.075301%, still above C67. At k=12,288 the retained rational control
has a conservative 27.198892% error upper bound, below the repeated C69 code.
Sixteen exact bounds preserve smaller-length losses and the stronger finite
control. Full small populations and constructed large diagnostics have distinct
execution scopes; larger risks are bounded analytically. Generic entropy
quantization/time sharing are established, with external review, near-optimal
codes and natural-agent/model/cost benefit open. Zero new model calls or episodes.

Earlier living draft v0.37 adds the [query-prior and timing deductions](../research/QUERY_PRIOR_TIMING_2026-10-02.md),
claim C70. Known class probabilities permit unequal allocation; five exact
witnesses include 25.718661% limiting error at p=1/4. Unknown-prior minimax
retains C67's rate-two limit, while an early actual class cue reaches 1/4
using 3n bits inside the same 4n cap. An opposite-orientation finite pair has
the same error for every source-independent p without extra instance state;
simple unequal allocation beats it at skewed known priors. Exact finite
sensitivity has 52 affine segments. These are scoped consequences and
controls, with external correctness/priority, other laws and efficient
near-limit finite codes open. Zero model calls or natural-task outcomes.

Earlier living draft v0.36 adds the [conditional six-block construction](../research/CONDITIONAL_SIX_BLOCK_CODE_2026-10-02.md),
claim C69. A refined component has 40,514/147,456 errors and no improving one-word
replacement, yet its two-copy product has an improving single joint word.
Eight conditional changes give 331,857,648/1,207,959,552 errors, below the stronger
product 331,890,688 at the same12-bit parent and one-bit child. Independent
six-block products preserve the error at 6n and win at common12n; public label
payload is 120 bytes. The gain is small, the three-block bracket width is 442,
and final six-block locality/optimality and external correctness/priority remain
open. Grouped weighted grading and full component replacement checks are
independent of native discovery. Zero model calls or natural-task outcomes.

Living draft v0.35 adds the [finite trellis code](../research/FINITE_TRELLIS_CODE_2026-10-02.md),
claim C68. At four blocks, an eight-bit parent and one-bit child give 867,837
errors on 3,145,728 outcomes, below the pair-product control's 869,376. Exact
16-state Viterbi uses 1024*k branch relaxations; independent four-block groups
preserve that error for k=4*n with two parent bits per block. At k=12*n the
existing three-block product remains better. Smaller cycles
lose to the existing controls. Finite optimality and codes approaching the
curve remain open; generic trellis coding is established and no new model or
natural-task result is added. Two bounded primary sources delimit the method.

Living draft v0.34 adds the [full unrestricted asymptotic curve](../research/UNRESTRICTED_RATE_CURVE_2026-10-02.md),
claim C67. Forty-eight exact polynomial inequalities extend the unsigned
scalar optimization to every positive slope, with strict coding slack inside
floor(k*r) parent bits. The earlier curve-open milestones below retain their
dated scope. Finite optimal codes, external correctness/priority and natural
workflow applicability remain open; no new model outcomes are added.

Living draft v0.33 adds the [completion theorem](../research/COMPLEMENTARY_COMPLETION_2026-10-02.md),
claim C66. Complementary decoders suffice for every k/B under balanced source
and independent queries, preserving the encoder/capacity and child timing.
The remaining supporting comparison has six families. A biased-source example
and individual harms delimit this average-error result. Numerical bounds and
the best finite witness are unchanged; no model or natural-task gain is added.

Living draft v0.32 adds the [parent-rate spectrum](../research/PARENT_RATE_SPECTRUM_2026-10-01.md),
claim C65. Eight all-decoder rational-rate asymptotic intervals are narrower
than 2e-11. A scalar unsigned-family reduction has a unique two-word/eight-word
support transition near 0.620690001029 information bits per block. This leaves
the unrestricted curve at untested rates and efficient finite codes open.
No model call, natural episode or production benefit is added.

Living draft v0.31 adds the [static source-analysis control](../research/STATIC_SCOPE_CONTROL_2026-10-01.md),
claim C64. With the codec held fixed, static and authored dispatch contracts
score 24/24, as do five of the seven saved model contracts; two remain oversized.
Three inspected programs and one constructed late-key family agree on 51,566
finite rows, including whole-input quota fallback. Eleven tests pass. This adds
no model call or natural task, universal Python proof or slicing novelty claim.

Living draft v0.30 adds the [all-decoder three-block converse](../research/ALL_DECODER_THREE_BLOCK_COVER_2026-10-01.md),
claim C63. The unrestricted D_3(6) is enclosed in [27.1756%, 27.4855%], including
noncomplementary and repeated prediction endpoints. An oracle gate and 46,492
near orbit cases cover all final decoders; seven independent tests check exact
witnesses, tied ideals and preserved auxiliary evidence. Exact finite optimum,
external proof/priority review and natural-agent performance remain open.

Living draft v0.29 adds the [complementary-decoder converse](../research/COMPLEMENTARY_DECODER_COVER_2026-10-01.md),
claim C62. The same finite bracket now includes all 256 complementary tables
per block, possibly depending on the late coordinate. Six symmetry orbits and
56 mixed cases have checked cover weights; five independent tests pass.
Noncomplementary decoders were outside C62; C63 above extends the converse.
The exact finite optimum remains open.

Living draft v0.28 adds the [source-only scope-inference findings](../research/SCOPE_INFERENCE_FINDINGS_2026-10-01.md),
claim C61. All eight permitted identities were dispatched: seven catalog-complete
contracts and one permanent timeout. Five contracts score 12/24 imposed late
queries; two exceed the parent cap and score 0/24. Strong zero-model controls
score 24/24. The original primary criterion remains unassessable; no natural-task
or production advantage is established.

Living draft v0.27 adds the [restricted three-block converse](../research/JOINT_THREE_BLOCK_COVER_2026-10-01.md),
claim C60. An elementary cover argument and exact finite ingredients give
40,072/147,456 as a lower bound for late-coordinate-independent prediction,
leaving a 457-outcome gap to the witness. Arbitrary joint encoders in that family
are covered; general endpoint decoders, finite optimality and novelty are not.

Living draft v0.26 adds the [three-block explicit code](../research/JOINT_THREE_BLOCK_WITNESS_2026-10-01.md),
claim C59. Six parent bits and one child bit achieve 40,529 errors on 147,456
outcomes, improving the existing 40,992-error concatenation. Independent route
grading and six new tests check the saved witness. This is a finite upper bound;
optimality, priority and model/task performance are not established.

Living draft v0.25 adds the [public-schema serialization control](../research/SCOPE_CODEBOOK_CONTROL_2026-10-01.md),
claim C58. The existing fixed-schema codec and cached public outcomes each
answer all 24 constructed late queries, versus 12/24 for ordinary authored JSON,
under unchanged byte caps. At that offline milestone the learner launch was
frozen and undispatched; the subsequent results are recorded in v0.28.
This is inspected offline development evidence, with no new compression or
caching novelty, model outcome or production-saving claim.

Living draft v0.24 adds the [local method audit and timing screen](../research/WORKFLOW_METHOD_AUDIT_2026-10-01.md),
claims C56–C57. Exact checked tables with fallback have the same receipt state
as direct retention; original model answers need not be equal. E0001 is B-only
for its actual query. A sixteen-file method freeze and four-arm fixture/replay
runtime support future work, with zero new provider generations or prospective
outcomes. External human review remains pending.

Living draft v0.23 records the [October 1 retained-evidence audit](../research/EVIDENCE_USE_AUDIT_2026-10-01.md),
claims C53–C54. It reconciles 319 observed final answers across three inspected
studies. A pure public-rule check contradicts 32 wrong proposals but cannot check
39 correct proposals. An elementary same-input/different-history example prevents
interpreting consistency as source completeness. There are zero new model calls
and no measured repairs. Actual task intake is segmented within ContextResearch;
future prospective evaluation and independent blind evaluation remain distinct.
Claim C55 records the first same-repository development episode: six successful
actual commands at two source checkpoints and a direct-receipt serialization
that fits both byte caps. No new model result is attributed to that intake.

Living draft v0.22 records the [interrupted executed-workflow follow-up](../research/EXECUTED_WORKFLOW_COMPARISON_2026-09-29.md),
claim C52. Two separately frozen launches produce 24 metered answers and two
transport gaps; 82 identities remain undispatched. One direct-record final
answer misuses sufficient retained evidence. Only one case is fully paired, so
the intended twelve-case comparison remains unassessable. The new corpus has
48 actual command runs in twelve scripted scenarios from one fixture family.

Living draft v0.21 adds the [September 29 development comparison](../research/WORKFLOW_LUNA6_COMPARISON_2026-09-29.md),
claim C51. All 36 Luna 6 medium calls complete. Checked/direct/indexed/full score
4/4 and prose 3/4; direct records use the fewest model credits in both cache views.
The four cases reuse one observed local workflow and three constructed controls,
not untouched real tasks. Local resource measurements are separate from model
credits. The packet's held-out primary criterion remains unassessed.

Living draft v0.20 records the [decoder-compatible handoff correction and branch
audit](../research/DECODER_COMPATIBILITY_REPLAY_2026-09-24.md), claim C50. The
parent certificate now exercises the actual child check on every owner pair;
the saved 12-parent/252-pair replay is unchanged. Wrong or missing non-ID state
can still pass. This is an offline software correction following the v0.19
cross-record negative result, not new model evidence or a semantic guarantee.

Living draft v0.18 adds the [prospective schema-transfer test](../research/SCHEMA_TRANSFER_PROSPECTIVE_2026-09-22.md), claim C48. It tests different constructed schema structures, whose definitions were visible in the frozen casebook, and makes 126 fresh Luna medium calls. Automatic direct meets the prespecified 1-versus-2 failure and lower-cost comparison with prompting, but indexed recovery is cheaper and succeeds on all 18 cases. Model-proposal checking mainly invokes fallback, and certified retention still permits final-model mistakes. The broader cost-superior mechanism remains unestablished.

Living draft v0.17 adds the [annotated-schema follow-up](../research/SCHEMA_CHECKS_UNSEEN_TRACES_2026-09-22.md), claim C47. Six new constructed evaluation traces and 72 Luna medium calls yield 12/12 for prompting, automatic checks, direct records, indexed recovery and full history. Automatic records cost less than prompting and tie direct outcomes, but the prespecified fewer-failure criterion fails; direct and indexed controls are cheaper. Evaluation holds out values within known annotated schemas, not new schema structures or production incidents. The local CPU sensitivity was calibrated after the run because the live timer resolved short operations as zero.

Living draft v0.16 adds the [fresh GPT-6 Luna medium study](../research/LUNA6_DELAYED_FAILURES_2026-09-22.md), claims C44-C46. It records 141 calls, live failures, complete model-cost accounting, and strong direct/recovery/full-history controls. A stronger prompt eliminates clipping but retains semantic failures. The study uses constructed handoffs and imposed byte limits; manual adapter knowledge, public-rule availability and development reuse remain explicit limitations.

Living draft v0.15 adds the [historical workflow replay](../research/HISTORICAL_WORKFLOW_REPLAY_2026-09-22.md), claims C41-C43. Eight real attempt records support counterfactual delayed handoff failures, byte-limited receipt repair and conditional synthetic cost frontiers. Direct receipts outperform iterative repair costs. Scope controls test reuse/invalidation. The evidence was inspected during development; there is no held-out, compaction-causal or production-saving claim.

Living draft v0.14 adds the [strict novelty audit](../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md), claim C40. The finite recovery/repair objective is explicitly reformulated as accepted strategies and weak coloring, with independent checks. Close architectural precedents further narrow the claim: no general feedback-algorithm novelty or practical superiority is established. Realistic evidence extraction and measured utility remain open systems questions.

Living draft v0.13 adds the [execution-graded feedback loop](../research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md), claims C37-C39. The finite loop repairs a weak schema and exposes cycling and information-channel mistakes, while the strong critical-field baseline matches it. Two actual record boundaries and 48 constructed contracts are implemented. No LLM, natural-task or matched-total-cost advantage is established; generic feedback and cumulative constraints are attributed to prior work.

Living draft v0.12 adds the [compaction collision auditor](../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md), claims C35-C36. This is a user-directed research pivot to executable whole-group failure and recovery certificates, with 12 constructed diagnostics and a finite repair codebook. Established dynamic programming and hypergraph methods are attributed; publication novelty, natural-task integration and practical improvement remain open. Prior mathematical and model-study evidence is preserved.

Living draft v0.11 adds the [decoder-complete rate-two certificate](../research/DECODER_COMPLETE_FRONTIER_2026-09-21.md), claim C34: a strict limiting-error interval (0.2618989799, 0.2618989801) and an all-k lower bound allowing every decoder. The standard-library verifier covers 1,679,616 decoder tables. Publication novelty and external correctness review remain open.

Living draft v0.10 added the [September 21 joint-coding extension](../research/JOINT_BLOCK_CODING_2026-09-21.md), claims C31-C33: a finite two-block improvement, an asymptotic upper bound at rate two, and the approximately 2.5488-bit threshold for approaching the child optimum. The earlier model studies are unchanged. The explicit finite witness is executable; the long-block results are analytic existence statements, with novelty and external review open.

The manuscript now incorporates the [exact finite-chain optimum](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md), [locally audited scaling derivation](../research/PROOF_AUDIT_2026-09-18.md), and [exact restricted recovery results](../experiments/dependency_memory/results/recovery_frontier_report.md). External review and novelty remain open. The short findings draft is versioned and dated; v0.3 added the [correctness audit](../research/CORRECTNESS_AUDIT_2026-09-19.md) and its refinements to the [staged pilot](../docs/LLM_PILOT_SPEC.md). For a new result, update its claim-register evidence and limitation, then the relevant manuscript/draft paragraphs and `docs/STATUS.md`. Keep the negative controls and avoid turning experiment plans into reported outcomes. Realistic agent performance remains unresolved.

Templates: [derivation](templates/derivation.md), [source note](templates/source-note.md), [experiment plan](templates/experiment-plan.md). The [current protocol](../docs/EXPERIMENT_PROTOCOL.md) is the governing experimental specification.

Living draft v0.9 includes the 96-request Luna tranche (C25), exact post-hoc parent/child grading (C26), the revision-direction design (C27), the offline held-out clue checkpoint (C28), the completed 24-request follow-up (C29), and the completed 1,536-request matched retention study (C30). The latter's primary comparison yields a small normalized benefit whose descriptive interval includes zero; improvement is not established. The follow-up's 24 optimal choices concern a separate simplified task and do not establish a fix for the first workflow. The earlier fake controls remain C24. No native-harness superiority or external endorsement is established; held-out request integration and evaluation remain unfinished.
