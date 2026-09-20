# Revision-aware parent diagnostic

Development only. Each selection is evaluated over 30 routes with an optimal later selector; those routes are not additional model trials.

Fake client: **False**. Model requests: **24**. Request cap: **24**. Held-out requests: **0**.

| Refresh rule | Complete / planned | Optimal parent | Mean availability | Mean exact parent regret |
|---|---|---|---|---|
| lexicographic_first | 8/8 | 8/8 | 4/5 | 0 |
| lexicographic_last | 8/8 | 8/8 | 4/5 | 0 |
| none | 8/8 | 8/8 | 1/3 | 0 |

Failures and incomplete decisions remain in the scheduled denominators. Means use only valid completed responses; no failure is imputed as an empty selection.

| Case | Rule | Status | Keys | Displayed positions (1-based) | Availability | Exact parent regret |
|---|---|---|---|---|---|---|
| f1-o3-r0 | lexicographic_first | completed | ['job-4', 'job-5'] | [3, 5] | 4/5 | 0 |
| f1-o1-r1 | lexicographic_last | completed | ['job-0', 'job-1'] | [6, 5] | 4/5 | 0 |
| f1-o0-r2 | none | completed | ['job-0', 'job-1'] | [1, 2] | 1/3 | 0 |
| f0-o1-r1 | lexicographic_last | completed | ['job-0', 'job-1'] | [6, 5] | 4/5 | 0 |
| f0-o0-r1 | lexicographic_last | completed | ['job-0', 'job-1'] | [1, 2] | 4/5 | 0 |
| f1-o0-r1 | lexicographic_last | completed | ['job-0', 'job-1'] | [1, 2] | 4/5 | 0 |
| f1-o3-r2 | none | completed | ['job-0', 'job-1'] | [2, 4] | 1/3 | 0 |
| f1-o3-r1 | lexicographic_last | completed | ['job-0', 'job-1'] | [2, 4] | 4/5 | 0 |
| f1-o2-r1 | lexicographic_last | completed | ['job-0', 'job-1'] | [5, 3] | 4/5 | 0 |
| f0-o1-r2 | none | completed | ['job-0', 'job-1'] | [6, 5] | 1/3 | 0 |
| f0-o1-r0 | lexicographic_first | completed | ['job-4', 'job-5'] | [2, 1] | 4/5 | 0 |
| f0-o2-r1 | lexicographic_last | completed | ['job-0', 'job-1'] | [5, 3] | 4/5 | 0 |
| f0-o3-r2 | none | completed | ['job-0', 'job-1'] | [2, 4] | 1/3 | 0 |
| f1-o1-r0 | lexicographic_first | completed | ['job-4', 'job-5'] | [2, 1] | 4/5 | 0 |
| f0-o2-r2 | none | completed | ['job-0', 'job-1'] | [5, 3] | 1/3 | 0 |
| f0-o2-r0 | lexicographic_first | completed | ['job-4', 'job-5'] | [4, 2] | 4/5 | 0 |
| f0-o3-r0 | lexicographic_first | completed | ['job-4', 'job-5'] | [3, 5] | 4/5 | 0 |
| f0-o0-r0 | lexicographic_first | completed | ['job-4', 'job-5'] | [5, 6] | 4/5 | 0 |
| f1-o2-r0 | lexicographic_first | completed | ['job-4', 'job-5'] | [4, 2] | 4/5 | 0 |
| f0-o3-r1 | lexicographic_last | completed | ['job-0', 'job-1'] | [2, 4] | 4/5 | 0 |
| f1-o0-r0 | lexicographic_first | completed | ['job-4', 'job-5'] | [5, 6] | 4/5 | 0 |
| f1-o1-r2 | none | completed | ['job-0', 'job-1'] | [6, 5] | 1/3 | 0 |
| f1-o2-r2 | none | completed | ['job-0', 'job-1'] | [5, 3] | 1/3 | 0 |
| f0-o0-r2 | none | completed | ['job-0', 'job-1'] | [1, 2] | 1/3 | 0 |

Refresh provides a free information channel; raw availability across refresh/no-refresh rules is not an understanding effect. Rule-specific exact regret and matched direction shifts are the diagnostic outcomes. The response enum and job metadata retain canonical order. Two receipt fixtures and four record orders do not establish population generalization or internal reasoning mechanisms.

| Fixture | Record order | Pair complete | First-minus-last selected-rank sum |
|---|---|---|---|
| 0 | 0 | True | 8 |
| 0 | 1 | True | 8 |
| 0 | 2 | True | 8 |
| 0 | 3 | True | 8 |
| 1 | 0 | True | 8 |
| 1 | 1 | True | 8 |
| 1 | 2 | True | 8 |
| 1 | 3 | True | 8 |

Conservative credit-equivalent budget: 12.0; committed: 0.58328; uncertain reservations: 0.0.

Actual subscription debit attributable to this diagnostic is unknown. API billing, purchases, and resets are excluded. Input includes cached input; output includes reasoning, so these buckets must not be added again.

| Reported token bucket | Subtotal | Attempts measured |
|---|---|---|
| input_tokens | 66200 | 24/24 |
| cached_input_tokens | 17920 | 24/24 |
| output_tokens | 5651 | 24/24 |
| reasoning_output_tokens | 5075 | 24/24 |
