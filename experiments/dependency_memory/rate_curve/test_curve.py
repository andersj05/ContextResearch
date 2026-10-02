"""Independent routes, algebra, large coefficients and coding-slack checks."""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
import json
from math import comb, gcd, prod
from random import Random
import unittest

from experiments.dependency_memory.rate_curve import comparison as c, polynomials as p
from experiments.dependency_memory.rate_curve import certificate as cert
from experiments.dependency_memory.joint_coding import decoder_frontier as frontier
from experiments.dependency_memory.rate_spectrum import derive


def route_loss(table, x, a):
    errors = 0
    for omitted in range(4):
        endpoints = frontier.PAIRS[table[omitted]]
        prediction = endpoints[(a>>omitted)&1]
        coordinates = [j for j in range(4) if j != omitted]
        for position, j in enumerate(coordinates):
            errors += ((prediction>>position)&1) != ((x>>j)&1)
    return errors


def naive_multiply(left, right):
    result = [0]*(len(left)+len(right)-1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            result[i+j] += x*y
    return p.trim(result)


def rational_eval(coefficients, value):
    # Independent power sum, rather than the production Horner evaluator.
    return sum(c*value**i for i, c in enumerate(coefficients))


def transformed_coefficient(coefficients, low, high, j):
    n = len(coefficients)-1
    denominator = low.denominator*high.denominator//gcd(low.denominator,high.denominator)
    a, b = int(low*denominator), int(high*denominator)
    powers_a = [a**i for i in range(n+1)]
    powers_b = [b**i for i in range(n+1)]
    powers_d = [denominator**i for i in range(n+1)]
    result = 0
    for i, coefficient in enumerate(coefficients):
        subtotal = sum(comb(i,h)*powers_a[i-h]*powers_b[h]*comb(n-i,j-h)
                       for h in range(max(0,j-(n-i)),min(i,j)+1))
        result += coefficient*powers_d[n-i]*subtotal
    return result


def decimal_value(value):
    return Decimal(value.numerator)/Decimal(value.denominator)


def information_and_error(channel, table):
    marginal = [sum(row[a] for row in channel)/16 for a in range(16)]
    information = Decimal(0)
    error = F(0)
    for x, a in product(range(16),repeat=2):
        probability = channel[x][a]
        error += probability*route_loss(table,x,a)/192
        if probability:
            information += decimal_value(probability)/16*decimal_value(probability/marginal[a]).ln()/Decimal(2).ln()
    return information, error, marginal


class CurveTests(unittest.TestCase):
    def test_signed_kronecker_products_match_naive_convolution(self):
        rng = Random(6702)
        for n in (1,2,4,11,24,65,100):
            left = tuple(rng.randrange(-(1<<180),1<<180) for _ in range(n))+(0,)
            right = tuple(rng.randrange(-(1<<110),1<<110) for _ in range(n+2))
            self.assertEqual(p.multiply(left,right),naive_multiply(left,right))
            self.assertEqual(p.multiply(left,(0,)),(0,))
        factor = (3,-5,0,7)
        direct = (1,)
        for exponent in range(17):
            self.assertEqual(p.power(factor,exponent),direct)
            direct = naive_multiply(direct,factor)

    def test_interval_transform_has_independent_binomial_coefficients(self):
        rng = Random(6703)
        for n in range(1,13):
            coefficients = tuple(rng.randrange(-40,41) for _ in range(n))+(0 if n%2 else 7,)
            for low, high, _ in c.WITNESSES:
                actual = p.interval_coefficients(coefficients,low,high)
                expected = tuple(transformed_coefficient(coefficients,low,high,j) for j in range(n+1))
                self.assertEqual(actual,expected)
        # Check a central coefficient at the actual maximum degree, where the
        # recurrence combines hundreds of large signed coefficients.
        case = next(row for row in c.cases() if row['family']==1 and row['interval']==1)
        j = (len(case['polynomial'])-1)//2
        actual = p.interval_coefficients(case['polynomial'],case['low'],case['high'])
        self.assertEqual(actual[j],transformed_coefficient(case['polynomial'],case['low'],case['high'],j))

    def test_cleared_dual_products_match_direct_query_routes(self):
        for case in c.cases():
            table, weights = case['table'], case['weights']
            for t in (F(1,7),F(5,7)):
                z = [sum(w*t**route_loss(table,x,a) for a,w in enumerate(weights))/sum(weights)
                     for x in range(16)]
                word = case['words'][0]
                gamma = sum(t**route_loss(table,x,word)/z[x] for x in range(16))/16
                actual_g = prod(z)*gamma**16
                uq = case['unsigned_weights']
                actual_h = prod(sum(w*t**route_loss(frontier.UNSIGNED,x,a) for a,w in enumerate(uq))/sum(uq)
                                for x in range(16))
                denominator = rational_eval(case['denominator'],t)
                k = rational_eval(case['raw'],t)
                self.assertEqual(actual_h-actual_g,t**48*k/(16**16*denominator*sum(uq)**16))
                # Every grouped column has the same actual gradient; this
                # includes columns carrying zero mass in the witness q.
                for other in case['words']:
                    direct = sum(t**route_loss(table,x,other)/z[x] for x in range(16))/16
                    self.assertEqual(direct,gamma)

    def test_exact_one_factors_and_closed_interval_seams(self):
        for case in c.cases():
            coefficients, roots = case['polynomial'], case['roots_at_one']
            factor = tuple((-1)**i*comb(roots,i) for i in range(roots+1))
            reconstructed = naive_multiply(tuple(case['content']*v for v in coefficients),factor)
            self.assertEqual(reconstructed,case['raw'])
            transformed = p.interval_coefficients(coefficients,case['low'],case['high'])
            self.assertTrue(all(v>=0 for v in transformed))
            self.assertGreater(transformed[0],0)
            self.assertGreater(transformed[-1],0)
            for v in (F(1,3),F(2)):
                n = len(coefficients)-1
                low, high = case['low'], case['high']
                denominator = low.denominator*high.denominator//gcd(low.denominator,high.denominator)
                t = (low+high*v)/(1+v)
                self.assertEqual(rational_eval(transformed,v),denominator**n*(1+v)**n*rational_eval(coefficients,t))

    def test_family_interval_cover_retains_every_inactive_word(self):
        covered = {}
        for case in c.cases():
            key = case['family'], case['interval']
            already = covered.setdefault(key,set())
            self.assertFalse(already.intersection(case['words']))
            already.update(case['words'])
            self.assertEqual(sum(case['weights']),sum(frontier.nearest_weights(frontier.loss_matrix(case['table'])))
                             //gcd(*frontier.nearest_weights(frontier.loss_matrix(case['table']))))
        self.assertEqual(len(covered),15)
        self.assertTrue(all(words==set(range(16)) for words in covered.values()))
        self.assertEqual([(str(low),str(high)) for low,high,_ in c.WITNESSES],
                         [('0','4/25'),('4/25','1/4'),('1/4','1')])
        self.assertTrue(any(case['weights'][word]==0 for case in c.cases() for word in case['words']))

    def test_gibbs_marginal_and_strict_rate_slack_on_actual_channels(self):
        with localcontext() as ctx:
            ctx.prec = 65
            previous_information, previous_error = None, None
            for t in (F(1,100),F(3,20),F(1,4),F(2,5),F(4,5),F(19,20)):
                low,high = derive.balanced_mass_bracket(t)
                balanced = (low+high)/2
                q = [(1-balanced)/2 if a in (0,15) else balanced/6 if a.bit_count()==2 else F(0)
                     for a in range(16)]
                partitions = [sum(q[a]*t**route_loss(frontier.UNSIGNED,x,a) for a in range(16)) for x in range(16)]
                channel = [[q[a]*t**route_loss(frontier.UNSIGNED,x,a)/partitions[x] for a in range(16)]
                           for x in range(16)]
                self.assertTrue(all(sum(row)==1 for row in channel))
                information,error,marginal = information_and_error(channel,frontier.UNSIGNED)
                self.assertTrue(all(abs(decimal_value(a-b))<Decimal('1e-25') for a,b in zip(q,marginal)))
                free = -sum(decimal_value(z).ln()/Decimal(2).ln() for z in partitions)/16
                cross_info = free+12*decimal_value(error)*decimal_value(t).ln()/Decimal(2).ln()
                self.assertLess(abs(information-cross_info),Decimal('1e-25'))
                mixed = [[F(15,16)*value+F(1,16)*int(a==0) for a,value in enumerate(row)] for row in channel]
                mixed_information,mixed_error,_ = information_and_error(mixed,frontier.UNSIGNED)
                self.assertLess(mixed_information,information)
                self.assertLessEqual(mixed_information,F(15,16).numerator*information/F(15,16).denominator)
                self.assertEqual(mixed_error,F(15,16)*error+F(1,32))
                if previous_information is not None:
                    self.assertLess(information,previous_information)
                    self.assertGreater(error,previous_error)
                previous_information,previous_error = information,error

    def test_zero_rate_and_oracle_endpoints_have_actual_information_and_loss(self):
        with localcontext() as ctx:
            ctx.prec = 65
            zero = [[F(int(a==0)) for a in range(16)] for x in range(16)]
            information,error,_ = information_and_error(zero,frontier.UNSIGNED)
            self.assertEqual((information,error),(Decimal(0),F(1,2)))
            words = [min(range(16),key=lambda a:route_loss(frontier.UNSIGNED,x,a)) for x in range(16)]
            self.assertTrue(all(sum(route_loss(frontier.UNSIGNED,x,a)==route_loss(frontier.UNSIGNED,x,word)
                                    for a in range(16))==1 for x,word in enumerate(words)))
            frequencies = Counter(words)
            self.assertEqual(sorted(frequencies.values()),[1]*6+[5]*2)
            oracle = [[F(int(a==word)) for a in range(16)] for word in words]
            information,error,_ = information_and_error(oracle,frontier.UNSIGNED)
            h = Decimal(4)-Decimal(5)/8*Decimal(5).ln()/Decimal(2).ln()
            self.assertLess(abs(information-h),Decimal('1e-60'))
            self.assertEqual(error,F(1,4))
            mixed = [[F(15,16)*value+F(1,16)*int(a==0) for a,value in enumerate(row)] for row in oracle]
            mixed_information,mixed_error,_ = information_and_error(mixed,frontier.UNSIGNED)
            self.assertLess(mixed_information,h)
            self.assertEqual(mixed_error,F(17,64))

    def test_saved_exact_continuum_certificate_and_frozen_discovery_match(self):
        fresh = cert.certificate()
        saved = json.loads(cert.OUTPUT.read_text(encoding='utf-8'))
        self.assertEqual(fresh,saved)
        self.assertEqual((fresh['distinct_comparison_polynomials'],fresh['column_interval_cases'],
                          fresh['transformed_integer_coefficients_checked']),(48,240,19474))
        self.assertTrue(fresh['full_unrestricted_asymptotic_curve_characterized'])
        self.assertFalse(fresh['finite_optimum_or_efficient_code_claimed'])
        self.assertEqual((fresh['new_model_calls'],fresh['natural_workflow_episodes_added']),(0,0))
        discovery = json.loads((cert.ROOT/'experiments/dependency_memory/rate_curve/auxiliary/polynomial_probe.json').read_text())
        for old,new in zip(discovery,fresh['comparisons']):
            self.assertEqual((old['family'],old['interval'],old['column'],old['degree'],old['roots_at_one'],old['polynomial_sha256']),
                             (new['family'],new['interval'],new['column_group'],new['primitive_degree'],new['roots_at_one'],new['primitive_polynomial_sha256']))
        # C65 remains a dated eight-point result. Do not rewrite its original
        # scope flag just because the later analytic theorem extends it.
        frozen = cert.verify_frozen_dependency('experiments/dependency_memory/results/rate_spectrum_2026-10-01.json')
        self.assertFalse(frozen['complete_all_rate_unrestricted_curve_claimed'])


if __name__ == '__main__':
    unittest.main()
