# AU REE 487 pre-MCDA census review

Recovered from GitHub Actions workflow artifacts on 2026-10-29:

- Workflow artifact `12874897589` (`australia-national-ree-scheme-a-screening-review`), SHA-256 `644cce020444e7e2add29c93844714812a933470d1ae2641caf1d7b517ec5a92`.
- Workflow artifact `12874618255` (`australia-national-unfiltered-raw-inventory`), SHA-256 `667d1061d2d2cc8855d901d5914ea8d444f72077c382dd1809cbce0d888d22e6`.
- Workflow artifact `12879078535` (`nationwide-487-tenement-company-reverse-trace`), SHA-256 `889ba353aace60db982ffa56aae25f8eac0aa8425950aa2cfc5f514792d14fac`.

The screened nationwide inventory contains 1,006 rows (803 E1, 163 E2, 40 E3). All 401 unlinked E1 target IDs resolve to exact candidate IDs in that inventory, and the legacy 86 target IDs are retained. The trace artifact contains 487 target rows, 487 status rows, 764 official title intersections, and response hashes.

Four cohort-extraction files remain missing from the repository and available workflow artifacts: `provisional_project_groups_126.csv`, `legacy_203_crosswalk_audit.csv`, `all_1006_evidence_decisions.csv`, and `E1_project_unlinked_review_queue.csv`. Thus the present 487 rows can be reviewed and traced, but the original 86+401 selection logic and all excluded records cannot be independently reproduced.

State source coverage has known limits: 128 SA targets have no verified official tenement layer; 50 targets lack usable matched coordinates; a title intersection is not proof of project ownership, developer, or operator. All inferred project links remain review-only, including the 16 SA native-ID project/deposit links.

The editable review package is generated locally under `outputs/01a18684-f243-7a91-ad23-3da8fc922076/deliverable/`. It includes a row-level five-condition matrix, candidate project dedup groups, review queue, SQLite, and workbook. No MCDA ranking, weights, or scoring are performed.
