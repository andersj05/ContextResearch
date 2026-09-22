# GPT-6 Luna medium delayed-release pilot

The [contract](CONTRACT.md) and executable gate were frozen in `136d589` before
production answers. The fixed schedule uses the mutable `gpt-6-luna` alias with
medium reasoning through the managed Codex subscription. Four constructed
release handoffs pass through two imposed byte limits and sixteen delayed
continuations per method. This is not native compaction or held-out evidence.

Saved data belong to
[`results/luna6_revision_2026-09-22`](../results/luna6_revision_2026-09-22).
The immutable manifest records source fingerprints and public fixtures;
`completion.json` supplies the terminal launch status. Every call has its public
request, final answer, token usage, and reservation record. Raw reasoning and
credential values are excluded. Shared parent calls count once in actual launch
usage and once per method in the hypothetical method cost.

Reproduce the offline evidence audit and report from the repository root:

```powershell
python scripts/analyze_luna6_revision.py
python -m unittest discover -s experiments/dependency_memory -v
python scripts/validate_context_repo.py
```

`scripts/benchmark_luna6_local_cost.py` separately measures local adapter CPU
time. Rerunning that calibration changes measured data and requires regenerating
the analysis. It never makes model calls. Tests check an independent gate truth
table, scope changes, byte capacity, future disclosure and complete usage.

Do not rerun `run.py` as a repository check. It is a live, explicitly opted-in
launcher and refuses an existing manifest. It never implicitly retries or
continues an interrupted experiment. The documented allocation and frozen
schedule are not authorization for other experiments.

The current preflight verifies ordinary top-level wrapper tools, separate base
instructions, exact public messages and one-generation termination. The client
does not expose authoritative nested-tool registry metadata. Legacy explanatory
text copied from the older isolation module must not be read as a new proof of
an empty registry. The operative contract rejects all tool attempts and certifies
only accepted no-tool model responses; remote internals remain unobserved.

Direct projections use a known gate schema. They retain underlying check scope,
test membership and negative blocker observations rather than an irrevocable
ready bit. Repair first pays for a model proposal and then substitutes this same
projection. The direct method is therefore an essential control. Indexed archive
access is also declared and metered. Unknown extraction and infrastructure costs
are not silently treated as measured production savings.
