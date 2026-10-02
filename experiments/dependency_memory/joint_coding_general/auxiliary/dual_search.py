"""Numerical witness selection, followed by inherited exact dual verification."""
from collections import defaultdict
from fractions import Fraction
import json
import math
from pathlib import Path
import numpy as np
from experiments.dependency_memory.joint_coding import decoder_frontier as f

refined=json.loads(Path('build/general_decoder_cover_refine.json').read_text())['cases']
tables={i:f.decode_table(i) for row in refined for i in row['indices']}
base_cache={}
slo,shi=tuple(-v for v in reversed(f.log2_bounds(f.T.numerator,f.T.denominator)))
for i,table in tables.items():
    loss=f.loss_matrix(table);w=f.UNSIGNED_WEIGHTS if table==f.UNSIGNED else f.nearest_weights(loss)
    n,d=f.dual_product(loss,w);lo,hi=f.log2_bounds(n,d);base_cache[i]=-hi/16
hard=[]
for row in refined:
    v=4096*(sum(base_cache[i] for i in row['indices'])-6)/shi
    low=-(-v.numerator//v.denominator)
    if max(low,row['lower'])<40072:hard.append(row)

cache={};records=[]
for row in hard:
    best=None
    for num in (30,40,50,60,70,80,90,100,110,116,120,130,140,160,180,200,240):
        t=Fraction(num,1000);s_hi=-f.log2_bounds(t.numerator,t.denominator)[0]
        constants=[];weights=[]
        for i in row['indices']:
            key=(i,t)
            if key not in cache:
                loss=f.loss_matrix(tables[i]);kernel=np.power(float(t),np.array(loss,dtype=float));q=np.ones(16)/16
                iterations=0
                for step in range(20000):
                    z=kernel@q;gradient=(kernel/z[:,None]).mean(axis=0);next_q=q*gradient;next_q/=next_q.sum()
                    iterations=step+1
                    if np.max(np.abs(next_q-q))<1e-13:
                        q=next_q;break
                    q=next_q
                rational=tuple(int(round(p*10**12)) for p in q)
                n,d=f.dual_product(loss,rational,t);lo,hi=f.log2_bounds(n,d)
                cache[key]=(-hi/16,rational,iterations)
            constant,w,iters=cache[key];constants.append(constant);weights.append(list(w))
        exact=4096*(sum(constants)-6)/s_hi
        lower=-(-exact.numerator//exact.denominator)
        candidate={'indices':row['indices'],'defects':row['defects'],'t':[t.numerator,t.denominator],
                   'weights':weights,'dual_lower_errors':lower,'cover_lower_errors':row['lower'],
                   'combined_lower':max(lower,row['lower'])}
        if best is None or lower>best['dual_lower_errors']:best=candidate
    records.append(best)
    print('case',len(records),'/',len(hard),'exact_dual',best['dual_lower_errors'],'combined',best['combined_lower'],flush=True)
out={'version':'general_dual_witness_exploration','numpy_version':np.__version__,'new_model_calls':0,
     'limits':'Numerical multiplicative iteration selects arbitrary rational q; only outward exact dual checks certify bounds. No optimizer or finite-code optimum claim.',
     'records':records,'weights_scale':10**12,'max_iterations':20000,'t_grid_numerators':[30,40,50,60,70,80,90,100,110,116,120,130,140,160,180,200,240]}
Path('build/general_decoder_dual_search.json').write_text(json.dumps(out,sort_keys=True),encoding='utf-8')
print('SUMMARY',{'cases':len(records),'minimum':min(row['combined_lower'] for row in records),'still_below_40072':sum(row['combined_lower']<40072 for row in records)},flush=True)
