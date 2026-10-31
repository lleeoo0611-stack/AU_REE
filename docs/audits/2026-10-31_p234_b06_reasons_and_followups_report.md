# P2–P4 外部技術補查 B06：339 筆證據原因分類與跨來源一致性核對

- 原始資料 as-of：**2026-10-29**；補查日期：**2026-10-31**。
- 基準：已合併至 `main` 的 PR #45 / #46 / #47；讀入 B05 339 筆來源分流，新增 P2 4 筆政府/發行人技術文字判讀，及 8 筆相關但不等同政府原生 ID 的定位線索。
- 同一筆來源只對應一個原始 `target_id`，保留原始 SHA、來源名稱、快照與 P1–P4 分級；所有本批分析都只加入新的 editable overlay 與人工判讀表。

## I. 最新工作量（單位：source rows）

| 分級 | 來源總筆數 | 公開技術文字有界補查 | 原件相關頁/HTML 既有判讀 | 待外部原文/身分補強 |
| --- | ---: | ---: | ---: | ---: |
| P2 | 28 | **20**（B05 16 + B06 4） | 先前桌面資料，未重宣告全文 | **8** 筆仍僅舊桌面判讀 |
| P3 | 216 | 既有 **11** | 117 筆保存相關內容 + 1 快取 | **87** 筆 native-only |
| P4 | 95 | 既有 **5** | 26 筆保存相關內容 | **64** 筆 native-only |
| **合計** | **339** | 各等級合計 36 筆新增/既有公開文字有界核查 | 143 保存原件相關頁 + 1 快取 | **159** 筆（8+87+64） |

P3/P4 的 **151 source rows** 共用 **100 個 state + native-ID 工作群組**（51 組重複定位）；加 P2 的 8 個獨立來源待查，目前優先查核為 **108 個工作單位**。全部曾列入原生 Census 的 source rows 仍保留。沒有新增正式 C1 admission、source freeze、Project entity merge 或 MCDA 排名。

## II. 八類原始證據問題：全部 339 筆、互斥

| 原始證據原因碼 | 筆數 | 解讀 | 實際工作方法 |
| --- | ---: | --- | --- |
| `NATIVE_FEATURE_ONLY_PROJECT_ROLE_NOT_VERIFIED` | **170** | 原始 339 分類中只有政府圖徵／缺具名 Project 角色；其中現有 151 筆尚只有 native-only，19 筆已在後續批次找到公開文字 | 逐 native-ID 找官方原件與 Project 親層，勿誤當 170 篇全文 |
| `GEOLOGICAL_CONTEXT_NOT_PROJECT` | **88** | 有地質或礦床/區域背景，但缺可回收 REE Project 身分 | 可進行 C0 来源範圍結案審查 |
| `REE_CLAIM_NEEDS_SAME_SCOPE_RESOURCE_ROLE_STAGE` | **40** | 有文獻主張 REE／資源／Project，仍缺同範圍、當期身分或階段資料 | 優先核對原件的單一 Deposit/Parent/Stage 和 JORC |
| `CROSS_SCOPE_RESOURCE_OR_ID_TRANSFER_REJECTED` | **21** | 現有來源反對跨專案/礦床、地區、礦權或礦種轉移數據 | 將負向比對結論寫回 provenance，不繼承外部數據 |
| `HISTORIC_OR_NON_TARGET_RESOURCE_CONTEXT` | **15** | 歷史、非 REE 產品、非主要研究時窗 | C0 級別的用途判斷與重開條件 |
| `PROJECT_ID_NAME_OR_GEOGRAPHY_CONFLICT` | **3** | 同名異地、座標或別名無法確認 | 先確認 source→entity identity，不配對 Project |
| `SAMPLED_TARGET_SPECIFIC_NEGATIVE_NOT_REGIONAL` | **1** | 僅特定已測標的的陰性證據 | 不得外推其他礦化區或日後資源 |
| `ORIGINAL_PUBLICATION_BYTES_ACCESS_BLOCKED` | **1** | Scaddan 的原始出版物 bytes 無法取得 | 標記外部取件 HOLD，保存查詢失敗與新資料重開條件 |
| **合計** | **339** | 此表是 2026-10-31 baseline 的原始證據原因，不是本輪新通過的原件數 | |

## III. 按「下一步卡在哪裡」分類：互斥 339 筆

