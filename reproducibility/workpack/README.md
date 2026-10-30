# 487 筆 Census 審閱工作包

此資料夾保存**歷史審閱工作包專用腳本**；與 `src/au_ree/` 五階段正式 pipeline、`scripts/` 的全澳資料篩選工具分開。它們依賴封存的 `trace_artifact/`、`scheme_a_upstream/`、`national_raw_upstream/` 與 `deliverable/`，不會自行憑名稱建立正式 MCDA Project。

## 入口

從儲存庫根目錄、已備妥封存原始資料的環境執行：

```bash
python reproducibility/rebuild_all.py \
  --root . --as-of-date 2026-10-29 --snapshot-id 2026-10-30-new-run
```

`--snapshot-id` 必須選用新的未使用 ID。runner 會引用 `scripts/build_487_definition_review.py`、`scripts/build_487_complete_proposal_workpack.py`、`scripts/build_487_editable_workbook.py` 及本目錄工作包專用的四個腳本：

| 檔案 | 職責 |
| --- | --- |
| `reproduce_86_401_cohorts.py` | 重建既有 86+401 選取規則與決策紀錄 |
| `enrich_candidate_evidence.py` | 加入來源佐證和納入條件審閱 |
| `complete_487_source_review.py` | 487 筆來源審閱與候選審查 |
| `build_row_level_trace_bundle.py` | 匯出逐列礦權／空間證據 |

這些腳本執行時接收工作包根目錄引數，並將產出寫入 `<root>/deliverable/`。相同名稱的 `scripts/enrich_candidate_evidence.py`、`scripts/reproduce_86_401_cohorts.py` 使用已追蹤 `outputs/`，是另一套用途，**不可互換**。

SQL migration 單一正式位置是 [`db/migrations/`](../../db/migrations/)；歷史根目錄的重複 SQL 已移除。舊研究快照的 provenance 引用仍按原 manifest 保留，新的 capture 記錄新的腳本路徑。

## 資料品質與驗證

- 必須保留 Project、Deposit、Tenement、公司角色、來源ID與證據核准狀態；不以名字相似直接合併專案。
- 既有 487 個來源 ID 不得隱性丟失，未解決者保留 HOLD；Census 審查不等於 MCDA 分析。
- 重新執行結果、SQLite 檢查、封存 SHA 與新舊快照比對見 [`reproducibility/README_QUALITY_AND_ENTITIES.md`](../README_QUALITY_AND_ENTITIES.md) 及 [CENSUS_RELEASE](../../CENSUS_RELEASE.md)。

完整系統操作指令見 [docs/RUNBOOK.md](../../docs/RUNBOOK.md)。
