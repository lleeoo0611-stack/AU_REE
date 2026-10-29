# Reproduced 86 + 401 cohort selection

## Reconstructed rules

1. **Legacy 86:** take the 203-row historical r963 list and remove the 117 project IDs crosswalked to the 126 provisional groups. The recorded links comprise 112 WA parent groups, 3 SA official project records, NSW Dubbo, and the documented NT Nolans Bore → Nolans alias. The remaining 86 split into 43 with a 1,006-source crosswalk clue but no 126 group and 43 without a direct 1,006 crosswalk.
2. **Unlinked E1 401:** take the 1,006 candidate ledger and select `tier=E1_DIRECT_REE` plus `decision=E1_MISSING_PROJECT_LINK`. This leaves 401 after 399 WA MINEDEX parent-coded records and 3 SA government Project rows are assigned direct source-level structure. The E1 set includes some records that can later be linked to known projects; ‘unlinked’ describes the source-layer linkage state at selection time.

## Validation

The reconstructed legacy IDs and E1 candidate IDs match the frozen 487 target list exactly. See `cohort_reproduction_summary.json` for state counts, input hashes, exact set comparisons, and limits. `legacy_203_selection_audit.csv`, `source_candidate_selection_audit_1006.csv`, and `reconstructed_cohort_487.csv` preserve row-level decisions.

This restores the documented selection logic; it does not prove that the 86+401 set is the complete Australian REE project census or that every selected row is an independent project. No MCDA was run.

