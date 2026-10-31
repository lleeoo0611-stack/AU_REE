# P0 第四輪：156 筆缺少 Project 父層的逐列證據審查

**審查日：2026-10-31。官方原始資料快照：2026-10-29。** 本輪的審查單位為 156 個 source `target_id`，保留原 272 筆母表、487 筆歷史來源母體及全部 C1 Gate；沒有修改已核准資料與正式排名。

[156 筆逐列可編輯證據表](2026-10-31_156_project_parent_evidence_review.csv) · [148 筆尚未證實 Project 的待查表](2026-10-31_156_project_parent_gaps.csv) · [來源與統計 JSON](2026-10-31_156_project_parent_evidence_summary.json) · [11 筆新官方／公司文件線索](../../inputs/source_review_20261031/round4_156_official_parent_documents.csv) · [重現腳本](../../scripts/audit_p0_156_project_parents.py)

## 1. 全量證據審查結果

| 證據狀態 | Source rows | 判讀與後續處理 |
| --- | ---: | --- |
| 官方／公司文件有具名 Project，與來源名稱可建立核查候選 | **8** | Project name candidate；下一關核對地理邊界、權利、日期、REE 產品與 JORC |
| 找到相似／區域型 Project 文件，但無法證明來源圖徵落在同一 Project 範圍 | **3** | 暫停建立父子關聯，優先補 title/Project extent |
| 沒有新 Project 原文，且政府來源已標為 Prospect／Occurrence／Target／Infrastructure | **32** | 留在 C0，原生實體層級可追溯 |
| 沒有新 Project 原文，但 TAS 政府來源帶有其他明確地質／作業狀態 | **4** | 留在 C0，按原始類別保留 |
| 沒有新具名 Project 原文，其餘官方礦床／資源原始紀錄 | **109** | 保留 deposit/occurrence source evidence，待開發範圍關聯 |
| **總計** | **156** | **0 筆正式 Project/C1 核准** |

補充：「找到具名 Project」指原始外部政府／公司公開文件確實載有該 Project 名稱，且本研究的來源名稱與之有可供審核的對照，**尚未驗證各來源 feature 點位確實落在公開 Project polygon 內**。故已取得原文但尚無正式 Project boundary 核准的數量仍為 156。

**跨來源同州同名：70/156 source rows**。這是資料重複、同一礦床或同名不同礦床的審查線索，**不是 70 個已證實 Project**。完整可追溯欄位包括來源 `target_id`、原生 native ID、原始 source feature locator、chunk SHA-256、原生 entity type／status／commodity、其他同名 target ID、已核准／未核准狀態。

## 2. 8 筆有具名 Project 的外部文件核查

