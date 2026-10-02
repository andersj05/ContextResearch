"""Standard-library regeneration of a fixed witness, without native search."""
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from . import codec
from experiments.dependency_memory.joint_coding.coding import CODEBOOK as PAIR_BOOK
from experiments.dependency_memory.joint_coding_finite3.witness import selected_book

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DISCOVERY = HERE / 'discovery'
OUTPUT = HERE.parent / 'results/trellis_coding_2026-10-02.json'


def source_blocks(source, k):
    return tuple((source >> (4 * r)) & 15 for r in range(k))


def nearest_parents(book):
    """Exhaustive finite parent assignment, independent of Viterbi recurrence."""
    if not book:
        raise ValueError('Expected a nonempty finite book')
    k = len(book[0])
    if (not 1 <= k <= 4 or not 1 <= len(book) <= 4 ** k
            or any(len(word) != k or any(type(a) is not int or not 0 <= a < 16 for a in word) for word in book)):
        raise ValueError('Expected a legal diagnostic book at 1..4 blocks')
    if k == 4:
        # Pair factorization avoids storing a 65536-by-256 cost matrix.
        left = [[codec.loss(low & 15, a) + codec.loss(low >> 4, b)
                 for a, b, _, _ in book] for low in range(256)]
        right = [[codec.loss(high & 15, c) + codec.loss(high >> 4, d)
                  for _, _, c, d in book] for high in range(256)]
        table, costs = [], []
        for high in range(256):
            second = right[high]
            for low in range(256):
                first = left[low]
                best_cost, best_message = 49, None
                for m in range(len(book)):
                    cost = first[m] + second[m]
                    if cost < best_cost:
                        best_cost, best_message = cost, m
                table.append(best_message)
                costs.append(best_cost)
        return table, costs
    table, costs = [], []
    for source in range(1 << (4 * k)):
        blocks = source_blocks(source, k)
        values = [sum(codec.LOSSES[x][a] for x, a in zip(blocks, word)) for word in book]
        minimum = min(values)
        table.append(values.index(minimum))
        costs.append(minimum)
    return table, costs


def grade(parents, k, tables=codec.TABLES):
    """Execute updater/final prediction; labels are read only after prediction."""
    if type(k) is not int or not 1 <= k <= 4:
        raise ValueError('Actor population grading is restricted to 1..4 blocks')
    if len(parents) != 16 ** k or any(type(m) is not int or not 0 <= m < 4 ** k for m in parents):
        raise ValueError('Expected one legal parent per source')
    branches = [[0] * 4 for _ in range(k)]
    histogram = Counter()
    occupancies = Counter(parents)
    for source, message in enumerate(parents):
        truth = tuple(int(bit) for bit in reversed(f'{source:0{4*k}b}'))
        errors = 0
        for block in range(k):
            for omitted in range(4):
                child = codec.update(message, block, omitted, k, tables)
                for query in range(4):
                    if omitted == query:
                        continue
                    answer = codec.predict(child, block, omitted, query)
                    wrong = answer != truth[4 * block + query]
                    branches[block][omitted] += wrong
                    errors += wrong
        histogram[errors] += 1
    errors = sum(count * n for count, n in histogram.items())
    outcomes = 16 ** k * 12 * k
    ratio = Fraction(errors, outcomes)
    return {'blocks': k, 'parent_bits': 2 * k, 'child_bits': 1,
            'errors': errors, 'outcomes': outcomes,
            'distortion': {'numerator': ratio.numerator, 'denominator': ratio.denominator},
            'branch_errors': branches,
            'per_source_error_histogram': {str(error): n for error, n in sorted(histogram.items())},
            'used_parent_messages': len(occupancies),
            'message_occupancies': [occupancies[m] for m in range(4 ** k)],
            'parent_assignment_sha256': hashlib.sha256(bytes(parents)).hexdigest()}


def shuffle(seed):
    permutation = list(range(64))
    state = seed
    if not seed:
        return permutation
    for i in range(63, 0, -1):
        state ^= (state << 13) & 0xffffffff
        state ^= state >> 17
        state ^= (state << 5) & 0xffffffff
        j = state % (i + 1)
        permutation[i], permutation[j] = permutation[j], permutation[i]
    return permutation


