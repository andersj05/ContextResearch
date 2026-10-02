# Conditional six-block code

October 2, 2026. **Checked finite upper bounds and a scoped local-search
counterexample**, claim C69. No model request or natural workflow is added.
All earlier codebooks, certificates and provider records remain unchanged.

The [research note](../../../research/CONDITIONAL_SIX_BLOCK_CODE_2026-10-02.md)
gives the information contract, grouping proof, comparisons and limitations.
[codec.py](codec.py) implements the fixed encoder/updater/final actor;
[tables.json](tables.json) holds the public codebook selected before X.
[certificate.py](certificate.py) independently checks the construction without
running native discovery. The [preserved search](discovery/README.md) includes
failed controls, source/header bytes, bounded trajectories and compiler metadata.

```powershell
python -m experiments.dependency_memory.conditional_coding.certificate
python -m unittest experiments.dependency_memory.conditional_coding.test_conditional -v
```

The refined three-block component has 40,514 / 147,456 errors, with no positive
gain among all 262,144 single-word replacements in the fixed unsigned family.
Its two-copy product has 331,890,688 errors; changing one six-block response
word reduces that to 331,886,587. Eight conditional changes give **331,857,648 /
1,207,959,552 = 2,304,567 / 8,388,608**, about 27.472579% error. Parent memory is
12 bits and child memory one bit. Labels use 120 packed public payload bytes,
with the override count eight a public protocol constant; Python/JSON/program
storage and optional count/framing are separate from both payload and instance
bits. Every possible parent is used on this uniform population.

The six-block check covers all 16,777,216 source pairs using an exact grouping
argument and weighted actor grading. It physically executes 11,783,592 actor
queries representing 1,207,959,552 equally weighted outcomes, rather than
calling the actor individually on every outcome. The three-block component
separately executes all 147,456 actor queries. The certificate reports both
counts and regenerates all 24 source/provenance bindings.

Independent six-block segments preserve the error at k=6*n with exactly 2*k
parent bits and one child bit. At common k=12*n, this improves on both the old
and refined three-block products. This is a derived product extension, not
enumeration of those larger populations. It remains above C67's rate-two
limit. Final six-block local/global optimality, efficient codes approaching
the curve, external correctness, publication priority and natural-agent
benefit remain open. Product quantization and codeword replacement are
established methods; this package claims only the specified finite results.
