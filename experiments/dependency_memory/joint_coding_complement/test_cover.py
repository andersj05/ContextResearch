"""Independent routes, symmetries, direct source sums and scope checks."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import heapq
from itertools import permutations, product
import json
import unittest

from experiments.dependency_memory.joint_coding_complement import cover
from experiments.dependency_memory.joint_coding_finite3 import witness


def direct_loss(source, decision, table):
    bits = list(reversed(f"{source:04b}"))
    actions = list(reversed(f"{decision:04b}"))
    errors = 0
    for omitted, index in enumerate(table):
        endpoint = cover.frontier.PAIRS[index][int(actions[omitted])]
        predictions = list(reversed(f"{endpoint:03b}"))
        for prediction, j in zip(predictions, (j for j in range(4) if j != omitted)):
            errors += prediction != bits[j]
    return errors


def independent_orbit(table):
    result = set()
    for permutation in permutations(range(4)):
        for flips in product((0, 1), repeat=4):
            transformed = [None] * 4
            for omitted, index in enumerate(table):
                new_o = permutation[omitted]
                endpoints = []
                for endpoint in cover.frontier.PAIRS[index]:
                    bits = list(reversed(f"{endpoint:03b}"))
                    positions = {permutation[j]: int(bit) ^ flips[permutation[j]]
                                 for bit, j in zip(bits, (j for j in range(4) if j != omitted))}
                    value = 0
                    for i, j in enumerate(j for j in range(4) if j != new_o):
                        value += positions[j] * 2**i
                    endpoints.append(value)
                transformed[new_o] = cover.frontier.PAIRS.index(tuple(sorted(endpoints)))
            result.add(tuple(transformed))
    return result


@lru_cache(None)
def direct_reward(sorted_score_triple):
    # Every distinct combination is checked by explicit source triple iteration;
    # caching equal sorted score multisets does not use histogram convolution.
    return sum(max(a + b + c, 0) for a, b, c in product(*sorted_score_triple))


class ComplementaryCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = cover.certificate()
        cls.tables = [table for table, _ in cover.orbits()]
        cls.losses = [[[direct_loss(x, a, table) for a in range(16)] for x in range(16)]
                      for table in cls.tables]

    def test_every_one_block_route_and_unique_oracle(self):
        for table, loss in zip(self.tables, self.losses):
            self.assertEqual(loss, [list(row) for row in cover.frontier.loss_matrix(table)])
            self.assertEqual(sum(min(row) for row in loss), 48)
            self.assertTrue(all(row.count(min(row)) == 1 for row in loss))
        profiles = [Counter(Counter(min(range(16), key=lambda a: row[a]) for row in loss).values())
                    for loss in self.losses]
        self.assertEqual(profiles, [{5: 2, 1: 6}, {3: 2, 2: 2, 1: 6}, {2: 8},
                                    {2: 4, 1: 8}, {3: 4, 1: 4}, {1: 16}])

    def test_independent_symmetry_partition_covers_all_complementary_tables(self):
        seen = set()
        for table, members in cover.orbits():
            fresh = independent_orbit(table)
            self.assertEqual(fresh, set(members))
            self.assertFalse(seen.intersection(fresh))
            seen.update(fresh)
        complementary = [cover.frontier.PAIRS.index((a, 7-a)) for a in range(4)]
        self.assertEqual(seen, set(product(complementary, repeat=4)))
        self.assertEqual([len(m) for _, m in cover.orbits()], [8, 96, 24, 96, 24, 8])

    def test_all_56_cover_cases_by_direct_source_sums_and_expanded_top_columns(self):
        columns = 0
        for row in self.data["cases"]:
            losses = [self.losses[i] for i in row["types"]]
            score_arrays, zeros = [], []
            for loss, target in zip(losses, row["targets_units"]):
                ideal = [min(range(16), key=lambda a: r[a]) for r in loss]
                zero = Counter(ideal[x] for x in range(16) if target[x] == 0)
                score_arrays.append([tuple(sorted(target[x] - 4*(loss[x][a] - min(loss[x]))
                                                  for x in range(16))) for a in range(16)])
                zeros.append([zero[a] for a in range(16)])
            weights = []
            for a, b, c in product(range(16), repeat=3):
                profiles = tuple(sorted((score_arrays[0][a], score_arrays[1][b], score_arrays[2][c])))
                weights.append(direct_reward(profiles) + 4*zeros[0][a]*zeros[1][b]*zeros[2][c])
            histogram = {int(k): v for k, v in row["column_weight_histogram_units"].items()}
            self.assertEqual(dict(Counter(weights)), histogram)
            top = sum(heapq.nlargest(64, weights))
            self.assertEqual(top, row["largest_64_column_sum_units"])
            zero_mass = sum(1 for x, y, z in product(range(16), repeat=3)
                            if row["targets_units"][0][x] == row["targets_units"][1][y] == row["targets_units"][2][z] == 0)
            lower = 4*36864 + sum(sum(t) for t in row["targets_units"])*256 + 4*zero_mass - top
            self.assertEqual(lower, row["lower_error_units"])
            self.assertGreaterEqual(Fraction(lower, 4), 40072)
            columns += len(weights)
        self.assertEqual(columns, 229376)
        saved = json.loads(cover.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(saved, json.loads(json.dumps(self.data)))
        print(f"Independent source sums: {direct_reward.cache_info().currsize} score-multiset triples; {columns} decision columns.")

    def test_per_source_inequality_and_missing_center_correction(self):
        book = witness.selected_book()
        for types in ((0, 0, 0), (0, 0, 4), (5, 5, 5)):
            row = next(r for r in self.data["cases"] if tuple(r["types"]) == types)
            losses = [self.losses[i] for i in types]
            total = 0
            for source in product(range(16), repeat=3):
                oracle = sum(min(loss[x]) for x, loss in zip(source, losses))
                target = sum(t[x] for x, t in zip(source, row["targets_units"]))
                ideal = tuple(min(range(16), key=lambda a: loss[x][a]) for x, loss in zip(source, losses))
                costs = [sum(loss[x][a] for x, a, loss in zip(source, word, losses)) for word in book]
                actual = min(costs)
                reward_sum = sum(max(target - 4*(cost - oracle), 0) for cost in costs)
                missing = target == 0 and ideal not in book
                self.assertGreaterEqual(4*actual, 4*oracle + target - reward_sum + 4*int(missing))
                total += actual
            self.assertGreaterEqual(total, row["integer_lower_errors"])

    def test_coordinate_dependent_pairs_admitted_noncomplementary_rejected(self):
        coordinate_table = (7, 7, 13, 22)
        self.assertEqual(cover.lower_bound([coordinate_table]*3), Fraction(5009, 18432))
        with self.assertRaisesRegex(ValueError, "Noncomplementary"):
            cover.lower_bound([(0, 7, 7, 7)]*3)
        for targets in ((0,)*15, (-1,)*16, (True,)*16):
            with self.assertRaises(ValueError):
                cover.block((7,)*4, targets)
        with self.assertRaises(ValueError):
            cover.lower_bound([(7,)*4]*2)


if __name__ == "__main__":
    unittest.main()
