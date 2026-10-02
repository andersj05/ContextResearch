"""Deterministic opposite-orientation pairs, and equally capped controls.

Public class membership: first half of the blocks is L, the second half R.
R is uniform inside its class; its class probability is source-independent.
Only the known-prior diagnostic encoder accepts prior weights. The balanced
encoder does not; no orientation bit, random tape or extra retained state.
"""
from experiments.dependency_memory.conditional_coding import codec as six

SINGLE_BOOKS = {1: (0, 15), 3: (0, 3, 5, 6, 9, 10, 12, 15)}


def encode_balanced(blocks, *, diagnostics=False):
    blocks = tuple(blocks)
    if not blocks or len(blocks) % 12:
        raise ValueError('Expected complete public twelve-block segments')
    parent, value = 0, 0
    half = len(blocks)//2
    for group in range(half//3):
        start = 3*group
        left, right = blocks[start:start+3], blocks[half+start:half+start+3]
        local = right+left if group % 2 else left+right
        m, loss = six.encode(local, diagnostics=True)
        parent |= m << (12*group)
        value += loss
    return (parent, value) if diagnostics else parent


def update_balanced(parent, block, omitted, block_count):
    if type(block_count) is not int or block_count < 12 or block_count % 12:
        raise ValueError('Expected a public positive multiple of twelve')
    if type(parent) is not int or not 0 <= parent < (1 << (2*block_count)):
        raise ValueError('Parent exceeds two bits per block')
    if type(block) is not int or not 0 <= block < block_count:
        raise ValueError('Invalid public block')
    half = block_count//2
    source_class, in_class = divmod(block, half)
    group, rank = divmod(in_class, 3)
    local = rank+3*(source_class ^ (group % 2))
    return six.update((parent >> (12*group)) & 4095, local, omitted)


def predict(child, block, omitted, query):
    return six.predict(child, block, omitted, query)


def validate_weights(left_weight, right_weight):
    if (type(left_weight) is not int or type(right_weight) is not int
            or left_weight < 0 or right_weight < 0 or not left_weight+right_weight):
        raise ValueError('Expected nonnegative integer public weights with positive sum')


def encode_known_prior(blocks, left_weight, right_weight, *, diagnostics=False,
                       base=six.BASE, overrides=six.OVERRIDES):
    """Fixed six-block book, reencoded with a prior public BEFORE X.

    This is a different information condition from frozen-parent evaluation.
    Diagnostic weighted loss is evaluator output; only M reaches the updater.
    """
    validate_weights(left_weight, right_weight)
    blocks = tuple(blocks)
    if len(blocks) != 6 or any(type(x) is not int or not 0 <= x < 16 for x in blocks):
        raise ValueError('Expected six four-bit source blocks')
    six.validate(base, overrides)
    left = sum(x << (4*r) for r, x in enumerate(blocks[:3]))
    right = sum(x << (4*r) for r, x in enumerate(blocks[3:]))
    left_costs = [left_weight*six.triple_loss(left, c) for c in base]
    left_value = min(left_costs)
    left_arg = left_costs.index(left_value)
    changed = {m >> 6 for m in overrides}
    best, message = 36*(left_weight+right_weight)+1, None
    for b, c in enumerate(base):
        if b in changed and left_weight:
            costs = [left_weight*six.triple_loss(left, overrides[a+64*b])
                     if a+64*b in overrides else left_costs[a] for a in range(64)]
            value = min(costs)
            a = costs.index(value)
        else:
            value, a = left_value, left_arg
        value += right_weight*six.triple_loss(right, c)
        if value < best:
            best, message = value, a+64*b
    return (message, best) if diagnostics else message


def encode_allocated(blocks, left_bits, right_bits):
    """Fixed1/3 or3/1 per-block allocation, two parent bits per block on average.

    Allocation is a public design choice fixed before X, not a source-dependent
    uncharged selector. Equal class sizes give two parent bits per block.
    """
    if (type(left_bits) is not int or type(right_bits) is not int
            or (left_bits, right_bits) not in ((1, 3), (3, 1))):
        raise ValueError('Expected the public1/3 or3/1 allocation')
    blocks = tuple(blocks)
    if not blocks or len(blocks) % 6 or any(type(x) is not int or not 0 <= x < 16 for x in blocks):
        raise ValueError('Expected complete six-block source groups')
    parent, offset = 0, 0
    for r, x in enumerate(blocks):
        bits = left_bits if r < len(blocks)//2 else right_bits
        costs = [six.LOSSES[x][c] for c in SINGLE_BOOKS[bits]]
        parent |= costs.index(min(costs)) << offset
        offset += bits
    return parent


def update_allocated(parent, block, omitted, block_count, left_bits, right_bits):
    if (type(left_bits) is not int or type(right_bits) is not int
            or (left_bits, right_bits) not in ((1, 3), (3, 1))):
        raise ValueError('Expected the public1/3 or3/1 allocation')
    if type(block_count) is not int or block_count < 6 or block_count % 6:
        raise ValueError('Expected a public positive multiple of six')
    if type(parent) is not int or not 0 <= parent < (1 << (2*block_count)):
        raise ValueError('Parent exceeds two bits per block')
    if type(block) is not int or not 0 <= block < block_count:
        raise ValueError('Invalid public block')
    if type(omitted) is not int or not 0 <= omitted < 4:
        raise ValueError('Invalid public omission')
    half = block_count//2
    bits = left_bits if block < half else right_bits
    offset = block*left_bits if block < half else half*left_bits+(block-half)*right_bits
    m = (parent >> offset) & ((1 << bits)-1)
    return (SINGLE_BOOKS[bits][m] >> omitted) & 1


def encode_early_class(blocks, class_id):
    """Actual realized class, not its probability, is revealed BEFORE M.

    Store three-bit majority signatures for that class only. At k=2*n the
    payload uses3*n bits, within the common4*n-bit cap. This changed timing
    condition supplies no early R/O/J and needs no source-dependent selector.
    """
    blocks = tuple(blocks)
    if (not blocks or len(blocks) % 2 or type(class_id) is not int or class_id not in (0, 1)
            or any(type(x) is not int or not 0 <= x < 16 for x in blocks)):
        raise ValueError('Expected two equal source classes and a public class ID')
    half = len(blocks)//2
    parent = 0
    for i, x in enumerate(blocks[class_id*half:(class_id+1)*half]):
        costs = [six.LOSSES[x][c] for c in SINGLE_BOOKS[3]]
        parent |= costs.index(min(costs)) << (3*i)
    return parent


def update_early_class(parent, block, omitted, block_count):
    if type(block_count) is not int or block_count < 2 or block_count % 2:
        raise ValueError('Expected two equal public classes')
    half = block_count//2
    if type(parent) is not int or not 0 <= parent < (1 << (3*half)):
        raise ValueError('Early-class payload exceeds three bits per queried block')
    if type(block) is not int or not 0 <= block < block_count:
        raise ValueError('Invalid public block')
    if type(omitted) is not int or not 0 <= omitted < 4:
        raise ValueError('Invalid public omission')
    # R determines its class. The experiment queries only the class disclosed
    # to the encoder; that public cue is not stored in M.
    m = (parent >> (3*(block % half))) & 7
    return (SINGLE_BOOKS[3][m] >> omitted) & 1
