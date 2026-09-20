# Parent-retention transfer study

Controlled synthetic development study; no native-compaction or full-agent comparison.

Fake: **False**. Model requests: **1536**. Scheduled: **1536**. Status counts: `{"completed": 1533, "transport_failure": 3}`.

## Prespecified primary comparison

Generic minus prospective guidance regret in fuller-workflow, unspecified-child, refresh-present cells. Positive values favor prospective guidance. The child reference is optimal for grading; its skill is not promised in these prompts.

Valid paired selections: 128/128. Complete blocks: 32/32.

Mean normalized regret benefit across valid pairs: **107/5120**. Complete-block mean: **107/5120**; its descriptive 95% block-bootstrap interval: **[-0.0203125, 0.060546875]**.

Raw availability-regret benefit by size: `{"12": "71/8448", "6": "-7/1920"}`. Mean valid-and-optimal benefit: `1/32`.

Regret uses valid pairs only; bootstrap uses fully valid blocks. Do not infer a clean treatment benefit when missingness differs.

## Complete factorial display

| Jobs | Framing/context | Later guarantee | Guidance | Refresh | Valid / planned | Optimal | Mean raw regret |
|---|---|---|---|---|---|---|---|
| 6 | compact | explicit_optimal | generic | first | 31/32 | 27 | 11/465 |
| 6 | compact | explicit_optimal | generic | last | 32/32 | 28 | 7/320 |
| 6 | compact | explicit_optimal | generic | none | 32/32 | 32 | 0 |
| 6 | compact | explicit_optimal | prospective | first | 32/32 | 28 | 11/480 |
| 6 | compact | explicit_optimal | prospective | last | 32/32 | 30 | 3/320 |
| 6 | compact | explicit_optimal | prospective | none | 32/32 | 32 | 0 |
| 6 | compact | unspecified | generic | first | 32/32 | 27 | 1/64 |
| 6 | compact | unspecified | generic | last | 32/32 | 27 | 1/40 |
| 6 | compact | unspecified | generic | none | 31/32 | 31 | 0 |
| 6 | compact | unspecified | prospective | first | 32/32 | 30 | 1/320 |
| 6 | compact | unspecified | prospective | last | 32/32 | 30 | 1/120 |
| 6 | compact | unspecified | prospective | none | 32/32 | 32 | 0 |
| 6 | workflow | explicit_optimal | generic | first | 32/32 | 29 | 1/96 |
| 6 | workflow | explicit_optimal | generic | last | 32/32 | 29 | 1/64 |
| 6 | workflow | explicit_optimal | generic | none | 32/32 | 32 | 0 |
| 6 | workflow | explicit_optimal | prospective | first | 31/32 | 29 | 1/93 |
| 6 | workflow | explicit_optimal | prospective | last | 32/32 | 30 | 1/96 |
| 6 | workflow | explicit_optimal | prospective | none | 32/32 | 32 | 0 |
| 6 | workflow | unspecified | generic | first | 32/32 | 28 | 1/80 |
| 6 | workflow | unspecified | generic | last | 32/32 | 29 | 17/960 |
| 6 | workflow | unspecified | generic | none | 32/32 | 32 | 0 |
| 6 | workflow | unspecified | prospective | first | 32/32 | 30 | 1/96 |
| 6 | workflow | unspecified | prospective | last | 32/32 | 28 | 13/480 |
| 6 | workflow | unspecified | prospective | none | 32/32 | 32 | 0 |
| 12 | compact | explicit_optimal | generic | first | 32/32 | 31 | 1/4224 |
| 12 | compact | explicit_optimal | generic | last | 32/32 | 24 | 37/1408 |
| 12 | compact | explicit_optimal | generic | none | 32/32 | 32 | 0 |
| 12 | compact | explicit_optimal | prospective | first | 32/32 | 28 | 41/4224 |
| 12 | compact | explicit_optimal | prospective | last | 32/32 | 27 | 49/2112 |
| 12 | compact | explicit_optimal | prospective | none | 32/32 | 32 | 0 |
| 12 | compact | unspecified | generic | first | 32/32 | 27 | 1/132 |
| 12 | compact | unspecified | generic | last | 32/32 | 30 | 7/1056 |
| 12 | compact | unspecified | generic | none | 32/32 | 31 | 1/192 |
| 12 | compact | unspecified | prospective | first | 32/32 | 28 | 17/4224 |
| 12 | compact | unspecified | prospective | last | 32/32 | 28 | 5/264 |
| 12 | compact | unspecified | prospective | none | 32/32 | 32 | 0 |
| 12 | workflow | explicit_optimal | generic | first | 32/32 | 29 | 31/4224 |
| 12 | workflow | explicit_optimal | generic | last | 32/32 | 26 | 5/176 |
| 12 | workflow | explicit_optimal | generic | none | 32/32 | 32 | 0 |
| 12 | workflow | explicit_optimal | prospective | first | 32/32 | 28 | 1/192 |
| 12 | workflow | explicit_optimal | prospective | last | 32/32 | 30 | 5/528 |
| 12 | workflow | explicit_optimal | prospective | none | 32/32 | 32 | 0 |
| 12 | workflow | unspecified | generic | first | 32/32 | 29 | 1/132 |
| 12 | workflow | unspecified | generic | last | 32/32 | 28 | 25/1408 |
| 12 | workflow | unspecified | generic | none | 32/32 | 32 | 0 |
| 12 | workflow | unspecified | prospective | first | 32/32 | 31 | 1/1056 |
| 12 | workflow | unspecified | prospective | last | 32/32 | 29 | 1/132 |
| 12 | workflow | unspecified | prospective | none | 32/32 | 32 | 0 |

## Accounting

Reported usage totals: `{"cache_write_input_tokens": {"measured_attempts": 1536, "reported": 0}, "cached_input_tokens": {"measured_attempts": 1536, "reported": 2412032}, "input_tokens": {"measured_attempts": 1536, "reported": 4768512}, "output_tokens": {"measured_attempts": 1536, "reported": 632736}, "reasoning_output_tokens": {"measured_attempts": 1536, "reported": 595880}}`. Conservative credit-equivalent accounting: `{"cap_credit_equivalent": 200.0, "cap_credit_equivalent_exact": "200", "committed_credit_equivalent": 48.78528, "committed_credit_equivalent_exact": "48.78528000", "remaining_credit_equivalent": 151.21472, "remaining_credit_equivalent_exact": "151.21472000", "settled_credit_equivalent": 48.78528, "settled_credit_equivalent_exact": "48.78528000", "uncertain_credit_reservations": 0.0, "uncertain_credit_reservations_exact": "0"}`. These token-derived equivalents are not an observed subscription debit.

No-refresh full pairs all tie. Larger n adds ranking/context load but reduces the maximum raw regret. Normalized regret divides by the full-pair range (4/15 at six jobs, 5/33 at twelve); underfilled answers can exceed one. The second boundary is nonbinding because child slots equal the candidate count. Intervals describe sampled-block variation, not natural-task generalization or an immutable model revision. All failures and incomplete cases remain recorded.

[Protocol](../../../../docs/TRANSFER_STUDY.md)
