from fractions import Fraction as F
import json
from pathlib import Path
from experiments.dependency_memory.priced_coding import design,bounds
from experiments.dependency_memory.weighted_overflow import certificate as old

raw=json.loads(Path('build/priced-vector/five.json').read_bytes())
saved=json.loads(Path('build/priced-vector/five_analysis.json').read_bytes())
checks=0
for source,record in zip(raw['runs'],saved['rows']):
    book=design.Book(5,tuple(source['price']),tuple(source['words']),
                     tuple(source['proposal_counts']),tuple(source['counts']))
    for expected in record['plans_12288']:
        actual=bounds.allocation(12288//5,book,tuple(record['loss_sums']),
                                F(record['exact_quantizer_error']),expected['degree'])
        upper=F((12288//5)*5,12288)*actual['error_upper']+F(12288%5,12288)*F(9,32)
        assert (actual['a'],str(old.rounded(upper)),actual['convex']) == (
            expected['a'],expected['error_upper'],expected['convex'])
        checks+=1
print({'original_large_bounds_reproduced_after_product_cancellation':checks})
