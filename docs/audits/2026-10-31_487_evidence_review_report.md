# P0.1 — 全量 487 筆來源的證據主張審查（2026-10-31）

**來源快照：2026-10-29**；審查日 2026-10-31。**審查單位是 487 筆 Census source targets**，不是 487 個互不重複的 REE Projects。本次將先前「資料關聯完整性」提升為**逐筆證據層級、可定位的文件線索及官方專案對照**；未完成原文封存／獨立簽核的主張保持 `C1_NOT_RELEASED`。

**可編輯輸出：**[487 筆證據審查 CSV](2026-10-31_487_evidence_claim_review.csv) · [機器可讀摘要](2026-10-31_487_evidence_claim_summary.json) · [西澳政府 20 個 REE Project/resource 線索](2026-10-31_wa_official_ree_project_leads.csv) · [可重跑程式](../../scripts/review_p0_487_evidence.py)。

## 1. 審查對象與方法

本次使用嚴格 `target_id` 對應下列既有已發布資料：

- [487 筆完整來源/身分/礦權審查](2026-10-31_census_487_batch_review.csv)；
- [原 441 筆 reverse-source trace](../../outputs/unlinked_441_source_trace.csv)，含原生 ID 比對、原始資料集快照路徑和 SHA-256 欄位、查詢紀錄 SHA、可定位新增文字來源；
- [95 筆 source locator review](../../outputs/source_evidence_locator_review_95.csv)（涉及 46 個不同 `target_id`）；
- [西澳政府 REE 清單](2026-10-31_wa_official_ree_project_leads.csv)，20 個政府公開的 Project/resource 統計項目；只對 WA 當州的來源名稱做**完全相同名稱**對照，避免以接近名稱推斷礦床歸屬。

441 trace 與另外 46 筆有 source locator review 的來源構成 487 個**不重複的原始目標**。新的 Python 腳本從封存資料重建每列的來源指標、可追溯文件定位和證據狀態，並在實際重跑時額外計算全部輸入檔**原始位元組的 SHA-256**。原先 trace 的 raw file SHA-256 是先前封存登錄值，這次沒有原始完整下載檔可重新逐位元組驗證，故此狀態為**archive metadata reviewed**。

## 2. 全 487 筆證據深度（互斥）

| 深度（`source_evidence_grade`） | 來源列數 | 判讀 |
| --- | ---: | --- |
| `PROJECT_CONTEXT_TEXT_LOCATED` | **42** | 先前文獻定位登錄找到 Project 相關文字位置；**內容／有效日期／原件核准仍待完成** |
| `ARCHIVED_TEXT_LOCATOR_CANDIDATE` | **56** | 原 441 trace 找到 PDF 頁/行或文字位置；**並未證實該段真的支持獨立 Project 身分** |
| `DOCUMENT_REVIEW_NOT_DIRECT` | **4** | 曾審閱文獻，但未有直接 Project 主張證據 |
| `URL_NO_TEXT_LOCATOR` | **24** | 有 URL 卻沒有可靠的文字定位 |
| `NATIVE_RECORD_ONLY` | **336** | 可追溯官方來源 native record，沒有額外已定位的 Project 證據 |
| `AMBIGUOUS_NATIVE_ID` | **2** | 同一原生 ID 對應多列，須核對 id+state/source scope |
| `SOURCE_RECORD_NOT_RECOVERED` | **23** | 缺可確認的原生快照／文件定位；仍保存原 Legacy/source ID |
| **總計** | **487** | 審查層級互斥，不等於 487 個獨立 Project |

**另外一種非互斥來源品質計數**：原 441 reverse trace 有 **407 個 `EXACT_NATIVE_VALUE_MATCH`、2 個 `AMBIGUOUS_NATIVE_MATCH`、32 個 `MISSING_OR_NOT_RECOVERED`**。剩餘 46 個 `target_id` 原本不在 441 trace 子集，須獨立使用 95-row locator；不得將這兩種計數相加成已確認 Project。上述 98 個文字定位（42 + 56）也不等於 98 個有效稀土 Project。

## 3. 本次新增的獨立官方來源

### A. Western Australia REE Official Project Resource Summary（2026 年 2 月發布，資料截至 2026 年 1 月）