| 目前工作阻礙 | 來源數 | 處理 |
| --- | ---: | --- |
| P3/P4 原生圖徵尚未綁定可核對技術來源 | **151** | 同州同 ID 100 工作群組；按 exact native key 找公告、報告、礦權 |
| C0 來源範圍已有較清楚證據，等待正式結案簽核 | **119** | 完成 F1 文書／證據驗收；`ADR-P0-028` 未採納前保持候選 |
| 有具名 REE 主張，但 Project/同範圍 JORC/Stage/GIS 未核准 | **37** | 技術原文與 C1 六 Gate，不得只用探勘樣本等同資源 |
| Project 身分／礦權／來源範圍核准不足 | **22** | 以 native site + 報告 + 當期 tenement + 地圖做 crosswalk |
| P2 尚未重新核對原始技術全文/來源 | **8** | 按 CR 報告 ID/ASX 原始揭露排程 |
| 身分／地理別名仍衝突 | **1** | 特別以原始來源座標、歷史實體辨識 |
| 網頁只有快取文字，原檔仍無法取用 | **1** | 保留可重開的原件存取 HOLD |
| **合計** | **339** | 這是工作流程主阻礙，與上表歷史原因維度不同 |

### B06 四筆新增 P2 原始來源範圍判讀

1. **Arthur Popes，NT** — NTGS [CR2007-0754 / EL24646](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/74268) 技術報告文字確定具碳酸岩相關 Cu–REE–Y 脈與局部 REO + Y₂O₃ 樣本；[CR2024-0188 / EL32196](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/93232) 為不同年代地權之區域地質/探勘回顧。局部化驗、歷史礦權與現行 REO JORC/Project 未能互相替代。
2. **Blues Folley（Blueys Folley），NT** — NTGS [CR2014-0992](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/91056) 與 [CR2015-0851](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/83058) 直接對 EL28029 原始報告及部分礦權放棄；放棄區域位於 REE anomaly 之外，不能說整個礦區已證明陰性。另 P4 已有政府 MODAT native source（`5548`），但 P2 Legacy 缺原始精確座標，跨分級 entity join 仍待核對。
3. **Bells Monazite，NT** — Vista Gold [CR2014-0275 / GR087](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/90694) 記載 Mt Todd／Wolfram Hill 附近的 Bell's Monazite 為含 Th 的 REE 礦點；另一方面，Cox Peninsula 1987 [EL2193 原始報告](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/61444/1/CR19870124.pdf) 和 NTGS 2017 [Bynoe CR2017-0146](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/93280) 之 Bells Mona 為不同地理位置的 Sn–Ta 偉晶岩。**判定為同名但不同地質實體的證據風險**，不得把 Bynoe 資源或座標歸給 Wolfram Hill。
4. **Elaine Dorothy，QLD** — [China Yunnan Copper Australia 2010 原始年報](https://www.aukingmining.com/site/PDF/2196db4b-4543-4e42-8a1c-fc6a99baa50d/AnnualReporttoshareholders)（印刷 p.4）和 [2010 發行人簡報](https://www.aukingmining.com/site/PDF/ee839a6a-7f76-495d-babe-8e8924214472/PresentationreSharePurchasePlanCapitalRaising) 明確報告歷史 JORC Inferred **83,000 t @ 3,200 ppm TREO、280 ppm U₃O₈，以 200 ppm U₃O₈ 為 cutoff**。**P3 兩筆早已正確記錄歷史 JORC REO，但 P2 舊描述只說歷史礦化/無 REO MRE，這是跨分級證據摘要不一致**。B06 新 P2 覆蓋紀錄補正此資訊；仍須取得原始 JORC 表格/Competent Person、同一期礦權、2026 活動與 pre-FID REE Study，不能憑 2010 JORC 宣告現行 C1 通過。

四筆可編輯審查依據：[B06 P2 public-primary CSV](../../inputs/source_review_20261031/p234_b06_p2_public_primary_reviews.csv)。本次 PDF 網頁搜尋文字有定位、頁面截圖請求回報 cache miss；PDF bytes 和原始檔 SHA 均**沒有**列為本次取得。

### 相關來源，但**未確認同一原生 feature** 的 8 筆定位紀錄

- **P2 Edwards Creek：**官方 [CR2023-0725](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/92910) 講的是 Edwards Creek South EL32758；同文指出 Edwards Creek 礦點在其他經營者的礦權上。需取真正 Edwards Creek 的 Legacy 原生來源及對應 2026 礦權，不能用 South 的放棄報告判斷整個礦點 REE。
- **P2 Pyramid：**[Altair Pyramid Lake](https://altairminerals.com.au/project/pyramid-lake/) 是 E74/594 石膏開發，1.3 Mt @78% gypsum（Indicated）與 2.6 Mt @67% gypsum（Inferred）。Legacy `Pyramid` 不得僅憑名稱映射至此，也不得將石膏資源當 REO/TREO。
- **P4 Spartacus（兩來源 ID）：** NTGS [CR2009-0162](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/77605) 紀錄當時局部 rock-chip REE/U 測試陰性；其他歷史 Quartz Hill 報告提到早期長石／Feldspar 異名與放射性偉晶岩。陰性只適用於被測標的與該次工作，需核對 MODAT `5645` 原始位置/礦權。
- **P4 North Bleechmore Dykes（兩來源 ID）：** [2012 NuPower Strangways GR122 技術原件](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/76943/1/GR122_2012_GA_01.pdf) 審慎評估當時所測脈體 REE 低品位／規模與碳酸岩假說，認定不足支持當時開發勘探；仍需與 MODAT `5488` 精確圖徵定位。
- **P4 Skyfall（兩來源 ID）：**新增 [2015 NTGS CR2015-0950](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/82890) 原始政府目錄明示歷史 metallurgy、trial pits、**preliminary scoping study**，但 2015 年 EL27151 已 relinquished。不能把歷史 scoping 自動追認為 2026 年活動中的 C1 pre-FID Project；之前 B05 的 2014 [CR2014-1016](https://geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/81038) 亦僅為有界地質/鑽孔證據。

[B06 8 筆 locator/cross-check CSV](../../inputs/source_review_20261031/p234_b06_related_locator_cases.csv) 明確保留 `same_native_feature_geospatial_match_approved=NO`，所以 **P3 87、P4 64 尚待外部原件補強的來源數不減少**；已取得有界相關來源線索可用於後續 source-native crosswalk。

## IV. 資料庫流程與凍結界線

已合併 B05 的 `proposed_freeze_route` 繼續保留 **119 筆人審候選**，不執行 source freeze、source merge、C1 或 JORC 自動核准；`ADR-P0-028` 仍是 **PROPOSED**。所有來源的 `C0_freeze_candidate_prior` 只是工作路由，不是實際結案狀態。

新的兩種原因分類是不同維度：

- `evidence_root_cause_code` 以原始 339 終端證據分類為基準，保留歷史可重跑性，不任意用 B06 檢索結果改寫原始分類。
- `operational_blocker_code` 依最新 B05 source-review 深度、B06 判讀及候選凍結狀態，分辨新技術原文、待人工來源結案、Project 身分、REE 資源/Stage 及取件阻礙。新來源進來時由 Python 重算此欄。
- `resource_basis_annotation`、`cross_source_consistency_issue` 與 `new_bounded_finding` 專門保存 Elaine Dorothy 2010 歷史 TREO 及 Bells/Wolfram–Bynoe 同名誤判，不冒稱取得 2026 的 C1 資格。

**下一輪優先：**（1）Elaine Dorothy 原始 competent-person 2010 JORC 定義/現行礦權及是否有 pre-FID REE 商業研究；（2）Bells Monazite 原始 source Legacy 座標拆開 Wolfram Hill/Bynoe；（3）P2 其餘 8 筆按 original report ID 逐案找正式全文；（4）P3/P4 的 100 同源工作群組按官方圖徵 ID 嵌回技術報告，先處理已定位名稱與試驗結果者。

## V. 重建與驗收

```bash
python scripts/build_p234_reason_classification_b06.py --check
python -m unittest discover -s tests -p test_p234_reason_classification_b06.py -v
# 確認人工審查表後才重建 derived outputs
python scripts/build_p234_reason_classification_b06.py --write
```

主要輸出：[B06 339 筆原因碼 CSV](2026-10-31_p234_b06_reason_classification_339.csv)、[統計 JSON](2026-10-31_p234_b06_reason_summary.json)、[四筆官方來源 CSV](../../inputs/source_review_20261031/p234_b06_p2_public_primary_reviews.csv)、[八筆相關文件定位 CSV](../../inputs/source_review_20261031/p234_b06_related_locator_cases.csv)。所有來源 IDs、快照、P1 與原 approval 均不改寫。

**Gate：SOURCE_TRIAGE_EXTENDED；C0 closure=PROPOSED；C1=NOT_RELEASED。**
