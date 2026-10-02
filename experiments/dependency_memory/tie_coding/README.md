# Coordinated equal-loss responses under a hard parent cap

October 2, 2026. Local construction and deductions; claim C72. Uniform iid
four-bit sources and independent uniform R/O/J only. Zero new model calls
or prospective natural episodes. Generic entropy quantization, weighted
greedy cover, prefix/arithmetic coding and time sharing are established.

The two constant answers tie for a weight-two source. Coordinate those choices
across public groups rather than choosing zero independently. The source-wise
constant error stays 5/16, while output entropy falls. For two blocks the exact
minimum compatible-output entropy is attained by counts [121,85,25,25]/256.
This is a restricted optimum, not the global rate-distortion curve.

The fixed eight-block cover uses 256 public priorities and fixed source
counts, checked on all 6561 weighted status categories. Mixing it with full
majority signatures, an implemented arithmetic-grid parent fits exactly
2k bits including one regular/fallback flag; the updater emits one bit before
J and the final actor sees only Z/R/O/J. The default actual code risk tends to
[0.269293075342,0.269293075343]. At k=12288, public a=1025 oracle groups and
margin multiplier four give error <=27080383700567/10^14. This upper bound
lies below both named C71 codes' base-error lower bounds, and below C69.
The selected four smaller-length designs provably lose to the stronger old
controls. Forty margin designs and five Chernoff exponents per design remain
visible; selection minimizes a conservative bound, not actual risk.

A separate growing schedule g(n)=max(1,floor(bit_length(n)/4)), k=n*g(n),
and margin multiplier 4*g(n) has polynomial design/actor bit complexity.
Published minimum-entropy cover guarantees plus the note's elementary
information/rank/prefix argument give cover entropy per block ->5/8. Its
actual risk tends to [0.267829178707,0.267829178708]. This analytic family
limit is not physical enumeration of all n, an efficient near-C67 guarantee,
a portable runtime measurement or a practical-agent gain.

Fixed-eight priority/count payload is 1280 packed bytes plus eight oracle
response/count bytes, total 1288; public n/g/a, program/runtime/framing and
growing-family tables are separate. Only M and Z cross boundaries. Internal
exact-integer workspace is discarded; no source, output list, histogram,
old parent, archive, environment or provider session is extra memory.

    python -m experiments.dependency_memory.tie_coding.certificate
    python -m unittest experiments.dependency_memory.tie_coding.test_tie -v

Nine scientific checks include independently recounted greedy choices, literal
small quantizers, complete small arithmetic populations, fractional intervals,
integer root bounds, rank/prefix primitives, old scalar equality and stronger
finite controls. Literal quantizers execute 153792 queries; complete small
arithmetic populations execute 915840; fifteen constructed large inputs
execute 1008 diagnostic queries. Larger uniform populations are not enumerated:
root-enclosed Chernoff moments give conservative whole-population upper bounds.
Seventeen source/provenance bindings include original C71 evidence and its
C67/C69 checks. [Discovery](discovery/README.md) is post-hoc and retains failures.
External correctness/priority, broader source/query laws and natural-agent/
model/token/credit/cost benefit remain open. See the [proof note](../../../research/COORDINATED_TIE_CODE_2026-10-02.md).
