# Historical workflow memory replay

An offline handoff task built from eight actual attempt records in the completed
September 19 transfer workflow. No model, provider client or network calls.

```powershell
python -m experiments.dependency_memory.workflow_replay.run
python -m unittest discover -s experiments/dependency_memory/workflow_replay -t . -v
```

- [Contract](CONTRACT.md): selection, information access, two byte limits, exact
  cost model, controls and limits of interpretation.
- `evidence.py`: source hashes, positional extraction, independent original
  classifier, complete field projection and scoped receipts.
- `replay.py`: visible-only continuation, serialized memory boundaries, metered
  checks, repair and archive tools. Baselines share the same rule and evidence.
- `run.py`: 180 resource contracts, 45 exact allowance frontiers, full primary
  operation ledgers and receipt invalidation controls.
- [Report](../results/workflow_replay_report.md) and
  [certificate](../results/workflow_replay_certificate.json): regenerated offline
  by the repository validator.

The actual observations include three charged generations whose answers were
lost and one preflight stop. A later plan must distinguish them despite their
shared failure label. The counterfactual compactions and delayed worker/target
reveals are constructed; no historical failure is attributed to memory loss.

The repair helps within some byte/resource envelopes. Directly retaining the
public rule's checked result is cheaper than auditing an insufficient summary
first. Preserve that strong baseline and the cheap-recovery losses. This is a
source-backed engineering replay, not a learned extractor, native compactor,
independent task sample or demonstration of production dollar savings.
