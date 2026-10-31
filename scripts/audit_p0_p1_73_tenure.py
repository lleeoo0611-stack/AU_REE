#!/usr/bin/env python3
"""Reconcile 73 P1 source points with already-frozen official tenure polygon intersections.

Tenure overlay indicates a point is within a queried title polygon in the
snapshot, not that the source is part of an approved mine Project footprint.
No new live external queries or release-gate approvals are performed.
"""
from __future__ import annotations
import csv
import json
import re
import argparse
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = Path("docs/audits/2026-10-31_p1_73_source_resolution.csv")
STATUS = Path("outputs/487_official_tenure_trace_status.csv")
OVERLAPS = Path("outputs/487_official_tenure_intersection_evidence_compact.csv")
DOCUMENTS = Path("inputs/source_review_20261031/p1_73_documented_tenement_numbers.csv")
OUT = Path("docs/audits/2026-10-31_p1_73_tenure_reconciliation.csv")
SUMMARY = Path("docs/audits/2026-10-31_p1_73_tenure_reconciliation_summary.json")
FIELDS = [
    "target_id", "state", "source_name", "case_id", "official_tenure_query_status",
    "official_tenement_intersection_count", "official_tenement_numbers_at_point",
    "official_layer_api_urls", "documented_tenement_numbers",
    "documented_tenement_source_url", "documented_title_time_context",
    "exact_title_matches", "matched_title_holders_as_reported",
    "documented_title_comparison", "project_or_mine_footprint_intersected",
    "independent_project_identity_approved", "C1_approved", "decision_note"
]

def read(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def normalized_title(title: str, state: str) -> str:
    text = title.strip().upper()
    if state == "WA":
        # WA database encodes district (2 digits) + number (5 digits)
        # e.g. E37/1311 -> E3701311, E09/2357 -> E0902357.
        m = re.fullmatch(r"([EPMR])\s*0?(\d{1,2})/(\d{1,5})", text)
        if m:
            return f"{m.group(1)}{m.group(2).zfill(2)}{m.group(3).zfill(5)}"
    return re.sub(r"[^A-Z0-9]", "", text)

def build(root: Path = ROOT):
    sources, statuses, overlaps, documents = (
        read(root / path) for path in (SOURCES, STATUS, OVERLAPS, DOCUMENTS)
    )
    status = {x["target_id"]: x for x in statuses}
    assert len(sources) == len({r["target_id"] for r in sources}) == 73
    grouped = defaultdict(list)
    for x in overlaps:
        grouped[x["target_id"]].append(x)
    docs = {r["case_id"]: r for r in documents}
    assert len(docs) == len(documents) == 13
    assert all(x["case_id"] in {s["case_id"] for s in sources} for x in documents)

    output = []
    for s in sources:
        st = status[s["target_id"]]
        found = grouped[s["target_id"]]
        d = docs.get(s["case_id"])
        observed = {normalized_title(r["official_title_number"], s["state"]): r
                    for r in found if r["official_title_number"].strip()}
        expected = (
            [normalized_title(x, s["state"]) for x in d["documented_tenement_numbers"].split("|")]
            if d else []
        )
        matched = sorted(set(expected) & set(observed))
        if st["target_status"] == "OFFICIAL_TENEMENT_LAYER_NOT_VERIFIED":
            comparison = "OFFICIAL_TENURE_LAYER_UNVERIFIED"
        elif not expected:
            comparison = "NO_CASE_LEVEL_DOCUMENTED_TENEMENT_FOR_MATCH"
        elif matched:
            comparison = "DOCUMENTED_TENEMENT_NUMBER_INTERSECTS_SOURCE_POINT"
        elif st["target_status"] == "NO_OVERLAP_IN_QUERIED_LAYERS":
            comparison = "DOCUMENTED_TITLE_NOT_FOUND_IN_QUERIED_CURRENT_LAYERS"
        else:
            comparison = "DOCUMENTED_TITLE_DIFFERS_FROM_INTERSECTED_TITLES"
        output.append({
            "target_id": s["target_id"], "state": s["state"],
            "source_name": s["source_name"], "case_id": s["case_id"],
            "official_tenure_query_status": st["target_status"],
            "official_tenement_intersection_count": len(found),
            "official_tenement_numbers_at_point": "|".join(sorted(observed)),
            "official_layer_api_urls": "|".join(sorted({x["api_url"] for x in found if x["api_url"]})),
            "documented_tenement_numbers": d["documented_tenement_numbers"] if d else "",
            "documented_tenement_source_url": d["evidence_url"] if d else "",
            "documented_title_time_context": d["tenement_time_context"] if d else "",
            "exact_title_matches": "|".join(matched),
            "matched_title_holders_as_reported": "|".join(sorted({
                observed[x]["official_holder_text"] for x in matched if observed[x]["official_holder_text"]
            })),
            "documented_title_comparison": comparison,
            "project_or_mine_footprint_intersected": "NOT_TESTED",
            "independent_project_identity_approved": "NO",
            "C1_approved": "NO",
            "decision_note": (
                "Exact tenure number overlap corroborates a dated source-location/title link; "
                "separate Project-deposit boundary and ownership review is required."
                if matched else
                "Historical/current title snapshots may differ; check source report effective date "
                "and historic title GIS before inferring identity or absence."
            )
        })
    output.sort(key=lambda r: (r["case_id"], r["target_id"]))
    st_counts = dict(sorted(Counter(r["official_tenure_query_status"] for r in output).items()))
    compare_counts = dict(sorted(Counter(r["documented_title_comparison"] for r in output).items()))
    matches = [r for r in output if r["exact_title_matches"]]
    assert len(output) == 73 and len(matches) == 14
    assert st_counts == {
        "NO_OVERLAP_IN_QUERIED_LAYERS": 11,
        "OFFICIAL_TENEMENT_LAYER_NOT_VERIFIED": 2,
        "TENURE_INTERSECTS_PENDING_COMPANY_VERIFICATION": 60
    }
    assert all(r["C1_approved"] == "NO" for r in output)
    stats = {
        "audit_date": "2026-10-31", "source_snapshot_as_of": "2026-10-29",
        "source_rows": len(output), "official_intersection_rows": sum(
            int(r["official_tenement_intersection_count"]) for r in output),
        "official_tenure_query_status_counts": st_counts,
        "documented_title_comparison_counts": compare_counts,
        "case_level_reported_tenement_numbers": len(docs),
        "rows_with_exact_documented_title_number_overlap": len(matches),
        "distinct_cases_with_exact_title_overlap": sorted({r["case_id"] for r in matches}),
        "official_project_polygon_intersection_performed": 0,
        "C1_approvals": 0,
        "input_sources": [str(x) for x in (SOURCES, STATUS, OVERLAPS, DOCUMENTS)],
        "interpretation": "Official tenement overlap does not establish legal Project boundary or "
                          "REE resource eligibility. No-overlap in snapshot is not proof historic "
                          "title absent; records retain as-of source vintage."
    }
    assert stats["official_intersection_rows"] == 204
    return output, stats

def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--write", action="store_true")
    arg.add_argument("--check", action="store_true")
    params = arg.parse_args()
    rows, stats = build(ROOT)
    if params.write:
        with (ROOT / OUT).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        (ROOT / SUMMARY).write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    if params.check:
        assert read(ROOT / OUT) == [{k: str(v) for k, v in x.items()} for x in rows]
        assert json.loads((ROOT / SUMMARY).read_text(encoding="utf-8")) == stats
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
