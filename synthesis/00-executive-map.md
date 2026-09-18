# LLM harness engineering research map

## Corpus at a glance

| Layer | Count | What is preserved |
|---|---:|---|
| academic papers and preprints | **171 PDFs** | 5,390 pages, checksums, metadata, extracted text QA, and one structured note per paper |
| verified academic publications | **100** | venue/status as recorded in the acquisition manifest |
| academic preprints | **71** | explicitly labelled so recent claims are not mistaken for peer review |
| practitioner and benchmark reports | **16 notes** | canonical URL, date, evidence/advocacy split, quantitative claims, biases, and verification record |
| harness implementations | **32 notes** | official sources, license, pinned release/commit, mechanism, limitations, and reproducibility variables |
| unified source records | **219** | stable IDs in [`catalog/sources.csv`](../catalog/sources.csv) |

The search snapshot is 2026-09-04. This is a broad, best-effort corpus rather than a claim that every web page or paper using adjacent terminology has been captured.

## The short answer

An LLM harness is the control and execution system around a model. It determines what the model sees, what actions it may propose, how those actions execute, what persists, how feedback returns, when work stops, and how success is judged.

The strongest conclusion from the corpus is:

> Measured agent capability is a property of a configured model–harness–environment–verifier–budget system, not a model name or harness brand in isolation.

The evidence does **not** show one universally best architecture. It shows that action interfaces, context policy, feedback source, retry/selection policy, execution environment, infrastructure, and grader validity can all move outcomes. Many popular claims become much weaker after matching compute, auditing the verifier, or testing a simple baseline.

## Twelve findings worth carrying into a paper

1. **The harness is a scientific treatment.** Prompt, tools, context compiler, memory, controller, executor, verifier, stopping rule, and budget must be versioned with the model.
2. **Interfaces often matter more than brand taxonomies.** SWE-agent and Agentless-style evidence shows large gains can come from action representation, repository navigation, environment feedback, and workflow structure.
3. **Intrinsic self-correction is unreliable.** Revision is more credible when it receives new information from execution, retrieval, tests, or a separately calibrated verifier.
4. **Search is constrained by selection.** Generating more candidates only helps when coverage grows and a sufficiently precise selector can identify useful candidates at acceptable cost.
5. **Repeated attempts are correlated.** The familiar (1-(1-p)^k) curve is conditional on independence; shared task difficulty and shared failure modes reduce effective diversity.
6. **Reliability and opportunity are different.** pass@(k) asks whether any attempt succeeds; pass(^{k}) asks whether all (k) succeed. A production system may need both.
7. **Multi-agent gains are not automatically collaboration gains.** Tokens, model mix, tool calls, parallelism, and merging commonly change together. Independent sampling at matched compute is a required baseline.
8. **Benchmarks are fallible software.** Tests may reject valid alternatives or accept incomplete patches. The Verified and Pro audit sequences show that expert screening is not permanent ground truth.
9. **Infrastructure is part of the treatment.** CPU, memory, time, networking, container image, and enforcement semantics can produce score changes comparable with leaderboard margins.
10. **Practitioner convergence identifies variables, not universal laws.** Durable state, bounded work, small stable interfaces, explicit context policy, trusted control planes, and outcome verification recur across organizations, but controlled public comparisons remain sparse.
11. **Searching for a harness is not evidence that it improved.** Best-so-far curves,
    adaptive validation, and extra candidate compute can all rise without a sealed-test
    gain; the proposal process and promotion process are separate research objects.
12. **Self-improvement guarantees are conditional.** A fixed-capacity candidate class
    and immutable independent gate can support a bounded promotion theorem. Open-ended
    code editing, shifting objectives, or repeated public-test reuse do not inherit it.

## Where to read next

