"""Explicit serialized actor views; this pure interface is not a process sandbox."""
from copy import deepcopy

PARENT_CAP, CHILD_CAP = 4096, 1536
PUBLIC_FIELDS = ("check", "snapshot", "run_id", "returncode", "artifacts", "argv", "stdout", "stderr")


def public_records(records):
    return [{k: deepcopy(row[k]) for k in PUBLIC_FIELDS} for row in records]


def actor_view(episode, stage, previous_memory=None):
    """Never return labels, storage paths, timings, inspection logs or Git access."""
    if stage == "parent":
        if previous_memory is not None:
            raise ValueError("No previous memory at first boundary")
        return {"tool_observations": public_records(episode["initial"])}
    cap = PARENT_CAP if stage == "child" else CHILD_CAP
    if not isinstance(previous_memory, str) or len(previous_memory.encode("utf-8")) > cap:
        raise ValueError("Previous memory is invalid or exceeds its UTF-8 byte cap")
    if stage == "child":
        return {"previous_memory": previous_memory, "new_observations": public_records(episode["between"]),
                "scope": deepcopy(episode["scope"])}
    if stage == "final":
        return {"memory": previous_memory, "final_public_state": {
            key: deepcopy(episode["task"][key]) for key in ("snapshot", "required_checks", "artifacts")}}
    raise ValueError("Unknown boundary")
