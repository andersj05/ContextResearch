# A JSON capacity failure disappears under the existing public schema

October 1, 2026. Separate offline control added before any scope-inference model
generation. The [eight-call launch](../experiments/dependency_memory/scope_inference/PROTOCOL.md)
is frozen at `313a877`; automatic approval review initially rejected dispatch.
The user subsequently approved this specific eight-call launch. At this offline
control milestone zero calls have been dispatched. Its sources and
requests remain unchanged.

The [new control](../experiments/dependency_memory/scope_codebook_control.py) uses
the existing `workflow_replay.evidence` fixed-schema codec without changing it.
It preserves the same exact record identity and original public classifier as
the prelaunch controls. The public schema is fixed independently of the record
values; it is not an extra instance-dependent channel or a new compression method.

| Encoding/control | Parent bytes | Child bytes over six worker pairs | Exact late queries |
|---|---:|---:|---:|
| Authored field projection as ordinary JSON | 3,030 | 1,432–1,599 | 12/24 |
| Same authored fields with existing fixed-schema codec | 1,957 | 949–1,009 | 24/24 |
| Cached public-program outcomes | 1,539 | 761–779 | 24/24 |
| Conservative whole root fields | 23,741; infeasible | Empty parent | 0/24 |
| Raw records | 55,031; infeasible | Empty parent | 0/24 |

The limits stay at 4,096/1,536 UTF-8 bytes. Three ordinary-JSON child tables fail
admission, while every fixed-schema/cached state fits. A missing parent cannot
be reconstructed from the evaluator's original records. Exact request hashes
remain necessary for a matching final query. The packed projection and original
classifier agree on all 14,505 constructed catalog rows, including repeated
rows; there are 14,490 distinct inputs. Three additional tests check all delayed
queries, source deletion/identity binding and absence/nonempty preservation.
[Certificate](../experiments/dependency_memory/results/scope_codebook_control_2026-10-01.json). [C58]

These are imposed timing/encoding controls on eight inspected historical records,
not eight new natural tasks or model outcomes. The plain JSON failure is not an
information-theoretic capacity obstruction. Field selection, dictionary coding
and cached outcomes must all be strong baselines; none is claimed novel here.
Local CPU/elapsed time is recorded separately, without fully priced lifecycle
cost or measured production savings.

The useful research target remains an automatically obtained complete contract
when later query demands cannot cheaply be precomputed. A known single function
admits the strong cached-outcome control. Changing that information order or
query family needs its own protocol; these findings do not authorize silently
altering the already frozen learner test.
