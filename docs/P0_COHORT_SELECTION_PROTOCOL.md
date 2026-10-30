# P0.1 — Primary MCDA Cohort Admission Protocol

**研究階段：**P0.1（Cohort 定義、資料覆蓋盤點與審查規則）  
**基準來源截止日：**2026-10-29；**設計與盤點日：**2026-10-31。  
**文件狀態：**`ADMISSION_RULES_PROPOSED / C1_LIST_NOT_FROZEN`。現行 v1 eligibility 和已封存的 G0/R1/S1/RS **完全不變**。對應 [研究總架構](RESEARCH_ARCHITECTURE.md) 與 [P0 資料盤點](audits/P0_C1_READINESS_2026-10-31.md)。

## 1. Project 定義與研究母體

**統計單位為 Project，不是某一份來源表的 row 或單一礦床。** Project 需要有可識別的開發範圍/名稱、REE 在計畫中的角色、活動/階段證據、資料截止時間和獨立審核；Deposit／Tenement／Company 僅作為關聯實體。未經核准的來源候選永遠保持 C0。

| Cohort | 定義 | 是否可進行主要 MCDA |
| --- | --- | --- |
| `C0_RAW_CENSUS` | GA/州別原始紀錄與 REE 候選，原 source IDs 保留；同名、同址可有多筆 | 否 |
| `C1_PRIMARY_MCDA` | 經核准的澳洲 REE pre-FID Project；Scoping/PFS/DFS/BFS/Feasibility；JORC 資源及共同六構面必要準則有可核准值；正式 GIS/source gate 已通過 | **是，通過全部關卡後** |
| `C2_VERIFIED_EXTENDED` | Project 身分可確定，但未通過 C1 所有資料/階段/比較性條件；每筆保留原因 | 僅描述 coverage 和獨立探索性情境 |
| `C3_HISTORICAL_EVAL` | 截止日前可重建當時 Project 身分、資料與後續里程碑；可與 C1/C2 部分重疊 | 僅使用獨立的 as-of 驗證 |

**C1 不能由 `INCLUDE_CANDIDATE`、`PASS_*` 或座標存在自動推定。** v1 `G0_BASELINE` 缺 R1/S1，凍結 19 Alternatives 僅是舊全域 Gate 的參照，不代表 v2 C1 已有 19 個核准專案。

## 2. C1 六層審核（逐 Project、逐日期保留狀態）

| Gate | 可核准的 PASS 條件 | HOLD／排除條件與註記 |
| --- | --- | --- |
| `ID` | 完整 Project 身分、範圍與 Deposit/alias crosswalk，獨立來源與審核決策 | 同名或位置近、群組尚待 sign-off → `HOLD_IDENTITY` |
| `ROLE` | REE 為主要／共同商品或**文件明確表述的計畫回收副產品** | 只有礦物出現而無開發/回收意圖 → HOLD；有反證才 EXCLUDE |
| `WINDOW` | Australia；活動正在進行/研究；截至截止日**已有且公開** Scoping/PFS/DFS/BFS/Feasibility 階段；當時尚未 FID | 僅 Exploration/Resource、Stage 模糊 → `HOLD_STAGE`；已確認 FID/Construction/Production → `OUTSIDE_WINDOW` |
| `JORC` | **與 REE 評分對象及範圍可對應**的 JORC Mineral Resource 聲明，具報告版本、M/I/I、Mt、grade、cut-off、日期與來源；可核對 R1 的 REE basis | 僅 Heavy Mineral (THM) 資源、monazite presence 或不相容 REO basis **不能自動換算** R1；缺證據 → HOLD |
| `PANEL` | 每個 Project 使用相同的、事先凍結的**六構面共同準則集合**，有審核值與逐準則來源 | 缺值／衝突／只靠假設補值 → `HOLD_COVERAGE`；不得為單一 Project 改權重 |
| `GIS_RELEASE` | Project 代表點/幾何角色核准，I1–I4 所需官方 GIS layer 的來源、時間、SHA 與距離 QA 達標 | 僅有未核准經緯度、官方 API 查到圖層、或直線距離無來源 QA 不代表 PASS |

各 Gate 皆記錄 `project_id`、`snapshot_as_of`、`gate_version`、`decision_status`（`PASS / HOLD / EXCLUDE / NOT_EVALUATED`）、`reason_code`、`source_id`、`approval_ref`、`reviewed_at`。**EXCLUDE 僅用於有確切反證或研究範圍不符；證據不足採 HOLD。**

