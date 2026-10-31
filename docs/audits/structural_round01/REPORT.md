# AU_REE Execution Round 01 — Structural Cohort evidence acceptance

執行 ID：`AU_REE_STRUCTURAL_R01_20261101`。研究截止日：**2026-10-29**；審查日：**2026-11-01（Asia/Taipei）**。
基線：`main@d723bc431389ea56bbf2a5b905fa52a8a64b3fee`，已含 [PR #49](https://github.com/lleeoo0611-stack/AU_REE/pull/49) 的 C1/C2 政策與 [PR #50](https://github.com/lleeoo0611-stack/AU_REE/pull/50) 的母子腳本及七案初審。

本輪實際取得原件，解決 **24 個明確列名的文件／範圍／口徑缺口**，並將 **27/195 個五項文件證據格**整理至可送審。**沒有正式 Gate PASS、研究者簽名、獨立 Project ID 核准或 MCDA。** 正式 Structural Cohort 仍未凍結。

## 1. 驗收口徑及限制

本輪依本次使用者的 Execution Round 01 要求，結合既有 [研究架構](../../RESEARCH_ARCHITECTURE.md)、[Cohort protocol](../../P0_COHORT_SELECTION_PROTOCOL.md)、[資源規格](../../P0_PROJECT_RESOURCE_SCHEMA.md)、[C1/C2 政策](../../C0_FREEZE_AND_C1_C2_POLICY.md) 執行。最新 main 未找到另一本以 `AU_REE Pre-MCDA Research Pipeline Completion Protocol` 為檔名／標題的文件；沒有據此另建一套管線或改動准入契約。

本輪五項是 **ID、ROLE、WINDOW、JORC、GIS_SOURCE** 的文件證據審查。`GIS_SOURCE` 僅定位具角色的原始圖件／來源對應；它**不等於**既有正式 `GIS_RELEASE`，也沒有完成 I1–I4 官方圖層 QA。Core／Extended Panel 均未選定。

`REVIEW_READY` 是文件包可交獨立審查；`data_complete` 是本輪五項文件格填足，不代表六項正式 C1 Gate 已核准。Jupiter 的文件包為本輪唯一五格可送審候選，但仍缺正式官方幾何與獨立時點／Gate 審查，不能稱為已准入 Structural Project。其餘 38 包保留 `BLOCKED_EVIDENCE`，逐 Gate 可另有 `REVIEW_PENDING`、`OUTSIDE_WINDOW` 或 `INACTIVE`。

**39/39 是有界分類完成，不是 39 份完整技術報告核准。** 深度分為 9 個技術原件相關頁面審查、17 個原始 HTML 層級審查、13 個沿用先前判讀並明列原件存取限制。後兩類未取得的研究／JORC 日期與範圍保留未知，不以空白推定不存在。沒有重複把 13 個 P1 source cases 加成 13 個新 Project。

## 2. 本輪十項結果

| 指標 | 本輪已驗證結果 |
| --- | --- |
| 原始 39 群組實際審查 | 39 個有界分類；其中 9 個技術原件頁面審查 |
| 新取得來源 | 36 個唯一 SHA-256 原始回應：13 份 PDF、23 份 HTML；另 17 個來源存取失敗 |
| 新獨立 Project ID | 正式獨立核准 0；8 個已有日期／範圍支持的 ID＋ROLE 文件候選，原群組 ID 保留 |
| 同範圍 REO 原始表線索 | 7 個；其中 4 個 JORC 文件格可送審；3 個仍有口徑／原件／cut-off 衝突 |
| 截止日前經濟研究原件 | 8 個 Project 有 Scoping／PFS／DFS／BFS 原始發布文件；不等於 8 個均已證明截至截止日仍 pre-FID |
| Structural Eligibility／Review Ready | 正式 Eligibility 0；Jupiter 文件包 Review Ready 1（只含 GIS 來源定位）；正式 GIS release 0 |
| C2 核准／待審 | 0／39；其中 8 個 ID＋ROLE 證據較完整的待審候選 |
| Gate 阻礙 | 168/195 格仍未達文件可送審，詳見下表及逐列原因 |
| 證據衝突處理 | Dubbo 研究日期及 Y basis 差異已定位原因；Goschen Central 與 Bungalally 原件矛盾保留；未強迫改值 |
| Git／測試／下輪 | 接入既有母腳本；29 項相關測試通過；下輪先處理 Jupiter、Browns Range、Donald、Wimmera 的審查／時點／幾何缺口 |

36 個原始回應共 **68,617,630 bytes**。HTML 原件包括公司頁面／入口頁，**不是 23 份完整技術研究**；回應存取成功也不代表該頁每項主張已核准。13 份 PDF 中，Avonbank 是無日期概要、Koppamurra 是發布簡報、Browns Range FID 是事件公告，不能全稱為 13 份完整經濟研究。

7 個有同範圍 REO 原始表的群組：Browns Range、Jupiter、Dubbo、Goschen Central、Wimmera/WIM100、Koppamurra、Donald/MIN5532。可送審的 4 個 JORC 文件格為 Browns Range、Jupiter、WIM100、Donald；後二者是**有原始氧化物分解的 REO_SCOPED_BREAKDOWN**，不是從 HM 自動假設 REO，也尚未核准可比 R1。

8 個有截止日前研究原始發布文件的群組：Browns Range（2025 DFS）、Jupiter（2026 Scoping）、Dubbo（2025 Heap Leach Scoping）、Goschen Central（2025 Scoping）、Wimmera（2023 revised PFS disclosure）、Sandy Mitchell（2024 Scoping）、Donald（2026 BFS）、Charley Creek（2013 Scoping）。Koppamurra 2026 PFS 發布已有原始簡報確認，但本輪未取得完整 PFS 原件，故不加入這 8 個。

## 3. 七個優先 Project 的具體結果

| Project | 原件／日期／定位 | 已縮小的缺口 | 保留的阻礙／下一份必需證據 |
| --- | --- | --- | --- |
| Browns Range | [15-Sep-2025 DFS](https://announcements.asx.com.au/asxpdf/20250915/pdf/06p6zt0hxtpg01.pdf)，PDF 實體 p13 Table5；p10/p12/p58 地圖；[30-Sep-2026 FID update](https://hermes-cdn.investorhub.com/announcement-pdfs/asx/7761221.pdf?v=63957945122) p1–2 | Wolverine 7.3Mt、0.96% TREO、0.15% cut-off；M/I/I 與 stockpiles 分列；Dazzler 不加入；以截止日前 FID 延後原件取代 30-Oct 線索 | 核對 30-Sep 至 29-Oct 事件連續性、官方 WA 幾何；保留四捨五入導致的 7.4Mt 類別和 vs 7.3Mt reported total |
| Jupiter | [12-Oct-2026 MRE](https://hermes-cdn.investorhub.com/announcement-pdfs/asx/7781179.pdf?v=63958972805) p1–5/Table1；[20-Oct-2026 Scoping](https://hermes-cdn.investorhub.com/announcement-pdfs/asx/7794821.pdf?v=63959663947) p3–4/p11/p16–17 | 160Mt Indicated＋1,500Mt Inferred、1,700ppm TREO、1,000ppm cut-off；1.7Bt headline 為取整；Jupiter 完全位於 E59/2463，與 Brothers 其餘發現分開；MREC base case | 五項文件證據可送審；仍需獨立核對截止日前介入事件及官方幾何／CRS／代表角色；概念礦區圖不是核准邊界 |
| Dubbo | [11-Jul-2025 Heap Leach Scoping](https://announcements.asx.com.au/asxpdf/20250711/pdf/06lq7vsvvk6yms.pdf)，實體 p26 Table2／註10；p44–45 | 原件確認研究發布為 2025；研究以 Toongi 42.81Mt Measured 子集為基礎，非全資源 75.18Mt；7,400ppm TREO **不含 Y₂O₃**，另列 1,400ppm Y₂O₃ | 取得 2017 原始 statement／cut-off；正式核定是否納 Y 的可比口徑；查核 2026 公司／FID 事件，不把收購等同 title 或 FID |
| Goschen Central | [12-Jun-2025 Scoping 原件](https://wcsecure.weblink.com.au/clients/acdcmetals/headline.aspx?headlineid=3669765)，實體 p4–10，尤其 p9 Table2 | 經濟研究確實完成；Phase1 HMC/REMC、Phase2 南澳 offsite REPP/MREO 分開；620Mt 資源及 REO-in-HM 表已取得 | 原件表題寫 2023／2% HM，正文／註解寫 2024／1% HM；1.9%／1.6% 是 HM 內 TREO−CeO₂，不是 bulk TREO。需 3-Dec-2024 原件／更正及 EL5278→RL008706 官方對應 |
| Wimmera | [22-Feb-2023 revised PFS disclosure](https://www.iluka.com/documents/2023/asx-releases/revised-announcement-wimmera-ore-reserve-and-mineral-resource-update/) p17–19；[29-Jan-2026 WIM100 MRE](https://www.iluka.com/media/0o0novln/29jan26-wim100-mineral-resource-estimate-increase.pdf) p1/p3–4/Table2 | 有原始 PFS 經濟假設，不再僅「DFS 在進行」；2026 WIM100 540Mt 及逐類別 REO-in-HM；WIM50/WIM50N 不混入當期 study | REO 表包含 Sc₂O₃ 及 zircon 內 Y allowance，需定義公式；2023 PFS 與 2026 MRE 保留版本差異；取得 2026 pre-FID 事件與官方 project polygon |
| Copi | [Ausenco 30-Sep-2025](https://ausenco.com/insights/ausenco-to-lead-the-definitive-feasibility-study-for-the-copi-project/)，study contractor award section；既有 NSW Copi entry | 具名承包商明確確認交付 2023 PFS，不再只靠未署名階段標籤 | 完整 2023 PFS、2024 MRE 原件及 REO basis 仍不足；Copi North／Copi／Gilligans 不自動合併 |
| Bungalally | [WIM 頁面](https://wimresource.com.au/project/bungalally/)，Overview／Resource Geology／JORC Resource | 明確分類為「Scoping Study 階段」，不是已發表完成研究；2015 Inferred THM basis、1% THM cut-off 線索 | 同頁 205／207Mt 衝突未解；未找到日期可用的完整研究、商業 REE recovery plan 或同範圍 REO statement，維持 Blocked Evidence |

上述六張關鍵資源表（Browns Range、Jupiter、Dubbo、Goschen Central、WIM100、Donald）另以本機 PDF 渲染檢查表頭、欄位與註解；有視覺問題或原件矛盾者未以文字擷取強制修正。

## 4. 擴展核查的成果與停止條件

- **Donald：**取得 [31-Mar-2026 BFS](https://wcsecure.weblink.com.au/pdf/ATR/03073797.pdf)。實體 p35 Tables8-2/8-3 具 MIN5532 的 530Mt M/I/I、1% HM cut-off 及 REO-in-HM；p3 Figure1 區分 Phase1 MIN5532 與 Phase2 RL2002，p36 將 Jackson 別列。BFS 的 Q2-2026 FID 是目標，尚未證明 cutoff 狀態。
- **Koppamurra：**[25-Jun-2026 發布簡報](https://hermes-cdn.investorhub.com/announcement-pdfs/asx/7600078.pdf?v=63949564486) 實體 p23 為 reserve、p24 為 243Mt／751ppm resource，不能互加。Study southern subset、廣域 SA/VIC resource、7,400km² tenure 分開；完整 PFS／MRE cut-off 仍待取得。
- **Sandy Mitchell：**[11-Dec-2024 Scoping](https://announcements.asx.com.au/asxpdf/20241211/pdf/06chs9z9cp3tcy.pdf) 原件及 SMP-SS-001 已取得；當期 71.8Mt／1,732.7ppm MzEq、700ppm MzEq cut-off 不是 TREO；不能搭配 2026 網頁 379.4Mt 直接換算。
- **Charley Creek：**[15-Apr-2013 Scoping](https://www.asx.com.au/asxpdf/20130415/pdf/42f7v06gx1svy4.pdf) 原件已取得；歷史研究不代表 2026 活動／pre-FID 身分，當期資源與 production target 仍需逐域對照，未升格 current JORC ready。
- **Avonbank：**取得 [project information sheet](https://wp-wimresource-2023.s3.ap-southeast-2.amazonaws.com/media/2024/11/WIM-Avonbank-Info.pdf) 實體 p2 的 BFS 完成敘述；檔案本身無明確發布日，網址的 2024/11 **不當成發布日期**。30 年舊概要與 36 年現行公司頁面版本差異保留。
- **Milo：**原始 issuer 頁面明確稱 2013 estimate 為 historical 且不視為 current；研究表不因重新刊登而升格。
- 其他群組逐列保留 Project／Deposit 界線與下一份具體文件；例如 Ironback Hill 不繼承 magnetite 資源，Temple Bar auger assay 不等於 MRE，Vecco 的 V/HPA/Mo formal product scope 不替代 REE recovery commitment。

存取失敗／入口殼層不無限重搜。取得新 report ID、可用原件 URL、更正聲明、日期證明、官方 native geometry 或正式研究發布才重開；既有相同 URL 的成功／失敗紀錄由取件子腳本快取沿用。網站內容變更須建立新的 source ID，不覆寫本輪 bytes/hash。

## 5. 各 Gate 阻礙及筆數

以下為互不相同 Gate 的**證據格數**，同一 Project 可同時出現在多項，不能加成 Project 數：

| Gate | 可送審格 | 尚未可送審格 | 最常見原因 |
| --- | ---: | ---: | --- |
| ID | 8 | 31 | 30 日期可用的有界 Project／Deposit／官方對應不足、1 Charley Creek 歷史身分連續性待證 |
| ROLE | 8 | 31 | 23 日期／商業產品計畫不足、6 REE 商業角色未確立、1 Vecco product scope 不符 REE 主張、1 Charley Creek 歷史產品計畫連續性待證 |
| WINDOW | 1 | 38 | 24 完成研究／as-of 狀態待證、5 已得研究但後續事件連續性不足、3 簡報／歷史連續性不足、2 reported outside-window、1 inactive、1 Copi 原件、1 Avonbank 無日期概要、1 Bungalally 僅階段 |
| JORC | 4 | 35 | 26 同範圍 REO 原件待補；其餘各 1：drill assay、exploration target、歷史非 current、MRE 簡報 cut-off、MzEq、鄰近 iron MRE、表題／cut-off 衝突、THM＋205/207Mt、Y exclusion |
| GIS_SOURCE | 6 | 33 | 原始 Project／resource／tenure 圖件角色未定位；已定位 6 個也尚未正式 GIS release |

正式人工簽核仍是另一層要求；本輪沒有以「尚無簽名」掩蓋有價值的原件進展，也沒有把文件 ready 寫成正式 PASS。

## 6. 可編輯成果與逐列追溯

| 成果 | 路徑 |
| --- | --- |
| Project Source／Identity Crosswalk | [identity_crosswalk.csv](identity_crosswalk.csv) |
| 五 Gate Evidence Resolution Table | [gate_evidence_resolution.csv](gate_evidence_resolution.csv) |
| Project Resource Statement Register | [resource_register.csv](resource_register.csv) |
| Economic Study／Stage Timeline | [study_stage_timeline.csv](study_stage_timeline.csv) |
| Structural Cohort Candidate List | [structural_candidates.csv](structural_candidates.csv) |
| C2 Identity Review List | [c2_identity_review.csv](c2_identity_review.csv) |
| Gate 未通過原因、優先佇列及重開條件 | [gap_priority_queue.csv](gap_priority_queue.csv) |
| P1 13 案來源交叉對照建議，無自動核准 join | [p1_case_crosswalk.csv](p1_case_crosswalk.csv) |
| 六構面現有準則的 coverage 架構，無補值／Panel 選定 | [criterion_coverage.csv](criterion_coverage.csv) |
| 新文件解決的 24 個明確缺口 | [source_gap_resolution.csv](source_gap_resolution.csv) |
| 統計與輸入 SHA-256 | [summary.json](summary.json) |
| 原件／失敗來源定位、時間、URL、報告 ID、hash、byte count、access level | [access manifest](../../../inputs/source_review_20261101/structural_round01_access_manifest.json) |
| 可審查的逐案輸入 | [review ledger](../../../inputs/source_review_20261101/structural_round01_reviews.json) |

原件在本機 repo 的 `work/structural_round01/originals/`，public Git 只保留 metadata、hash、頁碼和有界判讀，不刊登第三方完整文件。Manifest 的 `archive_path` 相對於本 repo 根目錄；每個 resource／event 透過 `source_id` 接到原始 URL／hash。網頁、PDF、官方向量資料存取層級不得互換。

## 7. 重建及驗證

```text
python scripts/run_research_pipeline.py --profile all --mode check
python scripts/build_structural_round01.py --write
python scripts/build_structural_round01.py --check --verify-originals
python -m unittest discover -s tests -p test_structural_round01.py -v
python -m unittest discover -s tests -p test_research_pipeline_supervisor_v1.py -v
```

本輪 11 個新測試、5 個母腳本測試、7 個 C0/C1/C2 政策測試、3 個原七案測試、3 個 P234 事件測試，**共 29 項通過**。檢查日期洩漏、scope transfer、THM/MzEq 轉 REO、EES scoping 誤作研究、原件缺失、虛構 PASS／簽名、GIS source／release 分離、類別取整、輸出重建與 source-case 分母。Windows 限制模式阻擋既有 `TemporaryDirectory` 測試；同一測試取得本機暫存目錄存取後 5/5 通過，沒有跳過測試。

新增 [專用 CI](../../../.github/workflows/structural-round01.yml)，GitHub 執行結果須另行查看；本機通過不代稱遠端 CI 通過。取件腳本 `acquire_structural_round01.py --fetch` 為明確線上操作，只對 curated inventory 取件並快取；日常母腳本不連網、不重搜、不執行 R／MCDA。原件逐 byte 重新取得後如 SHA 改變，應建立新版 source 而非覆蓋凍結證據。

## 8. 下一輪具體優先順序

1. **Jupiter：**獨立審閱 12/20-Oct 原件、截止日前事件及 E59/2463 官方幾何；把 resource outline 與 proposed mine layout 分角色審查。
2. **Browns Range：**核對 30-Sep→29-Oct funding/FID 原始事件鏈；官方 Wolverine／stockpile／infrastructure 對應，不混 Dazzler。
3. **Donald、WIM100：**官方 native polygon、cutoff-date FID 事件；逐類別 REO-in-HM 正規化方案。原件表已取得，不重取同份表。
4. **Dubbo：**2017 cutoff 原件、含／不含 Y 的明確口徑決策及最新公開事件，不能把 2025 Heap Leach study 與 OFS 參數混用。
5. **Goschen Central：**3-Dec-2024 MRE 或 issuer clarification，解 2023/2024、1%/2% 及 oxide labels；核對 RL008706 與 EL5278。
6. **Koppamurra、Copi：**完整經濟研究原件及同範圍 MRE；已有簡報／承包商佐證不再重搜。
7. **Bungalally：**只在取得日期可用的完成研究、REE product plan、原始 2015 MRE／更正時重開；205/207Mt 與 HM basis 未解前保留 blocked。

停在 Structural 文件與證據驗收：**正式 MCDA 未執行，Core／Extended Panel 未選定，研究者簽核欄均為空。**
