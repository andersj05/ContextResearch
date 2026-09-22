# Prospective transfer to new tool-schema structures

September 22, 2026. This is a **second, separate** study after the first
schema-check experiment returned 12/12 for every arm. Preserve that result and
do not rescore or tune its evaluation cases. This protocol, generator, graders,
and fixture hashes are frozen before implementing the second extractor or
seeing any second-study model response.

## Split and information order

Development uses escrow and package traces at seeds 52011/52012. Evaluation
uses different retry-queue, CI-promotion, and data-pipeline tool schemas at
seeds 97031/97032. Their 16-character opaque values differ. These are newly
constructed executable traces, not observed production incidents. Public JSON
schemas contain standard types, patterns, enums, booleans and descriptions;
there are **no** custom `x-reference`, critical-field, or ephemeral labels.
The implementation may be developed and checked against development cases only.
The evaluation families, values, late events, terminal graders and case hashes
are fixed here. A generic extractor must not contain evaluation family or field
names as special cases. The model must not see source truth, evaluator files or
future target/event before their scheduled disclosure.

Each trace has seven tool results. At boundary one, at most **3,000 UTF-8
bytes** of memory survive. Two candidates are then disclosed. At boundary two,
at most **1,050 bytes** survive. Only then is the target and one late event
revealed. There are three futures per evaluation trace: an irrelevant edit on
an initially invalid candidate, a relevant update there, and a gate-changing
update on an initially valid candidate. Six traces yield 18 paired terminal
cases. Later model calls use fresh processes/threads and receive no provider
history, opaque reasoning or undeclared archive. Indexed recovery receives the
selected original result, charged; full history receives all seven, charged.

## Methods and checks

- **Strong prompt:** the data-first memory writer makes parent and child
  summaries, then a final model decision. It knows that public rules repeat.
- **Checked proposal:** share the strong parent proposal, derive required exact
  IDs and owner/path/reference tuples from the currently available tool schema
  and result values, and conservatively replace an unverifiable proposal with
  a generic schema projection. A separate child writer reads the checked parent;
  the second check sees only that bounded parent. Charge the shared parent call
  fully to both hypothetical methods, all actual child calls, checks and copies.
- **Automatic direct:** the same generic projection/check without model memory
  writers. This isolates the value of writing a proposal.
- **Hand-written direct:** explicit family-specific critical records; its human
  design cost is unmeasured and reported as such.
- **Indexed:** costed target-record recovery after the second boundary.
- **Full:** fresh-thread final decision from all original tool results.

The first narrow check preserves every detected exact identifier byte-for-byte.
The second preserves the owner and full field path to each detected identifier,
including reference fields such as approval targets. If coverage cannot be
established from a schema/result, return unknown and count it; do not mark a
memory safe. Status and unannotated semantic conditions are outside the narrow
certificate. A conservative replacement must fit both byte caps; otherwise
record infeasibility, not silent clipping. The strong prompt memory alone is
prefix-clipped once with no reprompt, recording raw/admitted lengths.

The primary success criterion is fewer exact terminal failures for **automatic
direct** than strong prompting on the 18 paired evaluation cases, at equal or
lower total experimental cost, and no more failures than hand-written direct
records. The checked proposal is a separate secondary mechanism test. Report
all six arms, per-family failures, check verdicts, clipping, and cost frontiers
even if controls dominate or all arms tie. Do not tune caps, prompts, extractor,
fallback, grader or method order on evaluation outcomes.

## Cost and launch bound

Count every memory-writing and final model call (including malformed outputs),
cached/uncached input, output/reasoning, local extraction/check/selection CPU,
source/memory/archive bytes read, recovery, and wall time. Use a high-resolution
wall timer for brief local operations. The experimental total adds token-based
GPT-6 Luna medium planning credits, **0.0001 credit per local CPU second** and
**0.00000001 credit per locally read byte**. These local conversion rates are
synthetic, not observed provider billing. Report exact model usage and local
components separately, plus cache-neutral sensitivity and actual debit as
unknown. A method is eligible at a common allowance only when its entire
method cost fits. Direct human authoring and provider infrastructure remain
unmeasured limitations.

Use the previously audited managed-subscription fresh-thread transport with
`gpt-6-luna` at medium effort. The fixed schedule has **126 actual calls**:
three memory writes plus three futures times six final arms on each of six
evaluation traces. New ceiling: **132 dispatched calls and 10 planning
credits**. No retries, expansion, model fallback, API key, purchases, resets,
or run resumption. Save exact public requests, answers, usage, immutable source
hashes and a terminal completion record. A transport/accounting uncertainty
stops the schedule. This allocation belongs only to this second study.
