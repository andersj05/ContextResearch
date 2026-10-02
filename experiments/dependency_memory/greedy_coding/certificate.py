"""Independent routed losses, every greedy choice and exact small actors."""
from collections import Counter
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path

from . import design,codec,bounds
from experiments.dependency_memory.joint_coding import decoder_frontier as old

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE.parent/'results/greedy_coding_2026-10-02.json'
GROUPS = (1,2,3)
INVERSES = (16,32,64,128,256,512,1024,2048,4096)
LARGE_GROUPS = (10**4,10**6,10**8,10**10,10**12,10**14)


def direct_loss(x,a):
    return sum(((x >> j)&1)!=((a >> o)&1)
               for o in range(4) for j in range(4) if o!=j)


@cache
def direct_matrix(g):
    scalar = tuple(tuple(direct_loss(x,a) for x in range(16)) for a in range(16))
    rows = []
    for word in range(16**g):
        values = [0]
        for r in range(g):
            column = scalar[(word >> (4*r))&15]
            values = [previous+column[x] for x in range(16) for previous in values]
        rows.append(bytes(values))
    return tuple(rows)


@cache
def reference_layers(g):
    # Independent source-distance rows, rather than production's mask tensor.
    result = {}
    for word,row in enumerate(direct_matrix(g)):
        values = [0]*(12*g+1)
        for x,cost in enumerate(row):
            values[cost] |= 1 << x
        result[word] = tuple(values)
    return result


@cache
def direct_book_loss(g,book):
    rows = direct_matrix(g)
    minima = [12*g+1]*(16**g)
    for word in book:
        for source,cost in enumerate(rows[word]):
            if cost < minima[source]:
                minima[source] = cost
    return sum(minima)


def check_choices(g,rows,words):
    histogram = reference_layers(g)
    full = (1 << (16**g))-1
    choices = 0
    for row in rows:
        threshold = row['threshold']
        covers = {w:sum(histogram[w][:threshold+1]) for w in words}
        remaining = full ^ covers[0]
        if not row['book'] or row['book'][0]!=0:
            raise ValueError('Missing charged zero-response message')
        for chosen,gain in zip(row['book'][1:],row['gains']):
            candidates = [(int((mask&remaining).bit_count()),-w,w)
                          for w,mask in covers.items()]
            maximum,_,expected = max(candidates)
            if chosen!=expected or gain!=maximum or gain<=0:
                raise ValueError('Complete routed greedy choice/tie differs')
            remaining &= ~covers[chosen]
            choices += 1
        if len(row['book'])!=len(row['gains'])+1 or len(row['book'])>4**g:
            raise ValueError('Invalid capacity or greedy trace')
        if (len(row['book'])<4**g and
                any(mask&remaining for mask in covers.values())):
            raise ValueError('Early greedy stop still has a positive gain')
        if row['uncovered']!=remaining.bit_count():
            raise ValueError('Uncovered population changed')
        if row['errors']!=direct_book_loss(g,tuple(row['book'])):
            raise ValueError('Nearest population grading differs from routed losses')
    return choices


@cache
def design_checks():
    result = []
    for g in GROUPS:
        row = design.analyse(g)
        reference = reference_layers(g)
        if reference!=design.loss_layers(g):
            raise ValueError('Tensor layers differ from independent routed matrix')
        choices = check_choices(g,row['thresholds'],tuple(range(16**g)))
        best = min(row['thresholds'],key=lambda r:(r['errors'],r['threshold']))
        baseline_loss = direct_book_loss(g,tuple(sum(a << (4*r) for r,a in enumerate(word))
                                                for word in product(design.BASE,repeat=g)))
        if (baseline_loss!=12*g*16**g*F(9,32)
                or row['errors']!=min(best['errors'],baseline_loss)
                or row['threshold_only_best']!=best['threshold']
                or row['threshold_only_errors']!=best['errors']):
            raise ValueError('Public finite risk selection changed')
        result.append({'group':g,'candidate_words':16**g,'source_words':16**g,
                       'thresholds':len(row['thresholds']),'greedy_choices':choices,
                       'all_source_candidate_distances_checked':256**g,
                       'threshold_only_error':str(F(best['errors'],12*g*16**g)),
                       'selected_error':str(F(row['errors'],12*g*16**g)),
                       'selected_kind':row['selected_kind'],
                       'selected_threshold':row['selected_threshold'],
                       'public_word_count':len(row['book']),
                       'packed_public_word_bytes':len(design.pack_book(g))})
    return result


