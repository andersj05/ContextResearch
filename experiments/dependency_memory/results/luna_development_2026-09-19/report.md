# Development pilot report

Exploratory development/debugging only. These paired measurements share one development route; they are not independent trials, held-out evidence, or evidence of general superiority.

Client: **codex-subscription-gpt-5.6-luna-low**. Fake client: **no**. Version: `development_pilot_v0.3`.

Manifest SHA-256: `a88f9e53d6a3f80fabb2f5f77900aa5c63c7d58d22b24a3704417b1826c4aadb`. Request-audit SHA-256: `7b4d83a3658ad913932f02bd682cd869f94177800886665f3a67e4604d579ef3`.

## Completion and accounting

| Quantity | Recorded value |
| --- | --- |
| Maximum scheduled requests | 96 |
| Run request cap | 96 |
| Request attempts (including failures) | 96 |
| Recorded model requests | 96 |
| Held-out requests | 0 |
| Stage A decisions: planned / attempted | 12 / 12 |
| Stage A statuses | completed=12; policy_failure=0; transport_failure=0; incomplete=0; reserved=0 |
| Stage B episodes: planned / attempted | 36 / 36 |
| Stage B statuses | completed=36; policy_failure=0; transport_failure=0; incomplete=0; reserved=0 |
| Stage B request attempts | 84 |
| Stage B terminal successes / planned | 36 / 36 |
| Pre-recovery available / reached measurement | 21 / 36 |
| Pre-recovery measurement not reached | 0 |
| Recovery attempts | 15 |
| Synthetic action cost, all episodes including partial/failed | 431 |
| Synthetic action cost, completed episodes only | 431 |
| API dollars | 0 |
| Subscription usage | see provider ledger; not API dollars |
| Subscription credits consumed | unknown |
| Planning cap, credit equivalents (not an invoice cap) | 20.0 |
| Reservation per generation, credit equivalents | 10.4025 |
| Settled conservative credit equivalents | 2.5395 |
| Uncertain held reservations, credit equivalents | 0.0 |
| Committed total, credit equivalents | 2.5395 |
| Remaining planning budget, credit equivalents | 17.4605 |
| Basic-rate credit estimate, measured usage | 1.915656 reported (96/96 attempts measured) |
| Total measured request latency (seconds) | 1057.092953 reported (96/96 attempts measured) |
| Input tokens | 276048 reported (96/96 attempts measured) |
| Cached input tokens | 61952 reported (96/96 attempts measured) |
| Output tokens | 27140 reported (96/96 attempts measured) |
| Reasoning output tokens | 24944 reported (96/96 attempts measured) |

Request statuses: completed=96; policy_failure=0; reserved=0; transport_failure=0.

Input includes cached input; reasoning may overlap output. These buckets are not added together. Reported subtotals with incomplete coverage are not full-run totals. Synthetic action units, tokens, subscription credits, and API dollars are distinct quantities. Credit equivalents are conditional token-derived planning amounts, not observed account debits. Shared-account quota movement is not attributed wholly to this run.

| Transport field | Recorded value |
| --- | --- |
| Model alias | gpt-5.6-luna |
| Immutable model revision | mutable alias; no immutable revision exposed |
| CLI/client version | 0.155.0-alpha.9.2 |
| Reasoning effort | low |
| Service tier | default |
| Configured HTTP and stream retries | 0 |
| Generation continuation guard | one-generation weighted rollout budget; controlled sessionBudgetExceeded is retained |
| Hard output token cap | unknown |
| Published output maximum used for planning | 128000 |
| Verified subscription charge bound | unknown |
| Account quota stop, percent used | 80 |
| Cross-request state contract | New app-server process and ephemeral thread per request; no environments, archive, prior outputs, or session links |

Missing transport/accounting fields mean unknown, not zero. A model alias is not an immutable revision.

## Stage A: inspection decisions

Expected extra costs and regret use the exact uniform-route population calibration, in synthetic action units. Replicates are listed separately; no significance calculation is made.

