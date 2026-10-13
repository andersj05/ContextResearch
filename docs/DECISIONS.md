# Research decisions

These entries record the working interpretation of the discussion. Dates identify when a direction was adopted or documented, not an experimental result.

| Date | Decision | Reason and remaining question |
|---|---|---|
| 2026-09-16 | Separate output shaping, masking, summaries, opaque compaction, retrieval, and KV compression. | They change different information channels and have different cost models. |
| 2026-09-16 | Focus the first mathematical study on delayed dependencies and successive memory bottlenecks. | Finite encoders allow exact checks; a generic semantic theory is too broad for the first result. |
| 2026-09-16 | Treat the four-bit obstruction as a checked example, not a novelty claim. | Generalization and comparison with classical coding literature remain necessary. |
| 2026-09-16 | Use no archive in the first diagnostic, then evaluate equally metered recovery separately. | Retrieval changes the information constraints and invalidates a naive whole-system use of no-archive lower bounds. |
| 2026-09-18 | Make provider-managed reasoning continuity explicit in the experiment protocol. | Visible history edits can alter opaque state; a comparison must identify what it actually changes. |
| 2026-09-18 | Prefer a practical first intervention alongside supported native compaction. | Test dependency records and timing against a functioning native baseline with total-run accounting. |
| 2026-09-18 | Make `ContextResearch` the paper's working repository and preserve the original folder as a migration backup. | Keep the destination's existing Git history, import provenance, and avoid losing the broader source library. |
| 2026-09-18 | Use plain Markdown for the first drafts, with BibTeX references and an offline preview builder. | Documents remain easy for people and agents to edit; venue formatting can be selected once the paper has a clearer contribution. |

The [September 18 exploratory memo](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md) adds block and leave-one-out dependency families, a local robust-gap derivation, and an action-policy proposal. Its methodological recommendation is to require robustness to nonzero excess error before treating an exact-memory obstruction as practically important. These are research candidates, not a commitment to a model, environment, budget, or paper claim of novelty.

The user authorized a proof audit and one deterministic environment, with frequent commits on `task/` branches. The local audit preserves the block result, adds an analytic entropy lemma, and corrects the leave-one-out domain. Its independent formulations are not independent external review. The first environment will use a small artifact/manifest workflow and declared record budgets and action costs; it will not launch model calls.

The completed deterministic matrix uses five resource/availability settings, eight development seeds, two revision conditions, and four scripted policies. Its 320 configurations are diagnostics. The budgeted inspection rule has a declared two-unit price ceiling, so expensive inspection can trade success for cost; no optimality or cost-normalized superiority is claimed. A separately constructed paired witness restores context and environment and compares retention at equal cost. Source and fixture hashes plus fresh regeneration checks anchor the outputs.

Open decisions at setup: target venue, authorship, final dependency family, exact chain optimum, model for the pilot, spending budget, and power analysis. None was silently fixed by the repository setup; the finite optimum was subsequently computed on September 19 as recorded below.

## September 18: autonomous follow-up and living draft

The user authorized research direction, further investigation, and a short draft to maintain as findings accumulate. Work continues on `task/recovery-frontier-draft`. The focused literature comparison narrows the claim: graph signatures, costed information acquisition, and repeated-compaction evaluation already have close precedents. The next bounded milestone is metered recovery plus an exact finite record-selection reference, followed by a concise findings draft and an updated manuscript. This milestone uses no model services; paid/model-dependent experiments still need their specified protocol.

The completed reference enumerates the whole uniform subset/query distribution, not the eight development seeds. It preserves the existing lexicographically first-candidate revision rule, which creates nonuniform refresh probabilities across job names. It permits randomized policies under an expected incremental action budget and rejects binding per-episode limits; those are different constraints. Opaque atomic record selection, reliable recovery, and complete mandatory workflows define the scope. All four reference endpoints are checked through executable policies. Cheap recovery and a later tight memory boundary can remove inspection's cost advantage; these negative cases stay in the report.

The living findings draft is `paper/findings-draft.md`; `paper/manuscript.md` remains the paper entry point. Both now include the locally audited scaling result and the recovery findings with explicit review boundaries. The chosen next empirical milestone is a frozen pilot specification testing selective inspection against recovery, including null and adverse conditions. There is no model-performance claim or paid-run authorization inferred from the scripted results.

## September 19: staged pilot and exact finite follow-up

Continue the user's authorized autonomous research on `task/pilot-calibration-exact-chain`, committing coherent milestones. The [pilot design](LLM_PILOT_SPEC.md) first isolates inspection decisions using scripted optimal retention, then adds model record selection and inferred dependencies. This prevents a model's retention weakness from being mislabeled as an irrational inspection choice against an optimal-retention reference. All arms have identical reliable recovery; early-failure cost reductions are not success-one savings.

The offline plan reserves six regimes, one development family, four held-out families, disjoint sampled routes, and paired render modes/inspection arms. Its 432-request maximum is a planning ceiling, not spending authorization. Natural-language renderers, an isolated adapter, model revision/settings, hashes, price review, and dollar/token caps remain unfinished. No paid calls are needed to implement and validate these interfaces. The [evaluation source review](../research/PILOT_EVALUATION_REVIEW_2026-09-19.md) informs whole-episode evaluation, discarded diagnostic copies, and separate information-sufficient controls; these are prior methodological ideas, not novelty claims.

The finite chain question proved computationally tractable after reducing parent encoders to unlabeled partitions and optimizing child splits by coordinate-majority decoding. The completed scalar C99 search visits all 171,798,901 four-cell partitions and gives exact error 9/32, with 128 optima. An independent decoder grader checks every witness outcome; native and Python backends agree on small complete instances. Keep the old 49/192 certificate as historical evidence and register the new result separately as C21. The [dated derivation](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md) records the reduction, witness, and computational trust boundary. Routine validation checks the saved native source hash/count/witness; reproducing the full lower-bound computation is an explicit compiler-assisted command. This result does not justify extrapolating a 1/32 gap to joint block encodings or claiming practical LLM gains.

## September 19: correctness audit before model integration

The user's request to check correctness prompted a [scoped audit](../research/CORRECTNESS_AUDIT_2026-09-19.md) on `task/research-correctness-audit`. Fix the witness-capacity and candidate-order validation gaps before new inputs reach these interfaces. Regenerated established outputs preserve their numerical conclusions. Add complete in-memory comparisons for the original diagnostics and an optional read-only full-search comparison; all 65 tests and the full-search validation pass.

Keep the pilot small and explicitly exploratory. Under matched reliable recovery, empty memory still permits successful completion, so use pre-recovery availability and completion cost for retention quality. Record terminal success as execution/schema validity. Require fixed population-reference policies on the same reserved routes, whose realized costs can tie even when population preferences differ. Preserve those ties and the planned sample; do not choose replacement routes to improve apparent separation. One route per family cannot support a family-effect claim. Exclude evaluator IDs that suggest the intended answer from future outbound requests. These decisions refine the unperformed design to v0.2 without increasing its ceiling or launching model calls.

## September 19: development interface and requested subscription route

Implement the development template and allowlisted public requests before connecting a model. Preserve the reserved development route and paired receipt payloads across configurations, renderings, and arms. Keep the observation window and evaluator data outside later requests. Strict validation terminates malformed selections without corrective calls. Reserve attempts before dispatch and retain incomplete pairs. The fake optimal and forget-all controls both succeed through reliable recovery, with different recovery frequencies; these are software controls, not model evidence.

Honor the user's request for GPT-5.6-Luna through the existing Codex subscription. Official CLI sign-in is verified. Do not substitute an API key, apply API pricing to subscription credits, or infer zero cost from available credits. Set the first development ceiling to 96 requests and incremental API spending to zero. The subscription credit bound remains unresolved. The inspected CLI and app-server interfaces have not yet established complete context/tool isolation, provider retry limits, or hard output/charge bounds. Commit a fail-closed preflight and output parser rather than launch an experiment with undeclared channels; there is no bypass switch. This is a dated unresolved transport finding, not a claim that subscription experimentation is impossible.

The development implementation is v0.3; retain the saved v0.2 full schedule as the original planning artifact. The four held-out families are not implemented or evaluated. The [external review packet](../research/EXTERNAL_REVIEW_PACKET_2026-09-19.md) prepares concrete correctness and priority questions and adds bounded functional-compression and causal-refinement readings. It does not represent external review or authorize unsolicited outreach.

## September 19: amended Luna development launch

The user requested the Luna tests. Freeze the [v0.4 transport contract](LUNA_DEVELOPMENT_RUN.md) before generation: existing managed ChatGPT authentication, mutable `gpt-5.6-luna` alias, low effort/default tier, at most 96 attempts and 20 token-derived planning credit equivalents, zero API billing, no purchases or resets. The first request is also the connection diagnostic. New threads and processes exclude experiment history; fixed reviewed global instructions and three wrappers with no external tools are declared background. The installed-client loopback audit checks final responses, attempted tools, HTTP errors, and broken streams; all make one local POST. Verify all 45 effective configuration values before dispatch. A weighted rollout guard prevents a second generation; accept only the audited controlled `sessionBudgetExceeded` termination with a complete JSON decision and valid usage, retaining the actual harness status. Remote internals and actual invoice attribution remain unobserved.

Freeze only the implemented development template and original route for this tranche. Held-out renderers must be completed and frozen before a separately specified held-out launch; their absence does not block the user's requested development debugging. Preserve source hashes, attempted failures, incomplete pairs, and credit reservations. These choices do not establish native-harness gains or general superiority.

## September 19: first Luna tranche completed

The [saved run](../experiments/dependency_memory/results/luna_development_2026-09-19/report.md) exhausted its allocation at exactly 96 valid model requests, with 12 calibration decisions and 36 completed development episodes. There were no transport/schema failures or retries. Preserve both revision-cell calibration disagreements: exact reference agreement was 10/12, total expected excess cost 4/5 synthetic units. Stage-B availability was 21/36 and recovery occurred in 15 episodes. Never/always/selective arms cost 154/140/137 synthetic units on the single reserved route; these are descriptive realized totals, not population effects. The one-child selection differences can be equally good population tie-breaks. Use the public revision rule and the observed parent selections for the next offline investigation; do not infer the model's private reasoning.

Record 276,048 input and 27,140 output tokens, 2.5395 conservative credit equivalents, and unknown attributable subscription debit. Optional cache-write zeros are local defaults for an unavailable counter, not observed proof of zero cache writes. No API billing, purchases, resets, or held-out requests occurred. The [independent analysis](../research/LUNA_DEVELOPMENT_FINDINGS_2026-09-19.md) checked all 36 final availability/cost outcomes and 120 discarded-token exclusions. Offline saved-artifact validation checks manifest/request hashes, counts, and credit arithmetic; historical source hashes remain pinned rather than forced to match later edits. A new model tranche needs its own explicit budget and frozen manifest. External review and novelty remain open.

## September 19: revision-aware parent selection

The user requested the next focus. Analyze saved parent choices under their actual public views before collecting further data. The [exact offline grades](../experiments/dependency_memory/results/revision_analysis_report.md) find three strict parent deficits among 36 choices, all in uninspected revision cases; all observed child choices are conditionally optimal. Do not grade an inspected response over unseen manifests or call symmetric tie-breaking an error. A simple pair formula explains the asymmetric value of records when the lexicographically smaller candidate will be refreshed.

Prepare a separate [24-request diagnostic](REVISION_DIAGNOSTIC.md): first/last/no refresh crossed with four reversed-pair visible orders and two fixed token fixtures. No candidate or target is drawn. Declare an optimal child, grade every answer over all 30 routes, and retain canonical metadata/schema ordering as a known channel. This is post-pilot development, not a held-out or unchanged-prompt replication. Five fake controls and a separate installed-client loopback audit validate the setup without model calls. Propose a new 12-credit-equivalent cap; unused headroom does not renew the exhausted 96-request allocation. The new live runner requires an explicit allocation note and cannot resume an output directory. Correct future metadata so an unreported optional cache-write counter is unknown, while preserving the original run and its historical default-zero caveat.

## September 19: continued offline preparation and response accounting

Continue the user's research request with a bounded [held-out clue milestone](HELDOUT_RENDERERS.md) and an independent local review of the prepared revision diagnostic. Keep the existing 96 responses and reserved routes unchanged. Implement the four reserved families in a separate offline semantic module, with explicit and inferred forms and full candidate-pair coverage. Record static catalogs as public side information; selected clues still require boundary deletion in the future adapter. Freeze the semantic checkpoint without describing it as a complete live-launch manifest. Catalog sizes differ and the one-route-per-family sample remains confounded. This milestone establishes software properties, not a new model outcome or a novelty claim.

The local review found two prospective reporting defects. Missing optional cache-write usage was correctly unknown in the outer provider record but imputed to zero inside nested budget accounting; preserve unknown consistently while leaving conservative total-cost arithmetic unchanged. A complete, charged answer with malformed JSON was being treated as a transport failure; classify it as a policy failure and continue the prespecified schedule, as for other invalid outputs. Genuine transport failures or uncertain usage still stop the tranche and retain the required reservation. Test both paths without model calls and preserve historical artifacts. The separate 24-request allocation remains pending explicit confirmation; continued offline work does not spend it.

## September 19: explicit revision-diagnostic allocation

The user subsequently answered **"Yes—authorize the capped 24-request run"** to the explicit proposal for at most 24 Luna requests through the existing subscription, capped at 12 conservative credit equivalents, with no API billing, purchases, or resets. This is a new bounded allocation, separate from the completed 96-request tranche. Freeze launch code at `aa6c0e5`, preserve the 24 original public requests and their schedule, and record the allocation in the manifest before dispatch. Use the prepared first/last/no-refresh diagnostic only; no held-out launch, repair prompt, or answer-dependent change is authorized by this allocation. All outcomes and uncertain reservations remain in the saved evidence.

The [completed run](../research/REVISION_LUNA_FINDINGS_2026-09-19.md) returned 24 valid, full, optimal selections with no failures. All eight first/last pairs switch between the two rule-specific optimal sets. No-refresh always chooses the lowest two keys, which is an optimal tie. Record 66,200 input and 5,651 output tokens, 0.58328 conservative credit equivalents, zero uncertain reservations, and unknown attributable subscription debit. Explicit zero cache-write counts were reported in all 24 requests. The two completed request allocations total 120 calls and 3.12278 conservative equivalents; unused headroom authorizes no further calls. Preserve the positive result without calling it a fix for the earlier three deficits: prompt framing and the guaranteed later selector differ. The next behavioral comparison should isolate those changes on matched inputs before spending more. Rank shifts and paired regret are algebraically redundant for these full two-record outputs.

## September 19: larger matched retention study authorized

The user explicitly permitted thousands of further Luna requests and asked us to continue. Implement that broad authorization as a fixed new allocation of 1,536 requests across 32 blocks and 48 conditions, four concurrent serial workers, and 200 conservative credit equivalents (50 per worker). Reuse the existing subscription without API billing, purchases, or resets. The two completed runs remain immutable. No further permission question is needed for this bounded study.

Freeze the [transfer protocol](TRANSFER_STUDY.md), public requests, code, and new installed-client loopback audit before model calls. Randomize public refresh priorities independently of key names and record order; keep block materials paired across framing/context, later-selector guarantee, guidance, size, and refresh conditions. Canonical metadata/schema ordering remains a declared channel. The primary analysis is generic minus prospective normalized optimal-child-reference regret in workflow/unspecified/refresh-present cells: 128 pairs in 32 blocks. Report raw regret by size, policy failures, missing coverage, and a complete-block estimate with its descriptive bootstrap interval. Keep no-refresh ties outside the primary superiority comparison. A ceiling or null result remains a legitimate result.

Each worker has its own reservation ledger; a shared gate stops all new dispatch after transport or accounting uncertainty while allowing in-flight calls to settle. No retry, repair, resumed output directory, prompt revision, or outcome-dependent extension is allowed. Preserve source-commit provenance and independently re-enumerate every saved selection. This is an isolated early-retention/context-envelope study: the later selector is untested and its two-record capacity is nonbinding. It cannot demonstrate repeated-compaction gains, a natural-task benefit, or a fix for the first workflow's errors.

## September 19: zero-generation quota stop and operational correction

The frozen `999f14d` launch reached four preflight account checks and stopped with `quota_guard_80_percent` before any model dispatch or credit reservation. Preserve the complete stopped run and independent audit under `transfer_luna_2026-09-19`; its 1,536 scheduled rows are missing outcomes, not failed model decisions. A fresh read-only account check reported ordinary usage allowed, 85% weekly use, and existing credits. The 80% stop was our historical reserve policy, not an exhausted provider allowance.

Apply the user's explicit broad usage authorization by changing only this study's local quota threshold to 100% used; the earlier runners keep their 80% default. Provider usage denials, reached limits, account/individual spend controls, uncertain accounting, and the 200-equivalent aggregate cap remain binding. Do not purchase credits or redeem resets. Re-freeze the operational change and use a fresh output directory, keeping the original 1,536 request bytes, seed, schedule, scoring, and analysis unchanged. Because no model prompt was dispatched, this correction does not selectively replace an answer or add a generation beyond the allocation. Record the new threshold in transport metadata and retain failed quota snapshots prospectively.

