"""Independent scientific and coverage checks for the transfer-study schedule."""

from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import random
import unittest

from transfer_interface import (FRAMINGS, GUARANTEES, GUIDANCE, JOB_COUNTS, RULES,
                                job_keys, request_bytes, validate_response)
from transfer_study import (BLOCKS, FACTORS, MAX_REQUESTS, WORKERS, FakeClient,
                            aggregate, block_material, bootstrap_interval,
                            enumerate_availability, grade, make_plan)


def latest_receipt_availability(selected, priorities, rule):
    """Track revision values and explicitly answer every candidate/target route.

    This does not use the rank-sum formula or the module's availability routine.
    An updated record replaces its stale version even when the old one survived.
    At most two candidates exist, so the two-slot ideal child can retain every
    available candidate record.
    """
    keys = tuple(priorities)
    hits = []
    for pair in combinations(keys, 2):
        latest = {key: 1 for key in keys}
        parent = {key: 1 for key in selected}
        if rule != "none":
            lower, upper = sorted(pair, key=lambda key: priorities[key])
            refreshed = lower if rule == "first" else upper
            latest[refreshed] = 2
            parent[refreshed] = 2
        child = {key: parent[key] for key in pair if key in parent}
        if len(child) > 2:
            raise AssertionError("Child exceeds declared capacity")
        for target in pair:
            hits.append(child.get(target) == latest[target])
    return Fraction(sum(hits), len(hits))


def rows_for(plan, mode="optimal"):
    client = FakeClient(mode)
    rows = []
    for case in plan["cases"]:
        row = {key: case[key] for key in ("case_id", "block", "worker", *FACTORS)}
        try:
            selected = validate_response(client.complete(case["request"]), case["request"])
            row.update(status="completed", grade=grade(selected, case))
        except ValueError:
            row.update(status="policy_failure", grade=None)
        rows.append(row)
    return rows


class TransferScientificTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = make_plan()
        cls.cases = {(case["block"], case["jobs"], case["refresh_rule"]): case
                     for case in cls.plan["cases"]}

    def test_full_schedule_is_balanced_reproducible_and_four_worker_partitioned(self):
        plan = self.plan
        cases = plan["cases"]
        self.assertEqual((BLOCKS, WORKERS, MAX_REQUESTS), (32, 4, 1536))
        self.assertEqual(len(cases), 1536)
        self.assertEqual(len({case["case_id"] for case in cases}), 1536)
        self.assertEqual(plan["conditions_per_block"], 48)
        self.assertEqual(plan["worker_request_cap"], 384)
        self.assertEqual(Counter(case["block"] for case in cases), Counter({block: 48 for block in range(32)}))
        self.assertEqual(Counter(case["worker"] for case in cases), Counter({worker: 384 for worker in range(4)}))
        expected = set(product(JOB_COUNTS, FRAMINGS, GUARANTEES, GUIDANCE, RULES))
        by_condition = Counter(tuple(case[key] for key in FACTORS) for case in cases)
        self.assertEqual(by_condition, Counter({condition: 32 for condition in expected}))
        for worker in range(4):
            subset = [case for case in cases if case["worker"] == worker]
            self.assertEqual(len({case["block"] for case in subset}), 8)
            self.assertEqual(Counter(tuple(case[key] for key in FACTORS) for case in subset),
                             Counter({condition: 8 for condition in expected}))
        for block in range(32):
            subset = [case for case in cases if case["block"] == block]
            self.assertEqual({tuple(case[key] for key in FACTORS) for case in subset}, expected)
            self.assertEqual({case["worker"] for case in subset}, {block % 4})
        repeat = make_plan()
        self.assertEqual([(case["case_id"], case["request_sha256"]) for case in cases],
                         [(case["case_id"], case["request_sha256"]) for case in repeat["cases"]])
        self.assertEqual(plan["realized_routes_sampled"], 0)
        self.assertEqual(plan["heldout_requests"], 0)
        self.assertEqual(plan["model_requests_completed_by_plan"], 0)

    def test_materials_are_paired_within_block_size_and_vary_across_blocks(self):
        materials = {}
        for case in self.plan["cases"]:
            request = case["request"]
            material = (request["public_metadata"], request["visible_records"])
            previous = materials.setdefault((case["block"], case["jobs"]), material)
            self.assertEqual(material, previous)
            raw = request_bytes(request)
            self.assertEqual(case["request_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(case["request_bytes"], len(raw))
            self.assertNotIn(case["case_id"].encode(), raw)
        for jobs in JOB_COUNTS:
            priorities_seen, orders_seen = set(), set()
            for block in range(32):
                priorities, order, records = block_material(block, jobs)
                self.assertEqual(set(priorities), set(job_keys(jobs)))
                self.assertEqual(set(priorities.values()), set(range(jobs)))
                self.assertEqual(set(order), set(job_keys(jobs)))
                self.assertEqual(len(order), jobs)
                metadata, visible = materials[block, jobs]
                self.assertEqual(metadata["jobs"], [{"key": key, "refresh_priority": priorities[key]}
                                                    for key in job_keys(jobs)])
                self.assertEqual([row["key"] for row in visible], order)
                self.assertEqual({row["key"]: row["token"] for row in visible},
                                 {row["key"]: row["token"] for row in records})
                priorities_seen.add(tuple(priorities[key] for key in job_keys(jobs)))
                orders_seen.add(tuple(order))
            self.assertGreater(len(priorities_seen), 1)
            self.assertGreater(len(orders_seen), 1)
            for key in job_keys(jobs):
                tokens = {next(row["token"] for row in materials[block, jobs][1] if row["key"] == key)
                          for block in range(32)}
                self.assertEqual(len(tokens), 32)

    def test_formula_matches_independent_latest_revision_outcomes_for_every_selection(self):
        for block, jobs, rule in product((0, 7, 31), JOB_COUNTS, RULES):
            case = self.cases[block, jobs, rule]
            priorities, _, _ = block_material(block, jobs)
            choices = [choice for size in range(3) for choice in combinations(job_keys(jobs), size)]
            reference = max(latest_receipt_availability(choice, priorities, rule) for choice in choices)
            for choice in choices:
                with self.subTest(block=block, jobs=jobs, rule=rule, selected=choice):
                    observed = latest_receipt_availability(choice, priorities, rule)
                    result = grade(choice, case)
                    self.assertEqual(Fraction(result["availability"]), observed)
                    self.assertEqual(enumerate_availability(choice, priorities, rule), observed)
                    self.assertEqual(Fraction(result["reference_availability"]), reference)
                    self.assertEqual(Fraction(result["exact_parent_regret"]), reference - observed)
                    self.assertEqual(result["route_count"], jobs * (jobs - 1))
                    self.assertEqual(result["optimal_parent"], observed == reference)
                    self.assertEqual(result, grade(tuple(reversed(choice)), case))

    def test_full_pair_normalization_endpoints_and_underfilled_outcomes(self):
        for jobs in JOB_COUNTS:
            for rule in ("first", "last"):
                case = self.cases[0, jobs, rule]
                priorities, _, _ = block_material(0, jobs)
                ranked = sorted(priorities, key=priorities.get)
                best, worst = ((ranked[-2:], ranked[:2]) if rule == "first" else (ranked[:2], ranked[-2:]))
                self.assertEqual(Fraction(grade(best, case)["normalized_regret"]), 0)
                self.assertEqual(Fraction(grade(worst, case)["normalized_regret"]), 1)
                span = Fraction(4, 15) if jobs == 6 else Fraction(5, 33)
                self.assertEqual(Fraction(grade(worst, case)["full_pair_regret_span"]), span)
                self.assertGreater(Fraction(grade((), case)["normalized_regret"]), 1)
            case = self.cases[0, jobs, "none"]
            for pair in combinations(job_keys(jobs), 2):
                result = grade(pair, case)
                self.assertEqual(Fraction(result["availability"]), Fraction(2, jobs))
                self.assertTrue(result["optimal_parent"])
                self.assertIsNone(result["normalized_regret"])

    def test_fake_controls_separate_optimality_from_key_and_display_preferences(self):
        for mode in ("optimal", "static_low", "first_visible", "invalid"):
            rows = rows_for(self.plan, mode)
            summary = aggregate(rows)
            if mode == "invalid":
                self.assertEqual(summary["status_counts"], {"policy_failure": 1536})
                self.assertEqual(summary["primary"]["valid_pairs"], 0)
                self.assertEqual(summary["primary"]["transport_complete_pairs"], 128)
                self.assertIsNone(summary["primary"]["mean_normalized_regret_benefit"])
                self.assertEqual(summary["primary"]["mean_valid_and_optimal_benefit"], "0")
                continue
            self.assertEqual(summary["status_counts"], {"completed": 1536})
            primary = summary["primary"]
            self.assertEqual((primary["scheduled_pairs"], primary["valid_pairs"], primary["complete_blocks"]),
                             (128, 128, 32))
            self.assertEqual(primary["mean_normalized_regret_benefit"], "0")
            self.assertEqual(primary["block_bootstrap_95_percent_interval"], [0.0, 0.0])
            refresh_rows = [row for row in rows if row["refresh_rule"] != "none"]
            if mode == "optimal":
                self.assertTrue(all(row["grade"]["optimal_parent"] for row in rows))
                self.assertTrue(all(row["grade"]["exact_parent_regret"] == "0" for row in rows))
            else:
                self.assertGreater(sum(Fraction(row["grade"]["exact_parent_regret"]) for row in refresh_rows), 0)
                self.assertTrue(any(not row["grade"]["optimal_parent"] for row in refresh_rows))

    def test_primary_known_guidance_contrast_has_exact_normalized_and_raw_effects(self):
        for improved_guidance, expected in (("prospective", Fraction(1)), ("generic", Fraction(-1))):
            rows = rows_for(self.plan)
            for case, row in zip(self.plan["cases"], rows):
                if (case["framing"] != "workflow" or case["guarantee"] != "unspecified"
                        or case["refresh_rule"] == "none" or case["guidance"] == improved_guidance):
                    continue
                priorities = {item["key"]: item["refresh_priority"] for item in case["request"]["public_metadata"]["jobs"]}
                ranked = sorted(priorities, key=priorities.get)
                worst = ranked[:2] if case["refresh_rule"] == "first" else ranked[-2:]
                row["grade"] = grade(worst, case)
            primary = aggregate(rows)["primary"]
            self.assertEqual(Fraction(primary["mean_normalized_regret_benefit"]), expected)
            self.assertEqual(primary["block_bootstrap_95_percent_interval"], [float(expected)] * 2)
            self.assertEqual(Fraction(primary["mean_valid_and_optimal_benefit"]), expected)
            self.assertEqual(Fraction(primary["raw_regret_benefit_by_size"]["6"]), expected * Fraction(4, 15))
            self.assertEqual(Fraction(primary["raw_regret_benefit_by_size"]["12"]), expected * Fraction(5, 33))
            self.assertTrue(all(Fraction(row["normalized_regret_benefit"]) == expected for row in primary["pairs"]))

    def test_failures_and_incomplete_cases_preserve_denominators_and_block_coverage(self):
        rows = rows_for(self.plan)
        changes = {(0, 6, "first"): "policy_failure", (1, 12, "last"): "transport_failure",
                   (2, 6, "first"): "incomplete"}
        for row in rows:
            key = row["block"], row["jobs"], row["refresh_rule"]
            if (key in changes and row["framing"] == "workflow" and row["guarantee"] == "unspecified"
                    and row["guidance"] == "generic"):
                row.update(status=changes[key], grade=None)
        summary = aggregate(rows)
        self.assertEqual(summary["status_counts"], {"completed": 1533, "policy_failure": 1,
                                                   "transport_failure": 1, "incomplete": 1})
        primary = summary["primary"]
        self.assertEqual(primary["scheduled_pairs"], 128)
        self.assertEqual(primary["valid_pairs"], 125)
        self.assertEqual(primary["transport_complete_pairs"], 126)
        self.assertEqual(primary["complete_blocks"], 29)
        self.assertEqual(primary["mean_normalized_regret_benefit"], "0")
        self.assertEqual(Fraction(primary["mean_valid_and_optimal_benefit"]), Fraction(1, 126))
        self.assertTrue(all(row["scheduled"] == 32 for row in summary["by_condition"]))
        self.assertEqual(sum(row["completed"] for row in summary["by_condition"]), 1533)
        self.assertEqual(sum(row["valid_and_optimal_denominator"] for row in summary["by_condition"]), 1534)
        self.assertEqual(sum(row["policy_failures"] for row in summary["by_condition"]), 1)
        self.assertEqual(sum(row["transport_failures"] for row in summary["by_condition"]), 1)
        self.assertEqual(sum(row["incomplete"] for row in summary["by_condition"]), 1)
        self.assertEqual({row["block"] for row in primary["block_effects"] if not row["complete"]}, {0, 1, 2})
        empty = aggregate([])["primary"]
        self.assertEqual((empty["scheduled_pairs"], empty["valid_pairs"], empty["complete_blocks"]), (128, 0, 0))
        self.assertIsNone(empty["mean_normalized_regret_benefit"])
        self.assertIsNone(empty["block_bootstrap_95_percent_interval"])

    def test_bootstrap_is_seeded_and_does_not_modify_values_or_global_randomness(self):
        values = [index / 31 for index in range(32)]
        original = list(values)
        state = random.getstate()
        observed = bootstrap_interval(values)
        self.assertEqual(observed, bootstrap_interval(values))
        self.assertEqual(values, original)
        self.assertEqual(random.getstate(), state)
        self.assertAlmostEqual(observed[0], float(Fraction(197, 496)))
        self.assertAlmostEqual(observed[1], float(Fraction(75, 124)))
        self.assertEqual(bootstrap_interval([0.25] * 32), [0.25, 0.25])
        self.assertIsNone(bootstrap_interval([]))
        self.assertIsNone(bootstrap_interval([0.5]))


if __name__ == "__main__":
    unittest.main()
