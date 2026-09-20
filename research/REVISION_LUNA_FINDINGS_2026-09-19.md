# Luna responds to the refresh rule in an isolated retention diagnostic

September 19, 2026. **Evidence: 24 completed development requests, not a held-out
evaluation or an improvement experiment.** The [frozen diagnostic](../docs/REVISION_DIAGNOSTIC.md)
followed three avoidable early-retention choices in the first workflow. The user
explicitly authorized a separate 24-request allocation with a 12 conservative
credit-equivalent cap. Launch code was committed as `aa6c0e5` before dispatch.

## Result in plain language

When told that one of the possible future records will be supplied again, Luna
consistently kept the records that were most valuable to protect from deletion.
When we reversed which candidate would be refreshed, it reversed its selection.
This held across the four prespecified visible-record orders and two fixed
receipt-payload fixtures. In this simpler task, every selected pair was optimal.

The result establishes the observed behavior in these prompts. It does not show
that the earlier workflow errors have been fixed: the diagnostic changes the
prompt, removes the inspection decision, and explicitly guarantees an optimal
later selector. It does not reveal the model's internal reasoning.

## Completed schedule and exact grading

All 24 attempted requests completed with valid two-key responses. There were no
policy failures, transport failures, retries, underfilled outputs, or incomplete
scheduled cases. Each request used a fresh process/thread through the reviewed
subscription adapter, the mutable `gpt-5.6-luna` alias, low reasoning effort, and
the default tier. Every accepted decision retained the prescribed
`session_budget_exceeded` harness termination and zero observed tool events.

| Public rule | Selections in all eight cells | Optimal selections | Exact later availability | Exact regret |
|---|---|---|---|---|
| Refresh the smaller candidate | `job-4`, `job-5` | 8/8 | 4/5 | 0 |
| Refresh the larger candidate | `job-0`, `job-1` | 8/8 | 4/5 | 0 |
| No refresh | `job-0`, `job-1` | 8/8 | 1/3 | 0 |

Availability is calculated over all 30 equally likely candidate/target routes
with the guaranteed optimal later selector. No route was actually sampled or
disclosed to Luna. These are exact conditional scores of 24 model outputs, not
720 independent model observations or measured rates of complete agent success.
All full two-key selections tie in the no-refresh condition; its eight optimal
grades are consequently less informative than the 16 directional selections.

All eight matched first/last-refresh pairs have selected-rank-sum shift eight,
the ideal full-pair shift. This differs from each prespecified deterministic
static control, whose shift is zero. The no-refresh choices consistently use
the lowest two keys despite changes in displayed order, which is an observed
tie preference; canonical metadata and response-schema ordering remain possible
influences. No unseen naming or metadata-order variations were tested.

The shift and regret are not independent confirmations. For two selected records
in each matched cell, let `s_F` and `s_L` be their rank sums and `D = s_F - s_L`.
Direct substitution in the declared availability formulas gives
`r_F = (9 - s_F)/30`, `r_L = (s_L - 1)/30`, hence mean paired regret
`(r_F + r_L)/2 = (8 - D)/60`. Every observed answer fills its capacity, so this
identity applies to this run. Underfilled outputs require their selected counts
as well; a large rank shift alone would not certify optimal retention.

## Accounting and reproducibility

Reported usage is 66,200 input tokens, including 17,920 cached-input tokens, and
5,651 output tokens, including 5,075 reasoning tokens. Each request reports zero
cache-write tokens; unlike a missing counter, these are recorded observations.
The conservative total is **0.58328 credit equivalents**, with no uncertain
reservations, under the 12-equivalent cap. The actual subscription debit
attributable to this experiment is unknown. No API billing, purchase, reset,
repair request, or held-out model call occurred.

The two development allocations now contain 120 model requests in total and
3.12278 conservative credit equivalents. Their request limits remain separate:
96 in the first tranche and 24 here. Both request allocations are exhausted;
unused credit-equivalent headroom does not authorize another request.

The [saved report](../experiments/dependency_memory/results/revision_luna_2026-09-19/report.md)
lists all outputs and displayed positions. The [manifest](../experiments/dependency_memory/results/revision_luna_2026-09-19/manifest.json),
[ledger](../experiments/dependency_memory/results/revision_luna_2026-09-19/requests.json),
and [summary](../experiments/dependency_memory/results/revision_luna_2026-09-19/summary.json)
preserve the frozen requests, source hashes, allocation, responses, and usage.
The [read-only audit certificate](../experiments/dependency_memory/results/revision_luna_2026-09-19/independent_audit.json)
reconciles hashes, all 24 scheduled rows, independent route grades, and reservation
arithmetic. Historical source hashes identify launch code rather than requiring
future working files to remain unchanged.

A separate read-only local review recomputed every grade and all eight shifts,
checked all 46 frozen source hashes against raw Git blobs at `aa6c0e5`, and
confirmed 24 distinct threads and exact frozen public request bytes. This is
additional local verification, not external review or certification of provider
internals. Zero regret is also not perfect availability: the best conditional
scores remain 4/5 with refresh and 1/3 without it.

```powershell
python scripts/audit_revision_run.py --run-dir experiments/dependency_memory/results/revision_luna_2026-09-19
python scripts/validate_context_repo.py
```

## Interpretation and next question

The useful next question is why the rule-sensitive behavior observed here did
not reliably appear in the earlier, fuller workflow. The present result is
consistent with sensitivity to task framing or the downstream guarantee, but
does not identify either as the cause. A future comparison should vary those
features separately on matched inputs while keeping the objective, record
distribution, grading, and budget explicit. Specify it offline before allocating
more model calls; do not rewrite or rerun the successful cells to build a story.

This diagnostic has one observation per rule/order/payload cell, no paired
generation seed, and only eight directional pairs. It supports no population
accuracy estimate, natural-task generalization, native-compaction advantage,
causal improvement over the first pilot, or novelty claim. Held-out request
integration and external mathematical review remain separate unfinished work.
