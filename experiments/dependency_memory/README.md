# Dependency-memory diagnostics

An offline starting point for the September 16 research proposal. Python 3.10+ and the standard library suffice. No network, model calls, API credentials, training, or package installation are used.

Run from the repository root:

```powershell
python experiments/dependency_memory/experiment.py
python experiments/dependency_memory/compatibility.py
python experiments/dependency_memory/compatibility_scaling.py
python -m unittest discover -s experiments/dependency_memory -v
```

The scripts overwrite only their generated files under `results/`; `experiment.py --output PATH` can select another output directory for its files. The compatibility script always writes to its adjacent results directory.

## What each component establishes

`experiment.py` enumerates the minimum average error for a fixed-length classical message encoding one to four independent fair bits, with the queried coordinate revealed afterward. The query is uniform. Each message label determines a vector of predicted bits, so enumerating decoder codebooks and assigning each source string to its nearest codeword exhausts deterministic encoders/decoders. A fixed public codebook does not store the particular source instance. Randomized mixtures cannot improve the minimum average loss.

Its timing comparison selects a public equal-size block independently of the source values. Showing that block before the bottleneck permits encoding only its coordinates. Showing it afterward does not recreate deleted information. This comparison has a single value-memory bottleneck; it is distinct from the two-stage test below.

`compatibility.py` studies four fair bits, then a first bottleneck, then disclosure of a random three-coordinate subset, then a one-bit bottleneck, then a queried coordinate. It checks every optimal one-bit decoder for the subset and every combination across the four possible subsets. Reaching the subset-optimal 25% error requires at least eight first-stage states (three bits). Two first-stage bits cannot reach that target even though the isolated first bottleneck has an 18.75% error optimum. The exact minimum two-stage error with two first-stage bits is **not** computed.

The record-stream diagnostic separately compares LRU value records with a basic dictionary that releases records upon explicit retirement. An anchor fact must survive many short jobs. Retirements are sound, public events; they are not predicted by an LLM. Queries have no hidden grading value in their input. The policy's update method receives only its retained dictionary and the current event; evaluator truth is separate.

The record test uses a record budget. Serialized dictionary payload bytes are also reported, including keys and ordering, but those counts are not whole-process memory, model tokens, or information bits. It intentionally includes a regime where plain LRU loses the anchor. It is an invariant check and baseline diagnostic, not evidence of superiority over strong structured summaries or deployed harnesses.

## Generated artifacts

`compatibility_scaling.py` adds independent finite checks for the [September 18 derivations](../../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md). It enumerates one-bit child codebooks, grades leave-one-out witnesses, and certifies an entropy bound across all 256 optimal four-bit branch assignments using exact integers. An information argument in the note turns that finite certificate into a uniform error gap for arbitrary joint encoders across independent blocks. These are local derivations awaiting independent review and novelty comparison, not LLM trials or computed chain optima.

- `exact_frontier.csv`: exact finite optimum, an entropy lower bound, coordinate-retention error, and a witness codebook.
- `disclosure_timing.csv`: same source size with relevance disclosed on either side of the bottleneck.
- `compatibility_certificate.json`: exhaustive state-count histogram, explicit three-bit parent witness, and a conservative two-bit error lower bound.
- `compatibility_scaling_certificate.json`: child-codebook checks, leave-one-out witnesses, and the finite entropy certificate used by the block-family proof.
- `workflow_retention.csv`: 810 deterministic record-policy configurations.
- `example_events.json`: a small inspectable generated event stream.
- `summary.json`: scope and aggregate diagnostic counts.

Tests cross-check codebook enumeration against independent enumeration of binary encoders, validate the entropy lower bound, directly grade the compatibility witness, and check revisions, retirement, capacity, absence of query-answer leakage, and exact serialization invariance.

## What remains to build

This is not an LLM or closed-loop agent evaluation. Next work is independent review and novelty comparison of the scaling derivation, tighter bounds where useful, a natural-language compiler adapter with explicit token accounting, and an environment whose actions alter state and whose final result can be checked. Keep raw transcripts outside the compiler's accessible inputs when testing irreversible memory; enabling retrieval requires a separately declared and metered condition.
