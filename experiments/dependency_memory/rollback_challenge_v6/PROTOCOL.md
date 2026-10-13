# Rollback challenge v6: calibration before confirmation

October 9, 2026. New, repository-authored development tasks. The initial freeze
preceded live v6 observations; the separately labelled response-contract follow-up
below is informed by its completed control screen. The completed v5 allocation
and all its sources, receipts, ceilings and unknowns remain unchanged.

The purpose is to find a task distribution with room for both failure and
recovery, then measure rollback on independent tasks. Statistical significance
is a possible outcome, never a selection criterion or stopping rule.

## Questions and construction

Three finite families each have three levels. Levels are generator settings,
not claims about model difficulty:

| Family | Levels | What makes the question harder |
|---|---|---|
| Constraint grid | 4x4, 6x6, 9x9 | Coupled row/column/box, given-cell, cage-sum and inequality constraints; a locally valid change can violate another constraint |
| Bitvector program | 4/5/6-bit words, at most 3/5/7 operations | Infer a composition of add, XOR, multiply and rotate from examples; the final packet completes the full finite input domain |
| Revision ledger | 18/40/80 transaction IDs over 5/8/12 accounts | Revisions arrive out of order, replace entire transfers, and can void earlier work; later balances depend on earlier packets |

All accepted answers are finite integer arrays. Program candidates are a bounded
DSL, never submitted Python, eval, files or commands. A program is correct if
it matches the released examples, regardless of whether it matches the planted
program. Any valid grid is accepted; uniqueness is neither required nor claimed.
Ledger answers reconcile every transaction released so far, not future records.

Each seeded instance has a private witness and a checked answer at every stage.
Public graders are compared with separately formulated checks on witnesses,
mutations, hand fixtures and exhaustive small-word operation cases. This is
finite implementation verification, not a proof of model difficulty. There are
no hidden behavioral requirements or human judgments of correctness.

Records are partitioned across meaningful disclosure stages. Stage count and
action cap are frozen in the bundle and identical in calibration and confirmation.
Default: four stages, eight candidate actions. A smaller three-stage/five-action
screen is supported as a separately frozen design; it does not validate the
four-stage design. Stage depth, actual actions and visible history bytes are
reported. No actor is instructed to produce a wrong attempt. The deliberately
wrong first candidate used by offline fixtures is never a live task instruction.

## Access and interventions

