# Before an agent forgets: inspect, retain, or recover?

Living findings draft v0.38 — October 2, 2026. This is a short research summary, not a submission-ready paper. The [manuscript](manuscript.md) is the main paper entry point; the [claim register](claims.csv) links substantive statements to their evidence.

## A computable code improves the larger finite control

The [hard-cap arithmetic code](../research/HARD_CAP_ENTROPY_CODE_2026-10-02.md)
uses exactly two parent bits per four-bit source block, including its fallback
flag, and one child bit before the final coordinate query. It compresses a
public mixture of two constant responses and full majority signatures. A fixed
arithmetic midpoint stores the quantizer outputs when they fit; failure emits
zero. No source, old parent or auxiliary output list reaches the final actor.
The tables use 10 packed public bytes; public descriptors and program/framing
are separate from instance bits. Encoder/updater bit complexity is polynomial.
[C71]

At 12,288 blocks a retained simple schedule has error at most 27.198892%, below
C69's repeated six-block 27.472579%. The new default has a weaker bound there,
27.204464%, but its actual limiting risk is about 27.075301%. This remains
above the optimal 26.189898% limit. Both schedules provably lose at the four
checked smaller lengths; the simple control gives stronger finite bounds at
three larger lengths. Sixteen exact overflow/excess-loss bounds establish
these comparisons without enumerating the huge source populations. [C71]

All small sources and every public allocation at k<=3 execute 608,640 final
queries. Twelve constructed large inputs execute 864 additional diagnostics;
those spots do not measure a population risk. Exact integer frontier checks
and a whole-population proof supply the larger bounds, which are conservative
rather than exact average errors. Entropy-constrained quantization and time
sharing have classical precedent [@chou1989entropy]. This implements a specific
toy-model construction; near-optimal efficient codes, external correctness/
priority and natural-agent/model/token/cost benefit remain open. Zero new model
calls or prospective natural episodes. [C71]

## Query probabilities and early query information have different effects

The [new extension](../research/QUERY_PRIOR_TIMING_2026-10-02.md) divides uniform
four-bit blocks into two equal public classes. If the fixed source-independent
query prior p is known before compression, optimal limiting error is
min pD(r_L)+(1-p)D(r_R) over r_L+r_R<=4, with D from C67. At p=1/4 the
exact enclosure is [0.257186606420,0.257186606421], below the uniform
26.189898% limit. Five rational witnesses have strict combined coding slack
inside the same two parent bits per block and one child bit before J. No
efficient finite encoder near these limits is supplied. [C70]

If p is unknown to parent design, worst-case error instead tends to D(2).
A finite opposite-orientation pair preserves C69's 27.472579% for every fixed
source-independent p using 24 parent bits for twelve blocks, no orientation
state and the same 120 public label bytes. Known-prior unequal allocation is
a stronger control away from balanced queries: at p=1/4 a simple 1/3-bit
allocation gives 26.5625% and beats that pair. Fifty-two exact segments cover
known-prior reencoding of the fixed six-block book; this is not finite optimality.
The original frozen encoder can lose its product advantage under skew. [C70]

If the actual class T arrives before the parent, three-bit signatures for
its n blocks achieve 25% using 3n bits inside the common 4n cap. T is
independent of the source and R/O/J remain late. This early cue differs from
knowing query probabilities: its timing changes which source values need
retention. The late uniform limit has an additional 1.189898 percentage points
of error. These are local C33/C67 consequences and checked controls, with
generic allocation/symmetry/side-information novelty, external proof/priority,
adaptive/biased laws and natural-agent benefit open. Zero model calls or new
natural episodes; 589,824 final routing checks are not twelve-block source
enumeration. Earlier milestones below retain their dated scope. [C70]

## A stronger product control still leaves a small joint gain

The [new six-block construction](../research/CONDITIONAL_SIX_BLOCK_CODE_2026-10-02.md)
reduces error from 27.475315% for two refined three-block components to 27.472579%
at the same 12 parent bits and one child bit. The component has 40,514 errors
on 147,456 outcomes and no improving single-word replacement among all 262,144
candidates. Its product nevertheless has an improving single six-block word;
eight changes avoid 33,040 errors on 1,207,959,552 outcomes. This is a small
finite gain and a scoped counterexample, not a general quantization novelty.
Claim C69; the current unrestricted three-block bracket has width 442 errors.

The independent checker uses 16 groups of left sources and weighted actor
queries to cover all 16,777,216 six-block sources. It physically executes
11,783,592 actor queries representing 1,207,959,552 outcomes. Public labels occupy
120 payload bytes; instance memory is separately 12 bits. Independent six-block
segments preserve the result at k=6*n and beat the refined three-block product
at common k=12*n. Final six-block locality/optimality, external correctness,
priority and useful natural-agent gains remain open. No new model call or
prospective natural episode is added. Earlier milestones below retain their
dated scope, including C68's weaker repeated-code comparison.

## A finite encoder now improves the four-block controls

