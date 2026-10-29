# 487筆母體追溯狀態（2026-10-29）

## 結果

- 固定目標列：487（86筆歷史 ID、401筆 E1來源記錄）；原 target/source ID 全數保留。
- 最新逐列暫定狀態：`{"PROJECT_CANDIDATE_REVIEW": 37, "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE": 444, "HOLD_REE_ROLE": 6}`。
- 已核實來源支持的專案候選列數：37；已建立候選專案群：29。候選不等於完成 title/權利鏈核實或最終納入。
- 州／領地官方礦權圖層查詢狀態：487列全數有結果；258列有764筆空間相交證據、51列於已查圖層無相交、50列缺可用座標、128列SA官方title layer未驗證。相交僅是title候選，不證明Project邊界、現任持有人或營運商。
- 現任登記持有人與公司沿革全鏈完成核實：0列；holder/company欄僅列來源觀察或個案證據，不把holder視為operator。

## 逐州追溯範圍

本工作包是逐列 census/entity-linkage，不是所有列都完成外部官方來源閉環。已有 project-level 來源審核的列，才依五項操作定義更新；其餘留在 HOLD，不當作排除，也不以 deposit/occurrence 名稱推定專案。NT 本輪增加 Barkly/Vanadis/Benmara North、Bruce Prospect、Plenty River、Benmara South、Skyfall、Stromberg、Quantum 對照；名稱連結有歧義者仍待查。官方 title register、歷史轉讓及每列座標到 title polygon 的核對尚未完成。

## 全487列官方礦權追溯範圍

交付檔 `487_official_tenure_trace_status.csv` 對應全部487個 target ID；`487_official_tenure_intersection_evidence_compact.csv` 保留764筆相交列，含官方 title 編號、holder文字、狀態、來源圖層及查詢網址。`487_row_adjudication_latest_2026-10-29.csv` 是目前GitHub可用的精簡逐列五條件與來源判定表，487列完整。現行大欄位完整版仍以本地工作簿及 `487_definition_review.csv` 為準。由於既有幾何查詢快照部分州屬官方空間圖層而非歷史title register，且SA圖層未驗證，不能稱作487筆法律持權鏈已查清。另有50列無可用座標，需先找回target/project座標或原始地質來源。

## 北領地本輪結論

- Barkly/Vanadis/Benmara North：NT Government 與公司專案資料支持同一 Barkly REE Project 及其 prospect/resource 關係，作為候選；舊 observation 與現行 tenement 的空間／法律同一性仍待核。
- Bruce Prospect：ASX 明確把 Bruce Prospect 放在 MetalsGrove Arunta Project；NTGS 報告支持 REE 勘探，列為候選。
- Plenty River：歷史礦區與現代 MetalsGrove REE sampling 名稱重疊，無法用名稱證明同一目標，保留 HOLD。
- Skyfall、Stromberg、Quantum：政府確認 REE prospect 與礦化目標，但現行專案單位、proponent/title、階段未由目前來源閉環，保留 HOLD。
- Benmara South：現行 Barkly resource page 點名 North 而非 South；不得混併，保留 HOLD。

## 仍需完成

1. 其餘 HOLD 逐列核對州／領地官方 title register、公司正式揭露及 ASX/ASIC 公司沿革。
2. 建立 target → occurrence/deposit/prospect → tenement → named project → proponent/registered holder 證據鏈，並保留原 ID。
3. 對所有已分組候選做座標/title polygon 交叉核對；沒有 tenure/property record 的不能標成 title verified。
4. 暫不執行 MCDA；須先完成 census 人工覆核與納入簽核。

