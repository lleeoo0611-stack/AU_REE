# P0.1 — 487 筆 Census 來源的全量批次核查與母體分布

**批次審查日期：2026-10-31**；**凍結來源截止：2026-10-29**  
**研究單位：487 筆 source targets（86 Legacy + 401 E1）**，不可稱為 487 個獨立 mining Projects。  
**結果狀態：**`BATCH_EVIDENCE_INVENTORY_COMPLETE / C1_NOT_RELEASED`。本輪整合既有封存逐列來源、身分、礦權、公司與證據定位，**沒有新產生的逐文件獨立核准、JORC 資源觀測或 MCDA 分數**。

**本次交付**：[487 筆逐列可編輯 CSV](2026-10-31_census_487_batch_review.csv) · [機器可讀統計／來源版本](2026-10-31_census_487_batch_review_summary.json) · [可重跑腳本](../../scripts/build_p0_census_487_audit.py) · [39 個已先行查證群組](2026-10-31_project_source_screen_report.md)。

## 1. 批次納入資料與追溯方法

以 `target_id` **精確一對一**串接既有凍結檔：`487_full_census_adjudication.csv`、`487_inclusion_gate.csv`、`project_entity_membership_487.csv`、`source_entity_register_487.csv`、`487_official_tenure_trace_status.csv`、`company_entity_resolution_queue_487.csv` 與 `reconstructed_cohort_487.csv`；使用原 `project_entity_id` 對應 39-group source screen；以 `target_ids` 對接 95-row document locator review。每個來源檔的 Git blob SHA 與原始行數記載於 summary JSON；Python 重跑另在 summary 計算**實際讀取來源位元組 SHA-256**。

**資料繼承**：Census 原始裁定、Project 群組審查結論、source-native ID、原始座標基準與 hold 理由一律保留。新增僅為整合衍生 `action_priority`、`primary_review_action`、資料關聯/證據缺口與 `C1_NOT_RELEASED` 狀態，不修改 `outputs/` 歷史資料與 `inputs/verified_observations.csv`。

**核查完成的定義**：487/487 target_id 在全部規定來源檔出現、關聯鍵/州別/cohort 一致且可重現；**不是**所有 487 筆均已從現在的 ASX、政府、JORC 正本重新下載並獨立核定為 Project。

## 2. 完整母體的地理分布（source rows）

| State | 來源記錄 | 原 `INCLUDE_CANDIDATE` | 原 `HOLD_REE_ROLE` | 原身分/REE 證據不足 |
| --- | ---: | ---: | ---: | ---: |
| **SA** | 131 | 11 | 3 | 117 |
| **WA** | 127 | 4 | 0 | 123 |
| **NSW** | 56 | 8 | 1 | 47 |
| **NT** | 55 | 6 | 0 | 49 |
| **QLD** | 47 | 13 | 2 | 32 |
| **VIC** | 43 | 20 | 0 | 23 |
| **TAS** | 28 | 7 | 0 | 21 |
| **Total** | **487** | **69** | **6** | **412** |

SA + WA 為 258/487 來源列（約 **53.0%**）；這是凍結來源 inventory 的地理分布，不是可開發 REE Project 的權重分布。VIC 有 20 個 `INCLUDE_CANDIDATE` **來源列**，不能視為 20 個已核准 Project。

## 3. 地質實體與 Project 關係

| 原始 source entity type | Rows | 定義 |
| --- | ---: | --- |
| `DEPOSIT` | **323** | 礦床／地質母體，需找可證明的 Project parent |
| `OCCURRENCE` | **102** | REE 相關礦物出現，不直接等於可開發專案 |
| `SOURCE_PROJECT_RECORD` | **50** | 原來源記錄看似正式 Project，但仍須核對實際 project boundary |
| `HISTORICAL_RECORD` | **6** | 歷史資料，追溯 current Project 與公告日期 |
| `PROSPECT` | **6** | 探勘標的，需確認是否隸屬 Project |
| **Total** | **487** | 原始 source-level 分類，無自動升格 |

**Project 群組關聯：**78 rows 已有 `project_entity_id` → 39 個 reviewed Project groups；409 rows **未有**這種關聯，包含 283 Deposit、95 Occurrence、21 Source Project Records、6 Prospect 及 4 Historical Records。

39 群組本身的 source-check 類別（[2026-10-31 先前報告](2026-10-31_project_source_screen_report.md)）是：7 組已有 Study evidence、8 組 Stage/FID 待核、14 組主要 Resource/Exploration、7 組 REE role HOLD、2 組已非 pre-FID、1 組 Activity on-hold。這些值若映射到 78 source rows，分別是 9／20／37／9／2／1；**39 group counts ≠ 78 source row counts**。

### 未連結 409 rows 的 crosswalk 現況

