"""Independent exact finite checks, using no native search or model services.

The three-block replacement screen uses direct distance differences, rather
than the native histogram algorithm. Six-block grading groups left sources
by their vector of relative left minima: right decisions are identical inside
such a group, including ties. The weighted actor route count is distinguished
from the smaller number of actor calls physically executed.
"""
from collections import defaultdict
from fractions import Fraction
from functools import cache
import hashlib
import json
from pathlib import Path
import struct

from . import codec

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DISCOVERY = HERE / 'discovery'
OUTPUT = HERE.parent / 'results/conditional_six_block_2026-10-02.json'


@cache
def direct_losses():
    # Evaluator truth strings and explicit branch decisions; no popcount.
    bits = [tuple(map(int, reversed(f'{x:04b}'))) for x in range(16)]
    return tuple(tuple(sum(bits[x][j] != bits[c][o]
                           for o in range(4) for j in range(4) if j != o)
                       for c in range(16)) for x in range(16))


@cache
def cost_rows():
    one = direct_losses()
    nibbles = tuple((c & 15, (c >> 4) & 15, c >> 8) for c in range(4096))
    rows = []
    for x in range(4096):
        a, b, c = one[x & 15], one[(x >> 4) & 15], one[x >> 8]
        rows.append(bytes(a[i] + b[j] + c[k] for i, j, k in nibbles))
    return tuple(rows)


@cache
def nearest(base):
    columns = tuple(tuple(row[c] for c in base) for row in cost_rows())
    winners, minima, margins = [], [], []
    for row in columns:
        value = min(row)
        a = row.index(value)
        second = min(row[b] for b in range(64) if b != a)
        winners.append(a)
        minima.append(value)
        margins.append(second - value)
    return columns, tuple(winners), tuple(minima), tuple(margins)


@cache
def single_word_screen(base):
    """All 64*4096 fixed-decoder replacements, including ties and duplicates.

    Adding candidate c saves max(0,d(x)-L(x,c)) on every source. Removing a
    loses min(delta(x),max(0,L(x,c)-d(x))) only on sources whose old nearest
    codeword is uniquely a. These cases partition the exact new-minimum loss.
    """
    _, winners, minima, margins = nearest(base)
    gained = [0] * 4096
    penalties = [[0] * 4096 for _ in range(64)]
    for x, row in enumerate(cost_rows()):
        value, margin = minima[x], margins[x]
        penalty = penalties[winners[x]]
        for c, distance in enumerate(row):
            delta = distance - value
            if delta < 0:
                gained[c] -= delta
            elif margin and delta > 0:
                penalty[c] += min(margin, delta)
    best_by_slot, selected, maximum = [], None, 0
    digest = hashlib.sha256()
    positive = 0
    for a in range(64):
        scores = [gained[c] - penalties[a][c] for c in range(4096)]
        digest.update(struct.pack('<4096i', *scores))
        positive += sum(v > 0 for v in scores)
        gain = max(scores)
        c = scores.index(gain) if gain > 0 else base[a]
        best_by_slot.append([c, gain])
        if gain > maximum:
            selected, maximum = [a, c], gain
    return {'errors': sum(minima), 'candidate_replacements': 262144,
            'positive_gain_candidates': positive, 'maximum_gain': maximum,
            'selected': selected, 'best_by_slot': best_by_slot,
            'all_signed_gain_scores_sha256': digest.hexdigest(),
            'score_encoding': 'slot order0..63, candidate0..4095; signed int32 little endian',
            'locality_scope': 'one response triple at a time in the fixed unsigned decoder family'}


def grade_triple(base):
    """All 147456 physical delayed actor routes of the stronger component."""
    _, winners, minima, _ = nearest(base)
    errors, branches = 0, [[0]*4 for _ in range(3)]
    for x, a in enumerate(winners):
        truth = tuple(map(int, reversed(f'{x:012b}')))
        for r in range(3):
            for o in range(4):
                child = codec.update(a, r, o, base, {})
                for j in range(4):
                    if j != o:
                        wrong = codec.predict(child, r, o, j) != truth[4*r+j]
                        errors += wrong
                        branches[r][o] += wrong
    if errors != sum(minima):
        raise ValueError('Direct three-block actor routes and distances disagree')
    return {'errors': errors, 'outcomes': 147456, 'actor_routes_executed': 147456,
            'branch_errors': branches, 'used_parent_messages': len(set(winners))}


