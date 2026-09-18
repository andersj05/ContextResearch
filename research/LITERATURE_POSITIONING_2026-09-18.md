# Positioning the contribution: timing, compatibility, and recovery

Working research note, September 18, 2026. This is a targeted comparison, not an exhaustive priority search or an external proof review. The [local audit](PROOF_AUDIT_2026-09-18.md) remains the authority for our mathematical assumptions.

## Research decision

Focus the next experiment on the cost of learning relevance before deletion versus recovering evidence afterward. A positive comparison with a recent-record baseline is insufficient: inexpensive reliable recovery could remove the success advantage entirely. Compute a finite reference under the same information access, then compare practical policies with it. The reference will use record selection, not arbitrary bit encoders.

The proposed contribution has two parts: a restricted compatibility example with a locally audited uniform gap, and an executable method for locating the regimes where inspection, retention, and recovery are useful. Neither is currently certified novel, and there is no measured LLM improvement.

## Closest sources and what transfers

| Source and material read | Relevant result or model | Consequence for this project |
|---|---|---|
| [Equitz and Cover](https://isl.stanford.edu/~cover/papers/transIT/0269equi.pdf), Sections II–III, especially Theorem 2 | Progressive descriptions attain their isolated rate–distortion optima under a compatibility condition on optimal reconstructions. | Compatibility is established theory. Our late subset reveal and fixed one-bit child require a separate reduction; the word “successive” does not establish novelty. |
| [Weissman and Permuter](https://arxiv.org/pdf/0904.2311v2), Section II-A, Theorem 1 and its following remark | Decoder actions follow an encoded message and control side information. The asymptotic rate–distortion–cost expression jointly optimizes actions and coding. | Paying to obtain information is not a new idea. Our inspection changes disclosure timing before a record-capacity boundary; this is a finite task-specific instance to analyze, not a replacement coding theorem. |
| [Ahmadi et al.](https://arxiv.org/pdf/1207.2793v1), Sections II-A/B and III-A | An intermediate encoder maps a received message and local side information to a downstream message; actions and reconstruction constraints determine a rate region. | This is especially close to an updater that cannot reread the source. Some side information is also visible to the initial encoder, unlike our unrevealed subset; timing and access must be mapped explicitly. Proposition 1 alone does not prove our hard-capacity statement. |
| [Wang, Lim, and Gastpar](https://arxiv.org/pdf/1504.00553v2), Sections II and III, Theorem 1 | A cache precedes the request; an update encoder subsequently sees both source and request. | Relevance revealed after caching is established. Their update has source access. Our irreversible condition excludes that access; our new recovery condition restores a limited, charged channel. |
| [Doshi et al.](https://www.mit.edu/~medard/itmanet/papers/asilomar.pdf), Section I definitions and Theorem 1 statement | Characteristic graphs describe which source values must be distinguished for function computation; conditional entropy coloring has an asymptotic characterization. | Our exact branch-signature argument has a direct elementary graph interpretation below. Do not sell a signature representation as a new general functional-compression principle. Full proof and publication metadata were not audited. |
| [Colaco and Lahjouji](https://arxiv.org/html/2607.08032v1), Sections 2 and 13 | This July 2026 preprint explicitly discusses query timing, reversibility, repeated compaction, recovery evaluation, and joint reporting of memory and cost. | A broad “rate–distortion view of repeated agent compaction” is already occupied. We need a narrower claim with explicit information channels and a reproducible causal intervention. We have not replicated its experiments or adopted its general quantitative claims. |

Reading these statements does not amount to verifying every proof or empirical claim in the cited papers. Bibliographic keys and exact review scopes are maintained in the [focused bibliography](../paper/references.bib) and [reading guide](../sources/READING_GUIDE.md). No inherited corpus review labels are changed.

## The signature argument is a special graph construction

Fix one optimal branch function f_i for every possible revealed subset. Construct a graph on source strings x, joining x and x' when some branch distinguishes them: f_i(x) != f_i(x'). In our exact-target problem every branch has positive probability, and optimality forces its chosen function on every source string. A valid parent memory must therefore assign different states to adjacent strings.

Write F(x) = (f_1(x), ..., f_t(x)). Two vertices are nonadjacent exactly when their signatures agree. The graph is complete multipartite, with one part for each distinct signature. Its chromatic number is exactly the number of signatures: one state per part suffices, and selecting one vertex per part gives a clique of that size. Also F is a deterministic function of every valid parent memory, hence H(M) >= H(F).

This is an elementary reformulation of the existing proof, not a new theorem about graph entropy. It explains why both the range count and signature entropy are natural quantities. The specific four-bit rank/antipodal argument, its uniform error-gap extension, and their relation to known direct-sum bounds still need external review and a broader priority comparison. A difference between formulations does not demonstrate that a published theorem cannot imply our result.

## Concrete next experiment and decision rule

Use the existing artifact workflow, add one explicitly metered late recovery channel, and enumerate the complete small distribution of candidate sets and final queries. An exact reference must choose its first retained set before seeing an unrevealed manifest, and its second set before seeing the final query. It must not optimize separately for each hidden final answer. Revisions and their public scheduling rule must be included rather than silently treated as independent noise.

Report achievable success versus expected incremental action cost. Memory remains a hard record-slot bound at each boundary. Expected action cost is a different constraint from a hard episode spending limit. Include positive, null, and negative inspection cases. An optimal reference inside this restricted model is a calibration tool, not an optimal natural-language memory algorithm.

Only after this comparison should a model pilot be specified. Its purpose would be to test whether a model can infer and act on the relevant dependency information, with evaluator isolation, a frozen task split, exact model revision, and declared spending. If recovery removes the practical benefit, that is a useful boundary of the hypothesis, not a failed benchmark to retune away.
