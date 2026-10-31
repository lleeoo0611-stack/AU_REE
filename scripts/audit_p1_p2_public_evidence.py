#!/usr/bin/env python3
"""P1 remaining public evidence + P2 28-case scoped documentary desk review.

Source-level original 412 HOLD denominator frozen on 2026-10-29.
All output generated strictly from input provenance CSV, not current live web;
actual source PDFs are not automatically downloaded, hashed, or considered JORC.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P1_SOURCE=Path("docs/audits/2026-10-31_p1_73_source_resolution.csv")
P1_REMAINING=Path("inputs/source_review_20261031/p1_19_public_remaining_case_adjudications.csv")
P2_SOURCE=Path("docs/audits/2026-10-31_p2_28_source_triage.csv")
P2_CASES=Path("docs/audits/2026-10-31_p2_27_case_triage.csv")
P2_REMAINING=Path("inputs/source_review_20261031/p2_27_public_evidence_adjudications.csv")
P1_OUT=Path("docs/audits/2026-10-31_p1_31_remaining_public_source_review.csv")
P2_OUT=Path("docs/audits/2026-10-31_p2_28_public_terminal_desk_review.csv")
SUMMARY=Path("docs/audits/2026-10-31_p1_p2_public_review_summary.json")

P1_COLS=[
    "target_id","case_id","source_name","state","native_chunk_sha256",
    "original_documentary_verdict","new_review_track","scoped_documentary_status",
    "supporting_url","secondary_url","document_publication_date","document_locator",
    "reviewed_claim","reviewed_stage_or_resource_scope","original_source_spatial_identity",
    "official_WAMEX_original_PDF_sha256","ID_gate","ROLE_gate","WINDOW_gate",
    "JORC_gate","PANEL_gate","GIS_release_gate","C1_admitted",
    "public_evidence_scope_closed","remaining_action","reviewer_signature"]
P2_COLS=[
    "target_id","case_id","source_name","state","original_P2_priority","native_feature_sha256",
    "previous_P2_stage_status","scoped_documentary_verdict",
    "primary_or_lead_url","related_source_url","document_date","document_locator",
    "issuer_or_operator","tenement_numbers","source_scoped_claim",
    "REE_or_resource_basis","project_stage_supported","source_project_relation",
    "original_pdf_SHA256_if_archived","ID_gate","ROLE_gate","WINDOW_gate","JORC_gate",
    "PANEL_gate","GIS_release_gate","C1_admitted","public_evidence_scope_closed",
    "remaining_action","reviewer_signature"]
P2_VERDICTS={
    "SCOPED_PRIMARY_OR_ISSUER_FOUND__LEGACY_GIS_AND_C1_HOLD":17,
    "ISSUER_SCOPING_EXCLUDES_REE_RESOURCE_STAGE":1,
    "DOCUMENTED_HISTORIC_SITE_OUTSIDE_CURRENT_PREFID":3,
    "PRIMARY_DRILL_NEGATIVE_FOR_TESTED_REE_TARGET":1,
    "GOV_NATIVE_FEATURE_ONLY_PROJECT_ROLE_NOT_SHOWN":3,
    "REGIONAL_SECONDARY_NAME_COLLISION_NO_PRIMARY_JOIN":2,
}
P1_TRACKS={"POSITIVE_REE_OR_PROJECT_LEAD":13,"GEO_IDENTITY_CONFLICT":2,"WAMEX_OFFICIAL_PRIMARY_ACCESS":4}

def read(root:Path,path:Path)->list[dict[str,str]]:
    with (root/path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def build(root:Path=ROOT):
    p1_source=read(root,P1_SOURCE)
    p1_review=read(root,P1_REMAINING)
    p2_source=read(root,P2_SOURCE)
    p2_cases=read(root,P2_CASES)
    p2_review=read(root,P2_REMAINING)
    assert len(p1_source)==73 and len(p1_review)==19
    assert len(p2_source)==28 and len(p2_review)==len(p2_cases)==27
    assert len({r["target_id"] for r in p1_source})==73
    assert len({r["target_id"] for r in p2_source})==28
    assert len({r["case_id"] for r in p1_review})==19
    assert len({r["case_id"] for r in p2_review})==27
    assert Counter(r["decision_track"] for r in p1_review)==P1_TRACKS
    assert Counter(r["documentary_terminal_verdict"] for r in p2_review)==P2_VERDICTS
    assert {r["case_id"] for r in p2_review}=={r["case_id"] for r in p2_cases}
    source_p1={r["target_id"]:r for r in p1_source}
    review_p2={r["case_id"]:r for r in p2_review}
    out_p1=[]
    for x in p1_review:
        ids=x["source_target_ids"].split("|")
        assert len(ids)==int(x["source_row_count"])
        assert len(ids)==len(set(ids))
        assert x["public_search_scope_closed"].startswith("YES_")
        assert not x["reviewer_signature"]
        assert not x["original_government_PDF_SHA256_if_archived"]
        for tid in ids:
            s=source_p1[tid]
            assert s["case_id"]==x["case_id"]
            assert s["C1_approved"]=="NO"
            assert s["independent_JORC_REO_approved"]=="NO"
            row={
                "target_id":tid,"case_id":x["case_id"],"source_name":s["source_name"],
                "state":s["state"],"native_chunk_sha256":s["native_chunk_sha256"],
                "original_documentary_verdict":s["documentary_verdict"],
                "new_review_track":x["decision_track"],
                "scoped_documentary_status":x["documentary_status"],
                "supporting_url":x["supporting_url"],"secondary_url":x["secondary_url"],
                "document_publication_date":x["source_date"],
                "document_locator":x["source_locator"],"reviewed_claim":x["public_evidence_interpretation"],
                "reviewed_stage_or_resource_scope":x["reviewed_stage_or_resource_scope"],
                "original_source_spatial_identity":s["source_spatial_identity"],
                "official_WAMEX_original_PDF_sha256":x["original_government_PDF_SHA256_if_archived"],
                "ID_gate":x["formal_ID_gate"],"ROLE_gate":x["formal_ROLE_gate"],
                "WINDOW_gate":x["formal_WINDOW_gate"],"JORC_gate":x["formal_JORC_gate"],
                "PANEL_gate":x["formal_PANEL_gate"],"GIS_release_gate":x["formal_GIS_release_gate"],
                "C1_admitted":"NO","public_evidence_scope_closed":x["public_search_scope_closed"],
                "remaining_action":x["remaining_action"],"reviewer_signature":x["reviewer_signature"]
            }
            out_p1.append(row)
    out_p1.sort(key=lambda x:(x["case_id"],x["target_id"]))
    assert len(out_p1)==31 and len({x["target_id"] for x in out_p1})==31
    assert sum(x["new_review_track"]=="POSITIVE_REE_OR_PROJECT_LEAD" for x in out_p1)==22
    assert sum(x["new_review_track"]=="WAMEX_OFFICIAL_PRIMARY_ACCESS" for x in out_p1)==5
    assert sum(x["new_review_track"]=="GEO_IDENTITY_CONFLICT" for x in out_p1)==4
    assert not ({x["target_id"] for x in p2_source} & {x["target_id"] for x in p1_source})
    out_p2=[]
    for s in p2_source:
        x=review_p2[s["case_id"]]
        assert s["target_id"] in x["source_target_ids"].split("|")
        assert s["C1_admitted"]=="NO"
        assert s["original_priority"]=="P2"
        assert not x["reviewer_signature"]
        assert not x["original_pdf_SHA256_if_archived"]
        row={
            "target_id":s["target_id"],"case_id":s["case_id"],"source_name":s["source_record_name"],
            "state":s["state"],"original_P2_priority":s["original_priority"],
            "native_feature_sha256":s["native_sha256_in_round2"],
            "previous_P2_stage_status":s["p2_stage_status"],
            "scoped_documentary_verdict":x["documentary_terminal_verdict"],
            "primary_or_lead_url":x["primary_or_lead_url"],
            "related_source_url":x["related_source_url"],
            "document_date":x["evidence_date"],"document_locator":x["document_locator"],
            "issuer_or_operator":x["source_operator"],"tenement_numbers":x["tenement_numbers"],
            "source_scoped_claim":x["source_scoped_claim"],
            "REE_or_resource_basis":x["REE_or_resource_basis"],
            "project_stage_supported":x["project_stage_supported"],
            "source_project_relation":x["source_project_relation"],
            "original_pdf_SHA256_if_archived":x["original_pdf_SHA256_if_archived"],
            "ID_gate":x["formal_ID_gate"],"ROLE_gate":x["formal_ROLE_gate"],
            "WINDOW_gate":x["formal_WINDOW_gate"],"JORC_gate":x["formal_JORC_gate"],
            "PANEL_gate":x["formal_PANEL_gate"],"GIS_release_gate":x["formal_GIS_GATE"],
            "C1_admitted":"NO","public_evidence_scope_closed":x["public_evidence_scope_closed"],
            "remaining_action":x["reopen_requirement"],"reviewer_signature":x["reviewer_signature"]
        }
        out_p2.append(row)
    out_p2.sort(key=lambda x:(x["case_id"],x["target_id"]))
    assert len(out_p2)==28
    assert all(x["public_evidence_scope_closed"]=="YES_SCOPED_DESK_REVIEW_ONLY" for x in out_p2)
    assert all(x["C1_admitted"]=="NO" for x in out_p1+out_p2)
    assert all(not x["reviewer_signature"] for x in out_p1+out_p2)
    stats={
        "audit_date":"2026-10-31",
        "frozen_asof":"2026-10-29",
        "source_inventory_total":487,
        "HOLD_source_total":412,
        "P1_original_HOLD_sources":73,
        "P1_cases_with_remaining_issues_reviewed":19,
        "P1_remaining_issue_source_rows_reviewed":31,
        "P1_remaining_source_tracks":dict(sorted(Counter(x["new_review_track"] for x in out_p1).items())),
        "P1_positive_cases_still_formal_C1_HOLD":13,
        "P1_WAMEX_unique_reports_indexed":4,
        "P1_WAMEX_source_rows":5,
        "P1_WAMEX_official_pdf_originals_archived":0,
        "P1_identity_conflict_case_count":2,
        "P1_identity_conflict_source_rows":4,
        "P2_initial_source_rows":28,
        "P2_provisional_cases_public_reviewed":27,
        "P2_terminal_source_rows_documentary_scope_reviewed":28,
        "P2_case_documentary_verdict_counts":dict(sorted(
            Counter(x["documentary_terminal_verdict"] for x in p2_review).items())),
        "P2_legal_Project_or_JORC_resource_gate_approved":0,
        "P2_C1_admissions":0,
        "P3_source_rows_unchanged":216,
        "P4_source_rows_unchanged":95,
        "all_412_source_ids_reprioritised":False,
        "all_new_formal_C1_gates_approved":False,
        "WAMEX_public_search_only_no_email_sent":True,
        "evidence_retrieval_mode":"public government/issuer site and carefully attributed secondary indexed government-report text",
        "input_paths":[str(P1_SOURCE),str(P1_REMAINING),str(P2_SOURCE),
                       str(P2_CASES),str(P2_REMAINING)],
        "interpretation":"Desk evidence review is bounded and assigned a terminal documentary "
        "disposition on all 28 P2 targets. No archived original WAMEX PDFs, independent "
        "source-to-Project polygons, JORC REO approvals, or six-domain C1 signoffs "
        "are inferred. Future new original documents reopen cases with retained IDs."
    }
    return out_p1,out_p2,stats

def write(path:Path,rows:list[dict[str,str]],cols:list[str]):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--write",action="store_true")
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    a,b,s=build()
    if args.write:
        write(ROOT/P1_OUT,a,P1_COLS)
        write(ROOT/P2_OUT,b,P2_COLS)
        (ROOT/SUMMARY).write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if args.check:
        assert read(ROOT,P1_OUT)==a,P1_OUT
        assert read(ROOT,P2_OUT)==b,P2_OUT
        assert json.loads((ROOT/SUMMARY).read_text(encoding="utf-8"))==s,SUMMARY
    print(json.dumps(s,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
