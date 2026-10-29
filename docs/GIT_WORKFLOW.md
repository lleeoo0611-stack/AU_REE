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
