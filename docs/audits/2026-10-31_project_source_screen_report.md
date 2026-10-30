# P0.1 — 39 Project Review Groups: Source Verification & Cohort Distribution

**研究執行日：2026-10-31**；**固定判定日期：2026-10-29**。本輪逐案對照 GitHub 冷凍 `project_entity_register.csv` 的 **39 個 Project review groups**、`project_candidate_evidence_review.csv`、既有來源 URLs，再比對公開政府、發行人／公司計畫及技術揭露。這是 **source-level screening**，不是獨立 reviewer sign-off 或已建立可重建文件 SHA-256 的正式 `approved_project_reviews`。

**完整可編輯資料：**[39-project source review CSV](2026-10-31_project_source_screen_39.csv)；[review manifest](2026-10-31_project_source_screen_39.manifest.json)；[既有 P0 Readiness](P0_C1_READINESS_2026-10-31.md)；[C1 Gate 規格](../P0_COHORT_SELECTION_PROTOCOL.md)。

## 1. 母體總數與州別分布

| 州別 | 39 個 Review Groups | 原 `INCLUDE_CANDIDATE` | 原 HOLD |
| --- | ---: | ---: | ---: |
| VIC | **11** | 11 | 0 |
| SA | **7** | 4 | 3 |
| QLD | **7** | 4 | 3 |
| NSW | **6** | 5 | 1 |
| NT | **3** | 3 | 0 |
| WA | **3** | 3 | 0 |
| TAS | **2** | 2 | 0 |
| **合計** | **39** | **32** | **7** |

這是**39 個具有先前審查關聯的 Group ID** 的分布，不代表全澳實際 REE Project 地理分布、各州完整數量或正式可評分 Project 數量。更大的原始母體包含 123,323 筆官方來源、1,006 筆 REE screening candidate 和本次固定 487 個追溯目標，**母體單位不同，不直接相減或相加**。

## 2. 逐案來源篩選結果（互斥分類）

| 審查分類 | 群組數 | 判讀意義 |
| --- | ---: | --- |
| `STUDY_DOCUMENTED_PRE_FID_SCREEN` | **7** | 有來源支持經濟性 Scoping/PFS/DFS 或 FEED/DFS 等研究階段，仍需資源、實際 FID 日期、證據 SHA 與六構面核准 |
| `STUDY_WINDOW_RECHECK` | **8** | 政府標記「under feasibility」、公司提及開發或環評，或只有研究計畫；尚須確認**已完成的正式經濟研究**與當時 pre-FID |
| `RESOURCE_EXPLORATION_NO_STUDY_CHECKED` | **14** | 來源支持勘探／資源／技術實驗，但本輪未確認符合 Scoping–DFS 的完成研究；不是判定研究永遠不存在 |
| `REE_ROLE_HOLD` | **7** | REE 產出/回收承諾或獨立 Project 身分無法與來源關聯完全對上，保留舊有 HOLD |
| `OUTSIDE_PRE_FID_CONFIRMED` | **2** | 截止前已有明確 FID/施工或採礦，依現在研究窗口移出 C1，保留 C2/C3 |
| `ON_HOLD_ACTIVITY` | **1** | 官方指出專案暫停，活動條件未達 C1；須以新時點證據確認能否重啟 |
| **合計** | **39** | **這些是證據篩選狀態，不是 C1 已核准數** |

### 七組已有研究階段證據：優先作 C1 深入核查

