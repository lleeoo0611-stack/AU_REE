"""Regression tests for P0 source-byte recovery and 272 provenance-scoped links."""
from pathlib import Path
import csv
import hashlib
import json
import pytest

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"docs/audits"
if not (AUDIT/"2026-10-31_native_parent_reconciliation_manifest.json").exists():
    pytest.skip("Frozen original raw evidence requires the P0 artifact job", allow_module_level=True)
def csv_rows(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def test_complete_272_source_parent_table():
    rows=csv_rows(AUDIT/"2026-10-31_272_native_project_parent_audit.csv")
    assert len(rows)==272
    assert len({x["target_id"] for x in rows})==272
    assert all(x["source_project_identity_approved"]=="NO" and x["C1_approved"]=="NO" for x in rows)
    assert all(x["project_parent_resolution"] for x in rows)

def test_original_native_bytes_restored_and_hashed():
    rows=csv_rows(AUDIT/"2026-10-31_23_original_native_bytes_verified.csv")
    assert len(rows)==23 and all(x["byte_exact_recovery"]=="YES" for x in rows)
    man=json.loads((AUDIT/"2026-10-31_native_parent_reconciliation_manifest.json").read_text())
    ga=(AUDIT/"recovered_raw/2026-10-29/ga/GA_AIMR_REE_2026_features_0000000.json").read_bytes()
    sa=(AUDIT/"recovered_raw/2026-10-29/sa/SA_CRITICAL_REE.csv").read_bytes()
    assert hashlib.sha256(ga).hexdigest()==man["original_sha256_GA"]
    assert hashlib.sha256(sa).hexdigest()==man["original_sha256_SA"]
    assert man["raw_recovered_verified"]==23

def test_south_australia_feature_composite_keys_are_unique():
    rows=csv_rows(AUDIT/"2026-10-31_sa_10_compound_feature_keys.csv")
    assert len(rows)==10
    assert len({x["source_feature_key"] for x in rows})==10
    assert {x["deposit_id"] for x in rows}=={"3000","11849"}
    assert {x["deposit_id"]:sum(y["deposit_id"]==x["deposit_id"] for y in rows)
            for x in rows}=={"3000":4,"11849":6}
    assert all(x["feature_key_disambiguated"]=="YES" and
               x["independent_project_approval"]=="NO" for x in rows)
