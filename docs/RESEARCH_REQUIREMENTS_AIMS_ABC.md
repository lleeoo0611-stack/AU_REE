# Research requirements — Australian REE MCDA (Aims A/B/C)

**Status:** implementation specification / roadmap（v2 子規格，詳見 [RESEARCH_ARCHITECTURE](RESEARCH_ARCHITECTURE.md)）  
**Decision date:** 2026-10-30  
**Scope:** extends the existing five-stage Python/SQLite/GIS/R workflow; does not replace its evidence-approval gates or reclassify unapproved candidates.

> **版本使用原則（2026-10-31）**：本文件保留詳細 P0–P3 待辦，但後續實作以 [RESEARCH_ARCHITECTURE](RESEARCH_ARCHITECTURE.md)、[DATA_SPECIFICATION](DATA_SPECIFICATION.md)、[MCDA_PROTOCOL](MCDA_PROTOCOL.md)、[VALIDATION_PROTOCOL](VALIDATION_PROTOCOL.md) 的 v2 契約為研究定義依據。現有 `G0/R1/S1/RS` 和 `Commercial/ESG` 仍是 v1 的歷史語意；v2 第六構面名稱建議為 `Commercial & Regulatory Readiness`，尚待正式 criteria/version migration。所有數值門檻、weights 和主要 Cohort 必須在獨立 Gate 中審核定稿。

## 1. Research contract

**Aim A — Development Potential Assessment.** Assess Australian rare-earth projects across resource endowment, strategic REE composition, technical feasibility, development readiness, infrastructure and commercial/ESG factors. Report domain profiles and a clearly defined, preference-dependent composite evaluation.

**Aim B — Preference & Ranking Robustness.** Quantify how project priorities change with decision preferences, numerical evidence, scoring choices, algorithm choice and eligible cohort. Report rank acceptability, top-k frequencies and pairwise comparison probabilities under explicitly versioned assumptions.

**Aim C — Drivers of Development Priority.** Separate internal model drivers (criterion weights, utility functions, omissions) from observed associations of project characteristics (deposit type, lifecycle stage, resource characteristics, accessibility, evidence maturity) with scores or ranks. Report subgroup/sample sizes and distinguish associations from causality.

The publication unit is a **project**. Deposits, prospects, tenements, resource statements, companies and documents remain independently traceable entities. An Australian REE *candidate* is not automatically an approved MCDA alternative.

## 2. Current implementation versus required extension

| Area | Present baseline in repository | Required extension |
| --- | --- | --- |
| Population | Five-stage pipeline with official-source adapters, Scheme A review, persistent project identifiers; additional nationwide census/trace artifacts | Formal project–deposit–tenement and ownership temporal relations; reconcile outputs from the census review workstream into one versioned canonical schema |
| Evidence | Source SHA-256, independent approval, observation provenance, QA/review queues | Scoped JORC resource statements; typed missingness; explicit uncertainty-model and lineage tables |
| Criteria | 12 criteria in six conceptual domains (R1, S1, T1–T2, D1, I1–I4, C1–C3) | Frozen reference-scale utilities; dependency graph and hierarchical domain scoring; diagnostic resource/readiness scores |
| Eligibility | G0/R1/S1/RS point-value gates; 70% coverage, 4 domains, pre-FID Scoping–DFS/BFS/Feasibility; GIS release gates | Mandatory core evidence + domain coverage review; frozen and comparable cohorts; analyze selection/maturity bias instead of relying on one arbitrary completeness fraction |
| MCDA | AHP (CR), PROMETHEE II, SAW, TOPSIS, Dirichlet weight Monte Carlo, leave-one-criterion-out, threshold sensitivity | Joint weight/data uncertainty and SMAA-2-style rank acceptability; pairwise probabilities; cohort/method sensitivity |
| Drivers/validation | Limited criterion deletion and method comparison | Leave-one-domain-out, global sensitivity, lifecycle/deposit-type comparisons, historical forward validation |
| Reproducibility | Stage checkpoints, manifest, SQLite, frozen inputs, GitHub Actions offline and R synthetic tests | Immutable analysis-run registry, versioned criteria/utility/weight/missing-data schemas, release snapshot and derived-result lineage |

