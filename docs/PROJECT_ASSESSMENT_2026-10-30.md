# 澳洲稀土 MCDA：方法學、資料整理與研究進度評估

**評估時點：2026-10-30**  
**依據：**本儲存庫當時的 `README.md`、`src/au_ree/`、`R/run_mcda.R`、`config/criteria.json`、`config/eligibility.json`、`CENSUS_RELEASE.md`、`docs/NATIONAL_RAW_AND_SCREEN_RESULTS_2026-10-29.md`、`reproducibility/runs/2026-10-30-full-trace-release.json` 及研究需求。評估範圍為目前儲存庫的程式、文件、快照與已報告驗證；不將尚未正式核准的 Project、權重或排序視為研究結果。

## 綜合判斷

**研究問題與分析管線已成形；研究資料母體仍在核准階段；論文所需的 A/B/C 實證尚待完成。** 目前最有價值的已完成工作，是將來源擷取、身分辨識、證據審核、GIS、資格門檻及 MCDA 程式拆開，並保存來源與快照。下一個研究里程碑應是產出一份**同一日期、同一母體、來源已核准、具備六構面可比較指標**的決策矩陣。

| 項目 | 目前階段 | 評估 |
| --- | --- | --- |
| 研究架構 | A/B/C 研究目標及六構面已明確 | 研究設計成熟 |
| 來源擷取及原始資料保存 | 全澳政府 Raw-first 快照已發布、具 manifest/hash | 資料工程具規模 |
| Project Census / Entity Resolution | 候選與 HOLD 可追溯；尚未核定獨立專案母體 | 核心資料驗證持續中 |
| Resource / technical observations | 觀測模型與證據閘門已存在，JORC 專用關聯結構待實作 | 正式 MCDA 數據不足 |
| GIS / eligibility | 四項官方圖層距離、G0/子集 release gates 已寫入程式 | 程式具備，但正式釋出仍受 QA 約束 |
| MCDA | AHP、PROMETHEE II、SAW、TOPSIS、權重 Monte Carlo、LOO 已實作 | 合成資料演算法驗證已有基礎 |
| Aim B 資料不確定性、Aim C、歷史驗證 | 已有需求文件，未形成正式分析成果 | 待實作 |
| 研究級可發表排序 | 最新 Census release 明確記載未執行 MCDA | 尚未完成 |

以上是**分項質性成熟度**，不以任意百分比代表研究完成程度。

## 一、方法學評價

### 已形成的基礎

1. **研究問題有順序。** Aim A 建立不同專案的開發潛力構面，Aim B 檢查偏好與排序穩健性，Aim C 分析模型敏感度及地質／開發特徵的關聯。研究可以在同一套證據基礎上形成相互補充的結果。
2. **MCDA 有多方法比對。** `R/run_mcda.R` 已包含 AHP 一致性檢查、PROMETHEE II、SAW、TOPSIS、權重 Dirichlet Monte Carlo、leave-one-criterion-out 及偏好門檻變動。研究者 AHP 與 `--illustrative` 假設權重明確分開。
3. **納入條件與計算值分離。** `src/au_ree/stages/eligibility.py` 管理資格與 GIS release，缺值／未核准證據不自動計為零。這讓目前尚未滿足條件的專案仍可留在 Census。
4. **GIS 與證據有可稽核規則。** 四類基礎設施的直線距離有官方資料、座標與來源核准機制，適合作為一致的「鄰近性」指標。

### 實證分析前需要處理的設計問題

| 優先 | 問題及依據 | 建議處理 |
| --- | --- | --- |
| **P0** | `G0_BASELINE` 只有 T/D/I/C，缺 R1（contained TREO）與 S1（magnet REO share），無法代表完整六構面 | 先定義六構面的主比較母體；G0、R1、S1、RS 需按不同 cohort 名稱發布，不可直接比較異質母體排名 |
| **P0** | `config/eligibility.json` 設 70% coverage、至少四構面與 pre-FID Scoping–Feasibility；完整點值與 GIS approval gate 又造成額外選取限制 | 報告各 gate 的樣本流失與階段偏差，保留共同樣本的敏感度比較；避免成熟專案因揭露較多而系統性占優 |
| **P1** | `R/run_mcda.R` 的 SAW 以樣本 min–max 正規化；PROMETHEE V-shape 偏好門檻取樣本 IQR；TOPSIS 參照同批 Alternatives | 對跨期／跨母體研究增設固定參考尺度、預先指定的偏好門檻及排名反轉測試；保留現行演算法作基準 |
| **P1** | D1 已將 Study Maturity 納入評分，Aim C 又要比較 Lifecycle Stage | 主分析／替代模型分離 Stage 的「分數貢獻」與「外部分層差異」，避免循環論證 |
| **P1** | 現行 R1/S1 只有一項資源量與一項組成比例；T1/T2 及部分商業指標為 ordinal 評分 | 加入原始 JORC 規模、品位、資源分類、cut-off、元素 basis 與冶金證據；定義 ordinal codebook 及來源判讀者一致性 |
| **P1** | 現行 C1–C3 是融資、offtake、approvals，並未獨立評估完整 ESG 實際績效 | 若維持 Commercial/ESG 標籤，應增加可核准 ESG 指標；否則先用 Commercial & Approvals 的準確名稱 |
| **P2** | 現有 Monte Carlo 僅擾動權重，對缺值、數據範圍及數據間依賴無聯合抽樣 | 增加有證據依據的數據區間與相關性；分別輸出 weight-only、data-only、joint 分析，再加入 SMAA rank acceptability |
| **P2** | Aim C 尚缺專案特徵的獨立統計分析 | 將內部 model drivers 與外部 Deposit Type／Lifecycle Stage 關聯分開；報告各組樣本數、資料完整度及不確定區間 |
| **P3** | 尚未用歷史時點的資料檢驗後續專案進展 | 建立 publication-date 限制的 historical snapshot，再比較後續 PFS／DFS／FID 等事件 |

