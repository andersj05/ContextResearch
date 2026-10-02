"""Independent weighted covers, complete small actors and rational tail bounds."""
from collections import Counter
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
import gzip
import json
from pathlib import Path

from . import design,codec,bounds
from experiments.dependency_memory.joint_coding import decoder_frontier as display

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE.parent/'results/tie_coding_2026-10-02.json'
GROUPS = (1,2,3,4,6,8)
LENGTHS = (96,192,384,768,1536,3072,6144,12288)
MULTIPLIERS = (2,3,4,5,6)
DEGREES = (8,16,32,64,128)


def digest_integer(value):
    return sha256(value.to_bytes(max(1,(value.bit_length()+7)//8),'big')).hexdigest()


def round_upper(value,places=15):
    scale = 10**places
    return F(-(-value.numerator*scale//value.denominator),scale)


def direct_loss(x,word):
    return sum(((x >> j)&1) != ((word >> o)&1)
               for o in range(4) for j in range(4) if o!=j)


@cache
def group_check(g):
    priority,counts = design.prepare(g)
    patterns = []
    observed = Counter()
    branch_sum = F(0)
    for erased in range(1 << g):
        forced = ((1 << g)-1)^erased
        values = forced
        while True:
            weight = 6**erased.bit_count()*5**forced.bit_count()
            chosen = next(w for w in priority if w&forced==values)
            observed[chosen] += weight
            branch_sum += weight*(6*erased.bit_count()+F(12,5)*forced.bit_count())
            patterns.append((forced,values,weight))
            if not values:
                break
            values = (values-1)&forced
    if tuple(observed[w] for w in priority)!=counts:
        raise ValueError('Independent forced/erased source cover disagrees')
    if branch_sum/(16**g*12*g)!=F(5,16):
        raise ValueError('Whole-source nearest-constant risk is not 5/16')
    # Recount all remaining compatible mass from scratch at every step.
    # Production instead updates precomputed incidence lists only once.
    remaining = patterns
    for word,c in zip(priority,counts):
        masses = [0]*(1 << g)
        for forced,values,weight in remaining:
            free = ((1 << g)-1)^forced
            subset = free
            while True:
                masses[values|subset] += weight
                if not subset:
                    break
                subset = (subset-1)&free
        expected = max(range(1 << g),key=lambda w:(masses[w],-w))
        if expected!=word or masses[word]!=c:
            raise ValueError('Independent complete greedy choice/tie differs')
        remaining = [(f,v,p) for f,v,p in remaining if word&f!=v]
    if remaining:
        raise ValueError('Some weighted source categories remain unassigned')
    return {'group':g,'priority':list(priority),'counts':list(counts),
            'weighted_status_categories':len(patterns),'source_mass':16**g,
            'queried_bit_error':'5/16','all_greedy_choices_independently_recounted':len(priority),
            'packed_cover_payload_bytes':len(design.pack_tables(g)),
            'scope':'All weighted source categories, not physical enumeration of all 16**g sources.'}


@cache
def literal_quantizers():
    result = []
    for g in (1,2,3):
        priority,counts = design.prepare(g)
        observed = Counter()
        errors = queries = 0
        for source in range(16**g):
            blocks = tuple((source >> (4*r))&15 for r in range(g))
            word = codec.completion(blocks,g)
            observed[word] += 1
            for r,x in enumerate(blocks):
                response = 15 if (word >> r)&1 else 0
                if direct_loss(x,response)!=min(direct_loss(x,0),direct_loss(x,15)):
                    raise ValueError('Coordinated choice increases a source-wise constant loss')
                for o in range(4):
                    z = (response >> o)&1
                    for j in range(4):
                        if o!=j:
                            errors += codec.predict(z,r,o,j)!=((x >> j)&1)
                            queries += 1
        if tuple(observed[w] for w in priority)!=counts or F(errors,queries)!=F(5,16):
            raise ValueError('Literal constant-group population does not match type grading')
        result.append({'group':g,'sources':16**g,'errors':errors,
                       'physical_final_queries':queries,'exact_error':str(F(errors,queries))})
    return result


@cache
def small_populations():
    specs = [(n,1,a) for n in (1,2,3) for a in range(n+1)]
    specs += [(1,g,a) for g in (2,3) for a in (0,1)]
    result = []
    for n,g,a in specs:
        k = n*g
        errors = queries = fallbacks = length_bad = 0
        messages = set()
        for source in range(16**k):
            blocks = tuple((source >> (4*r))&15 for r in range(k))
            parent,diag = codec.encode(blocks,g,a,diagnostics=True)
            messages.add(parent)
            fallbacks += not diag['regular']
            length_bad += not diag['length_guaranteed']
            for r,x in enumerate(blocks):
                if not diag['regular']:
                    expected = 0
                elif r<a*g:
                    expected = sum((sum((x >> j)&1 for j in range(4) if j!=o)>1) << o for o in range(4))
                else:
                    group = r//g
                    low_word = codec.completion(blocks[group*g:(group+1)*g],g)
                    expected = 15 if (low_word >> (r%g))&1 else 0
                if codec.decode_response(parent,r,n,g,a)!=expected:
                    raise ValueError('Arithmetic decoder changed the intended response')
                for o in range(4):
                    z = codec.update(parent,r,o,n,g,a)
                    for j in range(4):
                        if o!=j:
                            errors += codec.predict(z,r,o,j)!=((x >> j)&1)
                            queries += 1
        proof = bounds.error_bound(n,g,a,DEGREES)
        risk = F(errors,queries)
        if not (proof['base']<=risk<=proof['error_upper']
                and F(fallbacks,16**k)<=F(length_bad,16**k)<=proof['tail_upper']
                and len(messages)<=(1 << (2*k-1))+1):
            raise ValueError('Complete small actors contradict the risk/cap proof')
        result.append({'n':n,'g':g,'a':a,'sources':16**k,'errors':errors,
                       'physical_final_queries':queries,'actual_fallback_sources':fallbacks,
                       'length_bad_sources':length_bad,'used_parent_messages':len(messages),
                       'exact_error':str(risk)})
    return result


def fixed_limit(g):
    (lo,hi),(hlo,hhi) = design.entropies(g,256)
    fraction_lo = (2*g-hi)/(hhi-lo)
    fraction_hi = (2*g-lo)/(hlo-hi)
    low,high = F(5,16)-fraction_hi/16,F(5,16)-fraction_lo/16
    return {'group':g,'low_entropy_per_group':display.decimal_enclosure(lo,hi,12),
            'low_entropy_per_block':display.decimal_enclosure(lo/g,hi/g,12),
            'oracle_fraction':display.decimal_enclosure(fraction_lo,fraction_hi,12),
            'actual_fixed_group_code_limit':display.decimal_enclosure(low,high,12)}


def growing_limit():
    (_, _),(hlo,hhi) = design.entropies(1,256)
    low = F(5,16)-F(2-F(5,8),16)/(hlo-F(5,8))
    high = F(5,16)-F(2-F(5,8),16)/(hhi-F(5,8))
    return {'group_schedule':'g(n)=max(1,floor(bit_length(n)/4)); k=n*g(n)',
            'margin_multiplier':'4*g(n), with sqrt(n*ceil(log2(n+1))) rounded upward',
            'constant_completion_entropy_per_block_limit':'5/8',
            'actual_growing_group_code_limit':display.decimal_enclosure(low,high,12),
            'risk_formula':'5/16 - (2-5/8)/(16*(h8-5/8)), h8=4-(10/16)*log2(5)',
            'published_input':'Cardinal/Fiorini/Joret Theorem 1 and its rational weighted extension; generic minimum-entropy greedy cover is established.',
            'entropy_proof':'Forced signs are recoverable from completion and erasure mask, giving H(Y)>=5*g/8. A random priority has expected log first-compatible rank <=5*g/8; an explicit prefix code adds at most 2*log2(g+1)+1. Published greedy guarantee adds log2(e), hence H_G/g tends to 5/8.',
            'cap_and_concentration':'Outward entropy precision grows with n; mean self-information <=2*k-m eventually. Variance <=(13/4)*n*g*g and m=4*g*ceil(sqrt(n*bit_length(n))) make the length-event probability vanish. Only the charged grid parent and one-bit child survive.',
            'polynomial_design':'16**g<=2*n for the public schedule (including small g=1 only once n>=8); design uses O(4**g) incidences and O(g)-bit weights. Encoder/updater use polynomially many operations on O(k)-bit integers; data/program/runtime costs are separate.',
            'scope':'Analytic family limit with implemented variable-g primitives and declared finite diagnostics; no all-n source enumeration, efficient near-C67 guarantee, generic novelty or portable runtime.'}


def finite_rows():
    old = json.loads((HERE.parent/'results/entropy_coding_2026-10-02.json').read_text())
    control = F(2304567,8388608)
    rows = []
    for k in LENGTHS:
        n,g = k//8,8
        old_rows = [r for r in old['finite_bounds'] if r['k']==k]
        old_lower = min(F(r['base_error_lower_for_this_fixed_code']) for r in old_rows)
        old_upper = min(F(r['coded_error_upper_rounded_outward']) for r in old_rows)
        for multiplier in MULTIPLIERS:
            a = codec.default_count(n,g,multiplier)
            data = bounds.error_bound(n,g,a,DEGREES)
            upper = round_upper(data['error_upper'])
            rows.append({'k':k,'n':n,'g':g,'public_margin_multiplier':multiplier,'oracle_groups':a,
                         'parent_bits':2*k,'payload_grid_bits':2*k-1,'charged_flag_bits':1,'child_bits':1,
                         'base_error_lower':str(data['base']),'conservative_error_upper':str(upper),
                         'computed_upper_enclosure':display.decimal_enclosure(data['error_upper'],data['error_upper'],15),
                         'best_chernoff_degree':data['best_degree'],
                         'chernoff_tail_uppers':{str(d):str(round_upper(v)) for d,v in data['all_tail_bounds'].items()},
                         'raw_upper_numerator_sha256':digest_integer(data['error_upper'].numerator),
                         'raw_upper_denominator_sha256':digest_integer(data['error_upper'].denominator),
                         'proves_improvement_over_C69':upper<control,
                         'proves_loss_to_C69':data['base']>control,
                         'proves_improvement_over_both_C71_codes':upper<old_lower,
                         'proves_loss_to_named_better_C71_code':data['base']>old_upper,
                         'full_source_population_power_two':4*k,
                         'large_source_population_enumerated':False})
    best = [min((r for r in rows if r['k']==k),key=lambda r:(F(r['conservative_error_upper']),r['public_margin_multiplier'])) for k in LENGTHS]
    return rows,best


@cache
def large_diagnostics():
    specs = [(k//8,8,4,'fixed-eight') for k in (1536,12288)]
    specs += [(n,design.growing_group(n),4*design.growing_group(n),'growing') for n in (16,256,4096)]
    rows = []
    for n,g,multiplier,label in specs:
        a = codec.default_count(n,g,multiplier)
        k = n*g
        last_word = design.prepare(g)[0][-1]
        for family in range(3):
            if family==0:
                blocks = (0,)*k
            elif family==1:
                blocks = tuple((11*r+5)%16 for r in range(k))
            else:
                blocks = tuple(3 if r<a*g else 15 if (last_word >> (r%g))&1 else 0 for r in range(k))
            parent,diag = codec.encode(blocks,g,a,diagnostics=True)
            positions = sorted(r for r in {0,a*g-1,a*g,k//4,k//2,k-1} if 0<=r<k)
            queries = 0
            for r in positions:
                if not diag['regular']:
                    word = 0
                elif r<a*g:
                    word = sum((sum((blocks[r] >> j)&1 for j in range(4) if j!=o)>1) << o for o in range(4))
                else:
                    group = r//g
                    binary = codec.completion(blocks[group*g:(group+1)*g],g)
                    word = 15 if (binary >> (r%g))&1 else 0
                for o in range(4):
                    z = codec.update(parent,r,o,n,g,a)
                    if z!=(word >> o)&1:
                        raise ValueError('Large diagnostic actor changes a response')
                    for j in range(4):
                        if o!=j:
                            if codec.predict(z,r,o,j)!=z:
                                raise ValueError('Final child-only route changed')
                            queries += 1
            rows.append({'family':label,'n':n,'g':g,'a':a,'constructed_source':family,
                         'regular':diag['regular'],'parent_bit_length':parent.bit_length(),
                         'parent_sha256':digest_integer(parent),'public_query_positions':positions,
                         'physical_final_queries':queries})
    return rows


def discovery_check():
    folder = HERE/'discovery'
    meta = json.loads((folder/'metadata.json').read_text())
    for name,digest in meta['file_sha256'].items():
        if sha256((folder/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Discovery artifact changed')
    raw = gzip.decompress((folder/'pair_probe.json.gz').read_bytes())
    if sha256(raw).hexdigest()!=meta['raw_pair_probe_sha256']:
        raise ValueError('Compressed pair record changes its original JSON bytes')
    pair = json.loads(raw)
    pair_words = tuple((a,b) for b in (0,3,5,6,9,10,12,15) for a in (0,3,5,6,9,10,12,15))
    costs = [[direct_loss(x&15,a)+direct_loss(x>>4,b) for a,b in pair_words] for x in range(256)]
    for row in pair['runs']:
        mapping = row['mapping']
        counts = Counter(mapping)
        errors = sum(costs[x][w] for x,w in enumerate(mapping))
        if {str(w):c for w,c in counts.items()}!=row['counts'] or F(row['branch_loss_mean'])!=F(errors,256):
            raise ValueError('An inspected pair map fails independent literal cost/count grading')
    for row in json.loads((folder/'greedy_probe.json').read_text()):
        words,counts = design.prepare(row['group'])
        if tuple(row['priority'])!=words or tuple(row['counts_in_priority_order'])!=counts:
            raise ValueError('Greedy direction probe changed its exact type counts')
    for row in json.loads((folder/'bound_probe.json').read_text()):
        n,g,multiplier = row['n'],row['group'],row['margin_multiplier']
        a = codec.default_count(n,g,multiplier)
        data = bounds.error_bound(n,g,a,DEGREES)
        if (a!=row['oracle_groups'] or any(str(float(data[k]))!=row[name]
                for k,name in (('base','base'),('tail_upper','tail_bound'),('error_upper','risk_upper')))):
            raise ValueError('Exact finite calculations do not reproduce inspected displays')
    upstream = meta['upstream']
    old = ROOT/upstream['path']
    if sha256(old.read_bytes()).hexdigest()!=upstream['sha256']:
        raise ValueError('Original C71 result changed')
    for path,digest in json.loads(old.read_text())['source_sha256'].items():
        if sha256((ROOT/path).read_bytes()).hexdigest()!=digest:
            raise ValueError('Original C71/C67/C69 bindings changed')
    return {'pair_maps_independently_graded':len(pair['runs']),
            'distinct_inspected_pair_maps':len({tuple(r['mapping']) for r in pair['runs']}),
            'greedy_group_sizes':6,'public_finite_margin_designs':40,'chernoff_exponents_per_design':5,
            'floating_displays_used_in_numeric_proof':False,'first_failed_search_has_no_saved_original_console_file':True}


def certificate():
    discovery = discovery_check()
    groups = [group_check(g) for g in GROUPS]
    table_path = HERE/'tables.json'
    if json.loads(table_path.read_text())!={'groups':groups,'chosen_fixed_group':8}:
        raise ValueError('Public cover tables or independent greedy choices changed')
    literal = literal_quantizers()
    small = small_populations()
    finite,best = finite_rows()
    large = large_diagnostics()
    files = [HERE/name for name in ('design.py','codec.py','bounds.py','certificate.py','test_tie.py','tables.json')]
    files += sorted(p for p in (HERE/'discovery').iterdir() if p.suffix in ('.py','.json','.gz'))
    files += [HERE.parent/'results/entropy_coding_2026-10-02.json',
              HERE.parent/'entropy_coding/codec.py',HERE.parent/'joint_coding/decoder_frontier.py']
    return {'version':'coordinated_tie_code_v1','date':'2026-10-02',
            'new_model_calls':0,'new_natural_episodes':0,'source_sha256':{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in files},
            'information_contract':{'source':'uniform iid four-bit blocks','R_O_J':'independent uniform block/omission/remaining coordinate',
                'parent_bits':'2*k including one fallback flag','child_bits':1,'parent_before_R_O':True,'child_before_J':True,
                'updater_inputs':['M','R','O','public n/g/a/cover and oracle tables'],
                'final_inputs':['Z','R','O','J'],'public_design_and_margin_before_X':True,
                'archives_source_parent_sessions_environment_diagnostics_after_boundary':False,
                'temporary_workspace':'Allowed within each stage and discarded; actors are trusted pure functions, not isolated untrusted processes.'},
            'weighted_cover_checks':groups,'literal_quantizer_populations':literal,
            'literal_quantizer_physical_final_queries':sum(r['physical_final_queries'] for r in literal),
            'pair_optimum_scope':'Among compatible source-wise nearest constant-pair choices: mandatory masses >=25 each and maximum <=121 imply domination by [121,85,25,25]/256. Greedy attains that vector. Not a global quantizer or rate-distortion optimum.',
            'fixed_group_limits':[fixed_limit(g) for g in GROUPS],
            'growing_family':growing_limit(),'finite_bounds':finite,'best_checked_bound_by_length':best,
            'large_source_populations_enumerated':False,'finite_bounds_are_exactly_rounded_conservative_not_actual_risks':True,
            'small_full_arithmetic_populations':small,
            'small_arithmetic_physical_final_queries':sum(r['physical_final_queries'] for r in small),
            'large_constructed_diagnostics':large,
            'large_diagnostic_physical_final_queries':sum(r['physical_final_queries'] for r in large),
            'fixed_eight_packed_public_payload_bytes':len(design.pack_tables(8))+8,
            'public_storage_scope':'Eight-block cover priority/counts 1280 bytes plus eight oracle response/count bytes. Public n/g/a, program/runtime/framing and growing-family tables are separate; value bits do not imply token/cost or RAM savings.',
            'root_precision_bits':64,'chernoff_degrees':list(DEGREES),'charged_parent_flag_bits':1,
            'discovery':discovery,
            'limits':'Specific uniform source/query law. Published weighted greedy-cover approximation and generic quantization/time sharing/arithmetic intervals are established. Pair entropy optimum is restricted; eight-group greedy code is not optimal. Large finite risk bounds use root-enclosed Chernoff moments, not exact risk/failure averages or complete physical source grading. Selected smaller designs lose; forty margin designs are inspected, not an exhaustive allocation search or independent trials. Growing-family proof has declared code complexity and finite diagnostic scope, not a near-C67 or portable-runtime guarantee. External correctness/priority and natural-agent/model/token/credit/production benefit remain open; original results and provider allocations unchanged.'}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'fixed_eight':result['fixed_group_limits'][-1]['actual_fixed_group_code_limit'],
                      'growing':result['growing_family']['actual_growing_group_code_limit'],
                      'finite_12288':{k:result['best_checked_bound_by_length'][-1][k] for k in ('oracle_groups','public_margin_multiplier','conservative_error_upper')},
                      'small_queries':result['small_arithmetic_physical_final_queries'],
                      'literal_queries':result['literal_quantizer_physical_final_queries'],
                      'diagnostic_queries':result['large_diagnostic_physical_final_queries'],
                      'bindings':len(result['source_sha256'])}))


if __name__=='__main__':
    main()
