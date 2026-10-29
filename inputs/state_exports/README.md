# 州政府資料匯入 — 已啟用，等待官方匯出

下列四個州的公開服務已建立來源登錄，但尚未選定經實測的可直接取得之單一 CSV 端點。
缺少資料時，管線會在 `source_registry.fetch_status` 顯示 `AWAITING_OFFICIAL_EXPORT`，**不會標記下載成功**。

| 州 | 本地檔案 | 官方發布系統 | 建議取得項目 |
|---|---|---|---|
| NT | `nt_modat.csv` | NT MODAT / STRIKE | Mineral Occurrences，保留來源 site ID |
| SA | `sa_sarig.csv` | SARIG（Mining Projects 與 MINDEP） | 需同時保留 Project/Deposit 層級 |
| NSW | `nsw_minview.csv` | MinView / GSNSW WFS | 礦產紀錄與稀土相關專案 |
| VIC | `vic_minsite.csv` | DataVic MINSITE / GeoVic | 礦產紀錄與專案關係 |

CSV 必須取自政府匯出檔或經可追溯的 ETL 轉製（保留原始檔、URL、日期、SHA-256）。
建議欄位：

`native_id,name,company,state,latitude,longitude,commodity,entity_level,source_url`

附加欄位 `project_name_hint,activity,deposit_family` 可保留，但**不會自動視為核准的 Activity、Lifecycle 或 GIS 坐標**。

`entity_level` 僅用 `PROJECT,DEPOSIT,OCCURRENCE,PROSPECT,TENEMENT,UNKNOWN`。
標為 `PROJECT` 的官方報告紀錄如無其他證據，也只納入未核准母體，不能因此通過 Stage 04。
