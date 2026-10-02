# Repeated Context Compression with Delayed Task Dependencies

Working draft — October 2, 2026. Authorship and venue are not set. For a short overview, read the [living findings draft](findings-draft.md). This manuscript reports an exact finite-chain optimum, scaling bounds, a joint-coding extension with an exact parametric unrestricted asymptotic curve and a tightly certified rate-two error, a two-class query-prior and timing extension, an implemented polynomial hard-cap entropy code with finite bounds, an exact restricted recovery reference, two small Luna development tranches, a completed 1,536-request matched retention study, an exploratory historical workflow replay, 141 GPT-6 Luna medium calls in a controlled memory-writing study, a 72-call annotated-schema transfer test, a 126-call prospective new-schema test, a cross-record stress test with one permanent transport gap and a separately frozen continuation, a post-hoc offline decoder-compatibility correction, two workflow development comparisons, and a retrospective retained-evidence audit. External mathematical review, novelty assessment, realistic production-workflow evaluation and production benefit remain open.

## Abstract

Long-running language-model agents must preserve information whose relevance may only become clear later. We study a finite model that separates memory capacity from the timing of task information. In a four-bit example, exhaustive computation gives optimal two-bit-then-one-bit chain error 9/32, while the isolated later bottleneck achieves 1/4. Three initial bits are necessary and sufficient to attain that later optimum. A locally audited independent-block extension gives a uniform positive error gap. Joint coding achieves two-block error 283/1024. Complementary completion and exact polynomial comparisons characterize the unrestricted asymptotic curve at every parent rate in this model. An exhaustive decoder certificate places the limiting error at two bits per block between 0.2618989799 and 0.2618989801; approaching the child optimum requires about 2.5488 bits per block, compared with three for exact finite attainment. Separately, an exact atomic-record reference shows that cheap recovery can dominate early inspection, and that improved retention need not lower completion cost. Initial Luna diagnostics motivated a fixed 1,536-request study of record retention under known future refresh rules. Of 1,533 valid responses, 1,422 attain the exact reference. In the 128 primary matched comparisons, prospective guidance yields 118 optimal selections versus 114 with generic guidance; mean normalized regret benefit is 0.02090, with descriptive 95% block-bootstrap interval [-0.02031, 0.06055]. This does not establish an improvement. The study measures isolated retention potential with an optimal later selector, not native compaction or full-agent performance. Mathematical novelty remains unresolved.

## 1. Introduction

An agent's transcript grows with its activity, but the amount of information needed for its next decisions need not grow at the same rate. A long sequence of completed independent subtasks may leave only a small number of unresolved facts. Conversely, a short history can contain many values that a later instruction may distinguish. The relevant resource is therefore not transcript length alone, but the information required to support possible continuations.

Prompt compression has already been studied through rate–distortion formulations, and hierarchical agent memory already summarizes work around subgoals. These provide foundations rather than novelty claims for the present study [@nagle2024; @hiagent2025]. Our question concerns the compatibility of representations across successive bottlenecks when additional task information arrives between them. Classical successive refinement establishes that separately optimal descriptions need not compose without suitable structure; translating that insight to a finite, shrinking-memory, delayed-query protocol requires stating the information constraints precisely [@equitz1991].

The practical motivation is a completed subtask whose result is needed later. A record saying that the subtask is finished may preserve immediate continuity while losing an identifier, qualification, or negative result required by a subsequent obligation. The present mathematical model abstracts this timing issue. It does not model all semantics of natural-language summaries or all behavior of a tool-using agent.

Costed information acquisition and functional compression are established foundations, with especially close connections to cascade encoders and request-dependent cache updates [@vending2009; @cascadevending2012; @caching2016; @graphcoloring]. A recent compaction preprint also addresses reversibility and query timing [@compactionview2026]. Our proposed scope is a restricted compatibility result and a controlled action-timing experiment; a broad new theory of agent memory is not claimed. The [positioning note](../research/LITERATURE_POSITIONING_2026-09-18.md) specifies the source sections reviewed and the remaining reduction questions.

## 2. Model and information timing

Let X = (X_1, ..., X_n) be independent fair bits. Independently of X, a subset S is drawn from a specified family F. A coordinate J is then drawn uniformly from S. The task is to answer X_J.

The first encoder observes X and retains M_1 = E(X), with at most 2^(B_1) states. After S is revealed, an updater forms M_2 = U(M_1, S), with at most 2^(B_2) states. The final decoder observes M_2, S, and J. Neither the updater nor decoder can reread X.

The programs and codebooks are fixed before the instance is sampled. S and J are public control information at their specified stages; their descriptions are not charged to the value-memory budget in this toy model. This convention must not be confused with a claim about total implementation bytes. An archive or opaque provider state that contains X would change the information constraints.

Define D_chain(B_1, B_2; F) as the infimum of the probability of an incorrect answer over valid encoders, updaters, and decoders. Let D_1(B_1) be the optimum when only the first bottleneck remains, and D_2(B_2) the optimum when the second encoder can observe the original X together with S. Every chain satisfies

```text
D_chain(B_1, B_2; F) >= max(D_1(B_1), D_2(B_2)).
```

We ask when this inequality is strict and how much additional first-stage memory is needed to attain the relaxed target. The composition gap is the difference between the two sides. Its dependence on the family F is the proposed subject of further analysis.

## 3. A finite incompatibility example

Take n = 4, let S be uniformly selected from the four three-coordinate subsets, and set B_2 = 1. The isolated first bottleneck with B_1 = 2 has optimum error 3/16. The isolated second bottleneck has optimum error 1/4. Nevertheless, a two-bit-then-one-bit chain cannot attain error 1/4.

For three fair bits encoded into one bit, a decoder chooses two prediction vectors from eight possibilities. Among the 28 unordered pairs, exactly four attain error 1/4: the complementary pairs. The nearest prediction is unique for every source string because the dimension is odd. Thus any child-optimal encoder implements a signed majority decision.

To attain the optimum after every possible S, the parent memory must support one appropriate signed-majority decision for each of the four triples. Let f_i be the chosen signed majority on the triple omitting coordinate i. In sign notation, x_i in {-1, +1}, each f_i contains a nonzero cubic Fourier monomial on its own triple. That monomial appears in no other f_j, so the four functions are linearly independent. Their joint output vectors therefore span four-dimensional space. Each function is odd, so the joint range is centrally symmetric. A centrally symmetric set spanning four dimensions requires at least four antipodal pairs: at least eight distinct parent states.

Two bits provide only four states and cannot support these branch decisions. Three bits suffice: the joint signature of the four ordinary unsigned majorities has eight possible values. Its values are the all-positive and all-negative vectors and the six vectors with two positive coordinates. Store the signature's fixed codebook index, then select the required branch decision after S is revealed.

The accompanying enumeration checks all 4^4 = 256 assignments of optimal child decoders. The required numbers of parent states are 8, 10, 12, and 16, appearing in 56, 96, 96, and 8 assignments respectively. The explicit three-bit witness is graded on all 192 equally likely source/subset/query cases.

The original incompatibility certificate implies the conservative bound D_chain(2, 1; F) >= 49/192. A separate September 19 [exhaustive search](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md) now establishes **D_chain(2, 1; F) = 54/192 = 9/32**. Randomized mixtures cannot improve on the best deterministic average loss in this finite setting.

Every deterministic two-bit parent partitions the 16 source strings into at most four cells. Refinement to four nonempty cells cannot remove a feasible child decision, so it suffices to enumerate the 171,798,901 such unlabeled partitions. For a child cut U and omitted coordinate o, its best decoder makes 24 - sum_{j != o}|sum_{x in U}(2x_j - 1)| errors. Each parent permits eight cuts up to child-label exchange, including the constant split; each omission can optimize its cut independently. The largest summed gain over the four omissions is 42, leaving 96 - 42 = 54 errors. There are 128 minimizing parent partitions. The [certificate](../experiments/dependency_memory/results/exact_chain_certificate.json) records the complete score histogram and a witness graded independently on all 192 outcomes.

This is a checked finite obstruction. It is not presented as a new general successive-refinement theorem. The full formulae, proof, certificate, and implementation are maintained with the research artifacts.

## 4. Locally audited scaling result

Let the source consist of k independent uniform four-bit blocks. The parent memory is formed before a uniformly selected block and omitted coordinate are revealed. An updater then forms one child bit before the final coordinate within the remaining triple is disclosed. Only that bit and the specified public side information are available at final decoding.

In this family, exactly 3k parent bits are necessary and sufficient to attain error 1/4. With at most 2k parent bits, every valid chain has error strictly greater than 1/4 + 1/512 for every k >= 1. Joint encoding across blocks is allowed. Hard state capacities and source-independent randomization are essential assumptions.

The exact-target statement uses Cartesian products of required branch-signature ranges. For the robust gap, an analytic antipodal-fiber argument gives signature entropy at least 4 - (5/8) log_2 5 > 5/2. A signature-reconstruction bound and source independence then conflict with a 2k-bit parent at the stated error threshold. The [derivation](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md) and [audit](../research/PROOF_AUDIT_2026-09-18.md) contain the full argument and independent finite certificates.

The [focused literature check](../research/SCALING_LITERATURE_CHECK_2026-09-19.md) places these steps within established methods. Distinguishing fixed branch signatures is a special case of characteristic-graph functional compression [@functionalcoloring2010]; combining per-block information requirements under joint encoding uses standard information direct-sum reasoning [@jain2003compression]. Stronger one-way direct-sum results also address indexed copies, but their access patterns and overall-output guarantees differ from our single-query loss and intervening one-bit memory [@jain2008directsum]. Those results do not directly supply the coefficient 3 or the stated gap at coefficient 2. Any contribution claim must concern this particular construction and its quantitative stability analysis; their novelty remains unresolved.

These are locally audited results pending external review and priority assessment. The signature graph itself is an elementary complete multipartite construction, not a new general functional-compression principle. The all-k error-gap constant remains conservative. The following extension proves that the exact one-block gap 1/32 becomes smaller under joint encoding.

### 4.1 Joint encoding and the asymptotic threshold

An explicit code for two blocks, with four parent bits and one child bit, achieves error **283/1024**, compared with 9/32 for independent optimal two-bit encoders. The parent indexes one of 16 pairs of branch-decision words; after the block and omission are revealed, the updater emits the indicated word's omission bit. The final decoder predicts that bit. An exact grader checks 1,698 errors on all 6,144 source/block/omission/query outcomes, versus 1,728 for the product control. Repeating pairs gives error at most 283/1024 for even k; for odd k the upper bound is 283/1024 + 5/(1024k). Thus 9/32 is not a valid lower bound for k >= 2. The two-block optimum itself remains unknown. [C31]

