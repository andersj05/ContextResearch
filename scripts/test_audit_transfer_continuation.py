"""Synthetic complete evidence round trips; no account checks or model calls."""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

import audit_transfer_continuation as subject
from audit_transfer_run import digest, independent_grade
from prepare_transfer_continuation import certificate_from_evidence
import test_prepare_transfer_continuation as certificate_tests
from luna_appserver import LunaClient, ResponseFormatError
from luna_isolation import wire_body_byte_bound
from transfer_interface import validate_response
import transfer_study as study
import continue_transfer_study as runner


def quota(used=100, ordinary=False):
    return {"codex":{"ordinaryUsageAllowed":ordinary,"primary":{"usedPercent":used},"secondary":None,
        "rateLimitReachedType":None,"spendControlReached":False,"individualLimit":None,
        "credits":{"hasCredits":True,"unlimited":False,"balance":"1937.45"}}}


class CreditQuotaAuditTests(unittest.TestCase):
    def test_included_and_existing_credit_modes_are_distinct(self):
        self.assertEqual(subject.credit_quota_mode(quota(85,True)),"included")
        self.assertEqual(subject.credit_quota_mode(quota()),"existing_credits")
        self.assertEqual(subject.credit_quota_mode(quota(100,True)),"existing_credits")

    def test_unclassified_limits_unknown_credit_and_spend_controls_are_rejected(self):
        for mutation in ("balance","unknown","spend","individual","reached","nan","bucket"):
            value=quota()
            row=value["codex"]
            if mutation=="balance": row["credits"]["balance"]="0"
            elif mutation=="unknown": row["credits"].pop("unlimited")
            elif mutation=="spend": row["spendControlReached"]=True
            elif mutation=="individual": row["individualLimit"]={"remainingPercent":0}
            elif mutation=="reached":
                row.update(ordinaryUsageAllowed=True,primary={"usedPercent":85},rateLimitReachedType="rate_limit_reached")
            elif mutation=="nan": row["primary"]["usedPercent"]=float("nan")
            else: value={"other":row}
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                subject.credit_quota_mode(value)


class SyntheticLive(LunaClient):
    """Only writes synthetic usage to the real runner's in-memory budget."""
    def __init__(self,worker,plan,barrier,mode):
        self.worker=worker;self.barrier=barrier;self.mode=mode;self.calls=0
        self.budget=runner.ContinuationCreditBudget(plan["certificate"]["workers"][worker])
        self.audit={"launch_ready":True,"public_request_contract":runner.REQUEST_VERSION}
        self.credit_backed_quota=True;self.last_metadata={}
        advertised={"model":"gpt-5.6-luna"}
        self.metadata={"worker":worker,"model":"gpt-5.6-luna","provider":"luna_research",
            "experiment_version":runner.VERSION,"approved_plan_sha256":digest(plan),
            "approved_continuation_sha256":digest(plan),"approved_original_plan_sha256":digest(plan["original_plan"]),
            "source_sha256":plan["source_sha256"],"source_commit":"a"*40,
            "fingerprinted_sources_match_commit":True,"cli_sha256":"1"*64,
            "isolation_profile_sha256":"2"*64,"global_instructions_sha256":"3"*64,
            "advertised_model":advertised,"advertised_model_sha256":digest(advertised),
            "reasoning_effort":"low","service_tier":"default","http_and_stream_retries":0,
            "maximum_wire_body_bytes":32768,"credit_backed_quota":True,
            "quota_policy":"included_or_existing_credits","quota_guard_used_percent":100,
            "account_quota_stop_used_percent":100,"budget":self.budget.snapshot()}

    def complete(self,request):
        self.calls+=1
        self.last_metadata={"dispatched":False,"credit_backed_quota":True,
            "quota_policy":"included_or_existing_credits","quota_guard_used_percent":100}
        if self.calls>1:
            raise RuntimeError("synthetic preflight stop")
        with self.dispatch_gate:
            ticket=self.budget.reserve()
        meta=self.last_metadata
        meta.update(dispatched=True,attempt_ticket=ticket,thread_id=f"continuation-{self.worker}",
            wire_body_byte_bound=wire_body_byte_bound(request),quota_before=quota(),quota_before_mode="existing_credits")
        usage={"inputTokens":1200,"cachedInputTokens":200,"outputTokens":100,
               "reasoningOutputTokens":80,"totalTokens":1300}
        meta.update(usage={"input_tokens":1200,"cached_input_tokens":200,"output_tokens":100,
            "reasoning_output_tokens":80,"cache_write_input_tokens":None},
            credit_accounting=self.budget.settle(ticket,usage),harness_termination="session_budget_exceeded",
            status="completed",model="gpt-5.6-luna",provider="luna_research",tool_events_observed=0,
            provider_generation_count_observed=1,quota_after=quota(),quota_after_mode="existing_credits")
        self.barrier.wait(timeout=15)
        if self.mode=="post_quota":
            meta["status"]="failed"
            meta["quota_after"]["codex"]["credits"]["balance"]="0"
            meta["quota_after_mode"]="blocked"
            raise RuntimeError("synthetic post-generation quota stop")
        if self.mode=="malformed":
            meta["response_status"]="invalid_json"
            raise ResponseFormatError("synthetic invalid JSON")
        return study.FakeClient("optimal").complete(request)


class ContinuationEvidenceRoundtripTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        certificate_tests.ContinuationCertificateTests.setUpClass()

    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory=Path(self.temporary.name)/"phase"
        fixture=certificate_tests.ContinuationCertificateTests()
        # One already-dispatched quota failure must remain permanently failed.
        self.prior=fixture.phase(0,[(0,0,"post_quota",".2")])
        original=self.prior["manifest"]["plan"]
        for worker,evidence in enumerate(self.prior["workers"]):
            attempts={a["case_id"]:a for a in evidence["ledger"]}
            evidence["summary"]["rows"]=[]
            for case in original["cases"]:
                if case["worker"]!=worker:continue
                row={**{k:v for k,v in case.items() if k not in ("request","request_sha256")},
                     "status":"incomplete","grade":None,"displayed_positions":None}
                if case["case_id"] in attempts: row["status"]=attempts[case["case_id"]]["status"]
                evidence["summary"]["rows"].append(row)
        certificate=certificate_from_evidence([self.prior])
        self.plan={"version":runner.PLAN_VERSION,"original_plan":original,"certificate":certificate,
            "prior_run_dirs":[self.prior["run_directory"]],"source_sha256":dict(original["source_sha256"])}
        self.source_patch=patch.object(subject,"verify_source_commit",return_value={
            "source_commit":"a"*40,"source_blobs_checked":52,"source_hash_policy":"synthetic fixture"})
        self.load_patch=patch.object(subject,"load_phase",side_effect=lambda path:deepcopy(self.prior))
        self.source_patch.start();self.load_patch.start()
        self.addCleanup(self.source_patch.stop);self.addCleanup(self.load_patch.stop)

    def run_phase(self,mode="completed"):
        barrier=threading.Barrier(4)
        clients=[SyntheticLive(worker,self.plan,barrier,mode) for worker in range(4)]
        with patch.object(runner,"make_launch_plan",return_value=self.plan):
            runner.execute(self.plan,clients,output=self.directory,authorization="Synthetic usage fixture; no provider calls")

    def test_live_schema_roundtrip_keeps_prior_dispatched_failure(self):
        self.run_phase()
        pooled=subject.pool(self.directory,write=True)
        result=subject.audit(self.directory)
        self.assertEqual(result["model_requests"],4)
        self.assertEqual(result["pooled_model_requests"],5)
        self.assertEqual(Decimal(result["settled_credit_equivalent"]),Decimal(".042"))
        self.assertEqual(Decimal(result["pooled_settled_credit_equivalent"]),Decimal(".242"))
        prior_case=self.prior["workers"][0]["ledger"][0]["case_id"]
        row=next(r for r in pooled["rows"] if r["case_id"]==prior_case)
        self.assertEqual((row["status"],row["grade"]),("transport_failure",None))
        self.assertEqual(len(pooled["rows"]),1536)
        self.assertIn("phase-0",pooled["phase_by_case_id"].values())

    def test_metered_malformed_responses_remain_failures_without_imputation(self):
        self.run_phase("malformed")
        pooled=subject.pool(self.directory,write=True)
        result=subject.audit(self.directory)
        self.assertEqual(result["status_counts"]["policy_failure"],4)
        self.assertEqual(result["model_requests"],4)
        self.assertEqual(sum(r["status"]=="policy_failure" and r["grade"] is None for r in pooled["rows"]),4)

    def test_settled_post_quota_failure_counts_cost_but_has_no_grade(self):
        self.run_phase("post_quota")
        subject.pool(self.directory,write=True)
        result=subject.audit(self.directory)
        self.assertEqual(result["status_counts"]["transport_failure"],4)
        self.assertEqual(Decimal(result["settled_credit_equivalent"]),Decimal(".042"))
        self.assertEqual(result["retained_credit_equivalent"],"0")

    def test_pooled_grade_tampering_and_phase_retry_are_rejected(self):
        self.run_phase()
        subject.pool(self.directory,write=True)
        path=self.directory/"pooled_summary.json"
        value=json.loads(path.read_text())
        next(r for r in value["rows"] if r["status"]=="completed")["grade"]["availability"]="1"
        path.write_text(json.dumps(value),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"Pooled summary"):
            subject.audit(self.directory)
        checked=subject._checked_phase(self.directory)
        prior_attempt=deepcopy(self.prior["workers"][0]["ledger"][0])
        checked["workers"][0]["ledger"].append(prior_attempt)
        checked["workers"][0]["summary"]["rows"].append(self.prior["workers"][0]["summary"]["rows"][0])
        with self.assertRaisesRegex(ValueError,"cannot be replaced"):
            subject.pooled_summary(checked)

    def test_residual_initial_budget_cannot_reset_to_fifty(self):
        self.run_phase()
        checked=subject._checked_phase(self.directory)
        worker=checked["workers"][0]
        transport=deepcopy(worker["manifest"]["transport"])
        transport["budget"].update(cap_credit_equivalent=50.0,cap_credit_equivalent_exact="50")
        with self.assertRaisesRegex(ValueError,"cap_credit_equivalent"):
            subject.worker_accounting(worker["ledger"],worker["summary"],transport,
                self.plan["certificate"]["workers"][0],checked["manifest"],set())


if __name__=="__main__":
    unittest.main()
