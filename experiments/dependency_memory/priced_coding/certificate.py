"""Public finite plans, full small actors, and bounded large diagnostics."""
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

from . import evidence, design, bounds, codec, tables
from .controls import constant_book, oracle_book
from experiments.dependency_memory.weighted_overflow import certificate as prior
from experiments.dependency_memory.joint_coding import decoder_frontier as display

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE.parent/'results/priced_coding_2026-10-02.json'
LENGTHS = (384, 768, 1536, 3072, 6144, 12288)


def public_plan(k, book, row, degree):
    n, r = divmod(k, book.g)
    if not n:
        raise ValueError('Finite comparison requires a full group')
    plan = bounds.allocation(n, book, tuple(row['loss_sums']), F(row['quantizer_error']), degree)
    total = F(n*book.g, k)*plan['error_upper']+F(r, k)*F(9, 32)
    base = F(n*book.g, k)*plan['base']+F(r, k)*F(9, 32)
    return total, {'k':k, 'g':book.g, 'n':n, 'tail_blocks':r, 'book':row['name'],
        'a':plan['a'], 'degree':degree, 'base_error':str(base),
        'error_upper':str(prior.rounded(total)),
        'error_upper_display':display.decimal_enclosure(total, total, 12)[1],
        'convex':plan['convex'], 'method':plan['method'],
        'binary_comparisons':plan['evaluations'],
        'left_difference_sign':None if plan['left_difference'] is None else
            (plan['left_difference'] > 0)-(plan['left_difference'] < 0),
        'right_difference_sign':None if plan['right_difference'] is None else
            (plan['right_difference'] > 0)-(plan['right_difference'] < 0)}


@cache
def finite_rows():
    discovery, books = evidence.grade_discovery()
    previous = json.loads(prior.OUTPUT.read_text(encoding='utf-8'))
    old = {row['k']:row for row in previous['selected_finite_codes']}
    target, target_scores = [], []
    for row in discovery['rows']:
        plans = [public_plan(12288, books[row['name']], row, d) for d in bounds.DEGREES]
        score, best = min(plans, key=lambda pair:(pair[0], pair[1]['a'], pair[1]['degree']))
        target.append({'book':row['name'], 'plans':[p for _,p in plans], 'best':best,
            'upper_below_C74_upper':score < F(old[12288]['error_upper']),
            'upper_below_named_C74_base':score < F(old[12288]['base_error_lower'])})
        target_scores.append((score, row['name']))
    _, selected = min(target_scores)
    finite_name, slack_name = tables.names()
    if finite_name != selected or tables.load(finite_name) != books[selected]:
        raise ValueError('Frozen finite descriptor differs from full target-bound comparison')
    for name in {finite_name, slack_name}:
        matched = next(r for r in discovery['rows'] if r['name'] == name)
        if tables.weights(name) != (tuple(matched['loss_sums']), F(matched['quantizer_error'])):
            raise ValueError('Public planning weights differ from literal complete grading')
    valid_limits = [(bounds.limiting_error(books[r['name']], F(r['quantizer_error'])), r['name'])
                    for r in discovery['rows'] if r['separate_slack_family_actual_limit'] is not None]
    # A smallest upper enclosure is an explicit public design choice; narrow
    # disjoint comparisons below establish the reported named improvements.
    _, selected_slack = min(valid_limits, key=lambda pair:(pair[0][1], pair[1]))
    if slack_name != selected_slack or tables.load(slack_name) != books[slack_name]:
        raise ValueError('Frozen limiting-family descriptor differs from outward comparison')
    row = next(r for r in discovery['rows'] if r['name'] == selected)
    selected_rows, all_plans = [], []
    for k in LENGTHS:
        candidates = [public_plan(k, books[selected], row, d) for d in bounds.DEGREES]
        score, plan = min(candidates, key=lambda pair:(pair[0], pair[1]['a'], pair[1]['degree']))
        all_plans.extend(p for _,p in candidates)
        plan.update({'C74_named_base':old[k]['base_error_lower'], 'C74_upper':old[k]['error_upper'],
            'upper_below_C74_upper':score < F(old[k]['error_upper']),
            'upper_below_named_C74_base':score < F(old[k]['base_error_lower']),
            'upper_below_exact_C69':score < F(2304567, 8388608),
            'base_above_exact_C69':F(plan['base_error']) > F(2304567, 8388608)})
        selected_rows.append(plan)
    return target, all_plans, selected_rows