The [September 21 derivation](../research/JOINT_BLOCK_CODING_2026-09-21.md) supplies a rational conditional distribution over unsigned branch signatures with expected distortion **101/384** and mutual information (371 - 40 log_2 5 - 95 log_2 3)/64 < 2. The strict rate inequality is equivalent to the exact integer comparison 2^243 < 5^40 3^95. Applying standard finite-alphabet rate-distortion achievability to these decision words preserves the one-bit child restriction and gives limsup D_k(2k) <= 101/384 [@polyanskiywu2016coding]. Concatenation also implies existence of the limit; together with the earlier converse, this initially placed it in [129/512, 101/384], tightened below. This is an asymptotic existence bound, not a supplied finite encoder at 101/384 or an exact distortion formula. [C32]

The asymptotic rate threshold for error tending to 1/4 is exactly **h_* = 4 - (5/8)log_2 5**, about 2.5488 bits per block. Near-optimal chains must approximately preserve high-entropy branch signatures on almost every block, giving a converse even for arbitrary joint encoders and branch decoder pairs. Typical-set coding of unsigned signatures supplies achievability. A fixed, vanishing fraction of unencoded blocks absorbs the coding slack, so floor(k h_*) bits suffice at the boundary itself. Exact finite attainment still requires 3k bits. The proof and its endpoint accounting are in the derivation. [C33]

These are specific constructions and deductions using established coding methods. Cascade functional compression already includes a codec that re-encodes a received message [@basu2022hypergraph]. The reviewed formulation differs in its timing and downstream capacity, but that difference alone does not establish novelty. The particular finite witness, bounds, and threshold need external comparison and review.

### 4.2 A certified interval allowing every final decoder

The [next derivation](../research/DECODER_COMPLETE_FRONTIER_2026-09-21.md) narrows the unrestricted rate-two optimum to

```text
0.2618989799 < lim_k D_k(2k) < 0.2618989801.
```

The lower inequality holds at every finite positive k. Its excess above 1/4 is approximately 1.189898 percentage points, over six times the earlier uniform guarantee. The upper inequality uses a rational test channel and asymptotic coding; it supplies no finite encoder at this error. This is a certified numerical enclosure, not an exact closed form. [C34]

For each block, a final decoder consists of four unordered pairs of three-bit prediction words. Including repeated and noncomplementary pairs gives 36^4 = 1,679,616 tables. Coordinate permutations and bit flips partition these into 4,751 disjoint orbits. For each table g, a 16-valued strategy A records the updater's potential bit on every omission, with integer loss L_g equal to its errors on the 12 omission/query routes. This applies established strategy-alphabet reasoning [@dupuis2004strategies].

A common dual inequality I(X;A) + s E L_g >= C is certified over every table using integer arithmetic and outward rational logarithm bounds. Source independence and data processing give sum_r I(X^(r);A_r) <= H(M) <= 2k, hence D_k(2k) >= (C-2)/(12s), allowing different tables and information allocations across blocks. The matching rational channel has distortion below 0.2618989801 and information below 1.999999994 bits. Standard fixed-length coding preserves the delayed one-bit child contract [@polyanskiywu2016coding].

The [certificate](../experiments/dependency_memory/results/decoder_frontier_certificate.json) is fully regenerated by the offline validator. Separate checks verify decoder losses, the group action, a Burnside orbit count, rational dual rounding, and actual channel information. The candidate contribution is this particular sharply quantified composition penalty; the coding, strategy, and duality methods are established. External proof review and priority assessment remain open. [C34]

An [October 2 continuum comparison](../research/UNRESTRICTED_RATE_CURVE_2026-10-02.md)
now extends the unsigned scalar optimization to the full unrestricted
asymptotic curve D_infinity(r)=lim_k D_k(floor(k*r)) for every r>=0. A
balanced-source completion reduces to six complementary families; 48 exact
polynomial inequalities cover every positive slope. A common supporting
inequality permits arbitrary joint encoders and heterogeneous block tables.
The optimal Gibbs channel parametrizes the intermediate curve, with error
1/2 at zero rate and 1/4 at/above h_star. Mixing with a source-independent
channel creates strict rate slack before fixed-length coding within floor(k*r)
bits. This supplies no finite optimal code or efficient encoder. [C67]

A [separate finite construction](../research/FINITE_TRELLIS_CODE_2026-10-02.md)
uses a fixed 16-state trellis with two parent bits per block and one child bit
before J. At four blocks it has 867,837 errors on 3,145,728 outcomes, below the
pair-product control's 869,376. An exact encoder uses 1024*k branch relaxations
within the fixed labels; independent four-block groups preserve the same
distortion for k=4*n; at k=12*n the existing three-block product still has
lower error. Smaller cycles with these labels lose to existing
controls. This implements one finite code; optimality and quality approaching
the full curve remain open. Section 8.18 gives the contract and checks. [C68]

A [later conditional six-block construction](../research/CONDITIONAL_SIX_BLOCK_CODE_2026-10-02.md)
gives 331,857,648 errors on 1,207,959,552 outcomes at 12 parent bits and one child
bit. It improves on two refined three-block components'331,890,688, whose
individual codebook has 40,514 errors on 147,456 outcomes. An exhaustive component
single-word replacement screen finds no positive gain, yet its product admits
an improving single joint word. Independent six-block groups preserve the
new error at k=6*n and improve both three-block products at common k=12*n.
Combining the refined component with C63 tightens the unrestricted three-block
bracket to [40,072,40,514]/147,456, width 442 errors. Section 8.19 specifies the
weighted grading and the small gain's scope; no optimality is claimed. [C69]

A [two-class extension](../research/QUERY_PRIOR_TIMING_2026-10-02.md) now
distinguishes known priors, unknown-prior minimax and early actual class cues.
At the same two parent bits per block, known p gives limiting error
min pD(r_L)+(1-p)D(r_R), r_L+r_R<=4; five exact witnesses include 25.718661%
at p=1/4. Unknown-prior minimax retains D(2). An early actual class attains
1/4 using 3n bits inside the 4n cap. A finite opposite-orientation pair is
robust to every source-independent p, but unequal allocation beats it for
skewed known priors. Section 8.20 states the conditions and limits. [C70]

An [implemented arithmetic-grid family](../research/HARD_CAP_ENTROPY_CODE_2026-10-02.md)
now improves the repeated C69 upper bound at larger checked lengths using
exactly 2k parent bits, including a fallback flag, and one child bit before J.
At k=12,288 a retained rational schedule has risk at most 27.198892%. The
default schedule's actual risk tends to about 27.075301%, still above C67.
The encoder/updater have polynomial bit complexity and ten packed public
response/probability bytes. Section 8.21 distinguishes analytic population
bounds, full small-population grading and constructed large diagnostics. [C71]

An [October 1 explicit three-block construction](../research/JOINT_THREE_BLOCK_WITNESS_2026-10-01.md)
uses six parent bits and one child bit under the same timing. Its fixed 64-word
codebook makes 40,529 errors among all 147,456 source/block/omission/query
outcomes, below the prior two-block-plus-one concatenation's 40,992 (427/1,536).
Average bit error decreases from approximately 27.7995% to 27.4855%. All 4,096
parent assignments and every route are checked with a separate coordinate
formulation. Heuristic discovery stops after eight swaps; this is an achievable
upper bound on D_3(6), not the optimum or a model/task-success result. The fixed
public codebook is not charged as instance memory. Existing coding machinery,
the asymptotic frontier and open external priority review remain unchanged. [C59]

For the family whose final prediction is independent of the late coordinate J,
a [separate finite cover argument](../research/JOINT_THREE_BLOCK_COVER_2026-10-01.md)
gives 40,072/147,456 = 5,009/18,432 as a lower bound. Together with C59,
the restricted optimum lies in [27.1756%, 27.4855%], width about 0.310 percentage
points. Every decision column has positive cover reward at most 25; missing
constant centers add disjoint 125-source penalties. Independent enumeration
checks all 16,777,216 source/column combinations. The bound covers arbitrary
joint encoders within this decoder family; coordinate-dependent endpoints remain
outside it. The unrestricted all-decoder frontier is unchanged. The elementary
cover method and publication novelty are not claimed new. External proof review
remains open. [C60]

The [complementary-decoder extension](../research/COMPLEMENTARY_DECODER_COVER_2026-10-01.md)
proves the same 40,072-error lower bound when every omission's two three-bit
prediction words are complementary, including coordinate-dependent endpoints.
Four pairs per omission give 256 tables per block; six symmetry orbits and
56 mixed cases cover all three-block combinations, including heterogeneous
tables. A per-source cover inequality adds a missing-ideal penalty on zero-target
sources. Summed column savings and those penalties are bounded by the largest
64 exact column weights. All 229,376 selected column instances are checked;
an independent implementation enumerates direct source triples for equal-score
multiset classes. Forty-six mixed cases cannot improve on C59 and ten remain
possible. Noncomplementary endpoints are outside this proof, and exact finite
optimality remains open. The all-decoder asymptotic frontier is unchanged.
External correctness and priority review remain open, with no new general
cover technique claimed. [C62]

The [all-decoder finite extension](../research/ALL_DECODER_THREE_BLOCK_COVER_2026-10-01.md)
established the following dated bracket with C59 for the unrestricted three-block optimum:

```text
5009/18432 <= D_3(6) <= 40529/147456.
```

At each omission the summed oracle loss is 12 for complementary endpoints,
16 for distinct noncomplementary endpoints and 24 for repeated endpoints.
Assigning branch defects 0, 1 and 3 gives a three-block oracle floor of
(144 + 4 total_defect) times 256. Total defect at least four yields 40,960
errors, above the incumbent. The remaining tables reduce to 46,492 mixed
orbit cases; 56 reuse C62 and 46,436 have new exact witnesses. This covers
all 36^12 ordered decoder triples through symmetries and the oracle gate,
allowing arbitrary joint encoders and heterogeneous tables. [C63]

For tied ideal actions, the zero-target correction is a union bound on ideal
incidences. Q counts zero-target sources once; each q_c counts its incidence
with a particular ideal cost column, so Q need not equal sum_c q_c. With
R_c the positive target saving, every 64-word book has source-summed loss at
least sum U + sum T + Q - Top_64(R_c + q_c). Equal entire source-loss functions
may be identified; equal histograms alone do not suffice. Selected nonnegative
quarter-unit targets certify at least 40,072 errors in every remaining case.
Integer histograms compute 178,240,944 cost-column instances; independent tests
check routes, polynomial counts, binary coefficients, fractional source sums
and overlapping ideal words. The interval is approximately
[27.1756%, 27.4855%], width 0.310 percentage points. Exact finite optimality,
external proof review and priority remain open. No asymptotic update, general
cover novelty, new model result or token/production saving follows. [C63]

## 5. Sparse dependencies and future queries

If exactly k of n named fields are active and each stores an arbitrary b-bit value, exact memory needs at least log_2 binomial(n, k) + kb bits when every configuration can be distinguished by future queries and no external channel supplies missing information. This is an elementary counting bound. It applies to identifiable active fields, not automatically to the much smaller set that happens to be queried in hindsight.

Before an unknown uniform coordinate query to A independent fair bits, a B-bit memory with average error epsilon <= 1/2 obeys B >= A[1 - h_2(epsilon)]. This is a standard random-access information bound, not a new theorem [@nayak1999]. If relevance is revealed only after an irreversible bottleneck, it cannot retroactively restore discarded distinctions.

