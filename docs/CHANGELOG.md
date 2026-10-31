# Change log

## P1/P2 publicly accessible evidence closing review — 2026-10-31

- Reassessed **P1 19 remaining cases / 31 immutable sources** on freely accessible government, issuer and secondary-index documents: 13 positive REE/Project leads (22 rows), 2 geographic identity conflicts (4), and 4 indexed WAMEX reports (5). New primary/context sources distinguish WA Wingellina Ni-Co from SA Claude Hills and Ambergate vs Witchcliffe name/tenement conflict; P1 C1 gates all remain HOLD.
- Official original PDFs for WAMEX A119194/A120393/A129842/A109188 remain unarchived; company-submitted page-text indexing yields bounded documentary claims but **does not supply original PDF SHA**. No email was sent.
- **P2 all 28 source rows / 27 provisional cases** assigned unique terminal scoped documentary review results and reopen conditions: 17 direct government/issuer leads still lacking approved Legacy source-to-Project identity, 1 REE stage outside issuer Scoping, 3 historic sites, 1 negative single drill target, 3 native features not Project proof, 2 regional index/name collisions. Factual report excerpts support Arthur Popes, Bell's Monazite, Blueys Folley, Duke, Blue Tier, Cruncher, DC, Tunnel Hill, Brumby Clydesdale and Wedderburn.
- Add editable source and case evidence inputs, reproducible 31+28 target CSV derivation, machine-readable QA, dedicated unit tests and CI. Preserve 412 original HOLD source IDs, 73 prior P1, untouched P3 216/P4 95, zero independent formal C1 or JORC/GIS approvals.
- Follow-up for inaccessible original archive (#30), P1 positive case signoffs (#32), and P2 source–Project/tenure checks (#35) remains open.


## P2 first-pass source triage within 412 HOLD — 2026-10-31

- Freeze historical denominator 412 = P1 73 + P2 28 + P3 216 + P4 95 (no re-ranking, no C1 admission).
- Audit all 28 P2 source IDs (22 Legacy / 6 E1) into 27 provisional source-site cases. Preserve a separate historical Mary Kathleen mine (two native deposit points) and Mary Kathleen tailings legacy research source.
- Curate government/issuer / native context: Mary Kathleen government remediation + 2026 Bayan bench testwork, Port Pirie SA SARIG #8908 treatment tailings, Tasmanian Anchor Tin Deeps 2024 EDGI REE drilling, Northern Territory Boulder Ridge and Bruce/Plenty River/Edwards Creek exploration, Elaine Dorothy historical REE, Douglas 2004–2012 historic Iluka HMS, P1 Talisker legacy cross-reference. VIC Bondi native feature prohibited from name-only joining Iluka Douglas Bondi mine.
- Current provenance: 11 documentary source-case leads pending same-scope identity, 12 Legacy names only, 3 VIC native features, 1 regional secondary index; all remain C0 without independent Project / JORC REO / GIS release / C1 approvals.
- Add `scripts/audit_p2_28_initial_triage.py`, dedicated `unittest`, CI workflow, evidence CSV, frozen source/case CSVs, snapshot JSON, report and index.
- P1 file-access (#30) and downstream C1 case approvals (#32) remain explicitly open. P2 subsequent research tracked in #35.
- Observed dedicated P2 phase-one, Python offline and R synthetic CI all successful on commit 787fa9f7 (GitHub Actions 41176845661, 41176845732, 41176841192); CI attestation saved under docs/audits.


## P0/P1 desk-search closeout, CI verified, C1 gate held — 2026-10-31

- Publish **73 immutable C0 source-terminal dispositions**: 22 positive Project/REE leads with 13 case-level six-gate reviews; 40 records without project-scoped REE product proof in the searched sources; 2 Benmara South exclusion from a different deposit's TREO resource; 4 native-source identity conflicts; 5 indexed WAMEX source rows requiring 4 government PDF originals.
- Wemen historical production now verified by Victorian government 2003/04 Statistical Review (issued April 2005): Wemen mineral sands mine ceased production in January 2004; prior 'catalogue-only' finding superseded.
- Preserve 204 official tenure source-title intersections, 60 source points with intersecting tenement layers, 20 exact documented title-number matches across 12 cases. No automatic project footprint or C1 promotion.
- Maintain explicit source/release separation: P1 source research closure does not approve project identity, current REE resource, GIS_RELEASE or criteria panel. All new C1 gates stay HOLD; `main` untouched.
- Original CI failure was due to GitHub account $0 Action budget blocking private-repository runners (confirmed in user-provided GitHub annotation and Billing screenshot). Switching repository to Public restored standard GitHub-hosted runners. Fixed two actual CI regressions: 48-parent Aileron resource-test expected two statements instead of four (two TREO 2025, two Nb2O5 2026), and two source-summary generator strings were out of sync with frozen provenance JSON. All four PRs now have passing actual P0/P1, Python and R workflows; record 14 successful workflow run IDs and commit heads in [CI verification attestation](audits/2026-10-31_p0_p1_ci_verification.json). PR #26→#27→#28 merged into main; PR #31 is the final closeout change. Primary WAMEX originals and formal C1 remain separate outstanding tasks #30/#32.
- Add standard-library closeout generator, unit tests and workflow, editable source CSV and JSON, final report and index.


## P0 P1: complete 73 target documentary audit and frozen 487 official-tenure reuse — 2026-10-31

- Audited all **73 P1 source IDs** into 44 distinct documented cases (25 proposed parents + 19 scope/index cases): 22 source rows with project/resource textual leads, 39 sources with only historical/geological/HM or non-REE product proof, 2 Benmara South scope exclusions, 4 sources with identity conflict, 5 indexed WAMEX report sources (four unique report IDs incl. Tutunup West A109188) lacking archived government PDF bytes, 1 catalogue-only source.
- Added 12 scoped resource claims (Y₂O₃ Korella version conflict, V₂O₅ Benmara South vs excluded Barkly TREO, Nowie THM, etc.) without modifying prior 14 resource entries.
- Reused **official polygon intersection inventory** from nationwide 487 targets: 73 P1 sources yield **204 official tenure intersection records**, 60 source rows with at least one tenure overlap, 11 with none in queried layers, 2 without verified official state layer. In 18 document-title cases, 20 source rows in 12 cases match documented tenement numbers.
- Distinguish tenement overlap from mining Project development footprints; flag Ambergate E70/4799 vs observed E70/4793, Jurien M70/436 within named M70/434–436, expired historic WAMEX titles and Wingellina SA cross-border.
- Reproducible standard-library Python, CSV and JSON source/tenure reconciliation, regression tests and README indexes. Formal Project/JORC/GIS Project footprint/C1 admissions remain 0.


## P0 P1: provisional 48-source / 25-parent identity and resource-basis review — 2026-10-31

- Freeze 48 named source candidates from prior 73-row P1 scope; publish 39 distinct state/name site keys and 25 pinned provisional parent review groups. Preserve all native target IDs, coordinates and source hashes; never create formal project_master IDs by name.
- Record project/deposit documentary scopes (Copi North, Tower, Mia, Yttria, Aileron Green/Emily/Crean, Redlings) and distinguish them from state/tenement polygon overlap (0 physically tested).
- Publish 14 resource claims: 10 historical TREO grade rows including nested cutoffs, reported totals and undated conflicting versions, 2 HM basis rows, and 2 April 2026 Aileron Nb₂O₅ MRE rows. Current niobium MRE 120Mt at 0.77% Nb₂O₅ supersedes prior niobium tonnage but does not imply current TREO grade; no cross-basis transfer. Record resource date, cutoff, reporting category and no-sum rule.
- Flag broad historical Willandra West/East source spreads and Fraser Range–Salazar adjacency. No new C1/JORC approvals.
- Add reproducible Python QA, regression tests, report and README index. Work continues in a stacked draft PR pending CI and official polygon evidence.


## P0 sixth-round source audit: 70 records with no supplemental document — 2026-10-31

- Audit all **70** frozen native source targets from the preceding 109-row source review, keeping project/deposit/occurrence and raw ID distinct; publish editable 70-row review, 59-row non-candidate parent queue, provenance SHA manifest and 25-name source document register.
- **34** targets gain external source/locator context (7 independently named historic Project/deposit candidate links; 4 indexed original-WAMEX government-held reports awaiting primary PDF; 8 Project/tenement/state scope holds; 15 only geological or non-REE primary commodity evidence). **36** still have no new independent external document.
- Explicit government and issuer evidence for Mt Clere/Tower, Tiwi/Puwanapi, historic VIC Ouyen/Galileo–Mercury–Titan, Jurien, WAMEX Hopelands East/Hassell Beach/Witchcliffe; separate HM/THM from TREO resources. No Project/JORC/C1 admission.
- Flag two `SA` Wingellina source rows west of 129°E as jurisdictional mismatch candidates; preserve existing source state pending official cadastral verification. Keep Benmara South historical EL6836 vs 2023 Barkly resource scope unresolved.
- Add `scripts/audit_p0_70_project_parents.py`, `tests/test_p0_70_project_parents.py`, and GitHub Actions snapshot regeneration. README, docs index, runbook, decision log and changelog updated; original 487/272/156/109 inventories and MCDA unchanged.


## P0 fifth round: audit 109 original-only source targets — 2026-10-31

- Verify **all 109 source targets** previously lacking independent Project parent text; preserve stable IDs, frozen original government source-feature location and SHA-256. Generate **109-row editable audit**, **89-row pending parent/identity queue** and statistics with input hashes.
- Curate 31 official/government/issuer/CSIRO documentary source names matched to **39 target rows**: **20 historical Project parent candidates**, 8 scope/tenement/name holds plus **2 Ambergate spatial conflicts**, and **9 independently documented geological or HMS deposits still lacking a Project parent**. **70** rows remain government-native-only; zero formal Project/JORC/C1 approvals.
- Check cross-source same-state names: **44** same-state-name source rows, **42** with comparable native coordinates, **38** with a source match ≤1km, and **2 Ambergate records 38.738km apart** quarantined as identity conflicts. Never infer unique Projects from matching names or coordinates alone.
- Publish reproducible standard-library `scripts/audit_p0_109_project_parents.py`, unit tests and auto-publishing GitHub Actions, plus 2014 CSIRO source scope (Twelve Mile/Prungle), ASX Yttria/Mia, WA EPA Happy Valley and issuer Governor Broome/Ambergate leads.
- Update README, docs index, runbook, research decisions and changelog without modifying C0/C1 primary source matrices, approved GIS, JORC or MCDA.


## P0 fourth-round audit of 156 Project-parent gaps — 2026-10-31

- Review **all 156** frozen native source IDs previously tagged `PROJECT_PARENT_UNLOCATED` using 2026-10-29 source-feature attributes, direct government records, typed deposit/prospect/occurrence status, REE commodity context and same-state duplicate-name relationships. Produce a **156-row editable CSV with per-row trace and source SHA**, a **148-row pending Project relation queue**, and a structured JSON provenance manifest.
- Add **11** government/issuer Project documentation leads: **8 named Project candidates**, **3 similar-name/scope holds**; the other **145** have no newly sourced named Project documentation. Cross-source same-state names occur in **70** source rows and cannot alone establish either Project membership or a JORC statement.
- Distinguish existing C0 geological records (including WA Prospect/Occurrence/Target/Infrastructure and TAS `RESOURCES=N`) from a true development Project. Keep all 156 Project boundary signoffs and C1 gates pending.
- Introduce standard-library reproducible `scripts/audit_p0_156_project_parents.py`, independent regression tests and auto-generating GitHub Actions workflow. No changes to the underlying 272/487 target snapshots, MCDA scoring, GIS or resource database.
- Update README, documents index, runbook, research decisions and changelog.


## P0 third round: 272 original-source entity / Project parent reconciliation — 2026-10-31

- Recovered and source-byte verified original GA AIMR JSON chunk, original SA critical REE CSV and 16 Legacy historical source rows; **23/23 previously missing native records** tied to physically archived original source bytes or original repo bytes.
- Independently rejoined **272/272** frozen 2026-10-29 source native features, retaining source key + native value + raw source feature locator and SHA (no auto Project or MCDA admission).
- Identified all **10 SA source feature rows** as two deposits Olympic Dam (4 rows) / Clarke (6 rows) with unique `source_key + MINDEP_NO + OBJECTID`. Not ten separate development projects.
- Added **13 source-target Project parent documentary leads** across seven different parent names (Redlings / Aileron / Coburn / Fraser Range / Glenaladale–Fingerboards / Copi / Korella); joined six existing prior reviewed relations. Final 272 queue: 15 REE-relevant document candidates, four non-REE project source rows, 92 non-project geological source entities, two parent deposit IDs, three VIC generic thematic labels, 156 unresolved parents.
- Original bytes stored under `data/raw_snapshots/2026-10-29/`, full 272 frozen native feature subset under `data/source_snapshots/`; evidence CSV, manifest and audit report under `docs/audits/`. All approval gates unchanged.
- Rebuild script + automated source artifact GitHub Actions + tests integrated; documentation index, README, runbook and research decisions revised.


## P0 original government source restoration and Project entity scope — 2026-10-31

- Retrieved October 29 raw-first government archive (GitHub Actions run 40821122179) and linked **all 272 previously native-only targets to a unique raw government feature**; retain 268 source records with no Project parent key and four with geological parent/group only as C0.
- Located the 23 prior missing source rows: 7 GA original JSON byte positions and 16 previously stored Legacy Census lines, with exact nonblank historical project_id UUIDs matching frozen Legacy target IDs.
- Identified Olympic Dam's 4 and Clarke's 6 source features by `MINERAL_DEPOSIT_NO + OBJECTID/FID`, preventing 10 duplicate observations from inflating the Project or Deposit count.
- Separated six cross-source Project parent candidates (Narraburra/Milo REE; Peculiar Knob/Carrapateena not documented as REE Projects); formal C1 still requires separate document and role approval.
- Added source raw SHA verifier, regression tests, four editable review CSV files, audit report and reproducibility summary; updated README, Runbook, decisions and file index.
- No changes to official C1/Resource/GIS approvals, v2 scoring or MCDA results.


## P0 487-record evidence source recovery (round 2) — 2026-10-31

- Re-audit all 487 preserved target IDs against 62 curated government, issuer and historical geological source leads; produce a **34-column editable evidence snapshot**, a separate **86-target before/after CSV** and provenance JSON.
- Reduce `NATIVE_RECORD_ONLY` **336→272** (64 additional cross-source leads) and `SOURCE_RECORD_NOT_RECOVERED` (no native/document locator) **23→3** (20 new external document locators). **All 23 native raw snapshots remain unrecovered**, kept explicitly separate from document discovery.
- Add official SA deposit evidence for Olympic Dam and Clarke; both **original multi-feature native ID ambiguities remain unresolved** (4 and 6 source rows) although they now have official references.
- Preserve all C0 source records and existing C1/Project/JORC/GIS approval gates. New reproducible standard-library script and regression tests prevent accidental promotion and historical-file overwrite.
- Update README, docs index, runbook, research decisions and changelog. No scoring or historical source modification.


## P0 source evidence review for all 487 records — 2026-10-31

- Audit all 487 Census targets at **claim/evidence depth**, distinguishing exact native source record, archived document text locator, URL without locator, ambiguous native match and unrecovered source; record evidence scope and next action without Project/JORC/GIS approval.
- Add `scripts/review_p0_487_evidence.py` and regression tests to reproduce a 487-row editable CSV and byte-level source SHA-256 run manifest.
- Extract 20 WA Government 2026-02 REE project/resource summary entries with 2026-01 staging and JORC aggregate grades: exact same-name crosswalk gives 13 government names / 20 Census source rows, including previously ungrouped advanced projects.
- Add NT 2023 Bruce Project → Plenty River prospect primary-source parent relation for review (not automatic merge).
- Add research report and structured source review/QA files under `docs/audits/`; update README, docs index, runbook, implementation plan and research decisions.
- No changes to historical 487 records, approvals, active GIS, JORC database or MCDA scoring.


## P0 complete 487-source batch audit — 2026-10-31

- Join **all 487 frozen Census source targets** by original `target_id` from identity, evidence/locators, source recovery, official tenure, company roles and the 39 reviewed-group screen.
- Publish an **editable 39-column, 487-row CSV**, machine-readable QA/statistics with Git blob provenance and a versioned report in `docs/audits/`.
- Add Python standard-library builder `scripts/build_p0_census_487_audit.py` and regression tests for exact 487-row coverage, stable Project/Deposit level, cohort lineage, no automatic C1 approvals and non-overwrite of released snapshots.
- Summarize 323 deposit, 102 occurrence, 50 source Project, 6 prospect and 6 historical source records; 78 linked to 39 review groups, 409 unlinked; external title spatial overlap is not legal ownership.
- Update README, docs index, Runbook, Implementation Plan and Decisions. **No Project/MRE/GIS independent approval, legacy source edits or MCDA calculations.**


## P0 individual Project source screen — 2026-10-31

- Source-check 39 frozen review Project groups against public government/company/issuer evidence and write editable `docs/audits/2026-10-31_project_source_screen_39.csv`, methodology report and provenance manifest.
- Summarize state distribution and 6 screening classes: 7 study documented, 8 study/FID recheck, 14 resource/exploration, 7 REE-role HOLD, 2 outside pre-FID, 1 on-hold activity.
- Flag post-cutoff 2026-10-30 Northern Minerals report as supplemental only; identify time-sensitive Jupiter JORC/Scoping update, Dubbo ASM acquisition, Nolans/Balranald FID, and THM/MzEq versus TREO basis.
- Document the proposed `C1_DIRECT_REO` vs `C2_HMS_REE_COPRODUCT` comparison split **as a pending scientific decision**, not a changed eligibility rule.
- Update README, docs index, implementation plan and research decisions; preserve all original sources and approval gates. **No** SQLite migration, Python/R code, score, population identity or published release altered.


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

## 2026-10-31 — P0 412 HOLD provenance/Gate continuation

- 完整保留 412 筆 target IDs，與 P1 73／P2 28 分離，產出 P3 216 Deposit/Prospect 與 P4 95 Occurrence 的 311-row 來源追溯工作表；本輪僅完成 provenance triage。
- 13 個正向案例（22 source rows）跨接原始 Gate、P1 Case、JORC basis、來源紀錄，確認正式 Project/JORC/GIS/C1 0 核准且全部留 HOLD。
- P2 28 source／27 cases 補上 Legacy/native source crosswalk 與歷史範圍旗標；不擅自合併同名及不同時點來源。
- 新增可重跑 Python、unit test 與 GitHub workflow；README 和研究索引同步更新。

- P3/P4 與 2026-10-29 政府原生 272-feature JSONL 做逐筆 ID/source/native SHA 回查：194/311 精確交叉核對，0 不一致，117 不在此 272 子快照內；新增自動 QA。

## 2026-10-31 — Reconcile legacy 487 priority P2 72 and original HOLD P2 28

- 合併原 PR #33 的 72-row／47 case source intake、7 dated documentary leads（涵蓋 22 sources）及 stdlib Python 重建。
- 以 source ID 建立 72-row priority crosswalk：28 原 412 HOLD P2、38 INCLUDE_CANDIDATE、6 HOLD_REE_ROLE；不得重複相加。
- 保留 2026-10-29 as-of、研究 C1/JORC/GIS 0 核准；補強 README／決策紀錄、測試、CI。
