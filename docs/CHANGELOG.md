# Change log

## 2026-11-01 — Evidence-approved confirmation of existing stable Legacy Project IDs

- 既有 `apply_identity_decisions` 增加明確 `CONFIRM_LEGACY_PROJECT` 核准動作，允許經原件 SHA256、發表／審查日期、Project 範圍與獨立 `approval_ref` 確認的歷史 Project **沿用既有 Stable Project ID**。不必另建重複同名 Project；`legacy_id_map`、原始 Legacy Record 及事件審查紀錄均保留。
- 僅接受 Project 層級的來源候選，以及有 Legacy 映射、相同正式名稱／州別、目前仍屬未核准或已過期且核准者一致的 Master。Deposit／Occurrence 不可直接升格；試圖改用另一 Project ID 或遭其他候選占用時拒絕。
- `independently_approved_project` 現亦驗證已完成上述確認且原始文件仍有效的 Legacy Project；撤銷證據時保留 ID 但取消正式分析資格。增加 synthetic Project/Deposit/撤銷/重建與衝突負向測試。**真實 Census 仍無任何人工批准；本次不代替獨立簽核。**

## 2026-11-01 — Atomic government-source ingestion and frozen-source provenance

- 修正 `src/au_ree/stages/population.py` 在單一官方 CSV/ArcGIS Source 第 N 筆發生例外時仍留下前面 Project／Deposit 候選、地質實體或來源雜湊的問題：逐來源採 SQLite SAVEPOINT，全部匯入成功後才發布該來源資料與計數；出錯則還原本次來源寫入並留下明確失敗紀錄。
- 同一 `source_key` 與 Census 資料截止日已存在且已有凍結 SHA-256 時，若原始來源 bytes/hash 或 URL 在重新執行時不同，必須人工確認新的來源版本；不得直接覆寫 `source_registry.raw_sha256` 或舊 Project/Deposit 身分。存取遺失時保留上一版實際來源筆數，避免標示為 0 筆而無聲抹去來源。
- 在既有 `tests/test_official_census.py` 使用合成來源故障注入驗證部分匯入回復、同截止日 SHA 變動及 URL 變動；不更動既有 487/451/39 census、正式核准或 MCDA。

## 2026-11-01 — Source-level cutoff and Project scope verification for technical evidence

- 修復既有 `scripts/build_structural_round01.py` 文件證據檢查：資源敘述（含 JORC 與 REO）、經驗證的開發研究事件與原始文件缺口處置皆須指向**同一受審 Project group** 的原件；禁止跨 Project 移用證據。
- `same_scope_REO_evidence` 和 `study_original_verified` 除需具原始來源封存與 2026-10-29 之前的發表日期，現在也要求敘述上的 `publication_date` 與 `structural_round01_access_manifest.json` 來源實際發表日期一致，阻止把 2026-10-30 公告或較晚報告標成較早的 resource/study。
- 核對現有 39 個群組的 **25 筆已註記同範圍 REO 資源行、8 筆已驗證研究事件、24 筆缺口處置**，目前無跨群組或日期不一致。直接更新既有 `tests/test_structural_round01.py` 的 5 個負向案例；不改原始 487 Target ID、39 候選 Project、批准欄位或 MCDA。
- 同步於既有 Structural 證據報告補回原先 404 的 `R01-WI-AR25` 對應 Iluka 官方 2025 Annual Report 正式 URL（2026-02-18 發布，PDF 實體 p23／印刷 p21 Wimmera 段落）。官方文件顯示該發表時點 DFS／EES 仍在進行；尚未在受控 archive 保存可重驗的 PDF bytes/hash，因此原 access status 與正式核准均不變。

## 2026-11-01 — No refetch into incomplete frozen ArcGIS snapshots

- 修補現有 `src/au_ree/source_adapters.py load_arcgis()` 已封存來源的完整性缺口：重建時先以原封存 `manifest.json` 驗證 metadata、Object ID 清單及每個原始 chunk 的 SHA-256，缺失或不同即拒絕，且檢查發生於任何新網路請求或原件寫入前；拒絕從同日不同版本政府 API 回應拼接歷史快照。
- 原生 Object ID 列表若重複，不能先 `set()` 靜默去重；以明確錯誤保留來源異常供審查。
- 既有 `tests/test_official_census.py` 新增 cache chunk／metadata 遺失時不重新抓取及重複 ID 的負向測試，既有內容 SHA 不符的測試改用更嚴格的早期檢查預期。未更動來源 cutoff、任何 Target ID／Project 審查表及 C1/C2。

## 2026-11-01 — Government ArcGIS feature snapshot replay integrity

- 修正 `src/au_ree/source_adapters.py`：同一來源 query 的 ArcGIS raw `manifest.json` 第一次成功寫入後不可在重跑時自動覆寫。重新計算 source metadata、ID 和每個 feature chunk SHA-256，與已封存 manifest 不一致即回報來源變動並拒絕重建。
- 在 `tests/test_official_census.py` 新增相同 OID 下原始 feature 屬性遭改動、metadata 遭修改的離線重建反例；要求舊 manifest 完全保留。屬 2026-10-29 Census 原始來源位元組保護，尚未核准 Project 身分或正式 MCDA。

## 2026-11-01 — Project identity release gate linked to independent original evidence

- `src/au_ree/identity_policy.py` 新增既有 SQLite 身分資料的核查函式，要求 source Project candidate、有效 `identity_review_decisions`、`EVIDENCE_BACKED_PROJECT` Master、穩定對應 ID 及獨立核准原件 bytes 全部吻合。
- `src/au_ree/stages/population.py` 不再讓僅取得 `project_reviews.csv` 技術／座標批准、仍屬 `LEGACY_UNVERIFIED` 的 Project 獲得 `RESEARCHER_VERIFIED` 細項與位置。舊資料庫研究准入的 `src/au_ree/stages/eligibility.py` 也增加 `G2_PROJECT_IDENTITY_NOT_INDEPENDENTLY_APPROVED` 阻擋條件，避免原始 Source/Project 未核准時意外釋出 Ranking Dataset。
- Synthetic v1 GIS/eligibility 測試須建立有效獨立 Project 身分審查，再分別測試 GIS/JORC；並加入撤銷身分、原始 PDF/HTML 位元組遺失、只有技術批准而無身分批准的負向案例。未變動任何真實 C1/C2 簽核、研究母體或準則權重。

## 2026-11-01 — Source-original leads for unresolved Goschen/Bungalally statements

