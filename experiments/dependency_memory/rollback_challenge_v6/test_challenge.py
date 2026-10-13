"""Scientific invariants, independent graders, failure accounting and real replay."""
from copy import deepcopy
import io
from contextlib import redirect_stdout
import itertools
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from .common import ROOT, FAMILIES, wire, sha, read, save_new
from .tasks import generate, public_check, candidate, run_program, ledger_answer
from .verification import verify_tasks, independent
from .contexts import render, actor_state
from .engine import run_episode
from .prepare import prepare, check_bundle, generation_bound, identities
from .statistics import mcnemar, power, plan, paired
from .analysis import select_screen, validate_selection, bounded_control_rate
from .runner import run, ScriptedTransport
from .audit import audit
from ..rollback_development_v5.engine import initial_state, apply_intervention
from ..rollback_development_v5_continuation.accounting import Ledger, CallUnknown
from ..rollback_development_v5.accounting import Stopped


class ChallengeTests(unittest.TestCase):
    def setUp(self):
        parent=ROOT/"tmp"/"rollback-v6-tests"; parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent)
        self.root=Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to(parent.resolve()))
    def tearDown(self): self.temp.cleanup()
    def tasks(self,**kwargs):
        return generate(split="fixture",replicates=1,stages=3,actions=5,**kwargs)

    def test_all_levels_have_independently_checked_witnesses(self):
        report=verify_tasks(self.tasks())
        self.assertEqual(len(report["tasks"]),9)
        self.assertEqual(report["candidate_checks"],9*3*32)
    def test_split_seeds_and_identities_are_disjoint(self):
        a=generate(split="screen",replicates=1); b=generate(split="confirmation",replicates=1)
        self.assertFalse({t["task_id"] for t in a}&{t["task_id"] for t in b})
        self.assertFalse({t["evaluator"]["seed"] for t in a}&{t["evaluator"]["seed"] for t in b})
        self.assertEqual(a,generate(split="screen",replicates=1))
    def test_independent_rotation_and_bit_operations_exhaustive_small_words(self):
        for width in (2,3,4):
            t={"family":"bitvector_program","contract":{"width":width,"max_instructions":1}}
            for op,k in itertools.product(range(4),range(2**width)):
                t["stages"]=[{"requirements":[{"x":x,"y":run_program([op,k],x,width)} for x in range(2**width)]}]
                self.assertTrue(independent(t,0,[op,k]))
    def test_ledger_revisions_are_replacements_and_voids_suppress(self):
        rows=[dict(kind="transaction",tx="a",revision=0,sequence=0,source=0,destination=1,amount=20,void=False),
              dict(kind="transaction",tx="a",revision=2,sequence=1,source=1,destination=0,amount=7,void=False),
              dict(kind="transaction",tx="a",revision=1,sequence=2,source=0,destination=1,amount=99,void=False)]
        self.assertEqual(ledger_answer(rows,2),[7,-7])
        rows.append({**rows[1],"sequence":3,"void":True})
        self.assertEqual(ledger_answer(rows,2),[0,0])
    def test_ledger_checks_intermediate_released_records_only(self):
        t=next(t for t in self.tasks() if t["family"]=="revision_ledger" and t["difficulty"]==3)
        for stage,r in enumerate(t["evaluator"]["stage_references"]):
            self.assertEqual(sum(r["values"]),0)
            self.assertEqual(public_check(t,stage,r)["status"],"public_pass")
    def test_private_witness_seed_and_future_packets_absent(self):
        for t in self.tasks():
            state=actor_state(t,initial_state(t)); serialized=wire(state)
            self.assertNotIn("evaluator",serialized)
            self.assertNotIn(str(t["evaluator"]["seed"]),serialized)
            future_id=t["stages"][-1]["requirements"][-1]["id"]
            self.assertNotIn(future_id,serialized)
            self.assertEqual(state["public_dossier"],[])
    def test_rollback_only_changes_history_in_matched_state(self):
        t=self.tasks()[0]; s=initial_state(t)
        s["history"]=[{"old_success":"kept in K"},{"failed_candidate":123}]
        s["feedback"]={"status":"public_mismatch"}
        lesson={"established":["Candidate failed"],"retained_observations":[],"uncertainties":[]}
        k=deepcopy(s); r=deepcopy(s)
        apply_intervention(k,"K",lesson); apply_intervention(r,"R",lesson)
        a,b=actor_state(t,k),actor_state(t,r)
        self.assertEqual(b["history"],[])
        self.assertEqual({k:v for k,v in a.items() if k!="history"},{k:v for k,v in b.items() if k!="history"})
    def test_fresh_control_has_all_released_packets_and_no_feedback(self):
        t=self.tasks()[0]; s=initial_state(t); s["stage"]=1; s["feedback"]={"status":"public_mismatch"}
        view=actor_state(t,s,"F")
        self.assertEqual(len(view["public_dossier"]),2); self.assertIsNone(view["feedback"])
    def test_candidates_cannot_submit_executable_code(self):
        t=self.tasks()[0]; c=deepcopy(t["evaluator"]["reference"]); c["files"]=[{"path":"engine.py","text":"raise Exception()"}]
        self.assertEqual(public_check(t,0,c)["status"],"invalid_candidate")
    def test_no_correct_answer_in_failure_receipt(self):
        t=self.tasks()[0]
        receipt=public_check(t,0,candidate([]))
        self.assertEqual(set(receipt),{"status","check","detail"})
    def test_writer_charged_and_no_writer_after_final_action(self):
        t=self.tasks(cells=[("constraint_grid",1)])[0]; calls=[]; transport=ScriptedTransport([t])
        def invoke(i,r): calls.append(i); return transport.generate(i,r)
        result=run_episode(t,"R",invoke)
        self.assertEqual(result["score"],1)
        self.assertEqual(len([i for i in calls if i.stage=="lesson"]),1)
        self.assertEqual(len(calls),result["actions_used"]+1)
        self.assertTrue(result["history_bytes_before_removal"])
    def test_unknown_scores_remain_missing(self):
        t=self.tasks()[0]
        def unknown(i,r): raise CallUnknown("fixture")
        result=run_episode(t,"R",unknown)
        self.assertIsNone(result["score"])
    def test_exact_mcnemar_known_values_and_symmetry(self):
        self.assertEqual(mcnemar(0,0),1)
        self.assertAlmostEqual(mcnemar(6,0),.03125)
        self.assertAlmostEqual(mcnemar(5,1),.21875)
        self.assertEqual(mcnemar(5,1),mcnemar(1,5))
    def test_power_matches_enumeration_when_all_pairs_discordant(self):
        expected=sum(.75**sum(b)*.25**(8-sum(b)) for b in itertools.product((0,1),repeat=8) if mcnemar(sum(b),8-sum(b))<=.05)
        self.assertAlmostEqual(power(8,.5,1),expected)
    def test_missingness_blocks_confirmatory_p_value(self):
        tasks=[{"task_id":str(i)} for i in range(7)]
        rows=[{"task_id":str(i),"arm":a,"score":1 if a=="R" else 0} for i in range(6) for a in ("K","R")]
        report=paired(rows,tasks,True)
        self.assertIsNone(report["confirmatory_p"])
        self.assertEqual(report["fixed_denominator_bounds"],[5/7,1])
    def test_budget_requires_complete_cohort_not_arbitrary_truncation(self):
        with self.assertRaises(ValueError): prepare(self.root/"too-large",max_calls=1)
        self.assertFalse((self.root/"too-large").exists())
    def test_screening_cannot_include_rollback(self):
        with self.assertRaises(ValueError): prepare(self.root/"biased",arms=["K","R"])
    def test_confirmation_needs_verified_selection_and_power(self):
        with self.assertRaises(ValueError): prepare(self.root/"unselected",split="confirmation")
    def test_invalid_designs_rejected(self):
        for kwargs in ({"stages":5,"actions":4},{"cells":[("no-family",1)]},{"replicates":0}):
            with self.assertRaises(ValueError): generate(**kwargs)
    def test_frozen_snapshot_detects_tampering(self):
        bundle=self.root/"bundle"; prepare(bundle,split="fixture",cells=[("constraint_grid",1)],replicates=1,stages=2,actions=4)
        t=read(bundle/"tasks.json"); t[0]["action_allowance"]+=1
        (bundle/"tasks.json").write_text(wire(t),encoding="utf-8")
        with self.assertRaises(ValueError): check_bundle(bundle)
    def test_ledger_preserves_unknown_and_allows_unrelated_calls(self):
        t=self.tasks(cells=[("constraint_grid",1)]); ids=identities(t,["K","R"])
        ledger=Ledger(self.root/"ledger.sqlite",ids,2,generation_ceiling=2)
        ledger.admit(ids[0],"hash"); ledger.unknown(ids[0],"fixture",fatal=False)
        self.assertFalse(ledger.stopped()); ledger.admit(ids[1],"hash")
        with self.assertRaises(Stopped): ledger.admit(ids[2],"hash")
        self.assertEqual(ledger.snapshot()["unknown_or_inflight_calls"],2)
    def test_real_files_parallel_simulation_and_independent_replay(self):
        bundle=self.root/"bundle"; output=self.root/"simulation"
        m=prepare(bundle,split="fixture",cells=[(f,1) for f in FAMILIES],replicates=1,stages=3,actions=5)
        with redirect_stdout(io.StringIO()): result=run(bundle,output,workers=4)
        self.assertEqual(result["model_calls"],0); self.assertIsNone(result["stop"])
        checked=audit(bundle,output)
        self.assertTrue(checked["all_passed"]); self.assertEqual(checked["jobs"],15)
        self.assertLessEqual(result["completed"],m["generation_ceiling"])
        self.assertIsNone(read(output/"analysis.json")["primary"]["confirmatory_p"])
        from .snapshot import audit_snapshot
        self.assertTrue(audit_snapshot(bundle,output)["all_passed"])
        with self.assertRaises(ValueError): run(bundle,self.root/"duplicate")
        with self.assertRaises(ValueError): run(bundle,self.root/"extended",prior=output)
    def test_global_stop_continuation_replays_receipts_without_retry(self):
        bundle=self.root/"bundle"; old=self.root/"stopped"; new=self.root/"continued"
        prepare(bundle,split="fixture",cells=[("constraint_grid",1)],replicates=1,stages=2,actions=4,arms=["K","R"])
        class FailsOnce(ScriptedTransport):
            calls=0
            def generate(self,identity,request):
                type(self).calls+=1
                if type(self).calls==3: raise RuntimeError("disclosed offline transport fixture")
                return super().generate(identity,request)
        with redirect_stdout(io.StringIO()),patch("experiments.dependency_memory.rollback_challenge_v6.runner.ScriptedTransport",FailsOnce):
            result=run(bundle,old,workers=1)
        self.assertIsNotNone(result["stop"]); self.assertTrue(audit(bundle,old)["all_passed"])
        old_rows=read(old/"analysis.json")["accounting"]["calls"]
        self.assertEqual(len(old_rows),3)
        with redirect_stdout(io.StringIO()): result=run(bundle,new,workers=1,prior=old)
        self.assertIsNone(result["stop"])
        checked=audit(bundle,new); self.assertTrue(checked["all_passed"]); self.assertEqual(checked["unknowns_preserved"],1)
        current={r["call_id"]:r for r in read(new/"analysis.json")["accounting"]["calls"]}
        for r in old_rows: self.assertEqual(current[r["call_id"]],r)
        self.assertTrue(audit(bundle,old)["all_passed"])
    def test_simulations_cannot_choose_live_difficulty(self):
        with self.assertRaises(ValueError): select_screen({"evidence_kind":"offline_scripted_fixture"},{"split":"screen"})
    def test_screening_rule_uses_controls_and_reports_no_suitable_cell(self):
        m={"split":"screen","arms":["K","F"],"seed":1,"actions":8,"stages":4}
        r={"evidence_kind":"observed_subscription_generations","control_cells":[]}
        cell={"family":"constraint_grid","level":2}
        for a in ("K","F"): cell[a]={"known":2,"scheduled":2,"success_rate":1.,"episodes_with_public_mismatch":1}
        r["control_cells"]=[cell]
        self.assertEqual(select_screen(r,m)["selected_cells"],[])
        for a in ("K","F"): cell[a]["success_rate"]=.5
        self.assertEqual(select_screen(r,m)["selected_cells"],[["constraint_grid",2]])
    def test_validation_never_drops_inconvenient_cells(self):
        screen={"selected_cells":[["constraint_grid",2],["revision_ledger",1]],"stages":4,"actions":8,"used_seeds":[1]}
        m={"split":"validation","arms":["K","F"],"seed":2,"actions":8,"stages":4,"cells":screen["selected_cells"]}
        cells=[]
        for f,l in screen["selected_cells"]:
            c={"family":f,"level":l}
            for a in ("K","F"): c[a]={"known":8,"scheduled":8,"success_rate":.5 if f=="constraint_grid" else 1.,"episodes_with_public_mismatch":4}
            cells.append(c)
        result=validate_selection(screen,{"evidence_kind":"observed_subscription_generations","control_cells":cells},m)
        self.assertFalse(result["ready_for_confirmation"])
        self.assertEqual(result["selected_cells"],screen["selected_cells"])

    def test_capacity_failures_do_not_establish_screening_difficulty(self):
        m={"split":"screen","arms":["K","F"],"seed":1,"actions":5,"stages":3}
        cell={"family":"revision_ledger","level":3}
        for arm in ("K","F"):
            cell[arm]={"known":2,"scheduled":2,"success_rate":.5,"episodes_with_public_mismatch":1,
                       "dispositions":{"correct":1,"action_budget_exhausted":1}}
        report={"evidence_kind":"observed_subscription_generations","control_cells":[cell]}
        self.assertEqual(select_screen(report,m)["selected_cells"],[["revision_ledger",3]])
        for arm in ("K","F"):
            limited=deepcopy(report)
            limited["control_cells"][0][arm]["dispositions"]={"correct":1,"context_capacity":1}
            result=select_screen(limited,m)
            self.assertEqual(result["selected_cells"],[])
            self.assertEqual(result["capacity_limited_cells"][0]["capacity_failures"][arm],1)
            # The failure and fixed denominator stay in the observed report.
            self.assertEqual(limited["control_cells"][0][arm]["known"],2)

    def test_capacity_failures_block_the_entire_validation_mixture(self):
        screen={"selected_cells":[["revision_ledger",3]],"stages":3,"actions":5,"used_seeds":[1]}
        m={"split":"validation","arms":["K","F"],"seed":2,"actions":5,"stages":3,"cells":screen["selected_cells"]}
        cell={"family":"revision_ledger","level":3}
        for arm in ("K","F"):
            cell[arm]={"known":8,"scheduled":8,"success_rate":.5,"episodes_with_public_mismatch":4,
                       "dispositions":{"correct":4,"action_budget_exhausted":4}}
        report={"evidence_kind":"observed_subscription_generations","control_cells":[cell]}
        self.assertTrue(validate_selection(screen,report,m)["ready_for_confirmation"])
        for arm in ("K","F"):
            limited=deepcopy(report)
            limited["control_cells"][0][arm]["dispositions"]={"correct":4,"action_budget_exhausted":3,"context_capacity":1}
            result=validate_selection(screen,limited,m)
            self.assertFalse(result["ready_for_confirmation"])
            self.assertEqual(result["selected_cells"],screen["selected_cells"])
            self.assertEqual(result["validation_checks"][0]["capacity_failures"][arm],1)

    def test_legacy_requests_stay_identical_and_candidate_mode_is_explicit(self):
        from ..rollback_development_v5.contexts import render as old_render, ACTION
        from ..rollback_pilot.subscription.profile import output_schema
        old=self.tasks(cells=[("constraint_grid",1)])[0]
        self.assertEqual(render(old,initial_state(old)),old_render(old,initial_state(old)))
        new=self.tasks(cells=[("constraint_grid",1)],require_candidates=True)[0]
        request=render(new,initial_state(new))
        self.assertEqual(output_schema(request)["properties"]["status"]["enum"],["candidate"])
        self.assertIn("best complete candidate",request.data()["messages"][0]["content"])
        self.assertIn("Do not intentionally make a wrong attempt",request.data()["messages"][0]["content"])
        self.assertEqual(ACTION["properties"]["status"]["enum"],["candidate","continue"])
        self.assertEqual(render(new,initial_state(new),"lesson"),old_render(new,initial_state(new),"lesson"))

    def test_response_modes_have_distinct_identities(self):
        old=self.tasks(); new=self.tasks(require_candidates=True)
        self.assertFalse({t["task_id"] for t in old}&{t["task_id"] for t in new})
        self.assertTrue(all(t["contract"]["require_candidates"] for t in new))
        self.assertTrue(all("require_candidates" not in t["contract"] for t in old))
        self.assertEqual(verify_tasks(new)["candidate_checks"],9*3*32)

    def test_deferral_is_rejected_only_in_the_required_candidate_contract(self):
        value={"status":"continue","candidate":candidate([]),"note":"Not yet solved."}
        def invoke(identity,request): return SimpleNamespace(text=wire(value),capped=False)
        old=self.tasks(cells=[("bitvector_program",1)])[0]
        new=self.tasks(cells=[("bitvector_program",1)],require_candidates=True)[0]
        a=run_episode(old,"K",invoke); b=run_episode(new,"K",invoke)
        self.assertEqual(a["disposition"],"action_budget_exhausted")
        self.assertEqual(a["actions_used"],5)
        self.assertEqual(b["disposition"],"invalid_record")
        self.assertEqual(b["actions_used"],1)
        self.assertEqual(b["score"],0)

    def test_candidate_contract_is_inherited_and_cannot_change_at_validation(self):
        screen={"selected_cells":[["bitvector_program",1]],"stages":3,"actions":5,
                "used_seeds":[1],"require_candidates":True}
        m={"split":"validation","arms":["K","F"],"seed":2,"stages":3,"actions":5,
           "cells":screen["selected_cells"],"require_candidates":False}
        with self.assertRaises(ValueError):
            validate_selection(screen,{"evidence_kind":"observed_subscription_generations","control_cells":[]},m)
        # Isolate design preservation; provenance itself is covered by the live
        # selection/replay tests and cannot be created by these fixtures.
        with patch("experiments.dependency_memory.rollback_challenge_v6.prepare.verify_selection"):
            manifest=prepare(self.root/"inherited",split="validation",seed=2,stages=3,actions=5,
                             replicates=8,selection=screen)
            self.assertTrue(manifest["require_candidates"])
            _,tasks=check_bundle(self.root/"inherited")
            self.assertTrue(all(t["contract"]["require_candidates"] for t in tasks))
            with self.assertRaises(ValueError):
                prepare(self.root/"changed-mode",split="validation",seed=2,stages=3,actions=5,
                        selection=screen,require_candidates=False)

    def test_candidate_mode_real_simulation_and_replay(self):
        bundle=self.root/"required"; output=self.root/"required-run"
        prepare(bundle,split="fixture",cells=[(f,1) for f in FAMILIES],replicates=1,
                stages=3,actions=5,arms=["K","F"],require_candidates=True)
        with redirect_stdout(io.StringIO()): result=run(bundle,output,workers=4)
        self.assertEqual(result["model_calls"],0)
        self.assertTrue(audit(bundle,output)["all_passed"])
        report=read(output/"analysis.json")
        self.assertTrue(all(c[a]["progress_only_actions"]==0 for c in report["control_cells"] for a in ("K","F")))
        self.assertTrue(all(c[a]["candidate_actions"]>=3 for c in report["control_cells"] for a in ("K","F")))

    def test_fresh_ceiling_mode_still_requires_retained_history_headroom(self):
        m={"split":"screen","arms":["K","F"],"seed":1,"actions":5,"stages":3}
        cell={"family":"revision_ledger","level":2,
              "K":{"known":4,"scheduled":4,"success_rate":.5,"episodes_with_public_mismatch":2},
              "F":{"known":4,"scheduled":4,"success_rate":1.,"episodes_with_public_mismatch":0}}
        report={"evidence_kind":"observed_subscription_generations","control_cells":[cell]}
        self.assertEqual(select_screen(report,m)["selected_cells"],[])
        m["allow_fresh_ceiling"]=True
        self.assertEqual(select_screen(report,m)["selected_cells"],[["revision_ledger",2]])
        for arm,key,value in (("K","success_rate",1.),("K","success_rate",0.),
                              ("F","success_rate",0.),("K","episodes_with_public_mismatch",0),
                              ("F","known",3),("K","dispositions",{"context_capacity":1})):
            with self.subTest(arm=arm,key=key,value=value):
                bad=deepcopy(report); bad["control_cells"][0][arm][key]=value
                self.assertEqual(select_screen(bad,m)["selected_cells"],[])

    def test_fresh_ceiling_validation_preserves_completeness_and_whole_mixture(self):
        screen={"selected_cells":[["revision_ledger",2],["bitvector_program",2]],
                "stages":3,"actions":5,"used_seeds":[1],"allow_fresh_ceiling":True}
        m={"split":"validation","arms":["K","F"],"seed":2,"stages":3,"actions":5,
           "cells":screen["selected_cells"],"allow_fresh_ceiling":True}
        cells=[{"family":f,"level":l,
                "K":{"known":16,"scheduled":16,"success_rate":.5,"episodes_with_public_mismatch":8},
                "F":{"known":16,"scheduled":16,"success_rate":1.,"episodes_with_public_mismatch":0}}
               for f,l in screen["selected_cells"]]
        report={"evidence_kind":"observed_subscription_generations","control_cells":cells}
        self.assertTrue(validate_selection(screen,report,m)["ready_for_confirmation"])
        for arm,key,value in (("K","success_rate",.8),("F","success_rate",.3),
                              ("F","known",15),("K","episodes_with_public_mismatch",3),
                              ("F","dispositions",{"context_capacity":1})):
            with self.subTest(arm=arm,key=key,value=value):
                bad=deepcopy(report); bad["control_cells"][1][arm][key]=value
                result=validate_selection(screen,bad,m)
                self.assertFalse(result["ready_for_confirmation"])
                self.assertEqual(result["selected_cells"],screen["selected_cells"])
        legacy_screen={**screen,"allow_fresh_ceiling":False}
        legacy_m={**m,"allow_fresh_ceiling":False}
        self.assertFalse(validate_selection(legacy_screen,report,legacy_m)["ready_for_confirmation"])
        with self.assertRaises(ValueError): validate_selection(screen,report,legacy_m)

    def test_calibration_rule_is_inherited_and_cannot_change_after_screening(self):
        screen={"selected_cells":[["revision_ledger",2]],"stages":3,"actions":5,
                "used_seeds":[1],"require_candidates":True,"allow_fresh_ceiling":True}
        with patch("experiments.dependency_memory.rollback_challenge_v6.prepare.verify_selection"):
            m=prepare(self.root/"gate-inherited",split="validation",seed=2,stages=3,actions=5,
                      replicates=8,selection=screen)
            self.assertTrue(m["allow_fresh_ceiling"])
            self.assertTrue(m["require_candidates"])
            with self.assertRaises(ValueError):
                prepare(self.root/"gate-changed",split="validation",seed=2,stages=3,actions=5,
                        replicates=8,selection=screen,allow_fresh_ceiling=False)
        with self.assertRaises(ValueError): prepare(self.root/"gate-invalid",allow_fresh_ceiling=1)

    def test_calibration_rule_does_not_change_actor_information(self):
        settings=dict(seed=19,cells=[("revision_ledger",2)],replicates=1,stages=3,actions=5,
                      require_candidates=True)
        prepare(self.root/"gate-old",**settings)
        prepare(self.root/"gate-new",allow_fresh_ceiling=True,**settings)
        _,old=check_bundle(self.root/"gate-old"); _,new=check_bundle(self.root/"gate-new")
        self.assertEqual(old,new)
        self.assertEqual(render(old[0],initial_state(old[0])),render(new[0],initial_state(new[0])))
        self.assertNotIn("allow_fresh_ceiling",wire(actor_state(new[0],initial_state(new[0]))))


    def test_missing_control_gate_matches_every_binary_completion(self):
        from fractions import Fraction
        for n in (8, 16, 17):
            for missing in range(4):
                for passed in range(n-missing+1):
                    cell={"scheduled":n,"known":n-missing,"passed":passed}
                    for lower,upper in ((.25,.85),(.4,.75),(.4,1.0)):
                        expected=missing<=n//8 and all(
                            Fraction(str(lower)) <= Fraction(passed+sum(v),n) <= Fraction(str(upper))
                            for v in itertools.product((0,1),repeat=missing))
                        self.assertEqual(bounded_control_rate(cell,lower,upper,8),expected)
        self.assertFalse(bounded_control_rate({"scheduled":8,"known":7,"passed":4},.4,.75,16))
        self.assertFalse(bounded_control_rate({"scheduled":8,"known":7,"passed":True},.4,.75,8))

    def test_robust_screen_never_fills_a_missing_score_favorably(self):
        m={"split":"screen","arms":["K","F"],"seed":1,"actions":5,"stages":3,
           "allow_fresh_ceiling":True,"robust_control_missingness":True}
        cell={"family":"revision_ledger","level":2,
              "K":{"known":7,"scheduled":8,"passed":4,"success_rate":4/7,"episodes_with_public_mismatch":4},
              "F":{"known":7,"scheduled":8,"passed":5,"success_rate":5/7,"episodes_with_public_mismatch":2}}
        report={"evidence_kind":"observed_subscription_generations","control_cells":[cell],"accounting":{"stop":None}}
        self.assertEqual(select_screen(report,m)["selected_cells"],[["revision_ledger",2]])
        self.assertEqual(select_screen(report,{**m,"robust_control_missingness":False})["selected_cells"],[])
        for arm,key,value in (("K","passed",1),("K","passed",7),("F","known",6),
                              ("K","episodes_with_public_mismatch",0),("K","dispositions",{"context_capacity":1})):
            bad=deepcopy(report); bad["control_cells"][0][arm][key]=value
            self.assertEqual(select_screen(bad,m)["selected_cells"],[])
        bad=deepcopy(report); bad["accounting"]["stop"]="unresolved source stop"
        self.assertEqual(select_screen(bad,m)["selected_cells"],[])
        self.assertEqual(report["control_cells"][0]["K"]["known"],7)

    def test_robust_validation_keeps_whole_mixture_and_scheduled_denominators(self):
        screen={"selected_cells":[["revision_ledger",1],["revision_ledger",2]],"stages":3,"actions":5,
                "used_seeds":[1],"robust_control_missingness":True,"allow_fresh_ceiling":True,
                "ledger_profile":"intermediate"}
        m={**screen,"split":"validation","arms":["K","F"],"seed":2,"cells":screen["selected_cells"]}
        cells=[{"family":f,"level":l,**{a:{"scheduled":16,"known":14,"passed":8,"success_rate":8/14,
                  "episodes_with_public_mismatch":4} for a in ("K","F")}} for f,l in screen["selected_cells"]]
        report={"evidence_kind":"observed_subscription_generations","control_cells":cells,"accounting":{"stop":None}}
        self.assertTrue(validate_selection(screen,report,m)["ready_for_confirmation"])
        for arm,key,value in (("K","passed",6),("K","passed",11),("F","passed",6),("F","known",13),
                              ("K","episodes_with_public_mismatch",3),("F","dispositions",{"context_capacity":1})):
            bad=deepcopy(report); bad["control_cells"][1][arm][key]=value
            selected=validate_selection(screen,bad,m)
            self.assertFalse(selected["ready_for_confirmation"])
            self.assertEqual(selected["selected_cells"],screen["selected_cells"])
        bad=deepcopy(report); bad["accounting"]["stop"]="systemic stop"
        self.assertFalse(validate_selection(screen,bad,m)["ready_for_confirmation"])
        bad=deepcopy(report)
        for a in ("K","F"): bad["control_cells"][0][a].update(scheduled=17,known=16)
        self.assertFalse(validate_selection(screen,bad,m)["ready_for_confirmation"])
        for field,value in (("robust_control_missingness",False),("ledger_profile","standard")):
            with self.assertRaises(ValueError): validate_selection(screen,report,{**m,field:value})

    def test_intermediate_ledger_is_disjoint_and_independently_checkable(self):
        settings=dict(cells=[("revision_ledger",v) for v in (1,2,3)],replicates=2,stages=3,actions=5)
        old=generate(**settings); explicit=generate(**settings,ledger_profile="standard")
        new=generate(**settings,ledger_profile="intermediate")
        self.assertEqual(old,explicit)
        self.assertFalse({t["task_id"] for t in old}&{t["task_id"] for t in new})
        self.assertEqual(verify_tasks(new)["candidate_checks"],6*3*32)
        for task in new:
            accounts,count=((5,22),(6,28),(7,34))[task["difficulty"]-1]
            self.assertEqual(task["contract"]["account_count"],accounts)
            self.assertEqual(len({r["tx"] for p in task["stages"] for r in p["requirements"]}),count)
        with self.assertRaises(ValueError): generate(ledger_profile="intermediate")

    def test_new_control_settings_are_frozen_inherited_and_not_actor_flags(self):
        screen={"selected_cells":[["revision_ledger",2]],"stages":3,"actions":5,"used_seeds":[1],
                "require_candidates":True,"allow_fresh_ceiling":True,"robust_control_missingness":True,
                "ledger_profile":"intermediate"}
        with patch("experiments.dependency_memory.rollback_challenge_v6.prepare.verify_selection"):
            m=prepare(self.root/"new-inherited",split="validation",seed=2,stages=3,actions=5,replicates=16,selection=screen)
            self.assertTrue(m["robust_control_missingness"]); self.assertEqual(m["ledger_profile"],"intermediate")
            for field,value in (("robust_control_missingness",False),("ledger_profile","standard")):
                with self.assertRaises(ValueError):
                    prepare(self.root/("changed-"+field),split="validation",seed=2,stages=3,actions=5,
                            replicates=16,selection=screen,**{field:value})
        for settings in ({"robust_control_missingness":1},{"ledger_profile":"unknown"},
                         {"robust_control_missingness":True,"replicates":7}):
            with self.assertRaises(ValueError): prepare(self.root/"invalid-new",**settings)
        settings=dict(seed=19,cells=[("revision_ledger",2)],replicates=8,stages=3,actions=5,
                      require_candidates=True,ledger_profile="intermediate")
        prepare(self.root/"missing-old",**settings)
        prepare(self.root/"missing-new",robust_control_missingness=True,**settings)
        _,old=check_bundle(self.root/"missing-old"); _,new=check_bundle(self.root/"missing-new")
        self.assertEqual(old,new)
        self.assertEqual(render(old[0],initial_state(old[0])),render(new[0],initial_state(new[0])))
        self.assertNotIn("robust_control_missingness",wire(actor_state(new[0],initial_state(new[0]))))


if __name__=="__main__": unittest.main()
