#!/usr/bin/env python3
"""Reconcile 272 unresolved native-only targets against the frozen 2026-10-29 RAW archive.

Requires the original national-unfiltered-raw-inventory Actions artifact extracted
under --raw-root. Source-declared project codes are *candidate parent links*; none
grants an independent Project/JORC/GIS approval. Uses no live/current source data.
Also byte-verifies 23 recovered native records and disambiguates 10 SA features.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FIELDS = {
    "GA_AIMR_REE_2026": ("entity_id", "entity_id"),
    "GA_CRITICAL_DEPOSITS_2025": ("objectid", "projectname"),
    "STATE_WA_MINDEX": ("site_code", "site_title"),
    "STATE_QLD_MINOCC": ("site_no", "occur_name"),
    "STATE_TAS_MRT": ("DEPOSIT_ID", "DEPOSIT_NAME"),
    "NSW_METINDEX": ("occurrence_id", "deposit_name"),
    "VIC_MINSITE": ("siteid", "mine_name"),
    "NT_MODAT_WFS": ("identifier", "name"),
    "SA_GEODATA_MINDEP": ("MINERAL_DEPOSIT_NO", "DEPOSIT_NAME"),
    "SA_CRITICAL_REE": ("MINERAL_DEPOSIT_NO", "DEPOSIT_NAME"),
}
RAW_NAMES = {
    "SA_GEODATA_MINDEP": "sa_geodata/sarig_md_details_exp.csv",
    "SA_CRITICAL_REE": "sa_projects/SA_CRITICAL_REE.csv",
}
RAW_COLS = [
    "target_id", "state", "source_name", "source_key", "source_native_id",
    "original_entity_type", "raw_match_count", "native_raw_match",
    "raw_relative_path", "raw_chunk_sha256", "raw_feature_locator",
    "raw_feature_id", "raw_feature_name", "source_declared_entity_type",
    "source_declared_project_code", "source_declared_project_title",
    "source_declared_parent_deposit_id", "project_parent_resolution",
    "source_project_relationship_basis", "raw_feature_commodity",
    "source_project_identity_approved", "C1_approved", "next_review_action",
]


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def git_blob_sha(blob: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()


def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def native(val):
    if val is None:
        return ""
    s = str(val).strip()
    return s[:-2] if re.fullmatch(r"\d+\.0", s) else s


def raw_objects(raw_dir: Path, needed: dict):
    """Return only source features with target native IDs, not entire 123k records."""
    by_key = defaultdict(list)
    hashes = {}
    for file in sorted(raw_dir.rglob("features_*.json")):
        p = file.relative_to(raw_dir).parts
        if len(p) < 3 or p[0] not in ("arcgis", "wfs"):
            continue
        source = p[1]
        if source not in needed:
            continue
        data = file.read_bytes()
        hashes[str(file.relative_to(raw_dir))] = sha(data)
        obj = json.loads(data)
        for i, feature in enumerate(obj.get("features", [])):
            attrs = feature.get("attributes") or feature.get("properties") or {}
            val = native(attrs.get(SOURCE_FIELDS[source][0]))
            if val in needed[source]:
                by_key[(source, val)].append((attrs, str(file.relative_to(raw_dir)), i))
    for key, rel in RAW_NAMES.items():
        if key not in needed:
            continue
        file = raw_dir / rel
        data = file.read_bytes()
        hashes[rel] = sha(data)
        # Historical SA export is CP-1252, explicitly preserve raw file bytes.
        decoded = data.decode("utf-8-sig" if key == "SA_CRITICAL_REE" else "cp1252")
        for line, attrs in enumerate(csv.DictReader(decoded.splitlines()), 2):
            val = native(attrs.get(SOURCE_FIELDS[key][0]))
            if val in needed[key]:
                by_key[(key, val)].append((attrs, rel, line))
    return by_key, hashes


def reconcile(root: Path, rawroot: Path, outroot: Path):
    raw_dir = rawroot / "national_raw"
    prev = read(root / "docs/audits/2026-10-31_487_evidence_round2_review.csv")
    census = {r["target_id"]: r for r in read(root / "docs/audits/2026-10-31_census_487_batch_review.csv")}
    recovery = read(root / "docs/audits/2026-10-31_23_native_source_recovery.csv")
    amb_previous = read(root / "docs/audits/2026-10-31_sa_10_duplicate_source_features.csv")
    reviewed = {r["target_id"]: r for r in read(root / "docs/audits/2026-10-31_272_project_parent_candidates_6.csv")}
    targets = [r for r in prev if r["round2_evidence_grade"] == "NATIVE_RECORD_ONLY"]
    if len(prev) != 487 or len(targets) != 272 or len(recovery) != 23 or len(amb_previous) != 10:
        raise ValueError("Frozen P0 input dimensions have changed")
    needed = defaultdict(set)
    for r in targets:
        c = census[r["target_id"]]
        key, ident = c["source_key"], native(c["source_native_id"])
        if key in SOURCE_FIELDS:
            needed[key].add(ident)
    # Preserve original SA FID records (deposit id is intentionally nonunique).
    needed["SA_CRITICAL_REE"].update(["3000", "11849"])
    # Seven previously missing GA records all share one original JSON chunk.
    needed["GA_AIMR_REE_2026"].update(native(census[r["target_id"]]["source_native_id"])
        for r in recovery if r["source_category"] == "GA_AIMR_REE_2026")
    records, hashes = raw_objects(raw_dir, needed)

    parent_rows = []
    frozen_features = []
    counts = Counter()
    for row in targets:
        c = census[row["target_id"]]
        key = c["source_key"]
        ident = native(c["source_native_id"])
        matches = records.get((key, ident), [])
        if key not in SOURCE_FIELDS:
            status, relationship = "LEGACY_NO_OFFICIAL_NATIVE_PARENT", "LEGACY_SOURCE_ONLY"
        elif len(matches) == 0:
            status, relationship = "RAW_FEATURE_NOT_MATCHED", "NO_VERIFIABLE_SOURCE_PARENT"
        elif len(matches) > 1:
            status, relationship = "RAW_NATIVE_ID_NONUNIQUE", "PARENT_NOT_PROMOTED"
        else:
            status, relationship = "RAW_FEATURE_EXACT_NATIVE_ID", "NO_PROJECT_PARENT_FIELD"
        attrs, rel, index = matches[0] if len(matches) == 1 else ({}, "", "")
        subtype = str(attrs.get("MINDEP_CLASS_CODE") or attrs.get("DEPOSIT_CLASS")
                      or attrs.get("site_type") or attrs.get("TYPE")
                      or attrs.get("mineralOccurrenceType") or row["source_entity_type"])
        proj_code = str(attrs.get("proj_code") or "").strip()
        proj_name = str(attrs.get("proj_title") or attrs.get("project") or "").strip()
        deposit_parent = str(attrs.get("PARENT_ID") or "").strip()
        proj_name = "" if proj_name.lower() in ("", "unknown", "none", "not applicable", "n/a") else proj_name
        if len(matches) == 1 and key == "STATE_WA_MINDEX" and proj_code and proj_name:
            relationship = "OFFICIAL_WA_PROJECT_CODE_AND_TITLE_RECORDED"
        elif len(matches) == 1 and key == "VIC_MINSITE" and proj_name:
            relationship = ("VIC_PROJECT_FIELD_CATEGORY_NOT_DISTINCT_PROJECT"
                            if proj_name.casefold() in ("critical minerals", "minerals", "mineral sands")
                            else "OFFICIAL_VIC_PROJECT_TEXT_CANDIDATE")
        elif len(matches) == 1 and key == "STATE_TAS_MRT" and deposit_parent:
            relationship = "TAS_PARENT_DEPOSIT_ID_NOT_PROJECT"
        elif len(matches) == 1 and subtype.lower() in ("occurrence", "mineral occurrence", "prospect"):
            relationship = "OFFICIAL_NONPROJECT_GEOLOGICAL_SOURCE_ENTITY"
        if row["target_id"] in reviewed:
            relationship = "PREVIOUSLY_REVIEWED_INDEPENDENT_SOURCE_PARENT_CANDIDATE"
            proj_name = reviewed[row["target_id"]]["documented_parent_candidate"]
        source_name_field = SOURCE_FIELDS.get(key, ("",""))[1]
        source_name = str(attrs.get(source_name_field) or "").strip()
        commodity = str(attrs.get("site_commo") or attrs.get("commodity") or
                        attrs.get("COMMODITIES") or attrs.get("DEPOSIT_COMMODITY_CODES") or
                        attrs.get("all_commodities") or attrs.get("commodities") or "").strip()
        next_action = (
            "Review official source Project code and boundary; check REE role" if
            relationship == "OFFICIAL_WA_PROJECT_CODE_AND_TITLE_RECORDED" else
            "Cross-check issuer source, project boundary and effective-date scope" if
            relationship in ("PREVIOUSLY_REVIEWED_INDEPENDENT_SOURCE_PARENT_CANDIDATE",
                             "OFFICIAL_VIC_PROJECT_TEXT_CANDIDATE") else
            "Retain in C0 as occurrence/prospect unless independent Project exists" if
            relationship == "OFFICIAL_NONPROJECT_GEOLOGICAL_SOURCE_ENTITY" else
            "Resolve parent deposit separately; do not treat as Project" if
            relationship == "TAS_PARENT_DEPOSIT_ID_NOT_PROJECT" else
            "Find official Project/Deposit linkage with source-specific geometry")
        record = dict(zip(RAW_COLS, [
            row["target_id"], row["state"], row["name"], key, ident,
            row["source_entity_type"], len(matches), status, rel,
            hashes.get(rel, "") if rel else "",
            (f"features[{index}]" if rel.endswith(".json") else f"CSV line {index}") if rel else "",
            (f"{key}:{ident}:{index}" if rel else ""), source_name, subtype,
            proj_code, proj_name, deposit_parent, relationship,
            "raw source official field" if rel else "no directly matched raw feature",
            commodity, "NO", "NO", next_action,
        ]))
        parent_rows.append(record)
        if len(matches) == 1:
            frozen_features.append({
                "target_id": row["target_id"], "source_key": key,
                "native_id": ident, "source_relative_path": rel,
                "original_chunk_sha256": hashes[rel],
                "source_feature_locator": record["raw_feature_locator"],
                "source_attributes": attrs,
            })
        counts[relationship] += 1

    # Strict, physical native-byte recovery check.
    recover_out = []
    save_roots = root / "data/raw_snapshots/2026-10-29"
    original_legacy = root / "inputs/legacy_r963_census.csv"
    legacy_blob = original_legacy.read_bytes()
    legacy_records = read(original_legacy)
    ga_path = raw_dir / "arcgis/GA_AIMR_REE_2026/be41683aff317735a685/features_0000000.json"
    ga_blob = ga_path.read_bytes()
    ga_features = json.loads(ga_blob)["features"]
    for r in recovery:
        source, target, recovered = r["source_category"], r["target_id"], False
        if source == "GA_AIMR_REE_2026":
            m = re.search(r"features\[(\d+)\]", r["raw_source_locator"])
            if m is None:
                raise AssertionError("GA original feature index missing")
            idx = int(m.group(1))
            f = ga_features[idx]["attributes"]
            recovered = (sha(ga_blob) == r["raw_source_sha256"]
                         and str(f["entity_id"]).strip().casefold() == r["source_name"].strip().casefold()
                         and f["state"] == r["state"])
            byte_source = str(ga_path.relative_to(raw_dir))
            bytes_sha = sha(ga_blob)
            git_sha = ""
        elif source == "LEGACY":
            legacy_id = target.split(":", 1)[1]
            recovered = (git_blob_sha(legacy_blob) == r["git_blob_sha"]
                         and any(x["project_id"] == legacy_id and
                                 x["canonical_name"].casefold() == r["source_name"].casefold()
                                 for x in legacy_records))
            bytes_sha = sha(legacy_blob)
            git_sha = git_blob_sha(legacy_blob)
            byte_source = "inputs/legacy_r963_census.csv"
        else:
            raise AssertionError("Unexpected original native source")
        if not recovered:
            raise AssertionError(f"Could not verify original bytes and row: {target}")
        recover_out.append({
            "target_id": target, "name": r["source_name"], "state": r["state"],
            "source": source, "original_byte_sha256": bytes_sha,
            "original_git_blob_sha": git_sha, "original_original_artifact": r["original_snapshot_location"],
            "original_byte_source_path": byte_source,
            "verified_original_record_locator": r["raw_source_locator"],
            "byte_exact_recovery": "YES", "project_parent_approved": "NO",
        })

    # SA: the true row primary key is MINDEP_ID plus OBJECTID, not MINDEP_ID alone.
    sa_blob = (raw_dir / RAW_NAMES["SA_CRITICAL_REE"]).read_bytes()
    sa_sha = sha(sa_blob)
    sa_rows = read(raw_dir / RAW_NAMES["SA_CRITICAL_REE"])
    sa_out, unique_keys = [], set()
    for row in sa_rows:
        no = native(row["MINERAL_DEPOSIT_NO"])
        if no not in ("3000", "11849"):
            continue
        oid = native(row["OBJECTID"])
        compound = f"SA_CRITICAL_REE:{no}:{oid}"
        if compound in unique_keys:
            raise ValueError("Source feature composite key collision: " + compound)
        unique_keys.add(compound)
        sa_out.append({
            "source_feature_key": compound, "deposit_id": no, "deposit_name": row["DEPOSIT_NAME"],
            "objectid": oid, "source_fid": row["FID"], "mineral_deposit_class": row["MINDEP_CLASS_CODE"],
            "major_commodity_code": row["MAJOR_COMMODITY_CODE"],
            "commodity_codes": row["DEPOSIT_COMMODITY_CODES"],
            "original_source_sha256": sa_sha,
            "feature_digest_sha256": sha(json.dumps(row,sort_keys=True,ensure_ascii=False).encode()),
            "feature_key_disambiguated": "YES", "deposit_id_shared": "YES",
            "independent_project_approval": "NO",
        })
    if len(sa_out) != 10 or len(unique_keys) != 10 or len(recover_out) != 23:
        raise ValueError("Raw recovery or SA disambiguation completeness failed")

    # Archive exactly the original source bytes, separate from derived CSVs.
    (save_roots / "ga").mkdir(parents=True, exist_ok=True)
    (save_roots / "sa").mkdir(parents=True, exist_ok=True)
    (save_roots / "ga/GA_AIMR_REE_2026_features_0000000.json").write_bytes(ga_blob)
    (save_roots / "sa/SA_CRITICAL_REE.csv").write_bytes(sa_blob)

    frozen_path = root / "data/source_snapshots/2026-10-29_272_native_features.jsonl"
    frozen_path.parent.mkdir(parents=True, exist_ok=True)
    frozen_path.write_text("".join(
        json.dumps(x, sort_keys=True, ensure_ascii=False) + "\\n"
        for x in sorted(frozen_features, key=lambda y:y["target_id"])
    ), encoding="utf-8")
    write(outroot / "2026-10-31_272_native_project_parent_audit.csv", parent_rows, RAW_COLS)
    write(outroot / "2026-10-31_23_original_native_bytes_verified.csv",
          recover_out, list(recover_out[0]))
    write(outroot / "2026-10-31_sa_10_compound_feature_keys.csv",
          sa_out, list(sa_out[0]))
    manifest = {
        "date": "2026-10-31", "as_of": "2026-10-29",
        "source_actions_run_id": 40821122179,
        "source_artifact_id": 12874618255,
        "source_artifact_name": "australia-national-unfiltered-raw-inventory",
        "source_gate": "COMPLETE_UNFILTERED_NATIONAL_RAW_ONLY",
        "target_count": len(parent_rows), "unique_target_ids": len(set(x["target_id"] for x in parent_rows)),
        "parent_classification_counts": dict(counts),
        "target_native_exact_single_record": sum(x["native_raw_match"]=="RAW_FEATURE_EXACT_NATIVE_ID" for x in parent_rows),
        "target_native_ambiguous": sum(x["native_raw_match"]=="RAW_NATIVE_ID_NONUNIQUE" for x in parent_rows),
        "target_native_unmatched": sum(x["native_raw_match"]=="RAW_FEATURE_NOT_MATCHED" for x in parent_rows),
        "raw_recovered_verified": len(recover_out), "sa_compound_keys_verified": len(sa_out),
        "frozen_native_feature_rows": len(frozen_features),
        "frozen_native_feature_sha256": sha(frozen_path.read_bytes()),
        "frozen_native_feature_path": str(frozen_path.relative_to(root)),
        "original_archived_GA_path": str((save_roots / "ga/GA_AIMR_REE_2026_features_0000000.json").relative_to(root)),
        "original_archived_SA_path": str((save_roots / "sa/SA_CRITICAL_REE.csv").relative_to(root)),
        "sa_deposit_ids_collapsed": 0, "project_approvals": 0,
        "original_sha256_GA": sha(ga_blob), "original_sha256_SA": sa_sha,
        "original_sha256_LEGACY": sha(legacy_blob),
        "inputs_sha256": {
            "round2": sha((root/"docs/audits/2026-10-31_487_evidence_round2_review.csv").read_bytes()),
            "census": sha((root/"docs/audits/2026-10-31_census_487_batch_review.csv").read_bytes()),
            "native23": sha((root/"docs/audits/2026-10-31_23_native_source_recovery.csv").read_bytes()),
        },
    }
    if manifest["target_count"] != 272 or manifest["unique_target_ids"] != 272:
        raise ValueError("Incorrect 272 target universe")
    (outroot / "2026-10-31_native_parent_reconciliation_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in manifest.items() if k in (
        "target_count", "parent_classification_counts", "target_native_exact_single_record",
        "target_native_unmatched", "raw_recovered_verified", "sa_compound_keys_verified"
    )}, ensure_ascii=False))
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--raw-root", type=Path, required=True)
    p.add_argument("--out", type=Path, default=ROOT / "docs/audits")
    a=p.parse_args()
    reconcile(a.root, a.raw_root, a.out)
