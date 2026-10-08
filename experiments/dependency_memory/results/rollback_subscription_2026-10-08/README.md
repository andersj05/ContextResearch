# Rollback subscription verification and E1

October 8, 2026. The [finding](../../../../research/ROLLBACK_SUBSCRIPTION_2026-10-08.md)
describes the user's selected subscription route and its limitations.

- [Offline checks](offline_checks.json): 19 scientific access, accounting and
  failure-semantics tests pass; no model calls.
- [Frozen E1 manifest](calibration_v1/manifest.json): eight authored calibration
  requests, new authorization, current client hashes and isolated runtime.
- [Installed-client preflight](calibration_v1/preflight.json): ten unauthenticated
  localhost probes, current signed-in model catalog and sanitized quota snapshot.
- [Runtime audit](calibration_v1/runtime_audit.json): pinned Python 3.11 Docker
  image, fixed limits and actual isolated interpreter execution.

Live outcomes will be added after the frozen calibration dispatch. The E0 archive
and old studies are preserved. This bundle does not establish rollback benefit.
