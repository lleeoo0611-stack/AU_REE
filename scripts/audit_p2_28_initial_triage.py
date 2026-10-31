#!/usr/bin/env python3
"""Reproduce P2 phase-1 evidence triage for 28 immutable 2026-10-29 HOLD source rows.

The census 487/P1 73 sets are unchanged. P2 observations are case-documentary
leads, never independent Project, JORC or MCDA C1 approvals.
Only Python >=3.11 standard-library dependencies.
"""
from __future__ import annotations
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENSUS = Path("docs/audits/2026-10-31_census_487_batch_review.csv")
P1 = Path("docs/audits/2026-10-31_p1_parent_identity_review.csv")
EVIDENCE = Path("inputs/source_review_20261031/p2_27_case_evidence.csv")
ROUND2 = Path("docs/audits/2026-10-31_487_evidence_round2_review.csv")
OUT_SOURCES = Path("docs/audits/2026-10-31_p2_28_source_triage.csv")
OUT_CASES = Path("docs/audits/2026-10-31_p2_27_case_triage.csv")
OUT_SUMMARY = Path("docs/audits/2026-10-31_p2_phase1_summary.json")
SNAPSHOT_ASOF = "2026-10-29"
REVIEW_DATE = "2026-10-31"

SOURCE_FIELDS = [
    "target_id", "case_id", "state", "source_record_name", "source_entity_type",
    "source_key", "source_native_id", "original_coordinate_latitude",
    "original_coordinate_longitude", "native_sha256_in_round2",
    "native_record_locator_in_round2", "original_priority", "prior_source_evidence_status",
    "original_source_lookup_status", "legacy_or_E1_source", "evidence_class",
    "source_review_provenance_grade", "p2_stage_status", "scoped_documentary_claim",
    "REE_product_role", "documented_stage", "project_identity_scope",
    "evidence_url", "publication_date", "source_locator", "tenure_trace_status",
    "official_tenement_point_intersection_count", "project_title_or_polygon_approved",
    "independent_project_id_approved", "independent_JORC_REO_approved",
    "C1_admitted", "next_evidence_action", "reviewer_signed_off"
]
CASE_FIELDS = [
    "case_id", "source_case_key", "source_target_count", "source_target_ids",
    "state", "case_name", "source_entity_type", "evidence_class",
    "source_review_provenance_grade", "scoped_documentary_claim", "REE_product_role",
    "documented_stage", "project_identity_scope", "evidence_url",
    "publication_date", "source_locator", "next_evidence_action",
    "project_polygon_approved", "independent_project_id_approved",
    "independent_JORC_REO_approved", "C1_admitted", "reviewer_signed_off"
]

