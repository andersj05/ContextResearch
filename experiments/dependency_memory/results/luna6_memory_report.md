# Live GPT-6 Luna memory benchmark

**141 fresh calls at medium reasoning; 1.3190825 planning credits; both evidence audits pass.**

Four constructed release handoffs pass through 900-byte and 440-byte memory limits. Each method faces sixteen delayed decisions. These reuse four histories and are not independent production incidents.

| Method | Exact decisions | Unsafe release | Model credits | Cache-neutral credits | Clipped memories | Phase |
|---|---:|---:|---:|---:|---:|---|
| prose | 12/16 | 0 | 0.3379850 | 0.3984650 | 4 | fixed pilot |
| structured | 8/16 | 1 | 0.2912620 | 0.3678700 | 5 | fixed pilot |
| data_first | 12/16 | 0 | 0.1908300 | 0.2714700 | 0 | post-pilot development |
| repair | 16/16 | 0 | 0.2653020 | 0.3361500 | 5 | fixed pilot |
| direct | 16/16 | 0 | 0.0865340 | 0.1389500 | 0 | fixed pilot |
| indexed | 16/16 | 0 | 0.0830870 | 0.1395350 | 0 | fixed pilot |
| full | 16/16 | 0 | 0.1293510 | 0.1777350 | 0 | fixed pilot |

All memory-writing and execution calls count. The main pilot shares four parent calls, charging their full cost to each method that uses them. Cache-neutral figures remove discounts arithmetically. Actual subscription debit is not attributable, and infrastructure and adapter-development costs are unmeasured.

## What failed

- The original structured child cut off `REL-543e`, an open blocker for `delta-e58`, at its byte limit. The later model incorrectly chose release after an irrelevant note update.
- A separately frozen data-first prompt announced that public rules would be repeated. It eliminated clipping but retained only 12/16 correct decisions.
- In that unclipped follow-up, `atlas-99c` became `atlas-99`, and `ember-0c4` became `ember-0c`. Another child dropped the current artifact and treated the approval identifier as the reference for stale CI. Exact identifiers and semantic field roles were damaged even with unused memory capacity.

## What repaired it, and at what cost

A checked projection retains the executable gate's fields in 769 bytes at the first boundary and 311–321 bytes at the second. It gets 16/16 correct decisions and costs 8.9% less than the original structured pipeline, including proposal calls; the saving is 8.6% without cache discounts.

The stronger data-first prompt is cheaper than that repair loop, but gets 12/16. Directly serializing the same checked fields gets 16/16 for much less than either. Indexed recovery and full-history access also get 16/16. Repair and direct terminal prompts are identical. This supports direct retention for this known gate; it does not establish a superior general feedback method.

Repeated local CPU measurements give 0.1875 ms for direct serialization and 0.5 ms for checked replacement across all four histories. The live per-check timer resolved zero, so those zeros must not be interpreted as free computation. Indexed recovery transfers 12,404 bytes. The direct/indexed ranking changes when cache discounts are removed.

An automatic projection extractor would have only 0.0428170 observed credits, or 0.0387850 cache-neutral credits, of extra budget across this four-history workload before direct retention loses its measured advantage over full-history access. No such extractor was run.

## Interpretation and reproducibility

The main schedule was frozen in `136d589`. The 24-call prompt follow-up was frozen in `8d8a358` after observing the first results; it is development evidence on reused fixtures. The prototype uses a manually specified gate adapter, not automatic semantic verification. Native compaction, production-total-cost savings, held-out transfer and publication novelty remain open.

- [Detailed findings](../../../research/LUNA6_DELAYED_FAILURES_2026-09-22.md)
- [Main contract](../luna6_revision/CONTRACT.md) and [main run](luna6_revision_2026-09-22/report.md)
- [Follow-up contract](../../../docs/LUNA6_DATA_FIRST_FOLLOWUP.md) and [saved follow-up](luna6_data_first_2026-09-22/analysis.json)
- [Prior-art comparison](../../../research/LUNA6_SCOPE_PRIOR_ART_2026-09-22.md)

Offline reproduction: `python scripts/summarize_luna6_studies.py`, then `python scripts/validate_context_repo.py`. Never run a launch script as a repository check.