| Source lineage／交叉索引狀態 | Rows | 後續行動 |
| --- | ---: | --- |
| E1 來源未建立 126-group 或 203 legacy parent 候選 | **305** | 先按州別與 entity type 找官方 Project parent 證據 |
| E1 來源與 legacy 203 存在候選 crosswalk | **49** | 核對 Project 範圍與相同資源的 parent/child |
| Legacy 來源已接到 1006 source crosswalk，但尚未有 Project group link | **37** | 檢查同一 Source Record 是否只是 Deposit/Occurrence |
| Legacy 沒有直接 1006/126 name-parent link | **18** | 依原始公告與歷史名稱建立候選關係，不按字串自動合併 |
| **合計** | **409** | 均保持 `UNLINKED`，保留 source-native ID |

## 4. 來源核對與空間／礦權證據

| 審查項目 | 狀態／Rows | 代表意義 |
| --- | --- | --- |
| 原生 source record 精確可重建 | **437** | 既有來源紀錄可依原生 ID 對應；尚未證明獨立 Project |
| Legacy 仍無精確原生 crosswalk | **35** | 原 Legacy ID 保留，待配對歷史來源 |
| Legacy 有 Project-level source link | **15** | 尚須獨立 Project approval |
| 有 95-row 文獻定位登錄的不同 target | **46** | 42 項可定位 Project-context 文字、3 項取回但未定位、1 項無法取得文內位置 |
| **無該 95-row 文獻定位登錄的 target** | **441** | 可有原始來源紀錄；表示尚無可直接引用的 Project-context 文件定位記錄 |
| Official spatial tenure intersects | **258** | 僅空間相交，titleholder/operator/ownership **未核准** |
| Official tenure layer not verified | **128** | 全部來自 SA，反映州別圖層核對缺口 |
| No overlap in queried layers | **51** | 只代表此次查詢範圍沒有相交 |
| No usable coordinate for tenure trace | **50** | 尚未有可用點位做此項比對 |

現有 487 筆包含來源層座標與獨立法律／GIS 關係不同的欄位；`OFFICIAL_SOURCE_POINT_UNVERIFIED_GEOMETRY` 不能直接當 Project approved coordinate，更不能推算 I1–I4 後發布正式 ranking。

## 5. 全母體審查佇列（只用來分配工作）

依已知 Source entity type、原納入 gate 和先前 39 群組篩查標記，對所有 487 筆產生互斥的 `action_priority`：

| Priority | Source rows | 審查工作 |
| --- | ---: | --- |
| **P1** | **29** | 已連至 Project group 且有 Study 證據／Stage 重大待核；先查公告日期、實際 FID、JORC REO 和 GIS |
| **P2** | **72** | 群組 REE role／Activity/Resource 待核，或未連結的 source-level Project／Historical Record |
| **P3** | **291** | 未連結 Deposit/Prospect，或已超出 pre-FID 而可作 C3 的來源 row；找 parent Project、避免重複計數 |
| **P4** | **95** | 未連結 Occurrence；保留 C0 地質母體，確認是否有 Project-level evidence |
| **合計** | **487** | Priority 是**工作順序**，不是 Project 可行性評分或 MCDA 排名 |

**工作優先建議：**先在完整 487 表中處理 P1 的 29 筆與 P2 的 72 筆（兩者合計 101 個**來源列**），可以較快確認正式 Project 身分與 C1 預備名單；同時對 P3 的 291 筆以 source ID、州別與 Deposit→Project scope 做可追溯的 group review，避免 1 筆礦床 1 個新 Project 的錯誤。

## 6. 下一個 Gate 與研究分流

1. **C0 Census 已有全 487 rows 可更新的審查矩陣**。其後每次 frozen source 變化需另建立 run date/SHA/CSV，不覆寫這份快照。
2. **C1** 必須先定稿 [六個納入 Gate](../P0_COHORT_SELECTION_PROTOCOL.md) 與六構面共同準則。39 群組有 Source Review evidence，但未有獨立批准；409 未連結應先解決 entity relationship，不能以 GIS 相鄰、Tenement 相交或 name similarity 自動升格。
3. **C2** 保留 REE 角色待查、Mineral Sands/HM/MzEq、未達 Scoping/PFS、Project 身分已確認但證據不完整的資料；對 Direct REO 與 REE 副產品進行 data availability/selection-bias 對照，是否正式拆分 C1 由研究決策記錄核定。
4. **C3** 可依發表日期保留已 FID／Construction／Production 的群組，用於歷史驗證；不可回填當代技術報告到早年快照。

**重現命令**（Python 3.11+，僅標準函式庫）：

```bash
python scripts/build_p0_census_487_audit.py \
  --root . --run-date 2026-10-31 --source-as-of 2026-10-29 \
  --output-dir work/audits
python -m pytest -q tests/test_p0_487_batch.py
```

新結果寫入 `work/audits/`（未追蹤），內附各 input 的**實際 SHA-256**；`docs/audits/` 保存本次發布的固定 CSV／JSON，後續不得改寫，需用新日期發布。CI 驗證 ID、來源鍵、歷史快照 equivalence、嚴格維持非核准狀態。

**最後研究判定：**487 row-level `P0_487_BATCH_REVIEW_V1` 完成；正式 `C1_PRIMARY_MCDA` 仍為 `NOT_RELEASED`。下一階段是**批次群組化資料庫的 Project/Deposit 關係與來源文件核准**，不是直接把 487 筆送入 MCDA。
