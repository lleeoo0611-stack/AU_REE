# 144 HOLD：原始文件與實體範圍審查（2026-10-31）

Execution: `P234-144-PRIMARY-SCOPE-20261031-V1`
Repository: `lleeoo0611-stack/AU_REE`
Branch: `audit/p234-144-primary-scope`
Base: `f327a4e5ab31d1e206642921f1cdacc2a4df8e59`（PR #40）
Fixed source snapshot: **2026-10-29**；新增文件取得／網頁觀察日期：**2026-10-31**。

本批對前次 144 個文件指標 HOLD（P3 118、P4 26）補做相關原始頁面與範圍判讀。142 筆讀到本機保存的原件，1 筆只讀到網頁呈現的原始 PDF，1 筆仍未讀到原件。這是 144 筆的本階段逐筆處置，**不是 144 筆全部技術原件查核完成，更不是 Project 或 C1 核准**。每筆均保留後續範圍／礦權缺口。

412 個 HOLD 的固定 ID 不變；本批僅更新其中 144 筆的 documentary disposition。P2 28 筆／27 案、P1 73 筆及其他 167 筆 P3/P4 的前次判讀不改寫。原始 339 筆帳本保持不動，另產生 339 筆最新處置對照。C1、13 案 Gate、JORC 正式核准及 MCDA 均暫緩，未寫入任何核准簽章。

## 覆蓋與限制

| 本批查核結果 | 來源筆數 |
|---|---:|
| 以本機原件 SHA、相關 PDF 頁／HTML 內容驗證 | 142 |
| Scaddan：網頁讀到 PDF 頁，原檔未保存／真實性未獨立核定 | 1 |
| Yellowband Plain：原件存取受限，未做內容結論 | 1 |
| 合計 | 144 |

142 筆使用 48 份不同的本機原件，Scaddan 為第 49 份不同文件；98 筆 PDF、44 筆 HTML、1 筆網頁 PDF、1 筆無可讀原件。紀錄的是相關頁面閱讀，不聲稱每份報告全頁人工通讀。GA 檔案本身只有參考文獻與附錄，不能稱為整本 GA 報告。Benmara North 為掃描原件，只人工讀封面及摘要頁（PDF 1、4），未宣稱 OCR／全文檢索完成。

另外 7 筆已讀到替代原始文件，但原指標文件仍未取得：Quantum 兩筆、Stronach、Yellowband Creek、Naracoopa、Rubble Flats、Mindarie。連同 Scaddan 與 Yellowband Plain，共 **9 筆**列入 `remaining_access.csv`。這 9 筆只表示原指標／原始檔取得缺口，不能解讀為其餘 135 筆已充分核准；其餘各筆仍有 `remaining_gap`。

## 分批原件查核的實質結果

1. **GA 附錄與歷史重礦砂表**：辨識礦床／strandline 與 Project、現行礦權的差別。Four Acres 的先前附錄指標未支持目標名稱，僅否定此引用範圍，不能推論礦床不存在。Byfield 與 Cooljarloo 的文件點與凍結來源點各差約 6.877／6.205 km；61 筆保留距離比較，皆不作身分核准或礦界推定。
2. **CSIRO EP14184 原件（PDF 109、117、118、120）**：9 筆來源取得實際歷史表格。Pooncarie、Ginkgo/Snapper、Jacks Tank North/South、Coombah 1/2 及不同運營者表格須分開。歷史 ore/HM 數值與礦物組成不是 TREO，群組總量不能分配到每個來源；重複名稱不能直接合併 Project。官方目錄文字的報告號與原件標題不一致時，以實際 EP14184 原件與 SHA 留存。
3. **SA 政府原始登錄內容（34 筆）**：逐一核對原生 MINDEP ID、Details、Location、Commodities、References。Kalkaroo West 正確 ID 是 9629；舊 URL 8455 是另一個 Kalkaroo 紀錄。Olympic Dam 的 REE 經濟性敘述、Morgans Creek 的 Occurrence／試驗／截距、Port Pirie 的歷史處理場、Clarke 的 gold Prospect、Fremantle Doctor 與 Carrapateena 的分離，均落入逐筆判讀。當日 live HTML 不能倒推 10 月 29 日網頁內容，也不能把 Cu/U/Fe 資源改稱 TREO。
4. **NT 遷移後的真正 ORIGINAL 報告**：舊 DSpace 頁面只有程式外殼；改由官方 API 精確核對 handle／原檔名，取得 10 份原始報告。Holsteins 只是 Undippa 報告內其他區域例子；Stromberg 與報告 licence 範圍不同；Charley Creek South 與南方 Crossland 資源不同；NT Browns Range 不得繼承 WA Wolverine 資源。Benmara North 的 1991 年 gold stream-sediment 工作不能替代後來 V/REE 目標的技術證據。日期矛盾／報告礦權編號疑似筆誤保留於判讀。
5. **公司／政府 Project 原件**：Newmont 123 Mt 與 O’Connor 107 Mt 不能各自繼承合計 230 Mt；Glenmorangie 探勘孔不等於 Salazar MRE。WIM100 原始 EES 明列 Wimmera 關係，但環評研究區不等於礦界。Eneabba stockpile、concentrator、refinery 與供料礦分開。Elaine-Dorothy 的小型歷史 U-REE 資源不能換成後來較大 Cu-Au 資源。Toongi 的正確公司頁與早先第三方公眾提交文件分開。部分公司原件僅在其他主機取得，另保留真實性缺口。
6. **Alluvial Flats 與 Scaddan**：Wind Break 原始 EDGI 報告（PDF 1、8、15、23、27）把 Alluvial Flats 列為五個富集區之一，並提及混合 clay／detrital 模型；不等於 Wind Break 或 Rubble Flats，不能分配整體 89 Mt。Scaddan 的宣傳 PDF（1、5、6）描述 E63/2097 申請、REE 土壤異常及未分析 REE 的 gold drilling；不能繼承鄰近 OD6 資源或視為已核定礦權。

