"""Reproduce finite robustness and exact bounds for the changed query law."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

from . import asymptotic, codec, finite
from experiments.dependency_memory.conditional_coding import codec as six
from experiments.dependency_memory.joint_coding import decoder_frontier as f

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DISCOVERY = HERE/'discovery'
OUTPUT = HERE.parent/'results/query_weighting_2026-10-02.json'


def discovery_check():
    meta = json.loads((DISCOVERY/'metadata.json').read_text(encoding='utf-8'))
    for name, expected in meta['file_sha256'].items():
        if sha256((DISCOVERY/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Preserved query-prior discovery changed')
    for name, record in meta['upstream'].items():
        path = ROOT/name
        if sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Original C67/C69 certificate bytes changed')
        data = json.loads(path.read_text(encoding='utf-8'))
        for source, digest in data['source_sha256'].items():
            if sha256((ROOT/source).read_bytes()).hexdigest() != digest:
                raise ValueError('Original source-bound theorem/witness changed')
    before = (DISCOVERY/'probe.py').read_bytes()
    after = (DISCOVERY/'probe_v2.py').read_bytes()
    if before.count(b'lo,hi=.00001,.299') != 1 or after != before.replace(b'lo,hi=.00001,.299', b'lo,hi=.00001,.9'):
        raise ValueError('Corrected probe changed more than the documented outer bracket')
    initial = json.loads((DISCOVERY/'initial_recomputed_probe.json').read_text(encoding='utf-8'))
    corrected = json.loads((DISCOVERY/'corrected_probe.json').read_text(encoding='utf-8'))
    bad = next(r for r in initial['float_witnesses'] if r['p'] == '2/5')
    good = next(r for r in corrected['float_witnesses'] if r['p'] == '2/5')
    if not (bad['left_rate']+bad['right_rate'] > 4 and abs(good['left_rate']+good['right_rate']-4) < 1e-12):
        raise ValueError('Initial floating failure/correction record changed')
    witnesses = json.loads((HERE/'witnesses.json').read_text(encoding='utf-8'))
    expected = [(1,9), (1,3), (1,2), (2,3), (1,1)]
    if [(r['m'],r['n']) for r in witnesses['points']] != expected or len(witnesses['exact_admission_attempts']) != 5:
        raise ValueError('Exact admission schedule changed')
    for point, attempt in zip(witnesses['points'], witnesses['exact_admission_attempts']):
        if (point['m'],point['n'],point['q']) != (attempt['m'],attempt['n'],attempt['q']) or not attempt['accepted']:
            raise ValueError('Declared first-attempt admission changed')
    return {'initial_bad_float_p': '2/5', 'initial_combined_rate_observed': str(bad['left_rate']+bad['right_rate']),
            'initial_record_is_explicit_offline_recomputation': True,
            'float_values_used_in_numeric_proof': False, 'accepted_exact_witnesses': 5,
            'exact_attempts': witnesses['exact_admission_attempts']}


def routing_check():
    """All local parent messages in both orientations; source-free routing.

    This is not enumeration of the 2**48 twelve-block source population or
    every 24-bit parent combination. Public extraction algebra handles the
    other independent group; complete-source diagnostics are separate tests.
    """
    response_checks = query_checks = 0
    for group in range(2):
        for source_class in range(2):
            for rank in range(3):
                block = source_class*6 + group*3 + rank
                for m in range(4096):
                    # Independently reconstruct public triples from parent digits.
                    low, high = m % 64, m//64
                    left = six.OVERRIDES.get(m, six.BASE[low])
                    right = six.BASE[high]
                    triple = (left, right)[source_class ^ group]
                    word = (triple >> (4*rank)) & 15
                    parent = m << (12*group)
                    for omitted in range(4):
                        child = codec.update_balanced(parent, block, omitted, 12)
                        if child != (word >> omitted) & 1:
                            raise ValueError('Opposite-orientation routing changed')
                        response_checks += 1
                        for query in range(4):
                            if query != omitted:
                                if codec.predict(child, block, omitted, query) != child:
                                    raise ValueError('Final actor changed the one-bit prediction')
                                query_checks += 1
    return {'local_response_checks': response_checks, 'source_free_final_query_checks': query_checks,
            'local_parent_messages_per_orientation': 4096,
            'larger_parent_or_source_populations_enumerated': False}


def control_routes():
    """All single-block sources/routes for the executable 1/3 allocation arms."""
    result = []
    for block, bits in ((0,1), (3,3)):
        errors, calls = 0, 0
        for source in range(16):
            parent = codec.encode_allocated((source,)*6, 1, 3)
            truth = tuple(map(int, reversed(f'{source:04b}')))
            for omitted in range(4):
                child = codec.update_allocated(parent, block, omitted, 6, 1, 3)
                for query in range(4):
                    if omitted != query:
                        errors += codec.predict(child, block, omitted, query) != truth[query]
                        calls += 1
        if (errors, calls) != ((60,192) if bits == 1 else (48,192)):
            raise ValueError('Independent single-block control grading failed')
        result.append({'parent_bits_per_block': bits, 'errors': errors, 'outcomes': calls,
                       'distortion': str(F(errors,calls)), 'physical_actor_query_calls': calls})
    return result


def comparison_regions():
    """Exact strict winning intervals against three named allocation controls."""
    controls = ((F(40514,147456), F(0)), (F(1,4), F(1,16)), (F(5,16), F(-1,16)))
    def strict(p):
        return finite.direct_value(p) < min(finite.controls(p).values())
    pieces = []
    for row in finite.envelope()['segments']:
        lo, hi = F(row['left']), F(row['right'])
        a, b = F(row['intercept']), F(row['slope'])
        cuts = {lo, hi}
        for c, d in controls:
            if b != d:
                root = (c-a)/(b-d)
                if lo < root < hi:
                    cuts.add(root)
        cuts = sorted(cuts)
        for left, right in zip(cuts,cuts[1:]):
            middle = (left+right)/2
            if all(a+b*middle < c+d*middle for c,d in controls):
                if pieces and pieces[-1][1] == left and strict(left):
                    pieces[-1][1] = right
                else:
                    pieces.append([left,right])
    regions = []
    for left, right in pieces:
        regions.append({'left': str(left), 'right': str(right),
                        'left_included': strict(left), 'right_included': strict(right)})
    return regions


def certificate():
    discovery = discovery_check()
    curve = finite.envelope()
    paired = finite.frozen_and_balanced()
    lower, upper = f.LOWER_TARGET, f.UPPER_TARGET
    witnesses = json.loads((HERE/'witnesses.json').read_text(encoding='utf-8'))['points']
    points = [asymptotic.point(r['m'],r['n'],F(r['q'])) for r in witnesses]
    if not (lower < F(points[-1]['distortion_lower']) < F(points[-1]['distortion_upper']) < upper):
        raise ValueError('Weighted uniform check disagrees with the old rate-two interval')
    diagnostics = []
    balanced = F(paired['balanced_pair_any_p_error'])
    frozen_left = F(paired['frozen_uniform_encoder_left_error'])
    frozen_right = F(paired['frozen_uniform_encoder_right_error'])
    for p in finite.POINTS:
        reencoded = finite.value_from_segments(p)
        if reencoded != finite.direct_value(p):
            raise ValueError('Entire-envelope and direct diagnostic losses disagree')
        controls = finite.controls(p)
        frozen = p*frozen_left + (1-p)*frozen_right
        if reencoded > frozen:
            raise ValueError('Known-prior nearest reencoding cannot lose to the old assignment')
        diagnostics.append({'p': str(p), 'frozen_uniform_encoder_error': str(frozen),
                            'known_prior_regular_six_error': str(reencoded),
                            'unknown_prior_balanced_pair_error': str(balanced),
                            'named_controls': {name:str(value) for name,value in controls.items()},
                            'best_named_control_error': str(min(controls.values()))})
    files = [HERE/name for name in ('codec.py','finite.py','asymptotic.py','certificate.py','test_weighting.py','witnesses.json')]
    files += [DISCOVERY/'metadata.json']
    files += sorted(p for p in DISCOVERY.iterdir() if p.suffix in ('.py','.json') and p.name != 'metadata.json')
    files += [ROOT/name for name in (
        'experiments/dependency_memory/results/conditional_six_block_2026-10-02.json',
        'experiments/dependency_memory/results/rate_curve_2026-10-02.json',
        'experiments/dependency_memory/joint_coding/decoder_frontier.py',
        'experiments/dependency_memory/rate_spectrum/derive.py')]
    return {'version': 'query_prior_weighting_v1', 'date': '2026-10-02',
            'new_model_calls': 0, 'new_natural_episodes': 0,
            'source_sha256': {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in files},
            'information_contract': {'source': 'k=2*n independent uniform four-bit blocks, two public classes of n blocks',
                'R': 'class chosen with source-independent fixed probability p; uniform block within class',
                'O_and_J': 'uniform omission and uniform remaining coordinate, independent of X',
                'parent_bits': '2*k=4*n', 'child_bits': 1,
                'public_labels_fixed_before_X': True, 'archives_sessions_source_parent_rereads': False,
                'final_value_inputs': ['Z','R','O','J'],
                'known_prior': 'p public before X; realized class/R/O/J still late',
                'unknown_prior': 'parent design cannot depend on p; p chosen independently of X; optional later public p does not change the minimax theorem',
                'early_class': 'actual realized class T, not p alone, is public before M; R/O/J remain late',
                'source_adaptive_or_instance_dependent_p_excluded': True},
            'finite_known_prior_curve': curve, 'finite_diagnostic_points': diagnostics,
            'regular_reencoding_beats_three_named_controls_on': comparison_regions(),
            'opposite_orientation_pair': paired,
            'balanced_pair_beats_three_named_known_prior_controls_iff':
                {'left': str(16*(balanced-F(1,4))), 'right': str(16*(F(5,16)-balanced)), 'endpoints_included': False},
            'routing_checks': routing_check(), 'single_block_allocation_controls': control_routes(),
            'known_prior_asymptotic_characterization': {
                'all_p_0_to_1': True,
                'formula': 'min_{r_L,r_R>=0, r_L+r_R<=4} p*D(r_L)+(1-p)*D(r_R), with D from C67',
                'scope': 'local analytic consequence of C67, not a new general allocation or source-coding theorem',
                'arbitrary_joint_encoders_and_heterogeneous_tables': True,
                'exact_2k_capacity_no_extra_o_k_bits': True, 'efficient_finite_code_supplied': False,
                'endpoint_error': '1/4', 'symmetric_about_p_half': True,
                'strictly_below_uniform_error_for_p_not_half': True,
                'exact_numeric_support_points': points,
                'other_p_values': 'analytic variational characterization; not extra numerical interval computations'},
            'unknown_prior_minimax_asymptotic_error': {'equals_C67_rate_two_error': True,
                'existing_strict_interval': [str(lower),str(upper)],
                'proof': 'lower from p=1/2; upper from equal-rate independent class codes inside 4*n bits'},
            'early_realized_class': {'error': '1/4', 'used_parent_bits': '3*n', 'available_parent_bits': '4*n',
                'class_cue_source_information': 'zero; T is independent of X',
                'cue_description': 'one public class bit with changed arrival time, excluded from the value budget',
                'physical_large_population_enumeration': False,
                'late_uniform_class_limiting_error_minus_early_error_strict_interval': [str(lower-F(1,4)),str(upper-F(1,4))]},
            'discovery': discovery,
            'limits': 'Changed query prior only; source and within-block query law unchanged. Finite balanced product counts are derived from bound C69, not enumeration of twelve-block sources. Three allocation controls are named achievable codes, not all finite allocations or optima. Frozen, prior-known and realized-class-early information conditions differ explicitly. All numerical intervals use exact rational witnesses/outward logs and reuse C67 all-slope decoder dominance; no new table enumeration or float proof. Generic symmetrization, allocation, side information and product coding are established; external proof/priority, other source/query laws and natural-agent/model/cost benefit remain open. Historical artifacts and provider allocations unchanged.'}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'finite_curve_segments': len(result['finite_known_prior_curve']['segments']),
                      'known_prior_points': [r['limiting_distortion_enclosure'] for r in result['known_prior_asymptotic_characterization']['exact_numeric_support_points']],
                      'balanced_pair_error': result['opposite_orientation_pair']['balanced_pair_any_p_error'],
                      'regular_winning_regions': result['regular_reencoding_beats_three_named_controls_on'],
                      'source_bindings': len(result['source_sha256'])}))


if __name__ == '__main__':
    main()
