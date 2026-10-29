# 澳洲 REE 五階段管線 v1.0.1｜離線驗證報告

- 版本：v1.0.1
- 日期：2026-10-29（台北）
- 測試環境：Python 3.13.5、SQLite、pytest、Shapely、pyproj；Linux，研究資料下載完全離線
- 版本來源：v1.0.0 Git 分支延伸；歷史 r963 母體與 r968 Observation 保持凍結
- 研究基準：六構面、12 準則；19 筆歷史 r974 Alternatives 作為 G0 固定母體

## 1. 修改內容與驗收

| 子系統 | v1.0.1 變更 | 驗證 |
|---|---|---|
| Source document | 新增封存檔實際 SHA-256 計算、原始 URL 與 `inputs/evidence/` 安全路徑檢查 | PASS |
| Independent review | `source_documents.csv` 與 `evidence_approvals.csv` 分離，記錄核准人、類型、日期及狀態 | PASS |
| Observation | 自行填寫 `VERIFIED` 無法取得評分資格；獨立批准後才能轉為 Verified | PASS |
| Evidence revocation | 原件更改、審查撤銷、日期超過截止日後，重新運算會取消原評分和衍生數值 | PASS |
| Project review | Project 活動階段、REE role、座標更新需要獨立核准；撤銷後重算還原未驗證狀態 | PASS |
| GIS local layer | 檢查封存 GeoJSON 的實際 hash、來源 URL、GIS_LAYER 核准；未核准圖層不產生正式 Verified 距離 | PASS |
| Global release | G0 固定 19 筆候選，正式點值矩陣需全部 19 筆完成四項已核准 GIS 與其他準則 | PASS |
| Subset release | R1/S1/RS 子集至少兩筆、所有子集成員均完成已核准 GIS；可與未釋出 G0 分開運作 | PASS |
| SQLite stage rollback | 模擬階段失敗時正式 SQLite 不變 | PASS |
| GitHub workflows | Python 3.11/3.13 offline regression 與 R 4.4.3 synthetic smoke workflow 檔案已產出，YAML 結構通過本機解析 | CONFIGURED |

## 2. Python 測試及獨立重建

- `pytest`：**18/18 PASS**。
- 從空白 SQLite 執行 `population → criteria → gis → eligibility → r_export`：**5/5 stages executed**。
- 第二次相同執行：**5/5 Checkpoints REUSED**。
- 使用不同工作目錄與全新 SQLite 獨立重建：母體筆數、階段 Fingerprint、Eligibility Gate 與資料表筆數完全一致。
- `PRAGMA integrity_check`：**ok**。
- `PRAGMA foreign_key_check`：**0 違規**。

### 正式凍結資料輸出

| 表格／指標 | 紀錄數 |
|---|---:|
| `project_master` | 203 |
| `population_candidates` | 203 |
| `source_registry` | 3（歷史來源 1，離線 GA 來源 2） |
| `criteria` | 12 |
| `observations` | 220（凍結歷史資料） |
| `criterion_values` | 2,436 |
| `gis_project_status` | 76 |
| `gis_metrics` | 76（可驗證的正式距離 0） |
| `coverage` | 2,436 |
| `eligibility` | 812（203 × 4 scenarios） |
| `gis_release_gates` | 4 |
| `source_documents` | 0（正式研究尚未填入封存文件） |
| `evidence_approvals` | 0（正式研究尚未加入獨立核准） |
| 已核准的觀測資料 | 0 |
| 正式 MCDA point-ready Alternatives | 0 |

### GIS Release Gate

| 情境 | Scope | Cohort | Verified GIS | Status |
|---|---|---:|---:|---|
| G0_BASELINE | Global frozen cohort | 19 | 0 | BLOCKED |
| R1_STRICT | Strict resource subset | 0 | 0 | BLOCKED |
| S1_DIRECT | Direct strategic subset | 0 | 0 | BLOCKED |
| RS_STRICT | Resource + strategic subset | 0 | 0 | BLOCKED |

合成測試另外證明：當只有兩個經過完整獨立核准、具有全部 GIS 值的專案時，R1 可標示 `RELEASED_SUBSET` 並輸出 2 列測試矩陣；G0 保持 BLOCKED。當 19 筆完整且全部符合點值分析時，G0 才可 `RELEASED_GLOBAL`。上述合成資料不在正式資料庫內。

## 3. GitHub Actions／R 的驗證邊界

- 本機無 `Rscript`，**R 的演算法未在本次離線環境實際執行**。
- `.github/workflows/r-mcda-smoke.yml` 已設定在 GitHub Runner 安裝 R 4.4.3，使用三筆 synthetic-only Alternatives 測試 AHP／PROMETHEE II／SAW／TOPSIS／Monte Carlo；確認相同 seed 結果一致及空矩陣拒絕執行。此流程需上傳至可存取的 GitHub Repository 才會真正執行。
- `.github/workflows/python-offline.yml` 在安裝 Python 依賴後，研究資料層全部採用 `--offline` 執行。此版本尚未執行 GitHub 雲端 Runner 測試。
- 正式 GA 與澳洲官方 GIS 線上資料下載不在本次離線測試範圍；兩個 GA Endpoint 在 offline 模式正確回報 `OFFLINE: external API disabled`。

## 4. 交付檔及接續工作

本版交付 Python、R、設定檔、SQLite 自動建立程式、合成驗收用測試資料、GitHub Actions 與可編輯報告。正式資料原始檔保留為空白登錄表，沒有對未知資料自動賦予 `VERIFIED`。

下一個研究步驟：歸檔 19 個主要 Alternatives 的來源文件與 GIS GeoJSON，計算 SHA-256、填寫獨立審查 CSV，重跑五階段；接著在 GitHub Actions 驗證 R 計算。

## 5. 主要驗證指令

```bash
python -m pytest -q
python -m au_ree run --through r_export --offline
python -m au_ree status
```

執行證據見獨立交付的 QA ZIP：`pytest.log`、`pytest.xml`、`run_1.log`、`run_2.log`、`reuse.log`、`verification.json`，以及隔離生成的 SQLite／CSV。
