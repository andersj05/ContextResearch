# Schema-derived checks on frozen tool-result traces

Six constructed evaluation traces across retry, CI handoff, and multi-stage data jobs; 12 paired terminal cases. This is a finite transfer test, not production evidence.

| Method | Failures / 12 | Model calls | Model credits | Local credits | Total experimental credits |
|---|---:|---:|---:|---:|---:|
| prompt | 0 | 24 | 0.2537065 | 0E-8 | 0.25370650 |
| automatic | 0 | 12 | 0.0725445 | 0.00058046 | 0.07312496 |
| direct | 0 | 12 | 0.0667650 | 0.00024514 | 0.06701014 |
| indexed | 0 | 12 | 0.0628880 | 0.00010760 | 0.06299560 |
| full | 0 | 12 | 0.0951865 | 0.00043100 | 0.09561750 |

**Prespecified primary success:** not met.
**Parity with hand-written direct records:** met.

Local CPU and byte prices are declared experimental conversion rates, not provider charges. The direct control excludes human schema-authoring cost. The prompt and all final decisions are fully charged. Stored response/usage records and case hashes support independent replay. No provider session history or evaluator files entered the model calls.

## Family outcomes

| Family | prompt | automatic | direct | indexed | full |
|---|---:|---:|---:|---:|---:|
| retry | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| ci_handoff | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| data_job | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |

Break-even local CPU price versus prompting, with the declared byte price: None credits/second.
