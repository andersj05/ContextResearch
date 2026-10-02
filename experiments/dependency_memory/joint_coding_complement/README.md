# Complementary decoder finite converse

October 1, 2026. [Proof and limits](../../../research/COMPLEMENTARY_DECODER_COVER_2026-10-01.md).
The same three-block bracket **[40,072, 40,529] / 147,456** now covers all
256 complementary decoder tables per block, with possibly coordinate-dependent
predictions and different tables across blocks. Six orbits and 56 mixed cases
cover these tables; 229,376 decision columns have exact checked cover weights.
Noncomplementary decoders and the unrestricted finite optimum remain open.

```powershell
python -m experiments.dependency_memory.joint_coding_complement.cover
python -m unittest experiments.dependency_memory.joint_coding_complement.test_cover -v
```

Five independent tests check direct routes, a separate symmetry partition,
all selected case histograms by direct source sums, the per-source inequality
and rejection of decoders outside the proof. Equal sorted score multisets are
cached explicitly; the generator uses histogram convolution instead.

The [certificate](../results/joint_three_block_complement_2026-10-01.json)
pins all proof/code inputs and the unchanged three-block upper witness.
[Discovery](discovery.json) records the 1,306 binary target triples and 144-point
quarter-unit diagnostic; every selected target is actually zero or one.
`python -m experiments.dependency_memory.joint_coding_complement.discover`
regenerates that exploratory witness trace. No optimizer, native compiler,
model call or claim of exhaustive codebook/target optimality is required.
External proof/priority review remains open; the elementary cover technique is
not claimed novel.
