"""Integer polynomial arithmetic and an exact interval-positivity certificate.

Coefficients use ascending powers. Kronecker substitution speeds convolution;
signed coefficients are recovered in balanced base digits with a proven bound.
The interval transform uses a separate Horner/Pascal recurrence, no optimizer,
floating point, logarithm or external algebra package.
"""
from functools import reduce
from math import gcd


def trim(p):
    p = list(p)
    while len(p) > 1 and not p[-1]:
        p.pop()
    return tuple(p)


def add(p, q):
    result = [0]*max(len(p), len(q))
    for i, value in enumerate(p):
        result[i] += value
    for i, value in enumerate(q):
        result[i] += value
    return trim(result)


def scale(p, c):
    return trim([c*value for value in p])


def multiply(p, q):
    if not any(p) or not any(q):
        return (0,)
    # Every product coefficient has absolute value <= ||p||_1 ||q||_1.
    # Base > 2*bound ensures that balanced decoding cannot carry ambiguously.
    bound = sum(map(abs, p))*sum(map(abs, q))
    bits = bound.bit_length()+1
    packed_p = sum(value << (bits*i) for i, value in enumerate(p))
    packed_q = sum(value << (bits*i) for i, value in enumerate(q))
    value = packed_p*packed_q
    base, half = 1 << bits, 1 << (bits-1)
    mask = base-1
    result = []
    for _ in range(len(p)+len(q)-1):
        coefficient = value & mask
        if coefficient >= half:
            coefficient -= base
        result.append(coefficient)
        value = (value-coefficient) >> bits
    if value:
        raise ArithmeticError('Polynomial product exceeded its digit bound')
    return trim(result)


def power(p, n):
    if type(n) is not int or n < 0:
        raise ValueError('Nonnegative integer polynomial power required')
    result = (1,)
    while n:
        if n & 1:
            result = multiply(result, p)
        n >>= 1
        if n:
            p = multiply(p, p)
    return result


def product(values):
    result = (1,)
    for p in values:
        result = multiply(result, p)
    return result


def primitive(p):
    content = reduce(gcd, p)
    if not content:
        raise ValueError('Zero polynomial has no primitive normalization')
    return trim([value//content for value in p]), content


def evaluate(p, t):
    result = 0
    for coefficient in reversed(p):
        result = result*t+coefficient
    return result


def remove_one_roots(p):
    """K = positive_content * (1-t)**roots * primitive_remainder."""
    if not any(p):
        raise ArithmeticError('Strict comparison polynomial cannot vanish')
    roots = 0
    while sum(p) == 0:
        result, running = [], 0
        for coefficient in p[:-1]:
            running += coefficient
            result.append(running)
        if not result or -result[-1] != p[-1]:
            raise ArithmeticError('Inexact division by 1-t')
        p = trim(result)
        roots += 1
    remainder, content = primitive(p)
    return remainder, roots, content


def interval_coefficients(p, low, high):
    """Coefficients of L**n*(1+v)**n*p((A+B*v)/(L*(1+v))).

    low=A/L, high=B/L. A nonzero polynomial with nonnegative transformed
    coefficients is positive for low<t<high. Positive first/last coefficients
    also certify the endpoints. This is a standard Bernstein/Mobius test.
    """
    if not 0 <= low < high <= 1:
        raise ValueError('Expected a nonempty rational interval in [0,1]')
    denominator = low.denominator*high.denominator//gcd(low.denominator, high.denominator)
    a, b = int(low*denominator), int(high*denominator)
    result, row, denominator_power = [p[-1]], [1], 1
    for coefficient in reversed(p[:-1]):
        row = [1]+[row[i-1]+row[i] for i in range(1, len(row))]+[1]
        denominator_power *= denominator
        new = [coefficient*denominator_power*value for value in row]
        for i, value in enumerate(result):
            new[i] += a*value
            new[i+1] += b*value
        result = new
    return tuple(result)
