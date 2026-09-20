"""Synthetic descriptive-summary invariants; never reads active model evidence."""
from copy import deepcopy
import unittest

import summarize_transfer_findings as subject
import transfer_study as study
from transfer_interface import validate_response


def row_for(case, selected):
    keys = validate_response({"keys":list(selected)},case["request"])
    positions = {item["key"]:index+1 for index,item in enumerate(case["request"]["visible_records"])}
    return {**{key:value for key,value in case.items() if key not in ("request","request_sha256")},
        "status":"completed","grade":study.grade(keys,case),
        "displayed_positions":[positions[key] for key in keys]}


class PatternOverlapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = next(case for case in study.make_plan()["cases"]
                        if case["jobs"] == 6 and case["refresh_rule"] == "first")

    def canonical_case(self, reverse=False):
        case = deepcopy(self.case)
        for index,item in enumerate(case["request"]["public_metadata"]["jobs"]):
            item["refresh_priority"] = 5-index if reverse else index
        return case

    def pattern_row(self, case, selected):
        row = row_for(case,selected)
        return {"patterns":subject.selection_patterns(row,case),
                "underfilled":row["grade"]["selected_count"] < 2}

    def test_extreme_names_and_opposite_priorities_can_overlap(self):
        low = self.pattern_row(self.canonical_case(),["job-00","job-01"])
        high = self.pattern_row(self.canonical_case(reverse=True),["job-04","job-05"])
        other = self.pattern_row(self.canonical_case(),["job-02","job-03"])
        underfilled = self.pattern_row(self.canonical_case(),["job-00"])
        result = subject.pattern_summary([low,high,other,underfilled])
        self.assertEqual(result["marginal_matches"],{
            "lowest_two_key_names":1,"highest_two_key_names":1,"opposite_refresh_optimum":2})
        self.assertEqual(result["intersection_matches"]["lowest_two_key_names & opposite_refresh_optimum"],1)
        self.assertEqual(result["intersection_matches"]["highest_two_key_names & opposite_refresh_optimum"],1)
        self.assertEqual((result["union_matches"],result["other_choices"],result["underfilled"]),(2,2,1))
        self.assertEqual(len(result["all_eight_boolean_signatures"]),8)
        self.assertEqual(sum(row["count"] for row in result["all_eight_boolean_signatures"]),4)
        self.assertGreater(sum(result["marginal_matches"].values()),result["union_matches"])

    def test_underfilled_extreme_key_is_not_a_whole_pair_match(self):
        case = self.canonical_case()
        row = row_for(case,["job-00"])
        self.assertFalse(any(subject.selection_patterns(row,case).values()))
        self.assertFalse(row["grade"]["optimal_parent"])

    def test_priority_pattern_uses_metadata_and_rejects_saved_rank_drift(self):
        case = self.canonical_case(reverse=True)
        row = row_for(case,["job-00","job-01"])
        patterns = subject.selection_patterns(row,case)
        self.assertTrue(patterns["lowest_two_key_names"])
        self.assertFalse(patterns["opposite_refresh_optimum"])
        row["grade"]["selected_priorities"] = [0,1]
        with self.assertRaisesRegex(ValueError,"original public metadata"):
            subject.selection_patterns(row,case)


class DescriptiveSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = study.make_plan()
        control = study.FakeClient("optimal")
        cls.rows = [row_for(case,control.complete(case["request"])["keys"]) for case in cls.plan["cases"]]

    def pooled(self,rows=None):
        rows = deepcopy(self.rows if rows is None else rows)
        return {"version":"transfer_pooled_phases_v1","fake":True,"rows":rows,**study.aggregate(rows)}

    def test_synthetic_optimal_control_has_48_conditions_and_128_primary_ties(self):
        pooled = self.pooled()
        with self.assertRaisesRegex(ValueError,"allow_fake"):
            subject.summarize(pooled,self.plan)
        result = subject.summarize(pooled,self.plan,allow_fake=True)
        self.assertEqual(result["overall"]["optimal"],1536)
        self.assertEqual(result["refresh_present"]["valid"],1024)
        self.assertEqual(result["no_refresh"]["valid"],512)
        self.assertEqual(len(result["all_48_condition_summaries"]),48)
        self.assertEqual(result["primary"]["paired_regret_counts"]["tie"],128)
        self.assertEqual(result["exploratory_suboptimal_patterns"]["all"]["strict_suboptimal_valid_choices"],0)
        self.assertEqual(result["new_model_requests"],0)

    def test_no_refresh_full_pairs_tie_and_underfills_are_visible(self):
        rows = deepcopy(self.rows)
        none_indices = [i for i,case in enumerate(self.plan["cases"]) if case["refresh_rule"] == "none"]
        i,j = none_indices[:2]
        keys = sorted(item["key"] for item in self.plan["cases"][i]["request"]["public_metadata"]["jobs"])
        rows[i] = row_for(self.plan["cases"][i],keys[2:4])
        rows[j] = row_for(self.plan["cases"][j],[])
        result = subject.summarize(self.pooled(rows),self.plan,allow_fake=True)
        self.assertEqual((result["no_refresh"]["optimal"],result["no_refresh"]["underfilled"]),(511,1))
        patterns = result["exploratory_suboptimal_patterns"]["all"]
        self.assertEqual((patterns["strict_suboptimal_valid_choices"],patterns["union_matches"],patterns["other_choices"]),(1,0,1))
        self.assertFalse(result["exploratory_suboptimal_patterns"]["cases"][0]["patterns"]["opposite_refresh_optimum"])

    def test_policy_and_transport_failures_keep_distinct_primary_denominators(self):
        rows = deepcopy(self.rows)
        generic = next(i for i,row in enumerate(rows) if row["block"] == 0 and row["jobs"] == 6
            and row["framing"] == "workflow" and row["guarantee"] == "unspecified"
            and row["refresh_rule"] == "first" and row["guidance"] == "generic")
        prospective = next(i for i,row in enumerate(rows) if row["block"] == 1 and row["jobs"] == 6
            and row["framing"] == "workflow" and row["guarantee"] == "unspecified"
            and row["refresh_rule"] == "first" and row["guidance"] == "prospective")
        rows[generic].update(status="policy_failure",grade=None,displayed_positions=None)
        rows[prospective].update(status="transport_failure",grade=None,displayed_positions=None)
        pooled = self.pooled(rows)
        result = subject.summarize(pooled,self.plan,allow_fake=True)
        primary = result["primary"]
        self.assertEqual(primary["arm_counts"]["generic"]["valid_and_optimal_denominator"],128)
        self.assertEqual(primary["arm_counts"]["prospective"]["valid_and_optimal_denominator"],127)
        self.assertEqual(primary["paired_regret_counts"]["not_both_valid"],2)
        self.assertEqual(primary["paired_valid_and_optimal_counts"]["not_both_transport_complete"],1)
        self.assertEqual(primary["paired_valid_and_optimal_counts"]["prospective_favored"],1)
        self.assertEqual(primary["frozen_estimates"]["raw_regret_benefit_by_size"],pooled["primary"]["raw_regret_benefit_by_size"])
        self.assertEqual(primary["frozen_estimates"]["block_bootstrap_95_percent_interval"],pooled["primary"]["block_bootstrap_95_percent_interval"])

    def test_frozen_endpoint_tampering_and_missing_original_rows_are_rejected(self):
        pooled = self.pooled()
        pooled["primary"]["raw_regret_benefit_by_size"]["6"] = "1"
        with self.assertRaisesRegex(ValueError,"does not reproduce"):
            subject.summarize(pooled,self.plan,allow_fake=True)
        pooled = self.pooled()
        pooled["rows"].pop()
        with self.assertRaisesRegex(ValueError,"1536 outcome denominators"):
            subject.summarize(pooled,self.plan,allow_fake=True)

    def test_summary_is_deterministic_for_identical_audited_inputs(self):
        pooled = self.pooled()
        self.assertEqual(subject.summarize(pooled,self.plan,allow_fake=True),
                         subject.summarize(pooled,self.plan,allow_fake=True))


if __name__ == "__main__":
    unittest.main()
