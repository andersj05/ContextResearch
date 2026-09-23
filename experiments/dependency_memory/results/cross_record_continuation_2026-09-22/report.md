# Cross-record continuation after permanent provider failure

The original 348-call preregistered run stopped after 199 dispatches. One projected-index final call was permanently missing. A separate frozen continuation dispatched only the remaining 149 identities. This is an exploratory post-stop analysis; the original primary criterion is unassessable.

Complete paired futures: 35/36. Known settled model planning credits: 3.8247600; missing usage has 7.65 credits of conservative reservation, not observed debit.

| Method | Exact failures / 36 | Model errors | Missing answers | Failures on complete pairs | Known model credits | Known local credits | Known lower total |
|---|---:|---:|---:|---:|---:|---:|---:|
| prompt | 3 | 3 | 0 | 3/35 | 0.8692970 | 0.00316717172 | 0.87246417172 |
| structured | 6 | 6 | 0 | 6/35 | 0.9607910 | 0.00300103239 | 0.96379203239 |
| checked | 18 | 18 | 0 | 18/35 | 1.0240565 | 0.0061524537 | 1.0302089537 |
| automatic | 7 | 7 | 0 | 7/35 | 0.3385855 | 0.00500175611 | 0.34358725611 |
| direct | 4 | 4 | 0 | 4/35 | 0.1920580 | 0.00169642753 | 0.19375442753 |
| indexed_raw | 1 | 1 | 0 | 1/35 | 0.2234505 | 0.0026904081 | 0.2261409081 |
| indexed_projected | 7 | 6 | 1 | 6/35 | 0.2780390 | 0.00388255505 | 0.28192155505 |
| full | 6 | 6 | 0 | 6/35 | 0.4389800 | 0.00587017696 | 0.44485017696 |

The lower total for an arm with a missing answer omits unknown model usage; the original failed indexed projection also lost its unsaved local recovery timer. It is not a measured equal-cost comparison for that arm.

| Family | prompt | structured | checked | automatic | direct | indexed_raw | indexed_projected | full |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| retry_queue | 2/12 | 5/12 | 5/12 | 1/12 | 4/12 | 1/12 | 2/12 | 5/12 |
| ci_promotion | 0/12 | 1/12 | 6/12 | 2/12 | 0/12 | 0/12 | 2/12 | 1/12 |
| data_pipeline | 1/12 | 0/12 | 7/12 | 4/12 | 0/12 | 0/12 | 3/12 | 0/12 |
