# Reproducible census database and update procedure

This package builds a research review database for the fixed 487-row cohort. It does not run MCDA. All input and review decisions remain traceable to the CSV deliverables, frozen source artifacts, and versioned scripts.

## Rebuild the current frozen state

Run from the work-package directory in PowerShell. Use Python 3.12+; the database builder itself uses only the standard library. The full pipeline's workbook step also needs `xlsxwriter`.

```powershell
$py = (Get-Command python).Source
& $py .\reproducibility\rebuild_all.py --root . --as-of-date 2026-10-29 --snapshot-id 2026-10-29-rN
```

Replace `rN` with a new, unused identifier. The runner refuses to reuse a snapshot ID. It regenerates the review tables from retained inputs, builds SQLite from every CSV in `deliverable/`, rebuilds the workbook, captures an immutable database snapshot, rebuilds a verification database from that snapshot, and verifies schema, row counts, canonical table hashes, SQLite integrity, foreign keys, and archived provenance hashes. Keep the generated run manifest and snapshot folder with the outputs.

To rebuild or verify an existing snapshot, use `reproducibility/build_census_database.py rebuild` or `verify`. The `compare --left <old-snapshot> --right <new-snapshot>` mode reports schema changes, table row count/logical hash differences, and changed provenance-file hashes.

## Make and review an update

1. Copy the package to a new dated working directory; retain the old package and snapshot unchanged. Do not edit `sources/`.
2. Refresh upstream government and company evidence using recorded source endpoints/acquisition artifacts. Save each response, query date, URL, and acquisition script/version in the new package. The current pipeline consumes retained local inputs; it does **not** automatically fetch all state tenure, company, or ASX sources.
3. Update row-level evidence and adjudications in editable CSVs/scripts. Preserve source row IDs and old IDs; unresolved links remain unresolved. Review additions/removals, company succession, title-holder versus operator distinctions, and source coverage.
4. Run the full command with a new snapshot ID and inspect its run manifest and validations.
5. Compare the old and new frozen database snapshots. A changed hash flags a review; it does not by itself mean that a project should be admitted or excluded.

## Frozen state and known limits

- Snapshots are immutable; every new state gets a new ID. A snapshot contains canonical JSONL for every database table and copies of the provenance artifacts listed in its manifest. Its verifier checks both.
- Logical table hashes are the cross-version reproducibility criterion. SQLite byte hashes are also recorded for convenience but can vary across SQLite builds.
- The original bytes of four intermediate ChatGPT extraction/decision files were not recovered. Their logical reconstructions and the exact 487 target list are retained; this limitation is listed in each snapshot manifest.
- A reviewed source state can be rebuilt deterministically. A future source refresh still requires acquisition and human review; network-source polling and automatic project admission are not part of this pipeline.
- Database rows reflect the review CSVs, including unresolved/hold decisions. The database is a reproducible record, not proof that every one of the 487 records is an independent qualifying project.
