# Deterministic distortion-cover coding

Claim C73. See the [construction and proof](../../../research/DETERMINISTIC_NEAR_LIMIT_CODE_2026-10-02.md).
The public builder scans all integer loss thresholds, constructs greedy
coverage books, grades their exact uniform-source nearest losses and
compares the scalar product control. Every selection precedes X.
Exactly 2k parent bits include all group/tail labels; the updater emits
one bit before J, and the final actor predicts that bit.

The default g=max(1,bit_length(k)//10) gives polynomial public design and
actor bit complexity and actual limiting risk C67 D_infinity(2). It is
an application of established covering/source-coding methods. Its slow
schedule and conservative convergence bounds do not demonstrate practical
near-optimal performance or model/token/cost benefit.

The supplied g=1/2/3 codes have exact errors 9/32,9/32,2543/9216.
The scalar product wins at one and ties at two; the three-block code loses
to both the refined three-block and conditional six-block controls.
Public response payloads are 2/16/96 packed bytes, with public parameters,
program/runtime/framing and builder workspace separate.

Run from the repository root:

    python -m experiments.dependency_memory.greedy_coding.certificate
    python -m unittest experiments.dependency_memory.greedy_coding.test_greedy -v

Outputs: [public finite designs](tables.json) and
[certificate](../results/greedy_coding_2026-10-02.json). The checker does
not build the enormous groups used by the conservative analytic bounds.
The complete old repository checks remain documented in the main README.

- The direct-query matrix checks 16,843,008 source/candidate distances and
  768 final-builder greedy choices at all 75 small thresholds.
- Six complete populations execute 454,848 final queries; forty constructed
  product/tail inputs execute 3,552 diagnostics.
- All 4,096 tiny set systems calibrate the general cover recurrence through
  307,200 competitor/step comparisons; the general proof is analytic.
- Rational channel checks retain C34's source/cross-information bounds.
  Fifty-four large g/h proximity bounds are analytic, not executed codes.
- [Original probes](discovery/README.md) preserve 150 inspected designs
  and 1,616 rechecked choices. Sixteen bindings preserve upstream evidence.

Public books/cache keys depend only on g. Instance source, assignments,
histograms and scratch are discarded at their boundary. Actors are trusted
functions, not isolated untrusted processes. No new model call or natural
episode is added. External proof/priority and useful finite convergence
remain open.
