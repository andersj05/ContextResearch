"""Independent grading of preserved finite maps; never imported by actors."""
from array import array
from collections import Counter
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

from . import design, bounds
from experiments.dependency_memory.tie_coding import design as logarithms
from experiments.dependency_memory.joint_coding import decoder_frontier as display

HERE = Path(__file__).resolve().parent
DISCOVERY = HERE/'discovery'
LOSS = tuple(tuple(sum(((x >> j)&1) != ((w >> o)&1)
                     for o in range(4) for j in range(4) if o != j)
                   for w in range(16)) for x in range(16))


def label_bytes(mapping):
    packed = array('H', mapping)
    if sys.byteorder != 'little':
        packed.byteswap()
    return packed.tobytes()


def verified_descriptor(book):
    rows = [f'{book.g} {len(book.words)} {book.price[0]} {book.price[1]}']
    for w, q in zip(book.words, book.proposal):
        lo, hi = logarithms.log2_bounds(q**book.price[0], 192)
        low, high = lo*(1 << 32), hi*(1 << 32)
        fixed = low.numerator//low.denominator
        if fixed != high.numerator//high.denominator:
            raise ValueError('The independent tensor log floor is not enclosed')
        rows.append(f'{w} {q} {fixed}')
    return ('\n'.join(rows)+'\n').encode()


def group_loss(x, w, g):
    return sum(LOSS[(x >> (4*r))&15][(w >> (4*r))&15] for r in range(g))


@cache
def machine_calibration():
    raw = gzip.decompress((DISCOVERY/'calibrate.json.gz').read_bytes())
    data = json.loads(raw)
    if data['scalar_matrix'] != [v for row in LOSS for v in row]:
        raise ValueError('Native scalar loss disagrees with all literal routed queries')
    values = (1, 2, 3, 5, 11, 121, 4096, 1 << 20, 1 << 24)
    index = 0
    for a, b in ((1, 2), (2, 5), (5, 12)):
        for ca, cb in product(range(73), repeat=2):
            for qa, qb in product(values, repeat=2):
                expected = (1 << (b*ca))*qb**a < (1 << (b*cb))*qa**a
                if expected != (data['price_less_bits'][index] == '1'):
                    raise ValueError('Bounded native price ordering disagrees with exact products')
                index += 1
    if index != len(data['price_less_bits']):
        raise ValueError('Unexpected native calibration population')
    return {'literal_scalar_queries':256*12, 'native_comparisons':index,
            'original_json_sha256':sha256(raw).hexdigest()}


@cache
def tensor_calibration():
    controls = json.loads((DISCOVERY/'transform_calibration.json').read_bytes())
    sources = queries = comparisons = 0
    for row in controls:
        g, price = row['g'], row['price']
        words, priors = row['words'], row['proposal_counts']
        expected = []
        loss = 0
        counts = Counter()
        for x in range(16**g):
            costs = [group_loss(x, w, g) for w in words]
            index = min(range(len(words)), key=lambda i:(
                F(1 << (price[1]*costs[i]), priors[i]**price[0]), i))
            expected.append(index)
            loss += costs[index]
            counts[index] += 1
        check = row['native_check']
        if (expected != row['expected_mapping'] or loss != row['literal_routed_loss_sum']
                or loss != check['exact_loss_sum'] or check['mismatches']
                or check['counts'] != [counts[i] for i in range(len(words))]
                or sha256(label_bytes(expected)).hexdigest() != check['expected_labels_sha256']):
            raise ValueError('Tensor minimum fails a full independent literal/Fraction control')
        book = design.Book(g, tuple(price), tuple(words), tuple(priors),
                           tuple(counts[i] for i in range(len(words))))
        if sha256(verified_descriptor(book)).hexdigest() != check['descriptor_sha256']:
            raise ValueError('Tensor calibration descriptor differs from certified log floors')
        sources += len(expected)
        queries += len(expected)*g*12
        comparisons += check['tensor_comparisons']
    return {'complete_controls':len(controls), 'sources':sources,
            'literal_routed_query_terms':queries, 'tensor_comparisons':comparisons}


def training_sample():
    state, seen = 0x243f6a88, set()
    while len(seen) < 131072:
        state ^= (state << 13)&0xffffffff
        state ^= state >> 17
        state ^= (state << 5)&0xffffffff
        seen.add(state&((1 << 24)-1))
    return sorted(seen)