@cache
def baseline_check():
    candidates = [(direct_book_loss(1,book),book)
                  for book in combinations(range(16),4)]
    best_loss,best_book = min(candidates)
    if best_loss!=54 or best_book!=design.BASE:
        raise ValueError('Fixed unsigned one-block control changed')
    return {'distinct_four_word_books':len(candidates),'best_book':list(best_book),
            'best_errors':best_loss,'outcomes':192,'exact_error':'9/32',
            'scope':'All four-distinct-word books with the fixed unsigned final decoder; C19 already has the stronger unrestricted optimum.'}


@cache
def small_populations():
    records = []
    for k,g in ((1,1),(2,1),(3,1),(2,2),(3,2),(3,3)):
        errors = queries = 0
        messages = Counter()
        table = tuple(design.book(g))
        matrix = direct_matrix(g)
        for source in range(16**k):
            blocks = tuple((source >> (4*r))&15 for r in range(k))
            parent = codec.encode(blocks,g)
            if not 0 <= parent < (1 << (2*k)):
                raise ValueError('Charged parent exceeds its state count')
            messages[parent] += 1
            groups,tail = divmod(k,g)
            for group in range(groups):
                packed = sum(x << (4*r) for r,x in enumerate(blocks[group*g:(group+1)*g]))
                expected = min(range(len(table)),key=lambda m:matrix[table[m]][packed])
                if (parent >> (2*g*group))&((1 << (2*g))-1)!=expected:
                    raise ValueError('Actor nearest assignment or integer tie differs')
            for r,x in enumerate(blocks):
                if r<groups*g:
                    group,coordinate = divmod(r,g)
                    message = (parent >> (2*g*group))&((1 << (2*g))-1)
                    word = (table[message] >> (4*coordinate))&15
                else:
                    expected = min(range(4),key=lambda m:direct_loss(x,design.BASE[m]))
                    word = design.BASE[expected]
                if codec.decode_response(parent,r,k,g)!=word:
                    raise ValueError('Group/tail response changed')
                for o in range(4):
                    child = codec.update(parent,r,o,k,g)
                    if child not in (0,1) or child!=((word >> o)&1):
                        raise ValueError('Child state or timing changed')
                    for j in range(4):
                        if o!=j:
                            errors += codec.predict(child,r,o,j)!=((x >> j)&1)
                            queries += 1
        group_risk = F(design.analyse(g)['errors'],12*g*16**g)
        expected_risk = bounds.tiled_error(k,g,group_risk)
        if F(errors,queries)!=expected_risk:
            raise ValueError('Complete actor population disagrees with tiled formula')
        records.append({'k':k,'group':g,'sources':16**k,'parent_states_used':len(messages),
                        'errors':errors,'physical_final_queries':queries,
                        'exact_error':str(F(errors,queries))})
    return records


@cache
def large_diagnostics():
    records = []
    for k,g in ((5,2),(6,2),(7,3),(8,3),(11,3)):
        families = [tuple(value for _ in range(k)) for value in (0,1,3,15)]
        families += [tuple((r*factor+offset)&15 for r in range(k))
                     for factor,offset in ((1,0),(3,1),(5,2),(7,15))]
        for index,blocks in enumerate(families):
            parent = codec.encode(blocks,g)
            errors = queries = 0
            for r,x in enumerate(blocks):
                word = codec.decode_response(parent,r,k,g)
                for o in range(4):
                    child = codec.update(parent,r,o,k,g)
                    for j in range(4):
                        if o!=j:
                            errors += codec.predict(child,r,o,j)!=((x >> j)&1)
                            queries += 1
                if not 0 <= word < 16:
                    raise ValueError('Invalid reconstructed response')
            records.append({'k':k,'group':g,'constructed_family':index,
                            'parent_bit_length':parent.bit_length(),'parent_cap_bits':2*k,
                            'errors':errors,'physical_final_queries':queries})
    return records


@cache
def cover_recurrence_check():
    comparisons = 0
    for system in product(range(8),repeat=4):
        remaining = 7
        residuals = [3]
        for _ in range(4):
            chosen = max(range(4),key=lambda w:((system[w]&remaining).bit_count(),-w))
            remaining &= ~system[chosen]
            residuals.append(remaining.bit_count())
        for size in range(1,5):
            for competitor in combinations(range(4),size):
                covered = 0
                for word in competitor:
                    covered |= system[word]
                residual = 3-covered.bit_count()
                for steps,observed in enumerate(residuals):
                    if observed > residual+3*F(size-1,size)**steps:
                        raise ValueError('Partial-cover recurrence primitive fails')
                    comparisons += 1
    return {'set_systems':8**4,'source_elements':3,'candidate_sets':4,
            'competitor_and_step_comparisons':comparisons,
            'scope':'Complete tiny set-system calibration; the general recurrence is proved in the note.'}


