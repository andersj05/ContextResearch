"""Derive a descriptive closeout from sealed and independently audited evidence."""
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from statistics import mean
import json
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from experiments.dependency_memory.rollback_development_v5.common import read, save_new, sha
from experiments.dependency_memory.rollback_development_v5_continuation.schedule import calls_for_job

folder = Path(__file__).resolve().parents[1]
live = folder / 'live'
audited = read(folder / 'launch_checks' / 'live_audit_result.json')
if not audited.get('all_passed') or not (live / 'evidence_manifest.json').is_file():
    raise ValueError('independent sealed-evidence audit must pass before reporting')
execution, analysis, manifest = (read(live / p) for p in ('execution.json', 'analysis.json', 'manifest.json'))
calls = analysis['accounting']['calls']
by_task = read(ROOT / manifest['continuation']['original_bundle'] / 'tasks.json')
tasks = {t['task_id']: t for t in by_task}
known = [c for c in calls if c['state'] == 'completed']
unknown = [c for c in calls if c['state'] == 'unknown']
assert len(known) == audited['known_generations_replayed']
assert len(unknown) == audited['unknown_generations_reconciled']
assert len(execution['jobs']) == 768 and len(tasks) == 48
rows = [r for r in execution['jobs'] if r['job']['arm'] != 'prefix']
scored = [r for r in rows if r['result'].get('score') is not None]


def resource(job):
    selected = [c for c in calls_for_job(job, calls) if c['state'] == 'completed']
    return {'calls': len(selected), 'input_tokens': sum(c['usage']['input_tokens'] for c in selected),
            'output_tokens': sum(c['usage']['output'] for c in selected),
            'cached_input_tokens': sum(c['usage']['cached_input'] for c in selected),
            'reasoning_tokens': sum(c['usage']['reasoning'] for c in selected),
            'planning_credits': sum((Decimal(c['planning_credits']) for c in selected), Decimal(0)),
            'call_seconds': sum(c['elapsed_seconds'] for c in selected)}


pairs = {}
for track in analysis['tracks']:
    indexed = {arm: {r['job']['task_id']: r for r in scored if r['job']['track'] == track and r['job']['arm'] == arm}
               for arm in ('K', 'R')}
    ids = sorted(indexed['K'].keys() & indexed['R'].keys())
    outcomes = Counter(); totals = {arm: defaultdict(lambda: 0) for arm in ('K', 'R')}
    task_pairs = []
    for task_id in ids:
        a, b = indexed['R'][task_id], indexed['K'][task_id]
        R, K = a['result']['score'], b['result']['score']
        outcomes['both_pass' if R == K == 1 else 'both_fail' if R == K == 0 else 'R_only' if R else 'K_only'] += 1
        one = {'task_id': task_id, 'family': tasks[task_id]['family'], 'R': R, 'K': K}
        for arm in ('K', 'R'):
            measured = resource(indexed[arm][task_id]['job'])
            for key, value in measured.items():
                totals[arm][key] += value
            totals[arm]['successes'] += indexed[arm][task_id]['result']['score']
            totals[arm]['actions'] += indexed[arm][task_id]['result']['actions_used']
            one[arm + '_resource'] = {k: str(v) if isinstance(v, Decimal) else v for k, v in measured.items()}
        task_pairs.append(one)
    assert len(ids) == analysis['tracks'][track]['R_minus_K']['complete_pairs']
    relative = {key: float((totals['R'][key] - totals['K'][key]) / totals['K'][key]) if totals['K'][key] else None
                for key in ('input_tokens', 'output_tokens', 'calls', 'planning_credits', 'actions')}
    pairs[track] = {'complete_pairs': len(ids), 'quality_outcomes': dict(outcomes), 'task_pairs': task_pairs,
                    'totals': {arm: {k: str(v) if isinstance(v, Decimal) else v for k, v in values.items()}
                               for arm, values in totals.items()}, 'R_relative_to_K': relative,
                    'scope': 'same complete-pair tasks; mechanism excludes common preparation, reported separately; missing pairs are not imputed'}

missing = []
for row in rows:
    selected = calls_for_job(row['job'], calls)
    unresolved = [c['call_id'] for c in selected if c['state'] != 'completed']
    if unresolved:
        assert row['result'].get('score') is None
        missing.append({'job': row['job'], 'unknown_call_ids': unresolved, 'disposition': row['result']['disposition']})
prefixes = [r['result'] for r in execution['jobs'] if r['job']['arm'] == 'prefix']
summary = {'evidence_kind': 'descriptive_derived_live_results', 'tasks': len(tasks), 'jobs': len(execution['jobs']),
           'known_episode_scores': len(scored), 'passed_episodes': sum(r['result']['score'] for r in scored),
           'remaining_global_stop_jobs': sum(r['result'].get('disposition') == 'unstarted_global_stop' for r in execution['jobs']),
           'prefix_dispositions': analysis['tracks']['mechanism']['prefix_dispositions'],
           'eligible_prefixes': sum(bool(p.get('eligible')) for p in prefixes), 'matched_pairs': pairs,
           'unknown_calls': [{'call_id': c['call_id'], 'identity': c['identity'], 'diagnostic': c.get('diagnostic'),
                              'retained_reservation': c['reserve_credits']} for c in unknown],
           'affected_missing_episodes': missing, 'accounting': {k: v for k, v in analysis['accounting'].items() if k != 'calls'},
           'control_calibration': analysis['control_calibration'], 'continuation': analysis['continuation'],
           'calibration_assessment': {
               'control_target': [0.4, 0.75],
               'cells_above_target': sum(cell[arm]['success_rate'] > 0.75 for cell in analysis['control_calibration'] for arm in ('K', 'F')),
               'control_cells': 12,
               'scope': 'point estimates from the fixed cohort; small cells and retained missingness; no exclusions or task retuning',
               'quality_ceiling': True,
               'memory_zero_bootstrap_interval_is_not_equivalence': True,
               'further_harder_task_calibration': 'unperformed; requires a separate freeze and new task identities',
           },
           'analysis_sha256': sha(analysis), 'execution_sha256': sha(execution), 'independent_audit_sha256': sha(audited),
           'conclusion_scope': 'constructed development tasks; post-observation failure-handling amendment; no confirmatory/native-compaction/actual-charge claim'}
