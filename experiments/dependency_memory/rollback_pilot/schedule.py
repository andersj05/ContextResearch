"""Stable slots; missing arms never shift another call's identity."""
from .accounting import Identity
from .contexts import ARMS
from .records import digest


def ordered_tasks(tasks):
    groups = {domain: sorted((t for t in tasks if t.domain == domain),
                            key=lambda t: (digest(f"rollback-v02|20261007|{t.task_id}"), t.task_id))
              for domain in ("math", "coding")}
    result = []
    for index in range(max(map(len, groups.values()), default=0)):
        for domain in groups:
            if index < len(groups[domain]):
                result.append(groups[domain][index])
    return result


def writer_order(domain_index):
    return ("lesson", "summary") if domain_index % 2 == 0 else ("summary", "lesson")


def terminal_order(domain_index):
    offset = domain_index % 4
    first = ARMS[offset:] + ARMS[:offset]
    return [(arm, 1) for arm in first] + [(arm, 2) for arm in reversed(first)]


def task_slots(launch_id, task, domain_index):
    return [Identity(launch_id, task.task_id, "checkpoint"),
            Identity(launch_id, task.task_id, "branch", slot=1),
            Identity(launch_id, task.task_id, "branch", slot=2),
            *(Identity(launch_id, task.task_id, kind) for kind in writer_order(domain_index)),
            *(Identity(launch_id, task.task_id, "terminal", slot=draw, arm=arm, draw=draw)
              for arm, draw in terminal_order(domain_index))]
