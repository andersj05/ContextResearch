---
title: "Empirical Evidence and Benchmark Validity in LLM Harness Engineering"
document_type: "cross-source synthesis"
last_evidence_check: "2026-09-04"
scope: "academic studies, primary benchmark audits, and practitioner engineering reports"
---

# Empirical Evidence and Benchmark Validity in LLM Harness Engineering

## Abstract

An LLM agent score is not a property of a language model alone. It is an end-to-end
measurement of a model embedded in a harness, supplied with a particular prompt and
tool protocol, operating under a budget and runtime configuration, and judged by an
imperfect evaluator. Controlled interface ablations, cost-controlled baselines, large
factorial evaluations, and production reports all support this systems interpretation.
At the same time, audits of SWE-bench and other agentic benchmarks show that test
coverage, underspecification, shortcuts, training exposure, infrastructure, and
selection of repeated samples can change scores without a corresponding change in the
target capability.

The defensible empirical conclusion is therefore narrower than the usual leaderboard
claim:

> A reported agent result estimates the performance of a specified
> model-harness-environment-verifier configuration on a specified task distribution
> under a specified resource and sampling policy.

This document synthesizes the strongest evidence for that conclusion, distinguishes
paper-reported results from our interpretation, and records counterevidence and
meme-risk. The accompanying mathematical treatment is in
[04-mathematical-foundations.md](04-mathematical-foundations.md).

## 1. Reading conventions

### 1.1 Citation convention

Bracketed citations use the repository source ID. Academic citations also give the
PDF page, section, table, or figure when verified locally. For example,
[yang-2024-swe-agent, PDF p. 6, Table 1] refers to the archived PDF with that source
ID. "PDF p." means the one-based page of the archived file, which can differ from a
publisher's printed page number.

For web-only sources, the citation names the visible section heading. The source index
at the end maps every source ID to a local PDF or canonical URL.

### 1.2 Evidence labels

- **Paper-reported:** a result or conclusion stated by the source.
- **Audit-reported:** a result from a primary benchmark audit that is not peer reviewed.
- **Practitioner-reported:** a production observation or engineering recommendation.
- **Derived here:** our mathematical or cross-source inference, not a claim made by a
  source.
- **Meme-risk:** a true or partly true result that becomes misleading when its
  denominator, budget, benchmark, scaffold, uncertainty, or conditional language is
  removed.

Publication status affects confidence but is not a substitute for method inspection.
A transparent preprint can provide stronger evidence for a bounded claim than a
peer-reviewed paper whose result cannot be reproduced.

## 2. The object being measured

Let a deployed or evaluated configuration be

\[
\mathcal C=(M,H,P,T,E,B,V,S),
\]

where \(M\) is the base model, \(H\) the harness implementation, \(P\) the prompt and
context policy, \(T\) the tool surface and schemas, \(E\) the execution environment,
\(B\) the token/time/dollar/resource budget, \(V\) the verifier, and \(S\) the sampling
and stopping policy. A benchmark score is more accurately written

\[
\widehat R(\mathcal C;\mathcal D),
\]

for a task sample \(\mathcal D\), rather than \(\widehat R(M)\).

This notation is **derived here**, but it formalizes what the empirical studies
actually manipulate:

- SWE-agent changes editing, search, file-view, and history interfaces while holding
  the main model family and task set approximately fixed
  [yang-2024-swe-agent, PDF p. 6, Table 3].
- AI Agents That Matter changes retry, temperature, escalation, and agent architecture
  and measures both accuracy and cost [kapoor-2024-agents-matter, PDF pp. 3-4,
  Figure 1].
- Harness-Bench crosses six configurable harnesses with eight API model backends on
  the same 106 tasks, budgets, timeouts, and evaluators
  [yao-2026-harness-bench, PDF p. 6, Tables 1-2].
- HAL evaluates models, scaffolds, and benchmarks as separate axes and logs cost and
  traces [kapoor-2026-hal, PDF pp. 2-4, Tables 1-2].
