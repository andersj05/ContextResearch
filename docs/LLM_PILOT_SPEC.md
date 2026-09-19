# Pilot specification: choosing inspection before compaction

September 19, 2026. Design candidate v0.1; **offline scheduling and calibration only**. No model adapter, natural-language fixture renderer, model result, or approved spending allocation is supplied by this document. The model launch remains gated on the unresolved fields below. The governing [experiment protocol](EXPERIMENT_PROTOCOL.md) and [atomic-record environment contract](../experiments/dependency_memory/ARTIFACT_WORKFLOW.md) still apply.

## Question and scope

Can a model choose when to inspect upcoming dependencies before a memory boundary, accounting for later recovery and a second memory limit? Can the same manager preserve useful records when dependencies must be inferred from task evidence?

Separate these questions. **Stage A** tests the inspection decision while exact scripted retention and reliable recovery are guaranteed. **Stage B** adds model retention and inferred dependencies. The exact optimal-retention decision is a calibration label in A; in B, a model's weaker retention or interpretation can change which action is best for that model. Reference disagreement alone therefore does not demonstrate an irrational decision in B.

This is a small exploratory debugging pilot, not a powered benchmark. It tests a model manager inside a scripted workflow. It does not test a full autonomous agent, prose versus structured summarization, native provider compaction, learned retirement, or bit-optimal compression. Those comparisons need separate protocols and baselines; restricting this first pilot does not satisfy the protocol's eventual native-harness comparison.

## Exact calibration cells

Use these six existing scenarios from [the recovery runner](../experiments/dependency_memory/run_recovery_frontier.py). All have six jobs, two candidates, inspection price one, reliable matched recovery, delay three, and common mandatory cost ten synthetic units. Preserve the existing nonbinding environment limits of 100 cost units and 128 tool attempts. These limits are separate from the model-request and dollar caps.

| Scenario | Parent / child record slots | Revision | Recovery price | Exact pre-recovery hit rate, no / early inspection | Cheapest success-one choice | Expected extra units |
|---|---|---|---|---|---|---|
| `cheap_recovery` | 2 / 2 | No | 1 | 1/3 / 1 | No inspection, recover misses | 2/3 |
| `costly_recovery` | 2 / 2 | No | 4 | 1/3 / 1 | Inspect | 1 |
| `revision_cheap_recovery` | 2 / 2 | Yes | 4 | 4/5 / 1 | No inspection, recover misses | 4/5 |
| `revision_costly_recovery` | 2 / 2 | Yes | 8 | 4/5 / 1 | Inspect | 1 |
| `ample_parent` | 6 / 2 | No | 4 | 1 / 1 | No inspection | 0 |
| `small_child` | 2 / 1 | No | 4 | 3/10 / 1/2 | No inspection, recover misses | 14/5 |

These are exact population expectations in the [restricted reference](../experiments/dependency_memory/RECOVERY_FRONTIER.md), not expected LLM performance or dollar savings. With revisions, `process_build` refreshes the lexicographically first candidate. This public schedule must be stated in every arm; do not quietly replace it with uniform random refresh. In the small-child cell, inspection improves retention but makes exact success-one completion more expensive: three extra units instead of 14/5.

The offline plan must reproduce the fractions, endpoint costs, and decision labels from the existing implementation and check endpoint attainment over all 30 candidate/target routes. The full-route calculation is the calibration population. A four-route held-out debugging sample must not be presented as that exact population.

## Two stages and three inspection arms

**Stage A: inspection decision calibration.** Issue two separate stateless model requests for each of the six cells: 12 requests total. Describe the uniform routing distribution, capacities, public revision rule, prices, guaranteed optimal scripted record selection, and reliable recovery. Give no realized candidate set, target, fixture seed, exact reference answer, or precomputed hit probabilities. Ask for one Boolean inspection decision. The scripted evaluator then applies that decision's exact retention/recovery policy across all 30 routes, reporting exact expected synthetic cost and success. The two requests are repeated measurements of one model on a configuration, not independent task samples or a guarantee of independent model randomness.

**Stage B: inspection and retention.** Run three arms on every paired fixture:

| Arm | Inspection policy | Boundary retention |
|---|---|---|
| `never_inspect` | Skip early inspection | Same model, prompt, settings, and output schema as other arms |
| `always_inspect` | Inspect before the first boundary | Same model retention |
| `model_selective` | One stateless model decision before the first boundary | Same model retention |

