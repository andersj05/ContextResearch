# A contribution through memory limits, information timing, and action

September 18, 2026. Exploratory research memo. Sections 2-4 contain local derivations with executable finite certificates. A subsequent [local proof audit](PROOF_AUDIT_2026-09-18.md) adds an analytic entropy argument, checks independent formulations, and corrects the leave-one-out domain to n >= 4. External review and novelty assessment remain open. Sections 5-7 propose experiments, not results. This memo extends the [active proposal](LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md); it does not select a venue, model, or spending budget.

## 1. Recommended research bet

Study **when an agent should act to make its future memory requirement smaller**. An upcoming irreversible compression boundary can change the value of inspecting a manifest, resolving an ambiguity, or finishing an obligation now. The proposed controller would choose among a small set of permitted information-gathering actions and retention choices using the remaining memory budget and the possible later dependencies.

The useful deliverable is a combination of a precise limitation, a controlled environment that exposes it, and an intervention that improves terminal success at matched total cost. A new memory schema alone would not establish this contribution. Existing dependency-aware memory and active context revision already occupy much of that design space.

There is also a concrete mathematical advance available from the current four-bit example. Independent copies yield a linear exact-memory overhead, and a finite entropy certificate yields an error gap that stays positive as the number of copies grows, even for encoders that mix information across copies. This provides a better foundation than an exact-optimum obstruction alone.

## 2. A scalable block family

Let k >= 1. The source consists of k independent blocks X^(r), each containing four independent fair bits. All fixed encoders, codebooks, and policies are chosen before the instance.

Timing:

1. Observe all 4k source bits and retain M with at most 2^B states.
2. A uniform block R and an independently uniform omitted coordinate O in that block are revealed. Write S for its three remaining coordinates. Retain one bit Z = U(M,R,O).
3. A uniform J in S is revealed. Predict X^(R)_J using Z,R,O,J.

R, O, and J are public side information at their specified stages, outside the value-memory budget. There is no archive, source reread, instance-bearing program, or other memory channel. The decoder cannot read M after stage 2. The first encoder does not know R or O. Changing these assumptions changes the result.

### Exact target: 3k parent bits are necessary and sufficient

The isolated second bottleneck has minimum error 1/4. The isolated first bottleneck with 2k bits has error at most 3/16: in each block retain the majority of three fixed coordinates and the fourth coordinate exactly. The final queried coordinate is uniform over the 4k coordinates. The construction has error 3/16 per block; no optimality claim for the joint first-cut code is needed.

To attain chain error 1/4, every block/omission branch must attain its own one-bit optimum. For three fair bits the only optimal decoder pairs are complementary, and the choice of nearer codeword is unique. The [existing certificate](../experiments/dependency_memory/results/compatibility_certificate.json) proves that the joint vector of the four required decisions in a block has at least eight possible values, for every choice of optimal branch decoders.

The required signature for block r depends only on X^(r). Every combination of block inputs has positive probability, so the joint signature has at least 8^k possible values. If two different joint signatures shared one parent state, some later branch would require different child decisions from that same state. Therefore B >= 3k. This argument allows an arbitrary joint encoder; it does not assume that M allocates separate fields to blocks.

Conversely, concatenate the existing three-bit signature construction for each block. The updater extracts the indicated block and branch decision. This attains error 1/4 with 3k bits.

Thus the independently sufficient budgets 2k then 1 do not compose at the child-optimal target, and the extra parent memory needed to attain that target is exactly k bits relative to the 2k reference budget.

### A gap that remains positive under arbitrary joint encoding

For the same family and B = 2k, the stronger local derivation below gives

\[
D^*_{\rm chain}(2k,1) > \frac14 + \frac1{512}
\qquad \text{for every } k\ge1.
\]

The additive constant is conservative: about 0.195 percentage points. It is not an exact optimum, a claim of a large practical effect, or a measured LLM result.

## 3. Proof of the uniform gap

