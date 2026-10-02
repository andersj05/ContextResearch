"""Independent exact-price, public-storage and two-boundary controls."""
from collections import Counter
from fractions import Fraction as F
import inspect
from itertools import product
import unittest

from . import design, codec, bounds
from .controls import constant_book, oracle_book
from experiments.dependency_memory.tie_coding import design as old_design


def routed(x, w):
    return sum(((x >> j)&1) != ((w >> o)&1)
               for o in range(4) for j in range(4) if o != j)


LOSS = tuple(tuple(routed(x, w) for w in range(16)) for x in range(16))


class PricedCodingTests(unittest.TestCase):
    def test_masked_loss_equals_independent_omission_query_matrices(self):
        for x, w in product(range(16), repeat=2):
            self.assertEqual(design.cost(x, w, 1), routed(x, w))
        for g in range(2, 7):
            for i in range(256):
                x = sum(((i*(r+1)+r*7)%16) << (4*r) for r in range(g))
                w = sum(((i+r*5)%16) << (4*r) for r in range(g))
                expected = sum(LOSS[(x >> (4*r))&15][(w >> (4*r))&15] for r in range(g))
                self.assertEqual(design.cost(x, w, g), expected)

    def test_shift_price_order_matches_fraction_products_including_ties(self):
        for numerator, denominator in ((1, 2), (2, 5), (5, 12)):
            for ca, cb in product(range(0, 73, 3), repeat=2):
                for qa, qb in product((1, 2, 3, 5, 11, 121, 4096, 1 << 24), repeat=2):
                    left, right = F(1 << (denominator*ca), qa**numerator), F(1 << (denominator*cb), qb**numerator)
                    self.assertEqual(design.compare(ca, qa**numerator, cb, qb**numerator, denominator),
                                     (left > right)-(left < right))

    def test_small_price_maps_equal_independent_fraction_minima_and_public_counts(self):
        for book in (constant_book(1), constant_book(2), constant_book(3), oracle_book()):
            observed = Counter()
            for x in range(16**book.g):
                expected = min(range(len(book.words)), key=lambda i:(
                    F(1 << (book.price[1]*sum(LOSS[(x >> (4*r))&15][(book.words[i] >> (4*r))&15]
                                             for r in range(book.g))), book.proposal[i]**book.price[0]), i))
                index = design.choose(x, book)
                self.assertEqual(index, expected)
                observed[index] += 1
                self.assertLessEqual(design.cost(x, book.words[index], book.g),
                                     design.cost(x, book.words[book.fallback], book.g))
            self.assertEqual(tuple(observed[i] for i in range(len(book.words))), book.counts)

    def test_packed_dictionary_has_no_full_source_assignment(self):
        for book in (constant_book(1), constant_book(3), oracle_book()):
            packed = design.pack_tables(book)
            self.assertEqual(len(packed), (len(book.words)*(12*book.g+1)+7)//8)
            value, rows = int.from_bytes(packed, 'big'), []
            g = book.g
            for _ in book.words:
                c = value&((1 << (4*g+1))-1)
                value >>= 4*g+1
                prior = (value&((1 << (4*g))-1))+1
                value >>= 4*g
                word = value&((1 << (4*g))-1)
                value >>= 4*g
                rows.append((word, prior, c))
            self.assertEqual(tuple(reversed(rows)), tuple(zip(book.words, book.proposal, book.counts)))
            self.assertEqual(value, 0)
        self.assertEqual(list(inspect.signature(design.compiled).parameters), ['book'])
        self.assertNotIn('mapping', inspect.getsource(codec))

    def test_fraction_intervals_and_grid_points_agree_with_full_small_actors_and_tails(self):
        specs = [(constant_book(1), k, a) for k in (1, 2, 3) for a in range(k+1)]
        specs += [(constant_book(2), k, a) for k in (1, 2, 3) for a in range(k//2+1)]
        specs += [(oracle_book(), k, a) for k in (1, 2) for a in range(k+1)]
        for book, k, a in specs:
            g, n = book.g, k//book.g
            for xs in product(range(16), repeat=k):
                parent, diag = codec.encode(xs, book, a, diagnostics=True)
                self.assertLess(parent, 1 << (2*k))
                if n:
                    lo, hi = F(0), F(1)
                    tokens = []
                    for block in range(a*g):
                        word = sum((sum((xs[block] >> j)&1 for j in range(4) if j != o)>1) << o for o in range(4))
                        index = codec.scalar.WORDS[1].index(word)
                        tokens.append((index, 16, codec.scalar.COUNTS[1]))
                    for group in range(a, n):
                        x = sum(xs[group*g+r] << (4*r) for r in range(g))
                        tokens.append((design.choose(x, book), 16**g, book.counts))
                    for index, denominator, counts in tokens:
                        width = hi-lo
                        lo, hi = lo+width*F(sum(counts[:index]), denominator), lo+width*F(sum(counts[:index+1]), denominator)
                    allowed = [m for m in range(1 << (2*n*g-1))
                               if lo <= F(2*m+1, 1 << (2*n*g)) < hi]
                    self.assertEqual(diag['regular'], bool(allowed))
                    self.assertEqual(diag['arithmetic_parent'],
                        ((1 << (2*n*g-1))+allowed[0]) if allowed else 0)
                for r, x in enumerate(xs):
                    if r >= n*g:
                        word = min(enumerate(codec.TAIL), key=lambda item:(LOSS[x][item[1]], item[0]))[1]
                    elif not diag['regular']:
                        word = (book.words[book.fallback] >> (4*(r%g)))&15
                    elif r < a*g:
                        word = sum((sum((x >> j)&1 for j in range(4) if j != o)>1) << o for o in range(4))
                    else:
                        group = sum(xs[(r//g)*g+j] << (4*j) for j in range(g))
                        word = (book.words[design.choose(group, book)] >> (4*(r%g)))&15
                    self.assertEqual(codec.decode_response(parent, r, k, book, a), word)
                    for o in range(4):
                        child = codec.update(parent, r, o, k, book, a)
                        self.assertEqual(child, (word >> o)&1)
                        for j in range(4):
                            if j != o:
                                self.assertEqual(codec.predict(child, r, o, j), child)

    def test_generic_weighted_bounds_and_convex_search_match_complete_small_lists(self):
        for book in (constant_book(1), constant_book(2), oracle_book()):
            losses = [0]*len(book.words)
            population_loss = 0
            for x in range(16**book.g):
                index = design.choose(x, book)
                cost = design.cost(x, book.words[index], book.g)
                population_loss += cost
                losses[index] += design.cost(x, book.words[book.fallback], book.g)-cost
            loss_sums = tuple(losses)
            error = F(population_loss, 12*book.g*16**book.g)
            self.assertEqual(F(sum(loss_sums), 12*book.g*16**book.g), F(1, 2)-error)
            for n in (1, 4, 12):
                for degree in bounds.DEGREES:
                    scores = [error+F(a, n)*(F(1, 4)-error)+bounds.excess_upper(n, book, loss_sums, a, degree)
                              for a in range(n+1)]
                    expected = min(range(n+1), key=lambda a:(scores[a], a))
                    plan = bounds.allocation(n, book, loss_sums, error, degree)
                    self.assertEqual(plan['a'], expected)
                    self.assertEqual(plan['raw_error_upper'], scores[expected])

    def test_final_actor_and_invalid_information_states(self):
        self.assertEqual(list(inspect.signature(codec.predict).parameters), ['child', 'block', 'omitted', 'query'])
        self.assertNotIn('query', inspect.signature(codec.update).parameters)
        book = constant_book(2)
        for args in (((), book, 0), ((True,), book, 0), ((16,), book, 0), ((0, 1), book, True)):
            with self.assertRaises(ValueError):
                codec.encode(*args)
        for parent in (-1, True, 1 << 6, 4):
            with self.assertRaises(ValueError):
                codec.update(parent, 0, 0, 3, book, 0)
        with self.assertRaises(TypeError):
            codec.predict(0, 0, 0, 1, parent=0)
        with self.assertRaises(ValueError):
            design.Book(1, (1, 2), (0, 0), (8, 8), (8, 8))

    def test_separate_entropy_slack_schedule_and_limit(self):
        book = constant_book(2)
        error = F(5, 16)
        limit = bounds.limiting_error(book, error)
        with self.assertRaises(ValueError):
            bounds.default_count(100, oracle_book())
        shares = []
        for n in (10**2, 10**4, 10**8, 10**12):
            a = bounds.default_count(n, book)
            shares.append(F(a, n))
            self.assertGreaterEqual(a, 0)
            self.assertLessEqual(a, n)
            precision = 64+8*(book.g+n.bit_length())
            low_hi = design.entropies(book, precision)[1]
            high_hi = book.g*old_design.entropies(1, precision)[1][1]
            margin = 4*(bounds.isqrt(n*n.bit_length()-1)+1)
            if a:
                self.assertLessEqual((n-a)*low_hi+a*high_hi, 2*n*book.g-margin)
            base = error+F(a, n)*(F(1, 4)-error)
            self.assertGreaterEqual(base, limit[0])
        self.assertEqual(shares, sorted(shares))
        self.assertLess(base-limit[1], F(1, 10**5))


if __name__ == '__main__':
    unittest.main()