The [fixed trellis code](../research/FINITE_TRELLIS_CODE_2026-10-02.md) achieves
867,837 errors on all 3,145,728 four-block outcomes, versus 869,376 for two
independent pairs. The parent still has eight bits and the child one bit formed
before the late coordinate. Exact reverse Viterbi uses 16 states and 1024*k
branch relaxations; the fixed response labels occupy 96 packed public bytes.
Independent four-block groups preserve the error 289279/1048576 for every
k=4*n at two parent bits per block. At common k=12*n, the existing three-block
product has lower error, leaving the best known asymptotic upper bound unchanged.
This gives a particular implemented finite
construction, while finite optimality and codes approaching C67's curve remain
open. Claim C68. The same long-cycle tables perform worse at k=1,2,3, and all
33 initial permutation attempts failed. Generic trellis/Viterbi and product
coding are established methods. No model call or prospective natural task is
added; external correctness and publication priority remain open.

## The full asymptotic bit-model curve is now characterized

The [new unrestricted theorem](../research/UNRESTRICTED_RATE_CURVE_2026-10-02.md)
closes the gap between the eight earlier support points. Forty-eight exact
polynomial comparisons prove that the unsigned decoder attains every
positive-slope minimum. Its scalar quadratic therefore parametrizes limiting
error at every parent rate under the same uniform four-bit source and one-bit
child. Claim C67. The curve goes from 1/2 at zero rate to 1/4 at about 2.548795
bits per block; the support transition occurs near 0.620690 bits per block.
Channel mixing provides strict coding slack inside floor(k*r) bits. Arbitrary
joint encoding and heterogeneous tables are included. This is an exact
parametric asymptotic model result, with finite optimal codes and efficient codes approaching the curve,
external correctness and priority still open. No new model or natural-task
outcomes are added.

## Complementary decoders suffice under the balanced source

The [new completion argument](../research/COMPLEMENTARY_COMPLETION_2026-10-02.md)
works for every block count and parent capacity, with the old encoder unchanged.
Public child-label swaps preserve one-bit memory and timing. Claim C66. It gives
a short alternative proof of the existing unrestricted three-block lower bound
and reduces the supporting comparison to six families. A biased source
has unrestricted zero error versus complementary minimum 1/6, and some individual
sources are harmed: this is a population-average theorem with explicit source
and query assumptions. Whole-code completion/reassignment improves the preserved
auxiliary books to 40,738 errors, still above the unchanged 40,529 witness.
The numerical frontier, model outcomes and natural-task count stay unchanged.

## The theoretical penalty now has a wider certified spectrum

The [new parent-rate result](../research/PARENT_RATE_SPECTRUM_2026-10-01.md)
encloses limiting error at eight rational early-memory rates while the child
remains one bit. Each slope covers every allowed final decoder; all interval
widths are below 2e-11. Claim C65. About 0.973 parent bits per block give 29.695%
limiting error, while 2.541 bits give 25.009%. These are bit-model calculations,
not token or workflow measurements. A separate unsigned-family proof reduces
every positive-slope objective to one mass and identifies a unique support
transition near 0.620690001029 information bits per block. C65 alone leaves
the unrestricted curve between slopes unproved; C67 supplies that comparison.
Finite encoders and publication priority remain open. No model call or natural
task is added.

## A stronger source-analysis control removes the need for more calls on this classifier

The [new AST control](../research/STATIC_SCOPE_CONTROL_2026-10-01.md) recovers a
finite-catalog-complete dispatch contract from source alone. With one common
codec, it and the authored contract answer 24/24 under unchanged byte caps;
five saved model contracts also reach 24/24, while two remain oversized.
Cached outcomes still use less memory. Claim C64. Three inspected repository
programs and a constructed late-key family agree on 51,566 finite rows, but
quota uses whole-input fallback. These are development checks, not a universal
Python proof or independent workflows. No model call or natural task is added;
the original missing answer and unassessable criterion remain unchanged.

## The finite bound now allows every final decoder

The [all-decoder proof](../research/ALL_DECODER_THREE_BLOCK_COVER_2026-10-01.md)
encloses the unrestricted three-block optimum D_3(6) in
**[27.1756%, 27.4855%]**, with six parent bits and one child bit. Claim C63.
It includes noncomplementary and repeated endpoints and permits tied ideal
predictions. An oracle-defect gate and 46,492 near mixed orbit cases cover all
allowed final decoders; 46,436 new exact target witnesses supplement the 56
complementary cases. Seven independent tests check the proof ingredients and
preserved auxiliary evidence. The existing 40,529-error construction remains
the upper endpoint. Exact finite optimality, external correctness and source
priority remain open. This is a three-block bit-error result; the asymptotic
frontier and evidence for natural agent workflows are unchanged.

## Earlier extension to complementary decoders

The [complementary-decoder proof](../research/COMPLEMENTARY_DECODER_COVER_2026-10-01.md)
extends the 27.1756%–27.4855% bracket to all 256 complementary decoder tables
per block, with possibly different tables across blocks and predictions that
depend on the late coordinate. Claim C62. Six symmetry orbits and 56 mixed cases
have exact cover witnesses; all 229,376 column instances are checked. Five tests
use direct routes, another symmetry construction and direct source sums rather
than the generator's convolution. Forty-six cases cannot improve the incumbent;
ten remain possible. Noncomplementary endpoints are outside C62's proof;
the all-decoder extension above leaves exact finite optimality and external
proof/priority review open.

## Complete scope can still exceed the memory budget