## September 19, 2026 — preserve a quota-stopped phase and finish only untouched cases

The `0414198` transfer phase stopped at its local 100%-used guard after 888 dispatches. It retained 885 valid answers; three fully metered post-quota answers were not saved and remain failures. A fourth preflight attempt dispatched nothing. Independent evidence and accounting audits pass: 28.25661250 conservative equivalents, zero uncertain reservations. Fresh account telemetry still reported ordinary usage allowed, no reached-limit classification or spend control, and existing credits.

Under the user's existing authorization for thousands of Luna requests, adopt the [separate operational continuation](TRANSFER_CONTINUATION.md). A certificate identifies only 648 never-dispatched cases and subtracts prior charges from each original 384-request/50-equivalent worker allocation. Preserve public request bytes and order, model settings, primary analysis, original 1,536-request/200-equivalent aggregate ceiling, and all historical evidence. Never repeat or replace a dispatched outcome. The new opt-in quota policy uses the same subscription route with fresh included/credit evidence; actual provider rejection, hard spending/depletion limits, or transport uncertainty stops dispatch. No purchases, resets, API fallback, or outcome-dependent extension is authorized. Freeze and audit the new phase separately; report administrative interruption and any missingness in pooled findings.

Preparation at `cfa1ba9` incorrectly required a raw offline audit to be launch-ready before client attestation and exited with zero provider clients or generations. Preserve that record. The correction at `f9012a2` checks the raw request contract first and still requires verified client readiness before execution; the regression uses the actual saved offline audit. Successful provider admission subsequently began the remaining-case phase. No case was repeated or replaced by this preparation correction.

## September 19: fixed transfer study completed and audited

Close the [transfer study](TRANSFER_STUDY.md) at its prespecified 1,536 unique model requests, 32 blocks, and 48 conditions. The [final pooled evidence](../experiments/dependency_memory/results/transfer_luna_2026-09-19_continuation/report.md) contains 1,533 valid selections, 1,422 optimal selections, and three permanent missing answers from the original phase's fully metered transport failures. No missing answer falls in the primary comparison. The continuation completed all 648 eligible first submissions without policy or transport failures; no dispatched case was repeated, repaired, or replaced. One valid empty no-refresh selection accounts for the sole underfill and sole no-refresh deficit; all full no-refresh pairs tie. Preserve all 111 strict deficits and the original failures.

The complete primary sample has 128 matched pairs in 32 blocks: generic guidance is optimal in 114/128 and prospective guidance in 118/128; regret favors prospective guidance in 13 pairs, generic guidance in nine, and ties in 106. The frozen normalized regret benefit is 107/5120, with descriptive 95% block-bootstrap interval [-0.0203125, 0.060546875]. The interval includes zero, so record **no confirmed benefit** and do not present prospective advice alone as a demonstrated solution. Keep the prespecified raw benefits by size (-7/1920 for six jobs; 71/8448 for twelve) and all condition counts, without adding significance claims or inferring a private reasoning mechanism from overlapping key-choice patterns.

The [independent final audit](../experiments/dependency_memory/results/transfer_luna_2026-09-19_continuation/independent_audit.json) verifies saved request identities, independent route grades, source hashes against frozen Git blobs, and pooled accounting. Preserve `999f14d` as a zero-generation quota stop, `0414198` as the 888-dispatch phase with three lost answers, and `f9012a2` as the separately frozen 648-dispatch continuation. There were 1,541 host attempts across the saved phases, 1,536 model generations, 48.78528000 conservative credit equivalents out of 200, and zero uncertain reservations. Actual attributable subscription debit remains unknown. The continuation used the existing-subscription route under the declared credit-backed quota policy; no API billing, purchases, resets, held-out calls, or outcome-dependent extension occurred. The earlier 96- and 24-request studies remain separate historical allocations.

The next design may test a binding downstream bottleneck, an executed later-selector policy, and more naturalistic workflows or the reserved held-out clue families. Those experiments have not been performed. First specify and validate their information-access contract, controls, scoring, provenance, and bounded allocation offline; completing that preparation does not automatically launch further model calls. The finished study's nonbinding child capacity and isolated atomic-record decisions cannot establish repeated-compaction gains or native-harness superiority, and none of these empirical findings changes the mathematical proof scope.

## September 21, 2026 — joint coding before another model allocation

Under the user's authorization to begin the next research phase with novelty as a requirement, pursue a specific open mathematical question first: whether the one-block 9/32 loss persists under joint encoding. The completed guidance study remains a null/uncertain primary result and its nonbinding child does not test repeated compression. Do not silently reuse its exhausted allocation. No model calls, external messages, or remote publication occur in this phase.

The [new derivation](../research/JOINT_BLOCK_CODING_2026-09-21.md) supplies three results: a 16-state two-block witness with 1698/6144 = 283/1024 error; a rational test-channel upper bound 101/384 on asymptotic error at rate two; and the threshold 4-(5/8)log2(5) for vanishing excess error, including the hard-capacity endpoint. Preserve the old 3k exact-attainment result and all-k positive gap. The finite witness disproves unchanged extrapolation of 1/32, but does not compute the two-block optimum. The asymptotic test channel is an existence argument, not an implemented finite encoder.

Use standard-library exact arithmetic and independent formulations to check the finite outcomes and rational information identity. Update claims C31-C33, manuscript, living draft, bibliography, and reading guide together. The source comparison identifies established coding machinery and a close hypergraph cascade formulation; it does not establish publication novelty. The next mathematical target is a tighter rate-two converse with arbitrary decoder pairs. The binding-child behavioral follow-up remains an offline design task until its information contract and new bounded allocation are specified. Work is on `task/joint-block-coding`.

Place the new mathematics in a separate `experiments/dependency_memory/joint_coding` package: historical revision and transfer plans fingerprint the parent's top-level Python files. Initial validation exposed this coupling. Moving the unrelated code preserves both old offline plans and all completed-run artifacts unchanged, without relaxing the fingerprint checks or regenerating historical evidence.

## September 21, 2026 — certify every decoder before claiming a sharp frontier

The user authorized the next research phase with novelty as a requirement. Pursue the open rate-two converse from the current handoff. Keep every legal final decoder: 36 unordered pairs per branch including repeats, hence 1,679,616 tables. Reduce by all 384 source symmetries and verify disjoint coverage plus an independently formulated Burnside count. Potential child decisions form a strategy alphabet; the information converse permits joint parent encoding and different tables or allocations across blocks.

Exploratory floating-point calculations identify a candidate near 0.261898979908. Certify only a rigorous interval using fixed rational witnesses, integer dual products, and outward rational logarithm bounds. The [completed proof](../research/DECODER_COMPLETE_FRONTIER_2026-09-21.md) establishes 0.2618989799 < lim_k D_k(2k) < 0.2618989801, with the lower endpoint valid for every k. Do not call the enclosure a closed form, statistical confidence interval, finite practical encoder, or LLM effect. The near-matching upper bound uses an explicit rational test channel and standard asymptotic coding with small positive rate slack.

Retain standard-library reproduction in the joint_coding subpackage, preserving historical top-level source fingerprints and all model-run evidence. The global validator regenerates this certificate. All 270 tests pass; the validator reports no errors; the manuscript builds with 23 cited sources. New literature review attributes strategy alphabets and dual optimization; the candidate contribution is the specific sharp, unrestricted composition penalty. External correctness and publication priority remain open. No model requests, paid allocation, external messages, or remote publication. Work is on task/decoder-complete-frontier. Next prioritize finite-length constructions and structural results across rates rather than more digits.

## September 21: pivot to compaction collision certificates

The user requested a substantive new direction rather than further tightening
the four-bit example. We built a finite auditor for a proposed retained state:
group exactly equal accessible channels, optimize adaptive read-only recovery,
check lower obstructions independently, and synthesize the smallest extra
message alphabet valid before a future task is revealed. The
[research note](../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md) records the
12 constructed specifications, assumptions, source comparison and kill criteria.

The novelty candidate is the compaction-specific audit protocol, not summary
repair, typed commitments, state abstraction, hypergraphs or dynamic programming.
The new source readings include direct precedents for those concepts. No model
launch was made, and no prior completed allocation was reused. Historical code
fingerprints remain intact because new Python lives in a separate subpackage.

Prioritize a sound execution-task adapter and a reproducible failure/repair at
matched total cost. Exact prose collisions may be too rare; inferred equivalence
is a separate research problem. Further forced compaction during rescue and
state-changing tools are outside the implemented solver. Keep those limitations
visible, retain the existing mathematical results, and deprioritize more decimal
tightening as the main research activity.

## September 22: feedback before forgetting, with a strong negative control

The user asked to pursue the feedback-loop direction intensively. Build an
execution-graded adapter over the existing receipt environment in a separate
subpackage, preserving all historical source fingerprints and model evidence.
Use eight explicit worlds, six public continuations, two record-memory boundaries
and costed final recovery. Derive accepted actions by restored terminal execution;
keep actual retained/public channels exact. No model calls or external messages.

The [completed loop](../research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md) preserves
verified unsafe-group constraints, not only the latest failure. It repairs the
main weak schema from 32/48 to 48/48 executions in three audits, while last-only
repair cycles. The strong critical-field baseline also achieves 48/48 in one
audit and matches the same 18 feasible contracts across the 48-contract sweep.
Record this as a negative control against practical superiority. Do not describe
fewer audits than enumeration as a full compute or economic gain.

Make the scope of family exhaustion explicit: a deliberate record-identity code
supports four binary source states in one tagged record. This finite public-
catalog construction invalidates an unrestricted one-record impossibility claim,
while ordinary receipt submission on it still fails half the outcomes. Add late
oracle feedback and partial-probe controls. Feedback packets, selected identifiers,
public catalogs and decoder code are information channels when they depend on
instance values. Two boundaries precede final rescue; no further compaction occurs
during rescue. All interfaces are trusted Python, not process isolation.

The [new primary readings](../research/FEEDBACK_PRIOR_ART_2026-09-22.md) include
WiCER's cumulative constraints and Appendix I limitations, Memento's specific
judge feedback, and established CEGAR/POMDP refinement. Generic feedback and
remembering prior failures are not novel. Record claims C37-C39 and the strong
baseline tie in the manuscript, living draft, status and claim register together.
The [next-stage design](FEEDBACK_RESEARCH_PROTOCOL.md) requires opaque-payload,
execution-graded snapshots and equally informed controls before model spending;
model revision, transport, sample size, seeds and allocation remain unfilled.
Work is on `task/feedback-compaction-research`.

## September 22: test novelty by reduction, not terminology

In response to the user's request to continue and assess novelty, read closer
primary precedents and explicitly reformulate the existing finite algorithm.
The [novelty memo](../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md) shows that
bounded recovery policies form an accepted-strategy relation. Downward closure
then makes minimum additional-state repair exactly weak coloring of minimal
unsafe groups. Preserve the distinction from strong coloring and from sources
whose hyperedges denote safe groups. Import no asymptotic source-coding theorem.

The new `novelty_audit` subpackage independently composes forward strategies and
searches color assignments. It checks 7,203 subset/budget cases and 1,029 small
colorings on the existing domain, plus the 12 original fixtures. This extends
verification rather than creating new independent tasks. Keep historical modules,
fingerprints, observations and model allocations unchanged. Claim C40 and living
draft v0.14 record the conclusion together with the manuscript and current status.

Do not claim novelty for generic feedback, cumulative constraints, pre-commit
validation, executable counterexamples or the present finite optimizer. Self-GC's
structural rehearsal must not be misrepresented as exhaustive semantic checking.
The remaining candidate systems contribution needs sound evidence extraction,
appropriate invalidation/reuse of checks and measured utility at matched total
costs. If simple critical-field retention continues to match it, report that
result and evaluate the auditor as a diagnostic tool. No new model calls or
external communications were made.

## September 22: real workflow evidence and cheap checked receipts

The user requested sustained work on concrete delayed failures and repairs that
improve outcomes at the same total cost. Work on
`task/real-workflow-memory-replay`. Mine the last two attempts from each worker
of the completed transfer phase, including four successful controls and four
failed-status records. Keep source files and historical launch artifacts intact;
record hashes and selectors instead of duplicating raw session logs.

The [historical replay](../research/HISTORICAL_WORKFLOW_REPLAY_2026-09-22.md)
separates three already dispatched failures from one preflight stop. Status-only
retry/hold plans have concrete delayed errors. Impose two byte boundaries and
meter exact canonical transfers, checks, repair, retrieval and unsuccessful work.
Retain named fields, compact fields and direct checked receipts as equally
informed baselines. Enumerate all allowance thresholds as well as the fixed
180-contract grid; do not choose a favorable budget and hide other regimes.

Checked receipts preserve the required identity/dispatch/accounting result more
compactly than all checker inputs. At one explicit synthetic resource envelope,
repair completes 24/24 routes versus 18/24 compact fields, including full archive
recovery. Direct receipts achieve the same outcomes more cheaply and never lose
to repair in the grid. Prefer this simpler mechanism for subsequent development.
The 17 wins and 30 losses against compact fields reinforce that repair is not a
universal default. Add scope controls for changed evidence, field presence,
request identity and checker revision, charging the current-evidence read.

The records were inspected, the routing/compactions are counterfactual, and the
prices are synthetic. Do not attribute historical transport failures to memory,
call the routes independent trials, claim native-agent gains, or equate byte
prices with dollars. The next evaluation must freeze a different workflow's
obligations before developing its extractor and compare indexed recovery. No
new model launch, allocation, purchase, reset or external message occurred.
Claims C41-C43 and living draft v0.15 record this bounded milestone together.

## September 22: new GPT-6 Luna medium calls

The user explicitly requested new model calls with GPT-6 Luna at medium reasoning.
Create `task/luna6-delayed-repair` and a separate
[release-gate pilot](../experiments/dependency_memory/luna6_revision/CONTRACT.md).
The frozen launch is `136d589`, with 117 scheduled requests inside a separate
144-request/20-planning-credit allocation. Do not reuse historical launch limits,
change the requested model, add automatic retries, or route through API keys.

The installed client is `codex-cli 0.155.0-alpha.16`. A no-generation managed-login
preflight confirms the exact model and medium effort. Unlike the older client,
this version serializes ordinary top-level wrappers and separate base instructions;
code-mode-only plus explicit namespace settings remove visible skill tools.
Authoritative nested-tool metadata is absent despite the resolved setting, so
the audit does not certify an empty hidden registry. Fresh processes, exact
public input checks, a one-generation guard, and rejecting any live tool item
define the accepted-response contract. Four mock failure/success controls pass.
No credential values or uncontrolled reasoning logs are saved.

Freeze the workflow, information order, grader, memory limits, baselines, and
cost accounting before answers. Structured and prose Luna summaries face two
byte limits. Repair and direct serialization share the same compact dependency
representation; the direct control tests whether the proposal calls are wasted.
Indexed recovery and full-history access receive separate cost accounting. The
adapter is manually specified for one executable gate, and tasks are constructed.
Only score after completing the fixed schedule; a positive result or publication
novelty is not assumed. Record clipping separately from semantic omission.

Current published Codex Luna rates have no separate cache-write charge. Meter
input, cache reads, output including reasoning, every memory-writing call, and
failed decisions. Persist a complete metered answer before any subsequent quota
gate, correcting the historical answer-loss pattern in the new adapter. Account
debit and unknown infrastructure costs remain distinct from planning credits.
The [scope/pinning reading](../research/LUNA6_SCOPE_PRIOR_ART_2026-09-22.md) keeps
close precedents and the unresolved novelty question explicit.

The fixed pilot completes 117 calls for 1.1282525 planning credits. Structured
memory obtains 8/16 exact decisions with one unsafe simulated release; checked
replacement obtains 16/16 at 8.9% lower model cost. Direct dependency rows,
indexed recovery and full history each obtain 16/16 more cheaply than repair.
Retain the strong-control result; do not promote the repair loop as optimal.

All four structured child proposals are clipped, so test the baseline weakness
before interpreting its failures as semantic loss. Freeze a 24-call data-first
prompt control in `8d8a358` and carry forward the original request/credit counters.
This adds no checker or archive. It completes with zero clipped memories but
12/16 correct decisions, at 0.1908300 credits; role and identity corruption remain.
Report the prompt package as post-pilot development on reused histories.
The combined allocation ends at 141 calls and 1.3190825 planning credits; three
unused request slots do not justify further launches. Preserve both original
launch sources and all failed decisions. The next useful test is an inexpensive
automatically extracted identity/role contract on an unseen workflow, with its
extraction cost included and direct/indexed/full controls retained.

Final validation for the live-study milestone: 334 tests pass, the repository
auditor reports PASS with no errors and reconciles 141 new requests/112 terminal
decisions, and the manuscript builds with 34 cited sources. The branch remains
local; no pull request, external message, deployment or publication was made.

