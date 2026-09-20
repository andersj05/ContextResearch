# Paper workspace

Working title: **Repeated Context Compression with Delayed Task Dependencies**. The title, venue, and authorship are provisional.

## Documents to edit

- [Manuscript](manuscript.md): the main paper entry point, including the finite example, locally audited scaling result, scripted recovery comparison, first Luna development diagnostic, and limitations.
- [Living findings draft](findings-draft.md): a short account of what we know, what the new results change, and the next milestone. Update it together with the claim register as evidence changes.
- [Outline](outline.md): section-by-section argument and remaining work.
- [Related-work map](related-work.md): nearby results and the distinctions a novelty argument must address.
- [Claim register](claims.csv): what may currently be stated, with evidence and limitations.
- [Bibliography](references.bib): stable citation keys and known metadata. Entries with incomplete metadata say so.

Use `[@citation-key]` citations in Markdown. The builder checks keys and appends readable references to the assembled Markdown. Its HTML preview is a self-contained reading copy with headings and linked citations; it does not typeset LaTeX mathematics. The editable document is always `paper/manuscript.md`, not a generated preview.

```powershell
python scripts/build_paper.py
python scripts/validate_context_repo.py
```

Generated files are under ignored `build/paper/`. No external typesetting software is required to begin drafting.

## Current draft and update discipline

The manuscript now incorporates the [exact finite-chain optimum](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md), [locally audited scaling derivation](../research/PROOF_AUDIT_2026-09-18.md), and [exact restricted recovery results](../experiments/dependency_memory/results/recovery_frontier_report.md). External review and novelty remain open. The short findings draft is versioned and dated; v0.3 added the [correctness audit](../research/CORRECTNESS_AUDIT_2026-09-19.md) and its refinements to the [staged pilot](../docs/LLM_PILOT_SPEC.md). For a new result, update its claim-register evidence and limitation, then the relevant manuscript/draft paragraphs and `docs/STATUS.md`. Keep the negative controls and avoid turning experiment plans into reported outcomes. Realistic agent performance remains unresolved.

Templates: [derivation](templates/derivation.md), [source note](templates/source-note.md), [experiment plan](templates/experiment-plan.md). The [current protocol](../docs/EXPERIMENT_PROTOCOL.md) is the governing experimental specification.

Living draft v0.8 includes the 96-request Luna tranche (C25), exact post-hoc parent/child grading (C26), the revision-direction design (C27), the offline held-out clue checkpoint (C28), and the completed 24-request follow-up (C29). The follow-up's 24 optimal choices concern a simplified task and do not establish causal improvement over the first workflow. The earlier fake controls remain C24. No native-harness superiority or external endorsement is established; held-out request integration and evaluation remain unfinished.
