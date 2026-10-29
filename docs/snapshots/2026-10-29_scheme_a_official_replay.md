# 澳洲稀土 Scheme A Project Master｜官方快照重跑摘要

日期：2026-10-29。版本：`1.0.4`。研究母體採 Scheme A：獨立開發專案身分證據先於正式新增，礦物伴生留在擴充名冊。

| 資料集 | 數量 |
|---|---:|
| 歷史 Project Master | 203（均為 `LEGACY_UNVERIFIED`） |
| 官方原始物件快照（包含不同原始來源 ID／版本） | 62,573 |
| Project + 地質候選原始辨識紀錄 | 62,773（含 203 歷史來源紀錄） |
| 地質實體／擴充礦點名冊 | 641 / 641 |
| 跨來源候選去重配對 | 108 |
| 母專案／礦床暫定關聯 | 388 |
| 正式核准的新增 Project | 0 |
| 12 項準則、歷史觀測 | 12 / 220 |

稀土分級：E1 直接稀土商品 634 筆；E2 礦物伴生 4 筆；E3 名稱／背景線索 3 筆。

去重配對：EXACT_NAME_STATE 56 筆, WITHIN_1KM_REVIEW 52 筆。所有配對為 `PROPOSED_ONLY`；388 筆父子關係同樣待審查，不曾執行自動合併。

資料庫完整性：`PRAGMA integrity_check=ok`、外鍵違規 0。五階段已由這份封存的官方快照離線重跑完成。GIS 未核准的距離不計入正式準則；Eligibility Gate 和 R 輸入維持無合格真實排名。

原始來源：GA AIMR／Critical Minerals、WA MINEDEX、QLD MINOCC、TAS MRT。NT、SA、NSW、VIC 的 WFS／CSV 來源由獨立全澳擷取流程追蹤，這份快照的數量不代表全澳最終去重 Project 數。

資料庫與來源 SHA256、來源清冊及階段狀態見同目錄的 JSON Manifest；SQLite、CSV 與政府原始 JSON 均保存於研究資料工作包。
