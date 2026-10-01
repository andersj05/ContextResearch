# Workflow evidence in one repository

October 1, 2026. The user chose **ContextResearch as the sole working repository**.
Keep method development, task observations, evaluator truth and result analysis
in separate segments. Existing frozen studies stay in their original locations.

| Segment | Location | Access and evidence role |
|---|---|---|
| Method implementation and retrospective diagnostics | [Evidence-use package](../evidence_use/README.md) | Inspected development evidence and hand-written public-rule interpreters. |
| Actual development task observations | `development/E0001/`, then consecutive task IDs | Raw allowlisted command outputs, source commits, receipts and artifact hashes. |
| Future prospective tasks | [Prospective intake](prospective/README.md) | Append actual eligible whole tasks after method freeze; record exclusions and inspection. |
| Evaluator manifests | [Evaluator segment](evaluator/README.md) | Complete observation grading and labels; excluded from serialized actor requests. |
| Actor input construction | [views.py](views.py) | Only the admitted memory and observations permitted at each boundary. |
| Chronological bookkeeping | [ledger.json](ledger.json) | Task-level sequence, checkpoint completeness, inspection and immutable file hashes. |
| New model outcomes | Separate future result directory | Unperformed; no new provider allocation or call. |

Folders organize evidence. Access is enforced by the actual request/runner:
fresh serialized model contexts, no repository tools/filesystem/Git, no evaluator
labels, no undeclared history or opaque state, and declared archive arms only.
The pure view functions are trusted interfaces, not process sandboxes. Provider
and physical isolation must be checked again before a launch.

An implementer who has read a task cannot call it a blind held-out task. A future
same-repository comparison can be **prospective observed evaluation** if its
method and grader are frozen before consecutive eligible tasks arrive. Record
who inspected each task and do not tune on its scores. Independent blind review
would require actual role/access separation even within this one repository;
no such independence is claimed for today's local development episode.

Do not generate artificial change tasks just to fill twelve slots. Capture actual
user-requested research work as it occurs, with failed, short and easy tasks kept
in the denominator. Two checkpoints, reruns, branch variants or query mutations
of one task remain one episode. Report this repository as one workload family.

The first episode is the current evidence-use investigation. Checkpoint A records
the implementation milestone; checkpoint B records the subsequent real research,
writing and intake changes. Earlier unrecorded commands are outside the capture
window. Only the two declared collector windows enter this reporting contract;
interim development commands are excluded. Every captured receipt is retained,
including failed runs. No failure was manufactured.
Generated artifact bytes remain in ignored local capture storage, while their
receipt hashes and controlled command output are committed. This respects the
repository rule excluding generated previews from Git.

[Episode E0001](development/E0001/README.md) is registered: six actual successful
commands at source commits `eeec334` and `f9a9511`. Direct receipt memory is 728
parent bytes and 1,455 child bytes, fitting the existing 4,096/1,536 caps. This
episode remains development evidence and an easy direct-record control. There
are zero prospective evaluation episodes and zero new model calls.

```powershell
python -m experiments.dependency_memory.workflow_intake.packet
```

The packet validates observation hashes and reconstructs the evaluator manifest.
It is not a model launcher. The old packet's private twelve-episode criterion
remains unassessed. A new same-repository protocol, complete intake, independent
grader review, priced resource table and bounded allocation precede any claim
of terminal improvement or total-cost benefit.
