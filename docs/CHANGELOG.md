# Change log

## Documentation roadmap — 2026-10-30

- Reorganize the root README into research goals, verified implementation state, executable workflows, planned requirements and reference navigation.
- Add `docs/RESEARCH_REQUIREMENTS_AIMS_ABC.md` defining development-potential assessment, ranking robustness and driver analysis with P0–P3 acceptance tests.
- Preserve the pre-reorganization five-stage README at `docs/archive/README_v1.0.4_pre_ABC_2026-10-30.md`.
- Distinguish G0/R1/S1/RS evidence/cohort scenarios from resource/development/strategic-supply weight perspectives; document that G0 currently omits R1/S1.
- Documentation-only change; program behavior, data and research results are unchanged.


## v1.0.1 — 2026-10-29

- Implement separate archived-document SHA-256 validation and independent reviewer decisions; input self-declared `VERIFIED` alone is not accepted.
- Introduce provenance tables `source_documents`, `evidence_approvals`, `evidence_links`, `approved_project_reviews`, and the `gis_release_gates` audit table.
- Re-evaluate coordinate and evidence approvals from current inputs on every upstream re-run; revoke stale scores and derived observations.
- Freeze G0 global eligibility to the original 19 Alternatives; block all global matrix exports until 19/19 approved GIS and point values are complete.
- Allow R1/S1/RS separately labelled subset releases only if at least two non-spatial eligible projects all have approved GIS.
- Require archived and separately approved local GIS layers; non-archived remote GIS endpoints remain `OFFICIAL_REMOTE_NOT_ARCHIVED_OR_APPROVED`.
- Add Python 3.11/3.13 offline CI, R 4.4.3 synthetic deterministic smoke CI, and regression tests for approval revocation and global/subset GIS gating.
- Historical 203-project census and 220 unverified observations remain unchanged; no real project promoted to Verified.

## v1.0.0

- Five-stage Australian REE census/criteria/GIS/eligibility/R-export pipeline.

## v1.0.4 — Scheme A evidence-backed identity policy

- Preserve original public-government records and extended REE-mineral occurrence inventory.
- Require independently approved project-identity documents for new Project Master entries; legacy 203 frozen seeds remain distinct.
- Add geological entity/provenance, parent links, cross-source review pairs, and identity audit tables, with editable CSV exports and repeatable tests.
