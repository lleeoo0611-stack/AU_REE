# P0／P1 桌面查核結案與正式發布門檻（2026-10-31）

**來源快照截止：2026-10-29**  
**研究版本：P0/P1 C0 census evidence closeout**  
**正式狀態：`P1_DESK_SEARCH_CLOSED`；`P0_CI_BLOCKED`；`C1_NOT_RELEASED`。**

## 1. 範圍與結案標準

本次以凍結 P1 73 筆原生政府來源 `target_id` 為固定分母，逐筆附來源文件、發表日期、報告定位、資源化學基準、當前可支持的 Project–Deposit 關係、官方礦權交集及重新開案條件。**結案的是 P1 指定來源範圍的文件搜尋與判讀**；保留原始 487 census、Project master、六構面 MCDA、JORC、GIS_RELEASE 與 C1 決策原狀。

`P1_REVIEW_CLOSED` 的條件：每筆 ID 只有一個最終處置，有來源與可追溯的理由，搜尋來源已列明，必要時有原始文件取得或範圍爭議的明確重新開案條件。文獻不足不被寫成地質上沒有稀土。

`P0_RELEASE_READY` 另須觀測 GitHub CI 綠燈、snapshot 再生、獨立 Project/Document/Geometry/JORC signoff、正式共同六構面 Panel，以及 C1 凍結審查。這些條件尚未全部成立。

## 2. P1 來源結案統計

| 互斥 P1 研究處置 | 原始來源列 | 工作決定 |
|---|---:|---|
| `C0_POSITIVE_PROJECT_OR_REE_LEAD` | **22** | 13 個正向案例完成六個 C1 Gate 的逐案 HOLD 評估 |
| `C0_NO_PROJECT_SCOPED_REE_PRODUCT_PROOF` | **40** | 依已列來源判定現階段無 Project-scoped REE 產品或資源支持；新主文出現才重開 |
| `C0_EXPLICIT_RESOURCE_SCOPE_EXCLUSION` | **2** | Benmara South 不可繼承 Barkly 40 Mt TREO 資源，V₂O₅ 主張另存 |
| `C0_UNRESOLVED_NATIVE_IDENTITY_CONFLICT` | **4** | Ambergate 同名位置 38.738 km、Wingellina 原生 SA-tag 與州界問題 |
| `C0_INDEXED_PRIMARY_DOCUMENT_ACCESS_BLOCKED` | **5** | 4 份具名 WAMEX 原始報告有編號和次級索引，政府 PDF bytes／SHA 未取得 |
| **合計** | **73** | **44 個案例均有文獻判讀與終止／重啟條件** |

