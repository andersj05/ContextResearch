"""Exact source grading, independent small actors and whole-population bounds."""
from collections import Counter
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

from . import bounds, codec
from experiments.dependency_memory.tie_coding import design, codec as original
from experiments.dependency_memory.joint_coding import decoder_frontier as display

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE.parent/'results/weighted_overflow_2026-10-02.json'
LENGTHS = (96, 192, 384, 768, 1536, 3072, 6144, 12288)


def digest_integer(value):
    return sha256(value.to_bytes(max(1, (value.bit_length()+7)//8), 'big')).hexdigest()


def rounded(value, places=15):
    scale = 10**places
    return F(-(-value.numerator*scale//value.denominator), scale)


def direct_loss(x, word):
    return sum(((x >> j)&1) != ((word >> o)&1)
               for o in range(4) for j in range(4) if o != j)


LOSS = tuple(tuple(direct_loss(x, w) for w in range(16)) for x in range(16))


@cache
def oracle_identity():
    rows = []
    for fallback in range(16):
        sums = [0, 0]
        for x in range(16):
            word = sum((sum((x >> j)&1 for j in range(4) if j != o) > 1) << o
                       for o in range(4))
            delta = LOSS[x][fallback]-LOSS[x][word]
            if delta < 0:
                raise ValueError('Oracle can never increase fixed-fallback loss')
            sums[x.bit_count() == 2] += delta
        if sums != [36, 12]:
            raise ValueError('Oracle weighted-moment identity depends on fallback')
        rows.append({'fallback_word':fallback, 'constant_fiber_excess_sum':sums[0],
                     'balanced_fiber_excess_sum':sums[1]})
    return rows


@cache
def small_populations():
    specs = [(n, 1, a) for n in (1, 2, 3) for a in range(n+1)]
    specs += [(1, g, a) for g in (2, 3) for a in (0, 1)]
    rows = []
    for n, g, a in specs:
        k = n*g
        loss = excess_bad = fallbacks = bad = queries = 0
        low_counts = Counter()
        low_delta = Counter()
        for source in range(16**k):
            xs = tuple((source >> (4*r))&15 for r in range(k))
            parent, diag = codec.encode(xs, g, a, diagnostics=True)
            intended = []
            for r, x in enumerate(xs):
                if r < a*g:
                    word = sum((sum((x >> j)&1 for j in range(4) if j != o) > 1) << o
                               for o in range(4))
                else:
                    group = xs[(r//g)*g:(r//g+1)*g]
                    binary = original.completion(group, g)
                    word = 15 if (binary >> (r % g))&1 else 0
                intended.append(word)
            delta = sum(LOSS[x][0]-LOSS[x][w] for x, w in zip(xs, intended))
            if delta < 0:
                raise ValueError('A source has negative fallback excess')
            bad += not diag['length_guaranteed']
            fallbacks += not diag['regular']
            if not diag['length_guaranteed']:
                excess_bad += delta
            for r, x in enumerate(xs):
                for o in range(4):
                    z = codec.update(parent, r, o, n, g, a)
                    if z != (((intended[r] if diag['regular'] else 0) >> o)&1):
                        raise ValueError('An actor changes its intended response')
                    for j in range(4):
                        if j != o:
                            loss += codec.predict(z, r, o, j) != ((x >> j)&1)
                            queries += 1
            if n == 1 and a == 0:
                binary = original.completion(xs, g)
                low_counts[binary] += 1
                low_delta[binary] += delta
        base = F(5, 16)-F(a, 16*n)
        actual = F(loss, queries)
        weighted_event = F(excess_bad, queries)
        if not base <= actual <= base+weighted_event:
            raise ValueError('Complete population does not respect loss-weighted overflow')
        if n == 1 and a == 0:
            priority, counts = design.prepare(g)
            if (tuple(low_counts[w] for w in priority) != counts
                    or tuple(low_delta[w] for w in priority) != bounds.loss_weights(g)):
                raise ValueError('Literal routed cell losses differ from source-category moments')
        for degree in bounds.DEGREES:
            if weighted_event > bounds.excess_upper(n, g, a, degree):
                raise ValueError('A Chernoff moment underestimates complete weighted overflow')
        rows.append({'n':n, 'g':g, 'a':a, 'sources':16**k,
                     'physical_final_queries':queries, 'errors':loss,
                     'exact_actual_error':str(actual), 'base_error':str(base),
                     'actual_fallback_sources':fallbacks, 'length_bad_sources':bad,
                     'exact_loss_weighted_length_event':str(weighted_event)})
    return rows


@cache
def finite_rows():
    old = json.loads((HERE.parent/'results/tie_coding_2026-10-02.json').read_text())
    scalar = json.loads((HERE.parent/'results/entropy_coding_2026-10-02.json').read_text())
    old_by_k = {r['k']:r for r in old['best_checked_bound_by_length']}
    scalar_lower = {}
    for r in scalar['finite_bounds']:
        scalar_lower.setdefault(r['k'], []).append(F(r['base_error_lower_for_this_fixed_code']))
    control = F(2304567, 8388608)
    margin_rows = []
    selected = []
    plans = []
    for k in LENGTHS:
        n = k//8
        for multiplier in (2, 3, 4, 5, 6):
            a = original.default_count(n, 8, multiplier)
            result = bounds.bound(n, 8, a)
            upper = rounded(result['error_upper'])
            margin_rows.append({'k':k, 'n':n, 'g':8, 'multiplier':multiplier, 'a':a,
                'degree':result['degree'], 'base_error':str(result['base']),
                'error_upper':str(upper), 'excess_upper':str(rounded(result['excess_upper']))})
        for degree in bounds.DEGREES:
            plan = bounds.allocation(n, 8, degree)
            plans.append({'k':k, 'degree':degree, 'a':plan['a'],
                'error_upper':str(rounded(plan['error_upper'])),
                'raw_error_upper_numerator_sha256':digest_integer(plan['raw_error_upper'].numerator),
                'raw_error_upper_denominator_sha256':digest_integer(plan['raw_error_upper'].denominator),
                'binary_comparisons':plan['binary_comparisons'],
                'difference_before_negative':plan['difference_before'] is None or plan['difference_before'] < 0,
                'difference_after_nonnegative':plan['difference_after'] is None or plan['difference_after'] >= 0,
                'positive_base_and_ratio_ge_one':plan['u'] >= 0 and plan['v'] >= 0 and plan['B'] > 1})
        a, degree = bounds.select(n, 8)
        result = bounds.allocation(n, 8, degree)
        upper = rounded(result['error_upper'])
        prior = old_by_k[k]
        selected.append({'k':k, 'n':n, 'g':8, 'a':a, 'degree':degree,
            'parent_bits':2*k, 'charged_flag_bits':1, 'child_bits':1,
            'base_error_lower':str(result['base']), 'error_upper':str(upper),
            'error_upper_decimal':display.decimal_enclosure(upper, upper, 15),
            'old_C72_a':prior['oracle_groups'],
            'old_C72_upper':prior['conservative_error_upper'],
            'old_C72_base_error_lower':prior['base_error_lower'],
            'strictly_tighter_than_old_C72_certificate':upper < F(prior['conservative_error_upper']),
            'proves_actual_improvement_over_old_C72_selected_code':upper < F(prior['base_error_lower']),
            'proves_improvement_over_C69':upper < control,
            'proves_loss_to_C69':result['base'] > control,
            'proves_improvement_over_both_named_C71_codes':upper < min(scalar_lower[k]),
            'public_allocation_is_bound_optimal_only':True,
            'large_source_population_power_two':4*k,
            'large_source_population_enumerated':False})
    return margin_rows, plans, selected


def entropy_bounds(counts, g):
    total = 16**g
    logs = {c:design.log2_bounds(c, 192) for c in set(counts)}
    return (4*g-sum(F(c, total)*logs[c][1] for c in counts),
            4*g-sum(F(c, total)*logs[c][0] for c in counts))


@cache
def discovery_check():
    folder = HERE/'discovery'
    meta = json.loads((folder/'metadata.json').read_text())
    for name, digest in meta['file_sha256'].items():
        if sha256((folder/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Original discovery bytes changed')
    for path, digest in meta['upstream_sha256'].items():
        if sha256((ROOT/path).read_bytes()).hexdigest() != digest:
            raise ValueError('Upstream result or warm-start source changed')
        if path.endswith('.json'):
            for source, pinned in json.loads((ROOT/path).read_text())['source_sha256'].items():
                if sha256((ROOT/source).read_bytes()).hexdigest() != pinned:
                    raise ValueError('An upstream evidence binding changed')
    oracle = design.entropies(1, 192)[1]
    low_control = tuple(h/8 for h in design.entropies(8, 192)[0])
    summaries, points = [], []
    sources = corrections = 0
    for name, record in meta['raw_records'].items():
        raw = gzip.decompress((folder/(name+'.gz')).read_bytes())
        if len(raw) != record['bytes'] or sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('Compression changed the original raw JSON')
        data = json.loads(raw)
        g, population = data['g'], 16**data['g']
        if len(data['runs']) != record['starts']:
            raise ValueError('Inspected starts count changed')
        for index, row in enumerate(data['runs']):
            mapping = row['mapping']
            if len(mapping) != population or any(type(w) is not int or not 0 <= w < population for w in mapping):
                raise ValueError('Malformed unsigned group quantizer')
            original_counts = Counter(mapping)
            fallback = max(original_counts, key=lambda w:(original_counts[w], -w))
            original_loss = corrected_loss = changed = 0
            counts = Counter()
            for x, w in enumerate(mapping):
                raw_cost = sum(LOSS[(x >> (4*r))&15][(w >> (4*r))&15] for r in range(g))
                zero_cost = sum(LOSS[(x >> (4*r))&15][(fallback >> (4*r))&15] for r in range(g))
                original_loss += raw_cost
                chosen = fallback if raw_cost > zero_cost else w
                corrected_loss += min(raw_cost, zero_cost)
                counts[chosen] += 1
                changed += chosen != w
            if original_loss != row['loss_sum'] or sum(counts.values()) != population:
                raise ValueError('Literal routed losses or occupancies differ')
            error = F(corrected_loss, 12*g*population)
            entropy = entropy_bounds(tuple(counts.values()), g)
            rate = tuple(h/g for h in entropy)
            if error == F(1, 4):
                # The per-omission three-bit majority is unique; attaining the
                # sum of its minima forces its complete product quantizer.
                rate = oracle
            if rate[0] <= 2 <= rate[1]:
                raise ValueError('An entropy enclosure crosses the comparison rate')
            # Every new point lies above the chord of the stronger old control
            # and oracle. This also excludes an improving convex mixture that
            # combines a discovered point with the existing low control.
            if error > F(1, 4):
                high = oracle[1] if rate[0] >= low_control[1] else oracle[0]
                line_upper = F(5, 16)-F(1, 16)*(rate[0]-low_control[1])/(high-low_control[1])
                if error <= line_upper:
                    raise ValueError('A discovered quantizer may improve the old control chord')
            points.append((error, rate, f'{name}:{index}'))
            summaries.append({'record':name, 'index':index, 'g':g,
                'slope':row['slope'], 'seed':row['seed'], 'stable':row['stable'],
                'literal_sources_graded':population, 'original_integer_loss':original_loss,
                'cost_capped_integer_loss':corrected_loss, 'cost_cap_changed_sources':changed,
                'fallback_word':fallback, 'positive_output_cells':len(counts),
                'exact_cost_capped_error':str(error),
                'entropy_per_block':display.decimal_enclosure(*rate, 12),
                'mapping_sha256':sha256(raw_map_bytes(mapping, g)).hexdigest()})
            sources += population
            corrections += changed
    points.append((F(1, 4), oracle, 'explicit-oracle-control'))
    low = [p for p in points if p[1][1] < 2]
    high = [p for p in points if p[1][0] > 2]
    candidates = [(p[0], p[2], None) for p in low]
    pair_count = 0
    for left in low:
        for right in high:
            # At rate two, oracle fraction decreases as either endpoint
            # entropy increases. Choose outward endpoints for a LOWER score.
            endpoints = (left[1][0], right[1][0]) if right[0] <= left[0] else (left[1][1], right[1][1])
            share = (2-endpoints[0])/(endpoints[1]-endpoints[0])
            value = left[0]+(right[0]-left[0])*share
            candidates.append((value, left[2], right[2]))
            pair_count += 1
    best = min(candidates, key=lambda row:(row[0], row[1], row[2] or ''))
    old_limit_upper = F(269293075343, 10**12)
    if best[0] <= old_limit_upper:
        raise ValueError('Discovery no longer supports the stated negative comparison')
    return {'starts_independently_graded':len(summaries), 'uniform_group_sources_graded':sources,
            'cost_cap_changed_sources':corrections, 'complete_final_quantizer_maps_checked':True,
            'float_objective_not_used_in_numeric_proof':True,
            'new_points_above_old_C72_oracle_chord':True,
            'interpolation_pairs_lower_bounded':pair_count,
            'best_rate_two_interpolation_lower':str(F(best[0].numerator*10**12//best[0].denominator, 10**12)),
            'best_interpolation_records':[best[1], best[2]],
            'old_C72_limit_upper_for_negative_comparison':str(old_limit_upper),
            'all_discovered_rate_two_interpolations_provably_lose_to_old_C72_limit':True,
            'rows':summaries}


def raw_map_bytes(mapping, g):
    width = (4*g+7)//8
    return b''.join(w.to_bytes(width, 'little') for w in mapping)


@cache
def large_diagnostics():
    rows = []
    for k in (384, 768, 12288):
        n = k//8
        a, degree = bounds.select(n, 8)
        for family in ('zeros', 'cycle', 'balanced'):
            xs = ((0,)*k if family == 'zeros' else (3,)*k if family == 'balanced'
                  else tuple((11*r+5)%16 for r in range(k)))
            parent, diag = codec.encode(xs, diagnostics=True)
            positions = sorted({0, a*8-1, a*8, k//2, k-1})
            positions = [r for r in positions if 0 <= r < k]
            queries = 0
            for r in positions:
                if not diag['regular']:
                    word = 0
                elif r < a*8:
                    x = xs[r]
                    word = sum((sum((x >> j)&1 for j in range(4) if j != o) > 1) << o for o in range(4))
                else:
                    binary = original.completion(xs[(r//8)*8:(r//8+1)*8], 8)
                    word = 15 if (binary >> (r % 8))&1 else 0
                for o in range(4):
                    z = codec.update(parent, r, o, n)
                    if z != (word >> o)&1:
                        raise ValueError('Large constructed route differs')
                    for j in range(4):
                        if o != j:
                            if codec.predict(z, r, o, j) != z:
                                raise ValueError('Final route needs extra state')
                            queries += 1
            rows.append({'k':k, 'a':a, 'degree':degree, 'family':family,
                'regular':diag['regular'], 'parent_bit_length':parent.bit_length(),
                'parent_sha256':digest_integer(parent), 'query_positions':positions,
                'physical_final_queries':queries})
    return rows


def timing_check():
    record = json.loads((HERE/'local_timings_2026-10-02.json').read_text())
    for path, pinned in record['source_sha256'].items():
        if sha256((ROOT/path).read_bytes()).hexdigest() != pinned:
            raise ValueError('A local timing sample refers to changed code')
    for row in record['planning']:
        if bounds.select(row['k']//8, 8) != (row['a'], row['degree']):
            raise ValueError('Local planning sample differs from the exact public plan')
        if min(row['wall_ns'], row['process_cpu_ns']) < 0:
            raise ValueError('Invalid local timing value')
    for row in record['constructed_actors']:
        k, family = row['k'], row['family']
        xs = ((0,)*k if family == 'zeros' else (3,)*k if family == 'balanced'
              else tuple((11*r+5)%16 for r in range(k)))
        if sha256(bytes(xs)).hexdigest() != row['constructed_input_sha256']:
            raise ValueError('Local actor sample has an unpinned input')
        if row['parent_bit_length'] > 2*k:
            raise ValueError('Measured actor exceeds the parent cap')
        for stage in ('encode', 'update_last_block', 'predict'):
            if min(row[stage]['wall_ns'], row[stage]['process_cpu_ns']) < 0:
                raise ValueError('Invalid stage timing')
    return record


def certificate():
    discovery = discovery_check()
    small = small_populations()
    margins, plans, finite = finite_rows()
    large = large_diagnostics()
    timings = timing_check()
    probe = json.loads((HERE/'discovery/weighted_probe.json').read_text())
    for row in probe:
        matched = next(r for r in margins if (r['k'], r['multiplier']) == (row['k'], row['c']))
        if (matched['a'], matched['degree'], matched['base_error'], matched['error_upper']) != (
                row['a'], row['s'], row['base'], row['upper']):
            raise ValueError('Original weighted-margin probe does not reproduce exactly')
    files = [HERE/name for name in ('bounds.py', 'codec.py', 'certificate.py', 'test_weighted.py',
                                   'benchmark.py', 'local_timings_2026-10-02.json')]
    files += sorted(p for p in (HERE/'discovery').iterdir() if p.is_file() and p.suffix != '.md')
    files += [HERE.parent/'tie_coding'/name for name in ('design.py', 'bounds.py', 'codec.py')]
    files += [HERE.parent/'results'/name for name in
              ('tie_coding_2026-10-02.json', 'entropy_coding_2026-10-02.json',
               'conditional_six_block_2026-10-02.json', 'greedy_coding_2026-10-02.json')]
    return {'version':'loss_weighted_overflow_v1', 'date':'2026-10-02',
        'source_sha256':{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in files},
        'new_model_calls':0, 'new_natural_episodes':0,
        'information_contract':{'source':'uniform iid four-bit blocks',
            'queries':'independent uniform R/O/J', 'parent_bits':'2*k including one flag',
            'child_bits':1, 'parent_before_R_O':True, 'child_before_J':True,
            'public_n_g_a_tables_before_X':True, 'final_inputs':['Z', 'R', 'O', 'J'],
            'no_source_parent_workspace_archive_environment_provider_reread':True,
            'actors':'C72 pure functions; new public allocation wrapper. Temporary stage computation discarded; no untrusted-process isolation.'},
        'public_table_envelope_bytes':262144, 'deployed_fixed_eight_table_bytes':1288,
        'storage_scope':'Only original cover/oracle response/count payload. Public n/g/a, program/runtime/framing and runtime workspace separate. Discovery maps are unused by actors.',
        'oracle_fixed_fallback_identity':oracle_identity(),
        'small_complete_actor_populations':small,
        'small_physical_final_queries':sum(r['physical_final_queries'] for r in small),
        'all_degrees_convexity_checks':[{'g':g, 'degree':d,
            'conditions':bounds.allocation(1, g, d)['B'] > 1 and bounds.allocation(1, g, d)['v'] >= 0}
            for g in bounds.GROUPS for d in bounds.DEGREES],
        'forty_old_margin_plans_with_new_bounds':margins,
        'forty_full_allocation_bound_minima':plans, 'selected_finite_codes':finite,
        'large_constructed_diagnostics':large,
        'large_diagnostic_queries':sum(r['physical_final_queries'] for r in large),
        'large_uniform_source_populations_enumerated':False,
        'local_timing_samples':timings,
        'discovery':discovery,
        'limits':'Established Chernoff/entropy-constrained quantization/time sharing, not generic algorithm novelty. Exact minimization is of each outward bound over integer a and five declared degrees, not actual code risk, every exponent, codebook or global finite optimum. Cost-capped search maps do not beat the old C72 entropy/distortion chord and are not deployed. New finite selector changes public allocations; its actual asymptotic limit has not been established. Old C72/C73 families, sources and claims remain unchanged. Larger population statements are conservative proofs, not exact errors/fallback rates or physical source enumeration. External correctness/priority, useful near-C67 coding and natural-agent/model/token/credit/production benefit remain open.'}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({'finite_codes':result['selected_finite_codes'],
        'discovery_starts':result['discovery']['starts_independently_graded'],
        'discovery_source_assignments':result['discovery']['uniform_group_sources_graded'],
        'small_queries':result['small_physical_final_queries'],
        'large_queries':result['large_diagnostic_queries'],
        'bindings':len(result['source_sha256'])}, indent=2))


if __name__ == '__main__':
    main()
