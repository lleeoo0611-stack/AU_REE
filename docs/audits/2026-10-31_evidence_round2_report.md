# P0 第二輪：487 筆來源證據補強與缺口縮減（2026-10-31）

**本輪成果**：[487 筆完整審核 CSV](2026-10-31_487_evidence_round2_review.csv) · [86 筆證據異動紀錄](2026-10-31_evidence_round2_changed_targets.csv) · [計數與來源 Manifest](2026-10-31_487_evidence_round2_summary.json) · [可編輯來源與定位登錄](../../inputs/source_review_20261031/round2_external_evidence_leads.csv) · [重跑程式](../../scripts/review_p0_evidence_round2.py)。

本輪保留 2026-10-29 的 **487 個來源 target_id**、原始第一輪證據分級、既有 39 群組關聯及正式 C1 Gate。新增外部官方/公司文獻、可定位的名稱／段落與下一步關聯依據，未覆寫歷史輸出或已核准資料。

## 1. 真正的 Before / After

| 舊有問題 | Round 1 | Round 2 尚無額外文件線索 | 新增文件線索 |
| --- | ---: | ---: | ---: |
| `NATIVE_RECORD_ONLY` | **336** | **272** | **64** |
| `SOURCE_RECORD_NOT_RECOVERED`（無原生資料亦無可定位文件） | **23** | **3** | **20** |
| `AMBIGUOUS_NATIVE_ID` | **2** | 0 筆仍毫無官方額外上下文 | 2 個 ID 取得官方資料，但原生來源多列歧義 **仍 2 筆** |
| **總計** | **361** | **275 個未新增文件的紀錄** | **86 個有新線索的 target** |

**證據分級提升不等於 Project 通過 Gate**。所有 487 筆繼續 `approved_for_C1=NO`；原來的 **23 個未恢復之原生快照仍未恢復**，只是其中 20 筆多了能定位的外部 PDF 或政府紀錄。兩筆有重複 feature rows 的原生 ID 仍需 source-row discriminator。

64 個原生資料紀錄的新增依據按支持層級分為：

- **23 筆**：歷史政府地質報告交叉定位（例如 QLD/NSW 海岸重礦砂、部分 WA 重礦砂礦點）；此證據確認 *geological record context*，不表示有可開發 REE Project。
- **6 筆**：西澳 2026 年官方 REE Mineral Resource 總覽，可核對 Project 名稱與資源總表，但獨立 JORC Statement 範圍和日期仍須核定。
- **35 筆**：政府或公司 Project/Prospect 文件（包括礦砂、REE 勘查或非 REE 主產品），記錄 REE role／parent scope，不能從文字中自動推定 C1 納入資格。

## 2. 20 個原先欠缺來源定位的逐件改善

