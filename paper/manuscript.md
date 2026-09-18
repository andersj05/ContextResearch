# Repeated Context Compression with Delayed Task Dependencies

Working draft — September 18, 2026. Authorship and venue are not set. This draft reports a finite mathematical diagnostic. A subsequent [scaling derivation](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md) is recorded separately pending independent review and novelty comparison; it is not incorporated as a manuscript result. Agent evaluation remains open.

## Abstract

Long-running language-model agents must preserve information whose relevance may only become clear later. We study a finite model in which a memory first compresses independent values, then observes a subset of potentially relevant coordinates, compresses again, and finally receives a query. This separates memory capacity from the timing of task information. In a four-bit example, the minimum distortions of the isolated bottlenecks do not characterize the achievable distortion of their composition: attaining the child-optimal error of one quarter requires three initial bits, while two are insufficient. An analytic argument and exhaustive finite certificate establish this obstruction. We outline controlled experiments to assess whether analogous losses affect practical context management, accounting explicitly for retrieval, provider-managed reasoning state, and cache costs. No improvement over a deployed agent harness is claimed.

## 1. Introduction

An agent's transcript grows with its activity, but the amount of information needed for its next decisions need not grow at the same rate. A long sequence of completed independent subtasks may leave only a small number of unresolved facts. Conversely, a short history can contain many values that a later instruction may distinguish. The relevant resource is therefore not transcript length alone, but the information required to support possible continuations.

Prompt compression has already been studied through rate–distortion formulations, and hierarchical agent memory already summarizes work around subgoals. These provide foundations rather than novelty claims for the present study [@nagle2024; @hiagent2025]. Our question concerns the compatibility of representations across successive bottlenecks when additional task information arrives between them. Classical successive refinement establishes that separately optimal descriptions need not compose without suitable structure; translating that insight to a finite, shrinking-memory, delayed-query protocol requires stating the information constraints precisely [@equitz1991].

The practical motivation is a completed subtask whose result is needed later. A record saying that the subtask is finished may preserve immediate continuity while losing an identifier, qualification, or negative result required by a subsequent obligation. The present mathematical model abstracts this timing issue. It does not model all semantics of natural-language summaries or all behavior of a tool-using agent.

## 2. Model and information timing

Let X = (X_1, ..., X_n) be independent fair bits. Independently of X, a subset S is drawn from a specified family F. A coordinate J is then drawn uniformly from S. The task is to answer X_J.

The first encoder observes X and retains M_1 = E(X), with at most 2^(B_1) states. After S is revealed, an updater forms M_2 = U(M_1, S), with at most 2^(B_2) states. The final decoder observes M_2, S, and J. Neither the updater nor decoder can reread X.

The programs and codebooks are fixed before the instance is sampled. S and J are public control information at their specified stages; their descriptions are not charged to the value-memory budget in this toy model. This convention must not be confused with a claim about total implementation bytes. An archive or opaque provider state that contains X would change the information constraints.

Define D_chain(B_1, B_2; F) as the infimum of the probability of an incorrect answer over valid encoders, updaters, and decoders. Let D_1(B_1) be the optimum when only the first bottleneck remains, and D_2(B_2) the optimum when the second encoder can observe the original X together with S. Every chain satisfies

```text
D_chain(B_1, B_2; F) >= max(D_1(B_1), D_2(B_2)).
```

We ask when this inequality is strict and how much additional first-stage memory is needed to attain the relaxed target. The composition gap is the difference between the two sides. Its dependence on the family F is the proposed subject of further analysis.

## 3. A finite incompatibility example

Take n = 4, let S be uniformly selected from the four three-coordinate subsets, and set B_2 = 1. The isolated first bottleneck with B_1 = 2 has optimum error 3/16. The isolated second bottleneck has optimum error 1/4. Nevertheless, a two-bit-then-one-bit chain cannot attain error 1/4.

For three fair bits encoded into one bit, a decoder chooses two prediction vectors from eight possibilities. Among the 28 unordered pairs, exactly four attain error 1/4: the complementary pairs. The nearest prediction is unique for every source string because the dimension is odd. Thus any child-optimal encoder implements a signed majority decision.

