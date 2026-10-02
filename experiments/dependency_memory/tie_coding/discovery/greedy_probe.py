"""Constructed floating direction probe; exact integer source-type counts."""
from itertools import product
from math import log2
from pathlib import Path
import json


def run(g):
    patterns = []
    by_word = [[] for _ in range(1 << g)]
    masses = [11**g]*(1 << g)
    for status in product(range(3),repeat=g):
        forced = sum((s != 2) << i for i,s in enumerate(status))
        values = sum((s == 1) << i for i,s in enumerate(status))
        free = ((1 << g)-1)^forced
        weight = 5**forced.bit_count()*6**(g-forced.bit_count())
        compatible = []
        subset = free
        while True:
            compatible.append(values | subset)
            if subset == 0:
                break
            subset = (subset-1)&free
        index = len(patterns)
        patterns.append((weight,compatible))
        for word in compatible:
            by_word[word].append(index)
    assigned = [False]*len(patterns)
    used = [False]*(1 << g)
    priority,counts = [],[]
    for _ in range(1 << g):
        word = max((w for w in range(1 << g) if not used[w]),key=lambda w:(masses[w],-w))
        priority.append(word)
        counts.append(masses[word])
        used[word] = True
        for index in by_word[word]:
            if assigned[index]:
                continue
            assigned[index] = True
            weight,compatible = patterns[index]
            for w in compatible:
                masses[w] -= weight
    assert all(assigned) and sum(counts)==16**g and all(c >= 5**g for c in counts)
    h = 4*g-sum(c*log2(c) for c in counts)/(16**g)
    high = g*(4-10*log2(5)/16)
    fraction = (2*g-h)/(high-h)
    return {'group':g,'priority':priority,'counts_in_priority_order':counts,
            'entropy':h,'entropy_per_block':h/g,'oracle_fraction':fraction,
            'mixture_risk':5/16-fraction/16,
            'status_categories':len(patterns),'source_mass':16**g,
            'scope':'Exact integer type counts; floating entropy/limit are discovery only. Greedy is not certified optimal.'}


rows = [run(g) for g in (1,2,3,4,6,8)]
Path(__file__).with_suffix('.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ('group','entropy_per_block','oracle_fraction','mixture_risk','status_categories')} for r in rows]))
