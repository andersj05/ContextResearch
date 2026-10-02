"""Regenerate the 48 strict inequalities covering every positive slope."""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from experiments.dependency_memory.joint_coding import decoder_frontier as frontier
from experiments.dependency_memory.joint_coding_complement import cover
from experiments.dependency_memory.rate_curve import comparison, polynomials
from experiments.dependency_memory.rate_spectrum import derive

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT/'experiments/dependency_memory/results/rate_curve_2026-10-02.json'


def polynomial_hash(p):
    return sha256(str(tuple(p)).encode('ascii')).hexdigest()


def coefficient_hash(p):
    digest = sha256()
    for value in p:
        digest.update(f'{value:x}\n'.encode('ascii'))
    return digest.hexdigest()


def source_bindings():
    here = Path(__file__).parent
    files = [here/name for name in ('polynomials.py','comparison.py','certificate.py',
                                    'test_curve.py','README.md')]
    files += [here/'auxiliary'/name for name in ('README.md','screen.py','screen.json',
               'screen_three.py','screen_three.json','polynomial_probe.py','polynomial_probe.json')]
    files += [ROOT/name for name in (
        'research/UNRESTRICTED_RATE_CURVE_2026-10-02.md',
        'research/COMPLEMENTARY_COMPLETION_2026-10-02.md',
        'research/PARENT_RATE_SPECTRUM_2026-10-01.md',
        'research/JOINT_BLOCK_CODING_2026-09-21.md',
        'experiments/dependency_memory/decoder_completion/complete.py',
        'experiments/dependency_memory/decoder_completion/certificate.py',
        'experiments/dependency_memory/results/decoder_completion_2026-10-02.json',
        'experiments/dependency_memory/joint_coding/decoder_frontier.py',
        'experiments/dependency_memory/joint_coding_complement/cover.py',
        'experiments/dependency_memory/rate_spectrum/derive.py',
        'experiments/dependency_memory/results/rate_spectrum_2026-10-01.json')]
    return {path.relative_to(ROOT).as_posix():sha256(path.read_bytes()).hexdigest() for path in files}


def verify_frozen_dependency(name):
    value = json.loads((ROOT/name).read_text(encoding='utf-8'))
    for path, digest in value['source_sha256'].items():
        if sha256((ROOT/path).read_bytes()).hexdigest() != digest:
            raise ArithmeticError(f'Frozen dependency changed: {path}')
    return value


