"""Exact-P0 source-level Project relation queue evidence invariants."""
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
import csv
import pytest

ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/"docs/audits/2026-10-31_272_native_project_parent_audit.csv").exists():
    pytest.skip("Raw source data must be recovered from immutable artifact first", allow_module_level=True)
spec=spec_from_file_location("p0parent", ROOT/"scripts/build_p0_parent_evidence_queue.py")
mod=module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

def test_272_join_13_new_6_prior_and_no_project_auto_approval():
    rows,counts=mod.build(ROOT)
    assert len(rows)==272
    assert len({r["target_id"] for r in rows})==272
    assert counts["native_exact"]==272
    assert counts["new_documented_parent_source_rows"]==13
    assert counts["previous_documented_parent_source_rows"]==6
    assert counts["documented_candidate_source_rows"]==15
    assert counts["documented_non_ree_project_source_rows"]==4
    assert counts["project_parent_unlocated"]==156
    assert counts["C1_approvals"]==counts["independent_project_approvals"]==0
    assert all(x["project_id_approved"]=="NO" and x["C1_approved"]=="NO" for x in rows)

def test_non_project_sources_remain_geological_sources():
    rows,_=mod.build(ROOT)
    from_col=lambda key:[x for x in rows if x["evidence_review_status"]==key]
    assert len(from_col("C0_NONPROJECT_SOURCE_ENTITY"))==92
    assert len(from_col("C0_DEPOSIT_PARENT_ONLY"))==2
    assert len(from_col("C0_THEMATIC_LABEL_NOT_PROJECT"))==3
    assert all(x["parent_project_candidate"]=="" for x in from_col("C0_NONPROJECT_SOURCE_ENTITY"))

def test_raw_and_issuer_evidence_not_conflated():
    rows,_=mod.build(ROOT)
    r={x["source_name"]:x for x in rows}
    redlings=[x for x in rows if x["source_name"] in
              {"Redlings 1 Jungle Well","Redlings 2 Jungle Well","Redlings 3 Jungle Well"}]
    assert len(redlings)==6
    assert {x["parent_project_candidate"] for x in redlings}=={"Redlings REE Project"}
    assert all(x["project_id_approved"]=="NO" for x in redlings)
    assert r["Copi North"]["parent_project_candidate"]=="Copi Mineral Sands Project"
    assert r["Glenaladale"]["parent_project_candidate"].startswith("Fingerboards")
