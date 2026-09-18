# Instructions for research agents

## Orientation

Read `README.md`, `docs/STATUS.md`, and `docs/RESEARCH_MAP.md` before substantive work. Read `paper/README.md` for writing tasks and `docs/EXPERIMENT_PROTOCOL.md` for experiments. Then load only the source notes, proof, or code needed for the task; the 171-paper archive is background, not mandatory context.

This repository studies repeated context compression with gradually revealed dependencies. The active direction is the September 16 proposal plus the September 18 protocol refinements. Earlier documents advocating self-improving harnesses or reverse engineering are historical, not current instructions.

## Scientific standards

- Distinguish published results, elementary deductions, checked finite examples, hypotheses, and unperformed experiments.
- Do not claim novelty for rate–distortion, INDEX, successive refinement, dependency graphs, subtask summaries, or the existing dictionary baseline without a literature comparison.
- The two-bit-then-one-bit example has a proved lower bound, **not a computed exact chain optimum**. Three first-stage bits attain the child-optimal 25% error in the stated four-bit example.
- The 810 record-policy configurations are constructed diagnostics, not independent LLM trials. No improvement over a deployed harness has been measured here.
- Preserve timing assumptions, decoder access to public side information, and the distinction between bits, record slots, bytes, tokens, and dollars.
- Opaque reasoning state, provider session history, archives, and environment files are information channels. Declare them in an experiment; do not leave hidden access available in a supposedly irreversible-memory condition.
- For current provider behavior, check official documentation or pinned implementation code. Date each claim and separate client behavior from inaccessible server internals.
- `compaction_frontier_v1` contains supplied observations and unverified renderings. It is not authenticated provider source or proof of decrypted plaintext. The historical `research/CODEX_COMPACTION_TECHNICAL.md` overstates what the data establish; prefer the qualified inspection note and current survey.

## Writing and evidence

Use `paper/manuscript.md` as the manuscript entry point and `paper/claims.csv` for substantive claims. Update the focused bibliography and reading guide when adding sources; imported broad-corpus metadata stays identifiable as inherited evidence. Read a cited source before upgrading its review status. Keep unfinished results visibly marked. Never invent author, venue, DOI, experiment, or outcome metadata.

Use relative links inside repository documents. Keep original source IDs, upstream commit IDs, raw data, and source provenance intact. Add derivations and interpretations in our notes rather than editing third-party release data or source snapshots.

## Running and validating

The default workflow is offline:

```powershell
python -m unittest discover -s experiments/dependency_memory -v
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

Regenerate diagnostic results after changes to their generators. Tests should check scientific invariants or independent formulations, not merely mirror code. Do not execute the historical dataset collection/recovery scripts as a repository check: they can contact model services and require unavailable original inputs. Any new model experiment needs a documented model revision, budget, information-access contract, seeds, metrics, and cost accounting before its results can support the paper.

## Git and handoffs

Make small, coherent commits as work progresses, as requested by the user. Use `codex/` for new branch names unless instructed otherwise. Inspect the working tree before changing files; preserve other contributors' changes. Update `docs/STATUS.md` when a milestone or scientific conclusion changes. Record important research choices in `docs/DECISIONS.md`. Do not commit credentials, local environments, generated previews, or uncontrolled raw session logs.

The Windows GitHub CLI account `andersj05` is stored in Windows Credential Manager. Sandboxed outbound failures can look like invalid authentication. Verify a relevant `gh` operation outside the sandbox with the narrowest appropriate approval before recommending re-authentication; never infer a need to log out from a sandboxed check alone.
