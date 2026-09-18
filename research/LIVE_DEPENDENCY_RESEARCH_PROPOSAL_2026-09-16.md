# Repeated compaction with delayed dependencies: a research proposal

September 16, 2026. This proposal follows a targeted primary-source review and a small executable mathematical investigation. The initial counting arguments and connections to coding theory are established foundations, not novelty claims. A finite compatibility obstruction is checked below; its novelty has not been established. No LLM experiments were run.

## Recommended question

> When future task dependencies become known gradually, which compressed representations can be updated through successive memory bottlenecks without additional decision error, and how much extra memory is required when they cannot?

The first project should study a finite, precisely specified model of independent facts and delayed queries. Characterize when individually attainable compression targets can be attained by one causal sequence of memory updates. Then test the predicted failure mechanism with a frozen LLM on generated tool workflows.

This is a narrower and stronger target than “use sparse memory” or “keep unfinished obligations.” It connects the live-dependency idea to an actual composition question. An implementation can begin on a laptop, and a useful negative result is possible: identifying when a requested memory budget is fundamentally insufficient, rather than attributing every failure to a bad summary prompt.

## 1. Correction to the earlier sparsity argument

Three different quantities must be separated:

- **Hindsight relevance:** facts that the realized continuation eventually uses.
- **Possible future relevance:** facts that some continuation consistent with current observations could use.
- **Representational compatibility:** whether the information retained now supports the different compressed states that may be needed later.

The earlier bound involving k active fields is valid under its distinguishability assumptions. It does not imply that a practical compressor knows which k fields are active or can attain a budget proportional to hindsight relevance.

