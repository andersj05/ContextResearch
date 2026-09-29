# Observed workflow evaluation packet

This is an offline, reviewable evaluation packet for real repository handoffs.
Start with the [protocol](PROTOCOL.md). The packet contains one observed local
development capture, a terminal grader, exact prompts, an integrity lock and
negative controls. It contains **no model results or dispatch implementation**.

```powershell
python -m experiments.dependency_memory.workflow_eval.packet
python -m unittest experiments.dependency_memory.workflow_eval.test_packet -v
```

The preflight checks the saved raw command outputs and graded development
example without rerunning the source commands. All paths/hashes in the saved
capture refer to the recorded historical snapshot, not the current checkout.
Generated HTML and Markdown previews are not committed; their hashes are
preserved in the observed build receipt. Only the output of the three named
offline commands is retained, not an unrestricted agent/session transcript.

`grader.py` determines expected terminal answers from the complete observation
ledger independently of any memory method. `packet.py` also constructs a
hand-written direct projection to report whether it fits the proposed caps;
that is a feasibility diagnostic, not an automatic extraction result.
`test_packet.py` uses explicitly mutated development observations to check stale
revision, later-failure and artifact-mismatch behavior. Those mutations are not
real recorded incidents and do not fill held-out slots.

The saved capture's source commit can be checked out separately to rerun its
three argv lists. Exact durations and unittest timing text will vary; a rerun
is a new observation, not a replacement of the original. Execution return codes
and expected build contents should agree in the declared environment. Source
snapshotting here uses the Git tree and a clean-worktree check; it does not
capture the OS, Python binary, ignored files or arbitrary installed packages.
Those channels need a fuller capture and isolation contract at launch.

To freeze a deliberate packet revision after review:

```powershell
python -m experiments.dependency_memory.workflow_eval.packet --write-lock
```

The lock is an integrity commitment, not authentication or evidence of unseen
data. The normal preflight only reads. A revision requires a recorded decision
and a new version before evaluation; do not use lock regeneration to hide a
changed historical result. See [current status](../../../docs/STATUS.md) for the
remaining intake, implementation and launch work.
