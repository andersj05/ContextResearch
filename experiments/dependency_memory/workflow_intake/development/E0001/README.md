# E0001: actual evidence-use research task

October 1, 2026. Inspected local development evidence from ContextResearch,
captured during this user-requested research phase. One whole task, two source
checkpoints, six allowlisted command runs; no new model experiment.

| Checkpoint | Source commit | Actual commands | Outcome |
|---|---|---|---|
| [A](A/capture.json) | `eeec3340fad02dc6220a8ee39c0d633840452720` | Unit suite, repository validator, paper build | All exit zero; 430 tests pass, 37 cited sources |
| [B](B/capture.json) | `f9a951186d4177e881d8bad3c5e7db526765eee8` | Unit suite, repository validator, paper build | All exit zero; 434 tests pass, 39 cited sources |

The source changed through actual research writing and single-repository intake
implementation. No failure was manufactured. Only the two collector windows
enter the reporting contract. Earlier and interim uncaptured commands are
excluded; the six recorded runs are not a complete developer-session transcript.

Each command retains exact stdout/stderr bytes, return code, argument vector,
elapsed time, run identity and source tree. Fourteen files are pinned in the
[chronological ledger](../../ledger.json). The original generated artifact
copies were hash-verified in ignored local capture storage before registration;
their receipt hashes are committed, while the previews remain ignored.

The [evaluator manifest](../../evaluator/E0001.json) reconstructs a ready answer
for B's source and artifact inventory. It does not certify subsequent writing or
registration revisions at another tree. Direct receipt memory uses 728 parent
bytes and 1,455 child bytes and retains both snapshots under the unchanged
4,096/1,536-byte caps. These are memory serialization bytes, excluding external
public instructions and task state. They are not model token counts or a total
request-cost measurement. This is an easy direct-record control.

Both source checkpoints and all observations have been inspected by the author
and implementer. Future prospective evaluation and independent blind evaluation
remain separate evidence classes. No actual byte-limited actor, consistency
veto or repaired execution has been run on this episode.

```powershell
python -m experiments.dependency_memory.workflow_intake.packet
```
