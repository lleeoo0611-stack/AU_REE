# P0 P1｜412 HOLD 中的 73 筆 Project 身分與來源優先核查

**審核日：2026-10-31；政府來源快照：2026-10-29；底稿：`54fc23d304d3`。**

## 查核範圍與結果

依原始 487 表的 `HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE` 固定 **412 筆**，以 immutable `target_id` 串接第三至第六輪來源稽核。選取並不加總重複的 P1 資料列 **73 筆**：**48** 筆具名／歷史 Project 母層候選、**4** 筆 WAMEX 原件待取索引、**21** 筆 Project／礦區／行政區／幾何身分 HOLD。Ambergate 同名兩來源相距 **38.738 km**，由先前具名候選轉入空間身分 HOLD（2 筆）；此調整不修改原始列的審核欄位。

本次新增 **14 筆逐來源定向核查紀錄**：8 筆政府／發行人／獨立技術文件原文（Tower 2、Ouyen 3、Glenaladale 1、Wingellina 2）、4 筆 WAMEX 轉載索引、2 筆 Ambergate 原生空間 QA。**14 是來源列數，不是 14 份獨立技術報告。** 未升格 Project、JORC、GIS 或 C1。剩下 59 筆已有前幾輪來源但尚未在本次新增逐筆外部核對。

| 本輪互斥類別 | 來源列 | 判定 |
|---|---:|---|
| `PARENT_CANDIDATE` | 48 | 已有具名父層線索，尚需時間、範圍、稀土角色及主文原件核准 |
| `INDEX_PRIMARY_PENDING` | 4 | WAMEX 編號及歷史礦砂 Project 索引，政府原文未封存 |
| `IDENTITY_SCOPE_HOLD` | 21 | 原生 source vs Project/tenement/州界問題，暫停自動合併 |
| **合計** | **73** | **正式 C1 = 0** |

## 本次核查的重要決策

1. **Tower × Mt Clere（2 筆）**：Krakatoa 的 [2023-03-29 ASX 原始公告](https://www.asx.com.au/asxpdf/20230329/pdf/45n40zttl1v5y5.pdf) 頁 1–2，將 Tower 視為 Mt Clere Project 內的 REE deposit，並陳述 101 Mt @ 840 ppm TREO。公司當時將 Scoping Study 描述為後續規劃；獨立 JORC 表、source polygon、截至快照的 stage 須分別核准。
2. **Galileo／Mercury／Titan（3 筆）**：[Resource Equity 2004 報告](https://www.recconsultants.com.au/PDFs/Bemax%2020040313.pdf) §12.8.1–12.8.3（報告頁 52），三者為歷史 Ouyen 重礦砂專案的不同礦化標的。表列 HM 並非可直接使用的 TREO；原始年代和 2026 現行開發案分開。
3. **Glenaladale × Fingerboards（1 筆）**：[Victoria Planning 2026 Project 文件](https://www.planning.vic.gov.au/environmental-assessments/browse-projects/referrals/fingerboards-critical-minerals-project) 明示 Fingerboards Critical Minerals Project 位在 Glenaladale Deposit，含 REE 相關產品及環評程序；[2021 舊案](https://www.planning.vic.gov.au/environmental-assessments/browse-projects/fingerboards-mineral-sands) 另行管理。保留 Deposit–Project 範圍核對。
4. **Wingellina（2 筆）**：[WA EPA](https://www.epa.wa.gov.au/proposals/wingellina-nickel-project) 為 WA Nickel Project，SA-tag 原生經度 128.938°E 跟行政區界需核實。Ni–Co 資源不可冒作 REE。
5. **WA WAMEX（4 筆）**：[WA 官方 WAMEX](https://www.wa.gov.au/service/natural-resources/mineral-resources/access-mineral-exploration-reports-wamex) 是原始報告儲存庫；[A119194](https://geothought.nlp-tlp.org/wamex/A119194)（Hopelands East）、[A120393](https://geothought.nlp-tlp.org/wamex/A120393)（Hassell Beach 2 列）、[A129842](https://geothought.nlp-tlp.org/wamex/A129842)（Witchcliffe）已讀索引，但逐報政府 PDF、SHA、範圍及 REE 產品仍列正式待辦。
6. **Ambergate（2 筆）**：前輪來源顯示同名政府礦床相距 38.738 km。規則改為 `IDENTITY_SCOPE_HOLD`，待官方 tenement/Project polygon 比對後才能判定是否同父層。

## 產出、使用方式及審核規則

- [73 筆逐列 CSV](2026-10-31_p1_parent_identity_review.csv)：固定 target_id、原始 SHA、最新前輪證據、P1 新增文件與定位、核准 Gate、下一步。
- [14 筆人工核查來源登錄](../../inputs/source_review_20261031/p1_parent_identity_web_checks.csv)：逐筆外部文獻與 frozen native GIS QA 主張；無新增核查的 59 筆保持清晰標記。
- [JSON 統計及輸入來源](2026-10-31_p1_parent_identity_summary.json)。
- [可重跑 Python](../../scripts/audit_p0_p1_parent_identity.py)、[回歸測試](../../tests/test_p0_p1_parent_identity.py)。

```bash
python scripts/audit_p0_p1_parent_identity.py --check
python -m unittest discover -s tests -p 'test_p0_p1_parent_identity.py' -v
```

**判定順序：**後輪覆蓋前輪的「證據工作類別」，不修改 source-native 欄位；Ambergate 的 `>25 km` 多來源分離依前輪交叉距離提高為 `IDENTITY_SCOPE_HOLD`。正式專案核准仍需 source PDF 原件/SHA、報告頁碼、dated project polygon、產品與資源基準、independent review signoff。C0 與 C1 分開，**正式 C1 = 0**。
