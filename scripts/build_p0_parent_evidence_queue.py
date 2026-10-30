#!/usr/bin/env python3
"""Derive evidence-backed Project/Deposit relation review queue from frozen 272 raw rows.

Only source claims explicitly containing a named Project can assign a provisional
parent. Never merge Project IDs, infer JORC resource scopes or release C1 here.
"""
from __future__ import annotations
import csv
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE="docs/audits/2026-10-31_272_native_project_parent_audit.csv"
OLD="docs/audits/2026-10-31_272_project_parent_candidates_6.csv"
NEW="inputs/source_review_20261031/round3_272_project_parent_issuer_leads.csv"
OUT="docs/audits/2026-10-31_272_project_parent_evidence_queue.csv"
STATS="docs/audits/2026-10-31_272_project_parent_evidence_summary.json"
COLUMNS=[
    "target_id","state","source_name","source_key","source_native_id",
    "original_entity_type","native_feature_exact","native_feature_locator",
    "native_chunk_sha256","parent_claim_type","parent_project_candidate",
    "parent_relation_type","parent_evidence_source","parent_locator",
    "evidence_effective_or_publication_date","REE_project_role",
    "evidence_review_status","project_id_approved","C1_approved",
    "remaining_action",
]


def read(root:Path, path:str):
    with (root/path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def unique_map(rows, label):
    by={}
    for row in rows:
        k=row["target_id"]
        if not k or k in by:
            raise ValueError(f"Duplicate or empty {label} target_id: {k}")
        by[k]=row
    return by


def build(root:Path=ROOT):
    base=read(root,BASE)
    previous=unique_map(read(root,OLD),"previous")
    new=unique_map(read(root,NEW),"issuer")
    ids=[x["target_id"] for x in base]
    if len(ids)!=272 or len(set(ids))!=272 or len(previous)!=6 or len(new)!=13:
        raise ValueError("Frozen corpus dimension or source input mismatch")
    if (set(previous)|set(new))-set(ids):
        raise ValueError("One or more document relations are not in 272 native population")
    if set(previous)&set(new):
        raise ValueError("Conflicting parent claims must be adjudicated explicitly")
    rows=[]
    hist=Counter()
    for x in base:
        ident=x["target_id"]
        parent, relation, url, loc, date, typ, ree, state, next_step=(
            "","","","","","", "UNKNOWN", "UNASSIGNED",
            "Find authoritative Project/Deposit boundary and dated REE target evidence")
        if ident in new:
            ev=new[ident]
            parent=ev["documented_parent_project"]
            relation=ev["relation_type"]
            url=ev["primary_issuer_url"]
            loc=ev["document_locator"]
            date=ev["publication_date"]
            typ="EXTERNAL_DOCUMENTED_PARENT_CANDIDATE"
            if ev["original_source_name"]!=x["source_name"] or ev["state"]!=x["state"]:
                raise ValueError(f"External review target mismatch {ident}")
            ree=("UNCONFIRMED_REE_ECONOMIC_ROLE" if x["source_name"]=="Coburn"
                 else "DOCUMENTED_REE_PROJECT_OR_MINERAL_TARGET")
            state="DOCUMENTED_CANDIDATE_REQUIRES_PARENT_SIGNOFF"
            next_step="Verify georeferenced source unit, ownership, effective date and project boundary"
        elif ident in previous:
            ev=previous[ident]
            parent=ev["documented_parent_candidate"]
            relation=ev["relationship_basis"]
            url=ev["primary_source_url"]
            loc=ev["evidence_locator"]
            typ="EARLIER_SOURCE_REVIEWED_PARENT_CANDIDATE"
            ree=("NO_REE_PROJECT_ROLE" if ev["REE_project_role"]=="NO_REE_PROJECT_ROLE"
                 else "DOCUMENTED_REE_PROJECT_OR_MINERAL_TARGET")
            state=("DOCUMENTED_NON_REE_PROJECT_SOURCE" if ree=="NO_REE_PROJECT_ROLE"
                   else "DOCUMENTED_CANDIDATE_REQUIRES_PARENT_SIGNOFF")
            next_step="Independently confirm title/right holder and REE commodity role"
        elif x["project_parent_resolution"]=="OFFICIAL_NONPROJECT_GEOLOGICAL_SOURCE_ENTITY":
            typ="OFFICIAL_SOURCE_ENTITY_NONPROJECT"
            state="C0_NONPROJECT_SOURCE_ENTITY"
            ree="SOURCE_GEOLOGICAL_OCCURRENCE"
            next_step="Keep geological occurrence in Census; link only with parent document"
        elif x["project_parent_resolution"]=="TAS_PARENT_DEPOSIT_ID_NOT_PROJECT":
            typ="PARENT_DEPOSIT_ID_NOT_PROJECT_ID"
            state="C0_DEPOSIT_PARENT_ONLY"
            next_step="Identify enclosing development Project independently"
        elif x["project_parent_resolution"]=="VIC_PROJECT_FIELD_CATEGORY_NOT_DISTINCT_PROJECT":
            typ="NON_PROJECT_CATEGORY_LABEL"
            state="C0_THEMATIC_LABEL_NOT_PROJECT"
            next_step="Do not treat 'Critical Minerals' category as a Project name"
        elif x["project_parent_resolution"]=="NO_PROJECT_PARENT_FIELD":
            typ="OFFICIAL_NATIVE_RECORD_WITHOUT_PROJECT_PARENT"
            state="PROJECT_PARENT_UNLOCATED"
        else:
            raise ValueError(f"Unexpected source relation class: {x['project_parent_resolution']}")
        hist[state]+=1
        rows.append(dict(zip(COLUMNS, [
            ident,x["state"],x["source_name"],x["source_key"],x["source_native_id"],
            x["original_entity_type"],"YES" if x["native_raw_match"]=="RAW_FEATURE_EXACT_NATIVE_ID" else "NO",
            x["raw_feature_locator"],x["raw_chunk_sha256"],
            typ,parent,relation,url,loc,date,ree,state,"NO","NO",next_step,
        ])))
    if any(x["native_feature_exact"]!="YES" or x["project_id_approved"]!="NO"
            or x["C1_approved"]!="NO" for x in rows):
        raise ValueError("One or more native records not uniquely matched, or auto-approval present")
    expected={
        "DOCUMENTED_CANDIDATE_REQUIRES_PARENT_SIGNOFF":15,
        "DOCUMENTED_NON_REE_PROJECT_SOURCE":4,
        "C0_NONPROJECT_SOURCE_ENTITY":92,
        "C0_DEPOSIT_PARENT_ONLY":2,
        "C0_THEMATIC_LABEL_NOT_PROJECT":3,
        "PROJECT_PARENT_UNLOCATED":156,
    }
    if dict(hist)!=expected:
        raise ValueError(f"Unexpected parent-group counts {dict(hist)}")
    stats={
        "snapshot":"2026-10-31",
        "source_as_of":"2026-10-29",
        "units":"272 source target rows, not 272 independent development projects",
        "input_rows":272,
        "native_exact":272,
        "new_documented_parent_source_rows":len(new),
        "previous_documented_parent_source_rows":len(previous),
        "documented_candidate_source_rows":15,
        "documented_non_ree_project_source_rows":4,
        "project_parent_unlocated":hist["PROJECT_PARENT_UNLOCATED"],
        "official_geological_nonprojects":hist["C0_NONPROJECT_SOURCE_ENTITY"],
        "deposit_parent_only":hist["C0_DEPOSIT_PARENT_ONLY"],
        "generic_thematic_label":hist["C0_THEMATIC_LABEL_NOT_PROJECT"],
        "parent_review_distribution":dict(hist),
        "independent_project_approvals":0,
        "C1_approvals":0,
        "distinct_new_parent_name_strings":len({x["documented_parent_project"] for x in new.values()}),
        "note":"Evidence-backed candidate Project name only; historic government prospectus, company declaration and official EIS have different scope. No official stage/resource/GIS automatic approval.",
    }
    return rows,stats


def output(root:Path=ROOT):
    rows,stats=build(root)
    csv_path=root/OUT
    csv_path.parent.mkdir(parents=True,exist_ok=True)
    with csv_path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=COLUMNS,lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    (root/STATS).write_text(json.dumps(stats,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(stats,ensure_ascii=False))
    return stats


if __name__=="__main__":
    output()
