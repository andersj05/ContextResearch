# Three-block finite converse for all final decoders

October 1, 2026. [Proof and limits](../../../research/ALL_DECODER_THREE_BLOCK_COVER_2026-10-01.md),
claim C63. For three independent uniform four-bit blocks, six parent bits before
R/O and one child bit before J, **every final decoder** has error at least
40,072/147,456. With the unchanged upper witness, D_3(6) lies in
**[27.1756%, 27.4855%]**. Arbitrary joint encoders and heterogeneous decoder tables
are allowed. Public books are fixed before source; source/parent rereads and
other hidden channels are excluded at their stated boundaries.

The oracle-defect gate and the existing 4,751 per-block symmetry orbits cover
all 36^12 ordered table triples. There are 46,492 near mixed orbit cases:
56 complementary cases reuse the earlier certificate, and 46,436 cases have
new exact target witnesses. Tied ideal predictions use an incidence union
bound rather than a unique-ideal assumption. Entire equal source-loss columns
are identified; histogram equality alone is insufficient.

```powershell
python -m experiments.dependency_memory.joint_coding_general.cover
python -m experiments.dependency_memory.joint_coding_general.audit
python -m unittest experiments.dependency_memory.joint_coding_general.test_cover -v
```

The [certificate](../results/joint_three_block_general_2026-10-01.json)
recomputes 178,240,944 cost-column instances using integer histograms and
declared profile multiplicities. Seven tests check direct routes, the branch
polynomial, binary basis coefficients, fractional source sums, overlapping
ideal words, source hashes and the optional auxiliary evidence. Direct fractional
checks cache equal sorted score multisets explicitly; the generator uses
histogram convolution instead.

[Discovery](discovery.json) records bounded post-hoc selection: 59,029 initial
binary candidates, 4,924 mixed refinements and 2,815 quarter-unit candidates.
`python -m experiments.dependency_memory.joint_coding_general.discover`
regenerates that trace; rerun `cover` afterward. This is not exhaustive target
or codebook optimization. The final inequalities require only the selected
witnesses and standard-library Python.

`auxiliary/` preserves the actual native and numerical exploration inputs,
source and outputs with a [manifest](auxiliary/manifest.json). The [audit](../results/joint_three_block_general_auxiliary_2026-10-01.json)
regrades eight books on every route and rechecks twelve rational dual points.
These computations guided discovery but are unnecessary for the cover proof;
the raw numerical script retains its original exploratory build paths. No
default check runs a compiler, imports NumPy or contacts a model service.

The interval is not an exact finite optimum or an asymptotic-frontier update.
External proof/priority review remains open; no general cover novelty,
new model result, natural workflow episode or token/production saving is claimed.
