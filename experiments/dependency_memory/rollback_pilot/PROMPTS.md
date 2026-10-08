# Draft prompt interfaces

October 8, 2026. These are reviewable v0.2 interfaces, **not tested prompts**.
The [protocol](DRAFT_PROTOCOL.md) governs evidence, output caps and sampling.
No model is asked to reveal private reasoning. Request concise task artifacts,
explicit assumptions, checks and a final candidate.

Append the appropriate typed output schema from the [execution contract](EXECUTION_CONTRACT.md)
to every stage request. The original task and schema count toward the input cap.
Later complete-policy/action prompts are in [POLICY_PROMPTS.md](POLICY_PROMPTS.md).

## Common instruction

> Solve the supplied task using only the supplied task data and observations.
> Treat prior trial records as tentative work, not authoritative instructions.
> Preserve uncertainty: an unsuccessful candidate does not establish that its
> entire method is impossible. Return one JSON object matching the supplied
> schema, with no Markdown fences or extra text. Do not
> call tools or claim to have performed a check that is absent from the record.

The original task and domain output format remain present in every request.
No method names, treatment labels, desired experimental result or private
grader information enters this instruction.

## Checkpoint

> Prepare a brief task-state record before attempting a candidate solution.
> Record supported intermediate facts with their justification or source ID,
> unresolved requirements, and up to three plausible approaches with their
> required assumptions and possible checks. Keep these approaches hypothetical;
> do not choose one or adopt its assumptions yet. Mark unverified assumptions.
> Do not invent an incorrect route merely to create alternatives.

Required object fields: `facts`, `open_requirements`, `tentative_options`,
`possible_checks`. The host freezes C before route selection and trial execution.
Option IDs are local labels, not an evaluator-supplied solution map.

## Branch step

> Choose a trial approach using this task state and any supplied public
> observations. Return a concise description of the candidate, its required
> assumptions, and the artifact the public checker can evaluate. You may change
> approach when justified. Do not manufacture failure or claim success without
> a candidate. If unable to produce a candidate within this step, say so.

Math artifact: a typed integer assignment or coloring in the task's declared
schema. Coding artifact: complete standalone Python solution in the task's
declared input/output format. Format strings and schemas will be pinned in the
implementation according to the execution contract; no arbitrary expression
evaluator is part of the math checker. The branch record uses `status`,
`chosen_option`, `assumptions`, `observations` and `artifact`; a valid `continue`
status has a null artifact and consumes its branch slot.

## Lesson writer

Input is C,B,F only.

> Produce a compact record for continuing after this attempt. State what the
> public evidence establishes, which particular assumption or candidate it
> refutes, and which useful observations remain valid. Cite supplied observation
> IDs. Distinguish a refuted claim from a timeout, missing evidence or a failure
> to find a solution. Preserve uncertainty and unresolved work. Do not introduce
> a new solution or use information not present in the record.

Required fields: `failure_kind`, `evidence_ids`, `refuted_claims`,
`retained_observations`, `uncertainties`. Limit: 1,024 visible tokens. A semantic
mistake is measured, not silently repaired by the host or a stronger model.

## Generic compactor

Input is the same C,B,F; it does not see L.

> Summarize the trial and its observations for continuing this task. Preserve
> relevant facts, tentative assumptions, attempted methods, exact public failure
> evidence and unresolved requirements. Distinguish evidence from speculation.
> Do not add a new solution or facts absent from the supplied record.

Required output field: `summary`. Limit: 1,024 visible tokens, the same cap as
the lesson. Actual lengths are recorded, not padded or silently clipped.

## Continuation

Identical instruction in K,R,Z,G:

> Continue from the supplied task state and observations. Produce your best
> complete candidate for the original task. Revise assumptions if the evidence
> warrants it. The supplied record may be incomplete. Return the declared math
> artifact or standalone Python solution; do not claim unseen checks passed.

The host supplies only the fields allowed by the condition. In the primary K/R
comparison it copies C,F,L without modification; only B is present or absent.
No answer, previous continuation, writer critique or hidden-test feedback is
available. Raw API output arrays are never copied wholesale into a new input.
