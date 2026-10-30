#!/usr/bin/env python3
"""Capture immutable SQLite snapshots and rebuild/verify them from JSONL tables.

Modes:
  capture --source-db <reviewed sqlite> --snapshot-root <dir> --snapshot-id <id>
  rebuild --snapshot-dir <immutable snapshot> --output <new sqlite>
  verify  --snapshot-dir <immutable snapshot> --database <existing sqlite>

Only the Python standard library is required. Rebuild verifies schema, table row
counts, canonical logical hashes, SQLite integrity, and foreign keys. SQLite file
bytes can differ across versions while logical content remains identical.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

FORMAT_VERSION = 1
CSV_BUILD_VERSION = "1.0.0"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def logical_hash(rows: list[tuple]) -> str:
    h = hashlib.sha256()
    encoded = sorted(canonical_json(list(row)) for row in rows)
    for row in encoded:
        h.update(row.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def table_inventory(db_path: Path):
    conn = sqlite3.connect(f"file:{db_path.resolve().as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    objects = conn.execute(
        "SELECT type,name,tbl_name,sql FROM sqlite_master "
        "WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' "
        "ORDER BY CASE type WHEN 'table' THEN 0 WHEN 'index' THEN 1 "
        "WHEN 'view' THEN 2 ELSE 3 END, name"
    ).fetchall()
    tables = [x["name"] for x in objects if x["type"] == "table"]
    schema = [{"type": x["type"], "name": x["name"], "table": x["tbl_name"], "sql": x["sql"]} for x in objects]
    data = {}
    for table in tables:
        quoted = '"' + table.replace('"', '""') + '"'
        rows = conn.execute(f"SELECT * FROM {quoted}").fetchall()
        data[table] = sorted((tuple(row) for row in rows), key=lambda r: canonical_json(list(r)))
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    fk = conn.execute("PRAGMA foreign_key_check").fetchall()
    conn.close()
    if integrity != "ok" or fk:
        raise RuntimeError(f"Source DB checks failed: integrity={integrity}; foreign_key_violations={len(fk)}")
    return schema, data


def capture(args) -> None:
    source = Path(args.source_db).resolve()
    root = Path(args.snapshot_root).resolve()
    dest = root / args.snapshot_id
    if dest.exists():
        raise FileExistsError(f"Immutable snapshot already exists: {dest}")
    schema, tables = table_inventory(source)
    (dest / "tables").mkdir(parents=True)
    schema_path = dest / "schema.json"
    schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    table_manifest = {}
    for table, rows in sorted(tables.items()):
        path = dest / "tables" / f"{table}.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(canonical_json(list(row)) + "\n")
        table_manifest[table] = {
            "file": f"tables/{table}.jsonl",
            "rows": len(rows),
            "sha256": sha256(path),
            "logical_sha256": logical_hash(rows),
        }
    evidence_paths = [
        "trace_artifact/inputs/reverse_trace_targets_487.csv",
        "scheme_a_upstream/national_screening/nationwide_ree_candidates.csv",
        "scheme_a_upstream/national_raw/national_raw_manifest.json",
        "trace_artifact/work/tenement_reverse_20261029/official_site_tenement_holder_links.csv",
        "trace_artifact/work/tenement_reverse_20261029/target_tenement_trace_status.csv",
        "trace_artifact/work/tenement_reverse_20261029/reverse_trace_evidence.sqlite",
        "national_raw_upstream/national_raw/national_raw_manifest.json",
        "reconstructed_from_chatgpt_artifact/reconstruction_manifest.json",
        "build_definition_review.py",
        "build_complete_proposal_workpack.py",
        "reproduce_86_401_cohorts.py",
        "complete_487_source_review.py",
        "build_row_level_trace_bundle.py",
        "reproducibility/quality_gate_487.py",
        "reproducibility/test_target_id_parser.py",
        "build_editable_workbook.py",
        "deliverable/AU_REE_487_pre_MCDA_five_definition_review.xlsx",
        "deliverable/quality_gate_487_summary.json",
        "deliverable/target_link_reconciliation_487.csv",
    ]
    evidence_paths += ["national-raw-inventory.zip", "scheme-a-screening-review.zip", "nationwide-487-tenement-company-reverse-trace.zip", "reproducibility/build_trace_review.py", "reproducibility/redact_release_outputs.py"]
    evidence_paths += [str(p.relative_to(provenance_root_candidate)).replace("\\", "/") for provenance_root_candidate in [Path(args.provenance_root).resolve() if args.provenance_root else source.parent.parent] for p in sorted((provenance_root_candidate / "research_20261029").rglob("*")) if p.is_file()]
    provenance = []
    provenance_root = Path(args.provenance_root).resolve() if args.provenance_root else source.parent.parent
    for relative in evidence_paths:
        p = provenance_root / relative
        item = {"path": relative, "available": p.is_file(), "sha256": sha256(p) if p.is_file() else None, "size_bytes": p.stat().st_size if p.is_file() else None}
        if p.is_file():
            archived = dest / "evidence" / relative
            archived.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, archived)
            item["snapshot_file"] = f"evidence/{relative}"
        provenance.append(item)
    manifest = {
        "format_version": FORMAT_VERSION,
        "snapshot_id": args.snapshot_id,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "as_of_date": args.as_of_date,
        "source_database_sha256": sha256(source),
        "source_database_name_at_capture": source.name,
        "schema_file": "schema.json",
        "schema_sha256": sha256(schema_path),
        "python_version_at_capture": sys.version,
        "sqlite_version_at_capture": sqlite3.sqlite_version,
        "tables": table_manifest,
        "provenance_artifacts": provenance,
        "missing_original_inputs": [
            "provisional_project_groups_126.csv (logical reconstruction available; original bytes unavailable)",
            "legacy_203_crosswalk_audit.csv (logical reconstruction available; original bytes unavailable)",
            "all_1006_evidence_decisions.csv (logical reconstruction available; original bytes unavailable)",
            "E1_project_unlinked_review_queue.csv (logical reconstruction available; original bytes unavailable)",
        ],
        "rebuild_policy": "Immutable snapshot; updates must create a new snapshot_id. Rebuild compares logical table hashes, not SQLite file bytes.",
        "source_refresh_policy": "A refreshed government/company source run must be reviewed and saved as a new source snapshot before capture. Never overwrite this snapshot.",
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"snapshot": str(dest), "tables": len(tables), "rows": sum(x["rows"] for x in table_manifest.values()), "manifest_sha256": sha256(dest / "manifest.json")}, ensure_ascii=False))


def load_snapshot(snapshot: Path):
    manifest_path = snapshot / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format_version") != FORMAT_VERSION:
        raise ValueError(f"Unsupported format version: {manifest.get('format_version')}")
    schema_path = snapshot / manifest["schema_file"]
    if sha256(schema_path) != manifest["schema_sha256"]:
        raise ValueError("Schema hash does not match manifest")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    for table, details in manifest["tables"].items():
        path = snapshot / details["file"]
        if sha256(path) != details["sha256"]:
            raise ValueError(f"Snapshot file hash mismatch: {path}")
    for artifact in manifest.get("provenance_artifacts", []):
        if artifact.get("available") and artifact.get("snapshot_file"):
            path = snapshot / artifact["snapshot_file"]
            if not path.is_file() or sha256(path) != artifact["sha256"]:
                raise ValueError(f"Provenance artifact hash mismatch: {path}")
    return manifest, schema


def read_table_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def db_table_hash(conn: sqlite3.Connection, table: str) -> tuple[int, str]:
    quoted = '"' + table.replace('"', '""') + '"'
    rows = [tuple(r) for r in conn.execute(f"SELECT * FROM {quoted}").fetchall()]
    return len(rows), logical_hash(rows)


def check_database(db_path: Path, manifest: dict, schema: list[dict]) -> dict:
    conn = sqlite3.connect(f"file:{db_path.resolve().as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    fk = conn.execute("PRAGMA foreign_key_check").fetchall()
    schema_rows = conn.execute(
        "SELECT type,name,tbl_name,sql FROM sqlite_master "
        "WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' "
        "ORDER BY CASE type WHEN 'table' THEN 0 WHEN 'index' THEN 1 "
        "WHEN 'view' THEN 2 ELSE 3 END, name"
    ).fetchall()
    actual_schema = [{"type": x["type"], "name": x["name"], "table": x["tbl_name"], "sql": x["sql"]} for x in schema_rows]
    if canonical_json(actual_schema) != canonical_json(schema):
        raise AssertionError("Database schema differs from frozen schema")
    table_results = {}
    for table, expected in manifest["tables"].items():
        count, digest = db_table_hash(conn, table)
        if count != expected["rows"] or digest != expected["logical_sha256"]:
            raise AssertionError(f"Logical table mismatch: {table}: rows {count}/{expected['rows']}, hash {digest}/{expected['logical_sha256']}")
        table_results[table] = {"rows": count, "logical_sha256": digest}
    conn.close()
    if integrity != "ok" or fk:
        raise AssertionError(f"SQLite checks failed: integrity={integrity}, foreign_key_violations={len(fk)}")
    return {"integrity_check": integrity, "foreign_key_violations": len(fk), "tables": len(table_results), "rows": sum(x["rows"] for x in table_results.values()), "table_results": table_results}


def rebuild(args) -> None:
    snapshot = Path(args.snapshot_dir).resolve()
    manifest, schema = load_snapshot(snapshot)
    dest = Path(args.output).resolve()
    if dest.exists() and not args.overwrite:
        raise FileExistsError(f"Refusing to overwrite database: {dest}; pass --overwrite explicitly")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    conn = sqlite3.connect(dest)
    conn.execute("PRAGMA foreign_keys=ON")
    # Create base tables first; secondary indexes/views are applied after inserts.
    for obj in schema:
        if obj["type"] == "table":
            conn.execute(obj["sql"])
    for table, details in manifest["tables"].items():
        quoted = '"' + table.replace('"', '""') + '"'
        cur = conn.execute(f"PRAGMA table_info({quoted})")
        cols = cur.fetchall()
        qcols = ", ".join('"' + x[1].replace('"', '""') + '"' for x in cols)
        marks = ",".join("?" for _ in cols)
        conn.executemany(f"INSERT INTO {quoted} ({qcols}) VALUES ({marks})", read_table_rows(snapshot / details["file"]))
    for obj in schema:
        if obj["type"] != "table":
            conn.execute(obj["sql"])
    conn.commit()
    conn.close()
    result = check_database(dest, manifest, schema)
    result.update({"snapshot_id": manifest["snapshot_id"], "output": str(dest), "database_sha256": sha256(dest)})
    print(json.dumps(result, ensure_ascii=False))


def verify(args) -> None:
    snapshot = Path(args.snapshot_dir).resolve()
    manifest, schema = load_snapshot(snapshot)
    result = check_database(Path(args.database).resolve(), manifest, schema)
    result.update({"snapshot_id": manifest["snapshot_id"], "database": str(Path(args.database).resolve()), "database_sha256": sha256(Path(args.database).resolve())})
    print(json.dumps(result, ensure_ascii=False))


def compare(args) -> None:
    """Compare immutable snapshots by canonical table hashes and provenance."""
    left, left_schema = load_snapshot(Path(args.left).resolve())
    right, right_schema = load_snapshot(Path(args.right).resolve())
    ltab, rtab = left["tables"], right["tables"]
    changes = []
    for name in sorted(set(ltab) | set(rtab)):
        a, b = ltab.get(name), rtab.get(name)
        if a is None or b is None or a["logical_sha256"] != b["logical_sha256"] or a["rows"] != b["rows"]:
            changes.append({"table": name, "left_rows": a["rows"] if a else None, "right_rows": b["rows"] if b else None,
                            "left_logical_sha256": a["logical_sha256"] if a else None,
                            "right_logical_sha256": b["logical_sha256"] if b else None})
    result = {"left_snapshot": left["snapshot_id"], "right_snapshot": right["snapshot_id"],
              "schema_equal": canonical_json(left_schema) == canonical_json(right_schema),
              "changed_tables": changes,
              "changed_provenance": [x["path"] for x in right.get("provenance_artifacts", [])
                                     if x.get("sha256") != next((y.get("sha256") for y in left.get("provenance_artifacts", []) if y["path"] == x["path"]), None)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def csv_build(args) -> None:
    """Build a fresh normalized database from the versioned CSV deliverables."""
    source_dir = Path(args.csv_dir).resolve()
    files = sorted(source_dir.glob("*.csv"), key=lambda p: p.name.casefold())
    if not files:
        raise FileNotFoundError(f"No CSV inputs found in {source_dir}")
    dest = Path(args.output).resolve()
    if dest.exists() and not args.overwrite:
        raise FileExistsError(f"Refusing to overwrite database: {dest}; pass --overwrite explicitly")
    dest.parent.mkdir(parents=True, exist_ok=True)
    inputs = []
    tables = []
    used_names = set()
    for path in files:
        table = re.sub(r"[^A-Za-z0-9_]+", "_", path.stem)
        if not table or table[0].isdigit():
            table = "t_" + table
        if table.casefold() in used_names:
            raise ValueError(f"CSV table-name collision: {table}")
        used_names.add(table.casefold())
        with path.open(encoding="utf-8-sig", errors="strict", newline="") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames or []
            if not fields or len(fields) != len(set(fields)):
                raise ValueError(f"Missing or duplicate CSV headers: {path}")
            rows = list(reader)
        if any(None in r for r in rows):
            raise ValueError(f"CSV row has more values than headers: {path}")
        tables.append((table, path, fields, rows))
        inputs.append({"file": path.name, "sha256": sha256(path), "bytes": path.stat().st_size, "rows": len(rows), "table": table})
    input_digest = hashlib.sha256(canonical_json(inputs).encode("utf-8")).hexdigest()
    if dest.exists():
        dest.unlink()
    conn = sqlite3.connect(dest)
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("CREATE TABLE _source_file_manifest (file TEXT PRIMARY KEY, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, rows INTEGER NOT NULL, table_name TEXT NOT NULL)")
    conn.execute("CREATE TABLE _build_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    for table, path, fields, rows in tables:
        qtable = '"' + table.replace('"', '""') + '"'
        qfields = ", ".join('"' + f.replace('"', '""') + '" TEXT' for f in fields)
        conn.execute(f"CREATE TABLE {qtable} ({qfields})")
        if rows:
            cols = ", ".join('"' + f.replace('"', '""') + '"' for f in fields)
            marks = ",".join("?" for _ in fields)
            conn.executemany(f"INSERT INTO {qtable} ({cols}) VALUES ({marks})", [[r.get(f, "") for f in fields] for r in rows])
    conn.executemany("INSERT INTO _source_file_manifest VALUES (?,?,?,?,?)", [(x["file"], x["sha256"], x["bytes"], x["rows"], x["table"]) for x in inputs])
    metadata = {
        "schema_version": "census-review-csv-v1",
        "as_of_date": args.as_of_date,
        "builder_version": CSV_BUILD_VERSION,
        "input_manifest_sha256": input_digest,
        "csv_input_count": str(len(inputs)),
        "python_version": sys.version.split()[0],
        "sqlite_version": sqlite3.sqlite_version,
    }
    conn.executemany("INSERT INTO _build_metadata VALUES (?,?)", sorted(metadata.items()))
    conn.commit()
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok" or conn.execute("PRAGMA foreign_key_check").fetchall():
        conn.close()
        raise RuntimeError("Built database failed SQLite validation")
    stats = {}
    for table, _, fields, rows in tables:
        stats[table] = {"rows": len(rows), "logical_sha256": logical_hash([tuple(r.get(f, "") for f in fields) for r in rows])}
    if "487_definition_review" in stats and stats["487_definition_review"]["rows"] != 487:
        raise AssertionError("The 487-row target table is incomplete")
    if "487_official_tenure_intersection_evidence_compact" in stats and stats["487_official_tenure_intersection_evidence_compact"]["rows"] != 764:
        raise AssertionError("The pinned tenure intersection table is incomplete")
    conn.close()
    manifest = {
        "format_version": FORMAT_VERSION,
        "csv_build_version": CSV_BUILD_VERSION,
        "as_of_date": args.as_of_date,
        "input_directory": source_dir.name,
        "input_manifest_sha256": input_digest,
        "input_files": inputs,
        "table_results": stats,
        "database_sha256": sha256(dest),
        "sqlite_integrity_check": integrity,
    }
    manifest_path = Path(str(dest) + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"database": str(dest), "tables": len(tables), "csv_files": len(inputs), "rows": sum(x["rows"] for x in inputs), "manifest": str(manifest_path), "integrity_check": integrity, "input_manifest_sha256": input_digest}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    cap = sub.add_parser("capture")
    cap.add_argument("--source-db", required=True)
    cap.add_argument("--snapshot-root", required=True)
    cap.add_argument("--snapshot-id", required=True)
    cap.add_argument("--as-of-date", required=True)
    cap.add_argument("--provenance-root")
    cap.set_defaults(fn=capture)
    reb = sub.add_parser("rebuild")
    reb.add_argument("--snapshot-dir", required=True)
    reb.add_argument("--output", required=True)
    reb.add_argument("--overwrite", action="store_true")
    reb.set_defaults(fn=rebuild)
    ver = sub.add_parser("verify")
    ver.add_argument("--snapshot-dir", required=True)
    ver.add_argument("--database", required=True)
    ver.set_defaults(fn=verify)
    cmp = sub.add_parser("compare")
    cmp.add_argument("--left", required=True)
    cmp.add_argument("--right", required=True)
    cmp.set_defaults(fn=compare)
    csvp = sub.add_parser("csv-build")
    csvp.add_argument("--csv-dir", required=True)
    csvp.add_argument("--output", required=True)
    csvp.add_argument("--as-of-date", required=True)
    csvp.add_argument("--overwrite", action="store_true")
    csvp.set_defaults(fn=csv_build)
    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
