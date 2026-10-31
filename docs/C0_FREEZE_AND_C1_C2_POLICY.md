# 澳洲稀土 C0 雙層凍結與 C1／C2 研究母體政策 v1

**決策狀態：研究規則已核定（2026-10-31）；逐來源結案、逐 Project 准入尚待各自的證據與獨立簽核。** 原始來源日期固定 `2026-10-29`；方案版本 `C0_F1F2_COHORT_C1C2_V1_20261031`。

這份規則取代原 `ADR-P0-028` **凍結方案待決**的政策狀態，並保留原始紀錄。它不取代 C1 的六個既有 Gate、JORC 資源核查或固定六構面準則選擇。原 P1–P4 欄位仍是證據核查優先級，不是開發程度分級。

## 1. C0 雙層凍結（已採納規則，個案未簽核）

| 層級 | 凍結對象 | 需要哪些可稽核證據 | 合法後續狀態 |
|---|---|---|---|
| **F1：來源範圍結案** | 已查得相關政府/發行人原件段落，而且能明確界定其主張適用範圍的 C0 source | 原 target ID、凍結來源特徵 SHA、原始文件保存位置／官方 HTML 來源、對應頁面、`GEO_CONTEXT_ONLY` / `HISTORIC_NON_TARGET` / `SCOPE_TRANSFER_REJECTED` 限定判讀、審核人與日期、重開條件 | `F1_SOURCE_SCOPE_FROZEN` |
| **F2：原生來源暫停搜尋** | 只有政府原生來源，沒有可用的新具名 REE Project/資源技術線索者 | 原生 site ID/座標/來源特徵 SHA、已嘗試的 URL/日期/查詢記錄、`NEGATIVE_SOURCE_SEARCH_LOG` 明確證據、審核人與日期、重開條件；若有未釐清的新定位線索則不得暫停 | `F2_NATIVE_SEARCH_PAUSED` |

F1 是**本輪有界來源判讀結案**；F2 是**暫停無效取件**。二者的 source row 永遠保留 C0，不表示「沒有 REE」或「具有/沒有經濟開發潛力」，也不影響將來新 Project。

### 目前資料與未執行的核准

- 339 筆 P2/P3/P4 仍完整保留。**119 筆 F1 審查候選**；**151 筆 F2 預審候選**（其中 6 筆已有 B06 NT 技術報告定位線索，不可直接 F2 暫停；其餘 145 仍須正式查詢失敗記錄才能申請 F2）。
- **F1 實際結案 0、F2 實際暫停 0**。政策獲採納並不等於每筆來源自動得到審核簽章。
- 其餘 69 筆依 REE 主張、身分衝突、快取原件或其他技術問題保留個別處置，不強行凍結。
- 已審來源與未審來源同時保留 `source_evidence_reason`、`source_review_status` 和原生來源鍵；任何新技術報告必須在新的 `evidence_asof` 增量寫入。

**重開觸發：**新的官方地質原件、政府 minerald eposit / mining title 更新、發行人具名 Project 原件、同一 Deposit 的 REO/JORC 表格、新的開發研究/GIS 範圍或足以推翻原 bounded 判讀的證據。保留舊版本與原始署名，不原地改寫歷史快照。

## 2. 正式 C1 母體（嚴格六 Gate）

C1 的統計單位是**獨立 Project**，不計入單筆政府礦床圖徵、礦權、公司、Legacy alias、P1 case 或 39 group 的未核准來源。

| Gate | 必須通過的條件 |
|---|---|
| `ID` | 獨立核准 Project／Deposit／別名與法定範圍、穩定 Project ID |
| `ROLE` | 原件明確證明 REE 為計畫主要、共同或預定回收產品 |
| `WINDOW` | 截至 2026-10-29 已公開 Scoping/PFS/DFS/BFS/Feasibility、計畫仍處於 pre-FID，日期與法定狀態可核 |
| `JORC` | 同 Project/deposit 範圍、可核 M/I/I、噸數、截止品位、TREO 或逐氧化物 REO 定義的 Mineral Resource |
| `PANEL` | 已事前核定的共同六構面指標集，逐欄資料有批准來源 |
| `GIS_RELEASE` | Project 代表點/幾何與當期官方圖層之 QA、版本及審核通過 |

12 準則與 9 準則皆仍是候選，**本決策不擅自選定 Panel**。EES 的「scoping」、HM/THM 資源、獨居石礦物比例、單一化驗截距、歷史礦權或打算未來製作的 PFS 都不能直接滿足上述研究 Gate。

