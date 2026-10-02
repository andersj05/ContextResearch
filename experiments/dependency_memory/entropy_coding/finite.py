"""Exact binomial overflow and conditional excess-loss upper bounds.

U counts balanced oracle signatures, V counts upper two-word outputs. The
length guarantee depends only on U,V, while the actual arithmetic-grid success
can also depend on sequence order. We bound failure by the length event, not
claim equality. Every per-source fallback excess is nonnegative.
"""
from fractions import Fraction as F
from functools import cache
from hashlib import sha256

from . import codec


def binomial_weights(n,yes,no):
    if type(n) is not int or n < 0:
        raise ValueError('Nonnegative binomial count required')
    values = [no**n]
    for u in range(n):
        numerator = values[-1]*(n-u)*yes
        denominator = (u+1)*no
        value,remainder = divmod(numerator,denominator)
        if remainder:
            raise ArithmeticError('Binomial recurrence must divide exactly')
        values.append(value)
    if sum(values) != (yes+no)**n:
        raise ArithmeticError('Binomial weights do not cover their population')
    return values


def integer_digest(value):
    return sha256(value.to_bytes(max(1,(value.bit_length()+7)//8),'big')).hexdigest()


@cache
def bound(k,a=None):
    a = codec.count(k,a)
    b = k-a
    weights_u = binomial_weights(a,3,5)
    weights_v = binomial_weights(b,5,11)
    tail,moment = [0]*(a+2),[0]*(a+2)
    for u in range(a,-1,-1):
        tail[u] = tail[u+1]+weights_u[u]
        moment[u] = moment[u+1]+u*weights_u[u]
    total = 1 << (3*a+4*b)
    threshold = 1 << (2*k+1)
    # Product = 5**(a-u+v) * 11**(b-v); U,V increasing only
    # decreases interval length. Follow the exact descending frontier.
    u,product = a,11**b
    failures = excess_numerator = 0
    cutoffs = []
    for v,weight in enumerate(weights_v):
        if u >= 0:
            while u >= 0 and product < threshold:
                u -= 1
                product *= 5
        cutoffs.append(u)
        failures += weight*tail[u+1]
        excess_numerator += weight*((18*a+36*v)*tail[u+1]-8*moment[u+1])
        if v < b and u >= 0:
            product,remainder = divmod(product,11)
            if remainder:
                raise ArithmeticError('Frontier update must divide its remaining power of eleven')
            product *= 5
    base = F(5,16)-F(a,16*k)
    excess = F(excess_numerator,60*k*total)
    if not (0 <= failures <= total and 0 <= excess <= F(failures,total)):
        raise ArithmeticError('Overflow/excess masses left their probability bound')
    return {'k': k, 'oracle_blocks': a, 'two_word_blocks': b,
            'base_error': base, 'failure_event_upper_probability': F(failures,total),
            'conditional_excess_upper': excess, 'error_upper': base+excess,
            'total_binomial_mass_power_two': 3*a+4*b,
            'bad_mass_numerator_sha256': integer_digest(failures),
            'excess_numerator_sha256': integer_digest(excess_numerator),
            'good_u_max_by_v': tuple(cutoffs),
            'full_source_population_size_power_two': 4*k,
            'binomial_cells_represented': (a+1)*(b+1),
            'frontier_steps': len(cutoffs)}
