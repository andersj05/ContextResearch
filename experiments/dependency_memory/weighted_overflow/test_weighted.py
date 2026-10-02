"""Independent weighted-loss identities and finite bound optimization checks."""
from collections import Counter
from fractions import Fraction as F
import inspect
from itertools import product
import json
import unittest

from . import bounds, codec, certificate
from experiments.dependency_memory.tie_coding import codec as original, design


class WeightedOverflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = certificate.certificate()

    def test_cell_losses_equal_literal_routed_populations(self):
        for g in (1, 2, 3):
            observed = Counter()
            masses = Counter()
            for xs in product(range(16), repeat=g):
                w = original.completion(xs, g)
                masses[w] += 1
                observed[w] += sum(certificate.direct_loss(x, 0)-
                    certificate.direct_loss(x, 15 if (w >> r)&1 else 0) for r, x in enumerate(xs))
            words, counts = design.prepare(g)
            self.assertEqual(tuple(masses[w] for w in words), counts)
            self.assertEqual(tuple(observed[w] for w in words), bounds.loss_weights(g))
        for g in bounds.GROUPS:
            self.assertEqual(sum(bounds.loss_weights(g)), F(9*g*16**g, 4))

    def test_oracle_weighted_moment_is_independent_of_public_fallback(self):
        rows = self.data['oracle_fixed_fallback_identity']
        self.assertEqual(len(rows), 16)
        for row in rows:
            self.assertEqual((row['constant_fiber_excess_sum'], row['balanced_fiber_excess_sum']), (36, 12))
        # Compare a completely literal degree-eight sum with the compressed
        # two-category formula, using independent decimal arithmetic.
        from decimal import Decimal, localcontext
        with localcontext() as context:
            context.prec = 70
            for g in (1, 3, 8):
                for degree in bounds.DEGREES:
                    _, _, mh, wh = bounds.moments(g, degree)
                    exponent = Decimal(1)/degree
                    counts = Counter(sum((sum((x >> j)&1 for j in range(4) if j != o)>1) << o
                        for o in range(4)) for x in range(16))
                    moment = sum((Decimal(c)/16)**(1-exponent) for c in counts.values())
                    weighted = Decimal(0)
                    for x in range(16):
                        w = sum((sum((x >> j)&1 for j in range(4) if j != o)>1) << o for o in range(4))
                        delta = certificate.direct_loss(x, 0)-certificate.direct_loss(x, w)
                        weighted += Decimal(delta)/192*(Decimal(16)/counts[w])**exponent
                    self.assertGreaterEqual(Decimal(mh.numerator)/mh.denominator, moment)
                    self.assertGreaterEqual(Decimal(wh.numerator)/wh.denominator, weighted)

    def test_complete_small_actors_bound_weighted_overflow_not_only_probability(self):
        rows = self.data['small_complete_actor_populations']
        self.assertEqual(len(rows), 13)
        self.assertEqual(self.data['small_physical_final_queries'], 915840)
        self.assertTrue(any(r['length_bad_sources'] > r['actual_fallback_sources'] for r in rows))
        for row in rows:
            base, actual, weighted = map(F, (row['base_error'], row['exact_actual_error'],
                                          row['exact_loss_weighted_length_event']))
            self.assertLessEqual(base, actual)
            self.assertLessEqual(actual, base+weighted)
            self.assertLessEqual(weighted, F(row['length_bad_sources'], row['sources']))
            for degree in bounds.DEGREES:
                self.assertLessEqual(weighted, bounds.excess_upper(row['n'], row['g'], row['a'], degree))

    def test_discrete_convex_search_matches_independent_complete_allocation_lists(self):
        for n, g in ((1, 1), (3, 2), (8, 3), (12, 4), (24, 8), (48, 8)):
            for degree in bounds.DEGREES:
                values = [F(5, 16)-F(a, 16*n)+bounds.excess_upper(n, g, a, degree)
                          for a in range(n+1)]
                expected = min(range(n+1), key=lambda a:(values[a], a))
                plan = bounds.allocation(n, g, degree)
                self.assertEqual(plan['a'], expected)
                self.assertEqual(plan['raw_error_upper'], values[expected])
                differences = [right-left for left, right in zip(values, values[1:])]
                self.assertEqual(differences, sorted(differences))
        self.assertTrue(all(r['conditions'] for r in self.data['all_degrees_convexity_checks']))
        self.assertEqual(len(self.data['forty_full_allocation_bound_minima']), 40)
        self.assertTrue(all(r['difference_before_negative'] and r['difference_after_nonnegative']
                            for r in self.data['forty_full_allocation_bound_minima']))

    def test_larger_code_is_provably_better_at_768_and_smaller_codes_remain_losses(self):
        rows = self.data['selected_finite_codes']
        self.assertEqual([r['k'] for r in rows], list(certificate.LENGTHS))
        for row in rows:
            self.assertEqual((row['parent_bits'], row['charged_flag_bits'], row['child_bits']),
                             (2*row['k'], 1, 1))
            self.assertTrue(row['strictly_tighter_than_old_C72_certificate'])
            if row['k'] < 768:
                self.assertTrue(row['proves_loss_to_C69'])
            else:
                self.assertTrue(row['proves_improvement_over_C69'])
                self.assertTrue(row['proves_improvement_over_both_named_C71_codes'])
        at768 = next(r for r in rows if r['k'] == 768)
        self.assertEqual(at768['a'], 59)
        self.assertTrue(at768['proves_actual_improvement_over_old_C72_selected_code'])
        self.assertTrue(rows[-1]['proves_actual_improvement_over_old_C72_selected_code'])
        self.assertLess(F(rows[-1]['error_upper']), F(27065, 100000))

    def test_public_selector_preserves_actors_and_final_information_contract(self):
        self.assertEqual(list(inspect.signature(codec.predict).parameters),
                         ['child', 'block', 'omitted', 'query'])
        self.assertNotIn('query', inspect.signature(codec.update).parameters)
        for k in (1, 2, 3):
            a = codec.count(k, 1)
            for xs in product(range(16), repeat=k):
                self.assertEqual(codec.encode(xs, 1), original.encode(xs, 1, a))
                parent = codec.encode(xs, 1)
                for r in range(k):
                    for o in range(4):
                        self.assertEqual(codec.update(parent, r, o, k, 1),
                                         original.update(parent, r, o, k, 1, a))
        for n, g, a in ((True, 8, 0), (1, True, 0), (1, 5, 0), (1, 8, True), (1, 8, 2)):
            with self.assertRaises(ValueError):
                codec.count(n, g, a)
        with self.assertRaises(TypeError):
            codec.predict(0, 0, 0, 1, parent=0)

    def test_cost_cap_moving_mass_into_largest_cell_has_majorization(self):
        for counts in product(range(1, 5), repeat=4):
            largest = max(range(4), key=lambda i:(counts[i], -i))
            for donor in range(4):
                if donor == largest:
                    continue
                for mass in range(1, counts[donor]+1):
                    moved = list(counts)
                    moved[largest] += mass
                    moved[donor] -= mass
                    before, after = sorted(counts, reverse=True), sorted(moved, reverse=True)
                    self.assertTrue(all(sum(after[:i]) >= sum(before[:i]) for i in range(1, 5)))
        discovery = self.data['discovery']
        self.assertEqual(discovery['starts_independently_graded'], 384)
        self.assertTrue(discovery['new_points_above_old_C72_oracle_chord'])
        self.assertTrue(discovery['all_discovered_rate_two_interpolations_provably_lose_to_old_C72_limit'])
        self.assertGreater(F(discovery['best_rate_two_interpolation_lower']),
                           F(discovery['old_C72_limit_upper_for_negative_comparison']))

    def test_no_discovery_tables_enter_the_deployed_code(self):
        source = inspect.getsource(codec)
        self.assertNotIn('discovery', source)
        self.assertEqual(self.data['deployed_fixed_eight_table_bytes'], 1288)
        self.assertLess(self.data['deployed_fixed_eight_table_bytes'],
                        self.data['public_table_envelope_bytes'])
        self.assertFalse(self.data['large_uniform_source_populations_enumerated'])
        self.assertEqual((self.data['new_model_calls'], self.data['new_natural_episodes']), (0, 0))
        self.assertEqual(self.data['large_diagnostic_queries'], 540)
        self.assertTrue(any(not r['regular'] for r in self.data['large_constructed_diagnostics']))
        meta = json.loads((certificate.HERE/'discovery/metadata.json').read_text())
        self.assertEqual(sum(r['starts'] for r in meta['raw_records'].values()), 384)


if __name__ == '__main__':
    unittest.main()
