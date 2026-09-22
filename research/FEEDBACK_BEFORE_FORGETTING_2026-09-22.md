# Feedback before forgetting: verified constraints, timing, and hidden channels

September 22, 2026. Claims C37-C39. Completed offline investigation; no model calls.

## Research conclusion

Feedback is useful here when it supplies a specific, checkable reason to reject a
memory and arrives while revision is still possible. It is not sufficient by
itself: repairs can cycle, a later memory boundary can remove the repair, probes
can miss obligations, and an oracle can quietly reintroduce deleted information.

The new artifact connects the existing executable receipt workflow to the
collision auditor and closes a finite propose-audit-repair loop. In the main
constructed case, accumulated unsafe-group constraints repair 32/48 successful
executions to 48/48. A simple workflow-aware critical-fields baseline also gets
48/48, with less synthesis work. **This establishes no advantage over that
baseline and is not evidence of an LLM or natural-task improvement.**

The broad feedback-loop idea, cumulative constraints, and counterexample-guided
refinement all have close precedents. Our defensible output in this phase is a
reproducible diagnostic and a sharper experiment contract, not a novelty claim.
The [source comparison](FEEDBACK_PRIOR_ART_2026-09-22.md) records what was read.

## What was implemented

The new [package](../experiments/dependency_memory/feedback_compaction/README.md)
uses the unchanged `ArtifactEnvironment` from the existing experiment. It:

1. Executes collection, manifest reveal, revision, two seals, intervening work,
   and the final requirement on restored environment instances.
2. Extracts the memory/public channels produced by a declared parent schema and
   child selector. It never infers equality between differently worded prose.
3. Derives accepted terminal actions by actually executing each possible catalog
   receipt through the environment's submit verifier. The verifier requires
   exact receipt equality; payloads outside that complete finite catalog fail.
4. Audits each resulting collision cell with all permitted final recovery actions.
5. Returns a minimum failing world group and a separately checked obstruction.
6. Searches a finite candidate family while preserving all accumulated constraints.
7. Replays successful controllers against the actual environment and records
   ordinary retained-receipt execution separately from codebook decoding.

The [report](../experiments/dependency_memory/results/feedback_compaction_report.md)
and [certificate](../experiments/dependency_memory/results/feedback_compaction_certificate.json)
include source hashes, complete primary repair traces, 48 contracts with five
methods each, timing controls and channel controls. The code and results are
separate from all historical model launch modules and saved studies.

## Information and cost contract

Three jobs have independent binary world coordinates, giving eight enumerated
worlds. For each key and revision, a public catalog maps that coordinate to one
of two distinct 32-character tokens. Revision-two tokens differ from the original
tokens but deliberately use the same coordinate. This correlation and the small
catalog are fixture assumptions, not properties of real receipts or model memory.

The parent retains a fixed subset of original records before seeing the manifest.
The manifest reveals one of the three pairs; the lower key is then refreshed.
The child sees only selected parent records, the manifest, and the fresh build
receipt. It keeps up to its capacity, prioritizing the unrefreshed higher key.
The target is one of the pair and is revealed after the second boundary. The
base child selector does not see it. There are six manifest/target continuations,
each possible in all eight worlds. The source observation window and parent
memory do not remain accessible after the respective boundaries.

Policies receive neither evaluator world IDs nor environment internals. The
evaluator does retain restored environments to grade counterfactual executions.
This is a trusted scripted interface, not a process-level isolation claim. All
tools, terminal actions, catalog rules and public traces are explicit. The only
optional post-boundary tool is the environment's once-only required-receipt
recovery. It costs three synthetic units, with budgets zero, two or three.
No further memory limit occurs during final rescue.

The repair loop operates **offline over the entire finite family**. It chooses
one schema before any realized world, manifest or target is selected. Witnesses
and the development catalog do not become extra instance-specific runtime
memory. This is schema synthesis, not an LLM repeatedly editing the current
episode's summary. Applying it to prose remains unimplemented.

Memory capacity is in tagged receipt records. The artifact separately reports
serialized UTF-8 bytes, feedback-constraint bytes and audit-log bytes. Nine
mandatory environment action units are charged per completed or failed
scripted episode; recovery adds three when used. Full audits, cell checks,
constraint checks, constructed candidate/route models, terminal grading calls
and prefix executions report offline work. Those counts are not interchangeable
with dollars, latency, model tokens or state bits. No matched-total-cost
superiority follows from fewer full audits alone.