Example: receive n independent random bits, compress, then receive a random index J and answer X_J. Only one bit is used in the realized continuation, but exact pre-query memory requires n bits. If J arrives before compression, one retained bit suffices. This is the classical INDEX/random-access setting. It is a useful reduction for our problem, not a new lower bound. [Roughgarden's communication-complexity notes](https://arxiv.org/abs/1509.06257), [Nayak's random-access-code lower bound](https://arxiv.org/abs/quant-ph/9904093).

Thus long transcripts with few unresolved, identifiable dependencies can be compressible. Long transcripts containing many unresolved possibilities need not be.

## 2. Closest prior work and the remaining candidate contribution

The search covered prompt compression, sequential source coding, random-access codes, agent memory, dependency graphs, query visibility, repeated compaction, and learned caching. Central distinctions were checked in the original mathematical setups and method sections where indicated. This is a targeted review, not an exhaustive novelty certification.

| Prior work | Relevant result or mechanism | Consequence for this proposal |
|---|---|---|
| [Nagle et al., NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/ac8fbba029dadca99d6b8c3f913d3ed6-Abstract-Conference.html) | A finite distortion–rate formulation for black-box hard-prompt compression, including query visibility. | Rate–distortion and the benefit of seeing the query are established starting points. |
| [Equitz and Cover, 1991](https://isl.stanford.edu/~cover/papers/transIT/0269equi.pdf) | Successive refinement requires compatibility between descriptions that are optimal separately. | Composition failure is a classical information-theoretic phenomenon. Our finite, shrinking-memory, delayed-query setting needs its own analysis; the classical theorem cannot simply be relabeled. |
| [Kaspi and Merhav, 2013](https://arxiv.org/abs/1301.0079) | Causal source coding with decoder side information and explicit timing constraints. | Encoder information and the timing of side information belong in the model. |
| [DeMem, May 2026 preprint](https://arxiv.org/html/2605.10870v1) | Decision-based memory distortion and online partition learning. Its formal encoder is query-aware: M_t = g_t(H_t,Q_t); the main learning model uses contextual decision instances. | Our first bottleneck occurs before the future dependency/query is known, and later updates cannot reread H_t. This is a material information-access difference, not a claim that DeMem lacks memory theory. |
| [HiAgent, ACL 2025](https://aclanthology.org/2025.acl-long.1575/) | Working memory organized around subgoals, with prior subgoal traces summarized. | Subtask summaries and hierarchical memory are existing methods. |
| [MemoBrain, January 2026 preprint](https://arxiv.org/html/2601.08079v1) | Dependency-aware trajectory memory with folding and flushing. | A dependency graph plus completed-subtask folding is not a novel method by itself. |
| [The Compaction Cliff, August 2026 preprint](https://arxiv.org/html/2608.22752v1) | Type-specific retention, including exact constraint preservation under feasible budgets and classifier assumptions. | Structured retention and constraint pinning are mandatory strong controls. |
| [TRACE, August 2026 preprint](https://arxiv.org/html/2608.06503v1) | Paired continuations from the same environment state to assess compression-induced execution regressions. | We should reuse this evaluation principle. Its stated verifier limitations also motivate delayed-outcome checks. |
| [Practical Online KV Cache Compaction, August 2026 preprint](https://arxiv.org/html/2608.00902v1) | Studies delayed future-query proxies in online agent KV compaction. | Delaying compression to obtain better relevance information is already investigated empirically at the KV level. |
| [Query Visibility Audit, July 2026 preprint](https://arxiv.org/abs/2607.11942) | Matched comparisons of query-aware and query-agnostic KV compression. | Query leakage is a known evaluation concern; our experiment must enforce information availability. |
| [MemRefine, June 2026 preprint](https://arxiv.org/html/2606.13177v1) | Compresses an existing memory store through pairwise deletion/merging, without conditioning on a particular future query. | Query-agnostic memory-store compression is also established work. |
| [Lykouris and Vassilvitskii, ICML 2018](https://proceedings.mlr.press/v80/lykouris18a.html) | Caching with fallible predictions and robustness guarantees. | Once recovery is allowed, connect to caching; do not claim predicted eviction is itself new. |

The candidate contribution is a finite causal model, compatibility bounds for specified dependency families, and controlled evidence of when that mechanism matters to tool agents. A publication claim would need a broader result or a convincing experimental finding beyond the examples below.

## 3. A precise first model

Let X=(X_1,...,X_n) contain independent fair bits. A future subset S is drawn from a specified family F independently of X. A final index J is drawn uniformly from S. The system must answer X_J.

The timing is:

1. Observe X and retain M_1=E(X), with at most 2^(B_1) possible memory states.
2. Observe S and update M_2=U(M_1,S), with at most 2^(B_2) states.
3. Observe J and answer D(M_2,S,J).

The first encoder knows the distribution and possible sets, but not the realized S or J. At stage two, X is no longer accessible. S and J are public control information at the specified stages and are not part of the value-memory budget in this toy model. Codebooks and update programs are fixed in advance; they cannot store the instance's X as uncharged program data.

Define

\[
D_{\mathrm{chain}}^*(B_1,B_2;\mathcal F)
=\inf_{E,U,D}\Pr\{D(U(E(X),S),S,J)\ne X_J\}.
\]

Now define two relaxed problems:

- D_1^*(B_1): keep only the first bottleneck; the final decoder can use M_1,S,J directly.
- D_2^*(B_2): keep only the second bottleneck; its encoder may read the original X together with S.

Every valid two-stage system satisfies

\[
D_{\mathrm{chain}}^*\geq\max\{D_1^*,D_2^*\}.
\]

The first nontrivial mathematical target is to characterize the excess

\[
\Delta=D_{\mathrm{chain}}^*-\max\{D_1^*,D_2^*\}.
\]

When is Delta zero? When is it positive? Which features of F determine the extra first-stage memory needed to make it zero? Begin with disjoint blocks, nested families, and overlapping subsets. “Overlap” alone is not proposed as a sufficient scalar statistic.

This is deliberately a restricted problem. It does not model all semantic facts, correlated values, adaptive tool behavior, or arbitrary natural-language summaries. Those restrictions make exact computation and proof possible.

## 4. Established lower bound and its limits

For A independent fair bits, a uniform future bit query, and a B-bit memory produced before the query, average error epsilon <= 1/2 requires

\[
B\geq A[1-h_2(\epsilon)],
\]

where h_2 is binary entropy. A short classical proof is useful here. If epsilon_i is the error for coordinate i, binary Fano bounds give H(X_i|M) <= h_2(epsilon_i). Therefore

\[
B\geq I(X;M)
\geq A-\sum_i h_2(\epsilon_i)
\geq A[1-h_2(\epsilon)].
\]

The last step is concavity. The zero-error consequence is B >= A. The approximate bound need not be tight for short, fixed-length messages; our enumeration explicitly shows the finite-block gap. The classic random-access literature is the appropriate foundation, rather than treating this argument as a new theorem. [Nayak](https://arxiv.org/abs/quant-ph/9904093).

If an early public clue restricts the possible query to an A-element block, the relevant bound uses A. If it arrives only after the first irreversible bottleneck, the earlier constraint still applies. For balanced blocks selected by s early clue bits, A=n/2^s. This exponential reduction belongs to that particular construction; it is not a universal conversion from clue entropy to memory savings.

A useful literature caution: a [July 2026 survey, Section 2](https://arxiv.org/html/2607.08032v1) describes H(Q) as the precise price of not knowing a query. That cannot hold universally. In the zero-error INDEX example, knowing J changes the required value memory from n bits to one, a gap of n-1, while H(J)=log_2(n). A one-answer entropy bound can miss the need to support many possible answers from the same pre-query message. Our formulation keeps that distinction explicit.

## 5. A checked example where the separate bounds are insufficient

The offline prototype provides a more interesting example than the basic INDEX reduction.

- X consists of four independent fair bits.
- The first memory has B_1=2 bits, hence four possible states.
- S is a uniformly selected three-element subset of the four indices.
- After seeing S, memory shrinks to B_2=1 bit.
- A uniformly selected member J of S is queried.

The first bottleneck alone can achieve error 3/16 = 18.75%. The second bottleneck alone can achieve error 1/4 = 25%. However, the causal two-stage system cannot achieve 25% error. Three first-stage bits, followed by one second-stage bit, are necessary and sufficient to reach 25% in this example.

Here is the finite argument, with every enumeration reproducible in the accompanying code.

For three fair bits encoded into one bit, a decoder chooses two predicted three-bit vectors. There are binomial(8,2)=28 unordered pairs. Exactly four pairs attain the optimal error 1/4: the complementary pairs. Each source vector has a unique nearer member of such a pair, so optimal encoding is a signed majority decision.

To attain 1/4 after every possible S, the first memory must support the appropriate optimal majority decision for all four triples. There are 4^4=256 choices of optimal decoder pairs across the four triples. For each choice, enumerate all 16 source strings and form the four-bit vector of required branch decisions. Different such vectors must receive different first-stage memory states, since some future S would require distinguishing them.

The complete enumeration gives:

| Distinct branch-decision vectors required | Number of decoder assignments |
|---|---:|
| 8 | 56 |
| 10 | 96 |
| 12 | 96 |
| 16 | 8 |

Thus at least eight first-stage states are necessary, while two bits provide only four. An explicit eight-state encoding using ordinary majority decisions attains the target. The code directly grades this witness over all 16*4*3=192 equally likely source/subset/query combinations.

There is also a short analytic proof of the eight-state lower bound. Write the source bits as signs x_i in {-1,+1}, and let f_i be the signed majority for the triple omitting coordinate i. Each f_i has Fourier expansion

\[
f_i(x)=\frac12\left(\sum_{j\ne i}s_{ij}x_j
-\left(\prod_{j\ne i}s_{ij}\right)\prod_{j\ne i}x_j\right),
\qquad s_{ij}\in\{-1,+1\}.
\]

The cubic monomial for f_i appears in no other f_j. Thus the four functions are linearly independent, so their joint output vectors span R^4. Each function is odd, making the joint range centrally symmetric. A centrally symmetric set spanning R^4 needs at least four antipodal pairs, hence at least eight elements. Ordinary unsigned majorities attain eight: the all-positive and all-negative outputs, plus the six outputs with two positive coordinates. This proves the minimum without relying on the enumeration histogram.

For the two-bit-then-one-bit system, impossibility of 48 errors out of 192 implies error at least 49/192, about 25.52%, for deterministic schemes. Randomization cannot improve the best average loss beyond the best deterministic choice in this finite problem. **This is a lower bound; the exact two-stage minimum error was not computed.**

The conclusion is limited but useful: individually adequate memory budgets need not compose. The missing property is the compatibility of the representations needed for possible continuations. This is an analytically justified and computationally checked finite obstruction, not a claim of a new general theorem or a measured LLM effect.

## 6. A route to a theorem

For a fixed family of branch encoders e_S, a common parent representation can support all branches exactly if it distinguishes their joint output signatures. Its minimum number of states is

\[
\left|\left\{(e_S(x))_{S\in\mathcal F}:x\in\mathcal X\right\}\right|.
\]

One must also optimize over which branch encoders attain the desired distortion. Ties, randomized schemes, nonuniform sources, and relaxed error targets require care; the four-bit example avoids ties at the branch optimum.

The research task is to turn this characterization into useful bounds and constructions for specified families F, rather than merely restating the enumeration:

1. Audit the analytic proof of the four-bit obstruction and identify its minimal assumptions.
2. Characterize exact compatibility for one restricted family, initially disjoint blocks or a simple chain of subsets.
3. Find a family in which the required extra memory grows with a structural parameter, or prove a bounded-overhead construction for that family.
4. Extend to three or more updates only after the two-stage result is understood.

Step 3 is the strongest candidate for a mathematical contribution. Steps 1 and 2 may reproduce known coding results and should be presented that way if they do. A careful comparison with functional compression, communication complexity, and successive refinement is required before any novelty claim.

This path is preferable to starting with unrestricted LLM semantics: the encoders are finite functions, losses are exact, and a small exhaustive search can refute an attractive conjecture before weeks are spent proving it.

## 7. Returning to sparse workflow state

For an exact record policy, observable lifecycle information gives a simpler baseline. Suppose values are introduced or revised in public observations; sound retirement events certify that a value cannot be used again; and at most w values remain potentially needed at any point. Keeping the current value of every unretired fact answers all permitted lookups exactly when the record budget is at least w.

That is a straightforward invariant, not a new memory algorithm. It establishes a feasibility reference. Independent b-bit values require wb payload bits at a boundary where any one can be queried exactly. Labels and metadata must also fit: a simple dictionary uses O(w(b+log n)) bits, and growing identifier spaces can introduce log-horizon overhead. Do not advertise constant total memory for an unbounded stream merely because w is fixed.

Practical difficulty enters when retirement or dependency membership must be inferred. A false retirement loses a live value; failure to recognize retirement fills memory with dead state. Explicitly distinguish exact tool-confirmed lifecycle events from LLM predictions. Storing a confidence number does not make the prediction calibrated.

The practical candidate to test is a summary with exact records for unresolved dependencies and compact outcomes for completed subtasks, updated from observable evidence. This is an established design pattern. Its possible contribution here is demonstrating, or failing to demonstrate, that it reduces the measured composition penalty relative to strong alternatives under matched information and cost.

## 8. An implementable experiment

**First, isolate representation loss.** Use the fixed event stream and a scripted reader. Facts should be unpredictable nonces, with revisions and explicit dependency-release signals. At selected boundaries, the compiler sees only its retained memory and the new observations. It cannot read evaluator state, old logs, or files holding evicted values.

**Second, introduce the LLM update problem.** Render those observations as tool results and ordinary task instructions. Compare a rolling prose summary, a structured state summary, and a summary that explicitly preserves unresolved dependencies. Use the same model, visible evidence, and output budget. A deterministic parser on structured events is a strong baseline and a diagnostic; the proposed method must not receive cleaner semantic labels than its competitors.

**Third, assess agent behavior.** Add actions that change environment state, dependency prerequisites, and a deterministic terminal verifier. Use one small realistic family, such as a temporary-file packaging workflow with changing manifest requirements and retained artifact identifiers. Only this stage supports claims about completed tasks. The current event-stream prototype does not implement this autonomous environment.

Hold out task templates and vary separately:

- Number of independent values and maximum unresolved candidate set.
- Structure of possible future dependency sets.
- Timing of relevance disclosure relative to each compaction.
- Number of compactions, delay until use, and distractor volume.
- Presence of revisions, and later the reliability of lifecycle interpretation.

The key intervention is paired: the same underlying values, future query, and task outcome, with relevance information arriving just before versus just after a binding compaction. Report the different information order explicitly; it is the treatment. Do not secretly provide an early oracle signal only to the proposed method.

A second intervention compares a single final compression with recurrent compression at matched declared budgets. Restore the environment as well as context for checkpoint continuations. Evaluate the final delayed obligation, since immediate next-action agreement can remain perfect after the decisive fact has been lost.

Use no archive initially. Then give every method the same metered archive access. Retrieval changes the problem from irreversible memory loss to storage, search, latency, and read-cost allocation; the no-archive lower bound no longer applies to the complete system.

Measure terminal success, exact retained facts, stale values, repeated work, retrieval, and all model usage. Count input/output, cached/uncached tokens, compactor calls, and metadata. Abstract bits, record slots, UTF-8 bytes, model tokens, and dollars must remain separate columns.

An initial LLM pilot can use six paired templates, two disclosure timings, three compiler methods, and one tight budget: 36 runs before replication. This is a debugging pilot, not a powered experiment. Use measured variability and a prespecified effect size to size held-out evaluation. Estimate cost from the first few runs before scaling.

## 9. What is implemented now

The standard-library Python prototype in `experiments/dependency_memory` contains:

- Exact optimal single-bottleneck encoders for one to four fair bits, enumerating decoder codebooks and choosing optimal encodings.
- Early-versus-late disclosure comparisons.
- The full 256-case two-stage compatibility certificate and an explicit achievable witness.
- A record-retention event test with long-lived and short-lived facts, revisions, retirements, and exact checkpoint serialization.
- Seventeen passing tests, including independent enumeration of binary encoders for smaller cases.

The record test ran 810 configurations. When record capacity met the generated live width, the lifecycle-aware baseline answered everything correctly in all 270 applicable runs, while the LRU-value-record baseline failed at least one query in each of its 270 counterparts. These are deliberately constructed diagnostics. They are not independent task samples, an LLM benchmark, a fairness claim against native harnesses, or evidence of a novel algorithm. A competent structured updater should solve this test.

Repeated exact serialization did not introduce loss. The single-bottleneck enumeration also confirms that storing selected coordinates is sometimes suboptimal: for three fair bits and one memory bit, a majority code gives 25% error, while keeping one fixed coordinate gives 33.33%. Thus an extractive policy cannot automatically serve as an information-theoretic optimum.

The exact chain optimum for the obstructed example, a scaling theorem, natural-language memory updates, noisy certificates, retrieval experiments, and realistic agent tasks remain future work. The proposal is ready to implement beyond this initial mathematical diagnostic; those larger results have not been obtained.

## 10. Scope, decision criteria, and feasibility

The smallest useful research unit is a two-stage theorem or counterexample family plus a controlled experiment. No foundation-model training, reinforcement learning, custom GPU kernels, or proprietary compaction internals are required.

Proceed in this order:

| Milestone | Concrete deliverable | Stop or revise if |
|---|---|---|
| Mathematical audit | Verify the finite certificate; compare the exact formulation to sequential/functional coding literature. | The desired result is already an immediate known corollary and offers no useful experimental distinction. |
| Restricted theorem | A compatibility bound or construction for one family F, with explicit budgets and information timing. | Only the original counting lower bound survives; then frame the project as an empirical study rather than a new theory paper. |
| Controlled LLM pilot | Matched-budget compiler comparisons on paired disclosure tasks, with attributable failures. | The effect is entirely parsing or output-format failure, or a strong ordinary state summary removes it. |
| Transfer test | One state-changing tool environment with held-out templates and honest cost accounting. | Gains occur only in artificial nonce recall and do not affect task completion. |

For someone comfortable with Python and basic probability, extending the existing diagnostic is modest work; proving a general compatibility result is the uncertain component. A realistic first scope is several weeks of focused work, with the initial theorem search and pilot evaluated separately. Publication-quality theory or broad deployment claims could take much longer.

The defensible proposed claim is conditional: **the structure and timing of unresolved dependencies can impose a composition cost beyond the distortion implied by each memory limit in isolation; a practical memory policy should be evaluated on whether it avoids unnecessary portions of that cost.** Establishing how often this matters in real agents is the empirical question, not an assumption of the proposal.
