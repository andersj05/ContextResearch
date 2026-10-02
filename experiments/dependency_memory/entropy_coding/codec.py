"""Exactly 2*k parent bits, including one fallback flag; one late child bit.

The first public a blocks use oracle majority signatures; the remaining blocks
use the two constant response words. Quantizer outputs enter one arithmetic
interval, with fixed public probabilities. A midpoint on the charged finite
grid either represents the full sequence or the encoder emits the all-zero
fallback. No interval, output list or source survives alongside M.
"""
from math import isqrt
from functools import cache

WORDS = ((0,15), (0,3,5,6,9,10,12,15))
COUNTS = ((11,5), (5,1,1,1,1,1,1,5))


@cache
def default_count(k):
    if type(k) is not int or k < 1:
        raise ValueError('Expected a positive public block count')
    # Public entropy slack grows faster than sqrt(k) and slower than k.
    # k.bit_length() is exactly ceil(log2(k+1)) for positive integer k.
    margin = isqrt(k*k.bit_length()-1)+1
    threshold = 1 << (32*k+16*margin)
    def admissible(a):
        # H_total(a)<=2*k-margin, after clearing all logarithms.
        return 5**(5*(k+a))*11**(11*(k-a)) >= threshold
    if not admissible(0):
        return 0
    low,high = 0,k
    while low < high:
        middle = (low+high+1)//2
        if admissible(middle):
            low = middle
        else:
            high = middle-1
    return low


def rational_count(k):
    if type(k) is not int or k < 1:
        raise ValueError('Expected a positive public block count')
    return max(0,2*k//3-(isqrt(4*k-1)+1))


def count(k, a=None):
    if type(k) is not int or k < 1:
        raise ValueError('Expected a positive public block count')
    if a is None:
        return default_count(k)
    if type(a) is not int or not 0 <= a <= k:
        raise ValueError('Oracle count must be public before X and inside 0..k')
    return a


def response(source, oracle):
    if type(source) is not int or not 0 <= source < 16:
        raise ValueError('Expected a four-bit source')
    weight = source.bit_count()
    if oracle:
        return sum((weight-((source >> o) & 1) >= 2) << o for o in range(4))
    return 15 if weight >= 3 else 0


def encode(blocks, a=None, *, diagnostics=False):
    blocks = tuple(blocks)
    k = len(blocks)
    a = count(k,a)
    low, width = 0, 1
    for r,x in enumerate(blocks):
        kind = int(r < a)
        index = WORDS[kind].index(response(x,kind))
        low = 16*low + width*sum(COUNTS[kind][:index])
        width *= COUNTS[kind][index]
    denominator = 1 << (4*k)
    scale = 1 << (2*k)
    # Least odd grid numerator j with j/scale >= low/denominator.
    j = (low*scale+denominator-1)//denominator
    j += not (j & 1)
    regular = j < scale and j*denominator < (low+width)*scale
    parent = (1 << (2*k-1)) | ((j-1)//2) if regular else 0
    guaranteed = width >= (1 << (2*k+1))
    if guaranteed and not regular:
        raise ArithmeticError('An interval at least one grid spacing must contain a midpoint')
    if diagnostics:
        return parent, {'oracle_blocks': a, 'regular': regular,
                        'interval_length_guaranteed': guaranteed,
                        'interval_low': low, 'interval_width': width,
                        'interval_denominator_power_two': 4*k}
    return parent


def decode_response(parent, block, k, a=None):
    a = count(k,a)
    if type(parent) is not int or not 0 <= parent < (1 << (2*k)):
        raise ValueError('Parent exceeds the charged 2*k-bit cap')
    if type(block) is not int or not 0 <= block < k:
        raise ValueError('Invalid public queried block')
    flag = 1 << (2*k-1)
    if parent < flag:
        if parent:
            raise ValueError('Only zero is a valid fallback message')
        return 0
    numerator, denominator = 2*(parent-flag)+1, 1 << (2*k)
    for r in range(block+1):
        kind = int(r < a)
        cumulative = 0
        for word,c in zip(WORDS[kind],COUNTS[kind]):
            if 16*numerator < (cumulative+c)*denominator:
                numerator = 16*numerator-cumulative*denominator
                denominator *= c
                break
            cumulative += c
        else:
            raise ArithmeticError('Public arithmetic decoder left its unit interval')
    return word


def update(parent, block, omitted, k, a=None):
    if type(omitted) is not int or not 0 <= omitted < 4:
        raise ValueError('Invalid public omission')
    return (decode_response(parent,block,k,a) >> omitted) & 1


def predict(child, block, omitted, query):
    if (type(child) is not int or child not in (0,1)
            or type(block) is not int or block < 0
            or type(omitted) is not int or not 0 <= omitted < 4
            or type(query) is not int or not 0 <= query < 4 or query == omitted):
        raise ValueError('Invalid one-bit final state or public query')
    return child


def pack_tables():
    values = tuple(v for rows in (WORDS,COUNTS) for row in rows for v in row)
    return bytes((values[i] << 4) | values[i+1] for i in range(0,len(values),2))
