# 487-row entity linkage and quality review

`quality_gate_487.py` runs inside `rebuild_all.py` after row adjudication and before CSV-to-SQLite construction. It requires only the Python standard library.

## 原始 ArcGIS Source bytes 的重建檢查

`src/au_ree/source_adapters.py load_arcgis()` 在同一 query-source snapshot 首次成功下載後建立 `manifest.json`，內容包含 metadata／IDs／每個原始 feature chunk 的 SHA-256、筆數、source URL 與查詢。後續離線重建重新比對，若同一 Object ID 的礦點內容被改寫、metadata/IDs 變動或查詢契約不同，立即拒絕重建；不得重新計算 hash 後覆蓋原先 manifest。**在任何重新下載／寫入前，先驗證全部舊 metadata、IDs、feature chunks 均存在且 SHA-256 不變；遺失檔案也不得自新 API 回應補入既有快照。原生 Object ID 清單若包含重複 ID 則明確拒絕，不可靜默去重。**修正資料必須另建版本化 source snapshot，不直接修改不可變原始檔。

## 現行 487-source SQLite 重建驗證（2026-11-01）

- **487 source targets** 仍各有獨立 `target_id`，對應 **451 個來源原生實體識別**。其中 36 組 Legacy／E1 targets 引用同一 `source_key/native_id`，均保留兩筆 Target ID，不能重複計算為 Project。
- 現行 `outputs/project_entity_register.csv` 是 **39 個未獨立核准的 Project 審查候選群組**；`project_entity_membership_487.csv` 中 78 筆來源有候選 group link，409 筆未連結。候選關係不代表獨立 Project、JORC 或 C1 簽核。
- `reproducibility/build_census_database.py csv-build` 現於 SQLite 寫入前驗證這些輸入 CSV 的來源 Target ID、州別、Cohort、Entity ID、已審查候選 Project 的關聯是否一致。同一 native entity 重複時，要求來源原生 ID、名稱、州別、實體類型與 Project 關係一致，否則拒絕重建。
- `tests/test_p0_487_batch.py` 在 CI 使用既有 `outputs/` CSV 測試實際 SQLite 重建、邏輯關聯和負向破壞案例。這是**程式及結構一致性檢查**，不代表已完成來源全文、人工核准或全澳 Census 科學驗收；正式 C1/C2 仍無核准專案。

以下「Current verified state (2026-10-29)」為**先前歷史工作包版本**的記錄（30 群組／46 筆連結），並非 2026-10-31 後的現行 39 群組資料；保留歷史計數以追溯。

## Output tables

- `project_entity_register.csv`: deterministic IDs for reviewed Project candidates and source-level entities. Project candidate IDs use the current candidate group key; a key change creates a new ID and must be reviewed as a possible rename/merge/split. Source records are retained separately as Project candidate, deposit, prospect, tenement, occurrence, or historical source-record entities.
- `project_entity_membership_487.csv`: exactly one row for each frozen target ID. The `project_entity_id` is populated only when the target occurs in the reviewed project candidate crosswalk. Other targets remain `UNRESOLVED_NO_PROJECT_LINK_INFERRED`.
- `project_evidence_register.csv`: one row per recorded URL. URL presence does not establish that the source supports a condition. Source type, publisher/date, page/section, claim, and condition supported are explicit review fields and stay blank/unclassified until checked.
- `quality_gate_487.csv` and `quality_gate_487_summary.json`: row counts, ID consistency, link coverage, source locator gaps, disposition counts, and input hashes.

Each of the five conditions is normalized to `PASS`, `FAIL`, `UNKNOWN`, or `CONFLICT`. Only `PASS` across all five on Project-level evidence is eligible for human-approved inclusion. `UNKNOWN` and `CONFLICT` remain HOLD; the script never promotes or excludes a Project by name similarity or missing evidence. Registered titleholder and operator/proponent are separate fields and remain blank until source evidence distinguishes them.

## Current verified state (2026-10-29)

- 487/487 original target IDs are unique and appear once in the inclusion gate and entity membership table.
- 30 reviewed candidate Project groups are represented, with 46 target rows linked to those groups and 441 without a reviewed Project link.
- 95 candidate source URLs are listed individually. All 95 still need page/section and claim-level review; the URLs have not been treated as proof by themselves.
- The original 37 `PROJECT_CANDIDATE_REVIEW`, 6 `HOLD_REE_ROLE`, and 444 `HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE` row dispositions are preserved. Candidate rows still require human sign-off; no exclusions or MCDA decisions are added.

This quality layer makes the gaps explicit and machine-checkable. It does not claim that the unresolved project, tenure, company-history, or evidence-location work is complete. Refreshing external sources requires a new dated evidence snapshot and review; there is no automatic web acquisition in this runner.

## Delimiter correction

Target ID lists accept pipe, semicolon and newline separators. All 487 IDs are retained; 46 have existing review-group links (37 candidate rows and 9 HOLD rows), with 441 unlinked. Three Mary Kathleen HOLD rows link only to a review group while their admission gate remains unresolved. Independent ID extraction, unknown/duplicate-ID checks and gate/group reconciliation guard against silent loss. The workbook includes 487 entity-link rows and cross-table differences. Release snapshot: 2026-10-29-r18-delimiter-release.

