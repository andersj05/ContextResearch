"""Independent endpoint routes, tied ideals, finite counts and cover ingredients."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import heapq
from itertools import product
import json
import unittest

from experiments.dependency_memory.joint_coding_general import audit, cover
from experiments.dependency_memory.joint_coding_finite3 import witness


def direct_loss(source, decision, table):
    bits = list(reversed(f"{source:04b}"))
    actions = list(reversed(f"{decision:04b}"))
    errors = 0
    for omitted, pair_index in enumerate(table):
        word = cover.frontier.PAIRS[pair_index][int(actions[omitted])]
        predictions = list(reversed(f"{word:03b}"))
        for prediction, j in zip(predictions, (j for j in range(4) if j != omitted)):
            errors += prediction != bits[j]
    return errors


@lru_cache(None)
def direct_reward(profiles):
    arrays = [tuple(score for score, count in profile for _ in range(count)) for profile in profiles]
    return sum(max(a+b+c, 0) for a, b, c in product(*arrays))


class GeneralCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.discovery = json.loads(cover.DISCOVERY.read_text(encoding="utf-8"))
        cls.selected = cls.discovery["selected_cases"]

    def test_all_pair_oracles_and_orbit_census_against_branch_polynomial(self):
        pair_counts = Counter()
        for a, b in cover.frontier.PAIRS:
            nearest = sum(min((x ^ a).bit_count(), (x ^ b).bit_count()) for x in range(8))*2
            d = 3 if a == b else int(a ^ b != 7)
            self.assertEqual(nearest, 12+4*d)
            pair_counts[d] += 1
        self.assertEqual(pair_counts, {0: 4, 1: 24, 3: 8})
        expected = Counter({0: 1})
        for _ in range(4):
            updated = Counter()
            for a, n in expected.items():
                for b, m in pair_counts.items():
                    updated[a+b] += n*m
            expected = updated
        actual = cover.census()
        self.assertEqual(actual["table_counts"], dict(sorted(expected.items())))
        self.assertEqual([len(g) for g in actual["groups"]], [6, 24, 170, 642])
        self.assertEqual(len(list(cover.near_cases(True))), 46492)
        self.assertEqual(len(list(cover.near_cases())), 46436)
        self.assertEqual((144+4*4)*256, 40960)

    def test_every_near_one_block_route_and_exact_loss_function_identification(self):
        for group in cover.census()["groups"]:
            for index, table, _ in group:
                direct = [[direct_loss(x, a, table) for a in range(16)] for x in range(16)]
                self.assertEqual(direct, [list(row) for row in cover.frontier.loss_matrix(table)])
                functions = {tuple(row[a] for row in direct) for a in range(16)}
                self.assertEqual(functions, set(cover.block(index, 0)["columns"]))
                self.assertTrue(all(sum(column) == 96 for column in functions))
                self.assertEqual(sum(min(row) for row in direct), 48+4*cover.defect(table))

    def test_binary_reward_identity_on_all_score_basis_triples(self):
        # Both sides are multilinear in source-score multiplicities. Checking
        # every score basis triple establishes the coefficients independently.
        for scores in product((-100, -4, 0, 4), repeat=3):
            profiles = tuple(sorted((((score, 1),) for score in scores)))
            self.assertEqual(cover.reward(profiles, True), max(sum(scores), 0))
        weighted = (((-100, 3), (-4, 2), (0, 7), (4, 4)),
                    ((-100, 1), (-4, 4), (0, 8), (4, 3)),
                    ((-100, 6), (-4, 1), (0, 4), (4, 5)))
        self.assertEqual(cover.reward(tuple(sorted(weighted)), True), direct_reward(tuple(sorted(weighted))))

    def test_every_quarter_unit_case_by_direct_source_triple_sums(self):
        direct_reward.cache_clear()
        for selected in self.discovery["quarter_unit_rows"]:
            blocks = [cover.block(i, t) for i, t in zip(selected[:3], selected[3:6])]
            independent = []
            for row in blocks:
                table = cover.frontier.decode_table(row["index"])
                loss = [[direct_loss(x, a, table) for a in range(16)] for x in range(16)]
                columns = sorted({tuple(r[a] for r in loss) for a in range(16)})
                oracle = [min(r) for r in loss]
                target = cover.unpack_target(cover.pack_target(row["target"]))
                independent.append([(tuple(sorted(Counter(t-4*(v-u) for t, v, u in zip(target, col, oracle)).items())),
                                     sum(t == 0 and v == u for t, v, u in zip(target, col, oracle))) for col in columns])
            weights = []
            for a, b, c in product(*independent):
                profiles = tuple(sorted((a[0], b[0], c[0])))
                weights.append(direct_reward(profiles)+4*a[1]*b[1]*c[1])
            checked = cover.bound(blocks)
            self.assertEqual(dict(Counter(weights)), checked["column_weight_histogram_units"])
            self.assertEqual(sum(heapq.nlargest(64, weights)), checked["largest_64_column_sum_units"])
            self.assertEqual(checked["integer_lower_errors"], selected[6])
            self.assertGreaterEqual(selected[6], 40072)
        self.assertEqual(len(self.discovery["quarter_unit_rows"]), 39)
        print(f"Independent quarter-unit source sums: {direct_reward.cache_info().currsize} score-multiset triples.")

    def test_tied_ideal_union_inequality_source_by_source(self):
        books = (witness.selected_book(), ((0, 0, 0),), tuple(product((0, 15), repeat=3)),
                 ((0, 0, 0), (0, 0, 4)))
        chosen = [r for r in self.discovery["quarter_unit_rows"] if r[2] in (144121, 149225)]
        self.assertEqual({r[2] for r in chosen}, {144121, 149225})
        overlaps = misses = 0
        for selected in chosen:
            for targets in (selected[3:6], (0, 0, 0)):
                blocks = [cover.block(i, t) for i, t in zip(selected[:3], targets)]
                original = [cover.frontier.loss_matrix(row["table"]) for row in blocks]
                for book in books:
                    for source in product(range(16), repeat=3):
                        oracle = sum(row["oracle"][x] for row, x in zip(blocks, source))
                        target = sum(row["target"][x] for row, x in zip(blocks, source))
                        costs = [sum(loss[x][a] for loss, x, a in zip(original, source, word)) for word in book]
                        actual = min(costs)
                        saving = sum(max(target-4*(cost-oracle), 0) for cost in costs)
                        incidence = sum(cost == oracle for cost in costs)
                        correction = 4*(1-incidence) if target == 0 else 0
                        self.assertGreaterEqual(4*actual, 4*oracle+target-saving+correction)
                        overlaps += int(target == 0 and incidence > 1)
                        misses += int(target == 0 and incidence == 0)
        self.assertGreater(overlaps, 0)
        self.assertGreater(misses, 0)

    def test_saved_all_decoder_certificate_and_invalid_target_shapes(self):
        fresh = cover.certificate()
        saved = json.loads(cover.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(saved, json.loads(json.dumps(fresh)))
        self.assertTrue(fresh["covers_arbitrary_final_decoders"])
        self.assertEqual(Fraction(fresh["upper_errors"]-fresh["lower_errors"], fresh["outcomes"]), Fraction(457, 147456))
        for code in (-1, 2**20, True, 1.5, 16, 9):
            with self.assertRaises(ValueError):
                cover.unpack_target(code)
        for target in ((0,)*15, (-1,)*16, (True,)*16, (1, 2)+(0,)*14):
            with self.assertRaises(ValueError):
                cover.pack_target(target)
        for index in (-1, 36**4, True):
            with self.assertRaises(ValueError):
                cover.block(index, 0)

    def test_preserved_auxiliary_native_books_and_rational_duals(self):
        fresh = audit.certificate()
        saved = json.loads(audit.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(saved, fresh)
        self.assertEqual(fresh["native_outcomes_checked"], 1179648)
        self.assertTrue(all(not r["strict_improvement_over_incumbent"] for r in fresh["native_books"]))


if __name__ == "__main__":
    unittest.main()
