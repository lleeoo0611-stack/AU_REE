# 文件索引

由 [根目錄 README](../README.md) 開始。主 README 只保留目標、現況與基本執行方式；細節依用途查閱下列文件。歷史報告與快照以**原始日期及路徑**保存，以免破壞證據溯源。

## 現行研究規格與操作

| 文件 | 內容 |
| --- | --- |
| **[Research Architecture v2.0](RESEARCH_ARCHITECTURE.md)** | **後續研究總規格**：A/B/C、C0–C3、六構面與階段 Gate |
| [P0.1 C1 Cohort Admission](P0_COHORT_SELECTION_PROTOCOL.md) | 六層納入規則、Stage、JORC 與 12/9 指標候選 Panel |
| [P0.2 Project–Deposit–JORC Schema](P0_PROJECT_RESOURCE_SCHEMA.md) | 既有資料表映射、JORC resource statement 欄位和防重複計算 |
| [P0 Cohort Readiness Audit](audits/P0_C1_READINESS_2026-10-31.md) | 2026-10-29 凍結資料的 487/39 盤點、待審訊號與輸入缺口 |
| [39 Project 來源驗證與母體分布](audits/2026-10-31_project_source_screen_report.md) | 逐專案 Stage／REE 資源比對、州別與階段分類、C1 判定問題 |
| [39 筆可編輯 Source Screen CSV](audits/2026-10-31_project_source_screen_39.csv) | 既有候選 ID 與 disposition、公開來源、研究階段及審查缺口 |
| **[487 全量來源與母體分布審查](audits/2026-10-31_census_487_batch_review_report.md)** | **487 target 全覆蓋**：州別、地質實體、Project 關聯、Tenure／來源定位與下一步 |
| [487 筆可編輯 Census CSV](audits/2026-10-31_census_487_batch_review.csv) | 精確 ID join 的 39 欄逐筆更新／審查矩陣 |
| **[487 筆證據核查報告](audits/2026-10-31_487_evidence_review_report.md)** | 原始證據層級 487 筆、官方 WA 20 個資源線索、NT Project–Prospect 父子關係 |
| [487 筆 Evidence Claim CSV](audits/2026-10-31_487_evidence_claim_review.csv) | 維持原始來源 ID 的逐筆證據強度、URL/頁碼、缺口與 C1 Gate |
| **[487 筆來源證據第二輪複核](audits/2026-10-31_evidence_round2_report.md)** | **86 筆新外部來源／文本定位**，保留 native ID 與 Project 核准狀態 |
| [487 筆第二輪完整 CSV](audits/2026-10-31_487_evidence_round2_review.csv) | 原始 + 新證據類別、網址／頁碼、原始 ID 是否真正恢復 |
| [86 筆證據變動 CSV](audits/2026-10-31_evidence_round2_changed_targets.csv) | 複核前後逐筆差異，適合作為下一輪人工核准佇列 |
| [WA 政府 2026 REE 資源清單](audits/2026-10-31_wa_official_ree_project_leads.csv) | 20 個官方名稱、2026-01 resource/stage、待審查 JORC basis |
| [487 Census batch QA Summary](audits/2026-10-31_census_487_batch_review_summary.json) | 來源 Git blob 版本、欄位與分類計數 |
| [Data Specification](DATA_SPECIFICATION.md) | Project–Deposit–Resource、JORC、Evidence、Snapshot schema |
| [MCDA Protocol](MCDA_PROTOCOL.md) | 固定評分尺度、依賴審查、AHP/Scenario、六構面比較 |
| [Validation Protocol](VALIDATION_PROTOCOL.md) | B1–B4、SMAA、C1/C2/C3 driver／歷史驗證 |
| [Implementation Plan](RESEARCH_IMPLEMENTATION_PLAN.md) | P0–P3 模組修改順序、驗收、PR／決策紀錄 |
| [P0–P3 工作追蹤 Issue #14](https://github.com/lleeoo0611-stack/AU_REE/issues/14) | 後續 PR、驗收證據與每階段工作完成狀態 |
| [A/B/C 研究需求](RESEARCH_REQUIREMENTS_AIMS_ABC.md) | 與 v2 Protocol 配套的模組待辦及測試清單 |
| [2026-10-30 專案評估](PROJECT_ASSESSMENT_2026-10-30.md) | 方法學、資料品質、研究進度及下一個里程碑 |
| [操作指令](RUNBOOK.md) | Python、GIS、R、更新、測試及審閱工作包 |
| [研究決策](RESEARCH_DECISIONS.md) | r983 研究母體、計量與資料驗證原則 |
| [Git 工作流程](GIT_WORKFLOW.md) | 分支、版本與快照保存 |
| [變更紀錄](CHANGELOG.md) | 程式／規格／文件變更摘要 |
| [Project Master 規則](SCHEME_A_PROJECT_MASTER.md) | Project–Deposit 身分與 Scheme A |
| [官方來源清單](official_population_sources.md) | GA 與州來源及查詢說明 |
| [Raw-first protocol](NATIONAL_RAW_FIRST_PROTOCOL.md) | 政府資料先全量再篩選的步驟 |

### 本輪新的 Project–Deposit 關聯證據

| 檔案 | 用途 |
| --- | --- |
| **[P0 第三輪總報告](audits/2026-10-31_p0_native_parent_resolution_report.md)** | 272/272 原始資料、23/23 原始 bytes、南澳 10 筆完整 source feature 鍵 |
| [272 筆 Parent Evidence Queue](audits/2026-10-31_272_project_parent_evidence_queue.csv) | 15 筆 REE Project parent 候選、4 筆非 REE Project、其餘依證據分類 |
| [272 筆政府原始欄位](../data/source_snapshots/2026-10-29_272_native_features.jsonl) | source feature attributes、原始 SHA、原始 ID |
| [13 筆新文件關聯](../inputs/source_review_20261031/round3_272_project_parent_issuer_leads.csv) | Redlings、Aileron、Coburn、Copi North、Glenaladale、Korella 等 |
| [Project Parent Summary](audits/2026-10-31_272_project_parent_evidence_summary.json) | 各類別計數與正式 C1 Gate 狀態 |

### 156 筆待建立 Project 母層的來源稽核

| 檔案 | 用途 |
| --- | --- |
| **[P0 第四輪證據審查](audits/2026-10-31_156_project_parent_review_report.md)** | 156 筆逐列原始與政府／公司文件查證結果 |
| [156 筆 Evidence Audit CSV](audits/2026-10-31_156_project_parent_evidence_review.csv) | 原生 id、status、礦種、source URL/locator、Project 文獻與核准 Gate |
| [148 筆待補 Project 關係](audits/2026-10-31_156_project_parent_gaps.csv) | 官方 Project boundary 與來源文件之待查佇列 |
| [11 筆官方／公司具名文件](../inputs/source_review_20261031/round4_156_official_parent_documents.csv) | 8 具名、3 名稱相近待查的有效日期與主張 |
| [156 Audit Summary](audits/2026-10-31_156_project_parent_evidence_summary.json) | 州別、證據類別及輸入 SHA-256 |

### 109 筆來源 Project 歸屬證據審核

| 檔案 | 用途 |
| --- | --- |
| **[109 筆審核報告](audits/2026-10-31_109_project_parent_review_report.md)** | 20 歷史 Project parent 候選、10 範圍 HOLD、9 獨立 Deposit 資料 |
| [109 筆 Evidence Review CSV](audits/2026-10-31_109_project_evidence_review.csv) | source-native ID、礦種、原始 SHA、文件定位、同名距離與 C1 Gate |
| [89 筆 Project 關係缺口 CSV](audits/2026-10-31_109_project_evidence_gaps.csv) | 有範圍問題、僅有礦床證據或尚無外部文件 |
| [31 個來源文件名稱線索](../inputs/source_review_20261031/round5_109_documented_project_deposit_leads.csv) | ASX、WA EPA、CSIRO 歷史 Project 與 geological-only claims |
| [109 證據統計與來源指紋](audits/2026-10-31_109_project_evidence_summary.json) | 跨來源同名座標、稽核結果與 SHA-256 |

### P0 P1：412 HOLD 的 73 筆母層優先查核

| 文件 | 用途 |
| --- | --- |
| [P1 73 筆審核報告](audits/2026-10-31_p1_parent_identity_report.md) | 48 Project 候選、4 WAMEX 索引、21 身分/範圍 HOLD 的來源分級與重要結論 |
| [P1 73-row Evidence CSV](audits/2026-10-31_p1_parent_identity_review.csv) | 原始 source ID、SHA、證據 URL/locator、逐筆下一步與維持 HOLD 的 Gate |
| [25 筆定向來源複核](../inputs/source_review_20261031/p1_parent_identity_web_checks.csv) | 來源原文、二手索引、原生空間 QA 的分級與證據主張 |
| [P1 QA JSON](audits/2026-10-31_p1_parent_identity_summary.json) | 互斥分類、source snapshot 與數量驗證 |

### P0 第六輪：70 筆資料重新來源驗證

| 文件 | 用途 |
| --- | --- |
| **[70 筆完整來源審核報告](audits/2026-10-31_70_project_parent_review_report.md)** | 歷史 Project parent、REE/HM 基準、州界／tenure scope 檢查 |
| [70 筆 Evidence Review CSV](audits/2026-10-31_70_project_evidence_review.csv) | 每列原生 ID、SHA、技術文獻來源、日期／locator、正式 Gate |
| [59 筆無具名歷史母專案候選的證據待查](audits/2026-10-31_70_project_evidence_pending.csv) | 需額外 Project 原件的樣本；全部 70 仍未正式 Project 核准 |
| [25 筆政府／公司與歷史 WAMEX 來源名稱](../inputs/source_review_20261031/round6_70_official_issuer_document_leads.csv) | 34 個來源列有補充文件；WAMEX 二手索引單獨標示 |
| [70-row Evidence Summary](audits/2026-10-31_70_project_evidence_summary.json) | 州別、證據升級、原始 SHA 與跨州邊界 flag |

## 原始來源恢復與實體審查（2026-10-31）

| 檔案 | 用途 |
| --- | --- |
| **[政府原始封存審查](audits/2026-10-31_original_archive_recovery_report.md)** | 272/23/SA 重複 feature 真實來源的分層判定 |
| [272 筆原生證據矩陣](audits/2026-10-31_272_native_project_scope_triage.csv) | target、source-native ID、原始封存路徑、地質 parent 與 C1 Gate |
| [23 筆原始來源恢復](audits/2026-10-31_23_native_source_recovery.csv) | GA 7 筆原始圖徵及 Legacy 16 筆歷史列定位 |
| [南澳 10 筆 feature 對照](audits/2026-10-31_sa_10_duplicate_source_features.csv) | Olympic Dam 4 筆、Clarke 6 筆，保持兩個礦床 ID |
| [6 筆外部 Project parent 候選](audits/2026-10-31_272_project_parent_candidates_6.csv) | Narraburra/Milo REE 及 Peculiar Knob/Carrapateena 非 REE scope |
| [原始來源 QA 摘要](audits/2026-10-31_original_archive_recovery_summary.json) | 所有數量、原始 Actions artifact、驗證程式 |

## 母體與審閱成果（歷史報告）

- **主要當前報告**：[487 筆追溯發布摘要](../CENSUS_RELEASE.md)、[2026-10-30 逐列審閱](FULL_TRACE_REVIEW_20261030.md)（內容相同，保留原引用路徑）。
- **政府來源與篩選**：[全澳 Raw + E1/E2/E3 結果](NATIONAL_RAW_AND_SCREEN_RESULTS_2026-10-29.md)、[全澳去重](NATIONAL_REE_CENSUS_DEDUP_2026-10-29.md)、[1006 筆證據縮減](EVIDENCE_BACKED_1006_REDUCTION_2026-10-29.md)。
- **487 筆分析前審閱**：[Census review](census_487_pre_mcda_review_2026-10-29.md)、[完整裁定摘要](FULL_487_CENSUS_ADJUDICATION_2026-10-29.md)、[重現 86+401 的選取規則](REPRODUCED_86_401_SELECTION_RULES.md)。
- **Tenement/Company/State**：[逆向追溯](REVERSE_TENEMENT_COMPANY_487_2026-10-29.md)、[NT 來源列追蹤](NT_STATE_ROW_TRACE_2026-10-29.md)、[487 重建指令](census_487_run_instructions_2026-10-29.md)。
- **測試與品質**：[v1.0.1 測試報告](TEST_REPORT_v1.0.1_2026-10-29.md)、[workpack 品質說明](../reproducibility/README_QUALITY_AND_ENTITIES.md)。

## 研究輸入、快照與歷史

- [`inputs/`](../inputs/)：legacy、候選身分決策、獨立 evidence approvals；原始資料不因重跑而覆寫。
- [`outputs/`](../outputs/README.md)：追溯審閱 CSV、候選／證據／持權鏈與品質輸出。
- [`artifacts/`](../artifacts/)：可攜、已遮蔽的發布快照。
- [`docs/snapshots/`](snapshots/)：帶日期的機器可讀 manifests；保持原路徑。
- [`docs/archive/`](archive/)：舊版 README、先前規格；[r983 README](previous_r983_modular_README.md) 保留作歷史比較。

**資料集合不可混為一談**：legacy 203、凍結 G0 19、1,006 來源候選、487 個固定審閱目標均有不同定義。審閱狀態不代表已核准 Project 或可正式排名。
