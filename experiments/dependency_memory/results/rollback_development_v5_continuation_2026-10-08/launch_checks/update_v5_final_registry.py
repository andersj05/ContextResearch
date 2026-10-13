"""Register the audited cumulative v5 result without creating independent trials."""
import csv
import json
from pathlib import Path

root = Path('experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08')
audit = json.loads((root / 'launch_checks/live_audit_result.json').read_text())
derived = json.loads((root / 'cumulative_diagnostics.json').read_text())
assert audit['all_passed'] and derived['remaining_global_stop_jobs'] == 0
path = Path('experiments/registry.csv')
with path.open(encoding='utf-8', newline='') as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
row = next(r for r in rows if r['study_id'] == 'rollback-development-v5')
row['status'] = 'completed'
row['as_of'] = '2026-10-09'
row['summary'] = (
    'User-authorized continuation finishes all 768 job dispositions on the same 48 tasks: '
    '2124 metered completions (eight excluded calibration) and four retained unknowns; no global stop or repeated identity. '
    'All R minus K quality means are zero: policy has 46 complete pairs (45 successes each; one R-only, one K-only, 44 ties), '
    'memory has 48 all-success pairs, and mechanism has three all-success pairs. Policy descriptive interval is [-6.52,+6.52] pp '
    'and fixed-denominator bounds are [-2.08,+2.08] pp. All twelve K/F calibration cells exceed the 40-75% target; the cohort '
    'has a strong ceiling. Independent cumulative replay/regrading reconciles every admitted call and disposition; all 754 '
    'distinct repository tests have passing results after two exact Windows rechecks, with nine Docker tests, full scientific '
    'validation and paper assembly passing.')
row['limitations'] = (
    'Failure handling and timing were amended after observations; original evidence and unknown reservation remain intact. '
    'Three eligible prefixes are below the six-pair interval threshold. A zero memory bootstrap interval reflects only observed '
    'all-success ties and is not equivalence. Marginal known rates approach 98-100%, and long controls usually use eight actions '
    'with only about 2-3 KB median raw history, limiting sensitivity. Four constructed families and reused tracks do not support '
    'family-generalization, deployed-harness or native-compaction claims. Known usage is 44.6089585 planning credits plus '
    '16.900 unresolved reservations; actual charges, immutable provider revision and sampling seed are unavailable. '
    'Harder-task calibration and human semantic ratings remain unperformed.')
new_entries = [
    'research/ROLLBACK_STAGED_CONTINUATION_2026-10-09.md',
    'experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/LIVE_RUN.md',
]
row['entry_points'] = ';'.join(new_entries + [p for p in row['entry_points'].split(';') if p not in new_entries])
with path.open('w', encoding='utf-8', newline='') as stream:
    writer = csv.DictWriter(stream, fields)
    writer.writeheader()
    writer.writerows(rows)
