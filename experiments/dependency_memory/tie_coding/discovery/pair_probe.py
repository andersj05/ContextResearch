"""Post-hoc floating exploration only; retained maps will need exact grading."""
from collections import Counter
from functools import cache
from math import log2
from pathlib import Path
import json
import random

WORDS = (0,3,5,6,9,10,12,15)
PAIR = tuple((a,b) for b in WORDS for a in WORDS)


def loss(x,w):
    return sum(((x >> j)&1) != ((w >> o)&1)
               for o in range(4) for j in range(4) if o != j)


SINGLE = [[loss(x,w) for w in WORDS] for x in range(16)]
COST = [[SINGLE[x&15][z%8]+SINGLE[x>>4][z//8] for z in range(64)]
        for x in range(256)]


@cache
def entropy(counts):
    return 8-sum(c*log2(c) for c in counts if c)/256


def score(mapping):
    counts = Counter(mapping)
    return (sum(COST[x][z] for x,z in enumerate(mapping))/256,
            entropy(tuple(sorted(counts.values()))), counts)


def run(slope, seed):
    if seed == 0:
        mapping = [min(range(64),key=lambda z:(COST[x][z],z)) for x in range(256)]
    elif seed < 0:
        book = (0,7,56,63) if seed == -1 else tuple(range(8))+tuple(range(56,64)) if seed == -2 else tuple(z for z in range(64) if z%8 in (0,7))
        mapping = [min(book,key=lambda z:(COST[x][z],z)) for x in range(256)]
    else:
        rng = random.Random(seed)
        book = sorted(rng.sample(range(64),rng.choice((8,12,16,24,32,48))))
        penalty = [rng.uniform(-.2,.2) for _ in range(64)]
        mapping = [min(book,key=lambda z:(COST[x][z]+penalty[z],z)) for x in range(256)]
    trajectory = []
    for iteration in range(40):
        cost,h,counts = score(mapping)
        trajectory.append((cost,h,cost+slope*h))
        penalty = [(z,-slope*log2(c)) for z,c in sorted(counts.items())]
        updated = [min(penalty,key=lambda zp:(COST[x][zp[0]]+zp[1],zp[0]))[0] for x in range(256)]
        if updated == mapping:
            break
        mapping = updated
    cost,h,counts = score(mapping)
    return {'slope':slope,'seed':seed,'iterations':len(trajectory),'branch_loss_mean':cost,
            'entropy':h,'risk':cost/24,'counts':dict(sorted(counts.items())),
            'mapping':mapping,'trajectory':trajectory,'scope':'Float search; no optimum or numerical-proof claim.'}


def main():
    slopes = (.25,.30,.35,.40,.425,.45,.475,.50,.525,.55,.60,.65,.70,.8,1.,1.25,1.5,2.)
    seeds = list(range(-3,24))
    rows = [run(t,s) for t in slopes for s in seeds]
    unique = {}
    for row in rows:
        key = tuple(row['mapping'])
        unique.setdefault(key,row)
    points = sorted(unique.values(),key=lambda row:(row['entropy'],row['risk']))
    candidates = []
    for left in points:
        if left['entropy'] > 4:
            continue
        candidates.append({'risk':left['risk'],'left':left,'right':None,'fraction_right':0})
        for right in points:
            if right['entropy'] < 4 or right['entropy']==left['entropy']:
                continue
            fraction = (4-left['entropy'])/(right['entropy']-left['entropy'])
            candidates.append({'risk':(1-fraction)*left['risk']+fraction*right['risk'],
                               'left':left,'right':right,'fraction_right':fraction})
    best = min(candidates,key=lambda row:row['risk'])
    result = {'slopes':slopes,'seeds':seeds,'runs':rows,'distinct_maps':len(unique),
              'best_rate_four_candidate':best,'no_model_calls':True}
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'runs':len(rows),'distinct_maps':len(unique),'risk':best['risk'],
                      'fraction':best['fraction_right'],
                      'left':{k:best['left'][k] for k in ('slope','seed','risk','entropy','counts')},
                      'right':None if best['right'] is None else {k:best['right'][k] for k in ('slope','seed','risk','entropy','counts')}}))


if __name__ == '__main__':
    main()