@cache
def grade_discovery():
    metadata = json.loads((DISCOVERY/'metadata.json').read_bytes())
    for name, expected in metadata['file_sha256'].items():
        if sha256((DISCOVERY/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Preserved discovery file changed: '+name)
    root = HERE.parents[2]
    for name, expected in metadata['upstream_sha256'].items():
        if sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Original upstream evidence changed: '+name)
    summaries, books = [], {}
    total_sources = native_comparisons = tensor_comparisons = deployed_checks = 0
    for stem in ('five', 'six'):
        original = gzip.decompress((DISCOVERY/(stem+'.json.gz')).read_bytes())
        pinned = metadata['raw_records'][stem+'.json']
        if len(original) != pinned['bytes'] or sha256(original).hexdigest() != pinned['sha256']:
            raise ValueError('Decompressed discovery does not restore the original bytes')
        data = json.loads(original)
        del original
        g, n = data['g'], data['population']
        if n != 16**g or len(data['runs']) != (8 if g == 5 else 2):
            raise ValueError('Incomplete discovery start population')
        if g == 6 and data['training_source_ids'] != training_sample():
            raise ValueError('The fixed training sample does not reproduce')
        transform = json.loads((DISCOVERY/(stem+'_transform.json')).read_bytes())
        if transform['source_sha256'] != pinned['sha256']:
            raise ValueError('Independent tensor check refers to a different map')
        for number, row in enumerate(data['runs']):
            name = f'{stem}_row{number}'
            book = design.Book(g, tuple(row['price']), tuple(row['words']),
                               tuple(row['proposal_counts']), tuple(row['counts']))
            check = transform['rows'][number]
            descriptor = verified_descriptor(book)
            if (descriptor != (DISCOVERY/(name+'.txt')).read_bytes()
                    or sha256(descriptor).hexdigest() != check['descriptor_sha256']
                    or check['mismatches'] or check['source_population'] != n
                    or check['book_words'] != len(book.words)
                    or check['counts'] != row['counts']
                    or check['exact_loss_sum'] != row['exact_loss_sum']):
                raise ValueError('Tensor minimum record or exact public descriptor disagrees')
            if sha256(label_bytes(row['mapping'])).hexdigest() != check['expected_labels_sha256']:
                raise ValueError('The saved tensor comparison used different complete labels')
            if len(row['mapping']) != n or row['fallback_index'] != book.fallback:
                raise ValueError('Incomplete price map or wrong largest-prior fallback')
            fallback = book.words[book.fallback]
            counts = [0]*len(book.words)
            losses = [0]*len(book.words)
            error_sum = 0
            for x, index in enumerate(row['mapping']):
                if type(index) is not int or not 0 <= index < len(book.words):
                    raise ValueError('Invalid recorded price label')
                cost = group_loss(x, book.words[index], g)
                excess = group_loss(x, fallback, g)-cost
                if excess < 0:
                    raise ValueError('A price minimum increases fixed-fallback group loss')
                error_sum += cost
                counts[index] += 1
                losses[index] += excess
            if (tuple(counts) != book.counts or error_sum != row['exact_loss_sum']
                    or row['exact_price_comparisons'] != n*len(book.words)):
                raise ValueError('Full literal source grading differs from original exact records')
            error = F(error_sum, 12*g*n)
            if F(sum(losses), 12*g*n) != F(1, 2)-error:
                raise ValueError('Fixed fallback expectation is not one half')
            # These are additional implemented Python-selector checks, not a
            # second claim of complete Python argmin enumeration.
            probe_sources = sorted({0, n-1, *(
                (104729*t+8191*t*t)%n for t in range(64))})
            for x in probe_sources:
                if design.choose(x, book) != row['mapping'][x]:
                    raise ValueError('Deployed exact Python rule differs from checked minima')
            entropy = design.entropies(book)
            limit = bounds.limiting_error(book, error) if entropy[1] < 2*g else None
            summary = {'name':name, 'g':g, 'price':row['price'], 'seed':row['seed'],
                'sources':n, 'book_words':len(book.words), 'quantizer_loss_sum':error_sum,
                'quantizer_error':str(error), 'entropy_per_block':display.decimal_enclosure(
                    entropy[0]/g, entropy[1]/g, 12),
                'separate_slack_family_actual_limit':None if limit is None else
                    display.decimal_enclosure(*limit, 12),
                'loss_sums':losses, 'fallback_word':fallback,
                'packed_book_bytes':len(design.pack_tables(book)),
                'packed_book_oracle_tail_bytes':len(design.pack_tables(book))+10,
                'proposal_actual_l1_difference':sum(abs(c-q) for c,q in zip(book.counts, book.proposal)),
                'float_stable':row['stable_float_proposal'], 'float_updates':row['iterations'],
                'float_changes':row['changed_float_assignments'],
                'float_change_scope':'complete population' if g == 5 else 'fixed training sample only',
                'native_price_comparisons':row['exact_price_comparisons'],
                'independent_tensor_comparisons':check['tensor_comparisons'],
                'independent_tensor_near_score_comparisons':check['near_score_exact_comparisons'],
                'independent_tensor_minimum_mismatches':check['mismatches'],
                'deployed_python_probe_sources':len(probe_sources)}
            summaries.append(summary)
            books[name] = book
            total_sources += n
            native_comparisons += row['exact_price_comparisons']
            tensor_comparisons += check['tensor_comparisons']
            deployed_checks += len(probe_sources)
            del row['mapping']
        del data
    return {'starts':len(summaries), 'complete_uniform_source_assignments':total_sources,
            'recorded_native_price_comparisons':native_comparisons,
            'independent_tensor_comparisons':tensor_comparisons,
            'independent_full_minimum_mismatches':0,
            'deployed_python_probe_sources':deployed_checks, 'rows':summaries}, books
