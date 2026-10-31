#!/usr/bin/env python3
"""Check source-specific substantive review progress against immutable baseline."""
import csv
from pathlib import Path
from scripts.check_external_primary_batch import validate as validate_batch01

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/audits/2026-10-31_p234_final_evidence_339.csv"
BATCH1 = ROOT / "inputs/source_review_20261031/external_primary_batch01_20261031.csv"
BATCH2 = ROOT / "inputs/source_review_20261031/external_primary_batch02_20261031.csv"
INDEX = ROOT / "docs/audits/2026-10-31_external_primary_progress_167.csv"
EXPECTED_BATCH2 = {
    "E1:C-3aa2c0ac30c404ee71885d", "E1:C-a606d3e73418c7da986cff",
    "E1:C-1f7de9bd699d45d7baf887", "E1:C-57c32fa527353a8b278717",
    "E1:C-6a04e3e46e0922bffc0194"
}

def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def validate():
    validate_batch01()
    original, b1, b2, progress = [read(p) for p in (BASE,BATCH1,BATCH2,INDEX)]
    original_ids = {r["target_id"]: r for r in original}
    native = {r["target_id"]: r for r in original
              if r["current_content_access_status"] ==
              "NATIVE_FEATURE_CONTENT_ONLY_NOT_TECHNICAL_DOCUMENT_REVIEW"}
    reviewed_b1 = {r["target_id"]: r for r in b1
                   if r["baseline_content_access"] ==
                   "NATIVE_FEATURE_CONTENT_ONLY_NOT_TECHNICAL_DOCUMENT_REVIEW"}
    reviewed_b2 = {r["target_id"]: r for r in b2}
    assert len(original_ids) == 339 and len(native) == 167
    assert len(reviewed_b1) == 5
    assert len(b2) == 5 and set(reviewed_b2) == EXPECTED_BATCH2
    assert set(reviewed_b1).isdisjoint(reviewed_b2)
    assert len(progress) == 167 and len({r["target_id"] for r in progress}) == 167
    assert {r["target_id"] for r in progress} == set(native)
    assert len([r for r in progress if r["recheck_batch"] == "B01"]) == 5
    assert len([r for r in progress if r["recheck_batch"] == "B02"]) == 5
    assert len([r for r in progress if not r["recheck_batch"]]) == 157
    for row in b2:
        old = original_ids[row["target_id"]]
        assert row["source_name"] == old["source_name"]
        assert row["source_snapshot"] == "2026-10-29"
        assert row["prior_native_grade"] == old["terminal_evidence_status"]
        assert row["technical_findings"] and row["source_locator"]
        assert row["source_document"].startswith("https://")
        assert row["remaining_gap"] and row["reopen_trigger"] and row["resource_basis_review"]
        assert row["original_document_sha256"] == "" and row["original_bytes_archived"] == "NO"
        assert row["full_technical_report_read"] == "NO"
        assert row["C1_admitted"] == "NO" and row["MCDA_changed"] == "NO"
        assert row["independent_signoff"] == "NO"
    for row in progress:
        old = native[row["target_id"]]
        assert row["source_name"] == old["source_name"]
        assert row["baseline_snapshot"] == "2026-10-29"
        assert row["baseline_source_key"] == old["source_key"]
        assert row["baseline_evidence_class"] == old["current_content_access_status"]
        assert row["baseline_terminal_status"] == old["terminal_evidence_status"]
        assert row["original_bytes_archived"] == "NO"
        assert row["original_fulltext_completed"] == "NO"
        assert row["current_C1_status"] == "NO" and row["independent_approval"] == "NO"
        assert row["remaining_action"]
        if row["target_id"] in reviewed_b1:
            assert row["recheck_batch"] == "B01"
            assert row["recheck_review_id"] == reviewed_b1[row["target_id"]]["review_id"]
            assert row["source_scoped_technical_finding"] == reviewed_b1[row["target_id"]]["technical_finding"]
        elif row["target_id"] in reviewed_b2:
            assert row["recheck_batch"] == "B02"
            assert row["recheck_review_id"] == reviewed_b2[row["target_id"]]["review_id"]
            assert row["source_scoped_technical_finding"] == reviewed_b2[row["target_id"]]["technical_findings"]
        else:
            assert row["recheck_batch"] == "" and row["recheck_review_id"] == ""
            assert row["source_scoped_technical_finding"] == ""
            assert row["source_scope_disposition"] == "REQUIRES_EXTERNAL_PRIMARY_TECHNICAL_DOCUMENT"
    assert all(r["approval_sufficiency_changed"] == "NO" for r in original)
    print("PASS: 167 frozen native source IDs, 10 source-scoped technical reviews (5+5); "
          "157 external original reviews pending; P2/C1/MCDA unchanged.")

if __name__ == "__main__":
    validate()
