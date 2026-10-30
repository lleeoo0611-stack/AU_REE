"""P0 source recovery: reproducible, no silent promotion to Project or JORC."""
from __future__ import annotations
import csv
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("p0_recovery2", ROOT/"scripts/review_p0_evidence_round2.py")
module = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def fixed_csv(name):
    with (ROOT/"docs/audits"/name).open(encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f)
        return rdr.fieldnames, list(rdr)


def test_487_row_evidence_snapshot_is_exactly_reconstructible():
    fields, rows, changes, summary = module.build(ROOT)
    got_fields, actual = fixed_csv("2026-10-31_487_evidence_round2_review.csv")
    assert got_fields == fields
    assert rows == actual
    assert len(rows) == len({r["target_id"] for r in rows}) == 487
    assert len(changes) == 86


def test_improvements_do_not_erase_unrecoverable_native_bytes_or_feature_row_ambiguity():
    fields, rows, changes, stat = module.build(ROOT)
    assert stat["native_only_before"] == 336
    assert stat["native_only_after"] == 272
    assert stat["missing_native_or_document_before"] == 23
    assert stat["missing_native_or_document_after"] == 3
    assert stat["native_bytes_missing_independent_of_doc_recovery"] == 23
    assert stat["ambiguity_unresolved_before"] == 2
    assert stat["ambiguity_with_context_after"] == 2
    assert all(x["approved_for_C1"] == "NO"
               and x["project_identity_approved_after_review"] == "NO" for x in rows)
    assert sum(x["native_identifier_status_after_review"] == "NATIVE_RECORD_STILL_UNRECOVERED"
               for x in rows) == 23
    assert sum(x["native_identifier_status_after_review"] == "MULTIPLE_NATIVE_FEATURE_ROWS_STILL_UNRESOLVED"
               for x in rows) == 2


def test_source_evidence_levels_are_distinct_from_project_class():
    fields, rows, changes, stat = module.build(ROOT)
    assert stat["grades_after"]["GOV_HISTORICAL_GEO_CONTEXT_LOCATED"] == 23
    assert stat["grades_after"]["OFFICIAL_RESOURCE_SUMMARY_LOCATED"] == 6
    assert stat["grades_after"]["EXTERNAL_PROJECT_OR_PROSPECT_DOCUMENT_LOCATED"] == 35
    missing = [x for x in rows if x["round2_evidence_grade"] == "SOURCE_RECORD_NOT_RECOVERED"]
    assert {x["name"] for x in missing} == {"Gascoyne", "Pyramid", "Webb Au"}
    assert all(x["native_identifier_status_after_review"] == "NATIVE_RECORD_STILL_UNRECOVERED"
               for x in missing)


def test_source_hash_and_overwrite_protection(tmp_path):
    fields, rows, changes, summary = module.build(ROOT)
    assert all(len(v) == 64 for v in summary["source_sha256"].values())
    files = module.save(fields, rows, changes, summary, tmp_path)
    assert all(p.exists() for p in files)
    with pytest.raises(FileExistsError):
        module.save(fields, rows, changes, summary, tmp_path)


def test_olympic_dam_ambiguity_not_silently_removed():
    _, rows, _, _ = module.build(ROOT)
    amb = [x for x in rows if x["native_identifier_status_after_review"] ==
           "MULTIPLE_NATIVE_FEATURE_ROWS_STILL_UNRESOLVED"]
    assert {x["name"] for x in amb} == {"OLYMPIC DAM", "CLARKE"}
    assert all(x["round2_source_url"] and x["round2_source_locator"] for x in amb)
    assert all(x["round2_evidence_grade"] == "AMBIGUOUS_NATIVE_ROWS_WITH_OFFICIAL_CONTEXT"
               for x in amb)
