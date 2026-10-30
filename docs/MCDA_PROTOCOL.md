# MCDA Protocol v2 — Six-Domain Project Assessment

**狀態：**研究方法契約／實驗參數待定稿。**現行已實作：** `config/criteria.json` 的 12 項 v1 指標及 `R/run_mcda.R` 的 AHP、PROMETHEE II、SAW、TOPSIS、權重 Monte Carlo。**v2 主分析尚未執行。**上位文件：[RESEARCH_ARCHITECTURE](RESEARCH_ARCHITECTURE.md)。

## 1. Analysis unit、母體與核准關卡

- Alternative = 一個經獨立證據核准的澳洲 REE **Project**；Project–Deposit–Resource Statement 的合併規則依 [DATA_SPECIFICATION](DATA_SPECIFICATION.md)。
- 主模型使用 **C1 Primary MCDA**：固定 `snapshot_as_of`、固定 `project_id` 名單、固定 `criteria_version`、固定有意義且數值完整的**共同六構面準則集合**。此集合須在正式排名之前預先簽定；不可依專案自行使用不同準則或重新分配缺值權重。
- 若缺任一構面或少於可合理比較的專案，**暫不發布六構面主排名**。另以 C2 呈現 coverage 與條件性次級情境；定義任何補值／區間模型前先記錄其科學假設。
- 現行 `G0_BASELINE` 缺 R1/S1；`RS_STRICT` 只是一個既有嚴格子集情境，其與 v2 C1 必須經共同 `cohort_version/criteria_version` 映射核准後才可比。現行 G0 19 筆 global release gate 維持原狀，直到正式移轉 PR 決定新 baseline。

## 2. 六構面：原始欄位、效用和資料品質

| Domain | 現有準則 | 建議主指標與處理 |
| --- | --- | --- |
| **R — Resource Potential** | R1, `contained_treo_kt` | 可比 TREO 元素/氧化物來源；保存 Mt、%TREO、JORC M/I/I、cut-off，避免與衍生 contained amount 共同重複加權 |
| **S — Strategic Composition** | S1, `magnet_reo_share_pct` | 明示 oxide set（例如 NdPr、DyTb，需與來源定義核對）、TREO 分母；絕對量與份額為相關變數 |
| **T — Technical Feasibility** | T1 processing complexity；T2 NORM burden | 固定 1–4 ordinal 判讀標準與證據級別；回收率若納入先定義 step vs overall |
| **D — Development Readiness** | D1 study maturity | 以實際報告/公告判定 1–6；D1 同時是 Aim C Stage 潛在循環來源，需主／排除模型比較 |
| **I — Infrastructure** | I1 Road, I2 Rail, I3 Power, I4 Port distance | EPSG:3577 與核准座標下的 proximity，單位 km，方向 MIN；不宣稱為交通成本、接入許可或供水能力 |
| **C — Commercial & Regulatory Readiness** | C1 Financing, C2 Offtake, C3 Approvals | 明訂 0–4／0–5 的文件判讀規則。v1 `Commercial/ESG` 是歷史標籤；現有指標不構成獨立 ESG outcome |

**需補齊的 Criteria Dictionary 欄位**：`criterion_code`, `domain`, `raw_variable`, `expected_unit`, `basis`, `direction`, `ordinal_codebook_version`, `missingness_policy`, `source_scope`, `utility_id`, `preference_function_id`, `dependency_group`, `required_for_C1`, `QA_tests`。

**指標相依審查**：`Mt × grade → contained TREO`，`contained TREO × magnet-REO-share → contained magnet REO`；另檢查成熟度與融資、承購、許可的概念重疊。主模型的 R/S 指標可各使用一個事先指定的代表值，其他值先做診斷；若有意加權兩個高度相依的量，需記錄獨立決策價值與調整依據。

## 3. 分數尺度與共通主模型

所有準則先依固定 reference 的效用函數 `u_j(x)` 轉為 `[0,1]`（0=最不理想，1=最理想）。正向／負向方向、截斷/飽和值、log 或 piecewise 轉換、極端值處理均須**在研究級計分前凍結**，並在 `config/scoring_functions.yaml`（擬定路徑，尚不存在）定義版本與試算案例。

`DomainScore(i,g) = Σ_{j∈g} v(g,j) × u_j(x(i,j))`

`TotalSAW(i,s) = Σ_{g=1..6} W(s,g) × DomainScore(i,g)`

