# P1 未結證據與 P2 28 筆的公開資料複核（2026-10-31）

**資料截止：2026-10-29；本輪公開資料核查：2026-10-31**  
**研究成果層級：來源／案例文件審查；正式 Project–Deposit 身分與 JORC／GIS／六構面 Gate 獨立保留。**  
本次依固定 487-source census、412 個原 HOLD 與 [P0/C1 protocol](../P0_COHORT_SELECTION_PROTOCOL.md) 執行。**沒有寄信、沒有登入非公開服務，也沒有修改 412 筆原始優先分層。**

## 1. 本輪可核對的成果分母

| 項目 | 個數 | 說明 |
|---|---:|---|
| P1 原始查核範圍 | 73 source rows／44 案 | 原有來源查核不重跑、不覆寫 |
| P1 尚待證據取得／核准部分的公開查核 | **31 source rows／19 案** | 22 個正向來源、4 個身分衝突來源、5 個 WAMEX 索引來源 |
| P2 原始範圍 | **28 source rows／27 案** | 22 Legacy + 6 E1，包含 Mary Kathleen 同站址 2 原生 deposit rows |
| P2 已指定來源查核與互斥文件處置 | **28／28 source rows** | 每筆有來源定位、範圍結論、下一步；本輪公開文件審查完成 |
| P3／P4 | 216／95 source rows | 未更動 |
| 正式 C1 新增准入 | **0** | 不以公開文字、同名、tenement intersection 自動升格 |

本輪輸出：[P1 未結 31 source](2026-10-31_p1_31_remaining_public_source_review.csv)、[P2 28 source](2026-10-31_p2_28_public_terminal_desk_review.csv)、[Machine summary](2026-10-31_p1_p2_public_review_summary.json)。兩份審核輸入表可人工更新並由 [Python 程式](../../scripts/audit_p1_p2_public_evidence.py) 重新生成。

## 2. P1：公開資料可以補到哪裡

### 2.1 四份 WA WAMEX 官方紀錄：索引內容確認，官方 PDF 位元組仍缺

