"""Prepare, calibrate, compare and replay a new fixed rollback allocation."""
import argparse
from pathlib import Path

from .common import ROOT, FAMILIES, SEED, read, save_new, wire
from .prepare import prepare, check_bundle
from .runner import run
from .audit import audit
from .analysis import select_screen, validate_selection
from .statistics import plan


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=["prepare","simulate","launch","audit","select","validate","power","preview"])
    p.add_argument("--bundle",type=Path); p.add_argument("--output",type=Path); p.add_argument("--run",type=Path)
    p.add_argument("--prior",type=Path); p.add_argument("--selection",type=Path); p.add_argument("--power-plan",type=Path)
    p.add_argument("--split",choices=["screen","validation","confirmation","fixture"],default="screen")
    p.add_argument("--seed",type=int,default=SEED); p.add_argument("--replicates",type=int,default=2)
    p.add_argument("--stages",type=int,default=4); p.add_argument("--actions",type=int,default=8)
    p.add_argument("--cells",nargs="+",help="family:level, e.g. constraint_grid:2")
    p.add_argument("--arms",nargs="+"); p.add_argument("--max-calls",type=int)
    p.add_argument("--require-candidates",action="store_true",default=None,help="require a best complete candidate on every action; inherited from calibration for later phases")
    p.add_argument("--allow-fresh-ceiling",action="store_true",default=None,help="new calibration design: require K headroom while allowing the fresh solvability control to saturate")
    p.add_argument("--robust-control-missingness",action="store_true",default=None,help="new controls only: require rate gates for every missing-score completion and at least seven eighths observed")
    p.add_argument("--ledger-profile",choices=["standard","intermediate"],help="ledger size family; inherited from calibration for later phases")
    p.add_argument("--workers",type=int,default=4); p.add_argument("--live",action="store_true")
    p.add_argument("--snapshot",action="store_true",help="audit with bound historical source, never for dispatch/selection")
    p.add_argument("--executable",type=Path); p.add_argument("--global-instructions",type=Path)
    p.add_argument("--effect",type=float,default=.10); p.add_argument("--discordance",type=float,default=.30)
    p.add_argument("--target-power",type=float,default=.80); p.add_argument("--task-index",type=int,default=0)
    args=p.parse_args()
    if args.mode=="power":
        result=plan(args.effect,args.discordance,args.target_power)
        if args.output: save_new(args.output,result)
    elif args.mode=="prepare":
        if not args.output: p.error("prepare requires --output")
        cells=[(v.rsplit(":",1)[0],int(v.rsplit(":",1)[1])) for v in args.cells] if args.cells else None
        m=prepare(args.output,split=args.split,seed=args.seed,cells=cells,replicates=args.replicates,
                  stages=args.stages,actions=args.actions,arms=args.arms,max_calls=args.max_calls,
                  require_candidates=args.require_candidates,
                  allow_fresh_ceiling=args.allow_fresh_ceiling,
                  robust_control_missingness=args.robust_control_missingness,ledger_profile=args.ledger_profile,
                  selection=read(args.selection) if args.selection else None,power_plan=read(args.power_plan) if args.power_plan else None)
        result={"tasks":len(m["jobs"])//len(m["arms"]),"jobs":len(m["jobs"]),"generation_ceiling":m["generation_ceiling"],"model_calls":0}
    else:
        if not args.bundle: p.error("--bundle required")
        if args.mode in {"launch","simulate"}:
            if not args.output: p.error("--output required")
            if args.mode=="launch" and not args.live: p.error("launch requires explicit --live")
            result=run(args.bundle,args.output,live=args.mode=="launch",workers=args.workers,prior=args.prior,
                       executable=args.executable,global_instructions=args.global_instructions)
        elif args.mode=="preview":
            from .contexts import actor_state
            from ..rollback_development_v5.engine import initial_state
            _,tasks=check_bundle(args.bundle); t=tasks[args.task_index]
            result=actor_state(t,initial_state(t))
        else:
            if not args.run: p.error("--run required")
            if args.snapshot and args.mode!="audit": p.error("--snapshot is for audit only")
            if args.snapshot:
                from .snapshot import audit_snapshot
                checked=audit_snapshot(args.bundle,args.run)
            else: checked=audit(args.bundle,args.run)
            if args.mode=="audit": result=checked
            else:
                if not args.output: p.error("--output required")
                m,_=check_bundle(args.bundle); report=read(args.run/"analysis.json")
                if args.mode=="select":
                    result=select_screen(report,m)
                    result["provenance"]={"screen_bundle":args.bundle.resolve().relative_to(ROOT).as_posix(),"screen_run":args.run.resolve().relative_to(ROOT).as_posix()}
                else:
                    if not args.selection: p.error("validate requires screening --selection")
                    screen=read(args.selection)
                    from .prepare import verify_selection
                    verify_selection(screen)
                    result=validate_selection(screen,report,m)
                    result["provenance"]={**screen["provenance"],"validation_bundle":args.bundle.resolve().relative_to(ROOT).as_posix(),"validation_run":args.run.resolve().relative_to(ROOT).as_posix()}
                save_new(args.output,result)
    print(wire(result),flush=True)


if __name__=="__main__": main()
