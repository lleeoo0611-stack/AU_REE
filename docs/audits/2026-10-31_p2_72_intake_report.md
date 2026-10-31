# P2 — 72 筆 Census 來源審查：案例化與首批文件驗證（2026-10-31）

**資料截止：2026-10-29**　｜　**來源：487 筆 Census 凍結審查資料**　｜　**進度：`P2_INTAKE_AND_TARGETED_DOCUMENT_REVIEW`**

## 1. 研究位置與分母

本文件中的 **P2 = Census 來源審查優先序**，承接先前完成的 P1 73 筆來源查核；與 [v2 Research Implementation Plan](../RESEARCH_IMPLEMENTATION_PLAN.md) 的 **P2.1 Rank Robustness / P2.2 Drivers（Aim B/C）**分屬不同任務。後者須待 C1 六構面母體與方法參數核准後才能發表研究級結果。

從固定的 [487 筆審查表](2026-10-31_census_487_batch_review.csv) 依 `action_priority=P2` 取得 **72 個唯一 target_id**，與[已完成的 P1 73 筆](2026-10-31_p0_p1_73_terminal_decisions.csv) **沒有任何相同 target_id**。P2 來源分為 22 個已存在的 **review group**（共 47 source rows）與 25 個未連結來源獨立處理，合計 **47 個審查案例**。Review group 不是正式 Project ID。

| 原本 P2 優先動作 | Source rows | 後續核對 |
|---|---:|---|
| `CHECK_REE_RESOURCE_AND_COMPLETED_STUDY` | 37 | 同一 Project／Deposit 範圍、JORC 類別與 cutoff、經濟 Scoping/PFS 正式發表時間 |
| `ESTABLISH_DISTINCT_PROJECT_IDENTITY_AND_SOURCE_LINK` | 25 | Legacy／原生 source feature、礦床與 Project 父層文字、歷史 licence 與正式邊界 |
| `REVIEW_REE_ROLE_AND_INDEPENDENT_PROJECT_ID` | 9 | 商業 REE 產品／礦物存在與可回收性、是否為核准 Project |
| `VERIFY_CURRENT_ACTIVE_STATUS` | 1 | 活動狀態、FID 及研究窗口 |
| **合計** | **72** | 保留每筆原始 target ID、州別、資料種別與審核決策 |

來源分布：QLD 17、VIC 12、TAS 12、SA 11、NT 8、NSW 6、WA 6。

## 2. 首批定向證據（7 條，覆蓋 22 筆來源）

所列數值是**發行人／政府文本內同一 Project 或礦床群的主張**；尚未通過獨立 Project–Deposit 關聯、JORC、GIS 或正式 C1 六層 Gate，因此不能按來源列數倍增，也不能拿來直接評分。

