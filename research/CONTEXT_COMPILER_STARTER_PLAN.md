# Starting research on context compilers for long tasks

Advisor working plan, 2026-09-11. This is a proposed research program, not an experimental result or a verified novelty claim. The default first milestone is a working experiment that can support a later theory-and-experiments paper. Calendar estimates assume roughly 8–12 focused hours per week and should be adjusted to programming experience and compute access.

## Recommendation

Study **preserving delayed dependencies across repeated context compaction**. First establish when memory loss causes downstream failure; then test a small compiler change; only later introduce automated compiler search.

The initial question is:

> At a fixed context budget, when does a summary that supports correct immediate behavior still lose information required to complete a task much later?

A candidate intervention is a compact record of unresolved obligations, their supporting observations, and their current status, combined with retrieval when needed. The research contribution would have to be a demonstrated mechanism, a useful evaluation method, or a sharper quantitative result. Structured records alone are not a defensible novelty claim.

## What this repository provides

This is a research corpus, not an implemented experimental harness. The inspected scripts fetch, extract, catalog, generate notes, and validate sources. The implementation notes point to external projects; they do not contain checked-out agent implementations.

- [README](../README.md): overview and the corpus's September 4 snapshot.
- [Thesis options, Option C](../synthesis/08-paper-thesis-options.md): context as a lossy control channel.
- [Mathematical synthesis](../synthesis/10-mathematics-of-harness-improvement.md): task-relevant distortion, sufficiency, belief states, and statistical selection.
- [Experimental blueprint](../synthesis/11-self-improving-experimental-blueprint.md): controls, data separation, outcome definitions, and reproducibility.
- [mini-SWE-agent note](../source-notes/harness-mini-swe-agent.md): a possible later coding-agent integration.

The existing blueprint combines several substantial projects: compression, compiler search, valid promotion, and transfer. Treat it as a destination. Its finite-class promotion argument is explicitly a specialization of standard uniform convergence; reproducing that argument alone is not a new mathematical contribution.

Use the notes as navigation aids and check central claims in original papers. The repository's integrity validation checks files, metadata, links, and related structure; it does not certify novelty or replicate reported experiments. For example, the local Nagle note labels the paper a preprint, whereas its [arXiv record](https://arxiv.org/abs/2407.15504) says accepted to NeurIPS 2024. Metadata deserves a separate audit before submission.

## Define the object before building it

At step t, the agent has received observations and taken actions. The compiler decides what representation of that history the next model call sees. It can select, order, summarize, retrieve, and update memory.

An implementable interface is:

```text
update(memory, new_events) -> new_memory
compile(goal, new_memory, accessible_archive, budget) -> model_context
```

The agent then takes an action, the environment changes, and the loop repeats. Freeze the executor model, tools, decoding settings, and evaluator while changing the compiler. Fix the summarizer model too when comparing summary strategies.

Distinguish three resources: model-visible context, persistent memory, and archived raw events. A compiler that scans the complete archive for free is solving a different problem from one that only sees its previous summary. Give treatments the same archive permissions, meter access, and report memory size, retrieval work, all model calls, and total tokens. Include constant instructions and tool descriptions in the declared input-token accounting.

Start with memory **within a single task**. Learning reusable lessons across tasks is a later experiment with separate contamination and evaluation issues.

## Prior work to read and reproduce

Read in this order. For each paper write one page: question, mechanism, strongest comparison, information access, costs, failure cases, and the smallest result you could reproduce.

