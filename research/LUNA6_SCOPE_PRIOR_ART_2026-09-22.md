# Scope changes, pinning, and the live Luna pilot

Primary sources reviewed September 22, 2026. This note does not certify novelty.
The live [release pilot](../experiments/dependency_memory/luna6_revision/CONTRACT.md)
was frozen before its model answers. These readings do not change its schedule.

[The Compaction Cliff](https://arxiv.org/html/2608.22752v1), Section 3.1 and
Section 3.3, already assigns retention rules by knowledge type and provides
scope-aware verification and restoration. Its classifier is a stated dependency
of the guarantees. Typed retention, protecting critical information, and checking
a compressed working set are therefore close precedents, not our contributions.
[@compactioncliff2026]

[Governance Decay](https://arxiv.org/html/2606.22528v1), abstract and Sections
3–4 and 7–9, studies constraint loss during compaction and restores constraints
through pinning. Its allowed-action controls and reported failures under forged
authority updates are especially relevant. The authors distinguish protected
system messages from constraints carried in ordinary memory. These are reported
findings, not replications by this repository. [@chen2026governancedecay]

Our release pilot keeps the decision rule public at every stage. What can be
lost is the evidence to which that rule applies: the approved artifact, CI scope,
required-test membership, and a previously empty blocker set. Legitimate late
updates can change the correct action in either direction. This operational
distinction motivates a measurement; it does not imply that the cited methods
cannot retain the same evidence or implement the same update checks.

The strongest cheap control is direct serialization of the executable gate's
dependencies. A repair loop that writes that same representation after an LLM
proposal has extra proposal cost. Any argument for a new general repair method
must survive that control and indexed recovery. The current adapter is manually
written for one gate schema. Automatically extracting a sound projection from
unseen workflow code, deciding which future updates matter, and improving a
complete agent's outcome at a fully measured total cost remain open.

An optional check result can be irrelevant to today's gate and become required
later. More generally, a representation sufficient for today's output need not
remain sufficient under allowed state updates. This is compatible with standard
state abstraction and functional-compression ideas. We do not claim a new
theorem or algorithm from restating that observation.
