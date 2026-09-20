# Held-out renderer semantics: offline checkpoint

September 19, 2026.

Four synthetic dependency families now have deterministic explicit and inferred clues. This checkpoint freezes their static metadata and every two-job clue. It makes zero model calls and does not implement a provider request or authorize held-out evaluation.

| Family | Candidate pairs | Clue forms | Target-route checks |
|---|---|---|---|
| alias_chain | 15 | 30 | 60 |
| package_prerequisites | 15 | 30 | 60 |
| validation_scope | 15 | 30 | 60 |
| deployment_handoff | 15 | 30 | 60 |

The 120 family/mode clue entries cover all 15 pairs in two modes across four families. There are 75 unique serialized clues because the 15 explicit forms are shared across families. Each pair has two possible final targets, giving 240 semantic checks; the target is not an argument to either renderer. Inferred forms resolve to exactly the same pair as explicit forms. Separate unit tests check the relation tables, malformed clues, and metadata channels. This is local software validation, not model evidence.

Public metadata describes every job and every relation, independently of the selected pair. Only a manifest selects a dependency request. Metadata stays available at each decision; the selected clue must be removed at memory boundaries by the future request adapter. The existing development and revision interfaces are unchanged and do not dispatch these new formats.

## Remaining limits

- Exact synthetic relation lookup; no natural-task or model-generalization evidence.
- Route repetitions are semantic checks, not independent observations.
- Fixed authored names and mappings; no model-guided prompt or name search.
- Historical route, payload, and call-order reservations remain unchanged.
- Provider allowlist, boundary serialization, and full launch freeze remain future work.
- Static metadata grows with the catalog; byte/token cost is not held equal between families.
- One reserved route per family still confounds family and route effects.

The [machine-readable checkpoint](heldout_renderer_audit.json) is evaluator-only: it contains all pair answers and must never be included wholesale in a model request. See the [renderer contract](../../../docs/HELDOUT_RENDERERS.md).
