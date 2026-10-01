# Actual workflow intake for the next comparison

October 1, 2026. This is collection preparation, not a new model launch or a
claim that the twelve untouched evaluation episodes have been acquired.

## Collection stream

The next local development task is this user-requested evidence-use investigation.
Record its actual offline test/validate/build commands at two committed source
checkpoints. The source change between those checkpoints is the ongoing research
implementation/documentation work, not a fabricated incident. No failure quota
is required. Source commits, command order, return codes, raw output hashes and
artifact bindings accompany every receipt. Source snapshots must remain fixed
during each command. Preserve failed and incomplete checkpoints.

The collector has exactly three allowlisted offline commands. It refuses dirty
sources and existing destinations and writes new raw observations only beneath
ignored `build/`. No API or historical dataset recovery script is run. Verify
the raw files before moving a completed checkpoint to a new committed evidence
directory. Do not rewrite an existing historical capture.

```powershell
python -m experiments.dependency_memory.evidence_use.observe build/evidence-use-observed/A --episode evidence-use-investigation --checkpoint A
# Continue the actual task, then commit its next source milestone.
python -m experiments.dependency_memory.evidence_use.observe build/evidence-use-observed/B --episode evidence-use-investigation --checkpoint B
```

This is one **familiar inspected local development episode**, even with two
snapshots, six commands and multiple later query scopes. It cannot fill a private
held-out slot. Its data and source commits are available to the implementer.
Byte-limited handoffs remain an imposed intervention; no model intervention has
yet run on this episode. Correct ordinary checks are allowed to be easy controls.

## Held-out collection requirements

For the proposed evaluation, keep the existing
[source intake and split rules](../workflow_eval/PROTOCOL.md#source-intake-and-split):
four actual development and twelve actual evaluation change tasks, consecutive
eligible intake, whole-task splits, failed/short/easy tasks retained, exclusions
recorded before method outputs, and two declared handoff checkpoints per task.
The remaining tasks must come from an actual recorded task stream. Authored
fixture scenarios, reductions of old mistakes and repeated variants of this
task do not create new independent episodes.

An evaluator who does not tune the actor must own the raw evaluation traces,
grader manifests and access log outside the actor/implementer workspace. A hash
or a directory named `private` does not provide isolation. Record the actual
inspection history. No such private source stream is available in the current
repository, so its held-out count remains zero. Acquire the stream before
constructing a full launch; do not substitute synthetic tasks to fill the quota.

## Prospective question and screening decision

Separate raw final-answer quality, retained-evidence consistency, a veto/abstention
outcome and any corrected/executed outcome. The current typed interpreter has
hand-written rule contracts; unfamiliar-workflow inference remains a distinct
candidate implementation. Count correct answers lost to abstention as well as
wrong actions blocked. A coverage/provenance token would be extra admitted state
with a byte count and checked lineage, not a free evaluator attestation.

Keep the existing five arms, byte caps and public information order. Add the
same separately charged final check to every arm in a new versioned protocol.
The final check may use only its own admitted evidence. A repair call needs a
frozen prompt, budget and accounting; an archive read is an explicit access arm.
Apply the existing practical screen against both direct and indexed controls:
no extra false-ready answers, and either at least two more successes at no
greater fully priced cost, or equal success with at least 20% lower fully priced
cost, under both cache views. This is a small-study decision, not significance.

Pin model/revision, actual serialization, isolation, request identities, token
limits, transport policy, usage reservations and a new bounded allocation only
after data/grader/implementation freeze. Old interrupted allocations and missing
answers remain closed. The present work makes zero model calls and assigns no
new provider budget.
