# Stage 01 · Official Census v1.0.2

正式輸入的 `config/sources.json` 目前包含九個州／聯邦資料來源：

| Source key | 官方資料 | Adapter | 資料層級 |
|---|---|---|---|
| GA_AIMR_REE_2026 | AIMR RareEarthElements (52) | ArcGIS | DEPOSIT |
| GA_CRITICAL_DEPOSITS_2025 | Critical Minerals MineralDeposit (7) | ArcGIS | DEPOSIT |
| STATE_WA_MINDEX | WA MINEDEX (0) | ArcGIS | DEPOSIT; `proj_title` 保存作 project hint |
| STATE_QLD_MINOCC | QLD MINOCC Mineral occurrence (17) | ArcGIS | OCCURRENCE |
| STATE_TAS_MRT | TAS MRT MineralOccurrences (3) | ArcGIS | OCCURRENCE |
| STATE_NT_MODAT | NT MODAT 官方匯出 | CSV | OCCURRENCE |
| STATE_SA_SARIG | SA SARIG Mining Projects / MINDEP | CSV | SOURCE-DEFINED |
| STATE_NSW_MINVIEW | NSW MinView 官方匯出 | CSV | OCCURRENCE |
| STATE_VIC_MINSITE | VIC DataVic MINSITE | CSV | OCCURRENCE |

**必要研究規則**

1. `population_candidates` 保存每筆來源資料，並保存原始屬性和 source-native ID。
2. `PROJECT` 以外的資料維持 REVIEW，不直接增加 `project_master`。若與 project 名稱一致，僅建立可能關係提示。
3. Project identity 比對順序為已存在的 source-native ID、精確名稱＋州別、已登記別名＋州別。25 km 內近鄰屬人工複核，不自動合併。
4. `operator_name` 可記錄官方專案來源所報之公司名稱，未報時保留空值；兩份來源公司不一致時送 Review。
5. 州別優先保留官方報告州別；州與圖層轄區不一致、州與座標粗略界線不一致時進 Review；bbox 非法律州界證明。
6. 官方的物件點是礦床或 occurrence 點，不自動成為正式代表專案座標；必須另經 Evidence Approval。
7. 即便是官方 Project 來源，新加入 Census 也以 `CENSUS_UNVERIFIED` 儲存，不自動核准為可排名 Alternative。
8. 從 ArcGIS REST 擷取使用 Metadata、IDs、完整 Feature chunks、`outSR=4326`、每檔 SHA-256、可恢復的快取。

**執行**

```bash
# 單一 GA 圖層連網刷新
au-ree run --stage population --source-key GA_AIMR_REE_2026 --refresh

# 一次全部已啟用來源
au-ree run --stage population --refresh

# 完全離線重建
au-ree run --through r_export --offline
```

在 iPhone 上可透過 `.github/workflows/population-official-refresh.yml` 的 `workflow_dispatch` 手動選擇來源。工作結束時下載 `official-ree-population-snapshot` Artifact，含 SQLite、逐來源快取、身份稽核與 Review Queue。雲端抓取成功**不代表** Project 身分、公司或歷程已完成獨立核准。

## 本次介面核實依據（2026-10-29）

- GA AIMR RareEarthElements（52）：https://services.ga.gov.au/gis/rest/services/AustraliasIdentifiedMineralResources/MapServer/52
- GA Australian Critical Minerals MineralDeposit（7）：https://services.ga.gov.au/gis/rest/services/AustralianCriticalMineralsOperatingMinesAndDeposits/MapServer/7
- WA MINEDEX： https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Industry_and_Mining_WFS/MapServer/0
- QLD Mineral occurrence： https://spatial-gis.information.qld.gov.au/arcgis/rest/services/GeoscientificInformation/MiningResources/MapServer/17
- TAS MineralOccurrences： https://data.stategrowth.tas.gov.au/ags/rest/services/MRT/GeoscienceWFS/MapServer/3
- NT MODAT 入口：https://data.nt.gov.au/dataset/strike---northern-territory-mineral-occurrences
- SA SARIG WFS 服務入口：https://www.energymining.sa.gov.au/industry/geological-survey/products-and-services/map-viewers-databases-and-services/data-services
- NSW MinView：https://www.resources.nsw.gov.au/geological-survey/minview
- VIC MINSITE：https://discover.data.vic.gov.au/en_AU/dataset/mines-and-mineral-occurrence-sites

備註：已核實公開端點及資料欄位名稱，但本執行環境無外網 DNS，因此 API 連線及真實批次下載尚未在此環境通過。狀態必須以 GitHub Actions 之官方擷取紀錄為準。