It suffices to consider deterministic schemes: random coins are independent of the instance, and the state-count capacities hold for every realization. Fix all coins to obtain a deterministic protocol with no larger average loss and the same capacity constraints. This reduction does not justify replacing the hard state-count constraint by an expected-memory constraint.

For each block r, let delta_r be its conditional error minus 1/4. Every delta_r is nonnegative, since giving the child encoder all source values cannot improve beyond the one-bit three-coordinate optimum. Let delta be the average of delta_r.

Call a block good if all four branch decoders use complementary codeword pairs. This is a definition about a fixed decoder, not a lifecycle classifier. If a block is not good, at least one branch uses a pair at Hamming distance at most two (including a repeated word). That branch has error at least 1/3, even with unrestricted source access. Averaging over its four branches gives delta_r >= 1/48. Consequently the fraction of blocks that are not good is at most 48 delta.

For a good block let Y_r be its four-bit vector of optimal branch decisions. The parent state M predicts this vector through the four updater outputs; denote that prediction by Yhat_r(M). A wrong branch decision increases the number of coordinate errors by at least one out of three. If q_r is the average probability of a wrong branch decision, delta_r >= q_r/3. The union bound then gives

\[
p_r := \Pr\{Y_r\ne\widehat Y_r(M)\}\le4q_r\le12\delta_r.
\]

The new [finite certificate](../experiments/dependency_memory/results/compatibility_scaling_certificate.json) checks every one of the 4^4 complementary branch-code assignments and establishes

\[
H(Y_r)\ge\frac52.
\]

This step uses exact integer arithmetic. If the nonzero signature fiber sizes are a_1,...,a_l, then their sum is 16 and

\[
H(Y_r)=4-\frac1{16}\log_2\prod_j a_j^{a_j}.
\]

Enumeration gives maximum product 5^10 < 2^24, attained at fibers (5,5,1,1,1,1,1,1). Therefore the stated 5/2 lower bound follows without a numerical entropy tolerance. Reversing either codeword label in a branch only permutes signatures, so the unordered decoder-pair enumeration covers all labelings. The actual minimum entropy is 4-(10/16)log2(5), approximately 2.5488 bits; the proof needs only 2.5.

The elementary conditional-error entropy bound gives H(Y_r|M) <= h2(p_r)+p_r log2(15) <= h2(p_r)+4p_r. One way to see this is to reveal whether the predicted signature is wrong, then specify which of at most 15 other signatures occurred. Since Y_r is a function of X^(r),

\[
I(X^{(r)};M)\ge\frac52-h_2(p_r)-4p_r
\]

for every good block. Give blocks that are not good the trivial mutual-information bound zero, and set their auxiliary p_r to zero for the following averaging step.

Assume for contradiction that delta <= 1/512. Then the average auxiliary p_r is at most 12 delta <= 3/128. Concavity of binary entropy and its monotonicity on [0,1/2] imply

\[
\frac1k\sum_r I(X^{(r)};M)
\ge \frac52(1-48\delta)-h_2(12\delta)-48\delta
=\frac52-168\delta-h_2(12\delta).
\]

Independence of the source blocks, rather than independence of their encodings, supplies the other side:

\[
\sum_r I(X^{(r)};M)
\le I(X^{(1)},\ldots,X^{(k)};M)
\le H(M)\le2k.
\]

The first inequality follows from conditional entropy subadditivity and the unconditional independence of the blocks. It remains valid when M mixes information across all blocks.

At delta <= 1/512 the lower bound is strictly greater than 2, because h2(3/128) < 11/64 and

\[
\frac52-\frac{168}{512}-\frac{11}{64}=2.
\]

The strict entropy inequality is certified by the exact integer comparison 3^3 * 125^125 > 2^874. This is a contradiction. It proves the claimed lower bound for arbitrary joint encoders and, by fixing random coins, randomized protocols too.

The certificate checks a finite lemma; the entropy argument supplies the result for all k. The [audit](PROOF_AUDIT_2026-09-18.md) also proves the finite entropy lemma analytically using antipodal fiber pairs. Enumerating four-bit cases alone would not establish the general result.

