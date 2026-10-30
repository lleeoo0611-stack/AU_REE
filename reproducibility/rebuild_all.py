#!/usr/bin/env python3
"""Run the frozen-input census pipeline, build the canonical DB and pin a snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(cmd: list[str], cwd: Path):
    proc = subprocess.run(cmd, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True)
    result = {"command": [str(x) for x in cmd], "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    if proc.returncode:
        raise RuntimeError(json.dumps(result, ensure_ascii=False))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="Workpack root containing frozen inputs and pipeline scripts")
    p.add_argument("--as-of-date", required=True)
    p.add_argument("--snapshot-id", required=True, help="New immutable snapshot ID; existing IDs are never overwritten")
    args = p.parse_args()
    root = Path(args.root).resolve()
    py = sys.executable
    out = root / "deliverable"
    repro = root / "reproducibility"
    db_builder = repro / "build_census_database.py"
    commands = [
        [py, str(root / "build_definition_review.py"), str(root)],
        [py, str(root / "build_complete_proposal_workpack.py"), str(root)],
        # The proposal workpack adds lineage fields; rebuild the five-condition
        # ledger afterward so its canonical columns are restored before review.
        [py, str(root / "build_definition_review.py"), str(root)],
        [py, str(root / "reproduce_86_401_cohorts.py"), str(root)],
        [py, str(root / "enrich_candidate_evidence.py"), str(root)],
        [py, str(root / "complete_487_source_review.py"), str(root)],
        [py, str(repro / "build_trace_review.py"), "--root", str(root), "--stage", "apply"],
        [py, str(root / "build_row_level_trace_bundle.py"), str(root)],
        [py, str(repro / "quality_gate_487.py"), "--root", str(root), "--as-of-date", args.as_of_date],
        [py, str(repro / "build_trace_review.py"), "--root", str(root), "--stage", "audit"],
        [py, str(repro / "redact_release_outputs.py")],
        [py, str(db_builder), "csv-build", "--csv-dir", str(out), "--output", str(out / "census_review.sqlite"), "--as-of-date", args.as_of_date, "--overwrite"],
        [py, str(root / "build_editable_workbook.py"), str(out)],
    ]
    execution = []
    for cmd in commands:
        execution.append(run(cmd, root))
    snapshot_dir = repro / "snapshots" / args.snapshot_id
    capture = [py, str(db_builder), "capture", "--source-db", str(out / "census_review.sqlite"), "--snapshot-root", str(repro / "snapshots"), "--snapshot-id", args.snapshot_id, "--as-of-date", args.as_of_date, "--provenance-root", str(root)]
    execution.append(run(capture, root))
    rebuilt = repro / "verification" / f"census_review_{args.snapshot_id}.sqlite"
    rebuild = [py, str(db_builder), "rebuild", "--snapshot-dir", str(snapshot_dir), "--output", str(rebuilt)]
    execution.append(run(rebuild, root))
    verify = [py, str(db_builder), "verify", "--snapshot-dir", str(snapshot_dir), "--database", str(out / "census_review.sqlite")]
    execution.append(run(verify, root))
    run_manifest = {
        "pipeline_version": "1.0.0",
        "snapshot_id": args.snapshot_id,
        "as_of_date": args.as_of_date,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "commands": execution,
        "final_database_sha256": sha(out / "census_review.sqlite"),
        "snapshot_manifest_sha256": sha(snapshot_dir / "manifest.json"),
        "status": "PASS",
    }
    run_path = repro / "runs" / f"{args.snapshot_id}.json"
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text(json.dumps(run_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "snapshot_id": args.snapshot_id, "database": str(out / "census_review.sqlite"), "database_sha256": run_manifest["final_database_sha256"], "snapshot": str(snapshot_dir), "run_manifest": str(run_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
