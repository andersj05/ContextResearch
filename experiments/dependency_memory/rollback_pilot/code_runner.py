"""Digest-pinned Docker executor. Never falls back to a host Python process.

Candidate containers receive one test input and their source only. Expected
outputs and private suites stay in the external checker. The container launcher
is trusted orchestration, not a security proof about Docker or its host kernel.
"""
from __future__ import annotations

import base64
import json
import re
import subprocess
import threading
import time
import uuid

from .grading import ExecutionResult, InfrastructureError
from .records import digest, strict_loads


STREAM_CAP = 65536
HOST_CAP = 196608
LAUNCHER = r'''
import base64,json,os,resource,signal,subprocess,sys,threading,time
payload=json.load(sys.stdin)
code=payload['code']; input_data=base64.b64decode(payload['stdin_base64'])
result={'status':'completed','stdout_base64':'','stderr_base64':'','elapsed_seconds':0.0}
try:
    compile(code,'/scratch/submission.py','exec')
except SyntaxError as exc:
    result.update(status='syntax_error',stderr_base64=base64.b64encode(str(exc).encode()[:65536]).decode())
    print(json.dumps(result,separators=(',',':'))); sys.exit(0)
with open('/scratch/submission.py','w',encoding='utf-8') as stream:
    stream.write(code)
with open('/scratch/input','wb') as stream:
    stream.write(input_data)
def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(5,5))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
buffers=[bytearray(),bytearray()]; overflow=threading.Event()
def read(stream,index):
    while True:
        data=stream.read(4096)
        if not data: break
        available=65536-len(buffers[index])
        buffers[index].extend(data[:max(0,available)])
        if len(data)>available: overflow.set()
start=time.monotonic()
with open('/scratch/input','rb') as inp:
    process=subprocess.Popen([sys.executable,'-I','/scratch/submission.py'],stdin=inp,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             cwd='/scratch',env={'PATH':'/usr/local/bin:/usr/bin:/bin','LANG':'C.UTF-8'},
                             start_new_session=True,preexec_fn=limits)
    threads=[threading.Thread(target=read,args=(stream,index),daemon=True)
             for index,stream in enumerate((process.stdout,process.stderr))]
    for thread in threads: thread.start()
    while process.poll() is None:
        if overflow.is_set() or time.monotonic()-start>payload['wall_seconds']:
            result['status']='output_limit' if overflow.is_set() else 'timeout'
            os.killpg(process.pid,signal.SIGKILL); break
        time.sleep(0.005)
    process.wait()
    # Descendants holding pipes must not survive completion of the candidate.
    try: os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError: pass
    for thread in threads: thread.join(timeout=0.5)
    if any(thread.is_alive() for thread in threads):
        result['status']='runtime_error'
    if overflow.is_set(): result['status']='output_limit'
    if result['status']=='completed' and process.returncode:
        result['status']='timeout' if process.returncode in (-signal.SIGXCPU,-signal.SIGKILL) else 'runtime_error'
result.update(stdout_base64=base64.b64encode(buffers[0]).decode(),stderr_base64=base64.b64encode(buffers[1]).decode(),
              elapsed_seconds=time.monotonic()-start)
print(json.dumps(result,separators=(',',':')))
'''


