"""Public exact-log descriptors and independent tensor verification driver."""
from array import array
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from experiments.dependency_memory.priced_coding import design
from experiments.dependency_memory.tie_coding import design as logs

HERE = Path('build/priced-vector')

def descriptor(g, price, words, priors):
    result = [f'{g} {len(words)} {price[0]} {price[1]}']
    for w, q in zip(words, priors):
        lo, hi = logs.log2_bounds(q**price[0], 192)
        lower, upper = lo*(1 << 32), hi*(1 << 32)
        fixed = lower.numerator//lower.denominator
        if fixed != upper.numerator//upper.denominator:
            raise ValueError('Fixed-point logarithm floor is not certified')
        result.append(f'{w} {q} {fixed}')
    return ('\n'.join(result)+'\n').encode()

def check(g, price, words, priors, mapping, name):
    d = HERE/(name+'.txt')
    expected = HERE/(name+'.bin')
    out = HERE/(name+'_transform.json')
    d.write_bytes(descriptor(g,price,words,priors))
    packed = array('H',mapping)
    if sys.byteorder != 'little':
        packed.byteswap()
    expected.write_bytes(packed.tobytes())
    # The native verifier constructs all minima via a separate tensor transform.
    run = subprocess.run([str(HERE/'transform.exe'),str(d),str(expected),str(out)],check=True)
    result=json.loads(out.read_bytes())
    result['descriptor_sha256']=sha256(d.read_bytes()).hexdigest()
    result['expected_labels_sha256']=sha256(expected.read_bytes()).hexdigest()
    return result

def main():
    for path in sys.argv[1:]:
        raw=Path(path).read_bytes()
        data=json.loads(raw)
        records=[]
        for i,row in enumerate(data['runs']):
            result=check(data['g'],row['price'],row['words'],row['proposal_counts'],
                         row['mapping'],Path(path).stem+f'_row{i}')
            if (result['exact_loss_sum']!=row['exact_loss_sum'] or
                result['counts']!=row['counts'] or result['mismatches']):
                raise ValueError('Independent tensor minimum disagrees with recorded map')
            records.append(result)
            print({k:v for k,v in result.items() if k!='counts'},flush=True)
        output={'source_sha256':sha256(raw).hexdigest(),
                'original_map_minima_independently_matched':True,'rows':records}
        Path(path).with_name(Path(path).stem+'_transform.json').write_text(
            json.dumps(output,indent=2)+'\n')

if __name__=='__main__':
    main()
