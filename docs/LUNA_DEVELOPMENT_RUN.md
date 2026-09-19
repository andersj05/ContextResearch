# Luna development run: v0.4 launch contract

September 19, 2026. This is the contract prepared **before the first model generation**. It amends the [v0.2 pilot design](LLM_PILOT_SPEC.md) and [v0.3 offline implementation](DEVELOPMENT_PILOT.md) for the requested Codex subscription transport. It reports no Luna result. Run manifests, ledgers, and reports must establish what was actually attempted and completed.

## Scope and stopping rules

The allocation is Stage A's 12 inspection decisions plus Stage B's 36 development episodes, using only `direct_artifact_tags` and the already reserved development route, index 21. The maximum is **96 attempted manager requests**: 12 decisions, 72 retention requests, and 12 selective-arm decisions. Failed attempts count. There is no repair prompt, automatic application retry, paid setup generation, or model fallback outside this allocation.

The four held-out renderers and their reserved routes are excluded. They must be completed and frozen before any held-out response is viewed, under a separate launch manifest and budget amendment. Their historical 336-request reservation does not authorize this runner to expand its 96-request tranche to 432.

| Choice | Frozen development setting |
|---|---|
| Model | `gpt-5.6-luna`, a mutable alias; no immutable revision exposed |
| Transport | Official Codex stdio app-server, `codex-cli 0.155.0-alpha.9.2` |
| Authentication | Existing managed ChatGPT subscription, checked before each dispatch |
| Reasoning / tier | `low` / `default`; no model sampling seed is asserted |
| Concurrency and retries | Serial; zero application, configured HTTP, and configured stream retries |
| Request allocation | At most 96 manager attempts; no held-out requests |
| Credit-equivalent ceiling | 20; reserve 10.4025 before each generation and release only against validated complete usage |
| Additional API spending | US$0; no API-key fallback |
| Account guard | Before and after each decision, reject a reached allowance/spend limit or any observed allowance window at 80% used or above |
| Purchases and resets | No credit purchase, reset redemption, or account-setting change |
| Complete client-body bound | At most 32,768 bytes under the audited fixed client-context assumptions |
| Generation deadline | 120 seconds after turn startup; timeout stops further dispatch but is not a token or charge limit |

The generation-attempt count concerns model submissions by this client. Account queries and rejected authentication traffic are separate. Provider-internal work is not directly observed. A timeout or uncertain transport failure retains the full outstanding credit-equivalent reservation and stops the batch. Budget, quota, transport, and schema stops remain distinct in the ledger; unfinished pairs remain reported.

## Declared information available to the model

Every decision starts a fresh app-server process and ephemeral thread with an empty scratch directory, no environments, no runtime workspace roots, no prior turns, and no provider/model fallback. No prior response, opaque reasoning item, archived receipt, evaluator fixture, or hidden session history is supplied. The allowlisted public request contains only public configuration and static metadata, current retained records, and new observations allowed by the workflow.

The installed client also supplies fixed public background: controlled base/developer instructions, reviewed global GitHub authentication guidance, three harness wrapper declarations, and a fixed rollout-budget message. This explicitly amends the earlier proposal that only experiment JSON would reach the model. The global guidance contains no experiment data; its normalized-text SHA-256 is `263fbf5f86b6338244e956ebe986e34e3aecafb5c061fe95d140a677b8d60714`. The adapter verifies it before dispatch.

The three declared wrappers are `functions.exec`, `functions.wait`, and `functions.request_user_input`. The audited exec runtime is a fresh V8 isolate with no Node, filesystem, network, or nested/deferred tools. This is **not an empty tool registry**. Shell, MCP, skills, browser, app, plugin, and arbitrary retrieval tools are excluded; a model tool attempt is rejected as an invalid run. The [complete loopback wire audit](../experiments/dependency_memory/results/luna_transport_audit.json) checks input-embedded tool declarations and authoritative registry metadata, not merely top-level `tools`.

The audit uses a synthetic local provider without authentication, not the production provider. It demonstrates the reviewed client's serialization and continuation behavior. Production checks verify the account type, selected provider, effective configuration, fresh thread, and allowed instruction source. Neither check certifies inaccessible server internals. A changed binary, configuration, global instruction hash, or newly enabled information channel requires renewed review.

## One response, strict host validation

Zero HTTP retries alone did not prevent an agent continuation after a tool response. The amended client therefore uses the existing weighted rollout-budget guard: limit 32,768, prefill-token weight 1,000,000, sampling weight 1, and no reminder thresholds. A completed response with at least one input token exhausts this budget before another model submission. The fixed reminder is model-visible public background, not a research memory limit or a dollar amount.

