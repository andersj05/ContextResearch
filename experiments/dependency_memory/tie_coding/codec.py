"""Only a charged 2*k-bit parent and then one-bit child cross boundaries."""
from math import isqrt
from functools import cache
from . import design
from experiments.dependency_memory.entropy_coding import codec as scalar


@cache
def default_count(n,g=8,multiplier=4):
    if (type(n) is not int or n < 1 or type(g) is not int or g < 1
            or type(multiplier) is not int or multiplier < 1):
        raise ValueError('Positive public count, group size and margin multiplier required')
    bits = 64+8*(g+n.bit_length())
    (_,low_upper),(_,high_upper) = design.entropies(g,bits)
    margin = multiplier*(isqrt(n*n.bit_length()-1)+1)
    numerator = 2*g*n-margin-n*low_upper
    if numerator < 0:
        return 0
    fraction = numerator/(high_upper-low_upper)
    return min(n,fraction.numerator//fraction.denominator)


def count(n,g,a=None):
    if type(n) is not int or n < 1 or type(g) is not int or g < 1:
        raise ValueError('Positive public count and group size required')
    if a is None:
        return default_count(n,g)
    if type(a) is not int or not 0 <= a <= n:
        raise ValueError('Public pre-source oracle count must be inside 0..n')
    return a


def completion(blocks,g):
    if len(blocks)!=g:
        raise ValueError('Exactly one public group required')
    forced = values = 0
    for i,x in enumerate(blocks):
        if type(x) is not int or not 0 <= x < 16:
            raise ValueError('Four-bit sources required')
        weight = x.bit_count()
        if weight!=2:
            forced |= 1 << i
            values |= (weight>2) << i
    return next(w for w in design.prepare(g)[0] if w&forced==values)


def encode(blocks,g=8,a=None,*,diagnostics=False):
    blocks = tuple(blocks)
    if type(g) is not int or g<1 or not blocks or len(blocks)%g:
        raise ValueError('Nonempty source length must be a multiple of public g')
    n,k = len(blocks)//g,len(blocks)
    a = count(n,g,a)
    priority,counts = design.prepare(g)
    low,width = 0,1
    for r in range(a*g):
        word = scalar.response(blocks[r],True)
        index = scalar.WORDS[1].index(word)
        low = 16*low+width*sum(scalar.COUNTS[1][:index])
        width *= scalar.COUNTS[1][index]
    for group in range(a,n):
        word = completion(blocks[group*g:(group+1)*g],g)
        index = priority.index(word)
        low = (1 << (4*g))*low+width*sum(counts[:index])
        width *= counts[index]
    denominator,scale = 1 << (4*k),1 << (2*k)
    j = (low*scale+denominator-1)//denominator
    j += not (j&1)
    regular = j<scale and j*denominator<(low+width)*scale
    parent = (1 << (2*k-1))|((j-1)//2) if regular else 0
    guaranteed = width >= (1 << (2*k+1))
    if guaranteed and not regular:
        raise ArithmeticError('A full spacing interval must contain an odd midpoint')
    if diagnostics:
        return parent,{'regular':regular,'length_guaranteed':guaranteed,
                       'interval_low':low,'interval_width':width,
                       'denominator_power_two':4*k,'oracle_groups':a}
    return parent


def decode_response(parent,block,n,g=8,a=None):
    a = count(n,g,a)
    k = n*g
    if type(parent) is not int or not 0 <= parent < (1 << (2*k)):
        raise ValueError('Parent exceeds charged 2*k-bit capacity')
    if type(block) is not int or not 0 <= block < k:
        raise ValueError('Invalid public queried block')
    flag = 1 << (2*k-1)
    if parent < flag:
        if parent:
            raise ValueError('Only zero is a valid fallback parent')
        return 0
    numerator,denominator = 2*(parent-flag)+1,1 << (2*k)
    priority,counts = design.prepare(g)
    stop = min(block+1,a*g)
    for r in range(stop):
        cumulative = 0
        for word,c in zip(scalar.WORDS[1],scalar.COUNTS[1]):
            if 16*numerator<(cumulative+c)*denominator:
                numerator,denominator = 16*numerator-cumulative*denominator,c*denominator
                break
            cumulative += c
    if block < a*g:
        return word
    for group in range(a,block//g+1):
        cumulative = 0
        for word,c in zip(priority,counts):
            if (1 << (4*g))*numerator<(cumulative+c)*denominator:
                numerator,denominator = (1 << (4*g))*numerator-cumulative*denominator,c*denominator
                break
            cumulative += c
    return 15 if (word >> (block%g))&1 else 0


def update(parent,block,omitted,n,g=8,a=None):
    if type(omitted) is not int or not 0 <= omitted < 4:
        raise ValueError('Invalid public omission')
    return (decode_response(parent,block,n,g,a) >> omitted)&1


def predict(child,block,omitted,query):
    return scalar.predict(child,block,omitted,query)
