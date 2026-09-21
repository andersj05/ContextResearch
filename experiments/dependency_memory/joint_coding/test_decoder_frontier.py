"""Independent formulations of the decoder, symmetry, and interval checks."""

from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import permutations, product
from math import prod
import unittest

from joint_coding import coding
from joint_coding import decoder_frontier as frontier


def direct_loss(table, x, a):
    count = 0
    for o in range(4):
        prediction = frontier.PAIRS[table[o]][(a >> o) & 1]
        for position, query in enumerate(j for j in range(4) if j != o):
            count += ((prediction >> position) & 1) != ((x >> query) & 1)
    return count


def separate_pair_transform(pair, omitted, permutation, mask):
    """Use coordinate dictionaries, independently of the generator's bit packing."""
    outputs = []
    for endpoint in pair:
        bits = dict(zip((j for j in range(4) if j != omitted),
                        [int(c) for c in f"{endpoint:03b}"[::-1]]))
        moved = {permutation[j]: bit ^ ((mask >> permutation[j]) & 1)
                 for j, bit in bits.items()}
        outputs.append(sum(moved[j] << i for i, j in enumerate(sorted(moved))))
    return tuple(sorted(outputs))


class DecoderFrontierTests(unittest.TestCase):
    def test_loss_against_direct_routes(self):
        # Covers every branch pair, with varied other branches including repeats.
        for index in range(36):
            table = tuple((index + 7*o) % 36 for o in range(4))
            actual = frontier.loss_matrix(table)
            for x, a in product(range(16), repeat=2):
                self.assertEqual(actual[x][a], direct_loss(table, x, a))
        unsigned = frontier.loss_matrix(frontier.UNSIGNED)
        self.assertEqual(unsigned, tuple(tuple(coding.branch_cost(x, a) for a in range(16))
                                        for x in range(16)))

    def test_all_symmetry_actions_against_coordinate_dictionaries(self):
        index = 0
        maps = frontier.symmetry_maps()
        for permutation in permutations(range(4)):
            for mask in range(16):
                mapping = maps[index]
                for o, (new_o, pairs) in enumerate(mapping):
                    self.assertEqual(new_o, permutation[o])
                    self.assertEqual(sorted(pairs), list(range(36)))
                    for pair_id, pair in enumerate(frontier.PAIRS):
                        expected = separate_pair_transform(pair, o, permutation, mask)
                        self.assertEqual(frontier.PAIRS[pairs[pair_id]], expected)
                index += 1

    def test_orbit_count_by_independent_burnside_fixed_points(self):
        # No orbit enumeration. A branch cycle's starting pair must be fixed
        # after traversing the cycle; distinct cycles can choose independently.
        fixed_sum = 0
        for permutation in permutations(range(4)):
            for mask in range(16):
                remaining = set(range(4))
                fixed_tables = 1
                while remaining:
                    start = min(remaining)
                    cycle = [start]
                    while permutation[cycle[-1]] != start:
                        cycle.append(permutation[cycle[-1]])
                    remaining.difference_update(cycle)
                    choices = 0
                    for pair in frontier.PAIRS:
                        transformed = pair
                        for o in cycle:
                            transformed = separate_pair_transform(transformed, o, permutation, mask)
                        choices += transformed == pair
                    fixed_tables *= choices
                fixed_sum += fixed_tables
        self.assertEqual(fixed_sum, 384*4751)

    def test_symmetry_preserves_actual_prediction_loss(self):
        table = (3, 9, 16, 25)
        for permutation in permutations(range(4)):
            for mask in (0, 3, 5, 15):
                new_table = [None]*4
                switches = [False]*4
                for o in range(4):
                    pair = frontier.PAIRS[table[o]]
                    new_pair = separate_pair_transform(pair, o, permutation, mask)
                    new_table[permutation[o]] = frontier.PAIR_INDEX[new_pair]
                    first = separate_pair_transform((pair[0], pair[0]), o, permutation, mask)[0]
                    switches[o] = first != new_pair[0]
                old_loss = frontier.loss_matrix(table)
                new_loss = frontier.loss_matrix(tuple(new_table))
                for x, a in product(range(16), repeat=2):
                    moved_x = sum(((x >> j) & 1) << permutation[j] for j in range(4)) ^ mask
                    moved_a = sum((((a >> o) & 1) ^ switches[o]) << permutation[o] for o in range(4))
                    self.assertEqual(old_loss[x][a], new_loss[moved_x][moved_a])

    def test_log_intervals_against_separate_high_precision_library(self):
        ratios = [(1, 1), (1, 2), (2, 1), (3, 2), (17, 129),
                  (2**500+1, 2**1000+7), (2**192+1, 2**192),
                  (frontier.T.numerator, frontier.T.denominator)]
        with localcontext() as context:
            context.prec = 90
            for n, d in ratios:
                low, high = frontier.log2_bounds(n, d)
                expected = (Decimal(n)/Decimal(d)).ln()/Decimal(2).ln()
                as_decimal = lambda v: Decimal(v.numerator)/Decimal(v.denominator)
                self.assertLessEqual(as_decimal(low), expected)
                self.assertGreaterEqual(as_decimal(high), expected)
                self.assertLess(high-low, Fraction(1, 10**52))
        for power in range(-20, 21):
            n, d = (2**power, 1) if power >= 0 else (1, 2**-power)
            self.assertEqual(frontier.log2_bounds(n, d), (power, power))

    def test_dual_rounding_dominates_exact_fraction_formulation(self):
        for table in (frontier.UNSIGNED, (0, 9, 20, 35), (8, 12, 22, 30)):
            loss = frontier.loss_matrix(table)
            weights = frontier.nearest_weights(loss)
            self.assertEqual(sum(weights), 256)
            q = [Fraction(w, 256) for w in weights]
            values = [[frontier.T**l for l in row] for row in loss]
            z = [sum(qa*w for qa, w in zip(q, row)) for row in values]
            g = max(sum(values[x][a]/z[x] for x in range(16))/16 for a in range(16))
            exact_product = prod(z)*g**16
            n, d = frontier.dual_product(loss, weights)
            self.assertGreaterEqual(Fraction(n, d), exact_product)
            self.assertLess(Fraction(n, d)/exact_product-1, Fraction(1, 10**40))

    def test_gibbs_channel_from_direct_routes_and_actual_marginal(self):
        table = frontier.UNSIGNED
        q = [Fraction(w, sum(frontier.UNSIGNED_WEIGHTS)) for w in frontier.UNSIGNED_WEIGHTS]
        channel = []
        for x in range(16):
            row = [q[a]*frontier.T**direct_loss(table, x, a) for a in range(16)]
            row = [p/sum(row) for p in row]
            self.assertEqual(sum(row), 1)
            channel.append(row)
        distortion = sum(channel[x][a]*direct_loss(table, x, a)
                         for x, a in product(range(16), repeat=2))/192
        result = frontier.primal_bounds(frontier.loss_matrix(table), frontier.UNSIGNED_WEIGHTS)
        self.assertEqual(distortion, result["distortion"])
        self.assertLess(distortion, frontier.UPPER_TARGET)
        marginal = [sum(row[a] for row in channel)/16 for a in range(16)]
        # Independent information computation, avoiding the KL-to-q shortcut.
        with localcontext() as context:
            context.prec = 65
            def decimal(v):
                return Decimal(v.numerator)/Decimal(v.denominator)
            information = sum(decimal(p)*(decimal(p/marginal[a]).ln()/Decimal(2).ln())/16
                              for row in channel for a, p in enumerate(row) if p)
            self.assertLess(information, Decimal(2))
            self.assertLessEqual(information, decimal(result["information_upper"]))
            self.assertLess(decimal(result["information_upper"])-information, Decimal("1e-24"))

    def test_complete_decoder_certificate(self):
        result = frontier.certificate()
        self.assertEqual(result["decoder_orbits"], 4751)
        histogram = result["orbit_size_histogram"]
        self.assertEqual(sum(histogram.values()), 4751)
        self.assertEqual(sum(int(size)*count for size, count in histogram.items()), 36**4)
        self.assertEqual(result["worst_dual_orbit"]["size"], 8)
        self.assertEqual(result["certified_strict_interval"]["decimal"],
                         ["0.2618989799", "0.2618989801"])
        self.assertEqual(result["model_requests"], 0)

    def test_bound_compatible_with_independent_known_codes(self):
        for error in (Fraction(9, 32), Fraction(283, 1024), Fraction(101, 384)):
            self.assertGreater(error, frontier.UPPER_TARGET)
        self.assertGreater(frontier.LOWER_TARGET, Fraction(129, 512))
        self.assertGreater(frontier.LOWER_TARGET-Fraction(1, 4), 6*Fraction(1, 512))

    def test_reject_invalid_witness_parameters(self):
        for n, d in ((0, 1), (1, 0), (-1, 2), (True, 1)):
            with self.assertRaises(ValueError):
                frontier.log2_bounds(n, d)
        for table in ((0,), (0, 0, 0, 36), (True, 0, 0, 0)):
            with self.assertRaises(ValueError):
                frontier.loss_matrix(table)
        for t in (Fraction(0), Fraction(1), Fraction(2)):
            with self.assertRaises(ValueError):
                frontier.kernel(frontier.loss_matrix(frontier.UNSIGNED), t)
        for weights in ((0,)*16, (1,)*15, (-1,)+(1,)*15):
            with self.assertRaises(ValueError):
                frontier.dual_product(frontier.loss_matrix(frontier.UNSIGNED), weights)


if __name__ == "__main__":
    unittest.main()
