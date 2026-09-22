# Feedback-loop prior art and what remains open

Reviewed September 22, 2026. Focused primary readings; no systematic priority
claim, no replication, and no inherited broad-corpus review upgrades.

| Source | Read scope | Consequence for this project |
|---|---|---|
| [WiCER v1](https://arxiv.org/html/2605.07068v1) [@wicer2026] | Sections 7.1-7.2, Algorithm 1, Appendix I | It already accumulates preservation constraints. The appendix discusses approximate verification and content displaced by repairs. Neither cumulative feedback nor identifying this risk is new. |
| [TRACE v1](https://arxiv.org/html/2608.06503v1) [@trace2026] | Sections 4.1-4.2 | Paired execution from restored PRE/POST states and verifier-guided compressor optimization are direct precedents. Our finite all-policy obstruction is a different signal, not evidence of a better method. |
| [Microsoft Research: Memento](https://www.microsoft.com/en-us/research/articles/memento-teaching-llms-to-manage-their-own-context/) [@memento2026article] | Dated title/byline, training-data construction and dual-information-stream sections | The pipeline retries compression using specific judge feedback. It also describes information persisting in retained KV representations. This is a primary research-team article, not an independent reproduction or a full paper review. |
| [Clarke et al., author-hosted CEGAR manuscript](https://www.cs.cmu.edu/~emc/papers/Conference%20Papers/Counterexample-guided%20Abstraction%20Refinement.pdf) [@clarke2000cegar] | Abstract, introduction, refinement overview and finite termination discussion | Counterexample-guided refinement and finite progress arguments are established. Our unsafe groups are real memory insufficiencies under a contract; they are not automatically the spurious program traces in the original formulation. |
| [Zhang, Wu and Lin v4](https://arxiv.org/html/1701.06209v4) [@zhang2017pomdp] | Abstract, Section II-A definitions, Section IV-B overview and counterexample-check description | Refinement under partial observability also predates this project. No theorem transfer to our bounded compressor is established; proofs were not audited. |
| [Self-Refine v2](https://arxiv.org/abs/2303.17651v2) [@madaan2023selfrefine] | Abstract and version/author metadata only | A single model generating, critiquing and revising is established. This reading supports mechanism attribution only, not a claim about experiment quality. |
| [Reflexion v4](https://arxiv.org/abs/2303.11366v4) [@shinn2023reflexion] | Abstract and version/author metadata only | Storing linguistic feedback for subsequent trials is established. Across-trial memory must not be confused with recovering an irreversibly lost value in the current episode. |
| [Self-GC v1](https://arxiv.org/html/2607.00692v1) [@selfgc2026] | Framework, rehearsal/commit, recovery/cache, metrics, limitations and Appendix Listing 5 | Pre-commit structural validation and recoverable sidecars are close precedents; rehearsal is not exhaustive semantic certification. |
| [The Compaction Cliff v1](https://arxiv.org/html/2608.22752v1) [@compactioncliff2026] | Section 3.1 and Section 3.3/Algorithms 1-3, including composition | Typed retention, constraint verification, restoration/rejection and a recovery cycle already exist. Classifier and scope assumptions matter. |
| [Sound black-box checking in the LearnLib](https://link.springer.com/article/10.1007/s11334-019-00342-6) [@meijer2019blackbox] | Abstract, Sections 1.1-1.2 and 2.2-2.3; publisher metadata | Learned models plus executable counterexamples are established; source soundness conditions cannot be dropped. No full proof audit. |
| [Basu et al. v2](https://arxiv.org/html/2204.02586v2) [@basu2022hypergraph] | Introduction, Sections II-A/II-B and Theorem 1 statement revisited | Their acceptable hyperedges and our forbidden hyperedges use different conventions; no asymptotic theorem is transferred. |
| [Bennett et al.](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v23i2p46) [@bennett2016weakstrong] | Journal abstract/metadata only | Supplies the standard weak/strong coloring distinction. Its weighted-coloring results are not used. |

The [existing audit comparison](COMPACTION_AUDIT_PRIOR_ART_2026-09-21.md) remains
relevant for typed commitments, state sufficiency and higher-order compatibility.

The candidate research question is narrower: how to obtain a sound, inexpensive
failure constraint from execution, make it survive later memory boundaries,
and separate useful feedback from extra information access. This phase's
[results](FEEDBACK_BEFORE_FORGETTING_2026-09-22.md) answer only the finite
calibration questions. A full matched-cost compactor comparison remains open.

No claim that these prior systems cannot incorporate our checks is justified.
The strong simple baseline matches the new loop in the tested fixture family;
publication novelty and practical benefit are both unestablished.

The [stricter novelty audit](FEEDBACK_NOVELTY_AUDIT_2026-09-22.md) now gives an
exact elementary strategy-alphabet/weak-coloring reformulation of the finite
repair mechanism, with independent finite checks. This is stronger evidence
against a general algorithmic novelty claim than a superficial similarity list.
It does not settle priority of every systems detail or the older coding results.
