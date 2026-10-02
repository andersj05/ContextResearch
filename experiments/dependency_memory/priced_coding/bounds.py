"""Generic fixed-point outward moments and public finite allocation."""
from fractions import Fraction as F
from functools import cache
from math import isqrt

from experiments.dependency_memory.tie_coding import bounds as roots
from experiments.dependency_memory.tie_coding import design as logarithms
from . import design

DEGREES = (8, 16, 32, 64, 128)
BITS = 64


@cache
def default_count(n, book):
    """A separate entropy-slack family, not the finite-bound minimizer."""
    if type(n) is not int or n < 1:
        raise ValueError('Positive public full-group count required')
    precision = 64+8*(book.g+n.bit_length())
    low_hi = design.entropies(book, precision)[1]
    high_hi = book.g*logarithms.entropies(1, precision)[1][1]
    if not low_hi < 2*book.g < high_hi:
        raise ValueError('The fixed book and oracle must straddle rate two')
    margin = 4*(isqrt(n*n.bit_length()-1)+1)
    numerator = n*(2*book.g-low_hi)-margin
    if numerator < 0:
        return 0
    share = numerator/(high_hi-low_hi)
    return min(n, share.numerator//share.denominator)


def limiting_error(book, error, bits=192):
    """Outward enclosure for the actual separate entropy-slack family."""
    lo, hi = design.entropies(book, bits)
    hlo, hhi = (book.g*v for v in logarithms.entropies(1, bits)[1])
    if not lo <= hi < 2*book.g < hlo <= hhi or not F(1, 4) <= error <= F(1, 2):
        raise ValueError('Rate-two interpolation with a valid population loss required')
    lower_share = (2*book.g-hi)/(hhi-hi)
    upper_share = (2*book.g-lo)/(hlo-lo)
    return (error+(F(1, 4)-error)*upper_share,
            error+(F(1, 4)-error)*lower_share)


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
    ml, wl, mh, wh = moments(book, loss_sums, degree)
    u, v = wl/ml, (wh/mh-wl/ml)/n
    return product_scale(n, book.g, a, ml, mh, threshold(n, book.g, degree))*(u+a*v)


def product_scale(n, g, a, ml, mh, target):
    """Cancel the known common powers before constructing a large Fraction."""
    return F(*product_parts(n, g, a, ml, mh, target))


def product_parts(n, g, a, ml, mh, target):
    return (mh.numerator**(g*a)*ml.numerator**(n-a)*target.denominator,
            mh.denominator**(g*a)*ml.denominator**(n-a)*target.numerator)


@cache
def allocation(n, book, loss_sums, error, degree):
    if type(n) is not int or n < 1:
        raise ValueError('Positive public full-group count required')
    ml, wl, mh, wh = moments(book, loss_sums, degree)
    target = threshold(n, book.g, degree)
    B, u, v = mh**book.g/ml, wl/ml, (wh/mh-wl/ml)/n
    slope = (F(1, 4)-error)/n

    def value(a):
        return error+a*slope+product_scale(n, book.g, a, ml, mh, target)*(u+a*v)

    def difference(a):
        return slope+product_scale(n, book.g, a, ml, mh, target)*((B-1)*(u+a*v)+B*v)

    def difference_sign(a):
        # Ordering needs only this integer numerator; do not reduce a huge
        # rational at each binary-search comparison.
        numerator, denominator = product_parts(n, book.g, a, ml, mh, target)
        coefficient = (B-1)*(u+a*v)+B*v
        cross = (slope.numerator*denominator*coefficient.denominator
                 +numerator*coefficient.numerator*slope.denominator)
        return (cross > 0)-(cross < 0)

    def curvature(a):
        return (B-1)**2*(u+a*v)+2*B*(B-1)*v

    convex = n <= 1 or min(curvature(0), curvature(n-2)) >= 0
    evaluations = 0
    if convex:
        low, high = 0, n
        while low < high:
            middle = (low+high)//2
            evaluations += 1
            if difference_sign(middle) >= 0:
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
