# P2–P4 339-source continuing verification — Batch 04 (2026-10-31)

**Scope:** fixed 2026-10-29 original government/source snapshot; read-only baseline `2026-10-31_p234_final_evidence_339.csv`; includes unmerged Batch 03 as ancestor. **No C1/JORC/GIS/13-case or MCDA approval.** This is a full **339-ID progress reconciliation** with **nine additional P2 authoritative-source scope rechecks**, not 339 newly read original technical reports.

## Correct units and current status

| Priority | Source rows / provisional cases | Prior source classification | Previously saved relevant primary-page content | Earlier external/source-scope text rechecks | New Batch 04 direct scope rechecks | Baseline desk/native still needing additional technical originals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| P2 | 28 / 27 cases | 28 / 28 | P2 inherited desk, **not** newly fulltext verified | 3 government HTML | **9** | **16** |
| P3 | 216 / not independently deduplicated projects | 216 / 216 | 117 relevant originals | 11 | 0 | **87** (plus 1 cached-original access hold) |
| P4 | 95 / not independently deduplicated projects | 95 / 95 | 26 relevant originals | 5 | 0 | **64** |
| **Total** | **339** | **339 classified** | **143 P3/P4 + 1 P3 cached** | **19** | **9** | **167** (16 P2 + 87 P3 + 64 P4) |

These last-column figures represent the **priority outstanding technical-document reading queue**; other source-scope/project/tenure approval gaps remain in previously reviewed cases. P3/P4 have 167 native-only entries at baseline; 16 prior external text overlays have been completed (11 P3 and 5 P4), leaving 151. New Batch 04 changes P2 3 to 12 direct government/issuer-public-source scope rechecks and 25 to 16 pending.

## Batch 04: nine P2 source-scoped rechecks

| Source | New verified public source-scope observation | Interpretation for the dataset |
|---|---|---|
| Boulder Ridge (NT) | NTGS GEMIS 2015 official abstract, 2014/2018 original report searchable text; 2017-18 mineral-rights transaction excludes HREE | Xenotime exploration ≠ Browns Range MRE; separate mineral rights from actual production |
| Port Pirie REE (SA) | SARIG Mineral Deposit 8908 directly records rehabilitated treatment site and historical single-oxide Y/Sc tailings grades | Historical Y₂O₃/Sc₂O₃ and tailings tonnes ≠ TREO JORC |
| Anchor Tin Deeps (TAS) | MRT EDGI Round 8 ATD1/2, 487m, Tin–Li–REE target | Historical drill test, no source-scoped REO MRE |
| Blue Tier (TAS) | MRT Round 7 award-list original names the multi-commodity target | Grant award ≠ drill result or Project MRE |
| Cruncher (TAS) | MRT Round 7 original result says CR001 missed target, low-tenor REE | Hole-specific negative, not entire region negative |
| DC Target (TAS) | MRT Round 9 results: S1699 reached skarn/dolomite in Renison sequence | REE commodity-list label ≠ REO result; separate from Tunnel Hill |
| Tunnel Hill (TAS) | MRT Round 9 results: S1717 abandoned, S1718 1.13% Sn and 0.52% Sn | Tin intervals ≠ TREO |
| Douglas Project (VIC) | Official Iluka project history, Bondi Main/East/West, mining ceased 2012 | Historic HMS mine/revegetation, not active pre-FID REE |
| Wedderburn Project (VIC) | WIM Resource project page: 223 Mt @2.9% **THM**, 2015 JORC | THM MRE cannot be treated as TREO; distinct Avonbank/Bungalally |

**Source IDs, locator sections, direct links, separate oxide/THM basis, remaining primary documents and reopening triggers:** [Batch-04 editable P2 CSV](../../inputs/source_review_20261031/p2_external_primary_batch04_20261031.csv). Public official HTML/issuer summaries were directly reviewed. Boulder Ridge PDF text was accessible via searchable output, **PDF screenshot cache-missed**; original PDF bytes/hash were not captured. New external review is **not complete original technical report verification**. No new original SHA is claimed.

## P3/P4: all 311 IDs retained with bounded further searches

The per-source overlay includes **all 216 P3 and 95 P4** with current pre-existing documentary dispositions, prior original-content levels, Batch01–03 additions, and next action. An additional 8-row [P3/P4 locator-attempt table](../../inputs/source_review_20261031/p34_batch04_locator_attempts.csv) records new exact-source searches **without promoting any of them to a new technical-original review**. In particular:

- SA native MINOS REE deposit **11910** must not be joined to government Minos gold prospect **11182** merely because both are called Minos; this affects separate P3/P4 source rows.
- `MICA PASS 11318`: exact official page inaccessible in this environment; both P3 and P4 native IDs still await source-specific original.
- `Gascoyne`: ANU regional research is **regional context**, not a source-point-to-Project confirmation.
- `Railway Rare Earth deposit`: mineral-locality secondary listing cannot replace NSW METINDEX 219646 original.
- `Gimli REE S0242520`: WA Mindex and Legacy rows share native locator; repeat provenance IDs do not imply two projects or JORC qualification.

These are meaningful **negative/non-identity scope checks**, not additional successful original-technical fulltext reviews. Existing 117 P3 and 26 P4 relevant saved-original interpretations remain part of baseline; new technical PDF/source downloads for P3/P4 were **0** in this batch.

## Next acceptance-critical actions

1. **P2 remaining 16**: obtain 25_9125/25_9134, 23_8746, 2024 ATD final report, original dated Wedderburn 2015 JORC, Boulder Ridge mineral-rights/assay chain and prospect polygons. Search by **official report ID** rather than common site name.
2. **P3 remaining 87**: prioritize SA exact MinDep IDs and WA source-native Mindex/ASX links, with evidence-based distinction between Project and occurrence.
3. **P4 remaining 64**: use native identifiers, official depositional/assay history and potential Project-parent evidence; don't force entries into C1 solely to clear queue.
4. **Prior archived 144 relevant-source cases**: preserve current relevant-page summaries, check byte/SHA externally where required, and resolve independent same-scope identity and resource issues.
5. Run offline validation/test for the 339 overlay and nine/8 new rows. Promotion to C1 still requires independent reviewer signatures, dated JORC/REE product evidence, approved Project footprint and eligibility panel.

## Reproducibility

```sh
python scripts/check_p234_all_sources_b04.py
python -m unittest discover -s tests -p test_p234_all_sources_b04.py -v
```

Check IDs, priority counts, status transitions, old archived/page scopes and **no simulated PDF bytes or C1 approvals**. The repository's earlier frozen 339, P2 28 and Batch03 167 source view are never overwritten; this file is an additive observation overlay.
