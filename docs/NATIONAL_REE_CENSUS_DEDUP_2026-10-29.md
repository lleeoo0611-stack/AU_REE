# 澳洲全境稀土資料母體｜來源篩選與去重規則（討論稿）

版本：`national-census-review-2026-10-29-r2`。研究目標：對澳洲稀土開發專案建立可追溯、穩定、不重複的 Project Master，並供後續 MCDA eligibility 使用。

## 一、分層收錄，不直接混算

| 層級 | 類型 | 儲存與角色 |
|---|---|---|
| L0 Raw | 官方 ArcGIS/WFS 原始圖徵 | 永久保留 native ID、原始欄位、原始快照 SHA-256、擷取時間與 query |
| L1 Evidence candidate | REE 直接目標／REE 礦物伴生／地質背景提及 | 保留所有初篩紀錄及篩選理由，不直接計入 Project Master |
| L2 Geological entity | Deposit、Occurrence、Prospect、Mine site、Tenement | 建立來源間 identity crosswalk；同一礦床兩來源可關聯，不代表開發專案重複 |
| L3 Development Project | 具備專案身分與母子地質實體關係 | 保有永久 `project_id`、別名、州別、營運者及證據；進入 Master |
| L4 MCDA Alternative | 通過 Current Activity／Feasibility／JORC／GIS／資料證據 Gate | 只有正式核准的可比條件才進入評分，缺值不可當作零分 |

`Project Master` 不是「所有稀土礦床的列表」。專案可以包含數個 Deposit/Mine site；同一 Deposit 可以有多筆官方觀測，不應各自計數。

## 二、篩選建議：保留寬母體，控制正式分析範圍

1. **E1 — 明確 REE 商品**：在 `commodity` / `major_comm` / `minor_comm` / `pri_comm` / `sec_comm` 等明確欄位出現 Rare Earths、REE、TREO、NdPr 等，進入稀土相關地質候選；但仍需獨立確認是否為開發 Project。
2. **E2 — 稀土礦物或礦砂伴生**：僅 Monazite、Xenotime、Allanite、Bastnäsite 等礦物名稱；記錄為 `REE_BEARING_MINERAL_ONLY`。需查明是否有獨立可回收 REE 資源或正式共產品計畫，才進 Project 主分析母體。避免將一般 Sn/W/重礦砂礦點都算成稀土專案。
3. **E3 — 地質背景提及**：僅地質分類、成礦模型、描述或名稱提到 REE；列為 `CONTEXT_ONLY`，優先留在佐證層，不自動升格為 REE Deposit。
4. **E4 — 排除無關**：不含任何可追溯 REE 證據的來源原始紀錄，保留在 Raw Manifest 與排除碼，不計入候選清單。
5. **E5 — Project identity**：官方 Project layer、公司技術揭露、JORC 報告、開發階段或政府項目資料可以建立正式專案關聯；僅同名或相距近不能通過此關。

## 三、去重：先重複「資料紀錄」，再處理「礦床身分」，最後才合併「專案」

| 順序 | 查核鍵 | 預設結果 |
|---|---|---|
| D0 | 同來源 + 同官方 native ID | 同一官方實體的重複回傳；留每次快照版本，不建立新實體 |
| D1 | 跨來源同一官方礦床代碼或已核對的交叉引用 ID | 合併 Geological Entity 層的來源觀測；原始紀錄不刪除 |
| D2 | 同州 + 標準化完全同名 + 高一致座標與商品資訊 | `POSSIBLE_SAME_DEPOSIT` 待人工確認，不自動合併 |
| D3 | 同一官方 `parent_project_code`／`proj_title` | 多礦床對一專案的 parent-child 關聯，**不得**將不同礦床視為一筆礦床，也不得重複加總資源 |
| D4 | 別名相似、營運公司可連接、位置約 5–25 km | `NEARBY_REVIEW`；只供稽核，**不是**去重充分條件 |
| D5 | 同名但跨州、公司不同或位置相差過大 | 保留為 `IDENTITY_CONFLICT`，由文件確認是否同一 project 或同名礦點 |

建議距離採階層式審查：≤ 1 km 為 *same deposit candidate*；1–5 km 為 *strong spatial review*；5–25 km 為 *regional review*。**距離門檻只排序審查優先序，不直接刪除或合併資料**。

名稱標準化可移除大小寫、標點及固定地名格式，但不能隨意刪除 `North/South/East/West` 或 `Deposit/Project`，因其可能代表不同礦床或母子層級。公司名稱為旁證，不是永久唯一 ID，因為專案可發生交易或 joint venture。

## 四、已完成的離線 Raw Replay（尚未納入 SA 新資料）

來源：GitHub 2026-10-29 `AU_REE_national_WFS_QA_round2.zip` 的官方原始 JSON、各 chunk SHA-256 Manifest 與五來源 SQLite；非公司網站人工編造。

- 原五來源 `REVIEW` 641 筆。
- 重新從原始 WFS 的 NSW 30,898、VIC 18,794、NT 2,105 筆圖徵執行獨立分層篩選，得到 NSW 114、VIC 40、NT 18 筆（172 筆）。
- 合計 **813 筆來源候選紀錄**，不是 813 個不同 REE 開發專案；同名、跨來源候選重複配對 **62 組**。
- WA 的 `proj_code` 暫分 **118 個母專案群**，仍需要逐組核對父子關係與活動／公司資訊。
- 203 筆 Frozen Project Master 與 19 筆歷史 MCDA cohort 保持不變，未升級現行 VERIFIED。

原始圖徵有各自時點與座標品質，例如 NSW MetIndEx 約 30,898 筆是地質點／歷史礦化記錄而不是 30,898 個現役礦山；必須以研究對象分類。

## 五、下階段資料庫與品質控制

建議追加 `source_feature_snapshot`、`geological_entity`、`project_geological_relation`、`identity_review_decisions`、`dedup_candidate_pairs` 五種資料表。每筆人工決策存 `decision`、`evidence_document_id`、`reviewer`、`reviewed_at`、`algorithm_version` 和來源 SHA。

GIS 一律以可核實代表座標為前提；跨州或邊界礦床用澳洲正式州界空間判定，再保留行政州別原文；不要以官方 WFS 的圖層歸屬就無條件覆寫州別。

正式 MCDA 可比較樣本沿用先前 r963–r983 與 proposal 的 Scoping/PFS/DFS、JORC、活動狀態與 evidence QA。GIS 未核准、AHP 未填、缺少正式值時保留空矩陣。

## 六、希望先確定的研究選擇

**建議主方案**：L0 保存全部官方礦點；L1 收錄全部 E1 與 E2、E3 作獨立背景附表；L3 Project Master 只收具有獨立 Project 身分的來源證據；L4 沿用嚴格 Eligibility Gate。這同時兼顧全澳調查的完整性與 MCDA Alternatives 可比性。

**待決策問題**：Monazite／Xenotime 僅列為伴生礦物、沒有 JORC REE 或獨立開發規劃的礦點，是否只留在 extended occurrence inventory？預設建議**是**，直到有進一步 REE materiality 證據再晉級。

資料來源：GA AIMR、GA Critical Minerals、WA MINEDEX、QLD MINOCC、TAS MRT、NSW MetIndEx、VIC MINSITE、NT MODAT WFS；SA SARIG 另行線上重擷取。完整 URL 與各來源版本請看專案 `config/sources.json` 與 `scripts/acquire_missing_states.py`。