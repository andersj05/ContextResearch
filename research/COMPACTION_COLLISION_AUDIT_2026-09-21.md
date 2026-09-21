# Before forgetting: certify the cost of recovering from a memory collision

September 21, 2026. New research direction and executable prototype. Claims C35-C36.

## Research choice

The user asked for a substantive departure from sharpening the four-bit bound.
This phase builds an auditor that asks whether a proposed retained state leaves
any policy capable of completing every declared future task within a recovery
budget. Its output can justify keeping an additional distinction before
compaction, allowing deletion when tools suffice, or declining to certify a
representation. It is a different research artifact from another coding bound.

The implementation is complete for a small, explicitly finite information model.
The [generated report](../experiments/dependency_memory/results/collision_audit_report.md)
and [machine-readable certificate](../experiments/dependency_memory/results/collision_audit_certificate.json)
contain 12 constructed specifications, optimal recovery trees, independently
checked lower proofs, and minimum additional-state repairs. They contain **zero
new model calls**. These are deliberately constructed checks, not independent
trials or evidence that a deployed compactor makes these errors.

The candidate contribution is a compaction audit that combines **whole collision
groups, multiple valid terminal actions, adaptive costed recovery, and an
explicit minimum-state repair chosen before the future task is revealed**.
The constituent mathematics is established. Publication novelty of this
particular audit protocol remains a hypothesis; a literature search cannot
certify priority. The phase should be judged by the executable artifact and
falsifiable next test, not by calling an old theorem new.

## Information contract

There are finitely many possible prehistories. Each supplies a visible history,
a retained JSON value, and a public JSON value. Two histories collide only when
their retained and public channels are exactly equal after canonical JSON
serialization. Public state may include an accessible workspace observation.
An evaluator label is not an agent observation. We do not infer equivalence
between differently worded natural-language summaries.

The full finite model is public. The realized history is known before compaction
and hidden afterward except through those channels. Distinct prehistories are
required so a proposed repair encoder can actually choose its label from its
declared observations. The encoder chooses the label before learning which of
the declared future tasks will occur. A future task has a shared public event
trace and a set of accepted terminal actions in each possible world; several
answers may be correct. All tasks are possible in every world. No future trace
or task identity carries an undeclared world-dependent clue.

After the task is revealed, a policy may invoke only the listed deterministic,
read-only tools. Each tool has a positive integer cost and an explicit response
in each world. Responses and policy state remain available during rescue.
There is **no additional forced compaction during recovery**. A terminal answer
ends the task; trying a wrong answer cannot become a free diagnostic query.
All other terminal answers are failures. No transcript, file read, provider
state, archive, clock, or environment access is allowed except the modeled
channels. This is a trusted finite-model calculation, not process isolation.

The objective is zero error with a worst-case cap on total recovery cost. The
terminal action's common cost is excluded. Units are synthetic action prices,
not tokens, dollars, latency, or storage expense. Serialized retained/public
UTF-8 lengths are reported separately. Fixed codebooks and tool schemas are
public model descriptions, not claimed free instance-specific archives.

## Exact audit and proof obligations

Let B be a nonempty set of worlds still possible from the policy's observations,
A_h the accepted terminal actions in world h, and B(t,o) the subset returning
observation o from tool t of cost c_t. Define V(B) as the minimum worst-case
additional recovery cost.

- If the intersection of all A_h in B is nonempty, V(B) = 0.
- Otherwise V(B) = min_t [c_t + max_o V(B(t,o))], considering tools that split B.
- An empty minimum is infinity.

A non-splitting, deterministic, read-only tool provides no information and can
be deleted from any policy at a strict cost saving. Every branch of a splitting
tool is a strict subset. Induction on |B| therefore establishes the recurrence,
termination, and an attaining policy whenever V(B) is finite. A reduced policy
uses at most |B|-1 queries on each path. This is elementary decision-tree dynamic
programming, not a new planning theorem. State sufficiency and dynamic
programming have extensive prior foundations [@subramanian2022ais].

For a budget b < V(B), the implementation emits a separate obstruction DAG.
Every legal terminal answer has a rejecting world. Every affordable splitting
tool has at least one realizable response leading to another obstruction at
budget b-c_t. Over-budget tools are explicitly rejected; non-splitting tools
are checked as useless queries that can be removed at a strict saving. A
separate verifier checks these facts directly without calling the optimizer.
Recursive branches strictly shrink the world set, so even very large budgets
do not create long chains of useless reads. Successive adversarial responses leave nested, nonempty
world sets, so the obstruction is consistent with a fixed original world;
it does not secretly change the underlying history between queries.

An infinite optimum additionally has a budget-independent certificate: a
nonempty subcell whose worlds return the same response to every allowed tool
but have no universally accepted terminal action. A separate checker validates
that subcell directly; a finite-budget failure alone is never used as proof of
unrecoverability at every budget.

These certificates also rule out a randomized policy that promises zero error
and the same hard per-run budget: a random first action cannot remove every
action's obstruction. We do not optimize average error, expected cost, or
distributional guarantees. A failed robust certificate is not a prediction
that the typical episode will fail.

For a repair, call a subset B safe if V_q(B) <= b for every listed future task q.
Partition each original collision cell into the smallest number of safe subsets.
The encoder retains the subset label. Exhaustive subset dynamic programming
finds the minimum. Labels can be reused across already distinguishable original
cells, so the largest cell's required label count determines the extra alphabet.
For M labels, the fixed-length cost is ceil(log2 M) bits. This exact finite
codebook optimizes states; it does not optimize natural-language length, select
semantic fields automatically, or implement a scalable learned compressor.

