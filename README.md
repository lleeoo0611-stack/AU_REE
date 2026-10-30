# Australian REE Projects — 可重現資料庫與 MCDA 決策分析

澳洲稀土礦業專案的**證據可追溯資料庫**、**開發潛力評估**及**多情境排名穩健性研究**。以 Python 3.11+、SQLite、官方 GIS 及 R 建立可更新、可重跑、可版本控制的研究管線。

研究依據：*Multi-Criteria Decision Support Framework for Screening the Development Potential of Australian Rare Earth Mining Projects*（2026-09-06 proposal）。本 README 將**現有功能、近期母體審閱成果、後續研究需求**分別說明，詳細的 A/B/C 實作規格見 [研究需求與驗收標準](docs/RESEARCH_REQUIREMENTS_AIMS_ABC.md)。

## 研究目標

| 研究面向 | 核心問題 | 主要研究成果 |
| --- | --- | --- |
| **Aim A — Development Potential** | 哪些專案在資源、技術、開發及空間條件上具有較高綜合表現？ | 六構面評估、構面分數、依情境定義的綜合排名 |
| **Aim B — Ranking Robustness** | 不同決策偏好、輸入不確定性與方法會如何改變排序？ | 權重情境、rank acceptability、top-k 與兩兩排序機率 |
| **Aim C — Ranking Drivers** | 哪些評分因素及礦床／生命週期特徵解釋排名差異？ | 敏感度分析、礦床類型及生命週期分層分析、歷史驗證 |

三個 Aim **共同使用**可審計的 Project–Deposit–Evidence 資料基礎。完整 Census、符合研究條件的 MCDA Alternatives，以及不同情境下的結果須明確區分。任何排名均須附上 cohort、資料截止日、評分函數、權重、分析版本與證據狀態。

## 目前狀態（截至 2026-10-30 的儲存庫紀錄）

| 工作線 | 已有內容 | 下一階段 |
| --- | --- | --- |
| **五階段管線** | `src/au_ree/` 提供 population → criteria → gis → eligibility → r_export，具 checkpoint、SQLite、CSV/manifest 與來源核准 | 整合 Project–Deposit–Resource Schema、歷史快照和資料不確定性 |
| **全澳來源母體** | 已有全澳政府 raw/screening 快照：123,323 筆來源紀錄、1,006 筆 REE 篩選候選，**不是** 1,006 個獨立專案 | 繼續實體辨識、來源條件與持權鏈審核 |
| **487 筆追溯審閱** | 2026-10-30 審閱記載 69 筆候選、6 筆 REE 角色待查、412 筆 Project 身分／REE 角色證據不足；候選群組尚非正式核准數 | 逐筆審核並建立可發布的獨立 Project 母體 |
| **現行 MCDA** | R 支援 AHP/CR、PROMETHEE II、SAW、TOPSIS、Dirichlet **權重** Monte Carlo、LOO、threshold sensitivity | 六構面完整分析、資料不確定性、SMAA、Aim C driver analysis |

相關審閱事實與版本請見 [CENSUS_RELEASE.md](CENSUS_RELEASE.md)、[全澳原始資料成果](docs/NATIONAL_RAW_AND_SCREEN_RESULTS_2026-10-29.md)、[最新逐列追溯](docs/FULL_TRACE_REVIEW_20261030.md)。**目前沒有以完整、獨立核准的主分析母體所發布的研究級 MCDA 排名。** 舊版 203 筆 legacy census、凍結的 19 筆 G0 Alternatives 與 487 筆待審閱目標屬於不同資料集合，不可直接相互代替。

## 已實作的五階段執行架構

```text
Official GA/State + frozen legacy + review decisions
          │
          ▼
01 population ── Candidate/Project/alias identity + source registry
          │
          ▼
02 criteria ──── Verified observations, 12 criteria, provenance and basis QA
          │
          ▼
03 gis ───────── Official road/rail/power/port proximity + GIS QA
          │
          ▼
04 eligibility ─ Cohort gates, data coverage and full/subset release checks
          │
          ▼
05 r_export ──── Matrices, scenarios, AHP templates
          │
          ▼
R/run_mcda.R ─── AHP + PROMETHEE II / SAW / TOPSIS + weight Monte Carlo
```

