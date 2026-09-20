"""Audit residual first submissions and pool immutable transfer phases offline."""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))
import audit_transfer_run as base
from audit_transfer_run import require, digest, amount, independent_grade, usage_totals, verify_source_commit
from prepare_transfer_continuation import load_phase, certificate_from_evidence, public_schedule
from luna_appserver import strict_json
from luna_isolation import wire_body_byte_bound
from transfer_interface import request_bytes, validate_response
import transfer_study as study

VERSION = "transfer_continuation_run_v1"
RESERVATION = Decimal("10.4025")
STATUSES = ("completed", "policy_failure", "transport_failure", "reserved")


def load(path):
    return strict_json(Path(path).read_text(encoding="utf-8"))


def credit_quota_mode(snapshot):
    """Independent interpretation of the declared existing-credit admission rule."""
    require(type(snapshot) is dict and snapshot, "Missing credit-quota snapshot")
    observed, credit_path = False, False
    for name, row in snapshot.items():
        require(type(row) is dict and type(row.get("ordinaryUsageAllowed")) is bool,
                "Unusable ordinary-usage permission")
        require(row.get("rateLimitReachedType") in (None, "rate_limit_reached")
                and row.get("spendControlReached") is False, "Provider or account spend restriction")
        individual = row.get("individualLimit")
        if individual is not None:
            remaining = individual.get("remainingPercent") if type(individual) is dict else None
            require(type(remaining) in (int, float) and math.isfinite(remaining) and 0 < remaining <= 100,
                    "Individual allowance exhausted or unavailable")
        used = []
        for field in ("primary", "secondary"):
            window = row.get(field)
            if window is not None:
                value = window.get("usedPercent") if type(window) is dict else None
                require(type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 100,
                        "Invalid reported allowance window")
                used.append(value)
                observed = True
        ordinary = row["ordinaryUsageAllowed"]
        exhausted = not ordinary or any(value >= 100 for value in used)
        require(row.get("rateLimitReachedType") != "rate_limit_reached" or exhausted,
                "Unclassified account restriction cannot use credits")
        if ordinary and row.get("rateLimitReachedType") is None and all(value < 100 for value in used):
            continue
        require(exhausted and name == "codex" and used, "No observed exhausted Codex allowance")
        credits = row.get("credits")
        require(type(credits) is dict and credits.get("hasCredits") is True, "Existing credits unavailable")
        if credits.get("unlimited") is not True:
            require(credits.get("unlimited") is False and type(credits.get("balance")) is str,
                    "Credit balance is not measured")
            try:
                balance = Decimal(credits["balance"])
            except InvalidOperation as error:
                raise ValueError("Invalid existing credit balance") from error
            require(balance.is_finite() and balance > 0, "Existing credit balance exhausted")
        credit_path = True
    require(observed, "No observed allowance window")
    return "existing_credits" if credit_path else "included"


def residual_snapshot(snapshot, cap, limit, attempts, settled, failed, spent, uncertain):
    require(type(snapshot) is dict, "Missing residual budget snapshot")
    for name, expected in (("cap_credit_equivalent", cap), ("per_attempt_reservation", RESERVATION),
        ("settled_credit_equivalent", spent), ("uncertain_credit_reservations", uncertain),
        ("committed_credit_equivalent", spent + uncertain),
        ("remaining_credit_equivalent", cap - spent - uncertain)):
        amount(snapshot, name, expected)
    require(0 <= spent + uncertain <= cap <= 50, "Residual worker allocation exceeded")
    for name, expected in (("generation_attempt_ceiling", limit), ("generation_attempts", attempts),
        ("settled_attempts", settled), ("failed_attempts", failed), ("api_dollar_spend_authorized", 0),
        ("credit_purchases", 0), ("reset_redemptions", 0)):
        require(type(snapshot.get(name)) is int and snapshot[name] == expected, "Residual counter mismatch: " + name)
    require(snapshot.get("pending_ticket") is None and snapshot.get("stopped") is (failed > 0)
            and snapshot.get("api_key_fallback") is False, "Unsafe residual budget state")


