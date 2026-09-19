# Luna transport isolation follow-up

September 19, 2026. This client investigation and its synthetic local-server checks made **zero external model-generation requests** and did not read or copy authentication credentials. It supplements the [original transport review](CODEX_SUBSCRIPTION_TRANSPORT_2026-09-19.md).

## Concrete app-server startup result

The installed `codex-cli 0.155.0-alpha.9.2` successfully accepted a fresh ephemeral `thread/start` through its official stdio app-server. A separate `account/read` response classified the existing authentication as `chatgpt`. The startup response reported `gpt-5.6-luna`, provider `openai`, low reasoning effort, an empty runtime-workspace-root list, and zero turns. No `turn/start` was sent. Selecting a model at startup is not itself a generation or model-quality test.

The request explicitly supplied `environments: []`, `selectedCapabilityRoots: []`, `dynamicTools: []`, `runtimeWorkspaceRoots: []`, `ephemeral: true`, `approvalPolicy: "never"`, and `sandbox: "read-only"`. It also supplied short controlled base and developer instructions and disabled model fallback. The scratch working directory contained no experiment data. The generated schema documents an empty environment list as disabling environment access; this is stronger than merely choosing an empty working directory. `dynamicTools: []` still means no client-added tools, not necessarily no built-in tools. [Official app-server documentation](https://learn.chatgpt.com/docs/app-server).

The following additional properties were found in the [official configuration schema](https://learn.chatgpt.com/docs/config-schema.json), then confirmed in the running app-server's `config/read` response:

| Property | Observed effective value | Scope |
|---|---|---|
| `include_environment_context` | `false` | Omit environment-context instructions |
| `include_permissions_instructions` | `false` | Omit permission instructions |
| `include_collaboration_mode_instructions` | `false` | Omit collaboration-mode instructions |
| `include_apps_instructions` | `false` | Omit app instructions |
| `features.skip_host_skill_discovery` | `true` | Conditional host-skill-discovery optimization, not a universal deny rule |
| `features.tool_registry.turn_metadata_includes_tool_info` | `true` | Request metadata can carry authoritative tool information |
| `features.shell_tool`, `features.unified_exec` | `false` | Disable these execution features |
| `features.apps`, `features.plugins` | `false` | Disable those integration features |
| `features.code_mode`, `features.tool_search` | `false` | Disable those access surfaces |
| `project_doc_max_bytes` | `0` | Project-document limit; does not remove the observed global instruction source |

The local pinned September 16 feature source describes `skip_host_skill_discovery` as skipping host snapshots only when no registered contributor needs them. It cannot be promoted to an unconditional skill-isolation guarantee. The startup probe did not inspect a model-facing skill list.

## Remaining instruction channel

Despite those controls and the explicit base/developer instructions, `thread/start.instructionSources` still reported the user's global `.codex/AGENTS.md`. Thus the fresh, no-environment setup does not meet the original claim that the model receives only the public experiment request and controlled instructions. The probe did not reveal receipt answers or establish actual leakage; it establishes an undeclared instruction source that must either be removed through a supported control or declared in a separately versioned harness condition.

`thread/start` exposes instruction-source paths, not the complete effective outbound payload or tool registry. `debug prompt-input` renders input messages; it does not expose the entire request. The metadata flag above is a concrete audit aid, but merely setting it does not establish that a complete registry was observed. No complete provider-payload or empty-registry certification is claimed here.

## Completed loopback serialization and continuation checks

The reusable [audit](../experiments/dependency_memory/audit_luna_transport.py) now runs the installed app-server against a fake Responses server bound only to `127.0.0.1`. Its distinct provider has `requires_openai_auth: false`, no credential source, disabled WebSockets, and zero configured HTTP/stream retries. The [sanitized result](../experiments/dependency_memory/results/luna_transport_audit.json) records four cases. This checks the installed client's serialized body and control flow; it is not a Luna result or a direct observation of proprietary server internals.

The initial capture found a significant trap: no top-level `tools` property did **not** mean no tools. This client sends tool declarations inside `input` items of type `additional_tools`. Authoritative registry metadata also showed inherited Node REPL and skill tools. An empty `mcp_servers` map did not clear the inherited server. Explicitly disabling `mcp_servers.node_repl.enabled`, disabling bundled skills and skill instructions, and excluding the `skills` namespace removed those data-access surfaces.

The final [shared configuration](../experiments/dependency_memory/luna_isolation.py) exposes only `functions.exec`, `functions.wait`, and `functions.request_user_input`. The declared exec runtime is a fresh V8 isolate without Node, filesystem, network, or nested tools. The exact registry has no nested or deferred tool entries. These three wrappers remain declared; we do not call this an empty registry. The adapter rejects tool attempts as invalid experiment responses, and the continuation guard described below prevents another model request after a completed first response.

The complete model-visible input allowlist consists of controlled base instructions, controlled developer instructions, the global GitHub authentication guidance, the public experiment JSON, and a fixed rollout-budget message. The global guidance contains no fixture, evaluator answer, route, retention recommendation, or research result. It is now declared fixed public background, with normalized-text SHA-256 `263fbf5f86b6338244e956ebe986e34e3aecafb5c061fe95d140a677b8d60714`. Skill catalogs, environment blocks, old conversation items, and additional context fail the audit. Unknown body fields, prior-response/conversation channels, and `store: true` also fail it.

Declaring this task-independent background changes the planned information contract explicitly. It does not supply deleted receipts and does not by itself invalidate a restricted-memory experiment conditioned on fixed public information. No previous live pilot exists to pool with the amended condition. Results under this configuration would concern the declared model interface, not superiority over native harness behavior or native compaction.

## One-generation guard and its observable terminal status

An adversarial fake response requesting `functions.exec` originally caused two HTTP requests, despite zero retry settings. This was an agent continuation, not a network retry. The final configuration enables the existing rollout budget with limit 32,768, prefill-token weight 1,000,000, sampling-token weight 1, and no reminder thresholds. Any completed response reporting at least one input token exhausts that weighted session budget. The client then stops before a continuation. This is a count guard, **not a hard limit on the first generation's output or reasoning tokens**.

The model sees the fixed public message reporting 32,768 weighted tokens remaining. Its text is part of the allowlist and protocol; it is not an evaluator clue. The weights and limit are client accounting choices and are unrelated to dollars, record slots, or the research memory capacity.

| Synthetic response | HTTP POSTs observed | Final model message | Terminal client result |
|---|---|---|---|
| Valid final JSON and complete token usage | 1 | One completed JSON message | `failed` / `sessionBudgetExceeded` |
| A tool call and complete token usage | 1 | None | `failed` / `sessionBudgetExceeded` |
| HTTP 503 | 1 | None | Provider failure |
| Response-created event followed by truncated stream | 1 | None | Stream failure |

In the first case, the app-server emits the completed `agentMessage`, then complete token usage, then the budget-exhausted terminal event. A single-generation adapter may accept the already completed model decision only when its exact response and usage validations pass and the sole terminal error is this intended budget stop. It must retain the actual client status and distinguish it from successful completion of a native agent turn. The negative tool case remains invalid; provider and stream failures are not converted into successful decisions.

The observed complete synthetic body was 12,742 bytes, of which 10,158 bytes remained after conservatively subtracting the separately counted public-text and output-schema encodings. The shared code allows 16,000 bytes of fixed overhead, adds the actual conservatively JSON-encoded public text and provider schema, and requires the resulting bound to be at most 32,768 bytes. This bound is conditional on the reviewed binary, configuration, and global-instruction hashes and the exact input/tool allowlist. It does not bound inaccessible provider-added context.

Ten offline invariant tests cover hidden tool insertion, deleted/old context, prior-response and unknown body fields, altered global instructions, schema projection, fresh empty environments, input/wire limits, and resolved-configuration drift. The preflight validator parses the shared overrides and compares all 45 declared leaves with `config/read`, including the continuation guard, exact skill overrides, and Boolean types; it also rejects every enabled MCP server. An actual initialize/config-read-only probe verified all 45 leaves with zero threads or model turns. The new subscription transport requires Python 3.11+ for standard-library TOML parsing; the original mathematical diagnostics do not depend on that API.

The fake-server audit records authentication disabled and no Authorization header in every case. Production authentication routing and subscription-charge reservations are separately reviewed in the [accounting follow-up](LUNA_ACCOUNTING_FOLLOWUP_2026-09-19.md); the mock artifact deliberately does not set the combined live launch gate.

To reproduce the opt-in installed-client audit:

```powershell
python experiments/dependency_memory/audit_luna_transport.py --global-instructions C:/Users/jense/.codex/AGENTS.md --output experiments/dependency_memory/results/luna_transport_audit.json
```

The path above selects the already declared local public instruction file. The script never reads authentication files or saves uncontrolled request transcripts. A different global-instruction hash, enabled MCP server, client binary, or additional tool/input channel requires renewed review.
