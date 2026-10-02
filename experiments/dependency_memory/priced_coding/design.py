"""Public descriptors, exact price selection and source-independent caches."""
from bisect import bisect_right
from dataclasses import dataclass
from functools import cache
from fractions import Fraction as F

from experiments.dependency_memory.tie_coding import design as logs


@dataclass(frozen=True)
class Book:
    g: int
    price: tuple
    words: tuple
    proposal: tuple
    counts: tuple

    def __post_init__(self):
        if type(self.g) is not int or not 1 <= self.g <= 6:
            raise ValueError('Supported public group size is 1..6')
        if (type(self.price) is not tuple or len(self.price) != 2
                or any(type(v) is not int or v < 1 for v in self.price)):
            raise ValueError('Positive rational public price required')
        n = 16**self.g
        if (any(type(v) is not tuple for v in (self.words, self.proposal, self.counts))
                or not 1 <= len(self.words) <= min(16384, n)
                or len(self.words) != len(self.proposal) or len(self.words) != len(self.counts)
                or len(set(self.words)) != len(self.words)
                or any(type(w) is not int or not 0 <= w < n for w in self.words)
                or any(type(c) is not int or not 1 <= c <= n for c in self.proposal)
                or any(type(c) is not int or not 0 <= c <= n for c in self.counts)
                or sum(self.proposal) != n or sum(self.counts) != n):
            raise ValueError('Malformed public response/proposal/CDF descriptor')

    @property
    def fallback(self):
        return max(range(len(self.words)), key=lambda i:(self.proposal[i], -i))


def masks(word, g):
    one = two = four = 0
    for r in range(g):
        weight = ((word >> (4*r))&15).bit_count()
        block = 15 << (4*r)
        if weight&1:
            one |= block
        if weight&2:
            two |= block
        if weight&4:
            four |= block
    return word, 3*word.bit_count(), one, two, four


def masked_cost(source, source_term, entry):
    word, response_term, one, two, four = entry
    dot = ((source&one).bit_count()+2*(source&two).bit_count()
           +4*(source&four).bit_count())
    return source_term+response_term-2*dot+2*(source&word).bit_count()


def cost(source, word, g):
    return masked_cost(source, 3*source.bit_count(), masks(word, g))


@cache
def compiled(book):
    """The entire key and value depend only on the fixed public descriptor."""
    numerator, denominator = book.price
    entries = tuple((masks(w, book.g), q**numerator) for w, q in zip(book.words, book.proposal))
    prefix = [0]
    for c in book.counts:
        prefix.append(prefix[-1]+c)
    return entries, tuple(prefix), denominator


def compare(cost_a, weight_a, cost_b, weight_b, denominator):
    difference = cost_a-cost_b
    left = weight_b << (denominator*max(0, difference))
    right = weight_a << (denominator*max(0, -difference))
    return (left > right)-(left < right)


def choose(source, book):
    if type(source) is not int or not 0 <= source < 16**book.g:
        raise ValueError('Exactly one public group of four-bit blocks required')
    entries, _, denominator = compiled(book)
    source_term = 3*source.bit_count()
    best = book.fallback
    best_cost = fallback_cost = masked_cost(source, source_term, entries[best][0])
    for i, (entry, weight) in enumerate(entries):
        value = masked_cost(source, source_term, entry)
        # A source cost above the largest-prior fallback cannot beat it
        # under a positive price. This is a proved rule, not a float prune.
        if value > fallback_cost:
            continue
        comparison = compare(value, weight, best_cost, entries[best][1], denominator)
        if comparison < 0 or (comparison == 0 and i < best):
            best, best_cost = i, value
    if best_cost > fallback_cost:
        raise ArithmeticError('Exact price rule violates its fixed-fallback guarantee')
    return best


def pack_tables(book):
    g = book.g
    value = 0
    for word, prior, count in zip(book.words, book.proposal, book.counts):
        value = (value << (4*g))|word
        value = (value << (4*g))|(prior-1)
        value = (value << (4*g+1))|count
    bits = len(book.words)*(12*g+1)
    return value.to_bytes((bits+7)//8, 'big')


def pack_planner(book, loss_sums):
    """Inclusive public words, priors, actual CDF and finite-planning weights."""
    if (len(loss_sums) != len(book.words) or
            any(type(v) is not int or not 0 <= v <= 12*book.g*c
                for v, c in zip(loss_sums, book.counts))):
        raise ValueError('Malformed fixed public cell loss weights')
    weight_bits = (12*book.g*16**book.g).bit_length()
    value = 0
    for word, prior, count, delta in zip(book.words, book.proposal, book.counts, loss_sums):
        value = (value << (4*book.g))|word
        value = (value << (4*book.g))|(prior-1)
        value = (value << (4*book.g+1))|count
        value = (value << weight_bits)|delta
    bits = len(book.words)*(12*book.g+1+weight_bits)
    return value.to_bytes((bits+7)//8, 'big')


@cache
def entropies(book, bits=192):
    n = 16**book.g
    distinct = {c:logs.log2_bounds(c, bits) for c in set(book.counts) if c}
    low = 4*book.g-sum(F(c, n)*distinct[c][1] for c in book.counts if c)
    high = 4*book.g-sum(F(c, n)*distinct[c][0] for c in book.counts if c)
    return low, high


def cdf_index(numerator, denominator, book):
    _, prefix, _ = compiled(book)
    target = 16**book.g*numerator//denominator
    if not 0 <= target < 16**book.g:
        raise ArithmeticError('Normalized arithmetic point outside the unit interval')
    index = bisect_right(prefix, target)-1
    if not book.counts[index]:
        raise ArithmeticError('An arithmetic point entered a zero-width cell')
    return index, prefix[index]