def read_csv(root: Path, path: Path) -> list[dict[str,str]]:
    with (root / path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def case_key(row: dict[str,str]) -> str:
    return "|".join((row["state"],
                     re.sub(r"\s+", " ", row["source_record_name"].strip()).upper(),
                     row["source_entity_type"]))

def grade(kind: str) -> str:
    if kind == "LEGACY_NAME_ONLY_NO_SCOPED_DOCUMENT":
        return "LEGACY_ID_ONLY_NO_SOURCE_SCOPED_PRIMARY"
    if kind == "VIC_NATIVE_GEOLOGICAL_FEATURE":
        return "NATIVE_GOVERNMENT_FEATURE_NO_PROJECT_PROOF"
    if kind == "SECONDARY_EXPLORATION_INDEX":
        return "REGIONAL_INDEX_NOT_PRIMARY_SOURCE_MATCH"
    return "DOCUMENTARY_LEAD_NO_APPROVED_SOURCE_PROJECT_JOIN"

def build(root: Path = ROOT):
    census = read_csv(root, CENSUS)
    p1 = read_csv(root, P1)
    evidence = read_csv(root, EVIDENCE)
    round2 = read_csv(root, ROUND2)
    assert len(census) == len(round2) == 487
    assert len({r["target_id"] for r in census}) == 487
    assert len(p1) == len({r["target_id"] for r in p1}) == 73
    all_hold = [r for r in census if r["original_inclusion_gate"] ==
                "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE"]
    p1_ids = {r["target_id"] for r in p1}
    assert len(all_hold) == 412
    assert p1_ids <= {r["target_id"] for r in all_hold}
    # No re-ranking of the 412 historical HOLD categories or reinterpreting P1.
    p2 = [r for r in all_hold if r["action_priority"] == "P2"
          and r["target_id"] not in p1_ids]
    p3 = [r for r in all_hold if r["action_priority"] == "P3"]
    p4 = [r for r in all_hold if r["action_priority"] == "P4"]
    assert len(p2) == 28 and len(p3) == 216 and len(p4) == 95
    assert len(p1_ids | {x["target_id"] for x in p2+p3+p4}) == 412
    assert len(p1_ids & {x["target_id"] for x in p2+p3+p4}) == 0
    assert Counter(x["cohort"] for x in p2) == {"LEGACY_86": 22, "UNLINKED_E1_401": 6}
    assert len({case_key(x) for x in p2}) == 27
    e = {r["source_case_key"]:r for r in evidence}
    assert len(evidence) == len(e) == 27
    assert {case_key(r) for r in p2} == set(e)
    sorted_keys = sorted(e)
    assert all(e[k]["case_id"] == f"P2G-{i+1:04}" for i,k in enumerate(sorted_keys))
    assert all(
        r["project_polygon_approved"] ==
        r["independent_project_id_approved"] ==
        r["independent_JORC_REO_approved"] == r["C1_admitted"] == "NO"
        and not r["reviewer_signed_off"]
        for r in evidence
    )
    indexed = {r["target_id"]: r for r in round2}
    by_case: dict[str,list[dict[str,str]]] = defaultdict(list)
    source_rows = []
    for r in p2:
        k = case_key(r)
        d = e[k]
        rd = indexed[r["target_id"]]
        # Legacy rows have no verified point and cannot inherit native coordinates.
        if r["cohort"] == "LEGACY_86":
            assert not r["latitude"] and not r["longitude"]
        assert r["C1_project_approval"] == r["C1_resource_approval"] == \
               r["C1_gis_approval"] == "NO"
        by_case[k].append(r)
        source_rows.append({
            "target_id": r["target_id"], "case_id": d["case_id"],
            "state": r["state"], "source_record_name": r["source_record_name"],
            "source_entity_type": r["source_entity_type"],
            "source_key": r["source_key"], "source_native_id": r["source_native_id"],
            "original_coordinate_latitude": r["latitude"],
            "original_coordinate_longitude": r["longitude"],
            "native_sha256_in_round2": rd["native_sha256"],
            "native_record_locator_in_round2": rd["native_record_locator"],
            "original_priority": r["action_priority"],
            "prior_source_evidence_status": r["source_evidence_status"],
            "original_source_lookup_status": r["source_record_lookup_status"],
            "legacy_or_E1_source": r["cohort"], "evidence_class": d["evidence_class"],
            "source_review_provenance_grade": grade(d["evidence_class"]),
            "p2_stage_status": "PHASE1_DOCUMENTARY_TRIAGE_NOT_FORMAL_SIGNOFF",
            "scoped_documentary_claim": d["scoped_documentary_claim"],
            "REE_product_role": d["REE_product_role"],
            "documented_stage": d["documented_stage"],
            "project_identity_scope": d["project_identity_scope"],
            "evidence_url": d["evidence_url"],
            "publication_date": d["publication_date"],
            "source_locator": d["source_locator"],
            "tenure_trace_status": r["tenure_trace_status"],
            "official_tenement_point_intersection_count": r["tenure_spatial_overlap_count"],
            "project_title_or_polygon_approved": "NO",
            "independent_project_id_approved": "NO",
            "independent_JORC_REO_approved": "NO",
            "C1_admitted": "NO",
            "next_evidence_action": d["next_evidence_action"],
            "reviewer_signed_off": ""
        })
    source_rows.sort(key=lambda r: (r["case_id"], r["target_id"]))
    case_rows = []
    for k in sorted_keys:
        d = e[k]
        rows = by_case[k]
        assert rows
        case_rows.append({
            "case_id": d["case_id"], "source_case_key": k,
            "source_target_count": len(rows),
            "source_target_ids": "|".join(sorted(r["target_id"] for r in rows)),
            "state": rows[0]["state"], "case_name": rows[0]["source_record_name"],
            "source_entity_type": rows[0]["source_entity_type"],
            "evidence_class": d["evidence_class"],
            "source_review_provenance_grade": grade(d["evidence_class"]),
            **{k: d[k] for k in (
                "scoped_documentary_claim", "REE_product_role", "documented_stage",
                "project_identity_scope", "evidence_url", "publication_date",
                "source_locator", "next_evidence_action", "project_polygon_approved",
                "independent_project_id_approved", "independent_JORC_REO_approved",
                "C1_admitted", "reviewer_signed_off"
            )}
        })
    assert len(source_rows) == 28 and len(case_rows) == 27
    assert sum(int(x["source_target_count"]) for x in case_rows) == 28
    assert sum(x["case_id"] == "P2G-0012" for x in source_rows) == 2
    assert not any(x["C1_admitted"] != "NO" for x in source_rows)
    stats = {
        "audit_date": REVIEW_DATE, "frozen_census_as_of": SNAPSHOT_ASOF,
        "original_hold_412": 412, "closed_prior_P1_source_rows": len(p1),
        "p2_source_rows": len(source_rows), "p2_distinct_source_case_keys": len(case_rows),
        "p2_legacy_source_rows": 22, "p2_native_E1_source_rows": 6,
        "p2_previously_missing_external_source_rows": 19,
        "p2_previously_gov_native_available_source_rows": 6,
        "p2_previously_primary_project_source_review_rows": 3,
        "p3_source_rows_untouched": len(p3), "p4_source_rows_untouched": len(p4),
        "p2_case_provenance_grade_counts": dict(sorted(
            Counter(x["source_review_provenance_grade"] for x in case_rows).items())),
        "p2_status": "PHASE1_TRIAGE_AND_TARGETED_DOCUMENTARY_REVIEW",
        "p2_independently_approved_project_identity": 0,
        "p2_project_polygon_signoffs": 0,
        "p2_JORC_REO_approvals": 0,
        "p2_C1_admissions": 0, "p1_WAMEX_official_pdfs_outstanding": 4,
        "inputs": [str(CENSUS), str(P1), str(EVIDENCE), str(ROUND2)],
        "guardrail": "28 P2 rows are 27 provisional source-site cases, not 27 independent "
                     "REE Projects. 2026-10-29 original priority, P1 closure, and C1 remain "
                     "unchanged. Government title/source point match and mineral or tailings "
                     "REE presence do not establish project ownership, a JORC REO resource "
                     "or pre-FID development study."
    }
    return source_rows, case_rows, stats

def write(path: Path, rows: list[dict[str,str]], fields: list[str]):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    a,b,c = build()
    if args.write:
        write(ROOT/OUT_SOURCES,a,SOURCE_FIELDS)
        write(ROOT/OUT_CASES,b,CASE_FIELDS)
        (ROOT/OUT_SUMMARY).write_text(json.dumps(c,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if args.check:
        assert read_csv(ROOT,OUT_SOURCES) == a, OUT_SOURCES
        assert read_csv(ROOT,OUT_CASES) == [
            {k:str(v) for k,v in r.items()} for r in b
        ], OUT_CASES
        assert json.loads((ROOT/OUT_SUMMARY).read_text(encoding="utf-8")) == c, OUT_SUMMARY
    print(json.dumps(c,indent=2,ensure_ascii=False))

if __name__ == "__main__":
    main()