| Question | Primary document |
|---|---|
| What exactly counts as a harness? | [`01-definitions-and-taxonomy.md`](01-definitions-and-taxonomy.md) |
| How do loops, tools, planning, memory, verification, security, and recovery fit together? | [`02-architecture-and-design-patterns.md`](02-architecture-and-design-patterns.md) |
| Which empirical claims are strong, weak, or benchmark-confounded? | [`03-empirical-evidence-and-benchmark-validity.md`](03-empirical-evidence-and-benchmark-validity.md) |
| What equations, estimators, proofs, and proposed models are available? | [`04-mathematical-foundations.md`](04-mathematical-foundations.md) |
| How do 32 current runtime and self-optimization implementations actually work? | [`05-open-source-harnesses.md`](05-open-source-harnesses.md) |
| What should be learned—and not inferred—from engineering reports? | [`06-practitioner-evidence.md`](06-practitioner-evidence.md) |
| What research questions and experiments follow? | [`07-research-agenda.md`](07-research-agenda.md) |
| Which thesis is most feasible for a mathematics paper? | [`08-paper-thesis-options.md`](08-paper-thesis-options.md) |
| What does current self-building and self-improving evidence actually establish? | [`09-self-building-and-self-improving-harnesses.md`](09-self-building-and-self-improving-harnesses.md) |
| Which theorems transfer, and under exactly what assumptions? | [`10-mathematics-of-harness-improvement.md`](10-mathematics-of-harness-improvement.md) |
| What experiment could become the paper? | [`11-self-improving-experimental-blueprint.md`](11-self-improving-experimental-blueprint.md) |
| What is the single cohesive deep-research report? | [`report-source.md`](report-source.md) |

For individual evidence, use the [academic paper-note index](../paper-notes/INDEX.md), [engineering-source index](../source-notes/INDEX.md), and [claim-to-source ledger](../catalog/claim-source-ledger.md).

## Evidence strength map

### Relatively strong

- controlled or multi-condition interface studies;
- negative results on unaided self-correction;
- test-time-scaling analyses that expose verifier and budget assumptions;
- repeated benchmark audits showing grader misalignment;
- long-context position and distraction effects;
- versioned source-code evidence for architecture and licensing.

### Useful but conditional

- retrieval, reflection, planning, memory, and tree-search gains on their studied tasks;
- multi-agent debate, role, and voting improvements;
- new harness factorial benchmarks and automatic harness-optimization results;
- time-horizon trend estimates;
- practitioner before/after metrics.

### Hypothesis-generating

- single-organization architecture essays without public data;
- project-authored benchmark wins without matched budgets;
- six-run or one-task microbenchmarks;
- throughput metrics such as lines of code or pull requests without quality-adjusted controls;
- very recent 2026 preprints not independently replicated.

## The recommended mathematics thesis

The recommended direction is a **bounded self-improving context compiler with valid
promotion**.

Let \(S\) be decision-relevant task state and let a compiler \(C_\phi\) produce the
model-visible context under a token budget \(B\):

\[
C_\phi\sim Q_\phi(\cdot\mid S),
\qquad |C_\phi|\le B.
\]

Define distortion by the decision regret induced when a frozen model acts from
\(C_\phi\) rather than full state. The information-theoretic question is then the
achievable task-relevant rate--distortion frontier. The self-improvement question is
whether an adaptive outer loop can modify \(\phi\) without fitting the evaluator.

For a fixed ex-ante family \(\Phi_0\) of \(M\) compilers, bounded loss, and an independent
i.i.d. gate of size \(n\), uniform convergence gives

\[
\sup_{\phi\in\Phi_0}
|\widehat R(\phi)-R(\phi)|
\le
\sqrt{\frac{\log(2M/\delta)}{2n}}
=\epsilon
\]

