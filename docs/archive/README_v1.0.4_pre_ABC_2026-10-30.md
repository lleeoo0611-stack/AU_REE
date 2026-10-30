# 澳洲稀土開發潛力 MCDA：五階段可重現管線

版本 `v1.0.4`｜基準日 `2026-10-29`｜Python 3.11+ / SQLite / R

以 2026-09-06 proposal 的六構面與 r963–r983 研究規格為基礎，將研究作業分為五個獨立、可重跑的階段。SQLite 是唯一正式研究資料庫；CSV 是可編輯、可追溯的輸入或輸出介面。

## 工作流程

```text
01  population  → 02  criteria → 03  gis → 04  eligibility → 05  r_export
      │                  │              │                  │
      └── Source Registry│              │                  └── R/run_mcda.R
          Candidate Audit├─ Evidence Model
          Project Alias  │              └── Official GIS + SHA256
                         └─ 12 Criteria, Six Domains
```

### 01. `population` — 網路擷取與可驗證專案母體

- 讀取唯讀 `inputs/legacy_r963_census.csv`（203 筆歷史種子，狀態保留為未經目前日期重新驗證）。
- 來源 adapter：Geoscience Australia AIMR Rare Earth Elements（Layer 52）、Australian Critical Minerals Deposits（Layer 7），以及可啟用的 WA/NT/SA/QLD/NSW/VIC/TAS 官方州資料 CSV。
- 透過 ArcGIS REST `returnIdsOnly`、Object ID 分批請求與 SHA-256 檢查點下載政府資料；以 `--refresh` 明確觸發更新。
- `PROJECT / DEPOSIT / PROSPECT / TENEMENT / UNKNOWN` 不混合；GA 的兩個 deposit layer 預設只進候選/審查佇列，不自動當成 project。
- 來源 native ID → 專案別名 → 標準化名稱+州別，僅高確定性證據自動合併。新專案永久 ID 為 `AU-REE-xxxxx`，重新執行不可重新編號。
- 保留 inactive/suspended 專案於 Census，與正式 MCDA 納入資格分開。
- 輸出：`population_master.csv`、`population_review_queue.csv`、`population_source_registry.csv`。

### 02. `criteria` — 變數、準則、證據與衍生計算

- 六構面共 12 個準則：R1、S1、T1、T2、D1、I1–I4、C1–C3。完整基準、方向與單位見 `config/criteria.json`。
- 輸入 `inputs/verified_observations.csv`（可編輯），每筆保留 `project_id`、variable、原值、basis、effective/publication date、source URL、source SHA-256、verification。
- 2026-10-29 之後的證據不納入當前快照。
- 計量基準區分 TREO、THM、MzEq 等，未有明確換算證據不強制合併。
- 同來源 SHA-256、同有效日期、原始文件雜湊已核對且具有獨立 APPROVED 紀錄時，可衍生：
  - `contained_treo_kt = ore_mt × treo_grade_pct × 10`
  - `magnet_reo_share_pct = Nd2O3 + Pr6O11 + Dy2O3 + Tb4O7`（四者均為 `% of TREO`）
- 原始 r968 observation 以 `LEGACY_FROZEN` 保存，不能直接變成 Verified MCDA 分數。研究者輸入中的 `verification=VERIFIED` 不是獨立核准的替代品。
- 輸出：`criteria_dictionary.csv`、`variable_dictionary.csv`、`observations_evidence.csv`、`criterion_values.csv`。

### 03. `gis` — 官方 GIS 取得與回填

`config/gis.json` 已登錄下列官方圖層：

| GIS 欄位 | 官方空間資料 | 計量 |
|---|---|---|
| I1 | Infrastructure Department — Key Freight Route / road (5) | 最近全國關鍵貨運道路直線距離 (km) |
| I2 | GA — Foundation Rail Infrastructure / Railway Lines (1) | 營運鐵路或側線直線距離 (km) |
| I3 | GA — Electricity Infrastructure / Power Lines (2) | 高壓電力線直線距離 (km) |
| I4 | GA — Maritime Facilities / National Major Ports Database (0) | 最近主要港口直線距離 (km) |

