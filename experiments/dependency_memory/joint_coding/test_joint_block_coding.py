"""Independent outcome and rational-information checks for joint witnesses."""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
import unittest

from joint_coding import coding as joint


def direct_cost(source: int, decisions: int) -> int:
    # Intentionally avoid the generator's popcount/branch-cost formula.
    bits = [int(c) for c in f"{source:04b}"[::-1]]
    predictions = [int(c) for c in f"{decisions:04b}"[::-1]]
    return sum(bits[j] != predictions[o]
               for o in range(4) for j in range(4) if j != o)


def factor(number: int) -> Counter:
    result = Counter()
    divisor = 2
    while divisor * divisor <= number:
        while number % divisor == 0:
            result[divisor] += 1
            number //= divisor
        divisor += 1
    if number > 1:
        result[number] += 1
    return result


class JointBlockCodingTests(unittest.TestCase):
    def test_every_source_and_route_against_separate_formulation(self):
        table = joint.parent_table()
        total = 0
        columns = [0] * 16
        for y, x in product(range(16), repeat=2):
            costs = [direct_cost(x, a) + direct_cost(y, b)
                     for a, b in joint.CODEBOOK]
            chosen = table[x + 16 * y]
            self.assertEqual(chosen, costs.index(min(costs)))
            total += costs[chosen]
            columns[y] += costs[chosen]
        self.assertEqual(total, 1698)
        self.assertEqual(Fraction(total, 6144), Fraction(283, 1024))
        self.assertEqual(set(table), set(range(16)))
        self.assertEqual(joint.grade_table(table)["errors"], total)
        # A compact independent five-row certificate for the explicit code.
        by_weight = {0: 48, 1: 96, 2: 134, 3: 102, 4: 54}
        self.assertEqual(columns, [by_weight[y.bit_count()] for y in range(16)])

    def test_product_control(self):
        book = tuple(product((0, 1, 14, 15), repeat=2))
        error = sum(min(direct_cost(x, a) + direct_cost(y, b) for a, b in book)
                    for x, y in product(range(16), repeat=2))
        self.assertEqual(error, 1728)
        self.assertEqual(Fraction(error - 1698, 6144), Fraction(5, 1024))

    def test_permutation_and_complement_symmetries(self):
        # Different tie choices and labels must not change the best distortion.
        for book in (joint.CODEBOOK[::-1],
                     tuple((b, a) for a, b in joint.CODEBOOK),
                     tuple((a ^ 15, b ^ 15) for a, b in joint.CODEBOOK)):
            self.assertEqual(joint.grade_table(joint.parent_table(book), book)["errors"], 1698)

    def test_rational_channel_information_and_loss(self):
        channel = joint.test_channel()
        marginal = [sum(row[a] for row in channel) / 16 for a in range(8)]
        self.assertEqual(marginal, [Fraction(45, 128)]
                         + [Fraction(19, 384)] * 6 + [Fraction(45, 128)])
        loss = Fraction(0)
        log_coefficients = defaultdict(Fraction)
        for x, row in enumerate(channel):
            self.assertEqual(sum(row), 1)
            self.assertTrue(all(p >= 0 for p in row))
            for a, probability in enumerate(row):
                loss += probability * direct_cost(x, joint.SIGNATURES[a]) / 192
                if not probability:
                    continue
                ratio = probability / marginal[a]
                for prime, exponent in factor(ratio.numerator).items():
                    log_coefficients[prime] += probability * exponent / 16
                for prime, exponent in factor(ratio.denominator).items():
                    log_coefficients[prime] -= probability * exponent / 16
        self.assertEqual(loss, Fraction(101, 384))
        self.assertEqual({p: c for p, c in log_coefficients.items() if c},
                         {2: Fraction(371, 64), 3: Fraction(-95, 64),
                          5: Fraction(-40, 64)})
        self.assertLess(2**243, 5**40 * 3**95)

    def test_signature_fibers_and_isolated_loss(self):
        signatures = []
        for x in range(16):
            minimum = min(direct_cost(x, a) for a in range(16))
            choices = [a for a in range(16) if direct_cost(x, a) == minimum]
            self.assertEqual(len(choices), 1)
            self.assertEqual(joint.majority_signature(x), choices[0])
            signatures.extend(choices)
        self.assertEqual(sorted(Counter(signatures).values()), [1] * 6 + [5, 5])
        self.assertEqual(sum(direct_cost(x, signatures[x]) for x in range(16)), 48)

    def test_reject_overcapacity_and_invalid_messages(self):
        for book in ((), joint.CODEBOOK + ((2, 2),), ((0, 0), (0, 0)),
                     ((0, 16),), ((True, 0),)):
            with self.assertRaises(ValueError):
                joint.parent_table(book)
        for table in ([0] * 255, [16] * 256, [True] * 256):
            with self.assertRaises(ValueError):
                joint.grade_table(table)


if __name__ == "__main__":
    unittest.main()
