# 外部技術原件補查 — Batch 01（2026-10-31）

Execution: `EXT-TECH-B01-20261031`; base `main@85525fe`; source census as-of **2026-10-29**. 本批是追加 evidence overlay，沒有改寫該日期的任何原始 CSV、DB、身份或歷史快照；公開來源查閱日期 2026-10-31。

## 本批可證實的進展

- **167 筆需補技術原件的 native-only source 中 5 筆**完成發行人公開 PDF *可讀文字* 的實質對照：Johnson Dam 1、Ketchowla K2 2、Victory 2。此處確認的是來源文句／表格及正負範圍；本環境未取得原始 PDF 位元組或目視頁面，沒有 SHA-256，也沒有全篇人工閱讀的宣稱。其餘 **162 筆**未補本批原件。
- **P2 28 筆、27 案**重新做完整固定 ID、baseline desk verdict、原來源、當前 339 列與 closure/gate 狀態的 join（[28 筆複核追蹤 CSV](2026-10-31_p2_28_recheck_tracker.csv)）；其中 **3 筆** Mary Kathleen 由目前 Queensland 政府正式 HTML 原文再複核。其餘 **25 筆**保留既有桌面判讀，技術原件重讀仍待執行。**28/28 交叉核對不等於 28/28 原件複核完成。**
- **Scaddan 1 筆**找到供應商 2025 版 PDF 的可讀文字，與 2024 版原宣傳 PDF 交叉核對。2024 使用 *ion adsorption clay type*，2025 版則表述 *fine grained secondary phosphates, not being ionic clays*。這是同一供應商兩版文件的**賦存模型主張衝突**；2025 版明言可能作為未來黃金開採的副產品，所引鄰近 OD6 鑽探不可當作 Scaddan 的 REE 資源或冶金實驗。**兩份原 PDF 位元組／頁面圖仍未取得**；上一批 Scaddan 原件 access HOLD 不變。2025 文字所在 URL 可由網頁索引讀取，不等於網域或 PDF 下載現已復原。

## 案件決策（來源層，不是 Project 核准）

| 來源（固定筆數） | 原件文本新增證據 | 有界決策 |
| --- | --- | --- |
| Johnson Dam（1） | Havilah 2025-09-08 ASX 及 2025-09-16 補充，KKRC0713 48 m @ 211 ppm **Nd（元素）**；以 U 為主的鑽探，未給出礦石 TREO 或 M/I/I 資源 | **鑽探截距範圍已釐清，Project/JORC/Gate HOLD** |
| Ketchowla K2（2） | Archer 2017-01-17 報告 K2 是 Ketchowla Co–Mn 專案內 prospect；K2RC002 33.6% **Mn**、1090 ppm Co；表列 Co/Cu/Ni/Zn/Mn，不能獨立驗證原政府 feature 的 **1667 ppm REE**；2011 報告僅提供多 prospect 的 REE 高值背景 | **歷史母層關係已有原文支持；REE 數值及獨立 Project 核准 HOLD** |
| Victory（2） | Reedy Lagoon 2011-01 公告列 Edward Creek/EL4377 與 Victory，單點 412 ppm U、**0.39% REE+Y**（尚待 fusion 重測），不等於 TREO MRE | **歷史樣品及母層範圍已釐清；資源及現行礦權 HOLD** |
| Mary Kathleen（P2 3） | Queensland Government（網頁最後更新 2026-04-01）確認歷史 U 礦 1982 停採、1982–85 除役及後續尾礦 REE 開發潛力研究 | **2 筆歷史 U 礦來源與 1 筆尾礦候選分開；新 REE 專案/資源資格 HOLD** |
| Scaddan（1） | 2024–2025 同供應商不同 REE 賦存說法；2025 版本指出 fine-grained secondary phosphates、非 ionic clays，兩版均稱 E63/2097 為 2021 年申請 | **新增有界矛盾證據，原件位元組與現行 title HOLD** |

## 來源與原文定位

1. Johnson Dam — [Havilah 2025-09-08 ASX drilling](https://announcements.asx.com.au/asxpdf/20250908/pdf/06nymqc6gml335.pdf) 及 [2025-09-16 ASX clarification](https://announcements.asx.com.au/asxpdf/20250916/pdf/06p912ky1nk88y.pdf)：KKRC0713 段落、表格／competent person explanation。JORC **Exploration Results** 不應改稱 Mineral Resource。
2. Ketchowla — [Archer 2017-01-17 來源](https://announcements.asx.com.au/asxpdf/20170117/pdf/43fc3bmm8tgpwj.pdf)：`Ketchowla Project`、`Summary of drilling results` 中 K2RC002 與 K2RC003。另 [2011-11-25 presentation](https://announcements.asx.com.au/asxpdf/20111125/pdf/422t3wnndyd0xb.pdf) 說明 REE peak 是區域多 prospect 高值，並非 K2 礦量。
3. Victory — [Reedy Lagoon 2011-01 quarterly](https://www.reedylagoon.com.au/wp-content/uploads/2018/07/ASX_11-01-20_10-Q4-Activities5B.pdf) 的 `Edward Creek (SA)`、`Victory prospect`、Figure 2。
4. Mary Kathleen — [Queensland Government remediation project](https://www.qld.gov.au/environment/land/management/abandoned-mines/remediation-projects/mary-kathleen)，`Project snapshot`、`Completed works`，網頁最後更新 2026-04-01。
5. Scaddan — 出售者 [2024-10 PDF](https://onestoptenementshop.com/wp-content/uploads/2021/07/Scaddan-Au-REE-Web-Promo-8-October-2024-B.pdf) 與 [2025-10 PDF](https://onestoptenementshop.com/wp-content/uploads/2021/07/Scaddan-Au-REE-Promo-1Oct25.pdf)，兩者 `RARE EARTHS` 段落及 E63/2097 application 說明。**未封存原 PDF，僅網頁索引提供原文，沒有測定位置、礦物學或溶出實驗交叉驗證。**

## 存取界線、結案和下一批

這一批 `9` 筆為 **substantive source-scope review overlay**，可結束本次已定位的「那份文件能／不能證明什麼」判讀；不能關閉原始 PDF 檔案存取缺口、法律 Project 身分、JORC MRE 或六構面 Gate。舊 339 與 P2 表不覆寫，**原件查核缺口保持**：162 筆 native 待查、P2 25 筆待全文重新核讀、Scaddan 原始位元組未補。批次查核結果與剩餘任務逐筆在兩份 CSV 中可見。

下一批優先查找「有直接原始技術報告編號」的 native 條目並取得可檔案封存的官方 / ASX 原文與頁碼；P2 優先補正 NT 官方 GEMIS 原始報告及來源點位對應。Scaddan 改從出版者取得兩版 PDF、WA 官方礦權 title 變化與同場域的稀土礦物學／可交換比例資料切入，不反覆重試相同失敗網址。

資料檢查：`python scripts/check_external_primary_batch.py` + `python -m unittest discover -s tests -p test_external_primary_batch.py -v`；CI 公開執行的作用是驗證行列結構、來源 join、沒有虛構 hash 或 gate promotion。若不能觀察通過，PR 不合併。
