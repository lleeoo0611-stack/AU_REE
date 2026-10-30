# Research Implementation Plan — v2 Research Gates & GitHub Workflow

**目的：**讓每一次後續資料庫、GIS、MCDA、統計與論文輸出變更，都可對照 [RESEARCH_ARCHITECTURE](RESEARCH_ARCHITECTURE.md) 的 A/B/C 研究目標，不因局部解決某個腳本錯誤而破壞其他研究功能。

**目前狀態：**只將 v2 契約納入版本控制；本次**不修改**既有 Python/R/SQLite scripts、不調整 v1 eligibility/weights、不產出正式排名。v2 實作仍需逐 Gate 的獨立 PR。

## 1. 單一規格入口

| 優先 | 文件 | 約束 |
| --- | --- | --- |
| 0 | [Research Architecture](RESEARCH_ARCHITECTURE.md) | A/B/C、Project 研究單位、C0–C3、Release Gates |
| 1 | [Data Specification](DATA_SPECIFICATION.md) | Project–Deposit–Resource、證據、日期、JORC、DB lineage |
| 2 | [MCDA Protocol](MCDA_PROTOCOL.md) | 六構面、固定效用、AHP、Scenario、方法比較 |
| 3 | [Validation Protocol](VALIDATION_PROTOCOL.md) | Aim B1–B4、SMAA、Aim C1/C2/C3 與統計規則 |
| 4 | [A/B/C Detailed Requirements](RESEARCH_REQUIREMENTS_AIMS_ABC.md) | 詳細模組待辦與測試清單 |
| 5 | [Research Decisions](RESEARCH_DECISIONS.md) | 歷史決策、尚未核定參數與往後變更證據 |

**定義衝突時**：現行 `config/`、`R/run_mcda.R`、`src/au_ree/` 等記錄 **v1 行為**；v2 契約指定 **預期行為**，尚未正式實作/驗證前不得假裝已經遷移。要偏離研究契約，先提出 decision record、理由和測試計畫，在 docs PR 核定再更新程式。

