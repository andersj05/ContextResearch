# Three-block finite construction

October 1, 2026. Six parent bits followed by one child bit in the unchanged
uniform delayed-query contract. The fixed 64-codeword witness has **40,529 errors
on 147,456 outcomes**, below the old pair-plus-one concatenation's 40,992.
This is an achievable upper bound, not a proof of the three-block optimum.

[Derivation and limits](../../../research/JOINT_THREE_BLOCK_WITNESS_2026-10-01.md).
[Exact certificate](../results/joint_three_block_certificate_2026-10-01.json).
[Discovery record](discovery.json) preserves both local starts, all greedy steps,
eight accepted swaps, the unchanged concatenation control, compiler/source hashes
and preliminary/corrected timing-label runs. The public codebook is fixed before
the source and is not charged as instance memory, as in the original bit model.

```powershell
python -m experiments.dependency_memory.joint_coding_finite3.witness
python -m unittest experiments.dependency_memory.joint_coding_finite3.test_finite3 -v
```

Grading uses only Python's standard library and directly executes all delayed
routes. Six tests compare nearest assignments against separately enumerated
one-block losses, the historical/product controls, relabelling/complement/block
symmetries, hard state limits and query timing. The native search is not required
to reproduce the certificate. Optional discovery needs a C11 compiler:

```powershell
python -m experiments.dependency_memory.joint_coding_finite3.discover --output build/finite3-new-discovery.json
```

Use a new output path; it refuses to overwrite saved discoveries. Compiled
executables stay under ignored `build/`. Search covers the 4,096 unsigned
decision triples as candidates, not all 64-element codebooks or all possible
decoders. The greedy start stops after eight swaps and has no local-optimum
certificate. The concatenation start admits no improving single swap. C `clock()`
and process wall time are recorded separately; no process-CPU, scalable-runtime,
LLM-performance or publication-priority claim is made.