- 在既有 `docs/audits/structural_round01/REPORT.md` 記錄 Goschen Central 2024-12-03 ACDC ASX JORC PDF 兩個替代原件連結，以及 620Mt@1% HM、190Mt@2% HM、584ppm in-situ TREO 對應表與尚未釐清的 2025 Scoping 表題差異。
- 補入 WIM 2016 Company Update 中 Bungalally 205Mt @ 2.7% THM 原始公司佐證，保留現行網站 207Mt 的未勘誤衝突。
- 原件仍須由既有封存機制取得、保存 SHA256 與完成 JORC／scope 審核；未產生核准、更改 `R01-GC-MRE` 或改動 39 個候選群組的正式 Gate。沒有建立新 CSV／腳本／平行 workflow。

## 2026-11-01 — Independent approved Project parent and current-byte evidence gate

- `apply_identity_decisions` 先處理有獨立核准原件的 **Project parent**，再處理依其建立的 Deposit/Prospect/Occurrence 子實體連結；不讓 `candidate_id` 字典排序決定合法父子關係是否建立。
- 無法再以僅有歷史名稱的 `LEGACY_UNVERIFIED` 或失效的 Project Master 當成已核准 parent。原生 Deposit／Occurrence 不能透過 `APPROVE_NEW_PROJECT` 直接產生獨立 Project；缺少 geological entity source 或核准 parent 變更時保持 review pending。重複 Candidate 審查紀錄在資料庫修改前拒絕。
- 使用既有 `evidence.verify` 直接重新檢查 `inputs/evidence` 原始檔 bytes/sha256，避免核准登記表載入後原件被改動、刪除而沿用舊的核准狀態。Scheme A 的 Project、Observation 及 GIS stage 都傳入實際研究根目錄。
- 新增 synthetic regression：未經身分核准的 Legacy parent、Deposit→Project 誤升格、Project 先於 child 核准的重建順序、歷史 parent 轉移、重複核准行、source bytes 在載入後遭修改或遺失。以上不產生任何真實候選的核准，不改動歷史 487 source rows 或正式 C1/C2。

## 2026-11-01 — SQLite Census publication rollback on second-file failure

- 完成既有 CSV→SQLite 重建安全性修復：資料庫與來源清單為兩個不同檔案，正式寫入前保存原有版本；若 `os.replace` 發布其中一項時發生一般 I/O 錯誤，回復上一版 SQLite 與 manifest，不留下混合版本。
- `tests/test_p0_487_batch.py` 模擬第二個檔案發佈失敗，驗證舊資料庫 bytes 與來源清單完全未變。跨兩檔的突然斷電仍無法宣稱原子性，使用者讀取資料庫時仍應比對 manifest 內的 database SHA-256。
- 未修改原始 487 筆來源、Source ID、Project ID、審查決策或任何研究母體定義。

## 2026-11-01 — Project–source lineage of Structural evidence reviews

- 現有 `scripts/build_structural_round01.py` 在 39 群組技術／來源證據衍生流程前，核對固定 2026-10-29 Census 的 487 筆 `target_id`、39 個候選 Project ID、原始群組名稱、州別與每個 Project 實際所屬來源關係。若證據審查群組沒有來源 parent，或 Project–Deposit source link 指向錯誤群組／州別，拒絕執行。
- 既有 `tests/test_structural_round01.py` 增加對 78 筆 linked／409 筆 unlinked 的實際回歸，以及未知 Project parent／無來源 Project group 的負面測試。屬 Census lineage 結構驗證；不將 39 個審查群組或 source group link 升格為正式批准 Project。

## 2026-11-01 — Census candidate-parent identity crosswalk safety

- 強化既有 `reproducibility/build_census_database.py`：487 筆 CSV→SQLite 重建時，核對每一個 `INCLUDE_CANDIDATE` 的原始 `candidate_group_key` 與 `project_entity_register` 的已審查群組名稱及 `PROJECT_LINK_REVIEWED_CANDIDATE` 關係一致；HOLD 來源不能藉由連到候選群組而繼承納入狀態。Mary Kathleen tailings 原本 2 個保留未決 group-link 名稱差異仍保持 HOLD，不強制合併。
- 在原 `tests/test_p0_487_batch.py` 加入錯誤 parent group 及 HOLD→Candidate relation 的拒絕測試。這是資料跨表一致性驗收，不代表 Project 已獨立核准或可進入 C1。

## 2026-11-01 — Census CSV→SQLite overwrite integrity

- 現有 `reproducibility/build_census_database.py csv-build` 改為在同目錄暫存建構、執行跨表與 SQLite 驗證，再以 `os.replace` 發布完整資料庫及 manifest；資料輸入、SQL、完整性或雜湊檢查失敗時不刪除上一版 SQLite／manifest。
- 在 `tests/test_p0_487_batch.py` 增加失敗注入、完整成功覆寫與原檔保留測試，沿用同一組 487 筆正式來源的既有整合驗證。此為可重現性與資料庫安全性修正，不代表 Project 身分、JORC 或 C1/C2 已核准。
- 修復既有 `scripts/acquire_structural_round01.py` 的證據快取驗證：同一 source ID 的 URL／日期／格式／審查範圍必須不變；標記已有原件但 PDF/HTML bytes 遺失、雜湊或尺寸不符、或僅剩無 manifest 的位元組時一律拒絕沿用，不覆寫舊檔。原件遺失必須補回相同 SHA，來源契約改變則建立新 source ID。增加 synthetic cache 負向測試。

## 2026-11-01 — Execution Round 01: Structural Cohort documentary review

- Extend existing PR #49/#50 mainline rather than create a second pipeline. New `build_structural_round01.py` runs after existing Stage1 in `c1`/`all`; online curated acquisition is explicit and cached, outside offline supervisor.
- Bounded classification of all 39 original groups: 9 technical-original page reviews, 17 primary-HTML scope reviews, 13 inherited reviews with explicit access limits. Preserve 13 P1 source cases separately and all formal signoff ledgers unchanged.
- Archive 13 PDFs and 23 HTML responses locally (36 unique SHA-256 hashes); public manifest records 53 source locators, including 17 unavailable. Resolve 24 individually named documentary gaps; 27 of 195 documentary gate cells ready for independent review. No fabricated PASS, signatures, Project approvals or MCDA.
- Acquire dated DFS/Scoping/PFS/BFS originals for Browns Range, Jupiter, Dubbo, Goschen Central, WIM100, Sandy Mitchell, Donald and historical Charley Creek; Koppamurra remains original presentation, Copi remains contractor corroboration, Bungalally remains stage-only.
- Locate WIM100 and Donald REO-in-HM category tables; preserve Dubbo Y-exclusion, Goschen Central table year/cutoff conflict, Bungalally 205/207Mt conflict, MzEq-versus-REO and resource-versus-reserve distinctions. No automatic resource normalization.
- Publish crosswalk, 195-cell gate table, resource register, study timeline, structural candidates, C2 queue, P1 case proposals, criterion coverage, priority queue and source-gap resolutions under `docs/audits/structural_round01/`. Jupiter is documentary packet ready only; official GIS release and formal Structural/C1/C2 admissions remain zero. Panels unselected.
- 11 new evidence tests plus 18 related regression/integration tests passed locally; dedicated offline CI added. Full evidence/limitations and next original-document priorities are in `docs/audits/structural_round01/REPORT.md`.

