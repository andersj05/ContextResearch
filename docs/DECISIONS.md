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
