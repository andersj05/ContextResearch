# Prior art for the compaction collision auditor

Reviewed September 21, 2026. This is a focused comparison, not a systematic
priority review. No inherited broad-corpus review labels are changed. Numerical
claims in the cited experiments were not reproduced.

| Primary source | Material read in this phase | Consequence for our claims |
|---|---|---|
| [WiCER, arXiv v1](https://arxiv.org/html/2605.07068v1), Juan M. Huerta | Abstract, Sections 7.1-7.2, Algorithm 1 | Diagnostic questions identify dropped facts and supply preservation constraints for recompilation. Counterexample-inspired summary repair is direct prior art; a new feedback-loop name would not establish novelty. |
| [TRACE, arXiv v1](https://arxiv.org/html/2608.06503v1), Guanghui Min et al. | Sections 4.1-4.2 reread | Paired closed-loop continuations restore the same environment. Its local score counts blocked/repeated actions; terminal outcomes enter later template selection. Our finite all-policy budget obstruction differs from that particular scoring procedure, but paired evaluation and verifier-guided improvement are established. |
| [Context Codec, arXiv v1](https://arxiv.org/html/2605.17304v1), Natalia Trukhina and Vadim Vashkelis | Contributions, Section 8 algorithm steps, Section 8.1 rejection criteria, Section 9 diagnostic scope | Typed, source-grounded commitments, verification and fallback are prior mechanisms. Our prototype neither extracts semantic atoms nor establishes a superior representation. |
| [Basu, Seo and Varshney, arXiv v2](https://arxiv.org/html/2204.02586v2) | Section II-B Definitions 1-4 and Examples 1-3, in addition to the earlier cascade reading | Functional compression already groups inputs into hyperedges whose outputs admit a common acceptable reconstruction. Higher-order compatibility and safe grouping are not new mathematical principles. Our arbitrary accepted-action sets and costed recovery trees are a finite implementation choice; no nonreducibility theorem is asserted. |
| [Approximate Information State, JMLR 23(12), 2022](https://jmlr.org/papers/v23/20-1165.html), Jayakumar Subramanian, Amit Sinha, Raihan Seraj and Aditya Mahajan | Journal abstract and metadata only in this phase | Information-state sufficiency and dynamic programming have an established framework. No theorem or proof from this paper is imported or certified here; a fuller relation is outstanding. |

This comparison led us to discard "diagnostic questions before forgetting" and
"typed commitments" as stand-alone novelty candidates. It also prevents us from
advertising the three-set counterexample or minimum safe partition as new theory.

The narrower candidate is an auditable interface between compaction and task
execution: retain the exact accessible channels, enumerate the resulting history
collision class, allow adaptive recovery at declared prices, and emit both a
success policy and a budget obstruction plus a pre-task repair codebook. The
current implementation handles at most 12 explicitly enumerated worlds, with
read-only deterministic tools and no further memory boundary during rescue.

That combination is a hypothesis about a useful research contribution. Search
results are not evidence of absence. Priority, natural-task prevalence,
scalability, and superiority to strong simple retention controls remain open.
See the [implementation and findings](COMPACTION_COLLISION_AUDIT_2026-09-21.md).
