# Retained evidence and final decisions

October 1, 2026. **Completed post-hoc offline investigation; zero new model calls.**
The [protocol](../experiments/dependency_memory/evidence_use/PROTOCOL.md) was
committed at `24da0e1` before the new interpreter was implemented. The historical
outcomes were already inspected; this is not preregistration or held-out evidence.
The implementation/result milestone is `eeec334`.

## What was audited

The [new report](../experiments/dependency_memory/results/evidence_use_2026-10-01/report.md)
reconstructs all scheduled terminal identities in the September 22 cross-record
study and both September 29 workflow comparisons. Its source lock pins 470
historical input files. There are 368 scheduled finals, 319 observed answers,
three permanent transport gaps and 46 never-dispatched finals. The 82
never-dispatched **requests** in the executed study include writer requests and
must not be confused with 46 never-dispatched **finals**. All original missing
dispositions, graders, writer costs and primary criteria remain unchanged.

The 319 answers contain 53 errors:

| Retrospective diagnosis | Errors | Meaning |
|---|---:|---|
| Wrong proposal despite matching retained readout | 31 | The public rule applied to typed admitted memory gives the full-ledger answer, but the model proposal differs. |
| Reviewed retained obligation misused | 1 | A bounded human reading confirms the prose kept the repository success omitted by the final answer. |
| Retained readout disagrees with full ledger | 1 | The admitted retry state is already wrong; another final readout alone does not repair it. |
| Empty terminal memory | 17 | No instance record survives in the final memory; these are separately diagnosed rather than treated as prose parsing failures. |
| Uncheckable representation | 3 | The new typed parser cannot decide semantic sufficiency; unknown is not proof of information loss. |

These pooled counts reconcile correlated development observations. They do not
estimate independent task prevalence. The three included studies were selected
by recency and terminal-task relevance, not by choosing favorable failures;
earlier release and schema-transfer pilots are outside this first audit. [C53]

## Actor-side intervention and measured limits

The [new guard](../experiments/dependency_memory/evidence_use/guard.py) receives
only a saved final request and answer. It interprets the already public receipt,
retry, CI and data-job rules from typed retained evidence. It does not import a
grader, read source/evaluator files, recover archives or call a model. The rule
compilers are hand-written; unfamiliar-workflow contract inference is unperformed.

It marks 32 wrong proposals contradicted. Of these, 31 have a correct derived
readout and one has an incorrect derived readout because the memory state is
wrong. No correct proposal is contradicted in these saved answers, but **39
correct proposals are uncheckable**. There are also 21 wrong uncheckable proposals.
Thus a policy releasing only consistent original proposals would retain 227
correct answers and withhold 92 others, including those 39 correct answers.
Neither withholding a wrong answer nor producing a hypothetical readout is a
measured repaired/executed task.

Across the 259 parseable final views, the separately graded deterministic readout
matches the original full-ledger answer 258 times. For the cross-record automatic,
direct and full-history arms it matches 36/36 each, versus their model answers'
29/36, 32/36 and 30/36. This diagnoses the constructed public-rule benchmark; it
does not establish an automatic compiler, general agent improvement or novelty.
Readout agreement is an instance-level calculation, not authentication or a
certificate of source coverage. [C53]

The [batched resource measurement](../experiments/dependency_memory/results/evidence_use_2026-10-01/measurement.json)
records 50 passes over 319 final checks. CPU and elapsed time are measured
separately; compact request/proposal traffic is 1,741,509 bytes per pass and
result traffic 65,282 bytes. Instructions and public state count in those bytes.
Evidence loading, evaluator grading, I/O, model calls and human rule compilation
are outside the timing. Local prices and production total cost are unknown.
The offline replay dispatches no provider request. Research-conversation usage
is outside this experiment's accounting.

## Four concrete reduced examples

The [witness artifact](../experiments/dependency_memory/results/evidence_use_2026-10-01/witnesses.json)
reduces four inspected final memories while preserving their public rule, target,
late event/state and diagnostic. It preserves exact identifiers and original
memory hashes. These reductions are not new samples.

1. `data_pipeline-1854593748-0-automatic`: the model proposes `publish`, although
   retained consent applies to another output; the rule requires `hold` with
   `approval_scope`.
2. `ci_promotion-3868710405-1-structured`: the proposal changes the correct ID
   `d36c6488ddb87bfc` to `d36c6488ddb87fbc`; the action and work list are otherwise
   correct.