## Completed findings

**Pairwise checks need not certify a whole memory state.** Three histories admit
builds {A,B}, {B,C}, and {A,C}. They have the same retained and public channels.
Every pair has a common accepted build; the triple has none. Therefore all three
pairwise zero-recovery feasibility checks pass, but no policy without recovery
can handle the whole cell. One unit-cost binary inspection suffices. At budget
zero, two retained states suffice and one does not. This is an elementary
set-intersection counterexample, not a new hypergraph theorem. Group-based
functional compression already has direct mathematical precedents
[@basu2022hypergraph].

**Tool adaptivity changes the recovery cost.** In the eight-world archive, a
directory identifies one of four shards, and that shard identifies one of two
receipts. Directory then shard costs two units in every world. A fixed batch
needs all four shard reads: omitting a shard leaves its two receipts unresolved,
even if the directory is included. Three shard reads leave the omitted pair
ambiguous. Thus the exact adaptive/fixed-batch costs are two/four. At budget one,
two retained message states suffice; with budget two, none beyond the existing
summary is necessary. The repair is an explicit finite codebook, not a claim
that one model token encodes an arbitrary receipt.

**Recoverability depends on version and access.** Two histories share the current
v2 artifact but differ in an original v1 receipt. Current-release tasks need no
extra memory. A later request for the original receipt needs a three-unit
versioned archive read. A latest-workspace read cannot distinguish the histories.
Removing the versioned archive makes the task impossible from the existing
state; retaining one distinguishing bit repairs this two-world fixture. The
auditor selects the shortest failing trace from the supplied catalog. It does
not generate arbitrary temporal event sequences or execute a live rollback.

**Negative controls behave correctly.** Free public evidence, a universally
accepted portable build, and sufficient recovery budgets each remove the need
for extra retained states. Losing an irrelevant fact is not automatically
labeled a failure. A separate eight-receipt binary-query calibration gives
8, 4, 2, and 1 retained states at recovery budgets 0, 1, 2, and 3. Binary-tree
leaf counting independently establishes those state counts.

## Literature comparison and novelty boundary

The [focused source note](COMPACTION_AUDIT_PRIOR_ART_2026-09-21.md) records exact
review scope and primary links. WiCER already evaluates compiled knowledge
with diagnostic questions and repairs omissions; that feedback loop is not our
contribution [@wicer2026]. TRACE already compares restored PRE/POST tool
continuations and uses execution regressions to rank summaries
[@trace2026]. Context Codec already represents and verifies typed commitments
[@contextcodec2026]. We therefore rejected simple renamings of those ideas.

Our restricted auditor asks for a **policy-independent obstruction over an entire
indistinguishable group under all allowed adaptive recovery actions**, rather
than scoring a sampled continuation. The word "independent" refers to policies
inside the declared model, not unknown tools or unrestricted real agents. The
explicit accepted-action relation allows useful information loss and catches
the pairwise/triple issue. State abstraction, decision-tree search, and
hypergraph representation are prior methods, not claimed inventions. No claim
that the reviewed systems cannot be extended to do this is justified.

## Verification and next falsification test

The focused tests compare the optimizer with explicit forward enumeration of
all depth-at-most-two binary-query controllers for all 343 nonempty accepted-
action tables on three worlds. Every nonempty world subset is checked, giving
2,401 value comparisons. Forward behavior enumeration also independently checks
repair partitions at three budgets. Separate tests replay synthesized policies,
tamper with proofs, test exact channel identity and nonrefining tools, and verify
the analytic binary-query state counts. These are software/finite-model checks.

The full repository suite passed 285 tests, the offline validator reported no
errors, and the paper builder produced a preview with 27 cited sources. The
new subpackage contributes 15 focused tests. The JSON input CLI was also run
against the saved example. These checks preserve the historical study data.

The next research test is **a blinded adapter to execution-graded task snapshots**:
extract visible prehistories, real retained states, accepted artifact outcomes,
and allowed recovery calls from a pinned local task fixture; freeze the channel
contract; then test whether a certificate predicts a reproducible failure and
whether its proposed retained distinction repairs it at matched total cost.
No such adapter or natural-task result is claimed here. Raw prose rarely collides
exactly, and inferred semantic equivalence would require separate validation.

Stop or downgrade this direction if (1) no useful exact channel collisions can
be obtained without an evaluator inventing equivalence, (2) a simple keep-all
critical-fields baseline matches the audit at the same cost, (3) complete-world
enumeration cannot be replaced by a sound tractable interface, or (4) prior work
already supplies the same compaction-specific certificate and repair protocol.
The mechanism earns a research claim only by surviving those tests.

## Reproduction

From the repository root:

    python -m experiments.dependency_memory.collision_audit.run
    python -m unittest experiments.dependency_memory.collision_audit.test_collision_audit -v
    python -m experiments.dependency_memory.collision_audit.run --input experiments/dependency_memory/collision_audit/example.json --output tmp/collision-audit.json

The [implementation contract](../experiments/dependency_memory/collision_audit/README.md)
describes the JSON adapter. Historical study data and their fingerprinted
top-level launch modules are unchanged.
