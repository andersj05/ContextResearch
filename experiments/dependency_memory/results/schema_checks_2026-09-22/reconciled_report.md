# Frozen schema-check comparison: reconciled cost sensitivity

The frozen 72-call run covers six constructed evaluation traces and 12 paired terminal decisions. Every arm succeeds on 12/12. The automatic method therefore **fails the preregistered primary criterion** of fewer failures than stronger prompting at no higher total cost. It matches the hand-written direct record outcomes.

| Arm | Failures | Calls | Model credits | Local read bytes | Estimated total credits |
|---|---:|---:|---:|---:|---:|
| prompt | 0/12 | 24 | 0.2537065 | 0 | 0.25370650 |
| automatic | 0/12 | 12 | 0.0725445 | 58046 | 0.0731251835798 |
| direct | 0/12 | 12 | 0.0667650 | 24514 | 0.0670101760896 |
| indexed | 0/12 | 12 | 0.0628880 | 10760 | 0.0629956186692 |
| full | 0/12 | 12 | 0.0951865 | 43100 | 0.09561753809 |

The matched allowance is the stronger prompt arm's observed total, 0.25370650 experimental credits; all controls fit. The direct and indexed controls are cheaper than the automatic method. The automatic method removes memory-writing model calls and is cheaper than prompting, but terminal outcomes are tied.

**CPU correction.** The live Windows `process_time_ns` reported zero for short local operations. The separate development-trace benchmark uses `perf_counter_ns` in seven 1,000-repeat batches. This table prices the largest measured batch for each family, twice for its two evaluation traces, at the preregistered 0.0001 credit/second plus exact locally read bytes at 0.00000001 credit/byte. Those prices are synthetic and the CPU calibration is post-run; only model tokens and local bytes were measured in the live comparison. No actual subscription debit is attributable.

The raw analysis field `source_commit` names the protocol-price commit (`284405d`); the implementation frozen before model answers is `75ab94f`, as recorded in this reconciliation.

The extractor uses schema-provided opaque-ID, reference and ephemeral annotations. It checks exact IDs and owner/path/reference triples but does not certify unannotated state. The evaluation cases have new identities and tool results within the three development schema families. They are constructed traces, not previously observed incidents or unseen schema structures. The direct records omit human schema-authoring cost. No native compaction or production gain is shown.

The raw [saved-evidence analysis](analysis.json), [local calibration](local_calibration.json), and [frozen protocol](../../schema_checks/FROZEN_PROTOCOL.md) give the inputs for this sensitivity report.