## September 22: annotated-schema checks on newly frozen traces

The user requested two cheap automatic checks for exact identifiers and scoped
relationships, separate development/evaluation cases for retry, CI handoff and
multi-stage data jobs, and a matched-budget comparison with strong prompting,
direct records, indexed recovery and full history. No suitable untouched traces
were present; the user explicitly selected new frozen traces. The terminal
grader and six evaluation cases were committed before the extractor. Their
values are held out from development, while their annotated schemas and
obligation families are shared. Do not describe this as transfer to unseen
schema structures or real production traces.

The generic extractor reads schema-provided opaque-ID, reference and ephemeral
annotations, projects scalar tool-result fields, and checks exact ID values plus
owner/path/reference triples across both byte boundaries. It does not validate
unannotated status fields or arbitrary model prose. The automatic arm verifies
its own deterministic projection; it is not a test of repairing a model-written
summary. Development mutation controls detect ID corruption and role
reassociation. Frozen implementation `75ab94f`, protocol `284405d`.

All 72 fixed GPT-6 Luna medium calls complete for 0.5510905 planning credits.
On 12 paired terminal cases, all five arms succeed 12/12. Automatic records
match hand-written direct outcomes and are cheaper than the 24-call strong
prompt pipeline, but direct and indexed controls remain cheaper. The primary
criterion of fewer failures at equal or lower cost fails because the strong
prompt has zero failures. Preserve this negative result; do not tune or extend
the evaluated set after seeing it. The live Windows process timer quantized
local work to zero, so a separate post-run high-resolution development-trace
calibration supplies only a cost sensitivity. The synthetic local prices and
unknown subscription debit preclude a fully measured production-total-cost
claim. Claim C47 records the limit.

## September 22: prospective new-schema transfer and model-proposal check

The user asked to keep pursuing cheap automatic survival checks after the
annotated-schema tie. Freeze different development and evaluation schema
structures, an exact terminal grader, and a 126-call/10-planning-credit ceiling
before implementing the generic detector or seeing evaluation responses.
Casebook/protocol commit `7067963`; implementation commit `649bbc9`.
Evaluation schema definitions were visible in that frozen casebook. Treat the
split as prospective at the response level and different in structure, not as
a blind unknown-schema holdout for the implementer.
The generic mechanism may infer ID roles only from ordinary schema/result
signals and must return unknown on ambiguous short strings. Preserve exact
detected IDs and owner/path associations; do not claim a state or execution
certificate. Charge both hypothetical prompt methods fully for their shared
actual parent call. Use the high-resolution local elapsed timer and declared
synthetic byte/second prices. No evaluation-driven tuning or restart.

All 126 scheduled calls complete. The prespecified automatic-direct comparison
meets its narrow success criterion: 1/18 failures versus 2/18 for prompting at
lower total experimental cost, with no more errors than hand-written direct.
Retain the stronger negative control: indexed recovery has 0/18 failures at
lower cost and dominates automatic direct under the declared accounting.
All model-written parent memories are prose and fail the table-only check;
checked fallback does not improve the error count. One automatic final response
misidentifies a correctly retained output dataset. Do not present this as a
general prose checker, an execution guarantee, production cost superiority,
or publication novelty. Claim C48 and the focused research note preserve the
specific paired failures and caveats.

## September 22: cross-record dependency and projected recovery test

The preceding indexed control recovered one complete nested workflow record
after the target was disclosed. To test the same obligation when its evidence
is split across results, freeze seven interleaved workflows per trace with a
root and one separate result per component, joined by an exact opaque
`workflow_key`. Keep the earlier escrow/package families for development and
retry, CI-promotion and data-pipeline families for twelve evaluation traces.
This is a constructed stress test using known domain grammars, not external
held-out traces. The user authorized newly frozen traces and a larger bounded
model allocation.

Freeze the protocol and development cases at `17d56a6`; freeze the generic
join/check, direct baseline, eight-arm runner and analyzer at `b7f7740`.
Derive four evaluation seeds per family from the full implementation commit,
then freeze the twelve fixture hashes at `dbaa6fd` before any model response.
The primary comparison requires automatic retention to improve on both strong
prose and unvalidated structured prompting at no greater experimental cost,
match or beat hand-written direct records, and remain nondominated by an
indexed control that retrieves and projects every related result. The fixed
348-call schedule has a 356-dispatch and 50-planning-credit ceiling. Charge
index construction, storage, recovery, projection, every writer and final call,
local work, reads and writes under the declared synthetic prices. Use an
independent executor diagnosis for structured retained memories. Do not change
the schedule, prompts, caps, code or cost weights after the implementation
freeze.

The original process stopped after 199 dispatches: 198 completed and one
CI projected-index final call with a provider generation error and unknown
usage. Preserve it as a permanent missing answer, and leave the original
36-pair primary criterion unassessable. Freeze a separate plan at `f448e2c`
for only the 149 never-dispatched identities, hashing all original evidence
files. Freeze its no-retry controller and analyzer at `258803e`. This is an
exploratory post-stop extension, not a quiet resumption of the original
preregistration. It completes all 149 new calls without another provider
error; the combined ledger has 347 metered answers and one permanent gap.

On the 35 fully answered pairs, automatic direct has 7 exact failures versus
3 for strong prose, 6 for structured prompting, 4 for hand-written direct,
and 1 for indexed raw full-workflow recovery. It costs less than prompting
but is dominated by direct and indexed raw under the declared synthetic
total-cost model. All 36 automatic tables are sufficient when a deterministic
reconstructor applies the frozen terminal rule, so the seven errors are final
model interpretation errors, including one simulated unsafe publish. Do not
claim the candidate contribution or a matched-budget gain. The checked arm's
18 errors include six traces where its parent ID check accepts legitimate
repeated component join-key columns but its child decoder rejects them and
deletes memory. Record this as a concrete implementation mismatch requiring
a new, prospectively frozen version; do not rescore the current evaluation.
The focused note and claim C49 retain the costs and remaining limitations.

## September 24: compose parent certificates with the child decoder

The latest cross-record result exposed a software mismatch, not evidence that
the proposed checking mechanism works or fails in general. Preserve the v1
implementation and all frozen model evidence. Add a separate v2 compatibility
check that rejects unsupported parent columns, validates public schema
types/enums, selects by the root owner field, and proves all possible
two-candidate child tables fit before source deletion. If a model proposal
fails, project from still-available source evidence and certify that fallback;
otherwise declare infeasible. Do not silently turn this post-hoc fix into a
rescore of the original checked arm.

The saved-parent replay checks twelve proposals. Nine pass the old ID check;
three pass v2. Six old-pass parents are newly rejected for unsupported fields.
All twelve admitted parents support 252/252 possible two-owner child handoffs
after fallback. This tests decoder reachability, not terminal success or
cost superiority. A schema-valid but wrong state still passes the certificate.
Claim C50 and the [focused note](../research/DECODER_COMPATIBILITY_REPLAY_2026-09-24.md)
record the scope.

Prioritize a frozen externally observed executable workflow for the next
empirical study. Keep direct checked receipts and raw indexed recovery as
strong controls, and specify any terminal action guard separately. Do not
spend new model calls repeating the known constructed grammars as if they
were independent evidence. No new model allocation is made by this decision.

## September 24: audit the certificate's implication, not just saved examples

An added long-prose source field with a short proposed replacement exposes a
parent-pass/child-fail counterexample at branch commit `9442d73`. Require the
actual child check for every possible owner pair before accepting a parent;
table selection and byte capacity alone do not establish compatibility.
Reject malformed proposals before admission and preserve the frozen v1 evidence.
The regenerated saved-parent replay is unchanged and is now checked by the
repository validator as well as unit tests. A missing-state negative control
passes both certificates, so compatibility must not be described as semantic
sufficiency. These fixes are software correctness work, not a new empirical
milestone or a reason to repeat model calls on inspected cases. The next
empirical gate remains an externally observed workflow with a frozen executor.

## September 29: freeze a concrete evaluation packet before another model study

The user requested the evaluation packet proposed after reviewing the negative
cross-record comparison. Use the repository's actual validation/build workflow
as a development capture and a narrow executable reporting task. Freeze the
terminal rule, five comparisons, two byte caps, exact prompts, practical go/no-go
margins and proposed 144-call / USD 20 ceiling in the
[packet](../experiments/dependency_memory/workflow_eval/PROTOCOL.md).

The grader must read complete raw receipt metadata independently of the memory
method and reject stale revisions, superseded successes and mismatched build
artifacts. Preserve an easy case where direct records fit comfortably. Do not
tune caps to manufacture a candidate advantage. The observed clean source is
`40cec05`; the three validation commands passed. Their saved stdout/stderr and
capture driver are controlled evidence, not an uncontrolled session transcript.

This single known local capture is development evidence only. Test mutations
are synthetic controls. Twelve uncollected episodes are not a held-out dataset,
and the design freeze is not a live-launch contract. No model calls or spending
are authorized by this packet. Collect/split actual change tasks, implement and
freeze the arms and isolation/cost contract, and obtain independent grader
review before launch. Keep execution guards separate from memory effects. No
new paper claim, novelty claim or provider behavior claim is added.

## September 29: run a separate Luna 6 development comparison

The user explicitly authorized live tests with Luna 6. Preserve the offline
packet and its pending real-workflow intake. Freeze a separate 36-call comparison
on the one observed local capture plus three labeled synthetic continuations.
Do not substitute those controls for the uncollected held-out episodes. Use
the existing subscription, exact `gpt-6-luna` alias and medium reasoning; no API
key, purchase or reset. The USD 20 proposal is not converted into credits: this
development launch uses a separate 20-planning-credit ceiling, reserving 7.65
before each single in-flight call. The current user instruction authorizes it.

The installed client changed serialization, so the old audit rejected the
payload before generation. Add a separate audited profile for CLI
0.158.0-alpha.2.1, preserving all historical code. Pin its full visible
wrapper/clock registry and messages, check four no-auth transport controls at
the largest public request, and freeze implementation and schedule at `ef31373`.
No changes to frozen code, prompts or conditions followed the first model call.

All 36 calls complete for 1.0105070 token-derived planning credits. Four methods
score 4/4 and prose scores 3/4; direct records are cheapest in both cache views.
Retain that unfavorable comparison for the candidate method. Checked fallback
repairs two syntactically invalid child memories but adds no success over direct
records. Prose unnecessarily requests repository work despite retaining the
correct successful receipt. Preserve all answers and make no retries. Claim
C51, the manuscript and living draft record these bounded development findings;
untouched real workflows, independent external grader review and production
total cost remain open.

## September 29: execute controlled workflows with narrow query scopes

The user authorized further experiments after the development comparison.
Use a separate 108-request, 20-planning-credit allocation with Luna 6 medium,
the same byte limits, five arms and no-retry subscription transport. The previous
pilot asked for every check, limiting the indexed arm's usefulness. Prespecify
twelve scenarios with narrower queries, source changes, failures and recovery;
execute real local commands and retain source/runtime/artifact bytes. Do not
fabricate new return codes or hashes from the old capture, and do not present
the new authored fixture family as untouched real-world evidence.

The shared child writer receives an explicit scope explanation. Checked/direct
filter only by the announced check names while retaining all possible source
snapshots, using bounded parent plus new observations. Index retrieval preserves
every requested run, including failed reruns. Preserve the original pilot code
and every old result; freeze the new runner, capture, analysis and full schedule
before live dispatch. An accuracy tie at higher cost does not justify additional
candidate complexity. This run measures reporting decisions, not autonomous
task execution, native compaction or general program correctness.

The original launch at `d7cb8e8` stopped on request 17 after four minutes without
a response or usage event. Preserve the exact 17-attempt prefix, all sixteen
answers and the failed identity `tests_later_failure-prose-final`. Freeze a
separate extension for the 91 identities never dispatched; do not repeat the
gap or revise cases/prompts based on scores. The combined ceiling remains 20
planning credits, including the permanent 7.65 uncertainty reservation. A fresh
four-case no-generation preflight passes. Any new transport failure stops the
extension. Complete-pair analysis, if available, is explicitly post-stop and
descriptive; it cannot restore the original complete 12-case comparison.

The suffix at `e32b576` itself stops on its ninth attempt, after eight answers,
with a provider generation error on `tests_recovery-full-final`. Keep both failed
identities permanently missing and retain both 7.65-credit uncertainty reservations.
Combined known cost is 0.2567650; another reservation cannot fit the original
20-credit ceiling. No further automatic extension is launched. Record all 26
attempts, 24 answers and 82 never-dispatched requests rather than declaring the
study complete. The post-stop audit finds one direct-record final-model error
despite a sufficient 203-byte retained receipt; only one case is fully paired.
This supports failure diagnosis, not a method ranking or a completed primary test.

## October 1: audit retained evidence before adding another model study

The user authorized the next research phase. Freeze a retrospective protocol
and 470-file historical source lock at `24da0e1`, then implement an actor-only
public-rule guard and separate evaluator replay at `eeec334`. Include every
scheduled final from the three selected recent studies; preserve all original
outcomes, missing dispositions and costs. This is post-hoc development analysis,
not preregistration. Separate retained-rule readouts, contradictions, abstentions
and actual repaired tasks. No provider call or new allocation is made.

The guard contradicts 32 wrong proposals but leaves 39 correct proposals
uncheckable. One retained state is already wrong. Do not turn 258/259 hypothetical
readout agreements into a measured gain, or claim that typed consistency certifies
source completeness. The same-input/different-history control and forged-receipt
control stay explicit. Known-rule compilation is manual; TierMem and Mem2ActBench
further narrow any generic verification or memory-use novelty claim.

## October 1: keep actual workflow research in one repository

The user selected ContextResearch as the sole working repository. Segment method
code, actual development observations, future prospective tasks, evaluator
manifests and actor serialization in a new `workflow_intake` package. Preserve
the original frozen packet. Capture the actual current task at two clean committed
source checkpoints, with command outputs, run identities and artifact hashes.
One task remains one development episode regardless of reruns, scopes or branches.
Generated previews remain ignored; only controlled command evidence is committed.

Future same-repository tasks can support prospective observed evaluation after
method/grader freeze and consecutive whole-task intake. Record inspection and
report one workload family. Folder names and hashes do not make an implementer's
observed task blind. Enforce actor access through serialized fresh contexts and
the launch runner, with archives declared as separate arms. Target twelve actual
future tasks without manufacturing changes to fill slots. The old private held-out
count stays zero. Complete grader review, cost accounting, model/revision/access
contract and a bounded allocation before any new live result.

Register the completed development episode E0001 with checkpoints `eeec334` and
`f9a9511`: six allowlisted runs, all exit zero. Fourteen raw manifest/output files
are pinned; artifact copies are checked locally but excluded from Git. The full
suite at B has 434 passing tests. Direct receipts retain both source snapshots
in 728 parent bytes and 1,455 child bytes, within the unchanged caps. Keep this
easy control and the zero prospective-evaluation count. Registration/writing
changes after B do not alter the pinned task or become automatically validated
by its receipts. Claim C55 records intake and feasibility, not model utility.

## October 1: audit exact-table redundancy and actual timing

Commit the local design at `66cebac` before implementation. A separate reverse-scan
specification agrees with the unchanged grader on 158,340 constructed queries;
5,652 writer proposals and 52,780 checked/direct chains have equal receipt state.
Derive the exact-format map equality, without extending it to unknown roles,
other codecs, original stochastic accuracy or unconditional production cost.
External human review remains pending despite independent software formulation.

The new canonical checked shadow is offline, not a paid arm. Freeze direct,
indexed, prose and full views with a common final check and six proposed slots
per task. E0001's actual query is answerable from B alone; keep this easy control.
Capture natural variable command sequences and screen every actual future query.
If all twelve are B-only and fit, stop this workload's two-boundary study without
cherry-picking tasks or shrinking caps. The current task remains development.

Under exact-snapshot matching, an A ledger without the final requested tree
cannot affect the answer even when B omits checks. Selective capture cannot
solve this structural limitation by itself. A naturally relevant same-snapshot
history or cross-snapshot obligation is needed; a reporting-rule change would
require another method version.

Its full logical request is 163,432 bytes, beyond the old 100,000-byte logical
cap. Use a predeclared 262,144-byte cap, keeping memory limits unchanged and
all logs intact. The design's transport-envelope phrase denotes logical public
serialization; actual provider wire/token limits need a separate fresh audit.
Freeze sixteen source/protocol/dependency files. Scripted completion and
hash-bound replay are interface controls, not model/prose performance. No new
provider allocation or generation is made; prospective intake and live gates
remain unfinished.

## October 1: test inferred scope instead of another known-table checker

The user's continuing goal authorizes online Luna calls. Commit the separate
eight-call / 20-planning-credit development protocol at `3abb7f7` before code
or model outcomes. Do not reopen historical allocations or fill the natural-task
cohort with manufactured tasks. The learner gets original public classifier
code and a restricted projection DSL; records, authored projection, catalog
and grader outcomes are excluded. No generated code is executed.