The local successful-response probe produced one complete model message and complete usage, followed by terminal `failed` / `sessionBudgetExceeded`. The adapter may accept that decision only when there is exactly one final JSON object, valid complete usage, no tool activity, and this exact controlled terminal error. Ordinary `completed` without the expected guard stop is also rejected; the guard is required on every accepted generation. It records the actual harness termination separately from the accepted decision. Any other error, missing usage, ambiguous output, tool call, or incomplete response remains a failure. This does not report a failed native agent turn as a successful native-harness task.

Provider schema projection removes unsupported `uniqueItems`; the host still rejects duplicate or invented keys, excess capacity, wrong types, nonfinite/duplicate JSON fields, and extra response fields. It copies only the exact current visible records selected by valid keys and deletes the old observation window. No evaluator answer repairs a response. The generation guard is **not a hard output-token cap**; low reasoning effort, schemas, and timeouts also are not such caps.

## Routing and accounting assumptions

The configured provider alias `luna_research` uses `requires_openai_auth=true`, no `base_url`, no `env_key`, and no custom bearer token or header. The official CLI owns authentication. Pinned OpenAI source at `da18000cae9884ab45f83b2d07fbd5a220a1de39` routes a provider with absent `base_url` and ChatGPT authentication to the Codex subscription backend. That September 16 source is not a reproducible-build certification of the installed September 19 binary; retain the distinction. [Routing and retry review](../research/LUNA_ACCOUNTING_FOLLOWUP_2026-09-19.md).

The 20-credit ceiling is a **token-derived planning equivalent**, not an observed subscription invoice or proof of a hard account debit cap. It uses the reviewed Luna credit rates and published 1,050,000-input / 128,000-output maxima, with a conservative input rate of 6.25 rather than 5 credits per million and an output rate of 30. Thus each serial reservation is `(1,050,000 × 6.25 + 128,000 × 30) / 1,000,000 = 10.4025` credits. It uses no cache discount for budget purposes. Complete usage must report fewer than 272,000 input tokens and no more than 128,000 output tokens; unexpected usage stops the run. Reasoning is already included in output and is not charged again.

The input margin accommodates a published API cache-write multiplier as an explicit planning assumption; subscription cache-write pricing and inaccessible provider-added context remain uncertainties. The body bound, short-context check, fixed default tier, and model selection constrain this calculation. Record conservative equivalents, basic-rate estimates, reported token buckets, and any observed account movement separately. Account limits and balances are shared with other work, so changes are not wholly attributable to this pilot. The prior unresolved-gate descriptions remain dated history; they are not retroactively rewritten as evidence that live calls had already run.

## Execute the bounded tranche

Use Python 3.11 or newer for this subscription runner and its tests/configuration checks, which use the standard-library TOML parser. The earlier offline mathematical diagnostics retain their separate Python requirements. From the repository root, select the reviewed installed executable and a new empty output directory:

```powershell
python experiments/dependency_memory/run_luna_pilot.py --run --executable "C:/Users/jense/AppData/Local/OpenAI/Codex/bin/247581e40ee272fb/codex.exe" --output "tmp/luna-development-v0.4"
```

This command dispatches the bounded live tranche. Its first scheduled generation is also the connection diagnostic and counts toward the same 96-attempt allocation. The wrapper verifies advertised Luna availability, freezes source and contract hashes, and writes the manifest before the first generation. It never resumes, overwrites a nonempty output directory, or silently retries. Do not run this command again as a setup check after a completed or failed tranche; preserve the first run and version any newly authorized rerun.

## Analysis and artifacts

Save the manifest before dispatch, including source/client/profile/instruction hashes, fixture definitions, evaluator seeds, schedule, and this accounting contract. Keep canonical public requests, validated responses, redacted provider metadata, errors, usage/reservation records, wall latency, and all incomplete outcomes. Do not save credentials or uncontrolled raw session transcripts.

The [report helper](../experiments/dependency_memory/pilot_report.py) reports each Stage-A choice and exact population-cost regret, then Stage-B pre-recovery availability, recovery attempts, completion coverage, synthetic cost, and fixed population policies on the same exact fixture. Partial episode costs cannot be presented as a completed-policy improvement. Reliable recovery allows successful completion even after forgetting everything, so terminal success alone is not evidence of good retention.

These are repeated measurements on one development route and one synthetic template. They are not independent trials, held-out generalization, or a native-compaction comparison. The tiny reserved held-out sample remains a debugging exercise even after a separately approved run.

## Running this version

The subscription adapter and its TOML configuration checks require Python 3.11 or newer. Set `$lunaExecutable` to the reviewed official `codex.exe` path, then use a new empty output directory:

```powershell
python experiments/dependency_memory/run_luna_pilot.py --run --executable $lunaExecutable --output experiments/dependency_memory/results/luna_development_2026-09-19
```

This is a live command, not a repository check. It never resumes an existing directory. A failed tranche must remain preserved; a further launch needs an explicit accounting amendment within the user's allocation, not an uncounted retry.
