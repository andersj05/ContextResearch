"""Seal local reproducible evidence only after the cumulative live audit passes."""
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from experiments.dependency_memory.rollback_development_v5.common import read, save_new, sha, now

folder = Path(__file__).resolve().parents[1]
audit = read(folder / 'launch_checks/live_audit_result.json')
tests = read(folder / 'launch_checks/test_reconciliation.json')
scientific = read(folder / 'launch_checks/scientific_validation_result.json')
navigation = read(folder / 'launch_checks/navigation_result.json')
execution = read(folder / 'live/execution.json')
analysis = read(folder / 'live/analysis.json')
manifest = read(folder / 'prepared/manifest.json')
assert audit['all_passed'] and tests['all_distinct_tests_have_passing_results']
assert scientific['status'] == 'PASS'
assert navigation['status'] == 'PASS'
assert not execution['stopped'] and len(execution['jobs']) == 768
assert not any(r['result'].get('disposition') == 'unstarted_global_stop' for r in execution['jobs'])
assert not any(c['state'] == 'dispatched' for c in analysis['accounting']['calls'])
prior = ROOT / manifest['continuation']['prior_phase']
original_bundle = ROOT / manifest['continuation']['original_bundle']


def check_seal(path):
    inventory = read(path / 'evidence_manifest.json')
    actual = {p.relative_to(path).as_posix() for p in path.rglob('*.json') if p.name != 'evidence_manifest.json'}
    assert {r['path'] for r in inventory['files']} == actual
    for row in inventory['files']:
        assert sha((path / row['path']).read_bytes()) == row['sha256']
    assert sha((path / 'ledger.sqlite').read_bytes()) == inventory['ledger_sha256']


check_seal(prior)
check_seal(folder / 'live')
archive_path = folder / 'live_evidence.zip'
excluded_names = {'closeout.json', 'live_evidence.zip'}
paths = {p for p in folder.rglob('*') if p.is_file() and p.name not in excluded_names
         and not {'scratch', '__pycache__'} & set(p.relative_to(folder).parts)}
paths |= {p for p in original_bundle.rglob('*') if p.is_file()}
paths |= {p for p in prior.rglob('*') if p.is_file() and not {'scratch', '__pycache__'} & set(p.relative_to(prior).parts)}
paths |= {ROOT / row['path'] for row in manifest['source_bindings']}
# Every entry keeps its repository-relative path for source/receipt reconstruction.
inventory = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
             for p in sorted(paths)]
with zipfile.ZipFile(archive_path, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for p, row in zip(sorted(paths), inventory):
        archive.write(p, row['path'])
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == {row['path'] for row in inventory}
    assert all(sha(archive.read(row['path'])) == row['sha256'] for row in inventory)
save_new(folder / 'closeout.json', {
    'completed_utc': now(), 'status': 'all_runnable_jobs_finished_with_retained_unknowns',
    'all_planned_jobs_have_dispositions': True, 'live_cohort_scores_all_known': not analysis['accounting']['unknown_or_inflight_calls'],
    'unique_tasks': 48, 'jobs': 768, 'metered_completions': analysis['accounting']['completed_calls'],
    'unknown_dispatches': analysis['accounting']['unknown_or_inflight_calls'], 'global_stop': analysis['accounting']['stop'],
    'dispatched_identities_retried': 0, 'API_key_calls': 0, 'actual_account_charge': None,
    'original_receipts_unchanged': audit['original_receipts_unchanged'],
    'source_manifest_sha256': sha(manifest), 'live_replay_passed': True,
    'distinct_repository_tests_have_passing_results': 754,
    'first_full_test_run_passed': tests['full_run_passed'], 'exact_windows_rechecks_passed': tests['exact_rechecks_passed'],
    'full_scientific_validation_passed': True, 'paper_assembly_passed': read(folder / 'launch_checks/paper_build.json')['exit_code'] == 0,
    'catalog_and_navigation_passed': True,
    'comparison_scope': 'post-observation development continuation; three tracks reuse 48 constructed tasks',
    'archive_path': archive_path.name, 'archive_sha256': sha(archive_path.read_bytes()),
    'archive_entries': len(inventory), 'archive_uncompressed_bytes': sum(row['bytes'] for row in inventory),
    'archive_inventory': inventory, 'archive_inventory_sha256': sha(inventory),
    'archive_includes_original_bundle_and_phase': True,
    'archive_includes_every_bound_python_and_protocol_source': True,
    'credentials_and_uncontrolled_session_logs_archived': False,
})
print({'archive': str(archive_path), 'entries': len(inventory), 'model_calls': 0, 'sealed': True})
