# Rollback tasks and grading

October 8, 2026. Review specification v0.2. Task generation and selection have
not run. The final 24 task IDs, bytes, licenses and grader hashes will be frozen
before model calibration. This file specifies how to choose them without observing
which condition wins. See [the protocol](DRAFT_PROTOCOL.md).

## Math cohort

Use 12 satisfiable constructive tasks. The candidate is a JSON object whose
`values` list assigns every variable or vertex in the declared order. Values
must be integers, with booleans, floats, missing values and duplicate JSON keys
rejected. The task includes all bounds, equations and allowed colors.

| Family and slots | Variables | Construction | Exact public check |
|---|---|---|---|
| Integer equations 1 to 4 | 4, 5, 6, 6, each in 0 to 5 | 2, 3, 3, 4 equations respectively; coefficients from -3 to 3; derive right sides from a planted assignment | All integer dot products equal their stated right sides |
| Modular equations 1 to 4 | 4, 5, 6, 6, each in 0 to 5 | 3, 4, 4, 5 congruences; coefficients 1 to 5 and moduli from 5, 7, 11; derive residues from a planted assignment | All congruences and bounds hold |
| List coloring 1 to 4 | 8, 9, 10, 12 vertices; colors 0, 1, 2 | Balanced planted colors, shuffled; each list includes its planted color and one other; edges only between different planted colors | Listed color at every vertex and unequal colors on each edge |

Use local Python `random.Random` instances, pinning the exact generator and
interpreter version. For family index f=0,1,2 and slot s=0,1,2,3, seed with
`20261008 + 100*f + s`. Draw integer/modular planted values uniformly from 0 to 5.
Reject an all-zero integer row and duplicate equations, with at most 100 redraws
per row; log exhaustion as construction failure. Do not redraw because a problem
looks too easy. For coloring, take `i modulo 3` as the initial witness, shuffle
it, draw the second allowed color from the remaining two, and inspect unordered
vertex pairs lexicographically with edge probabilities 0.35, 0.45, 0.55, 0.65
by slot. Preserve disconnected graphs and multiple solutions.

Save witness assignments only in evaluator material. A separate implementation
enumerates the finite candidate space to verify feasibility and cross-check the
grader. It must not obtain its answer by calling the production grader or merely
checking the planted witness. Maximum equation search is 6^6 = 46,656 assignments;
the listed-color construction has at most 2^12 = 4,096 assignments. These are
proposed search-space sizes, not completed checks or LLM trials.

The planted distribution may have exploitable regularities. Report this limitation
and preserve generator families as strata. Holding out seeds tests new instances
of these families, not broad mathematical reasoning or novel theorem discovery.

## Coding cohort

Proposed source is `livecodebench/code_generation_lite`, `release_v6`, with four
easy, four medium and four hard tasks. Pin an actual dataset commit and loader
implementation; the release label alone is insufficient. The official repository
documents the release selector and says the lite variant prunes tests. The
dataset card documents public/private tests and difficulty/date fields.
[@jain2024livecodebench; @livecodebench-datasets2026]

Use the complete retained public and private test sets of the selected variant.
Do not silently switch to the original full dataset or report lite-suite success
as proof of general functional correctness. The original dataset's live viewer
and its narrative report different counts; neither establishes availability of
full tests for every proposed v6 item. A later full-test audit must bind actual
matching tasks and bytes.

Selection is deterministic and independent of model answers:

1. Resolve the version/commit and inventory metadata. Verify the permitted use
   and handling of each underlying task source; do not infer data rights from
   the code repository's MIT license or a generic `cc` tag.
2. Keep noninteractive stdin/stdout tasks with at least one public and one reserved
   test, explicit easy/medium/hard labels, and a solution interface supported by
   standard-library Python. Exclude custom-judge, output-with-many-valid-answers,
   floating-tolerance and callable-method tasks from this initial runner.
3. Record each excluded item and reason. Reference execution under fixed limits
   is an infrastructure check, never an LLM difficulty screen. Reference solutions
   and their provenance must be acquired and hashed; the inspected schema does
   not establish that solutions are supplied in the dataset.
4. Deduplicate problem identities/content before assignment to any cohort. Sort
   eligible items within difficulty by SHA-256 of UTF-8
   `rollback-v02|20261007|platform|question_id`, then break a hash tie by that
   platform/ID pair. Take the first four per stratum, saving the full ordering.