**來源原件**：Western Australia Department of Mines, Petroleum and Exploration / Geological Survey of Western Australia，[Rare Earth Elements — Investment Opportunities (PDF)](https://www.wa.gov.au/media/159141/download?inline=)，第 2 頁「Projects with REE resources ranked by contained TREO」表。

- 官方表列 **20 個 REE resource Project/site names**，包含申報資源量 (Mt)、平均 %TREO、contained TREO (kt)、資料日期、業主及 2026 年 1 月時的開發狀態；登錄於本研究 [可編輯 WA 來源表](2026-10-31_wa_official_ree_project_leads.csv)。
- 嚴格同州＋同名比對本次 487 source rows，得到 **20 筆來源列、13 個官方名稱**。這 20 筆中有相同 Project 名在來源出現不止一次，**不能計為 20 個新 Project**。
- **7 個官方名稱未與 487 source name 完全相同**：`Mt Weld`、`Greater Brothers`、`Mt Clere`、`Salazar`、`Mount Ridley`、`Splinter`、`Mt Stirling`。例如官方 `Mt Weld` 可能對應來源 `Mount Weld`；Jupiter 與 Greater Brothers 需保留 Project–Deposit 範圍區別。這些是**待做 alias/parent scope review**，本次不靠字串自動合併或新增獨立 Project ID。
- 在已匹配的 13 個名稱中，包含 **Cummins Range、Yangibana、North Stanmore、Brockman** 等尚未隸屬先前 39-group review 的來源，反映過去 39 群組審查**覆蓋不足**；它們可直接成為下一次 Project identity / economic-stage 核查的待審候選。
- **資源基準審查**：此表為政府彙整 MRE，聲稱依 JORC (2012) 除非另述，但未提供各 Project 的 Measured/Indicated/Inferred 拆分、cut-off、完整 oxide composition／獨立 Competent Person statement；因此只標記 `WA_GOV_RESOURCE_SUMMARY_ONLY_NOT_JORC_APPROVED`，**尚不可填正式 R1/S1**。
- 當中 `Cummins Range` 和 `Brockman` 在 2026 年 1 月資料的官方 Stage 為 Scoping、`Yangibana` 和 `Browns Range` 為 Feasibility、`Mt Weld` 為 Operating；仍需核對是否符合**2026-10-29** 的最新 Stage/FID 和本研究的共同六構面 Gate。

### B. Northern Territory 2023 Exploration Report：Plenty River 與 Bruce Project

**原件**：[EL31225 Final Report (2023)](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/92857/1/EL31225_2023_C_01.pdf)，封面和 Introduction（PDF 前 1–2 頁）：標明 **MetalsGrove Bruce Project**；正文指出 **Plenty River 為 Bruce Project 南部的 prospect**，並說明該 Prospect 的 REE 探勘結果。

已對應本研究 `LEGACY:9adce0d1-2cc3-58c9-b162-0ecdcfc7ca88` 來源列，在證據表標記 `PROSPECT_PARENT_SOURCE_TEXT_BRUCE_PROJECT`；**屬可供 Project–Deposit/Prospect 關係審查的直接文字證據，尚非正式關聯核准、JORC Mineral Resource 或 pre-FID Scoping/PFS 證據**。

## 4. 全量母體對 C1 的實際貢獻

本次提供跨資料來源的**證據分流**：

1. **能追溯原始紀錄**（407/441 exact native record）可作 C0 geological/occurrence census 的資料完整度基礎，但不能自動算 C1 Project。
2. **有 Project-context 定位文字**的 42 筆可優先進入原始文件、Project boundary 和日期之人工審核；原 56 個候選定位需要逐段判定是礦床/礦點或 Project claim。
3. **官方西澳清單 13 個精確同名**可作交叉核對，支持建立新的 **Project identity review queue**；是獨立官方 evidence lead，而非所有 13 個都通過完整 Stage/JORC/GIS。
4. **Plenty River → Bruce Project** 為一筆明確的外部 Project–Prospect parent 文字關係，避免把地質 Prospect 自動視為新的 Project。
5. **正式 C1 規格／核准數未改**：所有 487 列的 `approved_for_C1=NO`，尚無獨立 reviewer signoff／JORC basis／可靠 GIS release。當前主要進展為擴充 Project 探勘母體的**真實證據線索與可再查閱範圍**。

## 5. 下一個 P0 Gate 的可執行清單

- **先處理西澳官方列名專案的 source-to-project 連結**，優先 Cummins Range、North Stanmore、Yangibana、Brockman；分別找到公布時有日期的原始 JORC statement、Project boundary、官方原生 Project ID/礦權角色；用 `MATCH_REVIEWED` 而非 alias 自動合併。
- **清掉 2 個 Ambiguous native IDs 和 32 個 Missing native IDs 的原始來源定位**。原始來源文件未隨 GitHub 複製時，按 manifest 的 SHA 至完整資料歸檔查找，缺件維持 HOLD。
- **審查已定位的 98 個文件文字位置**（42 Project context、56 candidate）；記錄 `supports_claim`、原文頁碼、出版／有效日期、正本 SHA 與 reviewer，在新的 approved evidence tables 中核准後才提升。
- **按州別批次處理其他 336 個 Native Record Only** 的 Project parent；應以官方 Project ID/cadastral tenure 的歷史關係與明確文件證據對應，不因同一礦床名字而合併。
- **正式研究級 R1/S1** 必須由 source-scoped JORC Mineral Resource 及 oxide composition 取得，不把官方總覽數字直接當完整礦床 resource statement。

**重現指令**：

```bash
python scripts/review_p0_487_evidence.py --root . \
  --date 2026-10-31 --as-of 2026-10-29 --output-dir work/evidence
python -m pytest -q tests/test_p0_evidence_487.py
```

此版本保留 [P0 Architecture](../RESEARCH_ARCHITECTURE.md)、[C1 Cohort Protocol](../P0_COHORT_SELECTION_PROTOCOL.md) 和已發布原始審閱快照；GitHub README 與 Changelog 同步更新。**此次採用的政府來源新內容仍以 URL、頁碼與編輯表為可引用線索，尚未將原 PDF 位元組封存於 Git 或取得 source-document SHA-256。**