## Finite repair guarantee and its assumptions

Let C be a finite candidate family under a fixed memory budget and a fixed
information/recovery contract. For a declared continuation q and candidate c,
write E(c,q,h) for the complete accessible state after both memory boundaries
in world h. A witness (q,B,b) consists of a nonempty world group B, recovery
budget b, and a verified proof that no legal terminal/recovery policy can succeed
in every world of B while their initial accessible states are identical.

The necessary repair constraint is:

    the values {E(c,q,h) : h in B} must not all be equal.

This is a constraint on the whole group; replacing it with arbitrary pairwise
conditions would lose the earlier auditor's multiple-valid-answer guarantee.
Breaking this one group is necessary, not sufficient for complete safety.
Every proposed replacement receives a fresh full audit.

**Elementary finite-elimination proposition.** Assume the verifier is sound and
complete for every candidate and declared continuation, every returned witness
has the above meaning, the contract is unchanged, and candidate selection finds
a member satisfying all accumulated constraints whenever one exists. Then the
loop makes at most |C| full candidate audits. It returns either a verified
candidate or exhaustion of this family. If a feasible candidate exists in C,
exhaustion cannot occur.

**Proof.** Each failure adds a constraint that the current candidate violates,
so that candidate cannot be chosen again. A feasible candidate cannot merge a
verified unsafe group, since its successful policy on a containing cell would
also succeed on the subgroup, contradicting the obstruction. Thus no feasible
candidate is eliminated. Finiteness gives the bound and the conclusion. The
result says nothing about how much work a full audit or candidate search takes.

This is standard finite candidate elimination, closely related to established
counterexample-guided refinement, not a new synthesis theorem
[@clarke2000cegar; @zhang2017pomdp]. In our implementation, witnesses are rechecked
against current accepted actions and tools before reuse; a changed recovery
budget rejects the old feedback. Prose compliance, incomplete world models,
stochastic tools, and unverified heuristic hints do not inherit the guarantee.
Exhaustion means **no feasible candidate in C**, never unrestricted impossibility.

## Completed execution findings

### 1. Accumulated constraints repair a bad schema; a known good schema wins

The primary budget is two parent and two child records, without recovery. The
initial schema keeps job-0/job-1. Because the lower manifest key is refreshed,
job-0's original receipt is never needed; job-1 and job-2 can each be the
unrefreshed higher key. The initial schema succeeds on 32 of the 48 world/routes.

| Method | Full audits | Cell checks | Constraint checks | Executed successes |
|---|---:|---:|---:|---:|
| Initial proposal, no repair | 1 | 11 | 0 | 32/48 |
| Enumerate alternatives after a failure | 7 | 58 | 0 | 48/48 |
| Preserve only latest witness | 3 before cycle detection | 25 | 11 | No accepted candidate |
| Preserve all witnesses | 3 | 38 | 14 | 48/48 |
| Workflow-aware critical fields | 1 | 24 | 0 | 48/48 |

The first failure says job-2 must remain distinguishable. A last-only repair
keeps job-2, then loses job-1, then reverses that choice and cycles. Accumulation
retains both requirements and selects job-1/job-2. The strong baseline obtains
that same schema directly from the public refresh rule. Keeping old failures
is already present in WiCER; our comparison tests verified constraints in this
finite environment rather than establishing priority [@wicer2026].

The 48-contract sweep crosses parent capacities 0-3, child capacities 0-2, and
four recovery settings. Accumulation, exhaustive enumeration and critical-field
retention each certify the same 18 contracts. Latest-only feedback cycles in 15.
These counts describe a constructed grid, not independent observations or an
effect-size estimate. A domain rule already solving this family is a successful
negative control and a reason to downgrade a practical-superiority claim.

### 2. Later forgetting can defeat an earlier repair

With one child record and an unknown target, no priority-selector candidate
passes the no-recovery contract, even with all three parent records. The child
must discard one of the two candidate receipts, and each can be requested later.
An explicitly separate treatment announces the target before the second seal;
then two parent records and one child record succeed on all 48 outcomes.

That treatment changes the timing of information; it does not extract knowledge
from a previously deleted distinction. Adequate recovery also restores success,
including with zero retained records, at its declared cost. Terminal success
alone consequently cannot measure retention quality.

