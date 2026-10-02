"""Outward Chernoff bounds weight overflow by its actual excess loss."""
from collections import defaultdict
from fractions import Fraction as F
from functools import cache
from itertools import product

from experiments.dependency_memory.tie_coding import design, bounds as roots

GROUPS = (1, 2, 3, 4, 6, 8)
DEGREES = (8, 16, 32, 64, 128)


def parameters(n, g, a=None):
    if type(n) is not int or n < 1 or type(g) is not int or g not in GROUPS:
        raise ValueError('Positive public group count and a supported public group size required')
    if a is not None and (type(a) is not int or not 0 <= a <= n):
        raise ValueError('Public oracle group count must be in 0..n')


@cache
def loss_weights(g):
    """Integer total L(x,0)-L(x,chosen) in each constant-response cell."""
    parameters(1, g)
    priority, counts = design.prepare(g)
    delta = defaultdict(int)
    observed = defaultdict(int)
    for status in product(range(3), repeat=g):
        forced = sum((s != 2) << r for r, s in enumerate(status))
        values = sum((s == 1) << r for r, s in enumerate(status))
        mass = 5**forced.bit_count()*6**(g-forced.bit_count())
        word = next(w for w in priority if w & forced == values)
        # Among forced-one sources, four weight-three inputs save six
        # routed errors and one weight-four input saves twelve: 36/5.
        excess = F(36*values.bit_count()*mass, 5)
        if excess.denominator != 1:
            raise ArithmeticError('An exact source category has noninteger loss mass')
        observed[word] += mass
        delta[word] += int(excess)
    if tuple(observed[w] for w in priority) != counts:
        raise ArithmeticError('Independent source categories disagree with public counts')
    losses = tuple(delta[w] for w in priority)
    if sum(losses) != 12*g*16**g*F(3, 16):
        raise ArithmeticError('Fallback gain must equal 1/2-5/16')
    return losses


@cache
def moments(g, degree):
    parameters(1, g)
    if type(degree) is not int or degree not in DEGREES:
        raise ValueError('One of the five declared root degrees required')
    _, counts = design.prepare(g)
    population = 16**g
    low_m = roots.moment_upper(counts, population, degree)
    root_n = roots.root_bounds(population, degree)[1]
    low_w = sum(F(delta, 12*g*population)*root_n/roots.root_bounds(c, degree)[0]
                for c, delta in zip(counts, loss_weights(g)))
    high_m = roots.moment_upper((5, 1, 1, 1, 1, 1, 1, 5), 16, degree)
    # Oracle excess sums are 36 on the two size-five fibers and 12 on
    # the six balanced singleton fibers. They do not depend on a fixed
    # fallback response; production uses zero.
    high_root = roots.root_bounds(16, degree)[1]
    high_w = F(3, 16)*high_root/roots.root_bounds(5, degree)[0]+F(1, 16)*high_root
    return low_m, low_w, high_m, high_w


def threshold(n, g, degree):
    quotient, remainder = divmod(2*n*g-1, degree)
    return (1 << quotient)*roots.root_bounds(1 << remainder, degree)[0]


def excess_upper(n, g, a, degree):
    parameters(n, g, a)
    ml, wl, mh, wh = moments(g, degree)
    total = F(0)
    if a:
        total += F(a, n)*wh*mh**(a*g-1)*ml**(n-a)
    if a < n:
        total += F(n-a, n)*wl*ml**(n-a-1)*mh**(a*g)
    return total/threshold(n, g, degree)


def bound(n, g, a):
    parameters(n, g, a)
    base = F(5, 16)-F(a, 16*n)
    values = {degree:excess_upper(n, g, a, degree) for degree in DEGREES}
    degree = min(values, key=lambda d:(values[d], d))
    return {'base':base, 'excess_upper':values[degree],
            'error_upper':min(F(1, 2), base+values[degree]),
            'degree':degree, 'all_excess_uppers':values}


@cache
def allocation(n, g, degree):
    """Exact discrete convex minimization of one outward bound over every a."""
    parameters(n, g)
    ml, wl, mh, wh = moments(g, degree)
    A = ml**n/threshold(n, g, degree)
    B = mh**g/ml
    u = wl/ml
    v = (wh/mh-u)/n
    if not (B > 1 and u >= 0 and v >= 0):
        raise ArithmeticError('The checked sufficient convexity conditions fail')

    def difference(a):
        return -F(1, 16*n)+A*B**a*((B-1)*(u+a*v)+B*v)

    low, high = 0, n
    evaluations = 0
    while low < high:
        middle = (low+high)//2
        evaluations += 1
        if difference(middle) >= 0:
            high = middle
        else:
            low = middle+1
    a = low
    base = F(5, 16)-F(a, 16*n)
    raw = base+A*B**a*(u+a*v)
    left = difference(a-1) if a else None
    right = difference(a) if a < n else None
    if (left is not None and left >= 0) or (right is not None and right < 0):
        raise ArithmeticError('Allocation is not the smallest discrete minimum')
    return {'a':a, 'degree':degree, 'base':base, 'raw_error_upper':raw,
            'error_upper':min(F(1, 2), raw), 'difference_before':left,
            'difference_after':right, 'binary_comparisons':evaluations,
            'B':B, 'u':u, 'v':v}


@cache
def select(n, g=8):
    parameters(n, g)
    plans = tuple(allocation(n, g, d) for d in DEGREES)
    selected = min(plans, key=lambda p:(p['error_upper'], p['a'], p['degree']))
    return selected['a'], selected['degree']
