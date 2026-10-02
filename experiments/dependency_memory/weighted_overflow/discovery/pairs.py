import sys
import json
from pathlib import Path

for name in sys.argv[1:]:
    data=json.loads(Path(name).read_text())
    rows=data['rows']
    best=None
    for left in rows:
        if left['rate']>2:
            continue
        for right in rows:
            if right['rate']<=2:
                continue
            share=(2-left['rate'])/(right['rate']-left['rate'])
            from fractions import Fraction as F
            risk=(1-share)*float(F(left['error']))+share*float(F(right['error']))
            if best is None or risk<best[0]:
                best=(risk,left,right,share)
    if best:
        print(name,'pair risk',best[0],'share',best[3],
              [{k:r[k] for k in ('slope','seed','error','rate','active_words')} for r in best[1:3]])