獨立的**全澳 raw-first 篩選、487 筆身份/來源追溯與可攜式快照重建**另見 `scripts/`、`reproducibility/`、`CENSUS_RELEASE.md`；這些審閱成果尚需經核准與一致的 schema 才能進入正式 MCDA。原始全澳來源明細見 [Official population sources](docs/official_population_sources.md) 與 [National raw-first protocol](docs/NATIONAL_RAW_FIRST_PROTOCOL.md)。

### 現行準則與情境

`config/criteria.json` 定義六個概念構面，共 **12 個準則**：R1（資源）、S1（磁性稀土組成）、T1–T2（技術）、D1（研究成熟度）、I1–I4（道路／鐵路／輸電／港口距離）、C1–C3（融資／承購／許可）。

`config/eligibility.json` 的主要研究窗口為澳洲、可辨識的 REE Project、Active/Under Study/Feasibility、**pre-FID Scoping–PFS–DFS/BFS/Feasibility**；現行 Gate 含 JORC、經核准證據、座標與 GIS、至少 70% 準則覆蓋及四構面覆蓋要求。缺值不給零分，也不以未核准來源替代正式觀測。

| 矩陣情境 | 意義 | 目前使用的構面 |
| --- | --- | --- |
| `G0_BASELINE` | 凍結的 global baseline，R/S 不入列 | T、D、I、C（共 10 項） |
| `R1_STRICT` | 有 R1 資源證據的子集 | R、T、D、I、C |
| `S1_DIRECT` | 有 S1 磁性稀土組成證據的子集 | S、T、D、I、C |
| `RS_STRICT` | 同時有 R1 與 S1 的子集 | R、S、T、D、I、C |

上述為**納入／證據情境**；`resource_driven`、`development_driven`、`strategic_supply_driven` 則是**權重決策偏好**。兩者不可混淆。`G0_BASELINE` 目前不能宣稱為完整六構面評分。正式 A/B/C 分析須先確定可比較且完整註記的分析母體與不確定性規則。

**GIS 現行指標**以核准的專案座標和官方圖層，於 EPSG:3577 計算最近路、鐵、高壓電線及主要港口的直線距離（km）；不是路網旅行時間、運費或接入能力。`config/gis.json` 與 `gis_metrics.csv` 保存圖層與 QA。G0 全域 GIS release gate 對應原凍結 19 筆 Alternatives；R1/S1/RS 子集若核准須標記 `RELEASED_SUBSET`，不得稱作全體排名。

## 快速開始

```bash
python -m pip install -e '.[test]'
au-ree plan
au-ree run --through r_export --offline
au-ree status
python -m pytest -q
```

首次離線執行會生成 `work/research.sqlite`、階段稽核 CSV、manifest 與 R 模板。若尚未有獨立核准的來源數值／座標，正式 MCDA matrix 保持空表，不自動補值或產生排名。

### 更新與續跑

```bash
# 需要網路及政府資料更新時
au-ree run --stage population --refresh
au-ree run --through r_export

# 特定階段重跑或續跑
au-ree run --stage criteria --force
au-ree run --through gis
au-ree run --through eligibility
au-ree run --through r_export
```

更新官方候選後，透過 `inputs/project_reviews.csv`、`inputs/project_identity_decisions.csv` 逐項核准 Project 身分；技術觀測輸入 `inputs/verified_observations.csv`，文件原件與獨立核准分別管理於 `inputs/evidence/`、`inputs/source_documents.csv`、`inputs/evidence_approvals.csv`。原始 SHA-256、來源 URL、有效／公開日期與審核紀錄缺一不可；單純填寫 `verification=VERIFIED` 不等於核准。

### R 分析（僅適用已通過 release gate 的決策矩陣）

```bash
Rscript R/run_mcda.R \
  --input work/outputs/04_eligibility/matrix_G0_BASELINE.csv \
  --criteria work/outputs/05_r_export/r_criteria_dictionary.csv \
  --weights work/outputs/05_r_export/r_weights.csv \
  --ahp work/outputs/05_r_export/ahp_pairs_G0_BASELINE.csv \
  --perspective development_driven \
  --reps 10000 --seed 20261029 \
  --out work/r_results/G0
```

研究者需先填寫 `ahp_pairs_*.csv` 的成對比較比例，並通過 AHP 一致性檢查。只有用於程式示範時才使用 `--illustrative`，其結果標記 `ILLUSTRATIVE_ASSUMED_WEIGHTS`，不作為研究級權重或排名。

