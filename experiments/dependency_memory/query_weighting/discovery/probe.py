"""Post-hoc floating witness discovery and exact finite query-weight probes."""
from collections import Counter
from fractions import Fraction as F
import json
from math import log2
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.dependency_memory.conditional_coding import certificate as finite, codec
from experiments.dependency_memory.joint_coding import decoder_frontier as frontier

parts=finite.partition(codec.BASE,codec.OVERRIDES)
columns,winners,minima,changed,groups,local=parts
unchanged=[b for b in range(64) if b not in changed]
right=Counter((min(row[b] for b in unchanged),row[52],row[58]) for row in columns)
baseline=40514*4096
outcomes=36*16**6
rows=[]
for p in (F(0),F(1,10),F(1,4),F(1,3),F(2,5),F(1,2),F(3,5),F(2,3),F(3,4),F(9,10),F(1)):
    total=p*baseline
    for (d52,d58), xs in groups.items():
        for (u,r52,r58),ny in right.items():
            total+=len(xs)*ny*min((1-p)*u,p*d52+(1-p)*r52,p*d58+(1-p)*r58)
    result={'p':str(p),'reencoded_six_error':str(total/outcomes),
            'fixed_balanced_pair_error':str(F(2304567,8388608)),
            'three_named_controls_error':str(min(F(40514,147456), F(1,4)+p/F(16), F(5,16)-p/F(16)))}
    rows.append(result)
    print(result,flush=True)

loss=frontier.loss_matrix(frontier.UNSIGNED)
def channel(t):
    # Oracle factors removed for stable floating computations.
    a=((1+t**12)/2,(1+t**6)/2,t*t)
    b=(t**6,(t*t+t**4)/2,(1+4*t*t+t**4)/6)
    weights=(1/8,1/2,3/8)
    def derivative(p):
        return sum(w*(v-u)/(u+(v-u)*p) for w,u,v in zip(weights,a,b))
    if derivative(0)<=0:
        mass=0.0
    else:
        lo,hi=0.,1.
        for _ in range(60):
            mid=(lo+hi)/2
            if derivative(mid)>0: lo=mid
            else: hi=mid
        mass=(lo+hi)/2
    q=[(1-mass)/2 if c in (0,15) else mass/6 if c.bit_count()==2 else 0. for c in range(16)]
    information,error=0.,0.
    for costs in loss:
        offset=min(costs)
        kernels=[t**(v-offset) for v in costs]
        z=sum(w*v for w,v in zip(q,kernels))
        excess=sum(w*v*(c-offset) for w,v,c in zip(q,kernels,costs))/z
        information+=(-log2(z)+log2(t)*excess)/16
        error+=(excess+offset)/192
    return information,error,mass

witnesses=[]
for m,n in ((1,9),(1,3),(1,2),(2,3),(1,1)):
    lo,hi=.00001,.299
    for _ in range(60):
        q=(lo+hi)/2
        r1,d1,b1=channel(q**m)
        r2,d2,b2=channel(q**n)
        if r1+r2>4: lo=q
        else: hi=q
    q=(lo+hi)/2
    r1,d1,b1=channel(q**m)
    r2,d2,b2=channel(q**n)
    row={'p':str(F(m,m+n)), 'm':m,'n':n,'q':q,'left_rate':r1,'right_rate':r2,
         'left_error':d1,'right_error':d2,'weighted_error':(m*d1+n*d2)/(m+n)}
    witnesses.append(row)
    print(row,flush=True)
Path(__file__).with_name('probe.json').write_text(json.dumps({'evidence_class':'post-hoc probes; floats are not proof',
    'finite_rows':rows, 'float_witnesses':witnesses, 'right_cost_histogram_types':len(right)},indent=2)+'\n',encoding='utf-8')
