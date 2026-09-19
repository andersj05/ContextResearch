# Exact finite optimum for the two-bit then one-bit chain

September 19, 2026. **Evidence status: checked exhaustive finite computation, with an analytic search reduction and an explicit attaining construction.** This is a local result, not external proof review, formal verification, a novelty certification, or an LLM experiment.

## Result and assumptions

The exact minimum average bit error in the existing four-bit example is

\[
\boxed{D^*_{2\to1}=\frac{54}{192}=\frac9{32}=28.125\%.}
\]

This is an absolute excess of 1/32, or 3.125 percentage points, above the isolated one-bit child's optimum of 1/4. It sharpens the earlier conservative lower bound 49/192. The earlier eight-state compatibility certificate remains valid: three initial bits attain 1/4, and two initial bits do not. Historical documents saying the exact optimum was uncomputed describe the state before this calculation.

The model is unchanged. A uniform source X in {0,1}^4 is encoded into at most four parent states. An independent uniform omitted coordinate O then identifies the three-coordinate subset. The updater receives only the parent state and O and produces one of two child states. A uniform J among the three remaining coordinates is then revealed. The final decoder receives the child state, O, and J, and predicts X_J. Neither updater nor decoder can reread X; the decoder cannot read the parent state. Fixed public codebooks are allowed. All state limits are hard capacities, with no archive, retained history, or source-dependent public side channel.

Randomization independent of X,O,J cannot improve the optimum: fix the complete random tape, obtaining an admissible deterministic system under the same hard capacities. The randomized loss is an average of deterministic losses. This argument would not establish the result for an expected-only memory constraint or random coins carrying source information.

## Why a finite partition search is complete

1. A deterministic parent encoder partitions the 16 source strings into at most four nonempty cells. Unused message names and permutations of names do not affect the attainable loss. Any partition with fewer than four cells can be refined to four cells, while preserving its behavior by assigning the new cells the old child outputs. Thus it suffices to minimize over exactly four nonempty cells.
2. For a fixed omission, a deterministic child encoder assigns each of the four cells to child label 0 or 1. Exchanging these labels leaves the attainable error unchanged. There are eight distinct splits modulo this exchange, including a constant split. Each is represented by a union U of cells that contains the first cell.
3. Once a child split is fixed, the optimal decoder predicts the majority value of each queried coordinate among sources with that child label. Coordinates are decoded separately because the loss is the sum of coordinate disagreements.
4. The child's split can be optimized independently for each omission: the omission is public to both the updater and decoder. The parent partition is shared across all four omissions.

The enumeration uses restricted-growth labels: source 0 starts in cell 0; each later source either joins an existing cell or creates the next unused cell. Every unlabeled partition occurs exactly once, because cell names are ordered by the least source they contain. Branches are pruned only when the unassigned sources cannot fill the remaining required cells. The number of visited leaves is the independently computed Stirling number

\[
S(16,4)=171{,}798{,}901.
\]

No restriction to complementary decoder words, majority branch functions, linear encoders, or symmetric parent partitions is made. Majority decoding appears only after fixing an arbitrary child split, where it is optimal coordinate by coordinate.

## Exact integer objective

For a source subset U and coordinate j, let

\[
v_j(U)=\#\{x\in U:x_j=1\}-\#\{x\in U:x_j=0\}.
\]

Across the full source universe, coordinate j has eight zeros and eight ones. If U contains a ones and b zeros, the optimal two-label decoder makes

\[
\min(a,b)+\min(8-a,8-b)=8-|a-b|=8-|v_j(U)|
\]

errors on coordinate j. Therefore a split U for omission o makes

\[
24-\sum_{j\ne o}|v_j(U)|
\]

errors among the 16 times 3 source/query cases in that branch. For a parent partition P define

\[
G(P)=\sum_{o=0}^3\max_{U\text{ a union of cells of }P}
             \sum_{j\ne o}|v_j(U)|.
\]

Its optimally decoded total error count is exactly 96-G(P), with common denominator 192. Complementing U negates every v_j and preserves the objective, justifying the eight-split reduction. The exhaustive search finds max G(P)=42. Thus every admissible system has at least 54 errors, and the construction below attains 54.

