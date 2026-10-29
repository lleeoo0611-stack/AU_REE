# AU REE 487 pre-MCDA census review

## Recovered inputs

- `scheme_a-screening-review.zip`: workflow artifact `12874897589`, SHA-256 `644cce020444e7e2add29c93844714812a933470d1ae2641caf1d7b517ec5a92`. Contains the 1,006-row candidate table, candidate screening summary, exact-name review table, and SQLite.
- `national-raw-inventory.zip`: workflow artifact `12874618255`, SHA-256 `667d1061d2d2cc8855d901d5914ea8d444f72077c382dd1809cbce0d888d22e6`. Contains the raw-first 2026-10-29 official data archive and source manifests.
- `nationwide-487-tenement-company-reverse-trace.zip`: workflow artifact `12879078535`, SHA-256 `889ba353aace60db982ffa56aae25f8eac0aa8425950aa2cfc5f514792d14fac`. Contains immutable 487 targets, 487 row status records, 764 official title intersections, per-response hashes, and the original SQLite evidence database.

The upstream screened inventory has 1,006 rows: 803 E1, 163 E2, 40 E3. All 401 E1 target IDs resolve exactly to source candidate IDs in that inventory; the 86 legacy project IDs are preserved in the target list.

## Still missing upstream extraction decisions

The following four cohort-creation files were not found in the repository or recovered workflow artifacts:

- `provisional_project_groups_126.csv`
- `legacy_203_crosswalk_audit.csv`
- `all_1006_evidence_decisions.csv`
- `E1_project_unlinked_review_queue.csv`

Therefore, the fixed 487 rows and their E1 source records can be re-reviewed, but the original rules for selecting the 86+401 cohorts and rows excluded before selection cannot be independently reproduced yet.

## Current outputs

- `deliverable/AU_REE_487_pre_MCDA_five_definition_review.xlsx`: editable workbook with summary, 487-row five-condition review, candidate project dedup groups, and review queue.
- `deliverable/487_definition_review.csv`: row-level source and five-condition matrix; all original IDs are retained.
- `deliverable/project_dedup_candidates.csv`: candidate project groups; no group is approved automatically.
- `deliverable/review_queue.csv`: cases needing evidence or human resolution.
- `deliverable/census_review.sqlite`: the same derived review tables in SQLite.
- `deliverable/census_review_manifest.json`: counts, input hashes, source status, and known missing upstream files.
- `deliverable/reconstructed_sa_project_deposit_crosswalk.csv`: exact native deposit ID joins from the raw SA snapshot; no fuzzy-name matches.

## Rerun

From this folder, run:

```powershell
$py = 'C:\Users\whatt\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py .\build_definition_review.py
& $py .\build_editable_workbook.py
```

The input archives are kept unchanged. The builder writes only under `deliverable/`.

## Interpretation limits

- This is a census/entity-linkage workpack only; no MCDA criteria, scoring, weights, or ranking have been run.
- Government point coordinates can locate a source record without establishing a project boundary. 401 E1 target locations are explicitly unverified source points; 50 legacy rows have no usable coordinates.
- Tenement point-in-polygon matches indicate spatial title candidates, not project ownership or operator identity. SA tenure was not verified for 128 targets.
- Project group names are candidates, not approved entity merges. ASX/company name changes and transfers still require dated primary-source review.
