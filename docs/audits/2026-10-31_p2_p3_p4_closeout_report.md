# P2／P3／P4：固定來源證據處置與限定結案

執行 ID：`P234-DOC-CLOSEOUT-20261031-V1`。基線：`main@aeddd2e`；分支：`audit/p2-p3-p4-documentary-closeout`。政府資料日期：2026-10-29；本次整理日期：2026-10-31。計量單位是 **source target ID**，不是獨立 Project。

## 本輪可結案的範圍

完整檢視固定 339 個來源的原生內容、身分鍵、歷次判讀與缺口，給每筆一個 terminal documentary disposition。這裡的 terminal 是本輪證據處置的終點，**不是全部外部技術文件已驗證，也不是已證明 Project 存在或不存在**。

| 批次 | 原始來源筆數 | 本輪處置 |
| --- | ---: | --- |
| P2 | 28／27 暫定案例 | 保留前輪限定公開桌面判讀，補原始 UUID／政府圖徵核對及完整 lineage |
| P3 | 216 | 98 筆原生紀錄審查完成、118 筆文件指標待原件／範圍審查 |
| P4 | 95 | 69 筆原生紀錄審查完成、26 筆文件指標待原件／範圍審查；保留 Occurrence |
| 合計 | 339 | 每筆有來源位置、內容事實、歷次證據、終端處置與再開案條件 |

固定母數仍為 **412 = P1 73 + P2 28 + P3 216 + P4 95**。P1 不改；舊 action_priority=P2 的 72 筆不另加進來。C1 正式准入、13 案 Gate、JORC／GIS 核准與 MCDA 均暫緩，未修改任何核准。

**驗收狀態：來源內容／處置覆蓋 PASS；外部原始技術文件完整驗證 PARTIAL，不能宣稱全部完成。** 本輪新增技術文件全文驗證 0、新 Project／C1 核准 0。144 筆文件指標 HOLD 是明確未完成的原件工作，不以結案措辭抹除。

## 原始證據核對方式

