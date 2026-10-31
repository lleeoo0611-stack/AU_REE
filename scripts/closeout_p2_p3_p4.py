#!/usr/bin/env python3
"""Frozen-source documentary dispositions, never Project or C1 approval.

--extract-raw --raw-root PATH selects original features after checking chunk
hashes against the 2026-10-29 archive manifests. --write/--check work offline
from that selection. Selection hashes are NOT original PDF hashes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = "docs/audits/"
PREFIX = AUDIT + "2026-10-31_p2_p3_p4_closeout"
SNAP = "data/source_snapshots/2026-10-29_p2_p3_p4_selected_features.jsonl"
MANIFEST = "data/source_snapshots/2026-10-29_p2_p3_p4_selection_manifest.json"
BASE = AUDIT + "2026-10-31_census_487_batch_review.csv"
P1 = AUDIT + "2026-10-31_p1_73_source_resolution.csv"
P2 = AUDIT + "2026-10-31_p2_28_public_terminal_desk_review.csv"
R2 = AUDIT + "2026-10-31_487_evidence_round2_review.csv"
ROUNDS = [
    AUDIT + "2026-10-31_272_project_parent_evidence_queue.csv",
    AUDIT + "2026-10-31_156_project_parent_evidence_review.csv",
    AUDIT + "2026-10-31_109_project_evidence_review.csv",
    AUDIT + "2026-10-31_70_project_evidence_review.csv",
]
LEGACY = "inputs/legacy_r963_census.csv"
ARC = {"GA_AIMR_REE_2026": "entity_id", "GA_CRITICAL_DEPOSITS_2025": "objectid",
       "STATE_WA_MINDEX": "site_code", "STATE_QLD_MINOCC": "site_no", "STATE_TAS_MRT": "DEPOSIT_ID"}
WFS = {"NSW_METINDEX": "occurrence_id", "VIC_MINSITE": "siteid", "NT_MODAT_WFS": "identifier"}
SA = {"SA_CRITICAL_REE": ("sa_projects/SA_CRITICAL_REE.csv", "SA_PROJECT_WFS"),
      "SA_GEODATA_MINDEP": ("sa_geodata/sarig_md_details_exp.csv", "SA_GEODATA")}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def unique(rows, key="target_id"):
    out = {}
    for row in rows:
        if not row[key] or row[key] in out:
            raise ValueError("Duplicate/empty " + key + ": " + row[key])
        out[row[key]] = row
    return out


def scope(root=ROOT):
    base = unique(read(root / BASE))
    hold = {k for k, r in base.items() if r["original_inclusion_gate"] ==
            "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE"}
    p1, p2 = unique(read(root / P1)), unique(read(root / P2))
    if len(hold) != 412 or len(p1) != 73 or len(p2) != 28 or set(p1) & set(p2):
        raise ValueError("Frozen 412 partition changed")
    if not (set(p1) | set(p2)) <= hold:
        raise ValueError("Cohort escape")
    targets = {k: base[k] for k in sorted(hold - set(p1))}
    priorities = {k: "P2" if k in p2 else "P4" if r["source_entity_type"] == "OCCURRENCE" else "P3"
                  for k, r in targets.items()}
    if Counter(priorities.values()) != {"P2": 28, "P3": 216, "P4": 95}:
        raise ValueError("339 partition changed")
    return base, targets, priorities, p2


def extract(raw, root=ROOT):
    """Exact ID lookup only; retain ALL matches, especially SA 4/6 features."""
    _, targets, _, _ = scope(root)
    mbytes = (raw / "national_raw_manifest.json").read_bytes()
    manifest = json.loads(mbytes)
    if not manifest.get("complete") or not manifest["as_of"].startswith("2026-10-29"):
        raise ValueError("Wrong/incomplete archive")
    wanted = defaultdict(set)
    for tid, row in targets.items():
        if row["source_key"]:
            wanted[row["source_key"]].add(row["source_native_id"].strip().casefold())
    index, chunks = defaultdict(list), {}

    def add_file(key, rel, expected, field, kind):
        payload = (raw / rel).read_bytes()
        actual = digest(payload)
        if actual != expected:
            raise ValueError("Archive SHA mismatch: " + rel)
        if kind == "csv":
            try:
                text = payload.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = payload.decode("cp1252")
            features = [(i, a, None) for i, a in enumerate(csv.DictReader(io.StringIO(text)), 2)]
        else:
            features = [(i, f["attributes" if kind == "arcgis" else "properties"], f.get("geometry"))
                        for i, f in enumerate(json.loads(payload)["features"])]
        used = False
        for i, attrs, geometry in features:
            value = str(attrs.get(field, "") or "").strip().casefold()
            if value in wanted[key]:
                used = True
                index[(key, value)].append({"source_path": rel,
                    "locator": ("CSV physical row " if kind == "csv" else "features[") + str(i) + ("" if kind == "csv" else "]"),
                    "original_chunk_sha256": actual, "attributes": attrs, "geometry": geometry})
        if used:
            chunks[rel] = actual

    for key, field in ARC.items():
        if key not in wanted:
            continue
        src = manifest["sources"][key]
        folder = raw / src["cache_path"]
        mb = (folder / "manifest.json").read_bytes()
        if digest(mb) != src["manifest_sha256"]:
            raise ValueError("ArcGIS manifest SHA mismatch: " + key)
        for item in json.loads(mb)["chunks"]:
            rel = (Path(src["cache_path"]) / item["file"]).as_posix()
            add_file(key, rel, item["sha256"], field, "arcgis")
    for key, field in WFS.items():
        if key in wanted:
            for item in manifest["sources"][key]["chunks"]:
                add_file(key, item["path"].replace("\\", "/"), item["sha256"], field, "wfs")
    for key, (rel, mkey) in SA.items():
        if key in wanted:
            item = next(x for x in manifest["sources"][mkey] if x["path"].replace("\\", "/") == rel)
            add_file(key, rel, item["sha256"], "MINERAL_DEPOSIT_NO", "csv")
    old = unique(read(root / LEGACY), "project_id")
    selected = []
    for tid, row in targets.items():
        legacy_row = None
        if tid.startswith("LEGACY:"):
            attrs = old[tid.removeprefix("LEGACY:")]
            if attrs["canonical_name"] != row["source_record_name"] or attrs["state"] != row["state"]:
                raise ValueError("Legacy UUID/name/state mismatch: " + tid)
            legacy_row = attrs
        if not row["source_key"]:
            if legacy_row is None:
                raise ValueError("No native key or Legacy row: " + tid)
            attrs = legacy_row
            features = [{"source_path": LEGACY, "locator": "project_id=" + attrs["project_id"],
                         "original_chunk_sha256": digest((root / LEGACY).read_bytes()),
                         "attributes": attrs, "geometry": None}]
        else:
            features = index[(row["source_key"], row["source_native_id"].strip().casefold())]
            expected = 4 if row["source_key"] == "SA_CRITICAL_REE" and row["source_native_id"] == "3000" else 6 if row["source_key"] == "SA_CRITICAL_REE" and row["source_native_id"] == "11849" else 1
            if len(features) != expected:
                raise ValueError(f"Native cardinality {tid}: {len(features)} != {expected}")
        selected.append({"target_id": tid, "source_key": row["source_key"],
                         "native_id": row["source_native_id"], "features": features,
                         "legacy_original_row": legacy_row})
    payload = ("\n".join(dumps(x) for x in selected) + "\n").encode("utf-8")
    meta = {"snapshot": "2026-10-29", "archive_run": 40821122179,
            "archive_artifact_id": 12874618255, "archive_manifest_sha256": digest(mbytes),
            "selection_sha256": digest(payload), "source_chunks": dict(sorted(chunks.items())),
            "target_count": len(selected), "government_target_count": 317, "legacy_only_target_count": 22,
            "legacy_uuid_rows_verified": 52,
            "interpretation": "Selected attributes/geometry, not original chunk bytes or technical PDF full text. Raw extraction checks original chunks; offline --check checks selection integrity only."}
    return payload, meta


def first(attrs, *keys):
    return next((str(attrs[k]).strip() for k in keys if attrs.get(k) is not None and str(attrs[k]).strip()), "")


def native_review(s):
    facts = []
    for f in s["features"]:
        a = f["attributes"]
        facts.append({"locator": f["locator"],
            "entity": first(a, "MINDEP_CLASS_CODE", "DEPOSIT_CLASS", "DEPOSIT_TYPE", "site_type_", "mineralOccurrenceType", "mine_type", "site_type", "size_code", "currentstatus", "status"),
            "commodity": first(a, "DEPOSIT_COMMODITIES", "DEPOSIT_COMMODITY_CODES", "COMMODITIES", "site_commo", "target_com", "major_comm", "commodities", "commodity", "all_commodities", "pri_comm"),
            "major_commodity": first(a, "MAJOR_COMMODITY_CODE", "main_commodity", "mineraldeposittype", "commodity", "major_comm", "pri_comm"),
            "project_or_geological_parent_hint": first(a, "proj_title", "projectname", "PARENT_ID", "group_name", "project"),
            "context": first(a, "DEPOSIT_SUMMARY", "SUMMARY_DESCRIPTION", "SITE_COMMENTS", "DEPOSIT_DESCRIPTION", "summary_desc", "work_desc", "DESCRIPTION", "description", "comments", "site_locality"),
            "resource_flag_or_text": first(a, "DB_RESOURCE_RESERVE", "RESOURCES", "is_metmin_resource", "resources", "size_"),
            "report_reference": first(a, "MAIN_REFERENCE", "reference", "source", "web_link", "DETAILS", "REPORT_REFERENCES", "ref_ids", "specification_uri"),
            "objectid_or_fid": first(a, "OBJECTID", "objectid", "FID", "id")})
    return facts


def classify(priority, p2, events):
    if priority == "P2":
        v = p2["scoped_documentary_verdict"]
        return "DESK_REVIEW_COMPLETE__" + v
    # These are terminal decisions on the available frozen corpus, not proof
    # that no Project exists or that all technical originals were searched.
    external_fields = {"round2_source_url", "additional_source_url", "parent_evidence_source",
                       "new_document_url", "external_document_url", "source_document_url"}
    if any(k in external_fields and v for e in events for k, v in e["record"].items()):
        return "HOLD_DOCUMENT_POINTER_REQUIRES_PRIMARY_SCOPE_REVIEW"
    return "C0_NATIVE_RECORD_REVIEW_COMPLETE_PROJECT_UNRESOLVED"


def validate_selected(s, b):
    tid, key = s["target_id"], s["source_key"]
    if (key, s["native_id"]) != (b["source_key"], b["source_native_id"]):
        raise ValueError("Source key/native ID mismatch: " + tid)
    if tid.startswith("LEGACY:"):
        a = s["legacy_original_row"]
        if "LEGACY:" + a["project_id"] != tid or (a["canonical_name"], a["state"]) != (b["source_record_name"], b["state"]):
            raise ValueError("Legacy identity mismatch")
    expected = 4 if key == "SA_CRITICAL_REE" and s["native_id"] == "3000" else 6 if key == "SA_CRITICAL_REE" and s["native_id"] == "11849" else 1
    if len(s["features"]) != expected:
        raise ValueError("Native cardinality mismatch: " + tid)
    identities = set()
    for f in s["features"]:
        a = f["attributes"]
        if not key:
            if "LEGACY:" + a["project_id"] != tid or (a["canonical_name"], a["state"]) != (b["source_record_name"], b["state"]):
                raise ValueError("Legacy identity mismatch")
        else:
            field = ARC.get(key) or WFS.get(key) or "MINERAL_DEPOSIT_NO"
            if str(a[field]).strip().casefold() != s["native_id"].strip().casefold():
                raise ValueError("Native attribute ID mismatch: " + tid)
        identity = (f["source_path"], f["locator"])
        if identity in identities:
            raise ValueError("Repeated source feature: " + tid)
        identities.add(identity)
        if key == "SA_CRITICAL_REE" and expected > 1:
            required = {"3000": {"13", "14", "15", "16"}, "11849": {"56", "57", "58", "59", "60", "61"}}
            if {str(x["attributes"]["OBJECTID"]) for x in s["features"]} != required[s["native_id"]]:
                raise ValueError("SA compound feature keys differ")


def build(root=ROOT):
    base, targets, priorities, p2 = scope(root)
    payload = (root / SNAP).read_bytes()
    meta = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    if digest(payload) != meta["selection_sha256"]:
        raise ValueError("Selected native payload checksum mismatch")
    selected = unique([json.loads(x) for x in payload.decode("utf-8").splitlines()])
    if set(selected) != set(targets):
        raise ValueError("Native target coverage mismatch")
    histories = defaultdict(list)
    paths = [R2] + ROUNDS + [P2]
    for path in paths:
        for tid, r in unique(read(root / path)).items():
            if tid in targets:
                histories[tid].append({"path": path, "record": r})
    names = defaultdict(list)
    for tid, b in base.items():
        names[(b["state"], b["source_record_name"].strip().casefold())].append(tid)
    rows, details = [], []
    for tid, b in targets.items():
        s, pri, events = selected[tid], priorities[tid], histories[tid]
        validate_selected(s, b)
        facts = native_review(s)
        r2 = events[0]["record"]
        original_hashes = {f["original_chunk_sha256"] for f in s["features"]}
        if b["source_key"] and r2["native_sha256"] and r2["native_sha256"] not in original_hashes:
            raise ValueError("Frozen round2 chunk hash conflict: " + tid)
        same = sorted(k for k in names[(b["state"], b["source_record_name"].strip().casefold())] if k != tid)
        documentary = p2.get(tid, {})
        latest = events[-1]
        latest_record = latest["record"]
        gaps = documentary.get("remaining_action") or latest_record.get("next_review_action") or latest_record.get("next_document_requirement") or latest_record.get("remaining_action") or r2["next_evidence_action"]
        disposition = classify(pri, documentary, events)
        row = {
            "target_id": tid, "priority": pri, "case_id": documentary.get("case_id", ""),
            "source_name": b["source_record_name"], "state": b["state"],
            "baseline_entity_type": b["source_entity_type"], "source_key": b["source_key"],
            "source_native_id": b["source_native_id"], "frozen_snapshot": "2026-10-29",
            "source_inspection": "LEGACY_UUID_ROW_VERIFIED_NOT_GOVERNMENT_ID" if not b["source_key"] else "ORIGINAL_GOVERNMENT_FEATURE_CONTENT_INSPECTED",
            "legacy_uuid_original_row_verified": "YES" if tid.startswith("LEGACY:") else "NOT_APPLICABLE",
            "native_feature_count": str(len(s["features"])),
            "source_locators_json": dumps([f["source_path"] + "#" + f["locator"] for f in s["features"]]),
            "original_chunk_sha256_json": dumps(sorted(original_hashes)),
            "inherited_related_native_chunk_sha256": r2["native_sha256"],
            "hash_scope_note": "Legacy row hash and related government feature hash have distinct scopes" if not b["source_key"] else "Original government chunk hash, not technical PDF hash",
            "selected_feature_sha256": digest(dumps(s).encode("utf-8")),
            "native_documentary_facts_json": dumps(facts),
            "source_id_disposition": "EXACT_LEGACY_UUID_RETAINED" if not b["source_key"] else "DEPOSIT_ID_MULTIPLE_SOURCE_FEATURES_RETAINED" if len(facts) > 1 else "EXACT_NATIVE_FEATURE_RETAINED",
            "prior_round2_native_status": r2["archived_native_match_status"],
            "latest_review_path": latest["path"],
            "latest_review_grade": first(latest_record, "scoped_documentary_verdict", "round6_evidence_grade", "project_parent_claim_status", "parent_review_result", "parent_claim_type", "round2_evidence_grade"),
            "review_history_count": str(len(events)),
            "documentary_references_json": dumps([{ "review_path": e["path"],
                "references": {k: v for k, v in e["record"].items() if v and
                    ("url" in k.lower() or "locator" in k.lower() or "date" in k.lower()
                     or k in {"parent_evidence_source", "evidence_effective_or_publication_date"})}}
                for e in events]),
            "existing_scoped_claim": documentary.get("source_scoped_claim") or latest_record.get("source_document_supported_claim") or r2["round2_supported_claim_scope"],
            "REE_role_disposition": documentary.get("REE_or_resource_basis") or latest_record.get("source_ree_role") or latest_record.get("REE_resource_role") or latest_record.get("source_level_ree_role") or "NATIVE_REE_METADATA_NOT_PROJECT_PRODUCT_PROOF",
            "source_to_project_relation": documentary.get("source_project_relation") or "NO_INDEPENDENT_PROJECT_LINK_APPROVED",
            "same_state_exact_name_target_ids_json": dumps(same),
            "duplicate_disposition": "REVIEW_ONLY_NO_NAME_OR_PROXIMITY_MERGE" if same else "NO_EXACT_STATE_NAME_PEER_IN_487_NOT_PROOF_OF_UNIQUENESS",
            "source_point_latitude": b["latitude"], "source_point_longitude": b["longitude"],
            "tenure_snapshot_status": b["tenure_trace_status"],
            "tenure_snapshot_overlap_count": b["tenure_spatial_overlap_count"],
            "titleholder_snapshot_status": b["legal_titleholder_review_status"],
            "reported_tenements": documentary.get("tenement_numbers", ""),
            "geography_disposition": "SOURCE_POINT_INTERSECTION_ONLY_PROJECT_FOOTPRINT_AND_TITLE_CHAIN_UNVERIFIED",
            "terminal_documentary_disposition": disposition,
            "frozen_source_review_complete": "YES",
            "inherited_public_desk_review_complete": "YES" if pri == "P2" else "NOT_CLAIMED",
            "technical_primary_fulltext_verified_this_run": "NO",
            "original_technical_document_sha256": "",
            "evidence_sufficient_for_project_approval": "NO",
            "Project_approval": "UNCHANGED_HOLD", "C1_admitted": "NO",
            "approval_work_status": "PAUSED_BY_USER_C1_13_CASE_GATE_MCDA",
            "remaining_gap_and_reopen_condition": gaps,
        }
        rows.append(row)
        details.append({**row, "selected_source": s, "documentary_history": events})
    inputs = [BASE, P1, P2, R2, *ROUNDS, LEGACY, SNAP, MANIFEST]
    summary = {
        "execution_id": "P234-DOC-CLOSEOUT-20261031-V1", "base_commit": "aeddd2e",
        "branch": "audit/p2-p3-p4-documentary-closeout", "frozen_snapshot": "2026-10-29",
        "scope_unit": "immutable source target ID, not independent Project",
        "counts": {"original_HOLD": 412, "P1_untouched": 73,
                   "P2": 28, "P2_provisional_cases": 27, "P3": 216, "P4": 95,
                   "government_source_content_inspected": 317, "legacy_only_source_rows": 22,
                   "legacy_uuid_rows_verified": 52,
                   "source_review_complete": len(rows), "new_technical_primary_fulltext_verifications": 0,
                   "new_Project_or_C1_approvals": 0},
        "dispositions": dict(sorted(Counter(r["terminal_documentary_disposition"] for r in rows).items())),
        "native_cardinality": dict(sorted(Counter(r["native_feature_count"] for r in rows).items())),
        "by_priority_dispositions": {p: dict(sorted(Counter(r["terminal_documentary_disposition"] for r in rows if r["priority"] == p).items())) for p in ("P2", "P3", "P4")},
        "source_chunk_verification": "At raw extraction only; offline --check verifies derived selection and manifests, not absent original bytes",
        "primary_document_limit": "Native feature content inspection and inherited scoped desk judgments are not original technical PDF full-text verification; absence of project evidence is not evidence of project absence.",
        "input_sha256": {p: digest((root / p).read_bytes()) for p in inputs},
    }
    return rows, details, summary


def render_csv(rows):
    f = io.StringIO(newline="")
    w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return f.getvalue().encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--extract-raw", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--raw-root", type=Path)
    args = parser.parse_args()
    if args.extract_raw:
        if not args.raw_root:
            parser.error("--extract-raw requires --raw-root")
        payload, meta = extract(args.raw_root)
        for path, content in [(SNAP, payload), (MANIFEST, (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))]:
            target = ROOT / path
            if target.exists() and target.read_bytes() != content:
                raise ValueError("Immutable selection differs; use a new snapshot: " + path)
            target.write_bytes(content)
        print("PASS: raw chunk hashes and exact source-native cardinality; 339 targets selected")
        return
    rows, details, summary = build()
    outputs = {PREFIX + ".csv": render_csv(rows),
               PREFIX + "_document_pointer_holds.csv": render_csv([r for r in rows if r["terminal_documentary_disposition"] == "HOLD_DOCUMENT_POINTER_REQUIRES_PRIMARY_SCOPE_REVIEW"]),
               PREFIX + ".json": (json.dumps(details, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
               PREFIX + "_summary.json": (json.dumps(summary, ensure_ascii=False, indent=2) + "\n").encode("utf-8")}
    for path, payload in outputs.items():
        if args.write:
            (ROOT / path).write_bytes(payload)
        elif (ROOT / path).read_bytes() != payload:
            raise ValueError("Reproduction differs: " + path)
    print("PASS: 28/216/95 terminal documentary dispositions; no approval changes")


if __name__ == "__main__":
    main()
