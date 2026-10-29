# 澳洲全境礦產原始資料優先收集流程

## 研究母體建構順序

```text
官方原始服務與公開全州資料包
        ↓
全量分頁下載／保留原始 CSV、JSON、全部商品、全部礦點
        ↓
各來源行數、分頁 ID、SHA-256 與涵蓋範圍完整性驗收
        ↓ 只有 National Raw Gate = PASS 才放行
REE 商品與含稀土礦物分層篩選
        ↓
Geological Entity 身分解析與去重候選
        ↓
獨立核准 Project Master（方案 A）
        ↓
GIS / MCDA eligibility / R-MCDA
```

## 原始資料收集範圍

| 行政範圍 | 原始官方來源 | 保存格式 | 完整性檢查 |
|---|---|---|---|
| Commonwealth | GA AIMR REE；Critical Minerals deposits | 原始 ArcGIS Metadata、IDs、Feature JSON | 每筆 ID／分頁與 SHA-256 |
| WA | MINEDEX | 原始 ArcGIS 全圖徵 | 每筆 ID／分頁與 SHA-256 |
| QLD | MINOCC | 原始 ArcGIS 全圖徵 | 每筆 ID／分頁與 SHA-256 |
| TAS | Mineral Resources Tasmania | 原始 ArcGIS 全圖徵 | 每筆 ID／分頁與 SHA-256 |
| NSW | NSW MetIndEx WFS | 原始 GeoJSON | numberMatched 與所有分頁 SHA-256 |
| VIC | Victoria MINSITE WFS | 原始 GeoJSON | numberMatched 與所有分頁 SHA-256 |
| NT | NT MODAT WFS | 原始 GeoJSON | numberMatched 與所有分頁 SHA-256 |
| SA | SA Geodata 礦床主檔、商品、礦物、文獻四個全州 CSV | 原始官方 CSV | S3 來源清冊 Size、日期與 SHA-256 |
| SA 開發專案 | SARIG Major／Developing Project 和 Critical Minerals WFS | 原始官方 CSV | CSV 行數、檔案 SHA-256 |
| ACT | GA 全國圖層 | 與 GA 原始圖徵共同保存 | 註明屬全國圖層涵蓋，未將其認作獨立州級資料庫 |

### 來源定義

本階段下載的原始資料**不施加 REE 關鍵字、活動狀態、JORC、開發階段或 MCDA 資格條件**。
`RAW_COMPLETE` 表示對單一官方資料集取得完整圖徵，不代表礦床已驗證為獨立開發專案。

`scripts/acquire_national_raw.py` 產生 `work/national_raw/national_raw_manifest.json`；
`scripts/verify_national_raw.py` 產生 `raw_validation.json`；
來源未齊、官方分頁不完整或 SHA-256 不符時，篩選管線不得開始。

### 版本控制與結果

程式與資料庫 schema 由 Git 管理。原始政府位元組、SQLite 與衍生工作資料使用單獨的不可變原始快照；SHA-256、版本、來源日期與取得方式可從 `national_raw_manifest.json` 回溯，後續 Stage 01–05 僅讀取通過驗收的原始快照。

GitHub Actions: `.github/workflows/national-raw-first.yml`。

### Scheme A 身分規則

全國原始資料驗收完成後，E1（明確 REE 商品）進候選層；
E2（Monazite、Xenotime 等含稀土礦物）進 Extended Occurrence Inventory；
E3（地質背景線索）進輔助層。任何新的 Project Master 均須具備開發專案身分的獨立來源核准，名稱相似或近距離不會自動合併。
