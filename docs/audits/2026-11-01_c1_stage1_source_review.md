# C1 Stage 1 第一輪公開來源核對 — 7 個經濟 Study 線索 Project

**來源日期截止：2026-10-29；查核日期：2026-11-01。** 已依 P0.1 既有的 39 個 Project Review Groups，選取 7 個標為 `STUDY_DOCUMENTED_PRE_FID_SCREEN` 者進行新的來源範圍查核。逐項公開來源、可核的資料、仍缺哪些原件均收於 [7 筆可編輯 CSV](../../inputs/source_review_20261101/c1_stage1_public_evidence_7.csv)，彙整至 [39 筆 Gate 初審表](2026-11-01_c1_first_pass_gate_39.csv)。

| Project | 新取得／明確定位的研究訊號 | C1 最主要未通過條件 |
| --- | --- | --- |
| Browns Range (WA) | 2025-09-15 Northern Minerals ASX 公開 DFS 原文位置；2026 後續新聞尚需檢查 publication as-of | DFS 對應 Wolverine / Dazzler 與 REO JORC Resource statement、Project GIS 與六 Gate 人工簽核 |
| Bungalally (VIC) | WIM 網站僅述 `at a Scoping Study stage`；205Mt @ 2.7% **THM** JORC Inferred | **已完成的** Scoping Study 是否在 cutoff 前公開、同範圍 TREO JORC 及 REE 回收產品是否存在 |
| Copi (NSW) | NSW 官方 Project 頁及舊 P1 案 2023 PFS 引述 | 2023 PFS **原始文件**、Copi vs Copi North、REE 氧化物資源/產品 |
| Dubbo (NSW) | 2026-03 Austrade 國家 Prospectus 引述 2021 Optimisation Feasibility 和 2025-07 Heap Leach Scoping | 兩種經濟方案不可混算；需 JORC 原件、採用的研究方案/日期與正式 Project 邊界 |
| Goschen Central (VIC) | 發行人頁指 2025-06 已完成 Scoping；Phase1 HMS/REMC 和 Phase2 refinery/MREO 分開 | 計畫階段之獨立 REO JORC Resource/原始原件、Licensed GIS |
| Jupiter (WA) | 2026-10-20 Critica ASX Scoping，引用 2026-10-12 1.7Bt @1,700ppm TREO MRE（1,000ppm cutoff，160Mt Indicated） | JORC Table/CP original、Jupiter deposit vs Brothers regional boundary、固定六構面及人工簽核 |
| Wimmera (VIC) | Iluka 2024 年報 WIM100 2023 PFS、稀土 Ore Reserve；進行中的 DFS | WIM100 / WIM50 deposit scope、相同時點 REO Resource/Reserve 表、2026 pre-FID/Panel/GIS |

上述訊號來自**官方或發行人可公開檢索的有界文字／報告索引**；本次未儲存 PDF 原始位元組與 SHA，也未宣稱完整原始技術文件已完成逐頁驗證。對其中頁面與研究截至日未能獨立核准者，維持 Gate HOLD。即便原始 Study 和某項 TREO 資源都有報導，也還需核對資源所屬 Deposit、分類、截至日期及 Project 權利範圍。

新增結果：**7／39** 具有新的有界來源核對；其餘 **32／39** 保留原 2026-10-31 來源初審，不宣稱缺乏 REE。**C1 0、C2 0 正式核准**。現有 R 腳本不得據此輸出實際研究級排名；Panel 9/12 候選尚未固定。

**下一輪 Gate 審查次序：**先讀 Jupiter 2026-10-12 MRE/2026-10-20 Scoping 與 Browns Range 2025-09-15 DFS 的完整 source-scoped JORC 表；Dubbo 的 2021/2025 原始研究；Goschen Stage1/Stage2 的 REO Resource；Wimmera 的 REE Mineral Reserve／THM 分離；Bungalally 和 Copi 先找 completed Study 與 REO 資源。每項完成後依 `inputs/review_decisions/c1_c2_project_gate_signoffs_v1.csv` 逐 Gate 人工簽核，否則保留 C1_NOT_ADMITTED。

## 原始來源 URL

- Browns Range — <https://announcements.asx.com.au/asxpdf/20250915/pdf/06p6zt0hxtpg01.pdf>
- Bungalally — <https://wimresource.com.au/project/bungalally/>
- Copi — <https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects>
- Dubbo — <https://international.austrade.gov.au/content/dam/austrade-assets/international/documents/reports/critical-minerals/australian-critical-minerals-prospectus-march-2026.pdf>
- Goschen Central — <https://acdcmetals.com.au/projects/goschen-central/>
- Jupiter — <https://investorhub.critica.limited/announcements/O12NJO-jupiter-scoping-study-defines-pathway-to-development>
- Wimmera — <https://www.iluka.com/media/hlbhtwnj/final-iluka-ar24-25225.pdf>
