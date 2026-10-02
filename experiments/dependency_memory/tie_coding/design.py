"""Public weighted-cover design and outward rational entropy bounds."""
from functools import cache
from fractions import Fraction as F
from itertools import product


@cache
def prepare(g):
    if type(g) is not int or g < 1:
        raise ValueError('Positive public group size required')
    patterns = []
    by_word = [[] for _ in range(1 << g)]
    remaining = [11**g]*(1 << g)
    for status in product(range(3), repeat=g):
        forced = sum((s != 2) << i for i,s in enumerate(status))
        values = sum((s == 1) << i for i,s in enumerate(status))
        free = ((1 << g)-1)^forced
        weight = 5**forced.bit_count()*6**(g-forced.bit_count())
        compatible = []
        subset = free
        while True:
            compatible.append(values | subset)
            if not subset:
                break
            subset = (subset-1)&free
        index = len(patterns)
        patterns.append((weight,compatible))
        for word in compatible:
            by_word[word].append(index)
    assigned = [False]*len(patterns)
    used = [False]*(1 << g)
    priority,counts = [],[]
    for _ in range(1 << g):
        word = max((w for w in range(1 << g) if not used[w]),
                   key=lambda w:(remaining[w],-w))
        priority.append(word)
        counts.append(remaining[word])
        used[word] = True
        for index in by_word[word]:
            if assigned[index]:
                continue
            assigned[index] = True
            weight,compatible = patterns[index]
            for w in compatible:
                remaining[w] -= weight
    if not (all(assigned) and sum(counts)==16**g
            and all(c >= 5**g for c in counts)
            and counts == sorted(counts,reverse=True)):
        raise ArithmeticError('Weighted cover failed its exact mass invariants')
    return tuple(priority),tuple(counts)


def ceil_div(n,d):
    return -(-n//d)


def ln_unit(n,d,bits):
    """Bounds on 2**bits ln(n/d), 1<=n/d<=2, via the atanh series."""
    if not 0 < d <= n <= 2*d:
        raise ValueError('Expected a normalized positive ratio')
    scale = 1 << bits
    terms = (bits+8)//2
    if n==d:
        return 0,0
    low,high = (n-d)*scale//(n+d),ceil_div((n-d)*scale,n+d)
    square_lo,square_hi = low*low//scale,ceil_div(high*high,scale)
    p_lo,p_hi = low,high
    total_lo = total_hi = 0
    for j in range(terms):
        total_lo += p_lo//(2*j+1)
        total_hi += ceil_div(p_hi,2*j+1)
        p_lo,p_hi = p_lo*square_lo//scale,ceil_div(p_hi*square_hi,scale)
    return 2*total_lo,2*total_hi+ceil_div(scale,3**(2*terms))


@cache
def log2_bounds(n,bits):
    if type(n) is not int or n < 1 or type(bits) is not int or bits < 32:
        raise ValueError('Positive integer and at least 32 public precision bits required')
    power = n.bit_length()-1
    low,high = ln_unit(n,1 << power,bits)
    ln2_lo,ln2_hi = ln_unit(2,1,bits)
    return power+F(low,ln2_hi),power+F(high,ln2_lo)


@cache
def entropies(g,bits):
    _,counts = prepare(g)
    denominator = 16**g
    bounds = {c:log2_bounds(c,bits) for c in set(counts)}
    low = 4*g-sum(F(c,denominator)*bounds[c][1] for c in counts)
    high = 4*g-sum(F(c,denominator)*bounds[c][0] for c in counts)
    log5lo,log5hi = log2_bounds(5,bits)
    oracle = (g*(4-F(10,16)*log5hi),g*(4-F(10,16)*log5lo))
    return (low,high),oracle


def growing_group(n):
    if type(n) is not int or n < 1:
        raise ValueError('Positive public group count required')
    return max(1,n.bit_length()//4)


def pack_tables(g):
    words,counts = prepare(g)
    value = 0
    for word,c in zip(words,counts):
        value = (value << g)|word
        value = (value << (4*g))|c
    payload_bits = len(words)*5*g
    return value.to_bytes((payload_bits+7)//8,'big')
