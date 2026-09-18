# Focused research plan: self-building and self-improving harnesses

## Decision and audience

This expansion supports a mathematics research paper about harnesses that construct,
evaluate, and revise their own context policies, prompts, tools, memory, workflows,
controllers, or code. The intended reader is mathematically mature and wants mechanisms,
formal questions, and reproducible experiments rather than product rankings.

## Primary question

Under what assumptions can an LLM-driven outer loop improve an agent harness, and how
can we distinguish genuine transferable improvement from extra compute, evaluator gaming,
benchmark reuse, unsafe self-modification, or a change in the task distribution?

## Link to Option C

Context compilation remains a central design object. The expanded thesis treats a context
compiler

\[
C_{\phi,t}:s_t\mapsto c_t,\qquad |c_t|\le W,
\]

as one component of a broader harness parameterization \(H_\phi\). A meta-harness proposes
\(\phi'\), evaluates it on an inner sample, and accepts or rejects the update under an
outer protocol. The paper can therefore combine task-relevant rate-distortion with
the statistics and safety of recursive harness optimization.

## Included mechanisms

- automatic agent/scaffold/workflow design;
- prompt, tool, context, memory, planning, routing, verifier, and code co-optimization;
- experience-driven and online harness evolution;
- agent-generated tools or skills and self-modifying source;
- meta-harness search, evolutionary search, program synthesis, reinforcement learning,
  and optimizer agents;
- evaluation leakage, nested selection, adaptive overfitting, transfer, rollback,
  monotonicity, and capability/safety regressions;
- formal models of task-relevant context compression and update acceptance.

## Exclusions

- model-weight self-training with no harness-level intervention;
- ordinary one-answer self-refinement that does not change a reusable harness component;
- product announcements without a method, code artifact, or falsifiable claim;
- unversioned benchmark tables without a reproducible optimizer/evaluator protocol;
- unsafe execution of research code or generated self-modifications in this repository.

## Evidence priority

1. Primary papers and official artifacts with reusable optimizer/evaluator details.
2. Official repositories, releases, configs, traces, and evaluation code.
3. Primary theory from adaptive data analysis, program synthesis, information theory,
   optimization, and formal methods when assumptions transfer explicitly.
4. Practitioner reports only when they expose a concrete mechanism, failure, or dataset.

## Work plan

1. **Completed — discovery:** inventoried the existing corpus and searched missing
   academic, implementation, theoretical, and counterevidence families to mechanism
   saturation.
2. **Completed — follow-up:** acquired lawful primary PDFs and pinned implementation
   artifacts covering transfer, nested overfitting, rollback, and context-policy search.
3. **Completed — extraction:** created one structured note per added source and extended catalogs,
   checksums, QA, and the claim ledger.
4. **Completed — synthesis:** wrote a dedicated self-improving-harness survey, mathematical
   framework, experimental blueprint, and revised thesis recommendation.
5. **Completed — verification:** validated files, citations, IDs, links, math/proof labels, PDF
   parsing/rendering, and a clean Git history.

## Success criteria

- Existing explicit 2026 harness papers are reconciled with earlier automated-agent-design
  work rather than treated as the origin of every mechanism.
- At least one strong source and one limitation/counterexample support every consequential
  claim about improvement, transfer, evaluation, and safety.
- The report separates optimizer, candidate representation, evaluator, data split,
  acceptance rule, budget, and deployment distribution.
- Mathematical statements label source-reported theorems, standard transferred results,
  new derivations, and conjectures distinctly.
- The final design includes locked or reusable outer evaluation, compute-matched baselines,
  rollback, and regression testing.

## Stopping rule

Stop when new searches predominantly return duplicate implementations of represented
search spaces and optimizers, every high-impact claim has primary support or an explicit
gap, and additional sources are unlikely to change the taxonomy or confidence. This is
mechanism saturation, not literal completeness.
