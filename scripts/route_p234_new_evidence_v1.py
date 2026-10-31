#!/usr/bin/env python3
"""Route NEW source-native P2-P4 evidence events; never repeat old URL searches.

An event is manually recorded with a concrete report locator and target ID.
This script only creates a scope-review work item. It never treats an external
URL as a downloaded original or automatically admits a Project to C1.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs/audits/2026-10-31_p234_b06_reason_classification_339.csv"
INPUT=ROOT/"inputs/evidence/p234_new_primary_evidence_events_v1.csv"
DECISIONS=ROOT/"inputs/review_decisions/p234_evidence_event_review_v1.csv"
OUTPUT=ROOT/"docs/audits/2026-11-01_p234_evidence_trigger_queue_v1.csv"
SUMMARY=ROOT/"docs/audits/2026-11-01_p234_evidence_trigger_summary_v1.json"
CUTOFF=date(2026,10,29)
COLUMNS=("event_id","target_id","priority","source_name","source_native_id","evidence_doc_id",
         "source_url","published_date","temporal_scope","review_status",
         "source_scope_locator","next_action","C1_admitted")

def rows(path):
    with path.open(encoding="utf-8-sig",newline="") as fp:
        return list(csv.DictReader(fp))

def require(ok,msg):
    if not ok: raise ValueError(msg)

def validate_event(e,source):
    require(bool(re.fullmatch(r"EV-P234-[A-Za-z0-9][A-Za-z0-9_-]{3,79}",e["event_id"])),
            "event_id must be stable and source-specific EV-P234-*")
    require(e["target_id"]==source["target_id"],"nonmatching source target")
    require(e["source_key"]==source["source_key"] and
            e["source_native_id"]==source["source_native_id"],"source-native key conflict")
    require(e["source_snapshot"]=="2026-10-29","cannot silently rewrite frozen source snapshot")
    require(e["evidence_doc_id"].strip() and e["section_locator"].strip() and
            e["submission_reason"].strip(),"need concrete NEW report and source-scoped locator")
    u=urlparse(e["official_url"])
    require(u.scheme=="https" and bool(u.netloc) and not u.username and not u.password,
            "original primary evidence must be HTTPS URL")
    p=date.fromisoformat(e["published_date"])
    require(e["original_bytes_archived"] in {"YES","NO"},"invalid original bytes flag")
    if e["original_bytes_archived"]=="YES":
        require(bool(re.fullmatch(r"[0-9a-fA-F]{64}",e["original_sha256"])),
                "archived original requires actual SHA256")
    else:
        require(not e["original_sha256"],"SHA256 cannot be claimed when original bytes unavailable")
    require(e["claim_type"] in {
        "PROJECT_IDENTITY","REE_PRODUCT_ROLE","RESOURCE_JORC_REO",
        "DATED_ECONOMIC_STUDY","LEGAL_TENURE","GEOMETRY_GIS",
        "HISTORICAL_GEOLOGY","CONTRADICTORY_PRIMARY_SOURCE"
    },"unknown claim type")
    return p

def generate(events=None,decisions=None):
    baseline=rows(BASE)
    event_rows=rows(INPUT) if events is None else events
    decision_rows=rows(DECISIONS) if decisions is None else decisions
    require(len(baseline)==339,"P2–P4 frozen census changed")
    by_id={r["target_id"]:r for r in baseline}
    require(len(by_id)==339,"duplicate baseline target ID")
    accepted={}
    for d in decision_rows:
        require(d["event_id"] not in accepted,"duplicate event review")
        require(d["review_status"] in {"SOURCE_SCOPE_REVIEWED","HOLD_UNRESOLVED"},
                "event review cannot approve Project/C1")
        for field in ("reviewer_id","reviewed_at","approval_ref"):
            require(bool(d[field].strip()),"no anonymous event review")
        accepted[d["event_id"]]=d
    used=set()
    doc_keys=set()
    queue=[]
    post=0
    reviewed=0
    for e in event_rows:
        require(e["event_id"] not in used,"duplicate event ID")
        used.add(e["event_id"])
        target=e["target_id"]
        require(target in by_id,"event target not in frozen P2–P4 cohort")
        source=by_id[target]
        p=validate_event(e,source)
        doc=(target,e["evidence_doc_id"].lower(),e["section_locator"].lower())
        require(doc not in doc_keys,"duplicate source/document/locator evidence")
        doc_keys.add(doc)
        temporal=("WITHIN_FROZEN_SOURCE_DATE" if p<=CUTOFF else
                  "POST_2026_10_29_NEW_VERSION_ONLY")
        if p>CUTOFF:post+=1
        approved=accepted.get(e["event_id"])
        status=approved["review_status"] if approved else "NEW_SOURCE_SCOPE_REVIEW_REQUIRED"
        if approved and status=="SOURCE_SCOPE_REVIEWED":reviewed+=1
        queue.append({
            "event_id":e["event_id"],"target_id":target,"priority":source["priority"],
            "source_name":source["source_name"],"source_native_id":source["source_native_id"],
            "evidence_doc_id":e["evidence_doc_id"],"source_url":e["official_url"],
            "published_date":e["published_date"],"temporal_scope":temporal,
            "review_status":status,"source_scope_locator":e["section_locator"],
            "next_action":("MANUAL_EXACT_SOURCE_SCOPE_AND_P1_PROJECT_CROSSWALK_CHECK" if not approved else
                           "RETAIN_SIGNED_SOURCE_SCOPE_DECISION_NO_AUTO_PROJECT_ADMISSION"),
            "C1_admitted":"NO"
        })
    require(set(accepted).issubset(used),"orphaned source review approval")
    count=len(queue)
    summary={
        "schema_version":"1.0","source_snapshot":"2026-10-29",
        "submitted_events":count,"validated_events":count,
        "awaiting_scope_review":sum(x["review_status"]=="NEW_SOURCE_SCOPE_REVIEW_REQUIRED" for x in queue),
        "reviewed_source_scope_events":reviewed,"post_snapshot_events":post,
        "trigger_state":"READY_SOURCE_SCOPE_REVIEW" if count else "SKIP_NO_NEW_EVIDENCE",
        "C1_automatic_promotions":0
    }
    return queue,summary

def csv_text(items):
    fp=io.StringIO(newline="")
    writer=csv.DictWriter(fp,fieldnames=COLUMNS,quoting=csv.QUOTE_ALL,lineterminator="\n")
    writer.writeheader()
    writer.writerows(items)
    return fp.getvalue()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    opts=ap.add_mutually_exclusive_group(required=True)
    opts.add_argument("--check",action="store_true")
    opts.add_argument("--write",action="store_true")
    args=ap.parse_args()
    queue,summary=generate()
    if args.write:
        OUTPUT.write_text(csv_text(queue),encoding="utf-8")
        SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    else:
        require(rows(OUTPUT)==queue,"P2–P4 event queue needs regeneration")
        require(json.loads(SUMMARY.read_text(encoding="utf-8"))==summary,
                "P2–P4 trigger summary needs regeneration")
    print(f"{summary['trigger_state']}: {summary['submitted_events']} new evidence events, "
          f"{summary['awaiting_scope_review']} awaiting source scope review, C1 autosign=0")

if __name__=="__main__":
    main()