- 對每筆**已驗證的專案座標**，先按半徑 25→100→250→500→1000 km 查數量，再用 Object ID 分批取得完整線段幾何；港口則分批下載全國圖層。
- 鐵路查詢含營運狀態與線別篩選。距離以 EPSG:3577 投影後的 Shapely `distance` 計算，不當成道路網路行駛時間或成本。
- 每個專案／圖層保存原始回傳檔、SHA-256、選定半徑、成功或失敗原因；可中斷再續跑。
- 本機 GIS 圖層須與已存檔原件的 SHA-256、獨立審查項及官方 URL 一致才可計入；尚未核准的遠端 GIS 來源只保留為待處理來源。未驗證座標或不完整圖徵回應不會寫入正式 `criterion_values`；`gis_metrics.csv` 記錄實際距離與 QA 狀態。

### 04. `eligibility` — 資料完整度與 Alternatives 名單

使用 `config/eligibility.json` 所列的 Gate：澳洲、明確 project、REE materiality、Active、Scoping/PFS/DFS/BFS、pre-FID、JORC 資源與來源證據、已驗證座標、準則覆蓋率與構面覆蓋、QA。缺值不給 0 分。

依 G0、R1、S1、RS 四種情境分別產生。v1.0.1 將 **GIS Release Gate** 明確拆成兩種：
- **G0 全域**：必須涵蓋凍結的全部 19 個基準 Alternatives，四項 GIS 均完成獨立來源核准，且目前 R 僅支援點值，因此完整 19 × 10 點值矩陣也須通過才能正式釋出。
- **R1／S1／RS 子集**：從已滿足非 GIS 條件的專案推導固定子集，至少兩個成員；所有該子集成員均須完成四項經核准的 GIS，才標記 `RELEASED_SUBSET`。此結果不得冒稱為全體排名。

釋出狀態另輸出 `gis_release_gates.csv`，保留範圍、母數、完成數與封鎖原因。

依四種情境分別產生：
- `alternatives_completeness.csv`：每專案、各情境有效資料比例、是否進入 MCDA、逐項原因。
- `criterion_coverage_long.csv`：每專案 × 每準則的驗證狀態。
- `mcda_eligibility_long.csv`、`mcda_alternatives.csv`：可進入各情境的清單。
- `matrix_G0_BASELINE.csv`、`matrix_R1_STRICT.csv`、`matrix_S1_DIRECT.csv`、`matrix_RS_STRICT.csv`：**只有全部必要 Point Values 通過驗證時**才寫入供 R 排序的數據列。

### 05. `r_export` — 生成 R 分析所需輸入

輸出 `r_criteria_dictionary.csv`、`r_weights.csv`、`r_scenarios.csv`、`r_settings.csv`，以及四種情境的 `ahp_pairs_*.csv` 成對比較空白問卷。

`R/run_mcda.R` 直接讀入第四階段的決策矩陣，提供：
- AHP 權重估計與一致性比率 CR；
- PROMETHEE II（V-shape 偏好函數）、SAW、TOPSIS；
- Dirichlet Monte Carlo **權重不確定性**下的 Rank Median／Top 3／Top 5 機率；
- Leave-one-criterion-out 與偏好門檻敏感度分析。

研究者需填寫 AHP 成對比較；預設不產生假權重。若要以研究設計內的三組權重做程式試算，才使用 `--illustrative`，輸出標記 `ILLUSTRATIVE_ASSUMED_WEIGHTS`。

## 安裝與執行（Windows PowerShell／macOS／Linux）

```bash
python -m pip install -e '.[test]'
au-ree plan
au-ree run --through r_export --offline
au-ree status
python -m pytest -q
```

首次離線運算會建立 `work/research.sqlite`、母體快照、各構面稽核表及 R 模板。若仍沒有研究者核准的最新座標或來源報告，Stage 4 的正式 MCDA 矩陣會是**只有欄名的空表**，不產生捏造的排行榜。

### 官方來源更新

```bash
au-ree run --stage population --refresh
au-ree run --through r_export
```

實務上若 Stage 1 新增大量 project，先審核 `population_review_queue.csv`，在 `inputs/project_reviews.csv` 逐筆補充並驗證目前 activity/lifecycle/REE role/座標後再重跑；接著在 `inputs/verified_observations.csv` 加入技術報告值及來源。Stage 2 會自動依最新版資料重建，Stage 3 只對已核准座標計算正式距離。

### 單獨重跑或續跑

```bash
au-ree run --stage criteria --force
au-ree run --through gis
au-ree run --through eligibility
au-ree run --through r_export
```

每個階段保存設定、程式、來源與上游指紋。相同輸入會使用 Checkpoint (`REUSED`)；來源、上游、設定或程式碼變更則自動使下游失效，舊輸出歸檔到 `work/snapshots/`。

