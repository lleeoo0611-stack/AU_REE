# P0 P1｜48 筆具名來源去重、Project–Deposit 與 REE 資源基準核查

**完成日期：2026-10-31｜來源快照截止：2026-10-29｜審查母體：先前 P1 的 48 筆 `PARENT_CANDIDATE`。**

## 1. 去重結果

- **48 筆來源紀錄 → 39 個州別＋來源名稱鍵 → 25 個可追蹤的暫定 Project 母層群組**。
- `P1G-0001`–`P1G-0025` 為固定的**審查群組鍵**，不作正式 `project_master.project_id`。
- 來源記錄重複在 group 下保留全部 `target_id`、`source_native_id`、原始 SHA、來源經緯度及文件定位。相同名稱鍵不是經核准的相同礦床。
- **Willandra West**（8 列；6 個名稱鍵；來源點最大距離 37.966 km）與 **Willandra East**（5 列；5 個名稱鍵；52.138 km）屬歷史區域性分組；維持兩個不同母層，待歷史礦權與 Project polygon 查核。
- 本輪完成**來源點空間分散度 QA**，未完成政府 Project／tenement polygon 的逐點幾何交集（本次交集核准 0/48）。原始點位與群組平均位置均不升格為正式 Project representative point。

### 25 個審查群組與來源

| Group ID | 暫定 Project 母層 | Source rows／名稱鍵 | REE 資源證據 | 原始點最大分散距離 |
|---|---|---:|---|---:|
| `P1G-0001` | Willandra West / Twelve Mile historical HMS area | 8（6 個名稱鍵） | REE 資源尚待補 | 37.966 km |
| `P1G-0002` | Willandra East / Prungle historical HMS area | 5（5 個名稱鍵） | REE 資源尚待補 | 52.138 km |
| `P1G-0003` | Copi Mineral Sands Project | 1（1 個名稱鍵） | REE 產品／角色來源 | 0.000 km |
| `P1G-0004` | Tiwi Islands Puwanapi historical exploration | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0005` | Korella Bore project prospectus | 2（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0006` | Ouyen historical mineral sands project | 3（3 個名稱鍵） | REE 資源尚待補 | 9.753 km |
| `P1G-0007` | Fingerboards Critical Minerals Project | 1（1 個名稱鍵） | REE 產品／角色來源 | 0.000 km |
| `P1G-0008` | Nowie (VHM) Project | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0009` | Wemen mineral sands historical mine | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0010` | Aileron Niobium–REE Project | 1（1 個名稱鍵） | 具 TREO 資源數值 | 0.000 km |
| `P1G-0011` | Coburn mineral sands operation | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0012` | Cooljarloo mineral sands operation | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0013` | Cyclone Mineral Sands Project | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0014` | Dongara Titanium Minerals Project | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0015` | Governor Broome Mineral Sands Project | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0016` | Happy Valley Titanium Minerals Project | 2（2 個名稱鍵） | REE 資源尚待補 | 2.641 km |
| `P1G-0017` | Jurien Mineral Sands Project | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0018` | Keysbrook Mineral Sands Mine | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0019` | Mount Ridley / Grass Patch complex (Mia) | 2（1 個名稱鍵） | 具 TREO 資源數值 | 0.005 km |
| `P1G-0020` | Mulga Rock Uranium Project | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0021` | Redlings Rare Earths Project | 6（3 個名稱鍵） | 具 TREO 資源數值 | 4.096 km |
| `P1G-0022` | Fraser Range / Talisker Project (separate Salazar) | 1（1 個名稱鍵） | REE 鑽探品位、無 MRE | 0.000 km |
| `P1G-0023` | Mt Clere Project / Tower Deposit | 2（1 個名稱鍵） | 具 TREO 資源數值 | 0.000 km |
| `P1G-0024` | Yalyalup mineral sands project | 1（1 個名稱鍵） | REE 資源尚待補 | 0.000 km |
| `P1G-0025` | Mt Stirling Project / Yttria Deposit | 2（1 個名稱鍵） | 具 TREO 資源數值 | 3.697 km |

## 2. REE 資源分層與數值核對

