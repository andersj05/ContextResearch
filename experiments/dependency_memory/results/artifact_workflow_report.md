# Artifact workflow: deterministic development results

September 18, 2026. Generated from 320 constructed configurations (8 seeds, 2 revision conditions, 5 settings, 4 scripted policies). These are not independent LLM trials or a powered benchmark.

Each table cell shows terminal successes out of 16 and mean synthetic action units. Failed episodes remain in cost accounting. Memory is capped in receipt records at two boundaries; bytes are recorded separately. The [CSV](artifact_workflow.csv) includes the recent-record baseline and every configuration.

| Setting | Structured, never inspect | Structured, always inspect | Structured, budgeted inspection |
|---|---|---|---|
| tight_cheap | 9/16; 10 units | 16/16; 11 units | 16/16; 11 units |
| ample_cheap | 16/16; 10 units | 16/16; 11 units | 16/16; 10 units |
| tight_expensive | 9/16; 10 units | 16/16; 18 units | 9/16; 10 units |
| tight_unavailable | 9/16; 10 units | 9/16; 11 units | 9/16; 10 units |
| child_too_small | 7/16; 10 units | 8/16; 11 units | 8/16; 11 units |

The tight/cheap case demonstrates the intended information-timing mechanism. With ample first-stage memory, structured retention succeeds without inspection. Expensive inspection exposes a cost/success tradeoff: the budgeted heuristic declines it and loses some successes. An unavailable clue cannot help, and an insufficient second-stage record capacity still loses obligations after early inspection.

The [paired witness](artifact_workflow_witness.json) is a separate hand-constructed regression fixture. Both continuations receive the same early clue and start from the same saved environment and context. Recent retention loses job-1 at boundary 1 and fails only when the delayed receipt is submitted; structured retention succeeds at the same action cost. This witness was not automatically minimized.

These outcomes establish expected behavior of this environment and these fixed policies. They do not establish a new policy's general superiority, theorem-optimal bit compression, API cost savings, or performance against native compaction. See the [information contract](../ARTIFACT_WORKFLOW.md).
