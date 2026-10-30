## 研究目的與 Gate

- **Aim：** <!-- A / B / C / Infrastructure --> 
- **工作包／Gate：** <!-- P0.1, P0.2, P1.1, P1.2, P2.1, P2.2, P3 -->
- **現有行為 → 預期行為：**
- **Gate Status：** <!-- PASS / PARTIAL / BLOCKED -->
- **關聯規格：** [Research Architecture](https://github.com/lleeoo0611-stack/AU_REE/blob/main/docs/RESEARCH_ARCHITECTURE.md) · [Implementation Plan](https://github.com/lleeoo0611-stack/AU_REE/blob/main/docs/RESEARCH_IMPLEMENTATION_PLAN.md)

## 研究契約檢查

- [ ] 已核對 C0/C1/C2/C3 的定義、Project/Deposit 身分和關聯；或本 PR 不涉及
- [ ] 已核對來源、文件 SHA-256、effective/publication dates、approval 狀態；或本 PR 不涉及
- [ ] 已核對 JORC／TREO／REE oxide basis、Resource Statement、重複計算；或本 PR 不涉及
- [ ] 已核對 Criteria Dictionary、固定效用、Dependency、AHP/Scenario 和 `G0 != 六構面`；或本 PR 不涉及
- [ ] 已核對 B1–B4／SMAA 假設及 Aim C Stage/D1 循環風險；或本 PR 不涉及
- [ ] 原始資料、穩定 `project_id`、凍結快照和 v1 baseline 可重建；或清楚說明 migration
- [ ] 任何參數/母體/科學假說的改動已加入 `docs/RESEARCH_DECISIONS.md`

## 驗收與可重現性

- **測試／結果：** <!-- pytest; R synthetic; lineage; acceptance tests; QA -->
- **研究數據狀態：** <!-- SYNTHETIC / REVIEW_PENDING / APPROVED / NOT_APPLICABLE -->
- **Snapshot ID／版本／Seed：** <!-- dataset, schema, criteria, utility, weights, method, commit -->
- **輸出與來源：** <!-- CSV/SVG/GPKG + manifest path; no unapproved ranking -->
- **保留的問題／下一步：**

## 文件同步

- [ ] README 的已實作／待實作狀態如有變更已更新
- [ ] `docs/CHANGELOG.md` 已更新
- [ ] 相關的 DATA / MCDA / VALIDATION Protocol 與 [研究需求](https://github.com/lleeoo0611-stack/AU_REE/blob/main/docs/RESEARCH_REQUIREMENTS_AIMS_ABC.md) 如有方法變動已更新
- [ ] PR 不直接改寫已發布歷史檔案；新增輸出有新 snapshot ID 與 checksum

> 設計契約：[docs/RESEARCH_ARCHITECTURE.md](https://github.com/lleeoo0611-stack/AU_REE/blob/main/docs/RESEARCH_ARCHITECTURE.md)。若 v2 參數尚未定稿，請先提出 docs/decision PR，再進行演算法／資料庫修改。
