# Schema-derived checks on new tool-result traces

September 22, 2026. Freeze this protocol, the case generator, schemas, and
terminal grader before developing the extractor or inspecting evaluation values.
These are newly constructed, executable tool-result traces, not observed
production incidents. Development seeds 41011/41012 and evaluation seeds
94121/94122 are disjoint within each of retry handling, CI handoff, and
multi-stage data jobs. Two late continuations per evaluation trace make 12 paired
terminal cases. The trace generator itself is public. Evaluation identities and
outcomes do not enter extractor development or memory-writing prompts.

The tool schemas supply `format: opaque-id`, `x-reference`, and `x-ephemeral`
annotations. The automatic method may use those annotations and same-stage tool
results, but no workflow-specific field list, evaluation target, grader output,
or late event before the applicable boundary. A schema without those annotations
has unknown coverage; this study cannot establish extraction from arbitrary raw
prose. The exact-ID check compares every annotated value. The relation check
compares each reference's owner and field path with its value. Both checks reject
loss or reassociation; a failed check cannot be called a safe memory.

All arms see identical initial tool results and public rules. At boundary one,
only a 2,600-byte memory survives. The pair is disclosed; at boundary two, only
1,300 bytes survive. The target and late event then arrive. No arm may read an
original result after boundary two except the indexed-recovery arm, which pays
for the selected original record. Full history is supplied again as an explicit
costed information control. Fresh model threads prevent provider history and
reasoning state from bridging boundaries. No archive or evaluator file is visible
to the decision model. A missing or malformed decision is a terminal failure.

Methods are: stronger data-first prompting (two model memory writes), automatic
schema extraction and the two local checks (no memory-writing model calls),
hand-written direct records, indexed recovery, and full original history. All
five use the same final decision model and output schema. The direct records are
an explicitly authored ideal control; their human design cost is excluded and
will be reported as such. Prompt memory is byte clipped once with no retry.

Primary success requires **fewer exact terminal failures for automatic checks
than stronger prompting**, at **equal or lower total measured planning credits**
over all 12 paired evaluation decisions. A second required condition for saying
the checks *match hand-written records* is no more failures than direct records.
Report indexed and full controls even if they dominate. A failure of either
condition is a negative result. This finite, correlated constructed set does not
support a production or statistical superiority claim.

Count every model write and final decision, including failures; raw token usage,
cached inputs, output/reasoning, and wall time. Use the same dated published
GPT-6 Luna short-context planning rates as the prior pilot; keep account debit
unknown. Count extractor/check CPU, source bytes read, memory bytes written, and
indexed recovered bytes separately. The preregistered experimental total adds
measured model planning credits, **0.0001 credit per measured local CPU second**,
and **0.00000001 credit per archive byte retrieved or full-history byte read**.
These two local prices are synthetic sensitivity assumptions, not a measured
provider bill; report the components and the break-even CPU price as well. Final
decisions use `gpt-6-luna`, medium reasoning and the prior audited fresh-thread
transport. Cap the new launch at 80 dispatched calls and 10 planning credits;
the fixed schedule has 72 calls (12 memory writes and 60 decisions). No retries,
model fallback, purchases, resets, or expansion based on outcomes. Stop on
transport/accounting uncertainty. Save exact public requests, answers, usage,
model alias, preflight, hashes, and completion status. Use no evaluation answers
to change extractor, prompt, cap, grader or case set.
