from collections import Counter
from fractions import Fraction as F
from math import log2
import json
from pathlib import Path

WORDS=tuple(range(16))
LOSS=tuple(tuple(sum(((x >> j)&1)!=((a >> o)&1) for o in range(4) for j in range(4) if j!=o)
                 for a in WORDS) for x in range(16))
H8=4-F(10,16)*log2(5)

def analyse(path):
    data=json.loads(Path(path).read_text())
    g=data['g']
    n=16**g
    output=[]
    for row in data['runs']:
        original=row['mapping']
        counts=Counter(original)
        fallback=max(counts,key=lambda w:(counts[w],-w))
        corrected=[]
        errors=0
        changes=0
        for x,w in enumerate(original):
            original_cost=sum(LOSS[(x >> (4*r))&15][(w >> (4*r))&15] for r in range(g))
            fallback_cost=sum(LOSS[(x >> (4*r))&15][(fallback >> (4*r))&15] for r in range(g))
            chosen=w if original_cost<=fallback_cost else fallback
            corrected.append(chosen)
            errors+=min(original_cost,fallback_cost)
            changes+=chosen!=w
        observed=sum(sum(LOSS[(x >> (4*r))&15][(w >> (4*r))&15] for r in range(g))
                     for x,w in enumerate(original))
        if observed!=row['loss_sum']:
            raise ValueError('Exploratory recorded distance sum differs')
        counts=Counter(corrected)
        entropy=4*g-sum(c*log2(c) for c in counts.values())/n
        error=F(errors,12*g*n)
        rate=entropy/g
        if rate<2:
            share=(2-rate)/(H8-rate)
            limit=(1-share)*float(error)+share*.25
        else:
            limit=None
        output.append({'slope':row['slope'],'seed':row['seed'],'stable':row['stable'],
                       'loss_sum':errors,'entropy':entropy,'error':str(error),
                       'rate':rate,'limit':limit,'fallback':fallback,'corrected_sources':changes,
                       'active_words':len(counts),'mapping':corrected,
                       'counts':dict(sorted(counts.items()))})
    candidates=[r for r in output if r['limit'] is not None]
    best=min(candidates,key=lambda r:r['limit'])
    print(Path(path).name,{k:v for k,v in best.items() if k not in ('mapping','counts')})
    for row in sorted(candidates,key=lambda r:r['limit'])[:8]:
        print({k:row[k] for k in ('slope','seed','error','rate','limit','active_words')})
    result={'source':str(path),'g':g,'alphabet':data['alphabet'],'rows':output,'best':best}
    Path(path).with_name(Path(path).stem+'_analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    import sys
    for path in sys.argv[1:]:
        analyse(path)
