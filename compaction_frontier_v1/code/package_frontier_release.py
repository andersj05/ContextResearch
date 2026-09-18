#!/usr/bin/env python3
"""Create and integrity-check a deterministic ZIP of the frontier release."""
from __future__ import annotations

import hashlib
import json
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release" / "compaction_frontier_v1"
ARCHIVE = ROOT / "release" / "compaction_frontier_v1.zip"
FIXED_TIME = (2026, 8, 12, 0, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    temporary = ARCHIVE.with_suffix(".zip.tmp")
    temporary.unlink(missing_ok=True)
    ARCHIVE.unlink(missing_ok=True)
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
        for path in sorted(RELEASE.rglob("*")):
            if not path.is_file():
                continue
            relative = Path(RELEASE.name) / path.relative_to(RELEASE)
            info = zipfile.ZipInfo(str(relative), FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            info.create_system = 3
            handle.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    os.replace(temporary, ARCHIVE)
    with zipfile.ZipFile(ARCHIVE) as handle:
        assert handle.testzip() is None
    digest = sha256(ARCHIVE)
    sidecar = ARCHIVE.with_suffix(ARCHIVE.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {ARCHIVE.name}\n")
    print(json.dumps({"archive": str(ARCHIVE), "bytes": ARCHIVE.stat().st_size, "sha256": digest}, indent=2))


if __name__ == "__main__":
    main()
