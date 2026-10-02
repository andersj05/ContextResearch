# Hard-cap arithmetic parent

October 2, 2026. Claim C71. An implemented encoder/updater uses exactly 2k
parent bits, including one fallback flag, followed by one bit before J. Uniform
iid four-bit sources and independent uniform R/O/J; final only Z,R,O,J. Fixed
words/probabilities and public k/a are chosen before X. No source, intervals,
instance histograms, archives or sessions cross the boundary alongside M.

[Derivation and finite comparisons](../../../research/HARD_CAP_ENTROPY_CODE_2026-10-02.md).
[Certificate](../results/entropy_coding_2026-10-02.json).
[Inspected discovery/control records](discovery/README.md).

`codec.py` quantizes the first a blocks to eight majority signatures and the
rest to two constants. Their nonuniform outputs enter one exact arithmetic
interval. A charged fixed-grid index either decodes the entire sequence or
M=0 selects the all-zero fallback. The default public entropy planner uses
integer powers and a growing slack; `rational_count` retains the simpler
prototype as a stronger control at several finite lengths. Only M reaches
`update`; only its one bit reaches `predict`.

`finite.py` computes exact conditional excess-loss bounds through two binomial
counts and a monotone integer frontier. This bounds the entire uniform source
population; it does not evaluate the exact large-code average. `certificate.py`
independently checks boundaries, source calibrations and original C67/C69
bindings, plus all 608,640 small final queries and 864 constructed large routes.
`test_entropy.py` has eight scientific tests using independent formulations.

```powershell
python -m experiments.dependency_memory.entropy_coding.certificate
python -m unittest experiments.dependency_memory.entropy_coding.test_entropy -v
```

The default actual code tends to error in [0.270753014417,0.270753014418],
improving C69's repeated finite-code upper bound while staying above C67's
optimal limit. At k=12288, public a=7970 gives error <=0.271988910419 under
the same 2k/one-bit cap. Four checked smaller lengths provably lose; the
prototype control wins at some larger lengths. Fifteen bindings regenerate.
Public response/probability payload is ten bytes; program, runtime, k/a and
framing descriptions are separate. Temporary stage workspace is allowed and
discarded; polynomial arithmetic complexity is not portable timing or a
practical implementation-cost measurement. No exponentially stored codebook
is required. Generic quantization, entropy coding, arithmetic intervals and
time sharing are established; optimality, external correctness/priority and
natural-agent/model benefit remain open. Zero model calls or natural episodes.