**跨階段任務與驗收追蹤：**[GitHub Issue #14 — Research v2.0 Architecture Implementation Tracker](https://github.com/lleeoo0611-stack/AU_REE/issues/14)。每項 Gate 完成時將 PR、tests、可編輯輸出、snapshot ID 與文件版本附回該 Issue，**不可僅勾選完成而沒有驗收依據**。

## 2. 開發工作包（依科學依賴排序，不以可快速完成的腳本優先）

| 工作包 | 依賴／預先決策 | 所涉路徑（預期） | 完成時的驗收成果 |
| --- | --- | --- | --- |
| **P0.1 Identity/Cohort** | 獨立 Project 定義、C0–C3、選擇偏差診斷 | `src/au_ree/stages/population.py`, `identity_policy.py`, `stages/eligibility.py`, `db/migrations/` | 保留每筆原始 ID，穩定 project_id；C1 進退原因/母體統計，未核准不自動升級 |
| **P0.2 Data Model/Evidence** | JORC/oxide basis、時間規則、missingness 分類 | `core.py`, `evidence.py`, `stages/criteria.py`, `db/migrations/`, `inputs/` | Resource statement 交叉表、來源校驗、資源不重複、撤銷核准連帶失效測試 |
| **P1.1 GIS + Criteria** | 核准點位、圖層與 12 指標 codebook、reference utility | `stages/gis.py`, `config/criteria.json`, `config/gis.json`, 擬定 `config/scoring_functions.yaml` | 固定尺度/來源記錄/基準對照；新增無關 Project 不改舊 Project 效用值 |
| **P1.2 MCDA** | C1 正式 matrix、Scenario-AHP 對應/權重與門檻核定 | `R/run_mcda.R` 或拆成 `R/analysis/`，`config/r_analysis.json`, tests | 6 domains、3 scenario 使用其**實際**權重、SAW/PROMETHEE/TOPSIS + audit |
| **P2.1 Rank Robustness** | data uncertainty 來源、correlation、ties | 獨立 R 模組、`tests/` | B1/B2/B3/B4 與 joint results，SMAA 合法機率與固定 seed |
| **P2.2 Drivers/Statistics** | Deposit/Stage codebooks、D1 double-count、有效樣本數 | 獨立統計模組 | C1 model drivers／C2 stratified associations、N、CI |
| **P3 Historical** | published-as-of snapshot、event definition、觀察窗 | SQL historical views、回測模組 | 無時間洩漏、已標明右設限的 historical output |
| **P3 Publication** | 所有主要 Gates PASS | export/report scripts，`docs/`、`reproducibility/` | 可編輯 CSV、SVG、GeoPackage、manifest、方法附件、README 進度更新 |

**不在工作包未完成時修改其他工作包定義。** 允許用 synthetic fixtures 開發模組，但應明確標示 `SYNTHETIC`；正式 Project 數值另待審核。

### P0 Cohort/Data 審查階段成果（2026-10-31）

- [C1 Cohort Protocol](P0_COHORT_SELECTION_PROTOCOL.md)：固定六層 `ID/ROLE/WINDOW/JORC/PANEL/GIS_RELEASE` 的草案，擬定 12 準則與 9 準則兩套**待核定**的固定 panel 候選。
- [Project–Deposit–Resource schema](P0_PROJECT_RESOURCE_SCHEMA.md)：對照既有 `core.py`、`db/migrations/0004–0009`，設計 resource statement/oxide/date 的增量關聯和測試，**尚未新增 migration**。
- [初步盤點](audits/P0_C1_READINESS_2026-10-31.md) 與 [39 群組 CSV](audits/2026-10-31_c1_review_groups.csv)：保留全部候選原決策與 Stage 訊號；沒有正式可核准 C1 排名。
- 可編輯輸入模板：[Project Gate](../inputs/templates/c1_project_gate_review_template.csv)、[JORC Statement](../inputs/templates/jorc_resource_statement_review_template.csv)。**下一步先補實體來源與審核，然後核定 Panel/C1 再寫 migration**。

## 3. 後續每個 PR 的最低要求

請使用 [GitHub PR Template](../.github/pull_request_template.md) 並填寫：

1. **目標**：對應 Aim A/B/C、P0–P3 與 Gate，明確列出現有行為和預期行為。
2. **來源**：變更原始資料時交代 document/source、日期、SHA-256、review status；只改演算法時明確說明無原始數據變更。
3. **結構/方法變動**：資料表欄位、遷移、cohort、criterion、utility、weights、rank/ties/uncertainty 的版本與決策紀錄。
4. **兼容性**：保留舊 `project_id`、snapshot IDs、原始 source hash、舊版 `G0/R1/S1/RS` 語意；若不可相容，記錄轉換關係及影響。
5. **測試**：Python regression、R synthetic test、新增功能的接受性/反例測試；宣稱正式研究結果前先驗證 evidence and release gates。
6. **文件**：同步更新 README（簡述狀態）、相應 Protocol（規格變動才更新）、`docs/CHANGELOG.md`、`docs/RESEARCH_DECISIONS.md`；不重複堆疊新的 README 副本。
7. **可重現性**：對分析結果保存 `dataset_snapshot_id`、`git_sha`、`cohort_version`、`criteria_version`、`weight_version`、`model_version`、`seed`、輸入/輸出 SHA。
8. **判定**：該 PR 的 Gate 為 `PASS`／`PARTIAL`／`BLOCKED`，及尚未完成的資料依賴。

不能因 PR tests 全 PASS 就宣稱研究級結果；CI 可檢驗程式功能，**來源審核和主母體條件**仍需資料驗收。

## 4. 給未來工作的研究決策格式

新增重大決策時，於 [RESEARCH_DECISIONS](RESEARCH_DECISIONS.md) 的 v2 Decision Log 新增一列（不可改寫既有 r983 歷史紀錄）：

| 欄位 | 要求 |
| --- | --- |
| Decision ID / Date | 例如 `ADR-2026-001` + YYYY-MM-DD |
| Status | `PROPOSED` / `ACCEPTED` / `SUPERSEDED` |
| Scope | Cohort / Entity / Evidence / Criteria / Weight / Uncertainty / Validation |
| Rationale | 地質/統計科學理由與替代方案 |
| Affected version | schema/config/criteria/method + old/new |
| Impact / Tests | 受影響 Aim、測試與快照、是否改變歷史結果 |
| Approval | 審查者與核定日期 |

**待核定的關鍵參數**不以假設數值代替：C1 required criteria、參考尺度與 cutoff、Ordinal T1/T2/C1–C3 codebook、三組 AHP 判斷、PROMETHEE thresholds、B2 distributions/相依結構、SMAA tie policy、Aim C sample-size/statistical plan。

## 5. Gate 狀態（本次寫入時）

| Gate | Spec | Implementation | Research Output |
| --- | --- | --- | --- |
| P0 Cohort/Data | **documented, parameters pending** | v1 basics exist; v2 schema pending | Not released |
| P1 Full six-domain | **documented, parameters pending** | v1 G0/R1/S1/RS + R engine; v2 not implemented | Not released |
| P2 B/C | **protocol documented** | weight-only MC and LOO exist; joint/SMAA/drivers pending | Not released |
| P3 Historical | **protocol documented** | pending | Not released |

**下一個可執行的研究工作**：先針對 C1 的 required criteria／樣本 coverage 審查，並鎖定 Project–Deposit–JORC Resource Statement 欄位。完成該決策後再啟動對應 P0 migration PR。此順序直接服務 Aim A/B/C 的研究驗證。