Sound public retirement events yield a simple feasibility reference: a dictionary can keep the current values of all unresolved records. Identifying valid retirements from natural-language evidence is a separate inference problem. The implemented record-stream diagnostic assumes explicit sound events and should be interpreted accordingly.

## 6. Scripted workflow and recovery results

The [implemented environment](../experiments/dependency_memory/ARTIFACT_WORKFLOW.md) has once-only receipts, two forced record-memory boundaries, optional early manifest inspection, a possible revision, delayed intervening work, and an exact terminal verifier. Its initial 320-case development diagnostic showed the intended timing effect: structured retention succeeded in 16/16 tight/cheap cases with inspection versus 9/16 without, at costs 11 versus 10 synthetic units. Ample initial memory removed the need to inspect. These are constructed cases, not independent model trials.

The [recovery extension](../experiments/dependency_memory/RECOVERY_FRONTIER.md) adds a declared archive channel that returns only the latest required receipt after the final query. We compute an exact reference over every uniformly selected candidate subset and final target, within an atomic-record policy class. The first retained set precedes an unrevealed manifest; the second precedes the final query. An independent decision-tree enumeration and executable reference policies check the calculation.

Let p_0 and p_1 be the optimal probabilities of retaining the required receipt without and with inspection. At reliable recovery price c_R, the success-one expected extra costs are (1-p_0)c_R without inspection and c_I+(1-p_1)c_R with inspection. Thus inspection is cheaper exactly when c_I < (p_1-p_0)c_R. The complete expected-cost frontier is the appropriate convex boundary of the retained-only and recovered endpoints. This elementary reference permits randomized policies and assumes nonbinding per-episode limits; it is not a hard-budget optimum.

For six jobs, two candidates, two record slots at each boundary, and no revisions, p_0=1/3 and p_1=1. Inspection at price one is dominated by recovery at price one, whose expected extra cost is 2/3. Recovery at price four reverses the preference. With one child record, inspection raises pre-recovery success from 3/10 to 1/2 but increases success-one extra cost from 14/5 to three at those latter prices. A known first-candidate refresh raises p_0 to 4/5 in the two-slot case, demonstrating the importance of retaining revision conditions separately.

The [generated comparison](../experiments/dependency_memory/results/recovery_frontier_report.md) records 2,640 scripted episodes and 3,000 exact parameter configurations. These are finite diagnostic computations, not estimates of real-world prevalence or API savings. Record slots, serialized bytes, synthetic action units, and theoretical information bits remain separate quantities.

## 7. LLM development studies

This section separates the earlier development observations, the completed matched retention study, and unperformed extensions.

The [current bounded pilot](../docs/LLM_PILOT_SPEC.md) separates two questions. Stage A makes 12 inspection-decision requests across six exact cost regimes while scripted optimal retention and recovery remain fixed. Stage B reserves 36 development and 144 held-out episodes, comparing never, always, and model-selected inspection under identical model retention and recovery interfaces. It pairs explicit-label and inferred-dependency renderings, with two forced record boundaries. The historical full schedule permits at most 432 requests, but only the 96-request development tranche has run under a separately frozen [Luna transport contract](../docs/LUNA_DEVELOPMENT_RUN.md). Four held-out clue renderers now have an [offline semantic checkpoint](../docs/HELDOUT_RENDERERS.md): alias chains, package prerequisites, validation scopes, and deployment handoffs. Exact checks cover 120 clue forms and 240 pair/target continuations, with no target or receipt input to rendering. These are software checks, not model observations. Live request integration, boundary deletion checks, and the full launch freeze remain unfinished. Catalog sizes vary across families; equal record capacity does not control prompt-token cost.

The [development implementation](../docs/DEVELOPMENT_PILOT.md) supplies the direct-artifact template and strict request interface. Optimal and forget-all fake controls each complete 36 episodes in 96 fake requests, with pre-recovery availability of 26/36 and 0/36 on one route. These remain software controls, separate from model evidence.

The [first live development tranche](../experiments/dependency_memory/results/luna_development_2026-09-19/report.md) used the mutable `gpt-5.6-luna` alias with low reasoning effort and the existing ChatGPT subscription. All 96 requests returned valid decisions, with no transport/schema failures or corrective calls. Stage A chose the exact lower-cost action in 10/12 decisions; the two revision-cell disagreements had expected excess costs 1/5 and 3/5 synthetic units. Stage B completed all 36 episodes, with evidence available before recovery in 21/36 and 15 recoveries. Never/always/model-selected inspection respectively gave availability 3/12, 10/12, and 8/12 and realized synthetic costs 154, 140, and 137. Reused fixtures, one route, and valid retention tie-breaks prevent interpreting these totals as population effects or general superiority. [Detailed checks and findings](../research/LUNA_DEVELOPMENT_FINDINGS_2026-09-19.md).

Reported usage totaled 276,048 input and 27,140 output tokens, with reasoning included in output. Conservative token-derived usage was 2.5395 credit equivalents within a 20-equivalent planning cap; actual subscription debit attributable to this run is unknown. The client used fresh processes and ephemeral threads, declared fixed public instructions and restricted wrappers, zero configured retries, and a locally audited one-generation guard. Every accepted decision retained the deliberate `sessionBudgetExceeded` harness termination. This is a controlled single-response diagnostic, not a successful native-agent-turn comparison or a certification of inaccessible server internals. No held-out model calls were made.

An [exact post-hoc analysis](../experiments/dependency_memory/results/revision_analysis_report.md) grades each saved parent against the best choice with the same public information and an optimal child. The 17 uninspected decisions use the full 30-route population; the 19 inspected decisions condition on the visible manifest and its two targets. Three parents have strict availability deficits, all in uninspected revision cases: 1/5, 4/15, and 1/5. The other 33 match their reference. All 36 observed child selections are optimal conditional on the available records; this establishes nothing about unseen child decisions. Under a uniform pair and at least two child slots, refreshing its smaller-ranked member gives fixed-parent availability `1/2 + sum(j for j in F)/[n(n−1)]`, whereas no refresh gives `|F|/n`. The observed smaller-key parent sets therefore leave avoidable loss under the public revision rule. These are offline grades of existing answers, not additional model trials or evidence of internal reasoning.

A separately authorized [24-request follow-up](../research/REVISION_LUNA_FINDINGS_2026-09-19.md) reversed the refresh direction and varied visible-record order, with no realized route sampled and an optimal child explicitly guaranteed. All 24 responses were valid full pairs with zero exact availability regret. Refresh-first selected the two largest keys in 8/8 cells; refresh-last selected the two smallest in 8/8; no-refresh selected the smallest pair in 8/8, where every full pair ties. All eight matched directional shifts equal eight. For full two-record outputs, mean paired regret equals `(8 - shift)/60`, so these metrics are redundant. The observed pattern differs from the prespecified deterministic static controls but does not establish internal reasoning or causal improvement over the first workflow: prompt framing and the downstream guarantee changed. Reported usage was 66,200 input and 5,651 output tokens, or 0.58328 conservative credit equivalents under the separate 12-equivalent cap; attributable subscription debit remains unknown. These two earlier completed allocations account for 120 model calls, with no held-out calls or API billing. Its 30-route grades are exact conditional calculations, not additional model observations.

This first pilot uses atomic-record selection. Prose/structured summary comparisons and an intact native-provider baseline remain later, separately specified experiments. Stage-B decisions are compared descriptively with the exact reference: a model's imperfect retention may change its effective inspection benefit, so disagreement is not by itself irrationality. Whole episodes, isolated diagnostic copies, and information-sufficient controls are informed by prior incremental and interactive memory evaluation [@memoryagentbench2025; @amemgym2026]. The [source review](../research/PILOT_EVALUATION_REVIEW_2026-09-19.md) distinguishes the reviewed results from our proposed controls.

The [correctness audit](../research/CORRECTNESS_AUDIT_2026-09-19.md) clarifies a limitation of the pilot's matched reliable recovery: even an empty-retention policy succeeds on every valid completed episode under scripted submission. Stage B therefore measures pre-recovery evidence availability and completion cost, with terminal success primarily an interface/execution check. Fixed population-reference policies are also evaluated on the same reserved routes. Two strict population cost preferences become ties on the four-route held-out sample; one route per family prevents separating family and route effects. The pilot makes no family-specific or population-generalization claim.

Provider-managed state requires particular care. OpenAI's compaction interface returns opaque state and instructs clients to preserve the returned window. Anthropic documents model-dependent reasoning preservation and prefix binding. An intervention that edits history may therefore change both visible memory and reasoning continuity [@openai-compaction; @anthropic-thinking]. Controlled representation tests must enforce their declared channels; production comparisons must evaluate the complete supported intervention against an intact native baseline.

Cost accounting includes every model call, compactor call, cache read/write, retrieval, and retry. Prefix invalidation may outweigh short-horizon token savings, whereas sufficiently repeated future use may repay consolidation [@openai-caching; @anthropic-editing]. Report task success alongside cost and latency. A smaller prompt is not itself evidence of improvement.

### 7.1 Matched transfer study: methods and completed results

The [frozen transfer design](../docs/TRANSFER_STUDY.md) crosses job count (6 or 12), framing (compact or workflow), later-selector guarantee (explicitly optimal or unspecified), guidance (generic or prospective information-arrival guidance), and refresh rule (minimum-priority candidate, maximum-priority candidate, or none). Its 48 conditions occur in each of 32 generated blocks, totaling 1,536 scheduled model requests. Public priorities are randomly assigned independently of stable job keys; visible-record order is independently shuffled. Conditions within a block share materials. Workflow framing adds three short fixed events as well as different wording; it is neither a pure wording treatment nor a naturalistic long-context task. Generic and prospective guidance contain 30 and 31 words respectively. Canonical metadata and schema ordering remain declared channels, so randomizing priorities does not remove every possible ordering influence.

Each request selects at most two records before a uniformly drawn candidate pair and its uniform final target would be known. Every valid selection is scored offline over all 30 possible pair/target routes at six jobs or 132 at twelve; these exact conditional calculations create no additional model trials. Grading uses the best later selector even when its skill is unspecified in the prompt. That selector is not invoked, and its two-record capacity equals the two-candidate count, making the second boundary nonbinding. The endpoint measures retention potential under that reference, not observed downstream behavior or an empirical test of the bit-chain theorem.

The primary comparison matches generic and prospective guidance within workflow framing, an unspecified later selector, and refresh-present conditions: four pairs per block, or 128 planned pairs across 32 blocks. Benefit is generic minus prospective availability regret, normalized by the best-to-worst full-pair range at each job count. Positive values favor prospective guidance. The protocol specifies descriptive block resampling and separate reporting of incomplete pairs and blocks. Generated blocks are the resampling units, not independent natural tasks; shared worker, timing, and backend dependence remain limitations.