上述結果均為文件所支持的有界判讀；未找到現行礦權或未支持某個資源移轉，不等於證明沒有 REE／沒有礦床。

## 可編輯與可追溯產物

- [144 筆人工判讀輸入](../../inputs/source_review_20261031/p234_144_primary_scope_adjudications.csv)：固定 `target_id`、原件 ID、頁碼／章節、短核對錨點、實體關係、REE 計量基礎、文件礦權、逐筆處置及缺口。
- [144 筆結果 CSV](2026-10-31_p234_144_primary_scope_review.csv)／[JSON](2026-10-31_p234_144_primary_scope_review.json)：補入原件 SHA、頁面文字 SHA、實際 URL、閱讀方法、來源點差異、取件錯誤。
- [339 筆最新處置對照](2026-10-31_p234_144_primary_scope_updated_339.csv)：195 筆非本批處置保持前次結果。
- [9 筆存取缺口](2026-10-31_p234_144_primary_scope_remaining_access.csv)；[統計及輸入 SHA](2026-10-31_p234_144_primary_scope_summary.json)。
- [公開原件證據索引](../../data/document_snapshots/2026-10-31_p234_primary/README.md)：取件 manifests、精確原件／頁碼綁定、保留在本機的完整原件位置與公開重跑的限制。
- [可編輯取件 URL／ID 表](../../inputs/source_review_20261031/p234_144_document_requests.csv)；[Scaddan 網頁閱讀紀錄](../../inputs/source_review_20261031/p234_web_original_review.json)。

公開 Git 保存來源、雜湊、頁碼與有界判讀。完整第三方 PDF／HTML 保留於本機研究封存，不將明載重製限制的全文散布至公共 repository。`reviewed_content_evidence.json` 是本機相關頁驗證後的研究紀錄，**不是獨立審核簽章**。

## 重跑與驗證

```sh
python -m pip install pypdf==6.10.0
# 公開 checkout：重算帳本、檢查既存頁碼／雜湊綁定，不能重新讀取不存在的原件。
python scripts/review_p234_144_primary_scope.py --check
python -m unittest discover -s tests -p test_p234_144_primary_scope.py -v
# 原件仍在本機：要求每個 DOC 原檔存在，重驗 SHA 並讀取所引頁面。
python scripts/review_p234_144_primary_scope.py --check --verify-originals
```

新增原件時，使用 acquisition／GEMIS resolver 產生**新的**取件 manifest，不覆蓋舊取件紀錄；填寫固定 ID 的判讀 CSV，將新 manifest 加入重跑清單，閱讀內容後才執行 `--seal-evidence`、`--write`。舊版證據在 Git 歷史保留。若原件被修改、頁碼／錨點／MINDEP ID 或 table context 改變，須重新提供並驗證真正原件，不能直接用取件成功代替審查。

測試涵蓋固定 144／339 ID、195 筆不變、SHA／頁碼／錨點／政府 ID／座標表列錯配、空 SPA、無原件的公開 checkout 重跑，以及禁止新增核准。CI 檢查研究紀錄的可重現性與程式防錯；**CI 不會冒稱重新閱讀未公開的第三方全文**。

## 仍須處理的證據

Yellowband Plain：UR2012_03 原件與替代 AR1927 存取受限，保留未完成內容查核。其餘 8 筆存取缺口依表補原檔／原指標；所有來源的精確 Project footprint、現行 title chain、同範圍 REE 技術資源與獨立核准仍依逐筆缺口處理。本次未授權 C1、13 案 Gate 或 MCDA，故不以此查核產出改寫正式核准。
