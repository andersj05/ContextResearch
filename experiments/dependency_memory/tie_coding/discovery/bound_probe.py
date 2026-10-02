import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from experiments.dependency_memory.tie_coding import codec,bounds

rows = []
for k in (96,192,384,768,1536,3072,6144,12288):
    for multiplier in (2,3,4,5,6):
        n,g = k//8,8
        a = codec.default_count(n,g,multiplier)
        result = bounds.error_bound(n,g,a)
        row = {'k':k,'n':n,'group':g,'margin_multiplier':multiplier,
               'oracle_groups':a,'base':str(float(result['base'])),
               'tail_bound':str(float(result['tail_upper'])),
               'risk_upper':str(float(result['error_upper'])),'degree':result['best_degree']}
        rows.append(row)
    print(json.dumps(min(rows[-5:],key=lambda r:float(r['risk_upper']))),flush=True)
Path(__file__).with_suffix('.json').write_text(json.dumps(rows,indent=2)+'\n')