Compare a concise prompt with explicit closure guidance on membership, absence,
container type and nonemptiness. Keep all four zero-model controls, especially
cached public-program results, which may eliminate any proposed cost advantage.
Constructed catalog/timing checks and eight correlated calls on one program
cannot establish natural-workflow prevalence, universal correctness or novelty.
The build-system source comparison attributes dependency traces and reuse.

Use a fresh audited CLI 0.159.2 with exact `gpt-6-luna`, medium/default settings,
existing ChatGPT sign-in, no model fallback or retries, durable 7.65 reservations,
and a committed request/source freeze. Alias revision and sampling seed are
unavailable; actual account debit remains unknown. New local tests and four
zero-generation transport controls precede dispatch. External review and the
prospective workflow launch gates remain unperformed.

## October 1: keep the established codec and cached-outcome controls strong

After freezing the source-only learner at `313a877`, add a separate offline
control using the unchanged public `workflow_replay.evidence` schema. Do not
edit frozen learner sources, requests, capacities or historical data. The
same authored fields now fit every worker-pair child and answer all 24 late
queries, as do cached public outcomes. Ordinary JSON answers 12/24. All
14,505 constructed catalog comparisons agree with the original classifier.
Record C58 as an encoding control, not a fundamental capacity obstruction,
new compression mechanism, model gain or natural-task prevalence result.

Automatic approval review rejected the live dispatch twice; neither command
executed and zero identities were dispatched or reserved. Request specific
human approval with payload, destination and bounded quota use. Leave the
frozen eight-call allocation untouched while independent offline work continues.

The user then specifically approved the eight-call payload, destination and
20-planning-credit ceiling, and reiterated broader authorization for sensible
Luna research. Proceed with this frozen allocation; larger future studies still
need their own scientific design and cost accounting, without redundant approval
requests for already authorized model calls. All 464 offline tests, repository
validation and paper assembly pass at the serialization-control milestone.

## October 1: preserve the abandoned launch and correct reservation setup

The approved original launch at `2de4672` stopped with `FileNotFoundError`
before any `turn/start`: it did not create the directory used by durable
reservations. Zero calls were dispatched or metered and no unknown reservation
was left. Preserve its complete original sources and launch/stop/analysis bytes.
This is a local runner defect, not a provider or research-treatment outcome.

Implement a separate version 2 that creates the directory before invoking the
unchanged frozen client. Mocked tests reproduce the failure and assert that a
durable 7.65 reservation precedes the fake generating RPC. A fresh CLI audit
passes all four zero-generation cases. Freeze eight new local identities and
the byte-identical public requests before generation, retaining the original
criterion and a fresh 20-planning-credit cap. User authorization covers this
correction; do not repeat an approval question. Never resume either launched
version or extend spent historical allocations.

## October 1: improve the finite construction without claiming optimality

Add a separate three-block package; preserve all prior mathematical source and
certificate bytes. Search 64 unsigned decision triples from 4,096 candidates
with deterministic greedy addition and at most eight best swaps. Retain the
entire discovery trace, both starts and the timing-label correction rerun.
The new book has 40,529 errors on 147,456 outcomes; the old pair-plus-one book
has 40,992 and no improving single swap under this search. Six independent tests
verify nearest assignments, direct outcomes, baseline books, symmetries, hard
state limits and timing. Register C59 as a checked achievable upper bound.
The greedy start reaches its swap cap, so do not claim a local optimum, exhaustive
codebook search, finite optimum, practical memory cost or publication novelty.
Keep the existing decoder-complete asymptotic converse and interval unchanged.

The replacement Luna launch at `ea5c450` returns two catalog-complete contracts,
then times out on its third dispatch after 240 seconds. Keep that identity
permanently missing and its 7.65 unknown reservation. Known usage costs 0.062325
planning credits. Any separate continuation may cover only the five never-
dispatched identities, with original prompts/criterion and the combined eight-
dispatch/20-credit ceiling. It cannot make the eight-metered-answer criterion
assessable or erase the original gap. No repeated approval is needed for this
already authorized bounded work.

Prepare the separate five-identity suffix without altering any original request,
order or capacity. Seed the unchanged client with three prior attempts and
7.712325 committed planning credits. Three tests check never-dispatched selection,
mutation rejection and a second unknown-reservation stop before server creation.
Fresh zero-generation CLI checks pass. All 480 tests, repository validation and
paper assembly pass before committing the suffix source/request/evidence freeze.
The original eight-metered-answer criterion remains unassessable regardless of
suffix completion.

## October 1: narrow the finite gap with an explicitly restricted converse

For final predictions independent of late coordinate J, reduce each parent state
to a triple of branch-decision words. An elementary positive-cover inequality,
maximum column reward 25 and disjoint missing-constant fibers yield at least
40,072 errors on 147,456 outcomes for any codebook of at most 64 states.
Combine with the 40,529-error witness; register C60. Four tests independently
check every source/column pair, one-block profiles, center fibers and rejection
of coordinate-dependent endpoint decoders. Keep the unrestricted frontier,
external correctness review and unresolved publication priority explicit.
Do not market the elementary cover technique or restricted interval as a new
general method, unrestricted finite optimum, token result or model benefit.

## October 1: report the source-only observations without replacing the timeout

The five-identity suffix finishes with five metered answers. Combine its counts
with the immutable replacement launch: eight dispatches, seven metered answers,
one permanent missing answer and zero remaining unattempted identities. Known
cost is 0.2232910 planning credits; retain the 7.65 unknown reservation under the
same combined 20-credit cap. Do not treat committed allocation as measured debit.

Register C61: every observed contract agrees on the finite catalog, but two
closure responses retain the whole accounting object and exceed the parent cap;
five narrower contracts fit the parent and answer 12/24 imposed late queries.
The fixed-schema and cached-outcome controls each answer 24/24. Sufficiency is
distinct from byte feasibility. The primary criterion requires eight metered
answers and remains unassessable; do not impute the timeout or rank prompts.
Future work must separate source analysis, codec choice and changing query
programs, with strong zero-model controls and a separate protocol. Preserve
all original source/request/evaluator bytes and keep prospective episodes at zero.

## October 1: extend the finite converse by retaining the column distribution

Use a separate package and preserve C59/C60 artifacts. Complementary endpoints
may depend on the late coordinate, but their odd-length predictions have unique
ideal child bits. All 256 per-block tables partition into six symmetry orbits;
56 mixed orbit cases cover heterogeneous three-block tables. A per-source cover
inequality plus zero-target missing-center counts reduces every 64-word book to
the largest 64 exact column weights. Selected integer targets give a common
40,072-error lower bound. Register C62; noncomplementary decoders remain outside it.

Record the post-hoc 1,306 binary target choices and 144 quarter-unit probes as
mathematical discovery, not a preregistered experiment or optimality proof.
All selected arrays use only target zero or one. Five independent tests verify
direct routes, another symmetry partition, all selected column histograms by
direct source sums and the pointwise inequality. Equal score-multiset caching
is declared; do not assert individually executed counts for the full Cartesian
source/column space. Forty-six orbit cases exceed the unchanged incumbent and
ten remain possible. External correctness/priority review stays open; no model
call, token result, unrestricted frontier improvement or general-technique
novelty follows from this extension.

## October 1, 2026 — extend the finite converse to every decoder

Use a separate joint_coding_general package and preserve C59/C60/C62 bytes.
Noncomplementary pairs can tie for the best child prediction, so replace the
unique-ideal correction with an incidence union bound. Q counts zero-target
sources once; q_c counts ideal incidences and may overlap. Identify only equal
entire source-loss functions, not equal histograms. This reduces repeated-action
columns without introducing an instance-dependent public table or restricting
the arbitrary joint parent/updater.

An independently checked branch census assigns defects 0, 1 and 3 to
complementary, distinct noncomplementary and repeated pairs. Total defect at
least four has oracle loss at least 40,960. The existing 4,751 symmetry orbits
reduce the remaining triples to 46,492 mixed cases: reuse 56 complementary
witnesses and save 46,436 new exact targets. Bounded post-hoc selection tries
59,029 synchronized binary candidates, 4,924 mixed refinements and 2,815
quarter-unit candidates. The target grid is not a model experiment, target
optimum or codebook-optimality claim.

All selected inequalities reach 40,072, giving the unrestricted three-block
D_3(6) bracket [40,072, 40,529] / 147,456. Integer histograms compute
178,240,944 cost-column instances with declared profile multiplicities.
Seven tests separately verify routes, polynomial counts, binary saving
coefficients, fractional source sums, zero-target overlaps and source bindings.
Fractional source sums cache 432 equal score-multiset triples explicitly.
Eight auxiliary native books and twelve rational dual points are preserved and
independently rechecked; none of the books improves the unchanged upper witness.
The final cover proof requires neither numerical search nor native compilation.

Register C63 and living draft v0.30. Exact finite optimality, scalable encoders,
external correctness and source priority remain open. Keep the asymptotic
frontier and all model-run evidence unchanged; no natural task, model call,
general cover novelty or token/production saving is added. The next finite
step is to tighten the 457-outcome interval or supply longer checked codes.
The empirical next step remains source-analysis controls on new program families
and actual variable-command workflow intake in this same repository.

All 492 offline tests pass at this milestone; repository validation reports
PASS with 63 claims and 47 bibliography entries, and paper assembly checks
40 cited sources. The final cover and auxiliary audit are regenerated with
matching source hashes. Preserve the raw exploratory bytes and the earlier
certificates; controlled build/test logs and previews stay ignored.

## October 1, 2026 — strengthen source-analysis controls before more model inference

Add a separate scope_static package; preserve the frozen learner, v2, suffix
and all original outcomes. The old literal-root AST control overretains whole
subtrees and cannot establish a need for model extraction. A source-only access-use
heuristic now propagates aliases, constant keys and literal helper contexts,
with separate value, membership and type/truth retention. Unsupported operations
retain their whole base or input and stay in the comparison. No universal Python
soundness, minimal-scope or slicing novelty claim is made.

Three inspected repository programs plus one constructed late-key family agree
on 51,566 finite input/query rows, including malformed types and errors. Quota
retains the whole input; its agreement is not a narrowing achievement. Hold the
codec algorithm fixed across projected dispatch arms, generating public schemas
from source-derived contracts alone. Static and authored contracts each answer
24/24 at 1,958 parent and 950–1,009 child bytes under unchanged caps. Cached
outcomes remain smaller. Uniform-codec replay of seven saved model contracts
gives five 24/24 and two oversized 0/24. This is scripted post-hoc replay, not new
LLM final decisions; the old permanent eighth-answer gap remains missing.

The analyzer receives no records, authored contract, labels or observed model
response. The evaluator separately runs trusted selected repository functions.
Public schema bytes, local timings and read/write bytes are explicit but are not
converted into a production-cost advantage. Historical token arithmetic is
pinned program behavior, not a current provider price claim. No model calls or
natural tasks are added.

Register C64 and living draft v0.31. Add a bounded reading of the original
abstract/Introduction of Horwitz, Reps and Binkley (1990), pp. 26–27, with verified
three-author metadata and DOI. Full algorithm/proofs and replication remain
unreviewed; the attempted scanned Weiser paper was not read or upgraded. Eleven
independent tests use actual program execution, generated field renamings,
branch joins, malformed aliases, presence/truth overlap, missing-key exceptions,
unsupported cases, codec roundtrips and irreversible-memory identities.

Stop spending inference calls on the same inspected classifier. The next cohort
must be separately frozen, include easy/unsupported cases and strong static,
direct and cached controls, and preserve the original byte caps and complete cost
scope. Continue actual variable-command intake in this repository without
manufacturing natural episodes from constructed inputs. Broader extraction,
external review, priority and practical advantage remain open.

All 503 offline tests pass at this milestone, including the eleven new tests.
Repository validation reports PASS with 64 claims and 48 bibliography entries;
paper assembly checks all 41 cited sources. The saved audit regenerates with
matching source/evidence bindings. Historical model requests, outcomes and the
permanent missing answer remain unchanged. Build and test logs stay ignored.

## October 1, 2026 — broaden the parent-rate theory after strengthening controls

The C64 static control removes a need for more inference calls on the same
classifier. Actual prospective intake still requires distinct incoming tasks;
continuing the present research creates no new natural episode. Use the interval
to address the documented wider rate-distortion question without spending model
credits or narrowing the information contract.

Preserve C34 and C59–C64 source/result/provider bytes. Add a separate rate_spectrum
package. Six bounded floating probes are post-hoc mathematical discovery; save
their original script and summaries. Derive unsigned source/reproduction kernel
classes directly, dominate odd words by an explicit positive mixture, and reduce
all positive-slope unsigned supporting optimization to one balanced mass.
An exact polynomial transformation proves a unique support transition near
0.620690001029 information bits per block. Reproduction support size is not
parent alphabet size or an additional final-decoder channel.

The final all-decoder certificate uses no optimizer or exploratory floating
weights. Eight rational t values each cover 4,751 orbits/all 1,679,616 tables;
nonunsigned q uses the existing nearest-word marginal as a witness only.
Strict other-table objective separation holds at every selected slope. Exact
Gibbs channels plus positive rate slack give asymptotic upper bounds; a common
supporting inequality gives lower bounds for every k and arbitrary joint,
heterogeneous chains. All eight intervals are narrower than 2e-11. Do not infer
an unrestricted full curve or finite optimum between the checked slopes.

Register C65 and living draft v0.32. Reread MIT 6.441 Chapter 25 Section 25.2,
Theorem 25.2 and its support remarks, pp. 258–259. Keep established duality,
symmetrization and support optimization identifiable as prior machinery;
publication priority and external proof review remain open. Six independent
tests cover routes, polynomial coefficients, positive factors, root/optimizer
brackets, Gibbs marginals and independently evaluated channel inequalities.
The coefficient test caught a middle factor coefficient of 34; correct it to
42 before committing. Regenerated route-based interval endpoints are unchanged.

Next mathematics: prove or refute all-decoder dominance between the checked
slopes, or construct efficient finite codes. Empirical work still needs a new
frozen cohort with strong static/direct/cached controls and actual command
timing. No token, total-cost, natural-task or model gain is inferred here.

All 509 offline tests pass, including the six new independent tests. Repository
validation reports PASS with 65 claims and 48 bibliography entries; paper
assembly checks all 41 cited sources. All nine source/provenance bindings and
eight exact supporting certificates regenerate. The corrected factor leaves
the independently route-based interval endpoints unchanged. Build logs stay
ignored and historical model/source/result bytes remain preserved.

The next proposed theorem is a balanced-source complementary-completion
reduction. Separate exploratory branch checks and a floating between-point
screen are not a whole-code proof and are not registered as C65 results. Check
the averaging argument with the old encoder/updater held fixed, public tables
selected before source, and no extra information after replacement; retain
source-balance and query-timing qualifications. This may simplify the remaining
all-rate comparison without requiring another model batch.

## October 2, 2026 — prove balanced-source complementary completion

Promote the exploratory completion idea to a separate analytic claim C66 and
decoder_completion package. Hold the old encoder/updater fixed while averaging
fair public fills on agreeing endpoint coordinates. Those old predictions have
error 1/2 under balanced source and independent queries. Some fixed completion
is no worse; canonical ordering only XORs a public R/O label into the one-bit
child. Choose the completion before source, never from the observed instance.

The constructive adapter chooses modal population X_j XOR old_child values.
Its finite design enumerates 1..3 blocks and up to 64 states; the theorem covers
every k/capacity. Do not turn design statistics into actor observations or claim
efficient practical computation. Parent mapping/capacity stay unchanged. Any
later nearest-parent reassignment is a separate legal construction.

The average-error theorem reduces all positive-slope supporting optimization
to complementary tables, preserving I(X;A) by a fixed output-word permutation.
Use the existing six complementary symmetry families for the remaining curve
problem. C62 now yields an alternative unrestricted three-block lower bound
by this new deduction; preserve C62's original restricted artifact and C63's
independent all-decoder certificate rather than rewriting their historical scope.

Check all 36 pairs/256 Boolean branch updaters: 9,216 cases, 35,840 oriented
completion scores and zero averaging disagreements. Execute 3,686,400 whole-code
routes across eight preserved books and identity on C59. Minimum completed/
reencoded error is 40,738, above the unchanged best 40,529; no frontier gain.
These inspected mathematical examples include symmetry-related cases and are
not independent trials. Keep all original source/book/result bytes untouched.

Record the biased-source counterexample X in {0000,0011}: two-state parent,
one-bit child, unrestricted error zero versus complementary minimum 1/6.
Also record an individual source whose loss increases despite equal mean loss.
Source/query hypotheses, average versus worst-case metrics and offline design
must remain explicit. This is elementary averaging, not a new general method,
model benefit, natural workflow or production-cost result. Eight independent
tests pass; all 517 repository tests pass. Validation reports PASS with 66
claims and 48 bibliography entries, and paper assembly checks all 41 cited
sources. External correctness and publication priority remain open.