| State · source target | 官方／公司資料可支持的 Project 名稱 | 科學上的 REE 角色及本輪決策 |
| --- | --- | --- |
| WA · **Keysbrook** | [Keysbrook Mineral Sands Mine，WA EPA Assessment 1580](https://epa.wa.gov.au/proposals/keysbrook-mineral-sands-mine) | 礦砂 Project 有官方記載；未證實分別申報 REE 產品，列具名 Project 候選 |
| WA · **Yalyalup** | [Yalyalup Mineral Sands Project，WA EPA Assessment 2141](https://www.epa.wa.gov.au/proposals/yalyalup-mineral-sands-project) | 礦砂 Project 來源明確；無法由該頁確認 REE product stage |
| WA · **Cyclone** | [Cyclone Mineral Sands Project，WA EPA Assessment 1970](https://www.epa.wa.gov.au/en/proposals/cyclone-mineral-sands-project) | 公開產品為 zircon 與 high-titanium minerals；不能把礦砂資源等同 TREO |
| WA · **Mulga Rock** | [Mulga Rock Uranium Project，WA EPA Assessment 1979](https://epa.wa.gov.au/proposals/mulga-rock-uranium-project) | 公開 EPA 資料證實鈾與多金屬開發；REE 的實際回收／獨立開發角色待查 |
| WA · **Cooljarloo JV** | [Cooljarloo Joint Venture，WA EPA report 369](https://epa.wa.gov.au/proposals/synthetic-rutile-plant-muchea) | 有歷史 JV 與 Cooljarloo mine 的正式政府文件；是否為本來源礦點同一子範圍仍需核對 |
| WA · **Dongara Project** | [Dongara Titanium Minerals Project，WA EPA Assessment 1698](https://epa.wa.gov.au/proposals/dongara-titanium-minerals-project) | 名稱截短對照；應確認 Dongara Project 原礦床地理範圍，不自動同一化 |
| VIC · **Wemen** | [Victorian Government Library：1998 Wemen mineral sands EES](https://www.vgls.vic.gov.au/client/en_AU/vgls/search/detailnonmodal?d=ent%3A%2F%2FSD_ILS%2F0%2FSD_ILS%3A301761~ILS~0&ps=300&qu=Victoria.+Planning+Panels.) | 歷史礦砂開發審查可查；不代表 2026 年仍在開發，也不代表有 REE 產品 |
| VIC · **Nowie** | [VHM ASX announcement 2025-10-15，Figure 1](https://announcements.asx.com.au/asxpdf/20251015/pdf/06qkvvhp20rxx2.pdf) | Nowie Project 與 EL6666 可由 issuer 圖件辨識；與 Goschen 不應直接合併，REE/JORC basis 另核對 |

這 8 筆是**8 個來源列**，並未直接批准為 8 個可比較的 pre-FID 稀土開發 Projects；後續應以正式核准的 Project boundary、權利主體、REE role、公布日期與 resource scope 決定是否納入 C1。

### 3 筆只有名稱相近的證據

- **Tutunup West（WA）**：政府 [Tutunup Mineral Sands Project](https://epa.wa.gov.au/en/proposals/tutunup-mineral-sands-project) 頁面並未證明名稱中的 West 位於政府 Project polygon 內。
- **Goschen South（VIC）**：[Goschen REE Project](https://www.planning.vic.gov.au/environmental-assessments/browse-projects/goschen-mineral-sands-and-rare-earths-project) 有政府範圍資料，但未直接證明 *Goschen South* 的來源 feature 是正式礦區之一。
- **Wim deposits（VIC）**：政府 [Wimmera Mineral Sands Project](https://www.planning.vic.gov.au/environmental-assessments/browse-projects/wimmera-mineral-sands) 明確指向 WIM100，原資料卻是複數區域泛稱，不能將同名區所有 deposits 視為同一 JORC 資源 statement。

## 3. 母體地域、來源與 REE 資料語意

| State | 需要 Project parent 的原始紀錄 |
| --- | ---: |
| WA | **72** |
| NSW | **33** |
| SA | **19** |
| QLD | **10** |
| VIC | **10** |
| TAS | **9** |
| NT | **3** |
| **合計** | **156** |

原始 156 筆的 REE 依據包含：

- **93 筆**聯邦圖徵有 `Rare earth elements` 等商品欄位，但該欄位本身未提供 Project parent；
- **14 筆**南澳 `MAJOR_COMMODITY_CODE` 並非 REE，REE 為聯合申報的礦物／商品資訊，**不把它當作稀土主產品**；
- **32 筆**西澳 MINEDEX 為 Prospect／Occurrence／Target／Infrastructure 等原生地質／礦業實體；
- **8 筆**塔州來源 `RESOURCES=N`，依來源原意保留資源揭露狀態；
- **9 筆**有其他政府礦種登錄但缺獨立 Project resource 依據。

## 4. 下一個需要取得的證據

**145 筆**尚無新增外部具名 Project 原文；其中一部分已能透過官方 raw source 的 native status 確認屬地質／勘探層級，維持 C0 即可。可優先處理**70 筆跨來源同州同名紀錄**，逐一用 source-native ID、座標誤差、同時間地質名稱及 tenure/ownership 檢核是否為同一 Deposit 的不同來源；這是去重審查，不能直接升格 Project。

Project parent 的下一階段驗證順序：具名官方 Project → 廠商/礦權時序 → 官方 Project 空間邊界 → Deposit 來源點／面確定歸屬 → REE 產品／礦物與 JORC 來源範圍 → C1 gate。每次新增證據需保留引用文件的發表日、原文 locator、來源位元組 hash 及 reviewer signoff。

## 5. 重現指令

```bash
python scripts/audit_p0_156_project_parents.py
python -m unittest discover -s tests -p test_p0_156_project_parents.py -v
```

由 `docs/audits/2026-10-31_272_project_parent_evidence_queue.csv`、`data/source_snapshots/2026-10-29_272_native_features.jsonl`、`docs/audits/2026-10-31_487_evidence_round2_review.csv` 與新增的 11 筆文件來源表重建 156 CSV、待查 CSV、摘要 JSON。腳本不修改既有 272／487 母表，不自動核准 Project ID、Resource 或 C1。