@cache
def channel_check():
    loss = old.loss_matrix(old.UNSIGNED)
    if any(loss[x][a]!=direct_loss(x,a) for x in range(16) for a in range(16)):
        raise ValueError('Original unsigned loss matrix changed')
    primal = old.primal_bounds(loss,old.UNSIGNED_WEIGHTS)
    if not primal['information_upper']<2 or not primal['distortion']<bounds.CHANNEL_ERROR_UPPER:
        raise ValueError('Original rational slack channel no longer meets its bounds')
    q = tuple(F(w,sum(old.UNSIGNED_WEIGHTS)) for w in old.UNSIGNED_WEIGHTS)
    active = tuple(a for a in range(16) if q[a])
    if active!=(0,3,5,6,9,10,12,15) or min(q[a] for a in active)<=F(1,32):
        raise ValueError('Reference-mass bound for information range changed')
    channel = []
    for x in range(16):
        normalizer = sum(q[a]*old.T**loss[x][a] for a in active)
        channel.append(tuple(q[a]*old.T**loss[x][a]/normalizer for a in active))
    for h in INVERSES:
        cost = F(0)
        for x,row in enumerate(channel):
            mixed = tuple((1-F(1,h))*p+q[a]/h for p,a in zip(row,active))
            if sum(mixed)!=1:
                raise ValueError('Rational mixture is not a channel')
            for p,a in zip(mixed,active):
                if not F(1,h)<=p/q[a]<32:
                    raise ValueError('Mixture information density leaves its proved range')
                cost += p*direct_loss(x,a)
        exact = (1-F(1,h))*primal['distortion']+F(1,2*h)
        if cost/192!=exact or exact>bounds.proximity(1,h)['mixed_error_upper']:
            raise ValueError('Independent mixture loss disagrees')
    return {'mixture_inverses':list(INVERSES),'conditional_entries_per_mixture':128,
            'reference_support_words':list(active),'cross_information_upper_below_two':True,
            'original_channel_distortion_upper':str(bounds.CHANNEL_ERROR_UPPER),
            'density_range':'[-log2(h),5]','physical_large_code_execution':False}


def proximity_rows():
    records,best = [],[]
    for g in LARGE_GROUPS:
        group = []
        for h in INVERSES:
            values = bounds.proximity(g,h)
            row = {'group':g,'mixture_inverse':h,
                   **{name:str(value) if isinstance(value,F) else value for name,value in values.items()},
                   'upper_decimal':old.decimal_enclosure(values['upper'],values['upper'],12)[1],
                   'first_default_k_power_of_two':10*g-1,
                   'large_codebook_built_or_population_executed':False}
            records.append(row)
            group.append(row)
        best.append(min(group,key=lambda r:(F(r['upper']),r['mixture_inverse'])))
    return records,best