def settled_charge(meta):
    usage, accounting = meta.get("usage", {}), meta["credit_accounting"]
    names = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")
    require(all(type(usage.get(key)) is int and usage[key] >= 0 for key in names), "Invalid settled token usage")
    inputs, cached, outputs, reasoning = (usage[key] for key in names)
    writes = usage.get("cache_write_input_tokens")
    require(writes is None or type(writes) is int and writes >= 0, "Invalid cache-write measurement")
    require(0 < inputs < 272000 and cached + (writes or 0) <= inputs
            and reasoning <= outputs <= 128000, "Settled usage outside envelope")
    require(accounting.get("usage") == {"inputTokens":inputs, "cachedInputTokens":cached,
        "cacheWriteInputTokens":writes, "outputTokens":outputs,
        "reasoningOutputTokens":reasoning, "totalTokens":inputs+outputs}, "Settlement usage differs from provider")
    require(accounting.get("cache_write_tokens_reported") is (writes is not None)
            and accounting.get("cache_write_pricing_unresolved") is (writes is None or writes > 0),
            "Unknown cache-write measurement was changed")
    actual = (Decimal(inputs)*Decimal("6.25") + Decimal(outputs)*30)/1000000
    basic = (Decimal(inputs-cached)*5 + Decimal(cached)/2 + Decimal(outputs)*30)/1000000
    amount(accounting,"conservative_credit_equivalent",actual)
    amount(accounting,"basic_rate_credit_estimate",basic)
    amount(accounting,"released_credit_equivalent",RESERVATION-actual)
    require(accounting.get("reasoning_already_in_output") is True
            and accounting.get("observed_credit_balance_debit") is None
            and accounting.get("observed_dollar_charge") is None, "Unsupported debit or double-counted reasoning")
    require(meta.get("harness_termination") == "session_budget_exceeded", "Missing one-generation guard")
    return actual


def worker_accounting(ledger, summary, transport, certificate, manifest, threads):
    worker = certificate["worker"]
    cap = Decimal(certificate["remaining_credit_equivalent_cap_exact"])
    limit = certificate["remaining_model_attempt_cap"]
    require(transport.get("worker") == worker and transport.get("experiment_version") == VERSION
            and transport.get("model") == "gpt-5.6-luna" and transport.get("provider") == "luna_research",
            "Unexpected continuation transport identity")
    require(transport.get("approved_plan_sha256") == transport.get("approved_continuation_sha256")
            == manifest["launch_plan_sha256"] and transport.get("approved_original_plan_sha256")
            == manifest["original_plan_sha256"], "Transport launch plan mismatch")
    require(transport.get("source_sha256") == manifest["source_sha256"]
            and transport.get("source_commit") == manifest["source_commit"]
            and transport.get("fingerprinted_sources_match_commit") is True, "Transport source provenance mismatch")
    base.hash_map({name:transport.get(name) for name in ("cli_sha256","isolation_profile_sha256",
        "global_instructions_sha256","advertised_model_sha256")})
    require(digest(transport.get("advertised_model")) == transport["advertised_model_sha256"], "Model catalog hash mismatch")
    require(transport.get("reasoning_effort") == "low" and transport.get("service_tier") == "default"
            and transport.get("http_and_stream_retries") == 0 and transport.get("maximum_wire_body_bytes") == 32768,
            "Continuation transport contract drift")
    require(transport.get("credit_backed_quota") is True and transport.get("quota_policy") == "included_or_existing_credits"
            and transport.get("quota_guard_used_percent") == transport.get("account_quota_stop_used_percent") == 100,
            "Undeclared existing-credit policy")
    residual_snapshot(transport.get("budget"),cap,limit,0,0,0,Decimal(0),Decimal(0))
    spent = uncertain = Decimal(0)
    attempts = settled = failed = 0
    for row in ledger:
        meta = row["provider_metadata"]
        if meta:
            require(meta.get("credit_backed_quota") is True and meta.get("quota_policy") == "included_or_existing_credits"
                    and meta.get("quota_guard_used_percent") == 100, "Attempt credit-quota policy differs")
        dispatched = meta.get("dispatched",False)
        require(type(dispatched) is bool, "Invalid dispatch flag")
        thread = meta.get("thread_id")
        if thread is not None:
            require(type(thread) is str and thread and thread not in threads, "Reused thread across phases")
            threads.add(thread)
        if not dispatched:
            require(row["status"] == "transport_failure" and not any(k in meta for k in
                ("attempt_ticket","credit_accounting","usage","turn_id")), "Preflight attempt was charged or generated")
            require(meta.get("dispatched") is False or not meta and row.get("error_type") == "StudyStopped",
                    "Ambiguous absent dispatch flag")
            continue
        require(thread is not None and not failed and spent+RESERVATION <= cap, "Dispatched outside residual reservation")
        require(meta.get("quota_before_mode") == credit_quota_mode(meta.get("quota_before")), "Preflight quota mode mismatch")
        attempts += 1
        require(meta.get("attempt_ticket") == attempts and attempts <= limit, "Residual ticket or attempt cap mismatch")
        require(meta.get("wire_body_byte_bound") == wire_body_byte_bound(strict_json(row["request_utf8"])) <= 32768,
                "Continuation wire-bound mismatch")
        account = meta.get("credit_accounting",{})
        require(type(account.get("ticket")) is int and account["ticket"] == attempts, "Settlement ticket mismatch")
        if account.get("status") == "settled":
            spent += settled_charge(meta)
            settled += 1
        else:
            require(account.get("status") == "reservation_retained" and row["status"] == "transport_failure",
                    "Dispatched attempt lacks settled or retained accounting")
            uncertain += RESERVATION
            failed += 1
        residual_snapshot(account.get("budget"),cap,limit,attempts,settled,failed,spent,uncertain)
        if row["status"] in ("completed","policy_failure"):
            require(account.get("status") == "settled" and meta.get("status") == "completed"
                    and meta.get("model") == "gpt-5.6-luna" and meta.get("provider") == "luna_research"
                    and type(meta.get("tool_events_observed")) is int and meta["tool_events_observed"] == 0
                    and type(meta.get("provider_generation_count_observed")) is int
                    and meta["provider_generation_count_observed"] == 1, "Unclean completed transport")
            require(meta.get("quota_after_mode") == credit_quota_mode(meta.get("quota_after")), "Post-generation quota mode mismatch")
    require(summary.get("model_requests") == attempts, "Worker dispatch total mismatch")
    residual_snapshot(summary.get("credit_budget"),cap,limit,attempts,settled,failed,spent,uncertain)
    return spent,uncertain