| A-number | 來源案例／筆數 | 文件內容與範圍 | 原件狀態 |
|---|---|---|---|
| [A119194](https://geothought.nlp-tlp.org/wamex/A119194) | Hopelands East／1 | Cristal 2019 annual，C35/1998、M70/599–603；2019 公司 HM 財務重估為當時不可行；索引報告頁 4、12 | 報告文字索引可核、WA 官方 PDF SHA 缺 |
| [A120393](https://geothought.nlp-tlp.org/wamex/A120393) | Hassell Beach／2 | Cristal 2019 annual，M70/562；Indicated **4.54 Mt @11.9% HM**（約 530 kt HM），公司當時評估不具經濟性；不是 TREO JORC | 報告文字索引可核、WA 官方 PDF SHA 缺 |
| [A129842](https://geothought.nlp-tlp.org/wamex/A129842) | Witchcliffe／1 | 2022 E70/5471 final surrender；僅文獻檢視、無顯著新結果；頁 4、9 | 報告文字索引可核、WA 官方 PDF SHA 缺 |
| [A109188](https://www.nextmaps.com.au/explorers/cristal-mining-australia) | Tutunup West／1 | 2016 Annual Tutunup West **M70/1108**（2015–2016），同地另有 A106109（2015）；不得合併 Iluka Tutunup | 次級書目索引可核、報告全文／WA 原始 PDF 缺 |

西澳州政府 [WAMEX 存取說明](https://www.wa.gov.au/service/natural-resources/mineral-resources/access-mineral-exploration-reports-wamex) 確認公開報告可免費下載；本輪未能從可達的查詢介面取得這四份原始政府 PDF 與分離附件，故在資料表保留 `REPORT_INDEX_ONLY_OFFICIAL_BYTES_NOT_ARCHIVED`。**不可寫入原件 SHA-256；沒有寄送任何索取郵件。** [來源取得待辦 #30](https://github.com/lleeoo0611-stack/AU_REE/issues/30) 保留開啟；可重開情況是官方 PDF 取得、查得其他現代獨立 REE 資源／產品聲明，或有效地理關係更新。

### 2.2 原生身分衝突，已補上可比較的正反證據

| `P1X-0012` | Hassell Beach | Hassell Beach Indicated JORC 2012 resource 4.54Mt at 11.9% HM = ~530kt HM, ilmenite/leucoxene/zircon products. Company reports uneconomic at 2019 reporting date. HM statement cannot be recast as TREO resource. | [來源](https://geothought.nlp-tlp.org/wamex/A120393) |
| `P1X-0013` | Hopelands East | Hopelands East: 2019 company review of heavy-mineral economics reported negative financial viability and no further exploration worthwhile at the time; target is mineral sands, not proven REE production, and it is not a JORC TREO MRE. | [來源](https://geothought.nlp-tlp.org/wamex/A119194) |
| `P1X-0018` | Tutunup West | Tutunup West is a named project on M70/1108 with indexed historical annual exploration reports. Secondary index alone does not establish REE recovery or whether historic resource meets JORC TREO, and is separate from Iluka Tutunup. | [來源](https://www.nextmaps.com.au/explorers/cristal-mining-australia) |
| `P1X-0019` | Witchcliffe | Witchcliffe E70/5471 final surrender: company completed literature review with no significant new results; concluded additional HMS potential absent in that reviewed licence and surrendered title, but no region-wide REE absence inference. | [來源](https://geothought.nlp-tlp.org/wamex/A129842) |
| `P1X-0005` | WINGELLINA | Issuer map separates WA Wingellina Ni-Co deposit and SA Claude Hills; source rows labelled SA near longitude 128.938E require original state/native-feature verification. Existing Ni-Co PFS does not establish commercially recoverable REE pro | [來源](https://www.metalsx.com.au/wp-content/uploads/2021/11/MLX-Nickel-Spin-out-EGM-NOM_v4_FINAL_COMBINED_compressed.pdf) |
| `P1X-0008` | Ambergate | Issuer historical Ambergate tenement E70/4799 must not be replaced by source-point overlay E70/4793, and one source-point equals Witchcliffe. Current native point evidence alone cannot adjudicate identity. | [來源](https://www.asx.com.au/asxpdf/20170130/pdf/43flm3q4b7bcnb.pdf) |

其中 Wingellina 原生 SA source 點與 **WA Wingellina nickel-cobalt** 的歷史範圍不可依相近名稱合併。[Metals X 2021 Central Musgrave 版圖](https://www.metalsx.com.au/wp-content/uploads/2021/11/MLX-Nickel-Spin-out-EGM-NOM_v4_FINAL_COMBINED_compressed.pdf) 將 Wingellina E69/535、E69/3065 列為 WA，Claude Hills EL5860、EL6240 列為 SA；[Austrade 2026 年 3 月專案簡介](https://international.austrade.gov.au/content/dam/austrade-assets/international/documents/reports/critical-minerals/australian-critical-minerals-prospectus-march-2026.pdf) 將 Wingellina 定義為 Ni–Co Project。這補強了錯配問題，但尚不足以確認南澳原生 feature 真正的地理站址。

Ambergate 的兩個原生 source 點相距 **38.738 km**，其中一點恰與 Witchcliffe 原生點重合；2017 年發行人專案資料的 **E70/4799** 不能直接由當前 source 點疊到的 E70/4793 取代。維持兩筆原生紀錄與衝突旗標，待 original native coordinate + historical title polygon 解決。

### 2.3 13 個正向案例的正式 C1 Release

- `P1G-0003` **Copi Mineral Sands Project**：HM_MRE_NOT_TREO; PFS_REFERENCED；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1G-0005` **Korella Bore project prospectus**：Y2O3_NOT_TREO_INTERNAL_VERSION_CONFLICT; HISTORICAL_NOT_VERIFIED_CURRENT；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1G-0007` **Fingerboards Critical Minerals Project**：PROJECT_ORE_PLAN_NOT_JORC_TREO; EES_PRE_FID_2026；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1G-0008` **Nowie (VHM) Project**：THM_JORC_WITH_NO_TREO_MRE; RESOURCE_EXPLORATION_NOT_PROVEN_SCOPING；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1G-0010` **Aileron Niobium–REE Project**：2026_NB2O5_MRE_NOT_CURRENT_TREO_GRADE; EXPLORATION_RESOURCE_DEFINED；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1G-0015` **Governor Broome Mineral Sands Project**：HM_JORC_NO_TREO_REPORTING; SCOPING_2024_HMS；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1G-0019` **Mount Ridley / Grass Patch complex (Mia)**：DIFFERENT_CUTOFFS_SCOPE_NO_AUTOSUM; RESOURCE_DEFINED_WITH_UNKNOWN_STUDY；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1G-0021` **Redlings Rare Earths Project**：PROJECT_SCOPE_11MT_NO_SUBALLOC; REE_RESOURCE_EXPLORATION；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1G-0022` **Fraser Range / Talisker Project (separate Salazar)**：NO_SCOPED_TREO_MRE; EXPLORATION；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1G-0023` **Mt Clere Project / Tower Deposit**：GRADE_VERSION_CONFLICT_840_801; SCOPING_PLANNED_2023；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1G-0025` **Mt Stirling Project / Yttria Deposit**：MII_TOTAL_OVERLAP_DO_NOT_SUM; REE_RESOURCE_EXPLORATION；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1X-0006` **Goschen South**：HM_MRE_NOT_SOUTH_SCOPED_REO; EES_MINISTER_ASSESSED_2024；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。
- `P1X-0007` **Wim deposits**：ORE_PLAN_NOT_SAME_AS_TREO_MRE; EES_PREPARATION；正式 Project／REE／Window／JORC／Panel／GIS 六個 Gate 尚待核准。

截至凍結資料時點，13 案的主來源及 REE role 已有不同程度文件支持；**公開來源補查並不構成獨立審核簽名**。與主群組一致的 JORC resource statement（嚴格區分 **TREO/REO、Y₂O₃、HM/THM、Nb₂O₅、Sc**）、已發布而非規劃中的經濟研究、開發/Deposit polygon、固定 Panel 與 GIS release 仍依 [Issue #32](https://github.com/lleeoo0611-stack/AU_REE/issues/32) 逐案處理。**不得把歷史來源 22 筆直接當作 22 個正式 Project。**

## 3. P2：28 筆來源的公開證據審核

P2 原本 27 案例中有 12 案只剩 Legacy 名稱，這次找到多個可定位的原始政府或發行人紀錄。結果按**案例**互斥分類：

| 來源文件審核結論 | 案例數 |
|---|---:|
| 找到具範圍的政府／發行人證據，Legacy 對應或正式 C1 Gate 仍待核 | **17** |
| 發行人 Scoping Study 的商業研究未包含 REE 資源階段 | **1** |
| 歷史礦場／處理場，現行 pre-FID 定義不適用 | **3** |
| 特定 REE 鑽探目標結果不支持顯著 REE 礦化（不外推整個區域） | **1** |
| 政府原生歷史地質 feature，尚無 Project 層級 REE 產品 | **3** |
| 只有區域次級索引或同名，原始 Legacy Source 身分未證明 | **2** |
| **合計** | **27** |

### P2 所有案例（原始 source IDs 見逐列 CSV）

| Case | 原始名稱 | 文件審查處置 | REE／資源證據基準 | 來源 |
|---|---|---|---|---|
| `P2G-0001` | Arthur Popes | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REE_OCCURRENCE_NOT_TREO_MRE | [文件](https://geoscience.nt.gov.au/web/entities/publication/45ff8135-1e9c-4b1f-b7b7-793f22a1d74f) |
| `P2G-0002` | Bells Monazite | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | MONAZITE_OCCURRENCE_NO_MRE | [文件](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/90694/1/GR087_2014_A_01.pdf) |
| `P2G-0003` | Blues Folley | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REE_ANOMALY_NO_MRE | [文件](https://www.geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/91056) |
| `P2G-0004` | Boulder Ridge | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | HREE_ROCK_CHIPS_NOT_MRE | [文件](https://www.geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/92342/1/GR334_2016_GA_01_Report.pdf) |
| `P2G-0005` | Bruce Prospect | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REE_INTERCEPT_NOT_MRE | [文件](https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree) |
| `P2G-0006` | Duke | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REE_SOIL_AND_DRILL_INTERCEPT_NOT_MRE | [文件](https://hreltd.com.au/projects/duke/) |
| `P2G-0007` | Edwards Creek | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | BASE_METAL_PROSPECT_REE_ROLE_UNVERIFIED | [文件](https://announcements.asx.com.au/asxpdf/20220704/pdf/45bjr9zgfpl2k9.pdf) |
| `P2G-0008` | Plenty River | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REGIONAL_REE_ANOMALY_NOT_MRE | [文件](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/92857/1/EL31225_2023_C_01.pdf) |
| `P2G-0009` | Brumby Clydesdale Project | 經濟研究未涵蓋 REE | REE_ONLY_CONCEPT_STAGE2_NO_MRE | [文件](https://intergroupmining.com/wp-content/uploads/2025/02/IGM-BC-Scoping-Study-2025-v1.pdf) |
| `P2G-0010` | Elaine Dorothy | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | HISTORICAL_REE_MINERALISATION_NOT_REO_MRE | [文件](https://aukingmining.com/site/pdf/69270e44-d780-40f0-9aec-b1e695241a0e/CuCoREEU-Mineralisation-at-Elaine-Dorothy-Project.pdf) |
| `P2G-0011` | Mary Kathleen tailings | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REE_TESTWORK_FEED_NOT_JORC_RESOURCE | [文件](https://www.qld.gov.au/environment/land/management/abandoned-mines/remediation-projects/mary-kathleen) |
| `P2G-0012` | Mary Kathleen | 歷史已生產／已復育 | HISTORIC_URANIUM_MINE_NO_REO_JORC_C1 | [文件](https://www.qld.gov.au/environment/land/management/abandoned-mines/remediation-projects/mary-kathleen) |
| `P2G-0013` | PORT PIRIE REE | 歷史已生產／已復育 | HISTORICAL_OXIDE_ESTIMATE_NOT_JORC | [文件](https://minerals.sarig.sa.gov.au/MineralDepositDetails.aspx?DEPOSIT_NO=8908) |
| `P2G-0014` | Anchor Tin Deeps | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REE_DRILLING_TARGET_NOT_JORC | [文件](https://www.mrt.tas.gov.au/exploration/exploration_drilling_grant_initiative_edgi_results/round_8) |
| `P2G-0015` | Blue Tier | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REE_ASSAY_TARGET_NOT_JORC_REO | [文件](https://www.mrt.tas.gov.au/news/old_news/seventeen_projects_share_exploration_drilling_grant_initiative_edgi_funding_in_round_7) |
| `P2G-0016` | Cruncher | 指定鑽探目標未見顯著 REE | TARGETED_DRILL_NO_SIGNIFICANT_REE_IN_CR001 | [文件](https://www.mrt.tas.gov.au/exploration/exploration_drilling_grant_initiative_edgi_results/round_7) |
| `P2G-0017` | DC Target | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REE_LISTED_TARGET_NOT_REO_RESOURCE | [文件](https://www.mrt.tas.gov.au/exploration/exploration_drilling_grant_initiative_edgi_results/round-9-edgi-results) |
| `P2G-0018` | Tunnel Hill | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REE_LISTED_TARGET_NOT_REO_RESOURCE | [文件](https://www.mrt.tas.gov.au/exploration/exploration_drilling_grant_initiative_edgi_results/round-9-edgi-results) |
| `P2G-0019` | Bondi | 政府原生地質紀錄（無 Project 身分） | NATIVE_HISTORICAL_FEATURE_REE_ROLE_UNKNOWN | [文件](https://resources.vic.gov.au/geology-and-data/minerals/metals/mineral-sands) |
| `P2G-0020` | Danube Prospect | 政府原生地質紀錄（無 Project 身分） | NATIVE_HISTORICAL_FEATURE_REE_ROLE_UNKNOWN | [文件](https://resources.vic.gov.au/geology-and-data/minerals/metals/mineral-sands) |
| `P2G-0021` | Douglas Project | 歷史已生產／已復育 | HISTORIC_HMS_PRODUCTION_NOT_REO_MRE | [文件](https://www.iluka.com/community-engagement/douglas/) |
| `P2G-0022` | Orion | 政府原生地質紀錄（無 Project 身分） | NATIVE_HISTORICAL_FEATURE_REE_ROLE_UNKNOWN | [文件](https://resources.vic.gov.au/geology-and-data/minerals/metals/mineral-sands) |
| `P2G-0023` | Wedderburn Project | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | HM_RESOURCE_NOT_REO_JORC | [文件](https://wimresource.com.au/project/) |
| `P2G-0024` | Mt Joy - Bolgart - Northam JV | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | OTHER_METAL_EXPLORATION_NO_REO_RESOURCE | [文件](https://northamresources.com/wp-content/uploads/2022/11/NRL_Prospectus2022_FINAL-DRAFT_28Oct2022.pdf) |
| `P2G-0025` | Pyramid | 區域索引／名稱關係未證實 | SECONDARY_REGIONAL_REE_MENTION_NOT_RESOURCE | [文件](https://www.nextmaps.com.au/explorers/pyramid-minerals) |
| `P2G-0026` | Talisker | 原始政府／發行人文件已定位，原生 Source–Project 關聯待核 | REE_EXPLORATION_NOT_MRE | [文件](https://announcements.asx.com.au/asxpdf/20250814/pdf/06mvmb9r2vhdhs.pdf) |
| `P2G-0027` | Webb Au | 區域索引／名稱關係未證實 | SECONDARY_REE_MENTION_UNSCOPED | [文件](https://www.nextmaps.com.au/exploration/east-pilbara/webb) |

### 研究上必須保留的四個區別

**一、P2 既有 Legacy Project 名稱 ≠ 已批准現代 Project。** 例如 Blueys Folley 已找到 2014 年 NT 政府 `EL28029` 報告（舊表作 Blues Folley），Wolfram Hill 的 Bell's Monazite 亦找到 2014 年政府技術報告，兩者的礦化事實可以保留，但原始 Legacy ID 對應之地理／礦權還沒有獨立簽核。

**二、REE 元素檢出 ≠ REE Mineral Resource。** [Duke](https://hreltd.com.au/projects/duke/) 的岩芯／土壤異常及 [Boulder Ridge](https://northernminerals.com.au/exploration/) 的 xenotime rock chips 屬 exploration；不可挪用 Browns Range 的 TREO MRE。[Brumby Clydesdale 2025 Scoping Study](https://intergroupmining.com/wp-content/uploads/2025/02/IGM-BC-Scoping-Study-2025-v1.pdf) 的經濟研究對象為 kaolin、silica、gold/HPA，Y/Ce 等深部 Stage 2 商品尚未納入該研究，不能據此通過 REE Window/JORC Gate。

**三、負結果有固定適用範圍。** [MRT 2023 Cruncher CR001](https://www.mrt.tas.gov.au/exploration/exploration_drilling_grant_initiative_edgi_results/round_7) 鑽孔未見所尋找的顯著 REE 礦化，限於該孔及測試目標；並沒有證據顯示整個 Cruncher 區域永無 REE 資源。[MRT 2025 DC/Tunnel Hill](https://www.mrt.tas.gov.au/exploration/exploration_drilling_grant_initiative_edgi_results/round-9-edgi-results) 雖將 REE 納為目標商品，但主要報告了 Sn–多金屬礦化，不能視作獨立 REO 資源。

**四、歷史生產／尾礦／現代試驗各有不同的法律與資源範圍。** Mary Kathleen 舊礦場、Mary Kathleen tailings 研發、Port Pirie treatment site、Douglas 已生產的 HMS 礦場，保留為不同 entity source，且從未直接進入 C1。Wedderburn 的 **223 Mt @ 2.9% THM** 亦不得換算成 TREO JORC。

## 4. 結案定義、研究資料庫與再開案條件

本次**P2 公開來源範圍的 28/28 逐案審核已完成**，且每筆以同一 `target_id` 記錄文件、日期、來源定位、商品基準、關聯候選、互斥判讀與再開案動作。這是 source desk review closure；Project identity / original legal title / 6-domain comparable matrix 尚未簽核。新的具體文件可直接在 curated input CSV 修訂後重跑，既有凍結輸出與 original target IDs 不刪改。

P2 再開案以最小材料觸發：原始政府 feature 座標、歷史與現時 licence polygon、發行人正式 Project footprint + Deposit alias、同範圍 REO JORC Resource (M/I/I, cut-off, dates)、已發布 Scoping/PFS/DFS、可核准的共同六構面 Panel。未找到文獻不能被解讀成地質缺少稀土。

原 412 筆 HOLD 工作排序與 487 Census 仍維持 **P1 73、P2 28、P3 216、P4 95**。本輪不啟動 P3/P4、不改寫 project_master/C1、JORC approvals、GIS_RELEASE、原 R1/S1/G0/RS 模擬結果。

## 5. 重跑、稽核與追蹤

```bash
python scripts/audit_p1_p2_public_evidence.py --check
python -m unittest discover -s tests -p 'test_p1_p2_public_evidence.py' -v
```

- 輸入：[P1 19 cases](../../inputs/source_review_20261031/p1_19_public_remaining_case_adjudications.csv) 與 [P2 27 cases](../../inputs/source_review_20261031/p2_27_public_evidence_adjudications.csv)
- 輸出：本報告、P1 31 source、P2 28 source、machine summary。
- 稽核：六個 Gate 均為 `HOLD`、C1 `NO`、全部原始 PDF archive SHA 尚未憑空填寫，`reviewer_signature` 空白。
- 追蹤：[WAMEX 官方原件 #30](https://github.com/lleeoo0611-stack/AU_REE/issues/30)、[P1 正向 C1 #32](https://github.com/lleeoo0611-stack/AU_REE/issues/32)、[P2 來源核准 #35](https://github.com/lleeoo0611-stack/AU_REE/issues/35)。