任何一個 Gate 不合格或未簽核，`C1_release_status` 保持未准入。日後正式 C1 應由逐 Project 版本化批准表生成，並保留完整 Gate 失敗分母與原因。

## 3. C2 的身分確認與用途

C2 對**已經獨立驗證 Project 身分與 REE 產品角色**、但缺少一項或多項 C1 條件的案例建檔。至少需要 `verified_project_id`、具證據的專案名稱／範圍、Project parent 跨來源關係、原始 REE 商品角色的文件，以及 `ID`／`ROLE` 兩項人工簽核。只靠政府來源中的同名點或群組標籤，仍留 C0。

C2 用於 coverage、缺漏機制、各地質／開發類型描述與**獨立標示的探索性情境**。**C2 不會自動混進 C1 主排名**，也不能為增加 C1 樣本數而放寬 C1 的 JORC、經濟研究及六構面要件。

超出 pre-FID 時窗但可重建歷史日期者另做 C3；已達 FID、營運或停產的 Project 不列入 2026 C1。

## 4. 實際第一輪母體工作

[39 個 Project 群組審查 CSV](audits/2026-10-31_c1_c2_project_review_39.csv) 保存既有唯一 group ID 與來源/階段：

- **7**：曾有 pre-FID 研究線索，優先核對原文 Study、有效日期、REA／REO JORC。
- **8**：研究時窗與 FID 需重新查日期。
- **14**：目前主要位於探勘或 Resource 階段，優先核對 Project 身分與研究是否存在。
- **7**：REE 產品/回收角色不清。
- **2**：文件已明確指向超過 pre-FID 時窗，進入歷史 C3 路線。
- **1**：活動暫停。
- **28**：由公司／政府具名來源與候選分類得到的 **C2 身分審查佇列**，尚未是 28 個正式獲證的 C2 Project。

[13 個 P1 正向案例交叉表](audits/2026-10-31_c1_p1_positive_case_crosswalk_13.csv) 與 39 群組分開，待來源確定後才同 Project 合併或另建正式 Project ID；**13 不是新增 13 個獨立 Project 的核准數**。

**目前正式准入：C1 = 0，C2 = 0**。這是如實執行未核准不升級原則的結果；母體建構管線已經建立，實際名單須獨立證據核准後才會出現。

## 5. 補查支線與工作優先級

- 先完成 B06 的 P2 待補 **8 筆**與已指出的 Elaine Dorothy 2010 歷史 JORC 跨來源一致性、Bell's Monazite 同名誤認；不將其當作 C1 必要前提。
- P3 **87**、P4 **64** 的原生圖徵維持 **100 個 `state|native_id` 原件查詢工作單位**；先追有相關 Project 名稱、同範圍 REE 產品、可靠資源和 Study 的群組，其餘參照 F2 審查。
- C1 主線先對既有 7+8 個 Project 群組收集 source-scoped 原始 Study 和 REO/JORC/GIS，逐 Gate 審核及更新可用 N；C2 須先核實正式 Project identity 再納入數量。

## 6. 再生與審核工作流

所有設定與輸出皆可編輯，命名固定且可追溯：

- 規則：`config/c0_freeze_policy_v1.json`、`config/cohort_c1_c2_policy_v1.json`。
- 獨立人工決策：`inputs/review_decisions/c0_source_freeze_signoffs_v1.csv`、`c1_c2_project_gate_signoffs_v1.csv`、`c1_c2_project_identity_metadata_v1.csv`（目前只有欄頭，沒有虛構簽名）。
- 輸出：`docs/audits/2026-10-31_c0_freeze_review_339.csv`、`2026-10-31_c1_c2_project_review_39.csv`、`2026-10-31_c1_p1_positive_case_crosswalk_13.csv`、`2026-10-31_c0_c1_c2_policy_summary.json`。
- 產生與驗證：`python scripts/build_c0_freeze_c1_c2_v1.py --write` 與 `--check`；另有回歸測試和 GitHub Actions。

**保護：**未來在 Signoff CSV 新增條目時，Python 需驗證原始 source-feature SHA、正式 reviewer、日期、來源文件與 Gate；不得因新增同名 Project、資源圖徵或 F1/F2 個案而觸發 C1 准入。研究方法仍維持 Aim A 地礦開發潛勢、Aim B 排名穩健性、Aim C 影響因素，待 C1 正式母體與固定 panel 可用時才產生研究級 MCDA。
