import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd()
out = root / 'build/evaluation_capture'
git = ['git', '-c', f'safe.directory={root.as_posix()}']
def read_git(*args):
    return subprocess.check_output(git + list(args), cwd=root).decode().strip()
if read_git('status', '--porcelain'):
    raise SystemExit('Capture requires a clean tracked/untracked working tree (ignored build output is allowed).')
snapshot = {'commit': read_git('rev-parse', 'HEAD'), 'tree': read_git('rev-parse', 'HEAD^{tree}')}
records = []
commands = [('tests', ['-m', 'unittest', 'discover', '-s', 'experiments/dependency_memory', '-v']),
            ('repository', ['scripts/validate_context_repo.py']),
            ('paper', ['scripts/build_paper.py'])]
for name, args in commands:
    start = time.perf_counter_ns()
    result = subprocess.run([sys.executable] + args, cwd=root, capture_output=True, timeout=600)
    elapsed = time.perf_counter_ns() - start
    row = {'check': name, 'argv': ['python'] + args, 'returncode': result.returncode,
           'elapsed_ns': elapsed, 'snapshot': snapshot['tree']}
    for field, raw in [('stdout', result.stdout), ('stderr', result.stderr)]:
        filename = f'{name}.{field}.txt'
        (out / filename).write_bytes(raw)
        row[field] = {'path': filename, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    row['artifacts'] = {}
    if name == 'paper' and result.returncode == 0:
        for path in ['build/paper/manuscript.md', 'build/paper/preview.html']:
            row['artifacts'][path] = hashlib.sha256((root / path).read_bytes()).hexdigest()
    row['run_id'] = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    records.append(row)
    print(name, result.returncode, round(elapsed / 1e9, 3), flush=True)
if read_git('status', '--porcelain'):
    raise SystemExit('Tracked inputs changed during capture; do not admit it.')
capture = {'version': 1, 'split': 'development', 'origin': 'observed_local_commands',
           'captured_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
           'source': snapshot, 'records': records,
           'limitations': ['Known repository and already inspected workflow.',
                           'Only command execution is observed; imposed memory boundaries and future changes are replay interventions.',
                           'Not externally sourced, held out, or a model-performance observation.']}
(out / 'capture.json').write_text(json.dumps(capture, indent=2) + '\n', encoding='utf-8')
