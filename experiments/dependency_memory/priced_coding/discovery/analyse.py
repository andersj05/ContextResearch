from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import json
from hashlib import sha256
from experiments.dependency_memory.priced_coding import design,bounds
from experiments.dependency_memory.weighted_overflow import certificate as old
from experiments.dependency_memory.tie_coding import design as old_design
from experiments.dependency_memory.joint_coding import decoder_frontier as display

LOSS=tuple(tuple(sum(((x>>j)&1)!=((w>>o)&1) for o in range(4) for j in range(4) if j!=o)
                 for w in range(16)) for x in range(16))

def analyse(path):
    original=Path(path).read_bytes()
    raw=json.loads(original)
    g,population=raw['g'],raw['population']
    results=[]
    h8=old_design.entropies(1,192)[1]
    control=F(270646703203513,10**15)
    for row_index,row in enumerate(raw['runs']):
        book=design.Book(g,tuple(row['price']),tuple(row['words']),
                         tuple(row['proposal_counts']),tuple(row['counts']))
        observed=Counter()
        loss_sums=[0]*len(book.words)
        errors=0
        fallback=book.words[book.fallback]
        if row['fallback_index']!=book.fallback or len(row['mapping'])!=population:
            raise ValueError('Malformed complete native price map')
        for x,index in enumerate(row['mapping']):
            word=book.words[index]
            cost=sum(LOSS[(x>>(4*r))&15][(word>>(4*r))&15] for r in range(g))
            fallback_cost=sum(LOSS[(x>>(4*r))&15][(fallback>>(4*r))&15] for r in range(g))
            if cost>fallback_cost:
                raise ValueError('A price output increases fallback group loss')
            errors+=cost
            observed[index]+=1
            loss_sums[index]+=fallback_cost-cost
        if (errors!=row['exact_loss_sum'] or tuple(observed[i] for i in range(len(book.words)))!=book.counts
                or row['exact_price_comparisons']!=population*len(book.words)):
            raise ValueError('Native exact map does not match literal source grading')
        error=F(errors,12*g*population)
        entropy=design.entropies(book)
        rate=tuple(h/g for h in entropy)
        if rate[1]<2:
            share_lower=(2-rate[1])/(h8[1]-rate[1])
            share_upper=(2-rate[0])/(h8[0]-rate[0])
            limit=(error+(F(1,4)-error)*share_upper,error+(F(1,4)-error)*share_lower)
        else:
            limit=None
        n,r=divmod(12288,g)
        plans=[]
        for degree in bounds.DEGREES:
            plan=bounds.allocation(n,book,tuple(loss_sums),error,degree)
            upper=F(n*g,12288)*plan['error_upper']+F(r,12288)*F(9,32)
            plans.append({'a':plan['a'],'degree':degree,'error_upper':str(old.rounded(upper)),
                          'display':display.decimal_enclosure(upper,upper,12),
                          'convex':plan['convex'],'method':plan['method'],
                          'evaluations':plan['evaluations']})
        chosen=min(plans,key=lambda p:(F(p['error_upper']),p['a'],p['degree']))
        summary={'row':row_index,'g':g,'seed':row['seed'],'price':row['price'],
                 'book_words':len(book.words),'exact_quantizer_error':str(error),
                 'entropy_per_block':display.decimal_enclosure(*rate,12),
                 'oracle_interpolation':None if limit is None else display.decimal_enclosure(*limit,12),
                 'packed_public_data_bytes':len(design.pack_tables(book))+10,
                 'native_float_changes':row['changed_float_assignments'],
                 'fallback_word':fallback,'loss_sums':loss_sums,'best_12288':chosen,'plans_12288':plans,
                 'proves_better_finite_certificate_than_C74':F(chosen['error_upper'])<control}
        results.append(summary)
        print({k:v for k,v in summary.items() if k not in ('loss_sums','plans_12288')},flush=True)
    output={'source':str(path),'original_sha256':sha256(original).hexdigest(),
            'g':g,'source_population_per_start':population,'rows':results}
    Path(path).with_name(Path(path).stem+'_analysis.json').write_text(json.dumps(output,indent=2)+'\n')
    return output

if __name__=='__main__':
    import sys
    for path in sys.argv[1:]:
        analyse(path)
