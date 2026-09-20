# Transfer study: remaining first submissions

Operational amendment, September 19, 2026. This supplements the [original frozen design](TRANSFER_STUDY.md); its scientific sample, public requests, order within each worker, model settings, scores, and primary comparison remain unchanged.

## Why a separate phase is necessary

The first launch at `999f14d` made zero model requests. The next launch at `0414198` dispatched 888 of the fixed 1,536 cases before the local 100%-used guard stopped all workers. It saved 885 valid responses. Three already generated and fully metered responses were rejected by the post-generation percentage check before their answers were saved; those outcomes remain transport failures permanently. A fourth host attempt failed its preflight check and never dispatched. Every reservation settled: 28.25661250 conservative credit equivalents, with no uncertain amount.

The fresh account snapshot after the stop reported `ordinaryUsageAllowed=true`, 100% displayed use, no reached-limit classification or spending restriction, and 1937.457633 existing credits. The percentage guard was a local operational rule, not an observed provider request rejection. The original no-resumption rule is superseded **only for provably never-dispatched cases in a new phase directory**. Historical files and source commits remain intact. This amendment follows the user's existing explicit authorization for thousands of Luna requests; it does not create a new allocation or depend on response quality.

## Residual allocation and immutable selection

The [offline certificate](../experiments/dependency_memory/results/transfer_continuation_plan.json) freshly audits both finalized prior launches and classifies dispatch evidence without selecting by answer quality. Exactly **648 cases** remain eligible for their first model submission. Keep the original worker assignment and relative case order. The three dispatched failures are ineligible and must not be replaced, even though no answer was retained. An ambiguous dispatch or unresolved reservation prevents certification.

| Worker | Prior dispatches | Remaining cases | Remaining conservative equivalents |
|---|---:|---:|---:|
| 0 | 226 | 158 | 42.77630375 |
| 1 | 222 | 162 | 42.97655500 |
| 2 | 225 | 159 | 42.83632875 |
| 3 | 215 | 169 | 43.15420000 |

The aggregate remains **1,536 model requests and 200 equivalents**, including every previous charge and uncertain reservation. This phase receives only the residual **171.74338750 equivalents**. It does not renew four 50-equivalent budgets. Preflight account reads are recorded host attempts, not model generations. No API billing, purchases, reset redemption, alternative account/model, repair requests, retries of dispatched cases, or held-out calls are included.

## Included allowance and existing credits

The September 19 [official pricing documentation](https://learn.chatgpt.com/docs/pricing) says available credits support continued eligible work after included limits. The pinned `0.155.0-alpha.9.2` client schema describes `ordinaryUsageAllowed` specifically as permission for ordinary **included** usage. Its credit snapshot reports availability and balance, but no explicit credit-backed admission flag. [App-server documentation](https://learn.chatgpt.com/docs/app-server) describes reached-limit classifications; neither percentages nor balance alone prove admission to the next generation.

The opt-in continuation policy uses the same reviewed subscription route and identity. It may attempt the next untouched scheduled case when included allowance remains eligible, or when fresh usable credit evidence supports normal credit-backed routing and no hard restriction is reported. A generic `rate_limit_reached` snapshot can be considered for the credit path only when consistent with included exhaustion. Explicit credit depletion, account or individual spending limits, unknown blocking classifications, unusable quota data, and actual provider request rejection stop dispatch. A positive balance never overrides such a restriction. A normal scheduled request is the admission attempt; no additional connection-probe generation is sent.

Save before/after quota snapshots and the selected quota mode. Keep the shared stop gate, one-generation guard, empty isolated request context, tool prohibition, usage validation, and conservative reservations. An actual turn-start or generation failure stops the phase, retains required uncertainty, and is never retried. Historical clients retain their default percentage-based behavior. No claim is made about inaccessible server internals or experiment-attributable account debit.

## Freeze, audit, and analysis

Before dispatch, freeze the [continuation runner](../experiments/dependency_memory/continue_transfer_study.py), optional quota policy, protocol, certificate generator, independent auditor, and tests in a local commit. The new launch plan fingerprints these files, embeds the original public plan and certificate, and rechecks all prior artifact hashes. Every worker manifest and initial denominator must exist before the first generation. Use a fresh output directory.

The certificate deliberately includes its preparer and prior-auditor implementation fingerprints. Reproducing it after those tools change may require checking out the recorded frozen commit; a mismatch with a newer auditor is not by itself evidence that historical responses changed.

The first continuation preparation at `cfa1ba9` exited before constructing any provider client or creating a run directory: it incorrectly required the raw offline wire audit's readiness flag, which is intentionally set only after the client verifies its binary, instructions, and audit evidence. The [zero-generation preparation record](../experiments/dependency_memory/results/transfer_continuation_preflight.json) is preserved. Correct the preparation check to require the proper public request contract, retain verified client readiness before execution, test both paths, and refreeze. This correction sends or replaces no model request and changes no scientific input.

Audit the new phase independently, then construct a separate pooled summary over the original 1,536 case IDs. Each actually dispatched case contributes its original outcome exactly once. A preflight-only failure remains visible in historical host-attempt accounting; its later first model outcome can fill that case's scientific row. Preserve source-phase attribution and all historical ledgers. Report cumulative tokens, charges, missingness, all 48 conditions, and the prespecified paired/block analyses. Three permanently missing responses remain visible; report whether they affect primary pairs or complete blocks. Do not count scored continuations as model trials.

This is an administrative change after one permitted descriptive checkpoint, not an unchanged single-launch study. Report the interruption and amendment with final findings. Shared worker, time, and backend dependence are not modeled by the descriptive block bootstrap. No native-compaction, downstream-agent performance, or generalization claim follows from this experiment.
