# Fixed finite trellis code

October 2, 2026. A fixed 16-state tail-biting trellis stores two parent bits per
four-bit block, then one child bit before the late coordinate. At four blocks,
the tuned labels achieve **867,837 errors on 3,145,728 outcomes**, below the
pair-product control's 869,376. This is an achievable upper bound for this
uniform delayed-query model; finite optimality and publication priority remain
open. Generic trellis coding and tail-biting are established methods.

Ordinary concatenation of independent four-block groups attains this same
distortion for every k=4*n, at exactly 2*k parent bits with one final child bit.
`encode_segments` and `update_segments` implement that separate product code.
At common lengths k=12*n, the preserved three-block product has lower error
40529/147456 than this four-block product. The improvement is at the named
four-block controls, with no stronger best known asymptotic upper bound.
One long cyclic trellis uses different overlap edges and has no such quality
claim. In fact, the selected long-cycle tables have 58/192, 1802/6144 and
41649/147456 error at k=1,2,3, worse than the respective existing controls.

[Derivation and source comparison](../../../research/FINITE_TRELLIS_CODE_2026-10-02.md).
[Exact certificate](../results/trellis_coding_2026-10-02.json).
[Frozen labels](tables.json). [Discovery metadata](discovery/metadata.json).

```powershell
python -m experiments.dependency_memory.trellis_coding.certificate
python -m unittest experiments.dependency_memory.trellis_coding.test_trellis -v
```

Regeneration uses the standard library and enumerates every source/message
combination at k<=4, then executes every delayed actor query. These small
population assignments use exhaustive nearest-message search, independently of
the general exact Viterbi encoder. Tests compare the Viterbi message and tie
choice against all messages for every k<=3 source and declared k=4/6 diagnostics.
The derivation establishes equality for general k, with exactly 1024*k branch
relaxations at k>=2. This counts recurrence work, not portable wall time or bit
operations; arbitrary finite-code optimality and asymptotic quality are open.

The parent integer contains all k quaternary symbols. Its last two symbols
specify the cyclic boundary, so no extra initial-state bits are retained. The
public three-phase tables have 192 four-bit entries, or 96 packed **label bytes**.
Program, runtime, JSON and metadata size are separate. The bit model charges
only the instance parent and child, with fixed tables chosen before the source.
The updater sees M/R/O and public k/tables; the final decoder sees Z/R/O/J.
There are no archives, source rereads, retained search paths or provider sessions.

The preserved native discovery first evaluated identity plus seeds 1..32 as
permutations of the old three-block code. None beat the pair-product control.
Four subsequent fixed sweeps tested all 15 alternative values at each of 192
public label entries, accepting 93 strict improvements. All candidate scores,
accepted/rejected visits and failed initial results are retained. The final
sweep still made nine changes; no local-optimum or complete-search claim is made.
Search and evaluation inspect the same exact finite population; no held-out
generalization or independent-trial inference is involved.

Optional discovery compilation needs a C11 compiler. Run each binary from a new
output destination rather than overwrite the frozen JSONL records; executables
belong under ignored `build/`. Both C files include the preserved local headers.
The recorded compiler is Clang 19.1.0, x86_64-pc-windows-msvc, with
`-O3 -std=c11 -Wall -Wextra -Werror`. The Windows C-clock observation is retained
as such and does not measure portable runtime. No model calls, workflow episode,
token/credit savings or production improvement is added.
