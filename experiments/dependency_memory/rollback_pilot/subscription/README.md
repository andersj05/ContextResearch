# GPT-6 Luna through the Codex subscription

Versioned subscription support for the October 8 rollback tests. Read the
[contract](CONTRACT.md) and the [saved calibration finding](../../../../research/ROLLBACK_SUBSCRIPTION_2026-10-08.md).
The original E0 sources and sealed evidence stay at their existing paths.

Run offline unit tests from the repository root:

```powershell
python -m unittest experiments.dependency_memory.rollback_pilot.subscription.test_subscription -v
```

The opt-in `preflight` module checks the signed-in model catalog and ten synthetic
localhost cases using the installed official CLI. It generates no model answers.
It verifies actual serialization, fixed instruction/tool surfaces and zero retry
behavior for final, tool, HTTP failure, truncated stream, missing usage and
duplicate answer cases. It does not authenticate or inspect server internals.

The `calibration` module has separate `freeze`, `launch` and `verify` commands.
A launch requires a successful current-client preflight, digest-pinned Docker
runtime, installed-client generated schema bindings and a new frozen allocation.
An exclusive start marker prevents repetition after interruption. All scheduled
identities and dispositions survive a stop. Responses contain only final visible
text, bounded metadata and complete token usage; raw reasoning is never saved or
replayed. Credentials remain inside Codex.

The subscription route exposes no verified configurable 16,384-token output cap.
The amended E1 contract records provider-default generation, observed telemetry,
32,768-byte complete-client-body admission and a 1,024-byte writer limit. Its
planning-credit estimates are distinct from actual account charges and API USD.
The user removed token/cost budget admission for these tests. Call identities,
isolation, no retry and unknown-outcome stops remain scientific requirements.

The full E2 task pilot also needs a complete task manifest and a recorded protocol
amendment for any source or limit change. E1 fixtures cannot fill study task slots.
Later policy stages remain separate.
