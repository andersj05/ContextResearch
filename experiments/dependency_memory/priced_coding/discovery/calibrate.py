from pathlib import Path
import json
from itertools import product
from hashlib import sha256

raw=Path('build/priced-vector/calibrate.json').read_bytes()
data=json.loads(raw)
loss=[sum(((x>>j)&1)!=((w>>o)&1) for o in range(4) for j in range(4) if j!=o)
      for x in range(16) for w in range(16)]
assert loss==data['scalar_matrix']
values=(1,2,3,5,11,121,4096,1<<20,1<<24)
index=0
for numerator,denominator in ((1,2),(2,5),(5,12)):
    for ca,cb in product(range(73),repeat=2):
        for qa,qb in product(values,repeat=2):
            # Independent full integer products, with no guarded shift,
            # branch on cost sign or bounded machine integer arithmetic.
            expected=(1<<(denominator*ca))*qb**numerator < (1<<(denominator*cb))*qa**numerator
            if expected!=(data['price_less_bits'][index]=='1'):
                raise ValueError((numerator,denominator,ca,cb,qa,qb))
            index+=1
assert index==len(data['price_less_bits'])
print({'scalar_routes':256*12,'exact_machine_price_comparisons':index,
       'record_sha256':sha256(raw).hexdigest()})
