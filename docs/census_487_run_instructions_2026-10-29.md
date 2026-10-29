# Re-run the 487-row census review

1. Download the three immutable GitHub Actions artifacts listed in `census_487_evidence_manifest_2026-10-29.json` and verify their SHA-256 values.
2. Expand the raw inventory and screening artifact under `<workpack>/national_raw_upstream/` and `<workpack>/scheme_a_upstream/`.
3. Expand the 487 reverse trace artifact under `<workpack>/trace_artifact/`.
4. Run `python scripts/build_487_definition_review.py <workpack>` from a Python 3.10+ environment. This writes `deliverable/487_definition_review.csv`, `project_dedup_candidates.csv`, `review_queue.csv`, `census_review.sqlite`, and a manifest.
5. Install `xlsxwriter` and run `python scripts/build_487_editable_workbook.py <workpack>/deliverable` to create the editable workbook. Without the optional workbook dependency, the CSV and SQLite outputs remain complete.

Do not promote candidate links to accepted projects automatically. The missing cohort-extraction files must be recovered before claiming that the original 86+401 sample selection is reproducible.
