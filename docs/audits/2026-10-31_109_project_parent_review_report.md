# P0 第五輪：109 筆未找到 Project 母層的逐筆證據審核

**審查日期 2026-10-31；原始政府來源截點 2026-10-29。** 本輪固定 [156 筆審查](2026-10-31_156_project_parent_evidence_review.csv)中 `NO_INDEPENDENT_PROJECT_PARENT_DOCUMENT_FOUND` 的 **109 個 source target IDs**；原始 487／272／156 母體、核准規則與 MCDA 評分均不修改。

[109 筆完整可編輯證據表](2026-10-31_109_project_evidence_review.csv) · [89 筆仍無具名 Project 母層候選／有範圍疑慮的待查清單](2026-10-31_109_project_evidence_gaps.csv) · [機器可讀統計與輸入 SHA-256](2026-10-31_109_project_evidence_summary.json) · [31 個跨來源文件名稱線索](../../inputs/source_review_20261031/round5_109_documented_project_deposit_leads.csv) · [重現程式](../../scripts/audit_p0_109_project_parents.py)。

## 1. 109 筆全量審查結果

| 證據分級 | Source rows | 判定 |
| --- | ---: | --- |
| 有具名歷史 Project／Deposit 關聯文件，可建立候選父層 | **20** | 7 筆具直接 issuer／政府 Project 描述、13 筆在 CSIRO 歷史 Project 分組中；仍須核實地理與有效日期 |
| 有相關文件但僅為名稱、歷史礦權或區域關係，或兩個官方同名來源座標衝突 | **10** | **8 筆**名稱／scope HOLD，加 **2 筆** Ambergate spatial conflict；不建立自動父層 |
| 有獨立地質／重礦砂礦床文件，但沒有 Project 關聯 | **9** | 只提高礦床記錄的來源深度，保留 C0 |
| 沒有新增外部文件，仍以政府來源原始圖徵為證據 | **70** | 已有原始 ID、source-feature locator 與原始 SHA；需再查 Project 與稀土角色 |
| **合計** | **109** | **39 筆有新增外部文獻線索；Project/JORC/C1 正式核准均為 0** |

**109 筆按州分布**：NSW 33、WA 33、SA 19、QLD 10、VIC 6、TAS 5、NT 3。來源型別涵蓋 GA AIMR 67、GA Critical Deposits 15、SA 14、QLD 8、TAS 5 筆。原生資料中 `Heavy mineral sands`、`Clay-hosted`、`Deposit`、`MINERAL_DEPOSIT_NO` 只能支持礦床實體、礦種與原始地質紀錄；不代表有經營主體／JORC 資源聲明／pre-FID 專案。

**20 source rows ≠ 20 Projects**。Yttria、Mia、Brigantine、Doubloon North 等在 GA 不同來源重複出現，應保留 source ID 並在獨立核對後建立一對多 Project–Deposit–source 關係。

## 2. 新增外部文件：可建立歷史母專案候選