- Infrastructure experiments change only runtime resources and still move pass rates
  [anthropic-2026-infrastructure-noise, sections "How we got here" and "How this
  affects measurement"].

The phrase "the model scored \(x\)" is acceptable shorthand only after \(\mathcal C\)
has been disclosed.

## 3. Direct evidence that harness choices change outcomes

### 3.1 Agent-computer interface ablations

SWE-agent supplies the cleanest early evidence that apparently minor interface choices
change repository-level coding performance. With GPT-4 Turbo on SWE-bench Lite, the
paper reports 11.00% resolved for a shell-only agent and 18.00% for SWE-agent. The
corresponding average costs were $1.46 and $1.67. On full SWE-bench, SWE-agent reports
12.47% at average cost $1.59; the RAG baseline reports 1.31% at $0.13
[yang-2024-swe-agent, PDF p. 6, Table 1].

The interface ablations are especially informative:

| Harness condition | Reported Lite resolution | Bounded interpretation |
|---|---:|---|
| summarized search | 18.0% | reference configuration |
| iterative result-by-result search | 12.0% | more interaction was worse under the budget |
| no dedicated search | 15.7% | a weak search interface can be worse than none |
| 30-line file view | 14.3% | too little local context hurt |
| 100-line file view | 18.0% | best of the tested windows |
| full-file view | 12.7% | indiscriminate context also hurt |
| last five observations | 18.0% | reference context policy |
| full history | 15.0% | retaining everything did not improve this setup |
| editor without linting | 15.0% | structured feedback added 3 points |

All values are **paper-reported** from one model, benchmark split, and development
process [yang-2024-swe-agent, PDF p. 6, Table 3]. They show configuration sensitivity;
they do not prove that 100 lines, five observations, summarized search, or linting are
universally optimal.

The trajectory analysis also rejects an i.i.d. view of repeated actions. Of 2,294 full
benchmark trajectories, 1,185 (51.7%) contained at least one failed edit. Before any
failed edit, an edit attempt had a reported 90.5% chance of eventually being
successful; after one failed edit, the reported recovery probability was 57.2%
[yang-2024-swe-agent, PDF pp. 31-32, Figures 19-20]. Successful runs had median
cost $1.21 and 12 steps, whereas unsuccessful runs averaged $2.52 and 21 steps
[yang-2024-swe-agent, PDF p. 8, Section 5]. The useful bounded finding is that failure
history changes the next-step distribution and that unsuccessful agents can consume
more budget without converging.

### 3.2 Simple baselines versus named agent architectures

AI Agents That Matter re-ran LDB, LATS, Reflexion, and simple baselines five times on
164 modified HumanEval tasks. Its warming baseline, which retries while increasing
temperature, had no statistically significant accuracy difference from the best
tested agent architecture. At similar accuracy, costs differed by almost two orders
of magnitude; Reflexion and LDB cost over 50% more than warming, and LATS cost over
50 times more [kapoor-2024-agents-matter, PDF pp. 3-4, Figure 1].

This is **paper-reported evidence against an attribution**, not evidence that planning,
reflection, or debugging never helps. The authors explicitly leave open whether these
mechanisms help on harder tasks such as SWE-bench
[kapoor-2024-agents-matter, PDF p. 4, Section 2.3]. The corrected conclusion is:
simple retry, warming, and escalation baselines are required before assigning gains to
a complex harness mechanism.

Agentless supplies a related repository-level result. Its fixed
localization-repair-validation pipeline reports 96/300, or 32.00%, on SWE-bench Lite
at average cost $0.70 [xia-2024-agentless, PDF pp. 1 and 10-11]. The current archived
version removes exact-patch, misleading, and insufficiently specified cases to form a
249-task Lite-S subset; Agentless resolves 84/249, or 33.73%
[xia-2024-agentless, PDF pp. 16-17, Table 5]. This shows that a constrained workflow
can be a strong baseline. It does not make the workflow "harness free": localization,
candidate generation, test generation, filtering, and validation are themselves
harness decisions.

### 3.3 Factorial and multi-benchmark evidence

Harness-Bench reports a full \(6\times 8\) configurable-harness by model-backend
matrix over 106 tasks, yielding 5,088 trajectories, plus 106 separate Codex
trajectories. External task state, budget, timeout, and evaluator are fixed; native
prompting, action format, tools, state policy, and recovery remain part of each harness
[yao-2026-harness-bench, PDF p. 6, Table 1 and Section 4.1]. Aggregated harness scores
range from 52.4% to 76.2%; token use ranges from 68.7K to 175.1K, and turns from 5.0
to 22.6 [yao-2026-harness-bench, PDF p. 6, Table 2]. Category-level cross-harness
variance is largest in data/analytics, workspace/tool use, and software engineering,
and lowest in office communication [yao-2026-harness-bench, PDF p. 13, Figure 4].

These are **paper-reported descriptive configuration effects**, not causal effects of
individual mechanisms. The authors expressly warn that native harness components move
together and that some process scores use an LLM judge
[yao-2026-harness-bench, PDF p. 9, Section 6]. Because the paper was a new preprint as
of the evidence date, independent reproduction remains a major gap.

HAL reports 21,730 rollouts across nine models and nine benchmarks at about $40,000
total cost and releases 2.5 billion tokens of model-call logs. It reports that higher
reasoning effort reduced accuracy in a majority of its comparisons and that trace
inspection exposed benchmark lookup, unsafe credit-card use, and a leaked few-shot
scaffold that the authors excluded [kapoor-2026-hal, PDF pp. 1-3, Abstract and
Section 1]. HAL is broader than Harness-Bench but not a complete balanced factorial
over every model, benchmark, scaffold, and budget. The result supports trace-aware,
multidimensional evaluation; it does not establish that greater reasoning effort
usually hurts outside the tested cells.

## 4. Benchmark validity: what does "success" mean?

### 4.1 Task validity and outcome validity

The Agentic Benchmark Checklist paper separates two equivalences:

1. **Task validity:** possessing the target capability should be equivalent to being
   able to complete the task.
2. **Outcome validity:** actual task success should be equivalent to a positive grader
   result.

[zhu-2025-rigorous-agentic-benchmarks, PDF pp. 2-4, Figure 1]

A shortcut violates task validity because an incapable system can pass. An impossible,
broken, or underspecified task also violates task validity because a capable system can
fail. Weak tests, brittle string matching, or an uncalibrated judge violate outcome
validity.

Applying the checklist to ten benchmarks, the authors report seven with task-validity
failures, seven with outcome-validity failures, and all ten with reporting limitations
[zhu-2025-rigorous-agentic-benchmarks, PDF p. 8, Figure 5]. Reported examples include
an empty-response agent scoring 38% on impossible tau-bench airline tasks, a no-solution
shortcut scoring 100% on SWE-Lancer, approximately 31 percentage points of
KernelBench overestimation, and 1.4-5.2 points of WebArena overestimation
[zhu-2025-rigorous-agentic-benchmarks, PDF pp. 2 and 8, Section 5.2].

These results establish that an execution-based or state-based grader is not
automatically a valid grader. They do not imply that every affected score is useless;
they require interpretation conditional on the measured failure modes.

### 4.2 The SWE-bench evidence sequence

SWE-bench originally assembled 2,294 GitHub issue tasks from 12 Python repositories.
The initial best reported system, Claude 2 with retrieval, resolved 1.96%
[jimenez-2024-swe-bench, PDF pp. 1-2, Abstract]. This benchmark was a major advance
over isolated function synthesis because it replayed repositories and tested patches.
Later evidence nevertheless shows that historical realism and automated tests do not
guarantee construct validity.

#### Weak tests and solution leakage

SWE-Bench+ manually reviewed 251 SWE-agent plus GPT-4 patches that passed the benchmark
tests. Three authors independently classified patches and resolved disagreements
collectively. The paper reports 82/251 (32.67%) cases in which the issue or comments
provided the solution and 78/251 (31.08%) weak-test cases comprising incorrect,
wrong-location, or incomplete fixes [aleithan-2024-swe-bench-plus, PDF pp. 2 and 4,
Table 1]. It also reports 94% of benchmark issues as predating the model cutoffs used
in the study [aleithan-2024-swe-bench-plus, PDF p. 2].

There is a material internal rate discrepancy. The introduction says filtering
suspicious fixes reduces 12.47% to 3.97%
[aleithan-2024-swe-bench-plus, PDF p. 3, Figure 1b], while Section 2.2 says retaining
the two "correct fix" classes yields 5.49%
[aleithan-2024-swe-bench-plus, PDF p. 7, Section 2.2]. A synthesis must not quote one
number without its definition and version. Further, "94% pre-cutoff" is only an
exposure-risk indicator; it is not proof that 94% of instances were in training data
or memorized.

#### Tests omitted from validation

Wang, Pradel, and Liu study patches from CodeStory, LearnByInteract, and OpenHands on
SWE-bench Verified. Running all available developer tests, rather than only the files
selected by the benchmark, identified 7.8% of plausible patches as incorrect and
reduced issue-resolution rates by 4.5 absolute points on average
[wang-2026-swe-solved-correctly, PDF p. 2, RQ1]. PatchDiff generated tests that
distinguished 29.6% of plausible patches from developer patches; manual review judged
28.6% of divergent patches certainly incorrect. Their combined estimate is 6.2
points of score inflation [wang-2026-swe-solved-correctly, PDF pp. 2 and 9-10,
RQ2-RQ4].

The strong conclusion is that benchmark tests have measurable false positives. The
bounded caveat is that a developer patch is not the unique valid implementation:
behavioral divergence is a screening signal, not automatically an error.

#### Verified audit

OpenAI later audited 138 SWE-bench Verified tasks that o3 failed inconsistently over
64 runs. At least six experienced engineers reviewed each task. The audit reports
material problems in 59.4% of this selected subset: 35.5% had tests that were too
narrow, 18.8% tests that demanded unspecified behavior, and 5.1% miscellaneous
issues. It also reports that every tested frontier model reproduced a gold patch or
verbatim task-specific information for at least some instances
[openai-2026-swebench-retirement, sections "Background", "Too narrow and too
wide tests", and "Contamination"].

This is **audit-reported** evidence that Verified no longer separates frontier
systems cleanly. The 59.4% figure must not be extrapolated to all 500 tasks: the sample
was deliberately enriched for frequently failed tasks. OpenAI is also a model vendor
and co-curator, although retracting a widely used metric runs against the immediate
incentive to preserve its earlier benchmark narrative.

#### Pro audit

After recommending SWE-Bench Pro as a replacement, OpenAI audited that benchmark too.
On its 731-task public split, frontier pass rate had reportedly risen from 23.3% to
80.3% in eight months. A screening pipeline flagged 286 cases; deeper agent-assisted
review labeled 200/731 (27.4%) broken, while a campaign with five experienced engineers
per reviewed item identified 249/731 (34.1%). OpenAI summarizes the prevalence as
approximately 30%, with overly strict tests, underspecified prompts, weak coverage,
and misleading prompts as the main classes
[openai-2026-swebench-pro-audit, sections "Methodology", "Human-supervised agent
review", and "Human annotation campaign"].

The reversal - first Verified, then the proposed replacement - is important negative
evidence. Benchmark curation is an ongoing measurement process, not a one-time filter.
Because the review pipeline determined which tasks received deeper scrutiny, an
independent full-population audit is still needed.

### 4.3 Contamination, leakage, and overfitting are distinct

At least four mechanisms are often collapsed into the word "contamination":

1. **Temporal exposure risk:** an item was public before a model cutoff.
2. **Confirmed corpus overlap:** the training corpus and evaluation item can be matched.
3. **Behavioral evidence of recall:** a model reproduces gold-patch or task-specific
   content without enough supplied evidence.
4. **Harness overfitting:** prompts, policies, lookup tables, or tools are directly
   optimized against public evaluation tasks.

The SWE-Bench+ 94% statistic is type 1
[aleithan-2024-swe-bench-plus, PDF p. 2]. The OpenAI reproduction probes provide type
3 evidence for some tasks [openai-2026-swebench-retirement, section
"Contamination"]. A separate localization study reports that two Claude models found
all edited files from issue text alone about six times as often on SWE-bench Verified
as on BeetleBox, and about three times as often as on the January 2025 SWE-rebench
split [prathifkumar-2025-swe-memory, PDF p. 3, Tables 3-4]. That is suggestive type 3
evidence, but project-distribution differences and a two-model sample prevent a causal
claim of memorization.

Harness overfitting can be more direct than passive model exposure. AI Agents That
Matter notes that a lookup table could score 100% on many small public agent
benchmarks and finds that most surveyed benchmarks lacked a holdout at the generality
level they claimed to measure [kapoor-2024-agents-matter, PDF pp. 7-9, Section 5 and
Table 1]. LangChain's production-oriented harness optimization report independently
warns that autonomous hill climbing overfits visible evals and therefore separates
optimization and holdout cases by behavior category
[langchain-2026-better-harness, sections "Building learning systems that generalize"
and "Better-Harness"].

## 5. Stochastic success, repeated sampling, and reliability

HumanEval introduced pass@\(k\), the probability that at least one of \(k\) candidate
programs is correct. Codex-12B was reported at 28.8% pass@1 and 70.2% pass@100
[chen-2021-codex-passk, PDF pp. 1-3, Equation 1]. This demonstrates opportunity from
sampling, not repeat-run reliability. The unbiased estimator and proof are given in
the mathematical synthesis.

Tau-bench introduced the opposite reliability statistic, pass\(^{k}\): the probability
that the same task succeeds on every one of \(k\) independent trials. GPT-4o function
calling reports 61.2% pass\(^{1}\) on retail and 35.2% on airline; retail
pass\(^{8}\) falls below 25% [yao-2024-tau-bench, PDF pp. 2 and 7, Table 2 and
Figure 4]. Pass@\(k\) rises with \(k\); pass\(^{k}\) falls. Quoting one without naming
which direction of reliability it measures is a category error.

The verifier can reverse the benefit of more samples. The Limits of Inference Scaling
Through Resampling generates at least 200 candidates per HumanEval+ task and studies
solutions that pass ordinary tests but fail extended tests. With a false-positive
cost-to-benefit ratio of 4, the reported optimal sample count is at most five for four
models; some settings make zero attempts optimal. The paper attributes the declining
returns to task heterogeneity: easy tasks are solved early, leaving a harder mixture
with a greater false-positive share [stroebl-2026-inference-scaling-flaws, PDF
pp. 4-7, Tables 1-2 and Figures 4-6].

This contradicts an unqualified "test-time compute always helps" claim, but only for
selection through an imperfect verifier under the paper's utility model. Proof
checkers and other sound verifiers have different error structure
[stroebl-2026-inference-scaling-flaws, PDF p. 4, Section 2].

## 6. Cost, budget, and infrastructure are experimental variables

### 6.1 Accuracy without cost is underidentified

An agent can often buy accuracy by retrying, branching, or escalating. A fair
architectural comparison must therefore fix or report the opportunity budget. AI
Agents That Matter recommends:

- compute normalization for scientific model comparisons;
- dollar cost for downstream procurement;
- input and output token counts so future readers can reprice historical runs; and
- accuracy-cost Pareto frontiers instead of a single accuracy rank.

[kapoor-2024-agents-matter, PDF pp. 4 and 6-7, Sections 3-4]

Its HotPotQA demonstration reports 53% lower variable cost for GPT-3.5 and 41% lower
for Llama-3-70B at similar accuracy after joint prompt/example optimization, with a
reported break-even around 1,350 tasks
[kapoor-2024-agents-matter, PDF pp. 5-6, Figure 2]. These are demonstration-specific
results, not universal savings.

### 6.2 Infrastructure can exceed leaderboard margins

Anthropic reports a six-point Terminal-Bench 2.0 difference between its least- and
most-resourced configurations, with \(p<0.01\), and infrastructure failure rates as
high as 6%. Moderate configurations still differed by just under two points. A separate
SWE-bench crossover using 227 tasks and 10 samples per task found 5x versus 1x RAM
increased score by 1.54 points
[anthropic-2026-infrastructure-noise, sections "How we got here", "How this affects
measurement", and "Other sources of variance"].

This is **practitioner-reported quantitative evidence** from one infrastructure stack,
not a universal three-point law. It nevertheless makes sub-three-point leaderboard
gaps difficult to interpret when CPU, RAM, enforcement method, timeout, API latency,
and retry policy are not matched.

## 7. Reproducibility requires traces, versions, and sampling frames

AI Agents That Matter records five recurring reproducibility problems: incompatible
evaluation scripts, repurposed model benchmarks, unaffordable repeated runs, stateful
environment effects, and implementation bugs. It notes that a single full SWE-agent
run could exceed $8,000 at the paper's $4-per-task cap, helping explain the absence of
error bars [kapoor-2024-agents-matter, PDF pp. 10-11, Section 6].

HAL responds with a minimal scaffold interface, isolated local/Docker/VM execution,
common task contracts, token/cost instrumentation, and complete traces. The authors
report finding API changes, provider-routing differences, scaffold failures, and a
TAU-bench data leak only through this infrastructure
[kapoor-2026-hal, PDF pp. 3-4, Table 2]. Standardization reduces accidental variation,
but it does not erase native scaffold differences and can itself introduce adaptation
bugs.

CORE-Bench demonstrates a useful research-agent evaluation shape: 270 tasks based on
90 reproducible papers, three difficulty levels, isolated VMs, and a requirement that
all task questions be correct. The best reported baseline achieves 21% on the hard
level [siegel-2025-core-bench, PDF pp. 1, 4, 6, and 13, Table 3]. The benchmark is
closer to scientific work than function synthesis, but it selects already reproducible
CodeOcean artifacts from three disciplines. It does not establish readiness for novel
mathematical research.

The METR time-horizon study uses approximately 170 tasks, over 800 human baselines
totaling 2,529 hours, and approximately eight runs per agent-task pair
[kwa-2025-long-software-tasks, PDF pp. 4-5, Section 2]. It uses a three-level
hierarchical bootstrap over task families, tasks, and runs, correctly recognizing that
rollouts and related tasks are not independent
[kwa-2025-long-software-tasks, PDF p. 6, Section 3.2]. This sampling structure is a
model for agent evaluation generally.

## 8. Practitioner evidence: recurring harness design patterns

Practitioner reports cannot establish universal causal effects, but they are often the
only sources describing production failure modes. The strongest patterns below either
have concrete observations or independent corroboration.

### 8.1 One authoritative, replayable state

Stencil inspected 78 official Pi extension examples: 60 were stateless, and only two
of 17 stateful examples were judged correct under rewind, fork, or resume. The linked
failures include transient checkpoint maps, branch-insensitive restore, counters in
closures, dynamic tools that survive rewind, and game state that disappears after a
crash [stencil-2026-harness-playbook, sections "The evidence: correctness is optional
in the API" and Appendix A].

The proposed remedy is one journal-derived session state from which transcript,
subagent lifecycle, UI, resume, rewind, and replication are projections. This is a
strong failure taxonomy and a plausible systems invariant, but omp2 was partly
prospective at publication and the audit was performed by a competing harness author.

### 8.2 Trusted control plane and bounded execution

Stencil places session state, inference, policy, routing, approval, limits, and
journaling on the trusted host; the sandbox receives a small execution protocol, and
every returned stream is bounded [stencil-2026-harness-playbook, section "The sandbox
should execute, not decide"]. It also treats tool execution as a cancellable structured
state stream rather than an unbounded string. These are architecture arguments rather
than controlled experiments, but they follow directly from hostile repository,
long-running call, and memory-exhaustion failure cases.

### 8.3 Small, stable, versioned tool surfaces

Stencil's one-task microbenchmark reports that limiting omp to five tools produced a
36.6-second median over six fresh runs, compared with 42.2 seconds for Codex and 37.0
for Pi. The article argues that permanent schemas tax decoding and that changing the
roster invalidates caches [stencil-2026-harness-playbook, section "Every schema has a
tax"]. The sample is too small for a universal optimum. The transferable recommendation
is narrower: measure the marginal value of every permanent schema, keep a stable core,
and place the long tail behind a discoverable compositional surface.

Stencil also recommends recording tool name, version, intent, input, output,
diagnostics, and usage so traces remain evaluable after a contract changes
[stencil-2026-harness-playbook, section "Contract hygiene: intent and version"].
Cursor independently reports per-tool, per-model error baselines and model-specific
edit protocols: patch editing for OpenAI-trained models and string replacement for
Anthropic-trained models [cursor-2026-improving-harness, sections "Tracking and
repairing degradations" and "Customizing the harness for different models"].

### 8.4 Context and cache policy must evolve with the model

Manus reports rebuilding its framework four times, an approximate 100:1
input-to-output token ratio, and tasks with roughly 50 tool calls. Its recommendations
include deterministic append-only serialization, stable cache prefixes, filesystem
offloading, preserving references before dropping bodies, maintaining an explicit todo
near the context tail, and retaining failures as evidence
[manus-2025-context-engineering, sections "KV-cache hit rate", "Mask, don't remove",
"Use the file system as context", and "Keep the wrong stuff in"].

Cursor reports removing many early static-context guardrails as models improved,
preferring on-demand context. It also reports that accumulated tool errors can cause
"context rot" and that mid-chat model changes cause cache misses and
out-of-distribution histories [cursor-2026-improving-harness, sections "Evolving the
context window", "Tracking and repairing degradations", and "Facilitating mid-chat
model switching"].

These claims are not actually inconsistent. The synthesis is to preserve a compact,
typed record of failure and state while pruning redundant raw output. No cited source
provides a controlled estimate of the optimal compression policy.

### 8.5 Offline evals must connect to production traces

Cursor combines an offline suite with online A/B tests. It monitors latency, tokens,
tool calls, cache hits, code Keep Rate, and an LLM classification of user satisfaction;
one more expensive summarizer was shelved after negligible online quality gain. A
focused reliability effort reportedly reduced unexpected tool errors by an order of
magnitude, reaching two to three nines for tools
[cursor-2026-improving-harness, sections "Two ways of assessing harness changes" and
"Tracking and repairing degradations"].

LangChain treats corrected production traces as candidate eval cases, tags cases by
behavior, maintains optimization and holdout splits per category, changes one targeted
component at a time, compares full traces, and requires human review
[langchain-2026-better-harness, sections "Sourcing good evals" and
"Better-Harness"]. Sample sizes and aggregate gains are not published, so the strong
evidence is for the process, not a performance effect size.

### 8.6 Repository legibility and enforceable feedback

OpenAI reports a five-month greenfield case with roughly one million lines, 1,500
merged pull requests, three engineers initially and seven later, and 3.5 pull requests
per engineer-day. The authors estimate one-tenth the manual development time. Practices
include isolated worktrees, a short map-like AGENTS.md, versioned plans and decision
logs, local logs/metrics/traces, dependency-direction lints, machine-readable
remediation, and recurring cleanup
[openai-2026-harness-engineering, sections "We started with an empty git repository",
"We made repository knowledge the system of record", "Enforcing architecture and
taste", and "Entropy and garbage collection"].

The workflow is direct production evidence; the productivity estimate is not a
controlled study. Lines and pull requests are output measures, not correctness or
maintainability, and the post explicitly says long-term coherence remains unknown.

### 8.7 Multi-agent gains must be budget matched

Anthropic's research system uses an orchestrator-worker design with parallel
subagents, checkpointing, end-state evaluation, and filesystem handoffs. It reports a
90.2% improvement over a single Opus 4 agent on an internal research evaluation,
approximately 15 times chat token use for multi-agent research, 40% lower task time
after tool-description optimization, and up to 90% lower wall time through parallel
work [anthropic-2025-multi-agent-research, sections "Evaluation", "The economics of
multi-agent systems", and "Prompt engineering our agents"].

The headline is high meme-risk: private tasks, undisclosed uncertainty, different
token budgets, and a breadth-first research domain. It supports the conditional claim
that parallel independent search can improve breadth when value exceeds roughly 15x
token use. It does not show that multiple agents outperform matched-compute sampling
or that the result transfers to coding and mathematics.

Anthropic's earlier cross-customer synthesis recommends the more conservative default:
begin with the simplest prompt or workflow that passes an evaluation; add agentic
complexity only when it produces measured value; keep planning visible; and document
and test the agent-computer interface
[anthropic-2024-building-effective-agents, sections "When (and when not) to use frameworks" and
"Summary"].

## 9. Meme-risk register

| Compressed claim | What the evidence actually supports | Risk |
|---|---|---|
| "Codex was 70.2% reliable." | Codex-12B achieved 70.2% pass@100: at least one test-passing candidate among 100, not one-run or eight-run reliability [chen-2021-codex-passk, PDF pp. 1-3]. | Very high |
| "A better model scored 12.47% on SWE-bench." | A specific GPT-4 Turbo plus SWE-agent ACI, budget, prompt, environment, and test grader reported 12.47% [yang-2024-swe-agent, PDF p. 6]. | High |
| "94% of SWE-bench was contaminated." | 94% predated selected model cutoffs, which establishes possible exposure, not corpus membership or memorization [aleithan-2024-swe-bench-plus, PDF p. 2]. | Very high |
| "SWE-bench+ proved the true score was 3.97%." | The paper reports both 3.97% and 5.49% under descriptions that require reconciliation [aleithan-2024-swe-bench-plus, PDF pp. 3 and 7]. | Very high |
| "Verified is 59.4% broken." | 59.4% of a failure-enriched 138-task audit subset had material issues; it is not a random estimate for all 500 [openai-2026-swebench-retirement]. | Very high |
| "Agent time horizon doubles every seven months." | An OLS trend on a selected software-task suite gives 207 days, bootstrap CI 166-240, with reference-human and external-validity caveats [kwa-2025-long-software-tasks, PDF pp. 5-8]. | High |
| "Agents will do month-long work by a forecast date." | The paper labels this a conditional extrapolation if its trend generalizes; contractor and maintainer times differed 5-18x [kwa-2025-long-software-tasks, PDF pp. 7-8]. | Very high |
| "Multi-agent is 90.2% better." | Anthropic reports that gain on a private breadth-first research eval while using roughly 15x chat tokens [anthropic-2025-multi-agent-research]. | Very high |
| "Five tools is optimal." | Five tools won one six-run latency microbenchmark; the broader claim is merely that schemas have measurable costs [stencil-2026-harness-playbook]. | Very high |
| "Codex made a product in one-tenth the time." | This is the team's estimate from one greenfield internal case, without a matched human counterfactual [openai-2026-harness-engineering]. | High |
| "More reasoning effort hurts agents." | HAL observes this in a majority of tested cells, not as a general law over models, tasks, or harnesses [kapoor-2026-hal, PDF p. 1]. | Medium-high |

## 10. Empirically defensible claims for a mathematics paper

The following propositions are **derived here** as a cross-source synthesis; they are
not verbatim claims from any single source:

1. **Configuration dependence:** changing the harness while holding model and task
   approximately fixed can change success, cost, and failure modes by practically
   meaningful amounts.
2. **Budget confounding:** repeated samples, retries, branching, escalation, and
   parallel agents change the opportunity set; accuracy comparisons without budget
   normalization do not identify an architectural effect.
3. **Verifier dependence:** an observed pass rate is a convolution of true capability
   and grader sensitivity/specificity. More candidates can increase false as well as
   true positives.
4. **Non-independent trials:** task difficulty, repository, failure history, shared
   context, provider, and runtime create dependence. Trial-level binomial intervals
   are generally too optimistic.
5. **Benchmark nonstationarity:** public tasks invite model exposure and harness
   overfitting; environments, APIs, prices, and models change; a benchmark requires
   versioning, holdouts, refresh, and repeated audit.
6. **Reliability differs from opportunity:** pass@\(k\) and pass\(^{k}\) measure
   opposite operational desiderata and should be reported together.
7. **Production observability is part of evaluation:** final reward alone cannot show
   unsafe shortcuts, loops, wrong-account actions, tool-contract failures, or recovery
   behavior.

The evidence does **not** yet justify universal numerical laws for the optimal number
of tools, agents, retries, context tokens, or planning steps.

## 11. Priority research gaps

The following gaps are **derived here** from the limitations above:

1. A preregistered, balanced model-by-harness-by-budget experiment on private,
   rotating, professionally specified repository tasks.
2. Independent audits estimating both verifier false-positive and false-negative
   rates from probability samples, not only failure-enriched subsets.
3. Reliability curves over repeated trials with task-, repository-, day-, and
   provider-level clustering.
4. A benchmark for mathematical research harnesses: theorem search, formal proof,
   counterexample discovery, symbolic computation, literature attribution, and
   reproducible artifact generation should be graded separately.
5. Matched-compute comparisons of single-agent retry, tree search, and multi-agent
   orchestration.
6. Controlled context-policy experiments comparing raw-history retention, typed
   state, summaries, retrieval, and filesystem offloading.
7. Longitudinal maintenance studies using defect escape, rollback, security,
   documentation accuracy, and time-to-repair rather than lines or pull requests.
8. Standard schemas for trace provenance, tool versions, budgets, environment images,
   verifier versions, and intervention logs.

## 12. Source index

### Academic PDFs

| Source ID | Status | Local evidence | Canonical record |
|---|---|---|---|
| chen-2021-codex-passk | preprint; foundational estimator | [PDF](../papers/academic/chen-2021-codex-passk.pdf) | <https://arxiv.org/abs/2107.03374> |
| jimenez-2024-swe-bench | ICLR 2024 | [PDF](../papers/academic/jimenez-2024-swe-bench.pdf) | <https://arxiv.org/abs/2310.06770> |
| yang-2024-swe-agent | NeurIPS 2024 | [PDF](../papers/academic/yang-2024-swe-agent.pdf) | <https://arxiv.org/abs/2405.15793> |
| kapoor-2024-agents-matter | TMLR 2025 | [PDF](../papers/academic/kapoor-2024-agents-matter.pdf) | <https://arxiv.org/abs/2407.01502> |
| xia-2024-agentless | FSE 2025 | [PDF](../papers/academic/xia-2024-agentless.pdf) | <https://arxiv.org/abs/2407.01489> |
| aleithan-2024-swe-bench-plus | preprint | [PDF](../papers/academic/aleithan-2024-swe-bench-plus.pdf) | <https://arxiv.org/abs/2410.06992> |
| wang-2026-swe-solved-correctly | ICSE 2026 | [PDF](../papers/academic/wang-2026-swe-solved-correctly.pdf) | <https://arxiv.org/abs/2503.15223> |
| zhu-2025-rigorous-agentic-benchmarks | NeurIPS 2025 Datasets and Benchmarks | [PDF](../papers/academic/zhu-2025-rigorous-agentic-benchmarks.pdf) | <https://arxiv.org/abs/2507.02825> |
| yao-2024-tau-bench | ICLR 2025 | [PDF](../papers/academic/yao-2024-tau-bench.pdf) | <https://arxiv.org/abs/2406.12045> |
| stroebl-2026-inference-scaling-flaws | ICLR 2026 | [PDF](../papers/academic/stroebl-2026-inference-scaling-flaws.pdf) | <https://arxiv.org/abs/2411.17501> |
| siegel-2025-core-bench | TMLR 2025 | [PDF](../papers/academic/siegel-2025-core-bench.pdf) | <https://arxiv.org/abs/2409.11363> |
| kwa-2025-long-software-tasks | NeurIPS 2025 | [PDF](../papers/academic/kwa-2025-long-software-tasks.pdf) | <https://papers.nips.cc/paper_files/paper/2025/hash/85069585133c4c168c865e65d72e9775-Abstract-Conference.html> |
| kapoor-2026-hal | preprint | [PDF](../papers/academic/kapoor-2026-hal.pdf) | <https://arxiv.org/abs/2510.11977> |
| yao-2026-harness-bench | preprint | [PDF](../papers/academic/yao-2026-harness-bench.pdf) | <https://arxiv.org/abs/2605.27922> |
| prathifkumar-2025-swe-memory | preprint | [PDF](../papers/academic/prathifkumar-2025-swe-memory.pdf) | <https://arxiv.org/abs/2512.10218> |

### Primary audits and practitioner sources

| Source ID | Class | Canonical URL |
|---|---|---|
| openai-2026-swebench-retirement | primary benchmark audit | <https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/> |
| openai-2026-swebench-pro-audit | primary benchmark audit | <https://openai.com/index/separating-signal-from-noise-coding-evaluations/> |
| stencil-2026-harness-playbook | practitioner postmortem and architecture playbook | <https://stencil.so/blog/harness-playbook> |
| anthropic-2024-building-effective-agents | practitioner synthesis | <https://www.anthropic.com/engineering/building-effective-agents> |
| anthropic-2025-multi-agent-research | internal production report | <https://www.anthropic.com/engineering/multi-agent-research-system> |
| manus-2025-context-engineering | production architecture report | <https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus> |
| openai-2026-harness-engineering | internal engineering case report | <https://openai.com/index/harness-engineering/> |
| cursor-2026-improving-harness | production experimentation report | <https://cursor.com/blog/continually-improving-agent-harness> |
| anthropic-2026-infrastructure-noise | quantitative industry experiment | <https://www.anthropic.com/engineering/infrastructure-noise> |
| langchain-2026-better-harness | practitioner evaluation methodology | <https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals> |