The proposed operational target is GPT-6 Luna, medium effort, on the existing
subscription, preserving the v5 audited client route. The user's October 9
instruction authorizes thousands of Luna requests without per-run reconfirmation.
The [campaign record](../results/rollback_challenge_v6_candidates_2026-10-09/campaign_authorization.json)
sets an agent-selected 6,000-additional-admission working ceiling; each allocation
still freezes its complete bound before dispatch. No API key, purchase or model fallback is used.
The model alias is mutable; immutable revision, provider sampling seed and actual
account charges are unavailable. Official interface references were read October
9: [Luna model](https://developers.openai.com/api/docs/models/gpt-6-luna) and
[app-server](https://learn.chatgpt.com/docs/app-server). The installed-client
preflight, not these pages, verifies the operational serialization contract.

Every action and writer starts a fresh process/thread in an empty workspace.
Only the public contract, current packet, accepted artifact, visible history,
retained memory, last feedback and remaining action count are allowed. Actors
cannot access witnesses, source seeds, future packets, evaluator files, task
archives, old provider threads, tools, network, or opaque reasoning replay.
The controller may read evaluator material; it is not part of the actor input.
Global client instructions and the visible tool registry are audited and pinned.

| Arm | At each eligible public mismatch |
|---|---|
| K | Append a model-written lesson; retain raw history |
| R | Append a model-written lesson; clear the entire current history field |
| Z | Clear raw history without a new lesson |
| G | Replace history and prior memory with a generic model-written summary |
| F | Fresh solve from initial artifact and all released packets, without trial feedback or lessons |

The last accepted artifact survives K/R/Z/G; rejected candidates are never
committed to it. A lesson may retain failed-candidate details. This intervention
changes visible representation; it does not erase all knowledge of a failure.
Independent K/R episodes have independent writers; this estimates full-policy
effect, not a matched-common-failure mechanism effect. Scheduled memory cuts and
native compaction are not tested in v6.

Writers use the same 4,096-byte structured contract as v5. All writers count in
usage. Every answer consumes an action, and no writer runs after the final action.
A malformed received answer is an observed failure. All serialized requests
must fit the 131,072-byte inherited admission bound. Bytes are not tokens.
This is an equal-action comparison, not equal token cost or verified equal dollars.

## Prospective stages and selection rule

1. **Screen:** K and F only, all nine family/level cells, normally two seeded
   replicates per cell. Within each family nominate the tier closest to K=57.5%,
   provided both arms are complete with at least two known tasks, K is in
   [25%,85%], F in [25%,90%], and K has a public mismatch on at least one episode.
   Neither arm may have a context-capacity failure in the nominated cell.
   Ties choose the smaller level. Report every cell and all floors/ceilings.
   If none qualifies, nominate none. Screening is small-sample development.
2. **Validate difficulty:** new root seed and new identities, the exact nominated
   cells, same stages/actions/access contract, K and F only. Each cell requires
   at least eight complete tasks per arm, each arm's success in [40%,75%], and
   public mismatches on at least 25% of K episodes. The whole nominated mixture
   must pass, with no context-capacity failures in either arm. Do not silently
   remove a failed validation cell. Capacity failures remain observed failures
   in the fixed-denominator report; they cannot establish question difficulty.
   These point-rate
   gates have sampling uncertainty; Wilson intervals are also reported.
3. **Confirm:** new seed/identities, same validated cells and access/action
   settings. Freeze a primary effect size, discordance assumption and fixed sample
   before any R/K outcomes. K/R are required; Z/G/F can be included as descriptive
   controls. Equal replicate counts per selected cell define the fixed mixture.

All selection artifacts bind audited live controls, their manifests and reports.
Offline fixtures cannot select difficulty or produce a confirmatory result.
Validation/confirmation preparation replays the source evidence before accepting
a selection. New seeds are necessary but do not establish new-family generality.

If the design stays saturated or falls to a floor, preserve the outcome and freeze
a new version/design. Do not change a live bundle, revisit inspected task IDs,
extend its sample until a p-value crosses a threshold, or tune on R-minus-K.

## Analysis and power

The sole confirmatory contrast is complete-episode binary success R minus K.
Report R-only, K-only, both-pass and both-fail pairs, effect size, fixed-denominator
missingness bounds, and the exact two-sided McNemar/binomial p-value at alpha .05.
Any missing selected outcome disables the confirmatory p-value; the complete-case
test remains descriptive. A significant negative effect is not a rollback gain.
Zero discordance is not equivalence. Secondary arms, family splits, resource use,
failed checks and history diagnostics are descriptive, without confirmatory claims.

Power is computed by summing over M~Bin(n,q) discordant pairs, then over
W|M~Bin(M,(q+delta)/(2q)), applying the exact two-sided test's rejection region.
For delta=.10 and q=.30, the 20-pair planning grid first reaches 80% at 260 pairs
(power approximately .81884). This is an assumed alternative, not measured power
or a guarantee of significance. A 260-pair two-arm design with eight actions has
at most 7,800 generations; it needs its own bounded allocation. With three equal
cells, round up to 261 tasks. Do not count generations, arms or packets as
independent task pairs. Provider time effects and fixed family membership limit
generalization; randomized nearby arm scheduling reduces but cannot erase them.

Resources are counted for all received calls including writers, and separately
on complete paired tasks. Input includes cached input; output includes reasoning,
both subsets counted once. The inherited planning-credit conversion is retained
as a declared accounting unit, not presented as current API pricing or actual
subscription debit. Unknown calls retain their reservations.

## Execution and boundedness

Four workers maximum. Freeze every call identity, seed, task, source hash, model,
effort, schedule and state-machine maximum in an immutable preparation bundle.
For action allowance H: K/R/G cost at most 2H-1 generations, Z/F at most H.
The max-calls option rejects a design whose full worst-case allocation exceeds
the budget; it does not truncate inconvenient late tasks. The standard screen
has 18 tasks, 36 episodes and a 414-generation maximum. The three-stage/five-action
screen has a 252-generation maximum. Neither count is a measured usage figure.

A central durable SQLite ledger admits each identity once, meters all replies,
enforces concurrency and the total ceiling, and rejects repeated provider threads.
Unknown dispatches end only that trajectory; unrelated work continues. Account,
source/client, information-access, ledger and evidence-write failures stop all
admissions. No automatic retries. Each completed run is sealed and independently
replayed/regraded without model calls. A global-stop continuation must use a new
output directory and verified receipt replay, preserving earlier unknowns and
counting previous admissions in the same allocation. Completed allocations cannot
be extended. A controller killed before sealing needs evidence recovery and is
not permission to relaunch; the exclusive launch marker remains authoritative
for duplicate prevention, not evidence that a process is still running.

Preparation, preview, tests, simulation, power calculation and audit make zero
provider generations. Only the explicit `launch --live` command dispatches.

## October 9 follow-up: require a candidate on every action

The [initial control screen](../results/rollback_challenge_v6_2026-10-09/LIVE_SCREEN.md)
has 92 progress-only responses among 154 received actions; 17 of its 20 known
failed episodes never produce a public mismatch. Neither the mixed-success
bitvector cell nor any other cell qualifies under the original selection rule.
Preserve that negative calibration result and its four unknown calls.

A new preparation may freeze `require_candidates=true`. Its action schema only
allows `status=candidate`, and its prompt requires the best complete candidate
even when uncertain. It explicitly prohibits intentional wrong attempts. A
received deferral violates this response contract and is an observed invalid
record; no fabricated candidate or feedback replaces it. Writers, public graders,
checkpoints, rollback policies, budgets and information isolation are unchanged.
The optional mode is included in task identities and the public contract. It is
frozen in the manifest and must be preserved by validation and confirmation.
Legacy bundles keep their original schema and remain replayable from snapshots.

The proposed bounded development follow-up has six new tasks: two each from
bitvector level 1, grid level 2 and ledger level 2, with seed 2026100943, three
stages, five actions and K/F only. These cells are chosen from control results,
before any R observations. This is a new screen after an interface change, not
held-out validation of a successful earlier selection. Its maximum is 84 model
generations. The completed initial screen admitted 165; together the maxima for
the completed calls plus this proposed follow-up total 249. The earlier unused
slots do not authorize a different allocation. The later broad user authorization
now covers this separately frozen follow-up and later stages. It cannot silently
extend or overwrite the closed initial screen.

Apply the same control-only rates, natural-mismatch, completeness and capacity
gates. Report every new task and any new floor or ceiling. If this change does
not produce a suitable cell, report that outcome; do not claim that requiring
answers guarantees recoverable mistakes or statistical significance.

## October 9 next design: retain headroom in K, allow a strong fresh control

The completed six-task candidate-required screen has no unknowns: K solves 5/6,
F solves 4/6, and all 49 received actions submit candidates. Its original gate
still nominates no cells. In ledger level 2, K solves 1/2 and F solves 2/2; the
fresh-control ceiling alone excludes this cell despite both K episodes having
public mismatches. Preserve the empty selection. Two tasks do not establish a
reliable performance rate, and this pattern is not a rollback effect.

A separately frozen, control-informed design may set `allow_fresh_ceiling=true`.
It changes only the calibration rule. Screening still requires complete K/F
outcomes, K success in [25%,85%], F success at least 25%, a K public mismatch,
no capacity failures, and the same nearest-57.5%/lower-tier tie rule. F success
may reach 100%. Independent validation still requires K success in [40%,75%],
F success at least 40%, at least eight complete tasks per arm/cell, K public
mismatches on at least 25% of episodes, and no capacity failures. The whole
nominated mixture must pass. F may reach 100% because it is a solvability
control; K supplies the required opportunity for improvement. This does not
assume that R will approach or beat F.

The flag is frozen in the manifest, carried in audited selection artifacts and
inherited unchanged by validation and confirmation. It is not actor information
and does not alter tasks, prompts, graders or interventions. Default false
preserves the original rates. Do not apply the new rule retroactively to either
completed screen. All new phases use new root seeds and disjoint task identities;
no R/K effect has been inspected in choosing this calibration change.

The next screen fixes levels 2 and 3 of all three families, four replicates per
cell, seed 2026100959, three stages/five actions, K/F only, and both optional flags
true. Its 24 tasks/48 episodes have a maximum of 336 generations. Use sixteen
new validation tasks per nominated cell; confirmation retains the independently
planned, fixed-size paired test. The broad campaign authorization covers these
separate allocations; track all admissions against its recorded working ceiling.

## October 9 prospective intermediate ledger and bounded missing controls

The five-action, forty-transaction ledger fails independent validation with
K=3/16 and F=7/16. A separate six-action screen has K=2/8, F=5/7 known and one
missing F outcome; its original complete-outcome rule nominates no cell.
Preserve both negative decisions. No v6 R-arm outcome has been observed.

A new `ledger_profile="intermediate"` retains the ledger semantics but uses
22/28/34 transaction IDs over 5/6/7 accounts at levels 1/2/3. Revision-count and
amount rules retain their original level dependence. The standard profile and
its task identities remain unchanged. Intermediate task identities include the
profile in their seed derivation, and the profile is restricted to ledger tasks.
It is frozen in manifests and selection records and inherited unchanged by later
phases. It is a size variant within the same authored family, not a new benchmark
family or evidence of generalization. The first screen will use level 2, eight
new tasks, three stages and five actions; the extra action is not retained.

A new `robust_control_missingness=true` option applies only to newly frozen
calibration. Screening requires at least eight scheduled tasks per arm/cell;
validation requires at least sixteen. At least seven eighths of scheduled
outcomes must be observed in each arm (at most floor(N/8) missing). For s observed
successes and m missing scores among N scheduled tasks, every completion must
satisfy the existing rate bounds: the entire interval [s/N,(s+m)/N] must lie
inside them. This is an empirical missingness interval, not a confidence interval.
The check is exact rational arithmetic and makes no assumption about why scores
are missing. It never fills in a missing score or retries an admitted identity.

Screening still needs a K public mismatch, no capacity failures and the same
nearest-known-K-rate/lower-level tie rule. Validation still requires the whole
nominated mixture, public mismatches in at least 25% of scheduled K episodes,
and no capacity failures. An unresolved global/source/accounting stop prevents
either stage from passing. The flag cannot change between screen, validation
and confirmation; it never enters actor requests. The default remains the old
complete-outcome rule. Neither of the completed negative results is reclassified.

This calibration rule does not alter the existing engine's primary report or
its suppression of confirmatory p-values when scores are missing. Any future
completion-bound analysis amendment must still be separately frozen and bound
before R/K dispatch, with a fixed sample and no significance-dependent extension.
