"""Preserve scoped checks and honest full-suite/recheck accounting."""
from pathlib import Path
import shutil
from experiments.dependency_memory.rollback_development_v5.common import read, save_new, sha

root = Path('experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08')
checks = root / 'launch_checks'
for stem in ('v5-continuation-scoped-tests-1', 'v5-continuation-scoped-tests-2', 'v5-continuation-scheduler-tests'):
    for suffix in ('.json', '.txt'):
        source = Path('tmp') / (stem + suffix)
        target = checks / source.name
        if target.exists():
            raise ValueError('preserve existing check evidence')
        shutil.copyfile(source, target)
for name in ('run_v5_recorded.py', 'run_v5_cont_repository_tests.py', 'recheck_v5_cont_tests.py'):
    shutil.copyfile(Path('tmp') / name, checks / name)
full = read(checks / 'repository_tests.json')
recheck = read(checks / 'repository_tests_exact_recheck.json')
assert full['exit_code'] == 1 and recheck['exit_code'] == 0
save_new(checks / 'test_reconciliation.json', {
    'evidence_kind': 'offline_test_reconciliation', 'model_calls': 0,
    'distinct_repository_tests': 754, 'full_run_passed': False,
    'full_run_passing_tests': 752, 'full_run_errors': 2,
    'error_kind': 'PermissionError WinError 5 during atomic file replacement',
    'rechecked_unchanged_tests': [
        'cross_record_continuation.test_continuation.ContinuationTests.test_full_suffix_dry_run_without_model_or_original_mutation',
        'test_development_pilot.DevelopmentPilotTests.test_budget_reservation_and_failed_attempts_do_not_retry'],
    'exact_rechecks_passed': True, 'all_distinct_tests_have_passing_results': True,
    'docker_tests_passed': 9, 'continuation_tests_passed': 10, 'original_v5_tests_passed': 26,
    'failed_full_run_sha256': sha((checks / 'repository_tests.txt').read_bytes()),
    'exact_passing_recheck_sha256': sha((checks / 'repository_tests_exact_recheck.txt').read_bytes()),
    'manifest_sha256': sha(read(root / 'prepared/manifest.json')),
    'earlier_scoped_error_preserved': 'report comparison used Python equality rather than canonical JSON equality; repaired and rechecked',
    'unresolved_test_assertion_failures': 0,
})
print('754 distinct tests have passing results; original failures and unchanged exact rechecks preserved')