**Important current distinction:** `G0_BASELINE` contains T1, T2, D1, I1–I4 and C1–C3; it has **no R1/S1**. R1/S1/RS are evidence-coverage decision-matrix variants, whereas resource/development/strategic-supply *decision perspectives* refer to weights. Do not conflate cohort scenarios with weight perspectives. A future six-domain Aim A result requires a comparable evidence-approved cohort containing both R1 and S1 (or an explicitly declared uncertainty treatment), rather than relabeling G0 as six-domain.

## 3. P0 — database semantics and identity

### 3.1 Relational entities

Retain original raw records and stable `project_id`; add/migrate at minimum:

- `deposit_master` and `project_deposit_links` with valid dates, role and evidence ID; accommodate one-to-many and many-to-many membership, without auto-promoting a deposit to a project.
- `tenement_master`, `project_tenement_links`, `company_entities` and `project_company_roles`; distinguish legal titleholder, operator, developer, proponent and proposed transferee, with effective/publication dates.
- `project_locations` with geometry/point role, coordinate accuracy, original CRS, publisher, snapshot and approval. Project representative points are not automatically deposit centroids or project boundaries.
- `source_documents` and `observations` tied through evidence lineage; retain immutable source bytes/SHA-256, page/table/section, raw text/value/unit/basis, normalized value, extraction method and independent approval.
- `project_events` for dated MRE/Scoping/PFS/DFS/FID/approvals/offtake/financing/suspension/restart/production events; derive lifecycle state **as of** a snapshot date instead of overwriting historical events.
- `analysis_runs`, `run_inputs`, `run_outputs`, `schema_migrations` for deterministic releases.

Linking an observation to a project requires the underlying statement's project/deposit scope and explicit aggregation logic. Keep unresolved many-to-many or conflicting relations in review queues.

### 3.2 Resource statement and chemical basis

Add `resource_statements`, `resource_statement_deposits`, `resource_category_rows` and `resource_composition_rows`. Preserve reporting code (JORC edition), statement scope, competent-person/source citation, report and effective dates, cut-off value **and unit**, tonnage, grade, M/I/I category, oxide or elemental reporting basis, and material/ore/metallurgical scope. Keep Mineral Resource distinct from Ore Reserve, and preserve the source's reporting basis (e.g., TREO versus THM/MzEq); do not silently combine incompatible resource estimates or cut-offs.

Version derived formulas. For a compatible grade basis:
`contained_treo_kt = mineral_resource_mt * treo_grade_pct * 10`.
Store measured/indicated/inferred components and reconciled totals without summing the same deposit or superseded statement twice. Store Nd/Pr/Dy/Tb oxide definitions and `%TREO` denominators explicitly.

### 3.3 Time, provenance and historical state

Every observation/event must separate `effective_date`, `publication_date`, `retrieved_at`, `source_id` and `verification_status`. A historical snapshot may use evidence **published by** the cutoff and valid/effective by the evaluation date; later evidence must not leak backwards. Each run records `snapshot_id`, frozen sample IDs, commit SHA, source manifests, configuration hashes, model version, RNG seed, QA decision and reasons for exclusion/review.

### 3.4 Missingness and uncertainty

Do not map missing to score zero. Add `missingness_records`: `NOT_REPORTED`, `NOT_MEASURED`, `NOT_APPLICABLE`, `SOURCE_UNAVAILABLE`, `CONFLICT`, `REVIEW_PENDING`. Add `uncertainty_models` specifying variable, evidence basis, distribution/interval, parameters, correlation/dependency group, estimator and scenario version. Experimental standard deviations/ranges take precedence; phase/study-stage-specific CV assumptions require calibration or explicit sensitivity scenarios. Preserve differences between stage recovery and overall process recovery.

### P0 acceptance tests

