# Matched checkpoint rollback v7

October 12, 2026. New development experiment requested by the user after reviewing
the v6 information-loss problem. Earlier source snapshots, allocations, calls,
unknowns and results stay unchanged. This protocol does not reopen any allocation.

## Question and contrast

Does removing one naturally failed visible branch improve subsequent recovery
when its pre-branch context, task evidence, public feedback and lesson are held
fixed? This returns to the [original mechanism design](../../../research/ROLLBACK_PILOT_DESIGN_2026-10-07.md).
The v6 policy cleared earlier task packets along with unsuccessful attempts.
Here public packets persist independently of generated trial records.

The first live pilot fixes 24 new intermediate-profile level-2 revision-ledger
tasks, construction seed 2026101267, three disclosure stages and four candidate
actions. Each has 28 transaction IDs over six accounts. Every action submits a
complete best candidate; no model is instructed to make a mistake. These tasks
reuse an authored generator with a new seed and identities. Prior controls inform
the chosen difficulty; this is development, not independent confirmation.

For each task, one shared prefix runs until the first natural public mismatch.
Immediately before that failed action, the controller has a saved checkpoint C:
the last accepted artifact, all successful earlier generated records, and the
exact public packets released so far. Original task instructions remain separate.
If at least one of the four actions remains, generate one lesson L from that
failure. Both continuations receive the same C, public feedback F, and L:

| Continuation | First reconstructed input |
|---|---|
| K | C, complete released public dossier, failed branch B, F, L |
| R | C, complete released public dossier, F, L |

The failed branch contains the unsuccessful candidate, its brief visible note
and receipt. It contains no unique external task packet. All packets previously
released remain byte-for-byte intact in a separate public dossier. This is an
explicit full-evidence condition, not an irreversible-memory condition. No
transaction-state oracle, corrected candidate, future packet or hidden witness
is added. The exact graders send only their ordinary public rejection receipt.

The controller checks that the first K/R request payloads are byte-identical
after removing only the `trial` field contents; the schema, instructions, model,
effort, checkpoint, feedback, lesson and remaining allowance are identical.
The actor receives no K/R label. Both reconstructed requests must fit before
either arm is sent. Pair-contract failure is a global implementation stop.

Each continuation uses the original remaining allowance. Its subsequent records
accumulate normally; there are no further experimental deletions or lesson
writers. A pass can reveal the next packet, which joins that arm's public dossier.
An arm's later trajectory may diverge naturally. Both start from the exact same
saved failure rather than independent failures. The common lesson can itself
retain failed values or hypotheses: the treatment removes the raw branch, not
all information derived from it. First-stage failures lack earlier accepted
progress and are reported separately from later-stage failures.

## Access and transport

Every action and lesson uses `gpt-6-luna`, medium effort, through the existing
Codex subscription route. The reviewed adapter starts a fresh isolated
process/thread, disables external integrations, excludes prior sessions and
opaque reasoning replay, and checks one received answer and one usage record
per admission. Any observed tool-use attempt stops admissions globally and
produces no accepted score from that call.
No API key, paid purchase, credit fallback or model fallback is authorized.

The initial preflight stopped before any model admission because installed
client 0.162.0-alpha.17.2 advertises three generic MCP resource helpers absent
from the older registry contract. Preserve that failure and its zero-admission
bundle. The v7 compatibility amendment pins the exact reviewed declarations,
requires a complete runtime inventory with every MCP server disabled and no
tools, resources or resource templates before each generation, and exercises
each helper in negative loopback tests. Audit-only metadata normalization lets
the unchanged historical auditor check the remaining payload; the actual
transmitted body and its byte limit are checked separately. No process-global
patch, enabled provider or additional evidence channel is permitted. This does
not prove a tool attempt could never execute before its event is observed; it
establishes an empty MCP capability inventory and rejects observed tool items.
The clock-only fixture yields no accepted answer and no exposed tool item. A
separate synthetic clock-plus-answer fixture is accepted with one request,
one answer/usage and the one-generation guard, while no tool event is exposed.
Every preflight saves this diagnostic as a known observation limit, not as a
successful tool-rejection test. Consequently zero observed tool items does not
prove absence of every attempted helper call. The answer already exists before
any client tool result, no subsequent model request can consume that result,
and later task calls replay only the saved explicit answer. The information
contract relies on this single-generation boundary and the disabled empty MCP
inventory; it does not claim universal detection of helper attempts. Freeze
this amendment before the first model admission. The task cohort, worker count,
outcome definitions and 192-call ceiling remain unchanged.

