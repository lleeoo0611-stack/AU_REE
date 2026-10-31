"""Regression tests for the frozen 487-target census evidence inventory.

These tests use the public archived repository fixtures, and do not imply that
the 487 source targets are independently verified mining Projects.
"""
from __future__ import annotations

import csv
import json
import sqlite3
from types import SimpleNamespace
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("p0_487_audit", ROOT / "scripts" / "build_p0_census_487_audit.py")
assert SPEC and SPEC.loader
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_complete_487_matrix_is_deterministically_reproducible():
    """The checked-in CSV must be regenerated from the frozen source tables."""
    rows, summary = MODULE.build_review(
        ROOT, run_date="2026-10-31", source_as_of="2026-10-29"
    )
    assert len(rows) == 487
    assert len({r["target_id"] for r in rows}) == 487
    assert summary["linked_source_rows"] == 78
    assert summary["unlinked_source_rows"] == 409
    assert summary["linked_review_groups"] == 39
    assert summary["distinct_sources_with_locator_review"] == 46

    snapshot = ROOT / "docs" / "audits" / "2026-10-31_census_487_batch_review.csv"
    with snapshot.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == MODULE.COLUMNS
        checked_in = list(reader)
    assert rows == checked_in


def test_entity_counts_and_release_protection():
    rows, summary = MODULE.build_review(
        ROOT, run_date="2026-10-31", source_as_of="2026-10-29"
    )
    assert summary["metrics"]["original_gate"] == {
        "INCLUDE_CANDIDATE": 69,
        "HOLD_REE_ROLE": 6,
        "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE": 412,
    }
    assert summary["metrics"]["entity_type"] == {
        "SOURCE_PROJECT_RECORD": 50,
        "DEPOSIT": 323,
        "OCCURRENCE": 102,
        "HISTORICAL_RECORD": 6,
        "PROSPECT": 6,
    }
    assert all(r["C1_release_status"] == "C1_NOT_RELEASED" for r in rows)
    assert all(r["C1_project_approval"] == "NOT_INDEPENDENTLY_APPROVED" for r in rows)
    assert all(r["C1_gis_approval"] == "NOT_APPROVED" for r in rows)
    assert all(r["C1_resource_approval"] == "NOT_EVALUATED_AS_PROJECT_RESOURCE" for r in rows)
    assert all(r["project_coordinate_approval"] == "NOT_APPROVED_SOURCE_POINT_ONLY" for r in rows)
    assert all(r["action_priority"] in {"P1", "P2", "P3", "P4"} for r in rows)


def test_no_project_promotion_from_deposit_or_tenement_intersection():
    rows, summary = MODULE.build_review(
        ROOT, run_date="2026-10-31", source_as_of="2026-10-29"
    )
    assert sum(r["reviewed_project_group_id"] == "" for r in rows) == 409
    assert summary["metrics"]["tenure"]["TENURE_INTERSECTS_PENDING_COMPANY_VERIFICATION"] == 258
    for r in rows:
        if not r["reviewed_project_group_id"]:
            assert r["group_source_screening"] == "NOT_GROUP_SOURCE_SCREENED"
        if r["source_entity_type"] in {"DEPOSIT", "OCCURRENCE", "PROSPECT"}:
            assert r["C1_project_approval"] == "NOT_INDEPENDENTLY_APPROVED"


def test_write_outputs_do_not_overwrite_archives(tmp_path):
    rows, summary = MODULE.build_review(
        ROOT, run_date="2026-10-31", source_as_of="2026-10-29"
    )
    csv_path, json_path = MODULE.write_outputs(
        rows, summary, tmp_path, "2026-10-31"
    )
    assert csv_path.is_file()
    assert json_path.is_file()
    with pytest.raises(FileExistsError):
        MODULE.write_outputs(rows, summary, tmp_path, "2026-10-31")
    # Explicitly versioned reruns in distinct dirs produce the same data bytes.
    csv2, _ = MODULE.write_outputs(rows, summary, tmp_path / "rebuild", "2026-10-31")
    assert csv_path.read_bytes() == csv2.read_bytes()


