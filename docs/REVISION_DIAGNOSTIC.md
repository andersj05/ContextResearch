# Revision-aware parent retention: development diagnostic v1

September 19, 2026. **Prepared; no follow-up model calls yet.** The initial 96-request Luna tranche is complete and remains immutable. This diagnostic is a separate, post-pilot development question. Its [plan](../experiments/dependency_memory/results/revision_diagnostic_plan.json) and [fake controls](../experiments/dependency_memory/results/revision_diagnostic_audit.json) are executable offline artifacts, not model outcomes.

## Question and motivating evidence

The [offline analysis of saved selections](../experiments/dependency_memory/results/revision_analysis_report.md) found exactly three strict parent-selection deficits among 36 observed first-boundary choices. All occur before the manifest is known in revision conditions. The other 33 choices match their same-public-view ideal-child reference; all 36 observed later selections are conditionally optimal. These are post-hoc grades of the original responses, not new trials or proof of the model's reasoning process.

The narrower question is whether a cold first selector responds to the direction of the public refresh rule. A static preference for low keys can be harmless without revision and strictly worse when the smallest candidate is refreshed later. Reversing that rule reverses the preferred parent set.

## Fixed task and allocation

Six jobs have initial revision-one receipts. The model selects at most two records before seeing a candidate pair. The pair is uniform over the 15 unordered pairs; the final target is uniform within it. A later selector is explicitly guaranteed optimal with two record slots. No actual candidate pair or target is sampled or supplied: each answer is evaluated offline over all 30 routes.

The maximum proposed new allocation is **24 requests**:

| Factor | Values |
|---|---|
| Public refresh rule | Lexicographically first candidate, lexicographically last candidate, no refresh |
| Visible-record order | Canonical and reverse; `(2,5,1,4,0,3)` and its reverse |
| Receipt payload fixture | Two fixed sets of opaque tokens, paired across rule/order cells |

Each key's mean displayed position across the four orders is 3.5, though this is not complete position balancing. The canonical job metadata and response-schema enumeration remain unchanged and are declared additional ordering channels. Rule wording changes only the operational refresh description. No ranking advice, oracle choice, per-key refresh probabilities, or evaluator condition labels appear in the request. This simplified task and optimal-child guarantee differ from the earlier full workflow; any result is not a clean causal comparison with the first tranche.

The evaluator-only schedule seed is `2026091907`; payload seed is `2026091908`. The 24 cells are shuffled once and frozen. The model has no claimed sampling seed. No answer-dependent rerendering, replacement cases, extra explanations, corrective prompts, or intermediate feedback are allowed. The schema permits underfilled choices so those can be measured; malformed choices remain failures rather than being scored as empty memory.

## Exact outcomes and controls

For selected ranks S within 0 through 5, with the declared optimal child:

| Rule | Availability | Best two-record choice | Best availability |
|---|---|---|---|
| Refresh first | `1/2 + sum(S)/30` | ranks 4 and 5 | 4/5 |
| Refresh last | `1/2 + sum(5-r for r in S)/30` | ranks 0 and 1 | 4/5 |
| No refresh | `len(S)/6` | Every two-record choice ties | 1/3 |

The primary outcome is exact parent-availability regret relative to the rule-specific optimum. Also report selected keys, displayed positions, valid/failed/incomplete counts, and the paired difference in selected-rank sums between first-refresh and last-refresh cells. The ideal shift is 8; static key/order controls have shift zero. Raw availability between refresh and no-refresh conditions does not measure understanding: a refresh supplies free information. Thirty evaluated routes are not thirty model observations.

Five fake controls cover an optimal rule-sensitive selector, always-low keys, always-high keys, first-visible records, and invalid output. Tests compare the formula with full route enumeration, reverse-rank symmetry, the two-key identity `h_first(S) + h_last(S) = 4/3`, order/payload invariance, injection rejection, balanced scheduling, and retained failure denominators.

## Transport and proposed budget

The strict [revision request contract](../experiments/dependency_memory/revision_interface.py) is separate from the original pilot interface. A two-version dispatcher accepts only those reviewed schemas. The original 96 request bytes remain unchanged. The [separate wire audit](../experiments/dependency_memory/results/revision_transport_audit.json) exercises the new request through four unauthenticated loopback cases with the installed client; each makes exactly one local POST and zero model calls.

Reuse the [reviewed Luna transport](LUNA_DEVELOPMENT_RUN.md): managed ChatGPT subscription, mutable `gpt-5.6-luna`, low effort, default tier, fresh process/thread, fixed declared public background, zero configured retries, no external tools or prior state, and the required one-generation guard. Effective configuration, client/global-instruction hashes, model identity, body size, and quota checks still apply. No API-key fallback, credit purchase, reset redemption, or held-out call is permitted. Optional unreported cache-write usage is now stored as unknown, not a measured zero.

The proposed new cap is **12 conservative credit equivalents**, reserving 10.4025 before each serial generation under the existing conservative accounting assumptions. This cap plus the first tranche's 2.5395 equivalents is below 20 equivalents. It is not a verified invoice or account-debit cap. Quota at 80% used, missing usage, uncertain transport, or any tool attempt stops the tranche; the outstanding reservation is retained when usage is uncertain. No implicit renewal of the completed 96-request allocation is authorized by unused credit headroom. A new allocation must be recorded explicitly before `--live`.

The frozen plan fingerprints every experiment Python source file, the revision wire audit, and this contract. Live preparation rejects source or contract changes before starting any client process. The launch manifest records the immutable plan content, request and source hashes, model catalog, transport audit, accounting, and new allocation. Output directories cannot be resumed or overwritten. Raw reasoning/session transcripts and credentials are never saved. Record all 24 scheduled outcomes even if the run stops early.

## Commands

Python 3.11+ and the standard library suffice. These commands are offline:

```powershell
python experiments/dependency_memory/revision_analysis.py
python experiments/dependency_memory/run_revision_diagnostic.py --plan --output experiments/dependency_memory/results/revision_diagnostic_plan.json
python experiments/dependency_memory/run_revision_diagnostic.py --offline-audit --output experiments/dependency_memory/results/revision_diagnostic_audit.json
python experiments/dependency_memory/run_revision_diagnostic.py --fake-mode optimal --output tmp/revision-fake-run
```

After a new allocation is explicitly authorized, the separate live entry point requires the reviewed executable and an allocation note:

```powershell
python experiments/dependency_memory/run_revision_diagnostic.py --live --executable $lunaExecutable --max-requests 24 --authorization $newAllocationNote --output experiments/dependency_memory/results/revision_luna_2026-09-19
```

The requested diagnostic can distinguish observed rule sensitivity from the prespecified static controls. It does not establish internal reasoning, natural-task generalization, a native-harness advantage, or novelty. The held-out families and external mathematical review remain separate unfinished work.