## 4. A useful failed direction: more memory need can hide negligible loss

An alternative extension uses n even source bits, with n >= 4, and all n subsets obtained by omitting one coordinate. The child still has one bit. Write m=n-1 and

\[
d_m=\frac12-\frac{\binom{m-1}{(m-1)/2}}{2^m}.
\]

Each optimal child decoder must use complementary codewords, inducing a signed majority on its odd-sized subset. For two codewords at distance d, the optimal average Hamming loss per coordinate is 1/2-E|S_d|/(2m), where S_d is a sum of d independent fair signs. The identity E|S_(d+1)|-E|S_d|=Pr(S_d=0) shows that the maximum over d<=m is attained only at d=m when m is odd. Thus the optimum is complementary and the encoding decision has no ties.

For unsigned majority on m odd signs, the full-degree Fourier coefficient is (-1)^((m-1)/2) * binom(m-1,(m-1)/2) / 2^(m-1), obtained by summing over Hamming weights. Signing the inputs multiplies this by the product of their signs. Thus every branch has a nonzero coefficient on its full (n-1)-coordinate monomial; no other branch contains that monomial. The n branch functions are therefore linearly independent. Their joint output range spans R^n and is centrally symmetric, so it has at least 2n elements. Consequently exact attainment requires at least ceil(log2(2n)) parent bits. Two bits suffice for the first cut alone: retain a majority of n-1 coordinates and the last coordinate exactly, giving error (n-1)d_(n-1)/n.

However, a one-bit global majority passed unchanged through both bottlenecks gives

\[
0<D^*_{\rm chain}(2,1)-d_{n-1}
\le \frac{\binom{n-2}{(n-2)/2}}{n2^{n-1}}
=O(n^{-3/2}).
\]

To verify the upper bound, the final queried coordinate is marginally uniform, so this scheme has the ordinary global-majority error 1/2-binom(n,n/2)/2^(n+1). Subtract d_(n-1) and simplify. The strict lower inequality follows from the 2n-state requirement and finiteness of the protocol search for fixed n. This does not compute the exact chain error.

Thus an unbounded exact-memory threshold is compatible with a vanishing penalty for missing the target. The block family above avoids this particular weakness. Finite checks for n=4,6,8,10 independently grade the witness errors and unsigned-majority signature sizes; all decoder pairs are checked for child lengths 1,3,5,7. The lower bound for arbitrary n comes from the argument, not from those finite samples.

## 5. Creative extension: act before forgetting

Now make some relevance clues available through a permitted, costly tool action before compression. The question becomes whether the reduction in future decision loss justifies acquiring the clue while the original information is still accessible.

Example environment: an agent sees temporary artifact receipts from several build jobs. A manifest determines which receipts will later be needed. The agent can inspect available manifest metadata before a memory boundary, finish an eligible obligation early, or retain information covering the still-possible branches. Revisions, inspection cost, unavailable clues, and transient observations make these choices consequential. Completing an obligation must actually discharge it under the task contract; a `done` marker is insufficient.

For the block family, revealing R early reduces the exact parent requirement to three bits, while revealing both R and O early reduces it to one. This is an elementary change in the information contract, not compression of the same input under the old contract. It motivates an action-cost experiment; by itself it does not establish an algorithmic gain. Probe responses must not leak source values, and public action choices or transcripts must not become an uncharged instance-memory channel.

Candidate hypothesis: **a policy that selects information-gathering actions using the upcoming memory budget improves the success/cost frontier when relevant clues are obtainable before a binding boundary.** Test the interaction with budget: the benefit should shrink when memory is ample, and costly or unavailable clues should sometimes make probing a poor choice.

This needs explicit prior-work comparison:

