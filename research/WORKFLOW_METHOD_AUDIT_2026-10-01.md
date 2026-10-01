# What the next workflow comparison can actually test

October 1, 2026. Completed local derivation, finite software audit and screening
of one inspected development task. Zero new provider generations. The
[offline design](../experiments/dependency_memory/workflow_prospective/PROTOCOL.md)
was committed at `66cebac` before implementation. The old code, outcomes and
development episode were already read; this is not preregistration of unseen
data. [Generated report](../experiments/dependency_memory/results/workflow_method_2026-10-01/report.md).

## Exact checked tables do not add receipt information here

Let P(L) map each (source snapshot, check name) to its last receipt in the
chronological public ledger L. The projected receipt contains exactly check,
snapshot, run_id, returncode and artifact bindings. These roles and the reporting
rule are already supplied to the method. Run identities are unique.

The original [checker](../experiments/dependency_memory/workflow_eval_live/study.py)
accepts a writer only when its decoded table has exactly those fields and equals
the entire projected receipt set. Every rejection falls back to the same direct
projection when it fits. An accepted table can reorder independent keys or add
whitespace, but cannot change the receipt map.

Within this **fixed JSON receipt-list grammar**, compact direct serialization
is no longer than an accepted encoding of the same rows: keys/check names,
artifact paths and hexadecimal identities are ASCII; integer return codes use
their shortest ordinary JSON representation. Permutations do not shorten it,
whitespace/escapes add bytes, and float encodings fail the integer requirement.
Thus if the direct table does not fit, no accepted exact table fits either;
both policies return infeasible empty memory. This is not an optimality statement
over other codecs, dictionary representations or all functionally sufficient
states.

For the second boundary, equal parent maps plus the same ordered new observations
give equal updated maps: a later run replaces the old run for its key. Filtering
by the same announced scope preserves equality. Therefore the checked/direct
chains expose the same receipt map at both boundaries, including after binding
caps. Every later reporting query under the declared rule has the same typed
readout. [C56]

The finite audit uses all 1,885 histories of length zero through three over a
twelve-event alphabet. It finds:

| Comparison | Checked cases | Disagreements |
|---|---:|---:|
| Separate reverse-scan specification versus unchanged primary grader | 158,340 | 0 |
| Direct projection versus full-ledger specification | 158,340 | 0 |
| Six writer variants and six caps on histories of length at most two | 5,652 | 0 |
| Two boundaries, four cap pairs, seven scopes | 52,780 | 0 |

This is independent **software formulation**, implemented and reviewed by the
current researcher, not external human review or statistical independence.
The finite examples support implementation checks; the map argument supplies
the stated general deduction for this grammar.

Two paid checked-writer calls consequently add no receipt information relative
to direct projection here. A canonicalized checker produces the exact same
memory string as direct. Conditional on equal downstream operations/prices and
nonnegative added writer costs, it has no cost benefit; positive added costs make
that particular arrangement more expensive. This is conditional arithmetic,
not a measured production-cost result.

The original checker retains accepted JSON presentations. Model decoding may
respond differently to order or whitespace, and provider/cache effects are not
proved equal. **Do not infer equality of original stochastic model accuracy or
overall costs from semantic equality.** Unknown role extraction, a more compact
codec, selective functional retention and unavailable fallbacks are different
problems. No general checking/compaction novelty or dominance theorem is claimed.

## The actual first episode does not require parent memory

For [E0001](../experiments/dependency_memory/workflow_intake/development/E0001/README.md),
the full six-receipt ledger and B's three receipts alone produce the same exact
answer to the actual B-tree query, including all supporting run IDs. Checkpoint B
reran every required check. Its direct memory is also feasible: 728 parent bytes
and 1,455 child bytes under the unchanged 4,096/1,536 caps. [C57]

There is a stronger structural reason for this particular equality. Every A
receipt binds a different source tree from the final B-tree query. Under the
declared exact-snapshot reporting rule, receipts outside the requested snapshot
cannot affect either required work or supporting run IDs. Removing them leaves
the answer unchanged even if B omits some checks; those checks then remain
missing under both views. Selective capture alone cannot create parent dependence
when the final snapshot is absent from A. Same-snapshot delayed checks or actual
cross-snapshot obligations would require appropriate natural tasks; changing
the reporting rule requires a separately versioned method.

This task is a useful easy/interface control. It does not establish a repeated
memory-capacity deficit or demand information preserved from A. Constructed
queries to the earlier tree can require A, but they remain constructed queries
of this same task. They do not turn into untouched natural episodes.

The full logical request for this task is 163,432 bytes, exceeding the old
100,000-byte public-request cap. The new predeclared limit is 262,144 serialized
bytes. Actual provider wire size, token capacity and isolation remain unverified;
no provider was contacted. The memory caps are unchanged and no log is clipped.

## Revised prospective direction

The [new pure runtime](../experiments/dependency_memory/workflow_prospective/runtime.py)
implements direct receipts, indexed raw recovery, prose and full history.
Checked memory is retained only as the canonical offline shadow above. Two
prose writers plus four final slots replace the previous nine-slot scheme;
seventy-two prospective completions for twelve tasks are a proposal, not a
provider allocation. The method is frozen separately from future task files.

Every final proposal receives the same actor-only consistency check. Raw answers,
vetoes, unknown representations, withheld correct answers and hypothetical
readouts stay separate. There is no repaired execution or grader feedback. A
scripted six-completion control validates stage order and the common check; its
prose slot deliberately emits a JSON table. It is not a model performance result.

Keep collecting actual consecutive whole tasks in ContextResearch. Record the
natural command sequence rather than forcing a full B refresh. Retain genuine
refreshes, short histories and failures without quotas. For every actual primary
query, screen full ledger versus B alone and direct cap feasibility. If all twelve
tasks are B-only and fit, stop this proposed two-boundary study for the workload
and report that the mechanism was not exercised. Do not select a favorable subset
or shrink caps after inspection.

Future variable-length command capture/registration, prospective episodes,
external human grader review, provider serialization/isolation, model revision,
sampling parameters, prices and a bounded allocation remain incomplete. The
fourteen new tests check information order, replay binding, chronological failures,
scope, UTF-8 caps, missing responses, resource stops, no source resurrection and
the distinction between consistency vetoes and repaired answers. No current
task is relabeled prospective merely because the method is frozen during it.

Final validation: all 448 offline tests pass, repository validation reports PASS
with 57 claims and 46 bibliography entries, and paper assembly resolves 39 cited
sources. The CLI completes six scripted interface slots for E0001. Historical
hashes and the sixteen-file method lock remain intact; prospective episodes
and new provider generations both remain zero.
