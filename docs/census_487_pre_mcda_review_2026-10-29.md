# AU REE 487 pre-MCDA census review

## Scope and recovered inputs

This work package reviews the 487 fixed targets (86 legacy IDs + 401 unlinked E1 rows) against the recovered 1,006-row nationwide screening inventory and the official-tenure trace. It preserves target IDs and source fields. It does not rank projects or run MCDA.

Recovered workflow artifacts and SHA-256:

- `scheme-a-screening-review.zip` (`12874897589`): `644cce020444e7e2add29c93844714812a933470d1ae2641caf1d7b517ec5a92`
- `national-raw-inventory.zip` (`12874618255`): `667d1061d2d2cc8855d901d5914ea8d444f72077c382dd1809cbce0d888d22e6`
- `nationwide-487-tenement-company-reverse-trace.zip` (`12879078535`): `889ba353aace60db982ffa56aae25f8eac0aa8425950aa2cfc5f514792d14fac`

The 1,006 inventory has 803 E1, 163 E2, and 40 E3 source rows. Every one of the 401 E1 target IDs maps to an exact candidate/source/native ID. Official title trace produced 764 spatial intersections across 258 targets; 51 targets have no overlap in queried layers, 50 have no usable matched coordinate, and the SA tenure layer is unverified for 128. A title intersection is not proof of developer/operator identity.

Four original cohort extraction/decision files are absent from the repository and recovered artifacts: `provisional_project_groups_126.csv`, `legacy_203_crosswalk_audit.csv`, `all_1006_evidence_decisions.csv`, and `E1_project_unlinked_review_queue.csv`. The reconstructed ledgers below do not claim to reproduce those missing decisions. Thus the fixed 487 can be audited, but the original 86+401 selection logic and exclusions cannot yet be independently reproduced.

## Five-condition census screen

Each target is recorded against: (1) Australian jurisdiction, (2) identifiable location, (3) independent Project identity, (4) explicit REE role as product/co-product/planned recovery/target, and (5) exploration/resource assessment/development stage. An official point establishes a source-record location but does not establish a project boundary. Consequently, 401 E1 rows pass the source-point location check while their project boundary remains unestablished; 36 exact-name-linked rows are location review cases; 50 lack a verifiable coordinate.

Current provisional review states: 15 project candidates for human review, 10 REE-role holds, and 462 holds for insufficient project identity or REE-role evidence. These are evidence states, not final inclusion/exclusion decisions. Candidate groups are not approved merges.

## Outputs

Generated under `deliverable/`:

- `AU_REE_487_pre_MCDA_five_definition_review.xlsx`: editable review workbook with summary, all 487 rows, dedup candidates, review queues, source coverage and evidence lineage tabs.
- `487_definition_review.csv`: 487-row five-condition matrix retaining original IDs.
- `review_queue.csv`, `project_dedup_candidates.csv`: review cases and unapproved project candidates.
- `reconstructed_1006_evidence_ledger.csv`: all upstream candidates; cohort membership is exact where established; missing original selection reasons remain explicit.
- `exact_state_name_cluster_candidates.csv`: 885 exact state/name clusters for duplicate review; these are string clusters, not 885 validated projects.
- `legacy_86_exact_name_crosswalk_review.csv`: exact-name-only crosswalk against the 1,006 inventory (43 no exact match, 38 single-record candidates, 5 ambiguous); no fuzzy matches.
- `company_entity_resolution_queue_487.csv`: per-target holder/applicant vs developer/operator, ASX/ASIC identity, historical names, transfer dates, and primary evidence fields. Corporate chains remain pending case-by-case verification.
- `state_source_coverage_and_gaps.csv`: coverage for WA, SA, QLD, NSW, VIC, NT, TAS, ACT, and national GA. ACT has national GA scope only, with no independent state survey source in this archive.
- `upstream_reproducibility_gaps.csv`, `five_condition_decision_rules.csv`, `reconstructed_sa_project_deposit_crosswalk.csv`.
- `census_review.sqlite`, `census_review_manifest.json`: derived tables, row counts and input hashes; SQLite integrity check is `ok`.

## Reproduction

Place the three recovered archives beside the scripts, extract them to `scheme_a_upstream/`, `national_raw_upstream/`, and `trace_artifact/`, then run from the work package root:

```powershell
$py = 'C:\Users\whatt\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py .\build_487_definition_review.py .
& $py .\build_487_complete_proposal_workpack.py .
& $py .\build_487_editable_workbook.py .\deliverable
```

The first builder regenerates row-level evidence and a baseline SQLite database; the second adds derived audit ledgers and queue tables; the third creates the workbook. Inputs are read-only and output is under `deliverable/`. Required dependency: `xlsxwriter` for workbook generation.

## Remaining evidence work

The source archive has declared raw coverage for all seven states/territories plus national GA, but that does not mean every jurisdiction's tenure layer was successfully verified for every target. State-level source coverage and the target-level trace status are separate fields. The 487 company queue is deliberately unresolved: ASX releases, ASIC identifiers, dated company changes, transfers, and operator status need primary-source review. No company match is inferred from title-holder text alone. No MCDA criteria, weights, scores, or ranks are included.
