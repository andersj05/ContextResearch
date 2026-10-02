# Exact-priced group coding

[Proof and limits](../../../research/EXACT_PRICED_GROUP_CODE_2026-10-02.md),
[generated certificate](../results/priced_coding_2026-10-02.json).
Claim C75: a six-block public quantizer improves the named C74 finite code
at 6144 and 12288 blocks under the same 2k-bit parent/one-bit child contract.
At 12288 the conservative error is at most 0.270475649358095.
The upper bound is below C74's named base lower bound.

The gain is small and public data are larger: 66513 packed actor bytes;
94754 including finite-planning loss weights, within the 262144-byte packed
envelope. Parameters/program/framing/JSON/Python caches/RAM/workspace are
separate. Local large encodes take seconds. Global optimality, useful
near-C67 convergence, novelty and agent benefit remain open.

- design.py: immutable public book, exact integer-price minimum, loss masks,
  packing and root-free outward entropy. Only public Book is cached.
- tables.json/tables.py: frozen response/proposal/actual-CDF/loss-weight data.
  Public planners need no historical map or source input.
- bounds.py: 64-bit outward weighted moments, exact discrete convex search
  for five root degrees, and a separate entropy-slack schedule.
- codec.py: charged flagged arithmetic parent, two-bit scalar tail, child
  before J and final actor using only Z/R/O/J. No assignment table or
  source-dependent cache crosses a boundary.
- evidence.py/certificate.py: complete saved-map grading, independent tensor
  minimum records, exact calibrations, small full actors and large diagnostics.
- discovery/: original protocols, programs, maps, terminal logs and provenance.
- benchmark.py/local_timings_2026-10-02.json: separately saved single local
  measurements; not rerun by default scientific validation.

All ten starts retain original data. Eight five-block bounds fail to beat
C74 at 12288. The first six-block start also fails. All 41943040 source
assignments match an independent complete tensor minimum calculation.
Default checks grade those recorded native runs and literal losses/counts;
they do not repeat discovery or require a compiler.

The finite selector's actual asymptotic error is unproved. A separately
implemented entropy-slack family has actual limit
[0.269017091392,0.269017091393], better than C72 fixed-eight but worse than
C72 growing. Large finite risks are analytic bounds, not exact actor
population averages. Trusted-function access is not process isolation.
Zero model calls or natural episodes; previous provider cases remain closed.

    python -m experiments.dependency_memory.priced_coding.certificate
    python -m unittest experiments.dependency_memory.priced_coding.test_priced experiments.dependency_memory.priced_coding.test_evidence -v
    python scripts/validate_context_repo.py

The benchmark records public planning after table loading. Public Book
compilation precedes warm actor timing. Certificate grading overlapped part
of measurement; clocks are descriptive local samples, not controlled speed
comparisons. Rerun benchmark.py only as a new preserved measurement.

Validation: all 597 offline tests pass, including fourteen new scientific
checks. Repository validation reports PASS with 75 claims/55 bibliography
entries/171 PDF hashes/195 immutable imports; the paper checks 48 cited
sources. All 71 bindings match, and original claim/decision/data bytes
remain intact.
