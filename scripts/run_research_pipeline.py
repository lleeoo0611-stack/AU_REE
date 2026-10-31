#!/usr/bin/env python3
"""Single supervisor for AU_REE research verification and approved data rebuilding.

All child scripts run as subprocesses without shell commands. The default
C1 mainline NEVER runs legacy R-MCDA, online census refresh, or arbitrary
P2–P4 source queries. P2–P4 routing requires a concrete new evidence event.
"""
from __future__ import annotations
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"config/research_pipeline_v1.json"

def read_manifest():
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema_version")!="1.0":
        raise ValueError("unknown pipeline manifest version")
    return data

def new_source_events(path,decision_path):
    """Count unreviewed source events, not all historical events in the ledger."""
    with path.open(encoding="utf-8-sig",newline="") as f:
        records=list(csv.DictReader(f))
    with decision_path.open(encoding="utf-8-sig",newline="") as f:
        decisions=list(csv.DictReader(f))
    reviewed={d["event_id"] for d in decisions if d["review_status"] in
              {"SOURCE_SCOPE_REVIEWED","HOLD_UNRESOLVED"}}
    return sum(r["event_id"] not in reviewed for r in records)

def build_plan(profile="all",mode="check",*,root=None,manifest=None):
    """Return deterministic child commands for inspection and regression tests."""
    root=root or ROOT
    cfg=manifest or read_manifest()
    if profile not in cfg["profiles"] or mode not in ("check","write"):
        raise ValueError("unknown profile or run mode")
    planned=[]
    for stage_name in cfg["profiles"][profile]:
        stage=cfg["stages"][stage_name]
        if stage_name=="p234_event_router":
            source=root/stage["trigger_input"]
            events=new_source_events(source,root/stage["review_decisions_input"])
            if events==0:
                planned.append({"name":stage_name,"action":"SKIP_NO_NEW_EVIDENCE",
                                "event_count":0,"command":[]})
                continue
        if stage["type"]=="python_script":
            file=root/stage["script"]
            if not file.is_file():
                raise FileNotFoundError(file)
            cmd=[sys.executable,str(file),stage["arg_check"] if mode=="check" else stage["arg_write"]]
        elif stage["type"]=="python_module":
            cmd=[sys.executable,"-m",stage["module"]]+stage["args_check" if mode=="check" else "args_write"]
        else:
            raise ValueError("invalid stage type")
        planned.append({"name":stage_name,"action":"EXECUTE","command":cmd,
                        "guard":stage["guard"]})
    return planned

def execute(profile,mode,dry_run=False):
    plan=build_plan(profile,mode)
    for step in plan:
        if step["action"]!="EXECUTE" or dry_run:
            continue
        proc=subprocess.run(step["command"],cwd=ROOT,check=False)
        if proc.returncode:
            raise RuntimeError("child stage failed: "+step["name"]+
                               " (exit "+str(proc.returncode)+")")
    return {"profile":profile,"mode":mode,"status":"PLAN_ONLY" if dry_run else "PASS",
            "stages":[{"name":s["name"],"action":s["action"]} for s in plan],
            "source_snapshot":"2026-10-29",
            "C1_automatic_admissions":0}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile",choices=("c1","p234","all","legacy"),default="all")
    parser.add_argument("--mode",choices=("check","write"),default="check")
    parser.add_argument("--plan",action="store_true",help="show commands without invoking child scripts")
    args=parser.parse_args()
    try:
        summary=execute(args.profile,args.mode,dry_run=args.plan)
    except (ValueError,FileNotFoundError,RuntimeError,subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        return 1
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
