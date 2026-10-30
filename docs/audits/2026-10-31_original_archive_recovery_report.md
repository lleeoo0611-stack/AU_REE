# P0 — 原始政府來源復原與 Project–Deposit 身分審查（2026-10-31）

**母體快照：2026-10-29；稽核：2026-10-31。** 全部 487 target_id、原 39 review groups、C0/C1 邊界、正式核准資料不變。

本次直接取回 GitHub Actions 工作流程 [Australia-wide raw mineral archive，run 40821122179](https://github.com/lleeoo0611-stack/AU_REE/actions/runs/40821122179) 的 **`australia-national-unfiltered-raw-inventory` artifact ID `12874618255`**（含原始 ArcGIS feature JSON、WFS GeoJSON、SA CSV 與 SHA-256 manifest），核對 **376 個原始資料檔（132,450,625 bytes），SHA-256 全數符合、0 個失敗**；並重新檢查原生 source ID，而非使用新的模糊名稱搜尋推定身分。

## 檢查結果

| 判讀面向 | 逐筆結果 | 後續資料庫處置 |
| --- | ---: | --- |
| 原「僅有 native 礦產紀錄」| **272/272 精確找回原始政府 source feature** | 繼續 C0 地質實體；原生特徵可追溯 |
| 原「原始資料缺失」— GA | **7/7** 找回 2026-10-29 的 ArcGIS feature JSON，含原始位元組 SHA、feature index | 恢復原始圖徵定位 |
| 原「原始資料缺失」— Legacy | **16/16** 在 Git 保留的 `inputs/legacy_r963_census.csv` 中精確找到州別＋名稱原始列 | 恢復歷史來源列；原始 `project_id` 非空且逐筆與 `LEGACY:UUID` 完全一致；屬歷史內部 ID，並非政府 native ID |
| SA 原 native deposit ID 歧義 | **2 個礦床 ID 對 10 個 source features**；以 snapshot `OBJECTID`＋`FID` 識別各原始列 | 10 個來源列保留；資料庫只計 **2 個礦床實體**，不多建 Project |
| 272 個 native source 的直接 Project parent | **0** | 地質來源沒有足以核准獨立開發專案的 parent key |
| Native 給的是 *地質 parent/group* | **4**（TAS 2、QLD 2） | 保留 C0 上層地質關聯，不能充當 Project |
| 額外已審閱的跨來源 Project 親子候選 | **6 筆來源列／4 個 Project 名稱** | Narraburra、Milo 可進 REE Project 身分複核；Peculiar Knob、Carrapateena 僅支持非 REE 專案來源對應 |

原先標成 **Victory Downs native 重複**，經檢查 SA GEODATA 檔案 Windows 編碼、避免 UTF-8 失敗時將部分列重複產生後，正式結果是 **272/272 單一原始 feature**。已更新 [272 筆完整清單](2026-10-31_272_native_project_scope_triage.csv)，不保留已排除的解碼假重複。

### 1. 272 個地質實體的來源核對

[可編輯的 272 筆 CSV](2026-10-31_272_native_project_scope_triage.csv) 保存 target_id、州別、來源名稱、政府 native identifier、原始資料快照定位、來源 entity 類型、上層關聯性質與 C1 待審理由。

原本 272 筆的地質實體分布是 Deposit 192、Occurrence 73、Prospect 4、Historical Record 3。這些是 **source entity**，因此即使原始政府紀錄精確可查，也不能直接把每個礦床當獨立 REE mining Project。

原始資料中 **268 筆未列有 Project parent key**，另有 **TAS Livingstone Creek A、Leach Scrub** 的 geology parent ID，以及 **QLD Milo、Florence Bore South Target 1** 的 geological group name 共 4 筆，均保留 `source_parent_relation`，不能升格為 Project parent。

依州別：SA 94、WA 81、NSW 40、NT 19、VIC 14、QLD 13、TAS 11。

### 2. 原先 23 筆 native source 不可追溯

[23 筆逐筆恢復表](2026-10-31_23_native_source_recovery.csv) 提供原始位元組或原始列定位。

- GA 原始檔 `national_raw/arcgis/GA_AIMR_REE_2026/be41683aff317735a685/features_0000000.json`，SHA-256 `3d5c448f23cbf5d9c0dc1169640f78aac820f4ce4ccb1057fb337abd082037dc`；7 筆原 `GA_AIMR_REE_2026` 的 entity_id 和原始 array index 重新確認（Gascoyne、Rodds Peninsula、Inskip Point、Round Hill Head/Deepwater、Thunderbird、Wild Cattle Island–Hummock Hill、Hat Head）。
- Legacy 16 筆依 [frozen historical census](../../inputs/legacy_r963_census.csv) 原始州別＋完整名稱各對應 1 列；原始 `project_id` 欄位具有 16 筆唯一 UUID，且各自與穩定的 `LEGACY:UUID` 完全相符，因此列為 `LEGACY_ORIGINAL_ROW_AND_ID_RECOVERED`；這些是歷史資料庫 ID，非政府來源 ID。

這兩種「source row 已恢復」並不等於 Project 法律身分、現行開發資格或 JORC MRE 成立。

### 3. Olympic Dam、Clarke：source ID 歧義解決

[10 個原始 source features 對照表](2026-10-31_sa_10_duplicate_source_features.csv) 逐列記錄 `MINERAL_DEPOSIT_NO`、`OBJECTID`、`FID`、主要 commodity 及依內容分類的 semantic group。

SA 原始 CSV `national_raw/sa_projects/SA_CRITICAL_REE.csv` 的 SHA-256 為 `4064f29eb934689606d5d4fa02f61e70c726c931752aaf1fd0a355adbc3c9fbc`。

- **Olympic Dam，MINDEP 3000**：`OBJECTID 13–16` 共 **4** 個圖徵；第 13 筆帶礦石／母岩層資料，其餘三筆缺該組地質欄位，形成兩個語意群組。主商品均為 Cu。
- **Clarke，MINDEP 11849**：`OBJECTID 56–61` 共 **6** 個圖徵；56–58 主要商品 Au，59–61 主要商品 REE，形成兩個語意群組。

源資料唯一性鍵使用 **`source_key + mineral_deposit_no + snapshot_objectid`**，且保存原始 `FID`；在 Project/Deposit 主體層仍維持各自一個礦床 ID。此處完成的是**來源 feature 的辨識**，與研究中專案核准分流。

### 4. 已有的 6 個跨來源親子候選

[6 筆可編輯候選關聯](2026-10-31_272_project_parent_candidates_6.csv) 中：

- **Narraburra Rare Earths Deposit → Narraburra REE Project**：issuer 2026-05-22 文件和 NSW 官方產業清單有名字／資源定位，尚須 Project boundary 和有效日期核准。
- **Milo → Milo Uranium-Copper-Gold-REE Project**：發行人已將 Milo 作為有 REE 的 Project 描述；尚須對應原礦點與現行開發主體。
- **Peculiar Knob (MINDEP 3010) → Peculiar Knob mine**：SA developing/major government project，主商品鐵礦，REE 資源開發角色未成立。
- **Carrapateena (MINDEP 8303) → Carrapateena mine**：SA government project，以 Cu/Au/Ag 為主；當前來源未支持單獨 REE product unit。

四個 SA 來源列映射到後兩個非 REE Project，不納入 REE development-potential MCDA。外部候選共 6 筆，剩餘 **266 筆沒有已記錄的獨立 Project parent 候選**；沒有新增正式 C1 核准。

## 重跑與版本控制

- 原始政府封存不必改寫或重新下載，可在 GitHub Actions 的 run 40821122179 取得；解壓後 `national_raw/` 下包含官方原始 JSON/CSV 及 `national_raw_manifest.json`。
- 用 `scripts/validate_p0_raw_recovery.py` 執行一致性檢查，對 ArcGIS、WFS 和 SA 原始檔驗證 SHA-256、所有 272 native keys、7 GA 原始 feature、16 Legacy 原始 row、SA 10 筆 source feature。
- 所有 source-level 識別、原始證據與 Project 身分簽核分開；GitHub 的正式 Project、JORC、GIS、MCDA outputs 不受這次變更影響。

```bash
python scripts/validate_p0_raw_recovery.py
python scripts/validate_p0_raw_recovery.py \
    --raw-root work/national_raw \
    --output work/evidence/p0_raw_recovery_verification.json
python -m pytest -q tests/test_p0_raw_recovery.py
```

本研究的 Project census 可保留全部地質來源紀錄並明確註記 C0；進入正式 C1 前仍需 **Project-level primary source + REE role + scope + signoff**，避免把原生礦點與發展計畫的生命週期混合。
