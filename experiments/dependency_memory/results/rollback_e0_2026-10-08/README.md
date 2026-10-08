# Rollback E0 evidence, October 8, 2026

**Controlled offline engineering only. Zero model calls and USD 0 provider spend.**
Start with the [finding](../../../../research/ROLLBACK_E0_IMPLEMENTATION_2026-10-08.md)
or [short report](report.md). The [package README](../../rollback_pilot/README.md)
provides runnable commands and access boundaries.

| Artifact | Contents |
|---|---|
| [summary.json](summary.json) | Acceptance, 12 math tasks, 144 scripted calls, 210,656 checked finite candidates and open live gates |
| [package_checks.json](package_checks.json) | All 66 package tests, including nine actual Docker tests, with durations and source hashes |
| [math_certificates.json](math_certificates.json) | Independently enumerated feasibility sets and exact grader agreement |
| [analysis.json](analysis.json) | All-task flow, every arm, task-level differences, secondary intersections, missingness and synthetic accounting |
| [scripted_controller/](scripted_controller/) | Exact sanitized requests, typed responses, common preparations, public/evaluator task files, terminal grades and durable event history |
| [launch_review/manifest.json](launch_review/manifest.json) | Source/task/prompt/runtime bindings and explicit unsatisfied live launch gates |
| [launch_review/calibration_requests.jsonl](launch_review/calibration_requests.jsonl) | Eight frozen disclosed E1 requests; these have not been sent to a model |
| [archive_manifest.json](archive_manifest.json) | Complete result-file inventory and verifier hash |

The fake solver intentionally constructs rejected branches and returns known
answers. Those outcomes validate implementation and analysis; they cannot support
a model-performance claim. Its USD 0.0478070 figure is synthetic billing arithmetic
using byte units and the review's rates. It is not actual spend.

The coding runtime is exercised on an authored sum fixture and isolation probes.
There are zero selected LiveCodeBench tasks in this packet. The missing coding
cohort, live endpoint/tokenizer/access checks, pricing calibration and new launch
allocation remain explicit gates. E3/E4/E5 remain separate unperformed designs.

Saved files are immutable. For a new run use a new output identity, then register
its evidence before committing. Read-only verification:

```powershell
python scripts/verify_rollback_e0.py --directory experiments/dependency_memory/results/rollback_e0_2026-10-08
```
