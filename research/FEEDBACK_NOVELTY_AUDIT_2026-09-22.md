# Is the feedback direction novel?

September 22, 2026. A focused priority check and an elementary reduction, not a
systematic literature review or an external referee report. Claim C40 records
the local reduction and its executable checks. No new model calls.

## Current verdict

**We do not have a defensible novelty claim for the feedback loop or the current
finite repair algorithm.** Iterative repair, cumulative constraints, execution
feedback, pre-commit validation and recovery-aware context management all have
close precedents. The finite optimization can also be written exactly as
budget-bounded strategy selection followed by weak hypergraph coloring.

This does not prove that every detail of the implementation has appeared in one
earlier paper. Nor does it rule out a useful systems contribution from combining
established methods. It does mean that a new name or a compaction-specific
interface is insufficient evidence of a new algorithm or information principle.
The existing strong-baseline tie also leaves practical superiority unestablished.

| Proposed claim | Closest foundation or precedent | Assessment |
|---|---|---|
| Generate, critique, revise | Self-Refine; Reflexion; Memento | Established mechanism; no novelty claim. |
| Preserve previous feedback across repairs | WiCER's cumulative preservation constraints; finite candidate elimination | Established mechanism; cycling is a useful diagnostic. |
| Evaluate compaction by execution | TRACE's paired continuations | Established evaluation idea. Our exhaustive finite obstruction has a stronger quantifier, but requires a supplied model. |
| Plan and validate context edits before commit, with recovery | Self-GC | Close architectural precedent; its structural rehearsal is not our all-policy semantic certificate. |
| Pin necessary constraints or reject an insufficient budget | Knowledge Triage / The Compaction Cliff; Context Codec | Established retention and verification approach. |
| Learn a model, execute counterexamples, refine it | Black-box checking and CEGAR | Established formal-methods pattern; finite observations alone do not certify an unknown system. |
| Compute minimum recovery cost and extra retained states | Decision trees, strategy alphabets, safe-group source coding and coloring | Exact elementary reformulation below; no new general algorithm claim. |
| Obtain useful, cheap, sound compaction witnesses from realistic workflows | Not demonstrated in our artifact or settled by this review | Candidate systems question, not established novelty. |

Source versions and read scopes are recorded in the
[prior-art note](FEEDBACK_PRIOR_ART_2026-09-22.md). The older delayed-query coding
results have separate priority questions; the reduction here does not settle
novelty of their particular constructions or constants.

## What the closer sources actually establish

