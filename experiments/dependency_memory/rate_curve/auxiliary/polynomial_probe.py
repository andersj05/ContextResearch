"""Exact polynomial discovery; no paper claim until independently checked."""
from collections import Counter
from fractions import Fraction as F
from functools import reduce
from hashlib import sha256
import json
from math import comb, factorial, gcd
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.dependency_memory.joint_coding_complement import cover
from experiments.dependency_memory.joint_coding import decoder_frontier as f


def trim(p):
    p = list(p)
    while len(p) > 1 and not p[-1]:
        p.pop()
    return tuple(p)


def add(p, q):
    result = [0] * max(len(p), len(q))
    for i, v in enumerate(p):
        result[i] += v
    for i, v in enumerate(q):
        result[i] += v
    return trim(result)


def scale(p, c):
    return trim([c*x for x in p])


def multiply(p, q):
    if not any(p) or not any(q):
        return (0,)
    bound = sum(map(abs, p))*sum(map(abs, q))
    bits = bound.bit_length()+1
    packed_p = sum(c << (bits*i) for i, c in enumerate(p))
    packed_q = sum(c << (bits*i) for i, c in enumerate(q))
    value = packed_p*packed_q
    mask, half = (1 << bits)-1, 1 << (bits-1)
    result = []
    for _ in range(len(p)+len(q)-1):
        c = value & mask
        if c >= half:
            c -= 1 << bits
        result.append(c)
        value = (value-c) >> bits
    assert value == 0
    return trim(result)


def power(p, n):
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
    return trim([c // content for c in p])


def evaluate(p, t):
    result = 0
    for c in reversed(p):
        result = result*t+c
    return result


def relative_profile(table, weights):
    loss = f.loss_matrix(table)
    rows = []
    groups = {}
    for row in loss:
        minimum = min(row)
        coefficients = [0]*13
        for c, l in zip(weights, row):
            coefficients[l-minimum] += c
        z = trim(coefficients)
        groups.setdefault(z, []).append(len(rows))
        rows.append(tuple(l-minimum for l in row))
    assert sum(min(row) for row in loss) == 48
    return rows, groups


def numerators(table, weights):
    rows, groups = relative_profile(table, weights)
    items = tuple(groups.items())
    denominator = product(power(z, 16-len(xs)) for z, xs in items)
    omitted = [product(z for j, (z, _) in enumerate(items) if j != i)
               for i in range(len(items))]
    numerators = []
    for a in range(16):
        n = (0,)
        for i, (_, xs) in enumerate(items):
            h = [0]*13
            for x in xs:
                h[rows[x][a]] += 1
            n = add(n, multiply(trim(h), omitted[i]))
        numerators.append(n)
    return denominator, tuple(sorted(set(numerators)))


def remove_one_roots(p):
    count = 0
    while sum(p) == 0 and any(p):
        q = []
        running = 0
        for c in p[:-1]:
            running += c
            q.append(running)
        assert -q[-1] == p[-1]
        p = trim(q)
        count += 1
    return primitive(p), count


def shift(p, c):
    if not c:
        return p
    n = len(p)-1
    facts = [factorial(i) for i in range(n+1)]
    a = tuple(p[i]*facts[i] for i in range(n, -1, -1))
    b = tuple(c**i*(facts[n]//facts[i]) for i in range(n+1))
    v = multiply(a, b)
    result = []
    for j in range(n+1):
        denominator = facts[j]*facts[n]
        q, remainder = divmod(v[n-j], denominator)
        assert remainder == 0
        result.append(q)
    return trim(result)


def interval_coefficients(p, low, high):
    n = len(p)-1
    l = low.denominator*high.denominator//gcd(low.denominator, high.denominator)
    a, b = int(low*l), int(high*l)
    q = shift(tuple(c*l**(n-i) for i, c in enumerate(p)), a)
    q = q + (0,)*(n+1-len(q))
    q = tuple(c*(b-a)**i for i, c in enumerate(q))
    facts = [factorial(i) for i in range(n+1)]
    v = multiply(tuple(q[i]*facts[n-i] for i in range(n+1)),
                 tuple(facts[n]//facts[i] for i in range(n+1)))
    result = []
    for j in range(n+1):
        denominator = facts[n-j]*facts[n]
        c, remainder = divmod(v[j], denominator)
        assert remainder == 0
        result.append(c)
    return tuple(result)


def main():
    orbits = cover.orbits()
    weights = [primitive(f.nearest_weights(f.loss_matrix(table))) for table, _ in orbits]
    unsigned = orbits[0][0]
    witnesses = [(F(0), F(4,25), weights[0]),
                 (F(4,25), F(1,4), tuple(9 if a in (0,15) else 1 if a.bit_count()==2 else 0 for a in range(16))),
                 (F(1,4), F(1), tuple(1 if a in (0,15) else 0 for a in range(16)))]
    records = []
    for family, ((table, orbit), q) in enumerate(zip(orbits, weights)):
        if not family:
            continue
        start = perf_counter()
        denominator, nums = numerators(table, q)
        print('family', family, 'groups', len(relative_profile(table, q)[1]),
              'columns', len(nums), 'degree', len(denominator)-1, flush=True)
        nums16 = [power(n,16) for n in nums]
        for low, high, u_q in witnesses:
            _, groups = relative_profile(unsigned, u_q)
            u = product(power(z, len(xs)) for z, xs in groups.items())
            left = scale(multiply(denominator, u), 16**16)
            for column, n16 in enumerate(nums16):
                k = add(left, scale(n16, -sum(u_q)**16))
                p, roots = remove_one_roots(k)
                transformed = interval_coefficients(p, low, high)
                bad = [i for i, c in enumerate(transformed) if c < 0]
                record = {'family':family, 'interval':[str(low), str(high)], 'column':column,
                          'degree':len(p)-1, 'roots_at_one':roots,
                          'negative_coefficients':len(bad), 'first_negative':bad[:1],
                          'polynomial_sha256':sha256(str(p).encode()).hexdigest()}
                records.append(record)
                print(record, 'elapsed', round(perf_counter()-start,2), flush=True)
    (ROOT/'build/completion-spectrum/polynomial_probe.json').write_text(json.dumps(records,indent=2)+'\n')


if __name__ == '__main__':
    main()
