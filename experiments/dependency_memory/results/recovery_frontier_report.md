# Exact recovery comparison: development results

September 18, 2026.

2640 scripted episodes across ten settings check the executable reference and heuristic policies. A separate grid contains 3000 exact parameter configurations. These are constructed diagnostics, not independent task samples or LLM trials.

Costs below are expected extra synthetic units above the common workflow cost of 10. p0/p1 are optimal hit probabilities without/with early inspection before recovery. All reported fractions are exact.

| Setting | p0 | p1 | Inspection / recovery price | Cheapest success-one endpoint(s) | Extra cost |
|---|---|---|---|---|---|
| cheap_recovery | 1/3 | 1 | 1 / 1 | retain+recover | 2/3 |
| costly_recovery | 1/3 | 1 | 1 / 4 | inspect, inspect+recover | 1 |
| revision_cheap_recovery | 4/5 | 1 | 1 / 4 | retain+recover | 4/5 |
| revision_costly_recovery | 4/5 | 1 | 1 / 8 | inspect, inspect+recover | 1 |
| ample_parent | 1 | 1 | 1 / 4 | retain, retain+recover | 0 |
| small_child | 3/10 | 1/2 | 1 / 4 | retain+recover | 14/5 |
| uninformative_manifest | 1/3 | 1/3 | 1 / 4 | retain+recover | 8/3 |
| inspection_unavailable | 1/3 | 1 | off / 4 | retain+recover | 8/3 |
| recovery_unavailable | 1/3 | 1 | 1 / off | inspect | 1 |
| anticipate_revision | 2/3 | 1 | 1 / 4 | inspect, inspect+recover | 1 |

## Findings

With six jobs, two candidates, and two record slots at each boundary, reliable recovery at price one reaches success one for an expected extra cost of 2/3. Inspection costs one and is dominated. Raising recovery price to four makes inspection the cheaper success-one choice. The break-even recovery price is 3/2 in this no-revision setting.

The public revision schedule raises the best uninspected hit probability from 1/3 to 4/5: storing job-4 and job-5 exploits the known refresh of the smallest candidate. The inspection break-even recovery price rises to five. This is an effect of the specified scheduling distribution, not a universal benefit of revisions.

With a one-record child and no revisions, early inspection raises pre-recovery success from 3/10 to 1/2, yet at recovery price four its one-unit charge exceeds the 4/5 expected recovery cost it avoids. Inspection helps retention while making the success-one policy more expensive. Ample parent memory and an uninformative manifest give additional null controls.

## Evidence and scope

[All executed outcomes](recovery_episodes.csv), [exact grid](recovery_grid.csv), and [summary with frontier vertices and source hashes](recovery_frontier_summary.json) are regenerated together. Reference endpoints are checked against actual environment runs over every candidate/target pair; tests independently enumerate small decision trees and hypergeometric probabilities.

The frontier allows randomized policies and constrains expected extra cost, with nonbinding episode limits. It assumes reliable late recovery, opaque atomic records, a known uniform routing distribution, and the published revision rule. It does not optimize arbitrary bit encodings, model summaries, archive storage, unreliable retrieval, or unknown real-world dependencies. See the [derivation and information contract](../RECOVERY_FRONTIER.md).