def partition(base, overrides):
    codec.validate(base, overrides)
    columns, winners, minima, _ = nearest(base)
    changed = sorted({m >> 6 for m in overrides})
    groups = defaultdict(list)
    local = []
    for x, row in enumerate(cost_rows()):
        values, args = {}, {}
        for b in changed:
            costs = list(columns[x])
            for a in range(64):
                if a + 64*b in overrides:
                    costs[a] = row[overrides[a + 64*b]]
            values[b] = min(costs)
            args[b] = costs.index(values[b])
        key = tuple(values[b] - minima[x] for b in changed)
        groups[key].append(x)
        local.append((values, args))
    return columns, winners, minima, changed, dict(groups), local


def grade_six(base, overrides, *, actors=False):
    """Exact population by grouped right choice, then weighted actor queries.

    b is the high digit of M. Its tied minimum therefore precedes the tie in
    a. Subtracting a source-dependent common left minimum cannot change b.
    Right updater outputs depend only on b; left outputs can depend on a/b.
    """
    columns, winners, minima, changed, groups, local = partition(base, overrides)
    errors, pairs, actor_calls, weighted_routes = 0, 0, 0, 0
    branches = [[0]*4 for _ in range(6)]
    occupancies = [0]*4096
    group_sizes = []
    for key, xs in sorted(groups.items()):
        adjustments = dict(zip(changed, key))
        counts, right_errors = [0]*64, 0
        representative = xs[0]
        for y, row in enumerate(columns):
            # Generic relative-minimum vector; no native threshold histogram.
            values = [distance + adjustments.get(b, 0) for b, distance in enumerate(row)]
            b = values.index(min(values))
            counts[b] += 1
            right_errors += row[b]
            if actors:
                a = local[representative][1].get(b, winners[representative])
                m = a + 64*b
                truth = tuple(map(int, reversed(f'{y:012b}')))
                for r in range(3, 6):
                    for o in range(4):
                        child = codec.update(m, r, o, base, overrides)
                        for j in range(4):
                            if j != o:
                                wrong = codec.predict(child, r, o, j) != truth[4*(r-3)+j]
                                branches[r][o] += wrong * len(xs)
                                actor_calls += 1
                                weighted_routes += len(xs)
        errors += right_errors * len(xs)
        for x in xs:
            truth = tuple(map(int, reversed(f'{x:012b}'))) if actors else None
            values, args = local[x]
            for b, count in enumerate(counts):
                if not count:
                    continue
                a = args.get(b, winners[x])
                m = a + 64*b
                occupancies[m] += count
                errors += count * values.get(b, minima[x])
                if actors:
                    for r in range(3):
                        for o in range(4):
                            child = codec.update(m, r, o, base, overrides)
                            for j in range(4):
                                if j != o:
                                    wrong = codec.predict(child, r, o, j) != truth[4*r+j]
                                    branches[r][o] += wrong * count
                                    actor_calls += 1
                                    weighted_routes += count
        pairs += 4096*len(xs)
        group_sizes.append({'relative_left_minima': list(key), 'left_sources': len(xs),
                            'right_counts_by_high_parent_digit': counts})
    outcomes = pairs*72
    if pairs != 16777216 or sum(occupancies) != pairs:
        raise ValueError('Grouping omitted or duplicated source pairs')
    if actors and (weighted_routes != outcomes or sum(map(sum, branches)) != errors):
        raise ValueError('Weighted actor routes and independent distance count disagree')
    ratio = Fraction(errors, outcomes)
    return {'errors': errors, 'outcomes': outcomes,
            'distortion': {'numerator': ratio.numerator, 'denominator': ratio.denominator},
            'source_pairs_covered': pairs, 'modified_right_groups': changed,
            'left_minimum_groups': group_sizes, 'used_parent_messages': sum(n > 0 for n in occupancies),
            'message_occupancies': occupancies, 'branch_errors': branches if actors else None,
            'physical_actor_query_calls': actor_calls, 'weighted_actor_outcomes': weighted_routes,
            'all_outcomes_executed_individually': False,
            'grouping_scope': 'exact finite factorization; right b independent of left source within each relative-minimum group'}


def read_rows(name):
    return [json.loads(line) for line in (DISCOVERY/name).read_text(encoding='utf-8').splitlines()]


