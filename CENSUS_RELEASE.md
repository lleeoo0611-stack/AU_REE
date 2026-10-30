# 487筆母體全量追溯審閱（2026-10-30執行；來源截止2026-10-29）

441筆原未連結紀錄全部保留原ID並建立逐列查核紀錄；309組名稱＋州別查詢共用搜尋紀錄，不能據此推定同一專案。17組正式來源關係審閱支持32筆新增候選，故全母體為69筆候選、6筆稀土角色待查、412筆專案身分／稀土角色證據不足。78筆已有審核群組對應（69候選＋9HOLD），409筆仍未連結；39個審核群組中32個為納入候選群，均非最終核准專案數。未執行MCDA。

原95筆來源對應76個不同URL；64筆有具體文字位置，13筆取得內容但無直接專案定位，18筆未取得可用內容。95筆保留原列序及5筆重複證據ID；PDF頁碼採實體頁序，HTML採封存文字行號，不能當作原網頁永久行號。泛用入口、失效來源及搜尋摘要均不當成已證明五條件的證據。另執行12組失效來源替代查找。瀏覽文字封存並非原始PDF／HTML位元組。

原生資料核對採各來源指定ID欄位：407筆唯一命中、2筆同一ID多個原始資料列（OLYMPIC DAM、CLARKE）、32筆未找回精確原生紀錄。多列原始值全保留，未以年份或其他非ID欄位匹配。

公司／礦權部分保留8筆具體審閱事件（更名、已披露收購、交易提案、條件式礦權延展及來源衝突）與文字定位線索。39個專案群的完整現任法律持權鏈仍未核實，全部在權利鏈缺口表維持HOLD；不把公司股權、計畫取得權益、礦權持有人及營運商視為同一角色。Yangibana舊公司頁與較新交易揭露的權益比例線索有衝突，尚未據此更新現任權利人。

## 核對表

- unlinked_441_source_trace.csv：441筆五條件、原生ID／文件hash、搜尋紀錄與缺口。
- source_evidence_locator_review_95.csv：95筆來源定位及無法定位原因。
- reviewed_project_relation_changes.csv：32筆候選關係變更及依據。
- reviewed_company_rights_events.csv／project_rights_history_review.csv：具體事件與39個群組的持權鏈待查狀態。
- AU_REE_487_pre_MCDA_five_definition_review.xlsx：32頁籤可編輯核對表。

## 離線重建

解壓縮本交付包，使用Python標準函式庫執行：

```powershell
python reproducibility/build_census_database.py rebuild --snapshot-dir portable_snapshot --output restored.sqlite
python reproducibility/build_census_database.py verify --snapshot-dir portable_snapshot --database restored.sqlite
python reproducibility/build_census_database.py csv-build --csv-dir deliverable --output rebuilt_from_csv.sqlite --as-of-date 2026-10-29
```

快照還原以schema、逐表列數及邏輯雜湊為準；SQLite檔案位元組可能因版本／插入順序而不同。同環境CSV重建應重現發佈DB雜湊。完整本地快照保存原政府擷取ZIP；可攜包不重複包含這三個大型原始ZIP，其雜湊列在manifest中，並清楚標為未隨包提供。原始四個歷史決策檔仍只有邏輯重建，並非位元組還原。

完整來源更新流程需在保留原工作包上執行rebuild_all.py；新來源必須建立新快照ID，不覆寫舊版。網路查詢結果、人工審閱關係和原始資料均凍結，重建不會重新搜尋網路。來源不足保留HOLD；本輪完成的是全量查找、可取得來源審閱與逐列裁定紀錄，並不聲稱所有文件、完整公司沿革或法律持權鏈已查清。

發布的衍生CSV、資料庫及可攜證據副本已移除URL憑證參數。原始輸入未改動；可攜副本如經遮蔽，manifest同時記錄原雜湊與衍生副本雜湊。原始政府擷取ZIP與礦權查詢SQLite保留在本地完整快照，不隨GitHub可攜包發布。
