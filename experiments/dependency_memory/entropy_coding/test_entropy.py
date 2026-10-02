"""Independent interval, population, binomial, framing and asymptotic checks."""
from fractions import Fraction as F
import inspect
from itertools import product
from math import comb,isqrt
import unittest

from . import certificate,codec,finite


class EntropyCodingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = certificate.certificate()

    def test_quantizer_counts_and_conditional_excess_from_literal_query_losses(self):
        rows = self.data['quantizers']
        self.assertEqual([(r['errors'],r['outcomes']) for r in rows],[(60,192),(48,192)])
        self.assertEqual(rows[0]['counts_out_of_sixteen'],[11,5])
        self.assertEqual(rows[1]['counts_out_of_sixteen'],[5,1,1,1,1,1,1,5])
        for x in range(16):
            for oracle in (False,True):
                a = codec.response(x,oracle)
                loss = certificate.direct_loss(x,a)
                self.assertLessEqual(loss,certificate.direct_loss(x,0))
                if oracle:
                    self.assertEqual(loss,min(certificate.direct_loss(x,w) for w in range(16)))
        self.assertEqual(self.data['public_label_probability_payload_bytes'],10)
        packed = codec.pack_tables()
        values = tuple(v for byte in packed for v in (byte >> 4,byte & 15))
        self.assertEqual(values,tuple(v for rows in (codec.WORDS,codec.COUNTS) for row in rows for v in row))

    def test_arithmetic_midpoints_against_independent_fraction_intervals(self):
        for k in range(1,4):
            for a in range(k+1):
                alphabets = [codec.WORDS[int(r<a)] for r in range(k)]
                for words in product(*alphabets):
                    low,high = F(0),F(1)
                    source = []
                    for r,word in enumerate(words):
                        kind = int(r<a)
                        index = codec.WORDS[kind].index(word)
                        width = high-low
                        cumulative = sum(codec.COUNTS[kind][:index])
                        low,high = low+width*F(cumulative,16),low+width*F(cumulative+codec.COUNTS[kind][index],16)
                        source.append(next(x for x in range(16) if codec.response(x,kind)==word))
                    allowed = [m for m in range(1 << (2*k-1)) if low <= F(2*m+1,1 << (2*k)) < high]
                    parent,diag = codec.encode(source,a,diagnostics=True)
                    self.assertEqual(diag['regular'],bool(allowed))
                    if allowed:
                        self.assertEqual(parent,(1 << (2*k-1))+allowed[0])
                        self.assertEqual(tuple(codec.decode_response(parent,r,k,a) for r in range(k)),words)
                    else:
                        self.assertEqual(parent,0)
                    if high-low >= F(1,1 << (2*k-1)):
                        self.assertTrue(diag['regular'])

    def test_complete_small_populations_bound_actual_risk_and_fallback(self):
        rows = self.data['small_full_population_actor_checks']
        self.assertEqual(len(rows),9)
        self.assertEqual(self.data['small_source_assignments'],17184)
        self.assertEqual(self.data['small_physical_final_queries'],608640)
        self.assertTrue(any(r['encoder_fallback_sources'] for r in rows))
        self.assertTrue(any(r['length_bad_sources']>r['encoder_fallback_sources'] for r in rows))
        for row in rows:
            k,a = row['k'],row['oracle_blocks']
            self.assertEqual(row['outcomes'],12*k*16**k)
            bound = finite.bound(k,a)
            actual = F(row['errors'],row['outcomes'])
            self.assertLessEqual(bound['base_error'],actual)
            self.assertLessEqual(actual,bound['error_upper'])
            self.assertLessEqual(row['used_parent_messages'],(1 << (2*k-1))+1)
            self.assertLessEqual(row['encoder_fallback_sources'],row['length_bad_sources'])

    def test_binomial_tail_formula_against_direct_two_dimensional_sums(self):
        for k in range(1,13):
            for a in range(k+1):
                b = k-a
                total = 8**a*16**b
                bad = excess = 0
                for u in range(a+1):
                    for v in range(b+1):
                        if 5**(a-u+v)*11**(b-v) < 2**(2*k+1):
                            mass = comb(a,u)*3**u*5**(a-u)*comb(b,v)*5**v*11**(b-v)
                            bad += mass
                            excess += mass*(18*a-8*u+36*v)
                data = finite.bound(k,a)
                self.assertEqual(data['failure_event_upper_probability'],F(bad,total))
                self.assertEqual(data['conditional_excess_upper'],F(excess,60*k*total))
        for n in range(21):
            for yes,no in ((3,5),(5,11)):
                self.assertEqual(finite.binomial_weights(n,yes,no),[comb(n,u)*yes**u*no**(n-u) for u in range(n+1)])

    def test_public_entropy_schedule_has_exact_slack_and_maximal_count(self):
        for k in (1,2,3,4,7,8,15,16,33,96,192,384,768,1536,3072,6144,12288):
            a = codec.default_count(k)
            length = k.bit_length()
            self.assertTrue(2**(length-1) < k+1 <= 2**length)
            margin = isqrt(k*length-1)+1
            self.assertTrue((margin-1)**2 < k*length <= margin**2)
            target = 2**(32*k+16*margin)
            self.assertGreaterEqual(5**(5*(k+a))*11**(11*(k-a)),target)
            if a<k:
                self.assertLess(5**(5*(k+a+1))*11**(11*(k-a-1)),target)
        self.assertGreater(5**5*11**11,2**48)
        self.assertGreater(5**25*11**11,2**96)
        result = self.data['asymptotic']
        low,high = map(F,result['implemented_entropy_schedule_error_limit_enclosure'])
        self.assertLess(F(261899,10**6),low)
        self.assertLess(low,high)
        self.assertLess(high,F(13,48))
        self.assertLess(F(13,48),F(2304567,8388608))
        self.assertTrue(result['scalar_fraction_limit_not_global_rate_distortion_optimum'])

    def test_large_bounds_include_stronger_controls_and_proved_small_losses(self):
        rows = self.data['finite_bounds']
        self.assertEqual(len(rows),16)
        for row in rows:
            k,a = row['k'],row['oracle_blocks']
            data = finite.bound(k,a)
            self.assertEqual(certificate.verify_frontier(data),k-a+1)
            self.assertEqual((row['parent_bits'],row['payload_grid_bits'],row['charged_flag_bits'],row['child_bits']),
                             (2*k,2*k-1,1,1))
            self.assertLessEqual(data['error_upper'],F(row['coded_error_upper_rounded_outward']))
            if k<=768:
                self.assertTrue(row['proves_loss_to_repeated_C69'])
                self.assertFalse(row['proves_improvement_over_repeated_C69'])
            else:
                self.assertTrue(row['proves_improvement_over_repeated_C69'])
        last = {r['schedule']:r for r in rows if r['k']==12288}
        self.assertLess(F(last['rational']['coded_error_upper_rounded_outward']),
                        F(last['entropy']['coded_error_upper_rounded_outward']))
        self.assertLess(F(last['rational']['coded_error_upper_rounded_outward']),F(272,1000))
        self.assertFalse(self.data['large_uniform_source_populations_enumerated'])
        self.assertTrue(self.data['finite_bounds_are_not_exact_large_code_risks'])

    def test_large_constructed_routes_and_every_valid_small_parent(self):
        large = self.data['large_constructed_diagnostics']
        self.assertEqual(len(large),12)
        self.assertTrue(any(r['regular'] for r in large))
        self.assertTrue(any(not r['regular'] for r in large))
        for row in large:
            self.assertLessEqual(row['parent_bit_length'],2*row['k'])
        for k in range(1,4):
            for a in range(k+1):
                for parent in (0,*range(1 << (2*k-1),1 << (2*k))):
                    for r in range(k):
                        word = codec.decode_response(parent,r,k,a)
                        for o in range(4):
                            z = codec.update(parent,r,o,k,a)
                            self.assertEqual(z,(word >> o) & 1)
                            for j in range(4):
                                if j!=o:
                                    self.assertEqual(codec.predict(z,r,o,j),z)

    def test_information_access_invalid_states_and_preserved_discovery(self):
        self.assertEqual(list(inspect.signature(codec.predict).parameters),['child','block','omitted','query'])
        self.assertNotIn('query',inspect.signature(codec.update).parameters)
        for parent in (-1,True,1,1 << 6):
            with self.assertRaises(ValueError):
                codec.update(parent,0,0,3,0)
        for a in (-1,4,True,F(1,2)):
            with self.assertRaises(ValueError):
                codec.encode((0,)*3,a)
        for blocks in ((),(True,),(16,),(-1,)):
            with self.assertRaises(ValueError):
                codec.encode(blocks)
        with self.assertRaises(TypeError):
            codec.predict(0,0,0,1,parent=0)
        with self.assertRaises(TypeError):
            codec.update(0,0,0,3,query=1)
        self.assertEqual((self.data['new_model_calls'],self.data['new_natural_episodes']),(0,0))
        self.assertTrue(self.data['discovery']['prototype_control_retained'])
        self.assertFalse(self.data['discovery']['float_displays_used_in_numeric_proof'])
        self.assertEqual(len(self.data['source_sha256']),15)


if __name__ == '__main__':
    unittest.main()
