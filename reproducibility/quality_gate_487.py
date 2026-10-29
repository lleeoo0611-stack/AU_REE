#!/usr/bin/env python3
"""Create normalized entity/evidence audit tables and validate the 487-row gate."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def digest(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def urls(s):
    return [x.strip() for x in (s or "").replace("|", ";").split(";") if x.strip().startswith(("https://", "http://"))]


def tri_state(value):
    v = (value or "").strip().upper()
    if v.startswith("PASS"):
        return "PASS"
    if v.startswith("FAIL") or v.startswith("EXCLUDE"):
        return "FAIL"
    if "CONFLICT" in v:
        return "CONFLICT"
    return "UNKNOWN"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--as-of-date", default=date.today().isoformat())
    args = ap.parse_args()
    root = Path(args.root).resolve()
    out = root / "deliverable"
    rows = read_csv(out / "487_row_adjudication_latest_2026-10-29.csv")
    gate_rows = read_csv(out / "487_inclusion_gate.csv")
    project_rows = read_csv(out / "project_candidate_evidence_review.csv")
    source_coverage = read_csv(out / "state_source_coverage_and_gaps.csv")

    target_ids = [r.get("target_id", "").strip() for r in rows]
    gate_ids = [r.get("target_id", "").strip() for r in gate_rows]
    dup_targets = sorted(k for k, n in Counter(target_ids).items() if k and n != 1)
    gate_missing = sorted(set(target_ids) - set(gate_ids))
    gate_extra = sorted(set(gate_ids) - set(target_ids))
    if len(rows) != 487 or len(gate_rows) != 487 or len(set(target_ids)) != 487:
        raise SystemExit(f"FAIL: expected 487 unique target rows; adjudication={len(rows)}, gate={len(gate_rows)}, unique={len(set(target_ids))}")
    if gate_missing or gate_extra:
        raise SystemExit(f"FAIL: target/gate ID mismatch; missing={gate_missing[:5]}, extra={gate_extra[:5]}")

    gate_by_id = {r["target_id"]: r for r in gate_rows}
    project_by_key = {r.get("candidate_group_key", ""): r for r in project_rows if r.get("candidate_group_key")}
    entities, memberships = [], []
    for key, p in sorted(project_by_key.items()):
        project_id = "PRJ-" + hashlib.sha256(key.casefold().encode("utf-8")).hexdigest()[:16]
        entities.append({
            "entity_id": project_id, "entity_type": "Project_candidate", "canonical_name": p.get("canonical_project_unit") or key,
            "state_or_territory": p.get("state_or_states", ""), "project_identity_status": p.get("project_identity_status", "UNKNOWN"),
            "jurisdiction_status": p.get("jurisdiction_status", "UNKNOWN"), "location_status": p.get("location_status", "UNKNOWN"),
            "ree_role_status": p.get("ree_role_status", "UNKNOWN"), "stage_status": p.get("stage_status", "UNKNOWN"),
            "inclusion_gate": p.get("inclusion_gate", "HOLD"), "dedup_decision": p.get("dedup_decision", "UNRESOLVED"),
            "current_project_or_rights_entity": p.get("current_project_or_rights_entity", ""),
            "company_history_status": "DOCUMENTED" if p.get("company_name_transfer_and_interest_history") else "UNKNOWN",
            "review_status": p.get("review_status", ""), "reviewer_decision": p.get("reviewer_decision", ""),
            "reviewer_notes": p.get("reviewer_notes", ""), "as_of_date": p.get("as_of_date", args.as_of_date),
            "registered_titleholder": "", "operator_or_proponent": "",
            "condition_1_jurisdiction_state": tri_state(p.get("jurisdiction_status")),
            "condition_2_location_state": tri_state(p.get("location_status")),
            "condition_3_project_identity_state": tri_state(p.get("project_identity_status")),
            "condition_4_ree_role_state": tri_state(p.get("ree_role_status")),
            "condition_5_lifecycle_state": tri_state(p.get("stage_status")),
        })
        ids = [x.strip() for x in (p.get("target_ids_preserved") or "").split(";") if x.strip()]
        for tid in ids:
            memberships.append((tid, project_id, p))

    # Every frozen row gets a source-level entity, even when a Project relation
    # cannot be established. This preserves coverage without inventing a link.
    known_memberships = {tid: (pid, p) for tid, pid, p in memberships}
    normalized_memberships = []
    for r in rows:
        tid = r["target_id"]
        source_key = r.get("candidate_id") or r.get("source_native_id") or tid
        source_entity_id = "SRCENT-" + hashlib.sha256((r.get("source_key", "") + "|" + source_key).encode("utf-8")).hexdigest()[:16]
        raw_type = (r.get("upstream_entity_level") or "Historical Project").strip().upper()
        source_type = next((x for x in ["DEPOSIT", "PROSPECT", "TENEMENT", "OCCURRENCE"] if x in raw_type), "SOURCE_PROJECT_RECORD" if "PROJECT" in raw_type else "HISTORICAL_RECORD")
        entities.append({"entity_id": source_entity_id, "entity_type": source_type, "canonical_name": r.get("name", ""),
                         "target_id": tid,
                         "state_or_territory": r.get("state", ""), "project_identity_status": "NOT_ESTABLISHED",
                         "jurisdiction_status": r.get("condition_1_jurisdiction", "UNKNOWN"), "location_status": r.get("condition_2_location", "UNKNOWN"),
                         "ree_role_status": r.get("condition_4_ree_role", "UNKNOWN"), "stage_status": r.get("condition_5_project_lifecycle", "UNKNOWN"),
                         "inclusion_gate": r.get("definition_screen_status", "HOLD"), "dedup_decision": "UNRESOLVED",
                         "current_project_or_rights_entity": "", "company_history_status": "UNKNOWN",
                         "review_status": r.get("evidence_status", ""), "reviewer_decision": "", "reviewer_notes": "Source record retained; Project linkage remains unverified unless separately evidenced.", "as_of_date": args.as_of_date,
                         "registered_titleholder": "", "operator_or_proponent": "",
                         "condition_1_jurisdiction_state": tri_state(r.get("condition_1_jurisdiction")),
                         "condition_2_location_state": tri_state(r.get("condition_2_location")),
                         "condition_3_project_identity_state": tri_state(r.get("condition_3_distinct_project")),
                         "condition_4_ree_role_state": tri_state(r.get("condition_4_ree_role")),
                         "condition_5_lifecycle_state": tri_state(r.get("condition_5_project_lifecycle"))})
        linked = known_memberships.get(tid)
        normalized_memberships.append({"entity_id": source_entity_id, "entity_type": source_type, "target_id": tid,
                                       "project_entity_id": linked[0] if linked else "",
                                       "source_name": r.get("name", ""), "state": r.get("state", ""),
                                       "relation": "PROJECT_LINK_REVIEWED_CANDIDATE" if linked else "UNRESOLVED_NO_PROJECT_LINK_INFERRED",
                                       "relation_evidence_status": "SOURCE_REVIEWED" if linked and linked[1].get("primary_source_urls") else "MISSING_OR_NOT_PROJECT_LEVEL",
                                       "dedup_relation": linked[1].get("dedup_decision", "UNRESOLVED") if linked else "UNRESOLVED",
                                       "original_id_preserved": "YES"})
    memberships = normalized_memberships

    evidence = []
    for p in project_rows:
        key = p.get("candidate_group_key", "")
        eid = "PRJ-" + hashlib.sha256(key.casefold().encode("utf-8")).hexdigest()[:16] if key else ""
        for u in urls(p.get("primary_source_urls", "")):
            evidence.append({"evidence_id": "SRC-" + hashlib.sha256((eid + "|" + u).encode("utf-8")).hexdigest()[:16],
                             "entity_id": eid, "target_ids": p.get("target_ids_preserved", ""), "source_url": u,
                             "source_type": "UNCLASSIFIED_REQUIRES_REVIEW", "publisher": "", "publication_date": "",
                             "accessed_date": args.as_of_date, "locator_page_or_section": "", "supports_condition": "",
                             "support_role": "UNASSESSED", "evidence_excerpt_or_summary": "",
                             "review_status": "URL_RECORDED_LOCATOR_AND_CLAIM_REVIEW_REQUIRED"})

    quality = []
    def metric(code, count, severity, meaning):
        quality.append({"check_id": code, "count": count, "severity": severity, "meaning": meaning})
    metric("TARGET_ROWS", len(rows), "PASS", "Exactly 487 row-level source records retained")
    metric("UNIQUE_TARGET_IDS", len(set(target_ids)), "PASS" if len(set(target_ids)) == 487 else "FAIL", "Original target IDs are unique")
    linked_ids = {m['target_id'] for m in memberships if m['project_entity_id']}
    metric("TARGETS_WITH_PROJECT_LINK_REVIEWED", len(linked_ids), "INFO", "Project relation from reviewed project candidate table")
    metric("TARGETS_WITHOUT_PROJECT_LINK", len(set(target_ids) - linked_ids), "REVIEW", "Remain unresolved; no name-only linking inferred")
    metric("PROJECT_CANDIDATE_ROWS", len(project_by_key), "INFO", "Candidate groups are not approved project count")
    metric("SOURCE_URLS_IN_REGISTER", len(evidence), "INFO", "URLs split into one row each; type, date, and locator not inferred")
    metric("EVIDENCE_ROWS_NEEDING_LOCATOR_REVIEW", sum(not e['locator_page_or_section'] for e in evidence), "REVIEW", "Add page/section, claim, source date, and condition supported")
    metric("UNKNOWN_COMPANY_HISTORY", sum(any(x in (p.get("company_name_transfer_and_interest_history", "") or "").upper() for x in ["PENDING", "NOT VERIFIED", "UNRESOLVED"]) or not p.get("company_name_transfer_and_interest_history") for p in project_rows), "REVIEW", "Candidate Project company/title succession not fully documented")
    metric("UNRESOLVED_DUPLICATES", sum(any(x in (p.get("dedup_decision", "") or "").upper() for x in ["PENDING", "UNRESOLVED", "HUMAN_SIGNOFF"]) for p in project_rows), "REVIEW", "Candidate Project deduplication or human signoff remains open")
    metric("JURISDICTION_COVERAGE_ROWS", len(source_coverage), "PASS" if len(source_coverage) == 8 else "REVIEW", "Coverage/gap inventory includes seven jurisdictions plus ACT/national scope")
    metric("JURISDICTIONS_WITH_TENURE_LIMITS", sum("not verified" in (x.get("scope_limit", "").lower()) or "national ga" in (x.get("scope_limit", "").lower()) for x in source_coverage), "REVIEW", "State-source limits remain explicit; coverage does not imply legal title-chain verification")
    dispositions = Counter(r.get("definition_screen_status", "UNKNOWN") for r in rows)
    for status, n in sorted(dispositions.items()):
        metric("ROW_DISPOSITION:" + status, n, "INFO", "Row disposition, not independent project count")

    project_entities = [e for e in entities if e["entity_type"] == "Project_candidate"]
    source_entities = [e for e in entities if e["entity_type"] != "Project_candidate"]
    entity_fields = ["entity_id", "entity_type", "canonical_name", "state_or_territory", "project_identity_status", "jurisdiction_status", "location_status", "ree_role_status", "stage_status", "inclusion_gate", "dedup_decision", "current_project_or_rights_entity", "registered_titleholder", "operator_or_proponent", "company_history_status", "condition_1_jurisdiction_state", "condition_2_location_state", "condition_3_project_identity_state", "condition_4_ree_role_state", "condition_5_lifecycle_state", "review_status", "reviewer_decision", "as_of_date"]
    write_csv(out / "project_entity_register.csv", project_entities, entity_fields)
    write_csv(out / "source_entity_register_487.csv", source_entities, ["target_id", "entity_id", "entity_type", "canonical_name", "state_or_territory"])
    write_csv(out / "project_entity_membership_487.csv", memberships, ["entity_id", "entity_type", "target_id", "project_entity_id", "source_name", "state", "relation", "relation_evidence_status", "dedup_relation", "original_id_preserved"])
    write_csv(out / "project_entity_membership_487_compact.csv", [{"target_id": m["target_id"], "source_entity_id": m["entity_id"], "project_entity_id": m["project_entity_id"], "relation": m["relation"]} for m in memberships], ["target_id", "source_entity_id", "project_entity_id", "relation"])
    write_csv(out / "project_evidence_register.csv", evidence, ["evidence_id", "entity_id", "target_ids", "source_url", "source_type", "publisher", "publication_date", "accessed_date", "locator_page_or_section", "supports_condition", "support_role", "evidence_excerpt_or_summary", "review_status"])
    write_csv(out / "quality_gate_487.csv", quality, ["check_id", "count", "severity", "meaning"])
    coverage_rows = [{"state_or_territory": x.get("state", ""), "target_count": x.get("target_count", ""),
                      "source_discovery_status": x.get("source_discovery_status", ""),
                      "official_source_urls": x.get("official_source_urls", ""),
                      "tenure_evidence_rows": x.get("official_tenure_link_rows", ""),
                      "scope_limit": x.get("scope_limit", "")} for x in source_coverage]
    write_csv(out / "state_source_coverage_matrix_487.csv", coverage_rows, ["state_or_territory", "target_count", "source_discovery_status", "official_source_urls", "tenure_evidence_rows", "scope_limit"])
    summary = {"as_of_date": args.as_of_date, "status": "PASS_WITH_REVIEW_ITEMS", "target_rows": len(rows),
               "unique_target_ids": len(set(target_ids)), "project_entity_candidates": len(project_entities), "source_entity_rows": len(source_entities),
               "target_memberships": len(memberships), "evidence_url_rows": len(evidence),
               "targets_with_project_link": len(linked_ids), "targets_without_project_link": len(set(target_ids) - linked_ids),
               "dispositions": dict(dispositions), "quality_checks": quality,
               "input_sha256": {p.name: digest(p) for p in [out / "487_row_adjudication_latest_2026-10-29.csv", out / "487_inclusion_gate.csv", out / "project_candidate_evidence_review.csv"]},
               "policy": "No automatic admission/exclusion; unknown/conflicting evidence remains HOLD; entity candidate ID is deterministic from current candidate key; merge/split decisions require reviewed evidence."}
    (out / "quality_gate_487_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["status", "target_rows", "unique_target_ids", "project_entity_candidates", "target_memberships", "evidence_url_rows", "targets_with_project_link", "targets_without_project_link"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

