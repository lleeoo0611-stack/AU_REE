#!/usr/bin/env python3
"""Deterministic batch-01 source-ID / evidence boundary checks. No network/approval."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "docs/audits/2026-10-31_p234_final_evidence_339.csv"
P2 = ROOT / "docs/audits/2026-10-31_p2_28_public_terminal_desk_review.csv"
BATCH = ROOT / "inputs/source_review_20261031/external_primary_batch01_20261031.csv"
TRACKER = ROOT / "docs/audits/2026-10-31_p2_28_recheck_tracker.csv"
EXPECTED = {
    "E1:C-0511f896977c4db0b9f979", "E1:C-2075adfceae784ee932371",
    "E1:C-05ee06733e0fc12c183d3d", "E1:C-137201a7af61bd1e2d62ca",
    "E1:C-3ab58c678f87054e3045da", "E1:C-c1e7aa1538298437b0bdec",
    "LEGACY:11ed2307-c2b3-5a43-a57d-93f5bc270772",
    "E1:C-025c12974b133bd17b4660", "E1:C-8ad124f45bd2a590eafdc8"
}
WEB_ACCESS = "WEB_INDEXED_PUBLISHER_ORIGINAL_PDF_TEXT_REVIEWED_BYTE_AND_VISUAL_VERIFICATION_UNAVAILABLE"
GOV_ACCESS = "GOVERNMENT_HTML_CONTENT_REVIEWED"

def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def validate():
    original, baseline, batch, tracker = map(read_rows, (FINAL, P2, BATCH, TRACKER))
    assert len(original) == 339, "historical 339 row count drifted"
    assert len(baseline) == 28 and len({r["case_id"] for r in baseline}) == 27
    native = [r for r in original if r["current_content_access_status"] ==
              "NATIVE_FEATURE_CONTENT_ONLY_NOT_TECHNICAL_DOCUMENT_REVIEW"]
    assert len(native) == 167, "167 unresolved native originals changed"
    om = {r["target_id"]: r for r in original}
    bm = {r["target_id"]: r for r in baseline}
    assert len(om) == 339 and len(bm) == 28
    assert len(batch) == 9 and {r["target_id"] for r in batch} == EXPECTED
    assert len({r["review_id"] for r in batch}) == 9
    assert len(tracker) == 28 and {r["target_id"] for r in tracker} == set(bm)
    assert len({r["target_id"] for r in tracker}) == 28
    new_p2 = set()
    external_native = set()
    for r in batch:
        old = om[r["target_id"]]
        assert r["cohort"] == old["priority"] and r["source_name"] == old["source_name"]
        assert r["state"] == old["state"] and r["source_snapshot"] == "2026-10-29"
        assert r["baseline_content_access"] == old["current_content_access_status"]
        assert r["baseline_terminal_evidence_status"] == old["terminal_evidence_status"]
        assert r["original_url"].startswith("https://") and r["locator"].strip()
        assert r["technical_finding"].strip() and r["entity_finding"].strip()
        assert r["remaining_gap"].strip() and r["reopen_condition"].strip()
        assert r["original_byte_sha256"] == "" and r["original_bytes_archived"] == "NO"
        assert r["source_point_to_current_project_verified"] == "NO"
        assert r["formal_C1_or_MCDA_change"] == "NO"
        assert r["independent_reviewer_signed"] == "NO"
        assert r["access_class"] in {WEB_ACCESS, GOV_ACCESS}
        assert old["C1_admitted"] == "NO", "prior C1 approval unexpectedly changed"
        if r["cohort"] == "P2":
            assert r["target_id"] in bm
            new_p2.add(r["target_id"])
            assert r["access_class"] == GOV_ACCESS
        elif r["target_id"] == "E1:C-c1e7aa1538298437b0bdec":
            assert r["access_class"] == WEB_ACCESS
        else:
            assert r["target_id"] in {n["target_id"] for n in native}
            external_native.add(r["target_id"])
    assert len(new_p2) == 3 and len(external_native) == 5
    rechecked = 0
    for row in tracker:
        old = bm[row["target_id"]]
        assert row["case_id"] == old["case_id"] and row["source_name"] == old["source_name"]
        assert row["baseline_verdict"] == old["scoped_documentary_verdict"]
        assert row["baseline_C1_admitted"] == "NO"
        assert row["technical_original_bytes_reverified"] == "NO"
        assert row["independent_C1_signature"] == "NO"
        if row["target_id"] in new_p2:
            assert row["review_2026_10_31"] == "NEW_DIRECT_GOVERNMENT_HTML_SOURCE_SCOPED_RECHECK"
            assert row["new_review_id"].startswith("EXT-TECH-B01-")
            rechecked += 1
        else:
            assert row["review_2026_10_31"] == "BASELINE_LINEAGE_RECONCILED_PRIMARY_FULLTEXT_RECHECK_PENDING"
            assert row["new_review_id"] == "" and row["new_document_scope_decision"] == ""
    assert rechecked == 3
    assert all(row["C1_admitted"] == "NO" and row["approval_sufficiency_changed"] == "NO"
               for row in original)
    print("PASS: baseline 339 / native 167 / P2 28 (27 cases), nine review overlays "
          "(five native, three P2, one Scaddan); no byte claims or C1 promotion.")

if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    validate()
