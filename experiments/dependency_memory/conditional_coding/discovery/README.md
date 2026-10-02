# Preserved adaptive discovery

These files are byte copies of the actual October 2 scratch search, not a
pre-registered experiment or a held-out evaluation. Compiled executables and
uncontrolled session logs are excluded. [metadata.json](metadata.json) pins
the files, original C59 upstream hash/commit, compiler, caps and observed clocks.

| Source | Raw output | Scope and outcome |
|---|---|---|
| [search.c](search.c), [base.h](base.h) | [discovery.jsonl](discovery.jsonl) | Original product plus three seeded one-bit-perturbed starts; eight modal updates each, nine scored steps. All fail to beat the original product. Original three-block modal control is stationary. |
| [swap.c](swap.c) | [swap.jsonl](swap.jsonl) | Complete native conditional single-word screen on the original product, 4,096 slots times 4,096 replacements. Selected gain 5,202 loses to the stronger component refinement. |
| [control.c](control.c) | [control.jsonl](control.jsonl) | Repeats that screen, then finds an original three-block replacement with gain 8. |
| [warm.c](warm.c) | [warm.jsonl](warm.jsonl) | Eight modal updates after the original selected joint change; stationary and worse than the refined component product. |
| [refine.c](refine.c) | [refine.jsonl](refine.jsonl) | Repeats the original screen; four accepted component replacements with gains 8,2,2,3, then a complete native zero-gain single-word screen. Cap 16, stopped at 4. |
| [couple.c](couple.c), [refined.h](refined.h) | [couple.jsonl](couple.jsonl) | Same algorithm as swap.c with only the header changed. Refined product still has a joint replacement with gain 4,101. |
| [iterate.c](iterate.c) | [iterate.jsonl](iterate.jsonl) | Eight complete native conditional single-word screens and accepted changes. Final error 331,857,648. Cap 8 exhausted; final locality is unproved. |

For conditional screens, only the best replacement/gain per slot is retained,
not every rejected candidate's numerical score. The Python certificate checks
every accepted loss/gain with separate grouped minima and performs the entire
final three-block replacement screen independently. It does not independently
recompute every rejected conditional score or certify that native greedy
choices are globally best in their neighborhoods. The resulting upper bounds
and product counterexample require the checked selected constructions only.

The two preserved preparers record the original scratch layout; their relative
paths assume that layout. They are historical provenance, not package commands.
The headers are independently regenerated from the untouched upstream and
refinement record by the certificate. A native rerun is optional: compile the
chosen C source beside these headers with Clang 19.1.0 and the recorded flags.
Ordinary tests/validation never execute the C search.

The PRNG is deterministic xorshift32 (shifts 13,17,5), seeds 0..3; seed 0 is the
product. Each nonzero start tests random_next()%8==0 to flip one of 12 response
bits. All sources are the same finite uniform population, not independent
training/test trials. Recorded Windows C clock readings are not portable
latency or independently measured process wall time. control.c/refine.c invoke
an inner old screen whose clock excludes subsequent work. No model, provider
budget, session, archive or natural workflow is involved.
