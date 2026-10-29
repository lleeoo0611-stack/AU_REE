#!/usr/bin/env python3
"""Rebuild the 487-row pre-MCDA census review from immutable GitHub Actions artifacts.

Inputs are the expanded upstream screening artifact, raw-source manifest,
reverse-trace artifact, and SA crosswalk when present. This script never edits
the original inputs or Project Master. All inferred Project links remain pending.
"""
from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import sqlite3
import sys
from collections import Counter, defaultdict

BASE = pathlib.Path(__file__).resolve().parent
DEFAULT = BASE
ROOT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT
OUT = ROOT / "deliverable"
TRACE = ROOT / "trace_artifact"
SCREEN = ROOT / "scheme_a_upstream"
TARGETS = TRACE / "inputs" / "reverse_trace_targets_487.csv"
RAW = SCREEN / "national_screening" / "nationwide_ree_candidates.csv"
RAW_MANIFEST = SCREEN / "national_raw" / "national_raw_manifest.json"
SCREEN_SUMMARY = SCREEN / "national_screening" / "screening_summary.json"
LINKS = TRACE / "work" / "tenement_reverse_20261029" / "official_site_tenement_holder_links.csv"
TRACE_STATUS = TRACE / "work" / "tenement_reverse_20261029" / "target_tenement_trace_status.csv"
TRACE_SUMMARY = TRACE / "work" / "tenement_reverse_20261029" / "reverse_tenement_summary.json"
SA = ROOT / "sa_official_project_deposit_crosswalk.csv"
SA_ARTIFACT_CROSSWALK = ROOT / "scheme_a_upstream" / "national_screening" / "sa_official_project_deposit_crosswalk.csv"
SA_RAW_PROJECTS = ROOT / "national_raw_upstream" / "national_raw" / "sa_projects"
SA_RAW_DEPOSITS = ROOT / "national_raw_upstream" / "national_raw" / "sa_geodata"


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    # SARIG's historic bulk CSV contains mixed legacy byte encodings; decode
    # losslessly enough for native IDs and names while retaining original archive.
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as f:
        return list(csv.DictReader(f))


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: pathlib.Path, rows: list[dict], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def norm(s: str) -> str:
    return " ".join((s or "").strip().casefold().split())


