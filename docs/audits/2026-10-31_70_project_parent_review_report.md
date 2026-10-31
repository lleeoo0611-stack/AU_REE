# P0 第六輪：70 筆僅有政府原生紀錄的證據審核

**審查日：2026-10-31；原始地質來源凍結於 2026-10-29。** 固定前期 [109 筆審核](2026-10-31_109_project_evidence_review.csv)中 `new_document_evidence_available=NO` 的 **70 個 source target IDs**。原始 487／272／156／109 層級、source/native ID、核准欄位與 MCDA 輸出不修改。所有有名稱的資料仍是 **source record → Deposit／Prospect → Project** 候選，並非 70 個獨立開發專案。

[70 筆逐筆審核 CSV](2026-10-31_70_project_evidence_review.csv) · [59 筆尚無具名歷史母專案文件的研究佇列](2026-10-31_70_project_evidence_pending.csv) · [25 個來源名稱的日期／定位登錄](../../inputs/source_review_20261031/round6_70_official_issuer_document_leads.csv) · [證據分布與 SHA manifest](2026-10-31_70_project_evidence_summary.json) · [可重跑腳本](../../scripts/audit_p0_70_project_parents.py)。

## 1. 70 筆全量來源／文件審核

| 審查結果 | Source rows | 證據意義 |
| --- | ---: | --- |
| 政府／公司原文支持歷史 Project–Deposit 候選 | **7** | 包含 2 Tower、1 Puwanapi、3 Ouyen 礦床、1 Jurien；須核實 Project extent、年度及 REE 角色 |
| 有政府歸檔報告的第三方全文索引，尚缺原始報告 bytes | **4** | Hopelands East 1、Hassell Beach 2、Witchcliffe 1；WAMEX 編號與歷史 Project 名稱已定位 |
| 有文件，但只能確認歷史礦權／相鄰地區／不同礦種，或行政區邊界需核查 | **8** | Benmara South 2、Bullant-Karridale、Jangardup South、North Dandalup、Kemerton 各 1，Wingellina 2；全部 HOLD |
| 增加官方地質／非 REE 主礦種／地區資料，未能建立 Project parent | **15** | 南澳 Cu/U、塔州沖積獨居石、西澳 HMS 地理資料、SA Eucla Basin 等 |
| 本輪無新增外部文獻，保留原始政府地質記錄 | **36** | 仍可由原生 ID、礦種／狀態與原始 source bytes／SHA 追溯 |
| **合計** | **70** | **34 筆增加外部文件線索；所有 Project/JORC TREO/C1 獨立核准均為 0** |

第二種「第三方全文索引」與第一種政府／公司原文應保持不同證據等級；外部文件網址與 report locator **尚非獨立封存 PDF 位元組或具有 reviewer signoff 的核准資料**。

### 歷史 Project／礦床從屬證據

