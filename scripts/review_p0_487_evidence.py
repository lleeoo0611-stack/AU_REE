#!/usr/bin/env python3
"""Rebuild the 487-source P0 evidence claims audit from archived sources.

The audit verifies *record pointers, text locator status and support scope*.
It never approves a Project, JORC Resource Statement, GIS location or title.
Use frozen repo sources, not text-search results as independent authority.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "batch": "docs/audits/2026-10-31_census_487_batch_review.csv",
    "trace": "outputs/unlinked_441_source_trace.csv",
    "locator": "outputs/source_evidence_locator_review_95.csv",
    "wa": "docs/audits/2026-10-31_wa_official_ree_project_leads.csv",
}
COLUMNS = [
    "target_id", "state", "name", "source_entity_type", "group_id",
    "archived_native_match_status", "native_sha256", "native_record_locator",
    "search_archive_sha256", "additional_source_url", "additional_document_locator",
    "prior_document_status", "prior_evidence_ids",
    "WA_official_exact_project_match", "WA_stage_Jan2026",
    "WA_MRE_mt_reported", "WA_grade_pct_TREO_reported",
    "new_parent_prospect_hint", "source_evidence_grade",
    "project_identity_claim", "JORC_claim", "next_evidence_action",
    "approved_for_C1",
]


def read_csv(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def unique_map(rows: list[dict[str, str]], key: str, title: str) -> dict[str, dict[str, str]]:
    found = {}
    for row in rows:
        value = row[key]
        if not value or value in found:
            raise ValueError(f"{title}: blank or duplicate {key} ({value})")
        found[value] = row
    return found


def evidence_index(
    locators: list[dict[str, str]], valid: set[str]
) -> dict[str, list[dict[str, str]]]:
    by_id = defaultdict(list)
    for loc in locators:
        for target in re.split(r"[;|,\s]+", loc["target_ids"]):
            if target in valid:
                by_id[target].append(loc)
    return by_id


def build_review(root: Path, *, as_of: str = "2026-10-29", date: str = "2026-10-31"):
    sources = {key: read_csv(root, path) for key, path in SOURCES.items()}
    batch, traces, locators, wa = (
        sources["batch"], sources["trace"], sources["locator"], sources["wa"]
    )
    if (len(batch), len(traces), len(locators), len(wa)) != (487, 441, 95, 20):
        raise ValueError("Unexpected frozen evidence inputs")
    ids = {r["target_id"] for r in batch}
    if len(ids) != 487:
        raise ValueError("Duplicate target_id in 487 audit")
    trace = unique_map(traces, "target_id", "441 native trace")
    if not set(trace).issubset(ids):
        raise ValueError("Trace source id absent from 487 target table")
    wa_map = unique_map(
        [{**row, "_casefold": row["source_project_name"].strip().lower()} for row in wa],
        "_casefold", "WA official source"
    )
    ev = evidence_index(locators, ids)

    stats = defaultdict(Counter)
    records = []
    for x in batch:
        target = x["target_id"]
        t = trace.get(target)
        documents = ev.get(target, [])
        found = [d for d in documents if d["review_status"] == "LOCATOR_FOUND_PROJECT_CONTEXT"]
        wa_record = wa_map.get(x["source_record_name"].strip().lower()) if x["state"] == "WA" else None
        has_text = bool(
            t and t["additional_source_status"] == "TEXT_LOCATION_CANDIDATE_REQUIRES_IDENTITY_CHECK"
            and t["additional_source_locator"]
        )
        if found:
            grade = "PROJECT_CONTEXT_TEXT_LOCATED"
        elif has_text:
            grade = "ARCHIVED_TEXT_LOCATOR_CANDIDATE"
        elif documents:
            grade = "DOCUMENT_REVIEW_NOT_DIRECT"
        elif t and t["additional_source_url"]:
            grade = "URL_NO_TEXT_LOCATOR"
        elif t and t["native_identity_status"] == "EXACT_NATIVE_VALUE_MATCH":
            grade = "NATIVE_RECORD_ONLY"
        elif t and t["native_identity_status"] == "AMBIGUOUS_NATIVE_MATCH":
            grade = "AMBIGUOUS_NATIVE_ID"
        else:
            grade = "SOURCE_RECORD_NOT_RECOVERED"

        parent = (x["state"] == "NT" and x["source_record_name"].strip().lower() == "plenty river")
        if x["reviewed_project_group_id"]:
            identity = "GROUP_LINK_REVIEWED_SIGNOFF_PENDING"
            next_step = "VERIFY_PRIMARY_DOCUMENT_AND_STAGE"
        elif parent:
            identity = "PROSPECT_PARENT_SOURCE_TEXT_BRUCE_PROJECT"
            next_step = "CHECK_BRUCE_PARENT_CHILD_RELATION"
        elif wa_record:
            identity = "WA_PROJECT_NAME_MATCH_SCOPE_UNCHECKED"
            next_step = "CHECK_WA_PROJECT_BOUNDARY_AND_RESOURCE_STATEMENT"
        else:
            identity = "PROJECT_ID_UNRESOLVED"
            if t and t["native_identity_status"] == "AMBIGUOUS_NATIVE_MATCH":
                next_step = "RESOLVE_DUPLICATE_NATIVE_RECORD"
            elif has_text:
                next_step = "READ_LOCATED_DOCUMENT_FOR_IDENTITY"
            elif t and t["native_identity_status"] == "EXACT_NATIVE_VALUE_MATCH":
                next_step = "LINK_DEPOSIT_TO_DOCUMENTED_PROJECT"
            else:
                next_step = "RECOVER_NATIVE_ID_AND_SOURCE"

        jorc = ("WA_GOV_RESOURCE_SUMMARY_ONLY_NOT_JORC_APPROVED"
                if wa_record else "JORC_NOT_APPROVED")
        row = [
            target, x["state"], x["source_record_name"],
            x["source_entity_type"], x["reviewed_project_group_id"],
            t["native_identity_status"] if t else "NOT_IN_441_TRACE",
            t["native_snapshot_sha256"] if t else "",
            t["native_record_locator"] if t else "",
            t["search_sha256"] if t else "",
            t["additional_source_url"] if t else "",
            t["additional_source_locator"] if t else "",
            ";".join(d["review_status"] for d in documents),
            ";".join(d["evidence_id"] for d in documents),
            wa_record["source_project_name"] if wa_record else "",
            wa_record["official_stage_as_reported_Jan2026"] if wa_record else "",
            wa_record["resource_mt_reported"] if wa_record else "",
            wa_record["average_grade_pct_treo_reported"] if wa_record else "",
            "Bruce Project (NTGS EL31225 2023, Introduction p1)" if parent else "",
            grade, identity, jorc, next_step, "NO",
        ]
        record = dict(zip(COLUMNS, row))
        if len(record) != len(COLUMNS):
            raise AssertionError("Claim evidence output width")
        records.append(record)
        for k, v in (
            ("grade", grade), ("native", t["native_identity_status"] if t else "NOT_IN_441_TRACE"),
            ("identity", identity),
            ("wa_match", "EXACT_SOURCE_NAME" if wa_record else "NOT_EXACT"),
            ("next", next_step),
        ):
            stats[k][v] += 1
    records.sort(key=lambda r: r["target_id"])
    wa_matches = {r["WA_official_exact_project_match"] for r in records
                  if r["WA_official_exact_project_match"]}
    if (stats["native"]["EXACT_NATIVE_VALUE_MATCH"] != 407
            or stats["identity"]["GROUP_LINK_REVIEWED_SIGNOFF_PENDING"] != 78
            or stats["grade"]["PROJECT_CONTEXT_TEXT_LOCATED"] != 42
            or len(ev) != 46
            or len(records) != 487):
        raise ValueError("Evidence coverage sentinel mismatch")

    summary = {
        "date": date, "frozen_as_of": as_of,
        "scope": ("487 historical source-target records; evidence pointers and "
                  "claim-specific statuses, not 487 independent Projects"),
        "source_files": [
            {"path": path, "rows": len(sources[key]),
             "source_sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
            for key, path in SOURCES.items()
        ],
        "rows": len(records), "columns": len(COLUMNS),
        "unique_ids": len({r["target_id"] for r in records}),
        "counts": {k: dict(v) for k, v in stats.items()},
        "wa_official_match_rows": sum(bool(r["WA_official_exact_project_match"]) for r in records),
        "wa_official_distinct_names_exact": len(wa_matches),
        "wa_official_names_missing_exact": [
            r["source_project_name"] for r in wa if r["source_project_name"] not in wa_matches
        ],
        "direct_doc_target_ids": len(ev), "full_signoffs": 0,
        "interpretation": ("source record/document pointer review only, not original JORC "
                           "document or independently signed Project verification"),
    }
    return records, summary


def save(records, summary, out_dir: Path, date: str, *, overwrite: bool = False):
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{date}_487_evidence_claim_review.csv"
    json_path = out_dir / f"{date}_487_evidence_claim_summary.json"
    if not overwrite and (csv_path.exists() or json_path.exists()):
        raise FileExistsError(f"Output already exists: {csv_path}")
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    summary["generated_csv_sha256"] = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return csv_path, json_path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--date", default="2026-10-31")
    p.add_argument("--as-of", default="2026-10-29")
    p.add_argument("--output-dir", type=Path, default=ROOT / "work" / "evidence")
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args()
    rows, summary = build_review(args.root, as_of=args.as_of, date=args.date)
    csv_path, json_path = save(rows, summary, args.output_dir, args.date, overwrite=args.overwrite)
    print(f"records={len(rows)} evidence_review={csv_path} summary={json_path} approved_C1=0")


if __name__ == "__main__":
    main()
