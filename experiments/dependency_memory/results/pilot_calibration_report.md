# Pilot calibration and reserved schedule

September 19, 2026.

This is an offline plan, not a model result or a launch-ready run manifest. No model requests have been made by this artifact. See the [pilot specification](../../../docs/LLM_PILOT_SPEC.md).

The costs below are exact full-route expectations for optimal atomic-record retention, reliable recovery, and nonbinding episode limits. They exclude the common ten-unit workflow and all API costs.

| Regime | Hit without / with inspection | Extra cost: skip / inspect | Cheaper decision | Cost of choosing the other decision |
|---|---|---|---|---|
| cheap_recovery | 1/3 / 1 | 2/3 / 1 | skip | 1/3 |
| costly_recovery | 1/3 / 1 | 8/3 / 1 | inspect | 5/3 |
| revision_cheap_recovery | 4/5 / 1 | 4/5 / 1 | skip | 1/5 |
| revision_costly_recovery | 4/5 / 1 | 8/5 / 1 | inspect | 3/5 |
| ample_parent | 1 / 1 | 0 / 1 | skip | 1 |
| small_child | 3/10 / 1/2 | 14/5 / 3 | skip | 1/5 |

## Prespecified stages

Stage A reserves 12 inspection decisions across six regimes, with exact scripted retention and recovery. Each decision can be evaluated over all 30 routes; those route checks are not independent model decisions.

Stage B reserves 36 development and 144 held-out episodes across three inspection arms and two render modes. One development route and four distinct held-out routes are paired across regimes, render modes, and arms. Template families are reserved specifications; their natural-language fixtures have not been authored or validated.

The maximum planned total is 432 requests, with no automatic retries. Exact model revision, settings, token caps, official price snapshot, dollar budget, renderer/prompt hashes, and isolation audit remain open. A request ceiling alone is not spending authorization.

## Interpretation

Under perfect scripted retention, costly recovery and costly recovery with the scheduled revision favor inspection. Cheap recovery, cheaper recovery with that revision, ample parent memory, and the small child capacity favor skipping it. In Stage B an imperfect model may face different effective hit rates; reference disagreement alone is not proof of an irrational inspection decision.

[Machine-readable plan](pilot_plan.json) includes evaluator-only route indices, reserved seeds, pair identifiers, execution order, unresolved launch fields, and source hashes. It must never be serialized wholesale into a model request. All counts are planned; the existing recovery report remains the completed scripted evidence.
