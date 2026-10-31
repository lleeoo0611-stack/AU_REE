#!/usr/bin/env python3
"""P0/P1: deduplicate 48 frozen project-parent leads without promoting census entities.

All grouping IDs are pinned in the curated CSV and are *review* IDs, not
authoritative project_master.project_id. Python 3.11+, standard library only.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("docs/audits/2026-10-31_p1_parent_identity_review.csv")
CENSUS = Path("docs/audits/2026-10-31_census_487_batch_review.csv")
GROUPS = Path("inputs/source_review_20261031/p1_48_parent_group_evidence.csv")
CLAIMS = Path("inputs/source_review_20261031/p1_48_resource_claims.csv")
OUT_LINKS = Path("docs/audits/2026-10-31_p1_48_source_parent_crosswalk.csv")
OUT_GROUPS = Path("docs/audits/2026-10-31_p1_25_provisional_parent_groups.csv")
OUT_RES = Path("docs/audits/2026-10-31_p1_48_resource_basis_review.csv")
OUT_SUMMARY = Path("docs/audits/2026-10-31_p1_48_dedupe_summary.json")

LINK_COLUMNS = [
    "target_id", "state", "source_name", "source_key", "source_native_id",
    "native_feature_locator", "native_chunk_sha256", "provisional_group_key",
    "canonical_parent_candidate", "source_site_key", "source_site_name_record_count",
    "source_site_name_coordinate_spread_km", "latitude", "longitude",
    "source_point_role", "source_point_inside_project_polygon",
    "documentary_parent_relation", "ree_resource_mre_inheritable_to_source",
    "identity_approval", "ree_role_approval", "C1_approval", "remaining_action"
]
GROUP_COLUMNS = [
    "provisional_group_key", "state", "source_parent_label",
    "canonical_parent_candidate", "source_record_count", "source_site_name_count",
    "source_target_ids", "source_site_names",
    "source_coordinate_centroid_lat_REVIEW_ONLY",
    "source_coordinate_centroid_lon_REVIEW_ONLY",
    "maximum_source_point_separation_km", "spatial_span_flag",
    "relation_evidence_class", "boundary_evidence_class", "ree_role_evidence_class",
    "resource_basis_class", "resource_claim_rows",
    "evidence_source_url", "evidence_publication_date", "evidence_locator",
    "geometry_polygon_intersection", "independent_project_approval",
    "JORC_TREO_approval", "C1_approval", "next_action"
]
RES_COLUMNS = [
    "statement_id", "provisional_group_key", "scope_name", "statement_class",
    "statement_publication_date", "as_of_cutoff_admissibility",
    "JORC_classification", "ore_mt", "grade_value", "grade_unit", "grade_basis",
    "cutoff_value_text", "contained_REO_t_reported",
    "contained_basis_mass_t_calculated_QA_ONLY", "difference_vs_reported_pct",
    "resource_relationship", "source_url", "source_locator", "approval_status",
    "scoreable_TREO_resource_value", "notes"
]
CUTOFF = "2026-10-29"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalise(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).casefold()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    p1, l1, p2, l2 = map(math.radians, (*a, *b))
    dlat, dlon = p2 - p1, l2 - l1
    h = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(h)))


def pair_spread(coords: list[tuple[float, float]]) -> float:
    return max((distance_km(p, q) for i, p in enumerate(coords)
                for q in coords[i + 1:]), default=0.0)


def build(root: Path = ROOT):
    review = read_csv(root / SOURCE)
    base = {r["target_id"]: r for r in read_csv(root / CENSUS)}
    parent = [x for x in review if x["p1_category"] == "PARENT_CANDIDATE"]
    groups = read_csv(root / GROUPS)
    claims = read_csv(root / CLAIMS)
    assert len(parent) == len({r["target_id"] for r in parent}) == 48
    assert len(groups) == 25
    assert len({r["source_parent_label"] for r in groups}) == 25
    assert len({r["provisional_group_key"] for r in groups}) == 25
    assert len(claims) == len({r["statement_id"] for r in claims}) == 14
    assert all(r["geometry_polygon_intersection"] == "NOT_PERFORMED" for r in groups)
    assert all(r["approval_status"] == "C0_REVIEW_NOT_APPROVED" for r in groups)
    by_label = {r["source_parent_label"]: r for r in groups}
    by_id = {r["provisional_group_key"]: r for r in groups}
    assert set(by_label) == {x["parent_project_candidate"] for x in parent}
    assert all(x["provisional_group_key"] in by_id for x in claims)
    assert all(x["approval_status"] == "REFERENCE_ONLY" for x in claims)

    sources_by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    site_coords: dict[str, list[tuple[float, float]]] = defaultdict(list)
    site_names = Counter()
    for row in parent:
        raw = base[row["target_id"]]
        assert raw["original_inclusion_gate"] == "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE"
        assert row["native_chunk_sha256"] and len(row["native_chunk_sha256"]) == 64
        assert raw["latitude"] and raw["longitude"]
        lat, lon = float(raw["latitude"]), float(raw["longitude"])
        assert -45 <= lat <= -10 and 112 <= lon <= 155
        site_key = row["state"] + ":" + normalise(row["source_name"])
        site_coords[site_key].append((lat, lon))
        site_names[site_key] += 1
        sources_by_group[by_label[row["parent_project_candidate"]]["provisional_group_key"]].append(row)

    link_rows = []
    for row in parent:
        raw = base[row["target_id"]]
        group = by_label[row["parent_project_candidate"]]
        key = row["state"] + ":" + normalise(row["source_name"])
        link_rows.append({
            "target_id": row["target_id"], "state": row["state"],
            "source_name": row["source_name"], "source_key": row["source_key"],
            "source_native_id": row["source_native_id"],
            "native_feature_locator": row["native_feature_locator"],
            "native_chunk_sha256": row["native_chunk_sha256"],
            "provisional_group_key": group["provisional_group_key"],
            "canonical_parent_candidate": group["canonical_parent_candidate"],
            "source_site_key": key,
            "source_site_name_record_count": site_names[key],
            "source_site_name_coordinate_spread_km": f"{pair_spread(site_coords[key]):.3f}",
            "latitude": raw["latitude"], "longitude": raw["longitude"],
            "source_point_role": "SOURCE_GEOLOGICAL_FEATURE_NOT_PROJECT_CENTROID",
            "source_point_inside_project_polygon": "NOT_TESTED",
            "documentary_parent_relation": group["relation_evidence_class"],
            "ree_resource_mre_inheritable_to_source": "NO_SCOPE_ALLOCATION_APPROVED",
            "identity_approval": "NO", "ree_role_approval": "NO",
            "C1_approval": "NO",
            "remaining_action": group["adjudication_note"]
        })
    link_rows.sort(key=lambda x: (x["provisional_group_key"], x["state"], x["source_name"], x["target_id"]))

    counts = Counter(c["provisional_group_key"] for c in claims)
    group_rows = []
    for g in groups:
        rows = sources_by_group[g["provisional_group_key"]]
        assert rows, g["provisional_group_key"]
        coords = [(float(base[r["target_id"]]["latitude"]),
                   float(base[r["target_id"]]["longitude"])) for r in rows]
        spread = pair_spread(coords)
        group_rows.append({
            "provisional_group_key": g["provisional_group_key"],
            "state": g["state"], "source_parent_label": g["source_parent_label"],
            "canonical_parent_candidate": g["canonical_parent_candidate"],
            "source_record_count": len(rows),
            "source_site_name_count": len({r["state"] + ":" + normalise(r["source_name"]) for r in rows}),
            "source_target_ids": "|".join(sorted(r["target_id"] for r in rows)),
            "source_site_names": "|".join(sorted({r["source_name"] for r in rows})),
            "source_coordinate_centroid_lat_REVIEW_ONLY": f"{sum(x for x, _ in coords) / len(coords):.6f}",
            "source_coordinate_centroid_lon_REVIEW_ONLY": f"{sum(y for _, y in coords) / len(coords):.6f}",
            "maximum_source_point_separation_km": f"{spread:.3f}",
            "spatial_span_flag": "WIDE_SOURCES_GEOMETRY_REQUIRED" if spread > 25 else
                                 "NEAR_SOURCE_POINTS_NOT_POLYGON_PROOF",
            "relation_evidence_class": g["relation_evidence_class"],
            "boundary_evidence_class": g["boundary_evidence_class"],
            "ree_role_evidence_class": g["ree_role_evidence_class"],
            "resource_basis_class": g["resource_basis_class"],
            "resource_claim_rows": counts[g["provisional_group_key"]],
            "evidence_source_url": g["evidence_source_url"],
            "evidence_publication_date": g["evidence_publication_date"],
            "evidence_locator": g["evidence_locator"],
            "geometry_polygon_intersection": "NOT_PERFORMED",
            "independent_project_approval": "NO",
            "JORC_TREO_approval": "NO",
            "C1_approval": "NO",
            "next_action": g["adjudication_note"]
        })
    group_rows.sort(key=lambda x: x["provisional_group_key"])

    resource_rows = []
    for r in claims:
        mt = float(r["ore_mt"])
        grade = float(r["grade_value"])
        if r["grade_unit"] == "ppm":
            mass = mt * grade
        elif r["grade_unit"] == "%":
            mass = mt * grade * 10000
        else:
            raise AssertionError("Unrecognized grade unit")
        reported = r["contained_REO_t_reported"]
        delta = (100 * (mass - float(reported)) / float(reported)) if reported else None
        date = r["statement_publication_date"]
        date_status = ("UNDETERMINED_UNDATED_SOURCE" if not date else
                       "CUTOFF_EXCLUDED" if date > CUTOFF else "DATE_WITHIN_CUTOFF")
        rr = dict(r)
        rr.update({
            "as_of_cutoff_admissibility": date_status,
            "contained_basis_mass_t_calculated_QA_ONLY": f"{mass:.1f}",
            "difference_vs_reported_pct": f"{delta:.2f}" if delta is not None else "",
            "scoreable_TREO_resource_value": "NO_NOT_SIGNED_OFF",
        })
        resource_rows.append(rr)
    resource_rows.sort(key=lambda r: r["statement_id"])

    total_site_names = len(site_names)
    assert total_site_names == 39, total_site_names
    assert sum(int(r["source_record_count"]) for r in group_rows) == 48
    assert len(link_rows) == 48
    assert all(r["source_point_inside_project_polygon"] == "NOT_TESTED" for r in link_rows)
    assert all(r["scoreable_TREO_resource_value"] == "NO_NOT_SIGNED_OFF" for r in resource_rows)
    # Aileron nesting and Yttria reporting totals must never be summed with components.
    relation = {r["statement_id"]: r["resource_relationship"] for r in resource_rows}
    assert relation["P1R-002"].startswith("STRICT_SUBSET_OF_P1R-001")
    assert relation["P1R-009"] == "TOTAL_CHECK_ONLY_NO_SUM_WITH_COMPONENTS"
    assert {r["resource_relationship"] for r in resource_rows if r["provisional_group_key"] == "P1G-0023"} == {
        "HISTORICAL_VERSION_CONFLICT_REVIEW", "ALTERNATIVE_UNDATED_VALUE_NOT_AUTOSUPERSEDING"}

    summary = {
        "audit_date": "2026-10-31", "snapshot_as_of": CUTOFF,
        "baseline_branch": "research/p0-p1-parent-identity-20261031",
        "total_source_rows": 48, "distinct_source_site_name_keys": total_site_names,
        "provisional_parent_groups": len(group_rows),
        "independently_approved_project_count": 0,
        "verified_source_point_in_project_polygon_count": 0,
        "C1_approved_count": 0,
        "resource_claim_rows": len(resource_rows),
        "resource_basis_counts": dict(sorted(Counter(r["grade_basis"] for r in resource_rows).items())),
        "ree_role_evidence_counts": dict(sorted(Counter(r["ree_role_evidence_class"] for r in group_rows).items())),
        "wide_group_source_spreads_gt25km": [r["provisional_group_key"] for r in group_rows
            if r["spatial_span_flag"] == "WIDE_SOURCES_GEOMETRY_REQUIRED"],
        "data_inputs": [str(SOURCE), str(CENSUS), str(GROUPS), str(CLAIMS)],
        "warning": "25 pinned parent labels are review groups, NOT verified unique Australian REE Projects. "
                   "Government GIS boundary intersection has not been performed. Reported HM and TREO "
                   "basis and nested MRE statements cannot be combined."
    }
    return link_rows, group_rows, resource_rows, summary


def write_csv(path: Path, rows: list[dict], keys: list[str]):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    links, groups, resources, stats = build(ROOT)
    outputs = [(OUT_LINKS, links, LINK_COLUMNS), (OUT_GROUPS, groups, GROUP_COLUMNS),
               (OUT_RES, resources, RES_COLUMNS)]
    if args.write:
        for p, rows, keys in outputs:
            write_csv(ROOT / p, rows, keys)
        (ROOT / OUT_SUMMARY).write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n",
                                        encoding="utf-8")
    if args.check:
        for p, rows, _ in outputs:
            assert read_csv(ROOT / p) == [{k: str(v) for k, v in r.items()} for r in rows], p
        assert json.loads((ROOT / OUT_SUMMARY).read_text(encoding="utf-8")) == stats
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
