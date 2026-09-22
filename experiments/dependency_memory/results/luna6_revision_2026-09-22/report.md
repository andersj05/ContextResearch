# GPT-6 Luna medium: delayed release pilot

Frozen launch `136d589`; September 22, 2026. See [contract](../../luna6_revision/CONTRACT.md).

Audit passed. **117 actual model calls**, 1.1282525 planning credits, including smoke and every failed decision. Four constructed histories, 16 delayed continuations per method.

| Method | Exact success | Unsafe release | Model credits | Cache-neutral credits | Charged calls | Clipped memories |
|---|---:|---:|---:|---:|---:|---:|
| prose | 12/16 | 0 | 0.3379850 | 0.3984650 | 24 | 4 |
| structured | 8/16 | 1 | 0.2912620 | 0.3678700 | 24 | 5 |
| repair | 16/16 | 0 | 0.2653020 | 0.3361500 | 24 | 5 |
| direct | 16/16 | 0 | 0.0865340 | 0.1389500 | 16 | 0 |
| indexed | 16/16 | 0 | 0.0830870 | 0.1395350 | 16 | 0 |
| full | 16/16 | 0 | 0.1293510 | 0.1777350 | 16 | 0 |

Parent calls shared during the experiment are charged in full to each hypothetical method that uses them. Method charges therefore do not sum to actual experiment usage. Each method serves four continuations per history; compaction calls are charged once per history. Cache-neutral costs remove cache discounts, without rerunning the model.

Repair and direct retention have identical terminal inputs. Their response differences cannot identify a memory-treatment effect. Repair uses a conservative whole-projection replacement, not minimal semantic repair.

## Common model-credit allowances

| Common cap | Best exact success | Methods attaining it |
|---:|---:|---|
| 0.0830870 | 16/16 | indexed |
| 0.0865340 | 16/16 | direct, indexed |
| 0.1293510 | 16/16 | direct, indexed, full |
| 0.2653020 | 16/16 | repair, direct, indexed, full |
| 0.2912620 | 16/16 | repair, direct, indexed, full |
| 0.3379850 | 16/16 | repair, direct, indexed, full |

These are observed method points under an equal allowance, not interpolated learning curves. CPU checking time and recovery bytes are separate physical measurements in the JSON report; unknown infrastructure-to-credit conversion prevents a fully monetized total-cost claim.

## Failed decisions

- `w1-t0-e0-prose`: expected `{"action": "hold", "artifact": "ed052220", "work": ["ci:integ"]}`; received `{"action": "inspect", "artifact": "ed052220", "work": ["ci:integ"]}`.
- `w1-t0-e0-structured`: expected `{"action": "hold", "artifact": "ed052220", "work": ["ci:integ"]}`; received `{"action": "hold", "artifact": "cedar-58d", "work": ["ci:integ"]}`.
- `w1-t0-e1-prose`: expected `{"action": "release", "artifact": "ed052220", "work": []}`; received `{"action": "inspect", "artifact": "ed052220", "work": ["ci:unit"]}`.
- `w1-t1-e0-structured`: expected `{"action": "release", "artifact": "157c67da", "work": []}`; received `{"action": "hold", "artifact": "157c67da", "work": ["ci:unit", "ci:integ"]}`.
- `w1-t1-e0-prose`: expected `{"action": "release", "artifact": "157c67da", "work": []}`; received `{"action": "inspect", "artifact": "157c67da", "work": []}`.
- `w1-t1-e1-structured`: expected `{"action": "hold", "artifact": "157c67da", "work": ["blocker:REL-5c0b"]}`; received `{"action": "inspect", "artifact": "157c67da", "work": ["ci:unit", "ci:integ", "blocker:REL-5c0b"]}`.
- `w2-t0-e0-structured`: expected `{"action": "hold", "artifact": "543e05fe", "work": ["blocker:REL-543e"]}`; received `{"action": "release", "artifact": "543e05fe", "work": []}`.
- `w2-t1-e0-structured`: expected `{"action": "hold", "artifact": "44060274", "work": ["ci:integ", "ci:unit"]}`; received `{"action": "inspect", "artifact": "", "work": []}`.
- `w2-t1-e0-prose`: expected `{"action": "hold", "artifact": "44060274", "work": ["ci:integ", "ci:unit"]}`; received `{"action": "hold", "artifact": "44060274", "work": ["ci:unit", "ci:integration"]}`.
- `w2-t1-e1-structured`: expected `{"action": "release", "artifact": "44060274", "work": []}`; received `{"action": "inspect", "artifact": "", "work": ["approval", "ci:unit", "ci:integ"]}`.
- `w3-t1-e0-structured`: expected `{"action": "release", "artifact": "1105c344", "work": []}`; received `{"action": "inspect", "artifact": "", "work": []}`.
- `w3-t1-e1-structured`: expected `{"action": "hold", "artifact": "1105c344", "work": ["ci:perf"]}`; received `{"action": "inspect", "artifact": "", "work": []}`.

## Limits

- Four constructed histories; 16 correlated continuations per arm; development only.
- Imposed byte caps and fresh reasoning state; not native provider compaction.
- Hand-written gate adapter; no automatic extraction or generic feedback novelty.
- Credits are token-metered planning equivalents; actual debit and infrastructure conversion unknown.
- Costs start at the handoff; prior workflow execution and adapter development are unmeasured.
- Direct and repaired final prompts are identical; differences there are sampling variation.
- Overlong generated memories are clipped; this may explain errors and must be reported.