| 來源目標 | 有文件的歷史候選範圍 | 來源與原文定位 |
| --- | --- | --- |
| **Tower（WA，2 列）** | Tower REE Deposit → **Mt Clere Project** | [Krakatoa ASX 2023-03-29](https://www.asx.com.au/asxpdf/20230329/pdf/45n40zttl1v5y5.pdf) p.1；黏土型 REE 探勘／資源公告；尚須原始 JORC category、cutoff、時點 |
| **Puwanapi（NT，1 列）** | Tiwi Islands historic EL24328 → Puwanapi HMS | [NTGS GEMIS 2012 CR2012-0338](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/89265)、[NTGS 2011 report](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/88315/1/GR051_2011_GA.pdf)；資源為 HM，非 TREO |
| **Galileo、Mercury、Titan（VIC，3 列）** | 歷史 **Ouyen HMS Project** 的三個礦床／靶區 | [Resource Equity 2004 independent report](https://www.recconsultants.com.au/PDFs/Bemax%2020040313.pdf) §12.8.1–12.8.3 p.52；不推定為 2026 年相同開發案 |
| **Jurien（WA，1 列）** | Jurien Mineral Sands Project M70/435 | [WA DWER L5319/1988/12](https://www.der.wa.gov.au/images/L5319-1988-12_-_Amendment_report.pdf)，Jurien 礦砂廠向 Cooljarloo 運送 concentrate；尚未證明 REE 產品 |
| **Hopelands East（WA，1 列）** | 歷史 Hopelands East HMS Project | [WAMEX A119194 二手索引](https://geothought.nlp-tlp.org/wamex/A119194)，2018–19 annual report，C35/1998；正式下載 WA government 原件後再升級 |
| **Hassell Beach（WA，2 列）** | 歷史 Hassell Beach HMS Project M70/562 | [WAMEX A120393 二手索引](https://geothought.nlp-tlp.org/wamex/A120393)，2018–19；4.54 Mt @11.9% 代表 **HM**，非 TREO |
| **Witchcliffe（WA，1 列）** | 歷史 Witchcliffe HMS Project E70/5471 | [WAMEX A129842 二手索引](https://geothought.nlp-tlp.org/wamex/A129842)，2022 surrender report；不能視為 2026 年仍在推進 |

## 2. 同名／行政區／礦種不相符的 HOLD（8 筆）

- **Benmara South，2 列（NT）**：[1991 NT GEMIS EL6836](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/71979) 提供歷史地名／礦權；[Transition Minerals 2023 Barkly](https://www.transitionminerals.com/wp-content/uploads/2023/11/231121-Barkly-Initial-MRE.pdf) 記載 Benmara South 探勘／採坑構想，但該總資源不能直接分配到 Benmara South，兩時期 title／polygon 仍待核。
- **Wingellina，2 列（來源記 SA）**：來源原始座標 **−26.0423782°、128.9380348°E**，位於 129°E 以西；[WA EPA Wingellina Nickel Project](https://www.epa.wa.gov.au/proposals/wingellina-nickel-project) 以 Ni–Co 為主要開發產品。需以官方州界及礦權圖資裁定 source jurisdiction，不能直接把本來源改成 WA Project 或當作 REE MRE。
- **Bullant-Karridale、Jangardup South、North Dandalup（WA，各 1）**：分別找到 [WAMEX A37443](https://geothought.nlp-tlp.org/wamex/A37443)、[Jangardup South 歷史探勘索引](https://www.nextmaps.com.au/exploration/nannup/jangardup-south)、[EPA Keysbrook](https://www.epa.wa.gov.au/sites/default/files/EPA_Report/1580_Bull1269_Keysbrook-291007.pdf) 的 Prospect／tenement／鄰近地理資訊，但**無法證明原 source feature 與該 Project footprint 同一**。
- **Kemerton（WA，1 列）**：政府 [Kemerton silica sand project](https://www.epa.wa.gov.au/proposals/kemerton-silica-sand-mining-proposal) 的主要礦種與本研究的 HMS／REE source 不相同，不當作稀土父專案。

## 3. 已補充官方地質證據，但不具可核准母專案（15 筆）

- **南澳 10 筆**：Mount Gee（1；鈾礦、Arkaroola 保護區）、Paratoo（2；銅礦為主）、Radford Creek North（2；銅礦為主）、Mount Victoria（2；鈾礦為主）、Armchair（2；鈾礦為主），再加 Eucla Basin（1；**多專案所處的地質盆地**）。官方 [南澳 REE overview](https://www.energymining.sa.gov.au/industry/minerals-and-mining/mineral-commodities/rare_earths) 明列 Jacinth–Ambrosia、Atacama、Sonoran、Typhoon 等不同開發案，不能把 *Eucla Basin* 字樣當作單一 Project ID。
- **塔州 2 筆**：Stronach、Yellowband Creek 的 [MRT 1947 Monazite report](https://www.mrt.tas.gov.au/mrtdoc/dominfo/download/UR1947_012_15/UR1947_012-15.pdf) 為沖積／礦物出現背景，原始政府來源 `RESOURCES=N`，沒有正式 REO 礦業專案。
- **西澳 3 筆**：Calypso（2）和 Perth Basin（1）可見 [GSWA 2026 Titanium brochure](https://www.wa.gov.au/media/159143/download?inline=) 地理／礦砂紀錄；Calypso 仍待 Project 範圍，Perth Basin 是區域名稱。

## 4. 尚無新增外部文件的 36 筆

| State | Source rows | 後續處理 |
| --- | ---: | --- |
| QLD | 10 | QLD occurrence site_no + 官方案卷及勘查歷史 |
| SA | 7 | SA MinDep source id、歷史營運狀態與 HMS/JORC 名稱 |
| NSW | 7 | 原始 GA 來源 deposit 與稀土產品／開發專案權屬 |
| WA | 6 | WA Project–Deposit／WAMEX 報告與 tenure／官方 Project polygon |
| VIC | 3 | 歷史 Murray Basin HMS 報告、source extent |
| TAS | 3 | MRT deposit ID 與原始 UR/TR technical reports |
| NT | 0 | 全 3 筆已找到外部地質或歷史 Project 資料 |
| **合計** | **36** | 均有原始 native target ID 和 geoscience source；**沒有獨立 Project 核准** |

本輪未核准的 70 筆均仍在 C0；當中 **59 筆**目前沒有足以建立具名歷史 Project parent 候選的文件（包含 8 HOLD、15 地質文獻及 36 原生紀錄）。更精確地說，**70 筆都尚需正式 Project boundary / REE/JORC Gate**，不能以 59 筆代替未核准總數。

## 5. 重現與可追溯性

```bash
python scripts/audit_p0_70_project_parents.py
python -m unittest discover -s tests -p test_p0_70_project_parents.py -v
```

腳本只讀前期 109-row 審查、272 原生圖徵 JSONL 與 25 名稱官方／公司／第三方原始文獻登錄，產生新版 70-row CSV、59-row 具名 Project evidence gap queue、逐輸入 byte-level SHA-256 summary。分層目錄遵循 `inputs/source_review_20261031`、`data/source_snapshots` 與 `docs/audits`；保留 source original bytes/provenance，**不以文獻索引 URL 取代原始 PDF SHA-256 與獨立 reviewer approval**。正式 C1 cohort、GIS、JORC 資源及 MCDA 未改。
