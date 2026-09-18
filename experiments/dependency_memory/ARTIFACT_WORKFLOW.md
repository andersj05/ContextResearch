# Deterministic artifact/manifest environment

September 18, 2026. Implemented in [artifact_workflow.py](artifact_workflow.py), with [invariant and counterfactual tests](test_artifact_workflow.py). These are scripted diagnostic workflows, not LLM trials or evidence of superiority over a deployed harness.

## Task

Collect once-only receipts for several build jobs, preserve enough information through two forced memory boundaries, process a possible revision, complete intervening work, and submit the exact latest receipt for a job revealed only at the end. Submission creates the terminal package and is allowed once. There is no retry oracle or intermediate package storage.

Before the first boundary, an optional manifest inspection reveals the candidate job set. It never reveals a receipt, the final selected job, or an answer. The same manifest appears automatically after the first boundary. This makes inspection change the timing of available evidence, not the eventual task.

## Transitions and costs

Every action costs one synthetic action unit except `inspect_manifest`, whose cost is configurable. A blocked admitted action is charged too. An action rejected because it would exceed the total budget is not executed or charged. Calls count attempts, including rejected ones. These units are neither dollars, model tokens, nor measured latency.

| Phase | Action | Observation / state change |
|---|---|---|
| Collect | `collect_receipts` | All initial receipts appear once. |
| Before first boundary | `inspect_manifest` (optional, one attempt) | Candidate keys, or a charged unavailable response. |
| Before first boundary | `seal_receipts` | First forced compaction; runner discards the prior observation window. |
| Manifest | `read_manifest` | Same candidate set as an early inspection would give. |
| Build | `process_build` | Optionally replace the first candidate's receipt with revision two. The new receipt appears once. |
| Before second boundary | `seal_build` | Second forced compaction; observation window discarded again. |
| Work | `work` repeated for the configured delay | Advances completed-work state; no receipt information. |
| Requirement | `get_requirement` | Required key and revision, without its token. |
| Submit | `submit` | Creates the package and ends the episode with success or a precise failure code. |

Other phase/action combinations are blocked and cannot reread a receipt, skip work, or submit early. The terminal verifier compares the submitted key, revision, and exact token with evaluator truth. A stale receipt fails even when its job is correct. A revision may legitimately replenish information lost at the first boundary; results must retain that condition explicitly.

## Information contract

Each decision is a fresh call to a stateless policy function. It receives exactly:

- Public configuration, phase, and whether the one permitted probe was attempted.
- Retained receipt records from the last compaction.
- Observations since that compaction, including any currently visible receipts or manifest.

At a boundary, the compactor receives only those records and observations. Its output must be a subset of visible, current records, with at most the configured record count and no duplicate keys. The runner serializes and reconstructs that output and clears the observation window. It does not pass transcripts, fixtures, seeds, truth, prior policy calls, or saved environment snapshots to the next policy call.

Memory is capped **at boundaries**, not during the temporary observation window. Limits are **record slots**, and serialized bytes (including key/revision/format overhead) are reported separately. Policies select exact records; arbitrary coding into labels or token strings is not permitted. These experiments do not instantiate the bit-optimal encoders of the theorem.

Configuration and workflow phase are persistent public control information. The candidate set must be observed by the current compactor; it is not an implicit persistent field in policy memory. The final query arrives after the second boundary. Evaluator traces and snapshots contain private values and are never supplied to policies. No archive, filesystem tool, provider state, or retrieval interface is available through this API.

This is a contract for trusted Python policies, not isolation against hostile Python introspection. A future LLM adapter must isolate evaluator files and session history before making an irreversible-memory claim. There is currently no model adapter, native-compaction baseline, learned retirement, or paid model call.

## Reference policies

All policies receive the same tool interface and initial information. Each can observe the published availability and price of inspection.

| Policy | Inspection | Retention |
|---|---|---|
| `recent_never` | Never | Most recently observed current records. |
| `structured_never` | Never | Filter by manifest when visible, otherwise retain recent records. |
| `structured_always` | Attempt once, even if unavailable | Same structured retention. |
| `structured_budgeted` | Inspect when candidate records fit but all jobs do not, inspection is available, and price <= 2 units | Same structured retention. |

Every baseline handles revisions. The budgeted rule is a specified heuristic, not a learned or optimal value-of-information policy. Its two-unit ceiling is a declared design choice, not a conversion from success to money. In expensive conditions it may trade success for fewer action units. Report both outcomes; do not silently combine them into a tuned score.

## Pairing and deterministic fixtures

`make_fixture(seed, config)` is evaluator-only. Route choices and 128-bit receipt strings use separate deterministic PRNG streams. Fixed-seed configurations are constructed diagnostics, not independent model trials or a proof of statistical independence of source bits. Tests also use explicit fixtures whose values and expected outcomes are independently stated.

`run_episode(..., stop_at_first_boundary=True)` captures the environment, retained memory, pending observation window, cost, and evaluator trace immediately before the first compaction. Resuming with `checkpoint=...` deep-copies all of that state and applies the selected compactor. Both branches therefore start with identical evidence and environment state. A different instance cannot be substituted at restore time.

This paired mode isolates retention with a common probe decision. Comparing early-probe policies requires complete separate episodes on the same fixture, because their information timing and action costs differ. Saved snapshots are evaluator artifacts, not a recovery channel.

## Checks and current limits

Tests cover a delayed missing-receipt witness; an ample-memory control; insufficient child capacity; zero capacity and delay; revisions; exact terminal grading; charged unavailable probes; cost termination; illegal actions; deterministic replay; receipt visibility after compaction; unchanged decisions under nonce replacement; and full environment/context restoration.

The environment deliberately makes information timing consequential. It does not estimate how often this situation occurs in ordinary work. No held-out LLM evaluation has been run. There is no automatically minimized failure search yet; paired explicit witnesses establish the initial debugging interface.

```powershell
python -m unittest discover -s experiments/dependency_memory -v
```
