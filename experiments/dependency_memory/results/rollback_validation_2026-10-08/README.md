# Repository verification for rollback implementation

October 8, 2026. These are offline checks, not additional model trials.
The [sealed E0 archive](../rollback_e0_2026-10-08/README.md) contains the new
engineering evidence; the [finding](../../../../research/ROLLBACK_E0_IMPLEMENTATION_2026-10-08.md)
explains its limits.

- [repository_tests.json](repository_tests.json): all 663 dependency-memory tests
  pass, with zero skips/failures/errors, including the 66 rollback tests and nine
  actual Docker integration checks. Elapsed time: 1,250.499 seconds.
- [scientific_regeneration.json](scientific_regeneration.json): full existing
  scientific regeneration PASS; 75 claims, 63 bibliography entries, 171 PDF hashes
  and 195 immutable imports. Its startup catalog snapshot has 53 entries and
  1,000 tracked result files because registration/staging continued while it ran.
- [saved_evidence_unit_checks.json](saved_evidence_unit_checks.json): 16 existing
  Luna/revision saved-evidence validator tests pass after the integration change.
- [verification.json](verification.json): final current catalog/navigation,
  E0 archive/math bindings, paper build and explicit scope of the combined checks.

Current catalog/navigation checks and the new sealed E0 mathematical/archive
verifier are recorded separately in the final verification record. The pre-existing
scientific packages and frozen numerical results were unchanged after the broad
regeneration began; the added E0 validator hook is covered by the separate verifier
and its five evidence probes. Counts from overlapping runs must not be added as
independent tests or observations. Actual new model calls and provider spend: zero.
