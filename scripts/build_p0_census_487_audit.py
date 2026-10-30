#!/usr/bin/env python3
"""Rebuild a non-approving census-wide P0 evidence/identity audit.

Reads *frozen, tracked* source review CSVs and joins strictly on target_id.
It never infers that Deposit/Occurrence/Tenement is an independent Project.
It never issues evidence or GIS approval and never computes an MCDA score.

Run from repo root:
  python scripts/build_p0_census_487_audit.py --run-date 2026-10-31 \
      --source-as-of 2026-10-29 --output-dir work/audits

Historical snapshot files under docs/audits/ must not be overwritten.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "full": "outputs/487_full_census_adjudication.csv",
    "gate": "outputs/487_inclusion_gate.csv",
    "member": "outputs/project_entity_membership_487.csv",
    "entity": "outputs/source_entity_register_487.csv",
    "tenure": "outputs/487_official_tenure_trace_status.csv",
    "company": "outputs/company_entity_resolution_queue_487.csv",
    "locators": "outputs/source_evidence_locator_review_95.csv",
    "group": "docs/audits/2026-10-31_project_source_screen_39.csv",
}
COLUMNS = [
    "target_id", "cohort", "state", "source_record_name", "source_key",
    "source_native_id", "candidate_id", "source_entity_id", "source_entity_type",
    "entity_level_assessed", "original_screen_status", "original_inclusion_gate",
    "reviewed_project_group_id", "group_candidate_name", "group_link_relation",
    "source_record_lookup_status", "original_coordinate_basis", "latitude",
    "longitude", "project_coordinate_approval", "tenure_trace_status",
    "tenure_spatial_overlap_count", "legal_titleholder_review_status",
    "source_evidence_status", "document_locator_rows",
    "document_locator_found_rows", "document_locator_review_state",
    "source_document_reference", "source_url_hint", "group_source_screening",
    "group_screen_source_depth", "action_priority", "primary_review_action",
    "C1_project_approval", "C1_resource_approval", "C1_gis_approval",
    "C1_release_status",
]


def read_source(root: Path, path: str) -> list[dict[str, str]]:
    with (root / path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def keyed(rows: list[dict[str, str]], name: str, field: str = "target_id") -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row[field]
        if not key or key in result:
            raise ValueError(f"{name}: blank or duplicate {field}={key}")
        result[key] = row
    return result


def source_locator_index(
    rows: list[dict[str, str]], valid_ids: set[str]
) -> dict[str, list[dict[str, str]]]:
    lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        for part in re.split(r"[;|,\s]+", row["target_ids"]):
            if part in valid_ids:
                lookup[part].append(row)
    return lookup


def classify_action(
    group_id: str, original_disposition: str, group_screen: str, entity_type: str
) -> tuple[str, str]:
    if group_id:
        if original_disposition != "INCLUDE_CANDIDATE":
            return "P2", "REVIEW_REE_ROLE_AND_INDEPENDENT_PROJECT_ID"
        if group_screen == "STUDY_DOCUMENTED_PRE_FID_SCREEN":
            return "P1", "CHECK_DATED_STUDY_JORC_REO_AND_GIS"
        if group_screen == "STUDY_WINDOW_RECHECK":
            return "P1", "VERIFY_ACTUAL_ECONOMIC_STUDY_AND_FID_DATE"
        if group_screen == "OUTSIDE_PRE_FID_CONFIRMED":
            return "P3", "RETAIN_FOR_C3_HISTORICAL_NOT_CURRENT_C1"
        if group_screen == "ON_HOLD_ACTIVITY":
            return "P2", "VERIFY_CURRENT_ACTIVE_STATUS"
        return "P2", "CHECK_REE_RESOURCE_AND_COMPLETED_STUDY"
    if entity_type in {"SOURCE_PROJECT_RECORD", "HISTORICAL_RECORD"}:
        return "P2", "ESTABLISH_DISTINCT_PROJECT_IDENTITY_AND_SOURCE_LINK"
    if entity_type == "DEPOSIT":
        return "P3", "CHECK_PARENT_PROJECT_DEPOSIT_SCOPE_AND_REE_ROLE"
    if entity_type == "PROSPECT":
        return "P3", "CHECK_PROSPECT_PROJECT_SCOPE_AND_REE_ROLE"
    return "P4", "CONFIRM_REE_OCCURRENCE_NOT_AUTOMATIC_PROJECT"


def build_review(
    root: Path, *, run_date: str, source_as_of: str, expected_count: int = 487
) -> tuple[list[dict[str, str]], dict]:
    data = {key: read_source(root, rel) for key, rel in INPUTS.items()}
    full = data["full"]
    ids = {row["target_id"] for row in full}
    if len(full) != expected_count or len(ids) != expected_count:
        raise ValueError("Unexpected baseline row count or duplicate target_id")

    maps: dict[str, dict[str, dict[str, str]]] = {}
    for name in ("gate", "member", "entity", "tenure", "company"):
        maps[name] = keyed(data[name], name)
        if set(maps[name]) != ids:
            raise ValueError(f"{name}: target_id not a strict 1:1 match to baseline")
    screens = keyed(data["group"], "39-group screen", "review_group_id")
    locators = source_locator_index(data["locators"], ids)

    result: list[dict[str, str]] = []
    metrics: dict[str, Counter[str]] = defaultdict(Counter)
    for x in full:
        target = x["target_id"]
        a = maps["gate"][target]
        b = maps["member"][target]
        ent = maps["entity"][target]
        ten = maps["tenure"][target]
        co = maps["company"][target]
        if any(y["state"] != x["state"] for y in (a, b, ten)):
            raise ValueError(f"State mismatch for {target}")
        if ent["state_or_territory"] != x["state"]:
            raise ValueError(f"Entity state mismatch for {target}")
        if any(y["cohort"] != x["cohort"] for y in (a, ten, co)):
            raise ValueError(f"Cohort mismatch for {target}")

        group_id = b["project_entity_id"]
        scr = screens.get(group_id) if group_id else None
        if group_id and scr is None:
            raise ValueError(f"Unknown review group for {target}: {group_id}")
        if a["inclusion_gate"] == "INCLUDE_CANDIDATE" and not group_id:
            raise ValueError(f"Candidate without review group: {target}")
        group_screen = scr["screening_class"] if scr else "NOT_GROUP_SOURCE_SCREENED"
        source_depth = scr["source_review_depth"] if scr else "NOT_APPLICABLE"
        loc = locators.get(target, [])
        found = [e for e in loc if e["review_status"] == "LOCATOR_FOUND_PROJECT_CONTEXT"]
        e0 = (found or loc or [None])[0]
        if not loc:
            locator_state = "NO_DOCUMENT_LOCATOR_IN_95_REVIEW"
        elif found:
            locator_state = "PROJECT_CONTEXT_LOCATOR_FOUND_NEEDS_DOCUMENT_APPROVAL"
        elif any(e["review_status"] == "RETRIEVED_NO_DIRECT_PROJECT_LOCATOR" for e in loc):
            locator_state = "FETCHED_NO_PROJECT_LOCATOR"
        else:
            locator_state = "RETRIEVAL_UNAVAILABLE"
        docref = (f'{e0["evidence_id"]} / {e0["locator_page_or_section"] or "NO_LOCATOR"}'
                  if e0 else "")
        url = (x["project_evidence_url"]
               or x["official_geoscience_or_project_register_url"]
               or a["primary_source_urls"].split(";")[0])
        priority, action = classify_action(
            group_id, a["inclusion_gate"], group_screen, b["entity_type"]
        )
        values = [
            target, x["cohort"], x["state"], x["name"], x["source_key"],
            x["source_native_id"], x["candidate_id"], ent["entity_id"],
            b["entity_type"], x["entity_level_assessed"], x["definition_screen_status"],
            a["inclusion_gate"], group_id, a["candidate_group_key"], b["relation"],
            x["source_lookup_status"], x["coordinates_basis"], x["latitude"],
            x["longitude"], "NOT_APPROVED_SOURCE_POINT_ONLY", ten["target_status"],
            ten["tenure_links"], co["titleholder_relation_status"], x["evidence_status"],
            str(len(loc)), str(len(found)), locator_state, docref, url,
            group_screen, source_depth, priority, action, "NOT_INDEPENDENTLY_APPROVED",
            "NOT_EVALUATED_AS_PROJECT_RESOURCE", "NOT_APPROVED", "C1_NOT_RELEASED",
        ]
        if len(values) != len(COLUMNS):
            raise AssertionError("Schema width mismatch")
        result.append(dict(zip(COLUMNS, values)))

        for name, value in (
            ("state", x["state"]),
            ("cohort", x["cohort"]),
            ("original_gate", a["inclusion_gate"]),
            ("entity_type", b["entity_type"]),
            ("review_link", "LINKED_TO_REVIEW_GROUP" if group_id else "UNLINKED"),
            ("review_relation", b["relation"]),
            ("review_priority", priority),
            ("review_action", action),
            ("group_screen", group_screen),
            ("locator_review_state", locator_state),
            ("tenure", ten["target_status"]),
            ("coordinate_basis", x["coordinates_basis"]),
            ("source_lookup", x["source_lookup_status"]),
            ("source_evidence_status", x["evidence_status"]),
            ("C1_release_status", "C1_NOT_RELEASED"),
        ):
            metrics[name][value] += 1
    result.sort(key=lambda row: row["target_id"])
    unique_groups = {r["reviewed_project_group_id"] for r in result
                     if r["reviewed_project_group_id"]}
    linked = sum(bool(r["reviewed_project_group_id"]) for r in result)
    if expected_count == 487 and (
        len(unique_groups) != 39 or linked != 78 or
        metrics["original_gate"]["INCLUDE_CANDIDATE"] != 69 or
        metrics["original_gate"]["HOLD_REE_ROLE"] != 6 or
        metrics["original_gate"]["HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE"] != 412
    ):
        raise ValueError("Frozen-487 sentinel counts changed unexpectedly")
    summary = {
        "schema_version": "P0_487_BATCH_REVIEW_V1",
        "run_date": run_date, "frozen_source_as_of": source_as_of,
        "repository": "lleeoo0611-stack/AU_REE",
        "scope": "487 target source records, not 487 independent Projects",
        "rows": len(result), "unique_target_ids": len(ids),
        "linked_review_groups": len(unique_groups),
        "linked_source_rows": linked, "unlinked_source_rows": len(result) - linked,
        "distinct_sources_with_locator_review": len(locators),
        "metrics": {k: dict(v) for k, v in metrics.items()},
        "gate_status": "BATCH_EVIDENCE_INVENTORY_COMPLETE_C1_NOT_RELEASED",
        "safety": ("No automatic Project approval, no JORC/REE-basis inference, "
                   "no legal-title inference from tenement spatial intersects, "
                   "no coordinate approval, no MCDA ranks"),
        "reference_paths": {
            rel: {"source_sha256": sha256((root / rel).read_bytes()).hexdigest(),
                  "rows": len(data[key])}
            for key, rel in INPUTS.items()
        },
        "output": {"columns": len(COLUMNS), "rows": len(result)},
        "method": ("Strict target_id 1:1 joins for 487 sources; 39 group joins "
                   "by reviewed Project group ID; document locator index by target_ids. "
                   "Review-only triage; no formal MCDA release."),
    }
    return result, summary


def write_outputs(
    rows: list[dict[str, str]], summary: dict, out_dir: Path, run_date: str,
    *, overwrite: bool = False
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{run_date}_census_487_batch_review"
    csv_path = out_dir / f"{stem}.csv"
    json_path = out_dir / f"{stem}_summary.json"
    if not overwrite and (csv_path.exists() or json_path.exists()):
        raise FileExistsError("Output exists: choose a new run date or explicit --overwrite")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary["output"]["path"] = str(csv_path)
    summary["output"]["sha256"] = sha256(csv_path.read_bytes()).hexdigest()
    with json_path.open("w", encoding="utf-8", newline="") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return csv_path, json_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "work" / "audits")
    parser.add_argument("--run-date", default="2026-10-31")
    parser.add_argument("--source-as-of", default="2026-10-29")
    parser.add_argument("--expected-count", type=int, default=487)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    rows, summary = build_review(
        args.root, run_date=args.run_date,
        source_as_of=args.source_as_of, expected_count=args.expected_count
    )
    csv_path, json_path = write_outputs(
        rows, summary, args.output_dir, args.run_date, overwrite=args.overwrite
    )
    print(json.dumps({
        "csv": str(csv_path), "summary": str(json_path),
        "rows": summary["rows"], "linked": summary["linked_source_rows"],
        "unlinked": summary["unlinked_source_rows"],
        "C1_status": summary["gate_status"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
