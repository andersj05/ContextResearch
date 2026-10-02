"""Only charged parent and child states cross the two memory boundaries."""
from . import design
from experiments.dependency_memory.entropy_coding import codec as scalar

TAIL = (0, 1, 14, 15)


def public_count(n, a):
    if type(n) is not int or n < 0 or type(a) is not int or not 0 <= a <= n:
        raise ValueError('Public full-group and oracle counts required')
    return a


def encode(blocks, book, a, *, diagnostics=False):
    xs = tuple(blocks)
    if not xs or any(type(x) is not int or not 0 <= x < 16 for x in xs):
        raise ValueError('Nonempty four-bit source required')
    k, g = len(xs), book.g
    n, r = divmod(k, g)
    a = public_count(n, a)
    _, prefix, _ = design.compiled(book)
    low, width = 0, 1
    for block in range(a*g):
        word = scalar.response(xs[block], True)
        index = scalar.WORDS[1].index(word)
        low = 16*low+width*sum(scalar.COUNTS[1][:index])
        width *= scalar.COUNTS[1][index]
    for group in range(a, n):
        source = sum(xs[group*g+j] << (4*j) for j in range(g))
        index = design.choose(source, book)
        if not book.counts[index]:
            raise ArithmeticError('Public CDF disagrees with an exact-rule output')
        low = (16**g)*low+width*prefix[index]
        width *= book.counts[index]
    arithmetic = 0
    regular = guaranteed = False
    if n:
        denominator, scale = 1 << (4*n*g), 1 << (2*n*g)
        j = (low*scale+denominator-1)//denominator
        j += not (j&1)
        regular = j < scale and j*denominator < (low+width)*scale
        arithmetic = (1 << (2*n*g-1))|((j-1)//2) if regular else 0
        guaranteed = width >= (1 << (2*n*g+1))
        if guaranteed and not regular:
            raise ArithmeticError('A full-spacing interval has no allowed midpoint')
    tail = 0
    for j, x in enumerate(xs[n*g:]):
        index = min(range(4), key=lambda i:(design.cost(x, TAIL[i], 1), i))
        tail |= index << (2*j)
    parent = (arithmetic << (2*r))|tail
    if parent >= 1 << (2*k):
        raise ArithmeticError('Parent exceeds charged 2*k bits')
    if diagnostics:
        return parent, {'full_groups':n, 'tail_blocks':r, 'oracle_groups':a,
            'regular':regular, 'length_guaranteed':guaranteed,
            'arithmetic_parent':arithmetic, 'interval_low':low, 'interval_width':width}
    return parent


def decode_response(parent, block, k, book, a):
    if type(k) is not int or k < 1:
        raise ValueError('Positive public source length required')
    if type(parent) is not int or not 0 <= parent < (1 << (2*k)):
        raise ValueError('Parent exceeds charged capacity')
    if type(block) is not int or not 0 <= block < k:
        raise ValueError('Invalid public queried block')
    g = book.g
    n, r = divmod(k, g)
    a = public_count(n, a)
    if block >= n*g:
        return TAIL[(parent >> (2*(block-n*g)))&3]
    arithmetic = parent >> (2*r)
    flag = 1 << (2*n*g-1)
    if arithmetic < flag:
        if arithmetic:
            raise ValueError('Only zero is a valid full-group fallback')
        return (book.words[book.fallback] >> (4*(block % g)))&15
    numerator, denominator = 2*(arithmetic-flag)+1, 1 << (2*n*g)
    stop = min(block+1, a*g)
    for pos in range(stop):
        cumulative = 0
        for word, c in zip(scalar.WORDS[1], scalar.COUNTS[1]):
            if 16*numerator < (cumulative+c)*denominator:
                numerator, denominator = 16*numerator-cumulative*denominator, c*denominator
                break
            cumulative += c
    if block < a*g:
        return word
    for group in range(a, block//g+1):
        index, cumulative = design.cdf_index(numerator, denominator, book)
        numerator, denominator = 16**g*numerator-cumulative*denominator, book.counts[index]*denominator
    return (book.words[index] >> (4*(block % g)))&15


def update(parent, block, omitted, k, book, a):
    if type(omitted) is not int or not 0 <= omitted < 4:
        raise ValueError('Invalid public omission')
    return (decode_response(parent, block, k, book, a) >> omitted)&1


def predict(child, block, omitted, query):
    return scalar.predict(child, block, omitted, query)
