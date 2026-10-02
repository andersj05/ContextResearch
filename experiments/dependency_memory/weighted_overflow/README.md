# Loss-weighted overflow and public finite allocations

[Research note](../../../research/LOSS_WEIGHTED_OVERFLOW_2026-10-02.md), claim
C74. [Result](../results/weighted_overflow_2026-10-02.json).

The original C72 arithmetic actors remain unchanged. A wrapper chooses the
public oracle allocation before X using loss-weighted Chernoff bounds.
Exact discrete convex search minimizes each of five outward bounds over
every integer allocation; it does not minimize actual risk.
Parent capacity is exactly 2k bits including its flag, then one child bit
before J. Final input is only Z/R/O/J.

At k=768, error is at most 8578395865937/31250000000000, below repeated C69.
At k=12288 it is at most 270646703203513/10^15. The three smaller checked
lengths provably lose to C69. Seven selected new codes have upper bounds
below the named prior C72 codes' base errors. The same 1288 packed public
table bytes fit the declared 262144-byte envelope; public parameters,
program/runtime/framing and workspace are separate.

- bounds.py: integer cell-loss weights, outward moments and public allocation.
- codec.py: C72 actor wrapper, with no discovery-table access.
- certificate.py: literal cell/actor checks, eight finite lengths and provenance.
- test_weighted.py: independent moments, complete allocation lists and contracts.
- benchmark.py: one local cold-plan/warm-actor sample per declared input.
- local_timings_2026-10-02.json: saved samples with exact source/input bindings.
- [discovery](discovery/README.md): all 384 unsuccessful quantizer starts.

    python -m experiments.dependency_memory.weighted_overflow.certificate
    python -m unittest experiments.dependency_memory.weighted_overflow.test_weighted -v

The deterministic certificate does not rerun compilers, model services or
timing samples. Complete small actors execute 915840 final queries;
larger constructed inputs execute 540 diagnostics. Larger guarantees are
whole-population analytic bounds, not source enumeration or exact errors.
Old evidence remains immutable. Generic Chernoff/ECVQ methods are prior work;
external correctness/priority, useful near-C67 codes and practical-agent
benefits remain open. Zero new model calls or natural episodes.