**方法學總評：**問題設定與模型框架已足以支撐完整研究。當前優先工作是**定義有效主母體、補齊可比較的地質與技術觀測、固定評分尺度與揭露選擇偏差**，現階段不需要再堆疊更多 MCDA 演算法。

## 二、資料整理評價

### 目前已有的證據

- `docs/NATIONAL_RAW_AND_SCREEN_RESULTS_2026-10-29.md`：官方原始來源紀錄 **123,323** 筆；以 E1（803）、E2（163）、E3（40）得到 **1,006** 筆篩選候選。這些是**來源紀錄與篩選候選**，尚未去重成獨立 Project 母體。
- `CENSUS_RELEASE.md`：487 個固定審閱目標中 **69** 筆為 Project 候選待審、**6** 筆 REE 角色待查、**412** 筆身分或角色證據不足；已審閱群組與候選紀錄數不應混用。最新審閱為 **78** 筆有群組連結、**409** 筆未連結。
- 同份 release：原 **95** 筆來源引用中，**64** 筆可定位具體文字、**13** 筆有取得內容但無直接定位、**18** 筆未取得可用文字；**407** 筆原生 ID 唯一命中、**2** 筆存在同 ID 多列、**32** 筆未找到精確原生資料。這些統計屬相關審閱子集合，不能與 487 個目標直接等同。
- 法律持權、營運者、公司更名與轉讓已拆分；**39 個 Project 群組**的現任法律持權鏈仍未完整核實。
- `reproducibility/runs/2026-10-30-full-trace-release.json` 記錄研究快照重建、邏輯表格雜湊、資料遮蔽與重跑結果，但不代表所有來源、專案或權利關係已得到實體核准。

### 資料工程判斷

**優點：**採用 Raw-first→候選篩選→Entity/Source review→稽核→快照，避免把 Mineral Occurrence 誤當開發 Project；原始 ID、審查狀態、HASH、快照與重新建置機制充分保留。分別保存 Legal Holder、Operator、Proponent 的規格也符合跨時點礦權追蹤需求。

**下一步：**建立一致的 Project–Deposit–Resource Statement 關聯；把 JORC M/I/I 分類、Mineral Resource 與 Ore Reserve、cut-off、TREO/THM/MzEq、Nd/Pr/Dy/Tb 氧化物 basis 做成可稽核的 observation schema。統一 `effective_date`、`publication_date`、`retrieved_at`，並將 `UNKNOWN`／`CONFLICT`／`NOT_REPORTED` 明確區分。

**資料總評：**可重現資料管線的設計成熟度高於目前可供正式 MCDA 的證據完整度。對本研究而言，**少量但已核准、同一基準且可比較的 Project 資料**將比擴大未定義候選數量更快推進 Aim A/B/C。

## 三、進度評價及下一個里程碑

目前完成的是**研究架構與資料工程基礎**，進入的是**Census 核准與正式比較資料建置**。CI 的 Python 離線重跑與 R 合成 MCDA 測試，證明主要程式的回歸與可重現路徑，尚未代替正式澳洲專案的樣本驗證。487 筆工作包端到端重建亦依賴凍結的來源封存，與一般 Python/R CI 測試範圍不同。

| 次序 | 工作 | 應交付的驗收成果 |
| --- | --- | --- |
| **1 — Project 母體** | 完成獨立 Project 辨識／去重與必需證據，保持未核准紀錄為 HOLD | 逐 Project 身分、別名、礦床關聯、排除原因、來源頁碼及核准紀錄 |
| **2 — 主要 MCDA 矩陣** | 蒐集可比較 JORC、REE 組成、冶金、開發、GIS 與 Commercial 證據 | 同一 cutoff 的六構面、完整 QA、分母與各 gate 的流失報告 |
| **3 — Aim A** | 固定 scoring、依賴與 AHP 權重，執行 baseline + 其他方法 | 可追溯 domain score、project profile 與正式 baseline ranking |
| **4 — Aim B** | 加入資料／偏好／樣本不確定性與 SMAA | Rank acceptability、P(Top k)、pairwise comparisons、跨情境圖表 |
| **5 — Aim C** | 進行 model sensitivity、Deposit Type／Lifecycle 分組、歷史驗證 | 影響因素與樣本數、條件式統計結果及歷史事件對照 |

### 一致的研究結論界線

- 目前有充分依據討論**資料擷取覆蓋、資料工程與方法設計**。
- 目前沒有足夠依據宣稱「哪個澳洲稀土開發專案排名最高」或「哪類礦床具有最高開發成功率」。
- 排名機率描述的是**已定義權重／資料模型與母體下的排序頻率**，不是礦業開發成功機率。

**實作規格：**[A/B/C 研究需求](RESEARCH_REQUIREMENTS_AIMS_ABC.md)。**執行與快照：**[Runbook](RUNBOOK.md)、[Census release](../CENSUS_RELEASE.md)。
