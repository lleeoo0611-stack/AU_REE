#!/usr/bin/env python3
"""Build the accepted C0 F1/F2 review policy and strict C1/C2 gate ledgers.

Source-level and Project-level approvals are separate and never inferred.
The as-of 2026-10-29 raw data and legacy/C0 snapshots are read-only.
Use --check to validate committed derived CSV/JSON; --write to regenerate.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"docs/audits/2026-10-31_p234_b06_reason_classification_339.csv"
RAW=ROOT/"docs/audits/2026-10-31_p234_final_evidence_339.csv"
SCREEN=ROOT/"docs/audits/2026-10-31_project_source_screen_39.csv"
GRP=ROOT/"docs/audits/2026-10-31_c1_review_groups.csv"
P1=ROOT/"inputs/source_review_20261031/p1_13_positive_case_gate_decisions.csv"
FREEZE_APPROVAL=ROOT/"inputs/review_decisions/c0_source_freeze_signoffs_v1.csv"
GATE_APPROVAL=ROOT/"inputs/review_decisions/c1_c2_project_gate_signoffs_v1.csv"
PROJ_METADATA=ROOT/"inputs/review_decisions/c1_c2_project_identity_metadata_v1.csv"
OUT_C0=ROOT/"docs/audits/2026-10-31_c0_freeze_review_339.csv"
OUT_COHORT=ROOT/"docs/audits/2026-10-31_c1_c2_project_review_39.csv"
OUT_P1=ROOT/"docs/audits/2026-10-31_c1_p1_positive_case_crosswalk_13.csv"
OUT_SUM=ROOT/"docs/audits/2026-10-31_c0_c1_c2_policy_summary.json"
POLICY="C0_F1F2_COHORT_C1C2_V1_20261031"
SNAPSHOT="2026-10-29"

F1="F1_SOURCE_SCOPE_EVIDENCE_REVIEW"
F2="F2_NATIVE_SEARCH_PAUSE_CONSIDERATION"
GATES=("ID","ROLE","WINDOW","JORC","PANEL","GIS_RELEASE")
ROLES={
"REE_CLAIM_NEEDS_SAME_SCOPE_RESOURCE_ROLE_STAGE":"C0_PROJECT_RESOURCE_EVIDENCE_TRACK",
"GEOLOGICAL_CONTEXT_NOT_PROJECT":"C0_DOCUMENTED_GEOLOGICAL_CONTEXT",
"HISTORIC_OR_NON_TARGET_RESOURCE_CONTEXT":"C0_HISTORICAL_OR_NON_TARGET",
"CROSS_SCOPE_RESOURCE_OR_ID_TRANSFER_REJECTED":"C0_SCOPE_TRANSFER_REJECTED",
"NATIVE_FEATURE_ONLY_PROJECT_ROLE_NOT_VERIFIED":"C0_UNRESOLVED_NATIVE_ORIGINAL",
"PROJECT_ID_NAME_OR_GEOGRAPHY_CONFLICT":"C0_IDENTITY_CONFLICT",
"SAMPLED_TARGET_SPECIFIC_NEGATIVE_NOT_REGIONAL":"C0_LIMITED_NEGATIVE_RESULT",
"ORIGINAL_PUBLICATION_BYTES_ACCESS_BLOCKED":"C0_PRIMARY_PUBLICATION_ACCESS_BLOCK"
}

def check(ok,msg):
    if not ok:
        raise ValueError(msg)

def read_rows(path):
    with path.open(encoding="utf-8-sig",newline="") as fp:
        return list(csv.DictReader(fp))

def by_unique(rows,key):
    idx={r[key]:r for r in rows}
    check(len(idx)==len(rows),f"duplicate {key}")
    return idx

def signed_freeze(row,decision):
    """Only explicit complete source approval allows F1 or F2 signed status."""
    check(decision["freeze_class"] in {"F1_SOURCE_SCOPE_FROZEN","F2_NATIVE_SEARCH_PAUSED"},"unsupported freeze decision")
    expected=F1 if decision["freeze_class"].startswith("F1") else F2
    check(row["proposed_route"]==expected,"freeze class does not match candidate classification")
    for k in ("reviewer_id","approved_at","source_snapshot_sha256","evidence_document_ref",
              "page_or_section","scope_decision","reopen_trigger","rule_version","approval_ref"):
        check(bool(decision[k].strip()),f"missing signoff field {k}")
    check(decision["rule_version"]==POLICY,"freeze policy version mismatched")
    check(bool(row["selected_feature_sha256"]) and
          row["selected_feature_sha256"]==decision["source_snapshot_sha256"],
          "cannot sign without matching frozen source feature SHA")
    if expected==F2:
        check(not row["related_source_locator_ref"],"known unresolved report locator: F2 pause denied")
        check("NEGATIVE_SOURCE_SEARCH_LOG" in decision["evidence_document_ref"],
              "F2 requires explicit dated negative-search log ref")
        check(row["source_review_status"]=="NATIVE_FEATURE_ONLY","F2 only government native point")
    else:
        check(row["source_review_status"]=="ARCHIVED_RELEVANT_PAGES","F1 requires reviewed relevant originals")
        check(decision["scope_decision"] in {"GEO_CONTEXT_ONLY","HISTORIC_NON_TARGET",
             "SCOPE_TRANSFER_REJECTED"},"F1 decision must be bounded, not claim geological absence")
    return decision["freeze_class"]

def gates_with_signatures(decisions,project,metadata):
    """Require signatures and evidence for approved gate PASS; C2 needs ID+ROLE."""
    status={g:None for g in GATES}
    for d in decisions:
        gate=d["gate_id"]
        check(gate in GATES,"unknown C1/C2 gate")
        check(d["decision_status"] in {"PASS","HOLD","EXCLUDE"},"invalid gate decision")
        check(d["cohort"] in {"C1","C2"},"invalid cohort")
        check(d["source_asof"]==SNAPSHOT,"post-cutoff gate not allowed without new snapshot")
        for k in ("reason_code","document_id","original_sha256_or_html_ref",
                  "reviewer_id","reviewed_at","approval_ref"):
            check(bool(d[k].strip()),f"{gate}: unsigned or missing original source {k}")
        if d["cohort"]=="C1" and d["decision_status"]=="PASS":
            check(metadata is not None,"C1 requires verified Project metadata")
            keys={"ID":("verified_project_id","project_identity_scope","project_footprint_ref"),
                  "ROLE":("ree_product_role_ref",),
                  "WINDOW":("approved_study_document_id","study_published_asof"),
                  "JORC":("resource_statement_id","resource_basis","original_jorc_ref"),
                  "PANEL":("approved_panel_version",),
                  "GIS_RELEASE":("approved_gis_evidence_id",)}
            for k in keys[gate]:
                check(bool(metadata[k]),f"cannot PASS {gate} without {k}")
            if gate=="JORC":
                check(metadata["resource_basis"].upper() in {"TREO","REO_SCOPED_BREAKDOWN"},
                      "HM/THM/Y2O3-only figures cannot PASS JORC without approved REO conversion")
        if d["cohort"]=="C2" and d["decision_status"]=="PASS" and gate in {"ID","ROLE"}:
            check(metadata is not None and bool(metadata["verified_project_id"]) and
                  bool(metadata["project_identity_scope"]),"C2 cannot PASS without independently verified project ID")
            if gate=="ROLE":
                check(bool(metadata["ree_product_role_ref"]),"C2 REE product role missing")
        status[gate,d["cohort"]]=d["decision_status"]
    return status

def build():
    src,raw,screen,base_groups,p1,freezes,review_gates,metadata=map(
        read_rows,(SRC,RAW,SCREEN,GRP,P1,FREEZE_APPROVAL,GATE_APPROVAL,PROJ_METADATA))
    check(len(src)==len(raw)==339 and len(screen)==len(base_groups)==39 and len(p1)==13,
          "frozen 339/39/13 source universe changed")
    original=by_unique(raw,"target_id")
    by_unique(src,"target_id");by_unique(screen,"review_group_id")
    by_unique(base_groups,"review_group_id")
    freeze_by=by_unique(freezes,"target_id")
    metadata_by=by_unique(metadata,"review_group_id")
    review_by={}
    for d in review_gates:
        check(d["review_group_id"] in {x["review_group_id"] for x in screen},
              "unknown project group in independent gate")
        key=(d["review_group_id"],d["cohort"],d["gate_id"])
        check(key not in review_by,"duplicate gate signoff")
        review_by[key]=d
    results=[]
    for x in src:
        raw_row=original[x["target_id"]]
        check(x["source_snapshot"]==raw_row["frozen_snapshot"]==SNAPSHOT,
              "source snapshot changed")
        route="CONTINUE_EVIDENCE_REVIEW"
        gap="REQUIRES_NEW_SOURCE_EVIDENCE_OR_SCOPE"
        if x["C0_freeze_candidate_prior"]=="YES":
            route=F1;gap="BOUNDED_PRIMARY_RELEVANT_PAGES_REVIEWED_SIGNOFF_NEEDED"
        elif x["source_review_status"]=="NATIVE_FEATURE_ONLY":
            route=F2;gap=("KNOWN_LOCATOR_LEAD_CROSSWALK_REQUIRED" if x["new_b06_related_locator_id"]
                           else "NEGATIVE_SOURCE_SEARCH_LOG_AND_SOURCE_ID_QA_REQUIRED")
        elif x["source_review_status"]=="WEB_CACHED_TEXT_ONLY":
            route="C0_ACCESS_HOLD";gap="ORIGINAL_PUBLICATION_BYTES_MISSING"
        elif x["evidence_root_cause_code"]=="REE_CLAIM_NEEDS_SAME_SCOPE_RESOURCE_ROLE_STAGE":
            route="C0_ACTIVE_PROJECT_GATE_REVIEW";gap="OFFICIAL_PROJECT_STAGE_JORC_REO_EVIDENCE_REQUIRED"
        elif x["evidence_root_cause_code"]=="PROJECT_ID_NAME_OR_GEOGRAPHY_CONFLICT":
            route="C0_IDENTITY_RECONCILIATION";gap="SOURCE_NATIVE_POINT_OR_LEGAL_BOUNDARY_REQUIRED"
        row={
            "target_id":x["target_id"],"priority":x["priority"],"source_name":x["source_name"],
            "state":x["state"],"source_key":x["source_key"],"source_native_id":x["source_native_id"],
            "source_snapshot":SNAPSHOT,
            "selected_feature_sha256":raw_row.get("selected_feature_sha256",""),
            "source_evidence_reason":x["evidence_root_cause_code"],
            "source_review_status":x["source_review_status"],
            "proposed_route":route,"precheck_gap":gap,
            "related_source_locator_ref":x["new_b06_related_locator_id"],
            "exact_native_shared_search_key":x["P34_shared_native_search_key"],
            "evidence_page_or_section_verified":"PENDING_REVIEW","current_F1_F2_status":"NOT_APPLIED",
            "approval_ref":"","reviewer_id":"","reviewed_at":"","original_document_sha256_new":"",
            "reopen_trigger":"NEW_OFFICIAL_DOCUMENT_OR_MINE_TENURE_OR_REO_RESOURCE_OR_PROJECT_FOOTPRINT_OR_MATERIAL_CONTRADICTION",
            "reopened_at":"","C1_admitted":"NO","original_C0_target_preserved":"YES"
        }
        approved=freeze_by.get(x["target_id"])
        if approved:
            row["current_F1_F2_status"]=signed_freeze(row,approved)
            row["approval_ref"]=approved["approval_ref"]
            row["reviewer_id"]=approved["reviewer_id"]
            row["reviewed_at"]=approved["approved_at"]
            row["evidence_page_or_section_verified"]=approved["page_or_section"]
            row["reopen_trigger"]=approved["reopen_trigger"]
        results.append(row)
    check(len(results)==339,"source loss")
    cohort=[]
    base_by=by_unique(base_groups,"review_group_id")
    signed_by_group={}
    for d in review_gates:
        signed_by_group.setdefault(d["review_group_id"],[]).append(d)
    for x in screen:
        group=base_by[x["review_group_id"]]
        check(x["source_as_of"]==group["source_as_of_date"]==SNAPSHOT,
              "39 Group as-of mismatch")
        outside=x["screening_class"]=="OUTSIDE_PRE_FID_CONFIRMED"
        hold_role=x["screening_class"]=="REE_ROLE_HOLD"
        study=x["screening_class"]=="STUDY_DOCUMENTED_PRE_FID_SCREEN"
        priority=("C3_HISTORY_OUTSIDE_2026_PREFID" if outside else
                  "FIRST_C1_GATE_REVIEW" if study else
                  "FIRST_C1_STAGE_RECHECK" if x["screening_class"]=="STUDY_WINDOW_RECHECK" else
                  "C2_ROLE_EVIDENCE_FIRST" if hold_role else
                  "C2_OR_C0_PROJECT_IDENTITY_REVIEW")
        primary=x["source_review_depth"].startswith((
            "PRIMARY_PROJECT","PRIMARY_COMPANY","PRIMARY_GOVERNMENT"))
        c2_candidate=x["original_disposition"]=="INCLUDE_CANDIDATE" and primary and not hold_role and not outside
        row={
            "review_group_id":x["review_group_id"],"source_snapshot":SNAPSHOT,
            "project_name":x["project_name"],"state":x["state"],
            "original_disposition":x["original_disposition"],"screening_class":x["screening_class"],
            "source_review_depth":x["source_review_depth"],"original_source_url":x["public_source_url"],
            "original_evidence_finding":x["source_based_finding"],
            "resource_basis_screen":x["resource_basis_gate"],
            "source_group_activity_class":priority,
            "project_identity_evidence_assessed":("PRIMARY_PROJECT_OR_GOVERNMENT_TEXT" if primary
                                                  else "SOURCE_CONTEXT_REVIEW"),
            "ID_gate":"HOLD_INDEPENDENT_ID_SCOPE_SIGNOFF",
            "ROLE_gate":"HOLD_REE_PRODUCT_ROLE" if hold_role else "HOLD_REE_ROLE_INDEPENDENT_SIGNOFF",
            "WINDOW_gate":("SCREEN_OUTSIDE_PREFID_REQUIRE_DATED_SIGNOFF" if outside else
                "STUDY_SIGNAL_REQUIRE_ASOF_VERIFICATION" if study else "HOLD_DATED_ECONOMIC_STAGE"),
            "JORC_gate":"HOLD_SAME_SCOPE_REO_JORC_RECONCILIATION",
            "PANEL_gate":"HOLD_FIXED_SIX_DOMAIN_DATA_APPROVAL",
            "GIS_RELEASE_gate":"HOLD_PROJECT_FOOTPRINT_AND_OFFICIAL_GIS_QA",
            "formal_identity_signoff":"","approved_ree_resource_statement_id":"",
            "approved_stage_document_id":"","approved_panel_version":"","approved_gis_evidence_id":"",
            "C1_candidate_review_priority":priority,"C1_release_status":"NOT_ADMITTED_SIX_GATES_UNAPPROVED",
            "C2_identity_review_candidate":"YES" if c2_candidate else "NO",
            "C2_project_id_approved":"NO","C2_release_status":"NOT_ADMITTED_IDENTITY_SIGNOFF_PENDING",
            "C3_history_review":"C3_SOURCE_STAGE_SCREEN_ONLY" if outside else "NOT_YET_SCREENED_FOR_HISTORY",
            "next_gate_action":("Verify FID / first production published-as-of and preserve in historical cohort review" if outside else
                "Confirm REE product development/recovery role with original issuer document" if hold_role else
                "Read original economic study and 2026 project-scoped JORC REO statement before first gate" if study else
                "Verify Project identity/dated activity and distinguish REO, HM, Nb or other resource basis")
        }
        meta=metadata_by.get(x["review_group_id"])
        gate_status=gates_with_signatures(signed_by_group.get(x["review_group_id"],[]),x,meta)
        for gate in GATES:
            rec=review_by.get((x["review_group_id"],"C1",gate))
            if rec:
                row[f"{gate}_gate"]=rec["decision_status"]+"_"+rec["reason_code"]
        if meta:
            row["approved_ree_resource_statement_id"]=meta["resource_statement_id"]
            row["approved_stage_document_id"]=meta["approved_study_document_id"]
            row["approved_panel_version"]=meta["approved_panel_version"]
            row["approved_gis_evidence_id"]=meta["approved_gis_evidence_id"]
        c2_ok=(meta is not None and bool(meta["verified_project_id"]) and
               gate_status["ID","C2"]=="PASS" and gate_status["ROLE","C2"]=="PASS")
        if c2_ok:
            row["C2_project_id_approved"]="YES"
            row["formal_identity_signoff"]=review_by[x["review_group_id"],"C2","ID"]["approval_ref"]
            row["C2_release_status"]="C2_VERIFIED_PROJECT_ID_AND_REE_ROLE_ADMITTED"
        c1_all=all(gate_status[g,"C1"]=="PASS" for g in GATES)
        if c1_all:
            check(not outside,"project outside 2026 preFID cannot be C1")
            check(meta is not None and meta["verified_project_id"] and
                  meta["approved_panel_version"] and meta["approved_gis_evidence_id"],
                  "C1 metadata required")
            check(meta["resource_basis"] in {"TREO","REO_SCOPED_BREAKDOWN"},
                  "C1 requires source-scoped rare earth oxide basis")
            row["C1_release_status"]="C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES"
        cohort.append(row)
    p1rows=[]
    for x in p1:
        check(not x["approval_ref"],"P1 unexpected signed release, requires independent audit")
        p1rows.append({
            "case_id":x["case_id"],"source_asof":SNAPSHOT,"source_case_name":x["source_case_name"],
            "state":x["state"],"source_row_count":x["source_row_count"],
            "ree_role_source_finding":x["ree_role_evidence_assessment"],
            "resource_basis_original":x["mre_and_grade_basis"],
            "study_stage_original":x["economic_study_stage_asof"],
            "historic_parent_or_footprint_scope":x["legal_title_or_project_footprint_scope"],
            "ID_gate":x["ID_gate"],"ROLE_gate":x["ROLE_gate"],"WINDOW_gate":x["WINDOW_gate"],
            "JORC_gate":x["JORC_gate"],"PANEL_gate":x["PANEL_gate"],
            "GIS_RELEASE_gate":x["GIS_RELEASE_gate"],
            "same_project_as_39_group":"UNVERIFIED","matched_39_review_group_id":"",
            "unique_project_counted_as_new":"NO","approval_ref":x["approval_ref"],
            "C1_release_status":"NOT_ADMITTED_SIX_GATES_UNAPPROVED",
            "C2_status":"NOT_ADMITTED_IDENTITY_SIGNOFF_PENDING",
            "original_stage_source_url":x["stage_evidence_url"],
            "original_resource_source_url":x["resource_evidence_url"],
            "missing_critical_evidence":x["missing_critical_evidence"]
        })
    source_counts=Counter(r["proposed_route"] for r in results)
    stage_counts=Counter(r["screening_class"] for r in cohort)
    as_count=lambda v:dict(sorted(v.items()))
    f2=[r for r in results if r["proposed_route"]==F2]
    summary={
        "policy_version":POLICY,"snapshot_asof":SNAPSHOT,"C0_source_rows":339,
        "C0_priority_counts":as_count(Counter(r["priority"] for r in results)),
        "C0_freeze_route_counts":as_count(source_counts),
        "proposed_F1_candidates":source_counts[F1],
        "proposed_F2_native_search_pause_prechecks":source_counts[F2],
        "F2_with_b06_known_unresolved_locator_lead":sum(bool(x["related_source_locator_ref"]) for x in f2),
        "F2_without_b06_locator_lead_requiring_negative_search_log":sum(not x["related_source_locator_ref"] for x in f2),
        "signed_F1_closures":sum(x["current_F1_F2_status"]=="F1_SOURCE_SCOPE_FROZEN" for x in results),
        "signed_F2_pauses":sum(x["current_F1_F2_status"]=="F2_NATIVE_SEARCH_PAUSED" for x in results),
        "project_review_group_count":len(cohort),"screening_class_counts":as_count(stage_counts),
        "preFID_study_documented_first_review_queue":stage_counts["STUDY_DOCUMENTED_PRE_FID_SCREEN"],
        "preFID_stage_recheck_queue":stage_counts["STUDY_WINDOW_RECHECK"],
        "C2_identity_review_candidates":sum(x["C2_identity_review_candidate"]=="YES" for x in cohort),
        "independently_confirmed_C2_project_ids":sum(x["C2_project_id_approved"]=="YES" for x in cohort),
        "approved_C2_cohort_projects":sum(x["C2_release_status"].startswith("C2_VERIFIED") for x in cohort),
        "approved_C1_cohort_projects":sum(x["C1_release_status"].startswith("C1_ADMITTED") for x in cohort),
        "P1_positive_source_case_records":len(p1rows),"P1_distinct_project_additions_approved":0,
        "criteria_panel_selected":"NO" if not any(x["approved_panel_version"] for x in cohort) else "PENDING_PANEL_RELEASE_QA",
        "six_domain_C1_released":"YES" if any(x["C1_release_status"].startswith("C1_ADMITTED") for x in cohort) else "NO",
        "pipeline_policy_accepted":"YES_SOURCE_FREEZE_AND_STRICT_C1_C2_BOUNDARY",
        "formal_per_source_freeze_signatures":"NONE" if not freezes else "REQUIRES_PER_ROW_REVIEW"
    }
    check((len(cohort),len(p1rows),len(results))==(39,13,339),"row cardinality change")
    check(summary["proposed_F1_candidates"]==119 and summary["proposed_F2_native_search_pause_prechecks"]==151,
          "C0 freeze source tiers changed")
    check(summary["preFID_study_documented_first_review_queue"]==7 and
          summary["preFID_stage_recheck_queue"]==8,"39 preliminary stage profile changed")
    check(summary["F2_with_b06_known_unresolved_locator_lead"]==6,"known source locator flag changed")
    check(summary["C2_identity_review_candidates"]==28,"C2 review candidate count changed")
    return results,cohort,p1rows,summary

def csv_text(rs):
    fp=io.StringIO(newline="")
    writer=csv.DictWriter(fp,fieldnames=list(rs[0]),lineterminator="\n",quoting=csv.QUOTE_ALL)
    writer.writeheader();writer.writerows(rs)
    return fp.getvalue()

def run():
    parser=argparse.ArgumentParser(description=__doc__)
    flag=parser.add_mutually_exclusive_group(required=True)
    flag.add_argument("--check",action="store_true")
    flag.add_argument("--write",action="store_true")
    args=parser.parse_args()
    source,project,p1,summ=build()
    outputs={
        OUT_C0:csv_text(source),OUT_COHORT:csv_text(project),OUT_P1:csv_text(p1),
        OUT_SUM:json.dumps(summ,ensure_ascii=False,indent=2)+"\n"
    }
    for path,value in outputs.items():
        if args.write:
            path.write_text(value,encoding="utf-8")
        elif path==OUT_SUM:
            check(json.loads(path.read_text(encoding="utf-8"))==summ,
                  "derived policy summary mismatch")
        else:
            expected=list(csv.DictReader(io.StringIO(value)))
            check(read_rows(path)==expected,f"derived review CSV mismatch: {path}")
    print(f"PASS strict cohort policy: {len(source)} C0 sources; 119 F1/151 F2 candidates; "
          f"{len(project)} review groups, {len(p1)} P1 source cases; "
          f"{summ['approved_C1_cohort_projects']} approved C1, "
          f"{summ['approved_C2_cohort_projects']} approved C2")

if __name__=="__main__":
    run()