| 審查案例 | 已定位來源與截至日期 | 主張、量測基準與必要核對 |
|---|---|---|
| **Kennedy**（QLD；3 rows） | [DevEx 2026-03-13 半年報告](https://announcements.asx.com.au/asxpdf/20260313/pdf/06xdgw8tr21hqs.pdf)，Directors’ Report 印刷頁 8、Competent Person 頁 10 | 2024 年 JORC Inferred 資源：150 Mt @ 1,000 ppm **TREO**（325 ppm **TREO–CeO₂ cutoff**）；或 88 Mt @ 1,200 ppm（475 ppm cutoff），是不同 cutoff 的替代陳述，不能相加；ANSTO 浸出試驗有磁性 REE 回收資料，仍待核對經濟研究 |
| **Narraburra**（NSW；4 rows） | [Godolphin 2026-04-29 季報](https://godolphinresources.com.au/downloads/reports/grl_qr202603.pdf)，印刷頁 8；頁 9 記錄 EL8420 | 94.9 Mt @ 739 ppm **TREOY**；47.6 Mt Indicated 與 47.4 Mt Inferred 可能有公布時四捨五入，20 Mt @ 1,079 ppm **TREO** 是高品位子集。發行人的 **Lewis Ponds** Scoping Study 屬另一個金銀計畫，**不能套用到 Narraburra** |
| **Deep Leads–Rubble Mound–Wind Break**（TAS；6 rows） | [ABx 2026-04-30 季報](https://abxgroup.com.au/announcements/7515516)，Rare Earths Strategy／MREC 章節 | 聯合三個礦床的 89 Mt @ 844 ppm **TREO** 資源，41 Mt Inferred、42 Mt Indicated、6 Mt Measured；已測試 MREC 樣品，**同一個 89 Mt 不得拆作六筆 source 獨立資源** |
| **Sybella**（QLD；3 rows） | [Red Metal 2026-02 展示簡報](https://redmetal.com.au/wp-content/uploads/2026/02/Red_Metal_RIU_Explorers_February_2026_final_ASX.pdf)，投影片 13 | 正在進行浸出／工程評估，提出 2026 Q3/Q4 完成 Scoping 或 PFS 的目標；「預定研究」本身不能認定為正式已發表研究 |
| **Milo**（QLD；4 rows） | [2026-05-01 發行人市場文件](https://announcements.asx.com.au/asxpdf/20260501/pdf/06z46jxzst25lx.pdf)，Milo 資源報告範圍段落 | 提及舊有資料須重新審核與準備 JORC 2012 Table 1、更新銅當量計算；不能繼承成當前有正式核准的 REO Mineral Resource |
| **Bruce Prospect**（NT；1 row） | [NT GEMIS EL31225 2023 年報](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/92857/1/EL31225_2023_C_01.pdf)，原生頁碼待核 | Bruce Project 與 Plenty River 具文獻關聯；Legacy 的 Bruce Prospect source ID 尚不能直接視為當前 Project 實體 |
| **Plenty River**（NT；1 row） | 同一 [NT 2023 年度報告](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/92857/1/EL31225_2023_C_01.pdf)，原生頁碼待核 | Plenty River 為 Bruce 上層 Project 的 prospect 關聯線索，保留自己的歷史 source ID；Project/GIS 仍待原生 scope 核准 |

目前另有 **27 筆來源**沿用已存在 review group 文件線索，**23 筆來源**僅有前次證據／原生追溯，合計尚未新增本輪定向文件的 **50 筆來源**。它們各自仍保留原始搜尋範圍、既有分級與下一步，不把「尚未補文件」寫成「無稀土」。

## 3. 可重跑的資料流程

```text
487-row frozen census ─────┐
487-row evidence round2 ──┤
39 review group screens ──┼─ exact target_id / existing review_group_id ──► P2 72 sources
P1 73 terminal decisions ┤        │                                    └─► 47 review cases
7 dated case-doc leads ───┘        └─ P1 overlap=0, source hash and C1=NO assertions
```

- [72 筆逐來源 CSV](2026-10-31_p2_72_source_intake.csv)：原生 ID／來源 SHA（如可得）、原始州別與資料類型、既有 group、tenement 結果、當次文件／cutoff／grade basis、下一步。
- [47 案例審查 CSV](2026-10-31_p2_case_review_queue.csv)：case key、target IDs、來源別名、resource nonaddition、經濟研究與正式審核狀態。
- [7 筆定向文件輸入 CSV](../../inputs/source_review_20261031/p2_72_targeted_documentary_leads.csv)：可增加查核來源；每一列必須有文件定位、公布時間、資源與 Project 範圍。
- [QA 摘要 JSON](2026-10-31_p2_72_intake_summary.json)；[Python 重建腳本](../../scripts/audit_p0_p2_72_intake.py)；[單元測試](../../tests/test_p0_p2_72_intake.py)。

```bash
python scripts/audit_p0_p2_72_intake.py --check
python -m unittest discover -s tests -p 'test_p0_p2_72_intake.py' -v
```

規則：同名、同 group 或 native point-tenement overlap 皆不能直接決定 Project 身分；TREO、TREOY、Y₂O₃、Nb₂O₅、HM/THM 分開記錄；總量與 subset 不重複加總。每個 source ID 只有一條 P2 分流，修改時只更新 evidence input 再使用腳本 `--write` 重建，先 `--check` 再提出 PR。

## 4. 與 P1 結案的銜接

截至本次，P1 的 73 筆文獻搜尋與來源級路由**已完成**，四個 PR #26/#27/#28/#31 已合併 main，GitHub Actions Python 與 R 驗收通過。但 P1 不等於所有相關專案已獲 C1 核准：

- [Issue #30](https://github.com/lleeoo0611-stack/AU_REE/issues/30)：四份西澳 WAMEX 已有 A-number 與可查文本，仍待取得**官方 PDF 原件**、SHA-256 和原始頁碼；[已備妥的索取稿](../requests/2026-10-31_wamex_primary_pdf_access.md)尚未寄送。
- [Issue #32](https://github.com/lleeoo0611-stack/AU_REE/issues/32)：原 P1 13 個正向案例獨立 Project／JORC／GIS／六構面 Gate；不與 P2 本次新 47 案自動合併。

**本次 Gate 結果：**P2 72 筆來源入口與首批 7 個案例的文獻判讀已建立，P2 全案正式文件核准尚未結案；C1、正式 JORC REO、GIS_RELEASE 均 0。本輪未產生任何正式 MCDA 排名。
