"""Archived P0 evidence audit integrity tests (never grants C1 approval)."""
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
import csv

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("review", ROOT / "scripts" / "review_p0_487_evidence.py")
module = module_from_spec(spec)
spec.loader.exec_module(module)


def test_487_claim_review_is_reproducible():
    rows, summary = module.build_review(ROOT)
    with (ROOT / "docs/audits/2026-10-31_487_evidence_claim_review.csv").open(
        encoding="utf-8", newline=""
    ) as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == module.COLUMNS
        frozen = list(reader)
    assert rows == frozen
    assert len(rows) == 487
    assert len({r["target_id"] for r in rows}) == 487
    assert summary["full_signoffs"] == 0
    assert all(r["approved_for_C1"] == "NO" for r in rows)


def test_specific_evidence_support_is_never_automatic_resource_approval():
    rows, summary = module.build_review(ROOT)
    assert summary["counts"]["native"]["EXACT_NATIVE_VALUE_MATCH"] == 407
    assert summary["counts"]["native"]["AMBIGUOUS_NATIVE_MATCH"] == 2
    assert summary["counts"]["grade"]["PROJECT_CONTEXT_TEXT_LOCATED"] == 42
    assert summary["counts"]["grade"]["ARCHIVED_TEXT_LOCATOR_CANDIDATE"] == 56
    assert summary["direct_doc_target_ids"] == 46
    assert summary["wa_official_distinct_names_exact"] == 13
    assert summary["wa_official_match_rows"] == 20
    assert all(x["JORC_claim"] != "APPROVED" for x in rows)
    nt = [x for x in rows if x["new_parent_prospect_hint"]]
    assert len(nt) == 1 and nt[0]["name"] == "Plenty River"