The first active phase dispatched 888 requests before a local percentage guard stopped admission. Three fully metered post-generation failures lost their answers and remain permanently missing; the other 885 responses were accepted. A documented [operational continuation](../docs/TRANSFER_CONTINUATION.md) completed only the 648 provably never-dispatched cases, preserving original public bytes, worker assignment, and relative order. Its existing-credit eligibility amendment changed admission, not scientific inputs or the original 1,536-request/200-equivalent allocation. Previously dispatched failures were never repeated or replaced. Five other host attempts failed before dispatch, including four at the initial zero-generation launch. The [pooled audit](../experiments/dependency_memory/results/transfer_luna_2026-09-19_continuation/independent_audit.json) verifies 1,536 unique dispatches, 1,533 valid responses, three transport losses, and no policy failures or unfinished cases. Historical source phases and the zero-request continuation preparation correction remain preserved.

Of the valid responses, 1,422 attain their exact reference and 111 have strict deficits. With refresh, 912/1,022 are optimal; without refresh, 510/511 are optimal, and the single exception is a valid empty selection. Every full pair ties in the no-refresh condition. These totals cover all conditions and are descriptive, not the primary treatment estimate.

All 128 primary matched pairs and all 32 blocks are complete; the three transport losses are outside that comparison. Generic guidance yields 114/128 optimal selections and prospective guidance 118/128. Exact regret favors prospective guidance in 13 pairs and generic guidance in nine, with 106 ties. The prespecified normalized benefit is 107/5120 = 0.0208984375. The 5,000-resample block bootstrap (seed 2026091914) gives descriptive 95% interval [-0.0203125, 0.060546875], which includes zero. Raw mean availability benefit is -7/1920 (-0.365 percentage points) at six jobs and 71/8448 (+0.840 points) at twelve. The normalized effect is a fraction of the full-pair loss range, not a task-success percentage-point gain. No treatment improvement or absence of an effect is established.

Exploratory error classification finds 50 selections matching the two smallest job names, 15 matching the two largest, and 37 matching the optimum for the opposite refresh direction. Two overlaps leave 100 of 111 errors matching at least one pattern; 11 match none, including the empty selection. These answer patterns do not identify internal mechanisms. All 48 condition summaries, the prespecified interim checkpoint, limitations, and reproduction links are retained in the [final findings](../research/TRANSFER_LUNA_FINDINGS_2026-09-19.md). A separate recomputation enumerated routes directly from saved selections and reproduced the primary counts, exact effect, and bootstrap endpoints without calling the study grading or aggregation functions.

Reported usage across the 1,536 dispatched requests is 4,768,512 input tokens (including 2,412,032 cached), and 632,736 output tokens (including 595,880 reasoning). Conservative planning usage is 48.78528 credit equivalents within the original 200-equivalent ceiling; no charge is uncertain, but actual experiment-attributable subscription debit remains unknown. The run used the mutable Luna alias at low effort through the isolated subscription client, with no API billing, purchases, resets, retries, or held-out calls. This completed diagnostic supports neither a native-compaction gain nor a claim about a binding second memory boundary.

## 8. A finite audit of compaction states

An executable [compaction collision auditor](../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md) broadens the project beyond the bit-chain example (C35-C36). It partitions finite prehistories by their exact retained and public channels, then computes the minimum worst-case cost of a zero-error adaptive recovery policy for each declared future task. Terminal correctness is a relation permitting multiple valid answers. Independent checks validate an attaining policy and a lower-bound DAG covering every allowed action. A second exact search finds a minimum additional-message partition that supports all declared tasks before their identity is revealed. This optimizes an explicit finite alphabet, not natural-language summaries or tokens.

Twelve constructed specifications include three accepted-action sets {A,B}, {B,C}, and {A,C}: each pair passes zero-recovery feasibility, but their common memory cell fails; two retained states repair it. An eight-world sharded archive has adaptive recovery cost two versus fixed-batch cost four. Versioned-access and harmless-loss controls prevent labeling every deletion a failure. Forward enumeration independently checks all 343 three-world accepted-action tables over all seven nonempty world subsets. These are finite diagnostics, not sampled LLM outcomes. The tools are deterministic and read-only, the model is public, and recovery observations persist until termination; no further memory boundary is imposed during rescue.

This proposed audit protocol is distinct from scoring a sampled continuation, but diagnostic summary repair, verifier-guided continuation evaluation and typed commitment verification already exist [@wicer2026; @trace2026; @contextcodec2026]. Information-state dynamic programming and group-based functional compression are also established [@subramanian2022ais; @basu2022hypergraph]. We claim neither a new general planning theorem nor novelty for the elementary three-set example. Publication priority, a sound natural-task adapter, and usefulness beyond simple critical-field retention remain open.

### 8.1 Feedback before forgetting

A new [execution adapter](../research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md)
closes a finite propose-audit-repair loop around the existing artifact environment
(C37). It derives accepted actions from restored terminal execution, enforces two
record-memory boundaries, and feeds independently checked unsafe collision groups
back into a finite candidate search. Under a fixed contract, each accumulated
constraint rejects its current candidate and no feasible candidate, giving the
elementary at-most-|C| full-audit bound. This is established refinement and finite
elimination machinery [@clarke2000cegar; @zhang2017pomdp].

In the main constructed case, a weak schema succeeds on 32/48 world/routes;
accumulated feedback finds a 48/48 schema in three audits. Latest-only feedback
cycles. A workflow-aware critical-field baseline already attains 48/48 with one
audit. Across 48 capacity/recovery contracts the accumulated, exhaustive and
critical-field methods certify the same 18 cases (C38). Offline synthesis costs
are separate from execution action units; no matched-total-cost advantage or
model improvement follows. Cumulative preservation constraints already occur in
WiCER [@wicer2026], while the Memento team describes specific judge feedback for
compression retries [@memento2026article].

Controls show that a binding child boundary can defeat the priority-selector
family, that incomplete probes miss obligations, and that value-dependent choice
of a tagged receipt can encode two binary values in four one-record states (C39).
The latter succeeds with a finite public-catalog decoder but not with ordinary
receipt-only submission on every outcome. Thus record counts are not state bits,
family exhaustion is not unrestricted impossibility, and the existence of a
successful decoder is not a performance guarantee for a chosen agent. Natural
task extraction, scalable verification and practical superiority remain open.

### 8.2 A stricter novelty boundary

The [follow-up audit](../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md) gives an
exact elementary reformulation (C40). For a fixed task and hard recovery budget,
regard each bounded decision tree as a strategy symbol. A collision group is
safe iff its worlds share an accepted strategy. Requiring this for every future
task gives a downward-closed safe family. Its minimal unsafe groups are forbidden
hyperedges; the smallest extra memory alphabet is their weak chromatic number.
Labels can be reused across already distinguishable retained/public cells.
These are established strategy and coloring ideas [@dupuis2004strategies;
@bennett2016weakstrong], with safe-group coding precedents [@basu2022hypergraph].
No asymptotic coding theorem is imported into the one-shot cost contract.

Forward strategy composition checks 7,203 subset/budget cases on the existing
343 three-world answer tables, and 1,029 colorings agree with repair optimization.
Independent color-assignment search also agrees on the 12 existing fixtures.
These extend verification of an existing finite domain, not independent trials.

Self-GC supplies pre-commit structural rehearsal and recoverable context objects
[@selfgc2026]; this differs from exhaustive semantic certification. Executable
counterexamples and learned-model refinement also have formal-methods precedents
[@meijer2019blackbox]. Therefore neither the broad architecture nor our finite
optimizer currently supports a general novelty claim. Cheap, sound extraction
from realistic workflows and measurable benefit at matched total costs remain
candidate systems contributions, not completed results.

### 8.3 Historical workflow extraction and conditional resource benefit

Constraint pinning is another close precedent: *Governance Decay* protects
memory-carried rules, evaluates allowed-action controls, and reports limits under
forged authority updates [@chen2026governancedecay]. The present release-oriented
extension keeps the rule public and tests loss of the changing evidence to which
it applies. This is an experimental distinction, not a claim that pinning or typed
retention cannot preserve such evidence. See the [scope comparison](../research/LUNA6_SCOPE_PRIOR_ART_2026-09-22.md).

The [new replay](../research/HISTORICAL_WORKFLOW_REPLAY_2026-09-22.md) extracts the
last two attempts from each of four workers in the completed transfer phase.
The four final attempts all have `transport_failure` status, but three generated
and settled before their answers were lost, whereas one stopped before dispatch.
A local plan that retries all four contains three duplicate-dispatch IDs; holding
all four loses one eligible first submission. These are counterfactual handoff
failures derived from observed evidence, not evidence that historical compaction
caused the transport events. The pinned original classifier and saved continuation
certificate independently agree on all eight extracted records. Claim C41.

All methods receive the same 53,736-byte canonical input. The task imposes two
byte limits, reveals a worker pair between them and a case ID afterward. Six pairs
and four targets produce 24 routes over the same records, not independent trials.
Lossless named fields require 2,722 bytes, a compact fixed schema 1,649, and checked
dispatch/accounting receipts 1,231. Case IDs, request hashes, exact amounts, schema
tags and wrappers count in these totals; no finite payload catalog is provided.

At caps of 1,536/768 bytes, a checker price of 128 units, a tool price of 128 units
and one unit per transferred UTF-8 byte, the first whole-record-recovery frontier
threshold where repair completes all routes is 62,501 total units. At that same
allowance, status summaries complete 3/24, named fields 11/24, compact fields 18/24,
and both repaired and direct receipts 24/24. The threshold is descriptive and
comes from the complete enumerated frontier. Direct receipts need only 58,761
units for all routes. These prices cover declared replay transfers and operations,
including failed work; they do not measure CPU, archive infrastructure, model
tokens, provider caching or production dollars. Claim C42.

Across 180 constructed contracts, repair never beats direct receipts (147 ties,
33 losses). It beats compact fields in 17, ties in 133 and loses in 30. Cheap
indexed recovery and expensive up-front checks supply adverse conditions. The
known public rule makes diagnosis redundant here; the candidate engineering
mechanism is cheap result retention with appropriate scope, not a better generic
feedback algorithm.

The separately authored projection/classifier agrees with pinned original
semantics on 1,388 adversarial inputs. Eleven receipt-scope controls permit reuse
for unchanged or irrelevant metadata and invalidate changed evidence, previously
absent fields, request/case identity and checker revision. Current evidence must
be read and hashed for this check; its byte cost is reported. These perturbations
are synthetic controls, separate from the immutable-artifact replay. Automatic
extraction on observed external workflows, adversarial isolation and live
matched-production-cost benefit remain unperformed; the separate constructed
new-schema test below does not resolve them. Claim C43.

### 8.4 Fresh GPT-6 Luna medium compaction calls

The [new release pilot](../research/LUNA6_DELAYED_FAILURES_2026-09-22.md) freezes
four constructed six-service histories, two memory boundaries of 900 and 440
UTF-8 bytes, and sixteen delayed continuations per method. It makes 117 fresh
`gpt-6-luna` calls at medium reasoning, including a smoke request. The exact
request/usage audit passes. Source histories, public rules, model inputs and
memory limits are saved; opaque reasoning, session history and tools are not
available to accepted continuation responses. This is a fresh-thread controlled
pipeline, not native provider compaction. Claim C44.

