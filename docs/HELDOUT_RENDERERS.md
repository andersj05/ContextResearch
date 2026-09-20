# Held-out dependency renderers: offline semantics v1

September 19, 2026. **Offline implementation checkpoint; no held-out model calls.**
The [historical pilot schedule](LLM_PILOT_SPEC.md) reserves four dependency families.
Their clue semantics are now implemented separately from the original development
request interface. The [audit report](../experiments/dependency_memory/results/heldout_renderer_report.md)
and [complete checkpoint](../experiments/dependency_memory/results/heldout_renderer_audit.json)
record the exact metadata and clues. This is not a complete live-launch freeze.

## Purpose

The original development clue matches a requested property directly to a job.
These four formats require resolving a relation before deciding which two records
can matter. They preserve the same six jobs, uniform candidate-pair distribution,
two possible targets per pair, and lexicographic revision rule. They change clue
representation, not the memory or recovery problem.

| Family | Relation needed to interpret the manifest |
|---|---|
| `alias_chain` | Requested aliases pass through intermediate names to source artifacts. |
| `package_prerequisites` | A requested package identifies prerequisite components supplied by two artifacts. |
| `validation_scope` | A verification obligation identifies a scope containing two artifacts. |
| `deployment_handoff` | A handoff identifies required delivery roles and their evidence artifacts. |

The [renderer module](../experiments/dependency_memory/heldout_renderers.py) accepts
only a family, canonical public metadata, candidate keys, and a render mode.
It does not accept a final target, receipt value, source fixture, hidden route,
or evaluator seed. All names and relations are fixed authored fixtures, not
model-optimized prompts. The earlier template-render seed remains a historical
reservation; this deterministic semantic layer does not draw random names.

Every family covers all 15 candidate pairs in both `explicit_labels` and
`inferred_dependencies` mode. Explicit clues state the same pair directly;
inferred clues provide only the selected relation request. An independent test
interpretation of each relation checks its meaning, rather than relying solely
on encoder/decoder round trips. Invalid or injected metadata and clues are rejected.

## Information and evidence boundary

Static public metadata lists all jobs and all dependency relations. It is the
same for every pair, target, retention policy, and receipt payload in a family.
This is permitted persistent public side information. The manifest selects one
request from that catalog and must appear only when inspection or mandatory
disclosure permits it. Its selected content must be deleted at the appropriate
memory boundary; that deletion still needs integration and verification in a
future request adapter.

The checkpoint is evaluator-only. Its `candidate_keys` fields are expected
answers used to check all clues, and the full checkpoint must never be serialized
into a model request. Neither existing live dispatcher accepts this renderer as
a new request version. The original development request bytes and reserved
route assignments are unchanged.

The 120 family/mode clue entries yield 240 pair/target semantic checks. There
are 75 unique serialized clues: the 15 explicit forms are shared across families.
These are
deterministic software checks, not independent trials, a model success rate, or
an estimate of how natural tasks behave. The final target is not an input to
rendering; its two continuations deliberately share the same clue.

## Remaining work before held-out evaluation

1. Integrate these formats into a separately versioned, strictly allowlisted
   request contract and runner, with tests for discarded-data exclusion at both
   boundaries and identical information timing across inspection arms.
2. Validate full-memory, answer-visible, forget-all/recovery, and failure controls
   using the final request format. Freeze instructions, schemas, fixture payloads,
   code, and transport audit together before viewing held-out model responses.
3. Record the model/settings, explicit allocation, accounting, and immutable
   launch manifest. This checkpoint authorizes no model requests.

The static catalogs differ in size, so request bytes and model tokens are not
controlled across families. Equal record slots do not imply equal context cost.
These are synthetic relational lookup tasks, not validated natural-language
reasoning benchmarks. The reserved one-route-per-family sample also confounds
family and route effects; it cannot support family-specific difficulty or broad
generalization claims. No routes have been resampled to improve separation.

## Reproduce without a model

```powershell
python -m unittest discover -s experiments/dependency_memory -p test_heldout_renderers.py -v
python experiments/dependency_memory/audit_heldout_renderers.py
python scripts/validate_context_repo.py
```

The audit records hashes of renderer code, semantic tests, and its generator.
Changes require regenerating the checkpoint and reviewing the intended semantics.
The separate revision diagnostic fingerprints all experiment Python files, so
its unrun plan must also be refreshed after these additions. Historical live
manifests and responses remain immutable.
