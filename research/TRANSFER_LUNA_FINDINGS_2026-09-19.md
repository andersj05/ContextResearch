# Luna transfer study: provisional first-eight-block findings

September 19, 2026. **Interim only; the fixed study remains active and unchanged. No treatment gain is confirmed.** This note covers blocks 0–7, the descriptive checkpoint permitted before launch. It excludes all later responses and is not a final usage or whole-run accounting report.

The [independent interim audit](../experiments/dependency_memory/results/transfer_interim_8blocks.json) checks 384 public requests and their responses, re-enumerates their possible continuations, and verifies 52 source blobs against frozen commit `04141984d56fa0f80429d19dc45f589fef8ac5a6`. Its saved timestamp is September 20 at 02:05 UTC, still September 19 in the project's local time zone. This is a local evidence check, not external scientific review.

## What the checkpoint contains

All **384 responses are valid**, and every response retains two records. **354/384 selections are optimal** under the declared later-selection reference. The useful separation is **226/256 optimal in refresh-present conditions** and **128/128 in no-refresh conditions**. Every full pair ties without refresh, so the latter result checks capacity and response validity rather than identifying a superior choice of records.

The [frozen design](../docs/TRANSFER_STUDY.md) varies six versus twelve jobs, compact versus workflow framing, an explicit versus unspecified later-selector guarantee, generic versus prospective guidance, and refresh direction. Public priorities are randomized independently of job names, and visible order is shuffled. The 48 conditions within each block share materials. These eight generated blocks are therefore the units for the reported resampling, not 384 independent natural tasks.

Every answer is graded over 30 possible continuations for six jobs or 132 for twelve. Those continuations provide exact conditional scores; they do not create additional model observations. The later selector itself is not run. Even where the prompt does not promise its skill, scoring measures the potential available to an optimal later selector.

## Prespecified guidance comparison

The primary comparison uses workflow framing, unspecified later-selector behavior, and refresh-present conditions. It supplies **32 matched pairs** in this checkpoint. Generic guidance produces **26/32 optimal selections**, compared with **30/32** for guidance to consider future information arrivals.

Mean normalized regret benefit, defined as generic minus prospective regret, is **13/256**. The descriptive 95% block-bootstrap interval is **[-0.0546875, 0.15625]**, from the fixed 5,000-resample procedure. The interval includes zero. The positive point estimate is consequently a provisional observation, not a confirmed guidance benefit. Normalization accounts for the different available regret ranges at the two job counts; it is not a direct percentage-point change in task success.

Mean raw availability-regret benefit is **1/96 at six jobs** and **5/528 at twelve**. Prospective guidance has lower regret in five matched pairs, generic guidance in one, and 26 tie. All eight blocks and all 32 primary pairs are complete, so missing-response exclusions do not separate the pair and complete-block estimates at this checkpoint.

## Error patterns and remaining boundaries

Among the 30 suboptimal selections, **17 match the two lowest or highest job names**, **10 match the optimum for the opposite refresh direction**, and **three match neither pattern**. These groups happen not to overlap in this interim. They describe outputs, not an identified internal mechanism, persistent policy, or explanation of why the model chose them. No answers are underfilled.

The earlier [24-request diagnostic](REVISION_LUNA_FINDINGS_2026-09-19.md) produced only optimal selections under simpler conditions. The current observations do not causally reproduce or explain the first workflow's three mistakes: priorities, task presentation, and experimental conditions differ. Neither experiment establishes improved native compaction or real-world agent performance.

The active allocation remains **1,536 requests and 200 conservative credit equivalents** across four workers. An earlier [launch at `999f14d`](../experiments/dependency_memory/results/transfer_luna_2026-09-19/summary.json) stopped before any model generation or credit reservation at the historical local quota threshold. That evidence is preserved. The documented operational amendment preceded the active launch and left all public requests unchanged. Final usage and conclusions await completion and the whole-run audit; this checkpoint causes no prompt change, retry, early stopping, or additional allocation.
