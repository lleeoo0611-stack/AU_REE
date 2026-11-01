#!/usr/bin/env python3
"""First-pass source-scoped C1 review for fixed 39 Project screening groups.

The evidence ledger is editable. This child script never changes C1/C2 admissions.
It distinguishes original dated studies from a claim that a Study is in progress.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"docs/audits/2026-10-31_c1_c2_project_review_39.csv"
REVIEWS=ROOT/"inputs/source_review_20261101/c1_stage1_public_evidence_7.csv"
OUT=ROOT/"docs/audits/2026-11-01_c1_first_pass_gate_39.csv"
SUMMARY=ROOT/"docs/audits/2026-11-01_c1_first_pass_summary.json"
FREEZE=date(2026,10,29)

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def ensure(b,msg):
    if not b: raise ValueError(msg)

def generate():
    groups,checks=read(INPUT),read(REVIEWS)
    ensure(len(groups)==39 and len(checks)==7, "expected 39 groups and 7 scoped evidence checks")
    idx={r["review_group_id"]:r for r in groups}
    byid={r["review_group_id"]:r for r in checks}
    ensure(len(idx)==39 and len(byid)==7,"duplicate review group")
    for item in checks:
        gid=item["review_group_id"]
        ensure(gid in idx,"C1 evidence refers to unknown Project group "+gid)
        g=idx[gid]
        ensure(g["screening_class"]=="STUDY_DOCUMENTED_PRE_FID_SCREEN","new first-pass evidence has wrong initial screening class")
        ensure(item["project_name"]==g["project_name"] and item["state"]==g["state"],"Project identity mismatch")
        ensure(item["source_asof"]=="2026-10-29" and item["reviewed_on"]=="2026-11-01","as-of or review date changed")
        if item["document_date_or_study_date"]:
            ensure(date.fromisoformat(item["document_date_or_study_date"])<=FREEZE,
                   "post-29-Oct source must not inform as-of-2026-10-29 C1")
        ensure(item["public_source_url"].startswith("https://") and item["document_locator"] and
               item["source_scoped_finding"] and item["critical_next_check"],"evidence locator or findings missing")
        ensure(item["pdf_original_bytes_archived"]=="NO" and not item["pdf_original_sha256"],
               "cannot invent downloaded/hashed full original PDF")
        ensure(item["official_project_footprint_verified"]==item["individual_six_gate_signed"]==
               item["formal_C1_admitted"]=="NO","manual six gate cannot be auto approved")
    results=[]
    for g in groups:
        ensure(g["source_snapshot"]=="2026-10-29","C1 source snapshot changed")
        ensure(g["C1_release_status"] in
               {"NOT_ADMITTED_SIX_GATES_UNAPPROVED", "C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES"},
               "unknown signed C1 release status")
        ensure(g["C2_project_id_approved"] in {"YES", "NO"}, "unknown C2 identity status")
        c1_admitted = g["C1_release_status"]=="C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES"
        c2_admitted = g["C2_project_id_approved"]=="YES"
        gates = ("ID", "ROLE", "WINDOW", "JORC", "PANEL", "GIS_RELEASE")
        signed_gate_count = sum(g[gate+"_gate"].startswith("PASS_") for gate in gates)
        e=byid.get(g["review_group_id"])
        results.append({
            "review_group_id":g["review_group_id"],"project_name":g["project_name"],
            "state":g["state"],"source_snapshot":"2026-10-29",
            "screening_class":g["screening_class"],
            "project_identity_gate":g["ID_gate"],"ree_product_gate":g["ROLE_gate"],
            "window_gate":g["WINDOW_gate"],"JORC_gate":g["JORC_gate"],
            "PANEL_gate":g["PANEL_gate"],"GIS_RELEASE_gate":g["GIS_RELEASE_gate"],
            "stage1_priority":g["C1_candidate_review_priority"],
            "new_study_evidence_review_id":e["review_id"] if e else "",
            "original_source_url":e["public_source_url"] if e else g["original_source_url"],
            "primary_review_level":("SCOPED_PUBLIC_PRIMARY_TEXT_NOT_FULL_ORIGINAL" if e else
                                    "EXISTING_PROJECT_SCREEN_ONLY"),
            "study_evidence_status":e["study_evidence_class"] if e else "NEEDS_DATED_ORIGINAL_REVIEW",
            "REE_resource_evidence_status":e["REE_resource_evidence_class"] if e else g["resource_basis_screen"],
            "source_scope_issue":e["source_scoped_finding"] if e else g["original_evidence_finding"],
            "next_first_gate_action":e["critical_next_check"] if e else g["next_gate_action"],
            "original_fulltext_verified":"NO","source_project_identity_signed":"YES" if c2_admitted else "NO",
            "approved_C1_gate_count":str(signed_gate_count),
            "independent_C1_release":"YES" if c1_admitted else "NO",
            "C2_status":g["C2_release_status"],
        })
    study=Counter(e["study_evidence_class"] for e in checks)
    summary={
        "row_count":39,"documentary_scope_rechecked":7,"remaining_group_screen_only":32,
        "source_snapshot":"2026-10-29","original_PDF_bytes_collected":0,
        "independent_C1_admitted":sum(r["independent_C1_release"]=="YES" for r in results),
        "independent_C2_admitted":sum(r["source_project_identity_signed"]=="YES" for r in results),
        "stage1_study_evidence_counts":dict(sorted(study.items()))
    }
    return results,summary

def csv_text(rs):
    buf=io.StringIO(newline="")
    w=csv.DictWriter(buf,fieldnames=list(rs[0]),quoting=csv.QUOTE_ALL,lineterminator="\n")
    w.writeheader();w.writerows(rs)
    return buf.getvalue()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_mutually_exclusive_group(required=True)
    sub.add_argument("--check",action="store_true")
    sub.add_argument("--write",action="store_true")
    args=ap.parse_args()
    rows,stats=generate()
    if args.write:
        OUT.write_text(csv_text(rows),encoding="utf-8")
        SUMMARY.write_text(json.dumps(stats,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    else:
        ensure(read(OUT)==rows,"derived 39-row C1 first-pass CSV changed")
        ensure(json.loads(SUMMARY.read_text(encoding="utf-8"))==stats,"C1 first-pass summary changed")
    print("PASS C1 Stage1: 39 candidate groups, seven source-scoped evidence checks; "
          f"{stats['independent_C1_admitted']} signed C1 and "
          f"{stats['independent_C2_admitted']} signed C2")

if __name__=="__main__":
    main()
