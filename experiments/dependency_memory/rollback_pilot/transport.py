"""Scripted transport only. This module cannot contact a model provider."""
from dataclasses import dataclass

from .accounting import Usage
from .contexts import Request


class UnknownDispatch(RuntimeError):
    pass


@dataclass(frozen=True)
class Response:
    text: str
    usage: Usage | None
    capped: bool = False
    metadata: tuple = ()


class FakeTransport:
    transport_id = "scripted-e0-no-network-no-model-calls"

    def __init__(self, script):
        self.script = script
        self.calls = []

    def generate(self, identity, request: Request):
        if identity.key in {row[0] for row in self.calls}:
            raise UnknownDispatch("duplicate fake dispatch")
        self.calls.append((identity.key, request.hash))
        value = self.script(identity, request)
        if isinstance(value, BaseException):
            raise value
        if type(value) is Response:
            return value
        return Response(value, Usage(request.input_units, request.input_units, 0, 0,
                                    len(value.encode("utf-8")), 0))
