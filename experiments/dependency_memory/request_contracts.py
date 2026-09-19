"""Route approved public request contracts to their strict serializers.

Adding a version here does not permit arbitrary model input. Each contract
owns its complete field, instruction, schema, and visible-information checks.
The original pilot serializer is reused without re-encoding its output.
"""
from __future__ import annotations


def request_bytes(request: dict) -> bytes:
    """Serialize exactly one approved contract, rejecting unknown versions."""
    if type(request) is not dict or type(request.get("version")) is not str:
        raise ValueError("Public request must declare an approved contract version")
    version = request["version"]
    if version == "pilot_public_request_v1":
        from pilot_interface import request_bytes as serialize
    elif version == "revision_parent_request_v1":
        from revision_interface import request_bytes as serialize
    else:
        raise ValueError("Unknown public request contract")
    return serialize(request)