def _checked_phase(directory, *, allow_fake=False):
    directory = Path(directory).resolve()
    manifest, summary = load(directory/"manifest.json"),load(directory/"summary.json")
    require(manifest.get("version") == summary.get("version") == VERSION, "Unexpected continuation evidence version")
    require(digest(manifest) == summary.get("manifest_sha256"), "Continuation manifest hash mismatch")
    fake = manifest.get("fake")
    require(type(fake) is bool and summary.get("fake") is fake and (not fake or allow_fake), "Fake continuation requires allow_fake")
    prior_dirs = [ROOT/Path(path) for path in manifest["prior_run_dirs"]]
    require(len(set(path.resolve() for path in prior_dirs)) == len(prior_dirs) and directory not in prior_dirs,
            "Duplicate/circular prior phases")
    phases = [load_phase(path) for path in prior_dirs]
    certificate = certificate_from_evidence(phases)
    require(certificate == manifest.get("certificate") and digest(certificate) == manifest.get("certificate_sha256"),
            "Continuation certificate differs from freshly audited prior evidence")
    original = manifest["original_plan"]
    require(digest(original) == manifest.get("original_plan_sha256")
            and public_schedule(original) == public_schedule(phases[0]["manifest"]["plan"]), "Original public plan mismatch")
    launch = {"version":"transfer_continuation_launch_v1", "original_plan":original,
        "certificate":certificate, "prior_run_dirs":manifest["prior_run_dirs"], "source_sha256":manifest["source_sha256"]}
    require(digest(launch) == manifest.get("launch_plan_sha256"), "Frozen continuation launch hash mismatch")
    provenance = {"source_hash_policy":"format only for explicitly allowed fake continuation"}
    base.hash_map(manifest["source_sha256"])
    if not fake:
        require(manifest.get("fingerprinted_sources_match_commit") is True
                and type(manifest.get("authorization")) is str and manifest["authorization"].strip(), "Missing continuation provenance or allocation note")
        provenance = verify_source_commit(manifest["source_sha256"],manifest.get("source_commit"))
    cap = certificate["remaining_model_attempt_cap"]
    require(manifest.get("worker_count") == 4 and manifest.get("request_cap") == summary.get("request_cap") == cap
            and manifest.get("credit_equivalent_cap_exact") == certificate["remaining_credit_equivalent_cap_exact"]
            and manifest.get("heldout_requests") == summary.get("heldout_requests") == 0, "Residual aggregate allocation mismatch")
    eligible = {key for worker in certificate["workers"] for key in worker["eligible_case_ids"]}
    cases = [case for case in original["cases"] if case["case_id"] in eligible]
    threads = {a["provider_metadata"]["thread_id"] for phase in phases for worker in phase["workers"]
               for a in worker["ledger"] if a["provider_metadata"].get("thread_id")}
    workers, all_attempts, row_map = [],[],{}
    spent = uncertain = Decimal(0)
    for worker in range(4):
        folder=directory/f"worker-{worker}"
        wm,ledger,ws=(load(folder/name) for name in ("manifest.json","requests.json","summary.json"))
        wc=certificate["workers"][worker]
        own=[case for case in cases if case["worker"]==worker]
        require([c["case_id"] for c in own]==wc["eligible_case_ids"], "Eligible worker order changed")
        require(wm.get("version")==ws.get("version")=="transfer_study_v1" and wm.get("phase_version")==VERSION
                and wm.get("worker")==ws.get("worker")==worker and wm.get("fake") is ws.get("fake") is fake,
                "Continuation worker identity mismatch")
        require(wm.get("aggregate_manifest_sha256")==digest(manifest) and wm.get("original_plan_sha256")==digest(original)
                and wm.get("cases")==own and wm.get("request_cap")==ws.get("request_cap")==len(own)
                and wm.get("credit_equivalent_cap_exact")==wc["remaining_credit_equivalent_cap_exact"], "Worker certificate allocation mismatch")
        require(digest(wm)==ws.get("manifest_sha256") and digest(ledger)==ws.get("request_audit_sha256"), "Worker evidence hash mismatch")
        require(wm.get("heldout_requests")==ws.get("heldout_requests")==0 and len(ledger)<=len(own)
                and ws.get("request_attempts")==len(ledger) and len(ws.get("rows",[]))==ws.get("planned_cases")==len(own),
                "All residual denominators must be retained")
        stopped=False
        for index,(case,row) in enumerate(zip(own,ws["rows"])):
            expected={k:v for k,v in case.items() if k not in ("request","request_sha256")}
            require({k:row.get(k) for k in expected}==expected, "Residual row case identity mismatch")
            row_map[case["case_id"]]=row
            if index>=len(ledger):
                require(row.get("status")=="incomplete" and row.get("grade") is None and row.get("displayed_positions") is None,
                        "Unattempted continuation case imputed")
                continue
            require(not stopped, "Worker continued after transport failure")
            attempt=ledger[index]
            require(attempt.get("attempt")==index+1 and attempt.get("case_id")==case["case_id"]
                    and attempt.get("worker")==worker and attempt.get("block")==case["block"], "Residual attempt order mismatch")
            raw=attempt["request_utf8"].encode("utf-8")
            require(raw==request_bytes(case["request"]) and hashlib.sha256(raw).hexdigest()==attempt.get("request_sha256")==case["request_sha256"]
                    and len(raw)==attempt.get("request_bytes")==case["request_bytes"], "Continuation public bytes changed")
            status=attempt.get("status")
            require(status in STATUSES[:3] and row.get("status")==status and type(attempt.get("provider_metadata")) is dict,
                    "Unfinished or invalid continuation attempt")
            latency=attempt.get("latency_seconds")
            require(latency is None if fake else type(latency) in (int,float) and latency>=0, "Missing attempt latency")
            if status=="transport_failure":
                stopped=True
                require(attempt.get("response") is None, "Failed transport contains accepted response")
            else:
                try:
                    keys=validate_response(attempt.get("response"),case["request"])
                except (ValueError,TypeError,KeyError):
                    require(status=="policy_failure", "Invalid response marked complete")
                else:
                    require(status=="completed" and row.get("grade")==independent_grade(keys,case), "Independent residual route grade mismatch")
                    positions={r["key"]:i+1 for i,r in enumerate(case["request"]["visible_records"])}
                    require(row.get("displayed_positions")==[positions[k] for k in keys], "Residual displayed positions mismatch")
            if status!="completed":
                require(row.get("grade") is None and row.get("displayed_positions") is None
                        and type(attempt.get("error_type")) is str, "Residual failure was imputed")
                if not fake and attempt["error_type"]=="ResponseFormatError":
                    meta=attempt["provider_metadata"]
                    require(status=="policy_failure" and attempt.get("response") is None
                            and meta.get("response_status")=="invalid_json"
                            and meta.get("credit_accounting",{}).get("status")=="settled", "Malformed metered answer lost")
        require(len(ledger)==len(own) or summary.get("shared_stop") is True, "Unexplained continuation stop")
        require(ws.get("attempt_status_counts")=={s:sum(a["status"]==s for a in ledger) for s in STATUSES}
                and ws.get("usage_totals")==usage_totals(ledger), "Residual worker totals mismatch")
        if fake:
            require(ws.get("model_requests")==0 and all(not a["provider_metadata"] for a in ledger), "Fake continuation has provider activity")
        else:
            require(wm.get("source_commit")==manifest["source_commit"] and wm.get("authorization")==manifest["authorization"]
                    and wm.get("transport")==ws.get("transport_manifest")==manifest["worker_transports"][worker], "Worker transport manifest mismatch")
            a,b=worker_accounting(ledger,ws,wm["transport"],wc,manifest,threads)
            spent+=a; uncertain+=b
        workers.append({"manifest":wm,"summary":ws,"ledger":ledger})
        all_attempts.extend(ledger)
    require(summary.get("worker_summaries")==[w["summary"] for w in workers]
            and summary.get("rows")==[row_map[c["case_id"]] for c in cases]
            and summary.get("planned_cases")==len(cases), "Aggregate residual rows differ from workers")
    counts={s:sum(a["status"]==s for a in all_attempts) for s in STATUSES}
    model_calls=sum(w["summary"]["model_requests"] for w in workers)
    require(summary.get("attempt_status_counts")==counts and summary.get("request_attempts")==len(all_attempts)
            and summary.get("model_requests")==model_calls and summary.get("usage_totals")==usage_totals(all_attempts), "Aggregate residual totals mismatch")
    require(type(summary.get("shared_stop")) is bool and summary["shared_stop"] is (counts["transport_failure"]>0), "Continuation shared-stop mismatch")
    for key,value in study.aggregate(summary["rows"]).items():
        require(summary.get(key)==value, "Continuation analysis mismatch: "+key)
    if not fake:
        for name,value in (("cap_credit_equivalent",Decimal(certificate["remaining_credit_equivalent_cap_exact"])),
            ("settled_credit_equivalent",spent),("uncertain_credit_reservations",uncertain),
            ("committed_credit_equivalent",spent+uncertain),
            ("remaining_credit_equivalent",Decimal(certificate["remaining_credit_equivalent_cap_exact"])-spent-uncertain)):
            amount(summary.get("credit_budget",{}),name,value)
    result={"version":"transfer_continuation_evidence_audit_v1","passed":True,"fake":fake,
        "requests_checked":len(all_attempts),"model_requests":model_calls,"scheduled_remaining_cases":len(cases),
        "settled_credit_equivalent":str(spent),"retained_credit_equivalent":str(uncertain),
        "manifest_sha256":digest(manifest),"summary_sha256":digest(summary),"status_counts":counts,
        "new_model_requests":0,**provenance}
    return {"directory":directory,"manifest":manifest,"summary":summary,"workers":workers,
            "prior_phases":phases,"audit":result}


