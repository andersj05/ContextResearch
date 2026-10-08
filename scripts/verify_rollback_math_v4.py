"""Replay the immutable v4 verifier from its pre-outcome Git source commit.

This lets current documentation receive a link correction after execution while
retaining every original source hash and running the original verifier unchanged.
It never starts a model or changes the experiment's frozen allocation.
"""
import argparse
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT=Path(__file__).resolve().parents[1]
FROZEN_COMMIT='1e927f8'
PACKAGES=('experiments/dependency_memory/rollback_pilot',
          'experiments/dependency_memory/rollback_recovery_v3',
          'experiments/dependency_memory/rollback_math_followup_v4')


def extract_sources(payload,target):
    target=Path(target).resolve()
    with tarfile.open(fileobj=io.BytesIO(payload),mode='r:') as archive:
        for member in archive.getmembers():
            destination=(target/member.name).resolve()
            if not destination.is_relative_to(target) or not (member.isdir() or member.isfile()):
                raise ValueError('unsafe source archive member')
        # Avoid Python 3.14's Windows ALLOW_MISSING canonicalization problem.
        # All paths and member types were checked before the first write.
        for member in archive.getmembers():
            destination=target/member.name
            if member.isdir():destination.mkdir(parents=True,exist_ok=True)
            else:
                destination.parent.mkdir(parents=True,exist_ok=True)
                with archive.extractfile(member) as source,destination.open('xb') as output:
                    shutil.copyfileobj(source,output)


def replay(folder,output=None,regrade=False):
    folder=Path(folder).resolve()
    if not folder.is_relative_to(ROOT) or not (folder/'evidence_manifest.json').is_file():raise ValueError('closed workspace archive required')
    if output is not None:
        output=Path(output).resolve()
        if not output.is_relative_to(ROOT) or output.exists():raise ValueError('fresh workspace verification output required')
    commit=subprocess.check_output(['git','rev-parse',FROZEN_COMMIT],cwd=ROOT,text=True).strip()
    manifest_path=(folder/'manifest.json').relative_to(ROOT).as_posix()
    original_manifest=subprocess.check_output(['git','show',f'{commit}:{manifest_path}'],cwd=ROOT)
    if original_manifest!=(folder/'manifest.json').read_bytes():raise ValueError('pre-outcome immutable manifest mismatch')
    payload=subprocess.check_output(['git','archive','--format=tar',commit,'--',*PACKAGES],cwd=ROOT)
    scratch=ROOT/'tmp/rollback_math_v4_source_replay';scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        snapshot=Path(directory).resolve()
        if not snapshot.is_relative_to(scratch.resolve()):raise ValueError('source replay escaped scratch root')
        extract_sources(payload,snapshot)
        import json
        import hashlib
        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        for item in manifest['source_bindings']:
            source=(snapshot/item['path']).resolve()
            if not source.is_relative_to(snapshot) or source.is_symlink() or hashlib.sha256(source.read_bytes()).hexdigest()!=item['sha256']:
                raise ValueError('immutable source replay binding mismatch')
        command=[sys.executable,'-m','experiments.dependency_memory.rollback_math_followup_v4.verify','--folder',str(folder)]
        if regrade:command.append('--regrade')
        if output is not None:command.extend(('--output',str(output)))
        subprocess.run(command,cwd=snapshot,check=True)
    return {'replayed_source_commit':commit,'verified_source_files':len(manifest['source_bindings']),
            'model_calls':0,'original_verifier_unchanged':True,'regraded_in_Docker':regrade}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--folder',type=Path,required=True)
    parser.add_argument('--output',type=Path);parser.add_argument('--regrade',action='store_true');args=parser.parse_args()
    import json
    print(json.dumps(replay(args.folder,args.output,args.regrade)))