The [source-only inference launch and separate unattempted suffix](../research/SCOPE_INFERENCE_FINDINGS_2026-10-01.md)
finish all eight allowed dispatches: seven metered answers and one permanent
timeout. All seven contracts preserve classifier answers on 14,505 constructed
catalog rows. Five narrow contracts score 12/24 imposed late queries; two closure
contracts retain the entire accounting object, exceed the parent cap and score
0/24. Existing fixed-schema and cached-outcome controls score 24/24. Claim C61.
The frozen eight-answer criterion remains unassessable; no prompt ranking or
natural-task advantage follows. Known cost is 0.2232910 planning credits, with
7.65 retained for unknown usage. Actual debit and fully priced cost remain unknown.

## A finite lower bound for the construction's decoder family

A [separate cover proof](../research/JOINT_THREE_BLOCK_COVER_2026-10-01.md)
puts the restricted three-block optimum between 27.1756% and 27.4855% with six
parent bits and one child bit. Claim C60. The decoder's prediction must be
independent of the late coordinate J. Four tests check the finite ingredients,
including all 16,777,216 source/column pairs, and reject other endpoint decoders
from the bound API. This narrows a finite restricted problem; it does not tighten
the unrestricted frontier or prove optimality or publication novelty.

## A tighter explicit finite coding bound

The [three-block construction](../research/JOINT_THREE_BLOCK_WITNESS_2026-10-01.md)
uses six parent bits and one later child bit. All 147,456 possible delayed-query
outcomes give 40,529 errors, versus 40,992 for the existing pair-plus-one
concatenation. Average bit error falls from 27.7995% to 27.4855%. Claim C59.
The complete codebook and parent table are saved, with independent route checks.
This is an achievable upper bound, not a finite optimum, LLM performance result
or certified publication novelty. The known asymptotic frontier remains stronger.

## Separate field selection from serialization cost

The [new offline control](../research/SCOPE_CODEBOOK_CONTROL_2026-10-01.md)
reuses the existing public dictionary schema on eight inspected historical
attempts. Under the unchanged 4,096/1,536-byte caps, ordinary authored JSON
answers 12/24 constructed late queries; the same fields with the fixed schema
answer 24/24, as do cached public-program outcomes. All 14,505 constructed
catalog rows agree with the original classifier. Claim C58. A failure of this
JSON encoding is not an information-theoretic memory obstruction.

The separately [frozen source-only learner](../experiments/dependency_memory/scope_inference/PROTOCOL.md)
tests inferred contract completeness on one known program. Its prelaunch freeze
and offline control are preserved; the later live findings are recorded above.
Neither this offline result nor the source-only calls establish
natural-workflow prevalence, dictionary-coding novelty or production savings.

## Check whether the task needs earlier memory

The [next local audit](../research/WORKFLOW_METHOD_AUDIT_2026-10-01.md) narrows
the comparison. In the known exact-table grammar, checked writers with fallback
retain the same latest receipts as direct projection at both boundaries, even
with binding caps. A separate specification agrees with the grader on 158,340
constructed queries; 5,652 proposals and 52,780 bounded chains have zero state
disagreements. Claim C56. Original JSON presentation can still affect model
answers; this is no empirical accuracy or production-cost theorem.

The first actual task also needs no parent memory for its primary query: B
reruns every required check. It gives the same answer and run IDs as the full
history, and direct memory fits both caps. Claim C57. Keep this easy control
and screen future actual tasks without manufacturing delayed obligations.

The [frozen four-arm runtime](../experiments/dependency_memory/workflow_prospective/README.md)
implements direct, indexed, prose and full views with a common final check.
Checked memory is an offline canonical shadow. A six-slot scripted control
checks interfaces, not model performance. Prospective intake, external review
and the provider/budget contract remain unfinished.

## Retaining evidence does not ensure its correct use

The [October 1 offline investigation](../research/EVIDENCE_USE_AUDIT_2026-10-01.md)
audits all 319 observed final answers in three recent inspected studies, including
53 errors. In 31 errors a hand-written public-rule interpreter recovers the correct
answer from the retained memory. One additional prose answer overlooks a retained
success. Another typed memory is already wrong; seventeen are empty and three
cannot be checked by this parser. These are correlated development observations,
not an estimate of error prevalence in independent tasks.

A guard that sees only the admitted final request and proposal contradicts 32
wrong proposals, but also leaves 39 correct proposals uncheckable. Its hypothetical
readout agrees with full-ledger grading in 258/259 parseable cases. Vetoes and
readouts do not count as executed repairs. The controls show that omission of a
later failure can leave exactly the same admitted inputs as a complete successful
history; consistency cannot certify coverage or authenticate a receipt. Claims
C53–C54. Known-rule interpretation is a diagnostic control with prior verification
and memory-use precedents [@tiermem2026; @mem2act2026], not a new general method.

The [next intake](../experiments/dependency_memory/workflow_intake/README.md)
uses this repository for actual development tasks, prospective observations and
separate evaluator manifests. This current task is inspected development evidence.
Future tasks require a method/grader freeze and explicit serialized actor access;
folder names do not make them blind. That intake adds no model call or private
held-out result.

The first new [registered development task](../experiments/dependency_memory/workflow_intake/development/E0001/README.md)
contains six actual successful checks at two pinned source revisions. Direct
receipt memory uses 728 parent bytes and 1,455 child bytes and fits both existing
caps, preserving both snapshots. This is one easy control, not a measured model
improvement. Claim C55. All 434 tests pass at the second source checkpoint.