The next full-curve attempt compares the other five complementary families
with the unsigned family using exact polynomial inequalities. Fixed-q float
screens are mathematical discovery only; a failed witness is not a better
decoder. Do not claim a full curve until the entire parameter interval is proved.

## October 2, 2026 — certify the unrestricted asymptotic curve (C67)

Use C66's proved complementary completion to reduce supporting optimization to
six families, then compare every word of the other five families against the
unsigned free-objective witness. Do not assume nearest-word marginals are
optimal or discard words outside their support. Three fixed rational unsigned
distributions and seams 4/25,1/4 suffice. The failed earlier two-witness float
screen is preserved; it is not a counterexample to unsigned optimality.

Clear the dual products into exact integer polynomials. All 240 column/interval
cases reduce to 48 distinct comparisons. Remove exact positive (1-t) factors,
then certify all 19,474 transformed coefficients and positive endpoint values
on the three covering intervals. The final Horner/Pascal transform differs
from the preserved factorial-convolution probe. Counts/digests are diagnostics;
the full regenerated arithmetic and model reduction supply the proof.

The unsigned family attains every positive-slope supporting minimum. Only the
five other complementary families are proved strictly separated; do not claim
that all noncomplementary equality cases have been classified. Apply a common
bound to arbitrary joint encoders and heterogeneous tables. C65's quadratic
scalar root now parametrizes the complete unrestricted asymptotic curve.

Prove coding at exact rates by mixing with a source-independent channel to
make I<r, then using an intermediate coding rate whose rounded codebook fits
floor(k*r) bits. This also gives the h_star endpoint without extra o(k) bits.
Keep the finite 3k-bit exact-attainment threshold and unchanged three-block
interval distinct from the asymptotic theorem. No efficient encoder is implied.

Reread the existing Polyanskiy/Wu primary Chapters 24 (Theorems 24.1-24.3) and
25 (Section 25.2/support remarks), with scope in the new note and reading guide.
These coding/duality methods, strategies, averaging and polynomial positivity
are established. The particular model curve is a local candidate contribution;
external correctness and publication priority remain open. Eight independent
focused tests and all 525 repository tests pass. Validation reports PASS with
67 claims and 48 bibliography entries; paper assembly checks 41 cited sources.
All 23 source/provenance bindings and 48 exact inequalities regenerate.

Keep all historical provider/source/certificate bytes unchanged. There are zero
new model calls or prospective natural episodes. Work remains in segmented
folders of this repository. Next steps are external proof/priority review and
finite encoders approaching the curve, not extra calls on the inspected source
classifier.

## October 2, 2026 — implement a compact finite trellis code (C68)

Follow C67's full curve with a finite encoder under the same parent/child timing.
Use fixed three-phase labels on a 16-state tail-biting quaternary trellis, storing
exactly two bits per source block. The boundary is the last two stored symbols,
with no extra retained state. Exact reverse Viterbi minimizes fixed-table loss;
its 1024*k branch relaxations are operation counts, not portable timing claims.
Public labels contain 96 packed bytes, excluding program/runtime/JSON size.

Preserve the failed initial extension: identity plus seeds 1..32 of C59's book
all lose to the four-block pair-product control, best 879,487 versus 869,376.
Four fixed phase/index sweeps consider all 15 alternative labels per entry.
After 93 accepted changes, 867,837 errors remain on 3,145,728 outcomes. Retain
all 768 coordinate visits/11,520 scores, both native sources, compiler flags,
Windows C-clock observation and upstream hashes. Search is adaptive post-hoc
mathematics, not independent trials or a local/global optimum certificate.

Independently enumerate nearest finite messages, then grade every actor route
at k=1..4. The selected labels lose at k=1,2,3; preserve that negative transfer.
Ordinary concatenation of separately closed four-block groups gives the same
error for every k=4*n without extra group state. At common k=12*n, C59
three-block products are better, so the best known asymptotic upper bound is
unchanged. That product proof does not
imply quality for one longer cycle or approach C67's asymptotic frontier.

Implement the code, proof and independent scientific tests in a new segmented
folder within this repository. Preserve C59/C67 source/results and all model
launch bytes; add zero model requests and zero prospective natural episodes.
Read QTIP v4 Sections 2.3/3.1/3.2 and Marcellin/Fischer's university abstract
record. General TCQ/Viterbi, bit-window decoding, table tuning, product coding
and tail-biting are established; finite optimality, external proof/priority
and natural-agent usefulness remain open. Add C68 and living draft v0.35.

## October 2, 2026 — stronger six-block control and product-locality counterexample (C69)

Follow C68 with a longer construction that must beat refined three-block
products at common lengths. Preserve the failed original modal product/three
seeded starts, weak original single-change gain and stationary modal continuation.
Refine C59's component with four accepted gains 8,2,2,3, then independently
screen all 262,144 single-word replacements: none improve40,514/147,456 error.
Combine it with C63's unchanged lower bound to tighten the unrestricted bracket
to [40,072,40,514], width 442. Leave original source/certificate bytes unchanged.

The refined two-copy product still has an improving single joint word. Keep
the same12-bit parent M=a+64*b and one-bit child before J. Changing one left
triple while preserving its right triple improves331,890,688 to 331,886,587.
Eight conditional changes reduce error to 331,857,648/1,207,959,552. This is a
scoped failure of single-word product locality, not a general new quantization
theorem or statement about globally optimal components. The small gain is
0.002735 percentage points over the refined product. Search stops at cap 8
with a positive last gain; final six-block locality/optimality is unproved.

Implement exact nested minima, the public updater and one-bit-only final actor
in a separate folder of this repository. Public labels contain120 payload
bytes,24 more than the base product; count 8 is a protocol constant and framing,
program/JSON/runtime size are separate. Instance caps remain12 and 1 bits.
Repeat independent six-block groups at 2*k parent bits, deriving the same error
for 6n and a win over both three-block products at common12n. C67's optimal
asymptotic curve is unchanged, and no approach-to-curve guarantee follows.

Use independent bit losses and direct addition/removal sums for component
locality. For six blocks partition left sources by relative group minima;
right high digits are then identical within each group. Execute weighted
source-inaccessible actor queries:11,783,592 physical calls cover 1,207,959,552
outcomes over 16,777,216 sources. Do not claim every outcome ran individually.
Independently rescore all accepted losses/gains; native rejected conditional
candidate maxima remain observations, not an independent complete replay.
Preserve controlled raw mathematical JSONL, actual native source/header bytes,
compiler flags, upstream commit/hash and qualified Windows C-clock observations.

Read Jégou/Douze/Schmid's author manuscript Sections II-A/B. Generic nearest
assignment, local tuning and product quantization are established. External
correctness/priority and natural-agent usefulness remain open. Claim C69 and
living draft v0.36; all 541 offline tests pass, including eight new scientific
tests. Validation reports PASS with 69 claims/51 bibliography entries/171 PDF
hashes; paper assembly checks 44 cited sources. All 24 bindings regenerate. Zero new model calls or
prospective natural episodes; all frozen model launches and permanent gaps stay
unchanged. Further calls on the inspected classifier remain uninformative.

## October 2, 2026 — query-prior robustness, allocation and early class timing (C70)

Extend the uniform-source model to two equal public query classes with a fixed
source-independent prior p. Keep within-class R, omission O and late J laws,
the 2k-bit parent/one-bit child cap, public-label accounting and no-reread
contract. Separate known p before X, unknown-prior parent design and actual
realized class T before M. Do not infer source-adaptive or instance-dependent
prior guarantees from this fixed-p analysis. The early cue carries no source
information but changes permitted encoder dependence.

The local C67 consequence gives known-prior optimum min pD(r_L)+(1-p)D(r_R)
under r_L+r_R<=4, with joint/heterogeneous converse and strict rounded-capacity
coding achievability. Five rational supporting/slack witnesses include
[0.257186606420,0.257186606421] at p=1/4. Uniform p is a consistency check
inside the old C34/C67 interval. Unknown-prior minimax is squeezed between
D_{2n}(4n) and D_n(2n), hence tends to D(2); do not assert finite equality.
An early actual class cue uses 3n signatures inside 4n and attains 1/4; late
uniform limiting excess is (0.0118989799,0.0118989801). These are scoped local
deductions, not new general allocation or side-information theorems.

Preserve the negative finite sensitivity result: C69's frozen encoder loses
its product advantage below p=59911/152862. Fixed-book known-prior nearest
assignment has 52 exact affine segments covering all 16,777,216 source pairs
by 1728 weighted terms. An opposite-orientation pair preserves
2304567/8388608 for every fixed source-independent p at k=12h, 2k parent bits
and one child bit without orientation instance state. Its 120-byte label
payload is shared; no twelve-block full-source enumeration is claimed.
All local messages/orientations/routes give 589,824 physical final checks.
Use stronger 1/3 allocations as named controls: at p=1/4 they achieve 17/64
and beat the balanced pair. Named controls are not all finite optima.

Retain the failed initial common-q bracket, corrected script and explicit
provenance of the recomputed original JSON. Initial output was overwritten,
so do not call that record an original raw artifact or recover its timing.
Only exact admission/outward logs support bounds. All five first rounded
rational candidates pass within the ten-attempt ceiling. Sixteen bindings
include original C67/C69 outputs and source checks; historical artifacts,
provider allocations and the natural-task ledger remain immutable.

Existing Polyanskiy/Wu Chapter 25 Section 25.2/support remarks were reread
within bounded scope; no new bibliography metadata or inherited review status
upgrade. Claim C70 and living draft v0.37. All 549 offline tests pass,
including the eight new scientific checks; repository validation reports PASS
with 70 claims, 51 bibliography entries and 171 PDF hashes. Paper assembly
checks all 44 cited sources. Zero model calls or natural
episodes. External correctness/priority, efficient finite codes approaching
the characterized limits, biased/adaptive laws and natural-agent benefit stay
open. Generic allocation/symmetry/product coding novelty is not claimed.

## October 2, 2026: implement a charged-cap entropy code and retain finite controls

Keep the original uniform iid four-bit source and independent uniform R/O/J
law for C71. Public scalar quantizers and counts are fixed before X. Compress
their outputs with exact arithmetic intervals and an odd grid, charging one
regular/fallback flag inside 2k parent bits. Only M and then one-bit Z cross
boundaries; temporary interval/source computations do not reach later actors.
The ten packed public response/probability bytes are separate from public k/a,
program/runtime/framing and instance bits. Polynomial bit complexity is proved,
without a portable runtime, linear bit-operation or practical-agent claim.

Use the nonnegative all-zero fallback excess and the entire bad-length event
to bound risk; never assume actual grid failure is independent of values or
sequence order. Exact binomial tails/first moments and direct-power frontier
checks justify whole-population upper bounds. These are conservative larger
risks, not exact average errors or physical enumeration of all source points.
Every small population/query for k<=3/all a is checked, with 608640 final
queries; twelve large constructed inputs supply only 864 diagnostic queries.

The default maximal-entropy-slack schedule has actual limiting error enclosed
by [0.270753014417,0.270753014418], below named C69 but still above C67. Retain
the original rational schedule: at k=12288 it gives the stronger finite upper
271988910418071/10^15 and beats the default finite bound at three lengths.
Both codes provably lose at the four checked smaller lengths. Preserve all
prototype/control outputs and honest post-hoc provenance; revised scratch
imports evolving code and is not a fully frozen historical runtime. Fifteen
bindings include original C67/C69 outputs and checks of their immutable sources.

Read Chou/Lookabaugh/Gray Introduction/Section II, pp.31–33, and Gray's author
metadata entry68 in bounded scope. Add verified `chou1989entropy` metadata;
do not invent a DOI or upgrade inherited full-review statuses. Entropy coding,
time sharing, quantization and concentration remain established foundations.
This phase adds the specific implemented code, overflow bounds and analytic
family limit; external proof/priority, efficient codes approaching C67 and
natural-agent/model/token/cost benefit remain open. Claim C71; draft v0.38.
All 557 offline tests pass, including the eight new scientific checks.
Repository validation reports PASS with 71 claims, 52 bibliography entries
and 171 PDF hashes; paper assembly checks all 45 cited sources. All 15 new
bindings regenerate. Zero new model calls or natural episodes; provider
allocations stay closed.

## October 2, 2026: coordinate equal-loss answers with established weighted covers

Keep uniform iid source and independent uniform R/O/J. Treat source weight
two as a choice between equal-loss constant responses; coordinating it across
groups reduces entropy without source-wise error increase. Prove the pair
minimum from mandatory 25/maximal 121 masses and majorization, attained by
[121,85,25,25]/256. Scope it to compatible constants, not a global quantizer.
Apply Cardinal/Fiorini/Joret's published weighted greedy-cover guarantee,
plus the local information/rank/prefix argument, to deduce entropy/block->5/8.
Read Introduction/Section 2/Theorem 1 with weighted extension and Lemma 2's
statement in bounded author-manuscript scope pp. 1–5; author metadata list
corroborates Algorithmica 51(1):49–60, 2008. Add cardinal2008entropy without an
invented DOI or inherited full-review upgrade. Generic methods remain prior art.

Implement exact mixed arithmetic subdivision, odd grid and one charged flag
inside 2k parent bits. Only M then one-bit Z survive; source, intervals, output
lists and provider/archive/environment channels do not. Fixed-eight data
increase to 1288 packed public bytes versus C71 ten. Public n/g/a, program/
runtime/framing and growing tables remain separate; no memory-footprint,
token/cost, portable speed or native-agent benefit claim follows.

Fixed-eight actual limit is [0.269293075342,0.269293075343]. A separate public
g=max(1,floor(bit_length(n)/4)), k=n*g, multiplier 4*g schedule gives a
polynomial builder/actor family and limit [0.267829178707,0.267829178708],
still above C67. Arbitrary g without the schedule is exponential; finite
diagnostics do not execute every n or demonstrate efficient convergence.
Forty inspected margin designs use five integer-root-enclosed Chernoff
exponents. Selected larger bounds beat both C71 codes' base-error lower
bounds; selected four smaller designs lose to stronger named controls.
Selection minimizes a conservative bound, not actual risk or every allocation.

Independently recount all weighted greedy choices at six group sizes.
Literal small quantizers execute 153792 queries, thirteen complete small
arithmetic populations execute 915840, and fifteen constructed large inputs
execute 1008 diagnostics. Keep those scopes distinct from whole-population
analytic bounds. Seventeen bindings preserve C71/C67/C69. Retain failed
first search, 486 revised maps, six probes and forty finite designs; gzip
preserves actual pair JSON bytes, scratch imports are not a frozen runtime.
Claim C72; draft v0.39. All 566 offline tests pass, including nine new
scientific checks. Repository validation reports PASS with 72 claims, 53
bibliography entries and 171 PDF hashes; paper assembly checks 46 cited
sources. All 17 code/provenance bindings regenerate.
Zero new model calls or natural episodes; provider allocations stay closed.
External correctness/priority, efficient near-C67 codes, broader laws and
natural-agent/model/token/credit/production benefit remain open.

## October 2: supply deterministic formal convergence and expose its finite cost

Continue from C72 commit d3fb3fb with a constructive rate-two question.
Implement public greedy covers at every integer loss threshold over all
sixteen response words per block. Reassign sources to nearest words, grade
exact uniform-source risk and compare the existing scalar-product control
before X. Do not give individual sources a free codebook selector. Full-group
2g-bit labels and scalar-tail two-bit labels fit exactly 2k; only M and then
one-bit Z cross the boundaries.