25 個群組中：
- **5 組**有可追溯 TREO 資源數值（Aileron、Mount Ridley／Mia、Redlings、Mt Clere／Tower、Mt Stirling／Yttria）。
- **2 組**有文件支持 REE 產品／共同商品角色，但目前參考資源主要為 **HM**（Copi、Fingerboards）。
- **1 組**只有 REE 探勘交集而無來源範圍相容的 JORC MRE（Fraser Range／Talisker）。
- **17 組**留存礦砂、歷史開發、原生地質及礦種來源，REE 產品／TREO 資源仍待核對。

**14 筆可編輯資源主張**中，10 筆 grade basis = TREO，2 筆 = HM，另 2 筆為 2026 年更新的 Nb₂O₅ 資源。此為**statement rows**，包含資源總量、子集合、分項、不同範圍及未註明日期版本，不能直接算成 12 個可加總的 REE 資源。

| 群組 | 附日期之資源主張 | cut-off | 去重與基準判定 |
|---|---|---|---|
| `P1G-0010` Aileron（Green／Emily／Crean） | 67.6 Mt @ 0.39% TREO | 0.25% Nb₂O₅ | 67.6 Mt 中包含 19.2 Mt 高品位子集，不能加總 |
| `P1G-0019` Mount Ridley／Central Mia | 168 Mt @ 1,201 ppm TREO | 750 ppm TREO | 只屬 Mia；另有未確認日期的 Grass Patch 122.5 Mt @ 889 ppm 資料，暫停混加 |
| `P1G-0021` Redlings | 11 Mt @ 1,130 ppm TREO | 800 ppm TREO | 6 筆資料來自 Jungle Well 1–3，不能各自配分 11 Mt |
| `P1G-0023` Mt Clere／Tower | 101 Mt @ 840 ppm TREO | 300 ppm TREO–CeO₂ | 另有 801 ppm 的未標日期公司頁面，須核對版本 |
| `P1G-0025` Mt Stirling／Yttria | 15 Mt @ 490 ppm TREO | 200 ppm TREO–Ce | 包含 Indicated 7.7 Mt 和 Inferred 7.3 Mt，不重複計數 |

### 重要來源與 Project–Deposit 邊界證據

