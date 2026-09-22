# Feedback before forgetting: executable diagnostic results

September 22, 2026. Zero model calls. All worlds and routes are constructed.

The adapter executes the existing artifact/manifest environment, grades submitted
receipts through its terminal verifier, and passes exact retained/public channels
to the collision auditor. There are two enforced record-memory boundaries.

## Main case: two parent records, two child records, no recovery

| Method | Audit outcome | Full audits | Cell checks | Constraint checks | Executed success |
|---|---|---:|---:|---:|---:|
| one_pass | rejected | 1 | 11 | 0 | 32/48 |
| enumerate | certified | 7 | 58 | 0 | 48/48 |
| last_only | cycle | 3 | 25 | 11 | no accepted candidate |
| accumulated | certified | 3 | 38 | 14 | 48/48 |
| critical_fields | certified | 1 | 24 | 0 | 48/48 |

The accumulated loop retains both unsafe-group constraints and selects job-1/job-2.
The last-only loop cycles between single-field repairs. Enumeration reaches the same
solution with more full audits, but the accumulated loop also pays constraint checks
and constructs counterfactual candidate states. These counts do not establish a CPU
speedup. The workflow-aware critical-fields baseline already chooses the solution:
**no advantage over that strong baseline is established.**

The successful memories use two records at each boundary. JSON byte lengths are in
the certificate. Each executed episode has nine mandatory environment units;
an allowed recovery adds three. Offline synthesis work is reported separately and
is never represented as free deployment work or mixed with record/bit counts.

## Binding second boundary and feedback timing

With one child record and a late target, the declared priority-selector family is exhausted_family.
Moving the target before that boundary gives certified.
This changes the information order. It does not show that feedback can reconstruct
an already lost value. Candidate-family exhaustion is not impossibility for arbitrary
encoders, as the identifier-channel control below demonstrates.

## A record identifier can carry hidden coding information

For two independent binary receipt values, choose the lower-key receipt when their
bits agree and the upper-key receipt otherwise. A public finite-catalog decoder can
then recover both values from one tagged record: the selected key carries equality
information. All 48 executable outcomes and certificate replays pass. There are FOUR
possible retained states per public route, hence two bits, despite one record slot.
Ordinary retained-receipt submission succeeds only 24/48 for this same representation.
This is a deliberate information-channel control, not practical arbitrary-token compression.

## Partial probes and late oracle feedback

Certifying only the two routes for manifest job-0/job-1 leaves a reproducible failure
on an unprobed manifest. A hypothetical 1% failure family escapes 20 independent probes
with probability (99/100)^20 = 0.817907.
That arithmetic is not a measurement of rare-task prevalence or a claim about adaptive probes.

After job-2's value is deleted, the best decoder using unchanged accessible channels
gets 4/8 worlds correct on the selected route. An oracle disclosing the missing value
gets 8/8 by adding one conditional bit under the two-value catalog. Such feedback is
a recovery channel; it cannot be excluded from the information budget.

## Capacity and recovery sweep

48 contracts cross four parent capacities, three child capacities and four archive/budget
settings. Each of five methods is run on every contract; these are deterministic
diagnostics, not 240 independent trials. Counts below summarize audit outcomes.

| Method | Certified | Rejected | Cycles | Exhausted candidate family |
|---|---:|---:|---:|---:|
| one_pass | 15 | 33 | 0 | 0 |
| enumerate | 18 | 0 | 0 | 30 |
| last_only | 15 | 0 | 15 | 18 |
| accumulated | 18 | 0 | 0 | 30 |
| critical_fields | 18 | 30 | 0 | 0 |

## Boundaries

A finite public token catalog, deliberate revision correlation, trusted Python
interfaces and hand-written selectors make this a calibration artifact. No semantic
prose compiler, natural-task distribution, LLM performance gain, complete end-to-end
cost advantage or publication novelty has been established. Final recovery has no
additional forced compaction. The earlier collision solver and historical model data
are unchanged. The synthesis algorithm is standard finite candidate elimination.

Reproduce: `python -m experiments.dependency_memory.feedback_compaction.run`.

[Research note](../../../research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md).
