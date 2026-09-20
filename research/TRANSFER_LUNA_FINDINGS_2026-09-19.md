# Luna transfer study: final development findings

Study label: September 19, 2026. Both phases with model generations began on September 20 UTC, still September 19 locally. **The fixed allocation is complete: 1,536 dispatched requests, 1,533 valid selections, and three permanently missing outcomes. The primary comparison does not establish a prospective-guidance benefit.** Its positive normalized-regret estimate has a descriptive interval that includes zero. This is controlled synthetic development evidence, not a natural-task or native-compaction benchmark.

The [descriptive findings](../experiments/dependency_memory/results/transfer_luna_2026-09-19_continuation/findings_summary.json), [pooled summary](../experiments/dependency_memory/results/transfer_luna_2026-09-19_continuation/pooled_summary.json), and [full report](../experiments/dependency_memory/results/transfer_luna_2026-09-19_continuation/report.md) preserve the denominators, all 48 condition summaries, and primary comparisons. The [saved independent local audit](../experiments/dependency_memory/results/transfer_luna_2026-09-19_continuation/independent_audit.json) passes. Local evidence checks establish consistency and provenance; they are not external scientific review or certification of provider internals.

## Question and controlled design

The study asks whether guidance to consider future information arrivals helps a model choose what to retain. It follows three parent-selection deficits in the first workflow and 24 optimal selections in a separate simplified diagnostic. Those earlier experiments changed several features together and could not identify why their outcomes differed.

The [frozen design](../docs/TRANSFER_STUDY.md) crosses six or twelve jobs, compact or workflow framing, an explicit or unspecified optimal-later-selector guarantee, generic or prospective guidance, and minimum-priority, maximum-priority, or no refresh. All 48 combinations occur in each of 32 generated blocks. The workflow condition adds handoff wording and three fixed public events; it is not a naturalistic long-context execution.

Public refresh priorities are randomized independently of stable job names, and visible-record order is independently shuffled. Matched conditions share materials. Canonical metadata and response-schema ordering remain visible. Each fresh isolated request selects at most two records, without access to the future candidate pair, final target, earlier answers, or outcome feedback. The model is the mutable `gpt-5.6-luna` alias, with low reasoning effort and default service tier.

Every valid selection is graded over all 30 possible pair/target routes at six jobs or 132 at twelve. These are counterfactual calculations for one answer, not additional model trials. The later selector is never invoked: scoring assumes optimal later use even when the prompt does not promise that skill. Its two slots equal the two-candidate count, making the second boundary nonbinding. Availability includes scheduled refreshed records, not only information preserved from the original memory.

## Execution and missing outcomes

An initial launch at `999f14d` stopped before generation at its local quota guard. The launch at `0414198` subsequently dispatched 888 requests and accepted 885 responses. Three completed, fully metered generations failed a post-generation percentage check before their answers were retained. Those three outcomes remain transport failures; their quality is unknown.

The [operational amendment](../docs/TRANSFER_CONTINUATION.md) permitted only the 648 provably never-dispatched cases to proceed through normal subscription routing with existing-credit eligibility checks. The continuation at `f9012a2` completed all 648. Public request bytes, case order within workers, scientific conditions, and the original 1,536-request/200-equivalent allocation were preserved. No dispatched case was retried or replaced. A separate zero-generation continuation-preparation error and its correction are also documented.

The pooled evidence contains 1,541 host-attempt records: five preflight-only failures explain the difference from 1,536 model requests. Each model case contributes exactly once. All three lost responses fall outside the primary comparison, so its 128 pairs and all 32 primary blocks are complete. Full factorial blocks 16–18 retain their missing outcomes. The administrative interruption remains part of the study history.

## Final selection results

| Conditions | Scheduled | Valid selections | Optimal | Strict deficits |
|---|---:|---:|---:|---:|
| Refresh present | 1,024 | 1,022 | 912 | 110 |
| No refresh | 512 | 511 | 510 | 1 |
| All conditions | 1,536 | 1,533 | 1,422 | 111 |

There were no schema-policy failures. One valid response selected no records; the other 1,532 selected two. Empty selection was permitted and is graded as suboptimal, not discarded as invalid. It occurred in a no-refresh condition, where every full two-record pair ties. Accordingly, the 510 optimal no-refresh answers do not demonstrate refresh-rule understanding. “Optimal” denotes the best achievable reference availability, not guaranteed success on every future route.

The prespecified primary comparison uses workflow framing, an unspecified later selector, and refresh-present conditions. Generic guidance gives **114/128 optimal selections**, compared with **118/128** for prospective guidance. Across matched pairs, prospective guidance has lower regret in **13**, generic guidance in **nine**, and **106 tie**.

Mean normalized regret benefit, defined as generic minus prospective regret, is **107/5120, approximately 0.0208984**. The complete-block mean is identical. Its descriptive 95% block-bootstrap interval, using the fixed 5,000-resample procedure, is **[-0.0203125, 0.060546875]**. Because the interval includes zero, this does not confirm a guidance gain; neither does it establish equivalence or absence of an effect.

Normalization uses each job count's best-to-worst full-pair regret range: 4/15 at six jobs and 5/33 at twelve. The estimate is not a percentage-point increase in task success. Mean raw availability-regret benefit is **-7/1920 at six jobs** and **71/8448 at twelve**; the point estimates have opposite signs. Blocks are constructed task sets, and the descriptive resampling does not model all shared worker, timing, or backend dependence.

## Descriptive error patterns

Among the 111 suboptimal valid selections, **50** match the two lowest job names, **15** the two highest, and **37** the optimum for the opposite refresh direction. These are overlapping marginal counts: two outputs match both a key-extreme and opposite-rule pattern. Their union covers **100** selections; the other **11** include the empty response.

These matches describe outputs. They do not identify internal reasoning, a stable model policy, or causes of error. The complete condition table remains available rather than selecting favorable cells after observing results. This study also does not causally explain the first workflow's mistakes or establish that its guidance fixes them.

## Accounting and relation to the interim

All 1,536 generations, including the three lost answers, have settled usage: **48.78528 conservative credit equivalents** against the original 200-equivalent cap, with no uncertain reservations. Reported totals are 4,768,512 input tokens, including 2,412,032 cached input, and 632,736 output tokens, including 595,880 reasoning tokens. Every generation explicitly reported zero cache-write tokens. Included categories are not added again. Actual experiment-attributable subscription debit remains unknown. No API billing, purchase, reset, or held-out call occurred.

The [first-eight-block checkpoint](../experiments/dependency_memory/results/transfer_interim_8blocks.json) remains preserved: 384 valid selections, 354 optimal, and a primary normalized benefit of 13/256 with an interval including zero. It did not change the sample, prompts, or analysis. Final results replace its provisional estimates; the checkpoint is not an independent replication.

The completed study supplies auditable record-selection evidence and a bounded, inconclusive guidance comparison. It does not measure repeated native compaction, unrestricted downstream agents, naturalistic long-context performance, or real-world savings. The mathematical bit-chain results remain a separate evidence layer; this record experiment neither proves nor empirically validates their practical prevalence.
