# Matched parent-retention transfer study v1

Frozen design, September 19, 2026. This is a new controlled synthetic development study. Its motivating observations are the first workflow's three strict parent-selection deficits and the separate simplified diagnostic's 24 optimal selections. Those earlier runs differ in several ways and do not by themselves identify a cause. This design compares specified changes on matched inputs.

Later operational amendment: after 888 model requests, the local percentage guard stopped the second launch. The separate [remaining-first-submissions contract](TRANSFER_CONTINUATION.md) documents a new phase for only the 648 never-dispatched cases, preserving the original sample, three dispatched failures, and cumulative 1,536-request/200-equivalent cap. Its explicit credit-backed routing policy supersedes the percentage-only and no-continuation clauses below solely for that new phase. All scientific design and analysis clauses remain in force.

Pre-generation operational amendment: launch `999f14d` stopped at all four workers' account checks before any model dispatch, because the historical local 80%-used reserve rule was exceeded. It produced zero answers, zero generation usage, and zero credit reservations. The account independently reported 85% weekly use and ordinary usage allowed. The user's explicit authorization for thousands of additional requests permits using the remaining allowance. For the new launch only, move the local threshold to 100% used while retaining actual provider denials, individual/account spend controls, and the 200-equivalent budget. No quota reset, purchase, or provider restriction is bypassed. Preserve the original stopped directory and its historical source commit; launch to a fresh directory. All 1,536 public requests, their order, and scientific analysis remain identical. This is a documented pre-generation operational correction, not an outcome-dependent extension or a retry of a dispatched model request.

## Allocation and question

The user explicitly authorized continued research using thousands of Luna requests. Bound that authorization here to **1,536 additional model requests**, **four concurrent workers**, and **200 conservative credit equivalents** through the existing ChatGPT subscription. Each worker receives 384 requests and 50 equivalents. This is separate from the completed 96- and 24-request allocations. No API billing, purchase, reset redemption, alternative model, repair call, retry, held-out request, or automatic extension is included.

The main question is whether guidance to consider future information arrivals reduces retention regret in a workflow-framed task without an explicit guarantee of an optimal later selector. A ceiling result, a null result, or a negative result is a legitimate outcome. No sample size, prompt, condition, endpoint, or exclusion is to change after observing study responses.

## Task and public information

Six or twelve jobs have revision-one receipts with opaque payloads. Before the candidate pair is known, the model chooses at most two records. The candidate pair is subsequently uniform over all unordered pairs, and the final required job is uniform within that pair. A public refresh rule supplies the latest receipt for the candidate with the minimum priority, the maximum priority, or neither. The later selector may keep two records. No candidate pair or target is actually drawn for a request: every answer is graded offline over all `n(n-1)` possible pair/target routes.

Each job has a unique public integer priority from zero through `n-1`, randomly assigned independently of its stable key. Visible-record order is independently shuffled. Metadata and response-schema keys remain in canonical order; these are declared ordering channels. Random priorities prevent a fixed key preference from implementing the rule-specific optimum. This does not claim to remove all ordering effects.

Requests contain only the allowlisted public model, current records, priorities, operational refresh rule, fixed instructions, optional fixed workflow context, and output schema. They exclude evaluator seeds, block/worker/case identifiers, factor labels, optimal keys, future pair/target data, earlier answers, and evaluator files. The host retains selected records only. Responses are constrained to selected keys; underfilled selections are legal and measured. The model receives no explanation or outcome feedback.

The later selector is not invoked in this study. Grading uses an optimal-child reference even when that skill is not promised in the prompt. Such regret measures available retention potential, not the observed behavior of an unknown downstream policy. The second boundary is nonbinding because child capacity equals the candidate count. This is an isolated early-retention experiment, not an empirical test of the bit-chain theorem, repeated native compaction, or a complete autonomous workflow.

## Frozen factorial schedule