def discovery_check():
    folder = HERE/'discovery'
    meta = json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    for name,digest in meta['sha256'].items():
        if sha256((folder/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Original discovery bytes changed')
    records = choices = 0
    for stem,alphabet in (('eight',tuple((0,3,5,6,9,10,12,15))),('all',tuple(range(16)))):
        data = json.loads((folder/f'{stem}_probe.json').read_text())
        for row in data:
            g = row['group']
            words = tuple(sum(a << (4*r) for r,a in enumerate(word))
                          for word in product(alphabet,repeat=g))
            choices += check_choices(g,row['rows'],words)
            for entry in row['rows']:
                if F(entry['error'])!=F(entry['errors'],12*g*16**g):
                    raise ValueError('Discovery exact error string changed')
            best = min(row['rows'],key=lambda r:(r['errors'],r['threshold']))
            if row['best']!=best:
                raise ValueError('Discovery selected public threshold changed')
            if stem=='all':
                current = design.analyse(g)
                stripped = [{k:v for k,v in entry.items() if k!='error'} for entry in row['rows']]
                if stripped!=current['thresholds']:
                    raise ValueError('Final all-word construction differs from preserved probe')
            records += len(row['rows'])
    for entry in meta['upstream']:
        path = ROOT/entry['path']
        if sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('Original upstream result changed')
        for name,digest in json.loads(path.read_text(encoding='utf-8'))['source_sha256'].items():
            if sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
                raise ValueError('Original upstream source chain changed')
    return {'inspected_threshold_designs':records,'greedy_choices_rechecked':choices,
            'new_model_calls':0,'new_natural_episodes':0,'discovery_is_post_hoc':True}


def certificate():
    discovery = discovery_check()
    checks = design_checks()
    tables = {'groups':[design.analyse(g) for g in GROUPS],
              'default_group':'max(1,bit_length(k)//10)','scalar_tail_book':list(design.BASE)}
    if json.loads((HERE/'tables.json').read_text())!=tables:
        raise ValueError('Frozen finite public designs changed')
    baseline = baseline_check()
    small = small_populations()
    diagnostics = large_diagnostics()
    primitive = cover_recurrence_check()
    channel = channel_check()
    proximity,best = proximity_rows()
    c72 = json.loads((HERE.parent/'results/tie_coding_2026-10-02.json').read_text())
    controls = {'one_block':'9/32','refined_three_block':'40514/147456',
                'conditional_six_block':'2304567/8388608',
                'C72_growing_limit':c72['growing_family']['actual_growing_group_code_limit']}
    if not F(checks[-1]['selected_error'])>F(controls['refined_three_block'])>F(controls['conditional_six_block']):
        raise ValueError('Required negative finite controls changed')
    files = [HERE/name for name in ('design.py','codec.py','bounds.py','certificate.py','test_greedy.py','tables.json')]
    files += sorted(p for p in (HERE/'discovery').iterdir() if p.suffix in ('.py','.json'))
    files += [HERE.parent/'results/tie_coding_2026-10-02.json',
              HERE.parent/'results/rate_curve_2026-10-02.json',
              HERE.parent/'results/decoder_frontier_certificate.json',
              HERE.parent/'entropy_coding/codec.py',HERE.parent/'joint_coding/decoder_frontier.py']
    return {'version':'deterministic_distortion_cover_v1','date':'2026-10-02',
            'new_model_calls':0,'new_natural_episodes':0,
            'source_sha256':{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in files},
            'information_contract':{'source':'uniform iid four-bit blocks','R_O_J':'independent uniform block/omission/remaining coordinate',
                'parent_bits':'exactly 2*k, including every group and scalar-tail label',
                'child_bits':1,'parent_before_R_O':True,'child_before_J':True,
                'updater_inputs':['M','R','O','public k/g/book'],'final_inputs':['Z','R','O','J'],
                'all_designs_before_X':True,'instance_schedule_histogram_selector_or_flag':False,
                'source_parent_scratch_archive_environment_provider_rereads_after_boundary':False,
                'temporary_workspace':'Allowed within each stage and discarded; trusted functions, not untrusted-process isolation.'},
            'finite_design_checks':checks,'baseline_check':baseline,'discovery':discovery,
            'small_populations':small,'small_source_populations':sum(r['sources'] for r in small),
            'small_physical_final_queries':sum(r['physical_final_queries'] for r in small),
            'constructed_diagnostics':diagnostics,
            'constructed_diagnostic_queries':sum(r['physical_final_queries'] for r in diagnostics),
            'cover_recurrence_calibration':primitive,'rational_channel_check':channel,
            'analytic_proximity_bounds':proximity,'best_checked_proximity_bound':best,
            'retained_controls':controls,
            'family':{'public_g':'max(1,bit_length(k)//10)','exact_risk_formula':'((k-k%g)*E_g+(k%g)*9/32)/k',
                      'proved_actual_limit':'C67 D_infinity(2)','old_limit_enclosure':['0.2618989799','0.2618989801'],
                      'public_design_bit_complexity_upper':'poly(g)*1024**g = O(k*poly(log k)) for g>=2',
                      'public_design_workspace_bits_upper':'poly(g)*256**g',
                      'actor_bit_complexity':'Polynomial in k, including exact parent packing/extraction; no linear or portable speed claim.',
                      'public_onsets':[{'g':g,'first_default_k_power_of_two':10*g-1} for g in (2,3,4,10)]},
            'large_codebooks_built':False,'large_source_populations_enumerated':False,
            'limitations':'Greedy coverage, logarithmic blocking, source coding and concentration are established. This is a local deterministic constructive application of C67, not a new generic algorithm or practical near-optimal result. Small greedy codes lose to stronger finite controls; the scalar product baseline wins at g<=2. Large proximity bounds are conservative analytic statements with enormous default input onsets, not executed populations, observed speed or exact risks. External correctness/priority, sharper useful codes, broader laws and natural-agent/model/token/cost benefit remain open.'}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'finite':result['finite_design_checks'],
                      'best_proximity':[{k:r[k] for k in ('group','mixture_inverse','upper_decimal')} for r in result['best_checked_proximity_bound']],
                      'small_queries':result['small_physical_final_queries'],
                      'diagnostic_queries':result['constructed_diagnostic_queries'],
                      'bindings':len(result['source_sha256'])}))


if __name__=='__main__':
    main()
