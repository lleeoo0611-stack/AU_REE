"""Converge 339 fixed source reviews, preserving content/access/approval distinctions.

New original reviews are sealed only after local SHA/page/content verification.
Public CI validates that record and the complete status ledger, not absent PDFs.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("p234_previous_scope", ROOT / "scripts/review_p234_144_primary_scope.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
redaction_spec = importlib.util.spec_from_file_location("p234_public_redaction", ROOT / "reproducibility/redact_release_outputs.py")
redaction = importlib.util.module_from_spec(redaction_spec)
redaction_spec.loader.exec_module(redaction)
PRIOR = "docs/audits/2026-10-31_p234_144_primary_scope_review.csv"
NINE = "docs/audits/2026-10-31_p234_144_primary_scope_remaining_access.csv"
INPUT = "inputs/source_review_20261031/p234_final_nine_adjudications.csv"
RULES = "inputs/source_review_20261031/p234_terminal_status_rules.json"
ACCESS = "inputs/source_review_20261031/p234_external_access_checks.json"
WEB = "inputs/source_review_20261031/p234_final_web_observations.json"
SEALED = base.SNAP + "final_reviewed_content_evidence.json"
MANIFESTS = [base.SNAP + name for name in (
    "final_retry_manifest.json", "final_quantum_manifest.json",
    "final_alternatives_manifest.json", "final_publisher_manifest.json", "final_pointer_manifest.json")]
PREFIX = "docs/audits/2026-10-31_p234_final_evidence"
APPROVALS = ["inputs/evidence_approvals.csv", "inputs/project_identity_decisions.csv",
             "inputs/source_review_20261031/p1_13_positive_case_gate_decisions.csv"]


def documents(root):
    docs, attempts = {}, []
    for rel in MANIFESTS:
        for doc in json.loads((root / rel).read_text(encoding="utf-8")):
            attempts.append({**doc, "manifest_path": rel})
            if "archive_path" not in doc:
                continue
            path = (root / doc["archive_path"]).resolve()
            if not path.is_relative_to((root / base.SNAP).resolve()):
                raise ValueError("Original path escapes archive")
            if path.exists() and base.sha(path.read_bytes()) != doc["sha256"]:
                raise ValueError("Original acquired-byte SHA256 mismatch")
            if doc["document_id"] in docs and docs[doc["document_id"]]["sha256"] != doc["sha256"]:
                raise ValueError("Conflicting original versions need separate review")
            docs[doc["document_id"]] = doc
    return docs, attempts


def access_checks(root, docs):
    checks = json.loads((root / ACCESS).read_text(encoding="utf-8"))
    parsed = {}
    for check in checks:
        doc = docs[check["document_id"]]
        if base.sha(check["response_utf8"].encode("utf-8")) != doc["sha256"] or check["sha256"] != doc["sha256"]:
            raise ValueError("External access response SHA differs")
        value = json.loads(check["response_utf8"])
        if value != check["parsed_response"]:
            raise ValueError("External access interpretation differs")
        parsed[check["document_id"]] = value
    if parsed["DOC-8a4e476fdf71"]["Status"] != 3:
        raise ValueError("Scaddan NXDOMAIN observation differs")
    if parsed["DOC-1e9605223a21"]["archived_snapshots"] or parsed["DOC-5961c35a3492"] or parsed["DOC-b28f5a388370"]:
        raise ValueError("Public archive search observation differs")
    return {"publisher_dns_at_retrieval": "NXDOMAIN", "exact_available_snapshot_count": 0,
            "exact_and_wildcard_cdx_results": 0,
            "limit": "Time-bounded public observations, not proof that no original copy exists elsewhere"}


def read_nine(root):
    fixed = base.unique(base.read(root / NINE))
    decisions = base.unique(base.read(root / INPUT))
    if len(fixed) != 9 or set(fixed) != set(decisions):
        raise ValueError("Immutable nine source IDs drifted")
    for tid, review in decisions.items():
        if review["source_name"] != fixed[tid]["source_name"]:
            raise ValueError("Source name differs from fixed ID")
        if review["C1_admitted"] != "NO" or review["independent_approval_signature"]:
            raise ValueError("Paused approval/signature changed")
        if not review["documentary_finding"] or not review["remaining_gap"]:
            raise ValueError("Missing scope finding or reopen condition")
    return decisions


def review_nine(root=ROOT, seal=False, require_originals=False):
    decisions = read_nine(root)
    prior = base.unique(base.read(root / PRIOR))
    docs, attempts = documents(root)
    observation = access_checks(root, docs)
    web = json.loads((root / WEB).read_text(encoding="utf-8"))
    if web["Scaddan"]["original_byte_sha256"] or web["Quantum_factsheet"]["original_byte_sha256"]:
        raise ValueError("Web-only observations cannot invent original byte SHA")
    base.SEALED = SEALED
    cache, registry, rows = {}, {}, []

    def verify(review, event_id):
        doc = docs[review["document_id"]]
        event = {**review, "target_id": event_id}
        if (seal or require_originals) and not (root / doc["archive_path"]).is_file():
            raise ValueError("Required original bytes absent: " + doc["document_id"])
        metadata, _ = base.verify_document(doc, event, root, cache)
        registry[event_id] = {"bindings": {k: event[k] for k in base.BINDINGS}, "metadata": metadata}
        return metadata

    for tid, decision in decisions.items():
        old = prior[tid]
        review = {**old, **decision}
        review["prior_document_id"] = old["document_id"]
        review["prior_documentary_disposition"] = old["terminal_documentary_disposition"]
        if decision["document_id"].startswith("DOC-"):
            review.update(verify(decision, tid))
            review["content_access_status"] = "ARCHIVED_ORIGINAL_RELEVANT_CONTENT_REVIEWED"
        else:
            if decision["document_id"] != "WEB-SCADDAN-PDF" or old["original_document_sha256"]:
                raise ValueError("Unexpected web-only original or invented byte hash")
            if decision["verification_anchor"] != web["Scaddan"]["short_anchor"] or base.pages_from_locator(decision["pdf_pages_or_html_sections"]) != web["Scaddan"]["pdf_pages_read"]:
                raise ValueError("Web original page/anchor binding differs")
            review["content_access_status"] = "WEB_CACHED_ORIGINAL_READ_NO_ORIGINAL_BYTES"
            review["content_review_method"] = "WEB_CACHED_EXTRACTED_TEXT_RECHECKED_NOT_VISUAL_BYTES_UNAVAILABLE"
        support = []
        for item in json.loads(decision["supporting_reviews_json"]):
            event_id = tid + "::SUPPORT::" + item["document_id"]
            support.append({**item, **verify(item, event_id)})
        review["supporting_content_verification_json"] = json.dumps(support, ensure_ascii=False, sort_keys=True)
        review["original_content_review_completed"] = "YES_RELEVANT_PAGES_ONLY"
        review["original_reference_scope_all_resolved"] = "NO_ALL_SOURCE_PROJECT_TITLE_JOINS_UNAPPROVED"
        review["publisher_provenance"] = "VENDOR_PROMOTIONAL_WEB_CACHE_ORIGINAL_UNAVAILABLE" if not review["original_document_sha256"] else "OFFICIAL_GOVERNMENT_ARCHIVE_OR_PUBLISHER_ORIGINAL_CONTENT"
        review["original_bytes_verified_targets_in_this_batch"] = "YES" if review["original_document_sha256"] else "NO"
        review["source_to_project_identity_approved"] = "NO"
        review["C1_and_13_case_gate_and_MCDA"] = "PAUSED_BY_USER"
        review["Project_approval"] = "UNCHANGED_HOLD"
        review["JORC_approval"] = "UNCHANGED_NOT_APPROVED"
        review["all_pages_human_fulltext_read_claimed"] = "NO_RELEVANT_PAGES_ONLY"
        review["batch_work_disposition"] = "CLASSIFIED_EXTERNAL_ORIGINAL_ACCESS_HOLD" if not review["original_document_sha256"] else "BOUNDED_PRIMARY_SCOPE_REVIEW_CLASSIFIED"
        own = [a for a in attempts if tid in a.get("target_ids", [])]
        review["new_acquisition_attempts_json"] = json.dumps([{k: a.get(k, "") for k in ("document_id", "requested_url", "status", "error", "manifest_path")} for a in own], ensure_ascii=False)
        rows.append(review)
    payload = (json.dumps(registry, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if seal:
        (root / SEALED).write_bytes(payload)
    elif require_originals and (root / SEALED).read_bytes() != payload:
        raise ValueError("Local original review differs from recorded evidence registry")
    return sorted(rows, key=lambda r: r["target_id"]), observation


def build(root=ROOT, require_originals=False):
    nine, access = review_nine(root, require_originals=require_originals)
    prior = base.unique(base.read(root / PRIOR))
    original = base.unique(base.read(root / base.PRIOR))
    replacements = base.unique(nine)
    if len(prior) != 144 or len(original) != 339 or not set(replacements).issubset(prior):
        raise ValueError("Immutable 144/339 source IDs drifted")
    if Counter(r["priority"] for r in original.values()) != {"P2": 28, "P3": 216, "P4": 95}:
        raise ValueError("Priority cohort drift")
    rules = json.loads((root / RULES).read_text(encoding="utf-8"))
    if rules["convergence_policy"]["C1_13_gate_MCDA"] != "PAUSED_BY_USER":
        raise ValueError("Paused gate policy changed")
    detail = {tid: replacements.get(tid, row) for tid, row in prior.items()}
    rows = []
    for tid, frozen in original.items():
        current = detail.get(tid)
        disposition = current["terminal_documentary_disposition"] if current else frozen["terminal_documentary_disposition"]
        if disposition not in rules["rules"]:
            raise ValueError("Unmapped documentary disposition: " + disposition)
        rule = rules["rules"][disposition]
        access_status = current.get("content_access_status", "ARCHIVED_ORIGINAL_RELEVANT_CONTENT_REVIEWED") if current else "INHERITED_P2_DESK_REVIEW_NOT_REVERIFIED_FULLTEXT" if frozen["priority"] == "P2" else "NATIVE_FEATURE_CONTENT_ONLY_NOT_TECHNICAL_DOCUMENT_REVIEW"
        finding = current["documentary_finding"] if current else frozen["existing_scoped_claim"] or frozen["REE_role_disposition"]
        gap = current["remaining_gap"] if current else frozen["remaining_gap_and_reopen_condition"]
        if not finding or not gap or frozen["Project_approval"] != "UNCHANGED_HOLD" or frozen["C1_admitted"] != "NO":
            raise ValueError("Missing evidence/gap or prior approval drift")
        rows.append({**frozen,
            "current_documentary_disposition": disposition,
            "terminal_evidence_status": rule["terminal_evidence_status"],
            "terminal_status_meaning": rule["meaning"],
            "review_work_disposition": "CLASSIFIED_WITH_EXTERNAL_ACCESS_HOLD" if access_status.startswith("WEB_") else "BOUNDED_REVIEW_CLASSIFIED_WITH_EXPLICIT_GAPS",
            "source_review_classification_complete": "YES",
            "original_technical_fulltext_complete_claimed": "NO",
            "current_content_access_status": access_status,
            "current_documentary_finding": finding,
            "current_source_document_entity_relation": current["source_document_entity_relation"] if current else frozen["source_to_project_relation"],
            "current_REE_resource_basis": current["REE_resource_basis"] if current else frozen["REE_role_disposition"],
            "current_document_id": current["document_id"] if current else "",
            "current_original_byte_sha256": current["original_document_sha256"] if current else "",
            "current_original_archive_path": current["original_archive_path"] if current else "",
            "current_original_url": current["actual_original_url"] if current else "",
            "current_pages_or_sections": current["pdf_pages_or_html_sections"] if current else "",
            "current_document_vintage": current["document_date_or_vintage"] if current else "INHERITED_RECORD_SEE_DOCUMENTARY_HISTORY",
            "current_documented_tenure": current["documented_tenure"] if current else frozen["reported_tenements"],
            "nominated_pointer_access_status": replacements[tid]["nominated_pointer_access_status"] if tid in replacements else "NOT_IN_NINE_RETRIEVAL_BATCH_SEE_HISTORY",
            "current_remaining_gap_and_reopen_condition": gap,
            "next_action": "PAUSED_GATES_OR_REOPEN_ONLY_ON_NEW_VERIFIABLE_EVIDENCE",
            "independent_approval_signature": "", "C1_13_gate_MCDA": "PAUSED_BY_USER",
            "approval_sufficiency_changed": "NO"})
    redacted_ids = []
    for i, row in enumerate(rows):
        public_row = redaction.clean(row)
        changed = public_row != row
        if changed:
            redacted_ids.append(row["target_id"])
        public_row["public_release_redaction"] = "CREDENTIAL_QUERY_REMOVED_DERIVED_ROW_ONLY_ORIGINAL_INPUT_UNCHANGED" if changed else "NOT_NEEDED"
        rows[i] = public_row
    rows.sort(key=lambda r: r["target_id"])
    paths = [base.PRIOR, PRIOR, NINE, INPUT, RULES, ACCESS, WEB, SEALED, *MANIFESTS, *APPROVALS]
    summary = {"execution_id": "P234-FINAL-EVIDENCE-20261031-V1",
        "base_commit": "8c79f2e74172bf48d75e2fc9c2872c35892aca9e", "branch": "audit/p234-final-evidence-status",
        "source_snapshot": "2026-10-29", "new_document_retrieval_date": "2026-10-31",
        "source_targets_classified": len(rows), "priority_counts": dict(Counter(r["priority"] for r in rows)),
        "P2_provisional_case_count": len({r["case_id"] for r in rows if r["priority"] == "P2"}),
        "terminal_evidence_status_counts": dict(sorted(Counter(r["terminal_evidence_status"] for r in rows).items())),
        "content_access_status_counts": dict(sorted(Counter(r["current_content_access_status"] for r in rows).items())),
        "new_batch_target_count": len(nine),
        "new_batch_archived_original_content_targets": sum(bool(r["original_document_sha256"]) for r in nine),
        "new_batch_nominated_original_targets_archived": sum(r["nominated_pointer_access_status"] == "NOMINATED_ORIGINAL_BYTES_ARCHIVED" for r in nine),
        "new_batch_replacement_primary_targets_original_pointer_unarchived": sum(r["nominated_pointer_access_status"].startswith("REPLACEMENT_") for r in nine),
        "new_batch_web_only_targets_original_bytes_unavailable": sum(not r["original_document_sha256"] for r in nine),
        "new_batch_distinct_original_documents": len({r["document_id"] for r in nine if r["original_document_sha256"]}),
        "all_144_archived_original_content_targets": sum(bool(r["original_document_sha256"]) for r in detail.values()),
        "all_144_web_only_original_content_targets": sum(not r["original_document_sha256"] for r in detail.values()),
        "new_original_scope_dispositions": dict(Counter(r["terminal_documentary_disposition"] for r in nine)),
        "Scaddan_external_access_checks": access,
        "public_redaction_target_ids": sorted(redacted_ids),
        "public_redaction_policy": "Reuse repository release redaction on new derived rows only; preserve historical inputs and their original hashes",
        "formal_approvals_changed": 0, "all_technical_originals_complete": False,
        "convergence": "All 339 sources classified against explicit evidence states; source-only, inherited desk, original content and external-access holds remain distinct. Classification closes this bounded work phase, not eligibility or every evidence gap.",
        "public_CI_limit": "Recorded content bindings and ledger reproduced; restricted original bytes remain local. --verify-originals requires new reviewed DOC originals and checks their cited pages.",
        "input_sha256": {p: base.sha((root / p).read_bytes()) for p in paths}}
    return rows, nine, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--seal-evidence", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--verify-originals", action="store_true")
    args = parser.parse_args()
    if args.seal_evidence:
        nine, _ = review_nine(seal=True)
        print("Recorded local original evidence for", sum(bool(r["original_document_sha256"]) for r in nine), "targets; Scaddan stays web-only")
        return
    rows, nine, summary = build(require_originals=args.verify_originals)
    def encoded(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    outputs = {PREFIX + "_339.csv": base.csv_bytes(rows), PREFIX + "_339.json": encoded(rows),
               PREFIX + "_nine.csv": base.csv_bytes(nine), PREFIX + "_nine.json": encoded(nine),
               PREFIX + "_physical_access_residual.csv": base.csv_bytes([r for r in nine if r["nominated_pointer_access_status"] != "NOMINATED_ORIGINAL_BYTES_ARCHIVED"]),
               PREFIX + "_summary.json": encoded(summary)}
    for rel, payload in outputs.items():
        path = ROOT / rel
        if args.write:
            path.write_bytes(payload)
        elif path.read_bytes() != payload:
            raise ValueError("Final evidence export differs: " + rel)
    print(json.dumps({k: summary[k] for k in ("source_targets_classified", "new_batch_archived_original_content_targets", "new_batch_web_only_targets_original_bytes_unavailable", "formal_approvals_changed")}))


if __name__ == "__main__":
    main()
