"""Exact-root Chernoff upper bounds, never float admission or tail estimates."""
from fractions import Fraction as F
from functools import cache
from . import design


@cache
def root_bounds(value,degree,bits=64):
    if (type(value) is not int or value < 1 or type(degree) is not int or degree<1
            or type(bits) is not int or bits<1):
        raise ValueError('Positive integer root inputs required')
    target = value << (bits*degree)
    low = 1 << ((target.bit_length()-1)//degree)
    high = 1 << ((target.bit_length()+degree-1)//degree)
    while high-low>1:
        middle = (low+high)//2
        if middle**degree<=target:
            low = middle
        else:
            high = middle
    scale = 1 << bits
    return F(low,scale),F(low if low**degree==target else low+1,scale)


@cache
def moment_upper(counts,denominator,degree):
    numerator = sum(root_bounds(c**(degree-1),degree)[1] for c in counts)
    divisor = root_bounds(denominator**(degree-1),degree)[0]
    return numerator/divisor


def tail_upper(n,g,a,degree):
    if (type(n) is not int or n<1 or type(g) is not int or g<1
            or type(a) is not int or not 0<=a<=n
            or type(degree) is not int or degree<2):
        raise ValueError('Invalid public bound parameters')
    _,counts = design.prepare(g)
    low_moment = moment_upper(counts,16**g,degree)
    high_moment = moment_upper((5,1,1,1,1,1,1,5),16,degree)
    quotient,remainder = divmod(2*n*g-1,degree)
    threshold = (1 << quotient)*root_bounds(1 << remainder,degree)[0]
    return min(F(1),high_moment**(a*g)*low_moment**(n-a)/threshold)


def error_bound(n,g,a,degrees=(8,16,32,64,128)):
    base = F(5,16)-F(a,16*n)
    tails = {degree:tail_upper(n,g,a,degree) for degree in degrees}
    degree = min(tails,key=lambda d:(tails[d],d))
    return {'base':base,'tail_upper':tails[degree],'error_upper':min(F(1,2),base+tails[degree]),
            'best_degree':degree,'all_tail_bounds':tails}