### 487 筆可攜 Census 快照

`CENSUS_RELEASE.md` 記載可攜資料包與離線重建程序。將該交付包解壓至包含 `portable_snapshot/` 與 `deliverable/` 的工作目錄後，依其中指示執行：

```bash
python reproducibility/build_census_database.py rebuild --snapshot-dir portable_snapshot --output restored.sqlite
python reproducibility/build_census_database.py verify --snapshot-dir portable_snapshot --database restored.sqlite
```

此為 Census 審閱快照重建，**不等於**通過 MCDA 的母體或排名。

## 新增研究需求與實作路線圖

完整規格、資料表欄位、數學定義、模組修改位置和驗收測試統一存於 **[Research requirements — Aims A/B/C](docs/RESEARCH_REQUIREMENTS_AIMS_ABC.md)**。以下為追蹤摘要：

| 順序 | 工作包 | 目的 | 狀態 |
| --- | --- | --- | --- |
| **P0** | Project–Deposit–Tenement／JORC Resource Statement、事件與來源歷史 | 可重建、無重複計算的研究資料庫 | 規格已建立；待實作與遷移 |
| **P0** | Missingness／Uncertainty／Lineage model | 區分未揭露、未測、衝突及實際數據不確定性 | 規格已建立；待實作 |
| **P1** | 固定參考尺度、依賴圖、階層式六構面評分與 Cohort bias audit | Aim A 的可比較開發潛力評估 | 規格已建立；待實作 |
| **P2** | 權重＋資料不確定性、SMAA rank acceptability、跨方法／樣本檢驗 | Aim B 的穩健性與條件式排序機率 | 現有權重 Monte Carlo；擴充待實作 |
| **P2** | Model drivers + Deposit/Lifecycle 分層統計 | Aim C 的數學敏感度與地球科學解釋 | 現有 LOO；擴充待實作 |
| **P3** | Historical snapshots、forward event validation、可編輯研究輸出 | 時間外推驗證與論文補充資料 | 規格已建立；待實作 |

新增要求**不直接修改**當前五階段程式的計算結果、正式 Gate 或已凍結輸入；完成獨立測試與資料遷移後，再分批納入正式 pipeline。

## 資料夾與版本控制

| 路徑 | 用途 |
| --- | --- |
| `src/au_ree/` | Python CLI、核心 schema、各 stage 與來源 adapters |
| `R/run_mcda.R` | 目前已實作的 R MCDA |
| `config/` | Criteria、Eligibility、GIS、來源與研究假設 |
| `inputs/` | 可編輯 CSV、唯讀 legacy、證據檔與獨立審查 |
| `docs/` | 方法、官方來源、研究決策、變更紀錄與完整需求 |
| `scripts/` | 全澳 raw-first、screening、其他專項審閱腳本 |
| `reproducibility/` | 487 筆工作包重建、品質檢查與快照 |
| `.github/workflows/` | 離線 Python、R synthetic smoke、官方資料擷取流程 |
| `work/` | 本機 SQLite、暫存、階段輸出、SHA manifest（不納入一般 Git） |

程式、設定、研究決策與小型可編輯輸入由 Git 管理。大型原始 API、PDF、GeoPackage 及 SQLite 快照以 Git LFS／DVC 或獨立封存配合 SHA-256 Manifest 追蹤；新分析建立新的 snapshot ID，不覆寫舊版。CI 中的合成案例用於演算法測試，不能作為實際專案研究結果。

## 文件索引

- [A/B/C 研究需求與驗收準則](docs/RESEARCH_REQUIREMENTS_AIMS_ABC.md)
- [研究方法決策（r983）](docs/RESEARCH_DECISIONS.md) · [原五階段 README 歷史存檔](docs/archive/README_v1.0.4_pre_ABC_2026-10-30.md)
- [全澳 487 筆最新審閱成果](CENSUS_RELEASE.md) · [逐列來源追溯](docs/FULL_TRACE_REVIEW_20261030.md)
- [Scheme A Project Master](docs/SCHEME_A_PROJECT_MASTER.md) · [官方資料來源](docs/official_population_sources.md)
- [Git 工作流程](docs/GIT_WORKFLOW.md) · [Changelog](docs/CHANGELOG.md)