### R 分析（有合格 Alternatives 後）

```bash
Rscript R/run_mcda.R \
  --input work/outputs/04_eligibility/matrix_G0_BASELINE.csv \
  --criteria work/outputs/05_r_export/r_criteria_dictionary.csv \
  --weights work/outputs/05_r_export/r_weights.csv \
  --ahp work/outputs/05_r_export/ahp_pairs_G0_BASELINE.csv \
  --perspective development_driven \
  --reps 10000 \
  --seed 20261029 \
  --out work/r_results/G0
```

填完 `ahp_pairs_G0_BASELINE.csv` 的 `ratio` 才能用 `--ahp`。輸出包含排名比較、Monte Carlo rank distributions、LOO、threshold sensitivity 與權重／門檻紀錄。若僅進行技術試算，用 `--illustrative` 取代 `--ahp ...` 並在結果標註假設權重。

## 重現性與 Git

- 主要輸入：`inputs/`、`config/`、`src/`、`R/`，全部可 Git 追蹤。
- 正式資料庫位於 `work/research.sqlite`，階段前先複製 SQLite，完整性檢查通過後才替換正式資料庫。
- 每階段輸出 `manifest.json`，記載來源、程式版本、輸入指紋、更新狀態。
- 原始 API JSON 暫存於 `work/cache/`，再次運算使用已取得內容；若需要凍結完整資料快照，將 `work/cache/` 連同 manifest 依 Git LFS／DVC 或獨立資料歸檔保存。
- `work/` 不加入 Git 追蹤，程式／規則變更以 commit 記錄，不覆寫凍結歷史輸入。
- 原始研究參考：`20260906 purposal.pptx`、`MCDA納入條件討論.txt`、r963–r983、Cook & Pétursson (2025)、Dayo-Olupona et al. (2020)。

## 原始公部門資料頁面