| Cell | Replicate | Status | Inspect | Expected extra cost | Exact regret |
| --- | --- | --- | --- | --- | --- |
| ample_parent | 0 | completed | no | 0 | 0 |
| ample_parent | 1 | completed | no | 0 | 0 |
| cheap_recovery | 0 | completed | no | 2/3 | 0 |
| cheap_recovery | 1 | completed | no | 2/3 | 0 |
| costly_recovery | 0 | completed | yes | 1 | 0 |
| costly_recovery | 1 | completed | yes | 1 | 0 |
| revision_cheap_recovery | 0 | completed | no | 4/5 | 0 |
| revision_cheap_recovery | 1 | completed | yes | 1 | 1/5 |
| revision_costly_recovery | 0 | completed | yes | 1 | 0 |
| revision_costly_recovery | 1 | completed | no | 8/5 | 3/5 |
| small_child | 0 | completed | no | 14/5 | 0 |
| small_child | 1 | completed | no | 14/5 | 0 |

## Stage B: retention and recovery

Reliable scripted recovery can make even empty retention succeed. Terminal success primarily checks execution; pre-recovery availability and synthetic completion cost carry the retention signal. Each row remains present after failure or a budget stop.

Cost delta compares a completed episode with the fixed population policy using the same inspection choice on the exact same fixture. Partial episode costs receive no completed-reference delta.

| Cell | Mode | Arm | Status | Requests | Inspect | Pre-recovery | Recovered | Success | Cost | Cost delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ample_parent | explicit_labels | always_inspect | completed | 2 | yes | yes | no | yes | 11 | 0 |
| ample_parent | explicit_labels | model_selective | completed | 3 | no | yes | no | yes | 10 | 0 |
| ample_parent | explicit_labels | never_inspect | completed | 2 | no | yes | no | yes | 10 | 0 |
| ample_parent | inferred_dependencies | always_inspect | completed | 2 | yes | yes | no | yes | 11 | 0 |
| ample_parent | inferred_dependencies | model_selective | completed | 3 | no | yes | no | yes | 10 | 0 |
| ample_parent | inferred_dependencies | never_inspect | completed | 2 | no | yes | no | yes | 10 | 0 |
| cheap_recovery | explicit_labels | always_inspect | completed | 2 | yes | yes | no | yes | 11 | 0 |
| cheap_recovery | explicit_labels | model_selective | completed | 3 | no | no | yes | yes | 11 | 0 |
| cheap_recovery | explicit_labels | never_inspect | completed | 2 | no | no | yes | yes | 11 | 0 |
| cheap_recovery | inferred_dependencies | always_inspect | completed | 2 | yes | yes | no | yes | 11 | 0 |
| cheap_recovery | inferred_dependencies | model_selective | completed | 3 | no | no | yes | yes | 11 | 0 |
| cheap_recovery | inferred_dependencies | never_inspect | completed | 2 | no | no | yes | yes | 11 | 0 |
| costly_recovery | explicit_labels | always_inspect | completed | 2 | yes | yes | no | yes | 11 | 0 |
| costly_recovery | explicit_labels | model_selective | completed | 3 | yes | yes | no | yes | 11 | 0 |
| costly_recovery | explicit_labels | never_inspect | completed | 2 | no | no | yes | yes | 14 | 0 |
| costly_recovery | inferred_dependencies | always_inspect | completed | 2 | yes | yes | no | yes | 11 | 0 |
| costly_recovery | inferred_dependencies | model_selective | completed | 3 | yes | yes | no | yes | 11 | 0 |
| costly_recovery | inferred_dependencies | never_inspect | completed | 2 | no | no | yes | yes | 14 | 0 |
| revision_cheap_recovery | explicit_labels | always_inspect | completed | 2 | yes | yes | no | yes | 11 | 0 |
| revision_cheap_recovery | explicit_labels | model_selective | completed | 3 | yes | yes | no | yes | 11 | 0 |
| revision_cheap_recovery | explicit_labels | never_inspect | completed | 2 | no | no | yes | yes | 14 | 4 |
| revision_cheap_recovery | inferred_dependencies | always_inspect | completed | 2 | yes | yes | no | yes | 11 | 0 |
| revision_cheap_recovery | inferred_dependencies | model_selective | completed | 3 | yes | yes | no | yes | 11 | 0 |
| revision_cheap_recovery | inferred_dependencies | never_inspect | completed | 2 | no | no | yes | yes | 14 | 4 |
| revision_costly_recovery | explicit_labels | always_inspect | completed | 2 | yes | yes | no | yes | 11 | 0 |
| revision_costly_recovery | explicit_labels | model_selective | completed | 3 | yes | yes | no | yes | 11 | 0 |
| revision_costly_recovery | explicit_labels | never_inspect | completed | 2 | no | yes | no | yes | 10 | 0 |
| revision_costly_recovery | inferred_dependencies | always_inspect | completed | 2 | yes | yes | no | yes | 11 | 0 |
| revision_costly_recovery | inferred_dependencies | model_selective | completed | 3 | yes | yes | no | yes | 11 | 0 |
| revision_costly_recovery | inferred_dependencies | never_inspect | completed | 2 | no | no | yes | yes | 18 | 8 |
| small_child | explicit_labels | always_inspect | completed | 2 | yes | no | yes | yes | 15 | 4 |
| small_child | explicit_labels | model_selective | completed | 3 | yes | no | yes | yes | 15 | 4 |
| small_child | explicit_labels | never_inspect | completed | 2 | no | no | yes | yes | 14 | 0 |
| small_child | inferred_dependencies | always_inspect | completed | 2 | yes | no | yes | yes | 15 | 4 |
| small_child | inferred_dependencies | model_selective | completed | 3 | no | no | yes | yes | 14 | 0 |
| small_child | inferred_dependencies | never_inspect | completed | 2 | no | no | yes | yes | 14 | 0 |

