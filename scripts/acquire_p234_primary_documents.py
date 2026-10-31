"""Acquire immutable documentary bytes for the fixed 144 target worklist.

Acquisition is NOT scope approval. Reviewers must read relevant full pages and
record source-specific scope findings separately. No frozen source is edited.
"""
import argparse
import concurrent.futures
import csv
import hashlib
import json
import time
import urllib.request
from urllib.parse import urlsplit, urlunsplit, parse_qsl
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/document_snapshots/2026-10-31_p234_primary"
QUEUE = ROOT / "docs/audits/2026-10-31_p2_p3_p4_closeout_document_pointer_holds.csv"


def inventory():
    urls = {}
    with QUEUE.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            for event in json.loads(row["documentary_references_json"]):
                for key, value in event["references"].items():
                    if "url" in key and key != "official_source_url" and value.startswith("http"):
                        urls.setdefault(value, set()).add(row["target_id"])
    return urls


def public_url(url):
    parts = urlsplit(url)
    if any(k.lower().startswith("x-amz-") or k.lower() in {"access_token", "token", "signature"} for k, _ in parse_qsl(parts.query)):
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    return url


def fetch(url, targets):
    ident = "DOC-" + hashlib.sha256(url.encode()).hexdigest()[:12]
    metadata = {"document_id": ident, "requested_url": url, "target_ids": sorted(targets),
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "acquisition_is_scope_verification": False}
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 AU-REE-research-source-review"})
        with urllib.request.urlopen(request, timeout=45) as response:
            chunks, size, started = [], 0, time.monotonic()
            while True:
                block = response.read(65536)
                if not block:
                    break
                chunks.append(block)
                size += len(block)
                if size > 35 * 1024 * 1024 or time.monotonic() - started > 90:
                    raise ValueError("Retrieval size/time limit exceeded; no content verification claimed")
            payload = b"".join(chunks)
            if len(payload) > 35 * 1024 * 1024:
                raise ValueError("Document exceeds 35MiB retrieval limit")
            metadata.update({"final_url": public_url(response.url), "http_status": response.status,
                             "content_type": response.headers.get("Content-Type", "")})
        sha = hashlib.sha256(payload).hexdigest()
        ext = ".pdf" if payload.lstrip().startswith(b"%PDF-") else ".html" if b"<html" in payload[:2000].lower() or b"<!doctype html" in payload[:2000].lower() else ".bin"
        path = OUT / (ident + "_" + sha[:16] + ext)
        if not path.exists():
            path.write_bytes(payload)
        metadata.update({"status": "BYTES_ARCHIVED_NOT_SCOPE_APPROVED", "sha256": sha,
                         "byte_count": len(payload), "archive_path": path.relative_to(ROOT).as_posix(),
                         "format": ext[1:]})
    except Exception as exc:
        metadata.update({"status": "ACQUISITION_FAILED", "error": str(exc)})
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supplement", type=Path, help="CSV: url,target_id (optional replacement primary pointers)")
    parser.add_argument("--manifest", default="acquisition_manifest.json")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / args.manifest
    if path.exists():
        raise FileExistsError("Use a new manifest name for new retrieval attempts")
    urls = inventory()
    if args.supplement:
        urls = {}
        with args.supplement.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                urls.setdefault(row["url"], set()).add(row["target_id"])
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch, url, targets): url for url, targets in urls.items()}
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            records.append(record)
            print(record["document_id"], record["status"], record.get("format", record.get("error", "")), flush=True)
    records.sort(key=lambda x: x["document_id"])
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Recorded", len(records), "document attempts; no scope approvals")


if __name__ == "__main__":
    main()
