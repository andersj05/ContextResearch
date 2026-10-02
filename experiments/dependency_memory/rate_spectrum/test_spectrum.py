"""Independent source enumeration and symbolic identities for rate support."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
import json
import unittest

from rate_spectrum import derive
from experiments.dependency_memory.rate_spectrum import certificate as c
from experiments.dependency_memory.joint_coding import decoder_frontier as f


def direct_loss(x, a):
    return sum(((x >> j) & 1) != ((a >> o) & 1) for o in range(4) for j in range(4) if j != o)


def multiply(a, b):
    result = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i+j] += x*y
    return result


class SpectrumTests(unittest.TestCase):
    def test_class_kernels_match_all_actual_source_word_routes(self):
        for t in (F(1,100), F(1,4), F(19,20)):
            groups = ((0,15), tuple(a for a in range(16) if a.bit_count()==2),
                      tuple(a for a in range(16) if a.bit_count() in (1,3)))
            coefficients = derive.classes(t)
            for x in range(16):
                source_class = min(x.bit_count(),4-x.bit_count())
                for group, column in zip(groups, coefficients):
                    direct = sum(t**direct_loss(x,a) for a in group)/len(group)
                    self.assertEqual(direct, column[source_class])

    def test_odd_domination_has_independent_positive_factor_identities(self):
        self.assertEqual(multiply((1,-2,1),(1,1,2,4,2,1,1)),[1,-1,1,1,-4,1,1,-1,1])
        self.assertEqual(multiply((1,-2,1),(4,1,4)),[4,-7,6,-7,4])
        for numerator in range(1,100):
            t=F(numerator,100)
            a,b,odd=derive.classes(t)
            mix=derive.dominating_mix(t)
            delta=[mix*x+(1-mix)*y-z for x,y,z in zip(a,b,odd)]
            expected0=(1-t**3)**2*(1-t)**2*sum(v*t**i for i,v in enumerate((1,1,2,4,2,1,1)))/(2*(1+t)**2)
            expected1=t**3*(1-t)**4*(4+t+4*t*t)/8
            self.assertEqual(delta,[expected0,expected1,F(0)])
            self.assertTrue(0<mix<1 and expected0>0 and expected1>0)

    def test_transition_and_endpoint_derivatives_factor_exactly(self):
        numerator=(1,-12,9,9,-8,1,1,-8,9,9,-12,1)
        self.assertEqual(multiply(multiply((1,-2,1),(1,1)),derive.TRANSITION),list(numerator))
        endpoint=(1,4,9,8,-44,8,9,4,1)
        self.assertEqual(multiply((1,-2,1),(1,6,20,42,20,6,1)),list(endpoint))
        for t in (F(1,100),F(1,4),F(3,10),F(19,20)):
            u=t*t
            zero=(1-u)**2*(1+u)*derive.polynomial(derive.TRANSITION,u)/(16*u*(1+u**3)*(1+u**6))
            one=-(1-u)**2*sum(v*u**i for i,v in enumerate((1,6,20,42,20,6,1)))/(16*u**3*(1+4*u+u*u))
            self.assertEqual(derive.log_partition_derivative(t,F(0)),zero)
            self.assertEqual(derive.log_partition_derivative(t,F(1)),one)
            self.assertLess(one,0)
        self.assertEqual(derive.TRANSFORMED[0],1)
        self.assertTrue(all(v<0 for v in derive.TRANSFORMED[1:]))
        for v in (F(1,10),F(1),F(10)):
            self.assertEqual((1+v)**8*derive.polynomial(derive.TRANSITION,v/(1+v)),derive.polynomial(derive.TRANSFORMED,v))

    def test_optimizer_brackets_and_exact_gibbs_constant_marginal(self):
        bounds=derive.transition_bracket()
        low,high=bounds['u']
        self.assertGreater(derive.polynomial(derive.TRANSITION,low),0)
        self.assertLess(derive.polynomial(derive.TRANSITION,high),0)
        self.assertLess(bounds['t'][0]**2,low)
        self.assertGreater(bounds['t'][1]**2,high)
        for t in c.POINTS:
            lo,hi=derive.balanced_mass_bracket(t)
            weights=derive.unsigned_weights(t)
            self.assertEqual(sum(weights),derive.WEIGHT_TOTAL)
            self.assertTrue(all(w>=0 for w in weights))
            if lo:
                self.assertGreater(derive.log_partition_derivative(t,lo),0)
                self.assertLess(derive.log_partition_derivative(t,hi),0)
                self.assertLess(hi-lo,F(1,2**89))
            else:
                self.assertLessEqual(derive.log_partition_derivative(t,F(0)),0)
                for a in (0,15):
                    marginal=sum(t**direct_loss(x,a)/(t**direct_loss(x,0)+t**direct_loss(x,15))
                                 for x in range(16))/16
                    self.assertEqual(marginal,F(1,2))

    def test_supporting_inequality_on_independent_channels(self):
        # Source-independent, identity and cyclic-noise channels; Decimal
        # computes actual I and E[L], independently of the dual implementation.
        with localcontext() as ctx:
            ctx.prec=65
            ln2=Decimal(2).ln()
            for t in (F(1,4),F(4,5)):
                weights=derive.unsigned_weights(t)
                n,d=f.dual_product(f.loss_matrix(f.UNSIGNED),weights,t)
                _,high=f.log2_bounds(n,d)
                bound=-high/16
                for channel in ('independent','identity','cyclic'):
                    probabilities=[[F(1,16) if channel=='independent' else F(int(a==x)) if channel=='identity'
                                    else F(3,4) if a==x else F(1,4) if a==(x+1)%16 else F(0)
                                    for a in range(16)] for x in range(16)]
                    marginal=[sum(row[a] for row in probabilities)/16 for a in range(16)]
                    info=Decimal(0)
                    loss=F(0)
                    for x,a in product(range(16),repeat=2):
                        p=probabilities[x][a]
                        loss+=p*direct_loss(x,a)/16
                        if p:
                            ratio=p/marginal[a]
                            info+=(Decimal(p.numerator)/Decimal(p.denominator)/16)*(Decimal(ratio.numerator)/Decimal(ratio.denominator)).ln()/ln2
                    slope=-(Decimal(t.numerator)/Decimal(t.denominator)).ln()/ln2
                    objective=info+slope*Decimal(loss.numerator)/Decimal(loss.denominator)
                    self.assertGreaterEqual(objective,Decimal(bound.numerator)/Decimal(bound.denominator))

    def test_saved_all_decoder_cover_and_strict_rate_slack(self):
        fresh=c.certificate()
        saved=json.loads(c.OUTPUT.read_text(encoding='utf-8'))
        self.assertEqual(fresh,saved)
        self.assertEqual((fresh['support_points'],fresh['orbit_point_checks']),(8,38008))
        self.assertFalse(fresh['complete_all_rate_unrestricted_curve_claimed'])
        self.assertEqual(fresh['new_model_calls'],0)
        for point in fresh['points']:
            self.assertGreater(F(point['rate_slack_lower']),0)
            self.assertGreater(F(point['other_decoder_objective_separation_lower']),0)
            self.assertLess(F(point['distortion_upper'])-F(point['distortion_lower']),F(2,10**11))
            self.assertEqual(point['worst_orbit'],f.encode_table(f.UNSIGNED))
