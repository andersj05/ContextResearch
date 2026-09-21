# Finite compaction collision auditor

A new experimental direction: check whether histories mapped to the same memory
and public state can still be handled within a recovery budget. This is a
standard-library exact prototype, not an LLM compressor or a live harness.

Run from the repository root:

    python -m experiments.dependency_memory.collision_audit.run
    python -m experiments.dependency_memory.collision_audit.run --input experiments/dependency_memory/collision_audit/example.json --output tmp/collision-audit.json
    python -m unittest experiments.dependency_memory.collision_audit.test_collision_audit -v

The first command regenerates [results](../results/collision_audit_report.md),
their certificate and the example specification. The input mode is read-only
except for an explicitly supplied output file; otherwise it prints JSON.

## Input contract

The [example](example.json) is a complete three-world specification.

- name: a diagnostic name; budget: a nonnegative integer recovery allowance.
- worlds: 1-12 entries, each with a distinct string id, a visible pre-compaction
  history, a retained JSON value, and a public JSON value. Histories plus public
  observations must uniquely identify the world before compaction. IDs are
  evaluator labels, not inputs to the execution policy.
- tools: name, strictly positive integer cost, and observations mapping every
  world ID to a JSON value. These are deterministic, read-only tool snapshots.
- tasks: distinct name, a shared public trace of event strings, and accepted
  terminal-action strings for every world. All listed tasks are possible in all
  worlds. Multiple answers may be accepted. Unlisted terminal answers fail.

Exact canonical JSON equality of retained and public values forms the collision
cells. No semantic equivalence is guessed. A task is revealed after compaction;
its trace is common across worlds. Policies see the initial cell and task, then
their chosen tools' responses. Responses are retained during rescue. Side
effects, stochastic tools, intermediate memory limits, hidden state, and
query-dependent tool tables require a different model. No existing provider's
behavior is represented by this specification.

## Output

For each task/cell the audit gives the exact minimum worst-case recovery cost,
an optimal adaptive policy and per-world replay, the best fixed-batch cost, and
a checked lower-bound DAG at one less than the optimum. An impossible cell gets
a proof at the supplied budget and an indistinguishable subcell with no common
answer even after every tool is available. The latter is independently checked
and certifies impossibility at every budget. Null cost means infinity, not missing evidence.
All accepted terminal actions and all supplied tools are covered by the proof;
all other terminal actions fail universally and cannot reveal information.

The minimum-cardinality failing world subset and shortest failing trace from the
declared catalog are diagnostic witnesses. A shortest arbitrary program
continuation is not searched. Pairwise feasibility is explicitly reported
alongside whole-cell feasibility.

The repair partitions each initial cell into as few subcells as possible while
supporting every task at the budget. Its label is retained before task reveal.
Labels are reusable across distinguishable original cells. Extra fixed bits
measure that finite alphabet, not the size of the shared codebook, serialized
JSON, archive, prompt tokens or a learned encoder. Retained and public JSON byte
lengths are separate fields. No total-storage or practical compression claim
follows from the label count.

## Scientific boundaries

The solver and proof verifier use different formulations: optimizing information
partitions versus checking rejecting worlds and adversarial query branches.
Forward controller enumeration supplies another check on all 343 three-world
accepted-action tables. Negative controls cover free public evidence, harmless
forgetting, adequate recovery, and old-versus-current archive access. Diagnostic
counts are not model trials. World enumeration is exponential and needs a sound
adapter before it can audit a natural task.

[Research note](../../../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md) and
[primary-source comparison](../../../research/COMPACTION_AUDIT_PRIOR_ART_2026-09-21.md).
