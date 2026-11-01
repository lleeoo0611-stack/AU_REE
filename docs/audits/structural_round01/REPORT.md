# AU_REE Execution Round 01 — Structural Cohort evidence acceptance

執行 ID：`AU_REE_STRUCTURAL_R01_20261101`。研究截止日：**2026-10-29**；審查日：**2026-11-01（Asia/Taipei）**。
基線：`main@d723bc431389ea56bbf2a5b905fa52a8a64b3fee`，已含 [PR #49](https://github.com/lleeoo0611-stack/AU_REE/pull/49) 的 C1/C2 政策與 [PR #50](https://github.com/lleeoo0611-stack/AU_REE/pull/50) 的母子腳本及七案初審。

本輪實際取得原件，解決 **24 個明確列名的文件／範圍／口徑缺口**，並將 **27/195 個五項文件證據格**整理至可送審。**沒有正式 Gate PASS、研究者簽名、獨立 Project ID 核准或 MCDA。** 正式 Structural Cohort 仍未凍結。

### 2026-11-01 延續驗收：Copi 已封存原件交叉審查

下列 Round 01 首輪的 **27/195**、**8 個 ID＋ROLE 文件候選**及 Gate 表為當時的歷史基準；本次在不增加原件／不新建流程的情況下，複核既有發行人委託之工程承包商原件 **`R01-CO-PFS-CONTRACTOR`**。最新 [summary.json](summary.json) 更新為 **29/195 文件格可送審、166/195 仍未就緒、9 個 ID＋ROLE 文件候選**，正式獨立核准 Project、C1、C2 仍均為零。

- **ID 文件格由 BLOCKED_EVIDENCE → REVIEW_READY：**[Ausenco 2025-09-30 Copi DFS 承包公告](https://ausenco.com/insights/ausenco-to-lead-the-definitive-feasibility-study-for-the-copi-project/)（正文第 1、3–4 段）明確命名 RZ Resources 的 Copi 開發計畫，工程研究範圍包含礦山、濕式選礦、稀土精礦廠、尾礦與運輸／供電基礎設施；因此可提供 Copi *開發 Project 層級* 的有界原始文件。**Copi North 的礦床／資源是否屬同一 JORC 或採礦範圍仍待官方 tenement／PFS 核對；Gilligans 不合併。**此文件格仍須獨立 Project 身分決策，無正式 ID 核准。
- **ROLE 文件格由 BLOCKED_EVIDENCE → REVIEW_READY：**同一日期原件的礦種、稀土精礦廠及「About RZ Resources」段落，支持 Copi 計畫將產出含 monazite／xenotime 的 **稀土礦物精礦（planned REE concentrate）**。未確認分離氧化物產量、TREO／NdPr/DyTb 品位、選冶回收率、目前實際投產或 REE 精礦計入當期可比 JORC。
- **可追溯封存：**此文已在原 2026-10-31 archive manifest 以 `R01-CO-PFS-CONTRACTOR` 記錄原始 HTML 32,421 bytes、SHA-256 `d6e9d2f503854ab05e9da0060ca6578ed11836fe6f9b61083e51418bcf05c8cc`、發表日期 2025-09-30，且僅對應 Copi 審查群組。原始 bytes 與 hash 沒有修改；新增文件證據格的可送審狀態須以本地 archive 持續驗證。
- **未變動 Gate：**WINDOW 仍待 2023 PFS 全文和截止日 FID 事件；JORC 仍待 2024 同範圍 REO 原表，GIS_SOURCE/GIS_RELEASE 仍待原生幾何、CRS 與批准。完整五格文件包仍為 BLOCKED_EVIDENCE，C2 只是文件可送審，未獲核准。

### 2026-11-01 來源重訪：WIM 2016 同份原件內的資源基準衝突與獨立 Project 邊界

針對最新 Census **Bungalally `PRJ-867a533642228a73`** 的 `THM_ONLY_AND_205_207MT_SOURCE_CONFLICT` 和 **Avonbank `PRJ-679f5da200a4564c`** 的歷史研究版本，查得同一份 WIM Resource 公司正式原始 PDF：[WIM Company Update, May 2016](https://wp-wimresource-2023.s3.ap-southeast-2.amazonaws.com/media/2023/10/GENERALCOMPANYUPDATEMAY2016.pdf)，發布索引為 [2016-05-13 公司公告](https://wimresource.com.au/media/media-centre/announcements/)。以下是公開原件 **頁面文字核對**，非已完成本機受控 PDF bytes／SHA 的新封存；因此所有新增主張均作為 **外部來源定位線索**，不可冒用原 `R01-S05`、`R01-S01` 受控 HTML 作為 2016 PDF 的原件證明。

- **Bungalally**：PDF 實體 **p10**（0-based p9），`BUNGALALLY PROJECT` 正文寫 **207 Mt**，同頁 **Table 3** 卻將 `Inferred / Total` 記成 **205 Mt @ 2.7% THM**（**1% THM cut-off**），並列 **monazite 1.4%（在 THM 內的礦物組成百分比）**。這證明 205／207 Mt 分歧至少在 2016 同一份 issuer document 的文字／表格內已存在，不能假定是 2026 官網更新造成的版本差異。**205 Mt Table 3 是歷史資源表的原文讀值；207 Mt 正文也保留，兩者仍未正式 adjudicate。**1.4% monazite ≠ 1.4% TREO，未取得分離 REO 氧化物含量，也不能推算 C1 的 REO-in-situ。原始 **2015 Optiro CP MRE**（及可能的 corrigendum）仍須查核。
- **Wedderburn**：同份 PDF 實體 **p11**（0-based p10）`WEDDERBURN PROJECT`／**Table 4** 記載 **223 Mt @ 2.9% THM**、**monazite 1.8% of THM**；目前已取得的 [2015-12-09 RL006195 申請文件](https://wp-wimresource-2023.s3.ap-southeast-2.amazonaws.com/media/2023/10/WEDDERBURNRL006195SUMMARYPROGRAMOFWORK.pdf) 實體 pp1–2 將 Wedderburn Deposit／RL 006195 申請範圍與 WIM 的三個獨立 Project 名稱分開，然而頁內 **RL001695／RL006195** 編號衝突尚待官方礦權檔確認。相關未連結來源為 Legacy `LEGACY:4fb6883c-bded-5363-af78-6fbfef190048`，及 GA `E1:C-8c2269b43a6f62bafcece0`、`E1:C-e5cc6ec45406fff096981e`。三筆僅維持待審，不因共同公司或名稱而自動新建第 40 個 Project 或 Project–Deposit 正式連結。
- **Avonbank**：2016 PDF 實體 **pp3–4**（0-based p2–3）`AVONBANK PROJECT – SCOPING STUDY`、`FINAL PRODUCTS` 說明當時 **Scoping Study 已完成**，提出 **32 年**採礦與約 **6,000 t/year Rare Earth Concentrate**（出口後精礦分選的歷史方案）；另有後續資訊表 **30／36 年**之差。這些屬**不同日期和研究版本的預測**；不得把 2016 已完成 Scoping 誤作 2026 BFS/DFS 原件，或把 2016 濃縮礦計畫當作 2026 實際 REE 產出。現行 `WINDOW`、`JORC` 仍未核准。

**實際已修正資料**：在原有 `structural_round01_reviews.json` 兩個群組的 `conflicts`、`reopen_condition`、受影響 `JORC`／`WINDOW` `limit` 和各 `next_evidence` 精確保留年份、表號、單位及缺口；六份既有衍生 CSV 與 summary 輸入 SHA 同步。**39 群組、29/195 文件格 ready、9 個 ID＋ROLE review packages、原始來源資料、source SHA、Project ID、C1/C2=0 全部未變**。下一個必需動作仍是**受控 PDF 原始 bytes 封存＋hash、2015 Optiro MRE／更正、官方 2015–2026 礦權紀錄及獨立審查簽核**；本次網頁來源定位不替代上述驗收。

## 1. 驗收口徑及限制

本輪依本次使用者的 Execution Round 01 要求，結合既有 [研究架構](../../RESEARCH_ARCHITECTURE.md)、[Cohort protocol](../../P0_COHORT_SELECTION_PROTOCOL.md)、[資源規格](../../P0_PROJECT_RESOURCE_SCHEMA.md)、[C1/C2 政策](../../C0_FREEZE_AND_C1_C2_POLICY.md) 執行。最新 main 未找到另一本以 `AU_REE Pre-MCDA Research Pipeline Completion Protocol` 為檔名／標題的文件；沒有據此另建一套管線或改動准入契約。

本輪五項是 **ID、ROLE、WINDOW、JORC、GIS_SOURCE** 的文件證據審查。`GIS_SOURCE` 僅定位具角色的原始圖件／來源對應；它**不等於**既有正式 `GIS_RELEASE`，也沒有完成 I1–I4 官方圖層 QA。Core／Extended Panel 均未選定。

`REVIEW_READY` 是文件包可交獨立審查；`data_complete` 是本輪五項文件格填足，不代表六項正式 C1 Gate 已核准。Jupiter 的文件包為本輪唯一五格可送審候選，但仍缺正式官方幾何與獨立時點／Gate 審查，不能稱為已准入 Structural Project。其餘 38 包保留 `BLOCKED_EVIDENCE`，逐 Gate 可另有 `REVIEW_PENDING`、`OUTSIDE_WINDOW` 或 `INACTIVE`。

**39/39 是有界分類完成，不是 39 份完整技術報告核准。** 深度分為 9 個技術原件相關頁面審查、17 個原始 HTML 層級審查、13 個沿用先前判讀並明列原件存取限制。後兩類未取得的研究／JORC 日期與範圍保留未知，不以空白推定不存在。沒有重複把 13 個 P1 source cases 加成 13 個新 Project。

### 2026-11-01 Project 身分來源層級的補充驗證

依現行 `outputs/project_entity_register.csv` 與 `outputs/project_entity_membership_487.csv` 原始關聯實際交叉核對，39 個候選 Project 審查群組中，**29 個至少有一筆 `SOURCE_PROJECT_RECORD`，10 個只有 Deposit／Occurrence 等來源紀錄**；29 個之中 **22 個有 `INCLUDE_CANDIDATE` 的 Project 層級來源，另 7 個僅為 HOLD**。其中無 Project 層級來源的 10 個群組是 Barkly、Browns Range、Caralue Bluff、Dubbo、Ironback Hill、Jupiter、Koppamurra、Nolans、Splinter Rock 與 Wudinna。這 10 個已有研究上的候選群組關係，但**不能因官方地質圖資只有 Deposit／Occurrence 就直接升格為獨立開發 Project**；正式審查還需要有明確公司／政府 Project scope 的原始文件、確認與 Legacy 身分的對應，及獨立核准紀錄。

原有 Scheme A 在遇到「既有 Legacy Master 與正式來源 Project 同名」時，`APPROVE_NEW_PROJECT` 會拒絕重複建立，但 `LINK_EXISTING_PROJECT` 也不能連至尚未核准的 Legacy Master。新的明確 `CONFIRM_LEGACY_PROJECT` 審查動作可以在取得簽核後**沿用已存在的 Stable Project ID**，保留 Legacy 對照、來源紀錄與更正稽核。未取得原件與獨立核准的群組維持 Review Pending；這項補強沒有將 39 個候選當成 39 個已證實 Project。

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

### 2026-11-01 後續原始文件定位（未完成封存驗收）
  **截止日前事件已寫回結構化資料（未簽核）：**既有本機封存的 Austrade 原件 `R01-S27`（archive manifest SHA-256 `2bbc7f637693bd71e7875a170cf236e50b8e517a24c6244e072724312debb200`）所對應的[澳洲政府公告](https://international.austrade.gov.au/en/news-and-analysis/success-stories/australias-first-ore-to-oxide-rare-earths-operation-starts-construction)具有 2026-10-27 發布日期，回述 Nolans 於 2026 年 5 月完成 FID、9 月啟動現場施工；[NT 政府 2026-05-21 原始新聞稿](https://newsroom.nt.gov.au/article?id=afd884bccdf73d23f624f2ed39bd6e4d)明確寫出同日 FID，[聯邦政府 2026-10-08 公告](https://www.trademinister.gov.au/minister/don-farrell/media-release/construction-starts-arafura-rare-earths-project)確認施工已開始。此筆作為 `FID_DATE_CORROBORATION` 寫入既有 `structural_round01_reviews.json` 的 Nolans 事件，並同步現有 `study_stage_timeline.csv`、`WINDOW` 證據格、Review Queue 與 summary SHA；將「尚無日期來源」縮小為「公開政府日期已對上，尚待核對封存內容與簽核」。`OUTSIDE_WINDOW`、`C1=0`、`C2=0` 及原 Project/Deposit 身分仍維持未核准。**封存的 `R01-S27` inventory `publication_date` 仍為空；公開網頁的 2026-10-27 與 NT 政府公告 2026-05-21 均屬已定位但尚未對照本機受控原件日期的證據。現行 `FID_DATE_CORROBORATION` 仍保留公開來源 URL 與日期文字，但其結構化 `publication_date`／`effective_date` 均留空，待 SHA-256 原件重驗後才能填入。未從遠端取得或修改原始 bytes，不能聲稱原件日期已核准。**5 月 FID 與 9 月工程啟動不拆為兩個 Project，也不把 2019 DFS 與 2026 改良版資源／產品混加。
- **Nolans — 發行人 2019 DFS 原件可定位 Project–Deposit 範圍：**Arafura Resources 的 [Nolans Project Definitive Feasibility Study Summary Report（2019-02-07）](https://www.arultd.com/wp-content/uploads/2023/01/Nolans_DFS_Summary_Report_-_Final_for_website.pdf) 在原件印刷 p17（§1.2–1.3）將 Nolans 定義為整體礦山及處理設施的開發 Project，p22（§2.1）與 p24–25（§2.3）則把 Nolans Bore 明確列為該 Project 的 REE-P-U 礦床，且 p25 說明周邊 Mulga/Goanna 勘探目標不包含於 Nolans Bore 資料庫。這是針對「原 Census 只有 Deposit/Occurrence 層級來源」的**新發行人 Project-scope 原件定位**，支持待審的 Project／Deposit 層級區分；**不直接新增 SOURCE_PROJECT_RECORD、建立／核准 Project ID、把勘探或處理設施分別計數，也不改 C1/C2/C3**。現階段只完成公開原件及頁碼核對，未把新 PDF bytes/SHA256、來源 ID／日期及與 Legacy Master 的 Project scope 對應放入既有封存／人工簽核紀錄；正式 ID Gate 持續 HOLD。原網頁的上傳目錄日期不作為 2019 文件發布日期；以原件 2019-02-07 為準。
- **Jupiter — 2026-10-20 至 10-29 事件鏈待查範圍縮小：**Critica 的 [正式 Scoping 發布頁（2026-10-20）](https://investorhub.critica.limited/announcements/O12NJO-jupiter-scoping-study-defines-pathway-to-development) 明確界定 100% 持有的 Jupiter REE Project 與 MREC 生產規劃；[發行人公告清單](https://investorhub.critica.limited/announcements)／[ASX 公告索引](https://www.marketindex.com.au/asx/CRI/announcements)列出 10-21 Investor Webinar Presentation、10-23 AGM／股東通知及 10-26 Director's Interest Notice，下一份 10-30 Quarterly Activities **晚於 2026-10-29 cutoff**。21 日簡報有[二次頁面轉錄](https://6ix.com/deck/3hvejo24/critica-investor-presentation-october-2026)（slide 23 為預計 2032 H1 首產的規劃時間線），但**未於受控封存取得 21 日正式簡報 PDF bytes/hash**。公告索引不能證明其間不存在其他具影響的 FID／工程事件；20 日 Scoping 的「未達 FID」也不能無條件延伸至 29 日。保持原 WINDOW 的 REVIEW_READY 文件狀態與 cutoff-date event continuity REVIEW_PENDING，不升格 C1、GIS_RELEASE 或獨立身分核准。

- **Goschen Central — 原 2024 MRE PDF 的替代存取位置：**找到 2024-12-03 ACDC Metals JORC 更新公告（ASX document 02889628）的[公開存取副本](https://www.aspecthuntley.com.au/asxdata/20241203/pdf/02889628.pdf)及[技術顧問網站副本](https://snowdenoptiro.com/wp-content/uploads/2025/01/ACDC-Metals-Announcements.pdf)。公告文字之 p1 Table 1 為 **620Mt（210Mt Indicated＋410Mt Inferred），1% THM cut-off**；p3 Table 2 報告全資源 **584ppm in-situ TREO**；p4 Table 3 同時報告 **1% cut-off 620Mt** 與 **2% cut-off 190Mt**，不是同一 cut-off 的兩個可加總資源。2025 Scoping Study p9 的「2023／2% HM」表題與 620Mt 註解尚需原始表引用／issuer clarification 對照，**不能因找到 2024 MRE 就直接視為原 2025 Scoping 表誤植已正式更正**。原原件 source ID `R01-GC-MRE` 的 URL／SHA 不覆寫；本次找到的是可重新取件的替代 URL。網路 PDF 文字可查，來源 bytes 未存入受控 archive、SHA-256 未獨立核對、視覺表格截圖亦未完成，因此其 Gate/Review 狀態保持原有 `BLOCKED_EVIDENCE`／`REVIEW_PENDING`。
- **Wimmera／Iluka 2025 年報替代原始連結：**既有來源 `R01-WI-AR25` 在舊路徑回傳 404。已從 [Iluka 官方財務成果頁](https://www.iluka.com/investors-media/financial-results) 找到 2026-02-18 刊登的 [2025 Annual Report 原始 PDF](https://www.iluka.com/media/yhwn2hzi/iluka-ar25-final-single-pages-18226.pdf)；瀏覽器 PDF 實體第 23 頁（由 0 起算 P22；文件印刷 p21）「Project Overview／Wimmera」明確描述當時仍在 **DFS 進行中、EES 籌備中**，並說明 Wimmera 稀土將作為 Eneabba refinery 的潛在長期原料。該報告發表於 2026-10-29 研究截止日前，可證明**2026-02-18 當時**的 Project scope／產品規劃與研究狀態，不能證明 2026-10-29 當日 FID 或 EES 是否完成。官方 PDF 可經網頁打開並已視覺核對 p21，但目前執行環境無法下載保留原件 bytes、計算 SHA-256 或在受控 archive 重播；故僅增加舊來源的替代 URL／具體頁碼，不修改 `R01-WI-AR25` 的凍結 URL、access status、正式 WINDOW/ID/ROLE Gate 與核准資料。\n- **Bungalally — 歷史公司原件佐證：**WIM Resource 的[May 2016 Company Update](https://wp-wimresource-2023.s3.ap-southeast-2.amazonaws.com/media/2023/10/GENERALCOMPANYUPDATEMAY2016.pdf) 封面及 p2 Table 1 均報告 **205Mt @ 2.7% THM**，並將 Avonbank、Wedderburn、Bungalally 列為三個不同的 JORC 2012 資源／Project。WIM 現行網站同時於 Overview/JORC 段落報告 205Mt、於 Resource Geology 段落報告 207Mt，**207Mt 的差異仍無正式勘誤證據**。2016 Company Update 不是 Bungalally 完整 JORC Table 1，更未證明完成 Scoping Study 或可比較 REO 基準；保留既有 JORC/ROLE/WINDOW 的 HOLD。新原件連結仍須封存 bytes/hash、核對原表格並審查，不能將文字檢索結果當作獨立簽核。

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
