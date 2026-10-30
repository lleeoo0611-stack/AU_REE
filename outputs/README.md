# 已追蹤的 Census 審閱輸出

此目錄保存 2026-10-29／30 審閱工作流輸出的可編輯 CSV、JSON manifest。它們是**有來源與版本的發布成果**，不能因重新執行而在 Git 內直接覆蓋；新更新須建立新的 snapshot/release 並記錄 SHA-256。

| 類別 | 代表檔案 |
| --- | --- |
| 固定目標與裁定 | `487_definition_review.csv`、`487_inclusion_gate.csv`、`487_row_adjudication_compact.csv` |
| 身分與去重 | `project_entity_register.csv`、`project_entity_membership_487.csv`、`project_dedup_candidates.csv` |
| 來源證據 | `project_evidence_register.csv`、`source_evidence_locator_review_95.csv`、`reconstructed_1006_evidence_ledger.csv` |
| 公司與礦權 | `project_rights_history_review.csv`、`company_entity_resolution_queue_487.csv`、`487_official_tenure_trace_status.csv` |
| QA／溯源 | `quality_gate_487_summary.json`、`census_review_manifest.json`、`upstream_reproducibility_gaps.csv` |

詳細資料來源、表格與重建方法：[`README_REPRODUCIBILITY.md`](README_REPRODUCIBILITY.md)；[Census Release](../CENSUS_RELEASE.md)。

請區分 `outputs/`（本儲存庫已有的發布審閱資料）和 `work/`（忽略追蹤的本機執行輸出），以及真正完成 evidence approval 的正式 MCDA matrix。