- 每構面 `Σ_j v(g,j)=1`；`Σ_g W(s,g)=1`，任一權重不可為負。
- **SAW + fixed utility scales**：主要跨年度/跨 cohort 的可比較**絕對效用分數**；其他專案加入時不改變未變項目的原始效用值與固定權重下的 SAW 值（**排名**仍可因新增候選而變化）。
- **PROMETHEE II**：互補主要排序法；每項 V-shape 或其他 preference function/threshold 以物理／決策意義與敏感度核定，避免只用當次 IQR 當唯一固定門檻。
- **TOPSIS**：方法交叉比對；需顯示理想/負理想解依當次候選而變，不能拿其相對結果直接當跨年度絕對分數。
- 原有 `R/run_mcda.R` 的 min–max SAW、樣本 IQR PROMETHEE threshold 與 TOPSIS 為 **v1 baseline/sensitivity**；保留舊版結果與其版本名稱，不要在沒有版本遷移的情況下悄悄變成 v2。

## 4. 三種決策偏好與 AHP 契約

| Scenario | 構面偏好（待 AHP/專家評估後定量） | 科學用途 |
| --- | --- | --- |
| `resource_driven` | R > 其他構面的相對優先性 | 資源稟賦導向 |
| `development_driven` | T/D/I/C 相對優先性 | 開發準備導向 |
| `strategic_supply_driven` | S 與供應條件相對優先性 | 磁性稀土供應導向 |

決定 **AHP 操作層級**：建議先做六構面配對，再做構面內配對；每一 scenario 必須有對應 AHP 判斷/權重來源、判讀者/日期、一致性比（通常 `CR ≤ 0.10`）與可重現配對矩陣。若採研究者假設權重，必須明確標示 `ILLUSTRATIVE`，不能當作專家實際偏好。

**現行已知待修正邏輯：** `R/run_mcda.R` 先以 `--perspective` 選 `config/r_analysis.json` 的權重，但若指定 `--ahp`，則以 AHP 權重覆寫；三種 scenario 不一定代表最終實際使用三組不同權重。v2 需改成明確的 `scenario -> ahp_judgment_set -> resolved_weights` 路由、檢查審核記錄與回填實際採用 weights 的 audit。**修改前須先核定預期行為，不能直接改動函式。**

## 5. 執行結果與版本欄位

每次正式 Aim A 至少輸出可編輯 `cohort_membership.csv`、`criteria_dictionary.csv`、`criteria_values.csv`、`domain_scores.csv`、`analysis_matrix.csv`、`ranking_comparison.csv`、`weights_and_thresholds.csv`；另有可編輯 SVG 與 GIS GeoPackage（在 GitHub 中可用 DVC/LFS 或封存 manifest 追蹤）。

每列結果應追溯 `run_id`、`snapshot_as_of`、`cohort_version`、`criteria_version`、`utility_version`、`weight_version`、`method_version`、`seed`、`evidence_approval` 與原始來源。v2 正式 release 應同時報告每構面 Project N／缺值、選取率、GIS release 與跨方法排名 Spearman/Kendall；如使用 Spearman 不可隱藏 rank flips。

## 6. 需先定稿的參數（尚不可當成既有真實數值）

| 決策編號 | 決策/缺口 | 定稿證據與驗收 |
| --- | --- | --- |
| `MCDA-01` | **C1 必要準則集合**是否全部 12 項，或每構面預先指定共同子集 | 預分析可用性／分層樣本 N、六構面不缺、僅一種固定集合；記錄版本 |
| `MCDA-02` | 每項 utility 的固定區間/轉換 | 文獻或工程/專家判斷依據，極端值／單調性測試 |
| `MCDA-03` | 六構面及各準則的權重與 AHP 來源 | 3 scenario 實際有可稽核的 weight sets、CR/權重和審核紀錄 |
| `MCDA-04` | PROMETHEE preference function/p/q threshold | 明確偏好語意及敏感度測試 |
| `MCDA-05` | v1/v2 baseline 雙跑可比性 | 固定 seed 和資料，列出成因及替代 cohort／方法差異 |
| `MCDA-06` | D1 inclusion/exclusion 模型 | 主模型及 C2 模型的事前定義、固定其他參數 |

完成以上項目並經 [RESEARCH_IMPLEMENTATION_PLAN](RESEARCH_IMPLEMENTATION_PLAN.md) 的 Stage Gate 驗收後，才將 v2 主模型稱為研究級 Aim A。Aim B/C 另依 [VALIDATION_PROTOCOL](VALIDATION_PROTOCOL.md)。