def pooled_summary(checked):
    """Select the sole dispatched outcome per original case, never a replacement."""
    manifest=checked["manifest"]
    original=manifest["original_plan"]
    canonical={c["case_id"]:{**{k:v for k,v in c.items() if k not in ("request","request_sha256")},
        "status":"incomplete","grade":None,"displayed_positions":None} for c in original["cases"]}
    selected,phase_by_case,attempt_log={}, {key:"unattempted" for key in canonical}, []
    phases=[*checked["prior_phases"],{"run_directory":str(checked["directory"]),"manifest":manifest,
                                     "workers":checked["workers"],"audit":checked["audit"]}]
    all_attempts=[]
    for index,phase in enumerate(phases):
        label=f"phase-{index}"
        fake=phase["manifest"].get("fake",False)
        for worker in phase["workers"]:
            rows={r["case_id"]:r for r in worker["summary"]["rows"]}
            for attempt in worker["ledger"]:
                case_id=attempt["case_id"]
                dispatched=attempt["provider_metadata"].get("dispatched",False)
                fake_outcome=fake and attempt["status"] in ("completed","policy_failure")
                require(case_id in canonical, "Unknown case during pooling")
                if dispatched or fake_outcome:
                    require(case_id not in selected, "Dispatched case cannot be replaced during pooling")
                    selected[case_id]=label
                    canonical[case_id]=rows[case_id]
                    phase_by_case[case_id]=label
                elif case_id not in selected:
                    canonical[case_id]=rows[case_id]
                    phase_by_case[case_id]=label
                attempt_log.append({"phase":label,"case_id":case_id,"worker":attempt["worker"],
                    "attempt":attempt["attempt"],"status":attempt["status"],"dispatched":dispatched,
                    "request_sha256":attempt["request_sha256"]})
                all_attempts.append(attempt)
    rows=[canonical[c["case_id"]] for c in original["cases"]]
    calls=sum(phase["audit"]["model_requests"] for phase in phases)
    spent=sum((Decimal(phase["audit"]["settled_credit_equivalent"]) for phase in phases),Decimal(0))
    uncertain=sum((Decimal(phase["audit"]["retained_credit_equivalent"]) for phase in phases),Decimal(0))
    require(calls<=1536 and spent+uncertain<=200, "Pooled original allocation exceeded")
    budget={}
    for name,value in (("cap_credit_equivalent",Decimal(200)),("settled_credit_equivalent",spent),
        ("uncertain_credit_reservations",uncertain),("committed_credit_equivalent",spent+uncertain),
        ("remaining_credit_equivalent",Decimal(200)-spent-uncertain)):
        budget[name]=float(value);budget[name+"_exact"]=str(value)
    return {"version":"transfer_pooled_phases_v1","fake":manifest["fake"],"planned_cases":1536,
        "request_cap":1536,"request_attempts":len(all_attempts),"model_requests":calls,"heldout_requests":0,
        "continuation_manifest_sha256":digest(manifest),"rows":rows,"phase_by_case_id":phase_by_case,
        "attempt_provenance":attempt_log,"attempt_status_counts":{s:sum(a["status"]==s for a in all_attempts) for s in STATUSES},
        "usage_totals":usage_totals(all_attempts),"credit_budget":budget,
        "phases":[{"phase":f"phase-{i}","manifest_sha256":digest(p["manifest"]),
                    "source_commit":p["manifest"].get("source_commit"),"model_requests":p["audit"]["model_requests"]}
                  for i,p in enumerate(phases)],
        "pooling_rule":"Keep the sole dispatched outcome, including failures. Earlier preflight attempts remain in attempt_provenance. Missing outcomes are not replaced.",
        **study.aggregate(rows)}


