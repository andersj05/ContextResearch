"""All-decoder supporting certificates at eight separately stated rational rates.

All 36**4 tables, repeats included, are covered by the unchanged symmetry
enumerator. No float or numerical optimizer participates in this check.
"""
from functools import lru_cache
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

from experiments.dependency_memory.joint_coding import decoder_frontier as f
from experiments.dependency_memory.rate_spectrum import derive

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT/'experiments/dependency_memory/results/rate_spectrum_2026-10-01.json'
POINTS = (F(1,100), F(1,20), F(3,20), F(1,4), F(2,5), F(3,5), F(4,5), F(19,20))
RATE_GRID = 10**10


def source_bindings():
    files = [Path(__file__).parent/'derive.py', Path(__file__), Path(__file__).parent/'test_spectrum.py',
             Path(__file__).parent/'README.md',
             ROOT/'experiments/dependency_memory/joint_coding/decoder_frontier.py']
    # Bind discovery provenance without using its floating values in the proof.
    files += [Path(__file__).parent/'auxiliary'/name for name in
              ('README.md', 'explore.py', 'exploration.json', 'default-analysis.json')]
    return {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in files}


@lru_cache(maxsize=1)
def certificate():
    orbits = tuple(f.decoder_orbits())
    if len(orbits) != 4751 or sum(size for _, _, size in orbits) != 36**4:
        raise ArithmeticError('Incomplete decoder cover')
    losses = tuple(f.loss_matrix(table) for _, table, _ in orbits)
    nearest = tuple(f.nearest_weights(loss) for loss in losses)
    unsigned = next(i for i, (_, table, _) in enumerate(orbits) if table == f.UNSIGNED)
    records = []
    for t in POINTS:
        weights = derive.unsigned_weights(t)
        digest = sha256()
        worst = other = None
        denominator = None
        for i, ((index, table, size), loss) in enumerate(zip(orbits, losses)):
            q = weights if i == unsigned else nearest[i]
            numerator, this_denominator = f.dual_product(loss, q, t)
            if denominator is not None and this_denominator != denominator:
                raise ArithmeticError('Dual denominators must agree')
            denominator = this_denominator
            item = (numerator, index, size)
            if worst is None or item > worst:
                worst = item
            if i != unsigned and (other is None or item > other):
                other = item
            digest.update(f'{index}:{size}:{numerator:x}\n'.encode('ascii'))
        if worst[1] != f.encode_table(f.UNSIGNED):
            raise ArithmeticError(f'Unsigned is not the worst certified orbit at t={t}')
        primal = f.primal_bounds(losses[unsigned], weights, t)
        # Strict rate slack is necessary for fixed-length achievability.
        scaled = primal['information_upper']*RATE_GRID
        rate = F(scaled.numerator//scaled.denominator+1, RATE_GRID)
        _, g_high = f.log2_bounds(worst[0], denominator)
        free_lower = -g_high/16
        t_low, t_high = f.log2_bounds(t.numerator, t.denominator)
        lower = (free_lower-rate)/(-12*t_low)
        upper = primal['distortion']
        if not (0 < primal['information_upper'] < rate and F(1,4) < lower < upper < F(1,2)
                and upper-lower < F(2,10**11)):
            raise ArithmeticError(f'Invalid or insufficiently sharp interval at {t}')
        # Separation is certified in objective units, not rounded float ranks.
        _, other_log_high = f.log2_bounds(other[0], denominator)
        other_lower = -other_log_high/16
        separation = other_lower-primal['free_high']
        if separation <= 0:
            raise ArithmeticError('Other-decoder separation is not strict')
        records.append({'t': str(t), 'parent_rate_bits_per_block': str(rate),
                        'rate_decimal': f.decimal_enclosure(rate, rate, 10)[0],
                        'unsigned_weights': list(weights),
                        'unsigned_support_size': sum(w > 0 for w in weights),
                        'all_decoder_objective_lower': str(free_lower),
                        'other_decoder_objective_separation_lower': str(separation),
                        'other_decoder_separation_enclosure': f.decimal_enclosure(separation, separation),
                        'worst_orbit': worst[1], 'runner_up_orbit': other[1],
                        'orbit_comparisons_sha256': digest.hexdigest(),
                        'information_upper': str(primal['information_upper']),
                        'rate_slack_lower': str(rate-primal['information_upper']),
                        'distortion_lower': str(lower), 'distortion_upper': str(upper),
                        'limiting_distortion_enclosure': f.decimal_enclosure(lower, upper),
                        'interval_width_upper': str(upper-lower),
                        'finite_lower_scope': 'all k>=1 with parent capacity <=floor(k*rate) bits; child one bit',
                        'upper_scope': 'asymptotic fixed-length existence; no finite blocklength or efficient code supplied'})
    phase = derive.transition_bracket()
    constants = derive.unsigned_weights(F(1,2))
    lower_t, upper_t = phase['t']
    # Complement symmetry makes the constant-word Gibbs marginal exactly 1/2.
    low_t_primal = f.primal_bounds(losses[unsigned], constants, lower_t)
    high_t_primal = f.primal_bounds(losses[unsigned], constants, upper_t)
    algebra = derive.algebra_record()
    algebra['restricted_transition_information_enclosure'] = f.decimal_enclosure(
        high_t_primal['cross_information_low'], low_t_primal['information_upper'], 12)
    algebra['restricted_transition_distortion_enclosure'] = f.decimal_enclosure(
        low_t_primal['distortion'], high_t_primal['distortion'], 12)
    return {'version': 1, 'date': '2026-10-01',
            'evidence_class': 'local analytic unsigned-family reduction and exact all-decoder supporting certificates',
            'decoder_tables_per_point': 36**4, 'orbits_per_point': len(orbits),
            'support_points': len(records), 'orbit_point_checks': len(orbits)*len(records),
            'algebra': algebra, 'points': records, 'source_sha256': source_bindings(),
            'new_model_calls': 0, 'natural_workflow_episodes_added': 0,
            'complete_all_rate_unrestricted_curve_claimed': False,
            'exact_finite_optimum_or_production_saving_claimed': False,
            'limits': 'Post-hoc mathematical witness selection, not model trials. Public decoder tables/codebooks fixed before source; source and parent vanish at their declared boundaries. All-rate optimality only within unsigned family. Eight all-decoder asymptotic intervals do not certify untested rates or finite codebooks. External proof and priority review remain open.'}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    for point in result['points']:
        print(point['rate_decimal'], point['limiting_distortion_enclosure'], flush=True)
    print('Restricted transition:', result['algebra']['restricted_transition_information_enclosure'])


if __name__ == '__main__':
    main()