從原 GitHub Actions [run 40821122179](https://github.com/lleeoo0611-stack/AU_REE/actions/runs/40821122179)（artifact 12874618255）的本機保留副本讀取原始政府 JSON／GeoJSON／CSV。先驗證 ArcGIS manifest 及 chunk SHA、WFS／SA manifest chunk SHA，再依 **source key＋native ID** 精確選取，不做模糊名稱或鄰近點接合。

- **317 個來源**有政府原生圖徵內容：保存原屬性、幾何、原始 chunk SHA、feature／CSV row locator；原生 commodity、entity、resource flag、地質 parent hint 與 report references 另抽成可讀事實。這是結構化政府原始紀錄內容檢視，並非原始技術 PDF 全文閱讀。
- **22 個來源**只具有 Legacy 原始列：逐筆依 UUID、州別與原始名稱核對，不冒充政府 native ID。
- 全部 **52 個 Legacy target IDs**另保存歷史 UUID 原列；其中 30 筆同時有政府來源。Legacy target ID 和政府 native ID 是兩個層次，均保留。
- 擷取共 339 個 target、347 個對應 feature／歷史列；SA 兩筆原生 ID 各有 4／6 個 feature，因此不能要求每個 target 只對一個原生 feature。

[選取資料 JSONL](../../data/source_snapshots/2026-10-29_p2_p3_p4_selected_features.jsonl)是經驗證的**衍生原生紀錄選集**，不是原始 chunk bytes 本身；[選取 manifest](../../data/source_snapshots/2026-10-29_p2_p3_p4_selection_manifest.json)記錄原 archive manifest SHA、所有使用 chunk SHA 與選集 SHA。重跑 `--check` 只驗證選集完整性與結果再生；如需重新證明原始 chunk bytes，須重跑 `--extract-raw --raw-root`。原封存與舊審查表均保留原樣。

## 更正舊狀態與保留實體關係

1. 舊第二輪將 Gascoyne、Rodds Peninsula、Inskip Point、Round Hill Head/Deepwater、Thunderbird、Wild Cattle Island–Hummock Hill、Hat Head 列為未恢復。本輪從原始 GA 圖徵精確找回這 **7 筆**；新表保留舊狀態欄位與新來源處置，避免歷史資料被悄悄覆寫。
2. SA_CRITICAL_REE 的 Olympic Dam（3000）保留 OBJECTID 13–16，Clarke（11849）保留 56–61。這是 **2 個原生 deposit IDs／10 個 source features**，不是 10 個 Project；SA_GEODATA 的同礦床紀錄也不刪除。
3. 同州同名候選保留全部 487 母表對應 ID，僅作待查關係，不能據名稱自動合併。Project、Deposit、Prospect、Occurrence、歷史場址與公司／持權人不互換。
4. 保留原 2026-10-29 來源點位、tenement intersection count 和 titleholder 查核狀態。點位在礦權內不證明 Project 開發區界，也不證明現行持權、開發者或營運者一致。本輪未取得新法律 title chain 或新 Project polygon。
5. Bruce／Plenty River、Mary Kathleen mine／tailings、Talisker／Salazar 等既有關係與禁止資源繼承的限制，保存在完整歷次 CSV records 中；不把同名資源、HM／THM、地質 REE 清單或探勘截距視為 Project TREO MRE。

## 逐筆 documentary disposition

### P2：28 個來源、27 個暫定案例

沿用既有 `p2_28_public_terminal_desk_review` 的限定判讀與缺口，沒有在本輪假裝重新取得原件：17 筆政府／發行人線索、4 筆歷史場址、1 筆研究未含 REE、1 筆指定鑽探 REE 負結果、3 筆僅政府 feature、2 筆區域索引／名稱衝突。**4 筆歷史來源是 3 案**，因 Mary Kathleen mine 有兩個 source rows。個別負結果只限被測試標的與文件範圍，不是整個地區不含 REE。

### P3／P4：311 個來源

- **167 筆 `C0_NATIVE_RECORD_REVIEW_COMPLETE_PROJECT_UNRESOLVED`**：完成原生政府紀錄內容與已封存審查紀錄的限定檢視；沒有足以核准獨立 Project 的證據。結案範圍是 C0 原生紀錄，不宣稱已窮盡外部文獻或專案不存在。
- **144 筆 `HOLD_DOCUMENT_POINTER_REQUIRES_PRIMARY_SCOPE_REVIEW`**：既有紀錄包含外部文件指標，保留原 URL、定位、日期、支持的主張與各輪 scope；尚須取得／核對原件及來源到 Project 的範圍。不能以「有 URL」提升為全文驗證。

原本 194 筆／117 筆只是「是否在 272-native 子快照內」的分類，不再作為原件可追溯性的上限。本輪對全部 317 個政府來源重新從完整封存選取，不因不在子快照而將來源判為不存在。

## 可編輯成果、欄位與重跑

- [339 筆 CSV](2026-10-31_p2_p3_p4_closeout.csv)：可篩選 priority、native entity、REE role、同名候選、地理／礦權限制、結案狀態與再開案條件；`documentary_references_json` 保留 URL／日期／locator。
- [339 筆完整 JSON](2026-10-31_p2_p3_p4_closeout.json)：每筆附原生內容與第二至第六輪及 P2 的完整歷史 row。衝突／缺口保留，不用較新的分類覆蓋較早的主張。
- [144 筆文件指標 HOLD CSV](2026-10-31_p2_p3_p4_closeout_document_pointer_holds.csv)：下一輪原件範圍工作清單，118 筆 P3、26 筆 P4。
- [摘要與輸入 SHA](2026-10-31_p2_p3_p4_closeout_summary.json)：分母、批次處置、來源 hash、執行 ID 及驗證限制。

`frozen_source_review_complete=YES` 只指固定來源內容與既有紀錄檢視；`technical_primary_fulltext_verified_this_run=NO`、`evidence_sufficient_for_project_approval=NO` 分別記錄全文驗證與核准證據狀態。不可只讀第一欄便稱正式准入。

CSV／JSON 可以編輯研究註記，但發布檔必須與來源再生一致。新增判讀應先修改對應 `inputs/source_review_20261031/` 的 evidence input，再重新產生；新增原件須另存新快照與 SHA，不直接更改凍結選集。

```bash
python scripts/closeout_p2_p3_p4.py --check
python -m unittest discover -s tests -p test_p2_p3_p4_closeout.py -v
python -m pytest -q
# 可選：持有原完整 archive 時，重新核對全部相關原始 chunks
python scripts/closeout_p2_p3_p4.py --extract-raw --raw-root /path/to/national_raw
```

CI 檢查可重現性、分母、原生 ID／Legacy UUID 反例、SA 一對多、禁止同名合併、文件 URL 不等於原件驗證。CI 通過只證明這些資料／程式契約，不會使 documentary HOLD 或任何 C1 Gate 自動核准。