- Stable project IDs and no silent record deletion; any merged candidate has auditable links and decision.
- JORC categories reconcile within rounding tolerance on identical scope/cut-off/basis; no double count across deposits or releases.
- Same snapshot and commit reproduce identical cohort, scores and manifests; a newer announcement cannot enter a prior snapshot.
- Revoked evidence approval removes dependent derived values and eligibility on rerun.
- Any unresolved source, spatial or resource-basis conflict stays outside verified scoring.

## 4. P1 — Aim A scoring and eligibility

1. Preserve six conceptual domains: Resource Potential, Strategic Composition, Technical Feasibility, Development Readiness, Infrastructure, Commercial/ESG.
2. Construct a **criterion dependency graph** before weighting: mathematical (ore Mt × TREO grade = contained TREO; contained NdPr = contained TREO × NdPr share), conceptual and empirical correlations. Avoid counting all derived forms as independent benefits without a justified decomposition.
3. Use versioned, ex ante reference-scale utility functions `u_j(x)` (monotonic piecewise, bounded, log/saturating as justified) instead of automatic cohort min-max in the principal cross-snapshot analysis. Save thresholds, directions, rationales and test cases in proposed `config/scoring_functions.yaml`.
4. Use hierarchical domain weighting: within-domain `v_gj` then between-domain `W_g(s)`; require per-level normalization and traceable AHP/elicitation inputs. Record analyst-assumed weights as illustrative, not elicited.
5. Produce a domain score vector and preference-dependent composite; separately expose resource-endowment and development-readiness **diagnostic** indices, not additional weighted terms (avoid double counting).
6. Treat legal/geographic/admission constraints as eligibility gates where compensation is inappropriate, and gradated performance as scored criteria. Pilot stage as stratification, with a documented alternative model including D1, to quantify lifecycle-stage self-reinforcement.
7. Keep census, resource-defined cohort, primary pre-FID feasibility cohort and sensitivity cohorts distinct. Start from the current `config/eligibility.json` behavior; evaluate the 70%/four-domain gate for stage-dependent selection bias before revising any threshold. Retain exact exclusion reason and cohort denominator.
8. Infrastructure: record location role and accuracy, operating/planned asset status, geometries and dataset versions. Current EPSG:3577 straight-line distances remain valid *proximity* measures; route/network cost, service capacity and water availability are additional metrics, not synonyms for straight-line distance.

### P1 acceptance tests

- Frozen scoring thresholds yield the same score for an unchanged project when unrelated alternatives are added.
- Derived criterion dependencies are tracked, and removing redundant inputs does not silently alter a domain weight sum.
- Every published ranking states cohort, cutoff, score function and weights; `G0` is never called a full six-domain score while R1/S1 are absent.
- No pseudo-weight or unapproved value is presented as an authoritative result.

## 5. P2 — Aim B rank robustness

Keep AHP/PROMETHEE II/SAW/TOPSIS baseline. Expand analyses in distinct layers:

**Weight uncertainty:** specified resource/development/strategic-supply preference regions, elicited weights and bounded/simplex sensitivity samples. Dirichlet is an implementation option; record concentration and preference constraints. Do not sample all perspectives from an unrestricted common distribution.

**Data uncertainty:** observed confidence intervals, literature/technical ranges, supported distributions, typed missing-data scenarios and preserved algebraic/cross-variable dependencies. Never independently draw contained TREO, ore Mt and grade if contained TREO is a deterministic product.

**Method uncertainty:** separately compare PROMETHEE II, SAW and TOPSIS; keep preference-function thresholds and normalization versioned. Evaluate rank reversals under alternative sets and fixed versus sample-dependent scales.

**Cohort uncertainty:** leave-one-project-out, alternative eligibility rules and frozen full/subset releases; compare rank probabilities only within identified cohorts or by comparable common-alternative subsets.

Implement SMAA-2-style rank acceptability where supported by valid inputs, including `b_i^r = P(Rank_i=r)`, `P(Top k)`, median rank, 90% rank interval and `P(i\u003e j)` under the defined preference/uncertainty ensemble. These are **conditional ranking frequencies, not project development-success probabilities**.

### P2 acceptance tests

