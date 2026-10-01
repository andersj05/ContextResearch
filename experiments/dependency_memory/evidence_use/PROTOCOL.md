# Retained evidence and final decisions — retrospective protocol v1

October 1, 2026. This is a new **post-hoc offline study**, designed after inspecting
the historical results. It is not preregistration of unseen model outcomes.

## Question and selected evidence

When a final answer is wrong, does the admitted evidence support the correct
decision? Can a deterministic interpreter of the already public reporting rules
identify a contradiction in that answer without reading the evaluator's ledger?

Include every scheduled terminal identity in these three recent studies:

- September 22 cross-record original and continuation: 288 terminal identities,
  eight arms, twelve constructed histories and three correlated futures each.
- September 29 observed-workflow development comparison: 20 terminal identities,
  five arms, one observed local capture and three constructed continuations.
- September 29 executed-workflow original and continuation: 60 terminal
  identities, five arms and twelve authored scenarios with actual command outputs.

The selection is by study, not by error or arm. Earlier early-retention studies,
release-gate pilots and schema-transfer studies are outside this first audit.
Preserve transport failures and never-dispatched identities as separate outcomes.
Do not create answers for them, retry them, rescore the historical studies, or
claim that their missing primary comparisons are restored. Pin input bytes in a
separate source lock before implementing the new interpreter.

## Actor and evaluator information

The actor-facing check receives exactly a saved final request and proposed
answer. It can read the admitted `memory`, the public target/late event or final
snapshot/artifact inventory, and the public rule already in that request. Its
pure implementation must not import graders, truth functions, archives, episode
files, schema extractors or model clients. The rule compiler is hand-written;
automatic discovery of contracts from unfamiliar workflows is unperformed.

The evaluator separately reconstructs the frozen historical requests and uses
the original independent graders to assess raw answers and interpreter outputs.
Full ledgers, private truth rows and intermediate memories are evaluator-only.
Hindsight probes of parent memory are diagnosis, not inputs to a new actor run.
A format that cannot be parsed is **unknown**, not proof of semantic loss. Empty
memory is reported separately. Any manually read prose example must retain its
memory hash and exact reviewed statement; this is not automatic prose checking.

## Intervention and limitations

Compile only the receipt reporting rule and the three public cross-record rules
(retry queue, CI promotion, data pipeline). Use strict JSON and typed, unique
field paths, exact owner selection, exact identifiers and late-event application
before decision predicates. Apply the same entry point to every arm.

Return `consistent`, `contradicted` or `uncheckable`. A contradiction can veto a
proposal; an uncheckable result abstains. Report correct proposals rejected or
abstained on as well as wrong proposals detected. Separately grade the derived
answer as a **counterfactual deterministic readout**, not a new LLM answer or
measured repair. No correction call, automatic deployment or archive lookup occurs.

Consistency with retained evidence does not authenticate that evidence or prove
coverage of the original history. Test a missing-later-failure counterexample:
the same admitted successful receipt is compatible with a successful history
and a history containing an omitted later failure. A check restricted to that
receipt and identical public state cannot distinguish them. An assertion of
complete coverage would be an additional information channel, requiring its own
provenance, bytes and prospective validation. Do not silently supply one here.

## Outputs and validation

Record study/arm/identity, missing disposition, original correctness, retained
evidence diagnosis, check status, changed answer fields and separately graded
derived answer. Summarize by study and arm; pooled counts are bookkeeping, not
independent samples. Preserve historical model costs and all writer calls; no
new provider calls or credits are allocated. Measure new local CPU, elapsed time
and byte traffic separately with a batched benchmark. Do not infer dollars or
total-cost superiority from unpriced resources.

Tests must include independent public-rule execution comparisons, omission and
forgery controls, scope/revision/artifact invalidation, duplicate paths and keys,
ambiguous owners, event timing, correct-answer vetoes and missing dispositions.
Recompute the report from pinned evidence in the repository validator. Run the
standard offline test/validate/build workflow.

## Prospective follow-up

Use the [observed-workflow intake design](../workflow_eval/PROTOCOL.md#source-intake-and-split)
for actual consecutive change tasks. This audit's inspected histories remain
development data. The twelve untouched episodes, independent grader review,
contract inference and a complete bounded model launch remain separate work.
Any next study must count abstentions, check cost and archive access, and retain
direct records, indexed recovery, strong prose and full history as controls.