def discovery_audit():
    """Check source bindings and all adaptive choices; do not rerun discovery."""
    metadata = json.loads((DISCOVERY / 'metadata.json').read_text(encoding='utf-8'))
    for name, expected in metadata['file_sha256'].items():
        if hashlib.sha256((DISCOVERY / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Preserved discovery source/output changed: ' + name)
    upstream = ROOT / metadata['upstream']['path']
    if hashlib.sha256(upstream.read_bytes()).hexdigest() != metadata['upstream']['sha256']:
        raise ValueError('Preserved three-block source witness changed')
    rows = [json.loads(line) for line in (DISCOVERY / 'initial.jsonl').read_text().splitlines()]
    if len(rows) != 33 or [row['seed'] for row in rows] != list(range(33)):
        raise ValueError('Initial search identities changed')
    for row in rows:
        if row['permutation'] != shuffle(row['seed']) or row['outcomes'] != 3145728:
            raise ValueError('Initial permutation or population changed')
    seed = min(rows, key=lambda row: row['errors'])
    if seed['seed'] != 11 or seed['errors'] != 879487 or rows[0]['errors'] != 884313:
        raise ValueError('Failed initial search or selected seed changed')
    base = json.loads(upstream.read_text(encoding='utf-8'))['runs']['greedy']['codeword_ids']
    # Header words are deterministic derivatives of the untouched upstream.
    expected_base = 'static const unsigned short BASE[64]={' + ','.join(map(str, base)) + '};'
    expected_seed = 'static const int PERM[64]={' + ','.join(map(str, seed['permutation'])) + '};'
    if (DISCOVERY / 'base.h').read_text().strip() != expected_base or (DISCOVERY / 'seed.h').read_text().strip() != expected_seed:
        raise ValueError('Native headers are not the declared source/permutation')
    labels = [[(base[seed['permutation'][index]] >> (4 * phase)) & 15 for index in range(64)]
              for phase in range(3)]
    records = [json.loads(line) for line in (DISCOVERY / 'optimization.jsonl').read_text().splitlines()]
    expected_initial = {'kind': 'initial', 'errors': 879487, 'passes': 4, 'outcomes': 3145728}
    if records[0] != expected_initial or len(records) != 1 + 4 * 193 + 1:
        raise ValueError('Bounded optimization record changed')
    current, moves, cursor, passes = 879487, 0, 1, []
    for sweep in range(4):
        changed = 0
        for phase in range(3):
            for index in range(64):
                record = records[cursor]
                cursor += 1
                old = labels[phase][index]
                scores = record['scores']
                if (record['kind'], record['pass'], record['phase'], record['index'], record['old']) != ('entry', sweep, phase, index, old):
                    raise ValueError('Coordinate visit order changed')
                if len(scores) != 16 or scores[old] != current or any(type(v) is not int or v < 0 for v in scores):
                    raise ValueError('Coordinate scores/old state inconsistent')
                value = min(scores)
                selected = scores.index(value) if value < current else old
                if record['selected'] != selected:
                    raise ValueError('Accepted choice not the declared strict improvement')
                if selected != old:
                    labels[phase][index] = selected
                    current = value
                    changed += 1
        passes.append({'kind': 'pass', 'pass': sweep, 'moves': changed, 'errors': current})
        if records[cursor] != passes[-1]:
            raise ValueError('Pass total inconsistent')
        cursor += 1
        moves += changed
    if records[cursor] != {'kind': 'final', 'errors': current, 'moves': moves, 'tables': labels}:
        raise ValueError('Final labels or totals inconsistent')
    if tuple(map(tuple, labels)) != codec.TABLES or (current, moves) != (867837, 93):
        raise ValueError('Selected public labels differ from preserved discovery')
    return {'initial_candidates': 33, 'failed_initial_best_errors': seed['errors'],
            'identity_errors': rows[0]['errors'], 'selected_seed': seed['seed'],
            'coordinate_visits': 768, 'alternative_label_evaluations': 11520,
            'accepted_changes': moves, 'passes': passes,
            'selected_errors': current, 'local_optimum_certified': False,
            'discovery_scores_independently_recomputed': 'final tables below; rejected alternatives stay native observations'}


def controls():
    """Exact product counts from independently computed small-block losses."""
    _, one_costs = nearest_parents(tuple((a,) for a in (0, 1, 14, 15)))
    _, pair_costs = nearest_parents(PAIR_BOOK)
    _, triple_costs = nearest_parents(selected_book())
    one, pair, triple = sum(one_costs), sum(pair_costs), sum(triple_costs)
    if (one, pair, triple) != (54, 1698, 40529):
        raise ValueError('Historical component losses changed')
    common_outcomes = 16 ** 12 * 12 * 12
    four_product = 3 * 867837 * 16 ** 8
    triple_product = 4 * triple * 16 ** 9
    return {'pair_product': 2 * pair * 256, 'three_plus_one': triple * 16 + one * 4096,
            'four_independent_blocks': 4 * one * 4096,
            'outcomes': 3145728, 'method': 'product additivity, not extra executed four-block actor routes',
            'component_source_loss_sums': {'one': one, 'pair': pair, 'triple': triple},
            'common_length_twelve': {'parent_bits': 24, 'child_bits': 1,
                'outcomes': common_outcomes, 'four_block_product_errors': four_product,
                'existing_three_block_product_errors': triple_product,
                'existing_three_block_product_wins': triple_product < four_product,
                'evidence': 'exact component-additivity derivation, no twelve-block population execution'}}


def certificate():
    discovery = discovery_audit()
    results = []
    for k in range(1, 5):
        candidates = codec.book(k)
        parents, minimum_costs = nearest_parents(candidates)
        result = grade(parents, k)
        if result['errors'] != sum(minimum_costs):
            raise ValueError('Independent route grading and nearest costs disagree')
        result['distinct_decision_words'] = len(set(candidates))
        result['possible_parent_messages'] = 4 ** k
        results.append(result)
    if results[-1]['errors'] != discovery['selected_errors']:
        raise ValueError('Python grader and selected native score disagree')
    baseline = controls()
    files = [HERE / name for name in ('codec.py', 'certificate.py', 'test_trellis.py', 'tables.json', 'README.md')]
    files += sorted(p for p in DISCOVERY.iterdir() if p.is_file())
    files += [HERE.parent / 'joint_coding/coding.py',
              HERE.parent / 'joint_coding_finite3/discovery.json',
              HERE.parent / 'joint_coding_finite3/witness.py']
    return {'version': 'delayed_query_trellis_witness_v1', 'date': '2026-10-02',
            'evidence_class': 'explicit finite witness and exact dynamic-programming derivation; bounded post-hoc discovery',
            'new_model_calls': 0, 'prospective_natural_episodes': 0,
            'source_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            'information_contract': {'source': 'uniform iid four-bit blocks; independent uniform R/O/J',
                'parent_bits': '2*k, formed before R/O', 'child_bits': '1, formed before J',
                'updater_inputs': ['M', 'R', 'O', 'public k', 'public fixed labels'],
                'final_inputs': ['Z', 'R', 'O', 'J'], 'archives_or_rereads': False,
                'cyclic_boundary_state': 'last two parent symbols, already in M; no separate bits',
                'tables_fixed_before_source': True},
            'trellis_states': 16, 'parent_alphabet_per_block': 4, 'public_label_entries': 192,
            'packed_public_label_bytes': len(codec.pack_tables()),
            'packing_scope': 'label payload only; excludes program, JSON, runtime and metadata; free public design in bit model',
            'exact_encoder_branch_relaxations': '1024*k for k>=2; k=1 checks four messages',
            'encoder_storage_scope': 'two cost tables of k*16 bounded integer entries, source costs and parent-symbol scratch; no wall-time claim',
            'encoder_optimality_scope': 'minimum within this fixed table construction; not all possible encoders/tables',
            'four_block_product_extension': {
                'blocks': 'k=4*n, n>=1', 'parent_bits': '2*k', 'child_bits': 1,
                'distortion': results[-1]['distortion'],
                'evidence': 'elementary product-additivity derivation; not enumerated 16^(4*n) outcomes',
                'group_reset_scope': 'each group independently tail-biting; different from one long cyclic trellis',
                'branch_relaxations': '1024*k',
                'quality_limit': 'worse than preserved three-block product at common lengths k=12*n; no improvement of best known asymptotic upper bound'},
            'population_assignment_method': 'enumerate all messages and exact nearest costs; Viterbi equivalence checked separately by tests/proof',
            'finite_results': results, 'four_block_controls': baseline,
            'four_block_errors_avoided_against_pair_product': baseline['pair_product'] - results[-1]['errors'],
            'actor_query_routes_executed': sum(row['outcomes'] for row in results),
            'discovery': discovery,
            'limits': 'Specific tables; four-block upper bound only, exact finite optimum and asymptotic quality of this trellis unknown. Generic TCQ, Viterbi, bit shifts and tail-biting are established. No portable timing, model/production gain, natural episode or publication priority. Existing C59/C67 evidence unchanged.'}


def main():
    data = certificate()
    OUTPUT.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'finite_errors': [row['errors'] for row in data['finite_results']],
                      'controls': data['four_block_controls'],
                      'errors_avoided': data['four_block_errors_avoided_against_pair_product'],
                      'routes': data['actor_query_routes_executed']}))


if __name__ == '__main__':
    main()
