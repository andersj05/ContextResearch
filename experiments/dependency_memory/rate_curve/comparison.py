"""Clear the exact dual inequalities into integer comparison polynomials."""
from fractions import Fraction as F
from functools import lru_cache

from experiments.dependency_memory.joint_coding import decoder_frontier as frontier
from experiments.dependency_memory.joint_coding_complement import cover
from experiments.dependency_memory.rate_curve import polynomials as p


WITNESSES = (
    (F(0), F(4,25), tuple(5 if a in (0,15) else 1 if a.bit_count()==2 else 0 for a in range(16))),
    (F(4,25), F(1,4), tuple(9 if a in (0,15) else 1 if a.bit_count()==2 else 0 for a in range(16))),
    (F(1,4), F(1), tuple(1 if a in (0,15) else 0 for a in range(16))),
)


def relative_profile(table, weights):
    """Subtract each source's oracle loss; group equal integer partitions."""
    if len(weights) != 16 or any(type(w) is not int or w < 0 for w in weights) or not sum(weights):
        raise ValueError('Sixteen nonnegative integer weights required')
    loss = frontier.loss_matrix(table)
    if any((frontier.PAIRS[index][0]^frontier.PAIRS[index][1]) != 7 for index in table):
        raise ValueError('Only complementary endpoint tables are in this comparison')
    rows, groups = [], {}
    for row in loss:
        minimum = min(row)
        coefficients = [0]*13
        for weight, cost in zip(weights, row):
            coefficients[cost-minimum] += weight
        z = p.trim(coefficients)
        # Any nonzero witness has z_x(t)>0 for t>0. Its relative partition
        # may have zero constant coefficient when oracle words are inactive.
        groups.setdefault(z, []).append(len(rows))
        rows.append(tuple(cost-minimum for cost in row))
    if sum(min(row) for row in loss) != 48:
        raise ValueError('This comparison uses complementary four-bit tables')
    return tuple(rows), tuple((z, tuple(xs)) for z, xs in groups.items())


def dual_polynomials(table, weights):
    """G_a=t**48*N_a**16/(16**16*denominator), for each of all 16 words.

    Source classes j have partition Z_j and multiplicity c_j. The denominator
    is product Z_j**(16-c_j), N_a=sum H_ja*product_(l!=j) Z_l. The witness
    normalizer cancels. No column outside the witness support is dropped.
    """
    rows, groups = relative_profile(table, weights)
    denominator = p.product(p.power(z, 16-len(xs)) for z, xs in groups)
    omitted = [p.product(z for j, (z, _) in enumerate(groups) if j != i)
               for i in range(len(groups))]
    columns = {}
    for a in range(16):
        numerator = (0,)
        for i, (_, xs) in enumerate(groups):
            h = [0]*13
            for x in xs:
                h[rows[x][a]] += 1
            numerator = p.add(numerator, p.multiply(p.trim(h), omitted[i]))
        columns.setdefault(numerator, []).append(a)
    return denominator, tuple((n, tuple(columns[n])) for n in sorted(columns))


@lru_cache(maxsize=1)
def cases():
    """48 distinct polynomials cover five families, 16 words and three intervals."""
    families = cover.orbits()
    if len(families) != 6 or sum(len(orbit) for _, orbit in families) != 256:
        raise ArithmeticError('Complementary decoder cover changed')
    result = []
    for family, (table, orbit) in enumerate(families):
        if table == frontier.UNSIGNED:
            continue
        weights, _ = p.primitive(frontier.nearest_weights(frontier.loss_matrix(table)))
        # Distribution weights are sixteen-dimensional, even with a zero tail.
        weights = weights+(0,)*(16-len(weights))
        denominator, columns = dual_polynomials(table, weights)
        powers = tuple(p.power(n,16) for n, _ in columns)
        for interval, (low, high, unsigned_weights) in enumerate(WITNESSES):
            _, groups = relative_profile(frontier.UNSIGNED, unsigned_weights)
            unsigned_product = p.product(p.power(z, len(xs)) for z, xs in groups)
            left = p.scale(p.multiply(denominator, unsigned_product), 16**16)
            for column, ((numerator, words), n16) in enumerate(zip(columns, powers)):
                raw = p.add(left, p.scale(n16, -sum(unsigned_weights)**16))
                polynomial, roots, content = p.remove_one_roots(raw)
                result.append({'family':family, 'table':table, 'orbit_size':len(orbit),
                               'weights':weights, 'interval':interval, 'low':low, 'high':high,
                               'column_group':column, 'words':words, 'denominator':denominator,
                               'numerator':numerator, 'unsigned_product':unsigned_product,
                               'unsigned_weights':unsigned_weights, 'raw':raw,
                               'polynomial':polynomial, 'roots_at_one':roots, 'content':content})
    if len(result) != 48:
        raise ArithmeticError('Expected 48 distinct comparison polynomials')
    return tuple(result)
