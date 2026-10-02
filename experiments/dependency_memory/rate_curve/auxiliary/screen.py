"""Float screening of two fixed unsigned witnesses; not a positivity proof."""
import json
from math import log2
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.dependency_memory.joint_coding_complement import cover
from experiments.dependency_memory.joint_coding import decoder_frontier as f

losses=[f.loss_matrix(table) for table,_ in cover.orbits()]
weights=[f.nearest_weights(loss) for loss in losses]

def objective(loss,weights,t):
    total=sum(weights)
    w=[[t**l for l in row] for row in loss]
    z=[sum(q*v for q,v in zip(weights,row))/total for row in w]
    free=-sum(log2(v) for v in z)/16
    gamma=max(sum(w[x][a]/z[x] for x in range(16))/16 for a in range(16))
    return free,free-log2(gamma)

constant=[1 if a in (0,15) else 0 for a in range(16)]
rows=[]
for i in range(1,1000):
    t=i/1000
    q=weights[0] if t<=0.2 else constant
    unsigned=objective(losses[0],q,t)[0]
    for family in range(1,6):
        dual=objective(losses[family],weights[family],t)[1]
        rows.append({'t':t,'family':family,'gap':dual-unsigned})
result={'evidence_class':'post-hoc floating screen of fixed q; not a proof',
        'switch':0.2,'checks':len(rows),'minimum':min(rows,key=lambda r:r['gap']),
        'negative':[r for r in rows if r['gap']<0]}
(ROOT/'build/completion-spectrum/screen.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
