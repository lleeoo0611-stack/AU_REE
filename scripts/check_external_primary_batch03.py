#!/usr/bin/env python3
"""Batch 03 frozen-source evidence accounting checks (no network or C1 approval)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "docs/audits/2026-10-31_external_primary_progress_167.csv"
NEW = ROOT / "docs/audits/2026-10-31_external_primary_progress_167_b03.csv"
BATCH = ROOT / "inputs/source_review_20261031/external_primary_batch03_20261031.csv"
FIELDS = {"recheck_batch", "recheck_review_id", "actual_primary_source_url",
          "source_scoped_technical_finding", "source_scope_disposition",
          "remaining_action", "review_date"}

def read(path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def validate():
    old, new, batch = map(read, (OLD, NEW, BATCH))
    assert len(old) == len(new) == 167
    assert len(batch) == 6 and len({x["target_id"] for x in batch}) == 6
    assert len({x["review_id"] for x in batch}) == 6
    old_by = {x["target_id"]: x for x in old}
    new_by = {x["target_id"]: x for x in new}
    batch_by = {x["target_id"]: x for x in batch}
    assert len(old_by) == len(new_by) == 167 and set(old_by) == set(new_by)
    for target_id, item in new_by.items():
        prev = old_by[target_id]
        assert item.keys() == prev.keys()
        for key in item:
            if key not in FIELDS:
                assert item[key] == prev[key], (target_id, key)
        if target_id in batch_by:
            b = batch_by[target_id]
            assert prev["recheck_batch"] == ""
            assert item["recheck_batch"] == "B03"
            assert item["recheck_review_id"] == b["review_id"]
            assert item["source_name"] == b["source_name"]
            assert item["source_priority"] == b["priority"]
            assert item["source_state"] == b["state"]
            assert b["source_snapshot"] == "2026-10-29"
            assert b["source_locator"] and b["technical_findings"] and b["resource_basis_review"]
            assert b["source_document"].startswith("https://")
            assert item["source_scoped_technical_finding"] == b["technical_findings"]
            assert item["source_scope_disposition"] == b["bounded_closure"]
            assert item["actual_primary_source_url"] == b["source_document"]
            assert b["original_document_sha256"] == ""
            assert b["original_bytes_archived"] == b["full_technical_report_read"] == "NO"
            assert b["C1_admitted"] == b["independent_signoff"] == b["MCDA_changed"] == "NO"
        else:
            assert item == prev, target_id
        assert item["original_bytes_archived"] == item["original_fulltext_completed"] == "NO"
        assert item["current_C1_status"] == item["independent_approval"] == "NO"
    assert sum(bool(x["recheck_batch"]) for x in old) == 10
    assert sum(bool(x["recheck_batch"]) for x in new) == 16
    assert sum(not bool(x["recheck_batch"]) for x in new) == 151
    assert sum(x["recheck_batch"] == "B03" for x in new) == 6
    return True

if __name__ == "__main__":
    validate()
    print("PASS Batch 03: 167 frozen IDs, 6 new native source reviews, 16 reviewed / 151 pending; C1/bytes unchanged.")
