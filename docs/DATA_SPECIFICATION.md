# Data Specification v2 — Australian REE Research Database

**文件角色：**資料欄位、身份、JORC basis、時間與可追溯性之契約。  
**狀態：**設計規格；下列新表是**擬定資料結構**，尚非現有 SQLite schema。須以 additive migration 與映射測試實作。主契約：[RESEARCH_ARCHITECTURE](RESEARCH_ARCHITECTURE.md)。

## 1. 原則與 ID

- 來源的 `source_key/native_id`、`original_value/unit/basis`、原始材料及 SHA-256 **唯讀保存**。採 `project_id` 穩定識別，任何候選合併／拆分需保留 `supersedes/merged_from/decision_id`，不得以排名順序或名稱臨時生成新正式 Project ID。
- 多來源同名或距離相近僅建立 review link；不自動合併。Entity types：`PROJECT`、`DEPOSIT`、`PROSPECT`、`TENEMENT`、`OCCURRENCE`、`COMPANY`。公司法律權利與營運／提案／規劃權利分開。
- 每一個有意義的值都應追溯到 **source → document/evidence → scoped observation/resource statement → normalized criterion → analysis run**。
- 新資料庫是原有 `src/au_ree/core.py` 及目前 census/trace 工作包的**統一目標 schema**。不建立與正式 pipeline 並行且規則不同的另一套「權威 Project DB」。

## 2. 擬定的關聯結構

| Logical table | 主鍵與核心欄位 | 連結／驗收 |
| --- | --- | --- |
| `project_master` | PK `project_id`, canonical name, state, lifecycle snapshot | 保留現行 ID，project identity 需獨立核准 |
| `deposit_master` | PK `deposit_id`, deposit type, mineralogy, source | Deposit 不自動成為 Project |
| `project_deposit_links` | PK `link_id`; `project_id`, `deposit_id`, relation role, valid_from/to, approval | 支援多對多，避免任意複製資源量 |
| `tenement_master` / `project_tenement_links` | jurisdiction, native tenement ID, holder, dates, evidence | Tenement≠Project；礦權變更須時間化 |
| `company_entities` / `project_company_roles` | company ID, relation role (legal holder/operator/developer/proponent/proposed buyer), interest, effective dates | 各角色不得由同名推斷 |
| `source_documents` | PK `document_id`, URL, publisher, publication_date, fetched_at, original SHA-256, archive path, license | URL/摘要本身不構成主張證據 |
| `evidence_approvals` / `evidence_links` | reviewer, decision, reviewed_at, document and scoped record reference | `VERIFIED` 欄位不是獨立核准 |
| `observations` | `obs_id`, entity_id/type, variable, raw/normalized value, units, basis, effective/publication dates, location within source, status | 單位轉換可重算，來源不可覆寫 |
| `resource_statements` | PK `statement_id`, `document_id`, effective_date, reporting code+edition, cut-off+unit, scope, reporting basis, supersedes | 報告版本彼此不可直接加總 |
| `resource_statement_deposits` | PK (`statement_id`,`deposit_id`), scope/coverage and overlap resolution | 專案級聲明與礦床級聲明不得 double count |
| `resource_category_rows` | PK `resource_row_id`, statement ID, Measured/Indicated/Inferred/combined; ore/rock tonnage, grade and unit | 同一基礎才做 M/I/I reconciliation |
| `resource_composition_rows` | statement ID, oxide/element code, fraction/value, denominator, unit, recovery context | Nd/Pr/Dy/Tb、TREO、THM、MzEq basis 分開 |
| `project_events` | event_id, project_id, event_type, valid/effective date, publication date, source and status | Scoping/PFS/DFS/FID/financing/offtake/permit/suspension 由事件導出 |
| `project_locations` | location_id, project_id/deposit_id, geometry role, lon/lat, CRS, accuracy, date, source, approval | 項目代表點、礦床中心、礦廠位置不可交換 |
| `gis_metrics` | project_id, criterion, value, method, source GIS version, coordinate role, uncertainty, QA | 現行 EPSG:3577 直線距離僅表示 proximity |
| `missingness_records` | observation target, reason, audit decision and date | 明確區分 missing 與實際低分 |
| `uncertainty_models` | variable/scope, model type, range/distribution, evidence, parameters, correlation group, version | 不假設未知 CV；完整依據可追溯 |
| `cohort_memberships` | snapshot_id, cohort_id, project_id, include/exclude, rule version and reason | 同一日期可重建完全相同集合 |
| `criteria_values` | run/snapshot/project/criterion, value, basis, evidence IDs, normalization version, status | 禁止未核准插補進正式 C1 |
| `analysis_runs` / `run_inputs` / `run_outputs` | run_id, git SHA, snapshot, criteria/weights/method/version, seed, file hashes, QA status | 每個發表圖表有可回溯 run ID |
| `schema_migrations` | migration ID, checksum, applied_at | 不修改舊版已釋出 schema |

