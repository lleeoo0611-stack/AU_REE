# Census and Entity Resolution acceptance — 2026-11-01

Execution ID: `CENSUS-ENTITY-20261101`. Source cutoff: `2026-10-29`.
Base: `839944ecc003d5e3e3c590441e1b95c94349ed35`, repository `lleeoo0611-stack/AU_REE`.
Local checkout: `C:\Users\whatt\.codex\.chatgpt-projects\g-p-6a74fa8105f88191b580dee7d5f22fdd\worktrees\AU_REE-census-20261101`.

**Technical reconstruction PASS; complete independent Project/evidence acceptance remains PARTIAL.** Tests and checksums do not resolve missing Project identity documents or supply independent signatures. No original source, historic target ID or approval ledger was changed.

## Verified implementation and database

- 262 regression tests passed on Windows / Python 3.13. Tests include stable Project IDs, same-batch parent-before-child resolution, revoked approvals/originals, wrong entity levels, source ingestion rollback and invalid Census crosswalks.
- GitHub PR #66, implementation commit `7c14f32e74b26d975945c8268d114a70073f5deb`: **18/18 checks passed**, including Python 3.11/3.13, evidence regression, documentary closeout and R synthetic smoke. Documentation-only updates after this commit do not add independent source approvals.
- Fixed Windows SQLite file locks by closing stage connections after transaction completion, including backups, failure paths and status checks. Fixed local GIS archive path separators without changing scientific criteria.
- Added optional `csv-build --review-dir`: joins the existing 487-source Census and current Structural Round 01 review in one database. Checks exactly the same 39 stable candidate IDs, Project names, states, cutoff, and all attached group references. Documentary CSV cannot declare an independently approved ID. A failed attachment cannot replace an existing release.
- Actual integrated build: **51 CSV tables / 15,018 data rows**, plus **2 metadata tables / 58 rows**. Census has **487 targets**, **451 source entities**, **36 repeated targets on the same native entity**, **78 linked targets**, **409 unresolved targets**, **39 candidate groups**, **195 documentary gate cells**. These are different entity levels.
- SHA-256 of local integrated database: `e3b062ff8d81d37c8236e7326506bd42488f399ec844278d00c78abd9885000d`.
- Captured immutable `CENSUS-ENTITY-20261101` snapshot and rebuilt it into a separate SQLite. Both original and restored databases passed schema, per-table row-count/logical-hash, integrity and foreign-key checks: **53 tables, 15,076 total rows, 0 FK violations**. SQLite file hashes need not match after logical restoration.
- Original five-stage offline replay completed, then reused all five stage checkpoints. Its **203 unverified legacy master records are separate from the 487-source review**, and no verified scores or rankings were admitted.

## Verified evidence and remaining dependencies

- `build_structural_round01.py --check --verify-originals` passed using the existing local archive: 36 available originals (13 PDF / 23 HTML), manifest SHA/size checks; source-specific 39-group review remained unchanged. This does not claim complete reading or independent approval of every technical report.
- `close_p234_evidence_status.py --check --verify-originals` passed with the existing local primary archive. All 339 fixed sources reproduce their distinct classifications. The final nine-target batch retains 8 archived-content targets and 1 web-only target. Its verification scope is specified by that script; unavailable originals remain unavailable.
- `review_p234_144_primary_scope.py --check --verify-originals` passed: 144 targets, 143 original-content-reviewed targets, 1 original-content access hold, 49 distinct reviewed documents; no changed approvals. `check_external_primary_batch03.py --check --verify-originals` also passed, reporting the frozen 167 native IDs, 16 reviewed / 151 pending. This native-only result is not a claim that every external PDF was available.
- **39/39 group identities remain independently unapproved; C1=0, C2=0.** Structural review retains 168 unresolved documentary gate cells (including 31 ID and 31 ROLE cells). Ten groups lack a Project-level source in the original government/legacy crosswalk; a Deposit cannot be relabelled to bypass this.
- Missing/undated Project scope, source-to-Project mapping, resource-basis conflicts, actual Project geometry and independent reviewer records remain in the existing `gap_priority_queue.csv`, `identity_crosswalk.csv` and `c2_identity_review.csv`. Exact reopen requirements remain visible in those tables.
- The work is **not** a claim that all Australian Projects are resolved or every original is available. Independent identity decisions must be supplied through the existing source-document and approval ledgers, with actual archived bytes, named reviewer and valid dates; no automatic signatures were introduced.

