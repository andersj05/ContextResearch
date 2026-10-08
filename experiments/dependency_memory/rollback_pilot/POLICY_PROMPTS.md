# Complete policy and autonomous rollback prompts

October 8, 2026. Draft interfaces for E4/E5 in [the suite](EXPERIMENT_SUITE.md).
These are whole-policy comparisons; their capability differences are declared
rather than represented as the isolated K/R deletion intervention in E2.

## Shared solver instruction for E4

> Solve the original task using the supplied task data, available work and public
> observations. Earlier guesses may be wrong. Return one complete candidate in
> the supplied artifact schema. Do not claim that unavailable tests have passed.

Give this same instruction to A/K/R/G/I. The model sees no condition label. All
receive the original task and domain schema. A/K see their accumulated history;
R/G see their permitted retained context; I sees no earlier candidate or feedback.
Host-generated receipts are the only execution evidence. The host's candidate
selector uses public tests identically for all policies and exposes no archive
to the actor. Reject excess context rather than adding undisclosed compaction.

## Recurring lesson and summary

Reuse the lesson and generic-compactor instructions in [PROMPTS.md](PROMPTS.md).
The writer receives the policy's current visible context, the new candidate and
its public receipt. It does not receive forgotten archive contents or private
scores. For R, append this clarification to the lesson prompt:

> The next attempt will receive the original task, latest receipt and your new
> lesson. Preserve still-relevant earlier lessons from the supplied record, as
> well as the new evidence. Do not infer that a missing old fact was false.

Use the same clarification for K's lesson writer; K retains additional history
afterward. G's compactor receives the analogous instruction referring to a summary.
L/S remain limited to 1,024 visible tokens. A writer's malformed or capped output
ends that policy episode with its best public-test candidate, if any; no uncharged
fallback or hidden memory restoration is allowed.

## Shared action interface for E5

Provide the original task, active context, public receipts, a bounded checkpoint
catalog and explicit controller capabilities. A catalog entry is an ID and a
description of at most 128 visible tokens; root plus three non-root entries gives
at most 512 description tokens, with JSON overhead counted separately. Capability
fields describe operations that can actually be enacted, not a preferred outcome.

> Work toward the original task. Return a public action record and either a
> complete candidate or null when you need a context action first. Use KEEP to
> continue, SAVE_CHECKPOINT to preserve the input state before this trial, or
> ROLLBACK with an available checkpoint ID to reconsider a branch. Use only
> operations supported by the controller. Explain the requested action briefly
> using supplied evidence; a guess or timeout alone does not prove a route false.

Output schema: `action` in KEEP/SAVE_CHECKPOINT/ROLLBACK; `checkpoint_id` string
or null; `checkpoint_description` string or null; `reason` string; `artifact`
domain artifact or null. Only ROLLBACK has a non-null target ID and only SAVE has
a non-null description. The reason is capped at 256 visible tokens. It is a
concise public justification, not a request for hidden chain of thought.

Append supports KEEP only. Automatic rollback supports KEEP/SAVE and advertises
that a public failure triggers restoration of the latest checkpoint. Chosen
rollback supports all three actions and does not roll back without a valid model
request. Thus E5 changes action capability and policy as well as resulting context;
use E2 for an isolated deletion estimate.

SAVE stores the exact active input before the current call, not its new trial
output. This prevents saving a just-adopted trial assumption into the checkpoint
intended to precede it. New IDs are assigned by the host. A ROLLBACK target must
be an available ancestor of the active branch. On restoration, remove descendant
checkpoints from the available catalog; their raw records stay evaluator-only.
Store at most four checkpoints, evicting the oldest non-root checkpoint on overflow.

A rollback request includes no candidate. The host generates one charged lesson
from the active suffix and public receipts, restores the chosen visible checkpoint
and appends the lesson. It never restores opaque provider state. Automatic rollback
uses the same writer after an objective failure. Both stop if the writer is unusable
or another call cannot be reserved. Enforce three rollbacks and 24 calls maximum.

SAVE/KEEP may return null, but the call still counts. A structurally invalid action
or unavailable target produces a fixed host receipt and no state change, without
an automatic model retry. It consumes its normal call allowance. All conditions
stop on a full public pass or resource exhaustion and use the same public selector.

## Calibration for the later stages

Each later stage reserves eight new requests on disclosed non-study fixtures.
For E4, exercise math/code solver schemas, L/S writers in each domain and two
continuations: eight calls total. For E5, exercise KEEP/SAVE/ROLLBACK formats in
both domains plus a lesson and a restored-context continuation. Pair these with
offline controller fixtures for invalid targets, eviction, ancestor restoration,
writer failure and budget exhaustion. Do not consume held-out study tasks for
calibration or treat these interface calls as policy performance results.

## Withheld feedback decision probe

Use the 12 authored diagnostic fixtures specified in the suite, outside all
natural-task cohorts. The model sees no grade, reference or correctness label.

> Inspect the original task and the proposed completed candidate. Decide whether
> to retain it as the final answer or reconsider it. Return one JSON object with
> `decision` equal to KEEP_FINAL or RECONSIDER and a brief `reason`. Do not produce
> a replacement answer or claim to have executed checks that were not supplied.

The reason has a 256 visible-token cap. A malformed decision is a diagnostic
interface failure, shown separately from correct acceptance or rejection. Use
one request per fixture, with no writer, retry or repair call.
