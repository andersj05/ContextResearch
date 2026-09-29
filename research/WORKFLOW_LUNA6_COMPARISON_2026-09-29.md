# Luna 6 comparison on an observed repository handoff

September 29, 2026. Claim C51. **Development evidence, not held-out evaluation.**

## Result

The user requested live Luna 6 tests after the offline evaluation packet.
A separate contract, implementation, 36-request schedule and fresh transport
preflight were committed at `ef31373` before dispatch. All 36 calls completed,
with one metered response each and no retries, transport errors or model
fallback. Total usage: **375,780 input tokens**, including **23,808 cached**;
**9,970 output tokens**, including **3,027 reasoning**. Token-derived cost is
**1.0105070 planning credits**, within the separate 20-credit reservation bound.
Actual subscription debit is not attributable; API-dollar spending is zero.

| Method | Exact decisions | False ready | Model planning credits | Cache-neutral model credits |
|---|---:|---:|---:|---:|
| Checked proposals | 4/4 | 0 | 0.2940470 | 0.3101750 |
| Direct records | 4/4 | 0 | 0.0325430 | 0.0452150 |
| Indexed raw recovery | 4/4 | 0 | 0.1968765 | 0.2032125 |
| Strong prose | 3/4 | 0 | 0.2858350 | 0.3002350 |
| Full history | 4/4 | 0 | 0.2012055 | 0.2052375 |

All memory-writing calls count. Direct records use the fewest model credits in
both cache views while matching the best observed score. The checked pipeline
has one fewer exact failure than prose but costs slightly more in both views;
it has no accuracy advantage over direct records. This does not establish a
candidate-method contribution. Local CPU, elapsed time, byte traffic and index
storage duration are recorded separately, not converted into a total-cost claim.

## What the four cases are

All cases reuse the actual local execution of tests, repository validation and
paper build on clean source commit `40cec05`, captured for the
[offline packet](../experiments/dependency_memory/workflow_eval/README.md).
The first case uses that unchanged successful handoff. The other three impose
a constructed source revision, a constructed later failed test, or a constructed
replacement of the HTML artifact. They are correlated counterfactual controls,
not four naturally observed incidents or independent workflow families.

Memory-only arms pass through the frozen 4,096- and 1,536-byte limits. At the
second boundary every arm receives the same new observations and check scope;
only afterward does the final source/artifact inventory arrive. The index and
full-history arms explicitly retain all raw observations. Because these cases
request all three checks, the index retrieves the entire relevant workflow;
this deliberately gives little retrieval-cost advantage over full history.
The direct representation of the original three receipts occupies 728 bytes.

The terminal grader is the packet's unchanged public-rule implementation. It
uses the raw chronological ledger independently of the memory implementation.
The live provider schema uses fixed nullable evidence keys; the host only
removes null entries before exact scoring. External independent grader review
remains pending. The offline invariant checks and saved-request reconstruction
are local validation, not external certification.

## Failure inspection

Prose fails only the later-failed-test case. It correctly marks `tests` as needing
work but also unnecessarily marks `repository` as needing work, omitting its
successful run from the evidence map. The **814-byte** admitted child is below
the 1,536-byte cap and explicitly retains the correct repository success and
exact run ID. Manual inspection therefore finds relevant evidence available at
the final step; the automatic table-based sufficiency test reports prose as
unknown. No truncation occurred and no unsafe false-ready decision was observed.

The checked arm falls back twice, at the child boundary in the new-snapshot and
replaced-artifact cases. Each 727-byte proposal omits the closing `]` of its
receipt list. Adding that single delimiter in a post-hoc syntax inspection
produces the same receipt objects as the admitted fallback. The live checker
did not repair text heuristically: it rejected invalid JSON and regenerated
records from the still-available bounded parent. No old source was reread after
deletion, no model response was retried and no terminal decision was rescored.

Checked/direct/indexed/full final inputs pass the deterministic receipt-sufficiency
diagnostic for each of the four current terminal tasks. That finite diagnostic
does not certify arbitrary future obligations or arbitrary prose.

## Transport and current-source scope

The model is the mutable `gpt-6-luna` alias at medium reasoning and default
Standard speed. No immutable revision or sampling seed is exposed. CLI
0.158.0-alpha.2.1, binary/profile/global-instruction hashes and the account's
returned model entry are pinned in the saved preflight. The September 22 audit
rejected this client's changed serialization before any model generation.
The separate updated audit checks the actual instruction and wrapper/clock
registry against a no-auth loopback server. All four controls make exactly one
HTTP attempt, including error cases; the largest observed body is 88,628 bytes
with 12,941 bytes of fixed overhead. Accepted live outputs have one complete
usage event and no tool items. Client evidence does not reveal provider internals.

The official [app-server documentation](https://learn.chatgpt.com/docs/app-server),
[Luna 6 model page](https://developers.openai.com/api/docs/models/gpt-6-luna), and
[Codex pricing](https://learn.chatgpt.com/docs/pricing) were reviewed September 29.
The published Standard rates are 2.5 input, 0.25 cached input and 12.5 output
credits per million tokens; reasoning is already included in output. The fresh
local audit supplies the serialization evidence, separately from those pages.

## Reproduce and interpret

- [Frozen contract](../experiments/dependency_memory/workflow_eval_live/CONTRACT.md)
- [Manifest and schedule](../experiments/dependency_memory/results/workflow_live_2026-09-29/manifest.json)
- [Transport preflight](../experiments/dependency_memory/results/workflow_live_2026-09-29/preflight.json)
- [Saved-evidence analysis](../experiments/dependency_memory/results/workflow_live_2026-09-29/analysis.json)
- [Generated comparison](../experiments/dependency_memory/results/workflow_live_2026-09-29/report.md)

The analyzer rebuilds every public request from frozen inputs and prior saved
responses, checks admitted memories and deletion paths, reconciles all usage,
and independently grades the final responses. It makes no model calls.

```powershell
python -m experiments.dependency_memory.workflow_eval_live.analyze experiments/dependency_memory/results/workflow_live_2026-09-29
```

This supports a narrow development conclusion: direct receipts are the most
economical successful model-input method in this small comparison. Keep that
baseline central. The packet's twelve untouched real change-task episodes,
fully priced infrastructure comparison and held-out engineering go criterion
remain unperformed. Do not enlarge the apparent sample by counting repeated
conditions, checks or token counts as independent workloads.
