# P0 第三輪 — 272 筆 Project 歸屬、23 筆原生資料恢復與南澳 ID 唯一化

**審查日期 2026-10-31；原始官方來源凍結 2026-10-29。研究單位為來源 target_id，不直接等於獨立 Project。**

## 1. 驗證結果

| 工作 | 前一輪狀態 | 本輪實際驗證結果 |
| --- | --- | --- |
| 272 筆只有原生資料、未有 Project 歸屬 | 272 筆 | **272/272** 對回官方原始 source feature；0 源 ID 缺漏與 0 source-feature 配對歧義 |
| 原始來源資料未恢復的 23 筆 | 7 筆 GA JSON + 16 筆 Legacy 歷史列僅見恢復索引 | **23/23 位元組雜湊與原始列識別驗證成功**；實際 GA JSON / SA CSV 原始資料片段已保存 GitHub |
| Olympic Dam / Clarke 2 個重複 native-ID 問題 | 3000 有 4 筆、11849 有 6 筆 source rows | **10/10** 使用 `SA_CRITICAL_REE:MINERAL_DEPOSIT_NO:OBJECTID` 建立唯一 source-feature key；保留 **2 個** MinDep 礦床 ID |
| 正式 Project–JORC–GIS / C1 核准 | 原本不核准 | **0** 自動核准；本輪沒有變更研究 cohort 或 MCDA 排名 |

重現性與輸出：
- [272 筆原始 source feature + parent 欄位](2026-10-31_272_native_project_parent_audit.csv)
- [272 筆補強文件後的最終 Project parent evidence queue](2026-10-31_272_project_parent_evidence_queue.csv)
- [23 筆來源原始 byte/hash 核對表](2026-10-31_23_original_native_bytes_verified.csv)
- [10 筆 SA 唯一來源圖徵鍵](2026-10-31_sa_10_compound_feature_keys.csv)
- [完整原始來源與快照 Manifest](2026-10-31_native_parent_reconciliation_manifest.json)
- [Project parent 證據摘要](2026-10-31_272_project_parent_evidence_summary.json)
- [13 筆新官方／公司文件父專案候選](../../inputs/source_review_20261031/round3_272_project_parent_issuer_leads.csv)

## 2. 272 筆 Project 歸屬結果

經官方原生欄位、前期 6 筆獨立文件與新找到的 **13 筆來源–Project** 文件證據整合：

| Project/Deposit 關聯狀態 | 來源列數 | 資料庫處理 |
| --- | ---: | --- |
| 有稀土相關 Project／探勘母專案的候選文件關聯 | **15** | Evidence-backed candidate parent；等待 Project/Deposit 邊界及核准 |
| 已有正式專案名字，但為非稀土開發主張（Carrapateena、Peculiar Knob） | **4** | 保留官方 Project 關聯，**不納入 REE C1** |
| 地質圖徵層級為 Occurrence/Prospect 等非 Project 實體 | **92** | 保留 C0 occurrence inventory；獨立 Project 須另行證明 |
| TAS 原始資料有上層 Deposit ID（並非 Project ID） | **2** | 建立 Deposit 層級候選，待核對 Project |
| VIC 原始欄位為「Critical Minerals」主題類別（並非 Project 名稱） | **3** | 排除錯誤 Project parent |
| 目前缺少可定位的 Project 母體關聯文件 | **156** | Source native 已驗證，仍待找官方專案身分與歸屬 |
| **合計** | **272** | **全部來源列已逐件分流；C1 自動通過 0** |

**統計單位重要限制**：以上 15 筆屬 *source rows*，**不代表 15 個新的 REE Projects**。其中 Redlings 1/2/3 各有 E1+Legacy 對應，6 筆指向同一 Redlings Project；Korella 有 GA 兩個來源紀錄，2 筆指向同一歷史 Project 名稱。新找到的 13 筆實際涵蓋 7 個不同 Project 名稱。先前 6 筆中 Narraburra、Milo 為稀土相關候選，另外 4 筆為 Carrapateena／Peculiar Knob 的非稀土礦業開發關係。

## 3. 可定位的額外 Project parent 來源

