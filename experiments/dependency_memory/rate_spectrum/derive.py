"""Parametric unsigned-decoder reduction, using rational arithmetic only."""
from fractions import Fraction as F
from math import comb, isqrt

# Coefficients are ascending powers of u=t**2.
TRANSITION = (1, -11, -1, -4, -2, -4, -1, -11, 1)
TRANSFORMED = (1, -3, -50, -185, -352, -401, -283, -128, -32)
CLASS_WEIGHTS = (F(1, 8), F(1, 2), F(3, 8))
WEIGHT_TOTAL = 12 * 10**15


def polynomial(coefficients, x):
    result = F(0)
    for c in reversed(coefficients):
        result = result*x+c
    return result


def classes(t):
    """Kernel averages for constant, balanced and odd reproduction words.

    Source classes have weights 0/4, 1/3 and 2, with masses 1/8, 1/2, 3/8.
    """
    if not isinstance(t, F) or not 0 < t < 1:
        raise ValueError('Expected 0 < t < 1')
    a = ((1+t**12)/2, (t**3+t**9)/2, t**6)
    b = (t**6, (t**5+t**7)/2, (t**4+4*t**6+t**8)/6)
    c = ((t**3+t**9)/2, (3*t**4+2*t**6+3*t**8)/8, (t**5+t**7)/2)
    return a, b, c


def dominating_mix(t):
    return (1-t+t*t)/(1+t)**2


def log_partition_derivative(t, p):
    a, b, _ = classes(t)
    return sum(w*(y-x)/(x+(y-x)*p) for w, x, y in zip(CLASS_WEIGHTS, a, b))


def balanced_mass_bracket(t, steps=90):
    """Enclose the unique optimum after odd-word domination and symmetrization."""
    if type(steps) is not int or steps < 1:
        raise ValueError('Positive integer bisection steps required')
    classes(t)
    if polynomial(TRANSITION, t*t) <= 0:
        return F(0), F(0)
    low, high = F(0), F(1)
    for _ in range(steps):
        middle = (low+high)/2
        if log_partition_derivative(t, middle) > 0:
            low = middle
        else:
            high = middle
    return low, high


def unsigned_weights(t):
    """A nearby rational witness; the certificate charges its dual residual."""
    low, _ = balanced_mass_bracket(t)
    scaled = low*WEIGHT_TOTAL/6
    middle = scaled.numerator//scaled.denominator
    constant = (WEIGHT_TOTAL-6*middle)//2
    return tuple(constant if a in (0, 15) else middle if a.bit_count() == 2 else 0
                 for a in range(16))


def transition_bracket(steps=90, places=12):
    low, high = F(0), F(1)
    for _ in range(steps):
        middle = (low+high)/2
        if polynomial(TRANSITION, middle) > 0:
            low = middle
        else:
            high = middle
    scale = 10**places
    lower = isqrt(low.numerator*scale**2//low.denominator)
    upper = isqrt(high.numerator*scale**2//high.denominator)+1
    return {'u': (low, high), 't': (F(lower, scale), F(upper, scale))}


def algebra_record():
    degree = len(TRANSITION)-1
    transformed = tuple(sum(TRANSITION[i]*comb(degree-i, j-i) for i in range(j+1))
                        for j in range(degree+1))
    if transformed != TRANSFORMED:
        raise ArithmeticError('Transition polynomial transformation changed')
    bounds = transition_bracket()
    return {'transition_polynomial_ascending': list(TRANSITION),
            'positive_line_transform_ascending': list(transformed),
            'u_root_bracket': [str(x) for x in bounds['u']],
            't_root_bracket': [str(x) for x in bounds['t']],
            'odd_domination_class0_positive_factor': [1, 1, 2, 4, 2, 1, 1],
            'odd_domination_class1_positive_factor': [4, 1, 4],
            'endpoint_one_positive_factor': [1, 6, 20, 42, 20, 6, 1],
            'restricted_scope': 'all 0<t<1 for the fixed unsigned decoder; not all-decoder optimality at untested rates'}
