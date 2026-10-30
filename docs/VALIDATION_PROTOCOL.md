# Validation Protocol v2 — Ranking Robustness, Drivers & Historical Evidence

**研究範圍：**Aim B / Aim C；依 [RESEARCH_ARCHITECTURE](RESEARCH_ARCHITECTURE.md)、[DATA_SPECIFICATION](DATA_SPECIFICATION.md) 和 [MCDA_PROTOCOL](MCDA_PROTOCOL.md) 的核准 C1 母體／準則／效用／權重為前提。此為**待實作設計**，不表示已有 SMAA、完整 Aim C 或歷史回測結果。

## 1. 不確定性的四個來源

| Block | 改動內容 | 固定內容 | 研究產出 |
| --- | --- | --- | --- |
| **B1 Weight** | 三種 scenario 下獲准的權重範圍/單純形 | C1、data、scoring、method | Weight-only rank acceptability、rank intervals |
| **B2 Data** | 技術報告估計區間、實驗誤差、觀測值模型 | C1、weight scenario、method | Data-only distributions、score/rank shifts |
| **B3 Method** | SAW、PROMETHEE II、TOPSIS 及合理門檻變體 | 同一資料、C1、對應權重 | Concordance、rank reversals、pairwise disagreement |
| **B4 Cohort** | eligibility rules、候選集加入/剔除、C1/C2 子集 | 以共同專案集合及明確準則比較 | Selection sensitivity、coverage-stage bias |

**不可將四個 Block 混在一次未標記的隨機模擬中。**先個別檢驗，再執行 B1+B2 joint 模擬；B3、B4 作為明確標記的 robustness strata。跨 cohort 排名比較需明訂「比較共同 alternatives」或「兩個不同 universe 的各自條件排名」，避免混淆 P(Top 5)。

## 2. 可重現的 B1+B2 模擬規格

- **權重**：使用每個 scenario 的既定 AHP 或可接受區域。Dirichlet 可用，但其 concentration、shape、限制、抽樣目的與來源必須明示；現有 `concentration=30` 僅是 v1 已用的假設，不自動升為 v2 真實偏好。
- **數值觀測**：擇一 `point_estimate`、`reported_interval`、`empirical_distribution`、`expert_scenario` 或 `missingness_sensitivity`；每種含來源、形狀與範圍。沒有誤差依據時不得以報告階段直接推定精確 CV。
- **相依性**：每次 draw 先抽同一 statement 的 Mt、Grade，再算 `contained_treo_kt = Mt × grade% × 10`；類似 NdPr contained = derived contained TREO × oxide share。若模型有聯合相關性，需指定 sampling/correlation group；單純獨立抽樣若破壞等式應 fail。
- **缺值／爭議**：C1 未通過 QA 就不納入正式 joint 模型；C2 可做明示的 exploratory missingness models，須獨立 ID 並標註結果非正式 C1 ranking。
- **基礎測試**：所有 weights 非負且總和為 1、分數有效、來源生效/公開時間符合 as-of、fixed seed 可重現、tie rule 固定、輸出指標取值合法。

## 3. SMAA-2-style 輸出

對指定的 `cohort_id`、`method_id`、`scenario_id`、`uncertainty_model_id`，以 `N` 次有效抽樣估計：

`b(i,r) = count(project i has rank r) / N`

`P(i in Top-k) = Σ_{r=1..k} b(i,r)`

`P(i outranks j) = count(score/rank i better than j) / N`

Tie handling 必須預先固定：建議**隨機 tie-break 僅用於排名可接受度估計時，並同時輸出 tie frequency**；或採其他一致的分數與排序約定且能使每個 i 的 `Σ_r b(i,r)=1`。不得將平均排名 2.5 當作整數名次的可接受度欄位。每個 Project 需提供 P(rank1)、P(top3/5，僅在 N≥k 時)、median rank、90% rank interval、pairwise probability；模擬抽樣誤差及收斂檢驗需報告。

**解釋邊界：**所有機率都以明示的 model/cohort/preferences/data assumptions 為條件；並非礦場投產、獲利或環境許可成功機率。

## 4. Aim C1：模型內部影響分析

