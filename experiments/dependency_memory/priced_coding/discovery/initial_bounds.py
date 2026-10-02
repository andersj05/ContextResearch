"""Generic fixed-point outward moments and public finite allocation."""
from fractions import Fraction as F
from functools import cache

from experiments.dependency_memory.tie_coding import bounds as roots

DEGREES = (8, 16, 32, 64, 128)
BITS = 64


def ceil_div(n, d):
    return -(-n//d)


@cache
def moments(book, loss_sums, degree):
    if (len(loss_sums) != len(book.words) or any(type(v) is not int or v < 0 for v in loss_sums)
            or degree not in DEGREES):
        raise ValueError('Nonnegative public cell loss sums and declared root degree required')
    n, scale = 16**book.g, 1 << BITS
    counts = tuple(c for c in book.counts if c)
    raw_m = roots.moment_upper(counts, n, degree)
    low_m = F(ceil_div(raw_m.numerator*scale, raw_m.denominator), scale)
    n_hi = roots.root_bounds(n, degree, BITS)[1]
    weighted_integer = 0
    for c, delta in zip(book.counts, loss_sums):
        if not c:
            if delta:
                raise ValueError('A zero-probability cell has nonzero excess')
            continue
        c_lo = roots.root_bounds(c, degree, BITS)[0]
        term = F(delta, 12*book.g*n)*n_hi/c_lo
        weighted_integer += ceil_div(term.numerator*scale, term.denominator)
    low_w = F(weighted_integer, scale)
    raw_high_m = roots.moment_upper((5, 1, 1, 1, 1, 1, 1, 5), 16, degree)
    high_m = F(ceil_div(raw_high_m.numerator*scale, raw_high_m.denominator), scale)
    root16 = roots.root_bounds(16, degree, BITS)[1]
    raw_high_w = F(3, 16)*root16/roots.root_bounds(5, degree, BITS)[0]+F(1, 16)*root16
    high_w = F(ceil_div(raw_high_w.numerator*scale, raw_high_w.denominator), scale)
    return low_m, low_w, high_m, high_w


def threshold(n, g, degree):
    quotient, remainder = divmod(2*n*g-1, degree)
    return (1 << quotient)*roots.root_bounds(1 << remainder, degree, BITS)[0]


def coefficients(n, book, loss_sums, degree):
    if type(n) is not int or n < 1:
        raise ValueError('Positive public full-group count required')
    ml, wl, mh, wh = moments(book, loss_sums, degree)
    return ml**n/threshold(n, book.g, degree), mh**book.g/ml, wl/ml, (wh/mh-wl/ml)/n


def excess_upper(n, book, loss_sums, a, degree):
    if type(a) is not int or not 0 <= a <= n:
        raise ValueError('Pre-source oracle group count required')
    A, B, u, v = coefficients(n, book, loss_sums, degree)
    return A*B**a*(u+a*v)


@cache
def allocation(n, book, loss_sums, error, degree):
    A, B, u, v = coefficients(n, book, loss_sums, degree)
    slope = (F(1, 4)-error)/n

    def value(a):
        return error+a*slope+A*B**a*(u+a*v)

    def difference(a):
        return slope+A*B**a*((B-1)*(u+a*v)+B*v)

    def curvature(a):
        return (B-1)**2*(u+a*v)+2*B*(B-1)*v

    convex = n <= 1 or min(curvature(0), curvature(n-2)) >= 0
    evaluations = 0
    if convex:
        low, high = 0, n
        while low < high:
            middle = (low+high)//2
            evaluations += 1
            if difference(middle) >= 0:
                high = middle
            else:
                low = middle+1
        a = low
        method = 'exact-discrete-convex-search'
    else:
        a = min(range(n+1), key=lambda x:(value(x), x))
        evaluations = n+1
        method = 'complete-integer-allocation-list'
    raw = value(a)
    return {'a':a, 'degree':degree, 'base':error+a*slope,
            'raw_error_upper':raw, 'error_upper':min(F(1, 2), raw),
            'convex':convex, 'method':method, 'evaluations':evaluations,
            'left_difference':difference(a-1) if a else None,
            'right_difference':difference(a) if a < n else None}


@cache
def select(n, book, loss_sums, error):
    plans = tuple(allocation(n, book, loss_sums, error, d) for d in DEGREES)
    chosen = min(plans, key=lambda p:(p['error_upper'], p['a'], p['degree']))
    return chosen['a'], chosen['degree']
