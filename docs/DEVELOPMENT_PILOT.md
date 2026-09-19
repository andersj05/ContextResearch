# Development pilot implementation and subscription setup

September 19, 2026. Implementation v0.3. The development template, public request interface, evaluator, and fake-client controls are implemented. **No live model request has been made.** The requested provider is the existing ChatGPT/Codex subscription with `gpt-5.6-luna`; the provider launch gate remains closed.

## What is ready

The [request interface](../experiments/dependency_memory/pilot_interface.py) implements `direct_artifact_tags` in explicit-key and inferred-property modes. Static metadata lists all six jobs independently of the candidate pair, target, and receipt values. Only a visible manifest identifies the applicable pair. Every request contains approved public configuration, static metadata, current receipts, and the current observation window. Scenario labels, evaluator identifiers, seeds, targets, exact answers, and reference costs are excluded.

At a boundary the client returns keys only. Validation rejects invented/duplicate keys, excess capacity, and extra fields. The host copies the exact latest visible records in canonical order and deletes the old window. A later request can regain a deleted value only through a declared new observation, such as the scheduled revision. Recovery occurs after the last manager request through the scripted controller.

The [development runner](../experiments/dependency_memory/run_development_pilot.py) executes 12 Stage-A decisions and 36 Stage-B episodes on the reserved development route. It reserves each attempt before dispatch, enforces a ceiling of 96, performs no automatic retry or corrective reprompt, and preserves failures and incomplete episodes. It writes an evaluator-only manifest, exact canonical public request bytes, responses, hashes, and summary. These files never enter client requests. Held-out templates and calls are excluded.

## Completed offline checks

The [reproducible audit](../experiments/dependency_memory/results/development_pilot_audit.json) records:

| Fake control | Fake requests | Completed development episodes | Required receipt available before recovery | Recoveries |
|---|---|---|---|---|
| Exact scripted selector | 96 | 36/36 | 26/36 | 10/36 |
| Forget every receipt | 96 | 36/36 | 0/36 | 36/36 |
| Invalid output | 48 | 0/36 | Not reached | 0 |

These are software controls, not LLM results or independent trials. The first control's realized numbers describe one reserved route, not the full routing population. Invalid output stops the affected episode without a repair call.

Tests cover all 30 routes and both modes, exact-reference attainment, changed private targets, unrevealed payloads, deleted receipts, nested field injection, revision ordering, full-memory and deliberately answer-visible offline controls, stale/wrong receipts, partial budgets, and failure accounting. A separate local review checked 540 paired target changes, 180 deletion cases, and every request cap from zero through 96. It found and prompted a fix for stale usage metadata carrying from a successful attempt into a later failed attempt. These checks establish the trusted Python interface contract; they do not certify provider isolation.

## Subscription connection and remaining gate

The installed official CLI reports `codex-cli 0.155.0-alpha.9.2`. A read-only status check outside the workspace sandbox returned `Logged in using ChatGPT`. The existing subscription connection works; no credential was copied and no API key was configured. This check does not establish model entitlement or make a model request.

The [subscription integration](../experiments/dependency_memory/codex_subscription.py) selects `gpt-5.6-luna`, proposes low reasoning effort, rejects API-key fallback, provides redacted diagnostics, prepares a candidate invocation, and validates structured CLI output. It deliberately refuses live dispatch. The [dated transport review](../research/CODEX_SUBSCRIPTION_TRANSPORT_2026-09-19.md) records three unresolved requirements:

1. Verify the actual complete outbound request and an empty tool registry. Local prompt inspection still showed global instructions and host skills; that debug command does not implement all `exec` isolation flags.
2. Bound all underlying provider attempts, including client retries. Ninety-six CLI processes cannot yet be certified as at most 96 model requests.
3. Establish hard reasoning/output limits and a conservative subscription quota/credit bound. API prices are not subscription charges, and available subscription credits must not be labeled free.

The chosen development ceiling is 96 requests with zero runner retries. Additional API spending is capped at **US$0** because API billing was not selected. The subscription-credit bound remains unresolved; zero API spending is not a zero-cost claim about the subscription. No credits were purchased or redeemed. A mutable Luna alias is documented rather than represented as an immutable model revision.

The next provider task is to verify a supported transport against these requirements. If the subscription client cannot expose those controls, a separately priced stateless API path or a separately versioned native-harness diagnostic would require an explicit design change. Neither is silently substituted into this pilot.

## Reproduce and inspect

From the repository root, use a new output directory for each full fake run:

```powershell
python experiments/dependency_memory/run_development_pilot.py --output tmp/pilot-optimal-v1
python experiments/dependency_memory/run_development_pilot.py --fake-mode forget_all --output tmp/pilot-forget-all-v1
python experiments/dependency_memory/run_development_pilot.py --offline-audit --output experiments/dependency_memory/results/development_pilot_audit.json
python experiments/dependency_memory/codex_subscription.py
python -m unittest discover -s experiments/dependency_memory -v
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

The subscription command is read-only and does not dispatch a model request. Optional authentication diagnostics use the official CLI's status command; a sandbox/home-directory failure is unverified, not proof of invalid credentials. The runner rejects live execution until a reviewed provider contract is implemented. Do not commit uncontrolled provider session logs or authentication data.

The [external mathematical review packet](../research/EXTERNAL_REVIEW_PACKET_2026-09-19.md) is prepared alongside this work. Targeted source comparisons narrow novelty questions; no external reviewer has yet been contacted. The four held-out families remain future work, and the tiny reserved sample remains a debugging exercise.
