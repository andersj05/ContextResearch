"""Access, recovery-flow and accounting invariants for the subscription E2 adapter."""
from decimal import Decimal
import io
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from ..accounting import Identity
from ..fixtures import math_example
from ..records import InterfaceError, strict_loads, wire
from ..schedule import task_slots
from ..test_controller import fixture_script
from ..transport import UnknownDispatch
from ..subscription.accounting import Usage
from ..subscription.profile import Renderer
from ..subscription.transport import Response
from .analysis import analyze
from .authored import generate, case
from .controller import Controller
from .run import cohort, schedule, slot_dispositions


class StubTransport:
    def __init__(self, overrides=None, unknown=False):
        self.script=fixture_script(overrides)
        self.calls=[]
        self.unknown=unknown

    def generate(self, identity, request):
        self.calls.append((identity,request))
        if self.unknown:
            raise UnknownDispatch("scripted ambiguous dispatch")
        return Response(self.script(identity,request),Usage(1000,0,200,100),{})


class CohortTests(unittest.TestCase):
    def run_case(self, overrides=None, unknown=False, capacity=False):
        task,evaluator,*_=math_example()
        root=Path(__file__).resolve().parents[4]/"tmp"/"rollback_cohort_tests"
        root.mkdir(parents=True,exist_ok=True)
        temporary=tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(temporary.cleanup)
        manifest={"launch_id":"offline-unit-only","task_ids":[task.task_id],
                  "schedule":[vars(x) for x in task_slots("offline-unit-only",task,0)],"source_bindings":[]}
        transport=StubTransport(overrides,unknown)
        controller=Controller(temporary.name,manifest,transport,SimpleNamespace(grades=[]))
        self.addCleanup(controller.ledger.close)
        if capacity:
            normal=controller.renderer.fits
            def fits(request):
                context=strict_loads(request.data()["messages"][1]["content"])
                return normal(request) and not (request.stage=="terminal" and context["trial"])
            controller.renderer.fits=fits
        with redirect_stdout(io.StringIO()):
            rows=controller.run([(task,evaluator)])
        return controller,transport,rows,manifest

    def test_original_tasks_have_distinct_private_material_and_complete_strata(self):
        pairs=generate()
        self.assertEqual(len(pairs),12)
        self.assertEqual(len({t.task_id for t,e in pairs}),12)
        for level in ("easy","medium","hard"):
            self.assertEqual(sum(t.stratum==level for t,e in pairs),4)
        for task,evaluator in pairs:
            evaluator.check_binding(task)
            data=evaluator.data()
            request=Renderer().render("checkpoint",task).json_text
            self.assertEqual(len(task.data()["public_examples"]),2)
            self.assertEqual(len(data["private_tests"]),11)
            for secret in (data["reference_code"],data["private_tests_sha256"],data["reference_sha256"]):
                self.assertNotIn(secret,request)
            self.assertNotIn("reserved-stress",request)
            self.assertIn("Not LiveCodeBench",data["benchmark_claim"])

    def test_task_construction_order_and_all_slots_are_frozen_without_sampling_claim(self):
        first,second=cohort(),cohort()
        self.assertEqual([(t.hash,e.material_json) for t,e in first],[(t.hash,e.material_json) for t,e in second])
        self.assertEqual([t.domain for t,e in first],["math","coding"]*12)
        planned=schedule([t for t,e in first],"unit-allocation")
        self.assertEqual(len(planned),312)
        self.assertEqual(len({Identity(**x).key for x in planned}),312)
        self.assertFalse(any("calibration" in t.task_id for t,e in first))

    def test_independent_singleton_oracles_include_impossible_brackets_and_empty_cover(self):
        self.assertEqual(case("runs",41,1)[1],"1\n")
        self.assertEqual(case("treecover",41,1)[1],"0\n")
        self.assertEqual(case("bottleneck",41,1)[1],"0\n")
        self.assertEqual(case("brackets",41,1)[1],"-1\n")

    def test_full_recovery_uses_identical_C_F_L_and_removes_only_branch_in_R(self):
        controller,transport,rows,manifest=self.run_case()
        row=rows[0]
        self.assertTrue(row["primary_scheduled"])
        self.assertEqual(row["grades"],{arm:[1,1] for arm in ("K","R","Z","G")})
        terminal={i.arm:r for i,r in transport.calls if i.stage=="terminal"}
        keep=strict_loads(terminal["K"].data()["messages"][1]["content"])
        rollback=strict_loads(terminal["R"].data()["messages"][1]["content"])
        self.assertIsNotNone(keep["trial"])
        self.assertIsNone(rollback["trial"])
        keep["trial"]=None
        self.assertEqual(keep,rollback)
        resources=analyze(rows,controller.ledger.events())["resources"]
        self.assertEqual(resources["shared_experiment_planning_credits"],"0.060")
        self.assertEqual(resources["usage"]["output"],2400)
        self.assertEqual(resources["usage"]["reasoning"],1200)
        self.assertEqual(resources["API_spend_USD"],"0")
        self.assertNotIn("cost_usd",controller.ledger.events()[-1])
        self.assertEqual(len(slot_dispositions(manifest,rows,controller.ledger.rows())),13)

    def test_unusable_lesson_preserves_independent_Z_and_G_with_no_format_retry(self):
        controller,transport,rows,manifest=self.run_case({"lesson":"{}"})
        self.assertFalse(rows[0]["primary_scheduled"])
        self.assertEqual(rows[0]["scheduled_arms"],["Z","G"])
        self.assertEqual(sum(i.stage=="lesson" for i,r in transport.calls),1)
        self.assertEqual(rows[0]["grades"]["K"],[None,None])

    def test_primary_capacity_loss_blocks_both_K_and_R_before_either_dispatch(self):
        controller,transport,rows,manifest=self.run_case(capacity=True)
        self.assertTrue(rows[0]["capacity_infeasible"])
        self.assertFalse(rows[0]["primary_scheduled"])
        self.assertFalse(any(i.stage=="terminal" and i.arm in {"K","R"} for i,r in transport.calls))

    def test_initial_success_stops_without_manufacturing_recovery_opportunity(self):
        def correct_branch(identity,request):
            result=strict_loads(fixture_script()(identity,request))
            result["artifact"]={"values":[6,4]}
            return wire(result)
        controller,transport,rows,manifest=self.run_case({"branch":correct_branch})
        self.assertEqual(len(transport.calls),2)
        self.assertEqual(rows[0]["initial_grade"]["score"],1)
        self.assertFalse(rows[0]["public_failure"])
        self.assertTrue(all(x["dispatch_state"]=="not_dispatched" for x in slot_dispositions(manifest,rows,controller.ledger.rows())[2:]))

    def test_unknown_dispatch_locks_full_subscription_reserve_and_never_retries(self):
        controller,transport,rows,manifest=self.run_case(unknown=True)
        self.assertEqual(len(transport.calls),1)
        self.assertTrue(controller.ledger.summary()["blocked"])
        self.assertEqual(Decimal(controller.ledger.summary()["locked_reserve_credits"]),Decimal("4.225"))
        self.assertEqual(rows[0]["flow"],["infrastructure_stop_checkpoint"])
        self.assertEqual(sum(x["dispatch_state"]=="unknown" for x in slot_dispositions(manifest,rows,controller.ledger.rows())),1)

    def test_invalid_terminal_is_known_failure_with_no_grade_fed_to_other_draws(self):
        override={("terminal","K",1,1):"{}"}
        controller,transport,rows,manifest=self.run_case(override)
        self.assertEqual(rows[0]["grades"]["K"],[0,1])
        draws=[r.json_text for i,r in transport.calls if i.stage=="terminal" and i.arm=="K"]
        self.assertEqual(draws[0],draws[1])

    def test_undeclared_identity_rejected_before_any_reservation_or_transport(self):
        controller,transport,rows,manifest=self.run_case()
        before=len(controller.ledger.events())
        task=math_example()[0]
        with self.assertRaises(InterfaceError):
            controller.dispatcher.call(Identity("other-launch",task.task_id,"checkpoint"),Renderer().render("checkpoint",task))
        self.assertEqual(len(controller.ledger.events()),before)
        self.assertEqual(len(transport.calls),12)


if __name__=="__main__":
    unittest.main()
