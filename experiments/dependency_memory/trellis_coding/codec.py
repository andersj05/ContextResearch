"""Exact tail-biting encoder and source-inaccessible local updater.

Public tables are fixed before the source. Two bits per block encode the
complete parent, including the cyclic boundary. The child is formed before J.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def validate_tables(tables):
    if (len(tables) != 3 or any(len(row) != 64 for row in tables)
            or any(type(a) is not int or not 0 <= a < 16 for row in tables for a in row)):
        raise ValueError('Expected three public 64-entry four-bit response tables')


def selected_tables():
    tables = tuple(tuple(row) for row in json.loads((HERE / 'tables.json').read_text(encoding='utf-8')))
    validate_tables(tables)
    return tables


TABLES = selected_tables()


def response(before, previous, current, phase, tables=TABLES):
    # The three index orders preserve the old three-block book at k=3.
    if phase == 0:
        index = current + 4 * before + 16 * previous
    elif phase == 1:
        index = previous + 4 * current + 16 * before
    else:
        index = before + 4 * previous + 16 * current
    return tables[phase][index]


def loss(source, word):
    """Integer sum of the 12 omission/query bit errors in one block."""
    weight = source.bit_count()
    return sum(3 - weight + ((source >> o) & 1) if ((word >> o) & 1)
               else weight - ((source >> o) & 1) for o in range(4))


LOSSES = tuple(tuple(loss(x, a) for a in range(16)) for x in range(16))


def decision_word(message, block, block_count, tables=TABLES):
    if type(block_count) is not int or block_count < 1:
        raise ValueError('Expected a positive public block count')
    if type(message) is not int or not 0 <= message < (1 << (2 * block_count)):
        raise ValueError('Parent exceeds two bits per block')
    if type(block) is not int or not 0 <= block < block_count:
        raise ValueError('Invalid public block')
    before = (message >> (2 * ((block - 2) % block_count))) & 3
    previous = (message >> (2 * ((block - 1) % block_count))) & 3
    current = (message >> (2 * block)) & 3
    return response(before, previous, current, block % 3, tables)


def update(message, block, omitted, block_count, tables=TABLES):
    """Only M, R, O and public k/tables; no source, archive or final query."""
    if type(omitted) is not int or not 0 <= omitted < 4:
        raise ValueError('Invalid public omission')
    return (decision_word(message, block, block_count, tables) >> omitted) & 1


def predict(child, block, omitted, query):
    """Final actor sees only the one-bit child and public R/O/J."""
    if type(child) is not int or child not in (0, 1):
        raise ValueError('Invalid one-bit child')
    if type(block) is not int or block < 0:
        raise ValueError('Invalid public block')
    if (type(omitted) is not int or not 0 <= omitted < 4
            or type(query) is not int or not 0 <= query < 4 or omitted == query):
        raise ValueError('Invalid delayed coordinate')
    return child


def book(block_count, tables=TABLES):
    """Small-block exhaustive diagnostic; the general encoder does not use it."""
    validate_tables(tables)
    if type(block_count) is not int or not 1 <= block_count <= 6:
        raise ValueError('Enumeration is restricted to 1..6 blocks')
    return tuple(tuple(decision_word(m, r, block_count, tables) for r in range(block_count))
                 for m in range(1 << (2 * block_count)))


def encode(blocks, tables=TABLES, *, diagnostics=False):
    """Minimum-loss message, ties by smallest integer M; exact reverse Viterbi.

    Each of 16 cyclic boundary states has k stages and 16*4 transitions.
    We store a cost-to-go table for one boundary at a time. Greedy traceback
    chooses the most significant unfixed quaternary symbol first, so tied
    messages require no growing integer path labels during the recurrence.
    The number of branch relaxations is 1024*k for k>=2, not a wall-time or
    bit-operation complexity claim.
    """
    blocks = tuple(blocks)
    if not blocks or any(type(x) is not int or not 0 <= x < 16 for x in blocks):
        raise ValueError('Expected a nonempty source of four-bit blocks')
    validate_tables(tables)
    k = len(blocks)
    if k == 1:
        values = [LOSSES[blocks[0]][decision_word(m, 0, 1, tables)] for m in range(4)]
        result = (values.index(min(values)), min(values), 4)
        return result if diagnostics else result[0]

    # In reverse traversal, state = previous + 4*current. Choosing 'before'
    # yields next state before + 4*previous. Start/end encode the last two
    # actual parent symbols; this state is not an additional memory channel.
    infinity = 12 * k + 1
    transition_costs = tuple(tuple(tuple(LOSSES[x][response(c, state & 3, state >> 2, r % 3, tables)]
                                        for c in range(4)) for state in range(16))
                             for r, x in enumerate(blocks))
    best_cost, best_start, best_rows = infinity, None, None
    for start in range(16):
        previous_row = [0 if state == start else infinity for state in range(16)]
        rows = []
        for r in range(k):
            row = [min(transition_costs[r][state][c] + previous_row[c + 4 * (state & 3)]
                       for c in range(4)) for state in range(16)]
            rows.append(row)
            previous_row = row
        if rows[-1][start] < best_cost:
            best_cost, best_start, best_rows = rows[-1][start], start, rows

    if best_rows is None:
        raise AssertionError('Every parent message supplies a valid cyclic path')
    symbols = [None] * k
    symbols[-2], symbols[-1] = best_start & 3, best_start >> 2
    state = best_start
    for r in range(k - 1, -1, -1):
        remaining = best_rows[r - 1] if r else [0 if s == best_start else infinity for s in range(16)]
        before = next(c for c in range(4) if transition_costs[r][state][c]
                      + remaining[c + 4 * (state & 3)] == best_rows[r][state])
        position = (r - 2) % k
        if symbols[position] is not None and symbols[position] != before:
            raise AssertionError('Tail-biting closure repeats a different parent symbol')
        symbols[position] = before
        state = before + 4 * (state & 3)
    if state != best_start or any(s is None for s in symbols):
        raise AssertionError('Tail-biting path did not close')
    packed = bytearray((k + 3) // 4)
    for r, symbol in enumerate(symbols):
        packed[r // 4] |= symbol << (2 * (r % 4))
    message = int.from_bytes(packed, 'little')
    result = (message, best_cost, 1024 * k)
    return result if diagnostics else message


def pack_tables(tables=TABLES):
    validate_tables(tables)
    values = [a for row in tables for a in row]
    return bytes(values[i] | (values[i + 1] << 4) for i in range(0, 192, 2))


def encode_segments(blocks, tables=TABLES, *, diagnostics=False):
    """Product of independently closed four-block codes, at exactly 2*k bits."""
    blocks = tuple(blocks)
    if not blocks or len(blocks) % 4 or any(type(x) is not int or not 0 <= x < 16 for x in blocks):
        raise ValueError('Expected complete four-block source segments')
    payload = bytearray()
    cost = 0
    for start in range(0, len(blocks), 4):
        message, value, _ = encode(blocks[start:start + 4], tables, diagnostics=True)
        payload.append(message)
        cost += value
    result = (int.from_bytes(payload, 'little'), cost, 1024 * len(blocks))
    return result if diagnostics else result[0]


def update_segments(message, block, omitted, block_count, tables=TABLES):
    if type(block_count) is not int or block_count < 4 or block_count % 4:
        raise ValueError('Expected a public multiple of four blocks')
    if type(message) is not int or not 0 <= message < (1 << (2 * block_count)):
        raise ValueError('Parent exceeds two bits per block')
    if type(block) is not int or not 0 <= block < block_count:
        raise ValueError('Invalid public block')
    local_message = (message >> (8 * (block // 4))) & 255
    return update(local_message, block % 4, omitted, 4, tables)


def unpack_tables(payload):
    if type(payload) is not bytes or len(payload) != 96:
        raise ValueError('Expected 96 packed public label bytes')
    values = tuple(nibble for byte in payload for nibble in (byte & 15, byte >> 4))
    return tuple(values[r * 64:(r + 1) * 64] for r in range(3))