Prove the actual group limit using the ordinary greedy partial-cover
recurrence and strict-slack excess-distortion coding. Set public
g=max(1,bit_length(k)//10): bit-set design costs poly(g)*1024^g, bounded by
O(k*poly(log k)) at g>=2; actors and workspace are polynomial. This resolves
formal deterministic convergence to C67 at every integer length, not useful
finite convergence. Keep the conservative quantitative mixture/Chebyshev/
coverage bound and all 54 inspected g/h cases. Large g=10^10 has bound
<=0.265608205363 and first default k=2^(99999999999); no such book is built.
Do not interpret polynomial complexity as practical speed or input sizes.

The scalar product wins at g=1 and ties at g=2; three gives 2543/9216 and
loses to both stronger finite three/six-block controls. Preserve eight/full
alphabet probes and all 150 inspected thresholds/1616 choices. Independently
check 16843008 routed distances and 768 final-builder choices, 454848 complete
small actor queries, 3552 constructed product/tail diagnostics and 307200
cover-recurrence comparisons on all 4096 tiny systems. Sixteen bindings
preserve upstream C72/C67/C34; large proximity populations remain unexecuted.

Read selected original Nemhauser/Wolsey/Fisher Section 4 passages with the
greedy definition, Proposition 4.1/proof and Theorem 4.2 statement, printed
pp. 276–281, plus verified publisher metadata. Reread existing Polyanskiy/Wu
Chapter 24 Theorem 24.4/short proof and selected memoryless argument pp. 251–252.
Read Śmieja/Tabor publisher-indexed Introduction/Section 3.1; direct retrieval
failed, and the full Section 3.2 proof is unreviewed. Add two verified focused
bibliography entries without upgrading inherited archive status. Generic
greedy coverage, logarithmic blocking and source coding remain established.

Claim C73; living draft v0.40. All 575 offline tests, repository validation
with 73 claims/55 bibliography entries/171 PDF hashes and 48-source paper
assembly pass. Zero new model calls or natural episodes. External correctness/
priority, useful finite near-limit codes, broader laws and agent/model/token/
cost benefit remain open. Do not populate untouched task slots from research
commands or repeat closed classifier cases.

## October 2: weight finite overflow by loss and optimize public allocation

Continue from C73 commit 2080019 under the existing uniform bit contract.
Preserve all 192 fixed-response and 192 centroid-updating starts; none beats
the stronger C72 entropy/distortion chord. Keep original gzip-restored JSON
bytes, native code, both protocols and upstream warm-start/result hashes.
Independently grade 11403264 source assignments and 14706 rate-two
interpolations. Established ECVQ Section III pp. 33–35 is read as a bounded
primary comparison; no generic quantizer novelty or global optimum follows.

Use nonnegative conditional fallback excess in the exponential-moment bound.
Exact forced-status cell sums and outward roots strengthen finite guarantees.
The public allocation objective is discrete convex under checked sufficient
conditions. Minimize each of five outward bounds over every integer a with
exact neighbor-sign checks, then choose the best clipped bound. This
optimizes the certificate, not actual error or every exponent. Retain forty
complete allocation minima and forty old margin-grid comparisons.

At k=768, a=59 has error <=8578395865937/31250000000000, below exact C69.
At k=12288, a=1030 has error <=270646703203513/10^15. Seven k>=192 selected
codes have upper bounds below the named previously selected C72 codes'
base errors; no comparison against every old C72 allocation follows.
Three smaller lengths still provably lose to C69, and k=96's allocation
is unchanged. Original arithmetic actors and 1288 public table bytes stay
inside the declared 262144-byte envelope; only a changes before X.
Exactly 2k flagged parent bits and one child before J remain charged.

Thirteen complete small populations execute 915840 final queries; nine
constructed larger inputs execute 540 diagnostics. Preserve separate local
wall/process timing samples: cold public planning at k=12288 takes 31.651
seconds wall; warm encodes take 0.022–0.044 seconds on three inputs.
Single samples do not establish portable speed or population latency.
Twenty-nine bindings preserve prior sources/results. New selector's actual
limiting risk is unproved; C72/C73 original family limits remain intact.

Claim C74; living draft v0.41. All 583 tests pass, including eight new
scientific checks; repository validation reports PASS with 74 claims,
55 bibliography entries, 171 PDF hashes and 195 immutable import hashes.
Paper assembly checks all 48 cited sources.
Zero new model calls or natural episodes; closed provider allocations and
untouched task slots remain unchanged. External correctness/priority,
useful near-C67 codes, broader laws and agent/model/token/cost benefit open.

## October 2: exact-price larger groups and preserve the resource tradeoff

Continue from C74 commit e109803. Freeze eight g=5 full-population starts
before execution; all eight fail the 12288-block C74 certificate target.
Preserve a separate post-hoc amendment before either g=6 launch: design
on one fixed 131072-source pseudorandom sample, then exact-grade both
final books on all 16777216 sources. Keep proposal weights separate
from actual CDF counts. The first six-block start fails; the second
7288-word descriptor gives the selected finite and separate limit families.

At k=12288, a=560/s=16 error is <=54095129871619/200000000000000,
below C74's named base lower bound. The same strict comparison holds
at k=6144; four other lengths establish only tighter certificates.
The smallest still loses to exact C69. Retain all fifty target and
thirty selected-book allocation minima, with exact integer neighbor signs.
Parent stays 2k flagged bits plus charged tail inside that cap, then
one child before J and final only Z/R/O/J. No forbidden information channel
or full source map is available to actors/public planners.

Count the larger public payload honestly: 66513 packed actor bytes,
94754 including cell loss weights for finite planning, within 262144.
Parameters/program/framing/JSON/cache RAM and stage workspace are separate.
Local single-sample encodes at 12288 take 10.609–18.625 seconds; planner
takes 11.897 wall seconds. Concurrent grading and uncontrolled hardware/
scheduling prohibit causal speed comparisons. The cheap C74 code remains
an important engineering control.

Complete independent tensor minima match all 41943040 saved source
assignments, with 1132736192 transform comparisons and zero mismatches.
Literal losses/CDF, all public log floors, 1294947 native comparator
cases, four full tiny controls and 650 Python probes have separate scopes.
Nineteen complete small actor populations execute 934848 final queries;
nine constructed large inputs execute 540. Preserve actual raw bytes,
both protocols, sample IDs, original programs/logs and 71 bindings.

The finite selector's actual limit remains unproved. A separately
implemented entropy-slack family has actual limit
[0.269017091392,0.269017091393], better than fixed C72 but worse than
growing C72. Old C67/C69/C71/C72/C73/C74 evidence and schedules stay intact.
Existing bounded Chou reading is reused without a status upgrade;
generic ECVQ/tensor/arithmetic/concentration novelty is not claimed.

Next freeze a full-population six-block design extension using the verified
tensor transform and separately measure actor improvements under the same
envelopes. This extension is unperformed. Claim C75; living draft v0.42.
All 597 offline tests pass (1118.063 seconds), including fourteen new
scientific checks. Repository validation reports PASS with 75 claims,
55 bibliography entries, 171 PDF hashes and 195 immutable import hashes;
paper assembly checks 48 cited sources. All 71 bindings match. Earlier
claim/decision prefixes, bibliography and all other original tracked
files retain their actual bytes. Zero model calls or natural episodes; do not repeat
closed classifier allocations or populate untouched tasks from research
commands. External review/priority, useful near-C67 codes, broader laws
and practical-agent benefit remain open.

## October 2: stop experimentation and preserve the final checkpoint

At the user's request, stop experimentation for today at bb71f37, claim C75,
living draft v0.42. Save the [closeout handoff](END_OF_DAY_2026-10-02.md)
and [verification record](../experiments/dependency_memory/results/closeout_2026-10-02.json).
Preserve the completed 597-test and PASS repository-validation evidence.
Fresh closeout checks verify all 16 C73, 29 C74 and 71 C75 source bindings,
discovery files and exact gzip restoration of original records. Rebuild
the 48-source paper preview. Full scientific checks were completed before
these documentation-only changes; do not imply they were repeated here.

Keep all failed starts, protocols, raw evidence, public tables and timing
limitations. Launch no new full-population extension, runtime measurement,
model call or natural episode. The proposed next steps remain unperformed.
Practical benefit and external review remain open; this is a daily
checkpoint, not completion of the research objective.

## October 7: centralize experiment navigation and keep evidence paths stable

The user requested a repository structure that research agents can navigate and
a clear home for summaries of completed experiments. The prior README, status
and research map duplicated milestone histories, while the implementation README
mainly described the earliest diagnostics.

Add [the study registry and generated catalog](../experiments/README.md), with
separate model, mathematical, offline, prepared-study and infrastructure views.
The initial inventory has 52 study/diagnostic/support entries, covering 38 tracked
implementation packages and 1,000 tracked result files. These are navigation
counts, not independent trials. Related launch phases share a summary but retain
their original ledgers, permanent failures and never-dispatched identities.

Replace the three startup documents with concise routing and current scope.
Archive the former status and map in [docs/history](history/README.md), with
relative links rebased and original-file hashes recorded. Add explicit
[placement rules](REPOSITORY_STRUCTURE.md) and update agent/maintenance guidance.
The registry is the sole editable source for generated experiment summaries;
primary protocols, reports and the claim register remain authoritative evidence.

Preserve scientific code, frozen contracts, saved result bytes, imported sources
and claim records at their existing paths. A wholesale physical move would affect
imports, source bindings and frozen manifests. The fast catalog/navigation check
detects missing paths, duplicate IDs, unknown claims, stale views and uncataloged
tracked packages/results without running experiments. The default validator keeps
its full scientific checks; navigation-only validation does not substitute for them.

This is organizational work only. C75 and draft v0.42 remain the scientific
checkpoint; no model launch, new natural episode, source-review upgrade or
scientific result is added, and no closed allocation is reopened.

Organization validation passes: catalog coverage/freshness, local documentation
links and claim paths, generated study anchors, and archival content comparison.
Five negative probes confirm rejection of duplicate IDs, missing evidence, unknown
claims, uncataloged results and stale views. The existing 16 saved-evidence
validator tests pass with temporary fixtures placed under workspace `tmp/` after
the sandbox's default temporary directory denied access. Paper assembly passes
with 48 cited sources. The full 597-test scientific suite and numerical result
regeneration were not rerun for this organization-only change.

## October 7: isolate branch removal in a small rollback pilot

The user requested research into testing checkpoint rollback on Luna with math
and coding tasks. Prepare a [design review](../research/ROLLBACK_PILOT_DESIGN_2026-10-07.md),
[draft protocol](../experiments/dependency_memory/rollback_pilot/DRAFT_PROTOCOL.md)
and [prompt interfaces](../experiments/dependency_memory/rollback_pilot/PROMPTS.md).
This resumes scoped research/design; no model calls, generated-code execution or
historical allocation are authorized by the draft itself.

The primary comparison keeps or removes the same failed branch while holding
checkpoint, public failure feedback, lesson and continuation allowance fixed.
Both arms reconstruct visible input without carried opaque reasoning. A generic
summary and removal without a generated lesson provide secondary controls.
Save the checkpoint before route selection so a committed failed assumption is
not accidentally retained in the prefix being tested.

Propose 12 exactly checkable constructive math tasks and 12 pinned coding tasks,
with two terminal draws per arm. Report all initial task dispositions; public
failure eligibility cannot use reserved test outcomes or reference answers.
The development pilot tests conditional recovery and feasibility, not autonomous
rollback selection or end-to-end efficiency. Stronger held-out repair/retry and
native-context comparisons remain separate later work.

Thought Rollback, LongSeeker and ARC establish close prior mechanisms. Record
bounded source readings in the [focused guide](../sources/READING_GUIDE.md#october-7-rollback-pilot-design)
and bibliography. No general rollback novelty, measured benefit or new paper
claim follows. C75 and living draft v0.42 remain unchanged.

The existing subscription adapter is historical. Local CLI/schema observations
do not establish the proposed output cap; Docker's engine was not reachable.
The protocol therefore requires fresh transport/runner checks and a separate
bounded launch manifest. The proposed 320-call / USD 5 direct-API envelope is a
conditional design calculation, not an active allocation or a subscription-credit
conversion. No credentials or account entitlement were tested.

## October 8: prepare the rollback experiment suite for user review

The user requested the experiment designs and a handoff before reviewing how
the work will run. Add the [review handoff](ROLLBACK_REVIEW_HANDOFF_2026-10-08.md)
and expand the unfrozen pilot to v0.2 with separate task/grading, controller,
analysis and later-policy specifications. Keep model calls and coding execution
unperformed; leave actual launch identities, data hashes and access unset.

Use E0 offline acceptance, E1 eight-call calibration and E2 the 24-task conditional
recovery pilot as the first implementation sequence. E3 confirmation, E4 complete
policies and E5 checkpoint choice have separate designs and resources. The USD 5
proposal covers E1/E2 only. A large E3 sample-size example illustrates sensitivity
to eligibility and discordance; it is not an allocated or selected cohort.

Keep the failed trial before its evidence and lesson in the serialized control
input. Alphabetical top-level JSON ordering would put the trial after the lesson
and change the intended comparison. Generic-summary failure blocks G only;
otherwise it would discard valid K/R comparisons for an unrelated writer failure.
Capacity-infeasible pairs and unknown dispatches retain explicit denominators.

Specify generated math families and deterministic coding selection. The proposed
LiveCodeBench lite release_v6 uses pruned retained tests; do not imply access to
full original suites. Record the distinction, unresolved data provenance/license
fields, and ten preview-exposed IDs excluded from new model cohorts. No corpus
was downloaded or used for inference. Refresh official rate/cap readings without
testing credentials or reusing historical subscription allocations.

The autonomous loop stops after a public pass, so rejection of a completed correct
answer is unobservable there. Add a separately labeled 12-call authored decision
probe with withheld correctness feedback; never pool it with natural policy
episodes. E5's proposed USD 19 ceiling includes this probe and calibration.

The authored JSON example and design manifest make context contents and resource
arithmetic reviewable. They are not evidence of model behavior, implementation
acceptance or an empirical effect. C75 and living draft v0.42 remain unchanged.

Design validation passes: 53-entry catalog freshness, navigation and citations
(63 bibliography entries and 75 claims), 48-source paper assembly, JSON parsing,
budget arithmetic and authored-example consistency. This is document validation,
not E0 acceptance, a scientific-result regeneration or a rerun of the 597-test suite.

## October 8: implement offline rollback E0 and keep live gates explicit

At the user's request, implement and test the first stage of the review handoff,
using only a fake transport. Save [the implementation finding](../research/ROLLBACK_E0_IMPLEMENTATION_2026-10-08.md)
and a separately cataloged controlled engineering archive. Preserve historical
allocations, supplied design bytes, source provenance and other working-tree edits.

Use immutable typed actor/evaluator records and a strict renderer; K/R retain
identical task/checkpoint/feedback/lesson and instructions. Append transactional
call events before dispatch, preserve ambiguous reservations, and never retry a
possibly dispatched identity. Writer failures block only dependent conditions;
K capacity loss blocks the pair before either continuation. Grade after generation,
retain the full cohort, and report fixed-denominator missingness and policy projections.

Bring up the installed Docker engine and pin an official Python 3.11 image. Actual
reference, incorrect-program, resource, channel and teardown probes pass. The
66 package tests and five archive probes validate engineering; 210,656 enumerated
finite candidates and 144 scripted calls are not independent LLM observations.
Preserve development-check errors and fixes rather than presenting a flawless
first start. Actual provider spend and model calls are zero.

The prepared bundle has 12 real generated math tasks and eight calibration
requests. Authored coding doubles do not replace the benchmark cohort. A bounded
static intake pins a candidate dataset revision/loader hash but does not resolve
source-specific rights, references or retained-test completeness. Keep these gates,
live endpoint/retry/tokenization/account checks, fresh pricing and a new allocation
open. E3/E4/E5 remain separate. No new paper claim or rollback-benefit assertion.

## October 8: use the requested subscription and disclose the engineering amendment

The user selected their existing Codex subscription for GPT-6 Luna and removed
token/cost budget concerns for completing implementation and tests. Use the
official installed app-server and existing ChatGPT sign-in; no API credential or
historical allocation is needed. Preserve the completed eight-call E1 separately
from a new at-most-312-call engineering pilot allocation. Unknown dispatch or
metering still stops for evidential validity; no purchase or credit fallback.

The installed client has no established configurable 16,384-output-token ceiling.
Declare provider-default output, UTF-8-byte admission, unavailable immutable model
revision and calculated subscription planning credits in a versioned amendment.
Never call those credits actual account charges or reuse API-dollar estimates.

The original benchmark source still lacks verified permissions and reference
programs. Prepare twelve original coding tasks for a clearly labeled engineering
pilot, alongside the original twelve math tasks, with independent finite oracles
and complete reference checks in Docker before freezing. This source change does
not fulfill or relabel the proposed LiveCodeBench comparison. Freeze all tasks,
source hashes and possible call identities before outcomes; preserve public-pass
stops and every skipped task/condition. Later stages and manuscript claims remain
separate decisions.

## October 8: preserve the instruction-gap run and freeze a complete language retest

The first authored run returned six C++ programs to a Python-only grader because
the coding actor statements omitted the Python requirement. Preserve all 24 tasks,
50 metered generations and every disposition; do not label that mismatch a clean
coding-ability result. No public mismatch was eligible for recovery in this run.

Correct the language contract in every coding statement and retest all 24 tasks
under new frozen sources, actor bindings, launch identities and a separate ledger.
Keep task contents, references, retained tests, IDs and order identical. This is
a disclosed post-observation engineering correction, not independent confirmation
or a new cohort. Repeat all reference checks before freezing. Report both runs'
actual usage and preserve every earlier error rather than hiding the first run.

## October 8: close the engineering tests without a superiority claim

The corrected full-cohort retest completes 57 metered generations: twelve coding
successes, ten initial math successes, one eligible math failure and one task
without a candidate. The single paired task has K=[1,1], R=[1,1], Z=[1,0]; an
oversized generic summary blocks G. Both domains fail the six-pair feasibility
screen. Report the tie and all missing/unperformed conditions without a general
rollback advantage, equivalence or lesson-benefit claim. Do not expand the cohort
according to this observed direction; a harder/longer study needs a new design.

All 700 current repository tests, six archive probes per version, independent
isolated regrading, full scientific validation and paper assembly pass. Preserve
the 115-generation combined accounting (2.1885340 calculated planning credits),
the language-gap run, the same-cohort correction and all source/evidence hashes.
Actual account charges remain unavailable; these are not independent cohorts.
The benchmark source and later stages remain unperformed; no manuscript claim
is upgraded.

## October 8: freeze a harder development cohort before further outcomes

The user asked to keep going to find useful results using the existing Luna
subscription. The earlier corrected pilot has one paired math task and no coding
pairs. Prepare 64 new tasks and change initial checkpoint/branch effort to low,
with identical medium recovery settings for all arms. Both difficulty and effort
change; do not attribute an eligibility change to effort alone or call this
held-out confirmation of the original policy. Never force an incorrect branch.

Freeze all tasks, eight excluded calibration requests and 832 possible study
identities before outcomes. Four 16-task ledgers are accounting partitions of
one fixed cohort; an unresolved call stops every later block. Complete all tasks
regardless of direction. Explicitly tell both writers the same 4,096-byte limit.
Keep subscription planning credits separate from actual account charges.

Coding has four variants of each of eight templates. Report family counts and
means and use a descriptive family interval only with six represented complete
eligible families. Do not count terminal draws or variants as independent
families. Preserve earlier bundles, public-pass stopping and all failures;
optional human ratings, benchmark tasks and manuscript upgrades remain separate.

## October 8: preserve the interrupted harder study and instrument future failures

An unknown Z terminal dispatch stops the fixed 64-task v3 study after thirteen
tasks start. Preserve all 64 dispositions, 832 task slots, 86 completed
generations including calibration and one unresolved 4.225-credit reservation.
Do not resume the allocation, retry its identity or launch its later blocks.

Five completed math pairs give K=9/10 and R=9/10, with one benefit, one drawback
and three ties. Only five pairs complete, so the new protocol's complete-pair
screen fails despite the inherited scheduled-pair flag being true. Bounds over
six scheduled pairs do not cover unstarted tasks. The full-cohort effect remains
unidentified. Six started coding tasks pass, leaving no coding recovery pair.

All 709 tests and independent archive/isolated regrading pass. Current read-only
subscription allowance is available; that does not identify the earlier generic
ProtocolError or clear its reservation. Before a distinct follow-up, capture
whitelisted protocol reason codes and event counts without credentials, provider
messages or opaque session logs. Freeze any new source and whole allocation
before outcomes; no task substitution, significance stopping or manuscript upgrade.

## October 8: freeze a separate instrumented math follow-up

The user-requested search for useful results continues with 32 new mathematical
tasks under seed 2026100851 and new identities. Math-only scope is chosen after
v3's prefix produced recovery pairs while six coding attempts passed. This is
development evidence, not confirmation or a coding-performance comparison.

Preserve actor prompts, low initial effort, medium writers/recovery, schemas,
isolation, one-generation/one-usage acceptance and no-retry unknown stopping.
Observe only whitelisted reason codes, fixed RPC/numeric codes and event counts;
never retain raw provider messages, arguments, credentials or reasoning logs.
Nine new invariant tests and 19 installed-client probes pass. Independently
certify the entire new finite task set before freezing all 424 possible calls.
The complete-pair screen is now coded separately from scheduled-pair metadata.

## October 8: close the full math follow-up with a qualified resource result

The fixed 32-task allocation completes without unknown calls: 27 recovery pairs,
three initial successes, one malformed branch and one task without a candidate.
All four recovery arms have 54 known draws. R=47/54 and K=46/54 give +1.85 pp,
with a conditional descriptive task interval [-7.41,+11.11] pp. Four task-level
benefits, three drawbacks and twenty ties establish neither a reliable quality
advantage nor equivalence. Do not enlarge this cohort to seek a positive mean.

Actual matched terminal inputs total 171,406 tokens in R versus 181,170 in K,
a 5.39% reduction under this serialization/client. Keep those recorded calls
separate from standalone policy projections, complete-policy costs, stochastic
output differences and actual account charges. Study plus excluded calibration
usage is 7.5049380 calculated planning credits, with no API-key spend; v3's
unknown reservation remains unresolved and separate.

The first K-better case retains an explicitly unverified impossibility hypothesis
in both the lesson and generic summary. Public enumeration finds 24 satisfying
assignments, so deleting the trial record does not erase every branch-derived
hypothesis. Treat possible anchoring as an untested mechanism; optional independent
ratings and a lesson ablation remain unperformed. A new ablation requires a new
frozen design rather than silently changing this completed study.

After all model calls ended, repair the public package README's relative-link
typo. Preserve the original bytes in commit 1e927f8 and replay the unchanged
original verifier from that source: all 93 source bindings, 819 evidence files,
416 task slots, durable accounting, 345 unique threads and candidate regrading
pass. All 718 repository tests and two replay-boundary tests pass. Preserve all
earlier archives and leave C75, draft v0.42 and benchmark work unchanged.

Final full scientific validation, paper assembly and catalog checks pass. Seal
the post-outcome package inventory including durable ledgers and check records;
keep it distinct from the immutable pre-outcome source and launch freeze.

## October 8, 2026: prepare staged development before increasing confirmation size

The user requests implementation of the proposed development tasks and parallel
Luna setup, with the model launch to follow. Build a separate v5 package and
48-task cohort instead of extending the completed v4 allocation. Preserve its
observations, historical sources and the unresolved v3 reservation.

Use four authored families (scheduling, routing, event-ledger repair, dependency
resolver repair), two difficulty settings, three disclosure/action horizons and
two replicates per cell. The short control needs one disclosure and two actions
so a failed first proposal leaves a genuine recovery opportunity. Medium and
long have four/eight disclosures and ten/thirty actions. Horizon alters timing
and allowed computation together, so no pure text-length causal claim follows.
Every model stage is medium effort; future difficulty calibration uses control
performance, not selection for an observed rollback benefit.

Separate a shared-failure mechanism track from independently started complete
policies and a repeated-compression track. Keep K/R, removal alone, generic
summary and a fresh solve from released public evidence. Add the same mechanical
receipt lesson to both KE/RE as a separately labelled lesson ablation. Every
future packet and reserved expected output stays outside actor access.

Parallelize independent episodes with a central atomic ledger, four workers by
default and an eight-worker maximum. Dependent steps and shared writers remain
ordered; unknown dispatch stops new admission and drains already admitted calls.
Freeze every possible identity, preserve non-execution dispositions, and never
retry a dispatched identity or reuse an old allocation. The eight live format
checks are excluded calibration and belong only to a future explicit launch.
Preparation uses reference checks, local mock client probes and clearly labelled
scripted simulations; none supplies model evidence or a manuscript upgrade.

## October 8, 2026: launch the fixed staged-development allocation

The user explicitly approves sending the 48 authored v5 task payloads through
the existing Codex subscription and using at most 13,640 generations, including
eight excluded calibration calls. Use Luna medium and four workers for all three
frozen tracks. Fresh reference execution, Docker isolation and installed-client
checks pass without source/client drift. This permission applies to the new v5
freeze and does not reopen historical allocations or unknown reservations.

Run the entire fixed cohort or honor its prespecified infrastructure stop; never
retry a dispatched identity. Finish offline replay and accounting reconciliation
before reporting final effects. Preserve all controls, ineligible prefixes,
malformed received outputs, capacity failures and missing outcomes. Do not change
the cohort or allocation in response to observed rollback performance. The
[live result record](../experiments/dependency_memory/results/rollback_development_v5_2026-10-08/LIVE_RUN.md)
will distinguish preparation, scripted rehearsal and model observations.

## October 8, 2026: preserve the staged-development stop and its permanent gaps

The approved v5 launch completes its eight excluded calibration calls and then
stops after 227 metered study completions and one unknown policy K action on
`v5-ledger-long-hard-2`. Already admitted calls drain; no identity is retried.
The exact safe transport diagnostic was not persisted beyond its exception class.
Preserve its 4.225 planning-credit reservation and the unknown request. The
allocation remains closed even though the user requested the complete test suite.

No complete R/K pair exists in any track. Report fixed-denominator missingness
bounds, all controls and unstarted outcomes; raw R/K pass counts are different
task subsets and cannot show an advantage. Three common prefixes ran: two initial
successes and one eligible mismatch, with all matched continuations unstarted.
Correct the frozen analysis's unstarted-prefix label defect in an explicitly
separate diagnostic, without editing its original bytes or primary denominators.

Independent live replay/accounting, all 744 distinct offline repository tests,
fresh task/client checks and full scientific validation pass. Keep sandbox test
failures and exact passing rechecks visible. A later allocation needs safe error
diagnostic retention, earlier paired coverage and a separately reviewed freeze;
neither improvement retrospectively resolves the missing outcome. The
[finding](../research/ROLLBACK_STAGED_DEVELOPMENT_2026-10-08.md) records the evidence.

## October 8, 2026: continue v5 under the user's explicit amendment

The user rejects the global-unknown stop and explicitly requests amending it so
all experiments run, authorizing thousands of Luna calls for useful results.
This supersedes the earlier v5 closed-allocation decision. Its original phase,
unknown request/reservation, completed results and frozen source remain intact.

Use the [continuation amendment](../experiments/dependency_memory/rollback_development_v5_continuation/PROTOCOL.md):
an unknown response ends that trajectory while independent jobs continue. Import
receipts into a fresh cumulative ledger, carry completed outcomes forward, and
restore healthy partial trajectories only from verified saved responses. Send
only never-admitted identities. Reuse the eight passed calibration identities;
refresh client mocks without additional calibration generations. Retain all
48 tasks, 768 jobs, four workers and Luna medium, with original admissions counted
against the 13,640 ceiling. Account/source/isolation/invariant failures remain
global stops. Report the post-observation amendment and phase effects explicitly.

Complete the fixed cohort before judging its difficulty from controls. Any task
redesign needs new IDs and a separate bounded freeze; a useful negative result
does not require a favorable rollback effect. The user's live authorization
already covers this continuation; no further permission gate is imposed.
## October 9, 2026: preserve the completed v5 ceiling result

The user-authorized amendment finishes every runnable job without a repeated
identity: 2,124 metered completions and four retained unknowns. Independent
replay/regrading reconciles all calls, 453 executed jobs, 315 ineligible
continuations and every fixed slot. No global stop or unstarted runnable job
remains; all 754 distinct tests have passing results after two unchanged Windows
rechecks. Original phase bytes and its unresolved reservation remain intact.

Policy has 46 complete R/K pairs with one benefit, one drawback and 44 ties;
memory has 48 all-success ties; three mechanism pairs also tie at success.
Report zero means, policy interval [-6.52,+6.52] pp, fixed-denominator bounds
[-2.08,+2.08] pp and the memory ceiling explicitly. A zero bootstrap interval
from all-success observed outcomes is not equivalence. All twelve K/F cells
exceed the 40–75% target; nominal long controls usually use eight actions and
only 2–3 KB median raw history. Retain this calibration failure rather than
changing the fixed cohort to produce a favorable effect.

On complete pairs, R input-token totals change by -34.62% in the three-task
mechanism set, +5.17% in policy and +4.22% in memory. Keep conditional resource
reductions separate from whole-policy and compression results; planning credits
are calculated units, not charges. A harder cohort, semantic ratings and
confirmation remain unperformed. C75 and manuscript v0.42 are unchanged. The
[dated finding](../research/ROLLBACK_STAGED_CONTINUATION_2026-10-09.md) is the entry point.

## October 9, 2026: calibrate new questions without selecting for a rollback win

The user asks for harder questions and an efficient testing environment. Add the
separate [v6 challenge package](../experiments/dependency_memory/rollback_challenge_v6/README.md),
preserving all v5 sources and results. Constraint grids, finite bitvector programs
and revision ledgers have exact public graders and independent reference checks.
Their levels remain difficulty hypotheses until live control observations exist.

Screen K/F only, validate nominated cells on new seeds, then freeze an independent
fixed-size R/K comparison. Do not select or extend tasks based on treatment gains
or a p-value. Keep missing scores missing and disable confirmatory inference when
selected paired outcomes are incomplete. All other comparisons are descriptive.
Statistical significance cannot be guaranteed by engineering the environment.

The concrete initial preparation has eighteen tasks, three stages, five actions,
and at most 252 generations including writers. Live model/budget choices remain
pending; the current artifacts contain only offline fixtures and power calculations.
Use the existing subscription route provisionally, without API purchases or model
fallbacks. A later larger validation/confirmation allocation must be separately
bounded. See the [dated preparation note](../research/ROLLBACK_CHALLENGE_PREPARATION_2026-10-09.md).

Before any live v6 generation, the offline size probe finds reachable capacity
stops with maximum-size notes/lessons, although all tested concise paths fit.
Keep such failures in end-to-end scores and fixed denominators, but do not use
them to establish that a question is difficult for the model. Screening cannot
nominate a cell with a K/F capacity failure; validation fails the whole nominated
mixture if one appears. Preserve the earlier freezes and replay them historically;
the new `prepared_screen_v2` has the same 18 tasks and 252-generation ceiling.

The user then explicitly approves: "Run the Luna screen, capped at 252 generations."
Record that approval against the revised manifest and launch its complete fixed
K/F schedule through the existing subscription. This resolves the earlier model
and screen-budget gate. It does not authorize a larger validation or confirmation
allocation, nor extra samples selected from partial outcomes.

The completed screen admits 165 calls, with 161 metered completions and four
unknowns. Each control solves 6/16 known episodes, but the selection is empty.
Ninety-two of 154 received actions defer a candidate; 17 of 20 known failures
never trigger the public checker. Retain this finding and the empty selection.
Prepare a separate six-task screen on new seeds, requiring a best complete
candidate each action and explicitly forbidding intentional wrong attempts.
Use bitvector level 1, grid level 2 and ledger level 2 based on the observed
control behavior, before any R outcome. Preserve the response contract through
later validation/confirmation. Its maximum 84 calls need separate authorization;
unused slots from the closed initial screen are not a transferable allocation.

The six-task follow-up is now frozen at manifest
`bdb1fd85c55aefe82fc44b3949faa76298a2e65add602ff43d5062ee4a10c7d6`.
All 33 package tests, 576 independent-formulation task checks, 259 scientific
validation categories, installed-client probes and the 54-response fixture replay
pass. Historical-source replay also preserves the initial screen's 161 known
calls and four unknowns. Register the [prepared follow-up](../experiments/dependency_memory/results/rollback_challenge_v6_candidates_2026-10-09/README.md)
separately and request its 84-generation allocation; no follow-up model calls
have been made at this preparation checkpoint.

The user subsequently says: "Stop asking me to approve this you can use thousands
of luna requests it doesnt matter." Treat this as authorization for the Luna
development screens, independent difficulty validation and fixed-size rollback
comparison needed for the research goal, without per-run reconfirmation. Adopt
a transparent 6,000-additional-admission working ceiling within that broad
authorization; this exact number is an agent accounting choice, not a quoted
user cap. Include writers and unknowns. Keep each cohort frozen before dispatch,
selection restricted to controls, and the confirmatory sample fixed before R/K
outcomes. Launch the prepared 84-generation candidate-required screen now.
The [authorization record](../experiments/dependency_memory/results/rollback_challenge_v6_candidates_2026-10-09/campaign_authorization.json)
supersedes the earlier pending-approval state without reopening any closed run.

The candidate-required screen finishes with 56 metered calls, no unknowns,
K=5/6 and F=4/6. All 49 actions submit candidates, but its original selection
remains empty. Ledger level 2 has K=1/2, F=2/2 and public mismatches in both K
episodes. This motivates a prospective calibration change, before any R outcome:
allow F to establish solvability at ceiling while retaining K's required
headroom. Preserve the old gate and empty selection; do not relabel inspected
tasks as an eligible cohort. Freeze `allow_fresh_ceiling=true` in a new screen
and inherit it in validation/confirmation. K retains its old rate bounds; F
retains its lower bounds, completeness and capacity requirements. Public
mismatches and whole-mixture validation remain required.

The [new screen](../experiments/dependency_memory/results/rollback_challenge_v6_headroom_2026-10-09/README.md)
has levels 2 and 3 from all three families, four replicates each, seed
2026100959, three stages/five actions and a 336-generation ceiling. Use sixteen
independent validation tasks per nominated cell. Its 37 package tests, 2,304
independent-formulation task checks and 216-response fixture replay pass before
launch. Historical-source replay preserves all 56 completed follow-up calls.
The campaign records 56 admissions plus 336 reserved against its 6,000-call
working ceiling. This is control-informed design development, not a rollback
benefit or a guarantee of a qualifying distribution.

Before any v6 R-arm observation, prepare a separate conservative inference
option for missing terminal scores. The [completion bound](../experiments/dependency_memory/results/rollback_missingness_bound_2026-10-09/README.md)
maximizes the existing exact paired-test p-value over every feasible binary
completion and retains sharp fixed-denominator missingness bounds. Five tests
and 1,118,481 enumerated complete assignments support the implementation; the
general justification is an elementary supremum-p-value argument, not a novelty
claim. This never lowers the complete-case p-value or imputes/retries a missing
score. Applying it to a future confirmation requires a separately source-bound
analysis amendment before the first confirmatory dispatch. Existing reports and
the live control screen stay unchanged. Complete-observation power assumptions
must not be presented as power guarantees under arbitrary missingness.

Freeze the [prospective confirmation amendment](../experiments/dependency_memory/results/rollback_challenge_v6_headroom_2026-10-09/confirmation_analysis_precommit.json)
while the 24-question control screen is running and no v6 R-arm outcome exists.
The future single primary decision is the worst-completion exact two-sided test
at alpha 1/20, with the original complete-observation power plan and fixed sample
rounding rule. It reduces to the original test for complete data. Keep the
engine's report unchanged and produce a separately labelled amendment report;
bind the exact selected cohort and analysis source before its first R/K call.
Do not infer significance from an unresolved source, information-access or
accounting stop, or extend the sample in response to any observed p-value.

## October 9: failed five-action validation and new six-action screen

The independently replayed ledger validation has K=3/16 and F=7/16, with 190
known calls and no missing outcomes. Preserve the failed frozen gate; do not
advance its selection to confirmation. Twelve of thirteen K failures had
passed two stages. Test one additional action on eight new tasks, keeping the
three-stage generator, information contract and candidate requirement unchanged.
The [new freeze](../experiments/dependency_memory/results/rollback_challenge_v6_six_actions_2026-10-09/README.md)
uses seed 2026100987 and at most 136 K/F calls. Require sixteen new validation
tasks if it screens successfully, then a new fixed 260-pair comparison. This is
control-informed development with no R outcomes, not evidence that the extra
action helps. No completed allocation or negative selection is changed.

Raise the assistant-selected working ceiling from 6,000 to 8,000 within the
user's explicit authorization for thousands of Luna requests. The complete
possible screen, validation and six-action confirmation total 6,691 admissions
including the 563 already used. This is an accounting amendment, not a request
for another approval or an exact number specified by the user. No purchases,
API fallback, unknown retries or significance-dependent sample extensions.
The separately frozen missingness inference rule and fixed power assumptions
remain; bind the exact future cohort before its first R/K dispatch.

## October 9: intermediate ledger profile and bounded missing controls

The closed six-action screen has K=2/8 and F=5/7 known, with one missing F
score and 104 admissions. Its original complete-outcome selection stays empty.
Both original-source and historical replay pass. Reducing question size is the
next control-informed change: the new intermediate ledger profile has
22/28/34 transaction IDs over 5/6/7 accounts, preserving original revision and
amount rules. The standard profile and its identities are unchanged. The new
screen uses eight level-2 tasks, seed 2026101001, three stages and five actions,
with at most 112 K/F calls. No v6 R-arm outcome has been observed.

For newly frozen controls, require at least seven eighths of scheduled scores
observed and every binary completion to satisfy the original rate bounds.
Screening requires at least eight scheduled tasks per arm/cell; validation
requires sixteen. Mismatches use scheduled denominators, capacity failures and
global stops remain disqualifying, and the whole mixture must pass. This is a
conservative fixed-denominator missingness check, not favorable imputation,
retry, confidence interval or retroactive reclassification. The new flag and
size profile are inherited unchanged. All 42 package tests, 768 independent
task checks and the 72-response replay pass before launch. Full scientific
validation is being rerun after the source changes. The campaign records 667
prior admissions against the existing 8,000-call assistant working ceiling.

The 28-transaction screen closes with K=F=8/8 and all 68 calls known; its K
ceiling disqualifies it. Audit passes, and the empty selection is preserved.
Next use eight new intermediate-profile level-3 tasks (34 IDs, seven accounts,
up to five revisions and amounts through 200), seed 2026101011, three stages
and five actions, maximum 112 calls. These are multiple task-distribution
parameters, not an isolated count effect. No source change is needed: the
42-test implementation and all source bindings are identical. The campaign
now has 735 admissions; no R outcome has been observed.

The 34-transaction screen finishes with K=3/8, F=5/8 and 88 known calls;
independent replay passes and the cell qualifies. Preserve its wide uncertainty
and K point rate below the later validation minimum. Proceed to sixteen new
validation tasks (seed 2026101023), retaining all generator, action and access
settings and the conservative missing-control gate. The 32 K/F episodes have
a 224-call bound. All 1,536 task checks and the 144-response replay pass;
the unchanged source has 42 passing package tests and 259 passing scientific
check categories. The campaign has 823 prior admissions, including one unknown.
No v6 R-arm observation or rollback-effect estimate exists.

The independent 34-transaction validation closes with K=5/16 and F=9/16,
181 known calls and passing replay. Its K lower-bound gate fails and remains
closed. Next test eight new 28-transaction level-2 tasks with four actions over
three stages (seed 2026101037, maximum 88 calls). In the earlier five-action
28-transaction run, six K and seven F episodes finished within four actions.
These are observed completion timings, not counterfactual four-action outcomes;
remaining-action prompts can change behavior. The new design must screen and
validate independently. No source change is needed, and no R outcome exists.
The campaign records 1,004 admissions, including the earlier unknown, against
the unchanged 8,000-call assistant working ceiling.

The new four-action screen qualifies at K=5/8 and F=7/8, with 60 known calls
and passing replay. Proceed to sixteen new validation tasks using seed
2026101049 and the identical three-stage/four-action intermediate level-2
setting. The 32 K/F episodes have a 176-call bound; all 1,536 task checks and
the 144-response rehearsal pass. The full unchanged-source unittest suite
finishes with 792 passes and nine optional Docker skips; 259 scientific check
categories and paper assembly pass. The campaign has 1,064 prior admissions,
including the earlier unknown. No R outcome is available or used in this choice.

The independent four-action validation passes with K=9/16 and F=12/16,
130 known calls and passing replay. Thirteen K episodes have public mismatches;
there are no capacity or malformed-record failures. Freeze exactly 260 new
R/K pairs (seed 2026101063), three stages/four actions, intermediate level 2,
and a full 3,640-generation bound. Bind the prior maximum-completion exact-test
amendment, its source/proof, cohort and source snapshot in the
[confirmation envelope](../experiments/dependency_memory/results/rollback_challenge_v6_four_actions_confirmation_2026-10-09/confirmation_envelope.json) before first
live R dispatch. The 2,600-response rehearsal passes. No R observation informed
this choice; no interim effects, significance stopping or sample extension is
allowed. The standing human authorization covers this allocation, with 1,194
prior campaign admissions and 4,834 used/reserved against the 8,000-call ceiling.

The fixed 260-task comparison closes at 2026-10-10T03:09:05.759896+00:00 with the result
recorded in [LIVE_RUN](../experiments/dependency_memory/results/rollback_challenge_v6_four_actions_confirmation_2026-10-09/LIVE_RUN.md). K succeeds on 122/254 known
tasks and R on 64/258. Replay passes for 2,496 responses; eight unknowns are
preserved. The worst-completion paired p-value is 2.4820775e-7, with R lower
under every feasible completion. Report this negative result and finish the
fixed study; do not extend the sample or seek a favorable replacement cohort.
The full campaign uses 3,698 admissions, including nine unknowns. The result
concerns whole-history deletion with lesson retention on one authored family,
not every possible rollback design or an isolated mechanism diagnosis.

## October 12: preserve the pre-failure information in a new rollback pilot

The user's review of the v6 result exposed a construct limitation: history
deletion removes old public transaction packets, while the accepted balance
vector does not preserve transaction-level facts needed for later revisions.
This explains an available information-loss path; it does not apportion the
observed deficit among causes or invalidate the measured whole-policy result.

Create [v7](../experiments/dependency_memory/rollback_checkpoint_v7/PROTOCOL.md)
as a new study without editing frozen v4-v6 evidence. Save the exact successful
pre-failure checkpoint and retain every released packet separately from model
trials. At the first natural rejection, generate one common lesson and compare
K with R from that same failure. Only the failed visible trial differs. Both
requests must fit and match byte-for-byte after removing that trial; independent
source comparisons also reject a symmetric omission from both requests.

Freeze 24 new intermediate level-2 ledgers with three stages, four actions,
seed 2026101267, eight workers and a 192-admission ceiling. Run the fixed pilot
under existing subscription authorization, with no retry, replacement or
sample extension. Prefix/writer unknowns prevent their dependent pairs; arm
unknowns stay missing while independent work continues. Account, source,
isolation and accounting faults stop admission globally. Offline oracle
fixtures are controller checks, not model observations.

Report all prefix dispositions and conditional paired recovery, with separate
shared-prefix costs and branch-size diagnostics. Six complete pairs permits
only a descriptive bootstrap interval, not a confirmatory claim. Shared lessons
may retain branch-derived details, and private reasoning is inaccessible. Full
evidence access differs from v6; do not attribute cross-study rate changes to a
single repair or update manuscript claim C75 from this small pilot.

The [completed pilot](../experiments/dependency_memory/results/rollback_checkpoint_v7_2026-10-12/LIVE_PILOT.md)
has 16 complete eligible pairs: K=10/16, R=8/16, three K-only and one R-only
success. All 130 admitted calls completed, peak concurrency was eight, and
frozen-source replay plus 114 independent action grades pass. Retain the
negative point estimate and wide descriptive interval; do not extend the
allocation or turn this development check into confirmation.

Preserve the initial zero-admission preflight failure. The installed client
advertised three generic resource helpers; the v7-only compatibility adapter
pins their declarations and checks an empty disabled inventory. Freeze the
amended source before calls, keeping the same cohort. Record the separate
clock-plus-answer diagnostic as an observation limitation: the one-generation
boundary prevents consumption of a later tool result, but tool-attempt
observability is not universal. Historical transport modules stay unchanged.

A post hoc literal check finds the failed balance vector in 15/16 shared
lessons. This was permitted by the frozen protocol, but the result therefore
concerns raw-record retention conditional on a lesson, often retaining the
same incorrect values. A future study should separate branch removal from
lesson content and use substantive visible failed work; a sufficient-memory
comparison is a distinct experiment. Those studies remain unperformed.

After the live allocation closed, repair only v7 test import paths for normal
repository-root discovery. Preserve the archived source snapshot for replay;
do not rewrite frozen manifests or raw results to match later test maintenance.

## October 13: improve execution and keep the rollback question explicit

The user's request for more workers leads to a separately frozen v8 engineering
allocation: a 64-call ABBA speed check followed by a 24-task pipeline capped at
192 calls. Keep the v7 prompts and intervention unchanged so scheduling work
does not silently become a new scientific treatment. Use sixteen workers,
durably release continuations after their own prefixes, retain bounded identity
admissions and stream complete executable hashes through a 1 MiB buffer.

The user explicitly renewed permission to send the synthetic prompts through
the existing Luna subscription, authorized thousands of calls and higher
parallelism, and asked for faster execution. Do not request per-run permission
again within that scope. Each new allocation still fixes its own cohort, access
contract, worker count and call ceiling before dispatch. The completed v8
allocation uses 200 admissions, with 199 known and one unknown; no retry or
extension. It does not open an API-key route or purchase credits.

The live speed comparison records 71.802 pooled seconds at eight workers versus
52.879 at sixteen, a descriptive 26.36% reduction. Cache, output, provider/order
effects and concurrent offline host validation limit causal interpretation.
The pipeline reaches sixteen admissions and starts 49 continuation calls before
the last prefix completion. Frozen-source audits and all 902 test dispositions
reconcile; nine optional Docker tests skip. Source and hash-memory changes have
separate offline diagnostics. [Completed engineering evidence](../experiments/dependency_memory/results/rollback_parallel_v8_2026-10-13/README.md).

The [information audit](../research/ROLLBACK_INFORMATION_BOUNDARY_2026-10-13.md)
clarifies the scientific target. Both v7 arms already retain the accepted
artifact; a failed candidate never overwrites it. The shared lesson repeats the
failed vector in 15/16 pairs. Post hoc eventual repair is 14/16 in each arm,
whereas immediate repair is 13/16 versus 10/16 and final completion 10/16 versus
8/16. Four actions for three stages leave no spare action after the shared
failure. Do not interpret every terminal failure as information becoming
unavailable or the test as rollback of private reasoning or a damaged workspace.

The next scientific proposal should separate raw-record retention, lesson
content and compact-state sufficiency. It should use substantive visible work
and report immediate recovery, later-stage errors and complete-policy resources.
It remains unperformed. V8's K=11/19 versus R=8/19 is descriptive engineering
evidence under the same limited intervention; do not pool it into a retroactive
confirmatory test or upgrade manuscript C75.


## October 13, 2026 — Separate larger-project rollback calibration

The resumed v9 live calibration produced sixteen initial patches, all passing
public and private tests. Its predeclared main-study gate therefore fails;
there is no factorial effect to interpret. Preserve its source and all results.
Under the user's renewed subscription authorization, prepare a separate v10
study with eight-component, two-file Python projects. Keep all specifications,
original code, examples and public feedback available. Cross failed-patch
deletion with categorical lesson presence, and allow three repairs of the same
task. Workspace restoration is identical in all arms.

Difficulty changes are informed by control-only task feasibility, before any
rollback outcomes. Calibration and main study use distinct seeded pools;
components recur within each allocation, so task-level bootstrap intervals are
descriptive and do not remove dependence. Coarse lesson categories cannot name
a particular component. Increase the new version's complete request-body bound
consistently in both controller and transport, including JSON escaping and
later patch history, while preserving old adapters. This avoids a client-size
artifact being interpreted as useful information deletion. No source packets,
patches or feedback are truncated to fit.


## October 13, 2026 — Explicit exploratory departure after v10 shortfall

V10 produced three substantive natural failures among sixteen prefixes, and
all three retained/no-lesson controls repaired correctly on the next attempt.
All 22 calls and replay are known; no capacity stops occurred. The original
four-failure feasibility rule fails and its main allocation remains closed.

Before observing any deletion or lesson-arm outcome, freeze a separate v11
exploratory cohort of 256 fresh tasks at seed 2026101312, with a 3,584-call
ceiling and the same four-arm intervention. This is an explicitly unplanned,
control-informed relaxation of the feasibility policy, not the originally
gated study or confirmatory evidence. Preserve the original failed gate inside
the new manifest; verify its only failure is the original headroom minimum.
All outcomes, missingness and component-family concentration must be reported.
Do not extend or replace the cohort based on treatment outcomes.

The client also has a one-million-character input limit. Enforce a conservative
1,048,576 UTF-8 request-text byte cap as well as the 4 MiB complete-body bound.
Complete ordinary histories fit; pathological histories may not. Any capacity
stop prevents interpreting a contrast as an isolated content effect. Never
truncate task facts, patches or feedback to fit.


## October 13, 2026 — Resume only unsent v11 work after client RPC stop

The initial v11 phase sealed 289 admissions (284 completed, five unknown)
before an internal account/rateLimits/read RPC error stopped admission. A
separate native check found ordinary included usage available (21% weekly
used). Original-source replay reconstructed every admission and all 256 task
dispositions. Only counts and transport diagnostics were inspected before
this recovery decision; no four-arm scores or contrasts informed it.

Freeze an [operational amendment](../experiments/dependency_memory/rollback_patch_v11_resume/PROTOCOL.md)
to finish the original cohort. Retain all terminal and unknown-containing
jobs; reconstruct healthy partial trajectories from their exact saved receipts
and dispatch only never-admitted identities. Preserve every old row and receipt,
the original 3,584-call cumulative ceiling and all five unknown calls. The
client's global-stop classification remains unchanged. This is no new cohort
or treatment change. The historical global stop permanently fails the original
isolated-content interpretation gate, even if recovery completes; report
exploratory descriptions and missingness bounds with that limitation.


## October 13, 2026 — Close the patch factorial with a repair ceiling

The original 256-task v11 allocation is complete across two sealed phases:
417 admissions, 408 known responses and nine preserved unknowns. Every call and
received patch replays; cumulative and independent arithmetic audits pass.
Twenty-eight eligible failures yield K0 27/27 known (+1 missing), R0 27/27
(+1 missing), KL 28/28 and RL 27/28. No deletion advantage is observed. Do not
interpret near-universal repair or all-tie bootstrap intervals as equivalence,
and do not extend the cohort to obtain a desired contrast.

The one failed RL trajectory disabled refund handling that the initial failed
patch had already corrected. Its original dependency defect was fixed later,
but the refund regression persisted. This establishes the content of one lost
partial fix and one subsequent regression, not a causal mediation result; R0
also deleted the patch and succeeded. The complete task specification remained
available in every arm. The lesson treatment is presence of a coarse categorical
hint, not a general test of lesson semantic quality or complete progress summaries.

Keep the original global-stop interpretation gate failed. The earlier v10
feasibility departure, related authored tasks, unknown prefix eligibility,
missing arm outcomes, provider revision uncertainty and repair ceiling remain
visible in the [result report](../experiments/dependency_memory/results/rollback_patch_v11_2026-10-13/README.md).
Posthoc source/component inspections are diagnostics on the same saved data,
not additional model trials or new confirmatory endpoints. No paper claim is
upgraded from these exploratory observations.