## 2026-11-01 後續 Census 來源層級複核（原基準不變）

最新 `outputs/project_entity_membership_487.csv` 重新依 entity type 交叉統計，409 個未連至 39 群組的 source targets，包含 **283 Deposit、95 Occurrence、21 SOURCE_PROJECT_RECORD、6 Prospect、4 Historical Record**。21 個「Source Project Record」仍是來源記錄類型，**不等於 21 個待核准新 Project**；當中多數是 Legacy 歷史名稱，沒有明確的當期獨立開發／REE 產品角色證據。原 487 個 target_id、78 候選群組連結、39 個群組及所有核准表不變。

**Wedderburn Project（VIC）是這 21 筆中具有更明確原始 Project 範圍線索的個案：**原 Legacy `LEGACY:4fb6883c-bded-5363-af78-6fbfef190048` 為尚未連結的 SOURCE_PROJECT_RECORD；GA `E1:C-8c2269b43a6f62bafcece0`（AIMR Wedderburn）與 `E1:C-e5cc6ec45406fff096981e`（Critical Deposits native 2259）均仍為個別 DEPOSIT 記錄、無已核准 Parent。WIM Resource 的 [2015-12-09 公告索引](https://wimresource.com.au/media/media-centre/announcements/)對應 [`RL 006195 – Overview & Details of Work Program` 原始 PDF](https://wp-wimresource-2023.s3.ap-southeast-2.amazonaws.com/media/2023/10/WEDDERBURNRL006195SUMMARYPROGRAMOFWORK.pdf)：PDF 實體 p1「Key Projects and Interests」將 Avonbank、Wedderburn、Bungalally **分別列為三個 HMS Project**；p2「About the Wedderburn HMS Project」稱 EL4912、約 93 km² 與申請 RL006195。**申請被受理不等於許可獲准／目前有效**，且 p2 同一段另有 `RL 001695` 與 `RL 006195` **編號不一致**，必須由 VIC 官方原生 licence ID/歷史核對。p3–4 計畫的 Scoping/PFS/DFS 年度進度不可作為已完成研究。現行 [WIM 專案頁](https://wimresource.com.au/project/)自稱 Wedderburn 2015 JORC HMS 223Mt @ 2.9% **THM**，不是可比較 REO/TREO 估值，也未證明 Wedderburn 獨立的商業 REE 回收計畫。

此筆已完成**公開原件文字與頁碼定位**，但本次未取得並保存新增 PDF 原始 bytes／SHA-256，亦未驗證官方 RL 當期有效性、REE 產品角色或正式 Project/Deposit 對應。因此 Wedderburn 仍在既有 Review Queue，**不增列第 40 個 Project、不得與 Avonbank／Bungalally 合併、亦不建立正式 Project–Deposit link 或 C1/C2 准入**。下一必要查核是封存該 2015 PDF、核對原生 RL/EL、確認 2026-10-29 截止日實際開發與 REE 產品角色，並以正式獨立審查決策處理三筆既有 source IDs。

### Wedderburn 與 Bungalally：2016 發行人原始資源表對照（2026-11-01 續查）

原 [WIM 2015-12-09 RL 006195 申請來源](https://wp-wimresource-2023.s3.ap-southeast-2.amazonaws.com/media/2023/10/WEDDERBURNRL006195SUMMARYPROGRAMOFWORK.pdf) 提供三個獨立 WIM HMS Project 名稱、Wedderburn `EL4912`、申請 `RL006195` 及正文 `RL001695` 矛盾。另取得 [WIM May 2016 Company Update](https://wp-wimresource-2023.s3.ap-southeast-2.amazonaws.com/media/2023/10/GENERALCOMPANYUPDATEMAY2016.pdf)（2016-05-13 發布索引）的公開 PDF 頁面文字：**Bungalally p10** 同時有正文 207 Mt 與 **Table 3 的 Inferred 205 Mt @ 2.7% THM（1% THM cutoff，monazite 1.4% of THM）**；**Wedderburn p11 Table 4** 列 **223 Mt @ 2.9% THM，monazite 1.8% of THM**。2016 表格清楚區分 WIM 的 Avonbank、Wedderburn、Bungalally 資源範圍，但沒有直接可比的 TREO 原位品位。Avonbank **pp3–4** 的 2016 Scoping 結果與歷史 `6,000 t/year REE concentrate` 設想，也不可覆蓋後續 BFS／DFS 版本。

本次新增的是有頁碼的 issuer original **公開文字定位**，未取得受控原始 PDF bytes／SHA，故僅更新現有 **Bungalally／Avonbank** Review Queue 缺口與來源範圍；**Wedderburn 原 Legacy／GA 三筆 source target_id 仍無正式 Parent join、未新增第 40 個 Project**。Bungalally 的 205／207 Mt 仍需 2015 Optiro CP 完整 MRE 或更正公告才能裁決；Monazite/THM 無法換算為 TREO；正式 487 Census、39 群組、C1/C2=0、獨立核准 0 均保留。

### 2026-11-01 身分證據獨立複查：地方政府委託的 2026 西北維州礦業名冊

在已凍結 2026-10-29 Census 的既有 39 群組／409 未連結來源中，另定位由 9 個維州地方議會委託、Urban Enterprise 編寫、正式 **2026-02-16** 發布的 [Resource Ready: North-Western Victoria Energy & Mining Impact and Readiness Strategy（Appendix B, printed pp. 89–90, Table 25）](https://www.yarriambiack.vic.gov.au/files/sharedassets/public/v/1/documents/your-council/council-agendas/2026/25-march-2026/15.5-resource-ready-north-western-victoria-energy-and-mining-impact-and-readiness-strategy.pdf)。表中分別列出 `M5 Bungalally Project`（WIM Resource、Horsham、Exploration Phase）、`M6 Avonbank Project`（WIM Resource、EES Received Acceptable Minister's Assessment, Not operational）及 **`M18 Wedderburn Project`**（WIM Resource、Wychitella North／Loddon、Exploration Phase）。這提供第三方具名 Project／開發主體／地理範圍的**歷史交叉佐證**，支持三者應保持獨立名稱與開發單位；無法直接判斷為三個合格稀土開採 Project。

**來源分級限制**：Appendix B p89 的 Stage Definitions 說明 `Exploration Phase` 廣泛包含早期 Scoping／Preliminary Feasibility 等活動；Table 25 註明原始資料由 Urban Enterprise **2025 年**自政府、公司及 Council 相關管道彙整。該文件不是 Victorian Mining Register 的法律礦權決策，也不是 JORC／REE 產品原件、官方 GIS polygon 或 2026-10-29 FID 狀態證明。此次有可定位網路原件，但尚未本地封存獨立 SHA；不更改現存已核准 Project 數、ROW ID 或來源 lineage。

因此，Wedderburn 的 `LEGACY:4fb6883c-bded-5363-af78-6fbfef190048`、`E1:C-8c2269b43a6f62bafcece0`、`E1:C-e5cc6ec45406fff096981e` 保持 **HOLD／不推定 Project–Deposit JOIN**；不把表中 M18 當成新官方原生 ID，不將其誤作第 40 個獨立 REE Project。現有 Bungalally 和 Avonbank 的 Stage Evidence 亦保持既有截止日前審查結果。下一步仍須官方有效 RL006195／EL4912 紀錄與 2015 Optiro 資源原件、2016/2026 REE 產品差異，及每一候選的獨立人工決策。

## Reproduce

```bash
python -m pytest tests -q
python scripts/run_research_pipeline.py --profile all --mode check
python scripts/build_structural_round01.py --check --verify-originals
python scripts/close_p234_evidence_status.py --check --verify-originals
python reproducibility/build_census_database.py csv-build --csv-dir outputs --review-dir docs/audits/structural_round01 --output work/census_with_identity.sqlite --as-of-date 2026-10-29
python reproducibility/build_census_database.py capture --source-db work/census_with_identity.sqlite --snapshot-root work/snapshots --snapshot-id CENSUS-ENTITY-20261101 --as-of-date 2026-10-29
python reproducibility/build_census_database.py rebuild --snapshot-dir work/snapshots/CENSUS-ENTITY-20261101 --output work/restored.sqlite
python reproducibility/build_census_database.py verify --snapshot-dir work/snapshots/CENSUS-ENTITY-20261101 --database work/restored.sqlite
```

Local outputs and manifests are under `work/census_acceptance/`, including test XML, source/restore verification JSON, integrated SQLite and immutable snapshot. Full third-party originals remain local. Git attributes preserve committed file bytes on Windows so source hashes are not changed by checkout line-ending conversion.
