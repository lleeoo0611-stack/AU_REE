# P2 — 412 筆 HOLD 中 28 筆來源的第一輪資料與文獻查核

**研究版本：P2 Phase 1 / 2026-10-31**  
**政府/研究來源截止：2026-10-29；查核日：2026-10-31**  
**單位：原生 source target ID（28），27 個暫定來源／站址案例，不是 Project 數量。**

## 1. P1 交接及本輪範圍

原 487 筆 C0 來源中有 412 筆 `HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE`。本輪**不修改**原 412 筆分層和 v1/v2 納入關卡，分別為：

| 固定工作批次 | Source rows | 處理階段 |
|---|---:|---|
| P1 | 73 | 文件查核已結案；來源簽核與 WAMEX 政府原件獨立追蹤 |
| **P2** | **28** | **本輪：來源分組、首輪證據與待補範圍** |
| P3 | 216 | 未處理 |
| P4 | 95 | 未處理 |
| **HOLD** | **412** | 原始 Census 母數不變 |

P2 28 列由 **22 筆 Legacy** Project 名稱來源與 **6 筆 E1** 原生政府來源構成，分成 27 個 `P2G-0001..0027` 來源案例。唯一多列站址鍵為 **Mary Kathleen 2 筆 Deposit source**；同地區的 Legacy **Mary Kathleen tailings** 保留另一 ID／案例。資料庫原本 P2 來源 **19 筆缺外部文件定位、6 筆已有原始地質紀錄、3 筆已有部分政府/發行人文件**，不是說 19 筆地質上不存在。

已產生 [28 列來源分流](2026-10-31_p2_28_source_triage.csv)、[27 個案例表](2026-10-31_p2_27_case_triage.csv)、[P2 分母與 provenance QA](2026-10-31_p2_phase1_summary.json)。證據輸入 [p2_27_case_evidence.csv](../../inputs/source_review_20261031/p2_27_case_evidence.csv) 可直接擴充，輸出由 [audit_p2_28_initial_triage.py](../../scripts/audit_p2_28_initial_triage.py) 以 `--write` 重建，以 `--check` 固定 QA。

## 2. 來源證據分布：27 個 provisional site cases

| 目前 provenance 級別 | 案例數 | 含義 |
|---|---:|---|
| `DOCUMENTARY_LEAD_NO_APPROVED_SOURCE_PROJECT_JOIN` | 11 | 有政府、發行人或既有同名來源線索，Project / Deposit / Title 的原生關係仍未核准 |
| `LEGACY_ID_ONLY_NO_SOURCE_SCOPED_PRIMARY` | 12 | 僅原始 Legacy ID／名稱；本輪尚未找到可與該原始 ID 對應的 Project 主文 |
| `NATIVE_GOVERNMENT_FEATURE_NO_PROJECT_PROOF` | 3 | VIC MINSITE 原生歷史紀錄，主體 commodity／Project role 未獨立判定 |
| `REGIONAL_INDEX_NOT_PRIMARY_SOURCE_MATCH` | 1 | Webb Au 有地區次級索引，但未能證明 Legacy 名稱對應該現代礦權 |
| **總計** | **27** | 包含 28 個 original target IDs |

上述 provenance 各類**均不等於正式准入**。`independent_project_id_approved=NO`、`independent_JORC_REO_approved=NO`、`C1_admitted=NO` 保持不變。

## 3. 有明確進展的案例

