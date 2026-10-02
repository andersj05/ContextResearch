"""Scientific invariants and independent formulations for the cover family."""
from fractions import Fraction as F
import inspect
import json
import unittest

from experiments.dependency_memory.greedy_coding import design,codec,bounds,certificate as check


class GreedyCodingTests(unittest.TestCase):
    def test_scalar_loss_is_literal_query_error(self):
        for x in range(16):
            for a in range(16):
                self.assertEqual(design.LOSS[x][a],check.direct_loss(x,a))
        self.assertEqual(check.baseline_check()['distinct_four_word_books'],1820)

    def test_all_tensor_layers_and_greedy_choices(self):
        rows = check.design_checks()
        self.assertEqual([r['thresholds'] for r in rows],[13,25,37])
        self.assertEqual(sum(r['all_source_candidate_distances_checked'] for r in rows),16843008)
        self.assertEqual([r['selected_error'] for r in rows],['9/32','9/32','2543/9216'])

    def test_entire_small_actor_populations_and_tail(self):
        rows = check.small_populations()
        self.assertEqual(sum(r['sources'] for r in rows),12816)
        self.assertEqual(sum(r['physical_final_queries'] for r in rows),454848)
        for row in rows:
            self.assertLessEqual(row['parent_states_used'],1 << (2*row['k']))

    def test_every_small_public_parent_state(self):
        for k,g in ((1,1),(2,2),(3,3),(4,3)):
            book = design.book(g)
            for parent in range(1 << (2*k)):
                for r in range(k):
                    if r<k//g*g:
                        group,coordinate = divmod(r,g)
                        message = (parent >> (2*g*group))&((1 << (2*g))-1)
                        expected = (book[message] >> (4*coordinate))&15
                    else:
                        expected = design.BASE[(parent >> (2*g*(k//g)+2*(r-k//g*g)))&3]
                    self.assertEqual(codec.decode_response(parent,r,k,g),expected)
                    for o in range(4):
                        self.assertEqual(codec.update(parent,r,o,k,g),(expected >> o)&1)

    def test_complete_tiny_cover_recurrence(self):
        row = check.cover_recurrence_check()
        self.assertEqual(row['set_systems'],4096)
        self.assertEqual(row['competitor_and_step_comparisons'],307200)

    def test_rational_channel_and_conservative_bounds(self):
        row = check.channel_check()
        self.assertTrue(row['cross_information_upper_below_two'])
        for g in check.LARGE_GROUPS:
            for h in check.INVERSES:
                value = bounds.proximity(g,h)
                separate = (1-F(1,h))*bounds.CHANNEL_ERROR_UPPER+F(1,2*h)+F(1,h)+F(1,12*g)
                separate += F(((5+h.bit_length()-1)**2+1)*h*h,4*g)
                separate += F(5,2**min(80,g//(2*h)))
                self.assertEqual(value['unclipped_upper'],separate)
                self.assertEqual(value['upper'],min(F(1,2),separate))
        self.assertLess(bounds.proximity(10**10,512)['upper'],F(267829178707,10**12))
        self.assertGreater(bounds.proximity(10**4,16)['unclipped_upper'],F(1,2))

    def test_growth_and_all_length_tiling(self):
        for g in (2,3,4,10,100):
            first = 1 << (10*g-1)
            self.assertEqual(design.group_size(first),g)
            self.assertEqual(design.group_size(first-1),g-1)
        for k in (1,2,16,2**19,2**29,2**39,2**99):
            g = design.group_size(k)
            self.assertLessEqual(g,k)
            if g>=2:
                self.assertLessEqual(1024**g,2*k)
        for g in check.GROUPS:
            risk = F(design.analyse(g)['errors'],12*g*16**g)
            for k in range(g,40):
                expected = F((k//g)*g,k)*risk+F(k%g,k)*F(9,32)
                self.assertEqual(bounds.tiled_error(k,g,risk),expected)

    def test_boundary_access_payload_and_invalid_states(self):
        self.assertEqual(list(inspect.signature(codec.update).parameters),['parent','block','omitted','k','g'])
        self.assertEqual(list(inspect.signature(codec.predict).parameters),['child','block','omitted','query'])
        self.assertEqual([len(design.pack_book(g)) for g in check.GROUPS],[2,16,96])
        for blocks,g in (((16,),1),((-1,),1),((True,),1),((0,),0),((0,),2),((),1)):
            with self.assertRaises(ValueError):
                codec.encode(blocks,g)
        for parent in (-1,4,True):
            with self.assertRaises(ValueError):
                codec.update(parent,0,0,1,1)
        for child in (2,-1,True):
            with self.assertRaises(ValueError):
                codec.predict(child,0,0,1)
        self.assertEqual(codec.encode((0,)),0)
        self.assertEqual(codec.update(0,0,1,1),0)
        self.assertGreater(check.large_diagnostics()[0]['physical_final_queries'],0)

    def test_discovery_negative_controls_and_source_bindings(self):
        result = check.certificate()
        self.assertEqual(result['discovery']['inspected_threshold_designs'],150)
        self.assertGreater(F(result['finite_design_checks'][2]['selected_error']),F(result['retained_controls']['conditional_six_block']))
        self.assertFalse(result['large_codebooks_built'])
        self.assertFalse(result['large_source_populations_enumerated'])
        self.assertEqual(result,json.loads(check.OUTPUT.read_text(encoding='utf-8')))


if __name__=='__main__':
    unittest.main()
