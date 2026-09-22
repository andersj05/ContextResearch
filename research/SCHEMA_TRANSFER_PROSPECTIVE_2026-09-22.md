# Prospective transfer of cheap schema checks to new workflow structures

September 22, 2026. This is a second, separate experiment following the
[annotated-schema instance test](SCHEMA_CHECKS_UNSEEN_TRACES_2026-09-22.md).
The [casebook and grader](../experiments/dependency_memory/schema_transfer/casebook.py),
[protocol](../experiments/dependency_memory/schema_transfer/FROZEN_PROTOCOL.md),
and fixture hashes were committed at `7067963` before writing the generic
extractor. The [implementation and analysis code](../experiments/dependency_memory/schema_transfer/)
were frozen at `649bbc9` before the held-out structural preflight or any live
model response. The [saved-evidence analysis](../experiments/dependency_memory/results/schema_transfer_2026-09-22/analysis.json)
reconciles the fixed schedule; the [cost report](../experiments/dependency_memory/results/schema_transfer_2026-09-22/report.md)
is generated from it. No prior evaluation cases were changed or rerun.

## Design and information boundary

The user chose newly frozen traces because no suitable untouched retry, CI, or
data-job traces were present locally. Development uses escrow and package
schemas. Evaluation uses **different schema structures and obligations** for
retry queues, CI promotion, and multi-stage data pipelines. There are two
frozen traces per evaluation family, seven tool results per trace, and three
late continuations per trace. These are **constructed executable fixtures**, not
observed incidents or independent natural task samples. Opaque values, cases,
events, and exact terminal graders were fixed before the implementation.
The evaluation schema definitions were present in the frozen casebook and
visible to the implementer. The generic extractor contains no evaluation
family or field-list special case and was tested only on development fixtures
before its commit, but this is **not a blinded test of unknown schemas**.

At boundary one, 3,000 UTF-8 memory bytes may survive. Two candidates then
become visible. Boundary two permits 1,050 bytes. Only afterward does a target
and late event become visible. Every model call receives a fresh process and
thread under the previously audited managed-subscription transport. No prior
model response, source archive, provider session history, opaque reasoning, or
evaluator file is supplied to a compressed-memory final call. Indexed and full
history are separate, metered controls with declared recovery access.

The public schemas use ordinary JSON types, patterns, and enums; there are no
custom critical-field or reference annotations. The generic extractor detects
exact IDs from schema patterns/formats, field names, and opaque-looking result
values. It keeps enum and numeric/boolean state, while an unconstrained short
string with unknown identity role causes **unknown coverage**, not a safety
certificate. It projects owner records as a compact field/row table. One check
compares exact detected ID multisets; a second compares each owner's full
field-path-to-ID association, including an approval's artifact reference. The
second boundary check derives its source rows from the bounded parent only.
Development mutation tests show that an altered ID and a reference exchanged
between owners are rejected. Long free-form notes are excluded, and
unannotated status semantics are **not certified** by either narrow check.
The automatic arm checks its own deterministic table against the source, so
this is a serialization invariant rather than an independent proof that the
chosen fields are sufficient for every future obligation.

The six methods are strong prompted parent/child memories, a checked model
proposal with conservative fallback, automatic direct projection/checking,
hand-written direct records, indexed target recovery, and full history. The
checked and strong methods share each actual parent call, which is charged in
full to each hypothetical method. Every child writer, final decision, local
extraction/check/selection, indexed recovery, and source/memory read is charged.
The largest automatic parent and child were 2,372/3,000 and 932/1,050 bytes.
All six generic and direct projections fit without clipping. The structural
feasibility check was run only after implementation freeze and did not change
the schedule.

## Frozen matched comparison

All **126 scheduled GPT-6 Luna medium calls** completed. Saved usage is 462,071
input tokens (184,576 cached) and 41,326 output tokens (28,072 reasoning), or
**1.2564565 token-derived planning credits**. Actual attributable subscription
debit is unknown. Local work uses the prespecified synthetic conversion of
0.0001 credit per measured local second and 0.00000001 credit per locally read
byte. A high-resolution elapsed timer measures brief Python operations; it is
not a processor or production infrastructure bill. The manually authored
direct-control design cost is unmeasured.

| Method | Exact failures / 18 | Calls charged | Model credits | Experimental total credits |
|---|---:|---:|---:|---:|
| Strong prompt | 2 | 30 | 0.4382190 | 0.43840213083 |
| Checked model proposal | 2 | 30 | 0.4389930 | 0.44173514106 |
| Automatic direct | 1 | 18 | 0.1249000 | 0.12644885386 |
| Hand-written direct | 2 | 18 | 0.1162340 | 0.11684766975 |
| Indexed recovery | 0 | 18 | 0.1159625 | 0.11673546631 |
| Full history | 1 | 18 | 0.2084235 | 0.21004742428 |

The prespecified primary criterion is **met on these 18 paired cases**:
automatic direct has fewer failures than strong prompting (1 versus 2), lower
measured experimental cost (0.12644885386 versus 0.43840213083), and no more
failures than hand-written direct records (2). At the common prompt-cost
allowance, every method except checked proposal is eligible. Cache-neutral
input pricing preserves the automatic-versus-prompt cost order.

This positive criterion does **not** establish the candidate contribution as a
generally worthwhile memory mechanism. Indexed recovery gets **0 failures at a
lower experimental total (0.11673546631)** and therefore dominates automatic
direct in this finite comparison; it also costs less under cache-neutral input
pricing. Its storage and infrastructure costs remain unmeasured. The evaluation
is small, correlated, constructed, visible to the implementer at the schema
level, and conditional on a particular model alias, prompt, byte budget,
grader, and synthetic local prices. A one-error margin is
descriptive, not a population performance estimate or significance result.

## Failure and certificate diagnosis

The strong prompt's two failures occur on the same CI trace. Its child memory
proposed 1,392 bytes and was clipped once to 1,050, truncating facts for the
second candidate. Three of six strong child memories were clipped overall;
none of the parent memories were. This supports a concrete boundary-loss
explanation for the CI errors, without isolating clipping as the sole cause.

All six model-written parent proposals were prose, so the table-only checker
returned an explicit unstructured verdict and used the generic projection.
The checked child checker accepted two proposals and replaced four; the checked
method still failed two data-job finals and cost slightly more than prompting.
It was therefore mostly a test of conservative fallback, **not** evidence that
the check can certify arbitrary model-written prose.

The automatic arm's sole failure was a data-job final response that returned
`load.run` where the required target was `load.output_dataset`. The exact
output dataset and approval reference were present in the certified child
table. The checked method also made two data-job target mistakes despite
receiving the same certified fallback table. The hand-written direct arm's two
retry failures omitted `billing_scope` after a late attempt change even though
its retained record contained the billing reference. Full history made one
data-job work-set error. Indexed recovery made none. These are final-model
interpretation errors, not evidence that the corresponding retained table
omitted the required field. The narrow certificates cannot prevent them.

The next unperformed discriminating test should freeze external tool traces,
include real index creation/storage costs, and separate retention sufficiency
from final-model execution error with an independently specified executor. It
should also test schemas whose ID roles cannot be inferred from simple pattern
and field-name heuristics. No novelty or production cost advantage follows
from the present finite result alone.