| 案例 | 首輪判讀與文件依據 | 下一個驗證關鍵 |
|---|---|---|
| `P2G-0012` Mary Kathleen（2 source deposits） | [QLD 政府](https://www.qld.gov.au/environment/land/management/abandoned-mines/remediation-projects/mary-kathleen)確認原 uranium mine 第二期生產 1982 年結束、之後除役；兩筆來源點仍各自保留 | 原礦床地點與尾礦現代權利分離，歷史礦場不自動轉 REE Project |
| `P2G-0011` Mary Kathleen tailings（1 legacy） | 同一州政府網站有尾礦 REE 潛力研究；[Bayan 2026-09-07 ASX](https://www.marketindex.com.au/asx/bmm/announcements/yttrium-upgrade-technology-initial-results-6A1342411) 的 UQ 實驗使用 Mary Kathleen tailings liquor，包含合成加標溶液，為 bench-scale 流程研究 | 分清來樣來源、礦權與商業 Project 身分；該加工試驗不直接建立尾礦 JORC MRE |
| `P2G-0013` PORT PIRIE REE（1 native） | [SA SARIG Deposit 8908](https://minerals.sarig.sa.gov.au/MineralDepositDetails.aspx?DEPOSIT_NO=8908) 說明 1955–62 uranium treatment site、歷史稀土氧化物／tailings 回收研究與已復育 `Treatment Site`；部分 Y₂O₃/Sc₂O₃ 是 1960–1970 年代非 JORC 估算 | 不將歷史尾礦估算轉成現代 TREO JORC；亦不把同在 Port Pirie 的第三方加工設施自動視為此地塊 |
| `P2G-0014` Anchor Tin Deeps（TAS legacy） | [Mineral Resources Tasmania](https://www.mrt.tas.gov.au/exploration/exploration_drilling_grant_initiative_edgi_results/round_8) 列 2024 年 `ATD1/ATD2`，目標 tin–lithium–REE，EDGI 原始 drill report 已開放 | 回查 EL17/2017、鑽孔表格／REE、正式 JORC 和原始 Legacy ID 地理對應 |
| `P2G-0004` Boulder Ridge（NT legacy） | [NT Geological Survey 官方 REE 專頁](https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree) 載有 xenotime-bearing veins 及規劃 maiden drilling；屬探勘線索 | 原始 Legacy Source 的座標／礦權與 Northern Minerals 現行區塊核對 |
| `P2G-0005` Bruce Prospect、`P2G-0008` Plenty River | 2023 年稀土探勘與 2024 年 Bruce gold–copper 方向見 [MetalsGrove 2024 ASX](https://announcements.asx.com.au/asxpdf/20241024/pdf/069hs405nzzgxf.pdf) 與 [NTGS 歷史 EL31225](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/92857/1/EL31225_2023_C_01.pdf) | Bruce、Plenty River、EL31225 舊礦場與現有 Project 的身分須各自確認，不可只用共現的名稱／地區合併 |
| `P2G-0007` Edwards Creek（NT legacy） | [NT 政府勘探登錄](https://environment.nt.gov.au/mining/exploration) 有 MetalsGrove Edwards Creek，先維持 Exploration 來源線索 | 同名 Legacy 區塊是否即登錄礦權、REE 是否為實際產品/資源 |
| `P2G-0010` Elaine Dorothy | [歷史發行人礦化來源](https://aukingmining.com/site/pdf/69270e44-d780-40f0-9aec-b1e695241a0e/CuCoREEU-Mineralisation-at-Elaine-Dorothy-Project.pdf)及 2026 [Mineralium Deposita 對前人資料整理](https://link.springer.com/article/10.1007/s00126-026-01485-w)；為 Cu–Au–REE/U 礦化研究，現代商業 REE 專案身分尚未核實 | 2010 礦化／JORC 分類、2017 權利移轉、2026 holder，與 Mary Kathleen 礦場區分 |
| `P2G-0021` Douglas Project | [Iluka](https://www.iluka.com/community-engagement/douglas/) 證實 Douglas HMS mine 2004–2012 已生產、目前復育 | Legacy 原生 Project ID 缺座標，不藉同名把原生 source 掛上 MIN5367；曾生產礦場不能直接成為 pre-FID |
| `P2G-0026` Talisker | 引用原 [P1G-0022 西澳 Talisker / Fraser Range](2026-10-31_p1_44_case_resolution.csv) ASX 2025-08-14 來源，與 Salazar 分屬不同範圍 | Legacy Talisker → 2025 Project relationship 尚未簽核；不能繼承 Salazar TREO MRE |

### 需要保留的名稱與地理反例

**Bondi**：VIC MINSITE `1015256` 原生點在 **-35.13213、142.54027**；Iluka [Douglas 礦場](https://www.iluka.com/community-engagement/douglas/) 也含 Bondi Main／East／West 之名，但兩者不是可憑字串核准的同一 Project。此筆的 `P2G-0019` 標記 `BONDI_NAME_COLLISION_DO_NOT_LINK_DOUGLAS`。

**Orion、Danube Prospect**：保留 VIC MINSITE 原始 Feature ID／SHA；來源中「Critical Minerals」主題分類與商業 REE 產品證據不同，不能直接作 Project。先列 native-only。另 **Webb Au** 目前只有區域二級索引，不可把整個 Webb exploration record 的 REE 記載轉為該 Legacy 項目。

## 4. 研究管線及剩餘工作

P2 已建立固定 **28 target → 27 evidence case** 交叉表，與 P1 的 73 筆及 P3/P4 完全不重疊。下輪應依來源優先序取得：**原始歷史 ID/座標 → 同期 tenement holder / licence polygon → dated Project / Deposit crosswalk → REE product role / JORC basis → published pre-FID study → GIS/Panel Gate**。先處理官方原文可用且可能有 REE 的 **Anchor Tin Deeps、Boulder Ridge、Mary Kathleen tailings、Port Pirie、Bruce/Plenty River、Elaine Dorothy、Edwards Creek**。

另有 **12 個 Legacy site cases** 仍僅有舊 ID／名稱，本輪未取得可對應的原始 Project PDF，不能寫為「不存在 REE」。分母不會因缺證據縮小。

### P1 收尾交接

- **[Issue #29](https://github.com/lleeoo0611-stack/AU_REE/issues/29)：Closed。** 公開 Repo 後 CI 恢復，P0/P1 PR #26→27→28→31 皆合併；最後 `main` Python、R 合成測試綠燈。
- **[Issue #30](https://github.com/lleeoo0611-stack/AU_REE/issues/30)：Open，資料取得阻擋。** 四份 WAMEX `A119194/A120393/A129842/A109188` 政府 PDF 原件與 SHA 仍未封存，已備妥[官方郵件申請稿](../requests/2026-10-31_wamex_primary_pdf_access.md)，未寄送。不可用 P2 開案替代原始封存。
- **[Issue #32](https://github.com/lleeoo0611-stack/AU_REE/issues/32)：Open，正式 C1 審查。** P1 的 13 個正向案例／22 筆來源仍為 Gate HOLD。這屬獨立 JORC / Project / GIS / Panel release 工作。
- P2 的任何 Project lead、原礦場或 tailings work **都不能自動變為 C1**；本輪未修改 `project_master`、JORC approvals、GIS_RELEASE、six-domain panel 或已凍結 G0/R1/S1/RS。

## 5. 可重跑驗收

```bash
python scripts/audit_p2_28_initial_triage.py --check
python -m unittest discover -s tests -p 'test_p2_28_initial_triage.py' -v
```

輸出為 CSV／JSON／Markdown，符合 Git 版本控制及後續更新資料庫需求。下次新增 Project 來源，更新 curated case evidence CSV，再重跑 `--write`，保留原始 Legacy／E1 target ID。
