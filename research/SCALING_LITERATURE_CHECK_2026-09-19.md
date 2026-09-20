# Focused literature check: the scaling argument

Reviewed September 19, 2026. This addendum checks the strongest nearby overlap with the [active scaling derivation](CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md) and [proof audit](PROOF_AUDIT_2026-09-18.md). It supplements the [literature positioning note](LITERATURE_POSITIONING_2026-09-18.md); it is not an exhaustive priority search or an external proof review. No experiment results enter this comparison.

**Conclusion:** functional signatures and information direct-sum arguments are established machinery. The candidate contribution must be confined to the particular delayed-query construction, its exact attainment threshold, and its quantitative stability analysis. This check does not establish that those specific results are new.

## The claim being compared

There are k independent uniform four-bit source blocks. A parent retains at most B bits before a uniformly selected block R and omitted coordinate O are disclosed. The child computes one bit from the parent state, R, and O. Only afterward is the queried coordinate J selected uniformly from the other three coordinates. The final decoder sees the child bit and the public indices, but cannot recover the parent or source.

The local derivation establishes that attaining the isolated-child error 1/4 requires and is possible with B = 3k. At B = 2k it derives error strictly greater than 1/4 + 1/512 for every k, including arbitrary joint encoders. The latter constant is conservative, not an exact optimum. The separate one-block optimum 9/32 does not itself establish the uniform gap.

## Primary material read

### 1. Functional compression and characteristic graphs

Vishal Doshi, Devavrat Shah, Muriel Médard, and Michelle Effros, *Functional Compression through Graph Coloring*. Reviewed the [author-hosted full manuscript](https://www.mit.edu/~medard/2010papers/funccomp.pdf), especially Sections II-A–C and III-A, Definition 2, and Theorem 13. This check uses that manuscript's statements, not a line-by-line comparison with the published version.

The characteristic graph separates two source values whenever a possible decoder-side observation requires different function values. A valid description must distinguish adjacent values. The paper also treats graph powers and establishes an asymptotic conditional coloring-entropy characterization. Its operational asymptotic rates must not be substituted for our finite, hard state-count constraint.

**Overlap:** once the optimal child branch functions are fixed, preserving every branch decision is a functional-compression problem. Our signature is the vector of function values over all branches. Counting distinct signatures is a special case of the characteristic-graph method; the graph and entropy viewpoints are not new here.

### 2. Information cost already supports direct-sum lower bounds

Rahul Jain, Jaikumar Radhakrishnan, and Pranab Sen, *A direct sum theorem in communication complexity via message compression*, [arXiv:cs/0304020v2, April 14, 2003](https://arxiv.org/pdf/cs/0304020v2). Reviewed the introduction, Section 2.3 (Definition 2 and Facts 6–7), and the statements of Theorem 4 and Corollary 3.

Section 2.3 defines information cost, records its lower-bound relation to communication, and explicitly gives superadditivity across independent copies under product distributions. The paper combines this with message compression to obtain bounded-round communication direct-sum results, with error slack and constants depending on the number of rounds.

**Overlap:** the step from per-block information requirements to a lower bound on a joint message is standard. Our proof's inequality sum_r I(X_r; M) <= I(X_1,...,X_k; M) <= H(M) is an elementary instance of that approach. It does not require independent block encoders, and accommodating arbitrary joint encoders is not by itself a new direct-sum technique.

### 3. A stronger one-way result and an indexed-query formulation

Rahul Jain, Jaikumar Radhakrishnan, and Pranab Sen, *Optimal Direct Sum and Privacy Trade-off Results for Quantum and Classical Communication Complexity*, [arXiv:0807.1267v1, July 8, 2008](https://arxiv.org/pdf/0807.1267v1). Reviewed Section 1.1, Theorem 1, Definition 1, and Section 3.2. The manuscript identifies a preliminary version at the 2005 Computational Complexity conference. The detailed Section 3.2 argument is quantum; the paper says it omits analogous classical proofs.

Theorem 1 includes a classical public-coin one-way direct-sum bound for relations: the communication for multiple instances grows linearly, allowing error slack. Section 1.1 defines success on the overall output. Definition 1 also gives an indexed-copy problem where Bob receives an index, earlier source strings, and a local query.

**Overlap and limit:** delayed identification of a relevant copy and linear communication scaling are established themes. The overall-output guarantee and indexed-copy access pattern differ from our uniform single-query loss and the replacement of the parent by a single child bit. This theorem does not directly provide our exact coefficient 3 or the explicit gap at coefficient 2.

## What the comparison establishes, and what remains unresolved

The following mapping is our deduction from the source definitions and the local proof, not a theorem claimed by those papers.

For fixed optimal child decoders, two parent inputs need different states exactly when some branch's optimal decision differs. Hence the exact-attainment graph is complete multipartite, with one part per distinct signature. Independent blocks produce a product of signature ranges. Once the four-bit lemma supplies at least eight signatures per block, the 8^k state count and 3k bit lower bound follow by standard counting. The substantive local work is forcing these optimal branch decisions and proving the eight-signature lower bound uniformly over decoder choices.

For the positive gap, the extra local ingredient is quantitative stability: near-optimal error forces approximate recovery of branch signatures whose entropy exceeds two bits. The conditional-error entropy bound and information superadditivity then turn that local fact into a uniform bound. The four-bit signature-entropy estimate and the conversion from excess error to signature prediction error warrant comparison as specific lemmas; the information argument itself should receive standard attribution.

A useful boundary check is that retaining two individual source bits per block already gives error 1/4 if the final decoder may inspect the parent after seeing J: half the queried bits are known and the rest can be guessed with error 1/2. Consequently an ordinary one-way INDEX lower bound for that relaxed access model cannot prove our strict excess over 1/4. The intermediate one-bit state formed before J is essential to the claim. A reduction to prior work must preserve that restriction rather than merely identify a late query.

**Unresolved:** this focused check did not locate or exclude the same four-bit construction, the exact 3k attainment result, or an equivalent quantitative theorem for this precise two-stage access contract. It also did not audit the full proofs of the three sources. Further priority review should target those items, including formulations under different terminology; absence from these sections is not evidence of novelty.

**Recommended qualification:** describe the result as a specific finite delayed-query separation, proved using established functional-compression and information direct-sum methods, with novelty of the construction and constants still under review. Avoid presenting it as a new general direct-sum principle or claiming that delayed queries themselves are new.
