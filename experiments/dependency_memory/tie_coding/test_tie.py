"""Independent scientific invariants for coordinated ties and hard-cap coding."""
from collections import Counter
from fractions import Fraction as F
import inspect
from itertools import permutations,product
from math import comb,isqrt
import unittest

from . import certificate,codec,design,bounds
from experiments.dependency_memory.entropy_coding import codec as scalar


class TieCodingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = certificate.certificate()

    def test_weighted_cover_and_literal_source_queries_agree(self):
        self.assertEqual([r['group'] for r in self.data['weighted_cover_checks']],list(certificate.GROUPS))
        for row in self.data['weighted_cover_checks']:
            g = row['group']
            self.assertEqual(sum(row['counts']),16**g)
            self.assertEqual(row['weighted_status_categories'],3**g)
            self.assertEqual(sorted(row['priority']),list(range(1 << g)))
            self.assertTrue(all(c>=5**g for c in row['counts']))
            self.assertEqual(row['all_greedy_choices_independently_recounted'],1 << g)
        self.assertEqual(self.data['literal_quantizer_physical_final_queries'],153792)
        for row in self.data['literal_quantizer_populations']:
            self.assertEqual(F(row['errors'],row['physical_final_queries']),F(5,16))
        self.assertEqual(self.data['fixed_eight_packed_public_payload_bytes'],1288)
        for g in certificate.GROUPS:
            words,counts = design.prepare(g)
            value = int.from_bytes(design.pack_tables(g),'big')
            reconstructed = []
            for _ in words:
                c = value&((1 << (4*g))-1)
                value >>= 4*g
                w = value&((1 << g)-1)
                value >>= g
                reconstructed.append((w,c))
            self.assertEqual(tuple(reversed(reconstructed)),tuple(zip(words,counts)))
            self.assertEqual(value,0)

    def test_pair_entropy_optimum_has_universal_mass_bounds_and_feasible_extremum(self):
        words,counts = design.prepare(2)
        self.assertEqual((words,counts),((0,3,1,2),(121,85,25,25)))
        for priority in permutations(range(4)):
            observed = Counter()
            for x,y in product(range(16),repeat=2):
                allowed = []
                for w in priority:
                    if all(certificate.direct_loss(v,15 if (w >> r)&1 else 0)
                           ==min(certificate.direct_loss(v,0),certificate.direct_loss(v,15))
                           for r,v in enumerate((x,y))):
                        allowed.append(w)
                observed[allowed[0]] += 1
            sorted_counts = sorted(observed.values(),reverse=True)
            self.assertTrue(all(c>=25 for c in sorted_counts))
            self.assertLessEqual(sorted_counts[0],121)
            self.assertTrue(all(sum(sorted_counts[:j])<=sum(counts[:j]) for j in range(1,5)))
        # Universal mandatory 5*5 masses and maximal 11*11 compatibility
        # imply the same inequalities for every assignment, not just priorities.
        self.assertEqual((5**2,11**2,256-2*25,256-25),(25,121,206,231))
        limits = self.data['fixed_group_limits']
        self.assertLess(F(limits[1]['actual_fixed_group_code_limit'][1]),
                        F(limits[0]['actual_fixed_group_code_limit'][0]))

    def test_fraction_intervals_find_the_first_charged_grid_point_independently(self):
        specs = [(n,1,a) for n in (1,2,3) for a in range(n+1)]
        specs += [(1,g,a) for g in (2,3) for a in (0,1)]
        for n,g,a in specs:
            tokens = [(16,scalar.WORDS[1],scalar.COUNTS[1],'high') for _ in range(a*g)]
            words,counts = design.prepare(g)
            tokens += [(16**g,words,counts,'low') for _ in range(n-a)]
            for symbols in product(*(t[1] for t in tokens)):
                low,high = F(0),F(1)
                sources = []
                for symbol,(den,alphabet,weights,kind) in zip(symbols,tokens):
                    index = alphabet.index(symbol)
                    old_low,width = low,high-low
                    cumulative = sum(weights[:index])
                    low,high = old_low+width*F(cumulative,den),old_low+width*F(cumulative+weights[index],den)
                    if kind=='high':
                        sources.append(next(x for x in range(16) if scalar.response(x,True)==symbol))
                    else:
                        sources.extend(15 if (symbol >> r)&1 else 0 for r in range(g))
                k = n*g
                allowed = [m for m in range(1 << (2*k-1))
                           if low<=F(2*m+1,1 << (2*k))<high]
                parent,diag = codec.encode(sources,g,a,diagnostics=True)
                self.assertEqual(diag['regular'],bool(allowed))
                self.assertEqual(parent,((1 << (2*k-1))+allowed[0]) if allowed else 0)
                self.assertEqual(F(diag['interval_low'],1 << (4*k)),low)
                self.assertEqual(F(diag['interval_width'],1 << (4*k)),high-low)

    def test_complete_arithmetic_populations_and_scalar_code_control(self):
        rows = self.data['small_full_arithmetic_populations']
        self.assertEqual(len(rows),13)
        self.assertEqual(sum(r['sources'] for r in rows),25888)
        self.assertEqual(self.data['small_arithmetic_physical_final_queries'],915840)
        self.assertTrue(any(r['actual_fallback_sources'] for r in rows))
        self.assertTrue(any(r['length_bad_sources']>r['actual_fallback_sources'] for r in rows))
        for row in rows:
            n,g,a = row['n'],row['g'],row['a']
            self.assertEqual(row['physical_final_queries'],12*n*g*16**(n*g))
            proof = bounds.error_bound(n,g,a)
            self.assertLessEqual(proof['base'],F(row['exact_error']))
            self.assertLessEqual(F(row['exact_error']),proof['error_upper'])
        for k in (1,2,3):
            for a in range(k+1):
                for source in range(16**k):
                    blocks = tuple((source >> (4*r))&15 for r in range(k))
                    self.assertEqual(codec.encode(blocks,1,a),scalar.encode(blocks,a))

    def test_root_moment_enclosures_and_small_tail_population_bounds(self):
        for value in (1,2,3,4,5,9,16,25,85,121,11**8):
            for degree in (1,2,3,8,16,32,64,128):
                low,high = bounds.root_bounds(value,degree,32)
                self.assertLessEqual(low**degree,value)
                self.assertGreaterEqual(high**degree,value)
                self.assertLessEqual(high-low,F(1,1 << 32))
        self.assertEqual(bounds.moment_upper((1,4,4),9,2),F(5,3))
        for row in self.data['small_full_arithmetic_populations']:
            q = F(row['length_bad_sources'],row['sources'])
            for degree in certificate.DEGREES:
                self.assertLessEqual(q,bounds.tail_upper(row['n'],row['g'],row['a'],degree))
        low,high = design.log2_bounds(5,128)
        self.assertTrue(F(16,7)<low<high<F(7,3))
        twice_lo,twice_hi = design.log2_bounds(25,128)
        self.assertLessEqual(twice_lo,2*high)
        self.assertLessEqual(2*low,twice_hi)
        for exponent in range(25):
            low,high = design.log2_bounds(1 << exponent,128)
            self.assertEqual((low,high),(F(exponent),F(exponent)))

    def test_entropy_plans_have_public_slack_and_growing_group_tables_are_polynomial(self):
        for n in (1,7,8,16,24,48,96,192,384,768,1536,4096):
            for g,multiplier in ((8,4),(design.growing_group(n),4*design.growing_group(n))):
                a = codec.default_count(n,g,multiplier)
                bits = 64+8*(g+n.bit_length())
                (_,lo),(_,hi) = design.entropies(g,bits)
                margin = multiplier*(isqrt(n*n.bit_length()-1)+1)
                if n*lo<=2*g*n-margin:
                    self.assertLessEqual(a*hi+(n-a)*lo,2*g*n-margin)
                    if a<n:
                        self.assertGreater((a+1)*hi+(n-a-1)*lo,2*g*n-margin)
                else:
                    self.assertEqual(a,0)
            g = design.growing_group(n)
            if n>=8:
                self.assertLessEqual(16**g,2*n)
                self.assertLessEqual(4**g*4**g,2*n)
        fixed = self.data['fixed_group_limits']
        self.assertLess(F(fixed[-1]['actual_fixed_group_code_limit'][1]),F(27,100))
        growing = self.data['growing_family']
        low,high = map(F,growing['actual_growing_group_code_limit'])
        self.assertLess(F(261899,10**6),low)
        self.assertLess(high,F(fixed[-1]['actual_fixed_group_code_limit'][0]))

    def test_first_compatible_rank_and_prefix_bounds_support_the_entropy_limit(self):
        for g in range(1,7):
            total = 1 << g
            for forced in range(g+1):
                compatible = 1 << (g-forced)
                denominator = comb(total,compatible)
                mass = [comb(total-r,compatible-1) for r in range(1,total-compatible+2)]
                self.assertEqual(sum(mass),denominator)
                mean = F(sum(r*c for r,c in enumerate(mass,1)),denominator)
                self.assertEqual(mean,F(total+1,compatible+1))
                self.assertLessEqual(mean,1 << forced)
        for g in range(1,9):
            lengths = [(r.bit_length()-1)+2*((r.bit_length()).bit_length()-1)+1
                       for r in range(1,(1 << g)+1)]
            self.assertLessEqual(sum(F(1,1 << length) for length in lengths),1)
        self.assertEqual(sum(F(comb(8,q)*5**q*3**(8-q)*q,8**8) for q in range(9)),5)

    def test_finite_controls_diagnostic_routes_and_every_small_parent(self):
        rows = self.data['finite_bounds']
        self.assertEqual(len(rows),40)
        best = self.data['best_checked_bound_by_length']
        for row in best:
            self.assertEqual(row['parent_bits'],2*row['k'])
            self.assertEqual((row['charged_flag_bits'],row['child_bits']),(1,1))
            if row['k']<=768:
                self.assertTrue(row['proves_loss_to_C69'])
                self.assertTrue(row['proves_loss_to_named_better_C71_code'])
            else:
                self.assertTrue(row['proves_improvement_over_C69'])
                self.assertTrue(row['proves_improvement_over_both_C71_codes'])
        self.assertLess(F(best[-1]['conservative_error_upper']),F(271,1000))
        large = self.data['large_constructed_diagnostics']
        self.assertTrue(any(r['regular'] for r in large))
        self.assertTrue(any(not r['regular'] for r in large))
        self.assertTrue(any(r['family']=='growing' for r in large))
        for row in large:
            self.assertLessEqual(row['parent_bit_length'],2*row['n']*row['g'])
        for n,g,a in ((1,1,0),(1,1,1),(1,2,0),(1,2,1),(1,3,0),(1,3,1)):
            k = n*g
            for parent in (0,*range(1 << (2*k-1),1 << (2*k))):
                for r in range(k):
                    word = codec.decode_response(parent,r,n,g,a)
                    for o in range(4):
                        self.assertEqual(codec.update(parent,r,o,n,g,a),(word >> o)&1)

    def test_information_contract_invalid_states_and_immutable_discovery(self):
        self.assertEqual(list(inspect.signature(codec.predict).parameters),['child','block','omitted','query'])
        self.assertNotIn('query',inspect.signature(codec.update).parameters)
        for parent in (-1,True,1,16):
            with self.assertRaises(ValueError):
                codec.update(parent,0,0,1,2,0)
        for sources,g,a in (((),8,0),((True,),1,0),((0,),True,0),((0,),1,True),((16,),1,1)):
            with self.assertRaises(ValueError):
                codec.encode(sources,g,a)
        with self.assertRaises(TypeError):
            codec.predict(0,0,0,1,parent=0)
        self.assertEqual(self.data['discovery']['pair_maps_independently_graded'],486)
        self.assertEqual(self.data['discovery']['distinct_inspected_pair_maps'],239)
        self.assertFalse(self.data['discovery']['floating_displays_used_in_numeric_proof'])
        self.assertEqual((self.data['new_model_calls'],self.data['new_natural_episodes']),(0,0))
        self.assertFalse(self.data['large_source_populations_enumerated'])
        self.assertEqual(len(self.data['source_sha256']),17)


if __name__=='__main__':
    unittest.main()