Prose succeeds on 12/16 decisions and structured summaries on 8/16, with one
unsafe simulated release in the latter. Checked dependency replacement, direct
dependency rows, indexed recovery and full-history access each achieve 16/16.
The unsafe release follows loss of an open blocker when the second structured
summary exceeds its cap. Unclipped summaries also omit negative evidence or
alter executable identifiers. All four structured child proposals are overlong,
so semantic omission and host clipping are not isolated explanations.

Including every memory-writing call, checked replacement costs 0.2653020
planning credits versus 0.2912620 for structured summaries, an observed 8.9%
reduction; the reduction is 8.6% without cache discounts. Direct rows cost
0.0865340, indexed recovery 0.0830870, and full history 0.1293510. The
direct/indexed ordering reverses without cache discounts. Repair and direct
final inputs are identical. A manually known gate permits direct serialization;
iterative proposals are not the best method here. Local CPU, recovery bytes,
unknown infrastructure costs and unknown subscription debit remain distinct
from token-based planning credits. No fully monetized production-cost or
held-out gain is established. Claim C45.

A 24-call follow-up, frozen after inspecting the pilot, explicitly announces
that public rules will be repeated and prioritizes service facts and exact
identifiers. It eliminates clipping in all eight retained memories but succeeds
on 12/16 decisions, at 0.1908300 credits (0.2714700 without cache discounts).
Unclipped memories shorten exact service IDs and confuse an approval identifier
with the current-artifact reference, creating incorrect delayed work. This
demonstrates surviving semantic failures in the tested pipeline, rather than a
pure truncation explanation. It is a prompt package on reused development
histories, not held-out or single-factor causal evidence. Both studies total
141 calls and 1.3190825 credits; the original and follow-up sources are separately
frozen. Claim C46.

### 8.5 Annotated-schema checks on new tool-result traces

The [frozen follow-up](../research/SCHEMA_CHECKS_UNSEEN_TRACES_2026-09-22.md)
uses six newly constructed evaluation traces with disjoint development values
across retry handling, CI handoffs, and multi-stage data jobs. Their obligation
families and annotated tool schemas are shared with development; the evaluation
is of new trace instances, not new schema structures. At 2,600- and 1,300-byte
boundaries, a generic extractor keeps scalar tool-result fields and checks
schema-annotated exact IDs and owner/path/reference triples before source
deletion. The second check sees only the bounded parent memory. It does not
certify unannotated state or inspect arbitrary model-proposed prose. The
hand-written direct baseline uses explicit family-specific critical fields.

A fixed GPT-6 Luna medium schedule makes 72 calls and records 0.5510905
token-derived planning credits. Across 12 paired terminal decisions, stronger
data-first prompting, automatic checked tables, hand-written direct records,
indexed recovery and full history each score 12/12. The automatic arm removes
memory-writing calls and costs 0.0725445 model credits versus 0.2537065 for
prompting; direct records cost 0.0667650 and indexed recovery 0.0628880.
Under declared synthetic local CPU/byte prices, the automatic total is about
0.07312518 versus 0.25370650 for prompting. The live Windows timer quantized
brief local operations to zero; this total uses a separately labeled post-run
high-resolution development-trace CPU calibration. Actual subscription debit
and full production costs remain unknown.

The prespecified primary criterion of fewer failures at equal or lower total
cost **fails**, because the strong prompt also has no failures. Automatic
records tie the hand-written control in this small constructed set, but the
direct and indexed arms are cheaper. This does not establish a novel mechanism,
robust unannotated extraction, or an advantage over strong simple retention.
Claim C47.

The separate [prospective transfer test](../research/SCHEMA_TRANSFER_PROSPECTIVE_2026-09-22.md)
froze retry-queue, CI-promotion and multi-stage-data evaluation schemas before
implementing a generic, annotation-free extractor. Development used escrow and
package schemas. Seven tool results per trace pass through 3,000- and
1,050-byte boundaries, with target and late event revealed only afterward.
One check preserves exact detected identifiers; another preserves their owner
and field-path associations, including approval scope. Model-proposed memory,
automatic direct projection, hand-written direct records, indexed recovery,
strong prompting and full history are compared on the same 18 terminal cases.
All 126 fresh GPT-6 Luna medium calls complete for 1.2564565 token-derived
planning credits; actual subscription debit is not attributable.

Automatic direct has 1/18 exact terminal failures versus 2/18 for stronger
prompting and hand-written direct. Its prespecified experimental total is
0.12644885386 synthetic credits versus 0.43840213083 for prompting, so the
**narrow primary success criterion is met**. Indexed recovery nevertheless
has 0/18 failures at 0.11673546631 and dominates automatic direct in this
finite comparison. The checked model-proposal path has 2/18 failures and costs
0.44173514106: all six prose parent proposals fail the table-only certificate
and fall back to automatic projection. One automatic final response confuses a
retained load run ID with the required output dataset. Thus certified retention
does not ensure correct execution. The evaluation uses newly constructed,
correlated traces whose evaluation schemas were visible in the frozen casebook,
and synthetic local prices. It is not a blinded unknown-schema test and does
not establish novelty, production savings, or superiority over cheap indexed
recovery. Claim C48.

### 8.6 Cross-record stress test and permanent transport gap

The [cross-record protocol](../experiments/dependency_memory/cross_record/FROZEN_PROTOCOL.md)
adapts the same constructed obligation grammars but splits each workflow into
a root and separate component tool results, shuffled among seven workflows.
The generic extractor joins by exact opaque workflow keys and checks retained
ID bytes and their root/component/field-path associations. Development cases
and protocol were committed before implementation; twelve retry, CI and
data-job evaluation cases were derived from the implementation commit before
model answers. These are new values and arrangements within known domain
grammars, not independently observed workflows or blinded unknown-schema
transfer. Two memory limits of 7,000 and 2,600 bytes precede a late target
and event. Eight arms include strong prose, unvalidated structured prompting,
checked proposals, automatic and hand-written direct records, raw and
projected full-workflow indexed recovery, and full history.

The original 348-call schedule stopped after 199 dispatches on one provider
generation error in the indexed projected arm. Its answer and usage are
unknown. A [separately frozen continuation](../experiments/dependency_memory/cross_record_continuation/FROZEN_PROTOCOL.md)
sent only 149 never-dispatched identities. The combined saved ledger contains
347 metered answers and one permanent gap, with 3.8247600 known token-derived
planning credits. The **original 36-pair primary criterion is unassessable**.
On the 35 fully answered paired futures, automatic direct has 7 exact
failures, strong prose 3, unvalidated structured prompting 6, hand-written
direct 4, and raw indexed full-workflow recovery 1. Automatic's synthetic
experimental total for all its completed calls is 0.34358725611 credits,
versus 0.87246417172 for prose, 0.19375442753 for direct and 0.2261409081
for raw index. It is cheaper than prompting but more expensive and less
accurate than two strong controls. The projected index has six model errors
on the 35 answered paired cases plus the permanent transport gap; its total
cost is not precisely known. These post-stop comparisons are exploratory and
do not establish the candidate contribution. Claim C49.

All twelve automatic parent/child certificates pass, with no infeasible
projection or memory clipping. Deterministic reconstruction from automatic
and direct tables supplies the correct frozen terminal outcome on all 36
futures, so their observed errors are in final-model interpretation of
sufficient facts. One automatic data-job final says `publish` where an
approval-scope mismatch requires `hold`; no real action was taken. The
checked proposal arm's 18/36 errors are additionally confounded by a
parent-check/child-decoder mismatch: six parent proposals include redundant
per-component join keys, pass the narrow ID check, and are rejected by the
child schema reader, leaving empty child memory. This is a concrete software
defect, not evidence against a corrected checker. Local cost conversion is
synthetic, direct authoring and provider infrastructure are unmeasured, and
actual subscription debit is unknown. See the [focused diagnosis](../research/CROSS_RECORD_RECOVERY_2026-09-22.md).

### 8.7 Decoder-compatible parent check: offline correction

The frozen checked arm tested exact detected identifiers and their owner/path
associations, but it did not require that the later decoder accept every
retained field. A separate [versioned check](../research/DECODER_COMPATIBILITY_REPLAY_2026-09-24.md)
now verifies the parent table's supported joined-schema paths, scalar types
and enums, exact root-owner selection, and both child capacity and acceptance
by the actual child checker for every possible two-candidate pair before source
deletion. A branch-audit counterexample showed that selection and serialization
alone do not imply child acceptance when ID coverage depends on retained values.
An incompatible model proposal
falls back to the deterministic source projection; the child check cannot
introduce paths absent from the bounded parent. The v1 requests, responses,
implementation and terminal outcomes remain unchanged.

In a post-hoc replay of the twelve saved structured parent proposals, nine
pass the old ID check and three pass the new compatibility check. The six
newly rejected old-pass proposals have unsupported paths. After fallback,
all twelve admitted parents support all 252 possible two-owner child
handoffs. This is a deterministic software diagnostic on inspected
constructed data, not a new model or terminal-performance result. The
certificate still accepts a schema-valid but wrong state value, or omission of
a non-ID state field; semantic sufficiency, final-model interpretation errors
and action safety require separate evaluation.
Claim C50.

### 8.8 Observed repository handoff: live development comparison

Following the offline evaluation packet, a separate contract and 36-call schedule
were frozen at `ef31373`. One observed local test/validate/build capture supplies
an unchanged handoff and three explicitly constructed continuations: a new source
snapshot, a later failed test and a replaced HTML artifact. All model requests
use `gpt-6-luna` medium through a freshly audited client; the mutable model alias
is not an immutable snapshot. Current model limits, protocol and token-credit
rates are dated official-source checks, while serialization is verified locally
[@openai-gpt6-luna2026; @openai-codex-appserver2026; @openai-codex-pricing2026].

Checked proposals, direct records, indexed raw recovery and full history score
4/4 exact decisions; strong prose scores 3/4. No false-ready decision occurs.
Charging both writers, model planning credits are respectively 0.2940470,
0.0325430, 0.1968765, 0.2012055 and 0.2858350. Direct records remain cheapest
without cache discounts. The entire schedule completes for 1.0105070 planning
credits with no retry or transport failure. Local CPU, byte traffic and index
storage duration are separate measurements; actual account debit, human effort
and fully monetized infrastructure cost remain unknown.

The prose failure omits a repository success from its final evidence despite
retaining that exact receipt in an unclipped 814-byte child. Two checked children
produce receipt-list JSON missing its closing bracket and fall back to records
derived from the bounded parent, without recovering deleted source. The
[saved-evidence analysis](../research/WORKFLOW_LUNA6_COMPARISON_2026-09-29.md)
reconstructs every public request before grading. These are four correlated
development conditions from one observed local workflow; they neither fill the
twelve untouched evaluation slots nor assess the packet's held-out go criterion.
Claim C51.

### 8.9 Executed workflows: interrupted follow-up