## 2026-11-01 — Census Project ID replay and evidence-decision safety

- 修正已核准新 Project 在乾淨 SQLite 重建時依 `max(project_id)+1` 分配編號、可能因新候選插入導致舊 ID 改變的問題；未明確指定 ID 時以穩定 source candidate ID 決定數字編號，明確指定及已核准的既有 Project ID 保留。
- 身分核准原始來源須通過獨立文件驗證及有效 ISO 日期；尚未核准的輸入不再預先釘選 resolved_project_id；嘗試修改歷史已核准 ID 會保留原 ID 並標記待更正。
- 於現有 Scheme A 測試新增跨新候選重建、無效簽核污染、歷史 ID 變更與無效日期的回歸案例；僅使用 synthetic evidence fixture，不改動 487 原始資料、C1/C2 簽核、JORC/GIS/MCDA。正式 Census 科學驗證與 Project 身分核准仍未完成。
- 強化既有 `reproducibility/build_census_database.py`：CSV→SQLite 寫入前，對 487 筆來源、納入 Gate、Source Entity、Project membership 及候選 Project group 進行跨表完整性檢查；若 target ID、entity ID 或關係錯位，拒絕重建並保留舊資料庫。歷史 487 targets 對應 **451 個不同原生來源實體**；36 組 Legacy/E1 重複指向相同原生 source key/native ID 且層級、名稱與 Project 關係一致，應保留雙方 target ID，不得當成 36 個新實體或誤判 SQLite 損毀。新增正向與破壞關係的負向測試；此 QA 為結構驗證，不代表身分或 JORC 的獨立科學核准。

## 2026-11-01 — Mainline supervisor, README diagrams, C1 Stage-1 and source-triggered P234 evidence (PR pending)

- Replaced sprawling root README with a concise current-project guide, **editable Mermaid research architecture and mother/child pipeline diagrams**; archived entire previous README under `docs/archive/README_pre_mainline_2026-11-01.md` to retain historical case/PR links.
- Reviewed actual repository structure across `src/au_ree/`, `scripts/`, `config/`, `inputs/`, `data/`, `reproducibility/`, `db/`, `R/`, `outputs/`, `tests/` and `.github/workflows/`; see `docs/DATA_STRUCTURE_AND_PIPELINE.md`.
- New parent `scripts/run_research_pipeline.py` dispatches `build_c0_freeze_c1_c2_v1.py`, `review_c1_stage1_v1.py`, and **only on genuinely submitted new evidence events**, `route_p234_new_evidence_v1.py`. Legacy five-stage CLI is explicit only; no live crawler and no automatic R/MCDA main ranking.
- Added seven detailed issuer/government original-public-text **C1 Stage 1 Project reviews** (Browns Range, Bungalally, Copi, Dubbo, Goschen Central, Jupiter, Wimmera) with dated studies vs merely being at Scoping Stage, resource basis, footprint and missing approvals preserved; overlay 39 candidates, 7 new documentary checks, **C1=0 and C2=0 signed**.
- P2–P4 new event CSV and independent source review ledger start empty; event router enforces frozen target IDs, exact native key, new report locator, published-as-of separation, duplicate rejection and SHA if original PDF bytes are claimed. Source routing remains a **side branch triggered by PR/event**, no repeated old URL crawl. Zero new event trigger presently.
- Dedicated CI for master supervisor and evidence events; tests validate replay/negative cases, C1 six-Gate release invariants. Snapshot 2026-10-29 and 487 baseline unchanged. No original PDF bytes or human approvals invented.


## Research P0 policy acceptance — C0 F1/F2 and strict C1/C2 cohort (2026-10-31)

- User accepted two-tier C0 source freeze policy (bounded F1 source-scope closeout, F2 native-feature search pause with documented negative query and reopening); **no source frozen automatically**. Source audit 339 rows: 119 F1 approval candidates, 151 F2 precheck (6 existing locator leads cannot directly pause), the other 69 stay in evidence/identity/access review.
- Add gate-ready **39 candidate Project group** rows (7 pre-FID Study screen; 8 dated stage check; 14 exploration/resource; 7 REE-role hold; 2 beyond pre-FID; 1 inactive) and **13 P1 positive source-case records** as a separate overlap-unverified queue; never count 52 unique Projects.
- C1 requires independent ID/ROLE/WINDOW/JORC/PANEL/GIS_RELEASE; C2 requires independently signed Project ID and REE role, and must not mix with main C1 ranking. 28 Project groups are C2 identity **review candidates**, zero approved C1/C2. Existing 12- and 9-criterion panels not auto selected.
- Add accepted config, decision inputs with no fake signatures, deterministic Python builder/checker, regression tests, GitHub Actions workflow, README and method documents. Preserve all 2026-10-29 immutable snapshots and v1 legacy analysis.


## P2–P4 B06 reason classification and source-scope consistency — 2026-10-31

- After merging #45 → #46 → #47 into main, join all frozen 339 P2–P4 source IDs with **4 newly examined P2 public-primary references** (Arthur Popes, Blueys/Blues Folley, Bells Monazite, Elaine Dorothy). Preserve snapshot and original baseline statuses; public source text is not a PDF SHA/fulltext signoff.
- Reconcile P2 Elaine Dorothy legacy description with existing two P3 historical-2010 **JORC Inferred REO 83,000 t @ 3,200 ppm TREO, 200 ppm U₃O₈ cutoff**; the parent remains historical and does not qualify C1 without REE study, same dated source/title and GIS. Identify Wolfram Hill Bell's Monazite as **different geography** from Bynoe's Bells Mona Sn-Ta pegmatite.
- Save eight related official locator rows (Edwards Creek vs Edwards Creek South; Legacy Pyramid vs Pyramid Lake gypsum; P4 Spartacus, North Bleechmore Dykes and Skyfall reports) without promoting exact government native feature joins.
- Build mutually exclusive **8-class evidence root-cause** and **7-class operational blocker** views over 339 source rows. Source-priority followups **159** = 8 P2 + 87 P3 + 64 P4; P3/P4 still 100 native workgroups, 119 proposed unsigned C0 closures; C1/JORC/MCDA 0.
- Add rebuild/check Python, regression tests and targeted PR workflow, README and a proposed research evidence-resolution note. No historical raw snapshot, user-unapproved source freeze or independent approval changed.


