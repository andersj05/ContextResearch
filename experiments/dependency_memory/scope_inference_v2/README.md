# Replacement source-only scope launch

October 1, 2026. [Protocol](PROTOCOL.md). The original frozen runner omitted
creation of its reservation directory and stopped before generation. Its
[saved stop](../results/scope_luna_2026-10-01/stop.json) and zero-dispatch analysis
remain intact. The replacement creates that directory; every scientific input,
prompt and scoring rule is unchanged. New local identities prevent resuming the
abandoned launch.

Three mocked tests reproduce the original failure, require durable reservation
before generation, check metering, and compare all public request bytes. The
original four-case CLI loopback/configuration audit applies with a fresh run.
It checks serialization and client behavior, not inaccessible provider internals.

```powershell
python -m unittest experiments.dependency_memory.scope_inference_v2.test_runtime -v
python -m experiments.dependency_memory.scope_inference_v2.run --prepare build/scope-inference-v2-preflight.json
python -m experiments.dependency_memory.scope_inference_v2.run --analyze
```

Preparation is one-time. Attestation requires all original and replacement
source bytes, abandoned-launch evidence and new manifest bytes to be committed
before any generation. The user approved the eight-call payload and bounded
quota use. No historical spent allocation is reopened. Eight calls and 20
planning credits remain maxima; no retries or model fallback are allowed.

All results concern one inspected public program and constructed catalog/timing
controls. No natural prospective task, universal correctness, model-independent
scope certificate or production saving is established.

The launch frozen at `ea5c450` dispatched three requests. Two metered answers
each agree on all 14,505 catalog rows and answer 12/24 byte-limited late queries.
The third has a permanent transport timeout with unknown usage; five identities
remain never dispatched. Known model cost is 0.062325 planning credits, with a
7.65 unknown reservation. The original eight-answer criterion is unassessable.
The [saved report](../results/scope_luna_v2_2026-10-01/report.md) preserves this
incomplete result. No failed identity was retried.