Official [Luna model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)
and [app-server documentation](https://learn.chatgpt.com/docs/app-server) were read
October 12. The installed-client preflight and loopback probes establish the
client-visible operational contract; documentation is not proof of provider
internals. Immutable server revision and provider sampling seed remain unavailable.
The full serialized client body remains bounded at 131,072 bytes. The lesson JSON
is bounded at 4,096 UTF-8 bytes. These are byte limits, not token or dollar caps.
Provider-default output remains disclosed; configurable output caps are unverified.

## Parallel execution and budget

The pilot uses eight parallel workers under one atomic SQLite admission ledger.
The implementation supports one through sixteen workers, frozen per allocation;
changing a running allocation's worker count is not allowed. Prefix tasks run
concurrently, and eligible K/R continuations run as independent jobs with
pre-frozen randomized arm order. Paired arms cannot exchange outcomes.

For a failure at action j with total allowance H, the maximum call count is
`j + 1 lesson + 2(H-j)`. Since j is at least one, this is at most `2H`.
The 24-task, four-action pilot therefore admits at most **192 generations**,
including all shared writers and unknowns. Its 312 possible call identities are
mutually exclusive possibilities, not 312 scheduled independent observations.
No-failure tasks use at most four actions and have no recovery pair.

Each identity is admitted at most once. Unknown calls stop only their affected
trajectory; a prefix/writer unknown prevents both dependent continuations.
Unknowns stay missing and keep their accounting reservation. Account, source,
isolation, duplicate identity, metering and evidence-write faults stop all new
admissions. In-flight calls drain; they are never assumed stopped from a timeout.
An exclusive launch marker prevents relaunching the same allocation. No automatic
retry, replacement task or completion-dependent extension is permitted.

## Gates and analysis

Before live dispatch: independently check generated answers and mutations; run
fact-preservation and counterfactual request-equality tests; verify eight-way
concurrency and duplicate/unknown accounting; freeze source, cohort, schedule,
protocol and analysis; run a scripted rehearsal and receipt replay; refresh
signed-in model/account/client checks and actual-payload loopback serialization.
Fixtures deliberately exercise failure paths and are never labeled model evidence.

Report all 24 prefix dispositions, eligibility, shared writer failures, missing
scores and explicit dependent skips. Primary outcome is conditional task-level
R-minus-K terminal success among eligible prefixes. Report paired wins/losses,
ties, complete pairs and fixed-denominator missingness bounds. At least six
complete pairs permits a descriptive 10,000-resample task interval with seed
2026101268; fewer pairs remain a feasibility-limited result. This threshold is
not a power calculation and does not authorize more tasks. A complete-case exact
paired p-value, if reported, is descriptive only. No confirmatory test is planned.

Count each actual prefix and shared lesson once, plus every continuation call.
Report complete-pair continuation resource totals separately. Standalone policy
projections may add the shared preparation to each arm, but overlap and cannot
be summed as actual spend. Input includes cached input and output includes
reasoning, counting each subset once. The inherited planning-credit conversion
is an accounting convention, not current API pricing or actual account charges.

Complete the fixed allocation regardless of effect direction. After completion,
reconstruct every received prompt and response, independently regrade candidates,
reconcile jobs and all call-slot dispositions, and verify source/evidence hashes.
Implementation validity and empirical benefit are separate findings. A pilot can
show that the intended test ran correctly without establishing an advantage.

## Interpretation limits

One authored task family, short visible branch notes, conditional selection on
natural failure and small sample limit transfer. This is a single deletion of
visible records; it does not manipulate private reasoning state or test repeated
autonomous rollback. Full public-evidence retention differs from v6, so cross-run
performance changes cannot identify the causal effect of fixing its deletion.
Keep broader policy, longer tasks, other families and independent confirmation
as separately designed work. Do not change the manuscript or claim C75 from a
small development result.