| Reading | What to learn | Reading task |
|---|---|---|
| [HiAgent](https://arxiv.org/abs/2408.09559), with [local note](../paper-notes/hu-2025-hiagent.md) | Hierarchical working memory organized around subgoals | Trace one action–observation–summary cycle and identify what can be lost. |
| [Fundamental Limits of Prompt Compression](https://arxiv.org/abs/2407.15504), with [local note](../paper-notes/nagle-2024-prompt-compression-rate-distortion.md) | A finite optimization formulation for compression under a fixed model | Work a tiny example by enumerating allowed messages and losses. |
| [TRACE](https://arxiv.org/html/2608.06503v1) | Paired continuations from a restored environment state to evaluate compaction | Identify what its local execution score observes and what terminal outcomes add. |
| [The Compaction Cliff](https://arxiv.org/abs/2608.22752) | Repeated compaction and retention policies that depend on information type | Determine how a proposed obligation record differs from existing type-based retention. |
| [Governance Decay / ConstraintRot](https://arxiv.org/abs/2606.22528) | Constraint loss and explicit constraint pinning | Treat simple pinning as a baseline, not a new contribution. |

[LongMemEval](https://arxiv.org/abs/2410.10813) is useful for memory diagnostics, but answering questions about long histories does not by itself establish successful interactive task completion. [ACE](https://arxiv.org/abs/2510.04618) belongs in the later reading stage on updating persistent contexts.

The targeted September 11 check found no catalog or paper-note matches for TRACE, ConstraintRot, The Compaction Cliff, or [AMA-Bench](https://arxiv.org/abs/2602.22769). These are additions to investigate, not evidence that the rest of the literature is now complete. TRACE's introduction and method were inspected; the other newly found sources were checked at abstract/metadata level here. Audit their complete methods and code before claiming a gap. TRACE's reference list also points to ACON, ReSum, and SUPO as relevant next searches.

## First experiment: a small, inspectable environment

Build a generated workflow simulator, initially without an LLM. A task contains prerequisites, changing facts, and obligations that become actionable later. Actions actually alter state; completion is graded by deterministic rules.

Example: early in a workflow the agent learns which of two artifacts must be retained until a final check. Several independent subtasks intervene. A later observation can supersede an earlier instruction. The agent must finish the workflow, retain the currently required artifact, and avoid replaying completed operations. Randomize names, order, and which obligations matter.

The simulator knows the true state for grading. Practical compilers receive only the observations actually exposed to the agent. A separately labeled oracle can receive sufficient state for diagnosis. Do not pass hidden dependency labels to the proposed compiler.

Vary these factors separately:

- Dependency delay: how many actions separate observing a fact from needing it.
- Number of simultaneously unresolved dependencies.
- Number of compactions and the context-token budget.
- Distractor volume and fact revisions.
- Recoverability: whether a forgotten fact can be retrieved, at what cost.

A long transcript is not automatically a difficult long task. Padding changes token pressure; adding necessary decisions changes the action horizon. A task that carries one bit for 1,000 steps differs from a task that must remember 100 independent unfinished obligations.

Use a scripted competent controller and exact state representation first to check that the generator is solvable. Then use one fixed LLM. A full-history LLM run is an empirical reference, not an optimal-policy oracle.

## Comparisons and proposed compiler

Start with recent-history truncation, a rolling prose summary, and a structured state summary at identical visible-context limits. Then add a type-aware or constraint-pinning baseline and the candidate obligation-aware compiler. Keep a full-history reference where it fits and an oracle-state diagnostic. Reproduce the actual published baseline when making a comparison claim; label simplified versions as adaptations.

The candidate state can contain:

```text
goal
current verified progress
unresolved obligations: id, condition, required action, source event
fact revisions: value, source event, superseded record
recent failures and completion evidence
archive pointers
```

Update individual entries when observations change them. Remove an obligation only on observed completion, cancellation, or supersession. Preserve source references to permit checking and retrieval. At budget overflow, specify an explicit allocation/eviction rule; the record cannot grow without limit.

All these components are hypotheses. Remove them one at a time to test their contribution. The key comparisons are against a careful structured summary and explicit pinning, not only a weak truncation baseline. First hold retrieval disabled across methods, then enable equal archive access to separate retention from recovery.

## Measurement that makes the experiment credible

Use two complementary evaluations:

1. At a saved compaction boundary, restore the exact same environment and history, swap only the compiled context, and run paired continuations. This estimates a local intervention effect on those sampled states.
2. Run each compiler from task start, allowing it to generate its own history. This measures the total policy effect, including future compactions and retrieval.

Do not treat a checkpoint effect as an end-to-end result. Compare short continuation scores with eventual task success, and quantify the cases that look fine locally but fail later. This is a candidate direction suggested by the prior work, not an established omission in every existing method.

Primary outcome: terminal task success at a prespecified context budget. Secondary outcomes: lost obligations, stale facts used, redundant actions, retrieval recovery, number of compactions, tokens, calls, and latency. Use verifier-readable event logs to attribute failures; readable summaries and text similarity are insufficient evidence.

Pair methods on task instances and, where supported, environment randomness. API seeds do not guarantee identical model randomness. Aggregate repeated runs within tasks and calculate paired uncertainty at the independent task/template level, rather than counting every checkpoint as independent.

Begin with 20–30 development tasks for debugging. This is a pilot, not a powered evaluation. Use its variability and a declared meaningful effect size to plan the larger run. Freeze the primary comparison before evaluating held-out task templates. Longer-delay and larger-active-state settings provide explicit shift tests. Keep failures and null results.

Cap the first LLM batch and estimate total cost from measured token usage before expanding it. No paid runs are part of this advisory pass.

## Mathematical entry point

Your mathematical advantage is in making assumptions precise and identifying which variables govern difficulty. Start with sufficiency and finite sequential decision problems; learn the implementation concepts alongside them. You do not need to master all transformer training or reinforcement learning first.

First exercise: a uniformly random bit X is observed early and is needed only at the final action. Suppose the post-compaction memory is independent of X and no later observation or retrieval reveals it. Any final guess based on that memory succeeds with probability at most 1/2. Keeping X exactly permits perfect performance by a competent decoder.

Now place that final action beyond the next h steps. A verifier that sees only rewards, errors, and actions in those h steps can fail to distinguish useful and useless memories if their observable prefixes coincide. Construct the example explicitly. This is a basic indistinguishability argument, not a publication claim.

Extend the exercise to n independent pending bits, with a query index revealed only later. Without external access or side information, exact recovery for every possible index requires a memory with at least 2^n distinguishable states, hence at least n bits. Conversely, arbitrarily long elapsed time can require only one bit if only one unresolved dependency remains. This motivates studying active information demand separately from horizon length.

Possible research target: characterize how budget, active dependency count, delayed relevance, update noise, and recovery cost jointly determine decision error. First solve a finite version exactly; then test whether it predicts the observed LLM behavior. Approximate recovery or nonuniform dependency distributions make the question richer, but their basic information-theoretic bounds already have extensive prior art.

Keep three distinctions explicit: token count is not Shannon information; a sufficient representation need not be decoded correctly by a particular LLM; repeated compression alone does not imply a universal geometric decay rate. Fresh observations, retrieval, and exact retained state change any loss-accumulation argument.

## Six stages, approximately six to eight weeks

| Stage | Deliverable | Decision criterion |
|---|---|---|
| 1. Learn and specify | Three paper worksheets, compiler interface, ten hand-written tasks | Explain where information enters, persists, and disappears. |
| 2. Build the microscope | Seeded simulator, exact grader, scripted oracle, full event logs | Tasks are solvable and intentional forgetting produces the expected failure. |
| 3. Establish baselines | Small LLM pilot, truncation and summaries, manually inspected failures | Failures are attributable to memory rather than broken tools or unsolvable tasks. |
| 4. Test one mechanism | Obligation records, structured/pinning controls, component ablations | Any advantage survives the strongest simple baseline and honest cost accounting. |
| 5. Formalize and test | Finite mathematical result, frozen held-out experiment | The result explains more than the deliberately constructed toy example. |
| 6. Evaluate scope | One realistic tool task family, second model if affordable, concise report | State where effects transfer, vanish, or reverse. |

If the oracle-state LLM also fails, fix task difficulty or investigate the decoder before optimizing memory. If pinning solves the whole problem, do not add complexity to force a result. If benefits disappear on held-out templates, report that limitation and revisit the mechanism. Only add automated compiler search once a stable measurement setup and a useful manual compiler exist.

## How to use an advisor each week

Bring a one-page memo containing the current hypothesis, the exact change, the comparison, one plot or table, two informative traces, and the next falsifying experiment. Separate observation from explanation. Ask for criticism of the strongest alternative explanation, not reassurance about a promising score.

The first assignment is small: read HiAgent and TRACE, draw the data flow of one compaction event, and design ten delayed-dependency tasks with unambiguous correct endings. The next collaboration can turn those into a simulator and a written pilot protocol. Choose a paper claim only after observing a stable, explainable result.
