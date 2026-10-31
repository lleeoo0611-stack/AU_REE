#!/usr/bin/env python3
"""P0 round 6 — review the frozen 70 original-only source targets.

Every output row preserves the original source-native feature, not a new Project
identity. External dated government/issuer documents have scoped evidence;
indexed original-government WAMEX reports are marked as secondary indexes
pending primary original-file verification. The census and C1 gates stay fixed.

Run:
    python scripts/audit_p0_70_project_parents.py
    python -m unittest discover -s tests -p test_p0_70_project_parents.py -v
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIOR = "docs/audits/2026-10-31_109_project_evidence_review.csv"
RAW = "data/source_snapshots/2026-10-29_272_native_features.jsonl"
LEADS = "inputs/source_review_20261031/round6_70_official_issuer_document_leads.csv"
OUT = "docs/audits/2026-10-31_70_project_evidence_review.csv"
GAPS = "docs/audits/2026-10-31_70_project_evidence_pending.csv"
SUMMARY = "docs/audits/2026-10-31_70_project_evidence_summary.json"

COLUMNS = [
    "target_id", "state", "source_name", "source_key", "source_native_id",
    "source_native_feature_locator", "source_original_chunk_sha256",
    "source_native_status", "source_native_main_commodity", "source_ree_role",
    "source_native_coordinate_lat", "source_native_coordinate_lon",
    "source_native_resource_flag", "source_native_report_ids",
    "source_native_context_excerpt", "prior_109_review_grade",
    "round6_documented_source", "round6_evidence_grade",
    "proposed_historical_project_or_context", "source_document_title",
    "source_document_url", "source_document_date_or_vintage",
    "source_document_locator", "source_document_supported_claim",
    "additional_document_url", "source_scope_note",
    "independent_external_primary_bytes_archived",
    "cross_source_same_name_review_only", "state_geometry_flag",
    "project_scope_approved", "ree_product_verified",
    "JORC_TREO_approved", "C1_approved", "next_review_action",
]
EXPLICIT = {
    "EXPLICIT_DEPOSIT_IN_REE_PROJECT",
    "EXPLICIT_DEPOSIT_IN_HISTORIC_EXPLORATION_PROJECT",
    "HISTORICAL_OUYEN_HMS_PROJECT_PARENT",
    "OFFICIAL_MINERAL_SANDS_PROJECT_HISTORICAL",
}
INDEXED_PROJECT = {"INDEXED_WAMEX_HISTORICAL_HMS_PROJECT"}
HOLD = {
    "HISTORICAL_TENEMENT_VERSUS_RECENT_PROJECT_HOLD",
    "INDEXED_WAMEX_PROSPECT_ONLY",
    "INDEXED_WAMEX_HISTORIC_TENEMENT_HOLD",
    "REGIONAL_NEAR_PROJECT_ONLY",
    "DIFFERENT_COMMODITY_SAME_LOCALITY",
    "CROSS_STATE_GEO_IDENTITY_HOLD",
}
GEOLOGICAL_ONLY = {
    "OFFICIAL_URANIUM_DEPOSIT_PROTECTED",
    "OFFICIAL_NONPRIMARY_REE_DEPOSIT",
    "OFFICIAL_URANIUM_PRIMARY_REE_MINOR",
    "OFFICIAL_HISTORIC_MONAZITE_ALLUVIAL",
    "OFFICIAL_MAP_ONLY_NOT_PROJECT_PARENT",
    "REGIONAL_GEOLOGICAL_LABEL_NOT_PROJECT",
}

def read_csv(root: Path, path: str):
    with (root / path).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def unique(rows, field, label):
    lookup = {}
    for r in rows:
        key = r[field]
        if not key or key in lookup:
            raise ValueError(f"{label}: duplicate/empty {field} {key!r}")
        lookup[key] = r
    return lookup

def att(attrs, *keys):
    for key in keys:
        val = attrs.get(key)
        if val is not None and str(val).strip() and str(val).strip().lower() not in ("none", "null"):
            return str(val).strip()
    return ""

def as_source_context(src, attrs):
    key = src["source_key"]
    if key.startswith("SA_"):
        status = att(attrs, "DEPOSIT_STATUS", "STATUS_TYPE_VALUE")
        primary = att(attrs, "MAJOR_COMMODITY_CODE")
        role = "ASSOCIATED_REE_IN_MULTICOMMODITY_MINDEP"
        report_refs = att(attrs, "MAIN_REFERENCE", "DEPOSIT_SYNONYMS")
        excerpt = att(attrs, "DEPOSIT_SUMMARY", "DEPOSIT_DESCRIPTION")[:650]
        resource = att(attrs, "DB_RESOURCE_RESERVE")
    elif key == "STATE_TAS_MRT":
        status = att(attrs, "OPERATIONAL_STATUS")
        primary = att(attrs, "COMMODITY_CATEGORY")
        role = "REE_BEARING_ALLUVIAL_GEOLOGICAL_OCCURRENCE"
        report_refs = att(attrs, "REPORT_REFERENCES")
        excerpt = att(attrs, "DEPOSIT_TYPE") + " | " + att(attrs, "DEPOSIT_SIZE")
        resource = att(attrs, "RESOURCES")
    elif key == "STATE_QLD_MINOCC":
        status = att(attrs, "explore_status", "mine_status")
        primary = att(attrs, "main_commodity", "main_commodity_code")
        role = ("NON_REE_PRIMARY_GEOLOGICAL_OCCURRENCE"
                if primary and "RARE EARTH" not in primary.upper() and "YTTRIUM" not in primary.upper()
                else "REE_TARGET_GEOLOGICAL_OCCURRENCE")
        report_refs = att(attrs, "site_no")
        excerpt = (att(attrs, "site_type") + " | " + att(attrs, "site_locality"))[:650]
        resource = ""
    else:
        status = att(attrs, "currentstatus", "status")
        primary = att(attrs, "mineraldeposittype")
        role = "REE_LISTED_IN_GA_SOURCE_NOT_PRODUCT_VERIFIED"
        report_refs = att(attrs, "source")
        excerpt = (att(attrs, "mineraldeposittype") + " | " + att(attrs, "commodity"))[:650]
        resource = ""
    return status, primary, role, report_refs, excerpt, resource

def normalize(s):
    return str(s).strip().casefold()

def build(root: Path = ROOT):
    old = read_csv(root, PRIOR)
    sources = unique(
        [json.loads(line) for line in (root / RAW).read_text(encoding="utf-8").splitlines()
         if line], "target_id", "original source feature")
    leads = read_csv(root, LEADS)
    target = [x for x in old if x["new_document_evidence_available"] == "NO"]
    if len(old) != 109 or len(target) != 70 or len(sources) != 272 or len(leads) != 24:
        raise ValueError("Changed frozen P0 source population: version a new run")

    lead_lookup = unique(
        [{**r, "lookup": r["state"] + "|" + normalize(r["source_name"])} for r in leads],
        "lookup", "government and issuer evidence leads"
    )
    source_keys = {r["state"] + "|" + normalize(r["source_name"]) for r in target}
    if set(lead_lookup) - source_keys:
        raise ValueError("External evidence name not in frozen 70-source population")
    classes = EXPLICIT | INDEXED_PROJECT | HOLD | GEOLOGICAL_ONLY
    if any(r["evidence_class"] not in classes for r in leads):
        raise ValueError("Unregistered evidence claim type")

    results = []
    counts = Counter()
    states = Counter()
    official_categories = Counter()
    flags = Counter()
    for oldrow in target:
        tid = oldrow["target_id"]
        raw = sources.get(tid)
        if not raw or raw["source_key"] != oldrow["source_key"]:
            raise ValueError(f"Missing frozen government feature: {tid}")
        attrs = raw["source_attributes"]
        if (raw["native_id"] != oldrow["source_native_id"]
                or raw["original_chunk_sha256"] != oldrow["source_original_chunk_sha256"]):
            raise ValueError(f"Government native ID/source file SHA mismatch: {tid}")
        status, commodity, role, reports, excerpt, resource = as_source_context(oldrow, attrs)
        evidence = lead_lookup.get(oldrow["state"] + "|" + normalize(oldrow["source_name"]))
        if evidence:
            kind = evidence["evidence_class"]
            if kind in EXPLICIT:
                grade = "HISTORICAL_PROJECT_PARENT_DOCUMENT_CANDIDATE"
                action = "Verify dated Project/Deposit polygon and 2026 operator; verify REE product and source-scoped JORC statement"
            elif kind in INDEXED_PROJECT:
                grade = "INDEXED_HISTORICAL_PROJECT_REPORT_PRIMARY_REQUIRED"
                action = "Retrieve WAMEX original file and source byte SHA; verify official tenement polygon, date and REE product"
            elif kind in HOLD:
                grade = "PROJECT_OR_JURISDICTION_IDENTITY_HOLD"
                action = "Resolve original site geometry/tenure, source name and actual parent; do not merge on locality alone"
            else:
                grade = "EXTERNAL_GEOLOGICAL_OR_NON_REE_CONTEXT_ONLY"
                action = "Retain independent geological documentation; do not create Project without a dated Project boundary"
            parent = evidence["candidate_parent_or_context"]
            url = evidence["source_url"]
            locator = evidence["source_locator"]
            dt = evidence["original_document_date_or_vintage"]
            assert url and locator
        else:
            kind = "NO_EXTERNAL_DOCUMENT_LOCATED_THIS_ROUND"
            parent = url = locator = dt = ""
            if oldrow["state"] == "SA" and oldrow["project_parent_claim_status"] == "NATIVE_MULTICOMMODITY_NONPRIMARY_REE_DEPOSIT":
                grade = "NATIVE_SA_NONPRIMARY_REE_DEPOSIT"
                action = "Retain Cu/U/etc source and deposit evidence; seek JORC-scoped REE resource and Project tenure separately"
            elif oldrow["state"] == "TAS":
                grade = "NATIVE_TAS_ALLUVIAL_GEOLOGICAL_ONLY"
                action = "Retrieve site-specific MRT report by original deposit ID; no inferred Project or REO Resource"
            elif oldrow["state"] == "QLD" and oldrow["source_key"] == "STATE_QLD_MINOCC":
                grade = "NATIVE_QLD_OCCURRENCE_NO_PROJECT"
                action = "Retrieve Queensland geological report for site_no and verify developer/REE commodity role"
            elif oldrow["source_native_id"] in ("Eucla Basin", "Murray Basin", "Sunshine Coast", "Shoalwater Bay Training Area"):
                grade = "REGIONAL_SOURCE_LABEL_NOT_PROJECT"
                action = "Identify individual deposits/sites in region; do not treat geographical unit as standalone mine project"
            else:
                grade = "NATIVE_DEPOSIT_WITHOUT_NEW_EXTERNAL_PROJECT_DOCUMENT"
                action = "Search dated state exploration/tenement/issuer report for exact source-native ID and Project"
        st = oldrow["state"]
        lat = oldrow["native_lat"]
        lon = oldrow["native_lon"]
        jurisdiction = ""
        if st == "SA" and lat and lon and -26.2 <= float(lat) <= -26.0 and float(lon) < 129:
            jurisdiction = "SA_TAGGED_SOURCE_WEST_OF_129E_NEAR_WA_BORDER_REVIEW"
            # Geographic sanity gate applies regardless of name/document lookup.
            grade = "CROSS_STATE_SOURCE_COORDINATE_HOLD"
            action = "Verify original WA/SA cadastral jurisdiction and source deposit boundary before assigning any Project"
        if (st == "TAS" and raw["source_key"] == "STATE_TAS_MRT"
                and resource.upper() == "N"):
            role = "MRT_RESOURCE_FLAG_N_GEOLOGICAL_RECORD"
        if not raw["original_chunk_sha256"] or not raw["source_feature_locator"]:
            raise ValueError(f"Missing source provenance: {tid}")
        source_name_refs = oldrow["other_same_state_name_source_ids"]
        values = [
            tid, st, oldrow["source_name"], oldrow["source_key"], oldrow["source_native_id"],
            raw["source_feature_locator"], raw["original_chunk_sha256"],
            status, commodity, role, lat, lon, resource, reports, excerpt,
            oldrow["project_parent_claim_status"],
            "YES" if evidence else "NO", grade, parent,
            evidence["source_author"] if evidence else "", url, dt, locator,
            evidence["document_claim"] if evidence else "",
            evidence["additional_source_url"] if evidence else "",
            evidence["scope_quality_note"] if evidence else "",
            "NO", "YES" if source_name_refs else "NO", jurisdiction,
            "NO", "NO", "NO", "NO", action,
        ]
        if len(values) != len(COLUMNS):
            raise AssertionError("Output schema width")
        results.append(dict(zip(COLUMNS, values)))
        counts[grade] += 1
        states[st] += 1
        official_categories[kind] += 1
        flags[jurisdiction or "NONE"] += 1

    if len(results) != 70 or len({x["target_id"] for x in results}) != 70:
        raise ValueError("70 target IDs or uniqueness broken")
    if any(x["C1_approved"] != "NO" or x["JORC_TREO_approved"] != "NO"
           or x["project_scope_approved"] != "NO" or x["ree_product_verified"] != "NO"
           for x in results):
        raise ValueError("An unapproved Project was erroneously promoted")
    source_docs = sum(x["round6_documented_source"] == "YES" for x in results)
    summary = {
        "review_date": "2026-10-31",
        "frozen_native_as_of": "2026-10-29",
        "unit": "70 source target records; not 70 independent rare-earth development projects",
        "original_109_rows": len(old),
        "source_target_count": len(results),
        "unique_source_target_ids": len({x["target_id"] for x in results}),
        "curated_external_source_names": len(leads),
        "new_external_source_target_rows": source_docs,
        "remaining_without_new_external_source": len(results) - source_docs,
        "parent_document_candidate_rows": counts["HISTORICAL_PROJECT_PARENT_DOCUMENT_CANDIDATE"],
        "indexed_project_report_primary_pending": counts["INDEXED_HISTORICAL_PROJECT_REPORT_PRIMARY_REQUIRED"],
        "scope_and_jurisdiction_holds": (counts["PROJECT_OR_JURISDICTION_IDENTITY_HOLD"]
                                         + counts["CROSS_STATE_SOURCE_COORDINATE_HOLD"]),
        "external_geological_only_rows": counts["EXTERNAL_GEOLOGICAL_OR_NON_REE_CONTEXT_ONLY"],
        "cross_state_coordinate_flagged": flags["SA_TAGGED_SOURCE_WEST_OF_129E_NEAR_WA_BORDER_REVIEW"],
        "all_project_approvals": 0, "all_JORC_TREO_approvals": 0, "all_C1_approvals": 0,
        "by_state": dict(states),
        "by_grade": dict(counts),
        "by_evidence_type": dict(official_categories),
        "source_input_sha256": {
            p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in (PRIOR, RAW, LEADS)
        },
        "source_scope_note": ("Primary external documents and indexed government-held reports"
            " are cited as pointers, not independently archived byte hashes. HM/THM resources"
            " are never treated as TREO. No Project spatial/legal/current-stage gate passed."),
    }
    return results, summary

def publish(root: Path = ROOT):
    rows, summary = build(root)
    root.joinpath(OUT).parent.mkdir(parents=True, exist_ok=True)
    with (root / OUT).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with (root / GAPS).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(x for x in rows if x["project_scope_approved"] == "NO")
    with (root / SUMMARY).open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(summary, ensure_ascii=False))
    return summary

if __name__ == "__main__":
    publish()
