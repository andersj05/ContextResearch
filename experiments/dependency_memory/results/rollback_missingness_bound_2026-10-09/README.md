# Conservative paired-test inference with missing outcomes

October 9, 2026. This is an elementary statistical completion argument and an
offline implementation check, prepared before any v6 R-arm observations. It is not
a measured rollback effect, a new statistical method, or permission to revise
a completed study. No model calls are made by this analysis.

The current v6 report suppresses its confirmatory p-value when any selected
outcome is missing. Retain that report. For a future confirmation, a separately
frozen analysis amendment can instead require the paired-test conclusion to
hold for every binary completion of the missing outcomes. This can never make
the ordinary complete-case p-value smaller. A result that depends on filling a
gap favorably cannot pass. The amendment must be bound before any R/K dispatch;
the present preparation alone does not reclassify any old analysis.

## Exact completion bound

Let `a` be known R-only successes and `b` known K-only successes. A partially
observed pair can be concordant or add one discordance in exactly one direction:

| Observed (R, K) | Possible contribution to R minus K |
|---|---|
| (1, missing) or (missing, 0) | 0 or +1; count these pairs as P |
| (0, missing) or (missing, 1) | -1 or 0; count these pairs as Q |
| (missing, missing) | -1, 0 or +1; count these pairs as U |

With N fixed selected pairs, the sharp missingness bounds on the empirical
success-rate difference are `(a-b-Q-U)/N` and `(a-b+P+U)/N`. These are not
population confidence intervals. No observed score is replaced or imputed.

For complete discordance counts x,y, the two-sided exact McNemar/binomial p-value
is `min(1, 2 * sum(comb(x+y,j), j=0..min(x,y)) / 2**(x+y))`.
The implementation retains an exact rational value for the decision at alpha
1/20 and a floating display value.

If a >= b, the largest possible p-value is obtained with discordances
`(a, b + min(a-b, Q+U))`. If a < b, use
`(a + min(b-a, P+U), b)`. Unknown pairs favoring the current majority may instead
be concordant. Adding a majority discordance cannot increase the two-sided tail
probability while the majority stays on that side; adding a minority discordance
increases it until balance, where the clipped p-value is one. Thus the displayed
completion achieves the maximum over every feasible missing-score assignment.

Let p_true denote the valid complete-data p-value for whichever completion is
the true one. Pointwise, p_max >= p_true. Therefore rejection when p_max <= alpha
is a subset of rejection when p_true <= alpha, and has type-I error at most alpha
whenever the underlying complete-data exact paired test is valid. This reasoning
allows arbitrary outcome-dependent missingness. It does not repair dependence
between task pairs, invalid randomization, information-access violations or an
incorrect complete-data null model.

## Implementation and limits

The [implementation](../../rollback_missingness_bound/rollback_missingness.py) computes the bound without
enumerating large samples. The [tests](../../rollback_missingness_bound/test_rollback_missingness.py)
compare complete data with the existing exact test, check direction symmetry,
invalid input, all-missing samples, and a single unknown that can either preserve
or remove significance. Independent enumeration checks all observed patterns
through four pairs in the unit tests; a separate saved check extends to five.
This finite check supports implementation correctness; the argument above gives
the general statement. All unknown requests remain recorded and are never retried.

The previous 260-pair power calculation assumes complete observation. The robust
missing-outcome decision is more conservative and may have lower power; no 80%
power claim is made under arbitrary missingness. A larger p-value cannot justify
an outcome-dependent sample extension. A future fixed sample and this decision
rule must be specified before the first confirmatory R/K dispatch.

The [saved exhaustive check](verification_v3.json) covers 66,430 observed patterns
and 1,118,481 complete assignments, with zero mismatches. All [five unit tests](tests.txt)
pass. The [source snapshot](source_snapshot_v3.zip) binds the implementation, tests,
package and this proof note. Earlier snapshots/checks are retained from before
documentation links and package placement were corrected; the mathematical
implementation is unchanged.

An initial repository-wide check exposed four historical diagnostic fingerprint
mismatches because those old plans enumerate every root-level Python file.
The new helper now lives in its own package. The affected checks pass unchanged
after relocation; no historical plan, audit, model response or score was rewritten.
The [failed checkpoint](repository_validation_before_packaging_fix.txt) and
[targeted repair verification](packaging_recheck.json) preserve that history.
