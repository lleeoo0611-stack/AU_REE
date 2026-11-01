# Census and Entity Resolution acceptance — 2026-11-01

Execution ID: `CENSUS-ENTITY-20261101`. Source cutoff: `2026-10-29`.
Base: `839944ecc003d5e3e3c590441e1b95c94349ed35`, repository `lleeoo0611-stack/AU_REE`.
Local checkout: `C:\Users\whatt\.codex\.chatgpt-projects\g-p-6a74fa8105f88191b580dee7d5f22fdd\worktrees\AU_REE-census-20261101`.

**Technical reconstruction PASS; complete independent Project/evidence acceptance remains PARTIAL.** Tests and checksums do not resolve missing Project identity documents or supply independent signatures. No original source, historic target ID or approval ledger was changed.

## Verified implementation and database

- 262 regression tests passed on Windows / Python 3.13. Tests include stable Project IDs, same-batch parent-before-child resolution, revoked approvals/originals, wrong entity levels, source ingestion rollback and invalid Census crosswalks.
- GitHub PR #66, implementation commit `7c14f32e74b26d975945c8268d114a70073f5deb`: **18/18 checks passed**, including Python 3.11/3.13, evidence regression, documentary closeout and R synthetic smoke. Documentation-only updates after this commit do not add independent source approvals.
- Fixed Windows SQLite file locks by closing stage connections after transaction completion, including backups, failure paths and status checks. Fixed local GIS archive path separators without changing scientific criteria.
- Added optional `csv-build --review-dir`: joins the existing 487-source Census and current Structural Round 01 review in one database. Checks exactly the same 39 stable candidate IDs, Project names, states, cutoff, and all attached group references. Documentary CSV cannot declare an independently approved ID. A failed attachment cannot replace an existing release.
- Actual integrated build: **51 CSV tables / 15,018 data rows**, plus **2 metadata tables / 58 rows**. Census has **487 targets**, **451 source entities**, **36 repeated targets on the same native entity**, **78 linked targets**, **409 unresolved targets**, **39 candidate groups**, **195 documentary gate cells**. These are different entity levels.
- SHA-256 of local integrated database: `e3b062ff8d81d37c8236e7326506bd42488f399ec844278d00c78abd9885000d`.
- Captured immutable `CENSUS-ENTITY-20261101` snapshot and rebuilt it into a separate SQLite. Both original and restored databases passed schema, per-table row-count/logical-hash, integrity and foreign-key checks: **53 tables, 15,076 total rows, 0 FK violations**. SQLite file hashes need not match after logical restoration.
- Original five-stage offline replay completed, then reused all five stage checkpoints. Its **203 unverified legacy master records are separate from the 487-source review**, and no verified scores or rankings were admitted.

## Verified evidence and remaining dependencies

- `build_structural_round01.py --check --verify-originals` passed using the existing local archive: 36 available originals (13 PDF / 23 HTML), manifest SHA/size checks; source-specific 39-group review remained unchanged. This does not claim complete reading or independent approval of every technical report.
- `close_p234_evidence_status.py --check --verify-originals` passed with the existing local primary archive. All 339 fixed sources reproduce their distinct classifications. The final nine-target batch retains 8 archived-content targets and 1 web-only target. Its verification scope is specified by that script; unavailable originals remain unavailable.
- `review_p234_144_primary_scope.py --check --verify-originals` passed: 144 targets, 143 original-content-reviewed targets, 1 original-content access hold, 49 distinct reviewed documents; no changed approvals. `check_external_primary_batch03.py --check --verify-originals` also passed, reporting the frozen 167 native IDs, 16 reviewed / 151 pending. This native-only result is not a claim that every external PDF was available.
- **39/39 group identities remain independently unapproved; C1=0, C2=0.** Structural review retains 168 unresolved documentary gate cells (including 31 ID and 31 ROLE cells). Ten groups lack a Project-level source in the original government/legacy crosswalk; a Deposit cannot be relabelled to bypass this.
- Missing/undated Project scope, source-to-Project mapping, resource-basis conflicts, actual Project geometry and independent reviewer records remain in the existing `gap_priority_queue.csv`, `identity_crosswalk.csv` and `c2_identity_review.csv`. Exact reopen requirements remain visible in those tables.
- The work is **not** a claim that all Australian Projects are resolved or every original is available. Independent identity decisions must be supplied through the existing source-document and approval ledgers, with actual archived bytes, named reviewer and valid dates; no automatic signatures were introduced.

## Reproduce

```bash
python -m pytest tests -q
python scripts/run_research_pipeline.py --profile all --mode check
python scripts/build_structural_round01.py --check --verify-originals
python scripts/close_p234_evidence_status.py --check --verify-originals
python reproducibility/build_census_database.py csv-build --csv-dir outputs --review-dir docs/audits/structural_round01 --output work/census_with_identity.sqlite --as-of-date 2026-10-29
python reproducibility/build_census_database.py capture --source-db work/census_with_identity.sqlite --snapshot-root work/snapshots --snapshot-id CENSUS-ENTITY-20261101 --as-of-date 2026-10-29
python reproducibility/build_census_database.py rebuild --snapshot-dir work/snapshots/CENSUS-ENTITY-20261101 --output work/restored.sqlite
python reproducibility/build_census_database.py verify --snapshot-dir work/snapshots/CENSUS-ENTITY-20261101 --database work/restored.sqlite
```

Local outputs and manifests are under `work/census_acceptance/`, including test XML, source/restore verification JSON, integrated SQLite and immutable snapshot. Full third-party originals remain local. Git attributes preserve committed file bytes on Windows so source hashes are not changed by checkout line-ending conversion.