## Executed workflows: interrupted comparison and an interpretation error

A [separate follow-up](../research/EXECUTED_WORKFLOW_COMPARISON_2026-09-29.md)
captures 48 actual subprocess outcomes across twelve scripted local scenarios,
including narrower queries, failures and recovery. Its 108-call Luna 6 schedule
stops on request 17; a frozen extension of only never-dispatched identities stops
on its ninth request. Combined evidence has 24 metered answers, two permanent
transport gaps and 82 never-dispatched requests. The known cost is 0.2567650
planning credits; two unknown-usage reservations prevent another dispatch under
the unchanged ceiling. The original twelve-case comparison is unassessable.

Eleven of twelve observed final answers are correct. Direct records fail once by
requesting a test rerun despite a sufficient 203-byte successful receipt. No
false-ready response occurs. This demonstrates a final-model interpretation
failure after successful retention, but only one case is fully paired: it does
not rank methods or establish a cost benefit. The scenarios are authored controls
with observed executions, not untouched real-world evidence. [C52]

## Observed handoff development comparison: direct records remain strongest

A separately frozen [36-call Luna 6 medium comparison](../research/WORKFLOW_LUNA6_COMPARISON_2026-09-29.md)
uses one actual local validation/build capture and three constructed continuations.
Checked memory, direct records, indexed raw recovery and full history each score
4/4; strong prose scores 3/4. All writers are charged. Direct records use 0.0325430
model planning credits versus 0.2940470 checked, 0.1968765 indexed, 0.2858350 prose
and 0.2012055 full history; cache-neutral costs preserve direct's advantage.
The entire launch uses 1.0105070 planning credits, with no retries or transport
failures. These are model-cost observations, not fully priced production savings.

The prose failure unnecessarily marks a repository check as needing work even
though the exact successful receipt remains in its unclipped 814-byte child.
Two checked children omit a JSON closing bracket; fallback preserves the correct
records from their bounded parents. The checker therefore handles a concrete
format failure, but offers no observed success advantage over direct records.
The four conditions are correlated development controls, not four untouched
workflows. The twelve-episode held-out study remains unperformed. [C51]

## Decoder-compatible handoffs after the cross-record failure

A [versioned offline correction](../research/DECODER_COMPATIBILITY_REPLAY_2026-09-24.md)
now checks whether a parent table can actually be selected and decoded at the
second boundary. On the twelve saved cross-record parent proposals, the old
ID check passes nine and the new compatibility check passes three. Six
proposals accepted by the old check have unsupported columns. Conservative
fallback before source deletion produces twelve compatible parents, and all
252 possible two-owner child handoffs pass deterministic checks. A subsequent
branch audit found and fixed a parent-pass/child-fail counterexample beyond
these saved inputs; admission now runs the actual child checker for every pair.
The saved results are unchanged. The certificate permits wrong or missing
non-ID state, so it does not establish semantic sufficiency or improve the
frozen study's terminal scores. An externally observed executable workflow,
strong indexed/direct controls, and a separately evaluated terminal guard
are the next empirical test. [C50]

## Cross-record dependencies: retention succeeds, decisions fail

The latest [cross-record test](../research/CROSS_RECORD_RECOVERY_2026-09-22.md)
splits each constructed workflow's evidence across shuffled tool results and
charges a raw and projected full-workflow index. The 348-call original protocol
stopped on a provider error after 199 dispatches. A separate frozen extension
sent only the 149 never-attempted calls; the combined ledger has 347 answers
and one permanent gap. The original 36-pair primary criterion is unassessable.
On 35 fully answered paired futures, automatic direct tables make 7 exact
terminal errors, versus 3 for strong prose prompting, 4 for hand-written
direct and 1 for raw indexed recovery. Automatic is cheaper than prompting
under the declared synthetic experimental price, but direct and raw recovery
are both cheaper and more accurate. Its tables contain sufficient facts for
all 36 futures under deterministic reconstruction. The failures arise in
final-model interpretation, including one simulated unsafe `publish`.
The checked-proposal arm also has a specific parent-check/child-decoder
mismatch that empties six child memories. This constructed post-stop result
does not establish cheap automatic checks as a terminal-performance or
total-cost contribution. [C49]

## New schema structures: narrow success, stronger recovery control

The separate [prospective transfer test](../research/SCHEMA_TRANSFER_PROSPECTIVE_2026-09-22.md)
froze six constructed retry, CI and data-job evaluation traces with schemas
different from escrow/package development. It removes custom ID/reference
annotations and runs 126 fresh Luna medium calls on 18 paired terminal cases.
Generic exact-ID and owner/path checks fit both byte boundaries. Automatic
direct fails 1/18 versus 2/18 for stronger prompting and hand-written direct,
at 0.12645 versus 0.43840 experimental credits for prompting. The
prespecified **narrow primary criterion is met**. Indexed recovery is cheaper
and succeeds on 18/18, so automatic direct does not win the full cost frontier.
All six model-written parent proposals are prose and require fallback; the
checked-proposal arm fails 2/18. A certified automatic table still leads to one
wrong target ID at final execution. Evaluation schema definitions were visible
in the frozen casebook, so this was not a blind unknown-schema test. This small
constructed result neither establishes general automatic survival detection
nor production savings. [C48]