| Factor | Values |
|---|---|
| Job count | 6, 12 |
| Framing/context | Compact task; completed-build handoff with three fixed public workflow events |
| Later-selector guarantee | Explicitly optimal; unspecified selection behavior |
| Retention guidance | Generic careful-selection guidance; prospective information-arrival guidance |
| Refresh rule | Minimum-priority candidate; maximum-priority candidate; no refresh |

The full crossing gives **48 conditions per block**. There are **32 independent generated blocks**, giving 1,536 scheduled calls. Within each block and size, the priority assignment, payloads, and visible order are shared across the 24 conditions. Condition order is shuffled within the block. Blocks are assigned to workers by `block % 4`; each worker processes its eight complete blocks serially. Execution across workers is concurrent, so global completion order is not controlled. Conditions share a block and must not be treated as independent natural-task samples.

The evaluator seed is `2026091913`; domain-separated deterministic randomization generates priorities, display order, payloads, and condition order. The model sampling seed is unavailable. The bootstrap seed is `2026091914`. All blocks are development fixtures, not a held-out evaluation. Public requests and their byte counts/hashes are recorded in the [plan](../experiments/dependency_memory/results/transfer_study_plan.json).

The compact/workflow factor is a framing and context-envelope package: the latter adds three short completed-work/timing events. It is not a realistic long transcript or an isolated wording intervention. The generic and prospective instructions are approximately length matched (30/31 words, 206/204 bytes); the prospective version asks about future information arrivals without recommending particular ranks or supplying probabilities. Both describe identical operational rules, capacities, and objective. Adding twelve jobs increases ranking and context load but does not increase the maximum raw availability penalty.

## Exact scoring and prespecified analysis

Let `S` be the selected public priority ranks and `n` the job count. Availability under the optimal-child reference is:

| Refresh | Exact availability | Best availability |
|---|---|---|
| Minimum priority | `1/2 + sum(S)/(n(n-1))` | `1/2 + (2n-3)/(n(n-1))` |
| Maximum priority | `1/2 + sum(n-1-r for r in S)/(n(n-1))` | Same |
| None | `len(S)/n` | `2/n` |

Exact regret is the best availability minus the selection's availability. For refresh cells, divide by the full-pair regret range `(2n-4)/(n(n-1))` when pooling sizes: `4/15` for six jobs and `5/33` for twelve. Underfilled answers can have normalized regret greater than one. No-refresh full pairs all tie; those cells are controls and excluded from the primary guidance comparison. Evaluated routes are deterministic scoring outcomes, not additional model observations.

**Primary comparison:** generic minus prospective normalized regret in the workflow, unspecified-child, refresh-present cells. This yields **128 matched pairs**, four within each of 32 blocks (two sizes times two refresh directions). Positive benefit favors prospective guidance. Report all paired effects, their mean, block means, and a descriptive 95% percentile interval from **5,000 fixed-seed resamples of complete blocks**. Report raw regret benefits separately by size. The interval reflects variation among these generated blocks and the sampled responses; it is not a guarantee about natural tasks, provider revisions, or future runs. No multiplicity-adjusted or unadjusted significance claim is prespecified.

Always report valid/invalid/transport-failed/incomplete counts, underfilled selections, valid-and-optimal proportions, selected keys/priorities/displayed positions, and all 48 condition summaries. Completed malformed/schema-invalid answers are policy failures and count as failures in valid-and-optimal comparisons. Exact regret is defined only for valid answers; paired regret uses both-valid pairs and the bootstrap uses fully valid blocks. Show the complete-block point estimate alongside its interval, separately from the all-valid-pair mean, and report any difference between these populations prominently. Transport-failed and incomplete cases remain visible and are not silently converted to poor choices. Secondary factorial summaries are descriptive. Any later exploratory contrast must be labeled as such.

The first eight complete blocks may support descriptive progress reporting only. There is no answer-dependent stopping, prompt revision, selective replacement, extra sampling, or selection of a new primary endpoint. The sample was chosen as a substantial matched development study, not from a formal power calculation; small differences and ceiling effects can remain unresolved.

