"""Scientific loss, nearest-parent, grouping, locality and memory checks."""
from fractions import Fraction
import inspect
import json
import unittest

from . import certificate, codec


def independent_book(base, overrides):
    # Separate public reconstruction, in integer M order; no codec lookup.
    words = []
    for right in range(64):
        for left in range(64):
            m = left + 64*right
            l = overrides.get(m, base[left])
            r = base[right]
            bits = f'{r:012b}{l:012b}'
            words.append(tuple(int(bits[24-4*i-4:24-4*i], 2) for i in range(6)))
    return tuple(words)


class ConditionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = certificate.certificate()
        cls.book = independent_book(codec.BASE, codec.OVERRIDES)

    def test_all_branch_losses_and_public_response_words(self):
        self.assertEqual(certificate.direct_losses(), codec.LOSSES)
        self.assertEqual(len(set(self.book)), 4096)
        for m, word in enumerate(self.book):
            for r, response in enumerate(word):
                self.assertEqual(codec.response_word(m, r), response)
                for o in range(4):
                    child = codec.update(m, r, o)
                    self.assertEqual(child, (response >> o) & 1)
                    for j in range(4):
                        if o != j:
                            self.assertEqual(codec.predict(child, r, o, j), child)

    def test_encoder_matches_complete_parent_book_with_declared_ties(self):
        sources = {sum(x << (4*r) for r in range(6)) for x in range(16)}
        state = 69329
        for _ in range(128):
            state = (1664525*state + 1013904223) & 0xffffffff
            sources.add(state & 0xffffff)
        # Include every changed left response, its complement and right labels.
        for m, c in codec.OVERRIDES.items():
            for left in (c, c ^ 4095, codec.BASE[m & 63]):
                sources.add(left | (codec.BASE[m >> 6] << 12))
        losses = certificate.direct_losses()
        for source in sorted(sources):
            blocks = tuple((source >> (4*r)) & 15 for r in range(6))
            distances = [sum(losses[x][a] for x, a in zip(blocks, word)) for word in self.book]
            expected = min(distances)
            self.assertEqual(codec.encode(blocks, diagnostics=True), (distances.index(expected), expected))

    def test_component_complete_single_replacement_screen_and_direct_spots(self):
        screen = self.data['component_all_single_word_replacements']
        self.assertEqual((screen['errors'], screen['maximum_gain'], screen['positive_gain_candidates']), (40514, 0, 0))
        self.assertEqual(screen['candidate_replacements'], 64*4096)
        upstream = json.loads((certificate.HERE.parent/'joint_coding_finite3/discovery.json').read_text(encoding='utf-8'))
        old = tuple(upstream['runs']['greedy']['codeword_ids'])
        positive_control = certificate.single_word_screen(old)
        self.assertEqual((positive_control['maximum_gain'], positive_control['selected']), (8, [44, 3888]))
        _, _, minima, _ = certificate.nearest(codec.BASE)
        rows = certificate.cost_rows()
        # Independently take all64 minima for replacement books, bypassing
        # the addition/removal formula. Include unchanged and extreme cases.
        for a, c in ((0, 0), (0, 4095), (2, 963), (15, 137), (38, 2698), (44, 3632), (63, 2048)):
            changed = list(codec.BASE)
            changed[a] = c
            new_error = sum(min(row[word] for word in changed) for row in rows)
            self.assertGreaterEqual(new_error, sum(minima))
        self.assertEqual(self.data['component']['actor_routes_executed'], 147456)
        self.assertEqual(self.data['unrestricted_three_block_interval_errors'], [40072, 40514])

    def test_local_component_product_has_an_improving_single_joint_word(self):
        row = self.data['product_locality_counterexample']
        self.assertEqual((row['parent_id'], row['replacement_left_triple']), (3330, 963))
        self.assertEqual((row['product_errors'], row['single_change_errors'], row['errors_avoided']),
                         (331890688, 331886587, 4101))
        changed = independent_book(codec.BASE, {3330: 963})
        product = independent_book(codec.BASE, {})
        self.assertEqual([m for m in range(4096) if changed[m] != product[m]], [3330])
        self.assertEqual(changed[3330][3:], product[3330][3:])
        self.assertFalse(self.data['discovery']['final_single_word_locality_certified'])

    def test_group_factorization_and_lowest_parent_tie_order(self):
        columns, winners, minima, changed, groups, local = certificate.partition(codec.BASE, codec.OVERRIDES)
        self.assertEqual(changed, [52, 58])
        self.assertEqual(sum(map(len, groups.values())), 4096)
        self.assertEqual(len(groups), 16)
        # Every left source against32 declared right diagnostics, separately
        # reconstruct each low-digit choice from all64 words. This checks the
        # factorization and tie rule used to cover the remaining population.
        ys = list(range(16)) + [4095-17*t for t in range(16)]
        for key, xs in groups.items():
            offsets = dict(zip(changed, key))
            expected_bs = []
            for y in ys:
                scores = [d + offsets.get(b, 0) for b, d in enumerate(columns[y])]
                expected_bs.append(scores.index(min(scores)))
            for x in xs:
                for y, b in zip(ys, expected_bs):
                    scores = [local[x][0].get(i, minima[x]) + columns[y][i] for i in range(64)]
                    self.assertEqual(scores.index(min(scores)), b)
                for b in changed:
                    left_distances = [certificate.cost_rows()[x][codec.OVERRIDES.get(a+64*b, codec.BASE[a])]
                                      for a in range(64)]
                    self.assertEqual(local[x][1][b], left_distances.index(min(left_distances)))
                self.assertEqual(columns[x].index(min(columns[x])), winners[x])

    def test_weighted_actor_population_and_stronger_common_length_control(self):
        six = self.data['six_block']
        self.assertEqual((six['errors'], six['outcomes']), (331857648, 1207959552))
        self.assertEqual(six['source_pairs_covered'], 16**6)
        self.assertEqual(sum(six['message_occupancies']), 16**6)
        self.assertEqual(sum(map(sum, six['branch_errors'])), six['errors'])
        self.assertEqual(six['weighted_actor_outcomes'], six['outcomes'])
        self.assertLess(six['physical_actor_query_calls'], six['outcomes'])
        self.assertFalse(six['all_outcomes_executed_individually'])
        common = self.data['common_length12_product_control']
        self.assertTrue(common['six_block_product_wins'])
        self.assertEqual(Fraction(common['six_block_product_errors'], common['outcomes']),
                         Fraction(six['errors'], six['outcomes']))
        self.assertEqual(Fraction(common['refined_three_block_product_errors'], common['outcomes']),
                         Fraction(40514, 147456))
        self.assertEqual(self.data['errors_avoided_against_refined_product'], 33040)

    def test_public_label_payload_and_information_access_boundaries(self):
        payload = codec.pack_tables()
        self.assertEqual(len(payload), 120)
        self.assertEqual(codec.unpack_tables(payload, 8), (codec.BASE, codec.OVERRIDES))
        self.assertEqual(list(inspect.signature(codec.update).parameters), ['message','block','omitted','base','overrides'])
        self.assertEqual(list(inspect.signature(codec.predict).parameters), ['child','block','omitted','query'])
        for m in (-1, 4096, True):
            with self.assertRaises(ValueError):
                codec.update(m, 0, 0)
        for child in (-1, 2, True):
            with self.assertRaises(ValueError):
                codec.predict(child, 0, 0, 1)
        for source in ((0,)*5, (16,)*6, (True,)*6):
            with self.assertRaises(ValueError):
                codec.encode(source)
        with self.assertRaises(TypeError):
            codec.update(0, 0, 0, query=1)
        with self.assertRaises(TypeError):
            codec.predict(0, 0, 0, 1, parent=0)

    def test_product_segments_without_extra_instance_state_and_failed_search_provenance(self):
        for k in (6, 12, 18):
            for seed in range(12):
                blocks = tuple((seed*7+r*11+r//3) % 16 for r in range(k))
                m, error = codec.encode_segments(blocks, diagnostics=True)
                components = [codec.encode(blocks[start:start+6], diagnostics=True) for start in range(0, k, 6)]
                self.assertEqual(m, sum(n << (12*i) for i, (n, _) in enumerate(components)))
                self.assertLess(m, 1 << (2*k))
                self.assertEqual(error, sum(e for _, e in components))
                actor_error = 0
                for r in range(k):
                    for o in range(4):
                        z = codec.update_segments(m, r, o, k)
                        for j in range(4):
                            if o != j:
                                actor_error += codec.predict(z, r, o, j) != ((blocks[r] >> j) & 1)
                self.assertEqual(actor_error, error)
        audit = self.data['discovery']
        self.assertEqual([r['gain'] for r in audit['component_steps']], [8,2,2,3,0])
        self.assertEqual(len(audit['failed_initial_modal_starts']), 4)
        self.assertEqual(len(audit['conditional_steps']), 8)
        self.assertTrue(audit['accepted_errors_and_gains_independently_recomputed'])
        self.assertFalse(audit['native_rejected_candidate_scores_independently_recomputed'])
        self.assertEqual((self.data['new_model_calls'], self.data['new_natural_episodes']), (0,0))
        if certificate.OUTPUT.exists():
            saved = json.loads(certificate.OUTPUT.read_text(encoding='utf-8'))
            self.assertEqual(saved, self.data)


if __name__ == '__main__':
    unittest.main()
