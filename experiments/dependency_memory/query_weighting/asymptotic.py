"""Exact weighted supporting bounds; no float optimizer participates.

C67 already proves unsigned dominance at EVERY positive slope. This module
reuses that theorem; it does not newly enumerate final decoder tables. A
single rational q gives t_L=q**m, t_R=q**n, the correct common budget slope
for source-independent query probability p=m/(m+n).
"""
from fractions import Fraction as F
from hashlib import sha256

from experiments.dependency_memory.joint_coding import decoder_frontier as f
from experiments.dependency_memory.rate_spectrum import derive

LOSS = f.loss_matrix(f.UNSIGNED)


def integer_binding(n, d):
    def raw(value):
        return value.to_bytes((value.bit_length()+7)//8, 'big')
    numerator, denominator = raw(n), raw(d)
    return sha256(len(numerator).to_bytes(8, 'big')+numerator+denominator).hexdigest()


def point(m, n, q):
    if (type(m) is not int or type(n) is not int or m <= 0 or n <= 0
            or not isinstance(q, F) or not 0 < q < 1):
        raise ValueError('Positive integer class weights and rational0<q<1 required')
    branches = []
    free_lower = F(0)
    information_upper = F(0)
    distortion = F(0)
    for power in (m, n):
        t = q**power
        weights = derive.unsigned_weights(t)
        numerator, denominator = f.dual_product(LOSS, weights, t)
        _, log_upper = f.log2_bounds(numerator, denominator)
        free = -log_upper/16
        primal = f.primal_bounds(LOSS, weights, t)
        free_lower += free
        information_upper += primal['information_upper']
        distortion += power*primal['distortion']/(m+n)
        branches.append({'power': power, 't': str(t), 'unsigned_weights': list(weights),
                         'supporting_objective_lower': str(free),
                         'information_upper': str(primal['information_upper']),
                         'distortion': str(primal['distortion']),
                         'information_upper_enclosure': f.decimal_enclosure(primal['information_upper'], primal['information_upper'], 12),
                         'distortion_enclosure': f.decimal_enclosure(primal['distortion'], primal['distortion'], 12),
                         'dual_integer_product_sha256': integer_binding(numerator, denominator),
                         'dual_integer_product_numerator_bits': numerator.bit_length(),
                         'dual_integer_product_denominator_bits': denominator.bit_length()})
    log_q_low, _ = f.log2_bounds(q.numerator, q.denominator)
    lower = (free_lower-4)/(-12*(m+n)*log_q_low)
    if not (information_upper < 4 and F(1,4) < lower < distortion
            and distortion-lower < F(2,10**11)):
        raise ValueError('Weighted bound or strict combined coding slack failed')
    return {'p': str(F(m,m+n)), 'weights': [m,n], 'q': str(q), 'branches': branches,
            'combined_information_upper': str(information_upper),
            'strict_combined_rate_slack_lower': str(4-information_upper),
            'distortion_lower': str(lower), 'distortion_upper': str(distortion),
            'limiting_distortion_enclosure': f.decimal_enclosure(lower, distortion, 12),
            'interval_width_upper': str(distortion-lower),
            'finite_lower_scope': 'all even k=2*h with4*h parent bits; arbitrary joint encoders and heterogeneous tables',
            'upper_scope': 'asymptotic separate class coding with strict slack inside2*k bits; no finite code near the limit supplied'}
