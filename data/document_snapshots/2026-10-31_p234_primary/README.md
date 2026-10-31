# Original-document research archive — 2026-10-31

Execution `P234-144-PRIMARY-SCOPE-20261031-V1`; immutable source snapshot 2026-10-29.

Full third-party PDF/HTML/bin originals remain in this local directory under the exact `archive_path` recorded in each acquisition manifest. They are ignored by Git to avoid redistributing restricted full text. Public manifests retain requested publisher/official URLs, attempts/errors, retrieval dates, exact byte SHA256, sizes and filenames. Expiring signed redirect queries are removed; the stable requested downloader URL remains.

`reviewed_content_evidence.json` binds each of 142 source-target reviews to the verified original-byte hash, relevant page/section locator, short anchor, optional exact government ID/table row, reviewed-page text hash and parsed government coordinates. It contains no full extracted page text. It is a research record, not a digital signature, independent approval or substitute for reading an unavailable original. Scaddan is separately recorded as web-only, without an invented byte hash. Yellowband Plain remains unread.

Public reproduction checks the recorded bindings and regenerates the ledger. With originals present, the same script validates all present acquired bytes and rereads relevant pages; `--verify-originals` requires all reviewed originals. If a byte hash changes, it fails. If an original is missing and a binding changes, it fails rather than treating the changed claim as verified. `--seal-evidence` explicitly requires all reviewed local DOC originals and rebuilds the registry after review; changes must be reviewed in Git/PR.

```sh
python -m pip install pypdf==6.10.0
python scripts/review_p234_144_primary_scope.py --check
python scripts/review_p234_144_primary_scope.py --check --verify-originals
```

For fresh acquisitions, use `scripts/acquire_p234_primary_documents.py --supplement inputs/source_review_20261031/p234_144_document_requests.csv --manifest NEW_NAME.json`. This is a new retrieval, may differ from historical content, and does not overwrite the old manifest or approve any scope. The GEMIS resolver additionally verifies exact original handles/filenames through the official API. Recovered new bytes must match the recorded historical hash for historical replay; otherwise retain a new version and review the differences. `scripts/extract_p234_document_text.py` creates local ignored review aids; text extraction is not human scope review. Scanned Benmara pages require visual review, not an empty extracted-text claim.

See [research report](../../../docs/audits/2026-10-31_p234_144_primary_scope_report.md) for findings, editable inputs and remaining gaps.
