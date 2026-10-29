# 全澳 REE Evidence-backed Development Project 母體縮減：2026-10-29

## 操作定義

Australian REE mining project = 位於澳洲、可辨識的礦業勘探／資源評估／開發決策單位，具可追溯專案名稱、來源或母專案識別碼，且有 REE 作為主要商品、共同產品、計畫回收副產品或獨立勘探目標的政府或正式技術證據。JORC 與 Scoping–DFS 作為後續 MCDA 分層，不作為 Project Census 先行納入條件。

## 量化處理結果

| 層次 | 數量 | 計數單位 |
|---|---:|---|
| Scheme A 全澳 REE 初篩 | 1,006 | 原始來源候選紀錄 |
| E2／E3 地質與稀土礦物延伸名冊 | 203 | 來源紀錄 |
| E1 明確 REE 商品 | 803 | 來源紀錄 |
| WA E1 有官方 Parent Project Code | 399 | 來源 Site／Deposit |
| WA 官方 Parent Project 群組 | 121 | 官方母群組代碼 |
| SA E1 官方具公司資料 Project | 3 | 官方 Project 紀錄 |
| 其他 E1、原始來源未提供直接 Project 鍵 | 401 | 來源紀錄，待官方資料關聯 |
| 補入 NT Nolans、NSW Dubbo 的獨立官方 Project 證據後 | **126** | 可辨識 Project 形狀的暫定群組，不等於已核准 Census |
| 逐項查閱官方 Project 來源的範例 | 7 | 不重複的專案名稱，均出現在歷史 203 名冊 |

核對歷史 203 筆時，有 **159 筆**能以來源記載的完全標準化名稱或 WA Parent 名稱對應，**44 筆**尚無完全一致名稱。這是 identity crosswalk，不代表已確認公司與開發身份；例如 `Nolans Bore` 對應 `Nolans` 需要別名證據。

## 各州來源分層

| 州 | E1 來源紀錄 | E2/E3 延伸紀錄 | 已有官方 Parent Code 的 E1 Site | 官方 Project Layer E1 | E1 尚待 Project Crosswalk |
|---|---:|---:|---:|---:|---:|
| WA | 505 | 0 | 399 | 0 | 106 |
| SA | 131 | 47 | 0 | 3 | 128 |
| NSW | 51 | 119 | 0 | 0 | 51 |
| VIC | 30 | 34 | 0 | 0 | 30 |
| QLD | 38 | 2 | 0 | 0 | 38 |
| NT | 27 | 1 | 0 | 0 | 27 |
| TAS | 21 | 0 | 0 | 0 | 21 |
| **合計** | **803** | **203** | **399** | **3** | **401** |

## Evidence 路徑

- A. **Direct Project**：官方 Project Layer＋具名公司＋REE 商品／獨立開發描述。SA Koppamurra、Wudinna；Kalkaroo 建立 REE 產品角色審查。
- B. **Official Parent**：WA MINEDEX `proj_code`／`proj_title`；以唯一 Project Code 建立母群組，另核對持有人、開發者、REE 開發目標及期間，避免將一般稀土礦物 Site 視作獨立 Project。
- C. **Official external crosswalk**：NT Nolans、NSW Dubbo 可由現行政府 Project Listing 與地質名稱建立別名關聯。
- D. **Geological-only**：E1 其餘來源僅證明 REE 礦化或商品；逐州連結 Tenement、公司登記、勘探及開發文件後形成 Project 候選。
- E. **Extended inventory**：E2／E3 保留全部原始 ID 與來源，進行地質／礦床分析，不直接升格專案。

## 資料庫與稽核檔案

`all_1006_evidence_decisions.csv` 保留所有候選及篩選狀態；`provisional_project_groups_126.csv` 表示初步 Project 結構；`WA_121_official_parent_group_candidates.csv` 展開所有 WA 群組與 Site 數；`E1_project_unlinked_review_queue.csv` 為其他 401 筆；`legacy_203_crosswalk_audit.csv` 提供新舊名冊交集。`evidence_backed_review.sqlite` 保留原始候選、分群與核查案例表。

**資料庫寫入規則：**本次不自動增加 `project_master`、不依名稱／距離合併不同 Project，所有公司角色與 Project 身分皆保留證據審查狀態。

## 優先核查的官方專案例子

Koppamurra（SA Energy & Mining）；Wudinna（SA 官方 Developing Project Layer）；Yangibana（WA EPA）；Browns Range（WA EPA）；Mt Weld（WA EPA）；Nolans（NT developing projects）；Dubbo（NSW Resources）。詳見 `independently_checked_project_examples.csv` 的政府來源網址。