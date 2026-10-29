# 澳洲稀土母體｜86＋401 全境礦權與公司反向追溯（2026-10-29）

## 母體與執行版本

- 輸入：歷史 `Project Master` 未重疊的 86 筆、1,006 候選版內未連結 Project 的 E1 401 筆，共 487 個追溯目標。
- 基準資料：2026-10-29 政府全澳原始資料快照；獨立查詢政府礦權現行、申請和歷史空間圖層。
- 結構：Site/Deposit → official Tenement → Registered Holder Candidate → Developer/Project 官方文件 → 人工身份審查。
- 統計單位：目標紀錄、空間交集、持有人名稱、官方專案證據各自統計。

## 官方來源查詢結果

| 州 | 追溯目標 | 有礦權交集 | 有較嚴格現行／核准礦權 | 官方 SA Project–Deposit 連結 |
|---|---:|---:|---:|---:|
| WA | 127 | 93 | 77 | — |
| SA | 131 | — | — | 20 |
| QLD | 47 | 22 | 21 | — |
| NSW | 56 | 51 | 38 | — |
| VIC | 43 | 30 | 23 | — |
| NT | 55 | 45 | 23 | — |
| TAS | 28 | 17 | 14 | — |
| 合計 | 487 | 258 | 196 | 20 |

共 764 條官方礦權交集，201 組原始持有人文字值（名稱不是法人唯一 ID）。

## Evidence-back 群組進度

- 12 筆歷史 86 項目具有可直接查核的政府 Project–Company 文件例證（不是新增 12 個 Project）。
- 20 筆 SA E1 紀錄在封存的 SA Geodata／官方 Project 資料中可追溯 Project–Deposit，其中 16 筆可用礦床原始 ID；其餘 4 筆用同名索引，需審查。
- 196 筆目標具有現行／核准的 Tenement 交集，可用於候選持有人對照。
- `Project Master` 本輪新增、合併、刪除數均為 0；所有公司與 Project 對照保留審查欄位。

## 身分辨識規則

1. 官方法人登記的 **Registered Holder／Applicant** 為礦權角色，與現行 **Developer／Operator／Owner** 分開。
2. NSW 的 `Granted`、`Historic`、`Applications` 分圖層；VIC 依 tenure 原始狀態；NT 僅納入 **MineralTenement** 而不含 petroleum；WA、QLD、TAS 依各自狀態欄位。
3. SA 以官方 `MINERAL_DEPOSIT_NUMBER` 與 Project 圖層連結，並將只有名稱關聯的項目獨立標示。
4. Project 最終合併需有公司技術報告、JORC／礦權合法持有人與開發工作證據，通過審查後才新增或更新主檔。
5. `LOCATION_NEEDED`、`SA_TENEMENT_SOURCE_PENDING`、`NO_OFFICIAL_TENEMENT_INTERSECTION_ON_QUERY_DATE` 分開保存。

## 可重跑內容

- `reverse_trace_targets_487.csv`：固定 86+401 個目標與座標來源。
- `487_target_resolution_matrix.csv`：每筆審查結果與官網連結。
- `official_tenement_holder_candidates.csv`：764 筆礦權來源對應、公司名稱與時間狀態。
- `sa_official_project_deposit_crosswalk.csv`：SA 20 筆官方 Project/Deposit 連結。
- `independent_government_project_company_evidence.csv`：12 筆歷史專案的官方 Project–Company 證據。
- `reverse_trace_review.sqlite`：以上對照表的 SQLite 版本。
- `run_official_tenement_queries.py`：官網 ArcGIS/WFS 空間查詢執行程式。
- `build_reverse_workpack.py`：從查詢紀錄與 SA Crosswalk 重新建立審查表。
- `AU_REE_487_nationwide_tenement_holder_trace_corrected_2026-10-29.zip`：官方空間查詢來源輸出。

來源目錄與資料庫驗收資訊見 `official_tenement_source_catalog.json`、`reverse_trace_final_summary.json`。
