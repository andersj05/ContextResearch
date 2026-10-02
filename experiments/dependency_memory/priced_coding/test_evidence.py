"""Preserved whole-population minima, outward arithmetic and tradeoff checks."""
from fractions import Fraction as F
import inspect
import unittest
from unittest.mock import patch

from . import evidence, certificate, design, bounds, codec, tables
from experiments.dependency_memory.tie_coding import bounds as roots


class PricedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.discovery, cls.books = evidence.grade_discovery()

    def test_complete_population_minima_and_separately_scoped_training(self):
        self.assertEqual(self.discovery['starts'], 10)
        self.assertEqual(self.discovery['complete_uniform_source_assignments'], 41943040)
        self.assertEqual(self.discovery['independent_full_minimum_mismatches'], 0)
        for row in self.discovery['rows']:
            self.assertEqual(row['native_price_comparisons'], row['sources']*row['book_words'])
            self.assertEqual(row['independent_tensor_minimum_mismatches'], 0)
            if row['g'] == 5:
                self.assertEqual(row['proposal_actual_l1_difference'], 0)
                self.assertEqual(row['float_change_scope'], 'complete population')
            else:
                self.assertGreater(row['proposal_actual_l1_difference'], 0)
                self.assertEqual(row['float_change_scope'], 'fixed training sample only')

    def test_two_complete_native_calibrations(self):
        self.assertEqual(evidence.machine_calibration()['native_comparisons'], 1294947)
        controls = evidence.tensor_calibration()
        self.assertEqual(controls['complete_controls'], 4)
        self.assertEqual(controls['sources'], 8464)

    def test_finite_bound_improvement_and_preserved_failed_starts(self):
        target, plans, selected = certificate.finite_rows()
        self.assertEqual(len(target), 10)
        self.assertEqual(sum(len(r['plans']) for r in target), 50)
        self.assertEqual(len(plans), 30)
        self.assertTrue(all(not r['upper_below_C74_upper'] for r in target[:8]))
        final = selected[-1]
        self.assertEqual((final['k'], final['g'], final['a'], final['degree']), (12288, 6, 560, 16))
        self.assertLess(F(final['error_upper']), F(final['C74_named_base']))
        self.assertTrue(final['upper_below_named_C74_base'])
        self.assertEqual(F(final['error_upper']), F(54095129871619, 200000000000000))
        for row in plans:
            self.assertTrue(row['convex'])
            if row['left_difference_sign'] is not None:
                self.assertLess(row['left_difference_sign'], 0)
            if row['right_difference_sign'] is not None:
                self.assertGreaterEqual(row['right_difference_sign'], 0)

    def test_inclusive_public_payload_and_independent_root_certificates(self):
        name, _ = tables.names()
        book = tables.load(name)
        losses, error = tables.weights(name)
        self.assertEqual(error, F(111976409, 402653184))
        actor, packed = design.pack_tables(book), design.pack_planner(book, losses)
        self.assertEqual(len(actor)+10, 66513)
        self.assertEqual(len(packed)+10, 94754)
        self.assertLess(len(packed)+10, 262144)
        width = (12*book.g*16**book.g).bit_length()
        value, rows = int.from_bytes(packed, 'big'), []
        for _ in book.words:
            delta = value&((1 << width)-1)
            value >>= width
            count = value&((1 << (4*book.g+1))-1)
            value >>= 4*book.g+1
            prior = (value&((1 << (4*book.g))-1))+1
            value >>= 4*book.g
            word = value&((1 << (4*book.g))-1)
            value >>= 4*book.g
            rows.append((word, prior, count, delta))
        self.assertEqual(value, 0)
        self.assertEqual(tuple(reversed(rows)), tuple(zip(book.words, book.proposal, book.counts, losses)))
        for degree in bounds.DEGREES:
            for count in {16**book.g, *book.counts}-{0}:
                lo, hi = roots.root_bounds(count, degree, bounds.BITS)
                self.assertLessEqual(lo**degree, count)
                self.assertGreaterEqual(hi**degree, count)

    def test_separate_actual_limit_and_no_discovery_access_in_actors(self):
        name, slack = tables.names()
        self.assertEqual(name, slack)
        book = tables.load(name)
        losses, error = tables.weights(name)
        lo, hi = bounds.limiting_error(book, error)
        self.assertLess(hi, F(269293075342, 10**12))
        self.assertGreater(lo, F(267829178708, 10**12))
        self.assertGreater(lo, F(2618989801, 10**10))
        n = 10**12
        a = bounds.default_count(n, book)
        self.assertLess(abs(error+F(a, n)*(F(1, 4)-error)-hi), F(1, 10**5))
        self.assertEqual(list(inspect.signature(tables.weights).parameters), ['name'])
        with patch.object(evidence, 'grade_discovery', side_effect=AssertionError('Forbidden saved map')):
            a, _ = bounds.select(2, book, losses, error)
            xs = (0, 15, 3, 12, 5, 10)*2+(7,)
            parent = codec.encode(xs, book, a)
            for block in range(len(xs)):
                child = codec.update(parent, block, 1, len(xs), book, a)
                self.assertIn(child, (0, 1))
                self.assertEqual(codec.predict(child, block, 1, 2), child)
            for tail in range(1, book.g):
                for x in range(16):
                    xs = (x,)*tail
                    parent = codec.encode(xs, book, 0)
                    self.assertLess(parent, 1 << (2*tail))
                    expected = min(enumerate(codec.TAIL),key=lambda item:(evidence.LOSS[x][item[1]],item[0]))[1]
                    for block in range(tail):
                        self.assertEqual(codec.decode_response(parent, block, tail, book, 0), expected)

    def test_complete_small_weighted_events_and_large_constructed_routes(self):
        small = certificate.small_populations()
        self.assertEqual(len(small), 19)
        self.assertEqual(sum(r['physical_final_queries'] for r in small), 934848)
        for row in small:
            self.assertLessEqual(row['actual_fallback_sources'], row['length_bad_sources'])
            self.assertLessEqual(F(row['base_error']), F(row['actual_error']))
            self.assertLessEqual(F(row['actual_error']), F(row['base_error'])+F(row['weighted_length_excess']))
        large = certificate.large_diagnostics()
        self.assertEqual(len(large), 9)
        self.assertTrue(all(r['parent_bit_length'] <= 2*r['k'] for r in large))


if __name__ == '__main__':
    unittest.main()
