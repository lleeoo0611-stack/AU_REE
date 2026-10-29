# 487-row entity linkage and quality review

`quality_gate_487.py` runs inside `rebuild_all.py` after row adjudication and before CSV-to-SQLite construction. It requires only the Python standard library.

## Output tables

- `project_entity_register.csv`: deterministic IDs for reviewed Project candidates and source-level entities. Project candidate IDs use the current candidate group key; a key change creates a new ID and must be reviewed as a possible rename/merge/split. Source records are retained separately as Project candidate, deposit, prospect, tenement, occurrence, or historical source-record entities.
- `project_entity_membership_487.csv`: exactly one row for each frozen target ID. The `project_entity_id` is populated only when the target occurs in the reviewed project candidate crosswalk. Other targets remain `UNRESOLVED_NO_PROJECT_LINK_INFERRED`.
- `project_evidence_register.csv`: one row per recorded URL. URL presence does not establish that the source supports a condition. Source type, publisher/date, page/section, claim, and condition supported are explicit review fields and stay blank/unclassified until checked.
- `quality_gate_487.csv` and `quality_gate_487_summary.json`: row counts, ID consistency, link coverage, source locator gaps, disposition counts, and input hashes.

Each of the five conditions is normalized to `PASS`, `FAIL`, `UNKNOWN`, or `CONFLICT`. Only `PASS` across all five on Project-level evidence is eligible for human-approved inclusion. `UNKNOWN` and `CONFLICT` remain HOLD; the script never promotes or excludes a Project by name similarity or missing evidence. Registered titleholder and operator/proponent are separate fields and remain blank until source evidence distinguishes them.

## Current verified state (2026-10-29)

- 487/487 original target IDs are unique and appear once in the inclusion gate and entity membership table.
- 30 reviewed candidate Project groups are represented, with 46 target rows linked to those groups and 441 without a reviewed Project link.
- 95 candidate source URLs are listed individually. All 95 still need page/section and claim-level review; the URLs have not been treated as proof by themselves.
- The original 37 `PROJECT_CANDIDATE_REVIEW`, 6 `HOLD_REE_ROLE`, and 444 `HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE` row dispositions are preserved. Candidate rows still require human sign-off; no exclusions or MCDA decisions are added.

This quality layer makes the gaps explicit and machine-checkable. It does not claim that the unresolved project, tenure, company-history, or evidence-location work is complete. Refreshing external sources requires a new dated evidence snapshot and review; there is no automatic web acquisition in this runner.

## Delimiter correction

Target ID lists accept pipe, semicolon and newline separators. All 487 IDs are retained; 46 have existing review-group links (37 candidate rows and 9 HOLD rows), with 441 unlinked. Three Mary Kathleen HOLD rows link only to a review group while their admission gate remains unresolved. Independent ID extraction, unknown/duplicate-ID checks and gate/group reconciliation guard against silent loss. The workbook includes 487 entity-link rows and cross-table differences. Release snapshot: 2026-10-29-r18-delimiter-release.