**Geoscience Australia 2011** [The Major Rare Earth Element Deposits of Australia](https://www.ga.gov.au/bigobj/GA19665.pdf)，Appendix / coastal mineral sands tables 為 Rodds Peninsula、Inskip Point、Round Hill Head/Deepwater、Hat Head 提供地質位置和礦床性質。Wild Cattle Island–Hummock Hill 的原始複合名稱對應報告中**兩個名稱**，保留拆分檢核，不把它們視為一個正式 Project。

**Northern Territory**： 
- [Blueys Folley, GEMIS EL28029](https://www.geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/91056) 對應舊稱 Blues Folley
- [Arthur Popes, GEMIS EL24646](https://www.geoscience.nt.gov.au/gemis/ntgsjspui/handle/1/74268) 證實 REE/Y 富集脈體及 Prospect 性質
- [Bruce Project EL31225 2023 report](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/92857/1/EL31225_2023_C_01.pdf) 提供 Bruce Prospect 與計畫背景
- [Edwards Creek，NT authorised sites](https://nt.gov.au/__data/assets/pdf_file/0004/256144/authorised-mining-site.pdf) 有 MetalsGrove、REE 勘查項目的政府清單

**其他來源：**[Elaine Dorothy, AuKing 技術揭露](https://www.aukingmining.com/site/pdf/69270e44-d780-40f0-9aec-b1e695241a0e/CuCoREEU-Mineralisation-at-Elaine-Dorothy-Project.pdf)；[ABx Deep Leads/Rubble Mound 政府投資項目](https://www.australiaminerals.gov.au/projects-and-exploration/ABx-Group-Investment-Fact-Sheet.pdf)；[MRT DC Target 探勘報告](https://www.mrt.tas.gov.au/exploration/exploration_drilling_grant_initiative_edgi_results/round-9-edgi-results)；[WIM Wedderburn](https://wimresource.com.au/project/)；[ACDC Douglas](https://acdcmetals.com.au/projects/victorian-projects-rare-earths-mineral-sands/)；[Intergroup Brumby Clydesdale 2025 Scoping](https://intergroupmining.com/wp-content/uploads/2025/02/IGM-BC-Scoping-Study-2025-v1.pdf)；[MinRex Talisker 2025 ASX](https://announcements.asx.com.au/asxpdf/20250814/pdf/06mvmb9r2vhdhs.pdf)；[Northam Mt Joy–Bolgart 2022 prospectus](https://northamresources.com/wp-content/uploads/2022/11/NRL_Prospectus2022_FINAL-DRAFT_28Oct2022.pdf)。

**部分名稱需保留層級差異：**Bells Monazite 的候選歷史來源 [NT EL2193](https://geoscience.nt.gov.au/gemis/ntgsjspui/bitstream/1/61444/1/CR19870124.pdf) 記錄的是 *Bells Mona* Sn/Ta pegmatite；可用於確認可能名稱來源，**不能宣稱已發現 Bells Monazite REE Project**。Mt Joy–Bolgart–Northam JV 的 composite name 在 [Northam prospectus](https://northamresources.com/wp-content/uploads/2022/11/NRL_Prospectus2022_FINAL-DRAFT_28Oct2022.pdf) 中只部分對應 Mt Joy/Bolgart，仍須核對原有 JV 身分。

## 3. 兩筆 native ID 歧義：已補來源，尚待唯一列識別

| 原始 target | 原生 identifier | 原 source rows | 新證據與判定 |
| --- | --- | ---: | --- |
| **OLYMPIC DAM (SA)** | `SA_CRITICAL_REE:3000` | **4** | [SARIG MinDep 3000](https://minerals.sarig.sa.gov.au/MineralDepositDetails.aspx?DEPOSIT_NO=3000) 確定 Olympic Dam 為同一政府礦床編號，REE 雖存在但現有礦石 REE 未經濟回收；4 列仍須建立不同 source-feature key |
| **CLARKE (SA)** | `SA_CRITICAL_REE:11849` | **6** | [SA 2026-06-25 developing resource list](https://map.sarig.sa.gov.au/CrystalRunner/Report/Export/2?exportName=DevelopingProjects) 將 Clarke 與 Baggy Green 放在 Wudinna 資源範圍；6 列尚未證明可唯一化為礦權／commodity／feature scope |

這是**礦床身份資料與 source feature 兩層問題**。目前知道 Olympic Dam 的 MinDep 3000 有官方可查標識，但不能因此將 4 列視為 4 個 Project 或自動壓成 1 個 observation。Clarke 同理。

## 4. 剩餘缺口清單

**尚無確認文件定位的 3 筆：**

| 州 | Name | 下一次驗證 |
| --- | --- | --- |
| WA | Gascoyne | Geological province vs distinct mine/deposit 名稱歧義；找 GA 來源 feature／官方 Project ID |
| WA | Pyramid | 多個同名 WA exploration prospects，尚無一對一 REE 身分依據 |
| WA | Webb Au | 找來源公司、礦權與 REE 角色；其他 Webb Project 名稱不能單靠字串合併 |

**仍只有原始地質紀錄的 272 筆**，按州為 SA 94、WA 81、NSW 40、NT 19、VIC 14、QLD 13、TAS 11。當中 192 Deposit、73 Occurrence、4 Prospect、3 Historical Record；後續工作重點是來源地質記錄到 Project parent 的 evidence-backed association。

已在 [完整 487 CSV](2026-10-31_487_evidence_round2_review.csv) 區分 `source_evidence_grade`（第一輪）、`round2_evidence_grade`（第二輪）、新文件 URL／locator／日期、原始 native identifier 是否仍未恢復，以及 C1 待核准。**改善統計以新證據的存在與定位為準，不把找不到真實 Project 的礦物出現點強制升格。**

## 5. 重現與下一個 Gate

```bash
python scripts/review_p0_evidence_round2.py \
  --root . --output-dir work/evidence
python -m pytest -q tests/test_p0_evidence_round2.py
```

實作原生來源完整保留、487-target ID 嚴格檢查、86 異動可再生、non-overwrite snapshot、原生 bytes 未恢復標記及任何 Project/Resource/GIS/C1 自動核准禁令。下一關以剩餘 272 筆為優先，將來源 ID、deposit name、公司及有明確時間戳的政府/ASX 文件建立 Project–Deposit 關係。對仍以政府地質出現點為單位的資料，保留 C0，不必為降低未確認筆數而納入正式 MCDA。
