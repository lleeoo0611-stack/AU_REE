# P0 C1 Readiness — Frozen Census Review Audit

**盤點日：**2026-10-31；**資料截止：**2026-10-29。此文件是既有 GitHub 資料的初步審核，不是現行企業公告或 JORC 技術報告的重新查證。

## 來源與版本

- [487 Inclusion Gate](../../outputs/487_inclusion_gate.csv)、[487 Membership](../../outputs/project_entity_membership_487.csv)、[39 Group Register](../../outputs/project_entity_register.csv)、[Quality Gate](../../outputs/quality_gate_487_summary.json)、[Cohort Reproduction](../../outputs/reconstructed_cohort_487.csv)。
- 39 Group Register 的 Git blob SHA：`00bdfdb2575e85133af41147f3db401f34ea146e`，**不是來源文件 SHA-256**。
- [39-group editable CSV](2026-10-31_c1_review_groups.csv) · [Source/Transform Manifest](2026-10-31_c1_review_groups.manifest.json)：依原始 Group Register 的 `canonical_name` 排序，原文 Stage 和 disposition 全保留；新增標籤僅提示需審查，不是 Project Gate PASS。
- `inputs/verified_observations.csv`、`inputs/evidence_approvals.csv`、`inputs/project_reviews.csv` 目前各為 **0 data rows**（僅 header）。

## 已完成盤點

| 計量單位 | 數量 | 說明 |
| --- | ---: | --- |
| 487 固定 target rows | 487 | 86 legacy + 401 E1；並非獨立 Project 數 |
| target rows 有 group link / 沒有 link | 78 / 409 | 69 candidate-linked + 9 HOLD-linked |
| Project review groups | 39 | 32 `INCLUDE_CANDIDATE`、6 `HOLD_REE_ROLE`、1 身分／REE 證據不足 |
| Group Register 的人工 reviewer_decision | **0** | 不是說所有官方文件都不存在，而是此 register 未記錄最後核准 |
| Group company history status | 39 `UNKNOWN_OR_PARTIAL` | 公司及礦權角色鏈須核實 |
| 固定 487 source rows 記有經緯度 | 437 | **原始來源點**，不可當成已核准的 Project 代表點或 GIS release |
| 已核准正式六構面 C1 矩陣 | **未發布** | 欄位/公式已有規格，但現有正式 input 沒有核准觀測可直接使用 |

**Stage 文字訊號（39 review groups，未核實事件日期）：**2 組有明確 `PASS_FEASIBILITY` 或 `PASS_EXPLORATION_AND_PFS` 標籤；1 組 `PASS_CONSTRUCTION`（Nolans Project）；其餘 36 組 Stage 文字不足以直接判定 Scoping–Feasibility。這些是**資料表字串提示**：前兩組仍須檢查 FID 與截止日期，施工訊號也須從正式公告核定日期，不能自動排除。

## 研究判定

**P0.1 = `PARTIAL`**（納入規則已提出、研究群組審核未完成）；**P0.2 = `DESIGN_READY`**（JORC 關聯 Schema 概念已建立、尚無 migration）。C1 維持 `C1_NOT_RELEASED`，不得以未核准候選群組產生正式 Project 排名。

1. 先按 [C1 Admission Protocol](../P0_COHORT_SELECTION_PROTOCOL.md) 審核 Identity → REE role → 有效 Stage → JORC R1/S1 → 六構面共同準則 → GIS。
2. 逐 Group 填寫 [Project Gate Review Template](../../inputs/templates/c1_project_gate_review_template.csv) 與 [JORC Resource Statement Review Template](../../inputs/templates/jorc_resource_statement_review_template.csv)，保存文件、頁碼、effective/publication dates 和 reviewer approval。
3. 以證據覆蓋先比較 `PANEL_12_CANDIDATE` 與 `PANEL_9_CANDIDATE`，檢查 Stage/State/Deposit-type 選擇偏差；**正式排名之前**決定唯一主分析 Panel。
4. C1 正式 Project IDs／准入原因和 `criteria_version` 能被重建後，再啟動 P0 資料庫 migration。

請勿把 123,323 raw records、1,006 REE screening candidates、487 target rows、39 review groups 或 32 candidate groups 視為同一種 Project 計數。