**Wemen 更新**：[Victoria Department of Primary Industries, *2003/04 Statistical Review*（2005 年 4 月出版）](https://resources.vic.gov.au/__data/assets/pdf_file/0008/462734/Earth-Resources-Annual-statistical-report-2003-2004.pdf) 的 Summary Minerals（印刷頁 5、25）明言 Wemen 礦砂礦場於 2004 年 1 月停止生產。該證據足以把 Wemen 自「只有歷史目錄」改為**歷史已生產礦場**，按 pre-FID 主母體條件維持 C0，不歸入新增 C1 專案。原始來源點與採礦坑界仍非經核准開發 polygon。

## 3. 13 個有正向證據的案例——全部完成 C1 Gate HOLD 判讀

以下是 Project／礦床證據候選，合計 **22 筆來源**。文件存在不等於通過 C1 的六層簽核。

| 案例 | 本輪主要證據 | C1 當前關鍵關卡 |
|---|---|---|
| `P1G-0003` Copi / Copi North | NSW 官方具名礦床關係及 REE byproduct；主資源為 HM | 相同範圍 TREO/JORC、正式開發界線 |
| `P1G-0005` Korella | 2011 年 Y₂O₃ 礦產資源，發行人摘要與內文數值不一致 | 資源版本、有效當代經濟研究階段 |
| `P1G-0007` Fingerboards / Glenaladale | 2026 維州 EES 與 RL2026 交集、規劃 REE 產品 | 正式 TREO/JORC、EES ≠ 經濟 Scoping Study |
| `P1G-0008` Nowie | 16.4 Mt @ 3.8% THM，monazite/xenotime | REE 可回收商品、TREO/JORC、經濟研究 |
| `P1G-0010` Aileron | Nb₂O₅ 為 2026 最新資源主要基準；2025 歷史 TREO 組分 | 同範圍 REE 資源基準、已發布經濟研究 |
| `P1G-0015` Governor Broome | HM Scoping、monazite 測試物流、R70/53 | 產品 REE 回收計畫及同範圍 REO MRE |
| `P1G-0019` Mia / Mount Ridley | Mia 與 Grass Patch 多資源區塊 TREO，E63/2112 | 不同 cutoff／範圍不可混加、經濟研究 |
| `P1G-0021` Redlings | 11 Mt @ 1,130 ppm TREO；6 筆來源同 E37/1311 | 已完成 Scoping/PFS 與正式資源範圍 |
| `P1G-0022` Fraser / Talisker | REE 探勘截距，與 Salazar 為不同礦權 | 本 Project 的 TREO JORC 與經濟研究 |
| `P1G-0023` Tower / Mt Clere | 101 Mt，840 vs 801 ppm 歷史版本；E09/2357 | JORC 版本、已完成 Scoping/PFS |
| `P1G-0025` Yttria / Mt Stirling | 15 Mt @ 490 ppm TREO；2 個地質點落不同礦權 | 正式 Yttria 資源 polygon、經濟研究 |
| `P1X-0006` Goschen South | 2024 EES 與規劃 REE 產品 | 南部來源點是否在實際 Project 區域、TREO |
| `P1X-0007` WIM deposits / Wimmera | 官方 WIM100 REE 產品，WIM50 與通稱需拆 | 指定礦床／Project footprint、同範圍 JORC |

所有 13 案目前 `ID/ROLE/WINDOW/JORC/PANEL/GIS_RELEASE` 正式欄位維持 `HOLD`，各案未達 C1 主分析資格。C0 本輪搜尋結案後，可依新文件逐門更新，不必重新掃描 73 筆。

## 4. 官方礦權空間關聯（已完成的來源級 QA）

- 既有 487 筆來源級官方 tenement 快照在 P1 固定範圍內有 **204 筆礦權交集**。
- **60/73** 筆來源點與至少一個已查官方礦權多邊形相交；**11/73** 已查詢圖層無交集；**2/73** 官方圖層未驗證。
- 將 18 個案例的發行人／政府明示礦權號碼與官方快照比對，**20 筆來源點、12 個案例**有精確 tenure 編號吻合。
- 已核實的礦權號碼包括 Redlings E37/1311、Tower E09/2357、Mia E63/2112、Aileron E80/5469、Fingerboards RL2026、Gwindinup M70/895／M70/899、Governor Broome R70/53、Yalyalup M70/1400、Jurien M70/436、Hopelands East M70/603、Tutunup West M70/1108。
- 精確 tenement 疊合是 source–title 身分支持，不代替法定 **Project 開發 footprint**、Resource block 或開發階段的 GIS release。

## 5. 具體 P0／P1 發布阻擋與交接

| 門檻 | 實際狀態 | 追蹤 |
|---|---|---|
| 73 筆 P1 原始來源與處置覆蓋 | **73/73 完成桌面判讀** | [逐筆結案 CSV](2026-10-31_p0_p1_73_terminal_decisions.csv) |
| 13 正向案例的六層 Gate 評估 | **13/13 已完成 HOLD 判讀** | [13 案 Gate 決策](../../inputs/source_review_20261031/p1_13_positive_case_gate_decisions.csv) |
| 4 個 WAMEX 原始政府 PDF + SHA | **0/4 已封存**（5 筆來源） | [來源申請紀錄](../requests/2026-10-31_wamex_primary_pdf_access.md)，[Issue #30](https://github.com/lleeoo0611-stack/AU_REE/issues/30) |
| Native source identity 正式矛盾校正 | **仍有 Ambergate／Wingellina 4 筆** | [44 案例審核表](2026-10-31_p1_44_case_resolution.csv) |
| C1 正式 Project/JORC/GIS／Panel 簽核 | **0** | [C1 Admission Protocol](../P0_COHORT_SELECTION_PROTOCOL.md)、[13 案下游核准 Issue #32](https://github.com/lleeoo0611-stack/AU_REE/issues/32) |
| GitHub Actions CI 可觀測測試通過 | **未通過，根因未判明** | [Issue #29](https://github.com/lleeoo0611-stack/AU_REE/issues/29) |
| Draft PR 合併 `main` | **不合併，待 CI Gate 通過** | PR [#26](https://github.com/lleeoo0611-stack/AU_REE/pull/26) → [#27](https://github.com/lleeoo0611-stack/AU_REE/pull/27) → [#28](https://github.com/lleeoo0611-stack/AU_REE/pull/28) → P0/P1 closeout PR |

### CI 查核記錄

GitHub Actions [run 41169549036](https://github.com/lleeoo0611-stack/AU_REE/actions/runs/41169549036) 在數秒內結束為 failure，工作 `resolution-regression` 的步驟 API 回傳 `steps=[]`，logs 下載 404 BlobNotFound。同一 head 的既有 Python regression 和 R MCDA smoke 也出現 pre-step 失敗；check-run 顯示 2 個 annotations，但目前連線工具無法讀取文字。**因此不能把此問題確診為測試程式錯誤或 GitHub 帳務錯誤。** P0 保留 `CI_BLOCKED_PRE_STEP_UNDIAGNOSED`。

本次 closeout [run 41173058358](https://github.com/lleeoo0611-stack/AU_REE/actions/runs/41173058358) 同樣在約 4 秒內失敗（`steps=[]`、logs 404）。已經重新執行失敗工作一次（attempt 2），依舊在第一步之前失敗，排除了單次偶發成功的可能，但根因仍須閱讀 GitHub UI annotations。

首次檢查需開啟 GitHub Actions Job UI 取得兩個 annotations，檢查 Actions 配額／runner／權限／workflow；再執行下列測試並留存綠燈 run ID：

```bash
python scripts/audit_p0_p1_parent_identity.py --check
python scripts/audit_p0_p1_48_dedupe.py --check
python scripts/audit_p0_p1_73_resolution.py --check
python scripts/audit_p0_p1_73_tenure.py --check
python scripts/audit_p0_p1_closeout.py --check
python -m unittest discover -s tests -p 'test_p0_p1_*.py' -v
```

**目前僅已獨立完成連線側 source CSV／JSON 數量、hash 欄位、target–case 對照、20 筆 tenure 精確匹配與 Gate 禁止升格檢查。** 這些核查不代替在 GitHub runner 上觀測 Python tests passed。

## 6. 主資料庫一致性

正式 `project_master`、C1 released list、JORC approvals、GIS_RELEASE 和原先 MCDA 中 G0/R1/S1/RS 的內容維持未改動。P1 closeout 輸出所有來源 `census_cohort=C0_ONLY_NOT_ADMITTED`、`independent_C1_admission=NO`，可逐列確認。後續以 `target_id` 做跨版本更新；source feature、Deposit、Tenement、Project 不合併為同一實體。