| 原始來源單位 | 文獻證據所指 Project | 可定位依據與差異 |
| --- | --- | --- |
| Redlings 1、2、3 Jungle Well（E1+Legacy 共 6 筆） | **Redlings REE Project** | [2019 ASX Redlings announcement](https://www.asx.com.au/asxpdf/20190625/pdf/4463d30d0cdm08.pdf)，pp.3–4，E37/1311；三處 Prospect/原生礦點，1 個 Project 候選 |
| Aileron（WA） | **Aileron Niobium–REE Project** | [Encounter Resources 2026 年公司披露](https://www.encounterresources.com.au/)，有具名 REE 研究／勘探單位；仍需有效日期與礦權界線 |
| Coburn（WA） | **Coburn Mineral Sands Project** | [Strandline 2023 報告](https://strandline.com.au/wp-content/uploads/2023/07/Shaws-Update-Report-24-July-2023.pdf)；Project 名稱成立，**REE 商業產出角色尚未獨立成立** |
| Talisker / West Cobar（WA） | **Fraser Range Project** | [2025 ASX announcement](https://announcements.asx.com.au/asxpdf/20250814/pdf/06mvmb9r2vhdhs.pdf)；Fraser Range 與鄰近 Salazar **不同** |
| Glenaladale（VIC） | **Fingerboards Critical Minerals Project（Glenaladale 礦床的一部分）** | [Victoria Planning referral 2026R-01](https://www.planning.vic.gov.au/environmental-assessments/browse-projects/referrals/fingerboards-critical-minerals-project) 明示 Project 位於 Glenaladale Deposit 內，屬**部分範圍關係** |
| Copi North（NSW） | **Copi Mineral Sands Project** | [RZ 2024 EIS Appendix 15](https://rzresources.com/wp-content/uploads/2024/06/26.-Appendix-15-Economic.pdf)，§2.1 p.20：Copi North EL8312 + Sunshine EL8385 |
| Korella（QLD，兩個 GA 來源） | **Korella / Korella Bore 歷史 Project 名稱** | [Austrade 2019 Critical Minerals Prospectus](https://kic.org.au/wp-content/uploads/2020/2020/04/Australian-Critical-Minerals-Prospectus_Lithium-Valley_RS_March-2019.pdf) p.74；**歷史潛在 REE Project**，目前開發狀態與業主必須重驗 |

Project–Deposit 關聯有 3 種不同語意：Project 名稱與 Deposit 相同、Deposit 作為 Project 中特定子範圍、以及歷史投資清單把地質礦床當作潛在 Project。下游地質資源與社經變數只能依驗證後的 source scope 加總，不能把上述全部當成互相獨立的專案。

## 4. 原始資料的實體保存與 SHA-256

完整官方資料可由 2026-10-29 [GitHub Actions raw-first run #40821122179](https://github.com/lleeoo0611-stack/AU_REE/actions/runs/40821122179) 原始 artifact `australia-national-unfiltered-raw-inventory` 下載。為避免 artifact 有限保存期影響重現性，**本研究亦已在 GitHub 保留實際使用的原始 bytes 與全部 272 對應特徵**：

- [原始 GA AIMR JSON bytes](../../data/raw_snapshots/2026-10-29/ga/GA_AIMR_REE_2026_features_0000000.json)，SHA256：`3d5c448f23cbf5d9c0dc1169640f78aac820f4ce4ccb1057fb337abd082037dc`。
- [原始南澳 SA_CRITICAL_REE CSV bytes](../../data/raw_snapshots/2026-10-29/sa/SA_CRITICAL_REE.csv)，SHA256：`4064f29eb934689606d5d4fa02f61e70c726c931752aaf1fd0a355adbc3c9fbc`。
- [272 筆政府來源欄位 JSONL](../../data/source_snapshots/2026-10-29_272_native_features.jsonl)，每筆附來源 chunk 原始 SHA-256、原生 ID、完整 attributes；注意此 JSONL 為衍生可重現的 *source-feature subset*，不等於 123,323 筆完整 raw archive。
- [Legacy r963 原始 203-row CSV](../../inputs/legacy_r963_census.csv)，16 筆缺原生資料對回 UUID 與該 CSV 的來源列。

19 筆有具名 Project 候選的來源紀錄仍需要個別文獻核對；恢復文件 bytes 不會自動把來源地質圖徵升格為 C1 Project。

## 5. 可重跑

```bash
# 先用 gh 工具下載 2026-10-29 原始完整政府資料 artifact
gh run download 40821122179 \
  --name australia-national-unfiltered-raw-inventory --dir work/p0_raw
python scripts/reconcile_p0_original_raw.py \
  --root . --raw-root work/p0_raw --out docs/audits
python scripts/build_p0_parent_evidence_queue.py
python -m pytest -q tests/test_p0_original_raw.py tests/test_p0_parent_evidence_queue.py
```

Github workflow [`p0-original-raw-recovery.yml`](../../.github/workflows/p0-original-raw-recovery.yml) 具備相同程序與 SHA 驗證，產出的 CSV、原始 source bytes 與 JSONL 分層保存。下一階段先處理 156 筆無 Project 母層的政府來源紀錄；對 92 筆地質出現點，不可因「沒有 Project」而刪掉 C0 Census，除非存在可定位的排除規則。**所有新增 Project 視為獨立審核候選，C1 尚未釋出。**
