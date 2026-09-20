# Parent-retention transfer study

Controlled synthetic development study; no native-compaction or full-agent comparison.

Fake: **False**. Model requests: **0**. Scheduled: **1536**. Status counts: `{"incomplete": 1532, "transport_failure": 4}`.

## Prespecified primary comparison

Generic minus prospective guidance regret in fuller-workflow, unspecified-child, refresh-present cells. Positive values favor prospective guidance. The child reference is optimal for grading; its skill is not promised in these prompts.

Valid paired selections: 0/128. Complete blocks: 0/32.

Mean normalized regret benefit across valid pairs: **None**. Complete-block mean: **None**; its descriptive 95% block-bootstrap interval: **None**.

Raw availability-regret benefit by size: `{"12": null, "6": null}`. Mean valid-and-optimal benefit: `None`.

Regret uses valid pairs only; bootstrap uses fully valid blocks. Do not infer a clean treatment benefit when missingness differs.

## Complete factorial display

| Jobs | Framing/context | Later guarantee | Guidance | Refresh | Valid / planned | Optimal | Mean raw regret |
|---|---|---|---|---|---|---|---|
| 6 | compact | explicit_optimal | generic | first | 0/32 | 0 | None |
| 6 | compact | explicit_optimal | generic | last | 0/32 | 0 | None |
| 6 | compact | explicit_optimal | generic | none | 0/32 | 0 | None |
| 6 | compact | explicit_optimal | prospective | first | 0/32 | 0 | None |
| 6 | compact | explicit_optimal | prospective | last | 0/32 | 0 | None |
| 6 | compact | explicit_optimal | prospective | none | 0/32 | 0 | None |
| 6 | compact | unspecified | generic | first | 0/32 | 0 | None |
| 6 | compact | unspecified | generic | last | 0/32 | 0 | None |
| 6 | compact | unspecified | generic | none | 0/32 | 0 | None |
| 6 | compact | unspecified | prospective | first | 0/32 | 0 | None |
| 6 | compact | unspecified | prospective | last | 0/32 | 0 | None |
| 6 | compact | unspecified | prospective | none | 0/32 | 0 | None |
| 6 | workflow | explicit_optimal | generic | first | 0/32 | 0 | None |
| 6 | workflow | explicit_optimal | generic | last | 0/32 | 0 | None |
| 6 | workflow | explicit_optimal | generic | none | 0/32 | 0 | None |
| 6 | workflow | explicit_optimal | prospective | first | 0/32 | 0 | None |
| 6 | workflow | explicit_optimal | prospective | last | 0/32 | 0 | None |
| 6 | workflow | explicit_optimal | prospective | none | 0/32 | 0 | None |
| 6 | workflow | unspecified | generic | first | 0/32 | 0 | None |
| 6 | workflow | unspecified | generic | last | 0/32 | 0 | None |
| 6 | workflow | unspecified | generic | none | 0/32 | 0 | None |
| 6 | workflow | unspecified | prospective | first | 0/32 | 0 | None |
| 6 | workflow | unspecified | prospective | last | 0/32 | 0 | None |
| 6 | workflow | unspecified | prospective | none | 0/32 | 0 | None |
| 12 | compact | explicit_optimal | generic | first | 0/32 | 0 | None |
| 12 | compact | explicit_optimal | generic | last | 0/32 | 0 | None |
| 12 | compact | explicit_optimal | generic | none | 0/32 | 0 | None |
| 12 | compact | explicit_optimal | prospective | first | 0/32 | 0 | None |
| 12 | compact | explicit_optimal | prospective | last | 0/32 | 0 | None |
| 12 | compact | explicit_optimal | prospective | none | 0/32 | 0 | None |
| 12 | compact | unspecified | generic | first | 0/32 | 0 | None |
| 12 | compact | unspecified | generic | last | 0/32 | 0 | None |
| 12 | compact | unspecified | generic | none | 0/32 | 0 | None |
| 12 | compact | unspecified | prospective | first | 0/32 | 0 | None |
| 12 | compact | unspecified | prospective | last | 0/32 | 0 | None |
| 12 | compact | unspecified | prospective | none | 0/32 | 0 | None |
| 12 | workflow | explicit_optimal | generic | first | 0/32 | 0 | None |
| 12 | workflow | explicit_optimal | generic | last | 0/32 | 0 | None |
| 12 | workflow | explicit_optimal | generic | none | 0/32 | 0 | None |
| 12 | workflow | explicit_optimal | prospective | first | 0/32 | 0 | None |
| 12 | workflow | explicit_optimal | prospective | last | 0/32 | 0 | None |
| 12 | workflow | explicit_optimal | prospective | none | 0/32 | 0 | None |
| 12 | workflow | unspecified | generic | first | 0/32 | 0 | None |
| 12 | workflow | unspecified | generic | last | 0/32 | 0 | None |
| 12 | workflow | unspecified | generic | none | 0/32 | 0 | None |
| 12 | workflow | unspecified | prospective | first | 0/32 | 0 | None |
| 12 | workflow | unspecified | prospective | last | 0/32 | 0 | None |
| 12 | workflow | unspecified | prospective | none | 0/32 | 0 | None |

## Accounting

Reported usage totals: `{"cache_write_input_tokens": {"measured_attempts": 0, "reported": null}, "cached_input_tokens": {"measured_attempts": 0, "reported": null}, "input_tokens": {"measured_attempts": 0, "reported": null}, "output_tokens": {"measured_attempts": 0, "reported": null}, "reasoning_output_tokens": {"measured_attempts": 0, "reported": null}}`. Conservative credit-equivalent accounting: `{"cap_credit_equivalent": 200, "cap_credit_equivalent_exact": "200", "committed_credit_equivalent": 0.0, "committed_credit_equivalent_exact": "0", "remaining_credit_equivalent": 200.0, "remaining_credit_equivalent_exact": "200", "settled_credit_equivalent": 0.0, "settled_credit_equivalent_exact": "0", "uncertain_credit_reservations": 0.0, "uncertain_credit_reservations_exact": "0"}`. These token-derived equivalents are not an observed subscription debit.

No-refresh full pairs all tie. Larger n adds ranking/context load but reduces the maximum raw regret. Normalized regret divides by the full-pair range (4/15 at six jobs, 5/33 at twelve); underfilled answers can exceed one. The second boundary is nonbinding because child slots equal the candidate count. Intervals describe sampled-block variation, not natural-task generalization or an immutable model revision. All failures and incomplete cases remain recorded.

[Protocol](../../../../docs/TRANSFER_STUDY.md)
