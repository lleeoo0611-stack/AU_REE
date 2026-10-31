# AU_REE 目前資料結構與母子腳本契約

**資料／程式盤點：**2026-11-01，對應 GitHub `main`（C0/F1/F2 + C1/C2 規範已合併）與本批母腳本增量開發。原始 Census 快照 as-of 2026-10-29，不因本批審查日期而自動更新。

## 1. 現有根目錄的真實用途

| 路徑 | 性質與內容 | 讀寫原則 |
| --- | --- | --- |
| `src/au_ree/` | 原有五階段程式庫，`cli.py` 順序是 population → criteria → GIS → eligibility → R export；SQLite 結構與邏輯核心 `core.py`；原 `python -m au_ree` 保留 | **獨立的舊版可重現運算**；C1 尚未通過不得以其輸出取代正式研究排名 |
| `scripts/` | Census 擷取、raw 恢復、歷史稽核及新增 C0/C1/證據分流子腳本；統一入口 `run_research_pipeline.py` | 不移動既有多年來源腳本，避免破壞舊快照的 reproducibility；新入口可決定何時執行 |
| `reproducibility/` | 487 row 凍結 workpack、SQLite rebuild/capture/verify、manifest 與 snapshots；已有 `rebuild_all.py` | **另一路不可替代的歷史快照母腳本**；保留既有輸出及資料來源 |
| `config/` | census/GIS/criteria/R 的 v1 config + `c0_freeze_policy_v1.json`、`cohort_c1_c2_policy_v1.json` 和新的 `research_pipeline_v1.json` | 研究政策與執行順序可讀、可版本控制 |
| `inputs/` | Legacy、政府來源、document references、P1–P4 判讀 CSV、`review_decisions/` 獨立審查表、`evidence/` 新證據事件 | **人工輸入**，不得由子腳本臆造簽章或更改 frozen IDs |
| `data/raw_snapshots/`、`data/source_snapshots/`、`data/document_snapshots/` | 原始來源快照/原件文字或元資料；保留 provenance | 固定版本，不覆寫原始取得之資料 |
| `db/migrations/` | SQLite 資料表變更版本 | 不因來源審核完成直接改 SQL schema |
| `docs/audits/` | 固定日期／批次的 487/339/39 筆 evidence rows、Gate、來源交叉表、JSON summary | **衍生可編輯成果**，由相應 Python script 重建後 commit |
| `outputs/` | 既有 487 census 與追溯輸出、審查工作表 | **舊資料產物**，不代表正式 C1 主排名 |
| `R/` | 現有 `run_mcda.R`、R 排名／情境工具 | 僅在 **C1 signed + panel fixed + GIS released** 後使用於研究主結果 |
| `.github/workflows/`、`tests/` | 分階段 CI、重建測試、錯誤輸入拒絕檢查 | CI 通過只代表程式／資料結構一致；不等於獨立來源真偽或科學准入核准 |

`README.md` 是導航入口，詳細時序的舊版 README 保留在 `docs/archive/README_pre_mainline_2026-11-01.md`，避免繼續向最上方堆疊歷史批次資訊。

## 2. 正式資料鍵與層級（不得混用）

```
Government source / Company report / Legacy census target
  source_key + source_native_id + source_snapshot + target_id
  ├─ Historic Source Claim (original URLs / pages / SHA)
  ├─ Deposit / Prospect / Tenement / Mineral Occurrence
  └─ Project candidate (verified project parent, stage as-of)
       ├─ Project–Deposit resource statement (category / units / cutoff / REO)
       ├─ Licence and GIS project boundary
       └─ Signed Project C1 / C2 Gate (independent reviewed decision)
```

**來源筆數**和 **Project 數量**不能等同。339 個 P2–P4 source target 的 baseline、151 個 native-only target 共享的 100 個來源工作群組，以及 39 個 Project 審查群組屬於不同層級；13 個 P1 source cases 也不能直接增加 13 個 Project。C1 的統計單位始終是獨立獲核准 Project。

## 3. 新母腳本及子腳本

`config/research_pipeline_v1.json` 是路由清單，母腳本 `scripts/run_research_pipeline.py` 按需用 `subprocess.run` 呼叫：

1. `scripts/build_c0_freeze_c1_c2_v1.py`：已採納的 F1/F2、C1/C2 簽核驗證及 339/39/13 筆衍生審查表。
2. `scripts/review_c1_stage1_v1.py`：**C1 主線**，7 個具經濟研究線索 Project 的來源範圍複核與 39 個群組 Gate 預審；保留 2026-10-29 截止日及人工核准條件。
3. `scripts/route_p234_new_evidence_v1.py`：**P2–P4 支線**，只有 `inputs/evidence/p234_new_primary_evidence_events_v1.csv` 實際新增具 source-native locator 的事件時才執行並產生來源審查任務；無事件時主腳本顯示 `SKIP_NO_NEW_EVIDENCE`，不得無意義地掃描既有 URL。
4. 舊 `src/au_ree/cli.py` 五階段，可選擇明確的 `--profile legacy`，`--mode check` 只列出五階段，`--mode write` 才呼叫既有 `run --through r_export --offline`；**不在標準 C1/all profile 自動執行。**

工作流程不是排程爬蟲；當 GitHub PR／commit 修改新證據 CSV、事件審核表、或 router 原始碼時，新的 Actions workflow 將驗證事件與衍生佇列。真正官方報告的發現、下載與獨立審查仍需外部來源或人工事件輸入。

## 4. 重新執行與核查

```bash
python scripts/run_research_pipeline.py --profile all --mode check
python scripts/run_research_pipeline.py --profile c1 --mode write
python scripts/run_research_pipeline.py --profile p234 --mode check
python scripts/run_research_pipeline.py --profile all --plan
python -m unittest discover -s tests -p test_c1_stage1_v1.py -v
python -m unittest discover -s tests -p test_p234_new_evidence_trigger_v1.py -v
python -m unittest discover -s tests -p test_research_pipeline_supervisor_v1.py -v
```

`--mode check` 只驗證 repo 的 tracked 衍生報表能依現有輸入重建；`--mode write` 只寫衍生 CSV/JSON，**不覆寫來源、人工決策、原始 PDF、Git 快照或正式 Approved Gate**。新證據 PR 需包括衍生結果；CI 的 diff check 檢測是否忘記重生。

## 5. 科學與版本控制

- 正式 C1：同一 Project 的身份、REE 產品角色、pre-FID 原始經濟 Study、JORC REO、固定六構面 Panel 和 GIS 六 Gate 必須獨立通過；審核 7 個 Study 線索只是第一步，C1=0 仍是正確目前狀態。
- C2：已簽核獨立 Project ID、範圍與 REE 產品角色但缺 C1 若干條件者；未核准的 28 個身份審查候選不是已通過的 C2。
- C0 F1/F2：119 筆有界來源結案候選、151 筆 native-only 搜尋暫停預審；未簽核者皆 HOLD。6 筆有外部新報告線索不可直接 F2。
- 後續正式結果須保存 `source_snapshot`、Git SHA、Gate 版號、Panel 版號、原始 provenance 與 model seed；舊 v1 pipeline 及 487 Census 不刪改。