- [Geoscience Australia — Rare Earth Elements / Layer 52](https://services.ga.gov.au/gis/rest/services/AustraliasIdentifiedMineralResources/MapServer/52)
- [Geoscience Australia — Critical Mineral Deposits / Layer 7](https://services.ga.gov.au/gis/rest/services/AustralianCriticalMineralsOperatingMinesAndDeposits/MapServer/7)
- [Infrastructure — Key Freight Road / Layer 5](https://spatial.infrastructure.gov.au/server/rest/services/KeyFreightRoutes/Key_Freight_Routes/MapServer/5)
- [Geoscience Australia — Railway Lines / Layer 1](https://services.ga.gov.au/gis/rest/services/Foundation_Rail_Infrastructure/MapServer/1)
- [Geoscience Australia — Power Lines / Layer 2](https://services.ga.gov.au/gis/rest/services/Electricity_Infrastructure/MapServer/2)
- [Geoscience Australia — Major Ports / Layer 0](https://services.ga.gov.au/gis/rest/services/Maritime_Facilities/MapServer/0)

## v1.0.1：獨立來源文件核准（Evidence Approval）

新增 `inputs/evidence/`（正式 PDF／原始 JSON／GIS GeoJSON 的封存目錄）、`inputs/source_documents.csv`、`inputs/evidence_approvals.csv`。這兩個 CSV 與觀測值／專案審查 CSV 分開管理。

1. 將原始來源檔放在 `inputs/evidence/<file>`，保留來源 URL。這些檔案必須是真正下載的原始位元組，不是輸入 SHA 字串的替代品。
2. 計算原件的 SHA-256：`python -c "from pathlib import Path; import hashlib; print(hashlib.sha256(Path('inputs/evidence/report.pdf').read_bytes()).hexdigest())"`。
3. 在 `inputs/source_documents.csv` 加上 `document_id,file_path,source_url,sha256`。`file_path` 限制在 `inputs/evidence/` 內。
4. 審查者在 **獨立** `inputs/evidence_approvals.csv` 加入 `approval_ref,record_type,document_id,reviewer,decision,reviewed_at,notes`；`record_type` 僅 `OBSERVATION`、`PROJECT_REVIEW` 或 `GIS_LAYER`，`decision=APPROVED` 且審查日期不晚於快照日期。
5. `inputs/verified_observations.csv` 與 `inputs/project_reviews.csv` 必須另填對應 `approval_ref`；GIS 則在 `config/gis.json` 各圖層提供 `local_geojson`、`expected_sha256`、`official_source_url`、`approval_ref`。
6. 重跑 `au-ree run --through r_export --offline`；Stage 02 另外輸出 `source_documents_audit.csv` 與 `evidence_approvals_audit.csv`，保留檔案完整性與核准結果。

更改封存檔位元組、撤銷審查、修改核准日期或變更來源 URL，都會使該核准失效。Stage 02 重跑會刪除舊的衍生 Observation 並按現有核准狀態重建；Stage 01 也會撤銷先前依審查得到的 VERIFIED 座標／活動階段。尚未核准的輸入只保留 `REVIEW_PENDING`，不作為正式數值。

此處的 SHA-256 代表 **原始檔案完整性**；審查者身份由研究工作流程與 Git 提交紀錄管理，並非密碼學數位簽章。正式研究需另外查驗文件來源、內容、有效日期和數值擷取。

### GitHub Actions

- `.github/workflows/python-offline.yml`：Python 3.11／3.13 的 pytest、完整五階段凍結資料離線重跑、Checkpoint 重用、SQLite integrity／FK、零未核准分數斷言。
- `.github/workflows/r-mcda-smoke.yml`：安裝 R 4.4.3，以 **完全合成** 的 3 個測試 Alternatives 驗證 AHP、PROMETHEE II、SAW、TOPSIS、Monte Carlo；檢查固定 seed 可重現，並確認空矩陣會被拒絕。

兩個 workflow 只在 GitHub 上啟動後執行；本機 Python 測試不要求連網或 R。CI 中的合成排名只供演算法驗收，不能用於研究結論。

### 本地回歸測試

```bash
python -m pytest -q
au-ree run --through r_export --offline
au-ree status
```

新表格由 `src/au_ree/core.py::setup` 以 `CREATE TABLE IF NOT EXISTS` 增量建立，保留既有 project／observation schema；新版本支援既有 SQLite 快照的向前遷移。

## v1.0.2：聯邦與州官方母體擷取／身份核查

- Stage 01 新增 `source_adapters.py`，支援五個正式 ArcGIS Feature Layer（GA ×2；WA／QLD／TAS ×1），以及四個已啟用但需政府匯出的州資料來源（NT／SA／NSW／VIC）。
- `PROJECT` 與 `DEPOSIT`、`OCCURRENCE` 分離。後者不會只憑相同名稱自動併入 `project_master`，而是提供 possible parent 候選。
- 自動比對 native ID、精確名稱／州別、別名；公司差異及州座標異常進 Review；近鄰 25 km 僅提示可能重複。
- 新增 `population_identity_audit.csv`、`population_duplicate_review.csv`；原有 `population_master.csv`、`population_review_queue.csv`、`population_source_registry.csv` 不變。
- `project_master.operator_name` 新增欄位，相容舊有 SQLite（自動遷移），保留未驗證資訊的 provenance。
- 每個官方 ArcGIS 來源的原始 Metadata／ID／Features JSON 與 SHA-256 Manifest 保存在 `work/cache/census/`；可逐來源更新。
- 離線模式中未有快取的網路來源標記 `OFFLINE_CACHE_MISSING`；州政府未匯出者為 `AWAITING_OFFICIAL_EXPORT`，避免將未取得資料算作「查無專案」。
- 本次環境禁止容器向外連線，故**沒有即時下載新的官方紀錄**；GitHub Actions 的線上更新 workflow 待推送遠端後執行。

來源詳細位置、欄位映射與資料使用規則請見 [`docs/official_population_sources.md`](docs/official_population_sources.md)，四州匯入方式見 [`inputs/state_exports/README.md`](inputs/state_exports/README.md)。


## v1.0.4：Scheme A 身分與去重閘門

- 官方稀土礦點／含 Monazite、Xenotime 的礦物伴生紀錄先進擴充礦點名冊，不自動成為開發專案。
- 有獨立、可追溯的 Project 身分審查紀錄才可將**新的**官方來源候選新增到 `project_master`；203 筆舊名冊維持歷史未驗證基準。
- 地質實體、來源重複、Project–Deposit 關係和人工審查決策分表存儲；同名／鄰近僅產生去重候選。
- 審查輸入：`inputs/project_identity_decisions.csv`；流程及新 CSV 請見 [`docs/SCHEME_A_PROJECT_MASTER.md`](docs/SCHEME_A_PROJECT_MASTER.md)。