## A simple attaining construction

Use coordinates 0,1,2,3 and retain two Boolean functions:

- m is the majority of coordinates 0,1,2.
- h is the majority of all four coordinates, with an even tie resolved by coordinate 3.

If coordinate 3 is omitted, pass m as the child bit. For each other omission, pass h. The final decoder predicts the child bit for whichever coordinate is queried.

The omission-3 branch is exactly the optimum three-bit majority code and makes 12 errors among its 48 cases. For any other omitted coordinate o, h disagrees with the majority of the remaining triple only on the two strings with total weight two and x_o=x_3. Each disagreement increases the triple's Hamming loss by one, giving 14 errors. The total is 12+14+14+14=54.

The search's first attaining partition has source masks (279,104,59520,5632), representing the four (h,m) combinations (0,0), (0,1), (1,1), (1,0), respectively. Bit x of a mask indicates membership of integer source x; coordinate 0 is the source's least significant bit. The independent witness grader constructs all child assignments and coordinate-majority decoders directly, then checks all 192 individual outcomes.

## Implementation, completed checks, and reproducibility

The [implementation](../experiments/dependency_memory/exact_chain.py) includes a transparent standard-library Python reference and an embedded portable scalar C99 search. A selected C compiler is an optional acceleration dependency; no compiler is needed for the ordinary repository tests. The native search uses integer objectives and counts throughout, with no optimization solver, floating-point tolerance, random search, or heuristic pruning. Its temporary source and executable are discarded after execution.

The complete scalar run with Clang 19.1.0 took approximately 24 seconds on this local machine. It visited all 171,798,901 partitions, found 128 attaining partitions, and independently graded the returned witness at 54/192. An earlier disposable SIMD implementation produced the same entire gain histogram; this is a cross-check, not a separate committed artifact or independent external review.

The [tests](../experiments/dependency_memory/test_exact_chain.py) check:

- Partition enumeration against an independent enumeration of labeled functions on a smaller universe, including uniqueness.
- All child functions against the reduced set of cuts, modulo label exchange.
- The signed-count objective against every ordered two-word decoder on every cut of a three-bit source.
- Every three-bit, three-state parent partition against direct outcome-by-outcome grading, with matching complete score histograms.
- The four-bit witness's 192 outcomes and its branch counts (14,14,14,12).
- Rejection of overlapping parent cells and incomplete search counts.

An independent local agent review additionally matched complete native and Python histograms and Stirling counts for every source-bit count in {2,3} and parent-state count in {1,2,3,4}, including all S(8,4)=1,701 three-bit/four-state partitions. It also exhaustively checked the two-bit/four-state optimum by directly enumerating labeled parent, child, and decoder functions, including unused labels. This is another local computational audit, not external proof review. The full four-bit computation is reproduced by:

```powershell
python experiments/dependency_memory/exact_chain.py --compiler clang --output experiments/dependency_memory/results/exact_chain_certificate.json
python -m unittest discover -s experiments/dependency_memory -p test_exact_chain.py -v
```

The output records the complete gain histogram, source hash of the embedded search, compiler version, timing, count, exact fraction, and complete witness decoder. The histogram and count are reproducibility checks, not a standalone lower-bound proof object: excluding a better encoder still relies on the stated reduction and the correctly executed exhaustive search. The Python backend can be selected explicitly with `--python`; use `--source-bits 3 --parent-states 4` for a quick reference run. Full four-bit Python enumeration is intentionally not a default test.

## Interpretation and remaining limits

This closes the exact finite optimization question in the stated four-bit model. It makes the local composition penalty concrete: 28.125% versus 25%, despite the independent bottleneck comparisons. It does not alter the separate block-family scaling derivation, whose uniform lower bound and assumptions remain as previously audited. In particular, 1/32 is this one-block excess; it is not an established per-block excess for arbitrary joint encoders as the number of blocks grows.

The calculation does not establish novelty, natural-language performance, an economic benefit from proactive inspection, or superiority to native provider compaction. Literature comparison and external checking of the mathematical work remain appropriate next steps. No model calls or paid experiments were performed.
