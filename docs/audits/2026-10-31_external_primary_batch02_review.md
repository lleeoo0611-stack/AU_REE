# External Technical Primary Batch 02 — 2026-10-31

Execution `EXT-TECH-B02-20261031`. Based on merged Batch 01 `main@0d34836`. Continues frozen 2026-10-29 source universe, no changes to that dataset, existing 412 fixed IDs or C1/13-case Gate/MCDA.

## 實質來源判讀（本批 5 筆原生來源 ID）

| 固定來源 | 原件文本／官方欄位 | 釐清內容與結案 |
| --- | --- | --- |
| **Pindari — 2 IDs** (SA, P3/P4) | Archer 2011 original annual-report searchable text; SA SARIG `mesac27025` official released-report catalogue synopsis (`Env 11157`, 2010–2019). | 2010 七口 RC 孔、歷史 Ni/Cr/REE 異常與後續鑽孔結果需分開；Archer 指中央深部 EM 異常尚未測完，政府摘要說 2010 RC cuttings 無異常 REE 分析。兩者樣本集合與時點不可混為「整個礦區已證實沒有 REE」。目前只有 geochemical/geophysical prospect，無 REO JORC MRE。**歷史勘探與來源母層可判讀；原始 Env 報告、具體 REE assays、Project 身分 HOLD。** |
| **Acropolis — 2 IDs** (SA, P3) | 官方 SARIG Mineral Deposit **3018** 列 Cu major／REE minor、Unworked Prospect、1986 十一孔；Dmitrijeva 等人 2019 學術原始研究摘要列 **4,864 core samples／14 drillholes**， hematite-associated REE geochemical signatures。 | 原生 SA `DEPOSIT`／`PROSPECT` 來源不等於獨立稀土開發 Project。磁鐵礦／赤鐵礦中伴生的 REE 地球化學特徵不可算成 TREO 礦石品位、資源或選礦回收。官方原件索引包含 BULL 054、RB86/00051、Envelope 09288，**待補實際原始報告及 REO 資源／礦權**。 |
| **Murray Basin — 1 ID** (VIC, P3) | Resources Victoria Mineral Sands 官方說明，以及 2025-10-20 `Current Mineral Projects and Selected Occurrences` 官方地圖文字（WIM50/WIM100、Bungalally、Avonbank、WIM150、Donald、Goschen 等分開列名）。 | Murray Basin 是跨 VIC/NSW/SA 的重礦物砂盆地，其 GA 地名 source point 不能視作單一 project polygon。官方圖列 Iluka WIM50/WIM100 **1,380 Mt @ 5.0% HM**，是 heavy minerals 不是 TREO；不同 operator 資源不可繼承或加總。**區域來源範圍可結案，Project／JORC/Gate 仍 HOLD。** |

## 可定位來源

- Pindari：[Archer 2011 Annual Report 原始 ASX 公告](https://announcements.asx.com.au/asxpdf/20110921/pdf/42170jxqzwg4ly.pdf)，印刷頁 66–67 的 Nickel / Pindari 段落、Figures 3–4；[SARIG `mesac27025` 官方目錄摘要](https://pid.sarig.sa.gov.au/document/mesac27025)，2010–2019 Carappee Hill annual reports，Env 11157、PRC001–PRC007。
- Acropolis：[South Australia SARIG Mineral Deposit 3018](https://minerals.sarig.sa.gov.au/MineralDepositDetails.aspx?DEPOSIT_NO=3018)，`Summary`／`Commodity significance`／`References`；[2019 Journal of Geochemical Exploration 原始研究之大學典藏摘要](https://digital.library.adelaide.edu.au/items/6bc3a0e1-bafc-4082-abfe-74404dd66252)，Dmitrijeva 等人 `Abstract`，DOI 10.1016/j.gexplo.2019.106333。
- Murray Basin：[Resources Victoria Mineral Sands](https://resources.vic.gov.au/geology-and-data/minerals/metals/mineral-sands) 的 `Murray Basin` 及 deposit types；[2025-10-20 官方 Project/Occurrence 圖](https://resources.vic.gov.au/geology-and-data/industry-investment/mineral-resources-development/Current-Mineral-Projects-and-Selected-Occurrences-2025-10-20-Web.pdf) 的 `Projects in development` 9–14/19–21。

以上來源有公開官方 HTML、目錄摘要、PDF 網頁可搜尋原文；但本執行環境**未封存 ASX/州政府 PDF 原始位元組**，原 PDF 視覺頁面驗證亦未成功。不得填入 SHA 或宣稱完整原件技術全文已審定；取得原始 PDF 後應獨立做 byte SHA256 + page table audit。

## 累計進度與下一步

- [完整 167 筆可編輯進度 CSV](2026-10-31_external_primary_progress_167.csv) 每筆維持固定 source ID、原生紀錄與過往分類，**10 筆**（Batch01 5 + Batch02 5）新增具體技術來源範圍判讀，**157 筆**仍需外部技術原件，全部保留項目缺口。原始 `2026-10-31_p234_final_evidence_339.csv` 不覆寫。
- P2 28 筆（27 案）仍沿用 [逐筆複核追蹤表](2026-10-31_p2_28_recheck_tracker.csv)：3 筆政府原始 HTML 重驗、25 筆待技術全文；Scaddan 兩版賦存說法衝突保留、原始 PDF 位元組 HOLD。
- 不是 167 筆都完成技術原件。10 筆目前只有「技術文件的公開文字／官方原文來源判讀」，尚未完成原 PDF 位元組封存；來源範圍結案不等於 C1／JORC／Project 審核核准。
- 下一批優先尋找 SARIG Env 原件與州政府有確切 report/MinDep IDs 的項目，不依相同地名／元素關聯進行 Project 去重。C1、13 案 Gate、MCDA 依使用者要求一律暫緩。

## Reproducibility

`python scripts/check_external_primary_batch.py`、`python scripts/check_external_primary_progress.py`、`python -m unittest discover -s tests -p test_external_primary_progress.py -v`。CI 核查 ID、內容非空、已定位原文、無假造原件 hashes、P2/Scaddan/正式 Gate 無漂移；CI 不能取代原 PDF 外部原件實讀。
