"""Twelve parent bits, followed by one child bit, for six delayed-query blocks.

The response book is public before X. Parent M = a + 64*b uses a common
three-block base book on the right and eight conditional changes on the left.
Only the encoder can read X; updater and final actor have no source argument.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def validate(base, overrides):
    if (len(base) != 64 or len(set(base)) != 64
            or any(type(c) is not int or not 0 <= c < 4096 for c in base)):
        raise ValueError('Expected 64 distinct public twelve-bit triples')
    if any(type(m) is not int or not 0 <= m < 4096
           or type(c) is not int or not 0 <= c < 4096 for m, c in overrides.items()):
        raise ValueError('Invalid conditional public entry')
    for b in range(64):
        if len({overrides.get(a + 64*b, base[a]) for a in range(64)}) != 64:
            raise ValueError('Duplicate left response triple within a right group')


def selected():
    data = json.loads((HERE / 'tables.json').read_text(encoding='utf-8'))
    base = tuple(data['base'])
    pairs = data['overrides']
    if pairs != sorted(pairs) or len({m for m, _ in pairs}) != len(pairs):
        raise ValueError('Public entries must have distinct ordered parent IDs')
    overrides = dict(pairs)
    validate(base, overrides)
    return base, overrides


BASE, OVERRIDES = selected()


def loss(source, response):
    weight = source.bit_count()
    return sum(3 - weight + ((source >> o) & 1) if ((response >> o) & 1)
               else weight - ((source >> o) & 1) for o in range(4))


LOSSES = tuple(tuple(loss(x, c) for c in range(16)) for x in range(16))


def triple_loss(source, response):
    return sum(LOSSES[(source >> (4*r)) & 15][(response >> (4*r)) & 15]
               for r in range(3))


def encode(blocks, base=BASE, overrides=OVERRIDES, *, diagnostics=False):
    """Exact nearest parent within the fixed book; smallest integer M on ties.

    Conditional left minima depend on b, so M can encode joint information
    about both halves. Unmodified right groups share the base left minimum.
    This avoids materializing a 4096-word book without changing the minimum.
    """
    blocks = tuple(blocks)
    if len(blocks) != 6 or any(type(x) is not int or not 0 <= x < 16 for x in blocks):
        raise ValueError('Expected six four-bit source blocks')
    validate(base, overrides)
    left = sum(x << (4*r) for r, x in enumerate(blocks[:3]))
    right = sum(x << (4*r) for r, x in enumerate(blocks[3:]))
    left_costs = [triple_loss(left, c) for c in base]
    left_value = min(left_costs)
    left_arg = left_costs.index(left_value)
    changed = {m >> 6 for m in overrides}
    best, message = 73, None
    for b, c in enumerate(base):
        if b in changed:
            costs = [triple_loss(left, overrides[a + 64*b])
                     if a + 64*b in overrides else left_costs[a] for a in range(64)]
            value = min(costs)
            a = costs.index(value)
        else:
            value, a = left_value, left_arg
        value += triple_loss(right, c)
        if value < best:
            best, message = value, a + 64*b
    return (message, best) if diagnostics else message


def response_word(message, block, base=BASE, overrides=OVERRIDES):
    if type(message) is not int or not 0 <= message < 4096:
        raise ValueError('Parent exceeds twelve bits')
    if type(block) is not int or not 0 <= block < 6:
        raise ValueError('Invalid public block')
    triple = overrides.get(message, base[message & 63]) if block < 3 else base[message >> 6]
    return (triple >> (4 * (block % 3))) & 15


def update(message, block, omitted, base=BASE, overrides=OVERRIDES):
    """Inputs are M, R, O and the public book; J has not arrived."""
    if type(omitted) is not int or not 0 <= omitted < 4:
        raise ValueError('Invalid public omission')
    return (response_word(message, block, base, overrides) >> omitted) & 1


def predict(child, block, omitted, query):
    """Inputs are the one-bit child and R/O/J; M and X are unavailable."""
    if type(child) is not int or child not in (0, 1):
        raise ValueError('Child exceeds one bit')
    if type(block) is not int or block < 0:
        raise ValueError('Invalid public block')
    if (type(omitted) is not int or not 0 <= omitted < 4
            or type(query) is not int or not 0 <= query < 4 or query == omitted):
        raise ValueError('Invalid delayed query')
    return child


def pack_tables(base=BASE, overrides=OVERRIDES):
    """120 label-payload bytes for the selected book, with count eight public.

    Each pair of base triples uses three bytes; each (M, triple) override also
    uses three. Program, JSON, count/framing and runtime tables are separate.
    """
    validate(base, overrides)
    payload = bytearray()
    for a in range(0, 64, 2):
        payload.extend((base[a] | (base[a+1] << 12)).to_bytes(3, 'little'))
    for m, c in sorted(overrides.items()):
        payload.extend((m | (c << 12)).to_bytes(3, 'little'))
    return bytes(payload)


def unpack_tables(payload, count):
    if type(count) is not int or count < 0 or type(payload) is not bytes or len(payload) != 96 + 3*count:
        raise ValueError('Invalid public payload or declared count')
    base = []
    for start in range(0, 96, 3):
        pair = int.from_bytes(payload[start:start+3], 'little')
        base.extend((pair & 4095, pair >> 12))
    pairs = []
    for start in range(96, len(payload), 3):
        pair = int.from_bytes(payload[start:start+3], 'little')
        pairs.append((pair & 4095, pair >> 12))
    if pairs != sorted(pairs) or len({m for m, _ in pairs}) != count:
        raise ValueError('Repeated or unordered parent ID')
    overrides = dict(pairs)
    validate(base, overrides)
    return tuple(base), overrides


def encode_segments(blocks, base=BASE, overrides=OVERRIDES, *, diagnostics=False):
    blocks = tuple(blocks)
    if not blocks or len(blocks) % 6:
        raise ValueError('Expected complete public six-block segments')
    parent, cost = 0, 0
    for start in range(0, len(blocks), 6):
        m, value = encode(blocks[start:start+6], base, overrides, diagnostics=True)
        parent |= m << (2*start)
        cost += value
    return (parent, cost) if diagnostics else parent


def update_segments(parent, block, omitted, block_count, base=BASE, overrides=OVERRIDES):
    if type(block_count) is not int or block_count < 6 or block_count % 6:
        raise ValueError('Expected a public positive multiple of six blocks')
    if type(parent) is not int or not 0 <= parent < (1 << (2*block_count)):
        raise ValueError('Parent exceeds two bits per block')
    if type(block) is not int or not 0 <= block < block_count:
        raise ValueError('Invalid public block')
    return update((parent >> (12*(block//6))) & 4095, block % 6, omitted, base, overrides)
