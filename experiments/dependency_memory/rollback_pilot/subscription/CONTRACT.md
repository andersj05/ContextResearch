# Subscription calibration contract

October 8, 2026. Version `rollback-subscription-v1`. This is an amendment for
the user's explicit instruction to use their Codex subscription with GPT-6 Luna.
The original E0 evidence and API proposal remain frozen at their existing paths.

Use the installed official Codex app-server, ChatGPT sign-in, `gpt-6-luna`,
medium effort and Standard speed. Pin the executable, generated protocol schemas,
configuration, global instruction text and source files before generation. The
model name is a mutable alias; no immutable server revision is established.
Credentials remain owned by Codex. No token extraction, API-key fallback,
provider HTTP proxy, model fallback, paid tools, credit purchase or limit reset.

The new authorization is the user's October 8 instructions to use the Codex
subscription with GPT-6 Luna and finish the tests without a token or cost budget.
The first allocation covers **eight E1 generation attempts** on the already
disclosed authored fixtures. It has no credit ceiling. No old allocation is
reopened. A task pilot uses its own frozen contract before generation; E3/E4/E5
remain separate.

Every decision starts a fresh ephemeral process and thread. The process receives
an empty scratch directory, no runtime environments, no workspace roots, no
dynamic tools, no actor-accessible evaluator files and explicit instructions.
The CLI can add fixed global instructions and harness tool descriptions. The
installed-client loopback audit must bind and disclose them. Reject every tool
attempt, model reroute, extra generation, compaction or unexpected input channel.
The rollout budget's very large prefill weight makes the harness stop after its
first provider response; this is a generation-count guard, **not an output cap**.
Mock final/tool/HTTP-failure/truncated-stream cases must establish one request.
The adapter sets zero request and stream retries on its subscription provider.

The current CLI has no verified configurable 16,384 output-token ceiling. E1
therefore audits the provider-default envelope rather than claiming the API
proposal's cap. The published GPT-6 Luna limits are 1,050,000 context tokens and
128,000 output tokens. Reserve **4.225 planning credits** before each attempt:
1,050,000 inputs at 2.5 credits/M plus 128,000 outputs at 12.5 credits/M. This is
a deliberately conservative **conditional planning bound**, assuming these
published model limits apply to subscription inference and Standard credit rates.
It is not a measured account charge or proof of a server-side spending cap.
Reservations remain useful for documenting unknown liability; the user's updated
instruction removes budget admission as a stopping criterion for these tests.
Input admission separately bounds the complete serialized client body at 32,768
UTF-8 bytes, including fixed overhead and duplicated response schema. Bytes are
not reported as provider tokens. Reject oversized requests without truncating.

Count cached inputs as a subset of total inputs, and reasoning as a subset of
output. Settle only complete, valid token telemetry. An unknown dispatch/usage
locks its full reservation and stops the allocation, including after reopening.
Known malformed model text remains a metered format failure. Never retry a
diagnostic or transfer unused slots. Record account quota snapshots separately
from calculated credits: account usage is shared with other work. Stop before
included usage reaches 100%; this calibration does not enable credit fallback.

E1 uses the eight requests frozen in E0: math/code checkpoint, math/code branch,
math lesson, code summary, math K continuation and code R continuation. Fixtures
remain excluded from every study cohort. Parse all structured artifacts, enforce
the 1,024-byte writer limit (an explicit replacement for the proposal's
unaudited token allowance), and grade code only
inside the pinned isolated Docker runtime. No format repairs or prompt tuning
within this allocation. Publish every response, metering and disposition in a
bounded evidence bundle. Preserve response text, but omit raw reasoning and
uncontrolled session logs.

Calibration cannot certify an unchanged v0.2 E2 launch: the smaller generation
cap and tokenizer audit remain unestablished, and the real twelve-task coding
cohort still requires verified provenance, references and complete retained
tests. Report those gates explicitly. Do not reinterpret E1 as a rollback gain.

Official sources inspected October 8:

- [Subscription authentication](https://learn.chatgpt.com/docs/auth)
- [App-server protocol](https://learn.chatgpt.com/docs/app-server)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Subscription credit rates](https://learn.chatgpt.com/docs/pricing)
- [GPT-6 Luna model limits](https://developers.openai.com/api/docs/models/gpt-6-luna)
