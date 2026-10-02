"""One existing codec algorithm for every projected contract; no value dictionary."""
from experiments.dependency_memory.scope_inference import codec
from experiments.dependency_memory.workflow_replay import evidence


def schema(contract):
    contract = codec.validate(contract)
    if "$" in contract["value_paths"]:
        return None
    result = {}

    def add(path, leaf):
        parts, node = path.split("."), result
        for key in parts[:-1]:
            if key in node and node[key] is None:
                return
            node = node.setdefault(key, {})
        if parts[-1] not in node or leaf is None:
            node[parts[-1]] = leaf

    for field in ("presence_paths", "value_paths"):
        for path in sorted(contract[field]):
            add(path, None)
    for path in sorted(contract["nonempty_paths"]):
        add(path + "." + codec.MARKER, None)
    return result


def encode(record, contract, public_schema):
    return evidence.encode_fields(codec.project(record, contract), public_schema)


def decode(memory, public_schema):
    return evidence.decode_fields(memory, public_schema)
