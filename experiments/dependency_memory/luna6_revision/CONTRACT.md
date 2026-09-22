# GPT-6 Luna medium: delayed release obligations

Frozen before production generation on September 22, 2026. This is an exploratory
development pilot, not a held-out result, native compaction comparison, or novelty
claim. The user explicitly requested new GPT-6 Luna medium calls. This separate
allocation permits at most **144 dispatched requests and 20 planning credits**,
through the existing managed ChatGPT login. No purchases, resets, API keys, or
automatic retries. The fixed main schedule contains 117 requests, including one
transport smoke request; unused allocation is not an instruction to launch more.

## Task and access

Four generated software-release handoffs, each with six services, represent CI,
artifact identity, approval scope, required test sets, and open release blockers.
Seeds 9201–9204 fix names, exact opaque identifiers, and record ordering. These
are constructed realistic workflows, not observed production incidents. A
deterministic executable release gate supplies the grader. Two handoffs contain
an initially invalid selected service; two provide additional valid/invalid
controls. Initial source evidence is compressed to **900 UTF-8 bytes** before a
pair of services is disclosed, and then to **440 bytes** before the target and a
late event are disclosed. Four continuations per handoff cover both targets and
both an irrelevant note update and a relevant gate update. A single missing,
stale, failed, or newly required obligation must block release. Absence of blockers
is a revocable observation. Exact artifact identity and unresolved work matter.

Every model invocation gets a fresh process and ephemeral thread, no environment
or archive, no prior reasoning or provider response IDs. Public request envelopes
are saved exactly. Fixed task-independent global GitHub instructions, base and
developer instructions, a rollout-budget reminder, and three wrapper tools are
declared background. The installed client omits authoritative nested-tool metadata;
we do **not** certify its hidden registry is empty. The no-auth loopback audit
checks every visible input, no skill catalog, one HTTP request, and termination
after one generation even for a tool response. Accepted live responses require
zero tool items; any tool attempt, reroute, uncertain usage, or transport failure
stops the schedule. Remote server internals remain unobserved.

## Methods, frozen before answers

- **prose**: Luna writes two concise summaries of the available observation.
- **structured**: Luna writes two summaries explicitly preserving identifiers,
  negative facts, test membership, and the scope of completed checks.
- **repair**: reuse the structured parent proposal, then check and restore a
  canonical dependency projection before forgetting. Luna writes a child proposal
  from that repaired parent. Check and restore again at the second boundary.
- **direct**: produce the identical dependency projection directly, without the
  proposal calls. This strong control reveals when proposing and repairing is
  needless overhead.
- **indexed**: always read the target's original record at the terminal boundary.
  No summary is written. All recovered bytes and model inputs are charged.
- **full**: provide the complete original handoff for every continuation. No
  summary is written. This is a fresh-thread information-sufficient control,
  not a native provider session.

The projection is a hand-written adapter for the **declared executable gate**,
not automatic extraction from unknown code. Its compact rows contain service,
artifact, approval, required tests, CI results, and blockers. It does not replace
facts with an irrevocable `ready` bit. At each boundary the checker sees only the
same evidence available to the compressor. The second checker obtains its state
by decoding the bounded repaired parent, never by consulting the original source.
If a candidate memory is not exactly the canonical projection, replacement uses
that projection. This conservative checker does not claim to understand arbitrary
prose or to achieve minimal repairs. Direct retention is expected to match repair
semantics at lower cost. A gate-specific success is not a generic algorithmic win.

Both repaired and direct memory, including format tags, must fit the same byte
limits. Ordinary generated overlong memories are clipped by UTF-8 prefix, without
a retry; record raw and admitted lengths. Missing/malformed memories become empty
and are counted as policy failures. The final model must emit `release`, `hold`,
or `inspect`, exact artifact identity, and an exact set of outstanding work.
`inspect` is an unsuccessful terminal answer under the irreversible arms. Indexed
recovery is the separately declared control. The checker never receives late
events or selected targets ahead of their disclosure.

## Measurement and analysis

Primary outcome: exact terminal answer. Secondary: unsafe releases, mistaken
holds, incorrect artifact, obligation-set error, overlong memory, wall latency,
admitted memory bytes, source/recovery/check bytes and checker CPU time. Check
the grader independently over the gate truth table and mutation invariants.
Score all outputs after the complete fixed launch. Reuse shared parent calls in
the experiment, but charge their full cost separately to every hypothetical arm.
Charge parent/child calls once per handoff and the four final calls actually made;
report per-query costs and measured cost-success frontiers. Do not pretend that
padding a cheaper method spends model compute or improves its answer.

Official Codex pricing reviewed September 22 lists GPT-6 Luna at 2.5 input,
0.25 cached-input, and 12.5 output credits per million tokens, standard tier;
there is no separate Codex cache-write charge. Reasoning is part of output and
must not be charged twice. Record raw usage. For dispatch safety reserve **7.65**
credits per in-flight call, covering the published 1.05M input/128K output maxima
even with the API's conservative long-context multipliers. Enforce the audited
32,768-byte wire bound and observed input below 272K. Settlement uses the published
short-context Codex rates. The ceiling is an internal planning bound, not an
attributable measurement of subscription debit or provider serving cost. Account
usage is shared with this research task. No inference about API dollars is made.

Record the mutable `gpt-6-luna` alias, **medium** effort, default service tier,
installed CLI version/hash, profile/global-instruction hashes, model catalog,
request/answer/usage ledgers, and frozen source hashes. No model sampling seed is
exposed. Workflows are correlated continuations; 16 cases are not 16 independent
natural workloads. Neither a positive result nor novelty is guaranteed.

Sources: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna),
[Codex pricing](https://learn.chatgpt.com/docs/pricing),
[prior-art comparison](../../../research/FEEDBACK_PRIOR_ART_2026-09-22.md).
