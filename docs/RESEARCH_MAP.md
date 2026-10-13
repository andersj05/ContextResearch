# Research map and authority

Start with [current status](STATUS.md), then choose one route. Read the selected
summary and linked evidence; expand to source code or literature only as needed.

## Task routes

| Task | First stop | Then inspect |
|---|---|---|
| Find what experiments ran and what happened | [Experiment catalog](../experiments/INDEX.md) | Its study summary, original report and frozen protocol |
| Review model behavior or cost | [Model studies](../experiments/summaries/model-studies.md) | Per-launch ledgers, missing-answer dispositions and cost units |
| Work on proofs or coding bounds | [Mathematical checks](../experiments/summaries/mathematical-checks.md) | Proof note, certificate, independent verifier and strong controls |
| Inspect failure checks, source analysis or replay | [Offline diagnostics](../experiments/summaries/offline-diagnostics.md) | Actor access, public rules, inputs and saved outputs |
| Plan a future empirical study | [Prepared studies](../experiments/summaries/planned-studies.md) | [Protocol](EXPERIMENT_PROTOCOL.md), launch gates and new bounded contract |
| Review or implement rollback experiments | [October 8 handoff](ROLLBACK_REVIEW_HANDOFF_2026-10-08.md) | [Pilot and complete suite](../experiments/dependency_memory/rollback_pilot/README.md), task/analysis/controller specifications and [prior art](../research/ROLLBACK_PILOT_DESIGN_2026-10-07.md) |
| Understand rollback validity and information loss | [Information boundary audit](../research/ROLLBACK_INFORMATION_BOUNDARY_2026-10-13.md) | V6 removes earlier source packets; v7 preserves them but deletes only a short record conditional on a shared lesson. Post hoc immediate recovery and final completion are distinct. [V9](../experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/README.md) has a calibration ceiling and no rollback outcomes; [v10](../experiments/dependency_memory/results/rollback_patch_v10_2026-10-13/README.md) has three real failed patches but misses its four-failure gate; [v11](../experiments/dependency_memory/results/rollback_patch_v11_2026-10-13/README.md) completed 28 eligible failures with near-universal repair and no observed deletion benefit; its inherited global stop preserves descriptive scope |
| Review longer rollback tasks and parallel runs | [Completed v5 allocation and verified replay](../research/ROLLBACK_STAGED_CONTINUATION_2026-10-09.md) | [User-authorized amendment](../experiments/dependency_memory/rollback_development_v5_continuation/PROTOCOL.md); 768 final dispositions, 2124 metered completions, four unknowns; 46/48/3 policy/memory/mechanism pairs all have zero mean quality difference, with a strong control ceiling |
| Calibrate harder rollback questions | [Completed v6 comparison](../experiments/dependency_memory/results/rollback_challenge_v6_four_actions_confirmation_2026-10-09/LIVE_RUN.md) | 260 fixed task pairs; K=122/254 known, R=64/258 known. Rollback is worse under the prospective conservative exact test (p=2.48e-7); all 2,496 known calls replay, eight unknowns remain missing. One authored ledger family; earlier control-only calibration is preserved |
| Write or revise the paper | [Paper workspace](../paper/README.md) | [Claims](../paper/claims.csv), manuscript, focused bibliography |
| Compare related work | [Focused reading guide](../sources/READING_GUIDE.md) | Source text and bounded review notes, then inherited indexes if needed |
| Locate derivations or interpretive notes | [Research notes](../research/README.md) | Topic-specific note and its evidence links |
| Understand a past choice | [Decisions](DECISIONS.md) | [Historical handoff/map](history/README.md) and original frozen contract |
| Add or reorganize files | [Placement rules](REPOSITORY_STRUCTURE.md) | [Catalog maintenance](../experiments/README.md) |

## Evidence authority

- **Project direction:** current status and explicit user instructions; old plans
  and recorded launch permissions do not reopen completed allocations.
- **Empirical outcomes:** saved evidence, original protocol and reproducible grader.
  A newer narrative does not overrule original observations.
- **Scientific claims:** [paper/claims.csv](../paper/claims.csv), with assumptions,
  evidence and limitations. Catalog summaries are retrieval aids, not new evidence.
- **Theory:** distinguish analytic proof, exhaustive finite computation, achievable
  witnesses, conservative bounds and conjectures. One does not substitute for another.
- **Units and access:** preserve bits, record slots, bytes, tokens and costs, along
  with timing, public side information, archives and provider-state access.

## Background and historical material

The inherited library contains 171 PDFs and broad harness notes. Use the
[academic index](../paper-notes/INDEX.md), [implementation index](../source-notes/INDEX.md)
and [source catalog](../catalog/sources.csv) selectively. Imported review labels
are inherited metadata; moving files does not upgrade review status. The
[historical corpus overview](../HARNESS_CORPUS_README.md) does not set current scope.

For the supplied compaction release, first read the
[qualified inspection](../research/COMPACTION_FRONTIER_REVERSE_ENGINEERING.md).
Its 2,061 claimed observations and 104 selected renderings are package contents,
not new project experiments or authenticated decrypted plaintext. The older
[technical explanation](../research/CODEX_COMPACTION_TECHNICAL.md) overstates hidden
mechanism evidence and remains historical. Collection dependencies are incomplete.

The [pinned harness snapshots](../sources/harness-snapshots/2026-09-16/README.md)
retain upstream commits and hashes. They are evidence slices, not current runnable
installations. Recheck official docs or pinned code for present provider behavior.

The [October 2 detailed map](history/RESEARCH_MAP_2026-10-02.md) preserves the prior
milestone-by-milestone inventory. It is optional history, not startup context.
