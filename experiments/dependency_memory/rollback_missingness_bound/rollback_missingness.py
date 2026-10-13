"""Conservative exact paired-test bounds over all completions of missing scores.

Pairs are (R, K), each score 0, 1 or None. This is an elementary completion
bound on the existing two-sided McNemar test, not a new missing-data model.
It makes no assumption about which outcomes go missing. Its error guarantee
still requires the usual complete-data paired test to be valid.
"""
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb


@lru_cache(maxsize=None, typed=True)
def exact_p(r_only, k_only):
    if any(type(x) is not int or x < 0 for x in (r_only, k_only)):
        raise ValueError("nonnegative integer discordance counts required")
    n = r_only + k_only
    denominator = 2 ** n
    numerator = min(denominator, 2 * sum(comb(n, j) for j in range(min(r_only, k_only) + 1)))
    return Fraction(numerator, denominator)


def analyze(pairs, alpha=Fraction(1, 20)):
    pairs = list(pairs)
    alpha = Fraction(alpha)
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between zero and one")
    a = b = plus = minus = both_missing = known = 0
    for pair in pairs:
        if len(pair) != 2 or any(x is not None and (type(x) is not int or x not in (0, 1)) for x in pair):
            raise ValueError("pairs must contain R/K scores 0, 1 or None")
        r, k = pair
        if r is None and k is None:
            both_missing += 1
        elif r is None:
            if k == 0: plus += 1
            else: minus += 1
        elif k is None:
            if r == 1: plus += 1
            else: minus += 1
        else:
            known += 1
            a += r == 1 and k == 0
            b += r == 0 and k == 1
    # Unknown pairs favoring the current majority can be concordant instead.
    # Add opposite discordances until balance, or exhaust their feasible count.
    worst_a, worst_b = a, b
    if a >= b: worst_b += min(a - b, minus + both_missing)
    else: worst_a += min(b - a, plus + both_missing)
    p = exact_p(worst_a, worst_b)
    lo, hi = a - b - minus - both_missing, a - b + plus + both_missing
    return {
        "pairs": len(pairs), "known_complete_pairs": known,
        "known_R_only": a, "known_K_only": b,
        "missing_may_add_R_only": plus, "missing_may_add_K_only": minus,
        "both_missing": both_missing,
        "effect_bounds_numerators": [lo, hi], "effect_denominator": len(pairs),
        "effect_missingness_bounds": [lo / len(pairs), hi / len(pairs)] if pairs else None,
        "known_complete_case_p": float(exact_p(a, b)),
        "worst_case_completion_counts": {"R_only": worst_a, "K_only": worst_b},
        "worst_case_completion_p": float(p),
        "worst_case_p_fraction": {"numerator": p.numerator, "denominator": p.denominator},
        "alpha_fraction": {"numerator": alpha.numerator, "denominator": alpha.denominator},
        "reject_for_every_completion": bool(pairs) and p <= alpha,
        "direction_if_rejected": ("R_higher" if lo > 0 else "R_lower") if pairs and p <= alpha else None,
        "scope": "Missingness bounds are not population confidence intervals. No missing score is imputed."
    }


def verify_small(max_pairs=5):
    """Independently enumerate every completion of all observed patterns."""
    if type(max_pairs) is not int or not 0 <= max_pairs <= 5:
        raise ValueError("bounded exhaustive check accepts zero through five pairs")
    patterns = completions = 0
    observations = list(product((0, 1, None), repeat=2))
    for n in range(max_pairs + 1):
        for observed in product(observations, repeat=n):
            result = analyze(observed)
            choices = [list(product((0, 1) if r is None else (r,),
                                    (0, 1) if k is None else (k,))) for r, k in observed]
            maximum = Fraction(0); minimum_effect = n; maximum_effect = -n
            for full in product(*choices):
                wins = sum(r > k for r, k in full)
                losses = sum(r < k for r, k in full)
                maximum = max(maximum, exact_p(wins, losses))
                minimum_effect = min(minimum_effect, wins - losses)
                maximum_effect = max(maximum_effect, wins - losses)
                completions += 1
            assert Fraction(**result["worst_case_p_fraction"]) == maximum
            assert result["effect_bounds_numerators"] == [minimum_effect, maximum_effect]
            patterns += 1
    return {"all_passed": True, "evidence_kind": "finite_exhaustive_missingness_completion_check",
            "maximum_pairs": max_pairs, "observed_patterns": patterns,
            "complete_assignments": completions, "model_calls": 0,
            "scope": "Finite implementation check; general validity follows from the separate completion argument."}