| Project | 州 | 已檢查來源所支持的里程碑 | 主要限制 |
| --- | --- | --- | --- |
| [Browns Range](https://invest.northernminerals.com.au/announcements/0zxX3V-september-2026-quarterly-activities-report) | WA | DFS/FEED、尚朝 FID 推進（**2026-10-30 發布的公告，晚於本輪 cutoff**） | 須取 2026-10-29 前已公開的 DFS/MRE 原件做 as-of 核准 |
| [Jupiter](https://investorhub.critica.limited/announcements/O12NJO-jupiter-scoping-study-defines-pathway-to-development) | WA | **2026-10-20 Scoping Study**；2026-10-12 更新 JORC MRE | 不可將較早網站 1.8 Bt 與更新 1.7 Bt 相加；Jupiter 屬 Brothers |
| [Goschen Central](https://acdcmetals.com.au/projects/goschen-central/) | VIC | 公司標記 2025-06 Scoping Study completed | 應與 VHM Goschen 不同 Project；HM/REO basis 要分清 |
| [Bungalally](https://wimresource.com.au/project/bungalally/) | VIC | 公司標示 Scoping Study Stage、JORC 205 Mt @ 2.7% THM | **THM 不是 TREO**，無法直接填 R1 |
| [Wimmera](https://www.iluka.com/community-engagement/wimmera) | VIC | Iluka DFS 進行中、WIM100 為計畫核心 | WIM100/WIM50 資源 scope 與稀土產品基準需分開 |
| [Copi](https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects) | NSW | NSW 列 PFS (2023)；[2026-05 development consent](https://www.planningportal.nsw.gov.au/major-projects/projects/copi-mineral-sands-project) | Development consent **不等於 FID**；需 REE composition/basis |
| [Dubbo](https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects) | NSW | NSW 將其列 2025 Scoping | **2026-08-28** Energy Fuels 完成 ASM 收購，應更新 Company/Project temporal relations |

### 八組研究階段仍須核定

Avonbank（已核准礦權、公司稱 feasibility complete，但未核對實際 FID）、Barkly（政府列 under feasibility，並非已讀到完成的 study）、Charley Creek（政府 under feasibility，需核對正式完成報告）、Donald（網站稱 FID targeted 2026，不能當 FID 已發生）、Fingerboards（**EES Scoping requirements 非礦業經濟 Scoping Study**）、VHM Goschen（多項環評/Work Plan 許可，**不能與 FID 畫等號**）、Koppamurra（SA 政府礦權申請的「scoping」是行政程序，需另看經濟 PFS）、Sandy Mitchell（2026-09 379.4 Mt @ 5430 ppm **MzEq**，公司稱更新 Scoping Study **預計** 2026 完成，待查既有完成研究）。

### 其他 24 組

- **14 組 Resource/Exploration 或未找到完成 Study：**Cannie、Caralue Bluff、Deep Leads–Rubble Mound–Wind Break、Doradilla、Ironback Hill、Kennedy、Milo、Mitre Hill、Narraburra、Splinter Rock、Sybella、Temple Bar、Watchem、Wudinna。這組同時有 JORC TREO 資源、有 NdPr/DyTb-specific 資源、有 THM 或僅 Exploration Target；**不能統一視為資料缺失或同一個成熟度**。
- **7 組 REE role / Project identity HOLD：**Euston、Korella North、Mary Kathleen tailings、Sonoran、Tripitaka、Typhoon、Vecco。特別是 [Vecco Queensland 政府項目](https://www.coordinatorgeneral.qld.gov.au/projects/find-a-project/current-coordinated-projects/vecco-critical-minerals-project) 的產物列 V/HPA/Mo，沒有列 REE；[Mary Kathleen 政府頁](https://www.qld.gov.au/environment/land/management/abandoned-mines/remediation-projects/mary-kathleen) 是舊鈾礦修復與再商業化評估。不得因稀土可能性直接當已核准 REE Project。
- **已超出 pre-FID：**[Nolans](https://international.austrade.gov.au/en/news-and-analysis/success-stories/australias-first-ore-to-oxide-rare-earths-operation-starts-construction)（2026-05 FID、2026-10 construction）；[Balranald](https://www.iluka.com/community-engagement/balranald)（2023-02 FID、2026-01 mining）。
- **活動暫停：**[WIM150](https://www.planning.vic.gov.au/environmental-assessments/browse-projects/wim150-mineral-sands) Victoria 規劃資料列 On hold，不能在未核准 active status 下進 C1。

## 3. 研究母體的三個實質方法學問題

### A. 一個 Mineral Sands Project 可有 REE 產品但缺可比較 R1

Bungalally、Wimmera、Copi、Goschen、Donald 等有公司或政府證據指出 REE/monazite/xenotime 產品，但原資源量可能以 **THM/Heavy Mineral** 表達；[Sandy Mitchell](https://arkmines.com/projects/sandymitchell/) 明確以 **MzEq** 表達、其技術資料另有 TREO 欄位。將所有 THM/MzEq 以 1:1 或簡單比例換成 contained TREO，會改變資源科學語意。

**建議預先定義：**主研究 `C1_DIRECT_REO` 僅納入 source-backed 可比 REO，另以 `C2_HMS_REE_COPRODUCT` 追蹤 REE product/output 與礦物組成；若決定合併兩類，必須先核定可以跨礦床類型比對的 `R1` 定義及轉換證據。**此為待研究者決定的新提案，尚未改動既有 C1 contract。**

### B. 研究窗口的正確範圍是「有日期的實際 Study 里程碑 + pre-FID」

政府的「Under feasibility」分類、EES scoping、礦權申請程序、公司預定的 PFS/DFS、已批准 Work Plan，都不保證「經濟性 Scoping/PFS/DFS 完成」。應以公告文件 `publication_date` 和 `event_status = ACTUAL / PLANNED` 過 gate。

**目前有完整 pre-FID Stage+JORC/REE basis+GIS+獨立核准的 C1 數量仍是未發布，不應把上表 7 或 15 當成 C1 Eligible。**

### C. Project 身分與權利人需要「有效日期」

[Energy Fuels 2026-08-28 收購 ASM](https://investors.energyfuels.com/2026-08-28-Energy-Fuels-Completes-Acquisition-of-Australian-Strategic-Materials) 直接影響 Dubbo 的母公司名稱，但 **Company acquisition 不必然代表 Project tenement 法律登記持有人已同步變更**；應分離 `owner_parent`、`registered_titleholder`、`operator` 與生效日期。同名 Goschen (ACDC vs VHM)、Jupiter/兄弟計畫、Project–Deposit parent-child 應維持獨立關聯。

## 4. 建議下一輪：先決定母體可比較性，再蒐集六構面

**第一優先（C1 底層資源證據）：**Jupiter、Browns Range、Dubbo、Goschen Central、Wimmera、Copi、Bungalally 的 Project ID、完整 Study report 及 JORC R1/S1 basis；並對 Avonbank／Koppamurra／Charley Creek 等重驗日期與 Study completion。

**第二優先（診斷性樣本）：**將 Kennedy、Mitre Hill、Narraburra、Splinter Rock、Wudinna、Deep Leads、Sybella 等有 REE 量測資源的早期個案保留於 C2；等研究問題確定是否需要延長 Stage 窗口，再決定是否另設 exploratory MCDA。

**第三優先（身份與 Scope）：**核對 7 HOLD 與 Mineral Sands 同名及副產品問題；離開 pre-FID 的 Nolans/Balranald 放入 C3 的歷史比較基線，保留而非刪除。

**下一個需討論的決策：**這篇研究的主比較應以「**相同直接 REO 資源量可比**」為前提，還是同時涵蓋「**可回收稀土副產品的礦砂專案**」？兩者都與 REE 供應有關，但需不同 R1 資料規格和完整度檢驗。建議主分析採前者、礦砂副產品作第二層情境，避免為了增加母體數而混用不同 resource basis。

## 5. 驗證界線與後續 Gate

本輪在 CSV 中逐案保留原 `INCLUDE_CANDIDATE/HOLD`，並記錄檢查到的公開來源網址、辨識深度、Stage 與 Resource basis 的判讀、和 C1 尚未核准狀態。部分項目僅有舊版冷凍來源或轉載文件，CSV 已使用 `ARCHIVED_SOURCE_NOT_REOPENED` 或 `ISSUER_REPORT_MIRROR_TEXT` 明確標記。對於截止日後公開的 Northern Minerals 2026-10-30 報告，僅作後續驗證線索，不回填 2026-10-29 snapshot。

**沒有逐份保存原 PDF/HTML 位元組、獨立 SHA-256 與 reviewer signoff，因此本輪不可寫入正式 `inputs/evidence_approvals.csv` 或將任何 Project 標示研究級 `VERIFIED`。** 下輪採用 [Project Gate CSV](../../inputs/templates/c1_project_gate_review_template.csv) 和 [JORC Statement CSV](../../inputs/templates/jorc_resource_statement_review_template.csv)，每份 evidence 綁定原件 SHA、頁碼／段落與有效日期。

**研究階段狀態：**`P0.1 SOURCE_SCREEN_REVIEWED; C1_NOT_RELEASED`。