def main() -> None:
    for p in (TARGETS, RAW, RAW_MANIFEST, SCREEN_SUMMARY, LINKS, TRACE_STATUS, TRACE_SUMMARY):
        if not p.exists():
            raise FileNotFoundError(f"Required evidence input missing: {p}")
    OUT.mkdir(parents=True, exist_ok=True)
    targets = read_csv(TARGETS)
    raw = read_csv(RAW)
    links = read_csv(LINKS)
    statuses = read_csv(TRACE_STATUS)
    sa_path = SA if SA.exists() else SA_ARTIFACT_CROSSWALK
    sa = read_csv(sa_path) if sa_path.exists() else []
    if not sa:
        # Reconstruct only exact native deposit-ID ↔ official project MINERAL_DEPOSIT_NUMBER
        # relationships from the immutable statewide SA snapshot. Do not fuzzy-join names.
        project_records = []
        for p in sorted(SA_RAW_PROJECTS.glob("SA_PROJECT_*.csv")):
            project_records.extend(read_csv(p))
        deposit_ids = set()
        for p in sorted(SA_RAW_DEPOSITS.glob("sarig_md_details_exp.csv")):
            for d in read_csv(p):
                v = d.get("MINERAL_DEPOSIT_NO") or d.get("MINERAL_DEPOSIT_NUMBER") or d.get("mineral_deposit_number") or ""
                if v:
                    deposit_ids.add(str(v).strip())
        # Build links for matched target names with their native IDs; only IDs present in
        # both the target source and government project/deposit tables are accepted.
        project_by_deposit = defaultdict(list)
        for p in project_records:
            dep = str(p.get("MINERAL_DEPOSIT_NUMBER", "")).strip()
            if dep:
                project_by_deposit[dep].append(p)
        generated = []
        for t in targets:
            if t["state"] != "SA" or not t.get("source_native_id"):
                continue
            dep = str(t["source_native_id"]).strip()
            if dep not in deposit_ids:
                continue
            for p in project_by_deposit.get(dep, []):
                generated.append({
                    "target_id": t["target_id"], "state": "SA", "name": t["name"],
                    "source_key": t["source_key"], "source_native_id": dep,
                    "deposit_number": dep, "deposit_name": t["name"],
                    "match_basis": "EXACT_GOVERNMENT_NATIVE_DEPOSIT_ID",
                    "project_name": p.get("PROJECT_NAME", ""),
                    "project_site_no": p.get("SITE_NO", ""),
                    "company_text": p.get("OPERATING_COMPANY", ""),
                    "development_status": p.get("DEVELOPMENT_STATUS", ""),
                    "project_commodities": p.get("COMMODITIES", ""),
                    "ree_materiality_in_project_commodity": "EXPLICIT_REE" if "rare earth" in p.get("COMMODITIES", "").casefold() or "ree" in p.get("COMMODITIES", "").casefold() else "NOT_EXPLICIT",
                    "evidence_status": "OFFICIAL_NATIVE_ID_PROJECT_DEPOSIT_LINK_REVIEW",
                    "developer_verified": "NO_HOLDER_VS_OPERATOR_NOT_RESOLVED",
                    "source_url": "https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs",
                })
        sa = generated
        if generated:
            sa_path = OUT / "reconstructed_sa_project_deposit_crosswalk.csv"
            write_csv(sa_path, generated)
    raw_manifest = json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))
    screen_summary = json.loads(SCREEN_SUMMARY.read_text(encoding="utf-8"))
    trace_summary = json.loads(TRACE_SUMMARY.read_text(encoding="utf-8"))
    by_status = {r["target_id"]: r for r in statuses}
    raw_by_candidate = {r["candidate_id"]: r for r in raw}
    title_by_target: dict[str, list[dict]] = defaultdict(list)
    for r in links:
        title_by_target[r["target_id"]].append(r)
    sa_by_target: dict[str, list[dict]] = defaultdict(list)
    for r in sa:
        sa_by_target[r["target_id"]].append(r)

    assert len(targets) == 487 and len({r["target_id"] for r in targets}) == 487
    assert Counter(r["cohort"] for r in targets) == {"LEGACY_86": 86, "UNLINKED_E1_401": 401}
    assert len(statuses) == 487 and len({r["target_id"] for r in statuses}) == 487
    assert len(links) == 764
    for r in targets:
        if r["cohort"] == "UNLINKED_E1_401":
            src = raw_by_candidate.get(r["candidate_id"])
            assert src, f"E1 candidate does not resolve to preserved upstream row: {r['target_id']}"
            assert src["source_key"] == r["source_key"] and src["native_id"] == r["source_native_id"]

    # Only strong, exact crosswalks are automatically placed in the same review group;
    # reviewer still approves project merging. Approximate names are held separately.
    strong_links = {
        "Baggy Green": "Wudinna Project (Baggy Green deposit)",
        "BAGGY GREEN": "Wudinna Project (Baggy Green deposit)",
        "Koppamurra": "Koppamurra Project",
        "KOPPAMURRA": "Koppamurra Project",
        "Nolans Bore": "Nolans Project (Nolans Bore deposit)",
        "NOLANS BORE": "Nolans Project (Nolans Bore deposit)",
    }
    official_projects = {
        "Koppamurra": {
            "url": "https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs",
            "note": "SA official project source labels Koppamurra as a project, names REE as project commodity, and links native deposit 11871; independently corroborate current company identity.",
        },
        "Wudinna": {
            "url": "https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs",
            "note": "SA official project/deposit relation maps Baggy Green native deposit 8433 to Wudinna; project commodity includes REE. Source notes gold and REE resources are separate; review which project development unit is in scope.",
        },
        "Wudinna Project": {
            "url": "https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs",
            "note": "SA official project record identifies Wudinna as a project and includes REE in project commodities; Baggy Green is one child deposit with its own deposit ID. Keep project and deposit as separate levels in the source columns.",
        },
    }
    project_evidence = {
        "Copi Mineral Sands Project": ("Copi Mineral Sands Project", "Distinct project; NSW government project record lists REE among project commodities. Company/developer history remains open.", "https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects"),
        "Narraburra REE Project": ("Narraburra REE Project", "NSW government identifies a distinct REE project/resource. Location is carried by two source points; project-boundary link and proponent/name-transfer history need review.", "https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-priority-metals/rare-earth-elements"),
        "Barkly": ("Barkly Rare Earths Project", "NT government identifies Barkly as an REE project. E1 point and legacy project identity align by name; project boundary and company/tenure chain remain reviewable.", "https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree"),
        "Charley Creek": ("Charley Creek Project", "NT government identifies the REE project. Two geological point records and a legacy name row are observations of a candidate project; exact spatial/project linkage and company history remain open.", "https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree"),
        "Avonbank Project": ("Avonbank Project", "Victorian government identifies the project and REE-bearing mineral-sands resource; verify that source explicitly supports an REE development target/planned recovery under the strict definition.", "https://resources.vic.gov.au/landholders-and-community/key-site-updates/avonbank-mineral-sands-project"),
        "Goschen Central Project": ("Goschen Central Project", "Government project list reports a separate Goschen Central project with TREO. Keep distinct from Goschen project unless a formal development-unit link says otherwise.", "https://resources.vic.gov.au/__data/assets/pdf_file/0007/1191841/e5d62c433eee909a700e26c3201ccb6aa4893982.pdf"),
        "Goschen Central": ("Goschen Central Project", "E1 deposit names map to a Goschen Central project candidate, but repeated points and project boundary/company relationship need manual evidence review.", "https://resources.vic.gov.au/__data/assets/pdf_file/0007/1191841/e5d62c433eee909a700e26c3201ccb6aa4893982.pdf"),
        "Goschen Project": ("Goschen Rare Earths and Mineral Sands Project", "VIC government identifies a named REE and mineral-sands project. Kept distinct from Goschen Central pending formal project-identity evidence.", "https://resources.vic.gov.au/landholders-and-community/key-site-updates/goschen-rare-earths-and-mineral-sands-project"),
        "Nolans Bore": ("Nolans Project (Nolans Bore deposit)", "NT government identifies the Nolans REE project; E1 Nolans Bore is a named child deposit. Do not count the deposit separately.", "https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree"),
        "Dubbo Project": ("Dubbo Project", "Government and formal project sources identify a distinct project with planned recovery of REE; cross-check current project stage and company chain.", "https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects"),
    }
    held_role_names = {
        "Balranald Mineral Sands Project", "Euston Critical Minerals Project", "Donald Mineral Sands Project",
        "Fingerboards Project", "Fingerboards", "The Fingerboards", "Sonoran", "Tripitaka", "Typhoon",
    }
    held_role_project_names = {
        "Balranald Mineral Sands Project": "Balranald Mineral Sands Project",
        "Euston Critical Minerals Project": "Euston Critical Minerals Project",
        "Donald Mineral Sands Project": "Donald Mineral Sands Project",
        "Fingerboards Project": "Fingerboards Project",
        "Fingerboards": "Fingerboards Project",
        "The Fingerboards": "Fingerboards Project",
        "Sonoran": "Sonoran Project candidate",
        "Tripitaka": "Tripitaka Project candidate",
        "Typhoon": "Typhoon Project candidate",
    }
    held_urls = {
        "Balranald Mineral Sands Project": "https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects",
        "Euston Critical Minerals Project": "https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-priority-metals/rare-earth-elements",
        "Donald Mineral Sands Project": "https://resources.vic.gov.au/landholders-and-community/key-site-updates/donald-mineral-sands-project",
        "Fingerboards Project": "https://resources.vic.gov.au/__data/assets/pdf_file/0007/1191841/e5d62c433eee909a700e26c3201ccb6aa4893982.pdf",
        "Fingerboards": "https://resources.vic.gov.au/__data/assets/pdf_file/0007/1191841/e5d62c433eee909a700e26c3201ccb6aa4893982.pdf",
        "The Fingerboards": "https://resources.vic.gov.au/__data/assets/pdf_file/0007/1191841/e5d62c433eee909a700e26c3201ccb6aa4893982.pdf",
        "Sonoran": "https://energymining.sa.gov.au/industry/minerals-and-mining/mineral-commodities/rare_earths",
        "Tripitaka": "https://energymining.sa.gov.au/industry/minerals-and-mining/mineral-commodities/rare_earths",
        "Typhoon": "https://energymining.sa.gov.au/industry/minerals-and-mining/mineral-commodities/rare_earths",
    }

    out_rows: list[dict] = []
    for t in targets:
        upstream = raw_by_candidate.get(t["candidate_id"], {})
        name = t["name"]
        project_name = ""
        source_url = ""
        basis = ""
        entity_level = upstream.get("entity_level", "Historical Project row")
        ree_status = "UNKNOWN_PENDING_PROJECT_LEVEL_EVIDENCE"
        project_status = "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE"
        project_link_status = "NOT_ESTABLISHED"
        source_case = project_evidence.get(name)
        if name == "Baggy Green" and t["source_key"] == "GA_AIMR_REE_2026":
            # A national deposit point has no native SA project/deposit join key;
            # preserve it as a candidate child record but do not claim exact linkage.
            source_case = None
        if source_case and t["cohort"] == "LEGACY_86":
            project_name, basis, source_url = source_case
            entity_level = "Project candidate"
            ree_status = "GOVERNMENT_PROJECT_LEVEL_REE_ROLE_REVIEWABLE"
            project_status = "PROJECT_CANDIDATE_REVIEW"
            project_link_status = "OFFICIAL_PROJECT_EVIDENCE_OR_NAME_CANDIDATE"
        elif name in official_projects and t["cohort"] == "UNLINKED_E1_401":
            project_name = name + " Project"
            basis = official_projects[name]["note"]
            source_url = official_projects[name]["url"]
            entity_level = "Official project row"
            ree_status = "GOVERNMENT_PROJECT_COMMODITY_REVIEWABLE"
            project_status = "PROJECT_CANDIDATE_REVIEW"
            project_link_status = "OFFICIAL_PROJECT_RECORD"
        elif name in strong_links and t["cohort"] == "UNLINKED_E1_401":
            project_name = strong_links[name]
            basis = "Name/native-ID link to official SA project/deposit crosswalk; this is an entity-link candidate. Preserve source row as a child and approve linkage only after reviewer check."
            source_url = "https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs"
            entity_level = upstream.get("entity_level", "Deposit")
            ree_status = "OFFICIAL_PROJECT_COMMODITY_CANDIDATE"
            project_status = "PROJECT_CANDIDATE_REVIEW"
            project_link_status = "OFFICIAL_PROJECT_DEPOSIT_LINK_REVIEW"
        elif name in held_role_names:
            project_name = held_role_project_names[name]
            basis = "Existing government project/mineral-sands evidence establishes a mineral project or REE-bearing mineral context, but this reviewed record does not establish REE as explicit target, co-product, or planned recovery product. HOLD pending formal project-level evidence; do not treat as a negative finding."
            source_url = held_urls[name]
            entity_level = "Project/site candidate"
            ree_status = "INSUFFICIENT_REE_ROLE_EVIDENCE"
            project_status = "HOLD_REE_ROLE"
            project_link_status = "PROJECT_CANDIDATE"

        if name == "Wudinna" and upstream.get("source_key") == "GA_CRITICAL_DEPOSITS_2025":
            project_name = "Wudinna Project"
            basis = "Geoscience Australia candidate point uses name Wudinna. SA official project record is a candidate name match, but the national source point does not carry the SA deposit native ID; retain linkage as review-only."
            source_url = "https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs"
            entity_level = upstream.get("entity_level", "Deposit")
            ree_status = "OFFICIAL_PROJECT_NAME_CANDIDATE"
            project_status = "PROJECT_CANDIDATE_REVIEW"
            project_link_status = "NAME_MATCH_REVIEW_NOT_NATIVE_ID"

        coordinate_ok = bool(t["latitude"] and t["longitude"])
        jurisdiction_status = "PASS_AU_STATE_CODE" if t["state"] in {"WA", "SA", "QLD", "NSW", "VIC", "NT", "TAS"} else "REVIEW"
        location_status = "HOLD_LOCATION_NOT_VERIFIED" if not coordinate_ok else (
            "HOLD_POINT_NOT_PROJECT_BOUNDARY" if t["coordinates_basis"] == "OFFICIAL_SOURCE_POINT_UNVERIFIED_GEOMETRY" else "REVIEW_LOCATION_MATCH"
        )
        distinct_status = "PASS_PROJECT_SOURCE_CANDIDATE" if project_name else "HOLD_INDEPENDENT_PROJECT_IDENTITY"
        lifecycle_status = "REVIEW_EXPLORATION_RESOURCE_OR_MINING_STAGE" if project_name else "HOLD_PROJECT_UNIT_UNRESOLVED"
        if source_case and name == "Avonbank Project":
            ree_status = "HOLD_REE_ROLE_NEEDS_EXPLICIT_RECOVERY_OR_TARGET"
            project_status = "HOLD_REE_ROLE"
        if name in held_role_names:
            project_status = "HOLD_REE_ROLE"

        status = by_status[t["target_id"]]
        title = title_by_target.get(t["target_id"], [])
        sa_links = sa_by_target.get(t["target_id"], [])
        tenure_status = status["target_status"]
        if tenure_status == "TENURE_INTERSECTS_PENDING_COMPANY_VERIFICATION":
            tenure_note = f"{len(title)} point-in-polygon official title intersections; title-holder is only a holder/applicant candidate, not proof of project developer/operator."
        elif tenure_status == "NO_OVERLAP_IN_QUERIED_LAYERS":
            tenure_note = "No intersection in the queried layer/date snapshot. Does not prove no historical, adjoining, or unqueried tenure relationship."
        elif tenure_status == "OFFICIAL_TENEMENT_LAYER_NOT_VERIFIED":
            tenure_note = "State tenure source not validated; zero links must not be interpreted as no tenure."
        else:
            tenure_note = "No usable matched coordinate for point-in-polygon tenure query."
        sa_ids = "; ".join(sorted({x.get("deposit_number", "") for x in sa_links if x.get("deposit_number")}))
        sa_projects = "; ".join(sorted({x.get("project_name", "") for x in sa_links if x.get("project_name")}))
        operators = "; ".join(sorted({upstream.get("operator", "")} - {""}))
        if not operators and sa_links:
            operators = "; ".join(sorted({x.get("company_text", "") for x in sa_links if x.get("company_text")}))
        if not source_url and sa_links:
            source_url = sa_links[0].get("source_url", "")
        if not basis and upstream:
            basis = f"Upstream screening row says tier={upstream.get('tier')}; source name/native ID only is not proof of an independent Project. Commodity/context: {upstream.get('commodity_text','')} {upstream.get('mineral_text','')} {upstream.get('context_excerpt','')}"
        out_rows.append({
            **t,
            "upstream_entity_level": upstream.get("entity_level", "Historical Project" if t["cohort"] == "LEGACY_86" else ""),
            "upstream_tier": upstream.get("tier", "LEGACY_NOT_IN_1006_E1_SOURCE"),
            "upstream_commodity_text": upstream.get("commodity_text", ""),
            "upstream_mineral_text": upstream.get("mineral_text", ""),
            "upstream_context_excerpt": upstream.get("context_excerpt", ""),
            "upstream_operator_text": upstream.get("operator", ""),
            "upstream_candidate_id_exact_match": "YES" if upstream else "LEGACY_ID_PRESERVED",
            "jurisdiction_check": jurisdiction_status,
            "location_check": location_status,
            "location_evidence": t["coordinates_basis"],
            "project_identity_check": distinct_status,
            "project_linkage_check": project_link_status,
            "canonical_project_candidate_not_approved": project_name,
            "entity_level_assessed": entity_level,
            "project_lifecycle_check": lifecycle_status,
            "ree_role_check": ree_status,
            "definition_screen_status": project_status,
            "tenure_trace_status": tenure_status,
            "tenure_observation_count": len(title),
            "tenure_candidate_holder_texts": "; ".join(sorted({x["official_holder_text"] for x in title if x.get("official_holder_text")})),
            "tenure_note": tenure_note,
            "sa_official_deposit_ids": sa_ids,
            "sa_official_project_names": sa_projects,
            "sa_crosswalk_match_basis": "; ".join(sorted({x.get("match_basis", "") for x in sa_links if x.get("match_basis")})),
            "known_company_operator_text_unverified": operators,
            "source_evidence_note": basis,
            "project_evidence_url": source_url,
            "evidence_status": "AVAILABLE_ROW_LEVEL" if (source_url or upstream) else "MISSING",
            "company_asx_name_transfer_review": "PENDING_HUMAN_ENTITY_RESOLUTION",
            "project_dedup_group_candidate": project_name or ("UNRESOLVED:" + t["target_id"]),
            "project_dedup_decision": "CANDIDATE_PENDING_REVIEW" if project_name else "NOT_LINKED",
            "reviewer_decision": "",
            "reviewer_notes": "",
        })

    # Project-level rollup is explicitly a candidate set, not a final count.
    roll: dict[str, list[dict]] = defaultdict(list)
    for r in out_rows:
        if r["canonical_project_candidate_not_approved"]:
            roll[r["canonical_project_candidate_not_approved"]].append(r)
    project_rows = []
    for pname, rows in sorted(roll.items()):
        project_rows.append({
            "canonical_project_candidate_not_approved": rows[0]["canonical_project_candidate_not_approved"],
            "candidate_group_key": pname,
            "candidate_observation_count": len(rows),
            "target_ids_preserved": " | ".join(r["target_id"] for r in rows),
            "source_names": " | ".join(sorted({r["name"] for r in rows})),
            "states": " | ".join(sorted({r["state"] for r in rows})),
            "cohorts": " | ".join(sorted({r["cohort"] for r in rows})),
            "minimum_definition_status": "; ".join(sorted({r["definition_screen_status"] for r in rows})),
            "open_review": "Confirm independent development decision unit; resolve child Deposit/Occurrence links; confirm current and historical developer/operator/name/transfer chain; retain all source IDs.",
            "review_decision": "PENDING",
        })

    queue = [r for r in out_rows if r["definition_screen_status"].startswith("HOLD") or r["project_dedup_decision"] != "CANDIDATE_PENDING_REVIEW"]
    write_csv(OUT / "487_definition_review.csv", out_rows)
    write_csv(OUT / "project_dedup_candidates.csv", project_rows)
    write_csv(OUT / "review_queue.csv", queue)

    con = sqlite3.connect(OUT / "census_review.sqlite")
    con.execute("DROP TABLE IF EXISTS row_review")
    con.execute("DROP TABLE IF EXISTS project_dedup_candidates")
    con.execute("DROP TABLE IF EXISTS review_queue")
    for table, rows in (("row_review", out_rows), ("project_dedup_candidates", project_rows), ("review_queue", queue)):
        fields = list(rows[0]) if rows else []
        con.execute(f'CREATE TABLE "{table}" ({", ".join(f"\"{x}\" TEXT" for x in fields)})')
        con.executemany(f'INSERT INTO "{table}" VALUES ({",".join("?" for _ in fields)})', [[str(r.get(k, "")) for k in fields] for r in rows])
    con.commit()
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    con.close()
    assert integrity == "ok"

    missing_upstream = [
        "provisional_project_groups_126.csv",
        "legacy_203_crosswalk_audit.csv",
        "all_1006_evidence_decisions.csv",
        "E1_project_unlinked_review_queue.csv",
    ]
    summary = {
        "scope": "census and entity linkage only; no MCDA",
        "target_rows": len(out_rows),
        "cohort_counts": dict(Counter(r["cohort"] for r in out_rows)),
        "definition_status_counts": dict(Counter(r["definition_screen_status"] for r in out_rows)),
        "tenure_status_counts": dict(Counter(r["tenure_trace_status"] for r in out_rows)),
        "project_candidate_groups_not_approved": len(project_rows),
        "review_queue_rows": len(queue),
        "title_intersection_rows": len(links),
        "sa_crosswalk_rows": len(sa),
        "five_conditions": ["Australian jurisdiction", "identifiable location", "distinct independent Project identity", "REE role in official/formal project evidence", "exploration/resource assessment/mining-development unit"],
        "missing_upstream_files": missing_upstream,
        "raw_archive_complete_for_declared_scope": raw_manifest.get("complete"),
        "raw_jurisdiction_status": raw_manifest.get("jurisdiction_status"),
        "upstream_screened_candidates": screen_summary.get("screened_candidate_records"),
        "upstream_screen_tiers": screen_summary.get("tier_counts"),
        "trace_source_status": trace_summary.get("source_status"),
        "source_hashes": {
            "targets_487": sha(TARGETS), "upstream_candidates_1006": sha(RAW),
            "raw_manifest": sha(RAW_MANIFEST), "official_tenure_links": sha(LINKS),
            "trace_status": sha(TRACE_STATUS),
            "sa_crosswalk": sha(sa_path) if sa_path.exists() else None,
        },
        "database_integrity": integrity,
        "result_interpretation": "PASS/HOLD values are evidence review states, not MCDA inclusion decisions. All candidate project groupings require human approval; title holder is not equated with developer/operator.",
    }
    (OUT / "census_review_manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"rows": len(out_rows), "project_candidate_groups": len(project_rows), "review_queue": len(queue), "status": summary["definition_status_counts"], "output": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