with probability at least \(1-\delta\). Under that simultaneous event, accepting
\(\phi'\) only when

\[
\widehat R(\phi')
\le
\widehat R(\phi)-(2\epsilon+\tau)
\]

implies \(R(\phi')\le R(\phi)-\tau\). The useful research problem is to weaken or
operationalize those assumptions, estimate the adaptive optimism when they fail, and test
the rule against naive best-validation selection.

The thesis combines:

- Shannon rate--distortion and information-bottleneck formulations of context;
- task-relative sufficiency and belief-state representations;
- the optimizer's curse and mutual-information bounds on adaptive bias;
- reusable-holdout, Ladder, and confidence-sequence promotion mechanisms;
- typed compiler grammars and proof-relative program synthesis;
- sealed-test experiments with grounded versus intrinsic feedback;
- model--harness interaction, regression, forgetting, and full search-cost accounting.

The prior correlated-retries and imperfect-verifier direction remains a strong Option A
and supplies useful evaluation machinery. It is no longer the primary recommendation
because the self-improving context-compiler problem is closer to designing harnesses
themselves.

## A defensible empirical design

1. Use a finite controlled task generator with known optimal action values and
   decision-regret distortion.
2. Restrict edits to a typed context-compiler grammar covering selection, ordering,
   compression, retrieval, and persistent memory.
3. Separate freely reusable search data, a metered gate, one sealed test, and a later
   shifted cohort.
4. Compare unchanged, careful manual, random-mutation, and LLM-guided compilers under
   identical tokens and target-evaluation counts.
5. Cross at least two executor models with grounded, scalar-only, and intrinsic feedback.
6. Run multiple complete outer-loop seeds; candidate evaluations within one search are
   not independent replications.
7. Predeclare the reachable class, promotion margin, protected slices, query budget, and
   cost objective.
8. Preserve every candidate, parent, diff, trace, score, rejection, cost, and rollback.
9. Report the rate--distortion frontier, sealed-test gain, adaptive optimism, regressions,
   interaction effects, forgetting, and amortized search cost.
10. Keep hidden data, evaluator code, authority, credentials, and release signing outside
    the editable region.

The complete protocol is
[`11-self-improving-experimental-blueprint.md`](11-self-improving-experimental-blueprint.md).

This design is valuable whether or not it finds a new “best” harness. A null result, calibrated dependence estimate, or ranking reversal would all be publishable scientific information if the sampling and artifacts are sound.

## What “meme risk” means in this corpus

A claim receives extra skepticism when it has several of these properties:

- a memorable agent/framework name substitutes for a specified intervention;
- several components and the token budget change at once;
- the comparison lacks a minimal or independent-sampling baseline;
- evaluation uses one narrow public benchmark;
- the same organization builds and scores the system;
- a model judge is not calibrated against experts;
- only aggregate success is published, without traces or failures;
- the result is a new preprint with no replication;
- benchmark exposure, grader flaws, or infrastructure are unmeasured;
- the reported outcome is throughput rather than correctness or value.

This is not a reason to discard the source. It determines how the source may be used: architecture evidence, effect estimate, contradiction, or hypothesis.

## Known boundaries of this snapshot

- The web and 2026 preprint landscape changes rapidly; pinned dates and commits matter.
- Seventy-one academic items are preprints, including much of the explicitly named
  “harness engineering” and self-improvement literature.
- Practitioner pages were not converted into PDFs when redistribution or rendering rights were unclear; canonical URLs and structured notes are preserved.
- The corpus emphasizes language agents, coding agents, tool use, evaluation, memory, search, multi-agent control, and safety. Adjacent workflow, distributed-systems, HCI, and formal-methods literatures are sampled only where they directly illuminate harnesses.
- The repository provides a research foundation and candidate formal results, not a finished mathematics paper or a completed new experiment.

## Reproducibility anchors

- [`catalog/sources.csv`](../catalog/sources.csv) — unified 219-source inventory.
- [`catalog/pdf-inventory.csv`](../catalog/pdf-inventory.csv) — archived PDF paths, sizes, pages, checksums, and access dates.
- [`catalog/paper-distillations.csv`](../catalog/paper-distillations.csv) — structured paper-level findings used to build notes.
- [`catalog/claim-source-ledger.md`](../catalog/claim-source-ledger.md) — bounded claims, sources, confidence, and caveats.
- [`research/SEARCH_LOG.md`](../research/SEARCH_LOG.md) — search and acquisition record.
- [`research/GAP_MATRIX.md`](../research/GAP_MATRIX.md) — coverage and remaining gaps.
- [`scripts/`](../scripts) — acquisition, extraction, note-generation, catalog, and validation code.

The preferred citation path is: claim ledger → structured note → archived PDF or canonical official source.