## New frozen traces: automatic checks tie the controls

The [schema-derived follow-up](../research/SCHEMA_CHECKS_UNSEEN_TRACES_2026-09-22.md)
froze new retry, CI handoff and multi-stage data-job traces before writing its
extractor. A generic table retains schema-annotated exact IDs and reference
roles through two byte boundaries; two checks detect ID changes and role
reassociation. Seventy-two GPT-6 Luna medium calls compare stronger prompting,
automatic tables, hand-written direct records, indexed recovery and full
history on 12 paired terminal cases. Every arm scores 12/12. The automatic arm
costs about 0.0731 experimental credits versus 0.2537 for prompting, but
direct records and indexed recovery cost less. **The prespecified fewer-failure
criterion fails** because prompting also makes no terminal error. The traces
hold out values within development schema families and the schemas explicitly
label IDs/references; general automatic extraction and production savings are
not established. [C47]

## Live memory failures and a stronger cost control

The [new GPT-6 Luna medium pilot](../research/LUNA6_DELAYED_FAILURES_2026-09-22.md)
made 117 fresh calls after freezing its gate, byte budgets and grader. Structured
memory succeeds on 8/16 delayed decisions, prose on 12/16, and checked replacement,
direct dependency rows, indexed recovery and full history each on 16/16. One
structured continuation releases a simulated service after its open blocker is
cut off at the second memory boundary. Other saved summaries lose explicit
negative evidence or change exact identifiers. The histories are constructed
and their continuations correlated; native compaction is not tested. [C44]

Checked replacement uses 8.9% fewer model credits than the original structured
pipeline while fixing its observed errors. Direct serialization and indexed
recovery are much cheaper still. Both cache-discounted and cache-neutral costs
are reported, including all memory-writing calls. The adapter is hand-written
for a known executable gate, and many summaries are overlong, so this is not a
general extraction or fully monetized production-saving result. [C45]

A separately frozen 24-call follow-up announces that public rules are repeated
and asks for service facts first. It eliminates all clipping but still succeeds
12/16: summaries shorten exact IDs and confuse approval with the current artifact.
This supplies concrete failures beyond truncation. The prompt is cheaper, while
direct checked rows and indexed recovery remain the best observed controls.
Both studies total 141 calls and 1.3190825 planning credits. [C46]

## A real handoff distinction and a cheap memory repair

The [historical workflow replay](../research/HISTORICAL_WORKFLOW_REPLAY_2026-09-22.md)
uses eight actual attempt records. Three failed-status requests had dispatched
and settled; a fourth failed before dispatch. A later plan that retries all four
would duplicate three generations, while holding all four would miss one eligible
first submission. These are local counterfactual plans. The historical transport
events were observed; compaction was not shown to cause them. [C41]

Checked decision receipts preserve request identity, dispatch class and exact
accounting in 1,231 bytes, compared with 1,649 for lossless compact fields. Through
1,536/768-byte boundaries and with whole-record archive recovery available, a
common allowance of 62,501 synthetic units yields 24/24 repaired continuations
versus 18/24 for compact fields. The direct-receipt baseline also succeeds on all
24 and needs less work. Cheap retrieval and expensive checking can make repair
lose. All 45 allowance frontiers are retained; the routes reuse one inspected
workflow and are not independent trials. No dollar savings are measured. [C42]

Eleven scope controls show when old receipts must be invalidated, including
changed settlement, newly present usage metadata and changed request/checker
identity. The new adapter matches the original source on 1,388 adversarial
inputs. Reading current evidence for invalidation has an explicit cost. Automatic
extraction on unseen task structures and production benefit remain open. [C43]

## Novelty verdict: no new feedback algorithm established

The [stricter investigation](../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md)
finds close context-management and formal-methods precedents and gives an exact
elementary reduction of our finite repair objective to accepted recovery
strategies and weak hypergraph coloring. Independent checks cover 7,203 small
subset/budget cases, 1,029 colorings and all 12 existing audit fixtures. These
reuse prior finite domains and narrow the claim; they are not a new algorithm
or evidence of model improvement. [C40]

A useful systems contribution remains possible if we can extract sound delayed
failure witnesses from realistic workflows at acceptable cost. The inspected
historical replay supplies one bounded adapter; the annotated-schema test above
does not cover unannotated tool results or show superiority over strong simple
retention. The older
delayed-query coding results have separate unresolved priority questions.

## Feedback-loop follow-up: preserve the failure constraints

The [new offline adapter](../research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md)
executes the receipt workflow through two memory boundaries and uses checked
collision failures to revise a finite retention schema. Accumulated feedback
repairs a 32/48 initial schema to 48/48; keeping only the newest failure cycles.
However, a simple critical-field rule also gets 48/48 with fewer full audits.
The same strong baseline matches feasibility across all 48 capacity/recovery
contracts. This is useful calibration, not a demonstrated better compactor. [C37-C38]

A separate control shows why one record cannot be equated with one bit: choosing
which tagged receipt to keep can encode four source states. A public catalog
decoder exploits that identity, while a receipt-only executor does not. Other
controls cover a later binding memory limit, missed obligations, and feedback
that reveals a deleted value as an additional information channel. [C39]

