"""Standard exact paired binary tests and prespecified power, using the stdlib.

No sample-size extension is allowed in response to observed treatment effects.
All power values are conditional on the supplied discordance/effect assumptions.
"""
from functools import lru_cache
import math


def binomial(n, p):
    if type(n) is not int or n < 0 or not 0 <= p <= 1: raise ValueError("invalid binomial")
    if p in (0, 1): return [float(k == int(n*p)) for k in range(n+1)]
    return [math.exp(math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)+k*math.log(p)+(n-k)*math.log1p(-p)) for k in range(n+1)]


@lru_cache(maxsize=4096)
def critical(m, alpha=.05):
    # Rejection for b<=c or b>=m-c under Bin(m, 1/2).
    total = 0.; c = -1
    for k, probability in enumerate(binomial(m, .5)):
        if k > m//2: break
        total += probability
        if 2*total <= alpha + 1e-14: c = k
        else: break
    return c


def mcnemar(wins, losses):
    if any(type(x) is not int or x < 0 for x in (wins, losses)): raise ValueError("invalid discordances")
    m = wins + losses
    return min(1., 2*sum(binomial(m, .5)[:min(wins, losses)+1]))


def power(n, delta=.10, discordance=.30, alpha=.05):
    if not 0 < abs(delta) <= discordance <= 1 or not 0 < alpha < 1: raise ValueError("infeasible paired alternative")
    result = 0.
    for m, pm in enumerate(binomial(n, discordance)):
        c = critical(m, alpha)
        if c < 0 or pm < 1e-14: continue
        b = binomial(m, (1+delta/discordance)/2)
        result += pm * (sum(b[:c+1]) + sum(b[m-c:]))
    return min(1., result)


def plan(delta=.10, discordance=.30, target=.80, alpha=.05, maximum=2000, increment=20):
    if not 0 < target < 1 or maximum < increment or increment < 1: raise ValueError("invalid planning range")
    for n in range(increment, maximum+1, increment):
        p = power(n, delta, discordance, alpha)
        if p >= target:
            return {"pairs": n, "power": p, "delta": delta, "discordance": discordance,
                    "alpha": alpha, "target_power": target, "grid_increment": increment,
                    "method": "exact unconditional power of two-sided conditional McNemar test",
                    "scope": "independent task pairs; assumed discordance and effect, not empirical assurance"}
    return {"pairs": None, "maximum_checked": maximum, "target_power": target, "delta": delta, "discordance": discordance}


def wilson(successes, n, z=1.959963984540054):
    if not n: return None
    p = successes/n; d = 1+z*z/n
    center = (p+z*z/(2*n))/d
    radius = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0., center-radius), min(1., center+radius)]


def paired(rows, tasks, confirmatory=False):
    index = {(r["task_id"], r["arm"]): r["score"] for r in rows}
    pairs = [(index.get((t["task_id"], "R")), index.get((t["task_id"], "K"))) for t in tasks]
    complete = [(a,b) for a,b in pairs if a is not None and b is not None]
    wins = sum(a > b for a,b in complete); losses = sum(a < b for a,b in complete)
    lo = sum((a if a is not None else 0)-(b if b is not None else 1) for a,b in pairs)
    hi = sum((a if a is not None else 1)-(b if b is not None else 0) for a,b in pairs)
    raw_p = mcnemar(wins, losses)
    # A complete-case p-value is descriptive when any selected outcome is missing.
    return {"scheduled_pairs": len(tasks), "complete_pairs": len(complete), "R_only": wins, "K_only": losses,
            "both_pass":sum(a==b==1 for a,b in complete),"both_fail":sum(a==b==0 for a,b in complete),
            "ties": len(complete)-wins-losses, "mean_difference": (wins-losses)/len(complete) if complete else None,
            "fixed_denominator_bounds": [lo/len(tasks), hi/len(tasks)] if tasks else None,
            "complete_case_exact_p": raw_p if complete else None,
            "confirmatory_p": raw_p if confirmatory and len(complete) == len(tasks) and tasks else None,
            "equivalence_established": False}
