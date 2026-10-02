"""Conservative analytic proximity bounds, not executed large codebooks."""
from fractions import Fraction as F

# Immutable C34 rational-channel upper bound, rechecked by the certificate.
CHANNEL_ERROR_UPPER = F(2618989801,10**10)


def proximity(g,h):
    if type(g) is not int or g < 1:
        raise ValueError('Expected a positive group size')
    if type(h) is not int or h < 2 or h&(h-1):
        raise ValueError('Mixture inverse must be a power of two >=2')
    log_h = h.bit_length()-1
    mixed_error = (1-F(1,h))*CHANNEL_ERROR_UPPER+F(1,2*h)
    variance = F((5+log_h)**2+1,4)
    # Truncating a large positive exponent only enlarges the upper bound.
    exponent = min(80,g//(2*h))
    information_and_loss_tail = variance*h*h/g
    rounded_threshold = F(1,12*g)
    covering_tail = F(5,1 << exponent)
    raw = mixed_error+F(1,h)+rounded_threshold+information_and_loss_tail+covering_tail
    return {'mixed_error_upper':mixed_error,'loss_slack':F(1,h),
            'threshold_rounding':rounded_threshold,
            'chebyshev_tail':information_and_loss_tail,
            'covering_tail':covering_tail,'exponential_bound_bits':exponent,
            'unclipped_upper':raw,'upper':min(F(1,2),raw)}


def tiled_error(k,g,group_error):
    if type(k) is not int or type(g) is not int or not 1 <= g <= k:
        raise ValueError('Expected a legal public length/group size')
    remainder = k%g
    return ((k-remainder)*group_error+remainder*F(9,32))/k