[Self-GC v1](https://arxiv.org/html/2607.00692v1) [@selfgc2026] proposes context
edits, structurally rehearses them and commits at safe boundaries. It retains
the transcript outside the active view and uses recoverable sidecars. Its
offline future-dependency metric is judge-based. This is strong overlap with
the architectural pitch, but not an exhaustive recovery-budget certificate.

[The Compaction Cliff v1](https://arxiv.org/html/2608.22752v1)
[@compactioncliff2026], Section 3.3, gives typed retention, a constraint verifier,
restoration or rejection, and a compaction/decomposition/retrieval cycle. Its
classification and preservation assumptions must remain attached to the claims.

[Meijer and van de Pol](https://link.springer.com/article/10.1007/s11334-019-00342-6)
[@meijer2019blackbox] combine learned models, model checking and execution of
counterexamples. Their soundness discussion distinguishes finite safety traces
from infinite behavior and states the necessary access assumptions. Merely
adding executable counterexamples to our loop would not create a new principle.

None of these readings is an independent replication. Absence of an identical
method in these selected sections is not evidence of priority.

## Reduction 1: a recovery policy is an ordinary strategy symbol

Fix one original retained/public cell C, a future task q and recovery budget B.
Use exactly the existing audit contract: finitely many visible prehistories,
finite terminal accepted-action sets A(h,q), deterministic read-only tools with
finite observation alphabets, positive integer prices, and no additional memory
boundary during recovery. The task becomes known after the repair message;
all declared tasks are required in every world. The model is shared, but the
controller does not observe the evaluator's world identifier h.

Let Pi(B,q) be all finite tool/observation decision trees whose leaves contain
terminal actions and whose every path costs at most B. This is a finite set:
depth is at most floor(B / c_min), with finite branching and finite labels.
If there are no tools, it consists only of terminal actions. Actions outside
the finite union of accepted sets can be discarded because they never succeed.

For each world define

    K(h,q,B) = {pi in Pi(B,q): executing pi in h ends in A(h,q)}.

For any nonempty D contained in C,

    D is recoverable within B for q
        iff intersection over h in D of K(h,q,B) is nonempty.       (1)

The reverse implication executes the shared strategy. For the forward
implication, take a successful controller on D. Unroll it to depth at most
floor(B / c_min); remove any irrelevant nonterminating behavior off its
realizable paths. Attach arbitrary terminal leaves to observations unreachable
from D. All paths now obey B and behavior on D is unchanged. This extension
matters: success on a cell initially constrains only paths possible in that cell,
whereas Pi(B,q) was defined with a global hard path bound.

Thus costed recovery changes which strategy symbols are accepted in each world.
It does not escape the usual shared-acceptable-output formulation. This is an
elementary local deduction using established strategy-alphabet reasoning
[@dupuis2004strategies], not a theorem imported from that source.

The explicit strategy alphabet may be enormous. The reduction is a
representation/novelty check, not a proposed efficient enumeration algorithm.
The existing dynamic program is a compact way to search these strategies.

## Reduction 2: extra memory is weak coloring of unsafe groups

A repair message is chosen from the visible prehistory before q is revealed.
Consequently a message cell D must be safe for **every** declared task:

    F_B = {D contained in C: for every q,
           intersection over h in D of K(h,q,B) is nonempty}.

Include the empty set as safe. F_B is downward closed: the policy for a group
also works for each subgroup. Every singleton is safe because the model gives
each world at least one accepted action. Let E_B be the inclusion-minimal sets
outside F_B. Every unsafe set contains an edge in E_B, since C is finite.

Build a hypergraph with vertices C and **forbidden** edges E_B. A repair label
is a color. A color class is safe exactly when it contains no forbidden edge,
which is exactly the weak-coloring condition that no edge is monochromatic.
Hence

    minimum additional message states on C = chi_weak(C, E_B).     (2)

The two directions are immediate: a valid repair partitions C into safe color
classes; a weak coloring supplies those same safe classes as repair labels.
The decoder uses the label and the later q to select a shared strategy from
(1). Different tasks may use different strategies, but must use the same
pre-task label partition. The encoder can choose the label because the existing
contract gives every world a distinct visible prehistory.

Across original retained/public cells, the label alphabet can be reused because
the decoder observes the original cell. Therefore the global number of extra
states is the **maximum**, not the sum, of the per-cell chromatic numbers.
An added fixed binary field uses ceil(log2 of that maximum) bits. This excludes
the shared codebook and policy descriptions and is not a byte or token bound.

Weak coloring is standard terminology: see the definition in
[Bennett et al.](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v23i2p46)
[@bennett2016weakstrong]. Strong coloring would require every vertex of an edge
to have a different color, which is unnecessarily restrictive here. In the
three-world compatibility example, the only forbidden edge is the whole triple:
weak coloring needs two colors, replacing it with three pair conflicts needs
three, and checking only actually unsafe pairs incorrectly permits one.

The relation to [Basu et al.](https://arxiv.org/html/2204.02586v2)
[@basu2022hypergraph] needs care. Their characteristic hyperedges are acceptable
groups under a metric approximation condition; ours are minimal forbidden groups
for a finite accepted-strategy relation. These are different conventions. The
downward-closed safe family can be described by maximal safe groups or minimal
unsafe groups. Equation (2) is our elementary one-shot reformulation, not a
claim that their asymptotic coding theorems directly solve this hard-budget
protocol. In particular, we import no asymptotic rate or vanishing-error result.

## Executable checks

The [new subpackage](../experiments/dependency_memory/novelty_audit/README.md)
and [generated report](../experiments/dependency_memory/results/feedback_novelty_report.md)
check both representations:

- All 343 nonempty accepted-action tables on the existing three-world,
  three-answer, two-tool domain, at budgets 0, 1 and 2. Forward tree composition
  gives 3, 15 and 27 distinct world-output vectors. It agrees with the recovery
  optimizer on 7,203 subset/budget checks and with the repair optimizer on
  1,029 strategy-derived coloring checks.
- All 12 existing audit specifications. Enumerated color assignments agree with
  the partition optimizer; minimal forbidden groups reconstruct every safe
  subset. These use the existing optimizer for feasibility, so they independently
  check the repair representation, not recovery optimality a second time.
- Assumption controls: labels can be reused across public cells; one common
  pre-task encoding can need three labels even when each of two tasks separately
  needs only two; nonhereditary safe families are rejected; expensive and
  uninformative tools do not create free strategy outputs.

These extend checks on an existing tiny domain; 7,203 comparisons are not
7,203 independent tasks, and no runtime or scalability claim follows. The
general statements rely on the arguments above, not exhaustive finite testing.

## Where further research could earn a contribution

The strongest remaining question is operational:

> Can a compaction audit discover a concrete delayed failure, or justify a
> recovery budget, from executable workflow evidence cheaply enough to improve
> the final outcome under the same total resource limit?

This requires a new capability or substantive empirical evidence beyond the
current enumerated model. The [next-stage protocol](../docs/FEEDBACK_RESEARCH_PROTOCOL.md)
already specifies equal evidence, opaque payloads, delayed targets, two boundaries
and full costs. Add these explicit gates:

1. **Evidence extraction:** obtain obligations and tool behavior from pinned
   executable snapshots. Replay each failure against the original system and
   distinguish witnessed failure, a complete finite certificate and unknown
   coverage. Supplying the correct critical-field set by hand does not pass.
2. **Incremental audit:** reuse checked obligations across revisions without
   treating stale evidence as valid after artifact or permission changes. Measure
   whether this saves total work against rerunning all tests. This is a candidate
   implementation target, not a newly invented verification principle.
3. **Decisive comparison:** beat equally informed critical-field retention and
   generic extra revision at matched full costs on a frozen evaluation split,
   or demonstrate useful refusal/recovery decisions that those baselines miss.
   Compare available source implementations before making a state-of-the-art claim.

If the simple baseline keeps matching the loop, retain the audit as an evaluation
tool and report that result. The useful insight in the original suggestion is to
make failures change the next decision; it does not require an academic priority
claim. We should pursue a concrete capability, not manufacture novelty by moving
from one familiar formalism to another.
