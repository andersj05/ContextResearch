# Mathematical questions in repeated agent compaction

Research addendum, September 16, 2026. This separates published results, elementary deductions under stated assumptions, and proposed experiments. It does not establish novelty or report new experiments.

The most useful starting point is a memory-limited controller interacting with an environment. Transcript length, memory capacity, and task difficulty are different quantities. A thousand-step task may require carrying one bit; a short task may require preserving hundreds of independent facts.

There is substantial relevant academic work. Nagle et al., **Fundamental Limits of Prompt Compression** (NeurIPS 2024), formulate a distortion–rate optimization for hard prompts consumed by a fixed black-box model. Their experiments illustrate the importance of knowing the downstream query. This is a rigorous starting point, with a restricted setup and small experimental settings; it is not a performance bound for arbitrary coding-agent runs. [Paper](https://proceedings.neurips.cc/paper_files/paper/2024/hash/ac8fbba029dadca99d6b8c3f913d3ed6-Abstract-Conference.html)

## 1. Compression as state abstraction in a controlled dynamical system

Let history be h_t, retained memory m_t, the next action a_t, and the next observation o_{t+1}. A simple agent has

\[
a_t\sim\pi(\cdot\mid m_t),\qquad
m_{t+1}=C(m_t,a_t,o_{t+1}).
\]

The environment's transition law completes the system. External archives, retrieval, and caches must be included when they affect available information or cost. A rolling-summary-only agent and an agent that can search its complete past have different information constraints.

The goal is a compact state that supports good future decisions. Preserving the wording of history is only a possible surrogate. Two histories may be merged when the differences between them cannot change relevant predictions or decisions; merely producing the same immediate action is insufficient.

This has a direct precedent in **approximate information states**. Subramanian et al. (JMLR 2022) give conditions involving reward prediction and prediction of the next information state, or recursively updating state and predicting observations. Approximate versions lead to bounds on policy suboptimality. These are assumptions to establish for an agent, not guarantees obtained by calling its summary an information state. [Paper](https://jmlr.org/papers/v23/20-1165.html)

An adjacent foundation is **predictive state representations**, which represent state through action-conditioned predictions of future observations. That suggests a useful question: can a compactor preserve the predictions needed by the remaining task more economically than it preserves a chronological narrative? [Littman, Sutton, and Singh, NIPS 2001](https://proceedings.neurips.cc/paper/2001/file/1e4d36177d71bbb3558e43af9577d70e-Paper.pdf)

**A tractable stability question.** Suppose reference and compressed states have a common representation and metric. If the reference update F is L-Lipschitz and a compressed update introduces at most epsilon_t additional error, a triangle-inequality argument gives

\[
e_{t+1}\leq L e_t+\epsilon_t,
\qquad
e_T\leq L^T e_0+\sum_{t=0}^{T-1}L^{T-1-t}\epsilon_t.
\]

For constant epsilon, L<1 gives a bounded geometric contribution, L=1 permits linear accumulation, and L>1 permits amplification. This is an elementary conditional bound, not a theorem about present LLMs. When actions change the environment, the comparison must account for that feedback—for example through joint state dynamics or a justified coupling of stochastic trajectories. Token strings do not automatically supply a useful smooth metric.

Two pitfalls matter. First, a summary can converge to a stable but useless fixed point, so stability must be paired with decision sufficiency. Second, a small next-step discrepancy can hide a large delayed failure: a forgotten constraint might not become actionable for fifty steps.

A separate elementary reliability bound needs no smoothness. If each of q compactions has probability at most delta of losing a necessary fact, the union bound gives probability at most q*delta of at least one such loss. Independence is unnecessary. This is an upper bound, not a prediction that observed failure will grow linearly; defining and measuring “necessary” is the hard part.

## 2. Sparsity of live dependencies

There are at least three distinct kinds of sparsity: few tokens receive large attention weights; a computation admits a low-rank approximation; or only a small subset of historical facts remains relevant to unfinished work. The third is especially useful for harness design, but does not follow from either of the first two.

**A counting example.** There are n named fields, exactly k are active, and each active field holds an arbitrary b-bit value. Assume every support/value configuration is possible; later queries can distinguish any two configurations; and no archive or other side channel reveals the missing data. Any fixed-capacity, exact memory representation requires

\[
B\geq\log_2\binom{n}{k}+kb
\]

bits. There are binomial(n,k)*2^(kb) distinguishable states, so fewer memory codes force a collision. If the active support is already supplied to the decoder for free, its encoding term disappears. This is a standard counting argument, not a new compression theorem.

It explains why the number of live dependencies is a better candidate difficulty variable than elapsed turns alone. It does not establish that a language model can use a representation near this bound. Model-readable tokens are not interchangeable with arbitrary bits; the representation, decoder, error tolerance, and distribution all matter.

**Qualification from the subsequent investigation:** hindsight relevance is not enough. If n independent bits are observed before compression and a queried index is disclosed afterward, only one bit is eventually used, but exact memory still requires n bits. The compressor's information about possible future dependencies matters. Moreover, representations that meet separate compression targets may not compose through successive bottlenecks. The follow-up research proposal and runnable finite examples investigate both distinctions.

Recoverable history changes the problem. A small live memory plus an archive may suffice, with retrieval latency, query generation, reading cost, and missed retrieval becoming part of the objective. Charging for those operations is essential to a fair comparison.

**Why attention scores are insufficient.** A rarely referenced fact can determine a later action. H2O gives a concrete example of attention-based KV eviction, retaining recent tokens and accumulated heavy hitters and analyzing a dynamic submodular formulation under assumptions. Its result does not establish that future agent-task utility is submodular. [H2O, NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/6ceefa7b15572587b78ecfcebb2827f8-Abstract-Conference.html)

In fact, a toy task immediately exposes a problem with that assumption: fact a identifies the required file, fact b gives its required checksum, and a check succeeds only with both. Utility can satisfy f(empty)=f({a})=f({b})=0 and f({a,b})=1. This violates diminishing returns. Selecting individual facts by standalone importance can discard a jointly essential pair.

**Subtask summaries as interfaces.** If future work depends on a completed subtask only through its output, completion evidence, side effects, and unresolved obligations, those form a candidate boundary representation. Its internal trace may be dispensable. Whether that conditional-independence claim holds is the substantive question. “Done” alone usually omits too much.

For example, a useful boundary record might be: migration applied to database revision r; verification passed under configuration c; backup artifact p must remain until final validation. Detailed intermediate commands can move to an archive. This is a proposed representation, not a proven sufficient state for arbitrary migrations.

HiAgent already uses subgoals to organize working memory and replaces prior subgoal traces with summaries. Thus hierarchical summarization itself is established prior work. A research contribution would need sharper conditions, stronger evaluation, or a demonstrated improvement. [HiAgent, ACL 2025](https://aclanthology.org/2025.acl-long.1575/)

In a workflow with known dependencies, task ordering also changes which facts must coexist in memory. Investigating the maximum live dependency set connects naturally to register allocation and graph-based scheduling. Any exact correspondence to graph width or pebbling would require specifying the computation and recomputation model first.

## 3. Where neural tangent kernels help

The classical NTK is built from derivatives with respect to trainable parameters:

\[
K_\theta(x,x')=J_\theta f(x)J_\theta f(x')^\top.
\]

It relates parameter-gradient learning to function-space dynamics, with a fixed limiting kernel under suitable infinite-width assumptions. Its strongest simple linear dynamics concern squared-loss training. [Jacot, Gabriel, and Hongler, NeurIPS 2018](https://arxiv.org/abs/1806.07572)

There is a direct nearby result: Liang et al. analyze training ultra-long soft prefixes using NTK in a stylized setting and construct an efficient approximation of prefix attention. This concerns learned prefixes and parameter-efficient adaptation; it is not an analysis of deleting arbitrary tool messages. [Towards Infinite-Long Prefix in Transformer, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.563/)

For a learned differentiable compressor C_phi feeding a frozen executor f_theta, define g_phi(h)=f_theta(C_phi(h)). An NTK with respect to phi is meaningful. In a justified fixed-kernel, squared-loss approximation, training residuals obey an equation of the form

\[
\dot r=-Kr.
\]

Small-eigenvalue components decay slowly. That suggests studying whether task distinctions associated with delayed constraints are learned poorly by a compressor. Their alignment with those eigendirections must be measured or proved; rarity alone does not establish it. Ordinary discrete summaries are not differentiable without additional machinery, and real training need not stay in this kernel regime.

For **a frozen model at inference**, the more direct local object is the derivative with respect to input embeddings z:

\[
f(z+\Delta z)-f(z)\approx J_zf(z)\Delta z.
\]

This is input sensitivity, not the parameter NTK. It suggests searching for perturbation directions that affect the relevant outputs little. However, deleting text changes length, positions, and often semantics; it can be far outside a local approximation. White-box derivatives also are not normally exposed by a black-box API. Sensitivity measured on today's question may fail on tomorrow's question.

My assessment is that NTK is a credible route for understanding **training a compression representation**. State abstraction and information theory provide a more direct starting point for improving a black-box agent harness today.

## 4. An experiment that could distinguish these explanations

Build an inspectable workflow environment with changing facts, prerequisites, and delayed obligations. Independently vary action horizon, dependency delay, maximum simultaneously live facts, fact revisions, distractor volume, and number of compactions. This separates long transcripts from large information requirements.

Start with a scripted controller and exact state to establish solvability, then freeze one executor model. Compare recent-history truncation, rolling prose summaries, structured summaries, constraint pinning, and a candidate dependency-aware representation. An oracle that sees true live dependencies is a diagnostic upper reference, not a deployable competitor.

First give all methods no retrieval. Then repeat with equal archive permissions and metered retrieval. Measure terminal success, violated obligations, repeated work, recovery effort, all model calls, cached and uncached tokens, and latency. Probe recall and next-action agreement are useful diagnostics but cannot replace task completion.

Checkpoint comparisons must restore the environment as well as conversation state. Reusing an altered filesystem for the second continuation would confound a compaction comparison. Keep training/search tasks separate from final evaluation and include simple structured-memory baselines.

The strongest candidate question is:

> Under which dependency structures can a recurrent memory representation retain reliable task performance with a budget governed primarily by the live dependency set, and how does error accumulate when that representation is approximate?

A second systems question is when to compact or retrieve once cache disruption, compressor cost, and recovery cost are included. A smaller token count is only one term in that optimization.

These are research directions, not claims that their solutions are absent from the literature. The immediate opportunity is to connect explicit assumptions and measurable failure mechanisms to the behavior of real agent loops.
