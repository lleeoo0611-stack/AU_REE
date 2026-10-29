# 澳洲全境官方礦產原始資料與 Scheme A 篩選結果（2026-10-29）

## 完整原始資料快照

- 來源：六州（WA、QLD、TAS、NSW、VIC、SA）與 NT；ACT 經 GA 全國服務覆蓋；另保留 GA AIMR REE 與 Critical Minerals 兩項聯邦圖層。
- 全國 Raw Gate：`PASS`；先完整擷取再進行 REE 篩選。
- 原始圖徵／主要礦床及開發專案來源紀錄：**123,323** 筆；此為來源加總，保留跨來源重複。
- 南澳資料附加保留 `sarig_md_commodity_exp.csv` **11,208** 筆、`sarig_md_mineralogy_exp.csv` **16,045** 筆、`sarig_md_reference_exp.csv` **14,739** 筆；南澳礦床主檔 **8,815** 筆。
- 原始 Manifest SHA-256：`5057e25f1711232a0057889d413913fd8f4a227cbe42235dc279e98bfbce4dc1`。
- 原始資料 GitHub Actions：[Run #40821122179](https://github.com/lleeoo0611-stack/AU_REE/actions/runs/40821122179)，Artifact `australia-national-unfiltered-raw-inventory`。

| 官方原始來源 | 原始記錄 | 取得狀態 |
|---|---:|---|
| `GA_AIMR_REE_2026` | 149 | RAW COMPLETE |
| `GA_CRITICAL_DEPOSITS_2025` | 421 | RAW COMPLETE |
| `STATE_WA_MINDEX` | 48,493 | RAW COMPLETE |
| `STATE_QLD_MINOCC` | 5,209 | RAW COMPLETE |
| `STATE_TAS_MRT` | 8,301 | RAW COMPLETE |
| `NSW_METINDEX` | 30,898 | RAW COMPLETE |
| `VIC_MINSITE` | 18,794 | RAW COMPLETE |
| `NT_MODAT_WFS` | 2,105 | RAW COMPLETE |
| `SA_GEODATA_MINDEP` | 8,815 | RAW COMPLETE |
| `SA_PROJECT_DEVELOPING` | 35 | RAW COMPLETE |
| `SA_PROJECT_MAJOR` | 31 | RAW COMPLETE |
| `SA_CRITICAL_REE` | 72 | RAW COMPLETE |

## 篩選後的可審查來源候選

- 先核對同一份 Raw Manifest 的 SHA-256；Raw Gate PASS 後才允許執行。
- E1 明確稀土商品：**803** 筆。
- E2 含稀土礦物：**163** 筆，列 Extended Occurrence Inventory。
- E3 地質背景線索：**40** 筆，列地質佐證候選。
- 總來源候選：**1,006** 筆；跨來源同州同名待審查配對：**137** 組。
- 自動 Project Master 新增：**0**；自動身份合併：**0**。
- 篩選 GitHub Actions：[Run #40822082016](https://github.com/lleeoo0611-stack/AU_REE/actions/runs/40822082016)，Artifact `australia-national-ree-scheme-a-screening-review`。

## 重跑程序


git checkout main
python -m pip install -e '.[test]'
python scripts/verify_national_raw.py --raw-dir work/national_raw
python scripts/screen_national_raw.py --raw-dir work/national_raw --out work/national_screening

Project Master 仍須逐筆以 Project 身分及獨立文件核准；地質礦點、母子礦床與名稱重複均保存為待審查關係，不直接合併。
