#!/usr/bin/env python3
"""Offline structural validation for 339 P2-P4 continuity and 9 bounded P2 originals."""
import csv
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/"docs/audits/2026-10-31_p234_final_evidence_339.csv"
CURRENT=ROOT/"docs/audits/2026-10-31_p234_all_339_continuation_b04.csv"
BATCH=ROOT/"inputs/source_review_20261031/p2_external_primary_batch04_20261031.csv"
ATTEMPTS=ROOT/"inputs/source_review_20261031/p34_batch04_locator_attempts.csv"
P2=ROOT/"docs/audits/2026-10-31_p2_28_recheck_tracker.csv"
NATIVE=ROOT/"docs/audits/2026-10-31_external_primary_progress_167_b03.csv"

def get_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def validate():
    old, now, batch, tries, p2, native=map(get_rows,(OLD,CURRENT,BATCH,ATTEMPTS,P2,NATIVE))
    assert len(old)==len(now)==339 and len(batch)==9 and len(tries)==8
    assert len(p2)==28 and len(native)==167
    O={r["target_id"]:r for r in old}; N={r["target_id"]:r for r in now}
    B={r["target_id"]:r for r in batch}; T={r["target_id"]:r for r in tries}
    assert len(O)==len(N)==339 and set(O)==set(N)
    assert len(B)==9 and len(T)==8 and not set(B)&set(T)
    assert Counter(x["priority"] for x in now)=={"P2":28,"P3":216,"P4":95}
    assert Counter(x["continuation_status"] for x in now if x["priority"]=="P2")=={
        "B04_DIRECT_OFFICIAL_SOURCE_SCOPE_REVIEW":9,
        "B01_DIRECT_GOV_HTML_SCOPE_RECHECK":3,
        "BASELINE_P2_DESK_REVIEW_ONLY":16
    }
    assert sum(x["continuation_status"].startswith("PRIOR_") for x in now if x["priority"]=="P3")==11
    assert sum(x["continuation_status"].startswith("PRIOR_") for x in now if x["priority"]=="P4")==5
    assert sum(x["continuation_status"]=="BASELINE_ARCHIVED_RELEVANT_CONTENT" for x in now)==143
    assert sum(x["continuation_status"]=="BASELINE_WEB_CACHED_ONLY" for x in now)==1
    assert sum(x["continuation_status"] in {"BASELINE_NATIVE_FEATURE_ONLY","B04_LOCATOR_ATTEMPT_ONLY_NOT_REVIEW"} for x in now if x["priority"]=="P3")==87
    assert sum(x["continuation_status"] in {"BASELINE_NATIVE_FEATURE_ONLY","B04_LOCATOR_ATTEMPT_ONLY_NOT_REVIEW"} for x in now if x["priority"]=="P4")==64
    for r in now:
        oid=r["target_id"]; before=O[oid]
        for col in ("priority","source_name","state","source_key","source_native_id"):
            assert r[col]==before[col],(oid,col)
        assert r["source_snapshot"]==before["frozen_snapshot"]=="2026-10-29"
        assert r["baseline_terminal_evidence_status"]==before["terminal_evidence_status"]
        assert r["baseline_content_access_status"]==before["current_content_access_status"]
        assert r["source_review_classification_complete"]=="YES"
        assert r["C1_admitted"]==before["C1_admitted"]=="NO"
        assert r["original_pdf_bytes_newly_archived"]=="NO"
        assert r["full_technical_original_newly_verified"]=="NO"
        assert r["independent_approval_signature"]==""
        if oid in B:
            b=B[oid]
            assert r["priority"]=="P2" and b["priority"]=="P2"
            assert r["continuation_status"]=="B04_DIRECT_OFFICIAL_SOURCE_SCOPE_REVIEW"
            assert r["continuation_review_id"]==b["review_id"]
            assert r["new_official_source_url"]==b["external_source_url"]
            assert r["source_scoped_finding_overlay"]==b["source_scoped_technical_finding"]
            assert b["original_pdf_bytes_archived"]==b["complete_technical_fulltext_verified"]=="NO"
            assert b["original_pdf_sha256"]==""
            assert b["formal_C1_admitted"]==b["independent_signoff"]==b["MCDA_changed"]=="NO"
        if oid in T:
            assert r["p34_locator_attempt_id"]==T[oid]["attempt_id"]
            assert T[oid]["exact_original_primary_verified"]==T[oid]["new_technical_original_review"]=="NO"
    assert sum(x["continuation_status"]=="B04_DIRECT_OFFICIAL_SOURCE_SCOPE_REVIEW" for x in now)==9
    return True

if __name__=="__main__":
    validate()
    print("PASS: 339 immutable source IDs; P2 9 new + 3 prior / 16 pending; P3 11 new text / 87 pending; P4 5 new text / 64 pending. No approvals.")
