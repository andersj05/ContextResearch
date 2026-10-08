"""A source replay must never extract outside its workspace snapshot."""
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

from scripts.verify_rollback_math_v4 import ROOT, extract_sources


def payload(name,kind=tarfile.REGTYPE):
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as archive:
        member=tarfile.TarInfo(name);member.type=kind
        if kind==tarfile.REGTYPE:member.size=6;archive.addfile(member,io.BytesIO(b'source'))
        else:member.linkname='../outside';archive.addfile(member)
    return stream.getvalue()


class ReplayTests(unittest.TestCase):
    def temporary(self):
        root=ROOT/'tmp/replay_tests';root.mkdir(parents=True,exist_ok=True)
        result=tempfile.TemporaryDirectory(dir=root);self.addCleanup(result.cleanup);return Path(result.name)

    def test_regular_source_bytes_preserved(self):
        root=self.temporary();extract_sources(payload('experiments/package/module.py'),root)
        self.assertEqual((root/'experiments/package/module.py').read_bytes(),b'source')

    def test_traversal_absolute_and_links_rejected_before_extraction(self):
        for name,kind in (('../outside',tarfile.REGTYPE),('/outside',tarfile.REGTYPE),('link',tarfile.SYMTYPE)):
            with self.subTest(name=name,kind=kind):
                root=self.temporary()
                with self.assertRaises(ValueError):extract_sources(payload(name,kind),root)
                self.assertEqual(list(root.iterdir()),[])


if __name__=='__main__':unittest.main()
