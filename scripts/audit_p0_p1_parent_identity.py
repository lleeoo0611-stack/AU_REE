#!/usr/bin/env python3
"""Rebuild frozen 73-row P0/P1 Project-parent and identity audit from source CSVs.

No official Project, JORC or C1 gates are modified. Python 3.11+ standard library.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = Path("docs/audits")
INPUTS = {
    "b": DIR / "2026-10-31_census_487_batch_review.csv",
    "p": DIR / "2026-10-31_272_project_parent_evidence_queue.csv",
    "s": DIR / "2026-10-31_156_project_parent_evidence_review.csv",
    "f": DIR / "2026-10-31_109_project_evidence_review.csv",
    "l": DIR / "2026-10-31_70_project_evidence_review.csv",
}
MANUAL = Path("inputs/source_review_20261031/p1_parent_identity_web_checks.csv")
OUT = DIR / "2026-10-31_p1_parent_identity_review.csv"
SUMMARY = DIR / "2026-10-31_p1_parent_identity_summary.json"
BASE_COMMIT = "54fc23d304d309dc8f4570b81584c8afe5f39d0d"
COLUMNS = ["target_id","state","source_name","source_key","source_native_id","source_entity_type","native_feature_locator","native_chunk_sha256","p1_category","classification_round","parent_project_candidate","inherited_evidence_grade","inherited_external_url","inherited_external_date","inherited_external_locator","new_p1_review_level","new_p1_evidence_url","new_p1_evidence_locator","new_p1_verified_claim","original_state_or_spatial_issue","project_ree_role_verification","original_project_identity_approved","original_JORC_REO_approved","original_C1_approved","external_primary_bytes_archived","p1_disposition","next_action"]
PARENT5 = set(["HISTORICAL_GROUPED_DEPOSIT_PARENT_CANDIDATE","ISSUER_EXPLICIT_DEPOSIT_WITHIN_PROJECT","GOV_EXPLICIT_NORTH_SOUTH_DEPOSITS_IN_PROJECT","ISSUER_EXPLICIT_SITE_PROJECT","ISSUER_EXPLICIT_TARGET_WITHIN_PROJECT"])
SCOPE5 = set(["HISTORICAL_TENEMENT_NOT_PROJECT_PARENT","REGIONAL_NAME_NO_PARENT_HOLD","PARTIAL_SITE_NAME_BOUNDARY_HOLD","HISTORICAL_ALTERNATE_SPELLING_HOLD"])

def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def build(root: Path = ROOT):
    stages = {k: read(root / p) for k, p in INPUTS.items()}
    original = [x for x in stages["b"] if x["original_inclusion_gate"] ==
        "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE"]
    assert len(original) == 412
    prior = {k: {r["target_id"]: r for r in rows} for k, rows in stages.items() if k != "b"}
    selected = {x["target_id"]: {"base": x, "category": "", "round": ""} for x in original}

    def mark(x, category, round_):
        rec = selected.get(x["target_id"])
        if rec is not None:
            rec.update(category=category, round=round_)

    for x in stages["p"]:
        if x["evidence_review_status"] == "DOCUMENTED_CANDIDATE_REQUIRES_PARENT_SIGNOFF":
            mark(x, "PARENT_CANDIDATE", "ROUND3")
    for x in stages["s"]:
        if x["parent_review_result"] == "DOCUMENTED_NAMED_PROJECT_CANDIDATE_NOT_APPROVED":
            mark(x, "PARENT_CANDIDATE", "ROUND4")
        if x["parent_review_result"] == "NAMED_PROJECT_FOUND_BUT_SOURCE_FEATURE_SCOPE_UNVERIFIED":
            mark(x, "IDENTITY_SCOPE_HOLD", "ROUND4")
    for x in stages["f"]:
        if x["document_evidence_class"] in PARENT5:
            mark(x, "PARENT_CANDIDATE", "ROUND5")
        if x["document_evidence_class"] in SCOPE5:
            mark(x, "IDENTITY_SCOPE_HOLD", "ROUND5")
    for x in stages["l"]:
        if x["round6_evidence_grade"] == "HISTORICAL_PROJECT_PARENT_DOCUMENT_CANDIDATE":
            mark(x, "PARENT_CANDIDATE", "ROUND6")
        if x["round6_evidence_grade"] == "INDEXED_HISTORICAL_PROJECT_REPORT_PRIMARY_REQUIRED":
            mark(x, "INDEX_PRIMARY_PENDING", "ROUND6")
        if x["round6_evidence_grade"] in {
            "PROJECT_OR_JURISDICTION_IDENTITY_HOLD", "CROSS_STATE_SOURCE_COORDINATE_HOLD"
        }:
            mark(x, "IDENTITY_SCOPE_HOLD", "ROUND6")
    for id_, rec in selected.items():
        b = rec["base"]
        if (b["state"], b["source_record_name"], rec["category"]) == (
            "WA", "Ambergate", "PARENT_CANDIDATE"
        ) and float(prior["f"][id_]["same_name_nearest_native_distance_km"]) > 25:
            rec.update(category="IDENTITY_SCOPE_HOLD", round="ROUND5_SPATIAL_QA")

    manual_rows = read(root / MANUAL)
    manual = {x["target_id"]: x for x in manual_rows}
    assert len(manual) == len(manual_rows) == 25

    def pick(round_, p, s, f, l, key3, key4, key5, key6):
        return ((l.get(key6, "") if round_ == "ROUND6" else
                 f.get(key5, "") if round_.startswith("ROUND5") else
                 s.get(key4, "") if round_ == "ROUND4" else
                 p.get(key3, "")) or "")

    result = []
    for id_, rec in selected.items():
        if not rec["category"]:
            continue
        b = rec["base"]; p = prior["p"].get(id_, {}); s = prior["s"].get(id_, {})
        f = prior["f"].get(id_, {}); l = prior["l"].get(id_, {})
        c = manual.get(id_, {})
        round_ = rec["round"]; category = rec["category"]
        qa = ("SAME_NAME_NATIVE_POINTS_38_738_KM_APART" if b["source_record_name"] == "Ambergate" else
              "SA_TAG_AND_WA_EPA_PROJECT_JURISDICTION_CONFLICT" if b["source_record_name"] == "WINGELLINA" else
              "PROJECT_DEPOSIT_OR_TENEMENT_BOUNDARY_UNVERIFIED" if b["source_record_name"] in {
                  "Goschen South", "Wim deposits", "Tutunup West"} else "")
        row = {
            "target_id": id_, "state": b["state"], "source_name": b["source_record_name"],
            "source_key": b["source_key"], "source_native_id": b["source_native_id"],
            "source_entity_type": b["source_entity_type"],
            "native_feature_locator": p.get("native_feature_locator") or f.get("source_native_feature_locator") or s.get("raw_snapshot_feature_id", ""),
            "native_chunk_sha256": p.get("native_chunk_sha256") or f.get("source_original_chunk_sha256") or s.get("original_raw_sha256", ""),
            "p1_category": category, "classification_round": round_,
            "parent_project_candidate": pick(round_, p, s, f, l, "parent_project_candidate", "parent_project_candidate", "parent_project_candidate", "proposed_historical_project_or_context"),
            "inherited_evidence_grade": pick(round_, p, s, f, l, "evidence_review_status", "parent_review_result", "document_evidence_class", "round6_evidence_grade"),
            "inherited_external_url": pick(round_, p, s, f, l, "parent_evidence_source", "new_document_url", "external_document_url", "source_document_url"),
            "inherited_external_date": pick(round_, p, s, f, l, "evidence_effective_or_publication_date", "new_document_date", "external_document_date", "source_document_date_or_vintage"),
            "inherited_external_locator": pick(round_, p, s, f, l, "parent_locator", "new_document_locator", "external_document_locator", "source_document_locator"),
            "new_p1_review_level": c.get("review_level", "NOT_YET_INDEPENDENTLY_REVIEWED_IN_P1"),
            "new_p1_evidence_url": c.get("review_url", ""),
            "new_p1_evidence_locator": c.get("review_locator", ""),
            "new_p1_verified_claim": c.get("verified_claim", ""),
            "original_state_or_spatial_issue": qa,
            "project_ree_role_verification": "REQUIRES_PROJECT_SCOPED_REE_EVIDENCE",
            "original_project_identity_approved": "NO", "original_JORC_REO_approved": "NO",
            "original_C1_approved": "NO", "external_primary_bytes_archived": "NO",
            "p1_disposition": {
                "PARENT_CANDIDATE": "HOLD_PARENT_SIGNOFF",
                "INDEX_PRIMARY_PENDING": "HOLD_OFFICIAL_DOCUMENT_BYTES",
                "IDENTITY_SCOPE_HOLD": "HOLD_SCOPE_OR_IDENTITY",
            }[category],
            "next_action": c.get("next_action") or {
                "PARENT_CANDIDATE": "Obtain authoritative dated Project-Deposit boundary, REE role and original technical statement.",
                "INDEX_PRIMARY_PENDING": "Retrieve official government report original and source SHA-256; validate REE product.",
                "IDENTITY_SCOPE_HOLD": "Resolve official native feature vs legal Project polygon, date and rights.",
            }[category],
        }
        result.append(row)
    result.sort(key=lambda x: (x["state"], x["source_name"], x["target_id"]))
    counts = dict(Counter(r["p1_category"] for r in result))
    assert len(result) == len({r["target_id"] for r in result}) == 73, counts
    assert counts == {"PARENT_CANDIDATE": 48, "INDEX_PRIMARY_PENDING": 4,
                      "IDENTITY_SCOPE_HOLD": 21}, counts
    assert all(len(r["native_chunk_sha256"]) == 64 for r in result)
    assert {x["target_id"] for x in manual_rows}.issubset({x["target_id"] for x in result})
    by_level = dict(sorted(Counter(x["review_level"] for x in manual_rows).items()))
    summary = {
        "audit_date": "2026-10-31", "source_snapshot_as_of": "2026-10-29",
        "source_baseline_commit": BASE_COMMIT, "cohort_original_hold": 412,
        "p1_target_rows": 73, "category_counts": counts,
        "manual_evidence_review_rows": 25, "manual_evidence_review_by_level": by_level,
        "project_approval_count": 0, "jorc_reo_approval_count": 0,
        "c1_approval_count": 0, "unique_source_target_ids": 73,
        "source_inputs": [str(x) for x in INPUTS.values()],
        "manual_source_input": str(MANUAL),
    }
    return result, summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="rebuild the tracked editable CSV/JSON")
    parser.add_argument("--check", action="store_true", help="compare all tracked source rows")
    args = parser.parse_args()
    rows, summary = build(ROOT)
    if args.write:
        with (ROOT / OUT).open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
        (ROOT / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.check:
        assert read(ROOT / OUT) == rows, "P1 CSV differs from regenerated source review"
        stored = json.loads((ROOT / SUMMARY).read_text(encoding="utf-8"))
        assert stored == summary, "P1 summary differs from regenerated source review"
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
