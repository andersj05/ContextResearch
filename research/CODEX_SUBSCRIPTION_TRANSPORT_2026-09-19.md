# Codex subscription transport review

Historical preflight finding. The subsequent [isolation follow-up](LUNA_ISOLATION_FOLLOWUP_2026-09-19.md), [accounting follow-up](LUNA_ACCOUNTING_FOLLOWUP_2026-09-19.md), and [v0.4 launch contract](../docs/LUNA_DEVELOPMENT_RUN.md) document the amended controlled transport. The original review below remains unchanged as evidence of what was unresolved at that stage.

Date: September 19, 2026. Status: account connection verified; **controlled model execution remains blocked**. No model request was made by this review. The implementation is [codex_subscription.py](../experiments/dependency_memory/codex_subscription.py); its local checks are [test_codex_subscription.py](../experiments/dependency_memory/test_codex_subscription.py).

## What works

The official CLI supports ChatGPT sign-in for subscription access. API-key sign-in has separate usage-based billing. We verified the existing local installation outside the workspace sandbox: `codex login status` returned `Logged in using ChatGPT`. No sign-in change, credential extraction, token copying, or API-key setup was necessary. A previous sandboxed home-directory error was an environment failure, not evidence of invalid credentials. [Official authentication documentation](https://learn.chatgpt.com/docs/auth).

The requested model name is `gpt-5.6-luna`; the current model guide explicitly lists that CLI selection. Account availability still depends on rollout, sign-in method, and client. This review did not make a generation request to test Luna availability. The API model page lists the Luna alias but no immutable dated snapshot, so any eventual manifest must acknowledge that reproducibility limitation. [Codex models](https://learn.chatgpt.com/docs/models), [Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

Installed client: `codex-cli 0.155.0-alpha.9.2`, in the desktop bundle directory `247581e40ee272fb`. Executable SHA-256: `bc45017e8239dc150258f69309ced9df6bbcdf5b8e4f346decf780ac0999e226`. The diagnostic command reports this fingerprint without inspecting credential files. A different binary requires renewed review.

## What we inspected without generating a response

We inspected local help for `exec`, `debug prompt-input`, and the app-server schema generator. The installed CLI exposes fresh non-interactive execution, ephemeral sessions, ignored user config/rules, JSONL events, and an output schema. These are useful building blocks. `--ephemeral` suppresses persisted rollout files; it does not establish a clean model input by itself. The official non-interactive guide documents CLI-turn events and aggregate token usage. [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).

A local `debug prompt-input` probe used a newly created empty working directory and disabled shell, unified exec, apps, plugins, remote plugins, hooks, memories, multi-agent, goals, artifact, browser, computer use, and local-image access. Web search was disabled; project-document byte limit was zero; memory use/generation was off; ChatGPT authentication was selected. The probe only rendered input locally.

**Observed:** the rendered input still contained the user's global AGENTS instructions and six host-skill catalog entries, plus permissions and environment context. This establishes that these toggles and an empty directory alone do not produce the desired public-input-only condition. It does not establish that those instructions contain receipt answers, or that a tool actually accessed a private fixture.

**Scope limit:** `debug prompt-input` rejected `--strict-config` and does not provide the exec command's `--ignore-user-config` switch. Its output is an input-message list, not a complete outbound request containing the effective tool registry. Therefore this probe is not an exact inspection of the proposed exec transport. We retained these observations rather than committing an uncontrolled machine-context transcript. Generated app-server schemas remain disposable build output.

## The remaining launch gates

1. **Information isolation:** verify the complete effective instructions, tools, skill catalog, MCP/apps, and supplied session state for the actual generation path. An empty directory and read-only sandbox do not deny reads elsewhere. Rejecting a tool event after execution detects contamination but cannot prevent it. A supported empty tool registry and controlled global instruction/skill loading still need evidence.
2. **Request counting:** our wrapper would make no retries, but the reviewed settings document retry parameters for custom providers and separately say built-in provider IDs cannot be overridden. We have not established a supported zero-retry configuration for the subscription provider. Thus 96 CLI invocations cannot be asserted to mean at most 96 actual provider requests.
3. **Cost and generation bounds:** we have not verified a hard output/reasoning-token cap through this CLI or a conservative per-request subscription-credit bound. A response schema limits shape; a byte cap limits supplied public input; a timeout limits waiting. None supplies the missing generation or charge bound. These requirements remain part of the [pilot specification](../docs/LLM_PILOT_SPEC.md).

These are review findings, not claims that such controls can never exist. The configuration reference documents individual toggles, memory settings, provider retry settings, and per-skill overrides, but does not establish the full research contract for this installed transport. [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

## Accounting decision

Use the existing subscription if these gates can be closed. The adapter fixes the model to Luna, proposes low reasoning effort, disallows API-key fallback, and declares zero authorized incremental API spending. Subscription allowance and credits are separate accounting units; their consumption is not free merely because no API key is supplied. Public pricing describes variable allowance consumption and estimated message ranges, not a fixed per-request credit charge. API token prices must not be applied as an observed subscription invoice. [Codex pricing](https://learn.chatgpt.com/docs/pricing).

No credit purchase, reset redemption, account-setting modification, or quota bypass is implemented. The first development allocation remains **at most 96 provider requests**, not an entitlement to consume the complete 432-request pilot schedule.

## Safe local interface

```powershell
python experiments/dependency_memory/codex_subscription.py --check
python experiments/dependency_memory/codex_subscription.py --check-auth
```

These commands inspect the official CLI and return redacted classifications. They never call a model. If the sandbox cannot reach the normal credential store, repeat the narrow status check outside it before diagnosing authentication.

`CodexSubscriptionClient.complete(request)` checks the launch gate before any dispatch and reports `dispatched: false`. There is no override flag. `prepare_request` returns a review-only candidate command and the allowlisted public stdin bytes; it explicitly reports `launch_ready: false`. These bytes are not mislabeled as the CLI's complete provider payload. `parse_events` rejects unknown/tool events, duplicate JSON keys, malformed usage, multiple threads/turns, and ambiguous final messages. Token fields remain separate, and unknown dollar/credit charges remain null.

The next implementation change must close the gates with supported controls, pin and inspect the actual transport, and version the manifest before launching. Until then, fake-model development and independent mathematical/literature review can proceed without contaminating the intended information condition or claiming a paid/model result.

Two concrete follow-up routes remain. First, investigate the official app-server's empty-environment and capability-root controls and an inspectable request-count/token-budget mechanism; test them with synthetic sentinels before exposing any experiment fixture. If they close every gate, retain the requested subscription path. Second, a separately versioned native-harness diagnostic could deliberately include Codex's declared instructions and tools and study that whole intervention. It would answer a different question and must not be pooled into the irreversible-memory pilot. A plain stateless API adapter is another technical route, but would require separately authorized API billing; no such fallback is configured here.

## Focused app-server schema follow-up

One additional read-only pass inspected the experimental JSON schemas generated by the same installed binary. `thread/start` supports `ephemeral`, `baseInstructions`, `developerInstructions`, `dynamicTools`, `selectedCapabilityRoots`, and `environments`. Its environment description explicitly says an empty list disables environment access unless a turn overrides it. `turn/start` also accepts an empty environment list and an `outputSchema`. These are concrete candidates for better control of filesystem access and declared instructions.

However, `dynamicTools: []` declares no client-added tools; neither its schema nor the reviewed documentation says it removes built-in or hosted tools. `selectedCapabilityRoots: []` is not documented as a complete tool-registry deny rule. Neither `ThreadStartParams` nor `TurnStartParams` exposes a hard output-token cap or a retry count. The generic thread `config` object accepts arbitrary properties in the generated schema, which is not evidence that a proposed property exists or takes effect. The app-server documentation separately describes dynamic-tool persistence and exposes instruction source paths on thread startup; neither guarantees a complete outbound-payload audit. [Official app-server documentation](https://learn.chatgpt.com/docs/app-server).

Therefore the schema pass identifies a specific next candidate but closes none of the three gates on its own. No app-server thread or model turn was started. The next bounded investigation should inspect the effective registry and retry/output-limit implementation in the corresponding published client revision, then test a synthetic sentinel request under an amended transport manifest only if those controls are demonstrated.