All arms use the same scripted mandatory workflow, exact submission code, and `if_missing` recovery controller. Every arm gets one reliable late read of the required latest receipt when its retained state lacks that receipt, at the same cell-specific price. The controller neither exposes other archive records nor gives the manager a hidden recovery hint. Automated submission isolates information preservation from token copying; success here cannot establish model submission competence.

The selective decision sees the same initial public configuration and observation window that a manager would have before inspection. It cannot inspect a manifest, then decide retroactively not to pay. Mandatory later disclosure occurs in all arms. Evidence differs only through the inspection treatment and prior selected records. Different full episodes on the same immutable fixture compare inspection policies; restoring both environment and context is required for any additional comparison that starts from a checkpoint.

Two retention requests are made per B episode, one at each boundary. The model returns only a list of keys selecting visible current records, within the declared slot capacity. A host-side validator maps those keys to the exact supplied current receipt records, serializes them canonically, and deletes the old observation window. Do not repair a wrong key using evaluator truth. Duplicate keys, invented keys, over-capacity output, or malformed output terminate as policy failures. No corrective model call is included in v0.1.

The representation is still atomic record selection. No free-form rationale, auxiliary label, previous response, tool transcript, or candidate-list field may persist across a boundary. Record ordering is canonical and extra fields are rejected. Record selection can still carry information through the selected keys, as in the original reference. Report record slots, serialization bytes, prompt tokens, and model reasoning/output tokens separately.

## Explicit-label calibration and inferred dependencies

Each B fixture has two render modes. In `explicit_labels`, the manifest directly states its candidate keys. This is a representation/action calibration condition. In `inferred_dependencies`, the manifest contains task evidence whose dependencies determine those same two keys. No sound relevance/retirement label is added by the evaluator. Retention accuracy in the first condition does not establish inference in the second.

Public task metadata may describe all six jobs and the dependency relationships needed to interpret a clue. It must be generated independently of the chosen candidate pair and target, be equally available in every arm, and be listed as persistent public side information. Only the manifest identifies the applicable dependency request, and it appears early only after paid inspection. Receipt values, the selected manifest, and past observations cannot be hidden in public metadata or a re-presented task instruction. The final target is uniform within the two inferred candidates and is still revealed only after the second boundary.

Reserve these renderer families; their text and executable validation are **not yet implemented**:

| Split | Family ID | Required dependency structure |
|---|---|---|
| Development | `direct_artifact_tags` | Match two requested artifact properties to job records |
| Held out | `alias_chain` | Resolve task aliases through an intermediate naming relation |
| Held out | `package_prerequisites` | Trace a requested package's prerequisites to two source artifacts |
| Held out | `validation_scope` | Identify the two artifacts within a stated verification obligation |
| Held out | `deployment_handoff` | Resolve which artifact evidence a later handoff requires |

These are controlled synthetic templates, not natural workload observations. Author templates offline without model calls. Every family must support all 30 candidate/target routes without changing the underlying distribution. Validate that its evidence unambiguously determines exactly the intended pair, including both directions of the key mapping; neither irrelevant metadata nor wording may encode the target or opaque receipt. Keep stable `job-*` keys for the existing revision rule. Surface artifact names and relation wording may vary independently. Ambiguous clues, unreliable recovery, and multiple obligations are later extensions, not silently mixed into this pilot.

Freeze the four held-out families, renderer code, instructions, schemas, and hashes before any held-out model response is viewed. Development uses only its designated family. Labels versus inference is a paired change in evidence format, not evidence that the model has generalized to naturally occurring tasks. If a held-out family must be changed after evaluation, preserve its original result and call the replacement a new version; it cannot remain an untouched test set.

## Counts, seeds, and stopping

| Component | Construction | Model episodes / decisions | Maximum requests |
|---|---|---|---|
| A calibration | 6 cells x 2 requests | 12 inspection decisions | 12 |
| B development | 6 cells x 2 render modes x 1 development fixture x 3 arms | 36 episodes | 84 |
| B held out | 6 cells x 2 render modes x 4 held-out family fixtures x 3 arms | 144 episodes | 336 |
| Total | A plus B | 12 decisions and 180 episodes | **432** |

Each B episode uses two retention requests; only the selective arm adds a decision request. These are ceilings, not a commitment to purchase 432 calls. No automatic API retry, corrective reprompt, prompt search, or uncounted manager call is allowed in this version. A provider refusal, malformed response, or request failure remains recorded; any later rerun needs a versioned schedule and budget amendment. Do not claim reproducibility from a seed when the chosen API does not support it.