### 3. One record is not one bit, and feasibility is not policy performance

Let x and y be the binary values of the lower and higher candidate receipts.
Keep the lower receipt if x=y, and the higher receipt otherwise. When the decoder
receives a lower receipt, both values equal its catalog bit. When it receives
the higher receipt, the lower value is the opposite bit. This is a bijection
between four source pairs and four tagged-record states.

Thus a deliberate value-dependent code succeeds on 48/48 executions with one
record at the second boundary. The original receipt-only submission policy on
that same memory succeeds on 24/48. The accessible representation has **four
states, hence two state bits**, and uses the public two-value catalog. This is
an elementary identifier-channel example, not compression of two arbitrary
128-bit receipts into one. It disproves an unrestricted interpretation of the
priority-family exhaustion and shows why a certificate of some successful
decoder is not a guarantee for the decoder actually deployed.

### 4. Passing probes does not certify untested obligations

Auditing only the two targets of manifest job-0/job-1 accepts the initial schema.
It still fails an unprobed manifest requiring original job-2. This is a
deterministic coverage control, not a statistical held-out evaluation.

For a hypothetical iid probe distribution with failure mass p, n independent
probes miss all failures with probability (1-p)^n. At p=0.01 and n=20 that is
about 0.817907. This elementary calculation assumes independent probes and a
fixed failure set; it is not a guarantee for adaptive adversarial search.

### 5. Late feedback must be counted as information

On a route requesting discarded job-2, unchanged accessible channels permit at
most 4/8 correct answers under the uniform eight-world catalog. Telling the
agent the true missing value raises that to 8/8 by adding one conditional bit.
A status message computed only from identical retained/public state cannot do
this: it is identical in the colliding worlds. A verifier that can inspect truth
can distinguish them, but its response is then a recovery channel.

More generally, if H -> S -> F is a Markov chain and F uses only accessible state
S and independent randomness, F cannot distinguish histories already identical
under S. If F additionally depends on hidden H, the no-new-information premise
is false. No general finite bit/error formula for noisy feedback is claimed.

## Independent checks and remaining limits

Eighteen focused tests include 1,872 independent forward controller comparisons
over every nonempty subcell in the main candidate family with and without the
archive. A separate algebraic feasibility rule checks all 48 capacity/recovery
contracts. Tests also cover proof tampering, changed-budget feedback, target
timing, terminal action execution, byte/record boundaries, all failed-run costs,
identifier coding and fresh token payloads without schema resynthesis. The fresh
payload check exercises a fixed program; it is not learned generalization.

Final repository verification passed all 303 tests, the read-only validator
reported no errors while regenerating the saved feedback artifacts, and the
paper builder produced Markdown/HTML with 30 cited sources. Historical source
fingerprints and completed model-study evidence remain valid. The full native
171,798,901-partition search was not rerun; ordinary witness/source validation
remains the existing default check for that unrelated result.

The program is an execution-graded adapter for **our constructed workflow**.
It does not establish a sound extractor for arbitrary repositories, tool APIs
or natural-language histories. Exhaustive worlds remain the main scaling limit;
the finite token catalog is intentionally unrealistic. The result does not
revive novelty for generic feedback loops or show gains over native compaction.

## Next experiment and stop conditions

The [next-stage design](../docs/FEEDBACK_RESEARCH_PROTOCOL.md) fixes the question:
can independently checkable failure constraints improve a bounded compressor
when the retention rule must be inferred, after counting the full cost of
discovering and maintaining those constraints?

Before model spending, build a frozen task family with executable obligations,
opaque payloads and named access channels, plus an equally informed critical-field
baseline. Separate targeted information from extra revision compute. Freeze the
proposer, repair limit and evaluation continuations; never feed evaluation truth
back into training. The present result supplies calibration and failure controls,
not evidence that such a larger experiment will be positive.

Stop treating the feedback mechanism as a research contribution if strong simple
retention matches it at equal resources, if a sound interface needs complete
world enumeration, or if apparent gains require hidden identifiers, archives or
oracle feedback. Pursue certification, rejection and safe fallback as a separate
systems objective only if their practical value can be demonstrated.

Reproduce with `python -m experiments.dependency_memory.feedback_compaction.run`.
