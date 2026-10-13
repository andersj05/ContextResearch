# Conservative paired-test completion bounds

Offline statistical support for a prospectively specified rollback comparison.
Read the [argument and verification](../results/rollback_missingness_bound_2026-10-09/README.md).
This package makes no model calls and does not rewrite existing study analyses.

```powershell
python -m unittest experiments.dependency_memory.rollback_missingness_bound.test_rollback_missingness -v
```

`rollback_missingness.analyze` accepts `(R, K)` binary scores with `None` for
unknowns. It returns the maximum exact paired-test p-value over all feasible
completions and sharp empirical missingness bounds. Those bounds are not
population confidence intervals. Applying the method to model observations
requires a source-bound analysis plan before the confirmatory allocation.
