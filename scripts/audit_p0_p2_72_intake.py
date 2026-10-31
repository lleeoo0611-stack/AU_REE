#!/usr/bin/env python3
"""P2 Census source-priority intake (72 exact target IDs), 2026-10-29 frozen snapshot.

P2 here is the *source review priority* of the 487 census, NOT the research
implementation P2/Aim B-C milestone. All joins use immutable target_id, or
prior *review* group IDs as document context only. No automatic C1 promotion.
Python >= 3.11, stdlib only; fixed inputs, no network.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path("docs/audits/2026-10-31_census_487_batch_review.csv")
ROUND2 = Path("docs/audits/2026-10-31_487_evidence_round2_review.csv")
SCREEN = Path("docs/audits/2026-10-31_project_source_screen_39.csv")
P1 = Path("docs/audits/2026-10-31_p0_p1_73_terminal_decisions.csv")
LEADS = Path("inputs/source_review_20261031/p2_72_targeted_documentary_leads.csv")
OUT_SOURCE = Path("docs/audits/2026-10-31_p2_72_source_intake.csv")
OUT_CASE = Path("docs/audits/2026-10-31_p2_case_review_queue.csv")
OUT_SUMMARY = Path("docs/audits/2026-10-31_p2_72_intake_summary.json")
AS_OF = "2026-10-29"
STAMP = "2026-10-31"

SOURCE_FIELDS = [
    "target_id", "p2_case_key", "p2_review_case_label", "source_cohort",
    "state", "source_name", "source_native_id", "source_key",
    "source_entity_type", "original_inclusion_gate", "original_review_priority",
    "original_review_action", "review_group_id_NOT_APPROVED_PROJECT",
    "native_sha256_if_archived", "round2_native_record_locator",
    "source_coordinate_basis", "source_latitude", "source_longitude",
    "tenure_query_status", "documented_project_parent_status",
    "prior_p1_target_overlap", "round2_source_evidence_grade",
    "round2_external_source_url", "round2_external_source_locator",
    "screening_class_from_review_group",
    "review_group_public_url", "new_document_lead_id",
    "new_document_url", "new_document_publication_date",
    "new_document_locator", "new_document_supported_claim",
    "new_document_ore_mt_CASE_SCOPE_ONLY",
    "new_document_grade_CASE_SCOPE_ONLY",
    "new_document_grade_unit", "new_document_grade_basis",
    "resource_nesting_or_cutoff_caution", "economic_study_document_status",
    "project_identity_evidence_caution", "ree_product_evidence",
    "p2_documentary_progress", "p2_next_action",
    "verified_Project_polygon", "independent_project_approved",
    "independent_JORC_REO_approved", "C1_approved", "reviewer_signature"
]
CASE_FIELDS = [
    "p2_case_key", "case_type", "case_review_label", "state",
    "source_rows", "target_ids", "source_site_aliases",
    "original_action_types", "new_document_lead_id",
    "new_document_publication_date", "new_document_url",
    "project_or_resource_evidence_scope", "resource_grade_basis",
    "resource_nonaddition_rule", "economic_study_status",
    "documentary_stage", "source_group_evidence_only",
    "formal_project_approval", "formal_C1_approval",
    "case_next_action", "reviewer_signature"
]

def read(root: Path, path: Path) -> list[dict[str, str]]:
    with (root / path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def one_to_one(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    assert all(r[field] for r in rows), field
    d = {r[field]: r for r in rows}
    assert len(d) == len(rows), "Duplicate " + field
    return d

def build(root: Path = ROOT):
    original = read(root, BASE)
    prior = read(root, ROUND2)
    screenings = read(root, SCREEN)
    past_p1 = read(root, P1)
    new_leads = read(root, LEADS)
    assert len(original) == len(prior) == 487
    assert len(screenings) == 39 and len(past_p1) == 73
    # New source leads can be appended as review advances; counts are derived.
    assert len(new_leads) >= 1
    full = one_to_one(original, "target_id")
    rounds = one_to_one(prior, "target_id")
    screened = one_to_one(screenings, "review_group_id")
    past_ids = set(one_to_one(past_p1, "target_id"))
    assert set(full) == set(rounds)
    p2 = sorted((r for r in original if r["action_priority"] == "P2"),
                key=lambda r: r["target_id"])
    assert len(p2) == 72 and len({r["target_id"] for r in p2}) == 72
    assert not past_ids.intersection(r["target_id"] for r in p2)
    assert Counter(r["primary_review_action"] for r in p2) == {
        "CHECK_REE_RESOURCE_AND_COMPLETED_STUDY": 37,
        "ESTABLISH_DISTINCT_PROJECT_IDENTITY_AND_SOURCE_LINK": 25,
        "REVIEW_REE_ROLE_AND_INDEPENDENT_PROJECT_ID": 9,
        "VERIFY_CURRENT_ACTIVE_STATUS": 1
    }
    p2_targets = {r["target_id"] for r in p2}
    p2_groups = {r["reviewed_project_group_id"] for r in p2 if r["reviewed_project_group_id"]}
    by_group = {}
    by_target = {}
    for lead in new_leads:
        assert bool(lead["source_review_group_id"]) != bool(lead["target_id"])
        assert lead["source_url"].startswith("https://")
        assert re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", lead["document_publication_date"])
        assert lead["document_publication_date"] <= AS_OF
        assert lead["reported_grade_basis"] in {
            "TREO", "TREOY", "NOT_STATED_IN_SCOPED_SLIDE",
            "NO_REO_MRE_IN_SCOPED_SECTION", "NOT_VERIFIED"
        }
        if lead["source_review_group_id"]:
            key = lead["source_review_group_id"]
            assert key in p2_groups and key not in by_group
            by_group[key] = lead
        else:
            key = lead["target_id"]
            assert key in p2_targets and key not in by_target
            by_target[key] = lead
    assert len(by_group) + len(by_target) == len(new_leads)

    result = []
    cases = defaultdict(list)
    for row in p2:
        tid = row["target_id"]
        key = row["reviewed_project_group_id"]
        is_group = bool(key)
        case_id = "GRP:" + key if is_group else "SRC:" + tid
        screening = screened.get(key) if is_group else None
        assert not is_group or screening is not None
        roundrow = rounds[tid]
        lead = by_target.get(tid) or by_group.get(key)
        assert not (tid in by_target and key in by_group)
        hashval = roundrow["native_sha256"]
        assert not hashval or re.fullmatch(r"[0-9a-f]{64}", hashval)
        if lead:
            stage = "NEW_ISSUER_OR_GOV_DOCUMENT_LOCATED__CASE_SCOPE_ONLY"
            action = lead["next_gate"]
        elif screening and screening["public_source_url"]:
            stage = "INHERITED_REVIEW_GROUP_DOCUMENT_CONTEXT__UNAPPROVED"
            action = row["primary_review_action"] + "__VERIFY_ORIGINAL_CASE_SCOPE"
        else:
            stage = "INHERITED_TRACE_OR_SOURCE_LEAD_ONLY"
            action = row["primary_review_action"] + "__DOCUMENTARY_REVIEW_REQUIRED"
        result.append({
            "target_id": tid, "p2_case_key": case_id,
            "p2_review_case_label": screening["project_name"] if screening else row["source_record_name"],
            "source_cohort": row["cohort"],
            "state": row["state"], "source_name": row["source_record_name"],
            "source_native_id": row["source_native_id"], "source_key": row["source_key"],
            "source_entity_type": row["source_entity_type"],
            "original_inclusion_gate": row["original_inclusion_gate"],
            "original_review_priority": row["action_priority"],
            "original_review_action": row["primary_review_action"],
            "review_group_id_NOT_APPROVED_PROJECT": key,
            "native_sha256_if_archived": hashval,
            "round2_native_record_locator": roundrow["native_record_locator"],
            "source_coordinate_basis": row["original_coordinate_basis"],
            "source_latitude": row["latitude"], "source_longitude": row["longitude"],
            "tenure_query_status": row["tenure_trace_status"],
            "documented_project_parent_status": row["group_link_relation"],
            "prior_p1_target_overlap": "NO",
            "round2_source_evidence_grade": roundrow["round2_evidence_grade"],
            "round2_external_source_url": roundrow["round2_source_url"],
            "round2_external_source_locator": roundrow["round2_source_locator"],
            "screening_class_from_review_group": screening["screening_class"] if screening else "",
            "review_group_public_url": screening["public_source_url"] if screening else "",
            "new_document_lead_id": lead["lead_id"] if lead else "",
            "new_document_url": lead["source_url"] if lead else "",
            "new_document_publication_date": lead["document_publication_date"] if lead else "",
            "new_document_locator": lead["source_locator"] if lead else "",
            "new_document_supported_claim": lead["supported_claim"] if lead else "",
            "new_document_ore_mt_CASE_SCOPE_ONLY": lead["reported_ore_mt"] if lead else "",
            "new_document_grade_CASE_SCOPE_ONLY": lead["reported_grade_value"] if lead else "",
            "new_document_grade_unit": lead["reported_grade_unit"] if lead else "",
            "new_document_grade_basis": lead["reported_grade_basis"] if lead else "",
            "resource_nesting_or_cutoff_caution": lead["resource_scope_and_nesting"] if lead else "",
            "economic_study_document_status": lead["economic_study_status_in_scoped_source"] if lead else "",
            "project_identity_evidence_caution": lead["spatial_or_identity_interpretation"] if lead else "",
            "ree_product_evidence": lead["REE_role_evidence"] if lead else "",
            "p2_documentary_progress": stage,
            "p2_next_action": action,
            "verified_Project_polygon": "NO",
            "independent_project_approved": "NO",
            "independent_JORC_REO_approved": "NO",
            "C1_approved": "NO",
            "reviewer_signature": ""
        })
        cases[case_id].append((row, lead))

    result.sort(key=lambda r: (r["p2_case_key"], r["target_id"]))
    case_rows = []
    for case_id, pairs in cases.items():
        rows = [r for r, _ in pairs]
        source_ids = [r["target_id"] for r in rows]
        screening = screened.get(rows[0]["reviewed_project_group_id"]) if case_id.startswith("GRP:") else None
        leads = {x["lead_id"]: x for _, x in pairs if x}
        assert len(leads) <= 1, case_id
        lead = next(iter(leads.values())) if leads else None
        case_rows.append({
            "p2_case_key": case_id,
            "case_type": "PREVIOUS_REVIEW_GROUP_NOT_PROJECT" if screening else "ONE_UNLINKED_SOURCE_ROW",
            "case_review_label": screening["project_name"] if screening else rows[0]["source_record_name"],
            "state": rows[0]["state"],
            "source_rows": len(rows),
            "target_ids": "|".join(sorted(source_ids)),
            "source_site_aliases": "|".join(sorted({r["source_record_name"] for r in rows})),
            "original_action_types": "|".join(sorted({r["primary_review_action"] for r in rows})),
            "new_document_lead_id": lead["lead_id"] if lead else "",
            "new_document_publication_date": lead["document_publication_date"] if lead else "",
            "new_document_url": lead["source_url"] if lead else "",
            "project_or_resource_evidence_scope": lead["supported_claim"] if lead else "",
            "resource_grade_basis": lead["reported_grade_basis"] if lead else "",
            "resource_nonaddition_rule": lead["resource_scope_and_nesting"] if lead else "",
            "economic_study_status": lead["economic_study_status_in_scoped_source"] if lead else "",
            "documentary_stage": "CASE_DOCUMENT_LEAD_REVIEWED_NO_APPROVAL" if lead else
                "PREVIOUS_GROUP_SOURCE_CONTEXT" if screening else "SOURCE_UNLINKED_REVIEW_PENDING",
            "source_group_evidence_only": "YES",
            "formal_project_approval": "NO",
            "formal_C1_approval": "NO",
            "case_next_action": lead["next_gate"] if lead else
                "|".join(sorted({r["primary_review_action"] for r in rows})),
            "reviewer_signature": ""
        })
    case_rows.sort(key=lambda r: r["p2_case_key"])
    assert len(result) == 72
    assert all(r["C1_approved"] == "NO" for r in result)
    assert all(r["prior_p1_target_overlap"] == "NO" for r in result)
    assert all(r["verified_Project_polygon"] == "NO" for r in result)
    assert sum(int(c["source_rows"]) for c in case_rows) == 72
    assert len({r["p2_case_key"] for r in case_rows}) == len(case_rows)
    assert len({r["target_id"] for r in result}) == 72
    assert set(r["new_document_lead_id"] for r in result if r["new_document_lead_id"]) == {
        x["lead_id"] for x in new_leads
    }
    summary = {
        "audit_date": STAMP, "frozen_as_of": AS_OF,
        "scope": "487-census P2 source-review priority; not research P2/Aim B-C",
        "original_census_rows": 487,
        "p2_frozen_source_rows": len(result),
        "p2_distinct_review_case_keys": len(case_rows),
        "p2_reviewed_group_cases": sum(r["case_type"] == "PREVIOUS_REVIEW_GROUP_NOT_PROJECT" for r in case_rows),
        "p2_unlinked_source_cases": sum(r["case_type"] == "ONE_UNLINKED_SOURCE_ROW" for r in case_rows),
        "prior_p1_73_exact_target_overlaps": 0,
        "original_p2_action_counts": dict(sorted(Counter(r["original_review_action"] for r in result).items())),
        "source_rows_with_new_document_context": sum(bool(r["new_document_lead_id"]) for r in result),
        "distinct_case_documentary_leads": len(new_leads),
        "p2_case_documentary_leads": sum(bool(r["new_document_lead_id"]) for r in case_rows),
        "document_progress_counts": dict(sorted(Counter(r["p2_documentary_progress"] for r in result).items())),
        "c1_approved": 0, "project_footprints_approved": 0,
        "source_scope_review": "GROUP_DOCUMENT_CONTEXT_ONLY_NOT_POINT_TO_PROJECT_PROOF",
        "stage_gate": "P2_INTAKE_COMPLETE_TARGETED_PRIMARY_LEADS_ADDED_NOT_CASE_CLOSED",
        "inputs": [str(x) for x in (BASE, ROUND2, SCREEN, P1, LEADS)],
        "outputs": [str(x) for x in (OUT_SOURCE, OUT_CASE, OUT_SUMMARY)],
        "warnings": [
            "P2 here is a work queue, not the v2 research phase P2 Aim B/C.",
            "Review group IDs and matching names do not constitute Project approvals.",
            "Original Legacy source records may not have a 64-char native SHA; blanks are preserved.",
            "A disclosed group Mineral Resource cannot be duplicated among multiple source rows.",
            "TREOY and TREO are separate source-reported basis labels; nested grades cannot be summed.",
            "Reports and company web URLs are source locators, not an independently archived original-file SHA.",
            "No formal Project, JORC, GIS, C1 or MCDA rankings are released."
        ]
    }
    return result, case_rows, summary

def write_rows(path: Path, rows: list[dict[str, str]], fields: list[str]):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--write", action="store_true")
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    sources, cases, stats = build(ROOT)
    if args.write:
        write_rows(ROOT / OUT_SOURCE, sources, SOURCE_FIELDS)
        write_rows(ROOT / OUT_CASE, cases, CASE_FIELDS)
        (ROOT / OUT_SUMMARY).write_text(
            json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    if args.check:
        assert read(ROOT, OUT_SOURCE) == sources, OUT_SOURCE
        assert read(ROOT, OUT_CASE) == [
            {k: str(r[k]) for k in CASE_FIELDS} for r in cases
        ], OUT_CASE
        assert json.loads((ROOT / OUT_SUMMARY).read_text(encoding="utf-8")) == stats
    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
