#!/usr/bin/env python3
"""Build the remaining census, linkage, company, location and provenance queues.

This creates traceable derived queues, not the missing original cohort decisions.
Name-only groups are never promoted to approved Project entities.
"""
from __future__ import annotations
import csv, hashlib, json, pathlib, sqlite3, sys
from collections import Counter, defaultdict

BASE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else BASE
OUT = ROOT / "deliverable"
TARGET = ROOT / "trace_artifact/inputs/reverse_trace_targets_487.csv"
RAW = ROOT / "scheme_a_upstream/national_screening/nationwide_ree_candidates.csv"
LINKS = ROOT / "trace_artifact/work/tenement_reverse_20261029/official_site_tenement_holder_links.csv"
TRACE_STATUS = ROOT / "trace_artifact/work/tenement_reverse_20261029/target_tenement_trace_status.csv"
CATALOG = ROOT / "trace_artifact/work/tenement_reverse_20261029/tenure_source_catalog.json"
SUMMARY = ROOT / "trace_artifact/work/tenement_reverse_20261029/reverse_tenement_summary.json"
RAW_MANIFEST = ROOT / "scheme_a_upstream/national_raw/national_raw_manifest.json"
SCREEN_SUMMARY = ROOT / "scheme_a_upstream/national_screening/screening_summary.json"
SA_CROSS = OUT / "reconstructed_sa_project_deposit_crosswalk.csv"

MISSING = ["provisional_project_groups_126.csv", "legacy_203_crosswalk_audit.csv", "all_1006_evidence_decisions.csv", "E1_project_unlinked_review_queue.csv"]

def read_csv(path):
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows):
    fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)

def key(state,name):
    return (" ".join((state or "").strip().upper().split()), " ".join((name or "").strip().casefold().split()))

