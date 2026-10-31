# External Technical Primary Review — Batch 03 (2026-10-31)

Execution: `EXT-TECH-B03-20261031` · Baseline: `main@3ddb4791d68b517c98d6a169912ebcabcb06f541` · Original government source universe: **2026-10-29**.

## Scope and disposition

This batch adds **6 frozen source rows in 3 named locality groups**: Ketchowla K3 (2), Ketchowla Hill (2), and Oak Dam East (2), selected from the 157 previously pending native-only source rows. They are **source observations, not six projects**. Two columns of distinct government source IDs remain intact. No C1/JORC/GIS/13-case gate/MCDA signoff is changed.

- **Ketchowla K3 — 2 native source IDs**: Archer's 2011 report (printed pp.35–36) identifies REE/Y geochemical enrichment across K1, K2, K3 and K9, and says economic significance was undetermined. Its explicit REE drill intersections are at **K9** (K9RC009: 2 m @ 0.3% REE; K9RC010: 3 m @ 0.12% REE), **not K3**; rock-chip maxima are from several targets. A 24 March 2017 company update describes planned K3–K9 cobalt-focused drilling, not a completed K3 REO resource. As the 2011 narrative separately lists a five-occurrence manganese set without K3, K3-specific source scope requires assay/certificate confirmation. **Decision:** Ketchowla Project-level exploration context supported; K3 REO resource/JORC and independent project remain HOLD.
- **Ketchowla Hill — 2 native source IDs**: Archer's 2011 report (printed pp.28–30) identifies an historic manganese mine, last worked 1941 with **358 tonnes of Mn ore**, a ~320 m Mn oxide outcrop, and a Table 1 of Mn/Co/Cu/Ni/Zn rock chips. It also refers to the old Ketchowla mine as K1 within the broader project. The 358 tonnes are **not REO production/resource**, and the modern K3 and K9 localities cannot inherit them. **Decision:** historic Mn mine/K1 locality scope supported; standalone REE resource/Project not supported by reviewed passages.
- **Oak Dam East — 2 native source IDs**: South Australia's official Mineral Deposit record **3100** labels Oak Dam East a **Prospect**, **Not Worked**; Cu major, REE minor, and monazite rare gangue. The historical ~**560 Mt at 41–56% Fe** and ~**300 Mt at 0.2% Cu** are Fe/Cu figures, not TREO. The current SA Energy & Mining uranium summary explicitly separates Oak Dam East from Oak Dam West. **Decision:** IOCG Cu-U-Fe prospect with accessory REE is documented; no REO JORC resource, independent REE development project or current legal polygon verified.

## Original sources and locators

1. [Archer Exploration, *Annual Report 2011*](https://announcements.asx.com.au/asxpdf/20110921/pdf/42170jxqzwg4ly.pdf), printed pp.28–30 (historic Hill mine, Table 1), pp.35–36 (REE, K9 drill intervals). PDF searchable text inspected on 2026-10-31; PDF-page screenshot returned **cache miss** and source PDF bytes were not saved.
2. [Archer Exploration, 24 March 2017 ASX Projects Update](https://archerx.com.au/wp-content/uploads/2018/03/20170324_Projects-Update-ASX-Release.pdf), p.2 Ketchowla drilling. Searchable PDF text reviewed; visual screenshot cache miss and PDF bytes not saved. This is historical project context, **not current title proof**.
3. [South Australia Geodata — Mineral Deposit 3100, Oak Dam East](https://drillhole.pir.sa.gov.au/MineralDepositDetails.aspx?DEPOSIT_NO=3100), `Details / Mineralogy / Commodities / References`. Official government HTML directly read.
4. [SA Energy & Mining — Uranium, notable deposits](https://www.energymining.sa.gov.au/industry/minerals-and-mining/mineral-commodities/uranium), `Oak Dam East` paragraph distinguishing Oak Dam West.

Source limits: the current environment did not obtain the ASX or Archer original PDF **bytes**, page images or hashes. Both Ketchowla documents have only inspectable searchable PDF text; government Oak Dam content was directly readable as HTML. The SA Geodata per-site detail pages for K3 #9325 and Hill #3914 did not resolve here; site-number linkage comes from the frozen native source metadata and must not be represented as newly independently verified. This review does not claim complete PDF/full technical report review, current title, JORC resource or formal C1 verification.

## Updated batch counts

| Universe / review type | Before | After Batch 03 |
| --- | ---: | ---: |
| Frozen native-only source targets | 167 | 167 |
| Source-scoped external technical text reviews | 10 | **16** |
| Pending external technical original follow-up | 157 | **151** |
| P2 independent original-fulltext rechecks | 3 direct government HTML from prior Batch 01 | unchanged; 25 require technical fulltext |
| Independent approved C1 projects in this batch | 0 | **0** |

`2026-10-31_external_primary_progress_167.csv` is the **immutable Batch-02 view**; the Batch-03 current view is [2026-10-31_external_primary_progress_167_b03.csv](2026-10-31_external_primary_progress_167_b03.csv). All 167 row IDs, names, native source keys and baseline statuses are preserved. Batch 03 source evidence is the editable input [external_primary_batch03_20261031.csv](../../inputs/source_review_20261031/external_primary_batch03_20261031.csv).

Next review requires per-site SA original report/assay (9325/3914), K3 sample-to-Ketchowla parent mapping, and East current tenure / original government Envelope 09288 or 03319. Do not promote K3's K9 assays, Hill Mn output, or Oak Dam Fe/Cu figures into resource, TREO, or C1 data. On genuinely new primary evidence, reopen the exact frozen source ID.

## Reproducibility

Run `python scripts/check_external_primary_batch03.py` and `python -m unittest discover -s tests -p test_external_primary_batch03.py -v`; these assert original 167-row preservation, six new reviews, no fabricated document SHA, zero signoff, and 16/151 accounting. They **do not** validate missing third-party PDF pages or substitute for independent source approval.
