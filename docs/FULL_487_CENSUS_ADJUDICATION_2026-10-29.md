# 487 筆母體完整度查核（2026-10-29）

## 全體結果

- 固定母體：487 筆；86 筆歷史 ID、401 筆 E1 來源記錄。
- `PROJECT_CANDIDATE_REVIEW`：21 筆。
- `HOLD_REE_ROLE`：4 筆。
- `HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE`：462 筆。
- 排除：0 筆；MCDA：未執行。

## 每筆審查結果如何解讀

487 筆全部保留原始 target/source ID，並逐列給出五項條件狀態、證據連結、公司關係及去重處置。21 筆連至已查核候選群；其餘列按保守門檻暫緩。E1 的稀土 commodity 或 occurrence 記錄是來源線索，不自動證明獨立 Project、專案稀土產品／目標或開發階段。歷史 ID 若無精確來源交叉表，標明只有 ID 並附州官方搜尋入口，不臆造專案匹配。

## 尚未完成的證據（明確保留）

目前可確認的是母體中哪些行有官方資料集記錄或歷史 ID、來源所報稀土／礦種線索，以及已查的 18 個候選群。其餘 462 筆尚無逐筆的正式專案技術揭露、當前持權人、營運商或更名／轉讓文件配對；故 Project 身分、專案層級稀土角色及公司沿革仍標為 HOLD／未解析。州級礦權服務的空間相交也不能取代正式 title register、礦種權利範圍及歷史轉讓文書。

## 納入門檻

五項操作定義均需在 Project 層級通過；至少有官方政府／礦權資料與正式技術或專案揭露；稀土需是主要產品、共同產品、計畫回收副產品或明確勘探／開發目標；Project 與 Deposit／Prospect／Tenement 關係須釐清。未知即 HOLD；只有正面證據證明不符必要條件才可 EXCLUDE。名稱相同不能單獨作為合併依據。

## 檔案

- `487_definition_review.csv`：487 筆逐列核查母表，含來源記錄 ID、官方目錄入口、五條件、公司與去重狀態。
- `487_inclusion_gate.csv`：固定 487 筆的候選／暫緩門檻表。
- `project_candidate_evidence_review.csv`：18 個已查候選群來源與證據評估。
- `project_inclusion_gate_rules.csv`：納入、待查、排除及去重規則。
- `AU_REE_487_pre_MCDA_five_definition_review.xlsx`：上述工作簿及各核對佇列。
- `487_full_census_adjudication_summary.json`：按州、來源鍵及狀態的覆蓋統計。

