"""Finite checks and fixed-code applications of the analytic completion lemma."""
from functools import lru_cache
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from pathlib import Path

from experiments.dependency_memory.decoder_completion import complete as c
from experiments.dependency_memory.joint_coding_complement import cover
from experiments.dependency_memory.joint_coding_finite3 import witness

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AUX = HERE.parent/'joint_coding_general/auxiliary'
OUTPUT = HERE.parent/'results/decoder_completion_2026-10-02.json'


def branch_check():
    digest = sha256()
    checks = completions = 0
    for pair in combinations_with_replacement(range(8), 2):
        choices = c.branch_completions(pair)
        for policy in range(256):
            old = sum((x ^ pair[(policy >> x) & 1]).bit_count() for x in range(8))
            scores = [sum((x ^ new_pair[((policy >> x) & 1) ^ flip]).bit_count() for x in range(8))
                      for new_pair, flip in choices]
            if sum(scores) != len(scores)*old or min(scores) > old:
                raise ArithmeticError('Balanced-source averaging identity failed')
            digest.update(f'{pair}:{policy}:{old}:{scores}\n'.encode('ascii'))
            checks += 1
            completions += len(scores)
    return {'branch_policy_cases': checks, 'oriented_completions_graded': completions,
            'average_disagreements': 0, 'comparison_sha256': digest.hexdigest()}


def biased_counterexample():
    # Sources 0000 and 0011, each probability 1/2. Coordinates 2/3 are biased.
    noncomp = tuple(c.f.PAIR_INDEX[(0, c.f.project(3, o))] for o in range(4))
    old = c.f.loss_matrix(noncomp)
    if old[0][0] != 0 or old[3][15] != 0:
        raise ArithmeticError('Noncomplementary zero-error counterexample failed')
    best = min(sum(min(c.f.loss_matrix(table)[x]) for x in (0, 3))
               for table, _ in ((member, None) for _, members in cover.orbits() for member in members))
    if best != 4:
        raise ArithmeticError('Biased-source complementary floor changed')
    return {'sources': [0, 3], 'source_probabilities': ['1/2', '1/2'], 'parent_states': 2,
            'noncomplementary_errors': 0, 'minimum_complementary_errors': best,
            'equally_weighted_outcomes': 24, 'minimum_complementary_error': '1/6',
            'scope': 'Biased-source counterexample to extending complementary optimality; not the active uniform source.'}


@lru_cache(maxsize=1)
def certificate():
    records = []
    routes = 0
    manifest = json.loads((AUX/'manifest.json').read_text())
    for name, digest in manifest['source_sha256'].items():
        if sha256((AUX/name).read_bytes()).hexdigest() != digest:
            raise ArithmeticError('Historical auxiliary provenance changed')
    inputs = sorted(AUX.glob('search_*.json'))
    if len(inputs) != 8:
        raise ArithmeticError('Expected the eight already preserved books')
    for path in inputs:
        raw = json.loads(path.read_text())
        tables = tuple(c.f.decode_table(i) for i in raw['decoder_indices'])
        book = tuple(witness.decode_id(i) for i in raw['codeword_ids'])
        parent = c.nearest_parent(tables, book)
        before = c.grade(tables, book, parent)
        changed = c.complete_code(tables, book, parent)
        preserved = c.grade(changed['tables'], changed['book'], changed['parent'])
        reassigned = c.nearest_parent(changed['tables'], changed['book'])
        reencoded = c.grade(changed['tables'], changed['book'], reassigned)
        if before != raw['errors'] or not reencoded <= preserved <= before:
            raise ArithmeticError('Whole-code completion failed to preserve or improve mean error')
        records.append({'source': path.relative_to(ROOT).as_posix(), 'old_errors': before,
                        'completed_preserved_parent_errors': preserved, 'completed_reencoded_errors': reencoded,
                        'outcomes': 147456, 'parent_states': len(book),
                        'completed_tables': [list(table) for table in changed['tables']],
                        'relabel_masks': list(changed['relabel_masks']),
                        'completed_codeword_ids': [sum(a << (4*r) for r, a in enumerate(word)) for word in changed['book']],
                        'old_parent_sha256': sha256(bytes(parent)).hexdigest(),
                        'preserved_parent_sha256': sha256(bytes(changed['parent'])).hexdigest(),
                        'reencoded_parent_sha256': sha256(bytes(reassigned)).hexdigest()})
        routes += 3*147456
    unsigned = (c.f.UNSIGNED,)*3
    book = witness.selected_book()
    parent = tuple(witness.parent_table(book))
    identity = c.complete_code(unsigned, book, parent)
    if identity['tables'] != unsigned or identity['book'] != book or identity['parent'] != parent:
        raise ArithmeticError('Existing complementary witness must be unchanged')
    if c.grade(identity['tables'], identity['book'], identity['parent']) != 40529:
        raise ArithmeticError('Historical upper witness changed')
    routes += 147456
    lower = cover.certificate()
    if lower['lower_errors'] != 40072:
        raise ArithmeticError('Underlying complementary converse changed')
    files = [HERE/name for name in ('complete.py', 'certificate.py', 'test_completion.py', 'README.md')]
    files += [HERE.parent/'joint_coding/decoder_frontier.py', HERE.parent/'joint_coding_complement/cover.py',
              HERE.parent/'joint_coding_complement/discovery.json', HERE.parent/'joint_coding/coding.py',
              HERE.parent/'joint_coding_finite3/witness.py', HERE.parent/'joint_coding_finite3/discovery.json',
              AUX/'manifest.json', *inputs]
    return {'version': 1, 'date': '2026-10-02',
            'evidence_class': 'local analytic average-loss completion theorem with finite branch and whole-code checks',
            'theorem_scope': 'Every k and parent capacity under balanced queried source marginals and source-independent public queries; arbitrary fixed joint encoder/updater and one-bit child. Public completion fixed before source. Existing uniform independent block law is included.',
            'unrestricted_optimum_equals_complementary_optimum': True,
            'all_table_choices_per_block': 36**4, 'complementary_table_choices_per_block': 256,
            'complementary_orbits_per_block': len(cover.orbits()), 'branch_checks': branch_check(),
            'whole_codes': records, 'whole_code_routes_executed': routes,
            'minimum_completed_reencoded_errors': min(r['completed_reencoded_errors'] for r in records),
            'existing_40529_error_witness_unchanged': True,
            'alternative_unrestricted_three_block_lower_errors': lower['lower_errors'],
            'biased_counterexample': biased_counterexample(),
            'source_sha256': {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in files},
            'new_model_calls': 0, 'natural_workflow_episodes_added': 0,
            'limits': 'Population average Hamming loss, not per-instance or worst-case preservation. Balanced queried marginals and source-independent queries matter. Design may require full population correlations; no efficient practical decoder design, general derandomization novelty, finite optimum, model gain or production-cost result. Original encoder/capacity fixed; canonical child labels only relabelled. Optional subsequent parent reassignment is a separate achievable finite code, not the completion proof. Full unrestricted rate curve and external proof/priority review remain open.'}


def main():
    result = certificate()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('branch_checks', 'whole_code_routes_executed',
                                          'minimum_completed_reencoded_errors', 'alternative_unrestricted_three_block_lower_errors')}, indent=2))


if __name__ == '__main__':
    main()