- Seeded simulation bitwise or numerically reproducible under declared environment; every draw is valid (weights sum to 1, no impossible derived values).
- Separate weight-only/data-only/joint uncertainty runs and model-method comparison have identifiable run IDs.
- Output probabilities lie in [0,1]; rank acceptability across ranks sums to one per project (subject to tie convention).

## 6. P2 — Aim C drivers and statistics

Split outputs into:

**C1 Internal model drivers:** leave-one-criterion-out, leave-one-domain-out, weight/utility perturbations, global sensitivity (appropriate for dependent factors), pairwise rank-flip analysis and rank/score decomposition. Quantify rank shifts, not only rank correlation.

**C2 Project characteristics:** deposit type, ionic-adsorption evidence versus other clay-hosted classification, mineralogy, lifecycle stage, REE composition, technical test maturity, evidence completeness and GIS accessibility. Compare score profiles and rank distributions by subgroup; record group size and missingness; use regression/mixed effects only where effective sample sizes support it.

Avoid circular inference: a criterion's statistical relation to its own weighted composite is a model-internal relationship. For deposit type/lifecycle contrasts, control stage/selection and note classification evidence. Claims from cross-sectional relationships are associative unless separately identified.

### P2 acceptance tests

- Driver outputs distinguish model-mechanical sensitivity from project-level associations.
- D1 stage-as-score versus stage-as-stratum models are reproducibly compared.
- Each subgroup chart/model reports project N, effective N, missingness, cohort and uncertainty interval.

## 7. P3 — historical validation and publication outputs

- Support immutable retrospective snapshots (e.g., 2022-12-31, 2024-12-31, 2026 cutoff) using only information published by each snapshot.
- Predefine forward outcome events: advancement to PFS/DFS/FID, permit/financing milestones, with fixed observation horizon and stage-adjusted baseline. Distinguish descriptive concordance from calibrated prediction.
- Generate editable, rerunnable datasets and figures: `project_database.csv`, `criterion_dictionary.csv`, `domain_scores.csv`, `analysis_matrix.csv`, `rank_acceptability.csv`, `pairwise_probabilities.csv`, `driver_results.csv`, `historical_validation.csv`, spatial GeoPackage and SVG/PDF figures; author scripts remain source of truth.
- Export a methods/supplement bundle including source coverage, original/canonical IDs, inclusion/exclusion reasons, independent approvals, formulas, weight configurations, simulations and reproducibility manifests.

## 8. Rollout plan, integration points and change control

| Priority | Proposed integration | Completion gate |
| --- | --- | --- |
| P0.1 | `src/au_ree/core.py`, SQL migrations, census reconciliation | Identity, JORC and source-lineage schema migration tests |
| P0.2 | `stages/criteria.py` and evidence review inputs | Resource-basis QA, missingness/uncertainty taxonomy tests |
| P1.1 | `config/criteria.json`, proposed `config/scoring_functions.yaml`, criteria builder | Six-domain dependency audit and frozen-reference scores |
| P1.2 | `stages/eligibility.py`, cohort manifests | Explicit gates, denominators, stage-bias diagnostics |
| P2.1 | `R/run_mcda.R` or dedicated R analysis modules | Weight/data joint uncertainty, rank acceptability and seeded tests |
| P2.2 | Separate sensitivity/statistics modules | C1/C2 driver reports and subgroup tests |
| P3 | Snapshot/export runner and report generators | Retrospective tests and publication-ready editable outputs |

Apply changes by migrations and targeted modules rather than adding another monolithic script. Keep the existing five stages executable while extending data/analysis modules. Use Git branches/PRs, document schema and calculation changes, preserve prior snapshot releases, and rerun Python offline tests and R synthetic smoke tests.

**Source anchors:** `20260906 purposal.pptx` (research aims and six domains); `config/criteria.json`, `config/eligibility.json`, `config/r_analysis.json`, `R/run_mcda.R` (implemented rules); `docs/RESEARCH_DECISIONS.md` (r983 decisions); `docs/FULL_TRACE_REVIEW_20261030.md` and `CENSUS_RELEASE.md` (recent census/evidence state); `docs/SCHEME_A_PROJECT_MASTER.md` (identity gate).