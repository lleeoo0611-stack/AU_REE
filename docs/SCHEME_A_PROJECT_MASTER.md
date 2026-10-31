# Scheme A — 澳洲 REE Project Master、礦床階層與去重規則

版本：`1.0.4`。研究對象為**稀土開發專案**，而非全部含稀土礦物的地質礦點。研究母體、礦床和 MCDA Alternative 採分層識別。

## 資料層級與收錄

| 層級 | 正式資料表 | 收錄準則 | 研究用途 |
|---|---|---|---|
| L0 | `source_feature_snapshot`, `population_candidates` | 所有官方原始紀錄；保留 Native ID、來源、原件雜湊及快照目錄 | 來源完整性、重跑與排除理由 |
| L1 | `extended_occurrence_inventory` | E1 明確 REE 的地質紀錄、E2 稀土礦物伴生及 E3 僅名稱背景提及者 | 全澳稀土地質候選，不計入 Project Master |
| L2 | `geological_entity`, `geological_entity_source` | 將各來源的 Deposit／Occurrence／Mine Site 先建立**來源範圍**地質實體 | 同一地質實體的跨來源比對 |
| L3 | `project_master`, `project_geological_relation`, `identity_review_decisions` | 有獨立且可核實的開發專案身分文件與審核紀錄；明確保留過去 203 筆 Legacy Frozen 作歷史基準 | 開發專案主檔與多礦床從屬關係 |
| L4 | `eligibility`, `criterion_values` | 經 Project Review、JORC、Scoping–DFS、GIS、AHP 與完整度閘門 | 正式 MCDA Alternative |

E1 = 商品欄明確 REE、TREO、NdPr 等（含 GA 已按 REE 篩選的官方圖層）；E2 = 只有 Monazite／Xenotime／Allanite／Bastnäsite 等礦物；E3 = 僅名稱／描述線索；E0 = 無相關證據。E2、E3 預設 `BACKGROUND_ONLY`。所有級別均先按原始來源保留；**E1 也不是自動取得 Project 身分**。

## 去重的三個不同問題

1. **重複下載紀錄**：同來源 + Native ID + 紀錄 SHA256 代表同一來源版本，可重用；來源版本不同仍可追蹤。
2. **地質實體重複**：同州同名、不同來源或距離 ≤1 km，進 `dedup_candidate_pairs.csv`，狀態僅 `PROPOSED_ONLY`。名稱、座標、公司相似度**不是合併依據**。
3. **開發專案身分**：官方 Parent Project 提示可以寫入 `project_deposit_relations.csv`，預設 `PROPOSED_ONLY`，不自動把不同礦床合成單一儲量。若有獨立核准證據，可確認 `PART_OF_PROJECT`，仍保留原礦床個別 ID。

作業上使用 Stage 01 的 `population_cross_source_duplicates.csv` 對 Project 標籤進行二次比對。公司名稱差異與跨州座標衝突保持 `REVIEW`。已核准來源的條件變更會重新觸發階段指紋及下游計算。

## 新專案如何進入 Project Master

填入 `inputs/project_identity_decisions.csv`：

`candidate_id,decision,project_name,project_id,source_url,source_sha256,evidence_date,approval_ref`

- `APPROVE_NEW_PROJECT`：僅接受原始候選層級為 **Project** 的來源紀錄，Deposit／Prospect／Occurrence 不可直接升格；使用已封存文件和**獨立批准**的 `approval_ref`；需填明確 `project_name`。`project_id` 留空時，以不受來源匯入／核准順序影響的 `candidate_id` 雜湊產生固定 `AU-REE-` 數字 ID（目前 12 位），不再使用當下最大編號加一。同州同名者仍進既有專案連結審查；已核准 ID 有衝突時須獨立更正，不自動改號。
- `LINK_EXISTING_PROJECT`：僅能指向**已取得獨立 Project 身分核准且核准仍有效**的 `project_id`；`LEGACY_UNVERIFIED` 或已撤回核准的 Master 不可作為已驗證母專案。來源若為 Deposit／Occurrence，必須存在可追溯的 Geological Entity Source，才可建立 `PART_OF_PROJECT`；若為 Project，審查同意的別名才可寫入 `project_aliases`。既有核准 parent 關係要變更，必須另行正式更正，不得默默轉移。
- `REJECT_PROJECT`：保留原始候選與審查狀態，不新增 Project。

每筆核准須在 `inputs/source_documents.csv` 登記實際封存檔、官方／公司來源 URL 與 SHA256，於 `inputs/evidence_approvals.csv` 由另一欄位明列 `record_type=PROJECT_REVIEW`、審查者、`decision=APPROVED` 和凍結日前審查日期。只有原件位元組、URL、SHA、日期及 `approval_ref` 全部吻合才允許新增／連結。取消審查會將相關新專案標記為 `IDENTITY_APPROVAL_EXPIRED`，其正式分析資格失效；保留永久 ID 與完整稽核紀錄。座標／活動／開發階段的**獨立**核准仍依 `inputs/project_reviews.csv` 進行。

歷史 `legacy_r963_frozen` 的 203 個 Project ID 保持在主檔，狀態維持 `LEGACY_UNVERIFIED`，不能以此宣稱最新政府已核准 203 個正式開發專案。其 MCDA 釋出條件與新增專案一致。

## 版本化及執行

```bash
python -m pytest -q
python -m au_ree run --through r_export --offline
python -m au_ree status
```

Stage 01 另外匯出：`population_raw_feature_index.csv`、`geological_entities.csv`、`geological_entity_provenance.csv`、`extended_occurrence_inventory.csv`、`project_deposit_relations.csv`、`dedup_candidate_pairs.csv`、`project_identity_decisions_audit.csv`。CSV 可直接編修，SQLite 為單一研究資料庫；原始 API JSON 封存及 SHA256 Manifest 由來源擷取模組管理。更改審查 CSV 或證據原件會使 Stage 01 Fingerprint 變動，後續重新計算。
