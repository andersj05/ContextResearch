# Focused reading guide

Start with the [proposal](../research/LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md). It records the exact local reasoning and the distinctions checked in the September 16 investigation. Then read original sources for the claim you are drafting.

## Mathematical core

| Source | Read for | Local material |
|---|---|---|
| [Fundamental Limits of Prompt Compression](https://proceedings.neurips.cc/paper_files/paper/2024/hash/ac8fbba029dadca99d6b8c3f913d3ed6-Abstract-Conference.html) | Distortion–rate and query information | [PDF](../papers/academic/nagle-2024-prompt-compression-rate-distortion.pdf), [inherited note](../paper-notes/nagle-2024-prompt-compression-rate-distortion.md) |
| [Successive Refinement of Information](https://isl.stanford.edu/~cover/papers/transIT/0269equi.pdf) | Compatible descriptions | Proposal, Sections 2 and 6; original PDF is linked, not archived locally |
| [Causal source coding with side information](https://arxiv.org/abs/1301.0079) | Information timing | Proposal, Section 2; online original |
| [Random-access lower bounds](https://arxiv.org/abs/quant-ph/9904093) | Necessary memory and error | Proposal, Sections 1 and 4; online original |
| [Approximate information states](https://jmlr.org/papers/v23/20-1165.html) | State abstraction and conditional control bounds | [Mathematics addendum](../research/CONTEXT_COMPACTION_MATHEMATICS_2026-09-16.md) |

## Closest memory and evaluation methods

Read [the related-work map](../paper/related-work.md) for DeMem, HiAgent, MemoBrain, The Compaction Cliff, TRACE, and observation masking. Most recent preprints were reviewed online during the investigation; the import does not create PDFs that were never downloaded. Their versioned URLs and analysis are preserved in the proposal/survey. The broader [academic index](../paper-notes/INDEX.md) covers the inherited local library.

## Harness implementation

Read [the survey](../research/CONTEXT_MANAGEMENT_SURVEY_2026-09-16.md) alongside [the pinned snapshots](harness-snapshots/2026-09-16/README.md). Distinguish output truncation, observation masking, summaries, native opaque state, archives, and KV policies. Client source cannot reveal a remote service's private compactor or training objective.

## Provider contracts

The September 18 review checked [OpenAI compaction](https://developers.openai.com/api/docs/guides/compaction), [OpenAI caching](https://developers.openai.com/api/docs/guides/prompt-caching), [Anthropic preserved thinking](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking), and [Anthropic context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing). These are living documents; the [protocol](../docs/EXPERIMENT_PROTOCOL.md) records their implications, not a permanent guarantee about all models.

## Before citing historical compaction data

Read [the qualified inspection](../research/COMPACTION_FRONTIER_REVERSE_ENGINEERING.md). Keep the supplied release's provenance, recovery procedure, and limitations attached to every use. It cannot establish a hidden model's full reasoning or exact compaction algorithm.