Use the following deterministic evaluator seeds, never supplied to model inputs:

| Seed role | Value |
|---|---|
| Development route sampling | 2026091901 |
| Held-out route sampling | 2026091902 |
| Payload root | 2026091903 |
| Template rendering | 2026091904 |
| Request ordering | 2026091905 |

Sample one development route from the 30 canonical routes. Sample four distinct held-out routes from the other 29 and assign one to each reserved held-out family. Reuse the assigned route across the six cells, both render modes, and three arms; pair revision on/off on the same underlying route and initial receipts. Domain-separate payload generation by split, family, and route so task pairs share their payloads while distinct fixtures do not. Store the realized route indices and fixture hashes. Deterministically shuffle the execution order to avoid fixed arm order. The model sampling seed and whether it is supported remain launch fields.

Four held-out family/route pairs are too few for a reliable generalization estimate. The repeated cells and arms are correlated paired measurements. Report denominators directly and do not treat 144 episodes, 432 calls, or the scripted route enumerations as independent samples. No significance threshold, powered superiority claim, or post hoc sample extension is justified by this design.

## Information isolation and provider contract

The existing Python interface is for trusted functions. A model launch requires an adapter with an explicit boundary:

1. Keep fixtures, archives, seeds, verifier truth, checkpoints, and complete logs in an evaluator process inaccessible to model tools. The model receives no shell, file, network, arbitrary retrieval, or evaluator-read tool.
2. Construct each request by an allowlist serializer from public configuration, approved persistent metadata, retained records, and observations since the last boundary. Do not forward the evaluator's object representation or whole trace. Record exactly the request bytes sent for later audit.
3. Use a fresh declared request state for every manager decision. Do not send a provider conversation/session identifier, previous-response link, opaque reasoning item, hidden compaction artifact, or earlier output unless the launch contract explicitly accounts for that additional channel. Inspect the actual outbound payload, not merely the visible prompt.
4. Document current provider/API behavior from official documentation or pinned client code before selecting the adapter. Record provider retention/session settings and any uncertain server-side behavior. This controls supplied state; it is not proof about inaccessible provider internals.
5. Test restoration of environment and visible context together; test that changing evaluator-only target/payload information cannot affect an earlier serialized public view when public inputs are held fixed. Test that a receipt removed at a boundary never appears in a later request unless the declared revision or recovery tool restores it.

Opaque state preserved inside a request may be necessary for the selected model. Its token limits and billing belong in the contract. Cross-request state that carries discarded receipts would invalidate this controlled irreversible-memory interpretation. A supported native-compaction comparison must preserve its supported state and be evaluated separately as a whole intervention.

## Launch gate and full accounting

The offline plan is reviewable now; the experiment is not frozen for model execution until every launch field has a recorded value and its supporting checks pass:

- Provider, API endpoint/version, immutable model revision or documented alias limitation, SDK/client commit, official-documentation review date, thinking settings, supported sampling settings, and cross-request state contract.
- Prompt files, request/output schemas, renderer versions, complete hashed fixture definitions, seed schedule, scheduled arm order, and analysis-code revision.
- Per-request input and reasoning/output caps, timeouts, the 432-request ceiling, total authorized dollar ceiling, and provider price currency/date with mutually exclusive billing buckets. These are unresolved, not zero-cost placeholders.
- A conservative maximum spend calculation including every planned request and billable input/output category. The runner must reserve the maximum remaining charge for a request before dispatch, stop before crossing the dollar cap, and record incomplete pairs if budget or availability stops a run. If the provider cannot support a defensible maximum-charge bound, the spending gate is unresolved.
- Offline serializer/isolation, state-restoration, schema, exact-reference, and renderer validation. Complete development-only full-memory and answer-visible controls that establish the verifier and scripted adapter can solve known instances; the latter intentionally reveals the final target early and is never a treatment result. A paid answer-visible diagnostic, if desired, requires an explicit amended schedule and cap before execution, not extra calls hidden inside 432.

Record all model calls, including unsuccessful ones, with provider request IDs, usage metadata, charged dollars where available, billing uncertainty, wall latency, tool attempts, synthetic tool cost, recovery, bytes, and peak/persistent memory. Distinguish cache reads, cache writes, uncached input, and output/reasoning without double-counting overlapping provider usage fields. Maintain a reconciliation ledger when invoices or usage records arrive late. Account for local archive storage/maintenance and evaluator runtime separately; do not label a synthetic recovery charge as an observed API or storage cost.

