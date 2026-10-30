# 操作說明（現行五階段管線）

## 環境與離線 QA

```bash
python -m pip install -e '.[test]'
au-ree plan
au-ree run --through r_export --offline
au-ree status
python -m pytest -q
```

`src/au_ree/` 的五階段依序為 `population → criteria → gis → eligibility → r_export`。SQLite 使用 `work/research.sqlite`；資料、程式及設定指紋記在階段 manifest。離線模式沒有已核准的專案/座標/數值時，決策矩陣可能只有欄名。

## 官方來源更新／續跑

```bash
au-ree run --stage population --refresh
au-ree run --through r_export

# 單獨重跑
au-ree run --stage criteria --force
au-ree run --through gis
au-ree run --through eligibility
au-ree run --through r_export
```

先在 `inputs/project_reviews.csv` 和 `inputs/project_identity_decisions.csv` 審查 Project 身分，再於 `inputs/verified_observations.csv` 填寫已追溯的技術資料。`inputs/source_documents.csv`、`inputs/evidence_approvals.csv` 和 `inputs/evidence/` 必須能核對來源原件的 URL/SHA-256 與獨立核准決策。GIS 的四個指標是核准座標對官方道路、鐵路、電線、主要港口的 EPSG:3577 直線近距離。

## R MCDA（須先通過 release gate）

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

需填妥 `ahp_pairs_*.csv` 比例並通過一致性檢查。僅在合成／示範試算中使用 `--illustrative`，輸出會標示 `ILLUSTRATIVE_ASSUMED_WEIGHTS`。現有 Monte Carlo 僅抽樣**權重不確定性**；SMAA、資料不確定性、Aim C 是 [待實作需求](RESEARCH_REQUIREMENTS_AIMS_ABC.md)。`G0_BASELINE` 缺 R/S，不能宣稱六構面完整排名；`RS_STRICT` 屬於另一個子集。

## 487 筆審閱與快照

`reproducibility/rebuild_all.py` 由 `reproducibility/workpack/` 的凍結審閱腳本及 `scripts/build_487_*.py` 重建資料。請閱讀 [workpack README](../reproducibility/workpack/README.md) 和 [Census release](../CENSUS_RELEASE.md)；執行前先準備先前封存的原始工作包，並使用新的 `--snapshot-id`，不可覆寫既有快照。

注意：`outputs/` 是**已追蹤的發布審閱結果**，`work/` 是本地未追蹤工作區；新數據應建立新快照與來源 manifest，而非改寫先前發布檔案。

### P0 487 Source Targets 一次性批次核查

本流程使用目前 Git 追蹤的完整來源審閱資料建立**非核准**的逐筆 Census audit，不需先安裝 xlsxwriter，也不會擅自修改 SQLite、JORC 或 MCDA：

```bash
python scripts/build_p0_census_487_audit.py \
  --root . \
  --run-date 2026-10-31 \
  --source-as-of 2026-10-29 \
  --output-dir work/audits
python -m pytest -q tests/test_p0_487_batch.py
```

產生 487 source-target 列、39 欄 CSV 與帶**實際 input SHA-256** 的 JSON summary。來源 join 必須是精確 `target_id`，並保留 39 group 的可追溯關聯；無關聯的 409 筆不自動提升 Project。**source record / spatial title intersect 不構成 Project 或權利關係核准。** 已發布的凍結結果：[報告](audits/2026-10-31_census_487_batch_review_report.md) · [CSV](audits/2026-10-31_census_487_batch_review.csv)。對後續來源時點使用新 `--run-date`，如已有輸出則拒絕覆寫；程式只在明確 `--overwrite` 下重跑同一路徑，不得將凍結 `docs/audits/` 當日常覆寫目錄。

## CI 與版本

`.github/workflows/python-offline.yml` 在 push/PR 測試 Python 3.11/3.13、五階段離線重跑、SQLite QA 與 checkpoint；`r-mcda-smoke.yml` 用合成 Alternatives 測試 R 4.4.3 的可重現性。工作包的完整 `rebuild_all.py` 需要封存來源與可選的 `xlsxwriter`，不屬於上述離線 CI 的測試範圍。
