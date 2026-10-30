"""Export the 487 target-level tenure query outcomes and every official spatial match."""
import csv
import json
import sqlite3
import sys
from pathlib import Path

BASE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
OUT = BASE / "deliverable"
TRACE_DB = BASE / "trace_artifact" / "work" / "tenement_reverse_20261029" / "reverse_trace_evidence.sqlite"


def export_query(conn, query, path):
    cur = conn.execute(query)
    names = [d[0] for d in cur.description]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=names)
        w.writeheader()
        w.writerows(dict(zip(names, row)) for row in cur.fetchall())


def main():
    con = sqlite3.connect(TRACE_DB)
    export_query(con, "SELECT * FROM target_trace_status ORDER BY state, target_id", OUT / "487_official_tenure_trace_status.csv")
    export_query(con, "SELECT * FROM official_tenure_matches ORDER BY state, target_id, dataset, official_title_number", OUT / "487_official_tenure_intersection_evidence.csv")
    counts = {
        "targets": con.execute("SELECT count(*) FROM targets").fetchone()[0],
        "status_rows": con.execute("SELECT count(*) FROM target_trace_status").fetchone()[0],
        "intersection_rows": con.execute("SELECT count(*) FROM official_tenure_matches").fetchone()[0],
        "targets_with_intersection": con.execute("SELECT count(DISTINCT target_id) FROM official_tenure_matches").fetchone()[0],
        "target_status_counts": dict(con.execute("SELECT target_status, count(*) FROM target_trace_status GROUP BY target_status")),
        "states": dict(con.execute("SELECT state, count(*) FROM targets GROUP BY state")),
    }
    con.close()
    assert counts["targets"] == counts["status_rows"] == 487
    (OUT / "487_official_tenure_trace_summary.json").write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(counts, ensure_ascii=False))


if __name__ == "__main__":
    main()
