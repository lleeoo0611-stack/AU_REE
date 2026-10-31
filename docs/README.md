# AU_REE 文件導覽

由 [根目錄 README](../README.md) 開始。此處只保留現行研究的**導航與檔案職責**；各批次來源查核及歷史結果保留原路徑，不再把每份 CSV、JSON 和報告逐一列入主索引。

## 目前真正的研究工作

**優先完成指定來源截止日的 Project Census & Entity Resolution**，確認 Source Record、Project、Deposit、Prospect、Tenement、Occurrence 的身分與關係，以及 REE 產品角色和 Stable Project ID。未達驗收前，不推動新的正式 MCDA 模型或額外 Pilot。

截至原始來源快照 **2026-10-29**：487 筆 source targets；39 個候選 Project 審查群組，尚未全部驗證獨立身分；正式 C1、C2 核准數皆為 **0**。2026-11-01 的 7 個來源文字複查只屬證據線索，並非已核准 Project。上述數字為歷史基準，使用時應核對最新 GitHub 證據與簽核紀錄。

**完成標準**：所有截止日來源皆有明確處置（已確認、排除或具體待查），Project–Deposit 關係不重複，已確認 Project ID 穩定；重要身分判斷可追溯，且同一快照重新執行能重建同一份 Census。未決來源不得無聲排除或升級。

## 從哪裡開始讀

| 用途 | 現行入口 | 性質 |
| --- | --- | --- |
| 研究邊界與 Aim A/B/C | [Research Architecture](RESEARCH_ARCHITECTURE.md) | 已採用的研究框架；v2 參數與正式實作尚待完成 |
| 現在要完成的工作與驗收 | [Research Implementation Plan](RESEARCH_IMPLEMENTATION_PLAN.md) | 先 Census/Entity Resolution；其餘為後續依賴與既有技術規格 |
| Source、Project、Deposit、JORC 資料契約 | [Data Specification](DATA_SPECIFICATION.md) · [Project Resource Schema](P0_PROJECT_RESOURCE_SCHEMA.md) | 身分、證據、日期及資料模型規格 |
| Census 身分與准入規則 | [Project Master](SCHEME_A_PROJECT_MASTER.md) · [C0/C1/C2 Policy](C0_FREEZE_AND_C1_C2_POLICY.md) | 區分來源處置、獨立 Project 與 MCDA 資格 |
| 程式、資料夾與執行指令 | [Data Structure and Pipeline](DATA_STRUCTURE_AND_PIPELINE.md) · [Runbook](RUNBOOK.md) | 說明現行、舊版與歷史重建入口的差異 |
| MCDA 後續方法 | [MCDA Protocol](MCDA_PROTOCOL.md) · [Validation Protocol](VALIDATION_PROTOCOL.md) | 待正式資料母體及參數核定後使用 |
| 研究判斷及版本追溯 | [Research Decisions](RESEARCH_DECISIONS.md) · [Change Log](CHANGELOG.md) · [Git Workflow](GIT_WORKFLOW.md) | 保留已確認決策與修改紀錄 |

## Repo 中的檔案角色

| 路徑 | 職責／目前使用限制 |
| --- | --- |
| [`src/au_ree/`](../src/au_ree/) | 既有 Python/SQLite/GIS 五階段核心；目前是歷史 v1 運算，不等於已核准的六構面 C1 |
| [`scripts/`](../scripts/) | Census 來源處理、Entity Resolution 輔助、審查與調度；保留有相依關係的歷史腳本 |
| [`config/`](../config/) | 來源、分類、研究與執行設定；不可直接把設計規格視為已實作 |
| [`inputs/`](../inputs/) | 人工決策、簽核及歷史輸入；不由程式自動偽造 |
| [`data/`](../data/) | 不可覆寫的原始來源及文件快照 |
| [`db/migrations/`](../db/migrations/) | SQLite schema 版本 |
| [`reproducibility/`](../reproducibility/) | 歷史 Census/工作包重建；保留原始結果與路徑 |
| [`docs/audits/`](audits/) · [`outputs/`](../outputs/) | 歷史審查、證據表、可編輯及再生輸出；不是正式核准母體 |
| [`R/`](../R/) | 舊版 MCDA 程式；正式排名需 C1 資料、Panel、權重與 GIS Gate 全部通過 |
| [`tests/`](../tests/) · [`.github/workflows/`](../.github/workflows/) | 程式與回歸驗證；CI 綠燈不等於科學證據核准 |

目前有**三種用途不同的既有執行入口**，不可混稱已整合的端到端管線：

- `scripts/run_research_pipeline.py`：C0/C1 來源審查檢查與 P2–P4 新證據事件路由；不自動執行正式 R-MCDA。
- `python -m au_ree`：既有五階段 Python/SQLite/GIS/R export，可進行離線歷史重現。
- `reproducibility/rebuild_all.py`：指定來源快照的歷史重建，不應被改寫成新資料的自動核准流程。

新程式先確認能否整合上述既有能力，避免再增加重疊入口；歷史腳本未驗證相依性前不搬移或刪除。

## 來源與舊紀錄去哪裡找

- **截止日來源及身分資訊**：[487 Census Release](../CENSUS_RELEASE.md)、[2026-10-29 來源快照](../data/source_snapshots/)、[來源清單](source_inventory.csv)。
- **現有 C1 Gate 審查**：[39 群組預審](audits/2026-11-01_c1_first_pass_gate_39.csv)、[7 案來源複查](audits/2026-11-01_c1_stage1_source_review.md)、[人工 Gate 簽核輸入](../inputs/review_decisions/c1_c2_project_gate_signoffs_v1.csv)。
- **全部歷史審查批次**：[docs/audits](audits/)；含 487、339、272、156、109、70、73、48 等不同用途與分母的 CSV、JSON 和報告。不能把批次筆數加總為獨立 Project 數量。
- **過去的研究導覽與發布說明**：[先前完整 README](archive/README_pre_mainline_2026-11-01.md)、[歷史發布輸出索引](../outputs/README.md)。
- **歷史研究文件**：[docs/archive](archive/)、[研究決策](RESEARCH_DECISIONS.md)、[Change Log](CHANGELOG.md)。

**Active / Legacy / Generated / Archive 依功能與版本辨識，不以檔名新舊或存放位置自行認定為核准資料。** 請優先修改現有主線檔案；來源快照、穩定 ID 與可追溯審查紀錄不得因整理而被覆寫。