The [prior-art check](../research/FEEDBACK_PRIOR_ART_2026-09-22.md) confirms that
feedback loops and cumulative preservation constraints are established. The
next test must make the retention rule nontrivial to infer and compare full
costs against an equally informed critical-field baseline. No new model calls
or natural-task gains are claimed.

## New direction: challenge a memory before accepting it

We have built a [finite compaction auditor](../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md) that asks whether any policy can finish from a proposed memory within the allowed recovery budget. It groups histories with identical retained and public state, considers every adaptive use of the declared tools, and produces a checkable obstruction when the budget is insufficient. It also computes the smallest additional message alphabet that would repair the declared task family before the future task is revealed. [C35]

The first 12 constructed specifications expose a useful audit failure: every pair of three histories can share a correct action, while the whole group has none. One extra retained bit repairs that example. Another fixture needs two recovery calls adaptively but four in a fixed batch. Controls ensure that free public evidence, harmless lost details and sufficient recovery budgets do not trigger unnecessary memory. These are executable finite results, not LLM trials or evidence of deployed-system gains. [C36]

This changes the active research direction from tightening a small coding bound to testing a proposed memory against future execution requirements. The [literature check](../research/COMPACTION_AUDIT_PRIOR_ART_2026-09-21.md) attributes existing summary repair, typed commitments, state abstraction and hypergraph coding. Novelty of the specific audit protocol remains provisional. The next decisive test is a sound execution-task adapter; inferring semantic equivalence between arbitrary prose summaries is not implemented.

## The question

An agent can finish a piece of work before it knows which details will matter later. A summary may preserve “the build succeeded” while losing the exact receipt needed to release the result. Keeping more history is one option. Learning which receipt matters before deleting anything, or retrieving it afterward, are two others.

We study when those choices are useful. The working hypothesis is that context management should consider the timing of future obligations and the cost of recovering evidence, alongside the size and quality of the retained summary. This is a hypothesis about useful agent behavior; it is not yet a measured LLM improvement.

## What we have found

**1. Individually adequate memory budgets can become incompatible when used in sequence—and we now know the exact penalty in the small example.** Two initial bits achieve 3/16 error for the isolated first task, and one later bit suffices for 25% error when its encoder sees the original source. With delayed relevance and a two-bit memory compressed again to one bit, the best error is **9/32 = 28.125%**. That is a 3.125 percentage-point penalty relative to the later task's isolated optimum. Three initial bits recover the 25% target. [C03–C05, C21; exact result](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md)

The September 19 computation examines all 171,798,901 partitions of the 16 possible source strings into four nonempty parent states. An independent decoder check grades a winning representation on all 192 outcomes. This closes the exact-optimum question for this finite example; it does not establish a new general compression theorem or an LLM effect.

**2. The obstruction survives a particular scaling construction.** For k independent four-bit blocks with the specified late block/subset reveal, exactly 3k initial bits are needed to attain error 1/4. With 2k initial bits, error is strictly greater than 1/4 + 1/512, even with joint encoding across blocks. A local audit added an analytic entropy proof and independent finite checks. External review and novelty assessment remain open. These are information bits, not receipt slots or model tokens. [C11–C12; derivation](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md)

**3. Recovery can remove the economic case for early inspection.** We built a deterministic workflow with two memory boundaries, delayed receipt requirements, revisions, optional early inspection, and a charged late recovery tool. We then computed an exact reference for a restricted class of record-selection policies under a known uniform routing distribution. It chooses retained records before seeing the hidden final query.

For six jobs, two possible required jobs, two receipt slots at each boundary, and no revisions, the best success rate before recovery is 1/3 without inspection and one with inspection. At an inspection price of one synthetic unit:

| Recovery price per missing receipt | Cheapest route to perfect success | Expected extra cost |
|---|---|---|
| 1 unit | Retain, then recover a miss | 2/3 unit |
| 4 units | Inspect before the first boundary | 1 unit |

Both costs exclude the same mandatory ten-unit workflow. All episodes contribute to cost accounting, including failed retention followed by recovery. The exact break-even recovery price is 3/2. These are model expectations over all routes, not estimates from a sample. [C17–C18; results](../experiments/dependency_memory/results/recovery_frontier_report.md)

**4. Better retention need not produce a cheaper completed task.** With only one receipt slot at the second boundary, inspection raises pre-recovery success from 3/10 to 1/2. Nevertheless, when inspection costs one and recovery costs four, reaching perfect success costs 3 extra units with inspection versus 14/5 without it. A later memory limit can erase enough of the early clue's benefit that inspection is no longer worth its price. [C20; exact reference](../experiments/dependency_memory/RECOVERY_FRONTIER.md)

The revision rule matters too. Our public schedule refreshes the smallest candidate job. A reference policy can exploit that schedule, raising uninspected success to 4/5 and moving the inspection break-even recovery price to five. This is a property of that schedule; pooling revision conditions would conceal it. [C19]

## Storing blocks together changes the penalty

The [September 21 extension](../research/JOINT_BLOCK_CODING_2026-09-21.md)
shows that independently compressing each small block leaves performance
on the table. A shared four-bit memory for two blocks achieves **27.64%
error**, below the **28.125%** one-block optimum at the same two bits per
block. Every one of its 6,144 possible outcomes is checked. The code is an
explicit achievable construction; the best possible two-block error is
still unknown. [C31]

