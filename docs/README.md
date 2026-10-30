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