def h(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    targets=read_csv(TARGET); raw=read_csv(RAW); links=read_csv(LINKS); trace_status=read_csv(TRACE_STATUS)
    final=read_csv(OUT/"487_definition_review.csv")
    raw_by_id={r["candidate_id"]:r for r in raw}
    target_by_candidate={r["candidate_id"]:r for r in targets if r["candidate_id"]}
    target_ids={r["target_id"] for r in targets}
    link_by_target=defaultdict(list)
    for r in links: link_by_target[r["target_id"]].append(r)
    review_by_target={r["target_id"]:r for r in final}
    trace_by_target={r["target_id"]:r for r in trace_status}

    # Candidate inventory with current cohort membership and explicit unknown rationale.
    e1_queue=[]
    exact_groups=defaultdict(list)
    for r in raw:
        member=target_by_candidate.get(r["candidate_id"])
        row={**r,
             "cohort_target_id":member["target_id"] if member else "",
             "cohort_membership":"IN_487_UNLINKED_E1" if member else "NOT_IN_487_SELECTION",
             "original_selection_reason":"RECOVERED_FROM_487_TARGET_LIST" if member else "NOT_RECOVERED",
             "original_evidence_decision":"MISSING_UPSTREAM_DECISION_FILE",
             "reviewer_decision":"PENDING",
             "project_identity_result":"PENDING_SOURCE_REVIEW",
             "ree_role_result":"PENDING_PROJECT_LEVEL_EVIDENCE"}
        e1_queue.append(row)
        exact_groups[key(r["state"],r["name"])].append(r)
    write_csv(OUT/"reconstructed_1006_evidence_ledger.csv",e1_queue)

    # Exact state/name groups are candidate duplicate clusters only, not canonical Projects.
    group_rows=[]
    for (st,nm), rs in sorted(exact_groups.items()):
        if not nm: continue
        ids=[x["candidate_id"] for x in rs]
        group_rows.append({
            "group_key":"STATE_NAME:"+st+":"+nm,
            "state":st,"normalized_name":nm,"source_row_count":len(rs),
            "candidate_ids":" | ".join(ids),
            "source_keys":" | ".join(sorted({x["source_key"] for x in rs})),
            "native_ids":" | ".join(sorted({x["native_id"] for x in rs})),
            "entity_levels":" | ".join(sorted({x["entity_level"] for x in rs})),
            "tiers":" | ".join(sorted({x["tier"] for x in rs})),
            "commodity_text":" | ".join(sorted({x["commodity_text"] for x in rs if x["commodity_text"]})),
            "group_decision":"NAME_CLUSTER_ONLY_PENDING_PROJECT_BOUNDARY_AND_PRIMARY_SOURCE_REVIEW",
        })
    write_csv(OUT/"exact_state_name_cluster_candidates.csv",group_rows)

    # Rebuild an exact-only legacy-to-upstream crosswalk. No fuzzy or approximate name links.
    raw_by_key=defaultdict(list)
    for r in raw: raw_by_key[key(r["state"],r["name"])].append(r)
    legacy_cross=[]
    for t in targets:
        if t["cohort"]!="LEGACY_86": continue
        m=raw_by_key.get(key(t["state"],t["name"]),[])
        n=len(m)
        legacy_cross.append({
            "legacy_target_id":t["target_id"],"legacy_project_id":t["legacy_project_id"],"state":t["state"],"legacy_project_name":t["name"],
            "exact_normalized_name_match_count":n,
            "exact_match_status":"NO_EXACT_MATCH" if n==0 else "ONE_SOURCE_RECORD_CANDIDATE" if n==1 else "MULTIPLE_SOURCE_RECORDS_AMBIGUOUS",
            "candidate_ids":" | ".join(x["candidate_id"] for x in m),
            "source_keys":" | ".join(x["source_key"] for x in m),
            "native_ids":" | ".join(x["native_id"] for x in m),
            "candidate_entity_levels":" | ".join(x["entity_level"] for x in m),
            "coordinates_basis_in_original_target":t["coordinates_basis"],
            "inherited_candidate_point_ids":" | ".join(x["candidate_id"] for x in m if x.get("latitude") and x.get("longitude")),
            "decision":"PENDING_NO_NAME_ONLY_MERGE",
        })
    write_csv(OUT/"legacy_86_exact_name_crosswalk_review.csv",legacy_cross)

    # One company evidence queue per target. Roles stay disaggregated; no holder is promoted.
    companies=[]
    for t in targets:
        f=review_by_target[t["target_id"]]
        title=link_by_target.get(t["target_id"],[])
        holder=sorted({x.get("official_holder_text","").strip() for x in title if x.get("official_holder_text","").strip()})
        e1=raw_by_id.get(t.get("candidate_id",""),{})
        govt_company=f.get("known_company_operator_text_unverified","")
        companies.append({
            "target_id":t["target_id"],"cohort":t["cohort"],"state":t["state"],"source_name":t["name"],
            "canonical_project_candidate_not_approved":f.get("canonical_project_candidate_not_approved",""),
            "registered_holder_or_applicant_text_candidates":" | ".join(holder),
            "holder_source_observation_count":len(title),
            "source_inventory_operator_text":e1.get("operator", ""),
            "government_project_company_text_unverified":govt_company,
            "titleholder_relation_status":"HOLDER_OR_APPLICANT_CANDIDATE_ONLY" if holder else "NO_TITLEHOLDER_EVIDENCE",
            "developer_status":"NOT_VERIFIED","operator_status":"NOT_VERIFIED","owner_status":"NOT_VERIFIED",
            "asx_code_or_security_id":"","asic_acn_abn":"","legal_entity_id":"",
            "current_company_name":"","historical_company_names":"","transfer_or_rename_effective_date":"",
            "asx_announcement_reference":"","company_announcement_reference":"",
            "relationship_source_url":"","review_status":"PENDING_PRIMARY_SOURCE_ENTITY_RESOLUTION",
            "reviewer_decision":"","reviewer_notes":"",
        })
    write_csv(OUT/"company_entity_resolution_queue_487.csv",companies)

    # State-by-state coverage; distinguish no result from an unverified source.
    catalog=json.loads(CATALOG.read_text(encoding="utf-8")); trsum=json.loads(SUMMARY.read_text(encoding="utf-8"))
    rawman=json.loads(RAW_MANIFEST.read_text(encoding="utf-8")); screensum=json.loads(SCREEN_SUMMARY.read_text(encoding="utf-8"))
    by_state_status=defaultdict(Counter)
    for r in trace_status: by_state_status[r["state"]][r["target_status"]]+=1
    by_state_targets=Counter(t["state"] for t in targets)
    state_sources=[]
    for st in ["WA","SA","QLD","NSW","VIC","NT","TAS"]:
        sc=[s for s in catalog if s.get("state")==st or (st=="WA" and s.get("key")=="WA_MINING_TENEMENTS") or (st=="QLD" and str(s.get("key","")).startswith("QLD_")) or (st=="TAS" and str(s.get("key","")).startswith("TAS_"))]
        urls=sorted({s.get("url","") for s in sc if s.get("url")})
        statuses=" | ".join(sorted({s.get("status","") for s in sc if s.get("status")}))
        state_sources.append({
            "state":st,"target_count":by_state_targets[st],"source_discovery_status":statuses,
            "official_source_urls":" | ".join(urls),
            "target_status_counts":" | ".join(f"{k}={v}" for k,v in sorted(by_state_status[st].items())),
            "official_tenure_link_rows":sum(r["state"]==st for r in links),
            "scope_limit":"SA tenure layer not verified; separate project/deposit crosswalk is not a title register." if st=="SA" else "Official layer queried; status/date meanings remain jurisdiction-specific.",
        })
    state_sources.append({"state":"ACT","target_count":0,"source_discovery_status":rawman.get("jurisdiction_status",{}).get("ACT","NOT_IN_TARGETS"),"official_source_urls":"","target_status_counts":"","official_tenure_link_rows":0,"scope_limit":"National GA coverage only; no independent ACT state mineral survey in recovered raw manifest."})
    write_csv(OUT/"state_source_coverage_and_gaps.csv",state_sources)

    missing_rows=[{"missing_input":name,"search_scope":"available project mirror + recovered GitHub repository/artifacts","status":"NOT_FOUND","effect":"The fixed 487 can be audited; original cohort selection logic and excluded cases cannot be independently reproduced."} for name in MISSING]
    write_csv(OUT/"upstream_reproducibility_gaps.csv",missing_rows)

    five_rules=[
      {"condition_no":1,"condition":"Australian jurisdiction","minimum_evidence":"State/territory jurisdiction or coordinates within Australian jurisdiction; government source locator.","decision_values":"PASS / HOLD / CONFLICT","auto_approval":"No"},
      {"condition_no":2,"condition":"Identifiable geographic location","minimum_evidence":"Official source coordinates or georeferenced official project/deposit record; separately record point vs boundary and spatial linkage confidence.","decision_values":"PASS_POINT_BOUNDARY_UNVERIFIED / REVIEW_LINK / HOLD_NO_LOCATION / CONFLICT","auto_approval":"No"},
      {"condition_no":3,"condition":"Distinct independent mining Project identity","minimum_evidence":"Government project record, formal project technical disclosure, or independently evidenced development unit; child records remain linked observations.","decision_values":"PASS_CANDIDATE / HOLD / CONFLICT","auto_approval":"No"},
      {"condition_no":4,"condition":"REE is primary/co-product/planned recovery by-product/explicit exploration-development target","minimum_evidence":"Project-level commodity, plan, JORC/technical report, company announcement, or government project evidence; mineral presence alone is insufficient.","decision_values":"PASS_CANDIDATE / HOLD_ROLE / CONFLICT","auto_approval":"No"},
      {"condition_no":5,"condition":"Exploration/resource assessment/mining development unit","minimum_evidence":"Project stage/activity evidence at the project level, dated and cited.","decision_values":"PASS_CANDIDATE / HOLD / CONFLICT","auto_approval":"No"},
    ]
    write_csv(OUT/"five_condition_decision_rules.csv",five_rules)

    # Append the expanded review queues into SQLite with source IDs preserved.
    db=sqlite3.connect(OUT/"census_review.sqlite")
    for table,path in [("reconstructed_1006_evidence_ledger",OUT/"reconstructed_1006_evidence_ledger.csv"),("exact_state_name_cluster_candidates",OUT/"exact_state_name_cluster_candidates.csv"),("legacy_86_exact_name_crosswalk_review",OUT/"legacy_86_exact_name_crosswalk_review.csv"),("company_entity_resolution_queue_487",OUT/"company_entity_resolution_queue_487.csv"),("state_source_coverage_and_gaps",OUT/"state_source_coverage_and_gaps.csv"),("upstream_reproducibility_gaps",OUT/"upstream_reproducibility_gaps.csv"),("five_condition_decision_rules",OUT/"five_condition_decision_rules.csv")]:
        rows=read_csv(path); fields=list(rows[0]) if rows else []
        db.execute(f'DROP TABLE IF EXISTS "{table}"')
        db.execute(f'CREATE TABLE "{table}" ({", ".join(f"\"{c}\" TEXT" for c in fields)})')
        db.executemany(f'INSERT INTO "{table}" VALUES ({",".join("?" for _ in fields)})',[[str(r.get(c,"")) for c in fields] for r in rows])
    db.commit(); integrity=db.execute("PRAGMA integrity_check").fetchone()[0]; db.close()
    assert integrity=="ok"
    manifest_path=OUT/"census_review_manifest.json"
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update({
       "condition_status_counts":{k:dict(Counter(r[k] for r in final)) for k in ["condition_1_jurisdiction","condition_2_location","condition_3_distinct_project","condition_4_ree_role","condition_5_project_lifecycle"]},
       "reconstructed_1006_rows":len(e1_queue),"exact_state_name_cluster_candidates":len(group_rows),
       "legacy_86_exact_match_status":dict(Counter(r["exact_match_status"] for r in legacy_cross)),
       "company_resolution_queue_rows":len(companies),"missing_original_upstream_files":MISSING,
       "original_project_grouping_recreated":False,
       "source_hashes":{**manifest.get("source_hashes",{}),"raw_candidate_1006":h(RAW),"tenure_source_catalog":h(CATALOG)},
       "database_integrity_after_extended_workpack":integrity,
       "interpretation":"Location points are evidence of a source-record location, not project boundary. Name clusters are candidate duplicate groups only. Company roles and ASX/corporate transfer history remain per-target primary-source review items.",
    })
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"raw_candidates":len(e1_queue),"name_clusters":len(group_rows),"legacy_exact_matches":dict(Counter(r["exact_match_status"] for r in legacy_cross)),"company_queue":len(companies),"state_rows":len(state_sources),"integrity":integrity},ensure_ascii=False))

if __name__=="__main__": main()