class DockerRunner:
    def __init__(self, image, executable="docker"):
        if not re.fullmatch(r"[a-zA-Z0-9./:_-]+@sha256:[0-9a-f]{64}", image):
            raise InfrastructureError("coding runtime must be pinned by an image digest")
        self.image, self.executable = image, executable

    def configuration(self):
        return {"image": self.image, "python_required": "3.11", "cpu_allocation": 1, "memory_mib": 512,
                "pids": 32, "cpu_seconds_per_test": 5, "wall_seconds_per_test": 10,
                "suite_wall_seconds": 120, "stdout_bytes": STREAM_CAP, "stderr_bytes": STREAM_CAP,
                "scratch_mib": 16, "network": "none", "user": "65534:65534", "read_only": True,
                "host_mounts": [], "launcher_sha256": digest(LAUNCHER)}

    def command(self, name):
        return [self.executable, "run", "--rm", "--pull", "never", "--name", name, "-i",
                "--network", "none", "--read-only", "--user", "65534:65534", "--cap-drop", "ALL",
                "--security-opt", "no-new-privileges", "--memory", "512m", "--memory-swap", "512m",
                "--pids-limit", "32", "--cpus", "1", "--ulimit", "nofile=64:64", "--ipc", "none",
                "--tmpfs", "/scratch:rw,noexec,nosuid,size=16m,mode=1777", "--workdir", "/scratch",
                "--entrypoint", "python3", self.image, "-I", "-c", LAUNCHER]

    def audit(self):
        try:
            version = subprocess.run([self.executable, "version", "--format", "{{json .}}"], capture_output=True, timeout=15, check=True)
            image = subprocess.run([self.executable, "image", "inspect", self.image], capture_output=True, timeout=15, check=True)
        except (OSError, subprocess.SubprocessError) as exc:
            raise InfrastructureError("Docker engine or pinned local image is unavailable") from exc
        result = self.execute("import sys; print(sys.version.split()[0])", "")
        if result.status != "completed" or not result.stdout.startswith("3.11."):
            raise InfrastructureError("runtime did not report the required Python 3.11")
        inspected = strict_loads(image.stdout.decode())[0]
        if inspected["Config"].get("Volumes"):
            raise InfrastructureError("image declares undeclared volumes")
        # Default image environment is public runtime configuration, never host env.
        if any(not entry.startswith(("PATH=", "LANG=", "PYTHON_VERSION=", "PYTHON_SHA256=", "GPG_KEY="))
               for entry in inspected["Config"].get("Env", [])):
            raise InfrastructureError("image declares an unaudited environment variable")
        return {"configuration": self.configuration(), "docker_version": strict_loads(version.stdout.decode()),
                "image_id": inspected["Id"], "repo_digests": inspected.get("RepoDigests", []),
                "runtime_python": result.stdout.strip(), "image_environment": inspected["Config"].get("Env", [])}

    def execute(self, code, stdin, wall_seconds=10):
        if type(code) is not str or type(stdin) is not str or not 0 < wall_seconds <= 10:
            raise InfrastructureError("invalid isolated execution parameters")
        name = "rollback-e0-" + uuid.uuid4().hex
        payload = json.dumps({"code": code, "stdin_base64": base64.b64encode(stdin.encode()).decode(),
                              "wall_seconds": wall_seconds}, ensure_ascii=True).encode()
        buffers = [bytearray(), bytearray()]
        overflow = threading.Event()
        try:
            process = subprocess.Popen(self.command(name), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as exc:
            raise InfrastructureError("Docker is unavailable; host execution is forbidden") from exc

        def reader(stream, index):
            while True:
                data = stream.read(4096)
                if not data:
                    break
                remaining = HOST_CAP - len(buffers[index])
                buffers[index].extend(data[:max(0, remaining)])
                if len(data) > remaining:
                    overflow.set()

        def writer():
            try:
                process.stdin.write(payload)
                process.stdin.close()
            except (BrokenPipeError, OSError):
                pass

        threads = [threading.Thread(target=reader, args=(stream, index), daemon=True)
                   for index, stream in enumerate((process.stdout, process.stderr))]
        threads.append(threading.Thread(target=writer, daemon=True))
        for thread in threads:
            thread.start()
        start = time.monotonic()
        timed_out = False
        try:
            while process.poll() is None:
                if overflow.is_set() or time.monotonic() - start > wall_seconds:
                    timed_out = not overflow.is_set()
                    break
                time.sleep(0.01)
        finally:
            if process.poll() is None:
                try:
                    removed = subprocess.run([self.executable, "rm", "--force", name], capture_output=True, timeout=15)
                    if removed.returncode and b"No such container" not in removed.stderr:
                        raise InfrastructureError("candidate teardown could not be verified")
                except (OSError, subprocess.SubprocessError) as exc:
                    raise InfrastructureError("candidate teardown failed") from exc
                finally:
                    process.kill()
            process.wait(timeout=10)
            for thread in threads:
                thread.join(timeout=1)
            process.stdout.close()
            process.stderr.close()
        elapsed = time.monotonic() - start
        if overflow.is_set():
            return ExecutionResult("output_limit", elapsed_seconds=elapsed)
        if timed_out:
            return ExecutionResult("timeout", elapsed_seconds=elapsed)
        if process.returncode:
            raise InfrastructureError("isolated launcher failed: " + buffers[1].decode(errors="replace")[:512])
        try:
            data = strict_loads(buffers[0].decode())
            if set(data) != {"status", "stdout_base64", "stderr_base64", "elapsed_seconds"}:
                raise ValueError("launcher envelope fields")
            if data["status"] not in {"completed", "syntax_error", "runtime_error", "timeout", "output_limit"}:
                raise ValueError("launcher status")
            stdout, stderr = [base64.b64decode(data[key], validate=True) for key in ("stdout_base64", "stderr_base64")]
            if max(len(stdout), len(stderr)) > STREAM_CAP:
                raise ValueError("launcher exceeded a stream cap")
            try:
                return ExecutionResult(data["status"], stdout.decode("utf-8"), stderr.decode("utf-8"), elapsed)
            except UnicodeDecodeError:
                return ExecutionResult("runtime_error", stderr="Candidate emitted invalid UTF-8.", elapsed_seconds=elapsed)
        except (ValueError, TypeError, KeyError) as exc:
            raise InfrastructureError("invalid isolated launcher result") from exc
