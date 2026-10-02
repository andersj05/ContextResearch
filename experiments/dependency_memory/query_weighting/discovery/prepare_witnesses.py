"""Select bounded rational witnesses; preserve failures, no model requests."""
from decimal import Decimal, ROUND_CEILING
from fractions import Fraction as F
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.dependency_memory.query_weighting import asymptotic

seed=json.loads(Path(__file__).with_name('corrected_probe.json').read_text())
points=[]
attempts=[]
for row in seed['float_witnesses']:
    numerator=int((Decimal(str(row['q']))*10**12).to_integral_value(rounding=ROUND_CEILING))+1
    for extra in range(10):
        q=F(numerator+extra,10**12)
        try:
            result=asymptotic.point(row['m'],row['n'],q)
        except ValueError as e:
            attempts.append({'m':row['m'],'n':row['n'],'q':str(q),'accepted':False,'reason':str(e)})
            continue
        attempts.append({'m':row['m'],'n':row['n'],'q':str(q),'accepted':True})
        points.append({'m':row['m'],'n':row['n'],'q':str(q)})
        print(row['p'],q,result['limiting_distortion_enclosure'], 'rate slack', float(F(result['strict_combined_rate_slack_lower'])),flush=True)
        break
    else:
        raise ValueError('No witness admitted within the declared10-step cap')
Path(__file__).with_name('witnesses.json').write_text(json.dumps({'points':points,'exact_admission_attempts':attempts},indent=2)+'\n',encoding='utf-8')
