# r983 重構的研究決策（2026-10-29）

| 研究問題 | Pipeline 決策 | 對應欄位／程序 |
|---|---|---|
| 專案母體完整性 | 維持 GA／各州／歷史 Legacy 多來源，來源原文與排除原因保留；非 project 實體進人工審核 | `population_candidates`, `project_master`, `project_aliases` |
| 專案與礦床層級 | Deposit / Prospect / Tenement 不自行升級為 Project | `entity_level`, `population_review_queue.csv` |
| 更新後保留 ID | project ID 一經核准就保持不變；不依排序編號 | `project_id`, `legacy_id_map` |
| 稀土資源資料語意 | TREO、THM、MzEq、magnet REO、REE mineral basis 保留原始計量定義 | `basis`、R1／S1 篩選 |
| 證據時點 | 凍結日期前的公告與資料對應評估快照 | `effective_date`, `publication_date`, `freeze_date` |
| 缺失資料 | Missing 不做零分，源證據不足或衝突保留待審核 | `criterion_values`, `coverage` |
| 開發階段可比性 | 主分析限定活躍的 pre-FID Scoping 至 DFS/BFS/Feasibility | `eligibility.json` |
| GIS 距離 | 官方資料、代表座標經核准、EPSG:3577 最近直線距離、每來源 SHA | `gis_metrics`, `gis_sources` |
| 情境穩健性 | G0 全域非 R/S、R1 嚴格資源、S1 嚴格戰略、RS 同時含兩者 | `eligibility.json`、R MCDA |
| 權重來源 | AHP 問卷為正式權重；研究假設權重獨立標示，Monte Carlo 權重擾動 | `ahp_pairs_*.csv`, `run_mcda.R` |
| 版本重現 | 程式／設定／資料快照 SHA-256 + 各階段 manifest + SQLite checkpoint | `stage_runs`, `manifest.json` |

樣本：歷史 r963 種子為 203 筆，這些母體證據不會自動認定為目前已確認的 MCDA Alternatives。正式個數由第四階段檢驗時點及證據決定。

## v2 研究架構（2026-10-31，設計契約）

依 [RESEARCH_ARCHITECTURE](RESEARCH_ARCHITECTURE.md) 採納以下**研究設計方向**；這些不會自動改動上方的 r983 歷史決策或 v1 程式：

| ID | v2 decision / requirement | 狀態 |
| --- | --- | --- |
| ADR-v2-001 | C0 Census／C1 Primary MCDA／C2 Extended／C3 Historical 分開；主要 Aim A/B/C 共用 C1 的固定六構面準則集合 | FRAMEWORK_ADOPTED，C1 required criteria、正式母體未核定 |
| ADR-v2-002 | Project–Deposit–Resource Statement、JORC resource/reserve／M/I/I、oxide basis、公司／礦權角色與時間／證據追溯 | FRAMEWORK_ADOPTED，schema migration 未實作 |
| ADR-v2-003 | 固定 reference utility＋階層式 domain weights；AHP scenario 實際權重須可回溯；PROMETHEE II／TOPSIS 做互補比較 | FRAMEWORK_ADOPTED，參數與專家判斷未核定 |
| ADR-v2-004 | B1 權重、B2 數據、B3 方法、B4 cohort；Joint uncertainty + SMAA 僅在分布有證據支持時執行 | FRAMEWORK_ADOPTED，分布和 tie rule 未核定 |
| ADR-v2-005 | C1 模型內部敏感度與 C2 外部專案特徵分開；D1 included/excluded；C3 歷史 as-of 無時間洩漏 | FRAMEWORK_ADOPTED，實證尚未執行 |
| ADR-v2-006 | Commercial/ESG 歷史名稱保留；v2 擬以 Commercial & Regulatory Readiness 精確描述 C1–C3 | PROPOSED，需 criteria migration 核定 |

### 後續重大方法變更紀錄（Decision Log）

| Decision ID | Date | Status | Scope / Rationale | Version change | Affected Aim / Tests | Approval |
| --- | --- | --- | --- | --- | --- | --- |
| _於對應 PR 經審核後新增；不得覆寫歷史紀錄_ | | | | | | |

狀態使用 `PROPOSED`、`ACCEPTED`、`SUPERSEDED`。上表 `FRAMEWORK_ADOPTED` 代表研究架構的方向已列為後續工作依據，**不代表所有參數、樣本或實作已獲實證核准**。詳細變更流程見 [RESEARCH_IMPLEMENTATION_PLAN](RESEARCH_IMPLEMENTATION_PLAN.md)。
