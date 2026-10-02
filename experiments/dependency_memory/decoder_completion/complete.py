"""Complete a fixed finite code without increasing its uniform-source mean loss.

This is an offline decoder-design adapter, not an actor with source reread.
The analytic lemma applies to arbitrary k/capacity. This exhaustive adapter
checks one to three four-bit blocks and at most 64 public parent states.
"""
from functools import lru_cache
from itertools import product

from experiments.dependency_memory.joint_coding import decoder_frontier as f


def branch_completion(pair, fill):
    if tuple(pair) not in f.PAIR_INDEX or type(fill) is not int or not 0 <= fill < 8:
        raise ValueError('Expected a canonical three-bit pair and fill in 0..7')
    first, second = pair
    disagreement = first ^ second
    agreement = 7 ^ disagreement
    if fill & disagreement:
        raise ValueError('Only agreement coordinates may be filled')
    zero = (first & disagreement) | (fill & agreement)
    one = zero ^ 7
    return tuple(sorted((zero, one))), int(zero > one)


def branch_completions(pair):
    disagreement = pair[0] ^ pair[1]
    return tuple(branch_completion(pair, fill) for fill in range(8) if not fill & disagreement)


def validate_code(tables, book, parent):
    k = len(tables)
    if not 1 <= k <= 3 or not 1 <= len(book) <= 64:
        raise ValueError('Finite adapter requires 1..3 blocks and 1..64 states')
    for table in tables:
        f.loss_matrix(tuple(table))
    if len(set(book)) != len(book) or any(len(word) != k or any(type(a) is not int or not 0 <= a < 16 for a in word) for word in book):
        raise ValueError('Invalid or duplicate decision words')
    if len(parent) != 16**k or any(type(m) is not int or not 0 <= m < len(book) for m in parent):
        raise ValueError('One valid parent message per source is required')


def source_blocks(source, k):
    return tuple((source >> (4*r)) & 15 for r in range(k))


@lru_cache(None)
def nearest_parent(tables, book):
    k = len(tables)
    validate_code(tables, book, (0,)*(16**k))
    losses = [f.loss_matrix(tuple(table)) for table in tables]
    result = []
    for source in range(16**k):
        x = source_blocks(source, k)
        result.append(min(range(len(book)), key=lambda m: sum(losses[r][x[r]][book[m][r]] for r in range(k))))
    return tuple(result)


def complete_code(tables, book, parent):
    """Use population correlations to choose fixed public agreement bits.

    The parent assignment is unchanged. All design statistics are computed
    before an actual source instance; they are never supplied to an actor.
    """
    validate_code(tables, book, parent)
    k = len(tables)
    counts = [[[[0, 0] for _ in range(3)] for _ in range(4)] for _ in range(k)]
    for source, message in enumerate(parent):
        for r, x in enumerate(source_blocks(source, k)):
            word = book[message][r]
            for o in range(4):
                bit = (word >> o) & 1
                for pos, j in enumerate(j for j in range(4) if j != o):
                    counts[r][o][pos][((x >> j) & 1) ^ bit] += 1
    completed, masks = [], []
    for r, table in enumerate(tables):
        changed, mask = [], 0
        for o, index in enumerate(table):
            pair = f.PAIRS[index]
            agree = 7 ^ (pair[0] ^ pair[1])
            fill = sum(int(counts[r][o][j][1] > counts[r][o][j][0]) << j for j in range(3) if (agree >> j) & 1)
            new_pair, flip = branch_completion(pair, fill)
            changed.append(f.PAIR_INDEX[new_pair])
            mask |= flip << o
        completed.append(tuple(changed))
        masks.append(mask)
    new_book = tuple(tuple(a ^ mask for a, mask in zip(word, masks)) for word in book)
    return {'tables': tuple(completed), 'book': new_book, 'parent': tuple(parent),
            'relabel_masks': tuple(masks), 'design_correlation_counts': counts}


def update(message, block, omitted, book):
    if type(message) is not int or not 0 <= message < len(book):
        raise ValueError('Invalid parent message')
    if type(block) is not int or not 0 <= block < len(book[message]) or type(omitted) is not int or not 0 <= omitted < 4:
        raise ValueError('Invalid public branch')
    return (book[message][block] >> omitted) & 1


def predict(child, block, omitted, query, tables):
    if type(child) is not int or child not in (0, 1) or type(block) is not int or not 0 <= block < len(tables):
        raise ValueError('Invalid child or block')
    if type(omitted) is not int or not 0 <= omitted < 4 or type(query) is not int or not 0 <= query < 4 or query == omitted:
        raise ValueError('Invalid final query')
    endpoint = f.PAIRS[tables[block][omitted]][child]
    pos = list(j for j in range(4) if j != omitted).index(query)
    return (endpoint >> pos) & 1


def grade(tables, book, parent):
    """Execute actual source/query routes, separate from nearest-parent losses."""
    validate_code(tables, book, parent)
    k = len(tables)
    errors = 0
    for source, message in enumerate(parent):
        truth = tuple(int(c) for c in reversed(f'{source:0{4*k}b}'))
        for r, o in product(range(k), range(4)):
            child = update(message, r, o, book)
            for j in range(4):
                if j != o:
                    errors += predict(child, r, o, j, tables) != truth[4*r+j]
    return errors
