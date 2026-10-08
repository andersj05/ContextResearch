"""Post-outcome metered terminal resources for the completed v4 K/R pairs.

This read-only extraction uses recorded calls, not independent policy projections.
It starts no model and does not change the frozen primary analysis.
"""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USAGE_KEYS = ('input_tokens', 'cached_input', 'output', 'reasoning')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def lines(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]


def audit(folder):
    folder = Path(folder).resolve()
    if not folder.is_relative_to(ROOT) or not (folder / 'evidence_manifest.json').is_file():
        raise ValueError('closed workspace archive required')
    if read(folder / 'summary.json')['selected_tasks'] != 32:
        raise ValueError('fixed v4 cohort required')
    rows = lines(folder / 'tasks.jsonl')
    analysis = read(folder / 'analysis.json')
    paired = [r for r in rows if r['primary_scheduled'] and None not in r['grades']['K'] + r['grades']['R']]
    if len(paired) != analysis['domains']['math']['primary_R_minus_K']['complete_tasks']:
        raise ValueError('completed-pair denominator mismatch')
    latest = {}
    for event in lines(folder / 'usage_events.jsonl'):
        latest.setdefault(event['call_id'], {}).update(event)
    indexed = {}
    for key, call in latest.items():
        identity = call['identity']
        if identity['stage'] != 'terminal':
            continue
        index = (identity['task_id'], identity['arm'], identity['draw'])
        if index in indexed:
            raise ValueError('duplicate terminal identity')
        indexed[index] = call
    arm_totals = {}
    retained = {}
    for arm in ('K', 'R'):
        calls = [indexed[(r['task_id'], arm, draw)] for r in paired for draw in (1, 2)]
        if any(c['state'] != 'completed' for c in calls):
            raise ValueError('complete pair lacks metered terminal call')
        for call in calls:
            usage = call['usage']
            computed = (Decimal(usage['input_tokens'] - usage['cached_input']) * Decimal('2.5')
                        + Decimal(usage['cached_input']) * Decimal('.25')
                        + Decimal(usage['output']) * Decimal('12.5')) / Decimal(1000000)
            if computed != Decimal(call['planning_credits']):
                raise ValueError('recorded planning-credit formula mismatch')
        arm_totals[arm] = {
            'calls': len(calls),
            'usage': {k: sum(c['usage'][k] for c in calls) for k in USAGE_KEYS},
            'planning_credits': str(sum((Decimal(c['planning_credits']) for c in calls), Decimal(0))),
            'correct_draws': sum(sum(r['grades'][arm]) for r in paired),
        }
        retained[arm] = [c['call_id'] for c in calls]
    k, r = arm_totals['K'], arm_totals['R']
    return {
        'evidence_kind': 'post_outcome_extraction_of_actual_metered_matched_terminal_calls',
        'complete_paired_tasks': len(paired), 'arm_totals': arm_totals,
        'R_minus_K': {
            'usage': {key: r['usage'][key] - k['usage'][key] for key in USAGE_KEYS},
            'planning_credits': str(Decimal(r['planning_credits']) - Decimal(k['planning_credits'])),
            'correct_draws': r['correct_draws'] - k['correct_draws'],
        },
        'call_ids': retained,
        'source_bindings': [
            {'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in (Path(__file__), folder / 'manifest.json', folder / 'evidence_manifest.json',
                      folder / 'tasks.jsonl', folder / 'usage_events.jsonl', folder / 'analysis.json')
        ],
        'model_calls': 0, 'API_spend_USD': '0', 'actual_account_charge': None,
        'scope': 'Terminal calls on completed K/R pairs only. Shared initial work and lesson writing are excluded. '
                 'Reasoning is included in output. Mutable alias and stochastic generation apply. '
                 'These are recorded experiment calls, not complete policy runs, native-harness savings or account charges.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT) or output.exists():
        raise ValueError('fresh workspace output required')
    value = audit(args.folder)
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True, separators=(',', ':'))
        stream.write('\n')
    print(json.dumps({k: value[k] for k in ('complete_paired_tasks', 'arm_totals', 'R_minus_K', 'model_calls')}))
