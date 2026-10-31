#!/usr/bin/env python3
"""Deterministic P0/P1 review of 73 immutable original REE source targets.

The outputs document which claims can/cannot be supported by searched sources.
They do NOT assert exhaustive absence on the public internet or admit projects to C1.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("docs/audits/2026-10-31_p1_parent_identity_review.csv")
RAW = Path("docs/audits/2026-10-31_census_487_batch_review.csv")
GROUPS = Path("docs/audits/2026-10-31_p1_25_provisional_parent_groups.csv")
EVIDENCE = Path("inputs/source_review_20261031/p1_73_resolution_evidence_cases.csv")
RESOURCE = Path("inputs/source_review_20261031/p1_73_new_resource_claims.csv")
OUT_SOURCES = Path("docs/audits/2026-10-31_p1_73_source_resolution.csv")
OUT_CASES = Path("docs/audits/2026-10-31_p1_44_case_resolution.csv")
OUT_QA = Path("docs/audits/2026-10-31_p1_73_resolution_summary.json")
DATE = "2026-10-31"
AS_OF = "2026-10-29"

SOURCE_FIELDS = [
    "target_id", "state", "source_name", "source_native_id", "source_key",
    "original_entity_type", "native_chunk_sha256", "native_feature_locator",
    "latitude", "longitude", "p1_source_category", "case_id", "case_label",
    "evidence_kind", "evidence_url", "evidence_publication_date",
    "source_locator", "supported_claim",
    "documented_parent_relationship", "REE_role_evidence",
    "resource_basis_evidence", "historic_or_current_stage",
    "source_spatial_identity", "source_point_polygon_tested",
    "documentary_verdict", "resource_claim_ids", "primary_pdf_archived",
    "independent_project_identity_approved", "independent_JORC_REO_approved",
    "C1_approved", "evidence_search_scope", "next_action"
]
CASE_FIELDS = [
    "case_id", "state", "source_case_kind", "case_label",
    "source_row_count", "source_target_ids", "source_site_names",
    "unique_source_coordinate_pairs", "max_source_coordinate_spread_km",
    "documentary_verdict", "evidence_kind", "evidence_url", "publication_date",
    "source_locator", "supported_claim", "documented_parent_relationship",
    "REE_role_evidence", "resource_basis_evidence", "stage_asof",
    "source_spatial_identity", "resource_claim_ids", "primary_pdf_archived",
    "polygon_tested", "C1_approved", "search_scope", "search_rule", "next_action"
]

def read_csv(root: Path, relative: Path) -> list[dict[str, str]]:
    with (root / relative).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def geo_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    x, y, u, v = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((u-x)/2)**2 + math.cos(x)*math.cos(u)*math.sin((v-y)/2)**2
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(h)))

def spread(coords: list[tuple[float, float]]) -> float:
    return max((geo_km(p, q) for i, p in enumerate(coords)
                for q in coords[i+1:]), default=0.0)

def evidence_verdict(e: dict[str, str]) -> str:
    if e["documentary_resolution"] == "CONFLICT_REQUIRES_SOURCE_CORRECTION":
        return "IDENTITY_CONFLICT_DOCUMENTED__NO_AUTOMERGE"
    if e["documentary_resolution"] == "SECONDARY_INDEX_WITH_PRIMARY_RETRIEVAL_GAP":
        return "REPORT_INDEX_FOUND__OFFICIAL_PDF_NOT_RETRIEVED"
    if e["evidence_kind"] == "STATE_LIBRARY_HISTORIC_CATALOGUE":
        return "CATALOGUE_CONTEXT_ONLY__PRIMARY_MISSING"
    if e["REE_role_interpretation"] == "REE_PRODUCT_NOT_DOCUMENTED":
        return "SOURCE_REVIEWED__NO_REE_PRODUCT_PROOF_IN_SOURCES"
    if "EXPLICIT_NO_MRE" in e["REE_role_interpretation"] or "EXPLICIT_NO_MRE" in e["resource_basis_interpretation"]:
        return "ORIGINAL_TECHNICAL_SOURCE_REJECTS_REE_MRE_INHERITANCE"
    return "DOCUMENTARY_CLAIM_EVIDENCED__GIS_AND_APPROVAL_PENDING"

def build(root: Path = ROOT):
    targets = read_csv(root, SOURCE)
    raw = {r["target_id"]: r for r in read_csv(root, RAW)}
    groups = read_csv(root, GROUPS)
    evidence = read_csv(root, EVIDENCE)
    claims = read_csv(root, RESOURCE)
    assert len(targets) == len({x["target_id"] for x in targets}) == 73
    assert len([x for x in targets if x["p1_category"] == "PARENT_CANDIDATE"]) == 48
    assert len([x for x in targets if x["p1_category"] == "INDEX_PRIMARY_PENDING"]) == 4
    assert len([x for x in targets if x["p1_category"] == "IDENTITY_SCOPE_HOLD"]) == 21
    assert len(groups) == 25 and len(evidence) == 44 and len(claims) == 12

    by_case = {x["case_id"]: x for x in evidence}
    assert len(by_case) == 44
    labels = {x["source_parent_label"]: x["provisional_group_key"] for x in groups}
    assert len(labels) == 25
    non = {(x["state"], x["case_label"], x["p1_case_kind"]): x["case_id"]
           for x in evidence if x["case_id"].startswith("P1X-")}
    assert len(non) == 19
    claim_ids_by_case = defaultdict(list)
    for x in claims:
        assert x["case_id"] in by_case
        claim_ids_by_case[x["case_id"]].append(x["claim_id"])
        assert x["grade_basis"] in {"Y2O3", "V2O5", "TREO", "HM", "THM", "ORE_TONNAGE"}
        assert not x["publication_date"] or x["publication_date"] <= AS_OF
    assert len({x["claim_id"] for x in claims}) == len(claims)
    assert set(x["target_id"] for x in targets) <= set(raw)

    source_rows = []
    partition = defaultdict(list)
    for t in targets:
        assert t["original_C1_approved"] == "NO"
        assert t["original_project_identity_approved"] == "NO"
        assert t["original_JORC_REO_approved"] == "NO"
        case_id = labels[t["parent_project_candidate"]] if t["p1_category"] == "PARENT_CANDIDATE" else \
                  non[(t["state"], t["source_name"], t["p1_category"])]
        e = by_case[case_id]
        r = raw[t["target_id"]]
        assert r["original_inclusion_gate"] == "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE"
        assert r["state"] == t["state"] and r["source_record_name"] == t["source_name"]
        assert len(t["native_chunk_sha256"]) == 64
        assert -45 < float(r["latitude"]) < -10 and 110 < float(r["longitude"]) < 155
        assert e["independent_C1_approval"] == "NO"
        assert e["official_project_polygon_intersection"] == "NOT_PERFORMED"
        partition[case_id].append(t)
        source_rows.append({
            "target_id": t["target_id"], "state": t["state"],
            "source_name": t["source_name"], "source_native_id": t["source_native_id"],
            "source_key": t["source_key"], "original_entity_type": t["source_entity_type"],
            "native_chunk_sha256": t["native_chunk_sha256"],
            "native_feature_locator": t["native_feature_locator"],
            "latitude": r["latitude"], "longitude": r["longitude"],
            "p1_source_category": t["p1_category"], "case_id": case_id,
            "case_label": e["case_label"], "evidence_kind": e["evidence_kind"],
            "evidence_url": e["evidence_url"],
            "evidence_publication_date": e["source_publication_date"],
            "source_locator": e["source_locator"],
            "supported_claim": e["supported_claim"],
            "documented_parent_relationship": e["project_relation_interpretation"],
            "REE_role_evidence": e["REE_role_interpretation"],
            "resource_basis_evidence": e["resource_basis_interpretation"],
            "historic_or_current_stage": e["asof_stage_interpretation"],
            "source_spatial_identity": e["identity_spatial_result"],
            "source_point_polygon_tested": "NO",
            "documentary_verdict": evidence_verdict(e),
            "resource_claim_ids": "|".join(sorted(claim_ids_by_case[case_id])),
            "primary_pdf_archived": e["official_primary_pdf_archived"],
            "independent_project_identity_approved": "NO",
            "independent_JORC_REO_approved": "NO", "C1_approved": "NO",
            "evidence_search_scope": e["search_sources"],
            "next_action": e["next_required_action"]
        })
    source_rows.sort(key=lambda x: (x["case_id"], x["target_id"]))

    case_rows = []
    for e in evidence:
        rows = partition[e["case_id"]]
        assert len(rows) == int(e["source_rows"]), e["case_id"]
        coords = [(float(raw[x["target_id"]]["latitude"]),
                   float(raw[x["target_id"]]["longitude"])) for x in rows]
        case_rows.append({
            "case_id": e["case_id"], "state": e["state"],
            "source_case_kind": e["p1_case_kind"], "case_label": e["case_label"],
            "source_row_count": len(rows),
            "source_target_ids": "|".join(sorted(x["target_id"] for x in rows)),
            "source_site_names": "|".join(sorted({x["source_name"] for x in rows})),
            "unique_source_coordinate_pairs": len(set(coords)),
            "max_source_coordinate_spread_km": f"{spread(coords):.3f}",
            "documentary_verdict": evidence_verdict(e),
            "evidence_kind": e["evidence_kind"],
            "evidence_url": e["evidence_url"],
            "publication_date": e["source_publication_date"],
            "source_locator": e["source_locator"],
            "supported_claim": e["supported_claim"],
            "documented_parent_relationship": e["project_relation_interpretation"],
            "REE_role_evidence": e["REE_role_interpretation"],
            "resource_basis_evidence": e["resource_basis_interpretation"],
            "stage_asof": e["asof_stage_interpretation"],
            "source_spatial_identity": e["identity_spatial_result"],
            "resource_claim_ids": "|".join(sorted(claim_ids_by_case[e["case_id"]])),
            "primary_pdf_archived": "NO", "polygon_tested": "NO",
            "C1_approved": "NO", "search_scope": e["search_sources"],
            "search_rule": e["search_rule"],
            "next_action": e["next_required_action"]
        })
    case_rows.sort(key=lambda x: x["case_id"])
    assert len(source_rows) == 73 and len(case_rows) == 44
    assert all(x["evidence_url"].startswith("https://") for x in case_rows)
    assert all(x["C1_approved"] == "NO" for x in source_rows)
    cases_by_verdict = dict(sorted(Counter(x["documentary_verdict"] for x in case_rows).items()))
    sources_by_verdict = dict(sorted(Counter(x["documentary_verdict"] for x in source_rows).items()))
    stats = {
        "review_date": DATE, "frozen_source_as_of": AS_OF,
        "source_rows_reviewed": len(source_rows),
        "source_id_count_unique": len({x["target_id"] for x in source_rows}),
        "case_count": len(case_rows), "prior_provisional_parent_cases": 25,
        "source_identity_or_index_cases": 19,
        "source_count_by_category": dict(sorted(Counter(x["p1_source_category"] for x in source_rows).items())),
        "case_documentary_dispositions": cases_by_verdict,
        "source_documentary_dispositions": sources_by_verdict,
        "additional_resource_statements": len(claims),
        "additional_resource_basis_counts": dict(sorted(Counter(x["grade_basis"] for x in claims).items())),
        "independently_approved_project_identity": 0,
        "independently_approved_TREO_JORC": 0,
        "official_polygon_source_row_intersections_tested": 0,
        "C1_admissions": 0,
        "external_WAMEX_government_report_bytes_retrieved": 0,
        "inputs": [str(x) for x in (SOURCE, RAW, GROUPS, EVIDENCE, RESOURCE)],
        "interpretation": "Every case has a source-specific documentary decision. It does not prove "
                         "exhaustive web absence, historical Project geometry, or MCDA admission; "
                         "four WAMEX indexed original reports (A119194 A120393 A129842 A109188) need "
                         "original government PDF bytes and project footprint validation."
    }
    return source_rows, case_rows, stats

def write_csv(path: Path, rows: list[dict], fields: list[str]):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    sources, cases, stats = build(ROOT)
    if args.write:
        write_csv(ROOT / OUT_SOURCES, sources, SOURCE_FIELDS)
        write_csv(ROOT / OUT_CASES, cases, CASE_FIELDS)
        (ROOT / OUT_QA).write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.check:
        assert read_csv(ROOT, OUT_SOURCES) == [{k: str(v) for k, v in x.items()} for x in sources]
        assert read_csv(ROOT, OUT_CASES) == [{k: str(v) for k, v in x.items()} for x in cases]
        assert json.loads((ROOT / OUT_QA).read_text(encoding="utf-8")) == stats
    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
