"""Hard capacity, whole-population bounds and source-free actor checks."""
from collections import Counter
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
import json
from pathlib import Path

from . import codec,finite
from experiments.dependency_memory.joint_coding import decoder_frontier as logs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE.parent/'results/entropy_coding_2026-10-02.json'
LENGTHS = (96,192,384,768,1536,3072,6144,12288)


def direct_loss(x,a):
    return sum(((x >> j) & 1) != ((a >> o) & 1)
               for o in range(4) for j in range(4) if o != j)


def quantizers():
    records = []
    for kind in (0,1):
        counts = Counter()
        costs = excess = 0
        buckets = {}
        for x in range(16):
            if kind:
                a = 0
                for o in range(4):
                    ones = sum((x >> j) & 1 for j in range(4) if j != o)
                    a |= (ones > 3-ones) << o
            else:
                a = min((0,15),key=lambda word:direct_loss(x,word))
            if a != codec.response(x,kind):
                raise ValueError('Independent query-loss quantizer disagrees')
            counts[a] += 1
            loss = direct_loss(x,a)
            delta = direct_loss(x,0)-loss
            if delta < 0:
                raise ValueError('Fallback may not improve the selected quantizer')
            category = 'balanced' if kind and a not in (0,15) else 'common' if kind else str(a)
            buckets.setdefault(category,[]).append(delta)
            costs += loss
            excess += delta
        if tuple(counts[w] for w in codec.WORDS[kind]) != codec.COUNTS[kind]:
            raise ValueError('Fixed probability model does not match uniform-source quantizer')
        means = {key:F(sum(values),len(values)) for key,values in buckets.items()}
        if means != ({'0':F(0),'15':F(36,5)} if not kind else {'common':F(18,5),'balanced':F(2)}):
            raise ValueError('Conditional excess-loss law changed')
        records.append({'kind':kind,'words':list(codec.WORDS[kind]),
                        'counts_out_of_sixteen':list(codec.COUNTS[kind]),
                        'errors':costs,'outcomes':192,'error':str(F(costs,192)),
                        'conditional_excess_branch_loss':{k:str(v) for k,v in means.items()}})
    return records


def asymptotic():
    l5,h5 = logs.log2_bounds(5,1)
    l11,h11 = logs.log2_bounds(11,1)
    h2lo,h2hi = 4-(11*h11+5*h5)/16,4-(11*l11+5*l5)/16
    h8lo,h8hi = 4-10*h5/16,4-10*l5/16
    lamlo = (2-h2hi)/(h8hi-h2lo)
    lamhi = (2-h2lo)/(h8lo-h2hi)
    low,high = F(5,16)-lamhi/16,F(5,16)-lamlo/16
    if not (0 < h2lo < h2hi < 1 < 2 < h8lo < h8hi < 3
            and 0 < lamlo < lamhi < 1 and logs.UPPER_TARGET < low < high < F(2304567,8388608)):
        raise ValueError('Scalar entropy-coding limit or existing frontier comparison failed')
    if not 5**5*11**11 > 2**48 or not 5**25*11**11 > 2**96:
        raise ValueError('Exact zero/full and rational-count entropy inequalities failed')
    return {'two_word_entropy_enclosure':logs.decimal_enclosure(h2lo,h2hi,12),
            'oracle_entropy_enclosure':logs.decimal_enclosure(h8lo,h8hi,12),
            'oracle_fraction_boundary_enclosure':logs.decimal_enclosure(lamlo,lamhi,12),
            'implemented_entropy_schedule_error_limit_enclosure':logs.decimal_enclosure(low,high,12),
            'error_limit_formula':'5/16 - (2-h2)/(16*(h8-h2)), h2=4-(11*log2(11)+5*log2(5))/16, h8=4-(10/16)*log2(5)',
            'rational_schedule_error_limit':'13/48',
            'scalar_fraction_limit_not_global_rate_distortion_optimum':True,
            'new_limit_above_unchanged_C67_rate_two_interval':True,
            'vanishing_overflow_proof':'Public slack m=ceil(sqrt(k*ceil(log2(k+1)))); mean self-information <=2k-m; independent bounded terms have variance <=9k/4; Chebyshev at 2k-1 makes the length-event probability vanish.',
            'exact_2k_parent_capacity_including_flag':True,
            'no_exponential_public_codebook_stored':True}