A separate analytic construction proves an asymptotic upper bound of
**26.30% error** at two bits per block. Its rate calculation is certified
by an exact integer inequality, but no finite encoder at that error has
been implemented. We also derive a precise distinction: approaching the
25% target needs about **2.549 bits per block**, while attaining it exactly
at any finite size still needs **three bits per block**. Rare overflow
cases can become negligible in the first setting; they cannot be ignored
in the second. [C32-C33]

## Earlier mathematical milestone: the remaining penalty is sharply bounded

The [decoder-complete follow-up](../research/DECODER_COMPLETE_FRONTIER_2026-09-21.md)
places the best limiting error between **26.18989799% and 26.18989801%**.
The lower endpoint also bounds every finite block count. This is a
mathematical certificate, not a statistical confidence interval. [C34]

The check covers all **1,679,616 final-decoder tables**, including constant
and noncomplementary prediction pairs, grouped into 4,751 symmetry classes.
An analytic information bound then covers arbitrary joint encoders, while
a rational channel supplies an asymptotically matching construction.
Every decisive comparison uses exact integer or rational bounds.

The unavoidable excess above 25% is therefore about **1.189898 percentage
points**, over six times our previous guaranteed minimum. The candidate
contribution is this sharply quantified penalty with every legal decoder
allowed. No practical finite encoder at this error is supplied, and no
model-performance improvement is established. The machinery comes from
established coding theory; external correctness review and publication
priority remain open. [C34]

## The resulting decision rule

Let p_0 and p_1 be the best probabilities of retaining the required receipt without and with inspection. With reliable recovery at price c_R, inspection at price c_I reduces the expected cost of perfect success exactly when

```text
c_I < (p_1 - p_0) * c_R.
```

This is elementary cost accounting within our declared model. Its value is as a reference against which to test an agent's decisions. We have not shown that a model can estimate these probabilities or use the rule effectively in ordinary work.

## What contribution is still plausible?

Successive refinement, functional compression, and costed side information already provide relevant theory. Recent compaction work also discusses query timing and recovery. The [literature comparison](../research/LITERATURE_POSITIONING_2026-09-18.md) therefore supports a narrow direction: a restricted compatibility result, plus a reproducible experiment that identifies when an action before compaction changes later task success and total cost. Broad novelty claims would be premature.

The current evidence comprises checked mathematics, offline invariant tests, the exhaustive finite-chain computation, 2,640 complete-route scripted episodes, and a 3,000-configuration exact reference grid. The earlier 320-case workflow and 810-case retention diagnostics remain separate constructed examples. None of these counts represents independent LLM trials. Archive storage, model tokens, provider state, latency, and API dollars have not been evaluated by the recovery model.

The [correctness audit](../research/CORRECTNESS_AUDIT_2026-09-19.md) reproduced the complete finite search and fixed two validation gaps without changing those numerical results. It also exposed an evaluation limit: reliable recovery lets an agent forget everything and still finish. The pilot must measure what survives before recovery and the cost of completing the task; completion alone cannot demonstrate good memory. [C23]

## First Luna development results

The [pilot design](../docs/LLM_PILOT_SPEC.md) separates inspection choice with ideal scripted retention from inspection with model-selected records. Its historical full schedule reserves 432 requests; only the 96-request development tranche has run. The four held-out families now have offline clue renderers, while request integration and model evaluation remain unfinished. [C22, C28]

The development renderer and strict request interface are now implemented. In fake-client checks, both optimal and forget-all controls completed 36 episodes with 96 requests; their pre-recovery availability differed, 26/36 versus 0/36. These are software controls on one route, not model trials. [C24; implementation and audit](../docs/DEVELOPMENT_PILOT.md)

The [first live run](../experiments/dependency_memory/results/luna_development_2026-09-19/report.md) completed all **96 Luna requests** through the existing Codex subscription, with no schema or transport failures. Ten of the 12 calibration decisions selected the exact lower-cost action. The two disagreements involved revisions, and identical repeated prompts produced different choices in those cells. This is a debugging observation, not an estimated general accuracy rate. [C25]

All 36 workflow episodes finished, but the required receipt survived before recovery in only **21/36**; the other 15 needed recovery. Never, always, and model-selected inspection had availability 3/12, 10/12, and 8/12, and synthetic action costs 154, 140, and 137. These totals describe one paired route. They do not establish population superiority, and a different valid tie-break can change the result on that route. Reliable recovery explains why completion alone would hide the retention differences. [C25; detailed findings](../research/LUNA_DEVELOPMENT_FINDINGS_2026-09-19.md)

The run used 276,048 input and 27,140 output tokens, including reasoning within output. Its conservative accounting equivalent was **2.5395 credits** under a 20-equivalent cap; the experiment's actual subscription debit is unknown. There was no API billing, credit purchase, reset redemption, or held-out call. The [transport contract](../docs/LUNA_DEVELOPMENT_RUN.md) declares fixed background instructions and restricted wrappers, fresh processes and threads, zero configured retries, and a one-generation guard. It does not expose remote internals or make the mutable model alias an immutable revision.

The [completed offline analysis](../experiments/dependency_memory/results/revision_analysis_report.md) now isolates three strictly worse first-boundary choices, all in uninspected revision cases. The other 33 parent choices attain the reference for their public view. All 36 observed later choices are optimal given the surviving records. This matters because a miss on one realized target can also be an equally good tie choice; the analysis distinguishes those cases from avoidable parent loss. It reuses existing responses and makes no new model calls. [C26]