A separate twelve-scenario casebook executes 48 actual local commands, including
seven failed runs, rather than mutating prior receipt metadata. The source/runtime
bytes and artifact contents are retained, and offline reproduction verifies every
exit code and build output. Eleven final queries select fewer than all three checks.
These are scripted scenarios in one fixture family, not untouched real incidents.

The 108-call Luna 6 medium schedule was frozen at `d7cb8e8` and stopped at request
17 on an app-server timeout. A separate extension frozen at `e32b576` dispatched
only never-attempted identities and stopped at its ninth call on a provider
generation error. The combined ledger has 26 attempts, 24 metered answers, two
permanent gaps and 82 never-dispatched identities. Neither failure was retried.
Known cost is 0.2567650 planning credits; retaining 15.30 credits in unknown-usage
reservations prevents another 7.65-credit reservation under the 20-credit ceiling.
Those reservations are not observed spending. Actual account debit is unknown.

Of twelve observed final answers, eleven are exact and none is false-ready.
The direct-record response in the repaired-test case unnecessarily requests a
rerun despite a sufficient 203-byte retained successful receipt. An independent
application of the public rule to that memory yields the correct ready answer.
This is a final-model interpretation failure after successful retention. Only
the unchanged case has all five answers, so neither a method ranking nor the
intended twelve-case outcome can be established. The [partial audit](../research/EXECUTED_WORKFLOW_COMPARISON_2026-09-29.md)
reconstructs every attempted input and preserves all missing dispositions.
Claim C52.

### 8.10 Retained evidence and final decisions: retrospective audit

A [separately frozen offline investigation](../research/EVIDENCE_USE_AUDIT_2026-10-01.md)
replays every scheduled final identity in the cross-record continuation and both
September 29 workflow studies. These studies were selected by recency and terminal
relevance after outcomes had been inspected. A 470-file source lock preserves the
historical inputs. Of 368 scheduled finals, 319 are observed, three are permanent
transport gaps and 46 were never dispatched. No new model call is made.

The 319 answers contain 53 errors. Thirty-one proposals differ from a correct
readout obtained by applying the public rule to their typed admitted memory.
One prose error overlooks a retained success, confirmed by bounded human reading.
One typed memory's readout disagrees with the source, seventeen are empty and
three representations remain semantically uncheckable by the new parser.
Uncheckable does not establish information loss.

The pure actor-side guard accepts only the saved final request and proposal. It
neither imports a grader nor reads files or archives. Its hand-written receipt,
retry, CI and data-job interpreters produce 227 consistent, 32 contradicted and
60 uncheckable verdicts. The 32 contradictions are wrong model proposals, but
one interpreter readout is itself wrong because retained state is already wrong.
Of the uncheckable proposals, 39 are correct and 21 wrong. Releasing only consistent
proposals would therefore withhold 92, including 39 correct answers. Separately
grading the 259 available readouts gives 258 correct; neither a veto nor this
hypothetical replacement measures a repaired or executed task. Claim C53.

Coverage is not inferred from consistency. An elementary control gives two full
histories the same public snapshot and final inventory. One contains a successful
receipt; the other adds a later failed run. Retaining only the success produces
identical admitted memory, task and proposal, while the full-ledger grader requires
different answers. A deterministic checker restricted to those inputs cannot
distinguish the histories. The implementation returns consistent and explicitly
does not certify completeness; a well-formed forged receipt also passes. This is
a checked information-channel example, not a new general impossibility theorem.
Claim C54.

Local measurement records 50 batches of 319 checks, CPU and elapsed time, and
1,741,509 compact input bytes plus 65,282 output bytes per batch. It excludes
evidence loading, evaluator grading, I/O and human rule compilation; production
total cost is unpriced. Independent formulations compare 1,234 finite cases to
the unchanged graders. They are implementation checks, not independent task trials.

Provenance-linked summary routing and escalation are prior methods in TierMem
[@tiermem2026]; memory-dependent tool-parameter evaluation is covered by
Mem2ActBench [@mem2act2026]. The known-rule readout is a diagnostic control.
Automatic unfamiliar-workflow contract extraction and prospective utility remain
unperformed. Actual task intake is [segmented within this repository](../experiments/dependency_memory/workflow_intake/README.md);
the current inspected task is development evidence. A future prospective observed
comparison must freeze the method and grader before new tasks arrive and enforce
serialized actor access. Folder separation alone does not provide blind evaluation.

The first newly registered development episode captures this actual research
task at source commits `eeec334` and `f9a9511`, with three offline commands per
checkpoint and six zero exit codes. The direct-receipt parent takes 728 UTF-8
bytes and the child retaining both snapshots takes 1,455, fitting the unchanged
4,096/1,536-byte caps. This preserves an easy feasible control; no capacity
obstruction or new model outcome is inferred. Fourteen raw manifest/output files
are hash-pinned, while generated artifact copies remain ignored locally after
verification. The final reporting task binds B's source and inventory, not later
writing/registration changes. Claim C55.

### 8.11 Exact-table redundancy and actual parent dependence

A [separate local audit](../research/WORKFLOW_METHOD_AUDIT_2026-10-01.md) defines
P(L) as the last receipt for each (snapshot, check) in the chronological ledger.
The original checker accepts only a table equal to that entire projected set,
otherwise falling back to direct serialization. In the fixed JSON-list grammar,
field names, check names, artifact paths and hexadecimal identities are ASCII;
permutations preserve length and whitespace/escaping cannot shorten compact
direct encoding. Integer fields reject float encodings. No valid exact table
fits when direct encoding fails; both policies then admit empty memory.

Equal bounded parent maps plus the same later observations and announced scope
give equal child receipt maps. This elementary deduction is not an optimum over
other codecs or all functionally sufficient states. A separate reverse-scan
software specification agrees with the unchanged grader on 158,340 constructed
queries. The audit also checks 158,340 direct projections, 5,652 writer proposals
and 52,780 two-boundary states with zero disagreements. These are finite checks,
not independent trials. Claim C56; external human review is pending.

Original JSON order/whitespace can affect stochastic model or cache behavior.
Semantic equality does not prove empirical accuracy or production-cost equality.
The new canonical shadow emits the same bytes as direct memory. Conditional on
equal downstream operations/prices and nonnegative writer costs, its two added
writer calls supply no benefit. Unknown extraction, different codecs and
unavailable fallbacks are different problems.

For E0001, B's receipts give the same exact answer and supporting run IDs as the
full ledger for the actual B-tree query. Direct state fits both caps. It is an
easy control without an actual parent-memory requirement; earlier-tree query
variants remain constructed. In fact, A has no receipt for the requested B tree:
under exact-snapshot matching, removing such A receipts cannot affect the answer
even if B leaves checks missing. Selective capture alone cannot overcome this
task-contract limitation. Its full logical request is 163,432 bytes, exceeding
the old local 100,000-byte cap. The new logical cap is 262,144; memory limits
are unchanged and actual provider wire/token limits remain unverified. Claim C57.

The new method supplies four arms, two prose writers and four final slots per
task, with the same retained-evidence check. Scripted completion/replay validates
interfaces only. Screen every future actual query for B-only sufficiency and
direct cap feasibility. If all twelve are B-only and fit, stop the proposed
two-boundary study for this workload, retaining all tasks in the denominator.
No retrospective cap reduction or prospective model gain is inferred.

### 8.12 Public-schema encoding and the cached-outcome control

A [separate source-driven control](../research/SCOPE_CODEBOOK_CONTROL_2026-10-01.md)
uses the existing public fixed-schema codec on eight inspected historical attempt
records. Across six constructed worker-pair scopes and 24 later exact-record
queries, authored JSON retains 3,030 parent bytes but fails three child caps,
scoring 12/24. The same authored fields in the existing schema use 1,957 parent
bytes and 949–1,009 child bytes, scoring 24/24. Cached public-program outputs also
score 24/24 with 1,539 parent bytes and 761–779 child bytes. Caps stay 4,096/1,536.
All 14,505 constructed catalog rows agree with the original classifier after the
packed projection. Claim C58; no new dictionary-coding novelty is implied.

A single JSON serialization's infeasibility does not prove a capacity obstruction.
The known program also permits the strong functional-retention control of caching
its outcomes before the record query arrives. Dependency traces and result reuse
are established mechanisms [@buildsystems2018]. The separately frozen source-only
Luna inference results are recorded below. This offline control supplies no
natural-task prevalence, model gain or fully priced production comparison.

### 8.13 Source-only contract sufficiency versus byte feasibility

The [frozen source-only study](../research/SCOPE_INFERENCE_FINDINGS_2026-10-01.md)
shows the original decision program, constants and retention DSL to Luna while
excluding historical records, the authored projection, catalog and labels.
Four paired replicates compare concise and closure instructions. The approved
first implementation stops locally before any dispatch; its separately frozen
replacement returns two answers, then times out on the third request. A further
frozen suffix dispatches only the five unattempted identities with identical
public requests and the original combined eight-call/20-credit ceiling. The
timed-out identity stays permanently missing and is never retried.

Combined, eight dispatches produce seven metered answers, one permanent transport
gap and no unattempted identities. All seven contracts have zero disagreements
and zero false preflight-only cases on 14,505 constructed catalog rows, including
14,490 distinct inputs; all also agree on eight inspected historical records.
This is finite-catalog completeness, not universal semantic certification. Five
contracts select narrow accounting fields, matching the authored 3,030-byte
parent on those observations and scoring 12/24 imposed late queries. Two closure
contracts retain the full accounting object: their 15,459-byte parent exceeds
the 4,096-byte cap, yielding 0/24. Final replay is scripted classifier execution,
not additional LLM final decisions. The schema and cached-result controls from
Section 8.12 each score 24/24 under the same caps.

Concise has three observed complete contracts and one missing answer; closure
has four observed complete contracts. The three fully observed pairs all agree
on catalog completeness. The original eight-metered-answer primary criterion
remains unassessable. Known cost is 0.2232910 planning credits, or 0.2399950 in
the cache-neutral view. The timeout retains 7.65 unknown-usage reserved credits;
7.8732910 is committed allocation, not measured spending. Actual debit and fully
priced lifecycle cost remain unknown. One inspected program with constructed
timing supports a development diagnostic of sufficiency and representation size,
not independent-workflow generalization, prompt superiority, a novel extraction
algorithm or production savings. Claim C61.

### 8.14 A stronger static control with the codec held fixed

The [separate offline control](../research/STATIC_SCOPE_CONTROL_2026-10-01.md)
analyzes public source, entry and formal names without record values, the
authored contract, evaluator labels or model responses. It tracks aliases,
constant keys, membership, type/truth uses and literal helper contexts.
Unsupported operations retain their whole base or input. Dependency analysis
through calls is established program-slicing prior work [@horwitz1990slicing];
this limited heuristic claims neither that algorithm nor general slicing novelty.

Three inspected repository programs and one constructed late-key family give
zero original/projected disagreements on 51,566 finite input/query rows:
14,505 dispatch, 20,769 token-validator, 16,207 quota-validator and 85 late-key
cases. The quota program uses whole-input fallback; its agreement is not a
narrowing success. Errors and malformed types stay in the comparison. Historical
token arithmetic is pinned program behavior, not current provider pricing.
Finite agreement does not certify arbitrary Python programs or inputs. [C64]

