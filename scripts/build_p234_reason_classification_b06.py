#!/usr/bin/env python3
"""Rebuild B06 fixed-source reason classification from manually reviewed evidence.

Never edits 2026-10-29 snapshots, B05 lineage, source approval or C1 cohorts.
Original public PDF text is documentary context, NOT proof of archived PDF bytes.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/audits/2026-10-31_p234_b05_source_triage_339.csv"
REVIEWS = ROOT / "inputs/source_review_20261031/p234_b06_p2_public_primary_reviews.csv"
RELATED = ROOT / "inputs/source_review_20261031/p234_b06_related_locator_cases.csv"
OUT = ROOT / "docs/audits/2026-10-31_p234_b06_reason_classification_339.csv"
SUMMARY = ROOT / "docs/audits/2026-10-31_p234_b06_reason_summary.json"

TERMINAL = {
    "DOCUMENTED_REE_CLAIM_SCOPE_HOLD": "REE_CLAIM_NEEDS_SAME_SCOPE_RESOURCE_ROLE_STAGE",
    "DOCUMENTED_GEO_CONTEXT_SCOPE_HOLD": "GEOLOGICAL_CONTEXT_NOT_PROJECT",
    "DOCUMENTED_NON_TARGET_OR_HISTORIC_SCOPE": "HISTORIC_OR_NON_TARGET_RESOURCE_CONTEXT",
    "DOCUMENTED_SCOPE_TRANSFER_REJECTED": "CROSS_SCOPE_RESOURCE_OR_ID_TRANSFER_REJECTED",
    "NATIVE_ONLY_PROJECT_REE_UNRESOLVED": "NATIVE_FEATURE_ONLY_PROJECT_ROLE_NOT_VERIFIED",
    "NAME_OR_GEOGRAPHY_UNRESOLVED": "PROJECT_ID_NAME_OR_GEOGRAPHY_CONFLICT",
    "TESTED_TARGET_NEGATIVE_ONLY": "SAMPLED_TARGET_SPECIFIC_NEGATIVE_NOT_REGIONAL",
    "WEB_ONLY_ORIGINAL_ACCESS_HOLD": "ORIGINAL_PUBLICATION_BYTES_ACCESS_BLOCKED",
}

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))

def assert_that(pred, msg):
    if not pred:
        raise AssertionError(msg)

def generate():
    previous = rows(BASE)
    reviews = rows(REVIEWS)
    locator = rows(RELATED)
    assert_that(len(previous) == 339 and len(reviews) == 4 and len(locator) == 8,
                "fixed 339 / 4 / 8 counts moved")
    assert_that(len({x["target_id"] for x in previous}) == 339, "duplicated baseline ID")
    by_id = {x["target_id"]: x for x in previous}
    by_review = {x["target_id"]: x for x in reviews}
    assert_that(len(by_review) == 4, "duplicated direct review")
    grouped = {}
    for x in locator:
        assert_that(x["target_id"] in by_id, "locator foreign ID")
        grouped.setdefault(x["target_id"], []).append(x)
        assert_that(x["same_native_feature_geospatial_match_approved"] == "NO",
                    "related report is NOT a source feature join")
        assert_that(x["original_technical_fulltext_verified"] == x["source_C1_admission"] == "NO",
                    "locator cannot grant fulltext or admission")
    for x in reviews:
        p = by_id[x["target_id"]]
        assert_that(p["priority"] == "P2" and p["source_review_status"] == "INHERITED_DESK_NO_NEW_ORIGINAL",
                    "source already reviewed at this level")
        assert_that(x["source_as_of"] == p["source_snapshot"] == "2026-10-29" and
                    x["source_name"] == p["source_name"], "source identity drift")
        assert_that(x["new_original_pdf_archived"] == "NO" and not x["original_pdf_sha256"] and
                    x["pdf_page_image_verified"] == x["technical_fulltext_verified"] == "NO",
                    "fabricated original/fulltext status")
        assert_that(x["independent_source_signoff"] == x["C1_admitted"] == x["MCDA_changed"] == "NO",
                    "illegal admission")
        assert_that(x["original_primary_url"].startswith("https://") and x["document_locator"],
                    "primary original URL or locator missing")
    results = []
    for x in previous:
        review = by_review.get(x["target_id"])
        related = grouped.get(x["target_id"], [None])[0]
        status = "PUBLIC_PRIMARY_TEXT_SCOPE_ONLY" if review else x["source_review_status"]
        if x["proposed_freeze_route"] == "SOURCE_SCOPE_CLOSURE_HUMAN_REVIEW_CANDIDATE":
            operational = "C0_DOCUMENTED_SCOPE_HUMAN_CLOSURE_SIGNATURE_PENDING"
        elif status == "NATIVE_FEATURE_ONLY":
            operational = "C0_EXACT_SOURCE_NATIVE_TECHNICAL_ORIGINAL_UNLINKED"
        elif status == "INHERITED_DESK_NO_NEW_ORIGINAL":
            operational = "P2_ORIGINAL_TECHNICAL_RECHECK_PENDING"
        elif status == "WEB_CACHED_TEXT_ONLY":
            operational = "WEB_ORIGINAL_BYTES_ACCESS_HOLD"
        elif x["baseline_terminal_evidence_status"] == "NAME_OR_GEOGRAPHY_UNRESOLVED":
            operational = "PROJECT_NAME_GEO_IDENTITY_CONFLICT"
        elif x["baseline_terminal_evidence_status"] == "DOCUMENTED_REE_CLAIM_SCOPE_HOLD":
            operational = "REE_CLAIM_REQUIRES_PROJECT_JORC_STAGE_GIS_SIGNOFF"
        else:
            operational = "PROJECT_ID_TITLE_SCOPE_OR_RESOURCE_GATE_OPEN"
        reason = TERMINAL.get(x["baseline_terminal_evidence_status"])
        assert_that(reason is not None and x["source_snapshot"] == "2026-10-29",
                    "unknown terminal status or snapshot changed")
        results.append({
            "target_id": x["target_id"], "priority": x["priority"], "source_name": x["source_name"],
            "state": x["state"], "source_key": x["source_key"], "source_native_id": x["source_native_id"],
            "source_snapshot": "2026-10-29", "evidence_root_cause_code": reason,
            "evidence_root_cause_original_code": x["baseline_terminal_evidence_status"],
            "source_review_status": status, "operational_blocker_code": operational,
            "new_b06_review_id": review["review_id"] if review else "",
            "new_b06_related_locator_id": related["locator_id"] if related else "",
            "new_source_evidence_url": review["original_primary_url"] if review else (
                related["related_source_url"] if related else ""),
            "new_bounded_finding": review["bounded_finding"] if review else (
                related["source_scoped_finding"] if related else ""),
            "resource_basis_annotation": review["resource_basis"] if review else "",
            "cross_source_consistency_issue": review["root_cause_annotation"] if review else (
                related["documentary_issue"] if related else ""),
            "original_pdf_sha256_new": "", "original_pdf_bytes_new": "NO", "PDF_visual_page_verified_new": "NO",
            "identity_approval": "NO", "source_freeze_approval": "NO",
            "C1_admitted": "NO", "formal_MCDA_changed": "NO",
            "C0_freeze_candidate_prior": "YES" if (
                x["proposed_freeze_route"] == "SOURCE_SCOPE_CLOSURE_HUMAN_REVIEW_CANDIDATE") else "NO",
            "P34_shared_native_search_key": x["source_native_shared_work_key"],
            "next_required_evidence": review["unresolved_evidence_and_reopen"] if review else (
                related["next_action"] if related else x["proposed_review_action"]),
        })
    cnt = lambda key: dict(Counter(x[key] for x in results))
    p2_text = sum(x["priority"] == "P2" and x["source_review_status"] == "PUBLIC_PRIMARY_TEXT_SCOPE_ONLY"
                  for x in results)
    remaining_p2 = sum(x["priority"] == "P2" and x["source_review_status"] == "INHERITED_DESK_NO_NEW_ORIGINAL"
                       for x in results)
    native_n = sum(x["source_review_status"] == "NATIVE_FEATURE_ONLY" for x in results)
    close_n = sum(x["C0_freeze_candidate_prior"] == "YES" for x in results)
    summary = {
        "execution_id": "P234-B06-CONTINUATION-REASON-CODES-20261031", "base_branch": "main",
        "snapshot_as_of": "2026-10-29", "new_evidence_review_date": "2026-10-31",
        "source_count": len(results), "priority_counts": cnt("priority"),
        "new_P2_bounded_primary_text": len(reviews), "P2_source_scoped_text_total": p2_text,
        "P2_remaining_desk_only": remaining_p2,
        "P3_remaining_native": sum(x["priority"] == "P3" and x["source_review_status"] == "NATIVE_FEATURE_ONLY" for x in results),
        "P4_remaining_native": sum(x["priority"] == "P4" and x["source_review_status"] == "NATIVE_FEATURE_ONLY" for x in results),
        "remaining_priority_source_rows": remaining_p2 + native_n,
        "remaining_P34_native_groups": 100, "remaining_priority_work_units": remaining_p2 + 100,
        "related_locator_rows": len(locator), "source_review_status_counts": cnt("source_review_status"),
        "evidence_root_cause_counts": cnt("evidence_root_cause_code"),
        "operational_blocker_counts": cnt("operational_blocker_code"),
        "original_C0_close_candidate_count": close_n, "formally_frozen_sources": 0,
        "C1_independent_approvals": 0, "new_original_pdf_bytes_archived": 0,
        "freeze_rule": "ADR-P0-028 PROPOSED, NOT_ACCEPTED"
    }
    assert_that(cnt("priority") == {"P3":216,"P4":95,"P2":28},
                "priority cohort drift")
    assert_that(p2_text == 20 and remaining_p2 == 8 and native_n == 151,
                "review completion change requires manual accounting")
    assert_that(len(locator) == 8 and close_n == 119, "source closure candidate drift")
    assert_that(summary["remaining_priority_source_rows"] == 159 and
                summary["remaining_priority_work_units"] == 108, "pending count drift")
    assert_that(all(x["identity_approval"] == x["source_freeze_approval"] ==
                    x["C1_admitted"] == x["formal_MCDA_changed"] == "NO" for x in results),
                "approval moved")
    return results, summary

def csv_content(rs):
    sink = io.StringIO(newline="")
    writer = csv.DictWriter(sink, fieldnames=list(rs[0]), quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rs)
    return sink.getvalue()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = ap.parse_args()
    rs, summary = generate()
    if args.write:
        OUT.write_text(csv_content(rs), encoding="utf-8")
        SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        assert_that(rows(OUT) == rs, "generated reason classification differs")
        with SUMMARY.open(encoding="utf-8") as file:
            assert_that(json.load(file) == summary, "generated summary differs")
    print("PASS B06: 339 unchanged, P2 20 scoped public texts / 8 desk, P3 87 P4 64 native, "
          "159 source follow-ups / 108 shared work units, 119 unsigned C0 candidates, C1=0")

if __name__ == "__main__":
    main()
