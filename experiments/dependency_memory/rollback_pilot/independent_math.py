"""Independent exhaustive solution sets; deliberately never imports the grader."""
from itertools import product


def exhaustive_solutions(public):
    """Intersect independently enumerated equation sets or edge-compatible lists."""
    n = len(public["variables"])
    if public["family"] == "coloring":
        universe = list(product(*public["allowed_colors"]))
        accepted = {x for x in universe if all(len({x[a], x[b]}) == 2 for a, b in public["edges"])}
    else:
        low, high = public["bounds"]["minimum"], public["bounds"]["maximum"]
        universe = list(product(range(low, high + 1), repeat=n))
        accepted = set(universe)
        for constraint in public["constraints"]:
            passing = set()
            for assignment in universe:
                terms = [constraint["coefficients"][column] * assignment[column] for column in range(n)]
                value = 0
                for term in terms:
                    value += term
                if public["family"] == "integer":
                    valid = value == constraint["equals"]
                else:
                    # Divisibility, rather than the production checker's residue comparison.
                    numerator = value - constraint["residue"]
                    valid = numerator // constraint["modulus"] * constraint["modulus"] == numerator
                if valid:
                    passing.add(assignment)
            accepted.intersection_update(passing)
    return universe, accepted
