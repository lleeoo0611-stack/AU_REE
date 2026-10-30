#!/usr/bin/env python3
"""Verify the original 2026-10-29 Australian REE raw archive against frozen P0.

Original archive: GitHub Actions run 40821122179, artifact 12874618255
(australia-national-unfiltered-raw-inventory).

Run locally:
  python scripts/validate_p0_raw_recovery.py --raw-root work/national_raw
  python scripts/validate_p0_raw_recovery.py  # repository-metadata-only checks

The source-native feature identity is not a Project identity.
No C1/JORC/GIS Project signoff is inferred or updated.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FILES = {
    "round2": "docs/audits/2026-10-31_487_evidence_round2_review.csv",
    "census": "docs/audits/2026-10-31_census_487_batch_review.csv",
    "scope": "docs/audits/2026-10-31_272_native_project_scope_triage.csv",
    "missing": "docs/audits/2026-10-31_23_native_source_recovery.csv",
    "sa": "docs/audits/2026-10-31_sa_10_duplicate_source_features.csv",
    "legacy": "inputs/legacy_r963_census.csv",
}
ARC = {
    "GA_AIMR_REE_2026": "entity_id",
    "GA_CRITICAL_DEPOSITS_2025": "objectid",
    "STATE_WA_MINDEX": "site_code",
    "STATE_QLD_MINOCC": "site_no",
    "STATE_TAS_MRT": "DEPOSIT_ID",
}
WFS = {
    "NSW_METINDEX": "occurrence_id",
    "VIC_MINSITE": "siteid",
    "NT_MODAT_WFS": "identifier",
}
SACSV = {
    "SA_CRITICAL_REE": ("sa_projects/SA_CRITICAL_REE.csv", "MINERAL_DEPOSIT_NO"),
    "SA_GEODATA_MINDEP": ("sa_geodata/sarig_md_details_exp.csv", "MINERAL_DEPOSIT_NO"),
}


def load_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def checksum(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate_registry(repo=REPO):
    r2 = load_csv(repo / FILES["round2"])
    base = {x["target_id"]: x for x in load_csv(repo / FILES["census"])}
    scope = load_csv(repo / FILES["scope"])
    missing = load_csv(repo / FILES["missing"])
    sa = load_csv(repo / FILES["sa"])
    legacy = load_csv(repo / FILES["legacy"])
    expected_scope = {x["target_id"] for x in r2
                      if x["round2_evidence_grade"] == "NATIVE_RECORD_ONLY"}
    expected_missing = {x["target_id"] for x in r2
                        if x["native_identifier_status_after_review"] ==
                        "NATIVE_RECORD_STILL_UNRECOVERED"}
    if (len(r2), len(scope), len(missing), len(sa), len(legacy)) != (487, 272, 23, 10, 203):
        raise ValueError("Frozen source row counts changed")
    if {x["target_id"] for x in scope} != expected_scope:
        raise ValueError("272 target IDs differ from frozen P0")
    if {x["target_id"] for x in missing} != expected_missing:
        raise ValueError("23 native targets differ from frozen P0")
    if len({x["target_id"] for x in scope}) != 272 or len({x["target_id"] for x in missing}) != 23:
        raise ValueError("Duplicate target ID")
    if any(x["project_parent_approved"] != "NO" for x in scope):
        raise ValueError("Project parent was silently approved")
    if any(x["project_parent_approval"] != "NO" for x in missing):
        raise ValueError("Missing-source project parent was silently approved")
    if any(x["project_parent_approved"] != "NO" for x in sa):
        raise ValueError("SA duplicated source features were promoted to projects")
    if Counter(x["native_parent_key_type"] for x in scope) != {
        "NO_PROJECT_PARENT_KEY_IN_NATIVE_RECORD": 268,
        "GEOLOGICAL_GROUP_NAME_ONLY": 2,
        "GEOLOGICAL_PARENT_ID_ONLY": 2,
    }:
        raise ValueError("Parent identity summary changed")
    if Counter(x["raw_feature_cardinality"] for x in scope) != {"1": 272}:
        raise ValueError("Source cardinality mismatch")
    if Counter(x["recovery_kind"] for x in missing) != {
        "ORIGINAL_GA_RAW_FEATURE_RECOVERED_FROM_ACTIONS": 7,
        "HISTORICAL_CENSUS_RAW_ROW_FOUND_ID_ABSENT": 16,
    }:
        raise ValueError("Original provenance type mismatch")
    if Counter(x["mineral_deposit_no"] for x in sa) != {"3000": 4, "11849": 6}:
        raise ValueError("SA feature count mismatch")
    for row in scope:
        src = base[row["target_id"]]
        if (row["source_key"], row["source_native_id"], row["source_name"]) != (
            src["source_key"], src["source_native_id"], src["source_record_name"]):
            raise ValueError("Source ID/name mapping changed")
    for row in missing:
        if row["recovery_kind"].startswith("HISTORICAL"):
            number = int(row["raw_source_locator"].split()[-1])
            old = legacy[number - 2]
            if old["canonical_name"] != row["source_name"] or old["state"] != row["state"]:
                raise ValueError("Legacy historic row mislocated")
            if old["project_id"].strip():
                raise ValueError("Expected empty native project_id in 16 historic records")
    return scope, missing, sa


def verify_archive(raw, scope, missing, sa, export_evidence=None):
    """Index raw government source records by native ID; check source bytes."""
    raw = Path(raw)
    if not (raw / "arcgis").is_dir() or not (raw / "sa_projects").is_dir():
        raise FileNotFoundError("Extract original GitHub Actions ZIP to raw-root")
    index = defaultdict(lambda: defaultdict(list))
    hashed = {}
    main_manifest = json.loads((raw / "national_raw_manifest.json").read_text())
    assert main_manifest.get("complete"), "Original raw archive not complete"
    for src, field in ARC.items():
        for file in sorted((raw / "arcgis" / src).glob("*/features_*.json")):
            j = json.loads(file.read_text(encoding="utf-8"))
            manifest = json.loads((file.parent / "manifest.json").read_text())
            hashes = {x["file"]: x["sha256"] for x in manifest["chunks"]}
            digest = checksum(file)
            if digest != hashes[file.name]:
                raise ValueError("Original ArcGIS SHA256 mismatch: " + str(file))
            hashed[str(file.relative_to(raw))] = digest
            for i, x in enumerate(j["features"]):
                attrs = x["attributes"]
                value = str(attrs.get(field, "") or "").strip().casefold()
                if value:
                    index[src][value].append((str(file.relative_to(raw)), i, attrs))
    for src, field in WFS.items():
        for file in sorted((raw / "wfs" / src).glob("features_*.json")):
            j = json.loads(file.read_text(encoding="utf-8"))
            digest = checksum(file)
            matching = {c["path"]: c["sha256"]
                        for c in main_manifest["sources"][src]["chunks"]}
            path_key = str(file.relative_to(raw))
            if matching.get(path_key) != digest:
                raise ValueError("Original WFS SHA256 mismatch: " + path_key)
            hashed[path_key] = digest
            for i, x in enumerate(j["features"]):
                props = x["properties"]
                value = str(props.get(field, "") or "").strip().casefold()
                if value:
                    index[src][value].append((str(file.relative_to(raw)), i, props))
    for src, (path, field) in SACSV.items():
        file = raw / path
        digest = checksum(file)
        if src == "SA_CRITICAL_REE":
            records = main_manifest["sources"]["SA_PROJECT_WFS"]
        else:
            records = main_manifest["sources"]["SA_GEODATA"]
        matching = {item["path"]: item["sha256"] for item in records}
        if matching.get(path) != digest:
            raise ValueError("Original SA CSV SHA256 mismatch: " + path)
        hashed[str(file.relative_to(raw))] = digest
        # SA GEODATA source is Windows encoded; keep raw bytes intact.
        for enc in ("utf-8-sig", "cp1252"):
            try:
                with file.open(newline="", encoding=enc) as stream:
                    entries = list(csv.DictReader(stream))
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Unable to decode original SA source: " + str(file))
        for i, attrs in enumerate(entries, 2):
            value = str(attrs.get(field, "") or "").strip().casefold()
            if value:
                index[src][value].append((str(file.relative_to(raw)), i, attrs))
    statuses = Counter()
    full_rows = []
    for row in scope:
        items = index[row["source_key"]].get(row["source_native_id"].strip().casefold(), [])
        if len(items) != int(row["raw_feature_cardinality"]):
            raise ValueError("Raw source row cardinality for " + row["target_id"] +
                             " expected=" + row["raw_feature_cardinality"] +
                             " got=" + str(len(items)))
        statuses[len(items)] += 1
        if export_evidence is not None:
            for source_path, source_index, attrs in items:
                entity_hint = next(
                    (str(attrs[k]) for k in (
                        "MINDEP_CLASS_CODE", "DEPOSIT_CLASS", "currentstatus",
                        "status", "site_type_", "site_type", "size_code",
                        "mine_status", "mineralOccurrenceType", "DEPOSIT_TYPE"
                    ) if attrs.get(k) is not None and str(attrs[k]).strip()), ""
                )
                full_rows.append({
                    "target_id": row["target_id"],
                    "state": row["state"],
                    "source_name": row["source_name"],
                    "source_key": row["source_key"],
                    "source_native_id": row["source_native_id"],
                    "original_source_file": source_path,
                    "source_index": source_index,
                    "original_source_file_sha256": hashed[source_path],
                    "entity_type_native": entity_hint,
                    "raw_source_parent_hint": str(attrs.get("proj_title") or "").strip(),
                    "raw_geological_group": str(
                        attrs.get("group_name") or attrs.get("PARENT_ID") or "").strip(),
                    "c0_only": "YES",
                    "project_parent_approved": "NO",
                })
    for row in missing:
        if row["recovery_kind"].startswith("ORIGINAL_GA"):
            file, idx = row["raw_source_locator"].split("#features[")
            idx = int(idx.rstrip("]"))
            rel = file.removeprefix("national_raw/")
            attrs = json.loads((raw / rel).read_text())["features"][idx]["attributes"]
            if (str(attrs["entity_id"]).strip() != row["source_name"]
                    or attrs["state"] != row["state"]
                    or hashed[rel] != row["raw_source_sha256"]):
                raise ValueError("Original GA archive mismatch: " + row["target_id"])
    source_rows = list(csv.DictReader((raw / SACSV["SA_CRITICAL_REE"][0]).open(
        encoding="utf-8-sig", newline="")))
    lookup = {(x["MINERAL_DEPOSIT_NO"], x["OBJECTID"]): x for x in source_rows}
    for row in sa:
        raw_row = lookup[(row["mineral_deposit_no"], row["source_objectid"])]
        if (raw_row["FID"] != row["source_fid"]
                or raw_row["MAJOR_COMMODITY_CODE"] != row["main_commodity"]
                or hashed[SACSV["SA_CRITICAL_REE"][0]] != row["source_sha256"]):
            raise ValueError("SA duplicate feature identity changed")
    if export_evidence is not None:
        output = Path(export_evidence)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            raise FileExistsError("Evidence file already exists; use a new output path")
        if len(full_rows) != 272:
            raise ValueError("Expected one archived feature per source target")
        with output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(full_rows[0]),
                                    lineterminator="\n")
            writer.writeheader()
            writer.writerows(full_rows)
    return {
        "archive_run": 40821122179, "archive_artifact_id": 12874618255,
        "scoped_targets_verified": sum(statuses.values()),
        "exact_one_feature": statuses[1], "two_features_one_native_deposit": statuses[2],
        "ga_originals_verified": 7, "historic_legacy_rows_verified": 16,
        "sa_duplicate_feature_ids_verified": 10, "sa_source_deposit_ids": 2,
        "source_chunk_hashes_verified_count": len(hashed),
        "source_gis_project_jorc_approval": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--raw-root", type=Path)
    parser.add_argument("--export-evidence", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    scope, missing, sa = validate_registry(args.repo)
    result = {"scope_rows": len(scope), "recovered_original_rows": len(missing),
              "resolved_source_feature_rows": len(sa), "project_approvals": 0}
    if args.export_evidence and not args.raw_root:
        parser.error("--export-evidence requires --raw-root")
    if args.raw_root:
        result.update(verify_archive(args.raw_root, scope, missing, sa,
                                     export_evidence=args.export_evidence))
    if args.output:
        args.output.parent.mkdir(exist_ok=True, parents=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