def pool(directory, prior_dirs=None, *, write=False, allow_fake=False):
    checked=_checked_phase(directory,allow_fake=allow_fake)
    if prior_dirs is not None:
        require([Path(p).resolve() for p in prior_dirs]==[(ROOT/p).resolve() for p in checked["manifest"]["prior_run_dirs"]],
                "Caller prior directories differ from frozen manifest")
    pooled=pooled_summary(checked)
    if write:
        for name,value in (("pooled_summary.json",json.dumps(pooled,indent=2,sort_keys=True)+"\n"),
                           ("report.md",study.report(pooled))):
            path=Path(directory)/name
            if path.exists():
                require(path.read_text(encoding="utf-8")==value, "Refuse to overwrite different pooled evidence")
            else:
                path.write_text(value,encoding="utf-8",newline="\n")
    return pooled


def audit(directory, *, allow_fake=False):
    checked=_checked_phase(directory,allow_fake=allow_fake)
    expected=pooled_summary(checked)
    require(load(Path(directory)/"pooled_summary.json")==expected, "Pooled summary differs from immutable phase evidence")
    require((Path(directory)/"report.md").read_text(encoding="utf-8")==study.report(expected), "Pooled report mismatch")
    return {**checked["audit"],"pooled_model_requests":expected["model_requests"],
        "pooled_host_attempts":expected["request_attempts"],"pooled_status_counts":expected["status_counts"],
        "pooled_summary_sha256":digest(expected),"pooled_settled_credit_equivalent":expected["credit_budget"]["settled_credit_equivalent_exact"],
        "limitations":"Local evidence consistency, not provider-internal or invoice certification. Execution phase and missing outcomes remain explicit."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir",type=Path,required=True)
    parser.add_argument("--allow-fake",action="store_true")
    parser.add_argument("--write-pooled",action="store_true")
    args=parser.parse_args()
    if args.write_pooled:
        result=pool(args.run_dir,write=True,allow_fake=args.allow_fake)
        print(json.dumps({"written":True,"pooled_model_requests":result["model_requests"],
            "pooled_host_attempts":result["request_attempts"],"new_model_requests":0}))
    else:
        print(json.dumps(audit(args.run_dir,allow_fake=args.allow_fake),indent=2))


if __name__=="__main__":
    main()
