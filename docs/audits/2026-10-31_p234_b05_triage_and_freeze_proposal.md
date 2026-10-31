# P2–P4 B05 — 全量來源分流、同源工作群組與凍結規則草案

- Execution: `P234-B05-NATIVE-WORKGROUP-TRIAGE-20261031`
- Geological/source as-of: **2026-10-29**；補查、分析與規則草案日期：**2026-10-31**
- Baseline: [339 筆終端分類](2026-10-31_p234_final_evidence_339.csv) + [B04 全量進度](2026-10-31_p234_all_339_continuation_b04.csv)，疊加未合併的 B03/B04。
- 本次未更改 P1 73、P2 28、P3 216、P4 95、原始 412 HOLD ID、原始快照、正式 C1/JORC/六構面/MCDA 核准。

## 總進度：工作單位與來源筆數分開計

| 狀態 | 來源筆數 | 說明 |
| --- | ---: | --- |
| P2–P4 全部原始來源 | **339** | 28 + 216 + 95，全筆保留原始 target ID |
| 保存原件相關頁／HTML 的舊查核 | **143** | 原件與有界章節，非全部完整技術報告 |
| 公開原始來源文字有界判讀 | **32** | P2 既有 12 + B05 新增 4；P3/P4 原先 16 |
| 網頁快取文字，原始位元組未保存 | **1** | Scaddan；原始 PDF 仍須存取 |
| P2 繼承舊桌面審查，待新技術原文 | **12** | 未將文件索引直接宣稱全文已驗證 |
| P3/P4 只有政府原生圖徵，未完成外部來源原文 | **151** | P3 87 + P4 64 |
| **優先待查清單** | **163** | P2 12 + P3 87 + P4 64；仍非全部 Gate 缺口 |
| **優先查核工作單位** | **112** | P2 12 單列工作 + P3/P4 100 同源群組 |

### 原生 ID 跨來源對應

151 筆 P3/P4 待查記錄，在同州與相同 `source_native_id` 下為 **100 組**；**51 組**含兩筆來源，另有 **30 組**涉及不同 `source_key`，有可能是同一個州政府資料實體的不同來源視圖或 Legacy 紀錄。逐群組檢查原始名稱與政府來源點，**0 組名稱不符，0 組點距超過 1 km**；全部 151 筆座標有值。

這是「共同查核工作單位」，**不是** 100 個唯一礦床／100 個經核准的 Project，也不是自動刪除重複 source ID。工作群組的穩定比對欄位是 `state|source_native_id`，群組編號 `P34WG-0001` 等只用於本次可編輯工作清單；下一次來源母體變動時，使用穩定鍵連結歷史組別。

### B05 補強的四個 P2 案件

