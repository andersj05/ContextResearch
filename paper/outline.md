# Argument outline

This outline is a writing plan, not a list of achieved contributions.

| Section | Argument | Evidence / claim IDs | Remaining work |
|---|---|---|---|
| Abstract | Delayed relevance can make individually adequate compressed representations incompatible. | C03–C05 | Rewrite after the actual final contribution is known. |
| Introduction | Context length alone does not describe the information an agent must retain. Future obligations and available recovery matter. | C01–C02, C07–C09 | Choose one concrete motivating task and delimit claims about deployed systems. |
| Related work | Relate the problem to prompt rate–distortion, random access, successive refinement, causal coding, and agent memory. | Bibliography; related-work map | Complete functional-compression comparison and novelty audit. |
| Model | Specify X, S, J, E, U, D, budgets, public information, and no-reread rule. | C02 | Decide which dependency family to generalize. |
| Finite obstruction | Prove the child-optimal decoder characterization, joint-signature lower bound, and three-bit witness. | C03–C05 | Independent mathematical review; optionally compute exact two-bit chain distortion. |
| Structural result | Bound compatibility overhead for a restricted family. | C10: open | This is the proposed mathematical contribution, not an existing result. |
| Experimental design | Separate representation, natural-language updating, and autonomous task completion. | Protocol | Implement adapters, declare hidden-state treatment, and freeze tasks. |
| Results | Report only completed diagnostics until genuine agent measurements exist. | C06 | Pilot, held-out evaluation, uncertainty and cost analysis. |
| Discussion | Native continuity, caching, recovery, complementarity, and limits of the abstraction. | C07–C09 | Relate any observed effect back to the formal mechanism. |
| Reproducibility | Code, fixed instances, exact certificates, complete usage, and artifact provenance. | Prototype and migration manifest | Add model-run manifests only when runs exist. |

A publishable paper may become primarily theoretical or primarily empirical. The current finite example is a sound starting point; it is not by itself a certified novel contribution. If a strong ordinary structured summary removes the empirical effect, report that and revise the method claim.