To attain the optimum after every possible S, the parent memory must support one appropriate signed-majority decision for each of the four triples. Let f_i be the chosen signed majority on the triple omitting coordinate i. In sign notation, x_i in {-1, +1}, each f_i contains a nonzero cubic Fourier monomial on its own triple. That monomial appears in no other f_j, so the four functions are linearly independent. Their joint output vectors therefore span four-dimensional space. Each function is odd, so the joint range is centrally symmetric. A centrally symmetric set spanning four dimensions requires at least four antipodal pairs: at least eight distinct parent states.

Two bits provide only four states and cannot support these branch decisions. Three bits suffice: the joint signature of the four ordinary unsigned majorities has eight possible values. Its values are the all-positive and all-negative vectors and the six vectors with two positive coordinates. Store the signature's fixed codebook index, then select the required branch decision after S is revealed.

The accompanying enumeration checks all 4^4 = 256 assignments of optimal child decoders. The required numbers of parent states are 8, 10, 12, and 16, appearing in 56, 96, 96, and 8 assignments respectively. The explicit three-bit witness is graded on all 192 equally likely source/subset/query cases.

Since 1/4 corresponds to 48 errors among those 192 cases, impossibility gives the conservative lower bound D_chain(2, 1; F) >= 49/192. Randomized mixtures cannot improve on the best deterministic average loss in this finite setting. **The exact chain optimum for two initial bits has not been computed.**

This is a checked finite obstruction. It is not presented as a new general successive-refinement theorem. The full formulae, proof, certificate, and implementation are maintained with the research artifacts.

## 4. Sparse dependencies and future queries

If exactly k of n named fields are active and each stores an arbitrary b-bit value, exact memory needs at least log_2 binomial(n, k) + kb bits when every configuration can be distinguished by future queries and no external channel supplies missing information. This is an elementary counting bound. It applies to identifiable active fields, not automatically to the much smaller set that happens to be queried in hindsight.

Before an unknown uniform coordinate query to A independent fair bits, a B-bit memory with average error epsilon <= 1/2 obeys B >= A[1 - h_2(epsilon)]. This is a standard random-access information bound, not a new theorem [@nayak1999]. If relevance is revealed only after an irreversible bottleneck, it cannot retroactively restore discarded distinctions.

Sound public retirement events yield a simple feasibility reference: a dictionary can keep the current values of all unresolved records. Identifying valid retirements from natural-language evidence is a separate inference problem. The implemented record-stream diagnostic assumes explicit sound events and should be interpreted accordingly.

## 5. Proposed agent evaluation

**This section is a design, not a report of completed model experiments.**

The first LLM experiment would compare rolling prose summaries, structured summaries, and explicit unresolved-dependency records under matched visible evidence and declared budgets. Paired instances would reveal the same relevance clue before or after a binding compaction. A subsequent environment would include state-changing actions and a deterministic verifier for delayed terminal obligations.

Provider-managed state requires particular care. OpenAI's compaction interface returns opaque state and instructs clients to preserve the returned window. Anthropic documents model-dependent reasoning preservation and prefix binding. An intervention that edits history may therefore change both visible memory and reasoning continuity [@openai-compaction; @anthropic-thinking]. Controlled representation tests must enforce their declared channels; production comparisons must evaluate the complete supported intervention against an intact native baseline.

Cost accounting includes every model call, compactor call, cache read/write, retrieval, and retry. Prefix invalidation may outweigh short-horizon token savings, whereas sufficiently repeated future use may repay consolidation [@openai-caching; @anthropic-editing]. Report task success alongside cost and latency. A smaller prompt is not itself evidence of improvement.

## 6. Limitations and open results

The source values are independent bits; real tasks have semantic structure, correlated observations, and adaptive actions. The current record diagnostics are constructed examples, not independent task samples. No natural-language updater, learned dependency classifier, or autonomous benchmark has been evaluated here. The exact two-bit chain optimum, independent review and novelty assessment of the separate scaling derivation, and the prevalence of the mechanism in real agents remain open. A novelty claim also requires a fuller comparison with functional compression and causal coding [@kaspi2013].

## 7. Reproducibility

The standard-library Python artifact contains 17 tests, exact small-codebook enumeration, a 256-assignment compatibility certificate, an explicit three-bit witness, and deterministic record-policy diagnostics. Source provenance and the repository migration are documented separately. The current artifact uses no model API, network, training, or GPU. Larger experimental claims will require additional artifacts and complete run-level accounting.