1. **Duke**：發行人 [Duke 官方頁面](https://hreltd.com.au/projects/duke/)與 [2026-10-29 季報](https://investors.hreltd.com.au/announcements/w57kvA-hre-september-2026-quarterly-activities-report-appendix-5b)確認 Duke 為 HREE 探勘專案，EL33101／EL33194，42 m @ 770 ppm TREO 是歷史鑽探結果；網站比較的 Browns Range 9.24 Mt 礦量是另一專案。公司持權敘述與原生座標、當期官方法律權利還需要交叉核對。**保留 C0，無 Duke-specific JORC REO 或 Scoping / PFS。**
2. **Bruce Prospect**：北領地 [REE 官方礦業頁面](https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree)及其 2024 資訊圖錄列 Bruce 探勘截距 2 m @0.4% TREO；同時參照 [EL31225 2023 NTGS 原始技術報告](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/92857/1/EL31225_2023_C_01.pdf)。所引 2m 與 Plenty River 其他截距不可互相代換；尚需 Legacy 原生點至 Project polygon 的獨立 join。
3. **Plenty River**：EL31225 2023 原件將 Plenty River 設為 Bruce Project 內 prospect；共鑽 11 RC 孔／1,622 m。Table 3 有 BRR23009 的 **3 m @1,010 ppm TREO** 與 BRR23016 的 **21–22 m 單樣 6,770 ppm TREO**；都是探勘證據，不能轉寫成 JORC MRE 或獨立 Project。需核對 2026 礦權及原始鑽探表。
4. **Brumby Clydesdale**：[2025 Scoping Study](https://intergroupmining.com/wp-content/uploads/2025/02/IGM-BC-Scoping-Study-2025-v1.pdf)印刷 pp.6、11、70–74 將 Stage 1 高嶺土／矽砂等現金流和 Stage 2 深部 Y、Ce 等關鍵礦物潛力分開；其現金流模型未計入未實現的關鍵礦物收入；文件提及另一份 Phase 2 PFS，但本輪未取到。**已有 Stage 1 Scoping Study 不等於已有同範圍 REE 的資源及經濟研究。**

資料、文件位置、個案應做的下一步：[4 筆可編輯 B05 P2 判讀](../../inputs/source_review_20261031/p234_b05_primary_scope_reviews.csv)。NT 與 Brumby 原始 PDF 的公開可搜尋文本已檢閱；網站頁面影像擷取 cache miss，**本輪沒有取得任何 PDF 原始位元組、雜湊或視覺全文核驗**。不得標為技術原件全文完成，也沒有獨立簽核。

### Skyfall — 新增兩筆 P4 原始技術文件索引，暫不移出待查群組

北領地官方 [GEMIS CR2014-1016](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/81038) 確認 **Skyfall Prospect** 歷史 EL27151、2014 年鑽探技術報告，並說明 SKDH05 深部目標未取得足夠的 REE 結果，不等於淺部 Skyfall 礦化不存在。另有政府 [稀土資源頁](https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree) 將 Skyfall 列為含 xenotime 的 HREE 地質目標。但官方 GEMIS 報告與 `NT_MODAT_WFS:mineraloccurrence/5904` 的**同一來源點、當期礦權、專案邊界**尚未獨立對回，故兩筆 P4 ID 仍是 **native-only 待核查**。參見[定位判讀 CSV](../../inputs/source_review_20261031/p234_b05_locator_followups.csv)。

## 新的逐筆分流欄位（不寫入既有 Approval 表）

- `source_review_status`：`ARCHIVED_RELEVANT_PAGES`、`PUBLIC_PRIMARY_TEXT_SCOPE_ONLY`、`WEB_CACHED_TEXT_ONLY`、`INHERITED_DESK_NO_NEW_ORIGINAL`、`NATIVE_FEATURE_ONLY`。**互斥的實際查核層級**，不是證據評分或礦業階段。
- `project_identity_status`：以基線 `terminal_evidence_status` 映射出具名 Project 主張、純地質脈絡、錯誤 scope transfer、歷史／非目標、名稱／地理衝突等**證據狀態**；不將其稱作正式 Project 核准。
- `C1_eligibility_status`：339 筆皆 `NOT_ADMITTED_SIX_GATES_UNAPPROVED`。
- `proposed_freeze_route`：來源審查的**建議工作路由**；`source_scope_human_signed=NO`，所以無任何資料正式凍結。
- `source_native_shared_work_key`：只用於來源複核共用取件及同步註記，不決定 Project 實體合併。

## 凍結規則草案（待使用者核定）

目前提出 **119 筆來源範圍結案候選**，來源於保存原件相關內容、且基線具有明確地質／非目標／歷史／跨專案資源移轉不成立的 bounded 判讀：88 筆地質脈絡、21 筆跨 scope 不可轉移、10 筆歷史／非目標內容；P3 96、P4 23，P2 0。這是**候選清單**，不含獨立審核簽章，不代表完全沒有 REE 礦化，也不代表 C1 已明確 EXCLUDE。

**方案 F1 — 證據支持的來源範圍結案（保守）**

- 只有原始政府/技術文件確實支持的 bounded scope 結論、可追溯文獻定位/版本、原始 source ID/座標，且已記錄需何種新資料才重開，才可進入 `SOURCE_SCOPE_FROZEN` 待核准階段。
- 審核者簽名、審核日、原件 bytes 或官方 HTML 文本校驗、所引頁碼、source snapshot hash 必備；所有正向具名 REE 資源/Project 主張仍需繼續查資源及身分。
- **0 筆直接自動批准**，119 筆先按此方案人工核准；失敗、無法定位或資料矛盾者仍 HOLD。

**方案 F2 — 雙層凍結（建議）**

- **第一層**採 F1：有實質原件支撐的來源範圍結案（先審 119 筆）。
- **第二層**允許 `C0_NATIVE_ONLY_ARCHIVED_PENDING_EXTERNAL_EVIDENCE`：對無新具名 Project/REE 資源證據的政府原生地質點，可停止無效的外部重複搜尋並保留 C0 來源，**不能宣稱已通過技術全文、沒有 REE 或不具開發潛力**。逐來源記錄確切 native ID、政府原始記錄、查詢日期與失敗記錄、重開條件、人工核准。
- 這類 C0 原生資料的凍結是「暫停來源蒐尋」，不會阻擋日後新增正式 Project 證據；以新的 evidence/version overlay 重開，不改歷史結果。

**方案 F3 — 全體必須有完整技術原件才結案**

- 所有 native-only 來源持續搜尋直到取得獨立全文；優點是原件一致性高，但對歷史 occurrence 與無 Project 母層資料可能成為無期限的工作佇列，且不能提升正式 C1 資料品質。

### 正式凍結最小欄位（草案）

`target_id, source_snapshot_sha256, source_review_status, scope_decision, decision_basis_document_id, original_sha256_or_official_html_archive_ref, page_or_section, evidence_as_of, reviewer_id, reviewed_at, freeze_rule_version, reopen_trigger, review_signature`。

同時禁止 `source_scope_frozen` 自動更新 `C1_admitted`、JORC 資源、正式項目 ID、GIS 代表點、MCDA 分數。撤銷或新證據需新增後續版本，不刪改原版。

## 重跑與驗收

```bash
python scripts/build_p234_source_triage_b05.py --check
python -m unittest discover -s tests -p test_p234_source_triage_b05.py -v
# 需在已核對人工輸入後才重生 derived data
python scripts/build_p234_source_triage_b05.py --write
```

輸入仍為 B04/原始 339 + 本批人工判讀，輸出為 [339 分流 CSV](2026-10-31_p234_b05_source_triage_339.csv)、[100 組 native 取件 crosswalk](2026-10-31_p34_b05_native_workgroups_100.csv)、[112 單位實際待辦](2026-10-31_p234_b05_priority_work_queue_112.csv)、[摘要 JSON](2026-10-31_p234_b05_triage_summary.json)。自動化只能檢查計數、關聯和 Gate 不變，不取代人讀第三方原件及獨立簽核。

**Gate 判斷：**來源分流／同源查核單位建立完成；凍結決策 `PROPOSED`、簽核 `NOT_EVALUATED`、C1 `NOT_RELEASED`。Aim A 的資料辨識繼續推進，Aim B/C 正式排名尚不發布。
