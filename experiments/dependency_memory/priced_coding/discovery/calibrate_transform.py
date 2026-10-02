from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import random

HERE=Path('build/priced-vector')
spec=importlib.util.spec_from_file_location('independent_transform_driver',HERE/'check_transform.py')
driver=importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
LOSS=tuple(tuple(sum(((x>>j)&1)!=((w>>o)&1) for o in range(4) for j in range(4) if j!=o)
                 for w in range(16)) for x in range(16))
controls=[]
for g,q,price,seed in ((1,16,(1,2),0),(2,12,(2,5),19),(3,32,(1,2),37),(3,24,(2,5),53)):
    rng=random.Random(seed)
    words=rng.sample(range(16**g),q)
    # A positive integer composition: source-independent unequal priors.
    cuts=sorted(rng.sample(range(1,16**g),q-1))
    endpoints=[0]+cuts+[16**g]
    priors=[v-u for u,v in zip(endpoints,endpoints[1:])]
    mapping=[]
    loss_sum=0
    for x in range(16**g):
        costs=[sum(LOSS[(x>>(4*r))&15][(w>>(4*r))&15] for r in range(g)) for w in words]
        chosen=min(range(q),key=lambda i:(F(1<<(price[1]*costs[i]),priors[i]**price[0]),i))
        mapping.append(chosen)
        loss_sum+=costs[chosen]
    record=driver.check(g,price,words,priors,mapping,f'calibration{len(controls)}')
    if record['mismatches'] or record['exact_loss_sum']!=loss_sum:
        raise ValueError('Independent tensor method fails literal complete controls')
    controls.append({'g':g,'price':price,'seed':seed,'words':words,'proposal_counts':priors,
                     'expected_mapping':mapping,'literal_routed_loss_sum':loss_sum,
                     'native_check':record})
    print({'g':g,'sources':16**g,'tensor_comparisons':record['tensor_comparisons']},flush=True)
Path(HERE/'transform_calibration.json').write_text(json.dumps(controls,indent=2)+'\n')