5. Freeze task and test hashes before any E1/E2 model call. If fewer than four
   valid tasks remain in a stratum, report the shortfall and amend the design;
   do not substitute after observing model performance.

The October 8 original-dataset viewer exposed sample rows, including partial
reserved-test text, to the design review. Exclude these IDs from all new model
cohorts: `abc301_a`, `abc301_b`, `abc301_c`, `abc301_d`, `abc301_e`, `abc301_f`,
`abc302_a`, `abc302_d`, `abc302_e`, `abc302_f` (platform `atcoder`). Record further
human/design exposure in the same exclusion ledger. No model was tested on them.

Development-held-out means not used to tune this experiment. It does not imply
that the public problems were absent from Luna's training. Later cohorts use
different IDs, seeds and a frozen independent selection salt; any broader source
or date-window change must be named as a distribution change.

## Public feedback

The E2 host issues one receipt after a submitted candidate. Its ordered fields
are `receipt_id`, `candidate_id`, `status`, `check_id`, `observed`, `expected`,
and `detail`. The model sees only this public version.

For math, check types and bounds first, then constraints in task order. Report
the first violated constraint and the candidate's exact evaluated value/residual.
No feasibility witness, repair suggestion or solution search enters the receipt.
For code, run tests in their frozen public order and return the first mismatch,
or a bounded syntax/runtime/timeout receipt. Expected values come solely from
public examples. Cap receipt text at 2,048 UTF-8 bytes using a declared deterministic
truncation with a `truncated` flag; failure status is unaffected by display limits.

Only a well-formed math candidate with a violated public predicate, or a completed
coding run with a public output mismatch, qualifies for E2. Syntax/runtime errors,
timeouts, no-candidate messages and malformed artifacts are feasibility categories
outside the primary recovery estimand. They are still costs and outcomes in the
all-task ledger. Do not confuse a timeout with a disproved mathematical route.

If the first branch returns no candidate but a valid continuation record, allow
the second planned branch call. Stop after a public failure or full public pass.
Stop malformed/incomplete branches; do not use the second slot as a formatting
repair. A public code pass can still be a reserved-test failure. Grade that case
only offline and retain it as no-public-failure in the initial cohort.

## Terminal grading

| Domain | Primary binary endpoint | Limit |
|---|---|---|
| Math | Candidate satisfies every original public constraint | No claim about proof quality or more general math |
| Coding | Program passes every frozen public and reserved test under fixed resources | Correctness relative to these tests and runtime limits |

Terminal malformed, absent or provider-capped output is a failed answer when the
dispatch outcome and usage are known. A transport-unknown response remains
missing. Grade all scheduled continuations with the same frozen grader after
generation; terminal scores cannot modify prompts, eligibility or draw order.

The proposed runner starts a fresh process for each test inside an isolated
runtime: Python 3.11 with a pinned image digest, one CPU allocation, 512 MiB RAM,
32 processes maximum, 5 CPU seconds and 10 wall seconds per test, and 120 wall
seconds per submitted program's full suite. Limit stdout and stderr to 64 KiB
each per test. Compare whitespace-separated output tokens exactly, preserving
case and numeric strings. No fuzzy numeric equivalence is implied.

Before freezing, every trusted reference must pass these limits. Keep the full
test list; do not make an infeasible suite fit by dropping slow tests. Resource
failure before cohort freeze is an explicit exclusion; after freeze it is a
recorded infrastructure issue or candidate failure as appropriate. Reference
checks and container launches consume local time and resources, reported
separately from provider dollars.

Candidate processes receive test stdin and their own program only. The grader
keeps expected outputs, other tests, repository files, credentials and private
archives outside the runtime. Require disabled network, non-root execution,
read-only base filesystem, bounded writable scratch and teardown after each test.
These are required implementation properties, not a claim that an arbitrary
Docker invocation alone supplies complete isolation.

## Freeze record

Each task record must bind task ID/domain/stratum, origin and license, source
revision, statement bytes, public checks, private tests or feasibility witness,
reference solution, grader configuration and hashes, exposure status and seed.
Actor and evaluator records are separate files. The review example is not an
eligible task. All launch fields remain unset until actual artifacts are prepared.