## P2–P4 B05 native-ID crosswalk / source-scope freeze proposal — 2026-10-31

- Deterministically join all frozen **339 P2–P4 source IDs** to Batch 04 and four new public-primary P2 reviews (Duke, Bruce Prospect, Plenty River, Brumby/Clydesdale). Separate prospect-level TREO drill assays from same-scope JORC REO resource and Stage 1 industrial-mineral economic study from unacquired Stage 2 REE claims.
- Reduce **151 P3/P4 source rows** to **100 shared native-ID search groups** (51 two-row groups; 30 shared source-key variants; zero name/ >1 km coordinate conflicts) **without merging any source IDs or Projects**. Two P4 Skyfall rows have new official GEMIS report locator only; native-ID spatial crosswalk remains HOLD.
- Publish 339 mutually exclusive source-review depth classes, 112 work units (12 P2 + 100 native groups), and **119 human-review source-scope closure candidates**. Source-review freeze F1/F2/F3 is **PROPOSED**, not enacted; zero C1, JORC, independent signatures, original PDF bytes or MCDA score changes.
- Add zero-network standard-library rebuild/check script, regression suite, PR workflow and README + decision proposal; maintain all prior raw snapshots and overlays immutable.


## P2/P3/P4 all-source continuation Batch 04 — 2026-10-31 (stacked after unmerged Batch 03)

- Deterministically reconcile **339 immutable P2–P4 source IDs** into an additive editable current-status overlay without replacing historical 339 or Batch03 167-row snapshots.
- Perform nine new authoritative **P2 source-scope/public-summary** checks: Boulder Ridge, Port Pirie REE, Anchor Tin Deeps, Blue Tier, Cruncher, DC Target, Tunnel Hill, Douglas Project and Wedderburn Project. Distinguish historic tailings/THM/Sn and prospect/sample REE from JORC TREO.
- Log eight P3/P4 exact-locator searches, including mismatched MINOS 11182 versus 11910 and generic Gascoyne region, without marking them as technical fulltexts. Pending original follow-ups: P2 16, P3 87, P4 64.
- Add offline ID/row cardinality, no-fabricated-PDF and no-approval validators and one regression test; README index updates. Independent CI and original-document/full technical verification remain separate.


## External primary evidence Batch 02 and 167-row progress — 2026-10-31

- Add five fixed native-source substantive scope reviews: Pindari pair (2011 Archer drill report vs released SARIG annual-report synopsis, historical anomalism versus later cuttings not conflated); Acropolis pair (official SARIG deposit 3018 Cu major/REE minor and 2019 hematite-associated REE whole-rock research); and the generic Murray Basin source (government basin scope versus distinct WIM, Donald and Goschen projects; HM ≠ TREO).
- Publish additive, editable 167-row progress CSV joining both batches by exact fixed IDs: 10 public-text technical scope reviews and 157 primary-original follow-ups. Keep originals byte/SHA unknown, independent approvals negative; previous frozen 339 and P2 28/27-case tracker unchanged.
- Add deterministic progression checks, regression tests, CI workflow, report, README and research decision note. C1, 13-case Gate and MCDA remain paused.

## External technical originals Batch 01 — 2026-10-31

- Add nine immutable-ID, source-level substantive overlays (five native, three P2, one Scaddan): Havilah Johnson Dam elemental Nd intercept, Archer Ketchowla K2 Mn/Co tables vs uncorroborated native REE peak, Reedy Lagoon Victory REE+Y historical grab sample, Queensland Mary Kathleen historical-mine vs tailings separation, and Scaddan 2024/2025 seller mineral-host contradiction.
- Reconcile all 28 P2 baseline IDs / 27 cases against the unchanged 339 record ledger; only three new government HTML scope rechecks, explicitly leave 25 technical-original fulltexts open. Keep 162 native originals and Scaddan PDF byte archive outstanding. No invented source PDF hashes, no visual/fulltext claims, no Project/C1/admission changes.
- Add editable evidence CSV and 28-source tracker, a standard-library cardinality/approval/status validator, regression tests and dedicated PR CI. Original documents are referenced via URLs and text locators; offline original-byte verification requires a separate later acquisition.

## P2/P3/P4 final evidence classification and nine retrieval follow-ups — 2026-10-31

- Recover five targets' nominated originals (Yellowband Plain, Stronach, Yellowband Creek, Naracoopa, Rubble Flats) and direct official replacement originals for Quantum (two IDs) and Mindarie. Read relevant pages/sections, distinguish mineral composition from ore TREO, offshore/onshore boundaries, bauxite analogues and historical intercepts from MREs.
- Preserve Scaddan as cached extracted text with original-byte access HOLD; public DNS/Internet Archive observations and failed attempts remain reproducible. Four nominated-pointer physical-access residuals remain distinct from eight targets with newly archived primary content. No invented byte hashes or complete-fulltext claims.
- Classify every fixed P2/P3/P4 source (339 rows, P2 27 provisional cases) into eight explicit evidence states with findings/gaps/reopen conditions. Keep 167 native-content-only and 28 inherited P2 desk reviews distinct. Add new editable CSV/JSON, original-review registry, deterministic script and 15 acceptance tests. Redact inherited URL credential parameters in two newly derived rows only; frozen snapshots, P1, approvals, 13-case Gate and MCDA unchanged/paused.

## 144 HOLD primary-document and scope review — 2026-10-31

- Review relevant original PDF/HTML content for 142 immutable targets, plus one web-rendered original PDF (Scaddan, no archived bytes); leave Yellowband Plain unread/access-blocked. Preserve seven alternative-original cases whose nominated pointers remain unrecovered, nine total access gaps, and all row-level scope/title reopen conditions.
- Recover exact GEMIS ORIGINAL bundles, CSIRO EP14184 and Wind Break EDGI; correct Kalkaroo West MINDEP 9629 versus 8455, prevent cross-project/state/resource-basis inheritance, and record 61 point comparisons without geography approval. Preserve P2 and all other 195 rows in the 339-source disposition overlay.
- Add editable CSV/JSON, acquisition manifests, reviewed-page hash/binding registry, local original verification, public offline ledger reproduction and adversarial tests. Keep restricted third-party full text local; CI does not claim absent-byte/full-text revalidation. C1, 13-case Gate and MCDA stay paused; zero approvals changed.

## P2/P3/P4 frozen-source documentary dispositions — 2026-10-31