`WINDOW` 需區分已發布的 FID 決定與「預計 FID」文字；同樣 `PASS_CONSTRUCTION` 是優先查核訊號，仍須核對事件生效與公開日期，不能僅憑字串確定截至快照的狀態。母體若跨時點研究，不得由 2026 公告逆推更早時間的資格。

## 3. 六構面 Panel 的定稿策略

目前 `config/criteria.json` 定義 R1、S1、T1、T2、D1、I1–I4、C1–C3，共 12 準則；正式觀測核准表仍無列，**無法合理宣稱任一 panel 已具可比較 C1 數據**。先審查各準則的原始文件覆蓋，再選擇「在評分前固定」且具地質/開發意義的 panel。

| 事前候選方案 | 固定指標集 | 評估目的 |
| --- | --- | --- |
| `PANEL_12_CANDIDATE` | R1 S1 T1 T2 D1 I1 I2 I3 I4 C1 C2 C3 | 保留原 12 項，但可能造成嚴格披露偏差 |
| `PANEL_9_CANDIDATE` | R1 S1 T1 D1 I1 I2 I3 I4 C3 | 每構面至少一項且 GIS 四項保留；T2/C1/C2 以獨立擴充/敏感度研究呈現 |

**兩個方案均非正式已採納主要指標集**。候選 Panel 的取捨只用於研究單位與**證據覆蓋／構念效度**審查；不能先觀看專案排名再為結果挑選指標。需有 `PANEL_SELECTION_DECISION`（來源與理由）、各方案/州別/Stage/Deposit Type 的可用 N、基礎設施單一構面影響審查，以及版本化的 `criteria_version`。

現行 v1 `minimum_coverage_fraction=0.7`、`minimum_domain_count=4` 是**歷史程式規則**，不自動滿足 v2「六構面共同 Panel」。若經審核仍無足量樣本，保留 `C1_NOT_RELEASED`，以 C2 的 coverage 作為成果，不擅自降低關卡。

## 4. 資料盤點工作流（不改動任何身份判決）

1. 以凍結 `outputs/project_entity_register.csv` 產生**39 群組**的機器可讀審查清單，保留群組 ID／名稱、既有 disposition、階段原字串、reviewer decision。
2. 對每個候選群組核對來源 Project 邊界、關聯 Deposit、REE role 與**對應日期**；必要時從同一 Document 的明確章節擷取有效的 source_id/page/section。
3. 從 [P0.2 Resource Model](P0_PROJECT_RESOURCE_SCHEMA.md) 紀錄 JORC statement 的 Project/Deposit coverage、Mineral Resource vs Ore Reserve、M/I/I、tonnage、grade、TREO/oxide basis；未提供則依實際原因標示。
4. 逐 Project 盤點 12 項準則的 `APPROVED / REVIEW_PENDING / NOT_REPORTED / BASIS_UNRESOLVED`，不可用目前資料表的「空欄」臆測來源不存在。
5. 生成各 Panel 的**完整案例數**、域別/州別/Stage/Deposit Type coverage；將 `ID/ROLE/WINDOW/JORC/PANEL/GIS_RELEASE` 各步 N 和 HOLD 原因整理為 flow table。
6. 只有取得可驗證的證據審核結果，才在 Decision Log 核定 `C1_FROZEN` 和固定 `criteria_version`、`snapshot_id`。輸出的正式矩陣不可再依排名改動 Panel。

### P0.1 驗收

- `C0` 的原始紀錄 ID 全部保留，39 群組只是本次查核的**待審候選**而非正式母體上限；C0 可繼續從其他來源補充候選。
- 沒有同一來源紀錄自動升格 Project；任何 merge/split 留有 evidence approval 和歷史 alias。
- 逐 gate 的 `PASS/HOLD/EXCLUDE` 人工核准和日期可稽核、分母及 source scope 清楚。
- C1 若無完整且核准的共同 Panel，測試應阻止研究級 SAW/PROMETHEE/TOPSIS 輸出；研究仍保留 C2 的 coverage 和版本化待審資料。
- 各個樣本選擇與缺失情境有獨立 cohort/scenario ID，不重寫 v1 G0 或已發布的工作包。

**操作模板：**[逐 Project Gate Review Template](../inputs/templates/c1_project_gate_review_template.csv)；[39 群組初步盤點](audits/P0_C1_READINESS_2026-10-31.md)。