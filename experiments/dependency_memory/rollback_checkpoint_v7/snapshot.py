"""Offline replay using the bound source bytes, never for live dispatch."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import zipfile

from .common import ROOT, read, sha


def audit_snapshot(bundle, folder):
    bundle, folder = Path(bundle).resolve(), Path(folder).resolve()
    manifest = read(bundle / "manifest.json")
    if sha(manifest) != read(bundle / "bundle.json")["manifest_sha256"]:
        raise ValueError("manifest changed")
    archive_path = bundle / "source_snapshot.zip"
    if sha(archive_path.read_bytes()) != manifest["snapshot_sha256"]:
        raise ValueError("snapshot changed")
    parent = ROOT / "tmp" / "rollback-v7-snapshot-replay"
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as directory:
        destination = Path(directory).resolve()
        if not destination.is_relative_to(parent.resolve()):
            raise ValueError("unsafe replay directory")
        with zipfile.ZipFile(archive_path) as archive:
            if set(archive.namelist()) != {r["path"] for r in manifest["source_bindings"]}:
                raise ValueError("snapshot inventory changed")
            for row in manifest["source_bindings"]:
                data = archive.read(row["path"])
                target = (destination / row["path"]).resolve()
                if not target.is_relative_to(destination) or sha(data) != row["sha256"]:
                    raise ValueError("unsafe or changed snapshot entry")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        script = ("import sys,json; sys.path.insert(0,sys.argv[1]); "
                  "from experiments.dependency_memory.rollback_checkpoint_v7.audit import audit; "
                  "print(json.dumps(audit(sys.argv[2],sys.argv[3]),sort_keys=True))")
        result = subprocess.run([sys.executable, "-I", "-c", script, str(destination), str(bundle), str(folder)],
                                cwd=destination, capture_output=True, text=True, check=True,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return {**json.loads(result.stdout), "source": "verified historical snapshot",
                "source_snapshot_sha256": manifest["snapshot_sha256"]}
