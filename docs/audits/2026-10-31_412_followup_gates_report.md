# P0 — 412 HOLD 後續來源證據與 C1 Gate 查核（2026-10-31）

**資料快照：2026-10-29；重新對表：2026-10-31；單位：source target ID。** 本報告為讀取已封存政府原始資料、第二輪來源線索與 P1/P2 已完成公開文件審查的**來源證據延伸稽核**。不將來源連結當作原始 PDF SHA，也不代表新增 311 筆原件人工全文複核。

## 1. 保留全部 412 source IDs

| 不重複分流 | Source rows | 本輪的工作界線 |
|---|---:|---|
| P1 | 73 | [已結案來源紀錄](2026-10-31_p0_p1_closeout_report.md)，44 案，正式核准仍獨立追蹤 |
| P2 | 28 | [公開文件審查](2026-10-31_p1_p2_public_evidence_closeout_report.md)，27 案；本輪新增 baseline 身分交叉表 |
| P3 | 216 | **210 Deposit、6 Prospect**；依 source/native ID、SHA、第二輪文獻定位整理證據層級及待核項目 |
| P4 | 95 | **95 Occurrence**；保留原始政府地質點，不擅自升格為 Project |
| **合計** | **412** | 所有 target ID 精確保留，無合併、刪除或 Project 升格 |

P3／P4 [311 筆逐列可編輯核查 CSV](2026-10-31_p3_p4_311_provenance_audit.csv)保存 state、原始 source key/native ID、source-feature 原始 hash/location、既有外部文獻線索與定位缺口。P3/P4 目前完成的是**全量 provenance-level triage**，還沒有逐件重新下載核對所有 311 筆外部原始 PDF，也沒有驗證新的現行 tenement 或 Project polygon。缺文件保持 HOLD，不推論專案不存在。

本輪另外直接比對已封存的 [272 筆官方來源 JSONL](../../data/source_snapshots/2026-10-29_272_native_features.jsonl)：其中 **194/311 筆**可逐一核對 `target_id + source_key + native_id + original_chunk_sha256`，**0 個欄位衝突**；其餘 **117 筆不屬於這份 272-source 子快照**，不可因此視為來源不存在，仍保留在其原本的來源/審查路徑。

P3 州別：NSW 24、NT 6、QLD 16、SA 80、TAS 1、VIC 10、WA 79。P4 州別：NSW 5、NT 32、QLD 9、SA 34、TAS 15。

## 2. 13 個 C1 正向案例：第二資料表交叉核查

[13 案可編輯 C1 Gate 表](2026-10-31_c1_13_independent_gate_readiness.csv)逐一串接前期 [13 案原始 Gate](../../inputs/source_review_20261031/p1_13_positive_case_gate_decisions.csv)、[44 案文件主張](2026-10-31_p1_44_case_resolution.csv)、[73 筆來源層級審查](2026-10-31_p1_73_source_resolution.csv)與[14 筆資源基準聲明](2026-10-31_p1_48_resource_basis_review.csv)。核對 **13 案／22 原始來源列**，保留原有日期、身分、產品、JORC/氧化物及研究階段差異。

13 案為 Copi、Korella、Fingerboards、Nowie、Aileron、Governor Broome、Mia/Mount Ridley、Redlings、Fraser Range/Talisker、Tower/Mt Clere、Yttria/Mt Stirling、Goschen South、Wim deposits。

**結果：13/13 均為 C1 HOLD，0 獨立核准。** 當前資料表仍缺可核准的 Project/Deposit footprint、原始文件 PDF bytes/sha、完整 REE JORC scope、截止日前完成的經濟研究與共同六構面 Panel，且無獨立 reviewer signature；不能以本次跨表覆核冒充正式簽核。對應 [Issue #32](https://github.com/lleeoo0611-stack/AU_REE/issues/32)。

尤其不得將 HM/THM、Y₂O₃、Nb₂O₅ 直接當 TREO，不能將不同日期與不同 cut-off 的 Resource 相加。另依既有來源 [Aileron 原始資源聲明表](2026-10-31_p1_48_resource_basis_review.csv)，2025 REO component 和 2026 niobium MRE 的化學基準需分開。新找到的 [Encounter 2026 年 7 月季度公告](https://www.marketindex.com.au/asx/enr/announcements/quarterly-activities-report-and-appendix-5b-6A1335855)亦以 **Nb₂O₅** 報告 120 Mt 級資源，不足以獨立放行 TREO。

## 3. P2 身分與證據補強

[28 筆可編輯 P2 Identity crosswalk](2026-10-31_p2_28_identity_crosswalk.csv)已對照原 487 母表及 [公開文件審查](2026-10-31_p2_28_public_terminal_desk_review.csv)的 27 案：

- **22 筆 Legacy UUID**：保留原始 ID，避免單憑同名將來源掛接新專案。
- **6 筆 E1**：保留 native source ID，尚須核對 Project/Deposit 法律範圍。
- 每筆保留官方/發行人來源、發表年份、tenement、REE 資源基準、研究階段和具體缺口。
- Mary Kathleen mine／tailings、Bruce／Plenty River、Talisker／Salazar、VIC Bondi／Douglas 等既有身分反例均維持分離。

本輪補強是**原始來源與文獻審查的逐列關聯驗證**，不是取得新文件 bytes 或現行法律持權核准。27 案公開文件階段已完成，正式 source-to-Project、JORC 和 GIS Gate 仍 HOLD。對應 [Issue #35](https://github.com/lleeoo0611-stack/AU_REE/issues/35)。

## 4. PR 與可重現驗收

截至本分支建立，PR #31、#36、#37 均已合併 main（base commit `ac1735d`）；[PR #33](https://github.com/lleeoo0611-stack/AU_REE/pull/33) **仍為 Draft**。#33 使用較早版本原始 `action_priority=P2` 的 72 筆／47 案，而本報告 P2 是由 412 HOLD 固定分流的 28 筆。兩者不可在未建立交叉索引前直接合併當作同一 P2。尚未改動 #33。

可重跑指令：

```bash
python scripts/audit_p0_412_gate_continuation.py --check
python -m unittest discover -s tests -p 'test_p0_412_gate_continuation.py' -v
```

輸入來自不可變原始快照及 Git 已追蹤 CSV，輸出只寫 `docs/audits/`。新增來源需先加入經審查的 evidence input 或下一版 snapshot，再由 `--write` 產生新版本；不得用推測的 reviewer 簽章、原始 PDF SHA 或 Project ID 通過 C1。
