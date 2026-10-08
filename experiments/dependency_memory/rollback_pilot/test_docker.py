"""Opt-in actual isolated-runtime checks; no model or benchmark corpus access."""
import os
import subprocess
import unittest

from .code_runner import DockerRunner, STREAM_CAP
from .fixtures import code_example
from .grading import CodeChecker


IMAGE = os.environ.get("ROLLBACK_E0_DOCKER_IMAGE")


@unittest.skipUnless(IMAGE, "set ROLLBACK_E0_DOCKER_IMAGE to a locally available audited digest for isolated integration checks")
class DockerIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = DockerRunner(IMAGE)
        cls.audit = cls.runner.audit()

    def test_reference_passes_full_frozen_authored_suite_and_wrong_program_fails(self):
        task, evaluator, _, branch, *_ = code_example()
        checker = CodeChecker(self.runner)
        self.assertEqual(checker.grade(task, evaluator, {"code": evaluator.data()["reference_code"]})["score"], 1)
        self.assertTrue(checker.receipt(task, branch.data()["artifact"]).eligible)
        self.assertEqual(checker.grade(task, evaluator, branch.data()["artifact"])["score"], 0)

    def test_nonroot_readonly_no_host_files_or_credentials_and_no_external_network(self):
        source = """import os,socket
assert os.getuid()==65534
assert 'OPENAI_API_KEY' not in os.environ
assert 'ROLLBACK_HOST_CANARY' not in os.environ
assert not os.path.exists('/workspace') and not os.path.exists('/var/run/docker.sock')
assert sorted(os.listdir('/scratch'))==['input','submission.py']
try:
    open('/root/undeclared','w').write('bad')
except OSError:
    pass
else:
    raise AssertionError('writable root')
try:
    open('/tmp/undeclared','w').write('bad')
except OSError:
    pass
else:
    raise AssertionError('writable base filesystem')
sock=socket.socket();sock.settimeout(0.3)
try:
    sock.connect(('1.1.1.1',443))
except OSError:
    pass
else:
    raise AssertionError('external network reachable')
print('isolated')
"""
        previous = os.environ.get("ROLLBACK_HOST_CANARY")
        os.environ["ROLLBACK_HOST_CANARY"] = "host-only-authored-canary"
        try:
            result = self.runner.execute(source, "one-input-only\n")
        finally:
            if previous is None:
                os.environ.pop("ROLLBACK_HOST_CANARY")
            else:
                os.environ["ROLLBACK_HOST_CANARY"] = previous
        self.assertEqual((result.status, result.stdout.strip()), ("completed", "isolated"), result.stderr)

    def test_each_test_has_fresh_scratch(self):
        first = self.runner.execute("open('/scratch/marker','w').write('prior candidate')\nprint('first')", "")
        second = self.runner.execute("import os\nassert not os.path.exists('/scratch/marker')\nprint('fresh')", "")
        self.assertEqual(first.status, "completed")
        self.assertEqual((second.status, second.stdout.strip()), ("completed", "fresh"))

    def test_public_syntax_runtime_and_wall_timeout_never_qualify_as_mismatch(self):
        task = code_example()[0]
        checker = CodeChecker(self.runner)
        for source, status in (("def broken(:\n", "syntax_error"), ("raise ValueError('authored runtime error')", "runtime_error")):
            receipt = checker.receipt(task, {"code": source})
            self.assertEqual(receipt.data()["status"], status)
            self.assertFalse(receipt.eligible)
        result = self.runner.execute("import time\ntime.sleep(60)", "", wall_seconds=3)
        self.assertEqual(result.status, "timeout")

    def test_cpu_memory_pids_and_cpu_allocation_are_enforced_in_runtime(self):
        source = """import resource
assert resource.getrlimit(resource.RLIMIT_CPU)==(5,5)
assert int(open('/sys/fs/cgroup/memory.max').read())==512*1024*1024
assert int(open('/sys/fs/cgroup/pids.max').read())==32
quota,period=map(int,open('/sys/fs/cgroup/cpu.max').read().split())
assert quota==period
print('bounded')
"""
        result = self.runner.execute(source, "")
        self.assertEqual((result.status, result.stdout.strip()), ("completed", "bounded"), result.stderr)
        spin = self.runner.execute("while True: pass", "")
        self.assertEqual(spin.status, "timeout")

    def test_process_limit_denies_excess_children_and_tears_them_down(self):
        source = """import subprocess,sys
children=[]
try:
    for i in range(40):
        children.append(subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']))
except OSError:
    print('process limit')
finally:
    for child in children: child.kill()
    for child in children: child.wait()
"""
        result = self.runner.execute(source, "")
        self.assertEqual((result.status, result.stdout.strip()), ("completed", "process limit"), result.stderr)

    def test_stdout_and_stderr_each_have_bounded_capture(self):
        for stream in ("stdout", "stderr"):
            result = self.runner.execute(f"import sys\nsys.{stream}.write('x'*70000)\nsys.{stream}.flush()", "")
            self.assertEqual(result.status, "output_limit")
            self.assertLessEqual(len(result.stdout.encode()), STREAM_CAP)
            self.assertLessEqual(len(result.stderr.encode()), STREAM_CAP)

    def test_invalid_utf8_is_not_silently_normalized_into_correct_output(self):
        result = self.runner.execute("import os\nos.write(1,b'\\xff')", "")
        self.assertEqual(result.status, "runtime_error")

    def test_candidate_cannot_leave_a_container_running_after_completion(self):
        result = self.runner.execute("print('done')", "")
        self.assertEqual(result.status, "completed")
        listing = subprocess.run(["docker", "ps", "--filter", "name=rollback-e0-", "--format", "{{.Names}}"],
                                 capture_output=True, timeout=15, check=True)
        self.assertEqual(listing.stdout.strip(), b"")