| 地區與原始礦床 | 文件支持的 Project 關係 | 來源、原文定位與判定 |
| --- | --- | --- |
| **WA Yttria**（2 筆） | Yttria REE Deposit → **Mt Stirling Project** | [Asra 2023-09-04 ASX](https://wcsecure.weblink.com.au/pdf/ASR/02707045.pdf) p.1 明示 Yttria clay-hosted REE 礦床在 Mt Stirling Project；屬稀土實際探勘／試驗線索 |
| **WA Mia**（2 筆） | Mia/Marvin targets → **Mount Ridley REE Project** | [Mount Ridley 2023-03-30 ASX](https://announcements.asx.com.au/asxpdf/20230330/pdf/45n5qsg8v6mcty.pdf) p.1：30-km Mia–Marvin mineralised trend、鑽探 REE 品位；無研究級 JORC Mineral Resource |
| **WA Ambergate**（2 筆） | 官方/公司名稱候選 **Ambergate HMS Project**；**本輪已暫停兩筆身分配對** | [SER 2025-03-13 disclosure](https://company-announcements.afr.com/asx/ser/8f66274a-ff91-11ef-9dde-fa1e67b8f469.pdf) 記載 11.2Mt @ 5.1% HM、重礦物 0.6% monazite；但同名原始資料座標相距 38.738 km，需查清才可建 parent |
| **WA Happy Valley North/South**（各 1 筆） | Happy Valley 的南北礦床 → **Happy Valley Titanium Minerals Project** | [WA EPA Assessment 1629](https://epa.wa.gov.au/en/proposals/happy-valley-titanium-minerals-project) 提及 northern/southern two deposits；**礦砂 ≠ 經核准 REO 產出** |
| **WA Governor Broome**（1 筆） | Governor Broome deposit → **Governor Broome Mineral Sands Project** | [Astro 2013-10-18 ASX](https://announcements.asx.com.au/asxpdf/20131018/pdf/42k3vp6pvzkp31.pdf) 獨立技術報告 printed p.12：contiguous tenements、一個 Project；須重驗 2026 經營、REE 副產品與實際資源基準 |
| **NSW Birthday Gift、Blind Pew、Brigantine、Doubloon North、Trelawney、Triangle**（8 來源列） | 歷史 **Willandra West / Twelve Mile mineral sands** 分組 | **CSIRO EP14184 (2014)** Appendix，printed pp.109–110 明列各 deposit 在 Willandra West/Twelve Mile 之下；為歷史 grouping，不能填入當代 Project polygon |
| **NSW Byrnes Tank、Finigans Tank、Coliban、Wakool、Campaspe**（5 來源列） | 歷史 **Willandra East / Prungle** 分組 | 同一 CSIRO 報告 Appendix printed pp.109–110，列 Willandra East (Prungle) 下多個 deposits；當代母專案與原始礦權未核准 |

CSIRO 研究文獻資料：Sparrow, Pownceby, Smith & Bruckard (2014), *Review and Assessment of Technology Issues Related to Processing of Murray Basin Mineral Sands*, Report **EP14184 / GA archive G171659**。原始來源登錄 [CSV](../../inputs/source_review_20261031/round5_109_documented_project_deposit_leads.csv)含 GA 原始 S3 object key；公開檢索時取得的是時效性簽名下載連結，**本次未將整份 PDF byte archive 與獨立 SHA-256 封存**，日後原文核准應重新向 GA/CSIRO 取得可永久引用檔案。摘要中的資源多為 **HM／THM**, 不可直接推算 TREO、NdPr 或獨立 REE JORC 量。

## 3. 10 筆有文件但不能建立 parent 的來源

- **2 筆 Ambergate（WA）**：聯邦 GA AIMR 的官方點位 **−33.71137, 115.306294**，GA Critical Deposits **−34.027115, 115.128998**；兩來源同州同名，相距 **38.738 km**，因此 `SPATIAL_IDENTITY_CONFLICT_PARENT_WITHHELD`。需要 Project footprint、歷史 Datum、礦床子區／類別原始備註，不能直接合併為同一資源。
- **3 筆 Gwindinup North／South（WA）**：[WA EPA Gwindinup Mineral Sands Mine](https://epa.wa.gov.au/proposals/gwindinup-mineral-sands-mine) 有正式提案，但未明示 North/South source feature 是否位於批准 Project 區界。
- **1 筆 Scott River（WA）**：Scott Coastal Plain 是地理／探勘區域，不代表 Scott River 礦床一定隸屬 Governor Broome。
- **NSW Barda、Cavalier（2 筆）、Western Strands**（4 筆）：CSIRO 列歷史 Tenement/Project 區域；Western Strands 和同報告 *Western Sands* 的名稱是否為同一 deposit 需要原始座標核對。**Tenement ≠ Project**。

## 4. 跨來源同名與座標核對：可執行去重線索

- **44/109** source rows 在全 487 母體內有同州同名紀錄。
- **42 筆**可在凍結的 272-source JSONL 中找到兩端原始座標，計算來源點的 WGS84 球面距離（haversine）。
- **38 筆**至少有一個同名原始來源距離 **≤ 1 km**，為優先的 Deposit 重複觀測候選；不能直接把兩筆 source records 視為兩個獨立 Project。
- **2 筆 Ambergate** 差異 **38.738 km**，應列優先人工核對並禁止無依據的自動同名合併。

這個地理檢查是**查核同一 Deposit 的可能性**，沒有基於鄰近距離直接判定 Project 身分。對其餘沒有可用雙端原始座標的紀錄，保留 missing/incomparable 而不填零。

## 5. 接下來的 Gate

| 目前證據 | 下一階段操作 |
| --- | --- |
| 20 筆有歷史 Project parent 文獻 | 對照官方 Project extent、Tenement titleholder 時間切片、最新 Stage/FID、稀土開發產品與原始 JORC 聲明 |
| 10 筆有 scope、Tenement 或身分衝突 | 以官方 source feature 坐標與 Project polygon 做獨立核對；Ambergate 先解決 38.7 km 衝突 |
| 9 筆有獨立 Deposit／HMS 文件 | 留存地質資料庫 C0，除非找到正式 parent，不能升格 |
| 70 筆仍只有原生資料 | 先查 NSW/WA 來源是否已有 Project-tenement 報告；SA 多金屬／U 主礦種與 REE 的產品角色分開核對 |

**完整 109 筆已逐列有來源與判讀，沒有額外新 Project/JORC/C1 正式核准。**

## 6. 可重複執行

```bash
python scripts/audit_p0_109_project_parents.py
python -m unittest discover -s tests -p test_p0_109_project_parents.py -v
```

執行時讀取 156 母體、272 原生 JSONL、487 來源列和 31 個外部來源名稱對照，輸出 109-row full audit、89-row pending Project relations CSV、SHA-256 summary JSON；所有輸出維持可編輯。每次來源變動須用新日期或版本的輸入，不得覆寫已發表的舊快照。