- [ARC, Sections 3.1-3.3](https://arxiv.org/html/2601.12030v1) already studies active context revision. The reviewed method separates internal reflection from action generation. The proposed distinction is selecting external actions for their effect on memory requirements, not the word "active."
- [Source Coding with a Side Information "Vending Machine"](https://arxiv.org/abs/0904.2311v2) already studies actions, side information, rate, distortion, and cost. Its abstract was reviewed here; a theorem-level comparison remains necessary.
- [Cascade Source Coding with a Side Information "Vending Machine"](https://arxiv.org/abs/1207.2793v1) is even closer because it includes multiple stages and jointly designed control and source descriptions. Only its abstract was reviewed here; do not claim that the action extension is an unstudied information-theoretic problem.

The specific opportunity is a causal repeated-memory formulation and an operational agent policy with evidence of usefulness. The broad idea of acquiring information to improve compression is established.

## 6. Useful artifact regardless of whether the new policy wins

Build a compaction test environment with executable delayed continuations. For each checkpoint, preserve a reproducible pre-compaction state and compare paired continuations after restoring both context and environment. Search development continuations for small witnesses to a lost dependency; reserve separate templates and seeds for final evaluation.

The distinguishing diagnostic is: can the compressed state preserve an obligation that becomes actionable only after a later branch reveal or revision? Report the triggering continuation and the terminal failure, not just a recall score. The result is a reproducible regression case that a harness maintainer can act on.

[TRACE, Section 4.1](https://arxiv.org/html/2608.06503v1) already supplies paired closed-loop continuations and a local verifier for blocked/repeated actions; its complete pipeline also uses end-to-end selection. The proposed extension is systematic generation and minimization of delayed-obligation witnesses. Paired evaluation itself is not our novelty claim. Adversarially selected failures diagnose vulnerability; they do not estimate typical deployment failure rates.

Use two distinct comparisons:

1. **Representation:** identical exogenous observations and clue timing for every compressor. Compare native policy where its access contract is compatible, strong structured retention, prose, and supported masking. Use a deterministic oracle for finite tasks.
2. **Action policy:** identical tools, initial information, maximum resources, and task distribution; policies choose different probes. Include always-probe, never-probe, a simple uncertainty heuristic, and the proposed budget-dependent policy. Compare total cost and terminal success, including failed runs and manager calls. An oracle choosing the best probe from evaluator state is a labeled ceiling only.

Also include a metered recovery condition. Archives, hidden session state, environment files, and probe outputs are information channels governed by the [existing protocol](../docs/EXPERIMENT_PROTOCOL.md). Token budgets in LLM runs are not identified with the bit budgets of the theorem.

## 7. Bounded next work and stopping criteria

1. Independently audit the block proof and map it against functional compression, successive refinement, direct-sum arguments, and cascade source coding. Novelty is unresolved, even if the proof is correct.
2. Tighten the finite or information lower bound if it improves an interpretable claim. The present 1/512 gap establishes robustness in n, not a compelling practical effect size. Do not make computing the exact four-bit optimum the entire project.
3. Build one generated artifact/manifest environment with a deterministic terminal verifier. Include cases where probing helps, hurts, and is unavailable. Verify the information contract with scripted policies first.
4. Prespecify one primary success/cost comparison, held-out templates, model revision, seeds, and budget. Only then run the small natural-language debugging pilot. No paid model experiment is authorized or performed by this memo.
5. Continue to a larger evaluation only if a strong baseline has a reproducible failure and the intervention improves terminal outcomes after full cost accounting. If a simple structured policy or ordinary probing matches it, report that result and retain the theorem and regression suite as the contribution.

Working paper proposition: **Which distinctions must survive repeated compression, and when can an agent cheaply eliminate the need to retain them?**

## Reproduce the completed checks

```powershell
python experiments/dependency_memory/compatibility_scaling.py
python -m unittest discover -s experiments/dependency_memory -v
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

The [new generator](../experiments/dependency_memory/compatibility_scaling.py) writes [its own certificate](../experiments/dependency_memory/results/compatibility_scaling_certificate.json). It preserves the existing four-bit outputs. No LLM performance, production savings, or exact two-bit chain optimum is established here.
