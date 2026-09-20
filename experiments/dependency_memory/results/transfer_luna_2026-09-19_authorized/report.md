# Parent-retention transfer study

Controlled synthetic development study; no native-compaction or full-agent comparison.

Fake: **False**. Model requests: **888**. Scheduled: **1536**. Status counts: `{"completed": 885, "incomplete": 647, "transport_failure": 4}`.

## Prespecified primary comparison

Generic minus prospective guidance regret in fuller-workflow, unspecified-child, refresh-present cells. Positive values favor prospective guidance. The child reference is optimal for grading; its skill is not promised in these prompts.

Valid paired selections: 70/128. Complete blocks: 16/32.

Mean normalized regret benefit across valid pairs: **0**. Complete-block mean: **0**; its descriptive 95% block-bootstrap interval: **[-0.06796875, 0.069140625]**.

Raw availability-regret benefit by size: `{"12": "25/4356", "6": "-1/111"}`. Mean valid-and-optimal benefit: `1/70`.

Regret uses valid pairs only; bootstrap uses fully valid blocks. Do not infer a clean treatment benefit when missingness differs.

## Complete factorial display

| Jobs | Framing/context | Later guarantee | Guidance | Refresh | Valid / planned | Optimal | Mean raw regret |
|---|---|---|---|---|---|---|---|
| 6 | compact | explicit_optimal | generic | first | 18/32 | 17 | 1/180 |
| 6 | compact | explicit_optimal | generic | last | 18/32 | 17 | 7/540 |
| 6 | compact | explicit_optimal | generic | none | 18/32 | 18 | 0 |
| 6 | compact | explicit_optimal | prospective | first | 18/32 | 17 | 1/270 |
| 6 | compact | explicit_optimal | prospective | last | 18/32 | 17 | 1/540 |
| 6 | compact | explicit_optimal | prospective | none | 18/32 | 18 | 0 |
| 6 | compact | unspecified | generic | first | 19/32 | 14 | 1/38 |
| 6 | compact | unspecified | generic | last | 20/32 | 15 | 1/25 |
| 6 | compact | unspecified | generic | none | 17/32 | 17 | 0 |
| 6 | compact | unspecified | prospective | first | 19/32 | 17 | 1/190 |
| 6 | compact | unspecified | prospective | last | 19/32 | 18 | 1/285 |
| 6 | compact | unspecified | prospective | none | 20/32 | 20 | 0 |
| 6 | workflow | explicit_optimal | generic | first | 19/32 | 18 | 4/285 |
| 6 | workflow | explicit_optimal | generic | last | 19/32 | 17 | 11/570 |
| 6 | workflow | explicit_optimal | generic | none | 19/32 | 19 | 0 |
| 6 | workflow | explicit_optimal | prospective | first | 19/32 | 18 | 1/190 |
| 6 | workflow | explicit_optimal | prospective | last | 18/32 | 18 | 0 |
| 6 | workflow | explicit_optimal | prospective | none | 17/32 | 17 | 0 |
| 6 | workflow | unspecified | generic | first | 20/32 | 16 | 1/50 |
| 6 | workflow | unspecified | generic | last | 18/32 | 16 | 1/60 |
| 6 | workflow | unspecified | generic | none | 18/32 | 18 | 0 |
| 6 | workflow | unspecified | prospective | first | 19/32 | 17 | 1/57 |
| 6 | workflow | unspecified | prospective | last | 20/32 | 17 | 3/100 |
| 6 | workflow | unspecified | prospective | none | 20/32 | 20 | 0 |
| 12 | compact | explicit_optimal | generic | first | 17/32 | 17 | 0 |
| 12 | compact | explicit_optimal | generic | last | 19/32 | 13 | 20/627 |
| 12 | compact | explicit_optimal | generic | none | 18/32 | 18 | 0 |
| 12 | compact | explicit_optimal | prospective | first | 18/32 | 16 | 1/198 |
| 12 | compact | explicit_optimal | prospective | last | 19/32 | 16 | 29/1254 |
| 12 | compact | explicit_optimal | prospective | none | 18/32 | 18 | 0 |
| 12 | compact | unspecified | generic | first | 18/32 | 14 | 5/792 |
| 12 | compact | unspecified | generic | last | 17/32 | 16 | 1/187 |
| 12 | compact | unspecified | generic | none | 19/32 | 19 | 0 |
| 12 | compact | unspecified | prospective | first | 18/32 | 16 | 1/792 |
| 12 | compact | unspecified | prospective | last | 18/32 | 17 | 5/594 |
| 12 | compact | unspecified | prospective | none | 17/32 | 17 | 0 |
| 12 | workflow | explicit_optimal | generic | first | 18/32 | 16 | 7/1188 |
| 12 | workflow | explicit_optimal | generic | last | 18/32 | 15 | 5/198 |
| 12 | workflow | explicit_optimal | generic | none | 19/32 | 19 | 0 |
| 12 | workflow | explicit_optimal | prospective | first | 17/32 | 15 | 1/132 |
| 12 | workflow | explicit_optimal | prospective | last | 20/32 | 19 | 1/132 |
| 12 | workflow | explicit_optimal | prospective | none | 20/32 | 20 | 0 |
| 12 | workflow | unspecified | generic | first | 18/32 | 17 | 1/1188 |
| 12 | workflow | unspecified | generic | last | 16/32 | 13 | 5/192 |
| 12 | workflow | unspecified | generic | none | 20/32 | 20 | 0 |
| 12 | workflow | unspecified | prospective | first | 18/32 | 18 | 0 |
| 12 | workflow | unspecified | prospective | last | 18/32 | 15 | 4/297 |
| 12 | workflow | unspecified | prospective | none | 19/32 | 19 | 0 |

## Accounting

Reported usage totals: `{"cache_write_input_tokens": {"measured_attempts": 888, "reported": 0}, "cached_input_tokens": {"measured_attempts": 888, "reported": 1317120}, "input_tokens": {"measured_attempts": 888, "reported": 2754970}, "output_tokens": {"measured_attempts": 888, "reported": 367935}, "reasoning_output_tokens": {"measured_attempts": 888, "reported": 346623}}`. Conservative credit-equivalent accounting: `{"cap_credit_equivalent": 200, "cap_credit_equivalent_exact": "200", "committed_credit_equivalent": 28.2566125, "committed_credit_equivalent_exact": "28.25661250", "remaining_credit_equivalent": 171.7433875, "remaining_credit_equivalent_exact": "171.74338750", "settled_credit_equivalent": 28.2566125, "settled_credit_equivalent_exact": "28.25661250", "uncertain_credit_reservations": 0.0, "uncertain_credit_reservations_exact": "0"}`. These token-derived equivalents are not an observed subscription debit.

No-refresh full pairs all tie. Larger n adds ranking/context load but reduces the maximum raw regret. Normalized regret divides by the full-pair range (4/15 at six jobs, 5/33 at twelve); underfilled answers can exceed one. The second boundary is nonbinding because child slots equal the candidate count. Intervals describe sampled-block variation, not natural-task generalization or an immutable model revision. All failures and incomplete cases remain recorded.

[Protocol](../../../../docs/TRANSFER_STUDY.md)