## Transport, parallel stop, and accounting

Reuse the [reviewed subscription transport](LUNA_DEVELOPMENT_RUN.md), with the new [public interface](../experiments/dependency_memory/transfer_interface.py) and [four-worker runner](../experiments/dependency_memory/run_transfer_study.py). The dated installed-client audit pins executable version `0.155.0-alpha.9.2` and SHA-256 `bc45017e8239dc150258f69309ced9df6bbcdf5b8e4f346decf780ac0999e226`. The model is the mutable `gpt-5.6-luna` alias, low effort, default tier; record the advertised catalog entry. This verifies the selected client and observed interface, not inaccessible server internals.

Every request starts a fresh process and thread in an empty temporary directory. Fixed reviewed global instructions and three wrapper tools are declared public background. No external tools, previous session, evaluator repository access, archive, or opaque earlier reasoning state is supplied. Effective configuration, global instruction and executable hashes, public byte/schema projection, one-generation guard, model identity, and account-quota checks are mandatory. A separate unauthenticated loopback audit exercises final responses, tool attempts, HTTP errors, and broken streams; each makes one local POST and zero model calls. The [saved wire audit](../experiments/dependency_memory/results/transfer_transport_audit.json) must match the new request contract before launch.

Four serial worker budgets prevent concurrent requests from sharing a reservation. Each generation reserves **10.4025 conservative equivalents** before dispatch; a completed valid usage record releases unused reservation and settles measured token-derived planning usage. A shared lock protects the immediate reservation/dispatch gate. An observed transport, tool, usage, quota, or budget stop closes admission for all workers; requests already in flight may finish and settle. Calls that reach the closed gate do not generate. No retries or resumption of a used output directory are allowed. The first requests also serve as connection diagnostics.

The 200-equivalent ceiling is the sum of four 50-equivalent caps, including outstanding/uncertain reservations. It is not an account invoice or verified debit limit. Input tokens use the existing conservative rate of 6.25 equivalents per million and output tokens 30 per million; reasoning is included in output, cached input in total input. Optional missing cache-write measurements remain unknown. Retain raw reported usage plus exact decimal arithmetic. A complete, guarded and metered malformed answer is a charged policy failure and does not stop unrelated planned cases. Actual transport/usage uncertainty retains its reservation and stops new dispatch. Under the pre-generation amendment, this transfer study stops at 100% reported use; historical runners retain their default 80% threshold. Ordinary-usage denial, reached provider limits, and account/individual spend controls still stop dispatch. No implicit credit top-up or reset is permitted.

## Evidence freeze and reproduction

The plan fingerprints every experiment Python file, this protocol, and the separate wire audit. Freeze them in a local Git commit before model generation. Live preparation must match the stored plan to freshly computed source/request hashes and record the same approved plan hash for all four clients. Aggregate and worker manifests, initial outcome denominators, and request ledgers are persisted before any generation. Each attempt is recorded before dispatch and after completion; raw reasoning and uncontrolled session transcripts are not retained. Save all failures and incomplete cases.

Offline formula tests independently enumerate complete routes. Fake optimal, static-low-key, first-visible, and invalid controls check scoring, pairing, and failure handling. A saved-evidence auditor independently re-enumerates grades, checks request/manifest hashes, worker and aggregate limits, usage arithmetic, unique thread identities, source provenance against the frozen commit, and regenerated summaries. These are software audits, not external scientific review.

```powershell
python experiments/dependency_memory/run_transfer_study.py --plan --output experiments/dependency_memory/results/transfer_study_plan.json
python experiments/dependency_memory/run_transfer_study.py --offline-audit --output experiments/dependency_memory/results/transfer_study_audit.json
python -m unittest discover -s experiments/dependency_memory -v
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

The live launch requires an explicit allocation note and reviewed executable; it is intentionally not part of offline repository validation. Interpret completed results against this frozen design and update the living draft, manuscript, claim register, status, and decisions together.
