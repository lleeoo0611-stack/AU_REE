# Git 工作流程

```bash
git clone <repository-url>
git switch -c feature/population-ga-2026
python -m pytest -q
git add src config R tests docs inputs
# Review inputs and generated manifests; do not commit private temporary databases.
git commit -m "feat(population): update official sources and QA rules"
git tag -a research-snapshot-2026-10-29 -m "Five-stage reproducible research baseline"
```

建議分支：`main` 凍結研究基線、`feature/population-*` 改官方母體、`feature/evidence-*` 修改變數及來源、`feature/gis-*` 調整圖層、`feature/mcda-*` 迭代 R 模型。

版本規則：程式碼與 config 使用 Git；大型 raw API JSON、官方 GIS 圖層與每次 SQLite 快照以 Git LFS 或 DVC／外部歸檔保存，並在 Release manifest 記錄 SHA-256、資料日期和原始 URL。更新資料日期時建立新的研究快照，保留舊版。

## v2 研究契約與 PR 驗收

後續對 `src/`、`R/`、`db/`、`config/`、`scripts/` 或研究輸入的修改，應先閱讀 [研究總架構](RESEARCH_ARCHITECTURE.md) 及 [實施與驗收計畫](RESEARCH_IMPLEMENTATION_PLAN.md)。依 [PR Template](../.github/pull_request_template.md) 明列對應 Aim、P0–P3 Gate、既有/預期行為、來源與核准狀態、版本與測試。首次需要改變 Cohort、Criteria、AHP 或不確定性參數時，應先提交 Decision Log/Protocol 的文件變更，再進行功能 PR。

主 README 僅保存概要與狀態；完整數據 Schema、MCDA、SMAA／Aim C 檢驗規格分別維持於專用 Protocol，不在各腳本旁重複貼同一份規格。每次 merge 更新 Changelog；freeze 的來源及已發佈快照須保留 hash 與原始位置。
