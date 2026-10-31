#!/usr/bin/env python3
"""Rebuild P3/P4 provenance triage, P2 identity crosswalk and C1 readiness; never auto-approve."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "audits"
INPUTS = {
    "base": AUDIT / "2026-10-31_census_487_batch_review.csv",
    "round2": AUDIT / "2026-10-31_487_evidence_round2_review.csv",
    "p1": AUDIT / "2026-10-31_p1_73_source_resolution.csv",
    "p2": AUDIT / "2026-10-31_p2_28_public_terminal_desk_review.csv",
    "c1": ROOT / "inputs/source_review_20261031/p1_13_positive_case_gate_decisions.csv",
    "cases": AUDIT / "2026-10-31_p1_44_case_resolution.csv",
    "resource": AUDIT / "2026-10-31_p1_48_resource_basis_review.csv",
}
OUT = {
    "p3p4": AUDIT / "2026-10-31_p3_p4_311_provenance_audit.csv",
    "p2": AUDIT / "2026-10-31_p2_28_identity_crosswalk.csv",
    "c1": AUDIT / "2026-10-31_c1_13_independent_gate_readiness.csv",
    "summary": AUDIT / "2026-10-31_412_followup_gates_summary.json",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def provenance_grade(grade: str) -> str:
    exact = {
        "NATIVE_RECORD_ONLY": "OFFICIAL_NATIVE_RECORD_ONLY",
        "GOV_HISTORICAL_GEO_CONTEXT_LOCATED": "HISTORICAL_GEOLOGY_CONTEXT_NOT_PROJECT",
        "ARCHIVED_TEXT_LOCATOR_CANDIDATE": "ARCHIVED_TEXT_NOT_PRIMARY_BYTES",
        "URL_NO_TEXT_LOCATOR": "URL_NO_DIRECT_SOURCE_LOCATOR",
        "SOURCE_RECORD_NOT_RECOVERED": "NATIVE_SOURCE_RECOVERY_REQUIRED",
        "DOCUMENT_REVIEW_NOT_DIRECT": "DOCUMENT_NOT_DIRECT_PROJECT_SCOPE",
    }
    if grade in exact:
        return exact[grade]
    if "NATIVE_UNRECOVERED" in grade:
        return "EXTERNAL_POINTER_NATIVE_RECOVERY_REQUIRED"
    if "AMBIGUOUS" in grade:
        return "NATIVE_ID_AMBIGUITY_REVIEW"
    if "PROJECT_OR_PROSPECT_DOCUMENT" in grade or "OFFICIAL_RESOURCE_SUMMARY" in grade:
        return "DOCUMENTARY_PROJECT_LEAD_NOT_APPROVED"
    return "SOURCE_CONTEXT_REVIEW_REQUIRED"


def generate() -> tuple[list[dict], list[dict], list[dict], dict]:
    data = {key: read(path) for key, path in INPUTS.items()}
    hold = [r for r in data["base"] if r["original_inclusion_gate"] ==
            "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE"]
    base = {r["target_id"]: r for r in data["base"]}
    p1 = {r["target_id"] for r in data["p1"]}
    p2 = {r["target_id"] for r in data["p2"]}
    hold_ids = {r["target_id"] for r in hold}
    assert len(hold) == len(hold_ids) == 412
    assert len(p1) == 73 and len(p2) == 28 and not (p1 & p2)
    assert p1 | p2 <= hold_ids
    round2 = {r["target_id"]: r for r in data["round2"]}
    out311 = []
    for b in hold:
        if b["target_id"] in p1 or b["target_id"] in p2:
            continue
        r = round2[b["target_id"]]
        priority = "P4" if b["source_entity_type"] == "OCCURRENCE" else "P3"
        out311.append({
            "target_id": b["target_id"], "priority": priority, "state": b["state"],
            "source_record_name": b["source_record_name"], "source_key": b["source_key"],
            "source_native_id": b["source_native_id"], "source_entity_type": b["source_entity_type"],
            "source_record_lookup_status": b["source_record_lookup_status"],
            "round2_native_match_status": r["archived_native_match_status"],
            "source_native_chunk_sha256": r["native_sha256"],
            "source_native_locator": r["native_record_locator"],
            "round2_evidence_grade": r["round2_evidence_grade"],
            "round2_evidence_class": r["round2_evidence_kind"],
            "round2_source_url": r["round2_source_url"] or r["additional_source_url"],
            "round2_source_locator": r["round2_source_locator"] or r["additional_document_locator"],
            "source_provenance_grade": provenance_grade(r["round2_evidence_grade"]),
            "project_identity_gate": "HOLD_NOT_INDEPENDENTLY_APPROVED",
            "REE_product_gate": "HOLD_NOT_PROJECT_SCOPED",
            "JORC_REO_gate": "HOLD_NOT_APPROVED", "C1_gate": "NO",
            "evidence_scope": ("C0_GEOLOGICAL_OCCURRENCE_NOT_PROJECT" if priority == "P4"
                               else "C0_DEPOSIT_OR_PROSPECT_PARENT_UNRESOLVED"),
            "next_document_action": (
                "Check original geological occurrence; require dated Project parent and REE product source before any Project-level promotion."
                if priority == "P4" else
                "Verify source-native feature and dated Project/Deposit/title polygon; obtain project-scoped REE resource/stage original document and reviewer signoff."),
        })
    out311.sort(key=lambda x: x["target_id"])
    assert len(out311) == 311 and Counter(x["priority"] for x in out311) == {"P3": 216, "P4": 95}

    outp2 = []
    for x in data["p2"]:
        b = base[x["target_id"]]
        assert x["target_id"] in hold_ids
        outp2.append({
            "target_id": x["target_id"], "case_id": x["case_id"],
            "state": x["state"], "source_name": x["source_name"],
            "baseline_entity_type": b["source_entity_type"],
            "baseline_source_key": b["source_key"],
            "baseline_source_native_id": b["source_native_id"],
            "baseline_source_lookup_status": b["source_record_lookup_status"],
            "baseline_native_sha256": x["native_feature_sha256"],
            "case_documentary_verdict": x["scoped_documentary_verdict"],
            "government_or_issuer_url": x["primary_or_lead_url"],
            "publication_date": x["document_date"],
            "source_locator": x["document_locator"],
            "reported_tenements": x["tenement_numbers"],
            "REE_resource_basis": x["REE_or_resource_basis"],
            "study_stage": x["project_stage_supported"],
            "source_identity_crosswalk": ("LEGACY_UUID_RETAINED_NATIVE_JOIN_PENDING"
                                          if x["target_id"].startswith("LEGACY:")
                                          else "NATIVE_FEATURE_RETAINED_PARENT_JOIN_PENDING"),
            "source_to_project_geometry": "NOT_INDEPENDENTLY_VERIFIED",
            "original_primary_doc_sha256": x["original_pdf_SHA256_if_archived"],
            "project_identity_gate": "HOLD_NO_INDEPENDENT_SIGNOFF",
            "JORC_REO_gate": "HOLD_NO_PROJECT_SCOPED_JORC_APPROVAL",
            "C1_gate": "NO", "reviewer_signature": "",
            "next_action": x["remaining_action"],
        })
    outp2.sort(key=lambda x: x["target_id"])
    assert len(outp2) == 28 and len({x["case_id"] for x in outp2}) == 27

    cases = {x["case_id"]: x for x in data["cases"]}
    p1cases = defaultdict(list)
    for x in data["p1"]:
        p1cases[x["case_id"]].append(x)
    res = defaultdict(list)
    for x in data["resource"]:
        res[x["provisional_group_key"]].append(x)
    outc1 = []
    for x in data["c1"]:
        src = p1cases[x["case_id"]]
        assert x["case_id"] in cases and len(src) == int(x["source_row_count"])
        r = res[x["case_id"]]
        outc1.append({
            "case_id": x["case_id"], "project_candidate": x["source_case_name"],
            "state": x["state"], "source_target_count": str(len(src)),
            "source_target_ids": "|".join(sorted(v["target_id"] for v in src)),
            "crosschecked_case_description": cases[x["case_id"]]["supported_claim"],
            "original_ree_role": x["ree_role_evidence_assessment"],
            "original_resource_basis": x["mre_and_grade_basis"],
            "reviewed_JORC_claim_ids": "|".join(v["statement_id"] for v in r),
            "reviewed_JORC_basis_list": "|".join(v["grade_basis"] for v in r),
            "study_asof": x["economic_study_stage_asof"],
            "stage_source_url": x["stage_evidence_url"],
            "resource_source_url": x["resource_evidence_url"],
            "original_critical_gap": x["missing_critical_evidence"],
            **{k: x[k] for k in (
                "ID_gate", "ROLE_gate", "WINDOW_gate", "JORC_gate", "PANEL_gate", "GIS_RELEASE_gate")},
            "original_primary_pdf_sha256": "", "independent_reviewer_signature": "",
            "final_Project_approval": "NO", "final_JORC_approval": "NO", "C1_admitted": "NO",
            "release_decision": "HOLD_P0_INDEPENDENT_EVIDENCE_SIGNOFF_REQUIRED",
        })
    outc1.sort(key=lambda x: x["case_id"])
    assert len(outc1) == 13 and sum(int(x["source_target_count"]) for x in outc1) == 22

    count = lambda rows, field: dict(sorted(Counter(x[field] for x in rows).items()))
    summary = {
        "audit_date": "2026-10-31", "frozen_source_asof": "2026-10-29",
        "repository": "lleeoo0611-stack/AU_REE",
        "input_reference_commit": "ac1735da2d13e32039cde504d8fa4fcf563d1623",
        "scope": "Original 412 HOLD source target IDs, not unique mining Projects",
        "counts": {
            "original_HOLD": len(hold), "P1_source_desk_closed": len(p1),
            "P2_public_documentary_closed": len(p2),
            "P3_source_provenance_triage": sum(x["priority"] == "P3" for x in out311),
            "P4_occurrence_provenance_triage": sum(x["priority"] == "P4" for x in out311),
            "all_source_ids_accounted_for": len(hold),
        },
        "P3_state_distribution": count([x for x in out311 if x["priority"] == "P3"], "state"),
        "P4_state_distribution": count([x for x in out311 if x["priority"] == "P4"], "state"),
        "P3_P4_provenance_grades": count(out311, "source_provenance_grade"),
        "C1_case_count": len(outc1), "C1_source_row_count": 22,
        "C1_independent_approvals": 0,
        "C1_nonapproval_reason": "Original primary PDF bytes+SHA, project-footprint joins, project-scoped REO JORC, completed pre-FID study, six-domain panel and independent reviewer signoff not complete.",
        "P2_source_rows": len(outp2),
        "P2_distinct_case_ids": len({x["case_id"] for x in outp2}),
        "P2_legacy_rows": sum(x["target_id"].startswith("LEGACY:") for x in outp2),
        "P2_native_rows": sum(not x["target_id"].startswith("LEGACY:") for x in outp2),
        "PR33_note": "PR #33 draft covers historic action_priority=P2 72-source tranche; not merged or counted as the 28-source HOLD P2 tranche.",
        "input_paths": [str(p.relative_to(ROOT)) for p in INPUTS.values()],
        "status": "C0_PROVENANCE_AUDITED; C1_NOT_RELEASED; NO_FORMAL_NEW_PROJECT_APPROVAL",
    }
    return out311, outp2, outc1, summary


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    p3p4, p2, c1, summary = generate()
    if args.write:
        for key, rows in (("p3p4", p3p4), ("p2", p2), ("c1", c1)):
            write_csv(OUT[key], rows)
        OUT["summary"].write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
        return
    for key, expected in (("p3p4", p3p4), ("p2", p2), ("c1", c1)):
        observed = read(OUT[key])
        assert observed == expected, f"{key} source-level export differs from reproducible input"
    archived = json.loads(OUT["summary"].read_text(encoding="utf-8"))
    assert archived == summary, "Summary no longer matches source-level audits"
    print("PASS: 412 HOLD partition (73/28/216/95), 311 provenance rows, 28 P2 identity rows, 13 C1 gates; 0 C1 admissions")


if __name__ == "__main__":
    main()