- Preserve 412 immutable HOLD IDs (P1 73 untouched, P2 28/27 provisional cases, P3 216, P4 95). Inspect selected original government feature content for 317 targets and 22 Legacy-only rows; verify all 52 Legacy UUID rows, including 30 targets also linked to government records. Validate original archive manifests/chunk SHA during extraction.
- Retain full second-to-sixth-round/P2 evidence history, dates/locators, source attributes/geometry, exact-name review candidates, original tenure intersection limits and reopen conditions in editable CSV/JSON. Recover seven stale GA native-source statuses and preserve SA 3000/11849 as two native IDs with four/six features, without overwriting historical audits.
- Assign 167 P3/P4 records bounded C0 native-record dispositions; explicitly HOLD 144 external document pointers for primary-scope review (118 P3/26 P4). Inherit P2's 28 source-scoped desk judgments; four historical source rows represent three cases. This is not complete primary technical-document full-text verification. New full-text verifications and Project/C1 approvals: zero.
- Add standard-library raw extractor, immutable derived feature selection, input hashes, offline reproduction, adversarial identity/cardinality tests and CI. Raw extraction verifies original chunks; offline checks verify the derived selection only. C1 admission, 13-case Gate approvals and MCDA remain paused; existing approvals/configuration unchanged.


## P1/P2 publicly accessible evidence closing review — 2026-10-31

