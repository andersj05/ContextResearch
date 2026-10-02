"""Exact finite prior curves using a separate three-line envelope formulation."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
import json

from experiments.dependency_memory.conditional_coding import certificate as component
from experiments.dependency_memory.conditional_coding import codec as six

SOURCE_PAIRS = 16**6
HALF_OUTCOMES = 36*SOURCE_PAIRS
POINTS = (F(0), F(1,10), F(1,4), F(1,3), F(2,5), F(1,2), F(3,5), F(2,3), F(3,4), F(9,10), F(1))


@cache
def terms():
    columns, _, minima, changed, groups, _ = component.partition(six.BASE, six.OVERRIDES)
    if changed != [52, 58] or len(groups) != 16:
        raise ValueError('Selected conditional structure changed')
    unmodified = [b for b in range(64) if b not in changed]
    right = Counter((min(row[b] for b in unmodified), row[52], row[58]) for row in columns)
    records = []
    for (d52, d58), xs in sorted(groups.items()):
        for (u, r52, r58), count in sorted(right.items()):
            # Cost = p*base_left + min_b(p*delta_left + (1-p)*right).
            # All unmodified b collapse to the least right cost. Identical
            # affine lines can be removed for loss; their message ties cannot.
            lines = tuple(sorted({(u, -u), (r52, d52-r52), (r58, d58-r58)}))
            records.append((len(xs)*count, lines))
    if sum(w for w, _ in records) != SOURCE_PAIRS:
        raise ValueError('Compressed terms omitted source pairs')
    return sum(minima)*4096, tuple(records), len(right)


def direct_value(p):
    if not isinstance(p, F) or not 0 <= p <= 1:
        raise ValueError('Expected a rational source-independent class probability')
    base, records, _ = terms()
    return (p*base + sum(weight*min(F(a)+p*b for a, b in lines)
                         for weight, lines in records))/HALF_OUTCOMES


@cache
def envelope():
    """Every exact segment on0..1, not a numerical probability grid.

    Each term has at most three integer affine lines. All pair intersections
    split its domain; its selected line on every open cell is identified at
    a rational midpoint. Endpoint continuity preserves tie costs. Sum the
    weighted changes, retaining only actual aggregate changes.
    """
    base, records, histogram_types = terms()
    intercept, slope = F(0), F(base)
    events = defaultdict(lambda: [F(0), F(0)])
    pair_crossings = 0
    for weight, lines in records:
        cuts = {F(0), F(1)}
        for i, (a, b) in enumerate(lines):
            for c, d in lines[i+1:]:
                if b != d:
                    crossing = F(c-a, b-d)
                    if 0 < crossing < 1:
                        cuts.add(crossing)
                        pair_crossings += 1
        cuts = sorted(cuts)
        previous = None
        for left, right in zip(cuts, cuts[1:]):
            middle = (left+right)/2
            chosen = min(lines, key=lambda line: F(line[0])+middle*line[1])
            if previous is None:
                intercept += weight*chosen[0]
                slope += weight*chosen[1]
            elif chosen != previous:
                events[left][0] += weight*(chosen[0]-previous[0])
                events[left][1] += weight*(chosen[1]-previous[1])
            previous = chosen
    segments, start = [], F(0)
    for point, (di, ds) in sorted(events.items()):
        if not di and not ds:
            continue
        if di+point*ds != 0 or ds >= 0:
            raise ValueError('Envelope changes must preserve continuity and concavity')
        segments.append({'left': str(start), 'right': str(point),
                         'intercept': str(intercept/HALF_OUTCOMES), 'slope': str(slope/HALF_OUTCOMES)})
        intercept += di
        slope += ds
        start = point
    segments.append({'left': str(start), 'right': '1',
                     'intercept': str(intercept/HALF_OUTCOMES), 'slope': str(slope/HALF_OUTCOMES)})
    return {'source_pairs_covered': SOURCE_PAIRS, 'right_histogram_types': histogram_types,
            'weighted_terms': len(records), 'pair_intersections_checked': pair_crossings,
            'segments': segments, 'scope': 'known-before-X prior and fixed C69 book; exact minimum of affine losses'}


def value_from_segments(p):
    for row in envelope()['segments']:
        if F(row['left']) <= p <= F(row['right']):
            return F(row['intercept']) + p*F(row['slope'])
    raise ValueError('Probability is outside the covered interval')


def frozen_and_balanced():
    data = json.loads(component.OUTPUT.read_text(encoding='utf-8'))
    left = sum(map(sum, data['six_block']['branch_errors'][:3]))
    right = sum(map(sum, data['six_block']['branch_errors'][3:]))
    base = data['component']['errors']*4096
    if (left, right, base) != (165852393, 166005255, 165945344):
        raise ValueError('Source-bound C69 half counts changed')
    threshold = F(right-base, base-left+right-base)
    paired = F(left+right, 2*HALF_OUTCOMES)
    return {'frozen_uniform_encoder_left_error': str(F(left, HALF_OUTCOMES)),
            'frozen_uniform_encoder_right_error': str(F(right, HALF_OUTCOMES)),
            'frozen_encoder_beats_refined_product_iff_p_greater_than': str(threshold),
            'balanced_pair_left_error': str(paired), 'balanced_pair_right_error': str(paired),
            'balanced_pair_any_p_error': str(paired), 'refined_product_any_p_error': str(F(base, HALF_OUTCOMES)),
            'balanced_pair_parent_bits': 24, 'balanced_pair_child_bits': 1,
            'balanced_pair_extra_orientation_instance_bits': 0,
            'public_label_payload_bytes': len(six.pack_tables()),
            'scope': 'derived opposite-orientation product for k=12*n and uniform within-class queries; p fixed independently of X; no large-population actor enumeration'}


def controls(p):
    return {'refined_six_six': F(40514,147456),
            'three_nine': F(1,4)+p/F(16),
            'nine_three': F(5,16)-p/F(16)}
