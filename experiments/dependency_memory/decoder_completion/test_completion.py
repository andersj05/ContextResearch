"""Independent route, label, mean-loss and information checks."""
from collections import Counter
from fractions import Fraction
from itertools import combinations_with_replacement, product
import json
import random
import unittest

from experiments.dependency_memory.decoder_completion import complete as c
from experiments.dependency_memory.decoder_completion import certificate as cert


def route_grade(tables, book, parent):
    # Coordinate dictionaries, no generator loss matrix or actor functions.
    errors = 0
    for source, message in enumerate(parent):
        for r, table in enumerate(tables):
            bits = {j: (source >> (4*r+j)) & 1 for j in range(4)}
            for o, pair_index in enumerate(table):
                endpoint = c.f.PAIRS[pair_index][(book[message][r] >> o) & 1]
                prediction = dict(zip((j for j in range(4) if j != o),
                                      (int(v) for v in reversed(f'{endpoint:03b}'))))
                errors += sum(prediction[j] != bits[j] for j in prediction)
    return errors


def constructed_code(k, seed, states):
    rng = random.Random(seed)
    tables = tuple(tuple(rng.randrange(36) for _ in range(4)) for _ in range(k))
    ids = rng.sample(range(16**k), states)
    book = tuple(tuple((a >> (4*r)) & 15 for r in range(k)) for a in ids)
    parent = tuple(rng.randrange(states) for _ in range(16**k))
    return tables, book, parent


class CompletionTests(unittest.TestCase):
    def test_all_pair_completions_against_coordinate_construction(self):
        for pair in combinations_with_replacement(range(8), 2):
            coords = [j for j in range(3) if ((pair[0] >> j) & 1) == ((pair[1] >> j) & 1)]
            independent = []
            for bits in product((0, 1), repeat=len(coords)):
                zero = {j: (pair[0] >> j) & 1 for j in range(3)}
                zero.update(dict(zip(coords, bits)))
                word = sum(bit << j for j, bit in zero.items())
                canonical = tuple(sorted((word, 7-word)))
                independent.append((canonical, int(word != canonical[0])))
            self.assertEqual(sorted(c.branch_completions(pair)), sorted(independent))
            for new, flip in independent:
                self.assertEqual(new[0] ^ new[1], 7)
                for bit, j in product((0, 1), range(3)):
                    if ((pair[0] ^ pair[1]) >> j) & 1:
                        self.assertEqual((new[bit ^ flip] >> j) & 1, (pair[bit] >> j) & 1)

    def test_branch_average_by_actual_bits_not_popcount(self):
        for pair in combinations_with_replacement(range(8), 2):
            choices = c.branch_completions(pair)
            for policy in range(256):
                old = sum(((x >> j) & 1) != ((pair[(policy >> x) & 1] >> j) & 1)
                          for x, j in product(range(8), range(3)))
                scores = [sum(((x >> j) & 1) != ((new[((policy >> x) & 1) ^ flip] >> j) & 1)
                              for x, j in product(range(8), range(3))) for new, flip in choices]
                self.assertEqual(sum(scores), old*len(scores))
                self.assertLessEqual(min(scores), old)

    def test_fixed_joint_codes_preserve_encoder_capacity_and_mean_loss(self):
        for k, states, seed in ((1,1,2026100201),(1,8,2026100202),(2,16,2026100203),(3,8,2026100204)):
            tables, book, parent = constructed_code(k, seed, states)
            result = c.complete_code(tables, book, parent)
            self.assertEqual(result['parent'], parent)
            self.assertEqual(len(result['book']), len(book))
            self.assertTrue(all((c.f.PAIRS[i][0] ^ c.f.PAIRS[i][1]) == 7 for t in result['tables'] for i in t))
            before = route_grade(tables, book, parent)
            after = route_grade(result['tables'], result['book'], parent)
            self.assertLessEqual(after, before)
            self.assertEqual(c.grade(result['tables'], result['book'], parent), after)
            for source in (0, len(parent)//2, len(parent)-1):
                m=parent[source]
                for r,o in product(range(k), range(4)):
                    self.assertEqual(c.update(m,r,o,result['book']), ((book[m][r] >> o) & 1) ^ ((result['relabel_masks'][r] >> o) & 1))

    def test_complementary_tables_are_unchanged(self):
        pairs = [i for i,pair in enumerate(c.f.PAIRS) if pair[0] ^ pair[1] == 7]
        book = ((0,),(3,),(12,),(15,))
        parent = tuple(x % 4 for x in range(16))
        for table in product(pairs, repeat=4):
            result=c.complete_code((table,),book,parent)
            self.assertEqual((result['tables'],result['book'],result['parent']),((table,),book,parent))
            self.assertEqual(result['relabel_masks'],(0,))

    def test_information_preserved_as_a_joint_count_permutation(self):
        tables,book,parent=constructed_code(2,2026100205,16)
        result=c.complete_code(tables,book,parent)
        for r,mask in enumerate(result['relabel_masks']):
            original=Counter(((x >> (4*r)) & 15,book[m][r]) for x,m in enumerate(parent))
            relabelled=Counter(((x >> (4*r)) & 15,result['book'][m][r]^mask) for x,m in enumerate(parent))
            self.assertEqual(original,relabelled)

    def test_biased_source_breaks_optimality_extension(self):
        counter=cert.biased_counterexample()
        self.assertEqual(Fraction(counter['minimum_complementary_errors'],counter['equally_weighted_outcomes']),Fraction(1,6))
        self.assertEqual(counter['noncomplementary_errors'],0)
        # Independently enumerate all four complementary pairs per omission
        # and both source-specific child responses; minima separate by O.
        total=0
        for o in range(4):
            positions=[j for j in range(4) if j!=o]
            costs=[]
            for first in range(4):
                pair=(first,7-first)
                cost=0
                for x in (0,3):
                    cost+=min(sum(((x>>j)&1)!=((word>>pos)&1) for pos,j in enumerate(positions)) for word in pair)
                costs.append(cost)
            total+=min(costs)
        self.assertEqual(total,4)

    def test_mean_preservation_is_not_pointwise_preservation(self):
        pair=(0,1)
        old=sum((x^pair[x&1]).bit_count() for x in range(8))
        new=sum((x^(7 if x&1 else 0)).bit_count() for x in range(8))
        self.assertEqual(old,new)
        self.assertEqual((1^pair[1]).bit_count(),0)
        self.assertEqual((1^7).bit_count(),2)

    def test_saved_certificate_and_independent_final_routes(self):
        fresh=cert.certificate()
        saved=json.loads(cert.OUTPUT.read_text())
        self.assertEqual(fresh,saved)
        self.assertEqual(fresh['branch_checks']['branch_policy_cases'],9216)
        self.assertEqual(len(fresh['whole_codes']),8)
        self.assertEqual(fresh['alternative_unrestricted_three_block_lower_errors'],40072)
        self.assertTrue(fresh['existing_40529_error_witness_unchanged'])
        for row in fresh['whole_codes']:
            tables=tuple(tuple(t) for t in row['completed_tables'])
            book=tuple(tuple((a >> (4*r)) & 15 for r in range(3)) for a in row['completed_codeword_ids'])
            parent=c.nearest_parent(tables,book)
            self.assertEqual(route_grade(tables,book,parent),row['completed_reencoded_errors'])
            self.assertEqual(row['old_parent_sha256'],row['preserved_parent_sha256'])
        self.assertEqual(fresh['new_model_calls'],0)
