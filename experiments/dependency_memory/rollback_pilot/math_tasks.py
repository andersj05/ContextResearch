"""Prespecified 12-task generator; witnesses never enter ActorTask records."""
from __future__ import annotations

import platform
import random

from .records import ActorTask, EvaluatorTask


BASE_SEED = 20261008
SLOTS = {"integer": ((4, 2), (5, 3), (6, 3), (6, 4)),
         "modular": ((4, 3), (5, 4), (6, 4), (6, 5)),
         "coloring": ((8, 0), (9, 0), (10, 0), (12, 0))}


def generate_math():
    result = []
    for family_index, (family, slots) in enumerate(SLOTS.items()):
        for slot, (n, equations) in enumerate(slots):
            seed = BASE_SEED + 100 * family_index + slot
            rng = random.Random(seed)
            witness = [rng.randrange(6) for _ in range(n)] if family != "coloring" else [i % 3 for i in range(n)]
            constraints, colors, edges = [], None, []
            if family == "coloring":
                rng.shuffle(witness)
                colors = [[color, rng.choice([x for x in range(3) if x != color])] for color in witness]
                probability = (0.35, 0.45, 0.55, 0.65)[slot]
                for a in range(n):
                    for b in range(a + 1, n):
                        if witness[a] != witness[b] and rng.random() < probability:
                            edges.append([a, b])
            else:
                signatures = set()
                for row_index in range(equations):
                    for _ in range(100):
                        coefficients = [rng.randint(-3, 3) if family == "integer" else rng.randint(1, 5) for _ in range(n)]
                        total = sum(c * x for c, x in zip(coefficients, witness))
                        row = {"id": f"q{row_index + 1}", "coefficients": coefficients}
                        if family == "integer":
                            row["equals"] = total
                            signature = (tuple(coefficients), total)
                        else:
                            modulus = rng.choice((5, 7, 11))
                            row.update(modulus=modulus, residue=total % modulus)
                            signature = (tuple(coefficients), modulus, total % modulus)
                        if any(coefficients) and signature not in signatures:
                            signatures.add(signature)
                            constraints.append(row)
                            break
                    else:
                        raise ValueError(f"construction exhausted: {family}/{slot}/{row_index}")
            public = {"domain": "math", "statement": "Find integer values in the declared variable order satisfying every public bound and constraint. Return {\"values\":[...]}."
                      if family != "coloring" else "Choose a listed color for every vertex, in the declared order, with different colors on every edge. Return {\"values\":[...]}.",
                      "family": family, "variables": [f"v{i + 1}" for i in range(n)],
                      "bounds": {"minimum": 0, "maximum": 2 if family == "coloring" else 5},
                      "constraints": constraints, "allowed_colors": colors, "edges": edges}
            task = ActorTask.from_dict(f"math-{family}-{slot + 1:02d}", family, public)
            evaluator = EvaluatorTask.bind(task, {"witness": {"values": witness}, "seed": seed,
                                                "origin": "authored finite construction", "license": "repository-authored",
                                                "generator_python": platform.python_version(), "cohort": "E2-math-preparation"})
            result.append((task, evaluator))
    return result
