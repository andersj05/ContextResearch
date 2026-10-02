# Preserved query-prior discovery

October 2, 2026. Post-hoc offline inspection and candidate discovery; zero
model calls or natural episodes. The exact proof is in the separate
[checker](../certificate.py) and
[research note](../../../../research/QUERY_PRIOR_TIMING_2026-10-02.md).

`probe.py` is the initial scratch script, with common q bracket [0.00001,0.299].
For p=2/5 it returned combined information 4.687711329867541, exceeding 4.
`probe_v2.py` changes only the upper bracket to 0.9 and supplies valid candidates.
q is a common slope parameter; q^m and q^n are the actual class parameters.
Floating outcomes are discovery values, never numerical proof.

Both versions wrote the same scratch output name, so the initial JSON was
overwritten before export. `initial_recomputed_probe.json` is the deterministic
offline rerun of the original script. It agrees with the original failure
stdout but is explicitly a recomputed record; original timing is unavailable.
`corrected_probe.json` preserves the corrected output. No provider call was
repeated or involved.

`prepare_witnesses.py` rounds decimal float q upward at scale 10^12, adds one,
then tries at most ten increasing numerators. Exact admission requires combined
information upper bound<4 and distortion upper-lower<2e-11. All five first
attempts passed; the candidate/attempt schedule is in [witnesses.json](../witnesses.json).

These files preserve actual scratch source bytes. Their relative-root and
output assumptions refer to the original ignored `build/query-weighting`
layout, not this package directory; they are historical records, not supported
package commands. Use the README's certificate command for regeneration.
`metadata.json` binds all five discovery files and original C67/C69 outputs
at commits b11d580/8e09d1d. Original sources/results are unchanged. No run-time,
independent-trial, complete literature or publication-priority claim is made.
