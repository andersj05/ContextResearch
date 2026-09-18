# Exact inspection–retention–recovery reference

September 18, 2026. This is an elementary finite decision model and executable calibration reference. It is not the unknown optimum of the four-bit coding example, a general source-coding theorem, or an LLM result.

## Distribution, policy class, and information access

There are n named jobs with opaque receipt records. The candidate set A is uniform over all m-subsets of the jobs, sorted lexicographically. The final target J is uniform within A. Receipt contents carry no information about A or J. When revisions are enabled, the first candidate receives a fresh receipt during `process_build`, following the existing public scheduling rule. This rule is not a uniformly random revision.

Before the first forced memory boundary a policy can pay c_I to inspect A. It can retain b_1 visible records, then learns A for free and receives the scheduled revision, then retains b_2 current records. J is disclosed only afterward. Policies can submit a visible exact receipt or fail; guessing opaque payloads and coding data into identifiers are outside this reference class. Selecting records is not arbitrary bit compression.

The new `recover_receipt` tool is available only after `get_requirement`. In the declared recovery condition it returns exactly the latest required receipt, at price c_R, once per episode. It exposes no other archive record. Receipt recovery is reliable; availability and price are public. In the irreversible condition it returns no receipt. Out-of-order, unavailable, and repeated admitted attempts are charged. A rejected action that would exceed the episode budget is not charged, as before.

The archive is an explicit additional information channel, held by the evaluator and reachable only through that tool. Recovery can replenish the observation window after the second boundary; there is no third boundary before submission. This models a late read, not recovery that somehow fits inside an earlier memory limit. Archive storage and maintenance costs are not measured; c_R is a declared synthetic access charge.

Reference policies complete the prescribed workflow. Its mandatory cost is K = 7 + delay. The frontier reports **expected incremental action cost above K**, with nonbinding per-episode cost/call limits. It permits randomization, independent of hidden future information. It is not a frontier for hard episode budgets, premature abandonment, unreliable retrieval, or multiple future queries. The implementation rejects binding episode limits for this calculation.

## Exact hit probability before recovery

Let T be the first retained set. Without early inspection, T must be chosen before A. Define R(A) = {min A} when revisions are enabled and the empty set otherwise. The number of available candidate records at the second boundary is

```text
h(T,A) = |(T intersect A) union R(A)|.
p_0 = max over |T| <= b_1 of E_A[min(b_2, h(T,A)) / m].
```

The maximum is outside the expectation. Moving it inside would incorrectly let the first memory see an unrevealed manifest. Since retaining another record cannot hurt, enumeration need only use |T| = min(b_1,n). The later retained set is chosen before J. Because J is conditionally uniform, each current candidate record contributes exactly 1/m to success; keeping min(b_2,h) is optimal. The planned key set is compiled from the public distribution, not an episode seed or answer.

With early inspection, retain candidate records and avoid the one guaranteed to be refreshed. Writing r = 1 for the revision condition and 0 otherwise gives

```text
p_1 = min(b_2, min(b_1, m-r) + r) / m.
```

These expressions are exact within the declared policy class. Payload-dependent selection or random mixtures cannot improve a maximum that already holds for each payload-independent routing distribution. For no revisions, an independent expression is

```text
p_0 = sum_h [C(b,h) C(n-b,m-h) / C(n,m)] min(b_2,h)/m,
where b = min(b_1,n).
```

The implementation compares exhaustive parent-set enumeration with this hypergeometric formula and with a separate small decision-tree enumeration that searches both parent and child subsets. Executable policies are then graded over every candidate/target pair, checking attainment through the actual environment rather than only through formula agreement.

## Expected-cost frontier

For reliable recovery, four endpoint strategies suffice:

| Strategy | Success | Expected incremental cost |
|---|---|---|
| Retain without inspection | p_0 | 0 |
| Inspect then retain | p_1 | c_I |
| Retain and recover every miss | 1 | (1-p_0)c_R |
| Inspect, retain, and recover every miss | 1 | c_I + (1-p_1)c_R |

Unavailable actions remove their endpoints. Partial recovery moves along the line between a strategy's unrecovered and fully recovered endpoints: every recovered miss adds one success and costs c_R. A randomized initial inspection decision mixes these segments. Better retention raises free hits and weakly reduces recovery cost, so a lower-hit representation cannot improve this frontier. The upper success boundary of the convex hull of the endpoints is therefore exact for the stated model. The code checks its hull against an independent enumeration of all two-endpoint mixtures at rational budgets.

At success one, inspection is strictly cheaper exactly when

```text
c_I < (p_1 - p_0) c_R.
```

Equality is a tie. This is elementary expected-cost accounting, not a new general value-of-information theorem. If p_1 = p_0, positive-cost inspection has no value in this model. If recovery is free, recovery without inspection reaches success one at zero incremental cost. If recovery is unavailable, success one may be infeasible.

## Interpretation and reproducibility

For n=6, m=2, b_1=b_2=2 and no revisions, p_0=1/3 and p_1=1. At inspection price one, the break-even recovery price is 3/2. With the scheduled revision, retaining job-4 and job-5 gives p_0=4/5 while p_1 remains one; the break-even price rises to five. Revision scheduling is therefore a material experimental factor, not a nuisance detail to pool away. An independently randomized revision schedule would be another distribution and needs another calculation.

The [generated results](results/recovery_frontier_report.md) contain both regimes, capacity/clue controls, fixed-policy comparisons, and a grid of exact references. All configurations are constructed diagnostics. They establish neither prevalence in real workloads nor API-dollar savings. Planned policies receive only the existing public policy inputs and fixed distribution parameters; the evaluator still uses trusted Python functions rather than a security isolation boundary.

```powershell
python experiments/dependency_memory/run_recovery_frontier.py
python -m unittest discover -s experiments/dependency_memory -v
```

The earlier 320-case diagnostic remains a separate development-seed comparison. Its generated artifacts are refreshed for the environment extension with recovery disabled; it is not reinterpreted as an exact expectation over this complete routing distribution.