@lru_cache(maxsize=1)
def certificate():
    completion = verify_frozen_dependency('experiments/dependency_memory/results/decoder_completion_2026-10-02.json')
    spectrum = verify_frozen_dependency('experiments/dependency_memory/results/rate_spectrum_2026-10-01.json')
    if not completion['unrestricted_optimum_equals_complementary_optimum']:
        raise ArithmeticError('All-decoder completion dependency absent')
    rows, coefficients, groups_covered = [], 0, Counter()
    for case in comparison.cases():
        transformed = polynomials.interval_coefficients(case['polynomial'],case['low'],case['high'])
        if (any(value < 0 for value in transformed) or transformed[0] <= 0
                or transformed[-1] <= 0 or case['roots_at_one'] < 2):
            raise ArithmeticError('Exact strict interval positivity failed')
        coefficients += len(transformed)
        groups_covered[(case['family'],case['interval'])] += len(case['words'])
        rows.append({'family':case['family'], 'table':list(case['table']),
                     'orbit_size':case['orbit_size'], 'weights':list(case['weights']),
                     'interval':[str(case['low']),str(case['high'])],
                     'column_group':case['column_group'], 'words':list(case['words']),
                     'unsigned_weights':list(case['unsigned_weights']),
                     'degree_before_removing_one_roots':len(case['raw'])-1,
                     'roots_at_one':case['roots_at_one'], 'positive_content_hex':f"{case['content']:x}",
                     'primitive_degree':len(case['polynomial'])-1,
                     'primitive_polynomial_sha256':polynomial_hash(case['polynomial']),
                     'transformed_coefficients':len(transformed),
                     'strictly_positive_coefficients':sum(value > 0 for value in transformed),
                     'first_and_last_strictly_positive':True,
                     'minimum_positive_bit_length':min(value.bit_length() for value in transformed if value),
                     'transformed_coefficients_sha256':coefficient_hash(transformed)})
    if len(groups_covered) != 15 or any(n != 16 for n in groups_covered.values()):
        raise ArithmeticError('A family/interval dropped a decision word')
    # Independent direct majority signatures give the limiting marginal.
    frequencies = [0]*16
    for x in range(16):
        a = sum(int(sum((x>>j)&1 for j in range(4) if j != o) >= 2)<<o for o in range(4))
        frequencies[a] += 1
    expected = [5 if a in (0,15) else 1 if a.bit_count()==2 else 0 for a in range(16)]
    if frequencies != expected:
        raise ArithmeticError('Unsigned signature distribution changed')
    log_low, log_high = frontier.log2_bounds(5)
    entropy = frontier.decimal_enclosure(4-F(5,8)*log_high,4-F(5,8)*log_low)
    families = cover.orbits()
    return {'version':1, 'date':'2026-10-02',
            'evidence_class':'local analytic unrestricted asymptotic curve with exact continuum comparison certificate',
            'complementary_tables':256, 'complementary_orbits':len(families),
            'orbit_sizes':[len(orbit) for _,orbit in families],
            'unrestricted_tables_covered_by_completion':36**4,
            'positive_slope_domain':'all s>0, equivalently all 0<t=2**(-s)<1',
            'intervals':[[str(low),str(high)] for low,high,_ in comparison.WITNESSES],
            'distinct_comparison_polynomials':len(rows),
            'column_interval_cases':sum(groups_covered.values()),
            'transformed_integer_coefficients_checked':coefficients,
            'maximum_primitive_degree':max(row['primitive_degree'] for row in rows),
            'strict_other_family_dominance':True,
            'comparisons':rows, 'unsigned_scalar_algebra':derive.algebra_record(),
            'unsigned_oracle_signature_frequencies':frequencies,
            'oracle_threshold_bits':'4-(5/8)*log2(5)', 'oracle_threshold_enclosure':entropy,
            'transition_information_enclosure':spectrum['algebra']['restricted_transition_information_enclosure'],
            'transition_distortion_enclosure':spectrum['algebra']['restricted_transition_distortion_enclosure'],
            'curve_characterization':'D_infinity(R(t))=E_t[L]/12; R(t)=I_t(X;A), optimal unsigned Gibbs channel; D_infinity(0)=1/2 and D_infinity(r)=1/4 for r>=h_star',
            'parent_capacity':'floor(k*r) bits; arbitrary joint encoders and heterogeneous public decoder tables',
            'achievability_slack':'Mix the optimal channel with a source-independent channel; then I<r, before choosing a fixed-length intermediate coding rate. No extra o(k) bits are assumed.',
            'full_unrestricted_asymptotic_curve_characterized':True,
            'finite_optimum_or_efficient_code_claimed':False,
            'new_model_calls':0, 'natural_workflow_episodes_added':0,
            'source_sha256':source_bindings(),
            'limits':'Specific uniform iid four-bit source, independent uniform R/O/J, one-bit child before J, average Hamming loss. Fixed public tables/books before source; parent/source/session/archive rereads excluded. Standard rate-distortion, strategy, completion and polynomial-positivity machinery is not claimed novel. Exact parametric asymptotic model result, not finite optimal code or production benefit. Discovery was bounded and post-hoc; external correctness and publication priority remain open.'}


def main():
    value = certificate()
    OUTPUT.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(value['distinct_comparison_polynomials'],'polynomials;',value['transformed_integer_coefficients_checked'],
          'integer coefficients; strict dominance on all 0<t<1',flush=True)
    print('Oracle threshold:',value['oracle_threshold_enclosure'],flush=True)


if __name__ == '__main__':
    main()
