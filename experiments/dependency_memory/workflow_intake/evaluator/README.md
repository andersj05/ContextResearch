# Evaluator-only manifests

These files derive labels from complete observed command histories using the
independent receipt grader. They are excluded by the actor-view schema and may
not be copied into prompts, retained memory, tool descriptions or instance
metadata. They are not available through an actor filesystem or archive.

The current implementer sees development manifests; this is explicitly logged.
Directory names alone do not create independent or blind evaluation. New model
calls require a separately verified runner and information-access contract.
