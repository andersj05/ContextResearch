# External review packet: irreversible compression with delayed queries

September 19, 2026. **Prepared for review; no external reviewer has been contacted and no external endorsement has been received.** This packet separates proof correctness, computation reproducibility, and novelty. A positive answer to one does not settle the others.

## The precise problem

Let X be uniform on {0,1}^4. An encoder observes X and produces M with at most four values. An independent uniform omitted coordinate O is then disclosed. An updater computes one bit Z = U(M,O). Finally J is drawn uniformly from the three coordinates other than O. A decoder predicts X_J using only Z,O,J. Minimize average bit error over X,O,J.

Programs and public codebooks are fixed before X is sampled. Capacities are hard bounds on state cardinality. Neither the updater nor decoder can reread X; the decoder cannot read M. There is no archive, hidden transcript, source-dependent public label, or auxiliary memory channel. Independent randomness is allowed but cannot lower the optimum: fixing its complete tape yields an admissible deterministic code, and randomized loss averages deterministic losses.

For k independent four-bit blocks, first form M from all blocks. Then disclose independent uniform block R and omission O, form one bit Z = U(M,R,O), and only then disclose uniform J among the remaining coordinates in block R. The decoder has Z,R,O,J. The parent may encode the blocks jointly.

## Results submitted for scrutiny

| Statement | Current evidence | Boundary |
|---|---|---|
| The four-bit, two-bit-parent chain has exact error 9/32 = 54/192. | [Finite search reduction and witness](EXACT_CHAIN_OPTIMUM_2026-09-19.md); complete enumeration of S(16,4) = 171,798,901 partitions, with 128 attaining partitions. | A checked computation with a mathematical reduction, not a formally verified lower-bound certificate. |
| A source-aware one-bit encoder for the revealed triple has optimum 1/4; three parent bits suffice to attain it through the chain. | [Original construction](LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md) and [compatibility certificate](../experiments/dependency_memory/results/compatibility_certificate.json). | The difference 1/32 applies to this one-block model. |
| For k blocks, attaining error exactly 1/4 requires and is attained by 3k parent bits. With 2k bits, error is strictly greater than 1/4 + 1/512. | [Block derivation](CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md), [analytic audit](PROOF_AUDIT_2026-09-18.md), and independent finite ingredient checks. | Allows joint encoders; does not establish the exact multi-block error or a 1/32 gap for every k. |

The September 18 audit's sentence saying the exact finite optimum was uncomputed is historical; the separate September 19 computation supplies that result. None of these statements establishes LLM superiority, an economic gain, or novelty.

## Review questions with concrete acceptance criteria

1. **Completeness of the finite reduction.** Check refinement from at most four parent cells to exactly four; restricted-growth enumeration without duplication; all eight binary child splits modulo label exchange, including constant splits; and coordinatewise majority decoding. For v_j(U) equal to the number of ones minus zeros in coordinate j over U, verify the branch error count 24 - sum_{j != o}|v_j(U)| and total error 96 - G(P), with denominator 192. Identify any admissible code excluded by the reduction.
2. **Independent computation.** Reproduce the complete count, maximum gain 42, and 128 optima using another compiler or independently written enumerator. Grade all 192 cases of the explicit two-function witness independently. Matching only the optimum or the leaf count does not establish enumeration completeness; the reduction and implementation also require review.
3. **Exact block threshold.** Verify that equality at 1/4 forces an optimal complementary decoder and unique branch decision on every positive-probability source. Check the signed-majority cubic-rank argument, antipodal range of at least eight signatures, and Cartesian-product lower bound of 8^k parent states without assuming separately encoded blocks.
4. **Robust block gap.** Audit the entropy bound H(Y) >= 4 - (5/8)log2(5) > 5/2, noncomplementary-branch penalty 1/48, signature mistake bound p_r <= 12 delta_r, and conditional entropy bound h2(p_r) + 4p_r. Check the direction sum_r I(X^(r);M) <= H(M), the averaging over good/bad blocks, and the strict endpoint at delta = 1/512. A stronger bound is welcome but is not required to validate this one.
5. **Priority and theorem transfer.** Supply a precise theorem and an explicit variable/access mapping if an existing result already implies any statement. Preserve fixed cardinalities, late public queries, the source-inaccessible updater, and the one-bit final state. A difference in terminology alone is insufficient to support novelty.