- Reassessed **P1 19 remaining cases / 31 immutable sources** on freely accessible government, issuer and secondary-index documents: 13 positive REE/Project leads (22 rows), 2 geographic identity conflicts (4), and 4 indexed WAMEX reports (5). New primary/context sources distinguish WA Wingellina Ni-Co from SA Claude Hills and Ambergate vs Witchcliffe name/tenement conflict; P1 C1 gates all remain HOLD.
- Official original PDFs for WAMEX A119194/A120393/A129842/A109188 remain unarchived; company-submitted page-text indexing yields bounded documentary claims but **does not supply original PDF SHA**. No email was sent.
- **P2 all 28 source rows / 27 provisional cases** assigned unique terminal scoped documentary review results and reopen conditions: 17 direct government/issuer leads still lacking approved Legacy source-to-Project identity, 1 REE stage outside issuer Scoping, 3 historic sites, 1 negative single drill target, 3 native features not Project proof, 2 regional index/name collisions. Factual report excerpts support Arthur Popes, Bell's Monazite, Blueys Folley, Duke, Blue Tier, Cruncher, DC, Tunnel Hill, Brumby Clydesdale and Wedderburn.
- Add editable source and case evidence inputs, reproducible 31+28 target CSV derivation, machine-readable QA, dedicated unit tests and CI. Preserve 412 original HOLD source IDs, 73 prior P1, untouched P3 216/P4 95, zero independent formal C1 or JORC/GIS approvals.
- Follow-up for inaccessible original archive (#30), P1 positive case signoffs (#32), and P2 source–Project/tenure checks (#35) remains open.


## P2 first-pass source triage within 412 HOLD — 2026-10-31

- Freeze historical denominator 412 = P1 73 + P2 28 + P3 216 + P4 95 (no re-ranking, no C1 admission).
- Audit all 28 P2 source IDs (22 Legacy / 6 E1) into 27 provisional source-site cases. Preserve a separate historical Mary Kathleen mine (two native deposit points) and Mary Kathleen tailings legacy research source.
- Curate government/issuer / native context: Mary Kathleen government remediation + 2026 Bayan bench testwork, Port Pirie SA SARIG #8908 treatment tailings, Tasmanian Anchor Tin Deeps 2024 EDGI REE drilling, Northern Territory Boulder Ridge and Bruce/Plenty River/Edwards Creek exploration, Elaine Dorothy historical REE, Douglas 2004–2012 historic Iluka HMS, P1 Talisker legacy cross-reference. VIC Bondi native feature prohibited from name-only joining Iluka Douglas Bondi mine.
- Current provenance: 11 documentary source-case leads pending same-scope identity, 12 Legacy names only, 3 VIC native features, 1 regional secondary index; all remain C0 without independent Project / JORC REO / GIS release / C1 approvals.
- Add `scripts/audit_p2_28_initial_triage.py`, dedicated `unittest`, CI workflow, evidence CSV, frozen source/case CSVs, snapshot JSON, report and index.
- P1 file-access (#30) and downstream C1 case approvals (#32) remain explicitly open. P2 subsequent research tracked in #35.
- Observed dedicated P2 phase-one, Python offline and R synthetic CI all successful on commit 787fa9f7 (GitHub Actions 41176845661, 41176845732, 41176841192); CI attestation saved under docs/audits.


## P0/P1 desk-search closeout, CI verified, C1 gate held — 2026-10-31

- Publish **73 immutable C0 source-terminal dispositions**: 22 positive Project/REE leads with 13 case-level six-gate reviews; 40 records without project-scoped REE product proof in the searched sources; 2 Benmara South exclusion from a different deposit's TREO resource; 4 native-source identity conflicts; 5 indexed WAMEX source rows requiring 4 government PDF originals.
- Wemen historical production now verified by Victorian government 2003/04 Statistical Review (issued April 2005): Wemen mineral sands mine ceased production in January 2004; prior 'catalogue-only' finding superseded.
- Preserve 204 official tenure source-title intersections, 60 source points with intersecting tenement layers, 20 exact documented title-number matches across 12 cases. No automatic project footprint or C1 promotion.
- Maintain explicit source/release separation: P1 source research closure does not approve project identity, current REE resource, GIS_RELEASE or criteria panel. All new C1 gates stay HOLD; `main` untouched.
- Original CI failure was due to GitHub account $0 Action budget blocking private-repository runners (confirmed in user-provided GitHub annotation and Billing screenshot). Switching repository to Public restored standard GitHub-hosted runners. Fixed two actual CI regressions: 48-parent Aileron resource-test expected two statements instead of four (two TREO 2025, two Nb2O5 2026), and two source-summary generator strings were out of sync with frozen provenance JSON. All four PRs now have passing actual P0/P1, Python and R workflows; record 14 successful workflow run IDs and commit heads in [CI verification attestation](audits/2026-10-31_p0_p1_ci_verification.json). PR #26→#27→#28 merged into main; PR #31 is the final closeout change. Primary WAMEX originals and formal C1 remain separate outstanding tasks #30/#32.
- Add standard-library closeout generator, unit tests and workflow, editable source CSV and JSON, final report and index.


## P0 P1: complete 73 target documentary audit and frozen 487 official-tenure reuse — 2026-10-31

- Audited all **73 P1 source IDs** into 44 distinct documented cases (25 proposed parents + 19 scope/index cases): 22 source rows with project/resource textual leads, 39 sources with only historical/geological/HM or non-REE product proof, 2 Benmara South scope exclusions, 4 sources with identity conflict, 5 indexed WAMEX report sources (four unique report IDs incl. Tutunup West A109188) lacking archived government PDF bytes, 1 catalogue-only source.
- Added 12 scoped resource claims (Y₂O₃ Korella version conflict, V₂O₅ Benmara South vs excluded Barkly TREO, Nowie THM, etc.) without modifying prior 14 resource entries.
- Reused **official polygon intersection inventory** from nationwide 487 targets: 73 P1 sources yield **204 official tenure intersection records**, 60 source rows with at least one tenure overlap, 11 with none in queried layers, 2 without verified official state layer. In 18 document-title cases, 20 source rows in 12 cases match documented tenement numbers.
- Distinguish tenement overlap from mining Project development footprints; flag Ambergate E70/4799 vs observed E70/4793, Jurien M70/436 within named M70/434–436, expired historic WAMEX titles and Wingellina SA cross-border.
- Reproducible standard-library Python, CSV and JSON source/tenure reconciliation, regression tests and README indexes. Formal Project/JORC/GIS Project footprint/C1 admissions remain 0.


## P0 P1: provisional 48-source / 25-parent identity and resource-basis review — 2026-10-31

- Freeze 48 named source candidates from prior 73-row P1 scope; publish 39 distinct state/name site keys and 25 pinned provisional parent review groups. Preserve all native target IDs, coordinates and source hashes; never create formal project_master IDs by name.
- Record project/deposit documentary scopes (Copi North, Tower, Mia, Yttria, Aileron Green/Emily/Crean, Redlings) and distinguish them from state/tenement polygon overlap (0 physically tested).
- Publish 14 resource claims: 10 historical TREO grade rows including nested cutoffs, reported totals and undated conflicting versions, 2 HM basis rows, and 2 April 2026 Aileron Nb₂O₅ MRE rows. Current niobium MRE 120Mt at 0.77% Nb₂O₅ supersedes prior niobium tonnage but does not imply current TREO grade; no cross-basis transfer. Record resource date, cutoff, reporting category and no-sum rule.
- Flag broad historical Willandra West/East source spreads and Fraser Range–Salazar adjacency. No new C1/JORC approvals.
- Add reproducible Python QA, regression tests, report and README index. Work continues in a stacked draft PR pending CI and official polygon evidence.


## P0 sixth-round source audit: 70 records with no supplemental document — 2026-10-31

- Audit all **70** frozen native source targets from the preceding 109-row source review, keeping project/deposit/occurrence and raw ID distinct; publish editable 70-row review, 59-row non-candidate parent queue, provenance SHA manifest and 25-name source document register.
- **34** targets gain external source/locator context (7 independently named historic Project/deposit candidate links; 4 indexed original-WAMEX government-held reports awaiting primary PDF; 8 Project/tenement/state scope holds; 15 only geological or non-REE primary commodity evidence). **36** still have no new independent external document.
- Explicit government and issuer evidence for Mt Clere/Tower, Tiwi/Puwanapi, historic VIC Ouyen/Galileo–Mercury–Titan, Jurien, WAMEX Hopelands East/Hassell Beach/Witchcliffe; separate HM/THM from TREO resources. No Project/JORC/C1 admission.
- Flag two `SA` Wingellina source rows west of 129°E as jurisdictional mismatch candidates; preserve existing source state pending official cadastral verification. Keep Benmara South historical EL6836 vs 2023 Barkly resource scope unresolved.
- Add `scripts/audit_p0_70_project_parents.py`, `tests/test_p0_70_project_parents.py`, and GitHub Actions snapshot regeneration. README, docs index, runbook, decision log and changelog updated; original 487/272/156/109 inventories and MCDA unchanged.


## P0 fifth round: audit 109 original-only source targets — 2026-10-31

- Verify **all 109 source targets** previously lacking independent Project parent text; preserve stable IDs, frozen original government source-feature location and SHA-256. Generate **109-row editable audit**, **89-row pending parent/identity queue** and statistics with input hashes.
- Curate 31 official/government/issuer/CSIRO documentary source names matched to **39 target rows**: **20 historical Project parent candidates**, 8 scope/tenement/name holds plus **2 Ambergate spatial conflicts**, and **9 independently documented geological or HMS deposits still lacking a Project parent**. **70** rows remain government-native-only; zero formal Project/JORC/C1 approvals.
- Check cross-source same-state names: **44** same-state-name source rows, **42** with comparable native coordinates, **38** with a source match ≤1km, and **2 Ambergate records 38.738km apart** quarantined as identity conflicts. Never infer unique Projects from matching names or coordinates alone.
- Publish reproducible standard-library `scripts/audit_p0_109_project_parents.py`, unit tests and auto-publishing GitHub Actions, plus 2014 CSIRO source scope (Twelve Mile/Prungle), ASX Yttria/Mia, WA EPA Happy Valley and issuer Governor Broome/Ambergate leads.
- Update README, docs index, runbook, research decisions and changelog without modifying C0/C1 primary source matrices, approved GIS, JORC or MCDA.


## P0 fourth-round audit of 156 Project-parent gaps — 2026-10-31

- Review **all 156** frozen native source IDs previously tagged `PROJECT_PARENT_UNLOCATED` using 2026-10-29 source-feature attributes, direct government records, typed deposit/prospect/occurrence status, REE commodity context and same-state duplicate-name relationships. Produce a **156-row editable CSV with per-row trace and source SHA**, a **148-row pending Project relation queue**, and a structured JSON provenance manifest.
- Add **11** government/issuer Project documentation leads: **8 named Project candidates**, **3 similar-name/scope holds**; the other **145** have no newly sourced named Project documentation. Cross-source same-state names occur in **70** source rows and cannot alone establish either Project membership or a JORC statement.
- Distinguish existing C0 geological records (including WA Prospect/Occurrence/Target/Infrastructure and TAS `RESOURCES=N`) from a true development Project. Keep all 156 Project boundary signoffs and C1 gates pending.
- Introduce standard-library reproducible `scripts/audit_p0_156_project_parents.py`, independent regression tests and auto-generating GitHub Actions workflow. No changes to the underlying 272/487 target snapshots, MCDA scoring, GIS or resource database.
- Update README, documents index, runbook, research decisions and changelog.


## P0 third round: 272 original-source entity / Project parent reconciliation — 2026-10-31

- Recovered and source-byte verified original GA AIMR JSON chunk, original SA critical REE CSV and 16 Legacy historical source rows; **23/23 previously missing native records** tied to physically archived original source bytes or original repo bytes.
- Independently rejoined **272/272** frozen 2026-10-29 source native features, retaining source key + native value + raw source feature locator and SHA (no auto Project or MCDA admission).
- Identified all **10 SA source feature rows** as two deposits Olympic Dam (4 rows) / Clarke (6 rows) with unique `source_key + MINDEP_NO + OBJECTID`. Not ten separate development projects.
- Added **13 source-target Project parent documentary leads** across seven different parent names (Redlings / Aileron / Coburn / Fraser Range / Glenaladale–Fingerboards / Copi / Korella); joined six existing prior reviewed relations. Final 272 queue: 15 REE-relevant document candidates, four non-REE project source rows, 92 non-project geological source entities, two parent deposit IDs, three VIC generic thematic labels, 156 unresolved parents.
- Original bytes stored under `data/raw_snapshots/2026-10-29/`, full 272 frozen native feature subset under `data/source_snapshots/`; evidence CSV, manifest and audit report under `docs/audits/`. All approval gates unchanged.
- Rebuild script + automated source artifact GitHub Actions + tests integrated; documentation index, README, runbook and research decisions revised.


## P0 original government source restoration and Project entity scope — 2026-10-31

- Retrieved October 29 raw-first government archive (GitHub Actions run 40821122179) and linked **all 272 previously native-only targets to a unique raw government feature**; retain 268 source records with no Project parent key and four with geological parent/group only as C0.
- Located the 23 prior missing source rows: 7 GA original JSON byte positions and 16 previously stored Legacy Census lines, with exact nonblank historical project_id UUIDs matching frozen Legacy target IDs.
- Identified Olympic Dam's 4 and Clarke's 6 source features by `MINERAL_DEPOSIT_NO + OBJECTID/FID`, preventing 10 duplicate observations from inflating the Project or Deposit count.
- Separated six cross-source Project parent candidates (Narraburra/Milo REE; Peculiar Knob/Carrapateena not documented as REE Projects); formal C1 still requires separate document and role approval.
- Added source raw SHA verifier, regression tests, four editable review CSV files, audit report and reproducibility summary; updated README, Runbook, decisions and file index.
- No changes to official C1/Resource/GIS approvals, v2 scoring or MCDA results.


## P0 487-record evidence source recovery (round 2) — 2026-10-31

- Re-audit all 487 preserved target IDs against 62 curated government, issuer and historical geological source leads; produce a **34-column editable evidence snapshot**, a separate **86-target before/after CSV** and provenance JSON.
- Reduce `NATIVE_RECORD_ONLY` **336→272** (64 additional cross-source leads) and `SOURCE_RECORD_NOT_RECOVERED` (no native/document locator) **23→3** (20 new external document locators). **All 23 native raw snapshots remain unrecovered**, kept explicitly separate from document discovery.
- Add official SA deposit evidence for Olympic Dam and Clarke; both **original multi-feature native ID ambiguities remain unresolved** (4 and 6 source rows) although they now have official references.
- Preserve all C0 source records and existing C1/Project/JORC/GIS approval gates. New reproducible standard-library script and regression tests prevent accidental promotion and historical-file overwrite.
- Update README, docs index, runbook, research decisions and changelog. No scoring or historical source modification.


## P0 source evidence review for all 487 records — 2026-10-31

- Audit all 487 Census targets at **claim/evidence depth**, distinguishing exact native source record, archived document text locator, URL without locator, ambiguous native match and unrecovered source; record evidence scope and next action without Project/JORC/GIS approval.
- Add `scripts/review_p0_487_evidence.py` and regression tests to reproduce a 487-row editable CSV and byte-level source SHA-256 run manifest.
- Extract 20 WA Government 2026-02 REE project/resource summary entries with 2026-01 staging and JORC aggregate grades: exact same-name crosswalk gives 13 government names / 20 Census source rows, including previously ungrouped advanced projects.
- Add NT 2023 Bruce Project → Plenty River prospect primary-source parent relation for review (not automatic merge).
- Add research report and structured source review/QA files under `docs/audits/`; update README, docs index, runbook, implementation plan and research decisions.
- No changes to historical 487 records, approvals, active GIS, JORC database or MCDA scoring.


## P0 complete 487-source batch audit — 2026-10-31

- Join **all 487 frozen Census source targets** by original `target_id` from identity, evidence/locators, source recovery, official tenure, company roles and the 39 reviewed-group screen.
- Publish an **editable 39-column, 487-row CSV**, machine-readable QA/statistics with Git blob provenance and a versioned report in `docs/audits/`.
- Add Python standard-library builder `scripts/build_p0_census_487_audit.py` and regression tests for exact 487-row coverage, stable Project/Deposit level, cohort lineage, no automatic C1 approvals and non-overwrite of released snapshots.
- Summarize 323 deposit, 102 occurrence, 50 source Project, 6 prospect and 6 historical source records; 78 linked to 39 review groups, 409 unlinked; external title spatial overlap is not legal ownership.
- Update README, docs index, Runbook, Implementation Plan and Decisions. **No Project/MRE/GIS independent approval, legacy source edits or MCDA calculations.**


## P0 individual Project source screen — 2026-10-31

- Source-check 39 frozen review Project groups against public government/company/issuer evidence and write editable `docs/audits/2026-10-31_project_source_screen_39.csv`, methodology report and provenance manifest.
- Summarize state distribution and 6 screening classes: 7 study documented, 8 study/FID recheck, 14 resource/exploration, 7 REE-role HOLD, 2 outside pre-FID, 1 on-hold activity.
- Flag post-cutoff 2026-10-30 Northern Minerals report as supplemental only; identify time-sensitive Jupiter JORC/Scoping update, Dubbo ASM acquisition, Nolans/Balranald FID, and THM/MzEq versus TREO basis.
- Document the proposed `C1_DIRECT_REO` vs `C2_HMS_REE_COPRODUCT` comparison split **as a pending scientific decision**, not a changed eligibility rule.
- Update README, docs index, implementation plan and research decisions; preserve all original sources and approval gates. **No** SQLite migration, Python/R code, score, population identity or published release altered.


## P0 Cohort and JORC data design — 2026-10-31

- Begin research P0.1/P0.2 **design and data-readiness audit** under Research Architecture v2, without modifying pipeline, SQL migrations or scoring.
- Add `docs/P0_COHORT_SELECTION_PROTOCOL.md` and `docs/P0_PROJECT_RESOURCE_SCHEMA.md` as detailed Project admission and scoped JORC resource model contracts.
- Add 39-group candidate review CSV and summary under `docs/audits/` (frozen 2026-10-29 sources); preserve unapproved/HOLD status, no auto-promotion to Project.
- Add editable, empty Project Gate and JORC Statement review CSV templates under `inputs/templates/`; update README, docs index, implementation plan and decision log.
- C1 required panel, approved Project set and v2 schema migration remain pending. No historical results, evidence approvals, original inputs or MCDA algorithms altered.


## Research Architecture v2 contract — 2026-10-31

- Add `docs/RESEARCH_ARCHITECTURE.md` as the canonical A/B/C research contract; define C0 Census, C1 Primary MCDA, C2 Extended Projects, C3 Historical Validation and P0–P3 release gates.
- Add `docs/DATA_SPECIFICATION.md`, `docs/MCDA_PROTOCOL.md`, `docs/VALIDATION_PROTOCOL.md`, and `docs/RESEARCH_IMPLEMENTATION_PLAN.md` to specify JORC/entity/evidence data semantics, six-domain scoring, scenario/AHP routing, SMAA and Aim C validation.
- Add `.github/pull_request_template.md` to require Aim/Gate, data lineage, compatibility, test and document review in future PRs.
- Update README, docs index, historical requirements, decisions and Git workflow to refer to the v2 design contract.
- **Documentation/workflow only:** no migration, scoring logic, current eligibility gate, source data, or research results changed; v2 parameters and C1 admission list remain pending.


## Research framework and status assessment — 2026-10-30

- Add an editable, GitHub-rendered Mermaid framework to the root README, distinguishing the implemented census/evidence/GIS/eligibility/MCDA pipeline from proposed Aim A/B/C research outputs.
- Add a compact qualitative assessment to the README and the evidence-based detailed review at `docs/PROJECT_ASSESSMENT_2026-10-30.md`; index it in `docs/README.md`.
- Document current census numbers, the G0 versus six-domain limitation, cohort/weight distinctions, evidence gaps, methodological selection biases, and P0–P3 research priorities.
- Documentation only: no source data, admission gate, scoring algorithm or published result changed.


## Repository structure — 2026-10-30

- Keep the root README concise and move operation details into `docs/RUNBOOK.md`; add navigation in `docs/README.md`, `outputs/README.md` and `reproducibility/workpack/README.md`.
- Remove root copies of three identical `scripts/build_487_*.py` entrypoints and SQL migrations `0007–0009`; retain the canonical `scripts/` and `db/migrations/` versions.
- Move four distinct frozen-workpack scripts into `reproducibility/workpack/`, update `rebuild_all.py` and provenance paths, and preserve dated snapshots and tracked research outputs.
- Remove accidental one-byte root `test` file; add repository layout regression test. No changes to official source records, release files, eligibility or MCDA formulas.
- **Compatibility:** historical command paths for root-level workpack scripts have changed; use `reproducibility/rebuild_all.py` and `docs/RUNBOOK.md`.


## Documentation roadmap — 2026-10-30

- Reorganize the root README into research goals, verified implementation state, executable workflows, planned requirements and reference navigation.
- Add `docs/RESEARCH_REQUIREMENTS_AIMS_ABC.md` defining development-potential assessment, ranking robustness and driver analysis with P0–P3 acceptance tests.
- Preserve the pre-reorganization five-stage README at `docs/archive/README_v1.0.4_pre_ABC_2026-10-30.md`.
- Distinguish G0/R1/S1/RS evidence/cohort scenarios from resource/development/strategic-supply weight perspectives; document that G0 currently omits R1/S1.
- Documentation-only change; program behavior, data and research results are unchanged.


## v1.0.1 — 2026-10-29

- Implement separate archived-document SHA-256 validation and independent reviewer decisions; input self-declared `VERIFIED` alone is not accepted.
- Introduce provenance tables `source_documents`, `evidence_approvals`, `evidence_links`, `approved_project_reviews`, and the `gis_release_gates` audit table.
- Re-evaluate coordinate and evidence approvals from current inputs on every upstream re-run; revoke stale scores and derived observations.
- Freeze G0 global eligibility to the original 19 Alternatives; block all global matrix exports until 19/19 approved GIS and point values are complete.
- Allow R1/S1/RS separately labelled subset releases only if at least two non-spatial eligible projects all have approved GIS.
- Require archived and separately approved local GIS layers; non-archived remote GIS endpoints remain `OFFICIAL_REMOTE_NOT_ARCHIVED_OR_APPROVED`.
- Add Python 3.11/3.13 offline CI, R 4.4.3 synthetic deterministic smoke CI, and regression tests for approval revocation and global/subset GIS gating.
- Historical 203-project census and 220 unverified observations remain unchanged; no real project promoted to Verified.

## v1.0.0

- Five-stage Australian REE census/criteria/GIS/eligibility/R-export pipeline.

## v1.0.4 — Scheme A evidence-backed identity policy

- Preserve original public-government records and extended REE-mineral occurrence inventory.
- Require independently approved project-identity documents for new Project Master entries; legacy 203 frozen seeds remain distinct.
- Add geological entity/provenance, parent links, cross-source review pairs, and identity audit tables, with editable CSV exports and repeatable tests.

## 2026-10-31 — P0 412 HOLD provenance/Gate continuation

- 完整保留 412 筆 target IDs，與 P1 73／P2 28 分離，產出 P3 216 Deposit/Prospect 與 P4 95 Occurrence 的 311-row 來源追溯工作表；本輪僅完成 provenance triage。
- 13 個正向案例（22 source rows）跨接原始 Gate、P1 Case、JORC basis、來源紀錄，確認正式 Project/JORC/GIS/C1 0 核准且全部留 HOLD。
- P2 28 source／27 cases 補上 Legacy/native source crosswalk 與歷史範圍旗標；不擅自合併同名及不同時點來源。
- 新增可重跑 Python、unit test 與 GitHub workflow；README 和研究索引同步更新。

- P3/P4 與 2026-10-29 政府原生 272-feature JSONL 做逐筆 ID/source/native SHA 回查：194/311 精確交叉核對，0 不一致，117 不在此 272 子快照內；新增自動 QA。

## 2026-10-31 — Reconcile legacy 487 priority P2 72 and original HOLD P2 28

- 合併原 PR #33 的 72-row／47 case source intake、7 dated documentary leads（涵蓋 22 sources）及 stdlib Python 重建。
- 以 source ID 建立 72-row priority crosswalk：28 原 412 HOLD P2、38 INCLUDE_CANDIDATE、6 HOLD_REE_ROLE；不得重複相加。
- 保留 2026-10-29 as-of、研究 C1/JORC/GIS 0 核准；補強 README／決策紀錄、測試、CI。

## 2026-10-31 — PR merge-state documentation QA

- 確認 PR #38 (`9a9b596`) 及 PR #33 (`d16bb31`) 已合併；回填 README / source-gate report 的最新 PR 狀態。
- 72-source legacy P2 與 412-HOLD P2 的交叉表已隨 PR #33 合併，28+38+6 不增加任何 C1 核准數量。