Every projected dispatch arm uses the same existing fixed-schema codec algorithm
with a public schema derived solely from its contract. Static and authored
contracts each use 1,958 parent and 950–1,009 child bytes and answer all 24 imposed
late queries under unchanged 4,096/1,536 caps. Public schema sizes, 263 and 240
bytes respectively, are reported separately from instance memory. Cached known
program outcomes use 1,539 parent and 761–779 child bytes and also answer 24/24.
Whole-root and raw contracts exceed the parent cap and answer 0/24. [C64]

Uniform-codec replay of seven already observed model contracts gives five
24/24, four with 1,958-byte parents and one with a 2,329-byte parent; the two
whole-accounting contracts propose 14,758 bytes and still score 0/24. This is
scripted post-hoc replay, not new LLM final decisions or an independent study.
The old eight-answer primary criterion and permanent gap remain unchanged.
No observed contract beats the static control here. Eleven tests check generated
program variations, malformed types, exceptions, overlap of membership/truth
requirements, conservative fallbacks, codec roundtrips and irreversible memory.
The result removes a reason to spend more calls on this inspected classifier;
broader automatic extraction, natural-workflow benefit and fully priced lifecycle
cost remain open. No new model call or natural task is added. [C64]

### 8.15 A parent-rate spectrum and a restricted support transition

The [separate exact spectrum](../research/PARENT_RATE_SPECTRUM_2026-10-01.md)
extends the C34 rate-two calculation to eight rational parent rates, preserving
the source/query law, one-bit child and all information boundaries. Every slope
checks all 4,751 orbits covering all 1,679,616 final tables, including repeated
and noncomplementary endpoints. Common supporting inequalities allow arbitrary
joint encoding and heterogeneous block tables. Rational Gibbs witnesses have
strict information slack; fixed-length coding supplies asymptotic upper bounds.
Each interval is narrower than 2e-11, with the lower bound valid for every k.
These are mathematical enclosures rather than confidence intervals. [C65]

For example, rate 0.9726441913 bits per block has limiting error in
[0.2969469397286971, 0.2969469397292819]; rate 2.5406225816 has limiting error
in [0.2500924641065645, 0.2500924641067975]. Rates are the reported rationals,
not claims at nearby round budgets. The old rate-two and finite three-block
results remain unchanged. [C65]

For the fixed unsigned decoder, symmetrization leaves three reproduction
classes. An explicit positive-kernel mixture dominates the odd-weight class
for every 0<t<1. The supporting optimization reduces to one balanced mass p,
with a unique transition from two constant words to those words plus six
balanced words. A polynomial transformation proves uniqueness and outward
arithmetic places the transition information in
[0.620690001029, 0.620690001030] bits per block. Support size is a property of
the test channel, not extra memory available at final decoding. [C65]

Supporting objectives and treatment of zero-support outputs use established
rate-distortion reasoning [@polyanskiywu2016coding]. The unsigned reduction is
valid at every positive slope; unrestricted decoder optimality is checked only
at the eight new slopes and the earlier C34 slope by C65 alone. Section 8.17
supplies the later all-positive-slope comparison. Efficient finite codes,
external proof and source priority remain open. Post-hoc mathematical
exploration is separate from the exact certificate.
No model call, natural task, token saving or production benefit is added. [C65]

### 8.16 Complementary final decoders suffice under the balanced source

The [completion theorem](../research/COMPLEMENTARY_COMPLETION_2026-10-02.md)
shows D_k(B)=D_k^complementary(B) for every k/B in the stated balanced-source,
source-independent-query, average-Hamming-loss model. Hold an arbitrary joint
encoder and updater fixed. Preserve endpoint bits where the two predictions
disagree; on each agreeing coordinate, fill the zero endpoint by an independent
fair design bit and the one endpoint by its complement. Both old constant-bit
error and averaged new error are 1/2. Some fixed public completion is therefore
no worse. Sorting endpoint labels only XORs a fixed public R/O bit into the
child; parent capacity and the late-J information boundary stay unchanged. [C66]

A constructive completion chooses modal population values of X_j XOR old_child
on the formerly constant coordinates. These are offline design statistics,
not post-compaction source access. The output-word relabeling is bijective,
so I(X;A) also stays unchanged. Every positive-slope supporting optimization
can thus be restricted to the six complementary symmetry families. The C62
converse supplies an alternative proof of the unchanged unrestricted 40,072/
147,456 lower bound; C63 remains an independent larger certificate. [C66]

The finite checks cover 9,216 branch/policy cases and execute 3,686,400 whole-code
query routes, including eight preserved auxiliary books and identity on C59.
Completion plus separate nearest-parent reassignment reduces the auxiliary
minimum to 40,738 errors, still above the existing 40,529 witness. A biased
two-source law has unrestricted zero error versus complementary minimum 1/6;
a separate instance example loses correctness despite equal mean loss. The
theorem gives average preservation under its hypotheses, not individual or
worst-case semantic safety, an efficient practical design method, a new general
derandomization principle or a model/natural-workflow result. Section 8.17
uses this reduction for the full curve comparison. External proof and
publication priority remain open. [C66]

### 8.17 The unrestricted curve at every parent rate

The [continuum certificate](../research/UNRESTRICTED_RATE_CURVE_2026-10-02.md)
proves that the unsigned family attains the minimum of I+s E L for every s>0
over all legal final decoders. C66 reduces to 256 complementary tables in six
symmetry families. For each of the other five, a nearest-word marginal is only
a dual witness; every output column, including inactive words, is retained.
Three fixed unsigned distributions on covering rational t intervals let the
comparison be cleared into 48 integer polynomial inequalities. After exact
division by positive (1-t) factors, all 19,474 interval-transformed coefficients
are nonnegative with positive endpoint coefficients. This proves continuum
dominance; a floating grid is not its evidence. The five other complementary
families are strictly separated; noncomplementary equality cases are not
classified. [C67]

C65's unique quadratic scalar optimizer and Gibbs channel consequently
parametrize the unrestricted D_infinity(r) for all 0<r<h_star. The channel's
actual mutual information and distortion vary continuously from (0,1/2) to
(h_star,1/4), covering every intermediate rate. The support transition
enclosures [0.620690001029,0.620690001030] bits/block and
[0.312681553947,0.312681553948] error now describe this unrestricted curve.
The endpoints are D_infinity(0)=1/2 and D_infinity(r)=1/4 for r>=h_star. [C67]

For r=I>0, mix the channel with a source-independent one to obtain I<r and
arbitrarily close distortion. Coding at an intermediate rate fits the rounded
codebook inside floor(k*r) bits for sufficiently large k. Applying a common
supporting bound to all block tables gives the matching converse; no uniform
information allocation is assumed. This handles the exact h_star endpoint
without extra o(k) bits. The decision-word alphabet is an offline codebook
device; the final decoder still receives one child bit after the parent is
discarded. Fixed-length coding and supporting optimization are established
[@polyanskiywu2016coding; @dupuis2004strategies]. The local addition is this
particular complete model curve. Exact finite optima, efficient encoders,
external proof/priority and natural-workflow gains remain open. [C67]

### 8.18 A compact implemented finite code (C68 checkpoint)

The [four-block trellis witness](../research/FINITE_TRELLIS_CODE_2026-10-02.md)
stores k quaternary symbols in exactly 2*k parent bits. A response at block R
uses only its own and two preceding cyclic symbols through three fixed public
64-entry tables. The updater returns the omission bit of that response word;
the final actor returns the child bit without parent/source access. The cyclic
boundary is already the last two parent symbols. Public labels occupy 96
packed bytes, excluding program/runtime size and charged instance memory. [C68]

An exact reverse Viterbi recurrence searches the 16 cyclic boundary states,
with 1024*k branch relaxations at k>=2. At k=4, all 65,536 source assignments
and 3,145,728 delayed routes independently give 867,837 errors, or
289279/1048576, below pair-product 869,376, three-plus-one 869,648 and independent
blocks 884,736. The population assignments use exhaustive nearest-message
enumeration, independently of the Viterbi recurrence. Tests compare Viterbi
against every message for all k<=3 sources and declared k=4/6 examples. [C68]

Repeating independently closed four-block groups gives the same distortion at
every k=4*n by product additivity, with 2*k parent bits and one final child bit.
At common k=12*n, the existing three-block product instead gives lower error
40529/147456. This C68 checkpoint did not improve the best known repeated-code
upper bound; the later C69 construction does.
One long cyclic trellis is different; its smaller k=1,2,3 tables have
58/192,1802/6144,41649/147456 error and lose to existing controls. The certificate
executes 3,299,520 routes including those failures. Bounded post-hoc search
preserves 33 failed initial permutations and four label sweeps with 93 accepted
changes. Neither local/global optimality nor longer-cycle quality is proved.
Generic trellis coding, Viterbi and tail-biting are established precedents
[@marcellinfischer1990tcq; @qtip2024]. This adds a particular finite upper bound
and codec for delayed queries, with no model/natural-task or production gain.
External correctness and publication priority remain open. [C68]

### 8.19 Stronger finite controls and failure of product locality

Four further response-triple replacements refine C59's component to 40,514
errors. Independently accumulated addition/removal losses check all 64*4,096
single-word replacements and find zero positive gains in the fixed unsigned
family. C63's unchanged all-decoder lower bound therefore gives the current
unrestricted interval [40,072,40,514]/147,456. This is a 442-error bracket,
not an exact finite optimum or locality under other decoder changes. [C69]

Write a twelve-bit parent as M=a+64*b. Its right response triple is B[b]; its
left triple is B[a], except for fixed public conditional entries. Changing only
M=3330's left triple to 963 reduces the two-copy product from 331,890,688 to
331,886,587 errors. Exactly one six-block response word changes. A component
locally optimal for single-triple replacements thus need not have a product
locally optimal for single six-block word replacements in this loss. This
does not concern globally optimal component books. Eight conditional changes
give 331,857,648/1,207,959,552=2,304,567/8,388,608 error, approximately27.472579%.
The gain over the refined product is only 0.002735 percentage points. [C69]

An exact encoder minimizes left loss within each right group and then chooses
the best high digit, ties by smallest integer M. The updater selects the R
response word's O bit before J; the final actor returns Z without parent/source
access. Public label payload is 120 bytes:96 for the base and 24 for overrides,
with public count 8. Program/JSON/framing and runtime memory are separate; the
instance cap remains12 bits, followed by one bit. Sixteen relative-left-minimum
groups preserve right choices and tie order. Weighted actor grading covers all
16,777,216 source pairs and 1,207,959,552 outcomes using11,783,592 physical actor
queries, agreeing with independently summed distances and the native search.
The component separately executes all 147,456 routes. [C69]