1. **Copi North → Copi**：[NSW 2019 政府專案目錄 §3.6](https://www.resources.nsw.gov.au/sites/default/files/2022-11/future-of-minerals-in-nsw-report-appendix-dec-2019.pdf) 直接點名 Copi North 與 Sunshine 等礦床屬於歷史 Copi Project；該份表格 **39.1 Mt @ 4.5% HM** 為重礦物資源，不作 REO。NSW [現行專案目錄](https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects) 列 REE 為其他產品。文字關聯已定位，現行法定 Project footprint 還需圖層交集。
2. **Aileron → Green／Emily／Crean**：[Encounter 2025-05-14 JORC Table 2](https://www.encounterresources.com.au/download/4/announcements/1887/inferred-niobium-mineral-resource-from-2024-exploration-drilling.pdf) 明列三礦床及 67.6 Mt @ 0.39% TREO（以 0.25% Nb₂O₅ 為資源 cut-off）。19.2 Mt @ 0.65% TREO 是其中的 **高品位子集**。[Encounter 2026-04-22 更新公告](https://www.marketindex.com.au/asx/enr/announcements/aileron-resources-grow-by-over-50-to-120mt-6A1321405) 已將鈮資源更新為 **120 Mt @ 0.77% Nb₂O₅**，其中 26 Mt @ 1.7% Nb₂O₅ 為子集。上述最新數值是 Nb₂O₅ 而非 TREO；2025 TREO 品位不能直接套用至 2026 更新後的資源範圍，需取得 2026 MRE 表內的 REE 同範圍分項。原始 `Aileron` source feature 的實體層級仍待對照，不任意建成第四個礦床。
3. **Mia → Mount Ridley**：[2024 年公司年報 Table 1／Figure 5](https://announcements.asx.com.au/asxpdf/20240920/pdf/068421026p0kt4.pdf) 支持 Mia 的 168 Mt @ 1,201 ppm TREO（750 ppm TREO cut-off），與整體 Mt Ridley／Grass Patch 資源尺度分開。
4. **Redlings**：[公司資源主張](https://www.marqueeresources.com.au/redlings-rare-earths-project) 11 Mt @ 1,130 ppm TREO（800 ppm TREO cut-off），列於 E37/1311、五個已鑽探 prospects。來源 Jungle Well 1–3 的六列屬三個名稱鍵；尚未配給各自礦量。
5. **Tower → Mt Clere**：[Krakatoa 2023-03-29 ASX](https://www.asx.com.au/asxpdf/20230329/pdf/45n40zttl1v5y5.pdf) 101 Mt @ 840 ppm TREO；[公司現行頁](https://ktaresources.com/projects/mt-clere/) 為 101 Mt @ 801 ppm TREO。將兩個版本分開登錄，待原始 JORC statement 與有效日期說明差異。
6. **Yttria → Mt Stirling**：[Asra 2025-07-31 JORC table](https://announcements.asx.com.au/asxpdf/20250731/pdf/06mdccyq4dppkh.pdf) 15 Mt @ 490 ppm TREO，包含 Indicated 7.7 Mt @ 480 ppm 和 Inferred 7.3 Mt @ 500 ppm，cut-off 為 **200 ppm TREO–Ce**。Total 僅作驗算，不與分項重複加總。
7. **Glenaladale → Fingerboards**：[Resources Victoria](https://resources.vic.gov.au/landholders-and-community/key-site-updates/fingerboards-mineral-sands-project) 記載 RL2023／RL2026 及 2026 更新版 EES；[州級專案資料](https://resources.vic.gov.au/geology-and-data/industry-investment/mineral-resources-development/Current-Mineral-Projects-and-Selected-Occurrences-2025-10-20-Web.pdf) 2,740 Mt @ 1.95% HM，仍需 Project 圖層與 REO 資源同範圍對照。
8. **Talisker／Fraser Range 與 Salazar**：[West Cobar 2025-08-14 ASX](https://announcements.asx.com.au/asxpdf/20250814/pdf/06mvmb9r2vhdhs.pdf) 指兩個 Project 相鄰、礦權不同。Talisker 的 TREO 探勘交集不繼承 Newmont、O'Connor 的 Salazar JORC 資源。

## 3. 地理邊界與審核

- **文字層級**：官方或發行人報告指明部分 Deposit/Prospect 位於既有 Project 內；詳見逐列 `documentary_parent_relation` 與逐母層 `boundary_evidence_class`。
- **來源座標 QA**：48 筆均連回原始 487 層之來源坐標，計算同名點間與同母層內最大距離。
- **政府 polygon 核准**：目前 0 筆。後續使用 [WA DMIRS 官方 Mining Tenements Polygon](https://services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Industry_and_Mining_WFS/MapServer/3)、[WA TENGRAPH](https://www.wa.gov.au/service/natural-resources/mineral-resources/access-tengraph-web)、NSW 官方專案圖層與 VIC EES／Retention Licence 圖件進行 `point-in-polygon`，須同時核對圖層發佈日期與權利期限。

## 4. 產出與重跑

- [48 筆 Project–Deposit source crosswalk](2026-10-31_p1_48_source_parent_crosswalk.csv)
- [25 個暫定母層去重表](2026-10-31_p1_25_provisional_parent_groups.csv)
- [14 筆原始數值、cut-off／套疊關係與 REE/HM 判讀](2026-10-31_p1_48_resource_basis_review.csv)
- [機器 QA 統計](2026-10-31_p1_48_dedupe_summary.json)
- [固定母層候選輸入](../../inputs/source_review_20261031/p1_48_parent_group_evidence.csv)／[固定資源主張](../../inputs/source_review_20261031/p1_48_resource_claims.csv)
- [純標準函式庫 Python](../../scripts/audit_p0_p1_48_dedupe.py)／[回歸測試](../../tests/test_p0_p1_48_dedupe.py)

```bash
python scripts/audit_p0_p1_48_dedupe.py --check
python -m unittest discover -s tests -p 'test_p0_p1_48_dedupe.py' -v
```

**P0 階段：**完成固定來源 ID 去重、附日期資源基準分層與待審 GIS scope；`project_master`、`JORC_approval`、`C1` 均維持原狀。
