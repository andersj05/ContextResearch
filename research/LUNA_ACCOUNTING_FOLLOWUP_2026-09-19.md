# Luna request and subscription accounting follow-up

September 19, 2026. This is an implementation review, not a model result. It refines the unresolved accounting discussion in the [initial transport review](CODEX_SUBSCRIPTION_TRANSPORT_2026-09-19.md). The checks described here sent no OpenAI generation request and read no credential file.

## Supported retry controls and local check

The current configuration reference reserves built-in provider IDs but permits a new provider with explicit HTTP and stream retry settings. The authentication guide says `requires_openai_auth = true` supports existing ChatGPT authentication for a custom provider. These are official configuration mechanisms; no extracted bearer token or unofficial authentication client is needed. [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), [authentication](https://learn.chatgpt.com/docs/auth).

The candidate subscription settings are:

```toml
model = "gpt-5.6-luna"
model_provider = "luna_research"
forced_login_method = "chatgpt"

[model_providers.luna_research]
name = "Luna Research"
wire_api = "responses"
requires_openai_auth = true
request_max_retries = 0
stream_max_retries = 0
supports_websockets = false
```

The current binary accepted this selected provider through `config/read`, including the zero retry values and omitted `base_url`. A separate pinned-source review inspected `ModelProviderInfo::to_api_provider` in `codex-rs/model-provider-info/src/lib.rs` at upstream commit `da18000cae9884ab45f83b2d07fbd5a220a1de39`, Git blob `9c27b15cc4800fbc8138423806e5e794122a211e`. When `base_url` is absent and the authentication mode is ChatGPT, that implementation selects `CHATGPT_CODEX_BASE_URL`, `https://chatgpt.com/backend-api/codex`, without requiring the provider name to be `openai`. This supplies source evidence for the custom alias retaining the subscription route. [Pinned OpenAI source](https://github.com/openai/codex/blob/da18000cae9884ab45f83b2d07fbd5a220a1de39/codex-rs/model-provider-info/src/lib.rs).

The source snapshot is from September 16; it is not a reproducible-build certification of the September 19 installed executable. Keep that distinction alongside current-binary configuration, authentication, and mock-wire observations. No direct HTTP client, extracted credential, alternative API key, or substitute model is used by this configuration.

A loopback-only fake-provider probe exercised the installed `codex-cli 0.155.0-alpha.9.2`. It used the same retry settings with `requires_openai_auth = false`, a local HTTP URL, no `env_key`, and no WebSocket transport. The two failures were deliberately induced before any real generation:

| Local fake response | Observed POSTs to `/responses` | Authorization header present | CLI outcome |
|---|---:|---|---|
| HTTP 503 error | 1 | No | Failed turn, exit 1 |
| SSE `response.created` followed by premature EOF | 1 | No | Failed turn, exit 1 |

These observations show that the selected HTTP/SSE retry settings take effect in the reviewed binary. They do not exercise managed OAuth refresh or certify inaccessible server behavior. The successful-response isolation probe is separate. The disposable probe was `build/luna_retry_probe.py`; it printed only method-path counts, header-presence booleans, exit codes, and event types, never request bodies, header values, or raw CLI transcripts.

The runner must still perform zero application retries, stop the batch after uncertain transport/authentication accounting, and retain the attempted call's reservation. Count generation submissions separately from account queries and rejected authorization traffic. If the contract promises at most 96 *all provider POST attempts*, managed-auth recovery also needs a verified bound or an explicit conservative reservation. A zero retry setting alone does not count hidden server work.

## Credit rates and reservation proposal

The current Codex pricing page supplies Luna rates of 5 credits per million input tokens, 0.5 per million cached-input tokens, and 30 per million output tokens. Available credits can fund continued usage after included limits. API dollars and subscription credits remain distinct. [Codex pricing](https://learn.chatgpt.com/docs/pricing).

The Luna model page lists a 1,050,000-token context window and 128,000-token maximum output. These published maxima are useful conservative planning bounds even without a smaller CLI output setting; they are not a verified per-call configuration override. [Luna model specification](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

A 20-credit accounting ceiling can reserve the maximum before each serial dispatch and release the unused part only after complete usage arrives. Under the listed basic rates and those model maxima, ignoring cache discounts gives a deliberately loose 9.09-credit single-response envelope. The implemented [credit-equivalent ledger](../experiments/dependency_memory/luna_budget.py) reserves **10.4025** per generation instead: all 1,050,000 possible input tokens at 6.25 credits per million, plus 128,000 output tokens at 30. The higher input rate supplies a 25% margin. This calculation is conditional on the reviewed model, standard tier, request count, and applicable pricing. Do not use a timeout, low reasoning effort, or response schema as a hard generation limit.

The API model page separately lists cache-write and long-context price multipliers; the subscription page does not state how those apply to credits. Keep that uncertainty visible. A verified input bound below 272,000 tokens removes the published long-context trigger; reserving input at 1.25 times the uncached rate also accommodates the published cache-write multiplier as a conservative planning assumption. Report a calculated credit equivalent separately from any observed account balance change.

The ledger requires a separate transport-enforced 32,768-byte request-body cap and rejects observed input at or above 272,000 tokens. It settles with all input at the conservative rate, gives no cache discount for budget purposes, and also reports a separate basic-rate estimate. Invalid usage retains the outstanding reservation; explicit failure retains it permanently and stops the batch. Thirteen [offline tests](../experiments/dependency_memory/test_luna_budget.py) check independent arithmetic, exact budget boundaries, malformed counters, request limits, single-use tickets, and failure reservations. These tests validate accounting logic, not provider billing.

Usage output includes reasoning within generated output accounting; do not add reasoning tokens a second time. The official API reasoning guide describes generated-token limits as including reasoning, visible output, and non-visible formatting. Whether the subscription telemetry exposes every relevant bucket must be checked independently. [Reasoning and output accounting](https://developers.openai.com/api/docs/guides/reasoning).

## Guardrails supported by the app-server interface

The official app-server exposes `account/rateLimits/read`, rate-limit notifications, and `thread/tokenUsage/updated`. Prefer the multi-bucket limits map, retain window durations and reset times, and fail closed when required accounting disappears. Read limits before each dispatch, record usage after completion, and stop when a prespecified margin is reached. Shared-account quota movement cannot be attributed wholly to this experiment. No credit purchase, earned-reset redemption, account-setting change, or API-billing fallback belongs in the runner. [App-server accounting interface](https://learn.chatgpt.com/docs/app-server).

The [v0.4 development launch contract](../docs/LUNA_DEVELOPMENT_RUN.md), prepared before generation, freezes these choices alongside the historical [development protocol](../docs/DEVELOPMENT_PILOT.md). The first tranche's request ceiling remains 96; a small live transport diagnostic must consume its declared allocation rather than becoming uncounted setup work. The 432-request full plan is not a launch authorization, and held-out renderers and their freeze are deferred to a separate amendment.

## Implemented development accounting condition

The [app-server adapter](../experiments/dependency_memory/luna_appserver.py) now checks managed ChatGPT authentication and effective provider settings before every generation. It rejects a reached rate/spending limit, missing allowance accounting, or an observed allowance window at 80% used or above. It checks the same guard after completion. API-key environment fallbacks are removed from the child environment, while credentials remain owned by the official CLI. There is no purchasing, reset-redemption, or account-setting operation.

The selected condition uses the mutable Luna alias, low reasoning effort, default service tier, no asserted model sampling seed, and one fresh process and ephemeral thread per decision. The adapter matches the reviewed executable, isolation-profile, and global-instruction hashes. It applies the conditional 32,768-byte full client-body bound and serial 20-credit-equivalent ledger described above. These checks do not convert a planning estimate into an observed subscription charge or certify provider-added context.

The [follow-up isolation audit](LUNA_ISOLATION_FOLLOWUP_2026-09-19.md) found that zero network retries did not alone prevent an agent continuation. Its weighted rollout-budget guard now stops after the first complete generated response. The valid synthetic response arrives before a terminal `sessionBudgetExceeded`; the adapter accepts only one valid final object with complete usage and this exact intended stop, while preserving the actual harness termination. Ordinary completion without this expected stop is rejected too. Tool calls, other errors, missing usage, and malformed answers remain failures. This is a one-generation continuation control, not a smaller hard output-token cap.

The measured request quantity is this client's generation submissions, with zero configured HTTP/stream retries and zero application retries. Account-query and rejected-authentication traffic are not generations. Hidden provider work and all underlying production HTTP attempts remain unobserved, so the run must not claim an exact total of every provider-internal operation. On a transport failure, the runner records the attempt, keeps its full reservation, and stops without a repair call. Full usage is settled before strict host response validation; a schema-invalid response still incurs its measured tokens and cost.

Report conservative credit equivalents and the basic-rate estimate separately from actual credit-balance debits and dollar charges. The latter remain unknown unless observed, and account-wide movement cannot be attributed entirely to the pilot. Cached input is included in input; reasoning output is included in output. The record-slot limits and synthetic recovery units do not measure any of these billing quantities. These are prelaunch implementation choices, not results from Luna generations.