def discovery_check():
    metadata = json.loads((DISCOVERY/'metadata.json').read_text(encoding='utf-8'))
    for name, expected in metadata['file_sha256'].items():
        if hashlib.sha256((DISCOVERY/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Preserved discovery bytes changed: {name}')
    upstream = ROOT/metadata['upstream']['path']
    if hashlib.sha256(upstream.read_bytes()).hexdigest() != metadata['upstream']['sha256']:
        raise ValueError('Original C59 discovery changed')
    old = tuple(json.loads(upstream.read_text(encoding='utf-8'))['runs']['greedy']['codeword_ids'])
    refined = read_rows('refine.jsonl')
    records = [r for r in refined if r['kind'] == 'refine']
    base = list(old)
    component_steps = []
    for i, row in enumerate(records):
        if row['step'] != i or row['errors'] != sum(nearest(tuple(base))[2]):
            raise ValueError('Native component trajectory does not independently rescore')
        if row['gain'] > 0:
            before = row['errors']
            base[row['removed_index']] = row['replacement']
            if before - sum(nearest(tuple(base))[2]) != row['gain']:
                raise ValueError('Accepted component gain does not independently rescore')
        elif i != len(records)-1:
            raise ValueError('Refinement continued after a zero screen')
        component_steps.append(row)
    if tuple(base) != codec.BASE or refined[-1]['book'] != base or len(records) != 5:
        raise ValueError('Selected component differs from four recorded changes')
    for name, values in [('base.h', old), ('refined.h', codec.BASE)]:
        expected = 'static const uint16_t BASE[64]={' + ','.join(map(str, values)) + '};'
        if (DISCOVERY/name).read_text().strip() != expected:
            raise ValueError('Public native header differs from declared component')
    if (DISCOVERY/'couple.c').read_bytes() != (DISCOVERY/'swap.c').read_bytes().replace(b'#include "base.h"', b'#include "refined.h"', 1):
        raise ValueError('Refined screen is not the preserved original algorithm with the refined header')
    initial = read_rows('discovery.jsonl')
    plain = [r for r in initial if r['kind'] == 'plain']
    if len(plain) != 9 or any(r['errors'] != 40529 for r in plain):
        raise ValueError('Failed plain component modal control changed')
    failed = []
    for seed in range(4):
        rows = [r for r in initial if r['kind'] == 'conditional' and r['seed'] == seed]
        if (len(rows) != 9 or [r['step'] for r in rows] != list(range(9))
                or any(r['errors'] < 332013568 for r in rows)
                or any(a['errors'] < b['errors'] for a, b in zip(rows, rows[1:]))):
            raise ValueError('Failed initial search trajectory changed')
        failed.append({'seed': seed, 'errors': [r['errors'] for r in rows]})
    warm = read_rows('warm.jsonl')
    warm_steps = [r for r in warm if r['kind'] != 'final']
    if len(warm_steps) != 9 or any(r['errors'] != 332008366 for r in warm_steps):
        raise ValueError('Failed warm modal continuation changed')
    initial_screen = read_rows('swap.jsonl')[-1]
    refined_screen = read_rows('couple.jsonl')[-1]
    if (initial_screen['gain'], refined_screen['gain']) != (5202, 4101):
        raise ValueError('Selected original/refined single-change screen changed')
    trajectory, overrides = [], {}
    iterative = read_rows('iterate.jsonl')
    for i, row in enumerate(iterative[:-1]):
        if (row['step'] != i or row['kind'] != 'screen' or len(row['best_by_slot']) != 4096
                or row['candidate_replacements'] != 16777216):
            raise ValueError('Conditional screen coverage/visit order changed')
        largest = max(p[1] for p in row['best_by_slot'])
        hole = next(m for m, p in enumerate(row['best_by_slot']) if p[1] == largest)
        if (row['gain'], row['selected_hole'], row['selected_word']) != (largest, hole, row['best_by_slot'][hole][0]):
            raise ValueError('Recorded selection is not the first maximum slot')
        independently_scored = grade_six(codec.BASE, overrides)['errors']
        if independently_scored != row['errors']:
            raise ValueError('Conditional trajectory does not independently rescore')
        overrides[hole] = row['selected_word']
        trajectory.append({'step': i, 'errors_before': independently_scored,
                           'parent_id': hole, 'left_triple': overrides[hole], 'recorded_gain': row['gain']})
    final = iterative[-1]
    if (overrides != codec.OVERRIDES or final['overrides'] != sorted(map(list, overrides.items()))
            or len(trajectory) != 8 or final['zero_screen'] or final['accepted'] != 8):
        raise ValueError('Final bounded conditional selection changed')
    scores = [r['errors_before'] for r in trajectory] + [grade_six(codec.BASE, overrides)['errors']]
    if any(scores[i]-scores[i+1] != r['recorded_gain'] for i, r in enumerate(trajectory)):
        raise ValueError('Accepted conditional gain does not independently rescore')
    if final['errors'] != scores[-1] or scores[-1] != 331857648:
        raise ValueError('Final conditional native/independent scores disagree')
    return {'failed_initial_modal_starts': failed, 'plain_component_modal_errors': [r['errors'] for r in plain],
            'failed_old_product_change_errors': initial_screen['errors'],
            'failed_warm_modal_errors': [r['errors'] for r in warm_steps],
            'component_steps': component_steps, 'conditional_steps': trajectory,
            'final_single_word_locality_certified': False,
            'native_rejected_candidate_scores_independently_recomputed': False,
            'accepted_errors_and_gains_independently_recomputed': True}


def certificate():
    if direct_losses() != codec.LOSSES:
        raise ValueError('Independent bit routes and encoder popcount losses disagree')
    discovery = discovery_check()
    component = grade_triple(codec.BASE)
    screen = single_word_screen(codec.BASE)
    if (component['errors'], screen['maximum_gain'], screen['positive_gain_candidates']) != (40514, 0, 0):
        raise ValueError('Stronger component error/locality check failed')
    one = read_rows('couple.jsonl')[-1]
    one_change = grade_six(codec.BASE, {one['hole']: one['replacement']})
    product_errors = 8192*component['errors']
    if product_errors-one_change['errors'] != 4101:
        raise ValueError('Product locality counterexample failed')
    six = grade_six(codec.BASE, codec.OVERRIDES, actors=True)
    if six['errors'] != 331857648:
        raise ValueError('Weighted final actor grading failed')
    files = [HERE/'codec.py', HERE/'certificate.py', HERE/'test_conditional.py', HERE/'tables.json',
             DISCOVERY/'metadata.json', HERE.parent/'joint_coding_finite3/discovery.json']
    files.extend(sorted(p for p in DISCOVERY.iterdir() if p.suffix in ('.c', '.h', '.py', '.jsonl')))
    # Common length12 uses independent six-block or three-block groups.
    common_outcomes = 16**12*144
    six_at12 = 2*six['errors']*16**6
    refined_at12 = 4*40514*16**9
    old_at12 = 4*40529*16**9
    ratio = Fraction(six['errors'], six['outcomes'])
    return {'version': 'conditional_six_block_v1', 'date': '2026-10-02', 'new_model_calls': 0,
            'new_natural_episodes': 0,
            'source_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            'information_contract': {'independent_uniform_four_bit_blocks': 6, 'parent_bits': 12, 'child_bits': 1,
                'parent_before_R_and_O': True, 'child_before_J': True,
                'updater_inputs': ['M', 'R', 'O', 'fixed_public_book'],
                'final_inputs': ['Z', 'R', 'O', 'J'], 'source_parent_session_archive_rereads': False,
                'public_book_fixed_before_X': True, 'public_label_bytes_charged_as_instance_memory': False},
            'public_label_payload_bytes': len(codec.pack_tables()),
            'public_label_count_is_protocol_constant': 8,
            'self_describing_count_and_framing_bytes': None,
            'component': component, 'component_all_single_word_replacements': screen,
            'unrestricted_three_block_interval_errors': [40072, 40514], 'three_block_outcomes': 147456,
            'three_block_interval_gap_errors': 442,
            'product_locality_counterexample': {'product_errors': product_errors,
                'parent_id': one['hole'], 'replacement_left_triple': one['replacement'],
                'single_change_errors': one_change['errors'], 'errors_avoided': 4101,
                'locality_scope': 'one triple replacement in the component; one six-block response-word replacement in its two-copy product'},
            'six_block': six, 'errors_avoided_against_refined_product': product_errors-six['errors'],
            'errors_avoided_against_old_product': 8192*40529-six['errors'],
            'common_length12_product_control': {'outcomes': common_outcomes, 'six_block_product_errors': six_at12,
                'refined_three_block_product_errors': refined_at12, 'old_three_block_product_errors': old_at12,
                'six_block_product_wins': six_at12 < refined_at12 < old_at12,
                'method': 'derived independent product additivity, not whole twelve-block actor enumeration'},
            'repeated_six_block_groups': {'block_count': '6*n, n>=1', 'parent_bits': '2*k', 'child_bits': 1,
                'distortion': {'numerator': ratio.numerator, 'denominator': ratio.denominator},
                'scope': 'independent fixed six-block groups and uniform selected block; exact derived product extension'},
            'discovery': discovery,
            'limits': 'Finite upper bounds and a scoped local-search counterexample. Six-block local/global optimality, efficient codes approaching the C67 curve, external correctness, priority and natural-task/model/cost benefit remain open. No generic Lloyd, product quantization or coordinate-replacement novelty; old artifacts and model studies unchanged.'}


def main():
    data = certificate()
    OUTPUT.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'component_errors': data['component']['errors'],
                      'component_maximum_single_word_gain': data['component_all_single_word_replacements']['maximum_gain'],
                      'six_errors': data['six_block']['errors'], 'outcomes': data['six_block']['outcomes'],
                      'physical_actor_query_calls': data['six_block']['physical_actor_query_calls'],
                      'weighted_actor_outcomes': data['six_block']['weighted_actor_outcomes'],
                      'groups': len(data['six_block']['left_minimum_groups']),
                      'source_bindings': len(data['source_sha256'])}))


if __name__ == '__main__':
    main()
