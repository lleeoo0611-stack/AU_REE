# Change log

## P0 Cohort and JORC data design — 2026-10-31

- Begin research P0.1/P0.2 **design and data-readiness audit** under Research Architecture v2, without modifying pipeline, SQL migrations or scoring.
- Add `docs/P0_COHORT_SELECTION_PROTOCOL.md` and `docs/P0_PROJECT_RESOURCE_SCHEMA.md` as detailed Project admission and scoped JORC resource model contracts.
- Add 39-group candidate review CSV and summary under `docs/audits/` (frozen 2026-10-29 sources); preserve unapproved/HOLD status, no auto-promotion to Project.
- Add editable, empty Project Gate and JORC Statement review CSV templates under `inputs/templates/`; update README, docs index, implementation plan and decision log.
- C1 required panel, approved Project set and v2 schema migration remain pending. No historical results, evidence approvals, original inputs or MCDA algorithms altered.


## Research Architecture v2 contract — 2026-10-31

- Add `docs/RESEARCH_ARCHITECTURE.md` as the canonical A/B/C research contract; define C0 Census, C1 Primary MCDA, C2 Extended Projects, C3 Historical Validation and P0–P3 release gates.
- Add `docs/DATA_SPECIFICATION.md`, `docs/MCDA_PROTOCOL.md`, `docs/VALIDATION_PROTOCOL.md`, and `docs/RESEARCH_IMPLEMENTATION_PLAN.md` to specify JORC/entity/evidence data semantics, six-domain scoring, scenario/AHP routing, SMAA and Aim C validation.
- Add `.github/pull_request_template.md` to require Aim/Gate, data lineage, compatibility, test and document review in future PRs.
- Update README, docs index, historical requirements, decisions and Git workflow to refer to the v2 design contract.
- **Documentation/workflow only:** no migration, scoring logic, current eligibility gate, source data, or research results changed; v2 parameters and C1 admission list remain pending.


## Research framework and status assessment — 2026-10-30

- Add an editable, GitHub-rendered Mermaid framework to the root README, distinguishing the implemented census/evidence/GIS/eligibility/MCDA pipeline from proposed Aim A/B/C research outputs.
- Add a compact qualitative assessment to the README and the evidence-based detailed review at `docs/PROJECT_ASSESSMENT_2026-10-30.md`; index it in `docs/README.md`.
- Document current census numbers, the G0 versus six-domain limitation, cohort/weight distinctions, evidence gaps, methodological selection biases, and P0–P3 research priorities.
- Documentation only: no source data, admission gate, scoring algorithm or published result changed.


## Repository structure — 2026-10-30

- Keep the root README concise and move operation details into `docs/RUNBOOK.md`; add navigation in `docs/README.md`, `outputs/README.md` and `reproducibility/workpack/README.md`.
- Remove root copies of three identical `scripts/build_487_*.py` entrypoints and SQL migrations `0007–0009`; retain the canonical `scripts/` and `db/migrations/` versions.
- Move four distinct frozen-workpack scripts into `reproducibility/workpack/`, update `rebuild_all.py` and provenance paths, and preserve dated snapshots and tracked research outputs.
- Remove accidental one-byte root `test` file; add repository layout regression test. No changes to official source records, release files, eligibility or MCDA formulas.
- **Compatibility:** historical command paths for root-level workpack scripts have changed; use `reproducibility/rebuild_all.py` and `docs/RUNBOOK.md`.


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
