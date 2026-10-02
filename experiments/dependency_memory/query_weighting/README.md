# Query-prior robustness and timing

October 2, 2026. Claim C70. Offline local consequences of C33/C67, exact
fixed-book sensitivity and executable allocation/timing controls. No new model
call or prospective natural episode. See the
[derivations and assumptions](../../../research/QUERY_PRIOR_TIMING_2026-10-02.md).

Uniform iid four-bit blocks are divided into two equal public classes. The
queried class has source-independent probability p, and block/O/J remain
uniform inside their declared sets. Parent cap is 2k bits, child cap one bit
before J. Final actor receives only Z,R,O,J. Three separate conditions declare
p known before X, p unknown to parent design, or actual realized class T known
before M. The last changes timing, even though T carries no source information.

- `codec.py`: fixed known-prior nearest encoder; opposite-orientation pairs
  robust to every p for k=12h; equally capped 1/3 allocation controls; early
  actual-class signatures using 3n bits inside 4n. No instance selector is free.
- `finite.py`: independent minimum-of-three-affine-lines formulation; 52 exact
  segments cover all p in [0,1] and all 16,777,216 six-block sources by weights.
- `asymptotic.py`: five rational support/slack witnesses for optimal class
  allocation, using C67's existing all-slope decoder theorem and outward logs.
- `certificate.py`: source/provenance binding, prior sensitivity, named
  controls, source-free routing and scoped analytic statements.
- `test_weighting.py`: eight tests using independent loss/entropy formulations,
  complete-message minima, seams, padding, access/capacity and negative controls.
- [Discovery](discovery/README.md): failed float bracket, corrected candidate
  probe, explicitly recomputed original failure and exact admission record.

```powershell
python -m experiments.dependency_memory.query_weighting.certificate
python -m unittest experiments.dependency_memory.query_weighting.test_weighting -v
```

Output: [query_weighting_2026-10-02.json](../results/query_weighting_2026-10-02.json).
It binds 16 files. C67/C69 outputs and source bindings remain immutable.
589,824 physical source-free final query checks validate local routing, not
enumeration of the twelve-block source population. Larger balanced-pair error
counts are derived from C69's checked component counts and independence.
The 120-byte public label payload is shared; program/framing/JSON/runtime are
separate from label bytes and parent/child instance bits.

Known-prior limiting error is min pD(r_L)+(1-p)D(r_R) over r_L+r_R<=4;
unknown-prior minimax tends to D(2). An early actual class cue attains 1/4
inside the same cap. These are local analytic deductions, with no efficient
near-limit finite encoder supplied. At p=1/4 the simple 1/3 allocation beats
the balanced pair. Three named achievable controls are not all finite optima.
Generic allocation/symmetry/side-information novelty, external correctness and
priority, biased/adaptive query laws and natural-agent benefit remain open.