save_new(folder / 'cumulative_diagnostics.json', summary)


def pct(value):
    return 'unidentified' if value is None else f'{100 * value:+.2f} pp'


lines = ['# V5 cumulative live results after the continuation amendment', '',
         f"All {len(execution['jobs'])} jobs have final dispositions; {summary['remaining_global_stop_jobs']} remain unstarted under a global stop. "
         f"The allocation has {len(known)} metered completions and {len(unknown)} unresolved dispatches, including eight excluded calibration completions. "
         'Every original receipt is preserved and no admitted identity is repeated.', '',
         'The user explicitly amended global failure handling after the first stopped phase. The 48 tasks, three tracks, '
         'Luna medium, four workers, fresh-thread access contract, action limits and cumulative allocation are unchanged. '
         'Independent replay validates all received generations, outcomes, shared states, metering and fixed denominators.', '',
         '| Track | Complete R/K pairs | R successes | K successes | R minus K | Descriptive interval | Fixed-denominator bounds |',
         '|---|---:|---:|---:|---:|---|---|']
for track, paired in pairs.items():
    contrast = analysis['tracks'][track]['R_minus_K']
    interval = contrast['interval']
    interval_text = f"[{pct(interval['lower'])}, {pct(interval['upper'])}]" if interval else 'fewer than six pairs'
    bounds = contrast['fixed_denominator_missingness_bounds']
    lines.append(f"| {track} | {paired['complete_pairs']} | {paired['totals']['R'].get('successes', 0)} | "
                 f"{paired['totals']['K'].get('successes', 0)} | {pct(contrast['mean_difference'])} | {interval_text} | "
                 f"{('[' + pct(bounds[0]) + ', ' + pct(bounds[1]) + ']') if bounds else 'unidentified'} |")
lines += ['', 'Mechanism estimates condition on a naturally observed public mismatch; independent-policy and repeated-memory estimates '
          'use separately started episodes. Tracks reuse tasks and must not be pooled as independent trials. '
          'Unknown scores remain missing. Bootstrap intervals describe this constructed task distribution.', '',
          'No quality improvement is measured here. Only three prefixes provide conditional recovery pairs, below the six-pair interval '
          'threshold. All 48 memory R/K pairs pass in both arms: its zero bootstrap interval reflects the observed ceiling and '
          'does not establish population equivalence.', '',
          'All twelve K/F calibration-cell point estimates exceed the 40–75% target. Whole-policy K passes 46/47 known tasks '
          '(one missing) and F passes 47/48. Long control cells use a median of eight actions; K has about 2.1–2.6 KB of '
          'visible raw trial history at the median action. Thus the nominal long horizon does not create a strong quality or history '
          'burden in these families. A future harder cohort needs a separate freeze; this finding preserves the current ceiling.', '',
          '| Track | R input-token change on complete pairs | R output-token change | R planning-credit change |',
          '|---|---:|---:|---:|']
for track, paired in pairs.items():
    relative = paired['R_relative_to_K']
    formatted = ['unidentified' if relative[key] is None else f"{100 * relative[key]:+.2f}%"
                 for key in ('input_tokens', 'output_tokens', 'planning_credits')]
    lines.append('| ' + track + ' | ' + ' | '.join(formatted) + ' |')
lines += ['', 'These resource comparisons use the same complete-pair tasks. Common mechanism preparation is charged once and '
          'reported separately in the primary analysis. Planning credits are a calculation from observed tokens, not actual account charges.', '',
          f"Known usage: {analysis['accounting']['usage']['input_tokens']:,} input tokens, "
          f"{analysis['accounting']['usage']['cached_input']:,} cached input tokens and "
          f"{analysis['accounting']['usage']['output']:,} output tokens including "
          f"{analysis['accounting']['usage']['reasoning']:,} reasoning tokens. "
          f"Calculated known usage is {analysis['accounting']['planning_credits']} planning credits; "
          f"{analysis['accounting']['locked_planning_credits']} remain reserved for unknown dispatches.", '',
          'Read [primary analysis](live/analysis.json), [derived comparisons and control calibration](cumulative_diagnostics.json), '
          '[independent audit](launch_checks/live_audit_result.json), [amendment](../../rollback_development_v5_continuation/PROTOCOL.md) '
          'and the [immutable original phase](../rollback_development_v5_2026-10-08/LIVE_RUN.md). '
          'Human semantic error ratings remain unperformed; immutable provider revision, provider sampling seed and actual charges are unavailable.']
path = folder / 'LIVE_RUN.md'
with path.open('x', encoding='utf-8', newline='\n') as stream:
    stream.write('\n'.join(lines) + '\n')
print(json.dumps({'tasks': len(tasks), 'metered_generations': len(known), 'unknown': len(unknown),
                  'pairs': {k: v['complete_pairs'] for k, v in pairs.items()}, 'model_calls': 0}, sort_keys=True))