3. `tests_recovery-direct-final`: the model requests a rerun despite a successful
   203-byte receipt; the retained-rule readout is ready with that exact run ID.
4. `retry_queue-215957210-0-structured`: `retry_policy.retry_allowed` is false in
   the parent and child, but true in the pinned source for request
   `5e61818b12a903c5`. A hindsight parent probe already disagrees with the source.
   The new readout holds rather than performing the correct retry. This is the
   concrete case that final interpretation cannot repair.

## Why retained consistency cannot certify completeness

The independent controls construct two histories with the same public source
snapshot and final inventory. One has a successful test receipt. The other has
that success followed by a failed run. If compaction keeps only the success,
both give the guard exactly the same memory, public task and proposed ready
answer. The full-ledger grader requires different answers. Any deterministic
check restricted to those identical inputs gives the same verdict in both.
Our guard returns consistent and explicitly reports that completeness is not
certified. A well-formed forged receipt likewise is not authenticated. [C54]

A source-coverage/lineage assertion could change the inputs, but it would be an
additional channel with provenance, a byte count and prospective checks. It is
not silently added to the replay. This is an elementary indistinguishability
example within the declared receipt contract, not a new general impossibility
theorem. Another control shows that a correct hold proposal can be contradicted
when the retained memory has omitted the later failure.

## Focused primary-source comparison

Read October 1, 2026; bounded scope, no replication or inherited review upgrade.

| Source and read scope | Relevant precedent | Consequence for this phase |
|---|---|---|
| [TierMem v1](https://arxiv.org/html/2602.17913v1), Sections 2.1–2.2, 3.1–3.2, 4.1.2 and 5.6 | Provenance-linked summaries, selective raw-log escalation, omission-versus-reasoning diagnostics and query-phase routing cost. | Generic sufficiency routing and evidence recovery are already prior art. A complete lifecycle-cost comparison remains our prospective requirement. |
| [Mem2ActBench](https://aclanthology.org/2026.acl-long.370.pdf), abstract, Section 3.3 and Sections 4.1–4.2 | Synthesized evolving memory chains and memory-dependent tool parameters; the main evaluation supplies the ground-truth tool. | Useful evaluation precedent, but it does not supply our untouched repository task stream or establish repeated irreversible-handoff performance. |

The earlier [feedback prior-art review](FEEDBACK_PRIOR_ART_2026-09-22.md) already
records structural checking, restored continuations and recovery precedents.
This new comparison narrows the claim further: a hand-written interpreter of
known public rules is a control, not a new verification method. [@tiermem2026;
@mem2act2026]

## Next experimental step

The user selected **ContextResearch as the sole working repository**. The
[segmented intake](../experiments/dependency_memory/workflow_intake/README.md)
keeps method development, actual task observations, evaluator manifests and
actor serialization distinct within it. Capture consecutive actual whole tasks,
source snapshots and delayed obligations under the
[intake contract](../experiments/dependency_memory/evidence_use/INTAKE.md).
The local collector records this actual research task at two source checkpoints;
it remains familiar inspected development evidence. Future tasks can support a
prospective observed comparison after method/grader freeze. Folder separation
does not make them independent blind tasks. The twelve private evaluation
episodes in the old packet remain uncollected.

Freeze a prospective comparison after intake and independent grader review.
Compare raw answers, consistency vetoes/abstentions and any actual repair as
separate outcomes. Preserve direct, indexed, prose and full-history controls,
count every contract-extraction/check/recovery/model cost, and budget any coverage
state. Unfamiliar-workflow contract inference is the open mechanism; all public
rule compilers and old fixtures stay development controls.

## Validation

Twenty new tests cover independent public-rule comparisons, omission/forgery,
correct-proposal vetoes, unknown prose, exact IDs, joins, late events, types,
duplicate keys/paths and missing ledgers. The independent comparisons include
210 receipt conditions, 252 fixture-row/event combinations, 36 raw-join futures
and 736 predicate combinations: 1,234 finite checks, not task samples.
At implementation checkpoint A (`eeec334`), all 430 repository tests pass. Four
additional intake tests check early/late disclosure, exclusion of evaluator
labels, UTF-8 byte caps and isolation of returned data from source objects.
Checkpoint B will validate these changes at its own pinned source revision.
The repository validator reconstructs the new analysis and reduced witnesses
and preserves every historical source hash. Paper assembly is checked separately
with the updated claim register.