### Fixed-policy comparison on the exact fixture

Both policies were fixed from the public population before evaluation. These realized costs are not population expectations and must not be used to refit the policy to this one target.

| Cell | Route | Skip cost | Skip pre-recovery | Inspect cost | Inspect pre-recovery |
| --- | --- | --- | --- | --- | --- |
| ample_parent | 21 | 10 | yes | 11 | yes |
| cheap_recovery | 21 | 11 | no | 11 | yes |
| costly_recovery | 21 | 14 | no | 11 | yes |
| revision_cheap_recovery | 21 | 10 | yes | 11 | yes |
| revision_costly_recovery | 21 | 10 | yes | 11 | yes |
| small_child | 21 | 14 | no | 11 | yes |

### Stage B reported token usage

Coverage counts include unsuccessful request attempts. Unknown or missing usage is not replaced by zero.

| Cell | Mode | Arm | Input tokens | Output tokens |
| --- | --- | --- | --- | --- |
| ample_parent | explicit_labels | always_inspect | 5963 reported (2/2 attempts measured) | 269 reported (2/2 attempts measured) |
| ample_parent | explicit_labels | model_selective | 8792 reported (3/3 attempts measured) | 548 reported (3/3 attempts measured) |
| ample_parent | explicit_labels | never_inspect | 5947 reported (2/2 attempts measured) | 163 reported (2/2 attempts measured) |
| ample_parent | inferred_dependencies | always_inspect | 5999 reported (2/2 attempts measured) | 181 reported (2/2 attempts measured) |
| ample_parent | inferred_dependencies | model_selective | 8812 reported (3/3 attempts measured) | 584 reported (3/3 attempts measured) |
| ample_parent | inferred_dependencies | never_inspect | 5966 reported (2/2 attempts measured) | 142 reported (2/2 attempts measured) |
| cheap_recovery | explicit_labels | always_inspect | 5800 reported (2/2 attempts measured) | 134 reported (2/2 attempts measured) |
| cheap_recovery | explicit_labels | model_selective | 8635 reported (3/3 attempts measured) | 627 reported (3/3 attempts measured) |
| cheap_recovery | explicit_labels | never_inspect | 5790 reported (2/2 attempts measured) | 355 reported (2/2 attempts measured) |
| cheap_recovery | inferred_dependencies | always_inspect | 5836 reported (2/2 attempts measured) | 138 reported (2/2 attempts measured) |
| cheap_recovery | inferred_dependencies | model_selective | 8655 reported (3/3 attempts measured) | 1188 reported (3/3 attempts measured) |
| cheap_recovery | inferred_dependencies | never_inspect | 5809 reported (2/2 attempts measured) | 279 reported (2/2 attempts measured) |
| costly_recovery | explicit_labels | always_inspect | 5800 reported (2/2 attempts measured) | 139 reported (2/2 attempts measured) |
| costly_recovery | explicit_labels | model_selective | 8645 reported (3/3 attempts measured) | 465 reported (3/3 attempts measured) |
| costly_recovery | explicit_labels | never_inspect | 5790 reported (2/2 attempts measured) | 405 reported (2/2 attempts measured) |
| costly_recovery | inferred_dependencies | always_inspect | 5836 reported (2/2 attempts measured) | 202 reported (2/2 attempts measured) |
| costly_recovery | inferred_dependencies | model_selective | 8682 reported (3/3 attempts measured) | 683 reported (3/3 attempts measured) |
| costly_recovery | inferred_dependencies | never_inspect | 5809 reported (2/2 attempts measured) | 225 reported (2/2 attempts measured) |
| revision_cheap_recovery | explicit_labels | always_inspect | 5800 reported (2/2 attempts measured) | 187 reported (2/2 attempts measured) |
| revision_cheap_recovery | explicit_labels | model_selective | 8645 reported (3/3 attempts measured) | 775 reported (3/3 attempts measured) |
| revision_cheap_recovery | explicit_labels | never_inspect | 5788 reported (2/2 attempts measured) | 1152 reported (2/2 attempts measured) |
| revision_cheap_recovery | inferred_dependencies | always_inspect | 5836 reported (2/2 attempts measured) | 398 reported (2/2 attempts measured) |
| revision_cheap_recovery | inferred_dependencies | model_selective | 8682 reported (3/3 attempts measured) | 917 reported (3/3 attempts measured) |
| revision_cheap_recovery | inferred_dependencies | never_inspect | 5849 reported (2/2 attempts measured) | 624 reported (2/2 attempts measured) |
| revision_costly_recovery | explicit_labels | always_inspect | 5800 reported (2/2 attempts measured) | 159 reported (2/2 attempts measured) |
| revision_costly_recovery | explicit_labels | model_selective | 8645 reported (3/3 attempts measured) | 636 reported (3/3 attempts measured) |
| revision_costly_recovery | explicit_labels | never_inspect | 5825 reported (2/2 attempts measured) | 580 reported (2/2 attempts measured) |
| revision_costly_recovery | inferred_dependencies | always_inspect | 5836 reported (2/2 attempts measured) | 193 reported (2/2 attempts measured) |
| revision_costly_recovery | inferred_dependencies | model_selective | 8682 reported (3/3 attempts measured) | 851 reported (3/3 attempts measured) |
| revision_costly_recovery | inferred_dependencies | never_inspect | 5807 reported (2/2 attempts measured) | 988 reported (2/2 attempts measured) |
| small_child | explicit_labels | always_inspect | 5800 reported (2/2 attempts measured) | 270 reported (2/2 attempts measured) |
| small_child | explicit_labels | model_selective | 8645 reported (3/3 attempts measured) | 973 reported (3/3 attempts measured) |
| small_child | explicit_labels | never_inspect | 5790 reported (2/2 attempts measured) | 438 reported (2/2 attempts measured) |
| small_child | inferred_dependencies | always_inspect | 5836 reported (2/2 attempts measured) | 195 reported (2/2 attempts measured) |
| small_child | inferred_dependencies | model_selective | 8655 reported (3/3 attempts measured) | 936 reported (3/3 attempts measured) |
| small_child | inferred_dependencies | never_inspect | 5809 reported (2/2 attempts measured) | 469 reported (2/2 attempts measured) |

## Interpretation limits

One development template and one route were used. Repeated modes and arms reuse paired fixtures; they do not increase the number of independent routes. The reserved held-out sample remains unrun by this runner and, when run, is a debugging exercise. This report establishes no native-harness comparison, statistical significance, generalization, or general superiority.