Independent six-block segments give the same distortion for every k=6*n at
2*k parent bits and one child bit. At common k=12*n this beats the refined
three-block product. It improves these explicit repeated-code upper bounds,
while C67's optimal curve is unchanged. Four initial modal starts and a weaker
joint change fail their controls; all remain preserved. Eight conditional
changes stop at a positive-gain cap, with final six-block locality unproved.
All accepted errors/gains independently rescore; rejected conditional scores
are not all reproduced. Nearest assignment, local codebook tuning and product
quantization are established [@jegou2011product]. The addition is the specific
finite construction and scoped counterexample, with optimality, external
correctness/priority and natural-agent/model/cost benefit open. [C69]

### 8.20 Query-prior allocation, minimax robustness and an early class cue

The [changed-law note](../research/QUERY_PRIOR_TIMING_2026-10-02.md) keeps
uniform iid four-bit sources and uniform omission/remaining-coordinate queries,
but divides k=2n blocks into two public equal classes. A source-independent
fixed p chooses the class, followed by a uniform block within it. Parent cap
is 4n bits and child cap one bit before J. Knowing p before X, designing a
parent without p, and receiving the actual sampled class T before M are three
separate access conditions. In the first two the realized R/O remain late;
source/parent/archive/session/environment rereads remain excluded. [C70]

If p is known, the limiting optimum is

\[
W(p)=\min_{r_L,r_R\ge0,\ r_L+r_R\le4}
       [pD(r_L)+(1-p)D(r_R)],
\]

where D is C67's full unrestricted curve. To obtain the converse, sum block
informations I(X_i;A_i)<=I(X_i;M); independence bounds their sum by H(M)<=4n.
The all-slope decoder inequality and Jensen within each class give the
formula, including joint encoders and heterogeneous tables. Separate class
coding with strict channel-mixing slack fits both rounded codebook indices
and fallbacks inside 4n; no extra o(k) bits or per-instance allocation marker
are assumed. W is symmetric and concave in p, equals D(2) at p=1/2 and is
strictly smaller elsewhere. This is a local consequence of C67 using
established supporting/coding reasoning [@polyanskiywu2016coding]. [C70]

Five rational slope/channel witnesses give exact outward intervals at
p=1/10,1/4,1/3,2/5,1/2. At p=1/4 the enclosure is
[0.257186606420,0.257186606421]. Dual residuals cover every response column,
C67 supplies all-slope decoder dominance, and the two channels have total
information upper bound strictly below 4. Floating discovery does not enter
the numeric proof. A failed initial common-parameter bracket and its
explicitly recomputed record remain preserved. Other p have the analytic
variational characterization; no additional numeric computations or efficient
finite codes near the limit are claimed. [C70]

For unknown-prior minimax U_n, uniform p=1/2 gives D_{2n}(4n)<=U_n, and
separate identical rate-two class codes give U_n<=D_n(2n). Thus lim U_n=D(2),
even if p may be disclosed after M; no finite equality is asserted. If actual
T arrives before M instead, encode only its n blocks' majority signatures.
This uses 3n bits within 4n and gives exactly 1/4 error. T has zero source
information and is recoverable from R, but moving it earlier changes the
encoder's permitted dependence. Late uniform T has limiting excess error
in (0.0118989799,0.0118989801). This timing deduction does not confuse query
statistics with the realized relevance cue. [C70]

At finite length, frozen C69 half-error counts show that its uniform encoder
beats the refined product only for p>59911/152862. Known-prior reencoding of
the same book yields 52 exact affine segments on [0,1], covering 16,777,216
source pairs through a weighted minimum-of-three-lines calculation. Pairing
two C69 components in opposite public orientations instead gives each class
error 2304567/8388608 for every fixed source-independent p. It uses 24 bits
for twelve blocks, one child bit and no orientation instance state; the
120-byte public label payload is shared. Independent pairs extend to k=12h.
These larger-source counts follow from C69 and independence; 589,824 physical
source-free final queries check all local messages/orientations/routes, not
the entire twelve-block source population. [C70]

Named unequal controls use one parent bit per block in one class and three
in the other, reaching p/16+1/4 or 5/16-p/16. The balanced pair beats those
and the refined product exactly for
207415/524288<p<316873/524288. At p=1/4 the simple unequal control gives
17/64 and beats the balanced pair. These three controls are not all finite
allocations or optima. Generic symmetrization, allocation, product coding and
early side information are established; external correctness/priority,
adaptive/within-class query laws and natural-agent/model/cost benefit remain
open. No new model call or prospective natural episode is added. [C70]

### 8.21 An implemented hard-cap entropy code with overflow bounds

The [construction](../research/HARD_CAP_ENTROPY_CODE_2026-10-02.md) returns to
the original uniform iid four-bit source and independent uniform R/O/J law.
Choose a public count a before X. The first a blocks use the eight majority
response signatures 0,3,5,6,9,10,12,15, with source counts 5,1,1,1,1,1,1,5.
The other blocks use constants 0,15 with counts 11,5 and ties at weight two
assigned zero. Their queried-bit risks are 1/4 and 5/16. Only response bit O
becomes the one-bit child before J; four counterfactual answers do not become
four retained bits. Final prediction is Z, with access only to Z,R,O,J. [C71]

Exact arithmetic subdivision gives each response sequence an interval of
length P, its product probability under the fixed public counts. Use odd grid
numerators over 2^(2k), spaced 2^(-(2k-1)). The least contained point has an
index requiring 2k-1 bits; a regular flag takes the remaining bit. If none is
contained, M=0 denotes the all-zero fallback response. Thus 2^(2k-1)+1 usable
messages fit inside the 2k-bit cap. The updater reconstructs the selected
prefix from M and public tables, without source or interval access, and emits
one bit. Fixed response/count payload is ten packed bytes, with k/a, framing,
program and runtime separate. O(k) arithmetic steps on O(k)-bit integers give
polynomial bit complexity, not a linear bit-operation or portable speed claim.
Temporary computation is discarded at each boundary; no provider/session,
archive, source, old parent or diagnostic list is an extra channel. [C71]

Let U~Bin(a,3/8) count balanced majority outputs and V~Bin(k-a,5/16) count
upper constant outputs. They are independent. Any interval at least one grid
spacing contains a point, so failure is contained in

\[
\mathcal B=\{5^{a-U+V}11^{k-a-V}<2^{2k+1}\}.
\]

All-zero replacement has nonnegative per-source excess over the chosen
quantizer, averaged across O/J. Conditional on U=u,V=v, its mean excess is
(18a-8u+36v)/(60k), as calibrated independently over the sixteen source words.
Actual failure may also depend on response order/values; using all of B gives
the safe whole-population bound

\[
\frac5{16}-\frac{a}{16k}\ \le D_{k,a}\ \le
\frac5{16}-\frac{a}{16k}+\mathbb E\!\left[
 \frac{18a-8U+36V}{60k}\mathbf1_{\mathcal B}
\right].
\]

Exact binomial tail masses and first moments evaluate this bound along a
monotone integer frontier. A separate direct-power check verifies every
frontier boundary; small cases also use literal two-dimensional sums. The
bound covers all sources/queries under the stated law without physically
enumerating the larger populations. It is not their exact average risk. [C71]

Put h_2=4-(11 log2 11+5 log2 5)/16 and h_8=4-10 log2 5/16. For
ell=ceil(log2(k+1)), m=ceil(sqrt(k*ell)), the default public schedule selects
the largest a with 5^[5(k+a)]*11^[11(k-a)]>=2^[32k+16m]. This exact integer
test is the mean-information constraint a*h_8+(k-a)*h_2<=2k-m.
Maximality gives a/k -> (2-h_2)/(h_8-h_2). Each information summand has
range below three bits, so Var(S)<=9k/4 and Chebyshev bounds Pr(B) by
9k/[4(m-1)^2] for m>1. This vanishes, squeezing the actual code's risk to

\[
D_{\rm scalar}=\frac5{16}-\frac{2-h_2}{16(h_8-h_2)}
 \in[0.270753014417,0.270753014418].
\]

This is the implemented schedule's suboptimal limit, above C67 and below
the named repeated C69 code's 2304567/8388608. The retained rational schedule
a=max(0,floor(2k/3)-ceil(2sqrt(k))) tends instead to 13/48, but has the
stronger checked finite bound at three lengths. At k=12,288 its risk is at
most 271988910418071/10^15, about 27.198892% rounded upward; the default bound
is 136022316101341/(5*10^14). Both use exactly 2k parent bits. Sixteen bounds
at eight multiples of six prove both schedules lose to C69 at k=96/192/384/768
and improve on it at k=1536/3072/6144/12288. These are inspected bounds rather
than trials or an optimal public-schedule search. [C71]

Complete k=1,2,3 populations for every a execute 608,640 final queries;
twelve constructed large inputs at k=1536/12288 execute another 864 at six
declared positions. The latter are diagnostics, not source-population grading.
Fifteen source/provenance bindings regenerate, preserving original C67/C69
evidence. Generic entropy-constrained quantization and time sharing have
classical precedent [@chou1989entropy]; arithmetic coding is established.
This adds a specific implementable model construction and checked hard-cap
bounds. External correctness/priority, efficient codes reaching C67, broader
source/query laws and natural-agent/model/token/cost benefit remain open.
Zero new model calls or prospective natural episodes. [C71]

## 9. Limitations and open results

The bit-model source values are independent; real tasks have semantic structure, correlated observations, and adaptive actions. The record diagnostics are constructed examples, not independent task samples. The recovery reference assumes reliable access, opaque record selection, a known routing distribution, and a public revision schedule. It excludes archive storage costs and does not optimize natural-language summaries. Source-only model inference has been evaluated only on one inspected classifier; the static control covers three inspected programs and one constructed family without universal certification; an open-ended native-agent benchmark remains unperformed. The one-block exact optimum is a local exhaustive computational result; external review and novelty assessment of the mathematical results, exact finite optima and efficient codes approaching the characterized curves, rate-distortion characterizations beyond the uniform four-bit source and stated two-class source-independent query priors, and the prevalence of the mechanism in real agents remain open. A novelty claim also requires deeper reductions to functional compression and causal coding [@kaspi2013; @functionalcoloring2010; @causalrefinement2019]. The [external review packet](../research/EXTERNAL_REVIEW_PACKET_2026-09-19.md) distinguishes asymptotic graph-coloring results and source-aware refinement encoders from this source-inaccessible updater; no theorem-transfer or priority conclusion is established.

## 10. Reproducibility

The Python artifact contains standard-library invariant tests, exact small-codebook enumeration, compatibility certificates, independent audit formulations, witnesses, deterministic workflow/recovery diagnostics, and an offline pilot schedule. The full four-state partition search has a transparent Python implementation and an embedded scalar C99 backend for practical regeneration; the recorded run used Clang 19.1.0. The normal repository validator checks that backend's source hash, the partition count, declared witness capacity, and every witness outcome; it does not rerun the full exhaustive search by default. Its optional compiler flag reruns and compares the complete search, as done in the correctness audit. It regenerates all smaller diagnostic contents in memory and verifies source/data provenance. Source provenance and the repository migration are documented separately. The offline commands use no model API, network, training, or GPU. Larger experimental claims will require additional artifacts and complete run-level accounting.
