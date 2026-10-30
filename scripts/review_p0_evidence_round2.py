#!/usr/bin/env python3
"""P0 evidence recovery round 2: retain 487 census IDs; attach located claims.

Conservative scope:
- a corroborating deposit/occurrence reference is not a Project approval;
- a newly located PDF/page does not recreate missing native raw bytes;
- MinDep identifier context does not resolve multiple source-feature rows;
- unpublished/dynamic company pages cannot be used as-of a frozen date.

Reads the published, frozen P0 evidence inventory, dated source leads and WA
government resource summary. Outputs a *new* review snapshot, never updates
approved Project, JORC or GIS data. Python 3.11+ standard library only.

Example:
  python scripts/review_p0_evidence_round2.py --output-dir work/evidence
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "prior": "docs/audits/2026-10-31_487_evidence_claim_review.csv",
    "leads": "inputs/source_review_20261031/round2_external_evidence_leads.csv",
    "wa": "docs/audits/2026-10-31_wa_official_ree_project_leads.csv",
}
EXTRA = [
    "round2_evidence_grade", "round2_evidence_kind", "round2_source_url",
    "round2_source_locator", "round2_source_date_or_snapshot",
    "round2_supported_claim_scope", "round2_name_match_rule",
    "round2_new_document_found", "native_identifier_status_after_review",
    "project_identity_approved_after_review", "round2_change_reason",
]
BASE_UNRESOLVED = {
    "NATIVE_RECORD_ONLY", "SOURCE_RECORD_NOT_RECOVERED", "AMBIGUOUS_NATIVE_ID"
}


def read_csv(root: Path, path: str) -> tuple[list[str], list[dict[str, str]]]:
    with (root / path).open(encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        return list(reader.fieldnames or []), list(reader)


def build(root: Path = ROOT):
    base_fields, old = read_csv(root, SOURCES["prior"])
    _, curated = read_csv(root, SOURCES["leads"])
    _, wa = read_csv(root, SOURCES["wa"])
    if (len(old), len(curated), len(wa)) != (487, 62, 20):
        raise ValueError("Frozen source row count changed")
    original_ids = [x["target_id"] for x in old]
    if len(set(original_ids)) != 487:
        raise ValueError("Duplicate baseline target_id")
    lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for rec in curated:
        lookup[rec["state"] + "|" + rec["source_name"].strip().lower()].append(rec)
    wa_map: dict[str, dict[str, str]] = {}
    for rec in wa:
        key = rec["source_project_name"].strip().lower()
        if key in wa_map:
            raise ValueError(f"Duplicate official WA project name: {key}")
        wa_map[key] = rec

    metrics: dict[str, Counter] = defaultdict(Counter)
    result = []
    changes = []
    for old_row in old:
        row = dict(old_row)
        before = row["source_evidence_grade"]
        possibles = lookup.get(row["state"] + "|" + row["name"].strip().lower(), [])
        lead = next((x for x in possibles if x["source_name"] == row["name"]),
                    possibles[0] if possibles else None)
        wa_item = wa_map.get(row["name"].strip().lower()) if row["state"] == "WA" else None
        weak = bool(lead and re.search(
            r"PARTIAL|COMPOSITE|REGIONAL|SOURCE_SCOPE_REVIEW", lead["match_rule"]))
        grade, kind, url, locator, date, claim, match, found = (
            before, "", "", "", "", "", "", "NO")
        reason = "UNCHANGED"
        if before in BASE_UNRESOLVED and (lead or wa_item):
            if wa_item is not None and not weak:
                kind = "WA_OFFICIAL_REE_MRE_SUMMARY"
                url = wa_item["source_url"]
                locator = wa_item["source_locator"]
                date = wa_item["official_source_pub_month"]
                claim = ("Official project-resource summary; no original JORC "
                         "Statement or approved Project scope")
                match = "EXACT_WA_NAME_AND_STATE"
            elif lead is not None:
                kind = lead["evidence_kind"]
                url = lead["source_url"]
                locator = lead["locator"]
                date = lead["source_date_or_snapshot"]
                claim = lead["supported_claim_and_boundary"]
                match = lead["match_rule"]
            found = "YES"
            if before == "NATIVE_RECORD_ONLY":
                if kind == "WA_OFFICIAL_REE_MRE_SUMMARY":
                    grade = "OFFICIAL_RESOURCE_SUMMARY_LOCATED"
                elif kind == "GEOLOGICAL_REPORT_CROSS_REFERENCE":
                    grade = "GOV_HISTORICAL_GEO_CONTEXT_LOCATED"
                else:
                    grade = "EXTERNAL_PROJECT_OR_PROSPECT_DOCUMENT_LOCATED"
                reason = "ADDITIONAL_DATED_OR_LOCATED_SOURCE"
            elif before == "SOURCE_RECORD_NOT_RECOVERED":
                grade = ("PARTIAL_ALIAS_DOCUMENT_LEAD_NATIVE_UNRECOVERED" if weak
                         else "EXTERNAL_DOCUMENT_LOCATED_NATIVE_UNRECOVERED")
                reason = "DOCUMENT_LOCATED_BUT_NATIVE_SNAPSHOT_STILL_MISSING"
            else:
                grade = "AMBIGUOUS_NATIVE_ROWS_WITH_OFFICIAL_CONTEXT"
                reason = "EXTERNAL_DEPOSIT_CONTEXT_NO_UNIQUE_FEATURE_ROW"

        if before == "SOURCE_RECORD_NOT_RECOVERED":
            native = "NATIVE_RECORD_STILL_UNRECOVERED"
        elif before == "AMBIGUOUS_NATIVE_ID":
            native = "MULTIPLE_NATIVE_FEATURE_ROWS_STILL_UNRESOLVED"
        elif row["archived_native_match_status"] == "EXACT_NATIVE_VALUE_MATCH":
            native = "SOURCE_ID_EXACT_NOT_PROJECT_APPROVED"
        else:
            native = "NO_CHANGE_TO_NATIVE_STATUS"
        for col, value in zip(EXTRA, [
            grade, kind, url, locator, date, claim, match, found, native, "NO", reason
        ]):
            row[col] = value
        result.append(row)
        if grade != before:
            changes.append(row)
        metrics["before"][before] += 1
        metrics["after"][grade] += 1
        metrics["reason"][reason] += 1
        if found == "YES":
            metrics["new_kind"][kind] += 1
            metrics["new_state"][row["state"]] += 1
            metrics["old_problem_with_source"][before] += 1

    if len(result) != 487 or any(r["approved_for_C1"] != "NO" or
        r["project_identity_approved_after_review"] != "NO" for r in result):
        raise ValueError("Census or approval invariant failed")
    if (metrics["before"]["NATIVE_RECORD_ONLY"],
        metrics["before"]["SOURCE_RECORD_NOT_RECOVERED"],
        metrics["before"]["AMBIGUOUS_NATIVE_ID"]) != (336, 23, 2):
        raise ValueError("Baseline evidence-grade sentinel failed")

    as_dict = lambda key: dict(metrics[key])
    stat = {
        "release_name": "P0_SOURCE_RECOVERY_ROUND2_2026-10-31",
        "review_date": "2026-10-31",
        "frozen_census_as_of": "2026-10-29",
        "rows": 487, "columns": len(base_fields) + len(EXTRA),
        "source_sha256": {p: hashlib.sha256((root/p).read_bytes()).hexdigest()
                          for p in SOURCES.values()},
        "grades_before": as_dict("before"), "grades_after": as_dict("after"),
        "transitions": as_dict("reason"),
        "new_source_kind": as_dict("new_kind"),
        "improved_target_count": len(changes),
        "source_lead_target_count": sum(1 for x in result
                                        if x["round2_new_document_found"] == "YES"),
        "native_only_before": 336,
        "native_only_after": metrics["after"]["NATIVE_RECORD_ONLY"],
        "missing_native_or_document_before": 23,
        "missing_native_or_document_after":
            metrics["after"]["SOURCE_RECORD_NOT_RECOVERED"],
        "ambiguity_unresolved_before": 2,
        "ambiguity_unresolved_after":
            metrics["after"]["AMBIGUOUS_NATIVE_ID"],
        "ambiguity_with_context_after":
            metrics["after"]["AMBIGUOUS_NATIVE_ROWS_WITH_OFFICIAL_CONTEXT"],
        "native_bytes_missing_independent_of_doc_recovery": 23,
        "source_status": ("Extra government / issuer document leads; no re-archived "
            "primary source bytes, independent project review or signed JORC/GIS approval."),
    }
    return base_fields + EXTRA, result, changes, stat


def save(fields, rows, changes, summary, out_dir: Path, *, overwrite=False):
    out_dir.mkdir(parents=True, exist_ok=True)
    files = (
        out_dir/"2026-10-31_487_evidence_round2_review.csv",
        out_dir/"2026-10-31_evidence_round2_changed_targets.csv",
        out_dir/"2026-10-31_487_evidence_round2_summary.json",
    )
    if not overwrite and any(x.exists() for x in files):
        raise FileExistsError("Evidence review output exists; use a new directory")
    for path, data in ((files[0], rows), (files[1], changes)):
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(data)
    summary = dict(summary)
    summary["output_csv_sha256"] = hashlib.sha256(files[0].read_bytes()).hexdigest()
    with files[2].open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=ROOT/"work"/"evidence")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    fields, rows, changes, summary = build(args.root)
    files = save(fields, rows, changes, summary, args.output_dir,
                 overwrite=args.overwrite)
    print(json.dumps({
        "output": str(files[0]), "rows": len(rows),
        "improved": len(changes),
        "native_only_after": summary["native_only_after"],
        "no_original_or_document_after": summary["missing_native_or_document_after"],
        "native_feature_ambiguity_unresolved": summary["ambiguity_with_context_after"],
        "C1_approved": 0,
    }))


if __name__ == "__main__":
    main()