@cache
def small_populations():
    specs = [(constant_book(1), k, a) for k in (1, 2, 3) for a in range(k+1)]
    specs += [(constant_book(2), k, a) for k in (1, 2, 3) for a in range(k//2+1)]
    specs += [(oracle_book(), k, a) for k in (1, 2) for a in range(k+1)]
    rows = []
    for book, k, a in specs:
        n, r = divmod(k, book.g)
        low_error = F(sum(evidence.group_loss(x, book.words[design.choose(x, book)], book.g)
                          for x in range(16**book.g)), 12*book.g*16**book.g)
        base = (F(n*book.g, k)*(low_error+F(a, n)*(F(1, 4)-low_error)) if n else F(0))
        base += F(r, k)*F(9, 32)
        errors = excess_bad = queries = fallback_sources = bad_sources = 0
        for xs in product(range(16), repeat=k):
            parent, diag = codec.encode(xs, book, a, diagnostics=True)
            intended = []
            for block, x in enumerate(xs):
                if block >= n*book.g:
                    word = min(enumerate(codec.TAIL), key=lambda item:(evidence.LOSS[x][item[1]], item[0]))[1]
                elif block < a*book.g:
                    word = sum((sum((x >> j)&1 for j in range(4) if j != o)>1) << o for o in range(4))
                else:
                    source = sum(xs[(block//book.g)*book.g+j] << (4*j) for j in range(book.g))
                    word = (book.words[design.choose(source, book)] >> (4*(block % book.g)))&15
                intended.append(word)
            delta = sum(evidence.LOSS[x][(book.words[book.fallback] >> (4*(block % book.g)))&15]
                        -evidence.LOSS[x][intended[block]]
                        for block,x in enumerate(xs[:n*book.g]))
            if delta < 0:
                raise ValueError('A small group has negative fallback excess')
            if n:
                fallback_sources += not diag['regular']
                bad_sources += not diag['length_guaranteed']
                if not diag['length_guaranteed']:
                    excess_bad += delta
            for block, x in enumerate(xs):
                word = intended[block]
                if block < n*book.g and not diag['regular']:
                    word = (book.words[book.fallback] >> (4*(block % book.g)))&15
                for o in range(4):
                    z = codec.update(parent, block, o, k, book, a)
                    if z != ((word >> o)&1):
                        raise ValueError('A charged small actor changes its response')
                    for j in range(4):
                        if j != o:
                            errors += codec.predict(z, block, o, j) != ((x >> j)&1)
                            queries += 1
        actual, weighted = F(errors, queries), F(excess_bad, queries)
        if not base <= actual <= base+weighted:
            raise ValueError('Full small population violates the weighted overflow bound')
        if n:
            losses = [0]*len(book.words)
            for x in range(16**book.g):
                index = design.choose(x, book)
                losses[index] += evidence.group_loss(x, book.words[book.fallback], book.g)-evidence.group_loss(x, book.words[index], book.g)
            for degree in bounds.DEGREES:
                if weighted > F(n*book.g, k)*bounds.excess_upper(n, book, tuple(losses), a, degree):
                    raise ValueError('An outward generic moment misses a complete weighted event')
        rows.append({'g':book.g, 'words':len(book.words), 'k':k, 'a':a,
            'sources':16**k, 'tail_blocks':r, 'physical_final_queries':queries,
            'errors':errors, 'actual_error':str(actual), 'base_error':str(base),
            'length_bad_sources':bad_sources, 'actual_fallback_sources':fallback_sources,
            'weighted_length_excess':str(weighted)})
    return rows


@cache
def large_diagnostics():
    _, _, finite = finite_rows()
    rows = []
    name, _ = tables.names()
    book = tables.load(name)
    for plan in finite:
        if plan['k'] not in (384, 768, 12288):
            continue
        k, a = plan['k'], plan['a']
        for family in ('zeros', 'cycle', 'balanced'):
            xs = ((0,)*k if family == 'zeros' else (3,)*k if family == 'balanced'
                  else tuple((11*j+5)%16 for j in range(k)))
            parent, diag = codec.encode(xs, book, a, diagnostics=True)
            positions = [v for v in sorted({0, a*book.g-1, a*book.g, k//2,
                                           diag['full_groups']*book.g, k-1}) if 0 <= v < k]
            queries = 0
            for block in positions:
                if block >= diag['full_groups']*book.g:
                    word = min(enumerate(codec.TAIL),key=lambda item:(evidence.LOSS[xs[block]][item[1]],item[0]))[1]
                elif not diag['regular']:
                    word = (book.words[book.fallback] >> (4*(block % book.g)))&15
                elif block < a*book.g:
                    x = xs[block]
                    word = sum((sum((x >> j)&1 for j in range(4) if j != o)>1) << o for o in range(4))
                else:
                    source = sum(xs[(block//book.g)*book.g+j] << (4*j) for j in range(book.g))
                    word = (book.words[design.choose(source, book)] >> (4*(block % book.g)))&15
                for o in range(4):
                    z = codec.update(parent, block, o, k, book, a)
                    if z != ((word >> o)&1):
                        raise ValueError('Large constructed actor differs from public response')
                    for j in range(4):
                        if j != o:
                            if codec.predict(z, block, o, j) != z:
                                raise ValueError('Final actor needs undeclared state')
                            queries += 1
            rows.append({'k':k, 'a':a, 'degree':plan['degree'], 'book':name, 'family':family,
                'regular':diag['regular'], 'length_guaranteed':diag['length_guaranteed'],
                'parent_bit_length':parent.bit_length(), 'parent_sha256':prior.digest_integer(parent),
                'query_positions':positions, 'physical_final_queries':queries})
    return rows


def timing_check():
    p = HERE/'local_timings_2026-10-02.json'
    if not p.exists():
        return {'status':'not measured'}
    data = json.loads(p.read_bytes())
    for path, expected in data['source_sha256'].items():
        if sha256((ROOT/path).read_bytes()).hexdigest() != expected:
            raise ValueError('A timing sample refers to changed source')
    for row in data['samples']:
        if min(row['wall_ns'], row['process_cpu_ns']) < 0:
            raise ValueError('Negative local timing')
    return data


def certificate():
    discovery, books = evidence.grade_discovery()
    targets, plans, finite = finite_rows()
    small, large = small_populations(), large_diagnostics()
    finite_name, slack_name = tables.names()
    row = next(r for r in discovery['rows'] if r['name'] == slack_name)
    limit = bounds.limiting_error(books[slack_name], F(row['quantizer_error']))
    files = [p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py', '.json')]
    files += sorted(p for p in (HERE/'discovery').iterdir() if p.is_file() and p.suffix != '.md')
    files += [HERE.parent/'tie_coding'/name for name in ('design.py', 'bounds.py')]
    files += [HERE.parent/'entropy_coding/codec.py', HERE.parent/'weighted_overflow/certificate.py']
    files += [HERE.parent/'results'/name for name in
              ('weighted_overflow_2026-10-02.json', 'tie_coding_2026-10-02.json',
               'conditional_six_block_2026-10-02.json', 'rate_curve_2026-10-02.json')]
    return {'version':'exact_priced_group_code_v1', 'date':'2026-10-02',
        'source_sha256':{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in files},
        'new_model_calls':0, 'new_natural_episodes':0,
        'information_contract':{'source':'uniform iid four-bit blocks',
            'queries':'independent uniform R/O/J', 'parent_bits':'2*k including fallback flag and scalar tail',
            'child_bits':1, 'parent_before_R_O':True, 'child_before_J':True,
            'public_book_counts_price_k_a_before_X':True, 'final_inputs':['Z', 'R', 'O', 'J'],
            'forbidden':'Source/old-parent/scratch/interval/output-list/instance-histogram/archive/environment/provider-session/source-dependent-cache rereads.',
            'actors':'Trusted pure functions with discarded stage workspace; not untrusted process isolation.'},
        'machine_calibration':evidence.machine_calibration(),
        'tensor_complete_small_calibration':evidence.tensor_calibration(),
        'discovery':discovery, 'all_ten_target_finite_comparisons':targets,
        'fixed_selected_book_all_five_degree_plans':plans, 'selected_finite_codes':finite,
        'deployed_finite_book':finite_name, 'separate_slack_family_book':slack_name,
        'separate_slack_family_actual_limit':display.decimal_enclosure(*limit, 12),
        'small_complete_actor_populations':small,
        'small_physical_final_queries':sum(r['physical_final_queries'] for r in small),
        'large_constructed_diagnostics':large,
        'large_physical_final_queries':sum(r['physical_final_queries'] for r in large),
        'large_uniform_actor_populations_enumerated':False,
        'public_packed_payload_bytes':{name:len(design.pack_tables(tables.load(name)))+10
                                      for name in sorted({finite_name, slack_name})},
        'public_planner_inclusive_packed_bytes':{name:
            len(design.pack_planner(tables.load(name), tables.weights(name)[0]))+10
            for name in sorted({finite_name, slack_name})},
        'public_packed_payload_envelope_bytes':262144,
        'native_search_array_envelope_bytes':268435456,
        'storage_scope':'Actor payload: selected words/proposal/CDF plus 8 oracle and 2 scalar-tail bytes. Inclusive finite planner additionally packs the fixed cell loss weights. Parameters/program/runtime/framing/JSON/Python caches/RAM/stage workspace and saved grading maps separate. Actors and public planners use no full source map.',
        'local_timing_samples':timing_check(),
        'limits':'Post-hoc mathematical design, not independent trials, new generic ECVQ/min-plus/arithmetic/Chernoff novelty, global book or actual-risk optimization. All ten native minima receive complete independent tensor checks, literal loss/CDF grading and fixed-log verification. Large hard-cap risks remain conservative analytic bounds, not exact actor population averages. Finite bound selector actual limit unproved; a separate implemented entropy-slack family has the stated actual limit. C67/C69/C71/C72/C73/C74 and their original sources/schedules unchanged. Growing C72 still has a better limiting error. Local timings are single samples, not portable speed or population latency. External correctness/priority, useful near-C67 coding, broader laws and natural-agent/model/token/credit/production benefit remain open.'}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({'finite_codes':result['selected_finite_codes'],
        'limiting_error':result['separate_slack_family_actual_limit'],
        'public_payload':result['public_packed_payload_bytes'],
        'discovery_sources':result['discovery']['complete_uniform_source_assignments'],
        'small_queries':result['small_physical_final_queries'],
        'large_queries':result['large_physical_final_queries'],
        'bindings':len(result['source_sha256'])}, indent=2))


if __name__ == '__main__':
    main()
