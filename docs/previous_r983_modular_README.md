# AU REE MCDA — Stagewise r983 Architecture

以 2026-10-14 r983 的 GIS materialisation、release gate、scenario 與 AHP/PROMETHEE 設計為規格來源；保留**已通過整合測試的 r963–r974 SQL 計算核心**，新增分段 DAG、QA 與研究資料版本治理。

## 狀態與來源

- `legacy_r974/`：原有 r963–r974 可重現 SQL pipeline（來源於 `AU_REE_SQL_pipeline.zip`）。凍結，不以示意值取代計算。
- `src/ree_modular/`：新的 r975–r983 分段工作流程（**重新實作**，不是聲稱為 r983 monolith 的逐行抽出）。
- `config/`：criterion freeze、scenario、官方 GIS source contracts、AHP 用戶輸入。
- `work/`：執行時 SQLite、GIS cache、audit（不進 Git）。
- 使用 `project_id` 當永久關聯鍵；SQLite 是 source of truth，CSV／JSON 為可重建成果。

## 安裝

Python 3.11+；在本套件根目錄執行：

```bash
python -m pip install -e .
python -m pip install -e '.[gis,test]'
au-ree plan --through r982
au-ree run --group foundation
au-ree run --through r982
au-ree status
pytest -q
```

Windows PowerShell 也可使用相同命令。**離線預設**不會下載任何網站；缺少官方 GIS URLs 時，GIS 階段會完成診斷但回報 `PARTIAL_OR_NOT_CONFIGURED` / `BLOCKED_GIS_INCOMPLETE`，不進行正式 MCDA 排名。

### 階段獨立執行／續跑

```bash
au-ree run --stage r975          # 只跑此階段；必要前置須已建立
au-ree run --through r983        # 從 r963 依照 DAG 跑到 r983，沿用一致的 checkpoint
au-ree run --through r982        # GIS materialisation → GIS QA → scenarios → MCDA
au-ree run --group gis-materialize
au-ree status
```

執行順序是 `r963 ... r979 → r983 → r980 → r981 → r982`。r983 只增強官方 GIS 取得的穩定性，避免將未成功完整覆蓋的 vector 視為可評分資料。所有研究變數都保留 NULL 與來源狀態，不將 missing 當 0。

## 階段總覽

| 階段 | 功能 | 來源 / QA |
|---|---|---|
| r963–r969 | Population、scope、observations、canonical SQLite | 保留 legacy SQL engine |
| r970–r974 | Resource、Strategic、Technical、Development、GIS proxy、Commercial/ESG | 保留 legacy SQL engine |
| r975 | 12 criteria freeze | 配置檔，保留多種 resource reporting basis |
| r976 | evidence domain coverage gate | 有表格 ≠ 數值通過評分閘門 |
| r977 | review gaps | 保留問題與核對任務 |
| r978 | resource / strategic semantic basis audit | 不互轉 THM、MzEq、TREO |
| r979 | GIS authoritative source contracts | 缺來源維持 NOT_CONFIGURED |
| r983 | count-only probes、ID chunks、bounded retry、per-project checkpoint | 只有完整成功的官方圖層才能給 r980 |
| r980 | 以 EPSG:3577 計算距離及 GIS release | 19/19 x 4，禁止 proxy 自動升級 |
| r981 | scenario-specific cohort release | G0/G1、R1、S1 subset，避免跨礦床不當合併 |
| r982 | AHP CR + PROMETHEE II | 預設**零排名**；必須有審查過的準則矩陣與資料 |

## GIS 資料

在 `config/gis.json` 提供經核實的官方 ArcGIS REST Feature Layer URL 或本機 GeoJSON。服務端呼叫使用 count-only 空間探測、id chunk 分批下載、bounded retry/backoff 與 project-level JSON checkpoint。Ports 使用全圖層下載。

如使用自行提供的 `local_geojson`，須於同一位置建立 `<file>.geojson.verified.json`（包含官方 `official_source_url`、exact `sha256`、`projects_with_hits:19`）；否則只供稽核，不能評分。

## MCDA 排名啟用

r982 應保留「準備完成但未排名」狀態。使用者必須提供經研究者判斷的 AHP pairwise matrix，與對應 scenario 的整個觀測矩陣和 threshold，且 CR ≤ 0.1。最小配置參考 `config/preferences.example.json`，開啟 `enable_ranking=true` 後：

```bash
au-ree run --stage r982 --preferences config/preferences.json
```

本版本實作 point PROMETHEE II 的 V-shape preference；interval sampling、Monte Carlo、跨方法一致性與分層統計列為後續獨立工作，不宣稱已完成。輸入數據須另附原文頁碼、發布日期、有效日期與 source hash。

## 版本控制

- `main` 保留經測試的研究資料／方法版本。
- 功能分支如 `feature/r983-stagewise-pipeline`，通過 pytest 與 SQLite QA 後再開 PR。
- 不追蹤 SQLite binary、PDF／原始 GIS 大檔或 secrets；改保留 schema、config、manifest SHA-256、版本化輸入與 migrations。
- 新的外部證據日期須用新的 snapshot，不覆蓋 2026-10-12/14 frozen evidence。

## 研究目的

對應 proposal 的 6 domains、Redundancy Audit、AHP/PROMETHEE、resource/deposit-type comparability 與 sensitivity。現有 19 alternatives 是 frozen verified cohort；未有證據不可推定為 2026-10-29 最新全澳洲專案名單。

> 在無網路環境安裝 editable package：`python -m pip install -e . --no-build-isolation --no-deps`，或在根目錄以 `PYTHONPATH=src python -m ree_modular ...` 執行。
