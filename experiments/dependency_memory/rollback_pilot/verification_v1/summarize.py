"""Build the final stage-separated result summary without dispatching models."""
import argparse
from decimal import Decimal
from pathlib import Path

from ..controller import write_new
from ..records import digest, wire
from ..cohort_v1.run import read
from ..subscription.accounting import RATES


def summarize(folder):
    folder=Path(folder)
    calibration=read(folder/"calibration_v1/summary.json")
    stages=[]
    e1_usage={key:sum(r["usage"][key] for r in calibration["results"] if "usage" in r)
              for key in ("input_tokens","cached_input","output","reasoning")}
    stages.append({"stage":"E1 calibration","completed_generations":8,"selected_study_tasks":0,"usage":e1_usage,
                   "planning_credits":calibration["accounting"]["completed_credits"],"format_valid":calibration["known_format_valid"],
                   "unknown_or_unperformed":calibration["unknown_or_unperformed"]})
    for name,label in (("pilot_authored_v1","instruction-gap engineering run"),("pilot_python_v2","corrected Python-language engineering retest")):
        result=read(folder/name/"analysis.json")
        resources=result["resources"]
        stages.append({"stage":label,"folder":name,"selected_study_tasks":24,"completed_generations":resources["known_completed_calls"],
                       "usage":resources["usage"],"planning_credits":resources["shared_experiment_planning_credits"],
                       "unknown_or_pending":resources["unknown_or_pending_calls"],
                       "domains":{domain:{"selected_tasks":r["selected_tasks"],"initial_correct":r["initial_candidates_correct"],
                           "initial_reserved_failures":r["initial_candidates_failed_reserved_grading"],"flow_counts":r["flow_event_counts"],
                           "public_failure_tasks":r["public_failure_tasks"],"primary_R_minus_K":r["primary_R_minus_K"],
                           "conditions":r["conditions"],"feasibility_screen_passed":r["feasibility_screen_at_least_six_primary_tasks"]}
                           for domain,r in result["domains"].items()},
                       "archive_manifest_sha256":digest((folder/name/"evidence_manifest.json").read_bytes())})
    tests=read(folder/"final_repository_checks.json")
    validation=read(folder/"repository_validation.json")
    archive_probes=[read(folder/name) for name in ("archive_checks_v1.json","archive_checks_v2.json")]
    rechecks=[read(folder/name) for name in ("verification_pilot_v1.json","verification_pilot_v2.json")]
    if not tests["successful"] or tests["skipped"] or validation["result"]["status"]!="PASS" or not all(x["successful"] for x in archive_probes):
        raise ValueError("required implementation checks did not all pass")
    if not all(x["regraded_in_Docker"] for x in rechecks):
        raise ValueError("both preserved runs require independent isolated regrading")
    combined={key:sum(x["usage"][key] for x in stages) for key in e1_usage}
    credits=sum((Decimal(x["planning_credits"]) for x in stages),Decimal(0))
    independently_priced=((combined["input_tokens"]-combined["cached_input"])*RATES["uncached_input"]
                          +combined["cached_input"]*RATES["cached_input"]+combined["output"]*RATES["output"])/1000000
    if credits!=independently_priced:
        raise ValueError("stage costs disagree with independently priced combined token buckets")
    result={"version":"rollback-subscription-final-summary-1","as_of":"2026-10-08","scope":"implementation, calibration and same-cohort engineering retests",
            "model":"gpt-6-luna","reasoning_effort":"medium","transport":"official Codex app-server, existing ChatGPT subscription",
            "stages":stages,"total_completed_generations":sum(x["completed_generations"] for x in stages),
            "combined_usage":combined,
            "combined_calculated_planning_credits":str(credits),
            "actual_account_charge":None,"API_model_calls":0,"API_spend_USD":"0",
            "unique_study_tasks":24,"independent_cohorts":1,"retest_is_confirmation":False,"LiveCodeBench_v02_performed":False,
            "checks":{"current_repository_tests":tests["tests_run"],"passed":tests["passed"],"failures":tests["failures"],
                      "errors":tests["errors"],"skipped":tests["skipped"],"installed_client_mock_probes":10,
                      "reference_retained_tests_per_version":156,"archive_probes_per_version":[x["tests_run"] for x in archive_probes],
                      "both_runs_independently_regraded":True,"scientific_repository_validation":"PASS","paper_cited_sources":48},
            "limits":["No immutable server model revision or provider sampling seed available.",
                      "No configurable 16384 output-token cap established; provider-default output and conditional envelope disclosed.",
                      "Constructed math and original coding tasks; structural strata are not benchmark difficulty ratings.",
                      "Version 1 omitted the Python language requirement; corrected version 2 retests the same tasks after observation.",
                      "Planning credits are calculated usage, not actual account charges.",
                      "Recovery comparisons apply only to eligible tasks; zero paired tasks leaves the contrast unidentified."],
            "paper_claims_upgraded":False,"later_E3_E4_E5_performed":False}
    write_new(folder/"summary.json",wire(result)+"\n")
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder",type=Path,required=True)
    result=summarize(parser.parse_args().folder)
    print(wire({k:result[k] for k in ("total_completed_generations","combined_calculated_planning_credits","unique_study_tasks","checks")}))