## Two additional primary-source comparisons

**Functional compression.** [Doshi, Shah, Medard, and Effros, author-hosted manuscript](https://www.mit.edu/~medard/2010papers/funccomp.pdf): Section II-A/B definitions and Section II-C/III-A through Theorem 13 were read on September 19. Their characteristic graph distinguishes source pairs that some decoder side information separates; graph powers and conditional coloring entropy characterize asymptotic functional compression. The [author's publication list](https://effros.caltech.edu/publications) identifies the journal article as *IEEE Transactions on Information Theory* 56(8), 3901–3917 (2010). The hosted manuscript was not compared line by line with that published version, and its proofs were not audited here.

Our inference: once optimal branch functions are fixed, our complete-multipartite signature graph is a simple instance of this established language. The open question is whether existing approximate functional-compression or direct-sum results directly yield our hard-capacity gap, with the extra one-bit intermediate restriction. Do not claim a new general graph principle.

**Causal successive refinement.** [Zhou and Hero, arXiv:1901.01356v2](https://arxiv.org/pdf/1901.01356v2), dated February 23, 2019: Sections II-A/B (Definitions 1–2, Theorem 1) and Section III-B (Theorems 3–4) were read on September 19. Every encoder sees the original source block, and decoder j retains messages S_1 through S_j alongside causal side information. Their converse includes a finite-blocklength probability bound and an asymptotic exponential strong converse. The full proof was not audited. [Publisher metadata](https://www.mdpi.com/1099-4300/21/4/410) lists *Entropy* 21(4), 410 (2019), DOI 10.3390/e21040410; the version read was the arXiv manuscript.

Our inference: chronological side-information revelation is established prior art. This access pattern differs from our source-inaccessible updater and discarded parent message. Theorem transfer remains a concrete reduction question; the existence of a finite-blocklength theorem alone does not settle our finite optimization.

These readings supplement the [existing comparison](LITERATURE_POSITIONING_2026-09-18.md) with successive refinement, cascade source coding, caching, and action-dependent information. They narrow the claim; they do not certify priority. The [bibliography](../paper/references.bib) and [reading guide](../sources/READING_GUIDE.md) record source-specific review scope.

## Minimal reproducibility bundle and review record

Provide this packet together with the linked derivations, [search implementation](../experiments/dependency_memory/exact_chain.py), [search certificate](../experiments/dependency_memory/results/exact_chain_certificate.json), [independent scaling audit](../experiments/dependency_memory/audit_scaling.py), and [scaling certificate](../experiments/dependency_memory/results/scaling_audit_certificate.json). No model credentials, raw sessions, or held-out task answers are needed.

From the repository root:

```powershell
python -m unittest discover -s experiments/dependency_memory -v
python scripts/validate_context_repo.py --exact-chain-compiler clang
```

The second command requires a C99-capable compiler; ordinary validation without that flag checks the recorded artifacts without repeating the complete search.

When an external review actually occurs, append its date, reviewer-provided scope, reviewed commit, reproduction environment, objections/counterexamples, and responses. Record mathematical correctness, computational reproduction, and novelty opinions separately. Until then all three external-review outcomes remain **pending**.

## September 21 addition: unrestricted rate-two certificate

The [new derivation](DECODER_COMPLETE_FRONTIER_2026-09-21.md) proves an all-k lower bound of 0.2618989799 and a limiting upper bound of 0.2618989801. The [standard-library generator](../experiments/dependency_memory/joint_coding/decoder_frontier.py) covers all 36^4 decoder tables via 4,751 disjoint symmetry orbits, including repeated and noncomplementary pairs. Its dual inequalities, information reduction, and coding achievability are distinct proof obligations.

Review the potential-output variable A_r as a function of M, the direction of the sum-information inequality, decoder labels and coordinate actions, the Jensen/KL dual bound, integer ceiling directions, rational logarithm enclosures, and strict rate slack. Independent tests include a Burnside count, actual query losses, and actual channel mutual information. A numerical optimizer is unnecessary for verification.

The priority question includes this particular tightly quantified composition penalty. Strategy alphabets, rate-distortion duality, and information direct sums are attributed to earlier work. No external review or outreach has occurred.
