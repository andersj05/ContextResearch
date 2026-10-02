"""Public uniform-source design; no source instance enters any cache key."""
from functools import cache
from itertools import product

WORDS = tuple(range(16))
BASE = (0,1,14,15)
LOSS = tuple(tuple(3*x.bit_count()+3*a.bit_count()
                   -2*x.bit_count()*a.bit_count()+2*(x&a).bit_count()
                   for a in WORDS) for x in range(16))


def group_size(k):
    if type(k) is not int or k < 1:
        raise ValueError('Expected a positive public source length')
    return max(1,k.bit_length()//10)


def loss_layers(g):
    """Tensor exact scalar loss histograms into bit sets of source indices."""
    if type(g) is not int or g < 1:
        raise ValueError('Expected a positive public group size')
    rows = {0:(1,)}
    for length in range(1,g+1):
        size = 16**(length-1)
        following = {}
        for prefix,old in rows.items():
            for a in WORDS:
                histogram = [0]*(12*length+1)
                for x in range(16):
                    cost,shift = LOSS[x][a],x*size
                    for previous,mask in enumerate(old):
                        if mask:
                            histogram[previous+cost] |= mask << shift
                following[prefix | (a << (4*(length-1)))] = tuple(histogram)
        rows = following
    return rows


def population_loss(book,layers,g):
    remaining = (1 << (16**g))-1
    errors = 0
    for level in range(12*g+1):
        mask = 0
        for word in book:
            mask |= layers[word][level]
        newly = mask&remaining
        errors += level*newly.bit_count()
        remaining &= ~newly
    if remaining:
        raise ArithmeticError('Public code did not assign every source')
    return errors


@cache
def analyse(g):
    layers = loss_layers(g)
    covers = {w:0 for w in layers}
    population = (1 << (16**g))-1
    rows = []
    for threshold in range(12*g+1):
        for w,histogram in layers.items():
            covers[w] |= histogram[threshold]
        remaining = population ^ covers[0]
        book,gains = [0],[]
        for _ in range(4**g-1):
            chosen = max(covers,key=lambda w:((covers[w]&remaining).bit_count(),-w))
            gain = (covers[chosen]&remaining).bit_count()
            if not gain:
                break
            book.append(chosen)
            gains.append(gain)
            remaining &= ~covers[chosen]
        rows.append({'threshold':threshold,'book':book,'gains':gains,
                     'uncovered':remaining.bit_count(),
                     'errors':population_loss(book,layers,g)})
    best = min(rows,key=lambda r:(r['errors'],r['threshold']))
    baseline = tuple(sum(a << (4*r) for r,a in enumerate(word))
                     for word in product(BASE,repeat=g))
    base_loss = population_loss(baseline,layers,g)
    # The fixed product baseline wins exact population ties.
    chosen = baseline if base_loss <= best['errors'] else tuple(best['book'])
    return {'group':g,'thresholds':rows,'threshold_only_best':best['threshold'],
            'threshold_only_errors':best['errors'],'baseline_errors':base_loss,
            'selected_kind':'base_product' if chosen==baseline else 'greedy_cover',
            'selected_threshold':None if chosen==baseline else best['threshold'],
            'book':list(chosen),'errors':min(base_loss,best['errors'])}


def book(g):
    return tuple(analyse(g)['book'])


def pack_book(g):
    """Four bits per response coordinate; public g/count/framing separate."""
    entries = tuple((word >> (4*r))&15 for word in book(g) for r in range(g))
    if len(entries)&1:
        entries += (0,)
    return bytes((entries[i] << 4)|entries[i+1] for i in range(0,len(entries),2))