def verify_frontier(data):
    k,a,b = data['k'],data['oracle_blocks'],data['two_word_blocks']
    five,eleven = [1],[1]
    for _ in range(k):
        five.append(five[-1]*5)
    for _ in range(b):
        eleven.append(eleven[-1]*11)
    threshold = 1 << (2*k+1)
    previous = a
    for v,u in enumerate(data['good_u_max_by_v']):
        if not -1 <= u <= previous:
            raise ValueError('Tail frontier is not monotone inside its count domain')
        if u >= 0 and five[a-u+v]*eleven[b-v] < threshold:
            raise ValueError('Declared last good cell has insufficient interval length')
        if u < a and five[a-u-1+v]*eleven[b-v] >= threshold:
            raise ValueError('Declared first bad cell still guarantees a midpoint')
        previous = u
    return len(data['good_u_max_by_v'])


def serialize_bound(data,schedule,control):
    checks = verify_frontier(data)
    base,upper = data['base_error'],data['error_upper']
    scale = 10**15
    rounded = F(-(-upper.numerator*scale//upper.denominator),scale)
    cutoffs = data['good_u_max_by_v']
    return {'schedule':schedule,'k':data['k'],'oracle_blocks':data['oracle_blocks'],
            'parent_bits':2*data['k'],'payload_grid_bits':2*data['k']-1,'charged_flag_bits':1,'child_bits':1,
            'base_error_lower_for_this_fixed_code':str(base),
            'coded_error_upper_rounded_outward':str(rounded),
            'coded_error_enclosure':logs.decimal_enclosure(base,upper,12),
            'error_upper_calculation_enclosure':logs.decimal_enclosure(upper,upper,15),
            'failure_probability_upper_enclosure':logs.decimal_enclosure(data['failure_event_upper_probability'],data['failure_event_upper_probability'],15),
            'conditional_excess_upper_enclosure':logs.decimal_enclosure(data['conditional_excess_upper'],data['conditional_excess_upper'],15),
            'raw_upper_numerator_sha256':finite.integer_digest(upper.numerator),
            'raw_upper_denominator_sha256':finite.integer_digest(upper.denominator),
            'bad_mass_numerator_sha256':data['bad_mass_numerator_sha256'],
            'excess_numerator_sha256':data['excess_numerator_sha256'],
            'total_binomial_mass_power_two':data['total_binomial_mass_power_two'],
            'full_source_population_size_power_two':4*data['k'],
            'binomial_cells_represented':data['binomial_cells_represented'],
            'all_frontier_boundaries_independently_checked':checks,
            'cutoffs_sha256':sha256(json.dumps(cutoffs).encode()).hexdigest(),
            'proves_improvement_over_repeated_C69':rounded < control,
            'proves_loss_to_repeated_C69':base > control,
            'scope':'Exact count-statistic upper bound for all sources and queries under the declared law; finite average is not evaluated exactly, and the large source population is not physically enumerated.'}


@cache
def small_populations():
    rows = []
    for k in range(1,4):
        for a in range(k+1):
            errors = failures = length_bad = queries = 0
            messages = set()
            for source in range(16**k):
                blocks = tuple((source >> (4*r)) & 15 for r in range(k))
                parent,diag = codec.encode(blocks,a,diagnostics=True)
                messages.add(parent)
                failures += not diag['regular']
                length_bad += not diag['interval_length_guaranteed']
                if not parent < (1 << (2*k)):
                    raise ValueError('Small parent capacity failed')
                for r,x in enumerate(blocks):
                    response = codec.decode_response(parent,r,k,a)
                    if response != (codec.response(x,r<a) if diag['regular'] else 0):
                        raise ValueError('Arithmetic midpoint did not recover the intended response sequence')
                    for o in range(4):
                        child = codec.update(parent,r,o,k,a)
                        for j in range(4):
                            if o != j:
                                errors += codec.predict(child,r,o,j) != ((x >> j) & 1)
                                queries += 1
            bound = finite.bound(k,a)
            risk = F(errors,queries)
            if not (bound['base_error'] <= risk <= bound['error_upper']
                    and F(failures,16**k) <= F(length_bad,16**k) == bound['failure_event_upper_probability']):
                raise ValueError('Full small population contradicts the conditional overflow bound')
            rows.append({'k':k,'oracle_blocks':a,'source_assignments':16**k,'errors':errors,
                         'outcomes':queries,'physical_final_queries':queries,'used_parent_messages':len(messages),
                         'encoder_fallback_sources':failures,'length_bad_sources':length_bad,'exact_error':str(risk)})
    return rows


@cache
def large_diagnostics():
    rows = []
    for k in (1536,12288):
        for schedule,get_a in (('entropy',codec.default_count),('rational',codec.rational_count)):
            a = get_a(k)
            for family in range(3):
                if family == 0:
                    blocks = (0,)*k
                elif family == 1:
                    blocks = tuple((11*r+5) % 16 for r in range(k))
                else:
                    blocks = tuple((3,5,6,9,10,12)[r % 6] if r < a else 15 for r in range(k))
                parent,diag = codec.encode(blocks,a,diagnostics=True)
                positions = sorted({0,a-1,a,k//4,k//2,k-1})
                calls = 0
                for r in positions:
                    word = codec.response(blocks[r],r<a) if diag['regular'] else 0
                    for o in range(4):
                        z = codec.update(parent,r,o,k,a)
                        if z != (word >> o) & 1:
                            raise ValueError('Large actor route disagrees with its charged parent')
                        for j in range(4):
                            if o != j:
                                if codec.predict(z,r,o,j) != z:
                                    raise ValueError('Final child-only route changed')
                                calls += 1
                rows.append({'k':k,'schedule':schedule,'oracle_blocks':a,'constructed_source_family':family,
                             'regular':diag['regular'],'length_guaranteed':diag['interval_length_guaranteed'],
                             'parent_bit_length':parent.bit_length(),'parent_sha256':finite.integer_digest(parent),
                             'public_query_positions':positions,'physical_final_queries':calls})
    return rows


def discovery_check():
    d = HERE/'discovery'
    meta = json.loads((d/'metadata.json').read_text(encoding='utf-8'))
    for name,digest in meta['file_sha256'].items():
        if sha256((d/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Preserved entropy-coding discovery changed')
    for name,row in meta['upstream'].items():
        if sha256((ROOT/name).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Original C69 result changed')
    for name in ('conditional_six_block_2026-10-02.json','rate_curve_2026-10-02.json'):
        old = json.loads((HERE.parent/'results'/name).read_text(encoding='utf-8'))
        for path,digest in old['source_sha256'].items():
            if sha256((ROOT/path).read_bytes()).hexdigest() != digest:
                raise ValueError('Original C67/C69 source bindings changed')
    for name,get_a in (('prototype_probe.json',codec.rational_count),('entropy_probe.json',codec.default_count)):
        records = json.loads((d/name).read_text(encoding='utf-8'))
        if tuple(r['k'] for r in records) != LENGTHS:
            raise ValueError('Preserved schedule-probe length set changed')
        for r in records:
            a = get_a(r['k'])
            data = finite.bound(r['k'],a)
            if a != r['oracle_blocks'] or any(str(float(data[key])) != r[key]
                    for key in ('base_error','failure_event_upper_probability','conditional_excess_upper','error_upper')):
                raise ValueError('Discovery display cannot be reproduced from its exact counts')
    return {'preserved_probe_lengths_per_schedule':8,'prototype_control_retained':True,
            'float_displays_used_in_numeric_proof':False,'new_model_calls':0,
            'source_snapshots':'Prototype files preserve actual bytes; revised scratch script imports evolving production code, not a frozen historical runtime.'}


def certificate():
    discovery = discovery_check()
    control = F(2304567,8388608)
    bounds = []
    for k in LENGTHS:
        for name,get_a in (('entropy',codec.default_count),('rational',codec.rational_count)):
            bounds.append(serialize_bound(finite.bound(k,get_a(k)),name,control))
    small = small_populations()
    large = large_diagnostics()
    files = [HERE/name for name in ('codec.py','finite.py','certificate.py','test_entropy.py')]
    files += sorted(p for p in (HERE/'discovery').iterdir() if p.suffix in ('.py','.json'))
    files += [HERE.parent/'results'/name for name in ('conditional_six_block_2026-10-02.json','rate_curve_2026-10-02.json')]
    files += [HERE.parent/'joint_coding/decoder_frontier.py']
    return {'version':'hard_cap_entropy_parent_v1','date':'2026-10-02','new_model_calls':0,'new_natural_episodes':0,
            'source_sha256':{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in files},
            'information_contract':{'source':'uniform iid four-bit blocks','R_O_J':'independent uniform block/omission/remaining coordinate',
                'parent_bits':'2*k including one fallback flag','child_bits':1,
                'public_before_X':['k','a or its public schedule','response words','fixed probability counts'],
                'parent_before_R_O':True,'child_before_J':True,'updater_inputs':['M','R','O','public k/a/tables'],
                'final_inputs':['Z','R','O','J'],'archives_sessions_source_parent_rereads':False,
                'instance_intervals_output_lists_statistics_or_source_reaching_updater':False,
                'temporary_computation':'Exact integer workspace is permitted inside an encoder/updater; only M or Z crosses its boundary.'},
            'quantizers':quantizers(),'public_label_probability_payload_bytes':len(codec.pack_tables()),
            'regular_grid_points':'2**(2*k-1)','valid_fallback_messages':1,'flag_bits_charged_inside_parent':1,
            'asymptotic':asymptotic(),'finite_bounds':bounds,'repeated_C69_control_error':str(control),
            'finite_bounds_are_not_exact_large_code_risks':True,
            'small_full_population_actor_checks':small,
            'small_physical_final_queries':sum(r['physical_final_queries'] for r in small),
            'small_source_assignments':sum(r['source_assignments'] for r in small),
            'large_constructed_diagnostics':large,
            'large_diagnostic_physical_final_queries':sum(r['physical_final_queries'] for r in large),
            'large_uniform_source_populations_enumerated':False,
            'complexity':'Encoder/selected-prefix updater have O(k) steps on O(k)-bit integers, hence polynomial bit complexity; public entropy planning uses binary search and exact O(k)-bit integer powers. No portable runtime or optimality claim.',
            'discovery':discovery,
            'limits':'Specific uniform-source/query law and two fixed scalar quantizers. A hard cap is implemented, not merely an average code length. Exact conditional overflow sums supply conservative finite upper bounds; small populations execute every query, large diagnostics are constructed spots. Four checked smaller lengths provably lose to C69; the rational control beats the entropy schedule at some larger lengths. The implemented entropy schedule limit remains above C67, so no efficient near-optimal guarantee. Generic entropy-constrained quantization, arithmetic intervals, time sharing and concentration are established; external proof/priority, other laws and natural-agent/token/cost benefit remain open. Old results and provider allocations unchanged.'}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'limit':result['asymptotic']['implemented_entropy_schedule_error_limit_enclosure'],
                      'finite_12288':[{key:r[key] for key in ('schedule','oracle_blocks','coded_error_upper_rounded_outward')} for r in result['finite_bounds'] if r['k']==12288],
                      'small_queries':result['small_physical_final_queries'],'large_queries':result['large_diagnostic_physical_final_queries'],
                      'source_bindings':len(result['source_sha256']),'public_bytes':result['public_label_probability_payload_bytes']}))


if __name__ == '__main__':
    main()
