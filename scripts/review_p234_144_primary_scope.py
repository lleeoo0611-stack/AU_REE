"""Reproduce substantive original-document scope findings for 144 fixed IDs.

Requires pypdf only for original PDF inspection. Reads acquisition manifests,
checks original bytes, resolves only curated target-ID findings, and validates
relevant PDF page / HTML anchors. Never admits Projects, C1 or resource claims.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
FROZEN = "docs/audits/2026-10-31_p2_p3_p4_closeout_document_pointer_holds.csv"
PRIOR = "docs/audits/2026-10-31_p2_p3_p4_closeout.csv"
INPUT = "inputs/source_review_20261031/p234_144_primary_scope_adjudications.csv"
SNAP = "data/document_snapshots/2026-10-31_p234_primary/"
MANIFESTS = [SNAP + name for name in (
    "acquisition_manifest.json", "gemis_originals_manifest.json",
    "supplement_acquisition_manifest.json", "supplement2_acquisition_manifest.json",
    "supplement3_acquisition_manifest.json", "supplement4_acquisition_manifest.json",
    "supplement5_acquisition_manifest.json", "supplement6_acquisition_manifest.json",
    "supplement7_acquisition_manifest.json")]
SEALED = SNAP + "reviewed_content_evidence.json"
WEB = "inputs/source_review_20261031/p234_web_original_review.json"
BINDINGS = ("document_id", "pdf_pages_or_html_sections", "verification_anchor", "expected_government_record_id", "table_context")
PREFIX = "docs/audits/2026-10-31_p234_144_primary_scope"


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def unique(rows):
    out = {}
    for row in rows:
        if not row["target_id"] or row["target_id"] in out:
            raise ValueError("Duplicate/empty immutable target ID")
        out[row["target_id"]] = row
    return out


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip += 1
        if tag in {"p", "div", "br", "tr"}:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def normal(text):
    return " ".join(text.split())


def pages_from_locator(locator):
    # Parenthetical visual-review notes are not page-number ranges.
    head = locator.split("(")[0].strip()
    pages = []
    for token in head.split(","):
        token = token.strip()
        if re.fullmatch(r"\d+-\d+", token):
            a, b = map(int, token.split("-"))
            pages.extend(range(a, b + 1))
        elif token.isdigit():
            pages.append(int(token))
        else:
            raise ValueError("Invalid PDF page locator: " + locator)
    if not pages or min(pages) < 1:
        raise ValueError("Invalid PDF page numbers")
    return sorted(set(pages))


def verify_document(doc, review, root=ROOT, cache=None):
    path = (root / doc["archive_path"]).resolve()
    if not path.is_relative_to((root / SNAP).resolve()):
        raise ValueError("Document path escapes archive")
    if not path.exists():
        records = json.loads((root / SEALED).read_text(encoding="utf-8"))
        record = records.get(review["target_id"])
        if not record or any(record["bindings"][k] != review[k] for k in BINDINGS):
            raise ValueError("Sealed evidence binding differs: page exceeds/anchor absent/Wrong government/Table row; original required")
        metadata = record["metadata"]
        if metadata["original_document_sha256"] != doc["sha256"] or metadata["original_archive_path"] != doc["archive_path"]:
            raise ValueError("Original document SHA256/archive differs from sealed evidence")
        return metadata, ""
    cache = {} if cache is None else cache
    bytes_key = ("bytes", doc["sha256"])
    if bytes_key not in cache:
        payload = path.read_bytes()
        if sha(payload) != doc["sha256"]:
            raise ValueError("Original document SHA256 mismatch")
        cache[bytes_key] = payload
    payload = cache[bytes_key]
    key = (doc["sha256"], review["pdf_pages_or_html_sections"])
    if key not in cache:
        if doc["format"] == "pdf":
            from pypdf import PdfReader
            if not payload.startswith(b"%PDF-"):
                raise ValueError("Non-PDF bytes cannot verify PDF")
            reader_key = ("pdf_reader", doc["sha256"])
            if reader_key not in cache:
                cache[reader_key] = PdfReader(io.BytesIO(payload))
            reader = cache[reader_key]
            numbers = pages_from_locator(review["pdf_pages_or_html_sections"])
            if max(numbers) > len(reader.pages):
                raise ValueError("PDF page locator exceeds original")
            text = "\n".join(reader.pages[n-1].extract_text() or "" for n in numbers)
            cache[key] = normal(text), len(reader.pages), numbers
        elif doc["format"] == "html":
            parser = Text()
            parser.feed(payload.decode("utf-8", errors="replace"))
            cache[key] = normal(" ".join(parser.parts)), 0, []
        else:
            raise ValueError("Unknown document content format")
    text, total, inspected = cache[key]
    if review["document_id"] == "DOC-3713d1609084":
        if "visually inspected scan" not in review["pdf_pages_or_html_sections"]:
            raise ValueError("Scanned Benmara report requires explicit visual method")
        method = "ORIGINAL_SCANNED_RELEVANT_PAGES_VISUALLY_READ_NO_OCR"
    else:
        if len(text) < 100 or review["verification_anchor"].casefold() not in text.casefold():
            raise ValueError("Target/scope anchor absent from relevant original pages: " + review["target_id"] + " / " + review["verification_anchor"])
        method = "ORIGINAL_RELEVANT_PAGES_OR_HTML_CONTENT_READ"
    if review["table_context"] and normal(review["table_context"]) not in text:
        raise ValueError("Table row/coordinates absent from cited original pages")
    number = review["expected_government_record_id"]
    if number and not re.search(r"Deposit Number:\s*" + re.escape(number) + r"\b", text):
        raise ValueError("Wrong government deposit ID in original HTML")
    coords = re.search(r"Long Degrees Decimal\s+([\d.]+)\s+Lat Degrees Decimal\s+(-[\d.]+)", text)
    return {"reviewed_government_longitude": coords.group(1) if coords else "",
            "reviewed_government_latitude": coords.group(2) if coords else "",
            "original_document_sha256": doc["sha256"], "original_archive_path": doc["archive_path"],
            "actual_original_url": doc.get("final_url", doc["requested_url"]),
            "original_format": doc["format"], "original_total_pdf_pages": str(total),
            "content_review_method": method, "inspected_pdf_pages": json.dumps(inspected),
            "reviewed_page_text_sha256": sha(text.encode("utf-8"))}, text


def distance(lat1, lon1, lat2, lon2):
    a, b = math.radians(lat1), math.radians(lat2)
    dlat, dlon = b-a, math.radians(lon2-lon1)
    value = math.sin(dlat/2)**2 + math.cos(a)*math.cos(b)*math.sin(dlon/2)**2
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(value)))


def build(root=ROOT):
    frozen, prior, decisions = unique(read(root / FROZEN)), unique(read(root / PRIOR)), unique(read(root / INPUT))
    if len(frozen) != 144 or len(prior) != 339 or set(decisions) != set(frozen):
        raise ValueError("Frozen 144 target IDs drifted")
    if Counter(r["priority"] for r in frozen.values()) != {"P3": 118, "P4": 26}:
        raise ValueError("Frozen source priorities drifted")
    attempts, docs = [], {}
    for rel in MANIFESTS:
        records = json.loads((root / rel).read_text(encoding="utf-8"))
        for d in records:
            attempts.append({**d, "manifest_path": rel})
            if "archive_path" in d:
                original = (root / d["archive_path"]).resolve()
                if not original.is_relative_to((root / SNAP).resolve()):
                    raise ValueError("Original archive path escapes snapshot")
                if original.exists() and sha(original.read_bytes()) != d["sha256"]:
                    raise ValueError("Acquired original SHA mismatch")
                docs[d["document_id"]] = d
    web = json.loads((root / WEB).read_text(encoding="utf-8"))
    cache, rows = {}, []
    for tid, old in frozen.items():
        d = decisions[tid]
        if d["source_name"] != old["source_name"] or d["independent_approval_signature"] or d["C1_admitted"] != "NO":
            raise ValueError("Source identity or paused approval drift")
        if old["source_key"].startswith("SA_") and d["expected_government_record_id"] != old["source_native_id"]:
            raise ValueError("Curated government ID differs from frozen native ID")
        if not d["documentary_finding"] or not d["remaining_gap"]:
            raise ValueError("Missing substantive scope finding/reopen condition")
        doc_id = d["document_id"]
        metadata = {"original_document_sha256": "", "original_archive_path": "", "actual_original_url": "",
                    "original_format": "", "original_total_pdf_pages": "0", "content_review_method": "NO_ORIGINAL_CONTENT_REVIEW_ACCESS_BLOCKED",
                    "inspected_pdf_pages": "[]", "reviewed_page_text_sha256": "",
                    "reviewed_government_longitude": "", "reviewed_government_latitude": ""}
        text = ""
        if doc_id.startswith("WEB-"):
            w = web[doc_id]
            if d["verification_anchor"] != w["short_verification_anchor"] or pages_from_locator(d["pdf_pages_or_html_sections"]) != w["relevant_pages_read"]:
                raise ValueError("Web original page/anchor binding differs")
            metadata.update(actual_original_url=w["source_url"], original_format="web_rendered_pdf_no_original_bytes",
                            original_total_pdf_pages=str(w["total_pdf_pages"]), inspected_pdf_pages=json.dumps(w["relevant_pages_read"]),
                            content_review_method="WEB_RENDERED_RELEVANT_ORIGINAL_PAGES_READ_BYTES_NOT_ARCHIVED")
        elif doc_id:
            if doc_id not in docs:
                raise ValueError("Original document not archived")
            metadata, text = verify_document(docs[doc_id], d, root, cache)
        elif d["terminal_documentary_disposition"] != "HOLD_ORIGINAL_DOCUMENT_ACCESS_UNRESOLVED":
            raise ValueError("A content conclusion without an original is forbidden")
        lat, lon, delta = "", "", ""
        # Geometry diagnostics are comparisons only; NEVER approve identity by distance.
        if d["table_context"]:
            m = re.search(r"\b(1\d\d\.\d+)\s+(-\d+\.\d+)", d["table_context"])
            if m:
                lon, lat = m.groups()
        elif d["expected_government_record_id"]:
            lon, lat = metadata["reviewed_government_longitude"], metadata["reviewed_government_latitude"]
        if lat and old["source_point_latitude"] and old["source_point_longitude"]:
            delta = f'{distance(float(old["source_point_latitude"]), float(old["source_point_longitude"]), float(lat), float(lon)):.3f}'
        own_attempts = [a for a in attempts if tid in a.get("target_ids", [])]
        rows.append({**d, "priority": old["priority"], "source_key": old["source_key"],
                     "source_native_id": old["source_native_id"], "frozen_source_snapshot": "2026-10-29",
                     "baseline_144_disposition": old["terminal_documentary_disposition"], **metadata,
                     "original_content_review_completed": "YES" if doc_id else "NO_ACCESS_BLOCKED",
                     "original_reference_scope_all_resolved": "NO" if "STILL_UNARCHIVED" in d["terminal_documentary_disposition"] or not doc_id or doc_id.startswith("WEB-") else "BOUNDED_REVIEW_ONLY_SEE_FINDING",
                     "publisher_provenance": "VENDOR_PROMOTIONAL_WEB_COPY_BYTES_AND_AUTHENTICITY_PENDING" if doc_id.startswith("WEB-") else "ISSUER_AUTHORED_COPY_ON_OTHER_HOST_AUTHENTICITY_PENDING" if doc_id in {"DOC-f3819ad0cec9", "DOC-95e76720858d", "DOC-b9e998408caa"} else "ISSUER_DISTRIBUTION_HOST_NOT_INDEPENDENT_AUTHENTICITY_SIGNOFF" if doc_id == "DOC-ceb59bb3a197" else "GOVERNMENT_OR_ISSUER_PUBLISHER_CONTENT" if doc_id else "NO_ORIGINAL_RETRIEVED",
                     "document_point_latitude": lat, "document_point_longitude": lon,
                     "frozen_to_document_point_distance_km": delta,
                     "coordinate_comparison_limit": "DOCUMENT_POINT_COMPARISON_ONLY_DATUM_VINTAGE_ACCURACY_AND_PROJECT_FOOTPRINT_NOT_APPROVED",
                     "Project_approval": "UNCHANGED_HOLD", "JORC_approval": "UNCHANGED_NOT_APPROVED",
                     "C1_and_13_case_gate_and_MCDA": "PAUSED_BY_USER",
                     "all_pages_human_fulltext_read_claimed": "NO_RELEVANT_PAGES_ONLY",
                     "acquisition_attempt_ids_json": json.dumps([a.get("document_id", a["requested_url"]) for a in own_attempts]),
                     "unresolved_access_errors_json": json.dumps([{"url": a["requested_url"], "error": a.get("error", "")} for a in own_attempts if "archive_path" not in a], ensure_ascii=False)})
    rows.sort(key=lambda r: r["target_id"])
    updated = []
    indexed = {r["target_id"]: r for r in rows}
    for tid, old in prior.items():
        new = indexed.get(tid)
        updated.append({"target_id": tid, "priority": old["priority"], "source_name": old["source_name"],
                        "prior_disposition": old["terminal_documentary_disposition"],
                        "current_disposition": new["terminal_documentary_disposition"] if new else old["terminal_documentary_disposition"],
                        "new_original_content_review": new["original_content_review_completed"] if new else "NOT_IN_144_BATCH",
                        "new_original_document_sha256": new["original_document_sha256"] if new else "",
                        "new_documentary_finding": new["documentary_finding"] if new else "",
                        "C1_admitted": "NO"})
    paths = [FROZEN, PRIOR, INPUT, WEB, SEALED, *MANIFESTS]
    summary = {"execution_id": "P234-144-PRIMARY-SCOPE-20261031-V1", "base_commit": "f327a4e5ab31d1e206642921f1cdacc2a4df8e59",
               "branch": "audit/p234-144-primary-scope", "frozen_source_snapshot": "2026-10-29",
               "document_retrieval_snapshot": "2026-10-31_p234_primary",
               "source_target_count": len(rows), "source_priority_counts": dict(Counter(r["priority"] for r in rows)),
               "original_content_reviewed_targets": sum(r["original_content_review_completed"] == "YES" for r in rows),
               "no_original_content_access_blocked_targets": sum(not r["document_id"] for r in rows),
               "alternative_originals_with_nominated_pointer_still_unarchived": sum("STILL_UNARCHIVED" in r["terminal_documentary_disposition"] for r in rows),
               "original_bytes_reviewed_targets": sum(bool(r["original_document_sha256"]) for r in rows),
               "web_only_original_content_targets": sum(r["document_id"].startswith("WEB-") for r in rows),
               "distinct_reviewed_documents": len({r["document_id"] for r in rows if r["document_id"]}),
               "reviewed_source_format_counts": dict(Counter(r["original_format"] or "NO_ORIGINAL" for r in rows)),
               "other_host_issuer_authored_copy_targets": sum(r["publisher_provenance"] == "ISSUER_AUTHORED_COPY_ON_OTHER_HOST_AUTHENTICITY_PENDING" for r in rows),
               "dispositions": dict(sorted(Counter(r["terminal_documentary_disposition"] for r in rows).items())),
               "coordinate_comparisons": sum(bool(r["frozen_to_document_point_distance_km"]) for r in rows),
               "updated_source_ledger_count": len(updated), "formal_approvals_changed": 0,
               "all_technical_originals_complete": False,
               "public_reproduction_limit": "CI validates sealed content-review bindings and ledgers, not absent restricted original bytes. --verify-originals requires all reviewed local bytes and rereads their cited pages. No full-text redistribution.",
               "limit": "Original relevant pages/HTML read and substantive scope findings; not all pages manually read, not independent signoff, not all nominated original pointers recovered. Live HTML capture cannot retrospectively establish 2026-10-29 content.",
               "input_sha256": {p: sha((root / p).read_bytes()) for p in paths}}
    return rows, updated, summary


def csv_bytes(rows):
    out = io.StringIO(newline="")
    w = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return out.getvalue().encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--seal-evidence", action="store_true", help="Create reviewed-page evidence registry from local original bytes")
    parser.add_argument("--verify-originals", action="store_true", help="Require local original bytes for all DOC reviews")
    args = parser.parse_args()
    if args.seal_evidence or args.verify_originals:
        documents = {}
        for rel in MANIFESTS:
            for doc in json.loads((ROOT / rel).read_text(encoding="utf-8")):
                if "archive_path" in doc:
                    documents[doc["document_id"]] = doc
        sealed, cache = {}, {}
        for review in read(ROOT / INPUT):
            if not review["document_id"].startswith("DOC-"):
                continue
            doc = documents[review["document_id"]]
            if not (ROOT / doc["archive_path"]).is_file():
                raise ValueError("Required local original bytes absent: " + doc["document_id"])
            metadata, _ = verify_document(doc, review, cache=cache)
            sealed[review["target_id"]] = {"bindings": {k: review[k] for k in BINDINGS}, "metadata": metadata}
        payload = (json.dumps(sealed, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if args.seal_evidence:
            (ROOT / SEALED).write_bytes(payload)
            print("Sealed", len(sealed), "local original content reviews; no approval")
            return
        if (ROOT / SEALED).read_bytes() != payload:
            raise ValueError("Local original review differs from sealed registry")
    rows, updated, summary = build()
    outputs = {PREFIX + "_review.csv": csv_bytes(rows),
               PREFIX + "_review.json": (json.dumps(rows, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
               PREFIX + "_updated_339.csv": csv_bytes(updated),
               PREFIX + "_remaining_access.csv": csv_bytes([r for r in rows if not r["document_id"] or r["document_id"].startswith("WEB-") or "STILL_UNARCHIVED" in r["terminal_documentary_disposition"]]),
               PREFIX + "_summary.json": (json.dumps(summary, ensure_ascii=False, indent=2) + "\n").encode("utf-8")}
    for rel, payload in outputs.items():
        if args.write:
            (ROOT / rel).write_bytes(payload)
        elif (ROOT / rel).read_bytes() != payload:
            raise ValueError("Original scope export differs: " + rel)
    print(json.dumps({k: summary[k] for k in ("source_target_count", "original_content_reviewed_targets", "no_original_content_access_blocked_targets", "distinct_reviewed_documents", "formal_approvals_changed")}))


if __name__ == "__main__":
    main()
