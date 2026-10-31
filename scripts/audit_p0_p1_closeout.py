#!/usr/bin/env python3
"""P0/P1: immutable 73-source desk closeout; no inferred Project/C1 admission.

Regenerates explicit desk-review disposition from government-native source rows,
documentary scope decisions, official tenure overlaps, and 13 positive C1 gate holds.
Does not manufacture independent review, original government PDF SHA, polygons,
or economic feasibility study. Python 3.11+ standard library only.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = Path("docs/audits/2026-10-31_p1_73_source_resolution.csv")
CASES = Path("docs/audits/2026-10-31_p1_44_case_resolution.csv")
TENURE = Path("docs/audits/2026-10-31_p1_73_tenure_reconciliation.csv")
POSITIVE = Path("inputs/source_review_20261031/p1_13_positive_case_gate_decisions.csv")
OUT = Path("docs/audits/2026-10-31_p0_p1_73_terminal_decisions.csv")
SUMMARY = Path("docs/audits/2026-10-31_p0_p1_closeout_summary.json")

FIELDS = [
    "target_id", "case_id", "source_name", "state", "source_key",
    "source_native_id", "native_chunk_sha256", "source_latitude",
    "source_longitude", "p1_source_category", "p1_desk_review_status",
    "p1_evidence_disposition", "p1_terminal_routing",
    "census_cohort", "independent_C1_admission", "independent_project_id_approved",
    "independent_JORC_REO_approved", "source_documentary_url",
    "document_publication_date", "document_locator",
    "document_supported_claim", "REE_product_evidence",
    "JORC_or_resource_basis_scope", "documented_stage",
    "source_title_overlap_status", "observed_tenement_titles",
    "documented_tenement_exact_matches", "legal_project_footprint_verified",
    "ID_gate", "ROLE_gate", "WINDOW_gate", "JORC_gate",
    "PANEL_gate", "GIS_RELEASE_gate", "primary_pdf_archive_status",
    "unresolved_item", "case_reopen_condition", "human_reviewer_signature",
]
CLASS_MAP = {
    "DOCUMENTARY_CLAIM_EVIDENCED__GIS_AND_APPROVAL_PENDING":
        ("C0_POSITIVE_PROJECT_OR_REE_LEAD", "C1_GATES_NOT_SATISFIED"),
    "SOURCE_REVIEWED__NO_REE_PRODUCT_PROOF_IN_SOURCES":
        ("C0_NO_PROJECT_SCOPED_REE_PRODUCT_PROOF", "SEARCH_SCOPE_CLOSED_REOPEN_ON_NEW_DOCUMENT"),
    "ORIGINAL_TECHNICAL_SOURCE_REJECTS_REE_MRE_INHERITANCE":
        ("C0_EXPLICIT_RESOURCE_SCOPE_EXCLUSION", "DO_NOT_INHERIT_OTHER_DEPOSIT_MRE"),
    "IDENTITY_CONFLICT_DOCUMENTED__NO_AUTOMERGE":
        ("C0_UNRESOLVED_NATIVE_IDENTITY_CONFLICT", "NATIVE_GEOMETRY_CORRECTION_REQUIRED"),
    "REPORT_INDEX_FOUND__OFFICIAL_PDF_NOT_RETRIEVED":
        ("C0_INDEXED_PRIMARY_DOCUMENT_ACCESS_BLOCKED", "OFFICIAL_PDF_SHA_REQUIRED"),
}
assert len(CLASS_MAP) == 5

def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def build(root: Path = ROOT):
    source = read(root / SOURCES)
    cases = read(root / CASES)
    tenure = read(root / TENURE)
    positives = read(root / POSITIVE)
    assert len(source) == len(tenure) == 73
    assert len(cases) == 44 and len(positives) == 13
    assert len({x["target_id"] for x in source}) == 73
    assert len({x["case_id"] for x in cases}) == 44
    pos = {x["case_id"]: x for x in positives}
    ten = {x["target_id"]: x for x in tenure}
    assert len(ten) == 73 and len(pos) == 13
    case_by_id = {x["case_id"]: x for x in cases}
    count_by_case = Counter(x["case_id"] for x in source)
    assert all(int(x["source_row_count"]) == count_by_case[x["case_id"]] for x in cases)
    positive_sources = [x for x in source if x["documentary_verdict"] ==
                        "DOCUMENTARY_CLAIM_EVIDENCED__GIS_AND_APPROVAL_PENDING"]
    assert len(positive_sources) == 22
    assert {x["case_id"] for x in positive_sources} == set(pos)
    assert sum(int(x["source_row_count"]) for x in positives) == 22

    rows = []
    for src in source:
        case = case_by_id[src["case_id"]]
        t = ten[src["target_id"]]
        positive = pos.get(src["case_id"])
        assert src["C1_approved"] == t["C1_approved"] == "NO"
        assert src["independent_JORC_REO_approved"] == "NO"
        assert t["project_or_mine_footprint_intersected"] == "NOT_TESTED"
        assert len(src["native_chunk_sha256"]) == 64
        assert src["documentary_verdict"] in CLASS_MAP
        cls, terminal = CLASS_MAP[src["documentary_verdict"]]
        pdf_status = ("WAMEX_INDEX_REPORT_KNOWN_OFFICIAL_PDF_NOT_ARCHIVED"
                      if src["documentary_verdict"] ==
                         "REPORT_INDEX_FOUND__OFFICIAL_PDF_NOT_RETRIEVED"
                      else "EXTERNAL_DOCUMENT_LINK_ONLY_NOT_HASH_ARCHIVED")
        # Positive source must link to a reviewed case-level six-gate dossier.
        if positive:
            assert all(positive[x] for x in ("ID_gate", "ROLE_gate", "WINDOW_gate",
                                             "JORC_gate", "PANEL_gate", "GIS_RELEASE_gate"))
            gates = [positive[k] for k in ("ID_gate", "ROLE_gate", "WINDOW_gate",
                                          "JORC_gate", "PANEL_gate", "GIS_RELEASE_gate")]
        else:
            gates = ["HOLD_NOT_EVALUATED_FORMAL_C1"] * 6
        if cls == "C0_UNRESOLVED_NATIVE_IDENTITY_CONFLICT":
            reopen = "Obtain official native feature and dated project polygon; resolve conflicting state/site coordinates."
        elif cls == "C0_INDEXED_PRIMARY_DOCUMENT_ACCESS_BLOCKED":
            reopen = "Request original WAMEX PDF from WA government; preserve SHA256, release date and page citation."
        elif cls == "C0_POSITIVE_PROJECT_OR_REE_LEAD":
            reopen = positive["missing_critical_evidence"]
        elif cls == "C0_EXPLICIT_RESOURCE_SCOPE_EXCLUSION":
            reopen = "Reopen only if independent Benmara South TREO Mineral Resource appears; do not inherit Barkly/Vanadis MRE."
        else:
            reopen = ("Review only when a dated, project-scoped REE recovery statement or "
                      "compatible JORC REO resource and valid pre-FID economic study is supplied.")
        rows.append({
            "target_id": src["target_id"], "case_id": src["case_id"],
            "source_name": src["source_name"], "state": src["state"],
            "source_key": src["source_key"],
            "source_native_id": src["source_native_id"],
            "native_chunk_sha256": src["native_chunk_sha256"],
            "source_latitude": src["latitude"], "source_longitude": src["longitude"],
            "p1_source_category": src["p1_source_category"],
            "p1_desk_review_status": "CLOSED_DOCUMENTARY_SEARCH_SCOPE_DEFINED",
            "p1_evidence_disposition": cls, "p1_terminal_routing": terminal,
            "census_cohort": "C0_ONLY_NOT_ADMITTED",
            "independent_C1_admission": "NO",
            "independent_project_id_approved": "NO",
            "independent_JORC_REO_approved": "NO",
            "source_documentary_url": src["evidence_url"],
            "document_publication_date": src["evidence_publication_date"],
            "document_locator": src["source_locator"],
            "document_supported_claim": src["supported_claim"],
            "REE_product_evidence": src["REE_role_evidence"],
            "JORC_or_resource_basis_scope": src["resource_basis_evidence"],
            "documented_stage": src["historic_or_current_stage"],
            "source_title_overlap_status": t["official_tenure_query_status"],
            "observed_tenement_titles": t["official_tenement_numbers_at_point"],
            "documented_tenement_exact_matches": t["exact_title_matches"],
            "legal_project_footprint_verified": "NO_NOT_PERFORMED",
            "ID_gate": gates[0], "ROLE_gate": gates[1],
            "WINDOW_gate": gates[2], "JORC_gate": gates[3],
            "PANEL_gate": gates[4], "GIS_RELEASE_gate": gates[5],
            "primary_pdf_archive_status": pdf_status,
            "unresolved_item": case["source_spatial_identity"],
            "case_reopen_condition": reopen,
            "human_reviewer_signature": ""
        })
    rows.sort(key=lambda r: (r["case_id"], r["target_id"]))
    dispositions = dict(sorted(Counter(x["p1_evidence_disposition"] for x in rows).items()))
    assert dispositions == {
        "C0_EXPLICIT_RESOURCE_SCOPE_EXCLUSION": 2,
        "C0_INDEXED_PRIMARY_DOCUMENT_ACCESS_BLOCKED": 5,
        "C0_NO_PROJECT_SCOPED_REE_PRODUCT_PROOF": 40,
        "C0_POSITIVE_PROJECT_OR_REE_LEAD": 22,
        "C0_UNRESOLVED_NATIVE_IDENTITY_CONFLICT": 4
    }
    assert len(rows) == 73 and len({r["target_id"] for r in rows}) == 73
    assert all(r["human_reviewer_signature"] == "" for r in rows)
    assert all(r["independent_C1_admission"] == "NO" for r in rows)
    assert all(r["legal_project_footprint_verified"] == "NO_NOT_PERFORMED" for r in rows)
    assert sum(bool(r["documented_tenement_exact_matches"]) for r in rows) == 20
    stats = {
        "audit_date": "2026-10-31",
        "frozen_source_snapshot": "2026-10-29",
        "p1_desk_source_rows_closed": len(rows),
        "p1_desk_cases_accounted_for": len(cases),
        "positive_cases_gate_reviewed": len(positives),
        "positive_source_rows_gate_reviewed": len(positive_sources),
        "source_dispositions": dispositions,
        "source_title_number_matches": 20,
        "official_tenure_polygon_intersecting_source_rows": 60,
        "legal_project_footprint_approved": 0,
        "independent_project_signoffs": 0,
        "independent_JORC_REO_signoffs": 0,
        "published_C1_project_rows": 0,
        "original_WAMEX_pdf_bytes_archived": 0,
        "CI_validated": False,
        "all_P1_search_scopes_desk_closed": True,
        "all_P1_primary_documents_archived": False,
        "all_P1_formal_eligibility_gates_passed": False,
        "inputs": [str(SOURCES), str(CASES), str(TENURE), str(POSITIVE)],
        "meaning": "P1 desk-search closure only. C0 source rows are NOT project IDs or MCDA C1 "
                   "admissions. Unretrieved WAMEX primary bytes, original source identity conflicts, "
                   "and independent JORC/project/GIS approval remain separate release blockers."
    }
    return rows, stats

def write_rows(path: Path, rows: list[dict[str, str]]):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    rows, summary = build(ROOT)
    if args.write:
        write_rows(ROOT / OUT, rows)
        (ROOT / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")
    if args.check:
        assert read(ROOT / OUT) == rows, OUT
        assert json.loads((ROOT / SUMMARY).read_text(encoding="utf-8")) == summary, SUMMARY
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
