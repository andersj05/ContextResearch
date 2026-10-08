"""Small official app-server stdio client; credentials stay inside Codex."""
import os
import queue
import subprocess
import threading
import time

from ..records import strict_loads, wire


class ProtocolError(RuntimeError):
    pass


class AppServer:
    def __init__(self, executable, cwd, overrides, timeout=45):
        command = [str(executable), "app-server", "--stdio"]
        for override in overrides:
            command.extend(("-c", override))
        blocked = {"OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN", "OPENAI_BASE_URL"}
        env = {key: value for key, value in os.environ.items() if key.upper() not in blocked}
        self.process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.timeout, self.next_id, self.closed = timeout, 0, False
        self.queue, self.notifications = queue.Queue(maxsize=512), []
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        try:
            while line := self.process.stdout.readline(16 * 1024 * 1024 + 1):
                if len(line) > 16 * 1024 * 1024:
                    self.queue.put({"fatal": "oversized_protocol_event"})
                    return
                try:
                    value = strict_loads(line.decode("utf-8"))
                    if type(value) is not dict:
                        raise ValueError()
                    self.queue.put(value)
                except (ValueError, UnicodeError):
                    self.queue.put({"fatal": "invalid_protocol_json"})
                    return
        finally:
            self.queue.put({"fatal": "appserver_closed"})

    def send(self, value):
        try:
            self.process.stdin.write((wire(value) + "\n").encode("utf-8"))
            self.process.stdin.flush()
        except (OSError, ValueError) as error:
            raise ProtocolError("appserver_write_failed") from error

    def receive(self, timeout=None):
        try:
            message = self.queue.get(timeout=self.timeout if timeout is None else timeout)
        except queue.Empty as error:
            raise ProtocolError("appserver_timeout") from error
        if "fatal" in message:
            raise ProtocolError(message["fatal"])
        if "method" in message and "id" in message:
            # No approval, tool, user-data or credential reply is ever supplied.
            raise ProtocolError("unexpected_server_request")
        return message

    def rpc(self, method, params):
        self.next_id += 1
        number = self.next_id
        self.send({"id": number, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            message = self.receive(max(.01, deadline - time.monotonic()))
            if message.get("id") == number:
                if "error" in message:
                    # Provider messages may echo sensitive context; retain codes only.
                    raise ProtocolError(f"rpc_error:{method}:{message['error'].get('code')}")
                if "result" not in message:
                    raise ProtocolError("rpc_missing_result")
                return message["result"]
            self.notifications.append(message)
            if len(self.notifications) > 1024:
                raise ProtocolError("unexpected_rpc_event_volume")
        raise ProtocolError("rpc_timeout")

    def initialize(self):
        result = self.rpc("initialize", {"clientInfo": {"name": "contextresearch_rollback", "version": "1"},
            "capabilities": {"experimentalApi": True}})
        self.send({"method": "initialized"})
        return result

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        for handle in (self.process.stdin, self.process.stdout):
            handle.close()
