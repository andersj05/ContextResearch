import unittest
from dataclasses import fields, replace
from unittest.mock import patch

from artifact_workflow import (Action, ArtifactEnvironment, Config, Fixture, Observation,
                               POLICIES, Policy, PublicView, Receipt, choose_action,
                               compact, make_fixture, run_episode, visible_records)


def instance(**changes):
    config = replace(Config(jobs=4, delay=2), **changes)
    receipts = tuple(Receipt(f"job-{i}", 1, f"receipt-{i}") for i in range(4))
    fixture = Fixture(receipts, ("job-0", "job-1"), "job-1",
                      Receipt("job-0", 2, "revised-0") if config.revise else None)
    return config, fixture


def ready_to_submit(config, fixture):
    env = ArtifactEnvironment(config, fixture)
    for name in ("collect_receipts", "seal_receipts", "read_manifest", "process_build", "seal_build"):
        env.step(Action(name))
    for _ in range(config.delay):
        env.step(Action("work"))
    env.step(Action("get_requirement"))
    return env


class ArtifactWorkflowTests(unittest.TestCase):
    def test_early_clue_prevents_late_unrecoverable_failure(self):
        config, fixture = instance()
        no_probe = run_episode(config, fixture, POLICIES[1])
        probe = run_episode(config, fixture, POLICIES[2])
        self.assertEqual(no_probe.failure, "missing_receipt")
        self.assertTrue(probe.success)
        self.assertEqual(probe.cost_units, no_probe.cost_units + config.probe_cost)
        self.assertEqual(probe.package, fixture.receipts[1])
        self.assertEqual([c["boundary"] for c in probe.compactions], [1, 2])

    def test_ample_memory_makes_probe_unnecessary_and_costly(self):
        config, fixture = instance(first_capacity=4)
        never = run_episode(config, fixture, POLICIES[1])
        always = run_episode(config, fixture, POLICIES[2])
        budgeted = run_episode(config, fixture, POLICIES[3])
        self.assertTrue(never.success and always.success and budgeted.success)
        self.assertFalse(budgeted.probe_attempted)
        self.assertGreater(always.cost_units, never.cost_units)

    def test_small_child_still_fails_after_successful_probe(self):
        config, fixture = instance(second_capacity=1, revise=False)
        fixture = replace(fixture, target="job-0")
        result = run_episode(config, fixture, POLICIES[2])
        self.assertEqual(result.failure, "missing_receipt")
        self.assertEqual(result.compactions[0]["retained_records"], 2)
        self.assertEqual(result.compactions[1]["retained_records"], 1)

    def test_probe_only_reveals_manifest_and_cannot_reread_receipts(self):
        config, fixture = instance()
        env = ArtifactEnvironment(config, fixture)
        env.step(Action("collect_receipts"))
        clue = env.step(Action("inspect_manifest"))
        self.assertEqual(clue.candidates, fixture.candidates)
        self.assertEqual(clue.receipts, ())
        self.assertIsNone(clue.required_key)
        env.step(Action("seal_receipts"))
        blocked = env.step(Action("collect_receipts"))
        self.assertEqual(blocked.error, "action_out_of_order")
        self.assertEqual(blocked.receipts, ())
        self.assertEqual(env.step(Action("read_manifest")).candidates, clue.candidates)

    def test_policy_api_and_window_reset_exclude_old_history(self):
        config, fixture = instance()
        views = []
        def observe(view, policy):
            views.append(view)
            return choose_action(view, policy)
        with patch("artifact_workflow.choose_action", side_effect=observe):
            run_episode(config, fixture, POLICIES[1])
        self.assertEqual({f.name for f in fields(PublicView)},
                         {"config", "phase", "probe_attempted", "memory", "window"})
        first = next(v for v in views if v.phase == "manifest")
        self.assertEqual(first.window, ())
        self.assertEqual({r.key for r in first.memory}, {"job-2", "job-3"})
        later = views[views.index(first):]
        # The lost target's receipt never reappears in any supplied input.
        self.assertTrue(all(fixture.receipts[1] not in visible_records(v.memory, v.window) for v in later))
        self.assertEqual(next(v for v in views if v.phase == "work").window, ())

    def test_snapshot_restores_environment_context_and_cost(self):
        config, fixture = instance()
        checkpoint = run_episode(config, fixture, POLICIES[2], stop_at_first_boundary=True)
        kept = run_episode(config, fixture, POLICIES[2], checkpoint=checkpoint)
        lost = run_episode(config, fixture, Policy("recent_same_prefix", probing="always", retention="recent"),
                           checkpoint=checkpoint)
        replay = run_episode(config, fixture, POLICIES[2], checkpoint=checkpoint)
        self.assertEqual(kept, replay)
        self.assertTrue(kept.success)
        self.assertFalse(lost.success)
        self.assertEqual(kept.cost_units, lost.cost_units)
        self.assertEqual(checkpoint.environment.phase, "manifest")
        self.assertEqual(checkpoint.environment.completed_steps, 0)
        self.assertEqual(checkpoint.environment._current["job-0"].revision, 1)
        self.assertEqual(checkpoint.compactions, [])
        self.assertEqual(kept.trace[:len(checkpoint.trace)], lost.trace[:len(checkpoint.trace)])

    def test_checkpoint_rejects_different_instance(self):
        config, fixture = instance()
        cp = run_episode(config, fixture, POLICIES[2], stop_at_first_boundary=True)
        with self.assertRaises(ValueError):
            run_episode(config, replace(fixture, target="job-0"), POLICIES[2], checkpoint=cp)

    def test_terminal_verifier_checks_key_revision_and_exact_token(self):
        config, fixture = instance()
        fixture = replace(fixture, target="job-0")
        cases = [(None, "missing_receipt"), (fixture.receipts[2], "wrong_artifact"),
                 (fixture.receipts[0], "stale_revision"),
                 (Receipt("job-0", 2, "guessed"), "wrong_receipt"),
                 (fixture.revision, None)]
        for receipt, error in cases:
            with self.subTest(error=error):
                env = ready_to_submit(config, fixture)
                outcome = env.step(Action("submit", receipt))
                self.assertEqual(outcome.error, error)
                self.assertEqual(outcome.success, error is None)
                self.assertEqual(env.package, receipt)
                with self.assertRaises(ValueError):
                    env.step(Action("submit", fixture.revision))

    def test_revision_is_used_and_old_observation_cannot_overwrite_it(self):
        config, fixture = instance(first_capacity=4)
        fixture = replace(fixture, target="job-0")
        result = run_episode(config, fixture, POLICIES[1])
        self.assertEqual(result.package, fixture.revision)
        state = visible_records((fixture.revision,), (Observation("old", receipts=(fixture.receipts[0],)),))
        self.assertEqual(state, (fixture.revision,))

    def test_blocked_probe_is_charged_and_budget_can_terminate(self):
        config, fixture = instance(first_capacity=4, probe_available=False, probe_cost=3)
        attempted = run_episode(config, fixture, POLICIES[2])
        skipped = run_episode(config, fixture, POLICIES[3])
        self.assertTrue(attempted.success and skipped.success)
        self.assertEqual(attempted.cost_units, skipped.cost_units + 3)
        self.assertEqual(sum(t["observation"]["error"] == "probe_unavailable" for t in attempted.trace), 1)
        exhausted = run_episode(replace(config, cost_budget=1), fixture, POLICIES[2])
        self.assertEqual((exhausted.failure, exhausted.cost_units), ("cost_budget", 1))

    def test_zero_capacity_and_zero_delay(self):
        config, fixture = instance(first_capacity=0, second_capacity=0, delay=0)
        result = run_episode(config, fixture, POLICIES[2])
        self.assertFalse(result.success)
        self.assertTrue(all(c["retained_records"] == 0 for c in result.compactions))
        self.assertFalse(any(t["action"]["name"] == "work" for t in result.trace))
        self.assertEqual(compact((), (Observation("receipts", receipts=fixture.receipts),), 0, POLICIES[1]), ())

    def test_future_query_and_nonce_values_do_not_steer_prefix_policy(self):
        config, fixture = instance()
        prefix = run_episode(config, fixture, POLICIES[3], stop_at_first_boundary=True)
        changed = replace(fixture, target="job-0", receipts=tuple(replace(r, token="different-"+r.key) for r in fixture.receipts))
        other = run_episode(config, changed, POLICIES[3], stop_at_first_boundary=True)
        self.assertEqual([r["action"]["name"] for r in prefix.trace], [r["action"]["name"] for r in other.trace])
        self.assertEqual([r.key for r in compact(prefix.memory, prefix.window, 2, POLICIES[3])],
                         [r.key for r in compact(other.memory, other.window, 2, POLICIES[3])])

    def test_seeded_runs_are_reproducible_with_boundary_capacity_enforced(self):
        for seed in range(8):
            for capacity in (0, 1, 2, 6):
                config = Config(first_capacity=capacity)
                fixture = make_fixture(seed, config)
                first = run_episode(config, fixture, POLICIES[3])
                second = run_episode(config, make_fixture(seed, config), POLICIES[3])
                self.assertEqual(first, second)
                self.assertTrue(all(c["retained_records"] <= c["capacity_records"] for c in first.compactions))

    def test_out_of_order_submission_cannot_skip_obligations(self):
        config, fixture = instance()
        env = ArtifactEnvironment(config, fixture)
        outcome = env.step(Action("submit", fixture.receipts[1]))
        self.assertEqual(outcome.error, "action_out_of_order")
        self.assertIsNone(env.package)
        self.assertIsNone(env.verdict)

    def test_invalid_configuration_is_rejected(self):
        for change in ({"first_capacity": -1}, {"jobs": 1}, {"probe_cost": 0}, {"delay": 0.5}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                Config(**change)


if __name__ == "__main__":
    unittest.main()