SQLite physical names/constraints/indices 在 migration PR 中定稿，**不得只憑本表推定已實作**。

## 3. JORC 與 REE 數值轉換

**資源分層**：Project → Deposit(s) → Resource Statement → Category Rows → REE Composition。每份 statement 必有 resource/reserve 類別、報告日期、cut-off（值及單位）、basis、reporting code/edition、原始來源定位。Mineral Resource 與 Ore Reserve 分開；Measured/Indicated/Inferred 與 Total 僅可在相同 reporting scope、cut-off、basis 下對帳。

**R1 計算示意（前提：噸位為 Mt、TREO 品位為質量百分比，且數值屬相同 statement/scope）：**

`contained_treo_kt = mineral_resource_mt × treo_grade_pct × 10`

例：100 Mt × 1.0% = 1000 kt TREO。若來源報 THM、MzEq、元素質量或不同 oxide 定義，**不直接套用**。原始 grades 與 tonnage 保留，派生值具 `formula_version`、`source_row_ids`，同一 statement 的 Total 與分項不得重複相加。R1、NdPr/TREO 比例、NdPr contained 量有代數依賴，進入權重前需做 double-count audit。

**Recovery**：區分礦石→精礦、浸出、萃取／分離和整體回收率；未提供階段定義時標記 `BASIS_UNRESOLVED`，不把單步 recoveries 當整體 recovery。

## 4. 資料時點與事件

欄位應同時保存：
- `effective_date`：礦產資源／事件適用日期；
- `publication_date`：文件實際對外公開日期；
- `retrieved_at`：系統取得時間；
- `approved_at`：研究核准時間；
- `snapshot_as_of`：分析可使用資料的截止時點。

歷史回推只接受**當時已公開**且當時適用的證據；未來公告不可倒填，即使後來說明其 effective date 更早也不能視為當時已知。後續 source correction 必須留有版本及校正紀錄。

## 5. 缺失、爭議與品質

`NOT_REPORTED`、`NOT_MEASURED`、`NOT_APPLICABLE`、`SOURCE_UNAVAILABLE`、`CONFLICT`、`REVIEW_PENDING`、`BASIS_UNRESOLVED` 為**審核原因**而非數值零；不能以空字串和 0 混用。

每筆正式 C1 值需有 `evidence_status=APPROVED`、可重建的 normalization、符合 snapshot 日期的 document 與 QA。包含需求但無可批准值時，Project 留 C2；C1 未達 release gate 則維持 `C1_NOT_RELEASED`。進入 B2 uncertainty 的分布由相應技術報告/研究數據/明訂的情境假設支撐，並保留相關性和 derived variable 一致性。

## 6. 核心資料品質驗收（後續 PR 必附測試）

1. 同一 `source_key/native_id` 重複來源不得靜默刪除；linked entities 有唯一性約束、稽核紀錄與 stable ID。
2. 同一礦床、cut-off、聲明版本的資源不得重算兩次；M/I/I 與總和對帳符合來源 rounding tolerance。
3. 改變證據審查決策（核准→撤回）後，依賴的 criterion 值、eligibility、GIS release 均重新評估。
4. snapshot as-of filtering 不讀取未來公開文獻；資料重跑可得到一致的 cohort／表格邏輯雜湊。
5. 每個輸出可向後追溯 document SHA、原始值/單位/basis、判讀位置、轉換與 QA。
6. 未核准、無法比對 basis、來源相互衝突不得發布研究級 MCDA 矩陣。

**既有輸入與已發布輸出不搬移、不覆寫：**`inputs/`、`outputs/`、`artifacts/`、`docs/snapshots/`、`reproducibility/` 的歷史檔案與 SHA 仍為可追溯來源。新增資料表以 migration 逐階段導入，並在 [RESEARCH_IMPLEMENTATION_PLAN](RESEARCH_IMPLEMENTATION_PLAN.md) 記錄 migration compatibility。
