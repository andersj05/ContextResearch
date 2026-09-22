# Prospective transfer to unseen workflow schemas

Six constructed evaluation traces, 18 paired terminal decisions. The casebook and protocol were frozen before implementation and model calls.

| Method | Failures / 18 | Calls charged | Model credits | Local credits | Total experimental credits | Eligible at prompt cost |
|---|---:|---:|---:|---:|---:|:---:|
| prompt | 2 | 30 | 0.4382190 | 0.00018313083 | 0.43840213083 | yes |
| checked | 2 | 30 | 0.4389930 | 0.00274214106 | 0.44173514106 | no |
| automatic | 1 | 18 | 0.1249000 | 0.00154885386 | 0.12644885386 | yes |
| direct | 2 | 18 | 0.1162340 | 0.00061366975 | 0.11684766975 | yes |
| indexed | 0 | 18 | 0.1159625 | 0.00077296631 | 0.11673546631 | yes |
| full | 1 | 18 | 0.2084235 | 0.00162392428 | 0.21004742428 | yes |

**Prespecified primary success:** met.

| Family | prompt | checked | automatic | direct | indexed | full |
|---|---:|---:|---:|---:|---:|---:|
| retry_queue | 0/6 | 0/6 | 0/6 | 2/6 | 0/6 | 0/6 |
| ci_promotion | 2/6 | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |
| data_pipeline | 0/6 | 2/6 | 1/6 | 0/6 | 0/6 | 1/6 |

## Scope and accounting

Actual calls: 126; token-derived planning credits: 1.2564565. The shared parent writer is one actual call per trace and is fully charged to both hypothetical prompt methods.
Local CPU and read-byte conversion rates are synthetic. Human authoring of the direct baseline and provider infrastructure are unmeasured. Actual subscription debit is not attributable to this experiment. These are constructed traces, not production incidents.

## Check verdicts

```json
{
  "proposed_parent_pass": 0,
  "proposed_child_pass": 2,
  "parent_fallbacks": 6,
  "child_fallbacks": 4,
  "automatic_infeasible": 0,
  "direct_infeasible": 0,
  "checked_infeasible": 0,
  "prompt_parent_clipped": 0,
  "prompt_child_clipped": 3,
  "checked_child_clipped": 0
}
```
