# Restricted three-block converse

October 1, 2026. An elementary weighted-cover argument gives **40,072 errors /
147,456 outcomes** as a lower bound when the final prediction is independent
of the late coordinate J. The [existing witness](../joint_coding_finite3/README.md)
gives the upper bound 40,529. The interval width is 457/147,456, or approximately
0.310 percentage points. This covers arbitrary joint encoders/codebooks in the
restricted family; it does not cover arbitrary final endpoint decoders.

[Proof and limits](../../../research/JOINT_THREE_BLOCK_COVER_2026-10-01.md).
[Exact finite ingredients](../results/joint_three_block_cover_2026-10-01.json).

```powershell
python -m experiments.dependency_memory.joint_coding_cover.bounds
python -m unittest experiments.dependency_memory.joint_coding_cover.test_bounds -v
```

Four tests independently enumerate all one-block routes and all 16,777,216
source/column combinations, check constant-center fibers and the saved witness,
and reject late-coordinate-dependent endpoint decoders from the bound API.
The certificate verifies the maximum single-column reward, not all codebooks.
Standard-library-only, zero model calls, no finite-optimum or novelty claim.