def test_reject_missing_or_duplicate_target_id():
    with pytest.raises(ValueError):
        MODULE.keyed([{"target_id": "x"}, {"target_id": "x"}], "dup")
    with pytest.raises(ValueError):
        MODULE.keyed([{"target_id": ""}], "missing")
    with pytest.raises(ValueError):
        MODULE.build_review(
            ROOT, run_date="2026-10-31", source_as_of="2026-10-29",
            expected_count=486,
        )


def _historical_census_relations():
    """Read the existing frozen CSV tables; no parallel review artifacts."""
    names=(
        "487_definition_review",
        "487_inclusion_gate",
        "project_entity_membership_487",
        "source_entity_register_487",
        "project_entity_register",
    )
    tables={}
    for name in names:
        with (ROOT/"outputs"/(name+".csv")).open(encoding="utf-8-sig",newline="") as source:
            tables[name]=list(csv.DictReader(source))
    return tables


def test_sqlite_census_rebuild_validates_source_entity_project_crosswalk():
    from reproducibility.build_census_database import validate_census_relations
    result=validate_census_relations(_historical_census_relations())
    assert result=={
        "status":"CENSUS_RELATIONS_STRUCTURALLY_VERIFIED_NOT_PROJECT_APPROVED",
        "source_targets":487,
        "linked_source_targets":78,
        "unlinked_source_targets":409,
        "reviewed_project_candidate_groups":39,
        "unique_native_source_entities":451,
        "repeated_targets_on_same_native_entity":36,
    }


@pytest.mark.parametrize("tamper",["unmatched_gate","duplicate_source","wrong_entity_id",
                                   "unknown_project_id","unreviewed_project_relation","native_source_identity_collision"])
def test_sqlite_census_rebuild_fails_closed_on_broken_identity_links(tamper):
    from reproducibility.build_census_database import validate_census_relations
    tables=_historical_census_relations()
    members=tables["project_entity_membership_487"]
    if tamper=="unmatched_gate":
        tables["487_inclusion_gate"].pop()
    elif tamper=="duplicate_source":
        tables["source_entity_register_487"].append(tables["source_entity_register_487"][0].copy())
    elif tamper=="wrong_entity_id":
        members[0]["entity_id"]="SRCENT-MISMATCH"
    elif tamper=="unknown_project_id":
        members[0]["project_entity_id"]="PRJ-UNKNOWN"
    elif tamper=="unreviewed_project_relation":
        members[0]["relation"]="UNRESOLVED_NO_PROJECT_LINK_INFERRED"
    elif tamper=="native_source_identity_collision":
        # Two frozen targets share the same source/native feature ID by design.
        # They may not silently diverge on the government native ID.
        baseline=tables["487_definition_review"]
        source_ids=tables["source_entity_register_487"]
        found={}
        for source in source_ids:
            key=source["entity_id"]
            if key in found:
                target=source["target_id"]
                next(row for row in baseline if row["target_id"]==target)["source_native_id"]="ALTERED-NATIVE-ID"
                break
            found[key]=source["target_id"]
    with pytest.raises(ValueError):
        validate_census_relations(tables)


def test_frozen_487_sqlite_rebuild_preserves_source_entity_identity(tmp_path):
    """Real tracked 487 CSV inputs must rebuild into a verifiable SQLite DB."""
    from reproducibility.build_census_database import csv_build
    dest=tmp_path/"census_review.sqlite"
    csv_build(SimpleNamespace(csv_dir=ROOT/"outputs",output=dest,
                              as_of_date="2026-10-29",overwrite=False))
    assert dest.is_file()
    with sqlite3.connect(dest) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("PRAGMA foreign_key_check").fetchall()==[]
        for table,expected in (
            ("487_definition_review",487),
            ("487_inclusion_gate",487),
            ("project_entity_membership_487",487),
            ("source_entity_register_487",487),
            ("project_entity_register",39),
        ):
            quoted='"'+table+'"'
            assert db.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0]==expected
    manifest=json.loads((tmp_path/"census_review.sqlite.manifest.json").read_text(encoding="utf-8"))
    assert manifest["sqlite_integrity_check"]=="ok"
    assert manifest["census_relation_check"]["unique_native_source_entities"]==451
    assert manifest["census_relation_check"]["repeated_targets_on_same_native_entity"]==36
    assert manifest["census_relation_check"]["status"]=="CENSUS_RELATIONS_STRUCTURALLY_VERIFIED_NOT_PROJECT_APPROVED"
