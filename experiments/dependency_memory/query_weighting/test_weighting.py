"""Independent loss, capacity, timing and weighted supporting-bound checks."""
from fractions import Fraction as F
import inspect
import json
import unittest

from . import asymptotic, certificate, codec, finite
from experiments.dependency_memory.conditional_coding import codec as six
from experiments.dependency_memory.joint_coding import decoder_frontier as f


def independent_losses():
    return tuple(tuple(sum(((x >> j) & 1) != ((a >> o) & 1)
                           for o in range(4) for j in range(4) if o != j)
                       for a in range(16)) for x in range(16))


def independent_book():
    words = []
    for m in range(4096):
        left = six.OVERRIDES.get(m, six.BASE[m % 64])
        right = six.BASE[m // 64]
        words.append(tuple((left >> (4*r)) & 15 for r in range(3))
                     + tuple((right >> (4*r)) & 15 for r in range(3)))
    return tuple(words)


class QueryWeightingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = certificate.certificate()
        cls.losses = independent_losses()
        cls.book = independent_book()

    def test_all_orientations_and_source_free_boundary_with_parent_padding(self):
        checks = self.data['routing_checks']
        self.assertEqual(checks['local_response_checks'], 196608)
        self.assertEqual(checks['source_free_final_query_checks'], 589824)
        self.assertFalse(checks['larger_parent_or_source_populations_enumerated'])
        for group in range(2):
            for m in (0, 17, 3330, 3714, 4095):
                for padding in (0, 31, 963, 4095):
                    parent = (m << (12*group)) | (padding << (12*(1-group)))
                    for source_class in range(2):
                        for rank in range(3):
                            r = source_class*6 + group*3 + rank
                            a = self.book[m][rank + 3*(source_class ^ group)]
                            for o in range(4):
                                self.assertEqual(codec.update_balanced(parent, r, o, 12), (a >> o) & 1)
        self.assertEqual(list(inspect.signature(codec.predict).parameters), ['child','block','omitted','query'])
        self.assertNotIn('query', inspect.signature(codec.update_balanced).parameters)
        self.assertNotIn('p', inspect.signature(codec.encode_balanced).parameters)
        with self.assertRaises(TypeError):
            codec.predict(0, 0, 0, 1, parent=0)
        with self.assertRaises(TypeError):
            codec.update_balanced(0, 0, 0, 12, query=1)

    def test_balanced_products_fit_capacity_and_grade_actual_routes(self):
        for k in (12, 24, 36):
            half = k//2
            for seed in range(6):
                blocks = tuple((seed*7+r*11+r//3) % 16 for r in range(k))
                parent, diagnostic = codec.encode_balanced(blocks, diagnostics=True)
                expected = errors = 0
                for group in range(half//3):
                    start = 3*group
                    left, right = blocks[start:start+3], blocks[half+start:half+start+3]
                    local = right+left if group % 2 else left+right
                    m = six.encode(local)
                    expected |= m << (12*group)
                    errors += sum(self.losses[x][a] for x,a in zip(local,self.book[m]))
                self.assertEqual(parent, expected)
                self.assertLess(parent, 1 << (2*k))
                actor_errors = 0
                for r in range(k):
                    for o in range(4):
                        z = codec.update_balanced(parent, r, o, k)
                        for j in range(4):
                            if j != o:
                                actor_errors += codec.predict(z,r,o,j) != ((blocks[r] >> j) & 1)
                self.assertEqual((diagnostic, actor_errors), (errors, errors))
        pair = self.data['opposite_orientation_pair']
        self.assertEqual(pair['balanced_pair_extra_orientation_instance_bits'], 0)
        self.assertEqual(pair['public_label_payload_bytes'], 120)
        self.assertEqual(F(pair['balanced_pair_left_error']), F(pair['balanced_pair_right_error']))
        self.assertEqual(F(pair['balanced_pair_any_p_error']), F(2304567,8388608))
        self.assertEqual(F(pair['balanced_pair_any_p_error']),
                         (F(pair['frozen_uniform_encoder_left_error'])+F(pair['frozen_uniform_encoder_right_error']))/2)

    def test_weighted_encoder_matches_all_messages_and_lowest_ties(self):
        sources = {sum(x << (4*r) for r in range(6)) for x in range(16)}
        state = 70102
        for _ in range(32):
            state = (1664525*state+1013904223) & 0xffffffff
            sources.add(state & 0xffffff)
        for m, a in six.OVERRIDES.items():
            for left in (a, a ^ 4095, six.BASE[m % 64]):
                sources.add(left | (six.BASE[m // 64] << 12))
        for source in sorted(sources):
            blocks = tuple((source >> (4*r)) & 15 for r in range(6))
            for left, right in ((0,1),(1,0),(1,3),(2,3),(1,1),(3,1)):
                costs = [sum((left if r < 3 else right)*self.losses[x][a]
                             for r,(x,a) in enumerate(zip(blocks,word))) for word in self.book]
                optimum = min(costs)
                self.assertEqual(codec.encode_known_prior(blocks,left,right,diagnostics=True),
                                 (costs.index(optimum),optimum))
            self.assertEqual(codec.encode_known_prior(blocks,1,1,diagnostics=True),
                             six.encode(blocks,diagnostics=True))

    def test_entire_exact_envelope_continuity_concavity_and_frozen_failure(self):
        data = self.data['finite_known_prior_curve']
        self.assertEqual((data['source_pairs_covered'],data['right_histogram_types'],data['weighted_terms']),
                         (16**6,108,1728))
        segments = data['segments']
        self.assertEqual(len(segments),52)
        last_right, last_value, last_slope = F(0), None, None
        for row in segments:
            left,right,a,b = (F(row[key]) for key in ('left','right','intercept','slope'))
            self.assertEqual(left,last_right)
            self.assertLess(left,right)
            if last_value is not None:
                self.assertEqual(a+b*left,last_value)
                self.assertLess(b,last_slope)
            for p in (left,(left+right)/2,right):
                self.assertEqual(a+b*p,finite.direct_value(p))
                self.assertEqual(a+b*p,finite.value_from_segments(p))
            last_right,last_value,last_slope = right,a+b*right,b
        self.assertEqual(last_right,1)
        self.assertEqual(finite.direct_value(F(0)),F(40514,147456))
        self.assertEqual(F(segments[0]['slope']),F(875,75497472))
        self.assertGreater(finite.direct_value(F(1,10)),F(40514,147456))
        pair = self.data['opposite_orientation_pair']
        p = F(pair['frozen_encoder_beats_refined_product_iff_p_greater_than'])
        left,right = F(pair['frozen_uniform_encoder_left_error']),F(pair['frozen_uniform_encoder_right_error'])
        control = F(pair['refined_product_any_p_error'])
        self.assertEqual(p,F(59911,152862))
        self.assertEqual(p*left+(1-p)*right,control)
        self.assertGreater(F(1,4)*left+F(3,4)*right,control)

    def test_named_allocations_and_strict_comparison_regions(self):
        controls = self.data['single_block_allocation_controls']
        self.assertEqual([(r['errors'],r['outcomes']) for r in controls],[(60,192),(48,192)])
        balanced = F(2304567,8388608)
        endpoints = self.data['balanced_pair_beats_three_named_known_prior_controls_iff']
        self.assertEqual((F(endpoints['left']),F(endpoints['right'])),
                         (F(207415,524288),F(316873,524288)))
        for p in (F(0),F(1,4),F(endpoints['left']),F(1,2),F(endpoints['right']),F(3,4),F(1)):
            wins = balanced < min(finite.controls(p).values())
            self.assertEqual(wins,F(endpoints['left']) < p < F(endpoints['right']))
        self.assertEqual(finite.controls(F(1,4))['three_nine'],F(17,64))
        self.assertLess(F(17,64),balanced)
        for region in self.data['regular_reencoding_beats_three_named_controls_on']:
            left,right = F(region['left']),F(region['right'])
            self.assertLess(finite.direct_value((left+right)/2),min(finite.controls((left+right)/2).values()))
            self.assertEqual(region['left_included'],finite.direct_value(left) < min(finite.controls(left).values()))
            self.assertEqual(region['right_included'],finite.direct_value(right) < min(finite.controls(right).values()))

    def test_rational_supporting_bounds_slack_and_independent_channel_entropy(self):
        points = self.data['known_prior_asymptotic_characterization']['exact_numeric_support_points']
        for row in points:
            m,n = row['weights']
            q = F(row['q'])
            self.assertGreater(F(row['strict_combined_rate_slack_lower']),0)
            self.assertLess(F(row['combined_information_upper']),4)
            low,high = F(row['distortion_lower']),F(row['distortion_upper'])
            self.assertLess(F(1,4),low)
            self.assertLess(high-low,F(2,10**11))
            mirror = asymptotic.point(n,m,q)
            self.assertEqual((low,high),(F(mirror['distortion_lower']),F(mirror['distortion_upper'])))
            self.assertEqual([r['t'] for r in row['branches']],[str(q**m),str(q**n)])
            if m != n:
                self.assertLess(high,f.LOWER_TARGET)
            # Independent I=E log P(a|x)-E log P_A(a). Do not assume the
            # rational witness's chosen q is the exact output marginal.
            for branch in row['branches']:
                t,weights = F(branch['t']),branch['unsigned_weights']
                channel = []
                for x in range(16):
                    raw = [w*t**self.losses[x][a] for a,w in enumerate(weights)]
                    total = sum(raw)
                    channel.append([v/total for v in raw])
                marginal = [sum(r[a] for r in channel)/16 for a in range(16)]
                entropy_upper = F(0)
                actual_loss = F(0)
                for x,rowp in enumerate(channel):
                    for a,p in enumerate(rowp):
                        if p:
                            ratio = p/marginal[a]
                            entropy_upper += p*f.log2_bounds(ratio.numerator,ratio.denominator)[1]/16
                            actual_loss += p*self.losses[x][a]/192
                self.assertEqual(actual_loss,F(branch['distortion']))
                # Separate outward rounding may put the direct bound a few
                # log ulps above the other upper bound; allow only 1e-24.
                self.assertLess(entropy_upper,F(branch['information_upper'])+F(1,10**24))
                self.assertGreater(entropy_upper,0)

    def test_actual_class_early_not_prior_only_and_quarter_error(self):
        for k in (2,6,12):
            half = k//2
            for cls in (0,1):
                errors = 0
                for x in range(16):
                    blocks = [x]*k
                    for r in range((1-cls)*half,(2-cls)*half):
                        blocks[r] = (r*7+9) % 16
                    parent = codec.encode_early_class(blocks,cls)
                    self.assertLess(parent,1 << (3*half))
                    changed = list(blocks)
                    for r in range((1-cls)*half,(2-cls)*half):
                        changed[r] ^= 15
                    self.assertEqual(codec.encode_early_class(changed,cls),parent)
                    r = cls*half
                    for o in range(4):
                        z = codec.update_early_class(parent,r,o,k)
                        for j in range(4):
                            if j != o:
                                errors += codec.predict(z,r,o,j) != ((x >> j) & 1)
                self.assertEqual(errors,48)
            self.assertLessEqual(3*half,2*k)
        early = self.data['early_realized_class']
        self.assertEqual(early['error'],'1/4')
        self.assertEqual(list(map(F,early['late_uniform_class_limiting_error_minus_early_error_strict_interval'])),
                         [f.LOWER_TARGET-F(1,4),f.UPPER_TARGET-F(1,4)])
        contract = self.data['information_contract']
        self.assertIn('realized class',contract['early_class'])
        self.assertIn('still late',contract['known_prior'])

    def test_invalid_channels_and_preserved_discovery_failure(self):
        for left,right in ((0,0),(-1,1),(True,1),(1,1.0)):
            with self.assertRaises(ValueError):
                codec.encode_known_prior((0,)*6,left,right)
        for k in (0,6,13):
            with self.assertRaises(ValueError):
                codec.encode_balanced((0,)*k)
        for parent in (-1,1 << 24,True):
            with self.assertRaises(ValueError):
                codec.update_balanced(parent,0,0,12)
        for cls in (-1,2,True,F(1,4)):
            with self.assertRaises(ValueError):
                codec.encode_early_class((0,)*6,cls)
        with self.assertRaises(ValueError):
            codec.encode_allocated((0,)*6,2,2)
        audit = self.data['discovery']
        self.assertGreater(F(audit['initial_combined_rate_observed']),4)
        self.assertTrue(audit['initial_record_is_explicit_offline_recomputation'])
        self.assertFalse(audit['float_values_used_in_numeric_proof'])
        self.assertEqual((self.data['new_model_calls'],self.data['new_natural_episodes']),(0,0))
        self.assertEqual(len(self.data['source_sha256']),16)
        source = json.loads((certificate.HERE/'discovery/metadata.json').read_text(encoding='utf-8'))
        self.assertEqual(len(source['upstream']),2)


if __name__ == '__main__':
    unittest.main()