- `LOO_criterion`：刪除一個準則、在同一構面內依事先指定規則正規化。
- `LOO_domain`：刪除一個構面、剩餘構面重新正規化；報告每個 project 的 score/rank shift，不能只報 Spearman。
- `utility/threshold`：合理的參考尺度、PROMETHEE p/q、權重變動；報告最大和中位排名變動、pairwise flips。
- 敏感度分析處理**數學相依**與相關輸入；不得直接把高度相依因素的獨立擾動 Sobol 指標解釋為其唯一實體貢獻。
- 所有輸出為**模型內的影響**，不能據此宣稱地質特徵「導致礦山成功」。

## 5. Aim C2：外部專案特徵研究

候選協變量包括 **Deposit Type、mineralogy、Lifecycle Stage、magnet REO composition、processing/recovery evidence maturity、GIS accessibility、evidence completeness、state/jurisdiction**。每項須列出 codebook、來源／品質與是否已參與 MCDA 打分。

| 假說／比較 | 主分析設計 | 控制與報告 |
| --- | --- | --- |
| 不同 Deposit Type 的 Domain profile | 固定 C1 下分層描述；樣本足夠才進行模型估計 | 分層 N、缺失、stage mix、bootstrap/CI |
| Stage 與排名／穩健性的關係 | **D1 included vs D1 excluded** 兩模型比對 | Stage 不可同時計分後又當獨立因果解釋 |
| 地質/冶金條件與優先順序 | 優先使用非直接打分的獨立特徵及其交互關係 | 若變數已入分數，標註 mechanical association |
| State／GIS coverage 與納入偏差 | C1/C2 覆蓋矩陣、分層選取率 | 不以資料揭露程度代表實際開發成功 |

樣本數偏小時採描述統計、置信區間與排列／非參數比較；只有有效 N 足夠、可辨識假設成立時才使用複雜迴歸或混合效應模型。假說、比較數目與多重比較（如 Holm）需事前凍結；所有結論僅表達資料支持的**關聯**。

## 6. C3 Historical Validation：as-of 回推

**目標**：檢查過去時點的模型排序，與後續「是否跨過客觀里程碑」之描述性關聯；不直接把其當作成功率預測。

- 可選候選 cutoff，例如 2022-12-31、2024-12-31（僅為方案，需先驗證當時來源的出版與有效日期）。
- 指定 forward outcome：例如初次 PFS、DFS、FID、重大許可、募資事件；事件定義應規避僅由同一 Stage 排名構成的循環檢驗。
- `public_date <= as_of_date` 且 `effective_date <= as_of_date`，按每個 cutoff 獨立重建已知資料；事後公告、回填關聯、當代更新 mineral resource 不可進入歷史評分。
- 報告固定觀察窗、right censoring、起始 Stage 分層、當時 C1 及分母、後續 event N；如資料不足，只提供資料可用性與 case-based retrospective analysis。
- 任何宣稱 predictive power 需另有預先定義的 outcome metric、外部驗證/誤差與可識別的 comparison baseline，不能只看少數成功個案。

## 7. 驗收與可編輯輸出

| Gate | 最低驗收條件 | 必要輸出 |
| --- | --- | --- |
| **B1** | 記錄 scenario-specific weight regions、seed、抽樣一致性 | `weight_draws_manifest.csv`, `rank_acceptability_weight.csv` |
| **B2** | 每個分布有 evidence basis；derived variables algebraically consistent | `data_uncertainty_registry.csv`, `rank_acceptability_data.csv` |
| **B3/B4** | common-alternative 比較規則、方法/樣本版本固定 | `method_comparison.csv`, `cohort_sensitivity.csv` |
| **B joint** | 有效總權重 1、每專案所有名次可接受度加總為 1、pairwise reciprocity/ties 檢查 | `rank_acceptability.csv`, `pairwise_probabilities.csv`, `simulation_manifest.json` |
| **C1** | Domain/criterion 的 rank shift、pairwise flips 可重跑 | `model_drivers.csv`, `rank_flip_pairs.csv` |
| **C2** | D1 雙模型、每組 N/CI/coverage、內部/外部關係分離 | `project_characteristics.csv`, `stage_deposit_comparison.csv` |
| **C3** | 無時間洩漏、固定 follow-up、起始階段/右設限記錄 | `historical_snapshot_audit.csv`, `historical_validation.csv` |

所有輸出以 CSV／SVG 等**可編輯格式**為主；對應 run_id、資料快照、參數、git commit、研究判讀與 QA 狀態。新研究腳本僅在 [RESEARCH_IMPLEMENTATION_PLAN](RESEARCH_IMPLEMENTATION_PLAN.md) 指定的實作 PR 中加入。
