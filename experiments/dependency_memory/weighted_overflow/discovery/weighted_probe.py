from collections import defaultdict
from fractions import Fraction as F
from functools import cache
from itertools import product
import json
from experiments.dependency_memory.tie_coding import design,codec,bounds

@cache
def low_weights(g):
    words,counts=design.prepare(g)
    delta=defaultdict(int)
    for status in product(range(3),repeat=g):
        forced=sum((s!=2)<<r for r,s in enumerate(status))
        values=sum((s==1)<<r for r,s in enumerate(status))
        weight=5**forced.bit_count()*6**(g-forced.bit_count())
        w=next(w for w in words if w&forced==values)
        value=F(36,5)*values.bit_count()*weight
        assert value.denominator==1
        delta[w]+=int(value)
    return tuple(delta[w] for w in words)

@cache
def weighted_moments(g,s):
    words,counts=design.prepare(g)
    n=16**g
    m=bounds.moment_upper(counts,n,s)
    w=sum(F(delta,12*g*n)*bounds.root_bounds(n,s)[1]/bounds.root_bounds(c,s)[0]
          for c,delta in zip(counts,low_weights(g)))
    high_m=bounds.moment_upper((5,1,1,1,1,1,1,5),16,s)
    high_w=F(3,16)*bounds.root_bounds(16,s)[1]/bounds.root_bounds(5,s)[0]+F(1,16)*bounds.root_bounds(16,s)[1]
    return m,w,high_m,high_w

def upper(n,g,a,s):
    ml,wl,mh,wh=weighted_moments(g,s)
    q,r=divmod(2*n*g-1,s)
    threshold=(1<<q)*bounds.root_bounds(1<<r,s)[0]
    total=F(0)
    if a:
        total+=F(a,n)*wh*mh**(a*g-1)*ml**(n-a)
    if a<n:
        total+=F(n-a,n)*wl*ml**(n-a-1)*mh**(a*g)
    return total/threshold

def rounded(value):
    scale=10**15
    return str(F(-(-value.numerator*scale//value.denominator),scale))

data=[]
for k in (96,192,384,768,1536,3072,6144,12288):
    n=k//8
    rows=[]
    for c in (2,3,4,5,6):
        a=codec.default_count(n,8,c)
        base=F(5,16)-F(a,16*n)
        scores={s:min(F(1,2),base+upper(n,8,a,s)) for s in (8,16,32,64,128)}
        s=min(scores,key=scores.get)
        rows.append({'k':k,'n':n,'a':a,'c':c,'s':s,'base':str(base),'upper':rounded(scores[s]),
                     'upper_float':float(scores[s])})
    selected=min(rows,key=lambda row:row['upper_float'])
    data.extend(rows)
    print(selected,flush=True)
open('build/entropy-vector/weighted_probe.json','w').write(json.dumps(data,indent=2)+'\n')
