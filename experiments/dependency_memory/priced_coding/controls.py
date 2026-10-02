"""Small public dictionaries with independently checked source laws."""
from collections import Counter
from . import design
from experiments.dependency_memory.tie_coding import design as old_design


def constant_book(g):
    priority, counts = old_design.prepare(g)
    words = tuple(sum((15 if (v >> r)&1 else 0) << (4*r) for r in range(g)) for v in priority)
    return design.Book(g, (1, 2), words, counts, counts)


def oracle_book():
    words = tuple(range(16))
    counts = Counter(sum((sum((x >> j)&1 for j in range(4) if j != o)>1) << o
                         for o in range(4)) for x in range(16))
    return design.Book(1, (1, 2), words, (1,)*16, tuple(counts[w] for w in words))
