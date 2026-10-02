"""Constructed evaluator catalogs, separate from the source-analysis interface."""
from copy import deepcopy
from itertools import product

from experiments.dependency_memory.scope_inference import study

MISSING = object()


def catalog(name):
    if name == "dispatch":
        for row in study.control_catalog():
            yield row, None
    elif name == "tokens":
        names = ("inputTokens", "cachedInputTokens", "outputTokens", "reasoningOutputTokens")
        for values, writes, total in product(product((MISSING, None, True, 0, 1, 2), repeat=4),
                                            (MISSING, 0, 1, 3), (MISSING, 0, 3, 6)):
            row = {k: v for k, v in zip(names, values) if v is not MISSING}
            if writes is not MISSING:
                row["cacheWriteInputTokens"] = writes
            if total is not MISSING:
                row["totalTokens"] = total
            row["unrelated"] = {"note": "ignored public development field", "count": 7}
            yield row, None
        for value in (None, False, [], "usage", {}):
            yield value, None
        base = dict(zip(names, (10, 2, 5, 1)))
        for key, value in product(names, (-1, "2", 0.5, [], {}, 272000, 128001)):
            yield {**base, key: value}, None
    elif name == "quota":
        windows = (MISSING, None, {}, {"usedPercent": 0}, {"usedPercent": 49.5}, {"usedPercent": 90},
                   {"usedPercent": 100}, {"usedPercent": True}, {"usedPercent": "0"}, {"usedPercent": -1})
        individuals = (MISSING, None, {}, {"remainingPercent": 0}, {"remainingPercent": 1}, {"remainingPercent": True})
        for primary, secondary, individual, reached, spending in product(windows, windows, individuals,
                                                                        (MISSING, None, "hit"), (MISSING, False, True)):
            row = {k: deepcopy(v) for k, v in (("primary", primary), ("secondary", secondary), ("individualLimit", individual),
                                              ("rateLimitReachedType", reached), ("spendControlReached", spending)) if v is not MISSING}
            row["unrelated"] = {"description": "public constructed quota metadata"}
            for ceiling in (50, 90, 100):
                yield {"bucket": row}, ceiling
        for snapshot in (None, False, [], {}, {"bucket": None}, {"bucket": False}, {"a": {"primary": {"usedPercent": 0}}, "b": None}):
            yield snapshot, 90
    elif name == "late_key":
        for values in product((0, 1), repeat=4):
            row = {"values": dict(zip(("alpha", "beta", "gamma", "delta"), values)), "unrelated": {"note": "outside the lookup"}}
            for key in ("alpha", "beta", "gamma", "delta", "absent"):
                yield row, key
        for value in (MISSING, None, {}, [], "wrong"):
            row = {} if value is MISSING else {"values": value}
            yield row, "alpha"
    else:
        raise ValueError("Unknown development program")
