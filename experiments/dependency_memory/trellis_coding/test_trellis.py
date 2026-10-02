"""Independent local routing, enumeration and closed-path optimality checks."""
from itertools import product
import json
import unittest

from . import codec, certificate


def route_loss(source, decision):
    truth = list(reversed(f'{source:04b}'))
    answer = list(reversed(f'{decision:04b}'))
    return sum(truth[j] != answer[o] for o in range(4) for j in range(4) if o != j)


def independent_book(k, tables=codec.TABLES):
    # Enumerate symbol tuples and reorder by their separately packed integer.
    candidates = {}
    for symbols in product(range(4), repeat=k):
        message = sum(symbol << (2 * r) for r, symbol in enumerate(symbols))
        word = []
        for r in range(k):
            current, previous, before = symbols[r], symbols[(r - 1) % k], symbols[(r - 2) % k]
            ordered = ((current, before, previous), (previous, current, before), (before, previous, current))[r % 3]
            index = ordered[0] + 4 * ordered[1] + 16 * ordered[2]
            word.append(tables[r % 3][index])
        candidates[message] = tuple(word)
    return tuple(candidates[m] for m in range(4 ** k))


class TrellisTests(unittest.TestCase):
    def test_response_lookup_and_all_one_block_losses_against_bit_routes(self):
        for k in range(1, 5):
            self.assertEqual(codec.book(k), independent_book(k))
        for x in range(16):
            for a in range(16):
                self.assertEqual(codec.loss(x, a), route_loss(x, a))

    def test_every_one_two_three_block_source_matches_exhaustive_messages(self):
        costs = [[route_loss(x, a) for a in range(16)] for x in range(16)]
        for k in range(1, 4):
            book = independent_book(k)
            for blocks in product(range(16), repeat=k):
                values = [sum(costs[x][a] for x, a in zip(blocks, word)) for word in book]
                m, cost, transitions = codec.encode(blocks, diagnostics=True)
                self.assertEqual((m, cost), (values.index(min(values)), min(values)))
                self.assertEqual(transitions, 4 if k == 1 else 1024 * k)

    def test_four_six_block_diagnostics_and_long_closed_encoder(self):
        costs = [[route_loss(x, a) for a in range(16)] for x in range(16)]
        for k, n in ((4, 128), (6, 24)):
            book = independent_book(k)
            sources = {sum(a << (4 * r) for r in range(k)) for a in range(16)}
            state = 68429
            for _ in range(n):
                state = (1664525 * state + 1013904223) & 0xffffffff
                sources.add(state % (16 ** k))
            for source in sorted(sources):
                blocks = tuple(int(f'{source:0{4*k}b}'[4*k-4*r-4:4*k-4*r], 2) for r in range(k))
                values = [sum(costs[x][a] for x, a in zip(blocks, word)) for word in book]
                m, cost, transitions = codec.encode(blocks, diagnostics=True)
                self.assertEqual((m, cost), (values.index(min(values)), min(values)))
                self.assertEqual(transitions, 1024 * k)
        blocks = tuple((r * 7 + 3) % 16 for r in range(32))
        m, cost, transitions = codec.encode(blocks, diagnostics=True)
        self.assertLess(m, 1 << 64)
        self.assertEqual(cost, sum(route_loss(x, codec.decision_word(m, r, 32)) for r, x in enumerate(blocks)))
        self.assertEqual(transitions, 32768)
        for control in (0, (1 << 64) - 1, sum((r % 4) << (2 * r) for r in range(32))):
            self.assertLessEqual(cost, sum(route_loss(x, codec.decision_word(control, r, 32)) for r, x in enumerate(blocks)))

    def test_selected_population_and_product_controls(self):
        book = independent_book(4)
        parents, values = certificate.nearest_parents(book)
        result = certificate.grade(parents, 4)
        self.assertEqual(sum(values), 867837)
        self.assertEqual(result['errors'], 867837)
        self.assertEqual(result['outcomes'], 3145728)
        self.assertEqual(certificate.controls()['pair_product'], 869376)
        self.assertEqual(certificate.controls()['three_plus_one'], 869648)
        self.assertEqual(certificate.controls()['four_independent_blocks'], 884736)
        common = certificate.controls()['common_length_twelve']
        from fractions import Fraction
        self.assertEqual(Fraction(common['four_block_product_errors'], common['outcomes']), Fraction(867837, 3145728))
        self.assertEqual(Fraction(common['existing_three_block_product_errors'], common['outcomes']), Fraction(40529, 147456))
        self.assertTrue(common['existing_three_block_product_wins'])
        self.assertEqual((common['parent_bits'], common['child_bits']), (24, 1))

    def test_pre_tuning_three_block_identity_and_failed_initial_search(self):
        rows = [json.loads(line) for line in (certificate.DISCOVERY / 'initial.jsonl').read_text().splitlines()]
        old = certificate.selected_book()
        for row in (rows[0], rows[11]):
            labels = tuple(tuple(old[index][phase] for index in row['permutation']) for phase in range(3))
            self.assertEqual(independent_book(3, labels), tuple(old[index] for index in row['permutation']))
            _, values = certificate.nearest_parents(independent_book(4, labels))
            self.assertEqual(sum(values), row['errors'])
            self.assertGreater(sum(values), 869376)
        audit = certificate.discovery_audit()
        self.assertEqual([row['moves'] for row in audit['passes']], [54, 15, 15, 9])
        self.assertFalse(audit['local_optimum_certified'])

    def test_no_extra_start_state_and_child_formed_before_query(self):
        for m in range(256):
            for block in range(4):
                decisions = codec.decision_word(m, block, 4)
                for omitted in range(4):
                    child = codec.update(m, block, omitted, 4)
                    self.assertEqual(child, (decisions >> omitted) & 1)
                    self.assertIn(child, (0, 1))
                    self.assertEqual([codec.predict(child, block, omitted, j) for j in range(4) if j != omitted], [child] * 3)
        for blocks in ((0,) * 4, (15,) * 4, (3, 5, 9, 6)):
            m = codec.encode(blocks)
            stored_symbols = tuple((m >> (2 * r)) & 3 for r in range(4))
            self.assertEqual(tuple(codec.decision_word(m, r, 4) for r in range(4)), independent_book(4)[m])
            self.assertEqual((m >> 4) & 15, stored_symbols[-2] + 4 * stored_symbols[-1])

    def test_public_label_packing_and_memory_contract_rejections(self):
        payload = codec.pack_tables()
        self.assertEqual(len(payload), 96)
        self.assertEqual(codec.unpack_tables(payload), codec.TABLES)
        for blocks in ((), (16,), (True,), (-1,)):
            with self.assertRaises(ValueError):
                codec.encode(blocks)
        for m in (-1, 256, True):
            with self.assertRaises(ValueError):
                codec.update(m, 0, 0, 4)
        with self.assertRaises(ValueError):
            codec.predict(0, 0, 0, 0)
        with self.assertRaises(ValueError):
            codec.predict(2, 0, 0, 1)
        with self.assertRaises(TypeError):
            codec.update(0, 0, 0, 4, query=1)
        with self.assertRaises(TypeError):
            codec.predict(0, 0, 0, 1, message=0)

    def test_four_block_segment_product_has_no_group_state_overhead(self):
        book = independent_book(4)
        costs = [[route_loss(x, a) for a in range(16)] for x in range(16)]
        for k in (4, 8, 12):
            for seed in range(32):
                blocks = tuple((seed * 5 + r * 11 + r // 3) % 16 for r in range(k))
                message, error, transitions = codec.encode_segments(blocks, diagnostics=True)
                values, expected_messages = [], []
                for start in range(0, k, 4):
                    alternatives = [sum(costs[x][a] for x, a in zip(blocks[start:start + 4], word)) for word in book]
                    values.append(min(alternatives))
                    expected_messages.append(alternatives.index(min(alternatives)))
                self.assertEqual(message, int.from_bytes(bytes(expected_messages), 'little'))
                self.assertLess(message, 1 << (2 * k))
                self.assertEqual(error, sum(values))
                self.assertEqual(transitions, 1024 * k)
                route_errors = 0
                for block in range(k):
                    for omitted in range(4):
                        child = codec.update_segments(message, block, omitted, k)
                        self.assertEqual(child, codec.update(expected_messages[block // 4], block % 4, omitted, 4))
                        for query in range(4):
                            if query != omitted:
                                answer = codec.predict(child, block, omitted, query)
                                route_errors += answer != ((blocks[block] >> query) & 1)
                self.assertEqual(route_errors, error)
        with self.assertRaises(ValueError):
            codec.encode_segments((0,) * 5)
        with self.assertRaises(ValueError):
            codec.update_segments(1 << 16, 0, 0, 8)


if __name__ == '__main__':
    unittest.main()