The mechanism is concrete. If the smaller member of the future pair will be refreshed, retaining the two largest keys gives ideal later availability 4/5. The observed low-key pairs instead give 3/5 or 8/15. With no refresh, all two-key parents tie at 1/3. This is an exact calculation for the declared uniform-pair model, not a claim about Luna's hidden reasoning.

The separately authorized [24-request diagnostic](../research/REVISION_LUNA_FINDINGS_2026-09-19.md) is now complete. Every response selected an optimal full pair: `job-4/job-5` in all eight refresh-first cells, `job-0/job-1` in all eight refresh-last cells, and that same low pair in all eight no-refresh cells, where all full pairs tie. All eight matched direction shifts equal eight, unlike the prespecified static controls. Exact regret is zero throughout; its paired form is algebraically equivalent to the direction shift for full outputs, not independent confirmation. The result shows rule-sensitive choices in these simplified prompts, but the changed framing and explicitly optimal later selector prevent calling it a fix for the first workflow's errors. The 30 evaluated routes per answer are exact scoring continuations, not extra model trials. [C27, C29]

That follow-up had no policy/transport failures, retries, or held-out calls. Reported usage was 66,200 input and 5,651 output tokens, or **0.58328 conservative credit equivalents** under its separately authorized 12-equivalent cap. Attributable subscription debit is unknown. These two earlier allocations total 120 model requests; no API billing, purchases, or resets occurred. They motivated the separately frozen matched comparison below. [C29]

## Completed matched retention study

The [1,536-request transfer study](../research/TRANSFER_LUNA_FINDINGS_2026-09-19.md) is complete. Across 32 generated blocks it varies six versus twelve jobs, compact versus workflow presentation, the stated skill of the later selector, generic versus prospective guidance, and which member of a future pair will be refreshed. Priorities are randomized independently of job names. The workflow presentation adds three short events; it does not recreate a long natural workflow. The prospective instruction asks the model to consider what will arrive again and protect what must survive. [C30]

There are **1,533 valid responses**, with three charged responses permanently lost during a local quota post-check. A continuation completed only the 648 cases never dispatched in the first 888-call phase. The original cases, allocation, missing outcomes, and source phases remain preserved; there were no retries or replacement cases. Overall, **1,422/1,533 selections are optimal** under the exact later-selector reference. With refresh, the count is 912/1,022; without refresh, it is 510/511, where all full pairs tie and the one exception is an empty selection. [C30]

The main comparison has no missing answers: 128 matched pairs across 32 blocks, using workflow presentation, an unspecified later selector, and a refresh rule. Generic guidance gives **114 optimal selections**, prospective guidance **118**. Thirteen pairs favor prospective guidance, nine favor generic guidance, and 106 tie. Mean normalized regret benefit is **0.02090**, with descriptive 95% block-bootstrap interval **[-0.02031, 0.06055]**. It includes zero, so an improvement is not established. This normalized number measures the fraction of the best-to-worst full-pair loss range, not percentage points of task success. Raw availability benefit is -0.365 percentage points at six jobs and +0.840 at twelve. These results do not establish that the guidance has no effect either. [C30]

Among 111 suboptimal choices, 100 match at least one descriptive pattern: the smallest job names, the largest job names, or the optimum for the opposite refresh rule. Categories overlap; they are observations about answers, not explanations of the model's internals. The original first-eight-block checkpoint and every condition summary remain available. Independent recomputation agrees with the final counts, primary estimate, and interval. [C30]

The study used **48.78528 conservative credit equivalents** within its original 200-equivalent cap. Actual subscription debit is unknown. There was no API billing, purchase, or reset. Each response is an isolated record choice scored over all possible later routes; those routes are not extra model trials. The later selector is assumed optimal but never invoked, and its two slots can hold both candidates. Consequently this is evidence about early retention potential, with a nonbinding second boundary. It does not test the repeated bit-compression theorem, native provider compaction, or full-agent performance. [C30]

The next behavioral design should make the later memory decision matter and check actual downstream behavior. It should retain matched inputs, declared information channels, and a frozen analysis. More repetitions of the current reminder alone are not a demonstrated route to a better memory system; the completed study provides the baseline and failure cases for a different, explicitly specified test.

The [held-out semantic checkpoint](../docs/HELDOUT_RENDERERS.md) covers alias chains, package prerequisites, validation scopes, and deployment handoffs. All 15 candidate pairs in both explicit and inferred formats resolve to the same intended pair, giving 120 clue forms and 240 pair/target checks across the four families. The renderer has no final-target or receipt-value input. This is offline software evidence only, with no change to the reserved routes or previous model results. Final request integration, boundary deletion checks, and a complete launch freeze remain necessary. Catalog sizes differ, and the tiny one-route-per-family sample cannot establish generalization or isolate family effects. [C28]

An [external review packet](../research/EXTERNAL_REVIEW_PACKET_2026-09-19.md) is ready, but no reviewer has been contacted. External mathematical review and novelty remain open, and the single-block exact gap does not strengthen the all-k bound automatically.

For each update, revise the result paragraphs and the claim register together, link the supporting artifact, and retain null or negative findings. Keep proposed work visibly separate from completed evidence.