Environment budget failures, provider spending stops, transport failures, and incomplete pairs are different outcomes. Publish coverage and incurred cost for each. Never drop failed runs from expenditure or silently resample until success. A new model revision, changed prompt, additional request, or changed cap requires a new manifest version before it is used.

## Prespecified analysis and failure taxonomy

For A, report each Boolean choice, expected synthetic completion cost under the guaranteed scripted controller, excess cost relative to the exact success-one reference, and schema/API failures. Cost-optimal inspection labels are meaningful here because retention and recovery performance are fixed by construction.

For B, the primary display is terminal success **together with** full synthetic and actual model cost for each cell, render mode, and arm. Report paired selective-minus-never and selective-minus-always differences on matched fixtures, keeping the revision and capacity cells separate. Retain all attempted episodes; separately identify infrastructure failures and incomplete pairs, reporting completion coverage so a lower cost from early failure cannot look like a better success-one policy. No success-to-dollar exchange rate or composite score is fitted after seeing results. Population-reference gaps are diagnostics, not an LLM optimum or a formal regret bound for a different information class.

Also report required-receipt availability immediately before recovery, archive-read rate, inspection rate, retained keys/revisions at each boundary, inferred-candidate errors where they can be independently reconstructed, schema failures, bytes/tokens, and latency. Comparisons of label and inferred modes diagnose inference burden. Do not pool modes to obscure that burden or use evaluator candidate labels to repair a model output. A supplementary scripted exact policy can be evaluated on the same sampled fixtures without model calls; that helps distinguish sample composition from model error.

Preserve multiple failure flags and the first causal event when supported by the trace:

| Code | Interpretation |
|---|---|
| `inspection_reference_disagreement` | Chosen inspection differs from optimal-retention reference; diagnostic only in B |
| `dependency_inference` | Available task evidence supports a different candidate set than the manager's retained choices demonstrably imply; otherwise mark cause unresolved |
| `parent_retention` / `child_retention` | Required evidence is lost at the indicated boundary, accounting for later revisions |
| `stale_revision` | An outdated receipt is used after an observed update |
| `schema_or_capacity` | Invalid selection, invented/duplicate key, wrong type, or excess retained records |
| `recovery_controller` | Declared matched recovery is unavailable or behaves incorrectly; adapter/environment defect |
| `submission_or_verifier` | Exact scripted submission or grading violates the validated fixture |
| `provider_or_transport` | Provider refusal/error, unavailable usage, timeout, or transport failure |
| `budget_or_schedule_stop` | Request/dollar cap or declared schedule stop prevents continuation |
| `information_leakage` | Hidden evaluator, session, archive, transcript, or other undeclared state is accessible |

Do not infer a reasoning failure from a retained-key list alone. Distinguish an unsupported causal story from an observed wrong selection. An information-leakage finding invalidates the affected information-condition interpretation; keep its raw record and cost, quarantine the affected result, repair offline, and version any rerun.

## Staging and artifacts

1. **Now, offline:** generate the schedule and exact calibration references; validate sample separation, pair keys, counts, and unresolved launch gates. Run the repository's existing tests, validator, and paper build. This is an implemented-plan check, not model evidence.
2. **Next, offline:** implement and validate the five renderer families, minimal stateless adapter interface with a scripted fake client, allowlist serializer, full-memory/answer-visible controls, cost reservation, and analysis/report writer. No credentials or paid endpoint are needed for these checks.
3. **Only after the gate is complete:** run A and B development within the declared allocation; inspect feasibility and errors. Freeze any development-driven amendments before touching held-out responses. A failure may justify stopping the pilot rather than consuming the remaining ceiling.
4. **Held-out run:** execute the frozen paired schedule once, preserve failures, then run the prespecified analysis. Update the [claim register](../paper/claims.csv), [living findings draft](../paper/findings-draft.md), [manuscript](../paper/manuscript.md), and [status](STATUS.md) only with the resulting evidence and its limits.

Required run artifacts are the versioned manifest, source/prompt/template hashes, request schedule, immutable fixture definitions, redacted request/response records, raw usage ledger, environment outcomes, analysis output, and a provenance/readme file. Secrets and uncontrolled raw session logs do not belong in Git. Evaluator-private artifacts must remain absent from policy-visible paths even when retained for audit.

**Results: unperformed.** The expected-cost fractions above belong to the completed deterministic reference. No model selection accuracy, generalization, native-harness improvement, dollar savings, or paid trial is reported here.
