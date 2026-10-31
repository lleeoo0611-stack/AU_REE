#!/usr/bin/env python3
"""Deterministic source-level triage; never modifies frozen source or approvals.

Inputs: 2026-10-29 immutable 339 source audit, B04 overlay, manual B05 public
source reviews. Outputs: all-339 triage, 100 native workgroups, 112 work units,
and a numerical summary. No data downloads, independent C1 signing or closure.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "docs/audits/2026-10-31_p234_final_evidence_339.csv"
B04 = ROOT / "docs/audits/2026-10-31_p234_all_339_continuation_b04.csv"
B05 = ROOT / "inputs/source_review_20261031/p234_b05_primary_scope_reviews.csv"
LOC = ROOT / "inputs/source_review_20261031/p234_b05_locator_followups.csv"
TRIAGE = ROOT / "docs/audits/2026-10-31_p234_b05_source_triage_339.csv"
GROUPS = ROOT / "docs/audits/2026-10-31_p34_b05_native_workgroups_100.csv"
QUEUE = ROOT / "docs/audits/2026-10-31_p234_b05_priority_work_queue_112.csv"
SUMMARY = ROOT / "docs/audits/2026-10-31_p234_b05_triage_summary.json"

TERMINAL_TO_IDENTITY = {
    "DOCUMENTED_REE_CLAIM_SCOPE_HOLD": "CLAIMED_PROJECT_OR_REE_SCOPE_AWAITING_INDEPENDENT_ID",
    "DOCUMENTED_GEO_CONTEXT_SCOPE_HOLD": "DOCUMENTED_GEOLOGICAL_CONTEXT_PROJECT_NOT_ESTABLISHED",
    "DOCUMENTED_NON_TARGET_OR_HISTORIC_SCOPE": "DOCUMENTED_HISTORIC_OR_NON_TARGET_CONTEXT",
    "DOCUMENTED_SCOPE_TRANSFER_REJECTED": "WRONG_PROJECT_SCOPE_TRANSFER_NOT_PERMITTED",
    "NATIVE_ONLY_PROJECT_REE_UNRESOLVED": "NATIVE_LOCALITY_PROJECT_ID_UNRESOLVED",
    "NAME_OR_GEOGRAPHY_UNRESOLVED": "NAME_OR_GEOGRAPHY_CONFLICT_REQUIRES_ORIGINAL",
    "TESTED_TARGET_NEGATIVE_ONLY": "TESTED_TARGET_SPECIFIC_RESULT_ONLY",
    "WEB_ONLY_ORIGINAL_ACCESS_HOLD": "ORIGINAL_ACCESS_BLOCKED_SCOPE_PENDING",
}
CLOSURE_ELIGIBLE_TERMINAL = {
    "DOCUMENTED_GEO_CONTEXT_SCOPE_HOLD",
    "DOCUMENTED_NON_TARGET_OR_HISTORIC_SCOPE",
    "DOCUMENTED_SCOPE_TRANSFER_REJECTED",
    "TESTED_TARGET_NEGATIVE_ONLY",
}
NATIVE_STATUSES = {"BASELINE_NATIVE_FEATURE_ONLY", "B04_LOCATOR_ATTEMPT_ONLY_NOT_REVIEW"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    x = math.sin((lat2 - lat1) / 2) ** 2
    x += math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 12742 * math.asin(min(1, math.sqrt(x)))


def generate() -> tuple[list[dict], list[dict], list[dict], dict]:
    old, prior, reviews, locators = map(read_csv, (OLD, B04, B05, LOC))
    require(len(old) == len(prior) == 339, "339 baseline drift")
    require(len(reviews) == 4 and len(locators) == 2, "B05 review count drift")
    old_by = {x["target_id"]: x for x in old}
    prior_by = {x["target_id"]: x for x in prior}
    rev_by = {x["target_id"]: x for x in reviews}
    require(len(old_by) == len(prior_by) == 339 and set(old_by) == set(prior_by), "missing or duplicate source ID")
    require(len(rev_by) == 4, "duplicate B05 review")
    require(len({x["target_id"] for x in locators}) == 2, "duplicate locator")
    for r in reviews:
        prior_row = prior_by[r["target_id"]]
        require(prior_row["priority"] == "P2" and prior_row["continuation_status"] == "BASELINE_P2_DESK_REVIEW_ONLY",
                "B05 changed already verified source " + r["target_id"])
        require(r["source_name"] == prior_row["source_name"] and r["source_snapshot"] == "2026-10-29", "review identity drift")
        require(r["original_document_bytes_archived"] == "NO" and r["original_document_sha256"] == "", "invented original bytes")
        require(r["pdf_visual_verified"] == r["full_technical_report_verified"] == "NO", "false full technical claim")
        require(r["C1_admitted"] == r["independent_reviewer_signed"] == "NO", "unapproved signature")
        require(r["precise_locator"] and r["technical_finding"] and r["primary_source_url"].startswith("https://"),
                "missing primary source locator")
    for x in locators:
        require(x["target_id"] in old_by and old_by[x["target_id"]]["priority"] == "P4", "locator not in P4")
        require(x["native_record_point_to_report_footprint_verified"] == "NO", "unapproved source-to-project mapping")
        require(x["new_source_original_fulltext_verified"] == x["C1_admitted"] == "NO", "false locator promotion")
    triage = []
    for r in prior:
        raw = old_by[r["target_id"]]
        fresh = rev_by.get(r["target_id"])
        require(r["source_snapshot"] == raw["frozen_snapshot"] == "2026-10-29", "snapshot drift")
        require(r["priority"] == raw["priority"] and r["source_native_id"] == raw["source_native_id"],
                "native metadata drift")
        require(r["C1_admitted"] == "NO", "unexpected C1 baseline approval")
        status = "B05_DIRECT_PUBLIC_SOURCE_SCOPE_REVIEW" if fresh else r["continuation_status"]
        if status == "BASELINE_ARCHIVED_RELEVANT_CONTENT":
            source_status = "ARCHIVED_RELEVANT_PAGES"
        elif status == "BASELINE_WEB_CACHED_ONLY":
            source_status = "WEB_CACHED_TEXT_ONLY"
        elif status == "BASELINE_P2_DESK_REVIEW_ONLY":
            source_status = "INHERITED_DESK_NO_NEW_ORIGINAL"
        elif status in NATIVE_STATUSES:
            source_status = "NATIVE_FEATURE_ONLY"
        else:
            source_status = "PUBLIC_PRIMARY_TEXT_SCOPE_ONLY"
        candidate = r["continuation_status"] == "BASELINE_ARCHIVED_RELEVANT_CONTENT" and (
            r["baseline_terminal_evidence_status"] in CLOSURE_ELIGIBLE_TERMINAL)
        if candidate:
            freeze = "SOURCE_SCOPE_CLOSURE_HUMAN_REVIEW_CANDIDATE"
        elif source_status == "NATIVE_FEATURE_ONLY":
            freeze = "C0_NATIVE_ONLY_LIMITED_CLOSURE_POLICY_PENDING"
        elif r["baseline_terminal_evidence_status"] == "WEB_ONLY_ORIGINAL_ACCESS_HOLD":
            freeze = "DOCUMENT_ACCESS_HOLD_REOPEN_ON_NEW_URL"
        elif r["baseline_terminal_evidence_status"] == "NAME_OR_GEOGRAPHY_UNRESOLVED":
            freeze = "IDENTITY_CONFLICT_HOLD"
        elif r["baseline_terminal_evidence_status"] == "DOCUMENTED_REE_CLAIM_SCOPE_HOLD":
            freeze = "ACTIVE_REE_CLAIM_GATE_EVIDENCE"
        else:
            freeze = "CONTINUE_BOUNDARY_ORIGINAL_EVIDENCE_REVIEW"
        shared_key = r["state"] + "|" + r["source_native_id"] if (
            r["priority"] != "P2" and source_status == "NATIVE_FEATURE_ONLY") else ""
        triage.append({
            "target_id": r["target_id"], "priority": r["priority"], "source_name": r["source_name"],
            "state": r["state"], "source_key": r["source_key"], "source_native_id": r["source_native_id"],
            "source_snapshot": "2026-10-29", "baseline_terminal_evidence_status": r["baseline_terminal_evidence_status"],
            "source_review_status": source_status,
            "project_identity_status": TERMINAL_TO_IDENTITY.get(r["baseline_terminal_evidence_status"], "MANUAL_REVIEW_REQUIRED"),
            "C1_eligibility_status": "NOT_ADMITTED_SIX_GATES_UNAPPROVED",
            "evidence_review_ref": fresh["review_id"] if fresh else r["continuation_review_id"],
            "primary_evidence_url": fresh["primary_source_url"] if fresh else r["new_official_source_url"],
            "source_scope_summary": fresh["technical_finding"] if fresh else r["source_scoped_finding_overlay"],
            "technical_original_fulltext_verified": "NO", "original_document_newly_archived": "NO",
            "source_native_shared_work_key": shared_key, "proposed_freeze_route": freeze,
            "source_scope_human_signed": "NO",
            "proposed_review_action": fresh["outstanding_gate_evidence"] if fresh else r["source_constrained_next_action"],
            "source_lifecycle": "C0_SOURCE_RECORD_RETAINED",
        })
    by_key = defaultdict(list)
    for row in triage:
        if row["source_native_shared_work_key"]:
            by_key[row["source_native_shared_work_key"]].append(row)
    groups = []
    for i, key in enumerate(sorted(by_key), 1):
        rows = by_key[key]
        originals = [old_by[r["target_id"]] for r in rows]
        coords = [(float(r["source_point_latitude"]), float(r["source_point_longitude"])) for r in originals]
        max_km = max((distance_km(a, b) for j, a in enumerate(coords) for b in coords[j + 1:]), default=0.)
        name_conflict = len({r["source_name"].strip().lower() for r in rows}) > 1
        groups.append({
            "work_group_id": f"P34WG-{i:04d}", "stable_join_key": key,
            "state": rows[0]["state"], "source_native_id": rows[0]["source_native_id"],
            "source_target_ids": "|".join(sorted(r["target_id"] for r in rows)),
            "member_source_count": str(len(rows)), "P3_count": str(sum(r["priority"] == "P3" for r in rows)),
            "P4_count": str(sum(r["priority"] == "P4" for r in rows)),
            "source_names": "|".join(sorted({r["source_name"] for r in rows})),
            "source_keys": "|".join(sorted({r["source_key"] for r in rows})),
            "original_feature_entity_types": "|".join(sorted({r["baseline_entity_type"] for r in originals})),
            "max_pairwise_point_km": f"{max_km:.5f}",
            "name_disagreement": "YES" if name_conflict else "NO",
            "coordinate_over_1km": "YES" if max_km > 1 else "NO",
            "same_native_id_is_approved_project_merge": "NO", "original_fulltext_cleared": "NO",
            "current_work_unit": "EXACT_NATIVE_ID_PRIMARY_DOCUMENT_AND_PROJECT_PARENT_SEARCH",
            "human_source_scope_freeze": "NO",
        })
    pending_p2 = [r for r in triage if r["priority"] == "P2" and
                  r["source_review_status"] == "INHERITED_DESK_NO_NEW_ORIGINAL"]
    queue = [{
        "work_unit_id": f"P2WG-{i:04d}", "unit_type": "P2_INDIVIDUAL_SOURCE", "priority": "P2",
        "source_target_ids": r["target_id"], "source_row_count": "1",
        "source_name": r["source_name"], "stable_native_locator": r["source_native_id"],
        "action": "FETCH_OFFICIAL_REPORT_BY_ID_AND_RECONCILE_PROJECT_ID_REO_MRE",
        "source_lifecycle": "C0", "closure_decision": "NOT_APPROVED", "source_boundary_status": "CURRENT_DESK_ONLY",
    } for i, r in enumerate(pending_p2, 1)]
    queue += [{
        "work_unit_id": r["work_group_id"], "unit_type": "P34_SHARED_NATIVE_LOCATOR",
        "priority": "P3" if int(r["P3_count"]) else "P4", "source_target_ids": r["source_target_ids"],
        "source_row_count": r["member_source_count"], "source_name": r["source_names"],
        "stable_native_locator": r["stable_join_key"], "action": r["current_work_unit"],
        "source_lifecycle": "C0", "closure_decision": "NOT_APPROVED", "source_boundary_status": "ORIGINAL_NATIVE_ONLY",
    } for r in groups]
    kinds = Counter(r["source_review_status"] for r in triage)
    candidates = [r for r in triage if r["proposed_freeze_route"] == "SOURCE_SCOPE_CLOSURE_HUMAN_REVIEW_CANDIDATE"]
    summary = {
        "execution_id": "P234-B05-NATIVE-WORKGROUP-TRIAGE-20261031",
        "source_snapshot": "2026-10-29", "evidence_review_date": "2026-10-31",
        "baseline_source_targets": 339, "priority_counts": {"P2": 28, "P3": 216, "P4": 95},
        "new_P2_official_source_reviews": len(reviews),
        "P2_prior_direct_source_scope_reviews": 12,
        "P2_current_public_source_scope_reviews": sum(
            r["priority"] == "P2" and r["source_review_status"] == "PUBLIC_PRIMARY_TEXT_SCOPE_ONLY" for r in triage),
        "P2_remaining_desk_only": len(pending_p2),
        "P3_pending_native_only": sum(r["priority"] == "P3" and r["source_review_status"] == "NATIVE_FEATURE_ONLY" for r in triage),
        "P4_pending_native_only": sum(r["priority"] == "P4" and r["source_review_status"] == "NATIVE_FEATURE_ONLY" for r in triage),
        "P34_pending_source_rows": sum(int(r["member_source_count"]) for r in groups),
        "P34_pending_native_work_groups": len(groups),
        "P34_shared_native_id_groups": sum(int(r["member_source_count"]) > 1 for r in groups),
        "P34_groups_with_native_name_conflict": sum(r["name_disagreement"] == "YES" for r in groups),
        "P34_groups_over_1km": sum(r["coordinate_over_1km"] == "YES" for r in groups),
        "P34_shared_across_source_keys": sum("|" in r["source_keys"] for r in groups),
        "all_priority_pending_source_rows": len(pending_p2) + sum(int(r["member_source_count"]) for r in groups),
        "all_priority_work_units": len(queue),
        "source_review_levels": dict(sorted(kinds.items())),
        "proposed_source_scope_closure_candidates": len(candidates),
        "proposed_closure_by_priority": {p: sum(r["priority"] == p for r in candidates) for p in ("P2", "P3", "P4")},
        "formally_frozen_source_rows": 0,
        "new_original_pdf_bytes_archived": 0, "new_independent_C1_approvals": 0,
        "policy_status": "FREEZE_RULES_PROPOSED_FOR_USER_DECISION_NOT_APPLIED",
    }
    require(Counter(r["priority"] for r in triage) == {"P2": 28, "P3": 216, "P4": 95},
            "339 cohort priority mismatch")
    require(len(groups) == 100 and len(pending_p2) == 12 and len(queue) == 112, "work unit drift")
    require(summary["P34_pending_source_rows"] == 151 and summary["P34_shared_native_id_groups"] == 51,
            "native shared-ID split drift")
    require(summary["P34_groups_with_native_name_conflict"] == 0 and summary["P34_groups_over_1km"] == 0,
            "source name/geo conflict needs manual review")
    require(summary["P34_shared_across_source_keys"] == 30, "cross-system join count drift")
    require(summary["proposed_source_scope_closure_candidates"] == 119, "closure proposal count drift")
    require(kinds == {
        "ARCHIVED_RELEVANT_PAGES": 143, "PUBLIC_PRIMARY_TEXT_SCOPE_ONLY": 32,
        "WEB_CACHED_TEXT_ONLY": 1, "INHERITED_DESK_NO_NEW_ORIGINAL": 12,
        "NATIVE_FEATURE_ONLY": 151
    }, "source review level drift")
    require(all(r["C1_eligibility_status"] == "NOT_ADMITTED_SIX_GATES_UNAPPROVED"
                and r["source_scope_human_signed"] == "NO" for r in triage), "unapproved admission")
    return triage, groups, queue, summary


def csv_content(rows: list[dict]) -> str:
    require(bool(rows), "cannot write empty audit")
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n", quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group(required=True)
    options.add_argument("--check", action="store_true", help="Validate existing generated outputs")
    options.add_argument("--write", action="store_true", help="Regenerate only derived B05 CSV/JSON")
    args = parser.parse_args()
    triage, groups, queue, summary = generate()
    targets = {
        TRIAGE: csv_content(triage), GROUPS: csv_content(groups), QUEUE: csv_content(queue),
        SUMMARY: json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    }
    for path, content in targets.items():
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        elif path == SUMMARY:
            require(json.loads(path.read_text(encoding="utf-8")) == summary,
                    "summary mismatch: " + str(path))
        else:
            actual = read_csv(path)
            expected = list(csv.DictReader(io.StringIO(content)))
            require(actual == expected, "derived CSV mismatch: " + str(path))
    print("PASS B05: 339 source IDs, P2 16 text/12 desk, P3 87 and P4 64 native; "
          "151 -> 100 workgroups (51 shared IDs); 119 unsigned closure candidates; 0 C1.")


if __name__ == "__main__":
    main()
