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

### P0 審查進度（2026-10-31；非正式准入決策）

| Decision ID | 日期 | 狀態 | 內容與科學依據 | 後續核准 Gate |
| --- | --- | --- | --- | --- |
| `ADR-P0-001` | 2026-10-31 | `PROPOSED` | C1 使用逐 Project 的 `ID → ROLE → WINDOW → JORC → PANEL → GIS_RELEASE` 審核；觀察到 review group/target row 與已核准 Project 不同 | [C1 Protocol](P0_COHORT_SELECTION_PROTOCOL.md)，需人工來源核准與 coverage |
| `ADR-P0-002` | 2026-10-31 | `PROPOSED` | 待比較 `PANEL_12_CANDIDATE`（全部 12 準則）與 `PANEL_9_CANDIDATE`（R1 S1 T1 D1 I1–I4 C3）；只按覆蓋/構念效度在看排名前定稿 | 全六構面共同準則/研究審查與樣本 N |
| `ADR-P0-003` | 2026-10-31 | `PROPOSED` | Resource statement 應有 scope/cutoff/edition/M-I-I/oxide/時間；沿用既有 Project ID 和 geological_entity，避免 JORC totals 與 deposit subtotals double count | [Schema Design](P0_PROJECT_RESOURCE_SCHEMA.md)，需增量 migration/test |
| `ADR-P0-004` | 2026-10-31 | `RECORDED_AUDIT` | 39 review groups（32 candidate/7 HOLD），正式 input approvals 及 observations 均空；本盤點 C1 `NOT_RELEASED` | [Readiness Audit](audits/P0_C1_READINESS_2026-10-31.md)，尚未簽核任何 Project |

以上 `PROPOSED` 表示可執行的審查設計，**沒有替研究者預先批准 C1 名單、JORC 數據或排名**；後續依來源記錄決策變更、審查人與日期。

### P0 source verification（2026-10-31；設計討論）

| Decision ID | Date | Status | Proposed change | Scientific basis / tests |
| --- | --- | --- | --- | --- |
| `ADR-P0-005` | 2026-10-31 | `PROPOSED` | 檢討是否將正式主分析定義為 `C1_DIRECT_REO`（可直接比對 JORC REO 的 pre-FID Project），將以 THM/MzEq 與 REE 副產品為主、未能計出可比 R1 的礦砂列於 `C2_HMS_REE_COPRODUCT` | 防止 THM/MzEq 被誤當 TREO；需先統計每 Project 六構面 N，檢查礦床類型偏差及資源範圍。**尚未接受/修改 C1 或 R1** |
| `ADR-P0-006` | 2026-10-31 | `RECORDED_AUDIT` | Nolans 和 Balranald 已有實際 FID/施工或採礦證據，按 2026-10-29 pre-FID window 不納入下一輪 C1 篩選，保留作歷史研究資料 | [39 組來源驗證報告](audits/2026-10-31_project_source_screen_report.md)。正式歷史事件仍需附文件 SHA、有效日期及獨立審核 |
| `ADR-P0-007` | 2026-10-31 | `RECORDED_AUDIT` | Jupiter 的 2026-10-12 JORC MRE、2026-10-20 Scoping 和 Dubbo 的 2026-08-28 母公司收購屬必須版本化的來源變更 | 須保留來源截至日；禁止 MRE 不同年份/Project–Deposit 總量重複相加，母公司收購不能直接推論礦權已轉讓 |

以上是**來源核查及待決定的科學問題**。任何 cohort/panel 實際變更須先有 Stage Gate 核准，不以此 Decision Log 取代正式 observations/evidence approval。

### P0 all-487 source audit（2026-10-31）

| Decision ID | Date | Status | Research/engineering decision | Evidence and next gate |
| --- | --- | --- | --- | --- |
| `ADR-P0-008` | 2026-10-31 | `RECORDED_AUDIT` | 精確 `target_id` 將 487 source records 一次整併；不以地名、州別、礦權空間交集推定 Project，也不把工作佇列 Priority 視為評分 | [487 全量審查報告](audits/2026-10-31_census_487_batch_review_report.md)、[37→39 欄逐筆 CSV](audits/2026-10-31_census_487_batch_review.csv)；409 筆尚未建立 Project group，C1 仍未核准 |
| `ADR-P0-009` | 2026-10-31 | `RECORDED_AUDIT` | 留存 source/entity/crosswalk/tenure/evidence locator 當次 status 並產生 P1–P4 review workstream；不同來源、快照、實體層級數不得混計 | [Batch QA Summary](audits/2026-10-31_census_487_batch_review_summary.json)、[Rebuild script](../scripts/build_p0_census_487_audit.py)、pytest；下一 Gate 為關聯核定和 JORC resource basis |

此處的 P1–P4 是**Census 審查工作優先順序**，與研究開發里程碑 P0–P3 **不同**，不可混用。

### P0 all-source claim evidence review（2026-10-31）

| Decision ID | Date | Status | Evidence / decision | Required follow-up |
| --- | --- | --- | --- | --- |
| `ADR-P0-010` | 2026-10-31 | `RECORDED_AUDIT` | 487 個來源列全納入證據深度分類；441-row trace 之原始資料定位與 95-row document locator 採不同層級；原生記錄 `EXACT` 不代表 Project 證明 | [逐筆 Evidence Claim CSV](audits/2026-10-31_487_evidence_claim_review.csv)、[報告](audits/2026-10-31_487_evidence_review_report.md) |
| `ADR-P0-011` | 2026-10-31 | `RECORDED_EVIDENCE_LEAD` | WA 2026-02 官方 REE 清單有 20 Project/resource names；同州完全同名與現有 487 對到 13 種名稱／20 原始列，包括 Cummins Range、Yangibana、North Stanmore | 需 Project scope/JORC statement 原文、期限、類別和 reviewer approval；不自動新增正式 Project ID |
| `ADR-P0-012` | 2026-10-31 | `RECORDED_EVIDENCE_LEAD` | NT EL31225 官方公開 2023 報告明示 Plenty River prospect 屬 Bruce Project，應優先審核 parent relation | 指派獨立來源/關聯審核；尚未新增正式資料庫 Project／Deposit link |

以上新來源和原始已核准觀測屬**不同層級**。本輪新增的 source leads 不能取代正式 `evidence_approvals.csv`。


### P0 evidence recovery round 2（2026-10-31）

| Decision ID | Date | Status | Evidence decision | Follow-up |
| --- | --- | --- | --- | --- |
| `ADR-P0-013` | 2026-10-31 | `RECORDED_AUDIT` | 487 Census source targets 再核查外部政府與公司報告，為 86 筆增加來源文字定位；保持 Round 1 欄位、native ID、Project/Deposit 層級與正式 Gate 不變 | [第二輪報告](audits/2026-10-31_evidence_round2_report.md)、[逐筆 CSV](audits/2026-10-31_487_evidence_round2_review.csv)、[62 筆可追溯來源線索](../inputs/source_review_20261031/round2_external_evidence_leads.csv) |
| `ADR-P0-014` | 2026-10-31 | `RECORDED_AUDIT` | 原無外部文件的 23 筆中 20 筆取得外部來源指標，但原 native bytes 仍缺；Olympic Dam/Clarke 取得政府來源仍保留 4／6 個 source feature row 歧義 | [86 個改變的 target](audits/2026-10-31_evidence_round2_changed_targets.csv)；需 source-native feature discriminator、官方原件 bytes SHA-256 及 independent review 才可能核准 |

